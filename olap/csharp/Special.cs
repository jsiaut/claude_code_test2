// v7 : niveau spécialisé des primitives à deux niveaux du banc OLAP en C# (constante SPECIAL ; olap/SPEC.md, 7).
// Même plan, mêmes structures, mêmes fonctions de hachage ; AVX-512 (F, BW, DQ, VL, VBMI) par les intrinsèques de
// System.Runtime.Intrinsics.
//
//   0. décodage : seize valeurs à la fois, par permutation d'octets et décalages variables ;
//   1. sélection : comparaison de 16 valeurs et compression des positions retenues (vpcompressd) ;
//   2. agrégation de T1 : sommes masquées par groupe, huit lignes à la fois ;
//   3. recherche de sous-chaîne : premier et dernier octet de l'aiguille comparés à 64 positions à la fois ;
//   4. répartition : un tampon de 64 octets par partition, vidé par une écriture non temporelle ;
//   5. préchargement des cases et des octets à venir dans les agrégations et les sondes (dans Olap.cs, sous SPECIAL).
#if SPECIAL
using System;
using System.Numerics;
using System.Runtime.CompilerServices;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;

/// Répartition. Chaque partition a un tampon de 64 octets ; plein, il part d'un trait dans le morceau, sans passer
/// par le cache. La taille d'un tuple divise 64.
unsafe struct Parts {
    byte** dst, end;
    public PChunk** head;
    PChunk** tail;
    byte* fill, wc;
    public uint tsize;
    Arena* arena;

    public void Create() {
        byte** m = (byte**)Olap.HugeAlloc((nuint)(4 * Olap.NPART * sizeof(void*)));
        dst = m; end = m + Olap.NPART; head = (PChunk**)(m + 2 * Olap.NPART); tail = (PChunk**)(m + 3 * Olap.NPART);
        fill = (byte*)Olap.HugeAlloc(Olap.NPART);
        wc = (byte*)Olap.HugeAlloc(Olap.NPART * 64);
    }
    public void Init(Arena* a, uint ts) {
        new Span<byte>(dst, 4 * Olap.NPART * sizeof(void*)).Clear();
        new Span<byte>(fill, Olap.NPART).Clear();
        tsize = ts; arena = a;
    }
    [MethodImpl(MethodImplOptions.NoInlining)]
    void Chunk(uint k) {
        PChunk* c = (PChunk*)arena->Alloc(64 + Olap.CHUNK);
        c->next = null; c->used = 0;
        if (tail[k] != null) { tail[k]->used = (uint)(dst[k] - (byte*)(tail[k] + 1)); tail[k]->next = c; }
        else head[k] = c;
        tail[k] = c;
        dst[k] = (byte*)(c + 1);
        end[k] = dst[k] + Olap.CHUNK;
    }
    /// Place du prochain tuple de la partition k, dans son tampon.
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public void* Push(uint k) {
        uint f = fill[k];
        byte* w = wc + 64 * k;
        if (f == 64) {  // tampon plein : il est vidé avant de resservir
            if (dst[k] == end[k]) Chunk(k);
            Avx512F.StoreAlignedNonTemporal(dst[k], Vector512.LoadAligned(w));
            dst[k] += 64;
            f = 0;
        }
        fill[k] = (byte)(f + tsize);
        return w + f;
    }
    public void Close() {
        for (uint k = 0; k < Olap.NPART; k++) {
            if (fill[k] != 0) {
                if (dst[k] == end[k]) Chunk(k);
                Buffer.MemoryCopy(wc + 64 * k, dst[k], 64, fill[k]);
                dst[k] += fill[k];
                fill[k] = 0;
            }
            if (tail[k] != null) tail[k]->used = (uint)(dst[k] - (byte*)(tail[k] + 1));
        }
        Sse.StoreFence();
    }
}

static unsafe partial class Olap {
    const string Level = "s";
    const ulong SearchStep = 64;
    const int AHEAD = 16;  // tuples d'avance pour le préchargement

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    static void Prefetch(void* p) => Sse.Prefetch0(p);

