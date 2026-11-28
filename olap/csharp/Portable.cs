// v7 : niveau portable des primitives à deux niveaux du banc OLAP en C# (compilé sans la constante SPECIAL). Aucune
// vectorisation explicite, aucune construction propre à une famille de processeurs.
#if !SPECIAL
using System;
using System.Runtime.CompilerServices;

/// Partitions. Tampons d'un fil : pour chaque partition, une liste de morceaux de CHUNK octets pris dans son arène.
unsafe struct Parts {
    byte** cur, end;
    public PChunk** head;
    PChunk** tail;
    public uint tsize;
    Arena* arena;

    public void Create() {
        byte** m = (byte**)Olap.HugeAlloc((nuint)(4 * Olap.NPART * sizeof(void*)));
        cur = m; end = m + Olap.NPART; head = (PChunk**)(m + 2 * Olap.NPART); tail = (PChunk**)(m + 3 * Olap.NPART);
    }
    public void Init(Arena* a, uint ts) {
        new Span<byte>(cur, 4 * Olap.NPART * sizeof(void*)).Clear();
        tsize = ts; arena = a;
    }
    [MethodImpl(MethodImplOptions.NoInlining)]
    byte* Chunk(uint k) {
        PChunk* c = (PChunk*)arena->Alloc(64 + Olap.CHUNK);
        c->next = null; c->used = 0;
        if (tail[k] != null) { tail[k]->used = (uint)(cur[k] - (byte*)(tail[k] + 1)); tail[k]->next = c; }
        else head[k] = c;
        tail[k] = c;
        cur[k] = (byte*)(c + 1);
        end[k] = cur[k] + Olap.CHUNK / tsize * tsize;
        return cur[k];
    }
    /// Place du prochain tuple de la partition k.
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public void* Push(uint k) {
        byte* t = cur[k];
        if (t == end[k]) t = Chunk(k);
        cur[k] = t + tsize;
        return t;
    }
    public void Close() {
        for (int k = 0; k < Olap.NPART; k++)
            if (tail[k] != null) tail[k]->used = (uint)(cur[k] - (byte*)(tail[k] + 1));
    }
}

static unsafe partial class Olap {
    const string Level = "p";
    const ulong SearchStep = 0;  // pas de recherche par 64 positions à ce niveau

    static ulong SearchCandidates(byte* p, uint m, byte c0, byte c1) => 0;

    static void Unpack(in Col c, long b, int start, int n, int* outp) => UnpackPortable(c, b, start, n, outp);

    /// 1 si x est entre lo et lo + span, 0 sinon ; sans branchement : la retenue d'une soustraction non signée.
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    static int InRange(int x, int lo, ulong span) => (int)(1 - ((span - (uint)(x - lo)) >> 63));

    /// Sélection. Positions (bas + i) des valeurs v[i] comprises entre lo et hi, bornes comprises.
    static int SelBetween(int* v, int n, int lo, int hi, uint bas, int* pos) {
        ulong span = (uint)(hi - lo);
        int k = 0;
        for (int i = 0; i < n; i++) {
            pos[k] = (int)(bas + (uint)i);
            k += InRange(v[i], lo, span);
        }
        return k;
    }
    /// Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
    static int KeepBetween(int* v, int* posIn, int* payIn, int n, int lo, int hi, int* posOut, int* payOut) {
        ulong span = (uint)(hi - lo);
        int k = 0;
        for (int i = 0; i < n; i++) {
            posOut[k] = posIn[i]; payOut[k] = payIn[i];
            k += InRange(v[i], lo, span);
        }
        return k;
    }

    /// Agrégation de T1 : un vecteur de n lignes dans le tableau des six groupes ; ship non nul : seules comptent les
    /// lignes dont la date ne dépasse pas cut (vecteur de sélection dans sel).
    static void T1Aggregate(Agg1* agg, int* grp, int* qty, int* ext, int* disc, long* dp, long* ch, int* ship, int cut, int n, int* sel) {
        if (ship == null) {
            for (int i = 0; i < n; i++) {
                Agg1* g = agg + grp[i];
                g->qty += qty[i]; g->bas += ext[i]; g->discPrice += dp[i]; g->charge += ch[i]; g->disc += disc[i]; g->count++;
            }
        } else {
            int k = SelBetween(ship, n, int.MinValue, cut, 0, sel);
            for (int j = 0; j < k; j++) {
                int i = sel[j];
                Agg1* g = agg + grp[i];
                g->qty += qty[i]; g->bas += ext[i]; g->discPrice += dp[i]; g->charge += ch[i]; g->disc += disc[i]; g->count++;
            }
        }
    }
}
#endif