    // ------------------------------------------------------------------------------------------------ 0. décodage
    // Seize valeurs à la fois (largeur de 25 bits au plus) : elles occupent 2 x largeur octets ; une permutation
    // d'octets (vpermb) amène dans chaque voie de 32 bits les 4 octets où commence sa valeur, un décalage variable la
    // cale, un masque la borne. Au-delà de 25 bits : huit valeurs à la fois dans des voies de 64 bits. Chaque pas lit
    // 64 octets : les colonnes sont chargées avec cette marge.
    static readonly byte* tabIdx = (byte*)HugeAlloc(33 * 64);
    static readonly uint* tabSh32 = (uint*)HugeAlloc(33 * 64);
    static readonly ulong* tabSh64 = (ulong*)HugeAlloc(33 * 64);
    static readonly bool tablesReady = MakeTables();

    static bool MakeTables() {
        for (uint w = 1; w <= 32; w++) {
            uint lanes = w <= 25 ? 16u : 8u, size = 64 / lanes;
            for (uint j = 0; j < lanes; j++) {
                for (uint k = 0; k < size; k++) tabIdx[64 * w + size * j + k] = (byte)((j * w >> 3) + k);
                if (w <= 25) tabSh32[16 * w + j] = j * w & 7; else tabSh64[8 * w + j] = j * w & 7;
            }
        }
        return true;
    }
    /// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 16.
    static void Unpack(in Col c, long b, int start, int n, int* outp) {
        Entry* e = c.dir + b;
        int w = (int)e->width;
        Vector512<int> bas = Vector512.Create((int)e->min);
        if (w == 0) {
            for (int i = 0; i < n; i += 16) bas.Store(outp + i);
            return;
        }
        byte* p = (byte*)(c.Words(b) + (ulong)(start / 64) * (ulong)w);
        Vector512<byte> idx = Vector512.LoadAligned(tabIdx + 64 * w);
        if (w <= 25) {
            Vector512<uint> sh = Vector512.Load(tabSh32 + 16 * w), mask = Vector512.Create((1u << w) - 1);
            for (int i = 0; i < n; i += 16, p += 2 * w) {
                Vector512<uint> x = Avx512Vbmi.PermuteVar64x8(Vector512.Load(p), idx).AsUInt32();
                ((Avx512F.ShiftRightLogicalVariable(x, sh) & mask).AsInt32() + bas).Store(outp + i);
            }
        } else {
            Vector512<ulong> sh = Vector512.Load(tabSh64 + 8 * w), mask = Vector512.Create((1UL << w) - 1);
            Vector256<int> bas8 = Vector256.Create((int)e->min);
            for (int i = 0; i < n; i += 8, p += w) {
                Vector512<ulong> x = Avx512Vbmi.PermuteVar64x8(Vector512.Load(p), idx).AsUInt64();
                (Avx512F.ConvertToVector256Int32(Avx512F.ShiftRightLogicalVariable(x, sh) & mask) + bas8).Store(outp + i);
            }
        }
    }

    // ------------------------------------------------------------------------------------------------ 1. sélection
    static readonly Vector512<int> Iota = Vector512.Create(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15);

    /// Masque des valeurs de v[0..16) comprises entre lo et hi, limité aux `left` valeurs qui restent. Les vecteurs de
    /// travail ont 16 cases de marge : chaque pas lit 16 voies entières.
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    static Vector512<int> Between(int* v, int left, Vector512<int> lo, Vector512<int> hi) {
        Vector512<int> x = Vector512.Load(v);
        Vector512<int> m = Vector512.GreaterThanOrEqual(x, lo) & Vector512.LessThanOrEqual(x, hi);
        return left >= 16 ? m : m & Vector512.LessThan(Iota, Vector512.Create(left));
    }
    /// Positions (bas + i) des valeurs v[i] comprises entre lo et hi, bornes comprises.
    static int SelBetween(int* v, int n, int lo, int hi, uint bas, int* pos) {
        Vector512<int> vlo = Vector512.Create(lo), vhi = Vector512.Create(hi), idx = Vector512.Create((int)bas) + Iota;
        int k = 0;
        for (int i = 0; i < n; i += 16) {
            Vector512<int> m = Between(v + i, n - i, vlo, vhi);
            Avx512F.CompressStore(pos + k, m, idx);
            k += BitOperations.PopCount(m.ExtractMostSignificantBits());
            idx += Vector512.Create(16);
        }
        return k;
    }
    /// Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
    static int KeepBetween(int* v, int* posIn, int* payIn, int n, int lo, int hi, int* posOut, int* payOut) {
        Vector512<int> vlo = Vector512.Create(lo), vhi = Vector512.Create(hi);
        int k = 0;
        for (int i = 0; i < n; i += 16) {
            Vector512<int> m = Between(v + i, n - i, vlo, vhi);
            Avx512F.CompressStore(posOut + k, m, Vector512.Load(posIn + i));
            Avx512F.CompressStore(payOut + k, m, Vector512.Load(payIn + i));
            k += BitOperations.PopCount(m.ExtractMostSignificantBits());
        }
        return k;
    }

    // ------------------------------------------------------------------------------------------------ 2. agrégation de T1
    /// Huit lignes à la fois : pour chacun des six groupes, un masque et cinq additions masquées.
    static void T1Aggregate(Agg1* agg, int* grp, int* qty, int* ext, int* disc, long* dp, long* ch, int* ship, int cut, int n, int* sel) {
        Vector512<long>* acc = stackalloc Vector512<long>[30];
        for (int j = 0; j < 30; j++) acc[j] = Vector512<long>.Zero;
        int* cnt = stackalloc int[6];
        new Span<int>(cnt, 6).Clear();
        Vector256<int> vcut = Vector256.Create(cut), iota8 = Vector256.Create(0, 1, 2, 3, 4, 5, 6, 7);
        for (int i = 0; i < n; i += 8) {
            Vector256<int> live = n - i >= 8 ? Vector256<int>.AllBitsSet : Vector256.LessThan(iota8, Vector256.Create(n - i));
            if (ship != null) live &= Vector256.LessThanOrEqual(Vector256.Load(ship + i), vcut);
            Vector256<int> g8 = Vector256.Load(grp + i);
            Vector512<long> q = Avx512F.ConvertToVector512Int64(Vector256.Load(qty + i));
            Vector512<long> e = Avx512F.ConvertToVector512Int64(Vector256.Load(ext + i));
            Vector512<long> d = Avx512F.ConvertToVector512Int64(Vector256.Load(disc + i));
            Vector512<long> x = Vector512.Load(dp + i), y = Vector512.Load(ch + i);
            for (int g = 0; g < 6; g++) {
                Vector256<int> m32 = Vector256.Equals(g8, Vector256.Create(g)) & live;
                Vector512<long> m = Avx512F.ConvertToVector512Int64(m32);  // voies à -1 ou 0
                Vector512<long>* a = acc + 5 * g;
                a[0] += q & m; a[1] += e & m; a[2] += x & m; a[3] += y & m; a[4] += d & m;
                cnt[g] += BitOperations.PopCount(m32.ExtractMostSignificantBits());
            }
        }
        for (int g = 0; g < 6; g++) {
            agg[g].qty += Vector512.Sum(acc[5 * g]);
            agg[g].bas += Vector512.Sum(acc[5 * g + 1]);
            agg[g].discPrice += Vector512.Sum(acc[5 * g + 2]);
            agg[g].charge += Vector512.Sum(acc[5 * g + 3]);
            agg[g].disc += Vector512.Sum(acc[5 * g + 4]);
            agg[g].count += cnt[g];
        }
    }

    // ------------------------------------------------------------------------------------------------ 3. sous-chaînes
    /// Candidates parmi les 64 positions qui partent de p : premier octet de l'aiguille en p + i, dernier en p + i + m - 1.
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    static ulong SearchCandidates(byte* p, uint m, byte c0, byte c1) =>
        Vector512.Equals(Vector512.Load(p), Vector512.Create(c0)).ExtractMostSignificantBits()
        & Vector512.Equals(Vector512.Load(p + m - 1), Vector512.Create(c1)).ExtractMostSignificantBits();
}
#endif
