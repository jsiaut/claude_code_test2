// v7 (docs/V7.md ; olap/SPEC.md) : le banc OLAP en C#. Même architecture que la référence (olap/c/olap.c), écrite
// avec les moyens du langage : code `unsafe` et mémoire native (NativeMemory) pour les colonnes, les arènes, les
// tables et les tampons de partition ; routines de décodage par largeur engendrées (UnpackGen.cs) ;
// fils persistants (Monitor). Les primitives qui ont deux niveaux sont dans Portable.cs et dans Special.cs
// (constante SPECIAL).
//
// Usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]
using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Numerics;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Threading;

// ------------------------------------------------------------------------------------------------ mémoire, arènes
[StructLayout(LayoutKind.Sequential)]
unsafe struct ArenaBlock { public ArenaBlock* next; public nuint cap, used; fixed byte pad[40]; }  // 64 octets

/// Une arène par fil : allocation par déplacement d'un pointeur, remise à zéro à chaque exécution ; la mémoire est
/// gardée d'une répétition à l'autre.
unsafe struct Arena {
    public ArenaBlock* first, cur;

    public void* Alloc(nuint n) {
        n = (n + 63) & ~(nuint)63;
        for (;;) {
            ArenaBlock* b = cur;
            if (b != null && b->used + n <= b->cap) { void* p = (byte*)(b + 1) + b->used; b->used += n; return p; }
            if (b != null && b->next != null && b->next->cap >= n) { cur = b->next; cur->used = 0; continue; }
            nuint cap = Math.Max(n, Olap.ARENA_BLOCK - 64);
            ArenaBlock* nb = (ArenaBlock*)Olap.HugeAlloc(64 + cap);
            nb->cap = cap; nb->used = 0;
            if (b != null) { nb->next = b->next; b->next = nb; } else { nb->next = null; first = nb; }
            cur = nb;
        }
    }
    public T* Array<T>(ulong n) where T : unmanaged => (T*)Alloc((nuint)n * (nuint)sizeof(T));
    public void Reset() { cur = first; if (cur != null) cur->used = 0; }
}

// ------------------------------------------------------------------------------------------------ colonnes
[StructLayout(LayoutKind.Sequential)]
struct Entry { public long min, max; public ulong dataOff, auxOff; public uint width, count; }

unsafe struct Col {
    public ulong nrows, nblocks, auxCount;
    public Entry* dir;
    public ulong* data;
    public byte* aux;

    public ulong* Words(long b) => data + dir[b].dataOff / 8;
    /// Entrée d'un dictionnaire : ses octets suivent la table des positions.
    public ReadOnlySpan<byte> Dict(uint code) {
        uint* pos = (uint*)aux;
        return new ReadOnlySpan<byte>(aux + 4 * (auxCount + 1) + pos[code], (int)(pos[code + 1] - pos[code]));
    }
}

// ------------------------------------------------------------------------------------------------ table de hachage
struct Cell { public long key, val; }

/// Adressage ouvert, sondage linéaire, capacité en puissance de deux, clé et valeur dans la même case ; doublement
/// quand la table est à moitié pleine. Clés entières positives ou nulles ; -1 marque une case vide.
unsafe struct Map {
    public Cell* cells;
    public ulong mask, count;
    public Arena* arena;

    public void Init(Arena* a, ulong cap) {
        arena = a; mask = cap - 1; count = 0;
        cells = a->Array<Cell>(cap);
        new Span<byte>(cells, (int)(cap * 16)).Fill(0xFF);
    }
    /// Case de la clé, dont h est le Hash64 ; null si elle manque.
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public readonly Cell* Find(long key, ulong h) {
        for (ulong i = h & mask; ; i = (i + 1) & mask) {
            Cell* c = cells + i;
            if (c->key == key) return c;
            if (c->key == -1) return null;
        }
    }
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public readonly Cell* Find(long key) => Find(key, Olap.Hash64((ulong)key));
    void Grow() {
        Map old = this;
        Init(old.arena, 2 * (old.mask + 1));
        for (ulong j = 0; j <= old.mask; j++)
            if (old.cells[j].key != -1) {
                ulong i = Olap.Hash64((ulong)old.cells[j].key) & mask;
                while (cells[i].key != -1) i = (i + 1) & mask;
                cells[i] = old.cells[j];
            }
        count = old.count;
    }
    /// Rend la case de la clé, créée avec la valeur 0 si elle manquait (fresh le dit).
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public Cell* Upsert(long key, out bool fresh) {
        if ((count + 1) * 2 > mask + 1) Grow();
        for (ulong i = Olap.Hash64((ulong)key) & mask; ; i = (i + 1) & mask) {
            Cell* c = cells + i;
            if (c->key == key) { fresh = false; return c; }
            if (c->key == -1) { c->key = key; c->val = 0; count++; fresh = true; return c; }
        }
    }
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public Cell* Upsert(long key) => Upsert(key, out _);
}

/// Filtre de Bloom par blocs, devant les sondes de semi-jointure : 16 bits par clé, deux bits dans un même mot de
/// 64 bits. Un refus est sûr ; une acceptation se confirme dans la table.
unsafe struct Bloom {
    public ulong* bits;
    public ulong mask;

    public void Init(Arena* a, ulong nkeys) {
        ulong words = 64;
        while (words * 4 < nkeys) words *= 2;
        bits = a->Array<ulong>(words);
        new Span<ulong>(bits, (int)words).Clear();
        mask = words - 1;
    }
    static ulong Two(ulong h) => 1UL << (int)(h & 63) | 1UL << (int)((h >> 6) & 63);
    public void Add(ulong h) => bits[(h >> 12) & mask] |= Two(h);
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public readonly bool Test(ulong h) { ulong m = Two(h); return (bits[(h >> 12) & mask] & m) == m; }
}

/// Même table pour des clés faites d'un entier et d'une chaîne : la case garde le hachage, l'entier, la position et
/// la longueur de la chaîne, et un compte. Hachage nul : case vide.
struct SCell { public ulong hash; public long ikey; public ulong pos; public uint len, count; }

unsafe struct SMap {
    public SCell* cells;
    public ulong mask, n;
    public Arena* arena;
    public byte* bytes;

    public void Init(Arena* a, ulong cap, byte* b) {
        arena = a; mask = cap - 1; n = 0; bytes = b;
        cells = a->Array<SCell>(cap);
        new Span<byte>(cells, (int)(cap * 32)).Clear();
    }
    void Grow() {
        SMap old = this;
        Init(old.arena, 2 * (old.mask + 1), old.bytes);
        for (ulong j = 0; j <= old.mask; j++)
            if (old.cells[j].hash != 0) {
                ulong i = old.cells[j].hash & mask;
                while (cells[i].hash != 0) i = (i + 1) & mask;
                cells[i] = old.cells[j];
            }
        n = old.n;
    }
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public void Add(ulong hash, long ikey, ulong pos, uint len) {
        if ((n + 1) * 2 > mask + 1) Grow();
        for (ulong i = hash & mask; ; i = (i + 1) & mask) {
            SCell* c = cells + i;
            if (c->hash == hash && c->ikey == ikey && c->len == len &&
                new ReadOnlySpan<byte>(bytes + c->pos, (int)len).SequenceEqual(new ReadOnlySpan<byte>(bytes + pos, (int)len))) {
                c->count++;
                return;
            }
            if (c->hash == 0) { *c = new SCell { hash = hash, ikey = ikey, pos = pos, len = len, count = 1 }; n++; return; }
        }
    }
}

// ------------------------------------------------------------------------------------------------ état des fils
[StructLayout(LayoutKind.Sequential)]
unsafe struct PChunk { public PChunk* next; public uint used, pad; fixed byte fill[48]; }  // 64 octets, puis les tuples

/// Vecteurs de travail d'un fil. Ceux de 32 bits ont 16 cases de marge pour les pas entiers du niveau spécialisé.
unsafe struct Scratch {
    public fixed int a[Olap.VEC + 16], b[Olap.VEC + 16], c[Olap.VEC + 16], d[Olap.VEC + 16], e[Olap.VEC + 16], f[Olap.VEC + 16],
        g[Olap.VEC + 16], sel[Olap.VEC + 16], sel2[Olap.VEC + 16], pos[Olap.VEC + 16];
    public fixed long x[Olap.VEC], y[Olap.VEC];
    public fixed ulong h[Olap.VEC];
    public fixed int len[Olap.BLOCK + 16], rows[Olap.BLOCK + 16];
}

/// Liste d'entiers de 64 bits dans une arène.
unsafe struct List {
    public long* v;
    public ulong n, cap;
    public Arena* a;

    public void Init(Arena* arena) { v = null; n = cap = 0; a = arena; }
    public void Push(long x) {
        if (n == cap) {
            ulong c = cap != 0 ? 2 * cap : 1024;
            long* nv = a->Array<long>(c);
            if (n != 0) Buffer.MemoryCopy(v, nv, c * 8, n * 8);
            v = nv; cap = c;
        }
        v[n++] = x;
    }
}

/// Compteur de morceaux partagé : la seule opération atomique.
sealed class Counter {
    long next;
    public long n;
    public void Set(ulong count) { Volatile.Write(ref next, 0); n = (long)count; }
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public long Take() {
        long i = Interlocked.Increment(ref next) - 1;
        return i < n ? i : -1;
    }
}

/// Les fils sont créés une fois et attendent, bloqués, entre deux phases.
sealed class Pool {
    int n = 1, pending;
    long generation;
    Action<int>? task;
    readonly object gate = new();

    public void Start(int threads) {
        n = threads;
        for (int i = 1; i < n; i++) {
            int tid = i;
            new Thread(() => Worker(tid)) { IsBackground = true }.Start();
        }
    }
    void Worker(int tid) {
        long seen = 0;
        for (;;) {
            Action<int> t;
            lock (gate) {
                while (generation == seen) Monitor.Wait(gate);
                seen = generation;
                t = task!;
            }
            t(tid);
            lock (gate) {
                if (--pending == 0) Monitor.PulseAll(gate);
            }
        }
    }
    /// Exécute t sur tous les fils (le fil principal est le fil 0) et attend la fin de tous.
    public void Run(Action<int> t) {
        if (n > 1) lock (gate) {
            task = t; pending = n - 1; generation++;
            Monitor.PulseAll(gate);
        }
        t(0);
        if (n > 1) lock (gate) {
            while (pending > 0) Monitor.Wait(gate);
        }
    }
}

static unsafe partial class Olap {
    public const int PBITS = 10;          // bits de partition
    public const int VEC = 2048;          // lignes d'un vecteur
    public const int CHUNK = 16384;       // octets utiles d'un morceau de tampon de partition
    public const int BLOCK = 65536;       // lignes d'un bloc : un morceau
    public const int NPART = 1 << PBITS;  // partitions des grandes tables
    public const int MAXT = 64;           // fils au plus
    public const nuint ARENA_BLOCK = 32 << 20, HUGE_PAGE = 1 << 21;
    public const ulong K1 = 0x9E3779B97F4A7C15, K2 = 0xC2B2AE3D27D4EB4F;

    static void Die(string msg) {
        Console.Error.WriteLine("olap : " + msg);
        Environment.Exit(2);
    }

    [DllImport("libc")]
    static extern int madvise(void* addr, nuint len, int advice);

    /// Toute la mémoire du programme hors du tas (colonnes chargées, arènes, vecteurs de travail) vient du système
    /// par zones alignées sur 2 Mio et signalées comme pages larges.
    public static void* HugeAlloc(nuint n) {
        n = (n + HUGE_PAGE - 1) & ~(HUGE_PAGE - 1);
        void* p = NativeMemory.AlignedAlloc(n, HUGE_PAGE);
        madvise(p, n, 14);  // MADV_HUGEPAGE
        return p;
    }

    static string dataDir = "";

    static Col Open(string table, string name) {
        using var f = File.OpenHandle(Path.Combine(dataDir, table, name + ".msc"));
        long size = RandomAccess.GetLength(f);
        byte* b = (byte*)HugeAlloc((nuint)size + 64);  // la colonne est lue en entier, en pages larges, avec 64 octets de marge
        new Span<byte>(b + size, 64).Clear();
        for (long off = 0; off < size;) {
            int n = RandomAccess.Read(f, new Span<byte>(b + off, (int)Math.Min(size - off, 1 << 30)), off);
            if (n <= 0) Die("lecture");
            off += n;
        }
        if (*(uint*)b != 0x3143534D) Die("format");  // « MSC1 »
        if (*(uint*)(b + 12) != BLOCK) Die("taille de bloc");
        ulong* h = (ulong*)(b + 16);
        return new Col { nrows = h[0], nblocks = h[1], dir = (Entry*)(b + h[2]), data = (ulong*)(b + h[3]), aux = b + h[4], auxCount = h[5] };
    }

    // ------------------------------------------------------------------------------------------------ décodage
    // Une routine par largeur, engendrée (GenUnpack.cs écrit UnpackGen.cs) : un groupe de 64 valeurs occupe W mots ;
    // chaque routine est la suite des 64 affectations d'un groupe, à positions constantes. Le compilateur à la volée
    // ne déroule ni ne vectorise la boucle générale : le texte engendré le fait pour lui.
    /// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 64.
    static void UnpackPortable(in Col c, long b, int start, int n, int* outp) {
        Entry* e = c.dir + b;
        if (e->width == 0) {
            new Span<int>(outp, n).Fill((int)e->min);
            return;
        }
        UnpackFn[e->width](c.Words(b) + (ulong)(start / 64) * e->width, outp, n, (uint)e->min);
    }
    /// Décode les valeurs du bloc b aux positions pos (lignes dans le bloc), dans l'ordre : out[i] est celle de pos[i].
    static void UnpackSel(in Col c, long b, int* pos, int n, int* outp) {
        Entry* e = c.dir + b;
        ulong* inp = c.Words(b);
        uint w = e->width, bas = (uint)e->min;
        if (w == 0) {
            new Span<int>(outp, n).Fill((int)bas);
            return;
        }
        ulong mask = (1UL << (int)w) - 1;
        for (int i = 0; i < n; i++) {
            ulong bit = (ulong)pos[i] * w, idx = bit >> 6;
            int sh = (int)(bit & 63);
            ulong v = (inp[idx] >> sh) | (inp[idx + 1] << 1 << (63 - sh));
            outp[i] = (int)((uint)(v & mask) + bas);
        }
    }

    // ------------------------------------------------------------------------------------------------ hachage
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public static ulong Hash64(ulong k) { k *= K1; return k ^ (k >> 32); }
    /// Octets : deux voies de mots de 64 bits ; le dernier mot, incomplet, est masqué (8 octets lisibles après la fin).
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    static ulong HashBytes(byte* p, uint n) {
        ulong h1 = K1 ^ n, h2 = K2;
        while (n >= 16) {
            h1 = (BitOperations.RotateLeft(h1, 5) ^ *(ulong*)p) * K1;
            h2 = (BitOperations.RotateLeft(h2, 5) ^ *(ulong*)(p + 8)) * K2;
            p += 16; n -= 16;
        }
        if (n >= 8) { h1 = (BitOperations.RotateLeft(h1, 5) ^ *(ulong*)p) * K1; p += 8; n -= 8; }
        if (n != 0) h2 = (BitOperations.RotateLeft(h2, 5) ^ (*(ulong*)p & ((1UL << (int)(8 * n)) - 1))) * K2;
        ulong h = (h1 ^ BitOperations.RotateLeft(h2, 32)) * K1;
        h ^= h >> 32;
        return h != 0 ? h : 1;  // 0 marque une case vide
    }
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    static uint PartOf(ulong h) => (uint)(h >> (64 - PBITS));

    static ulong Pow2For(ulong n) {  // capacité pour n clés : au moins le double, 16 au moins
        ulong cap = 16;
        while (cap < 2 * n) cap *= 2;
        return cap;
    }
    /// Capacité de départ d'une table d'agrégation qui recevra n tuples ; elle double ensuite à la demande.
    static ulong Pow2Start(ulong n) => Pow2For(n / 8);

    // ------------------------------------------------------------------------------------------------ partitions
    static ulong PartsCount(Parts* ps, int nt, long k) {
        ulong n = 0;
        for (int t = 0; t < nt; t++)
            for (PChunk* c = ps[t].head[k]; c != null; c = c->next) n += c->used / ps[t].tsize;
        return n;
    }

    // ------------------------------------------------------------------------------------------------ état des fils
    static int NT;
    static readonly Pool pool = new();
    static Arena* arena;
    static Scratch** scratch;
    static Parts* parts, parts2;

    // ------------------------------------------------------------------------------------------------ résultat
    static byte[] res = new byte[1 << 16];
    static int resLen;

    static void Room(int n) {
        if (resLen + n > res.Length) System.Array.Resize(ref res, Math.Max(2 * res.Length, resLen + n));
    }
    static void Emit(ReadOnlySpan<byte> s) {
        Room(s.Length);
        s.CopyTo(res.AsSpan(resLen));
        resLen += s.Length;
    }
    static void Emit(long v) {
        Room(24);
        v.TryFormat(res.AsSpan(resLen), out int n, default, CultureInfo.InvariantCulture);
        resLen += n;
    }
    static void Emit(ulong v) {
        Room(24);
        v.TryFormat(res.AsSpan(resLen), out int n, default, CultureInfo.InvariantCulture);
        resLen += n;
    }
    static ulong Fnv1a(ReadOnlySpan<byte> s) {
        ulong h = 0xCBF29CE484222325;
        foreach (byte c in s) h = (h ^ c) * 0x100000001B3;
        return h;
    }

    // ------------------------------------------------------------------------------------------------ dates
    static int DaysFromCivil(int y, int m, int d) {  // jours depuis le 1er janvier 1970
        if (m <= 2) y--;
        int era = (y >= 0 ? y : y - 399) / 400, yoe = y - era * 400;
        int doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
        return era * 146097 + yoe * 365 + yoe / 4 - yoe / 100 + doy - 719468;
    }
    static readonly int[] YearStart = MakeYears();  // premier jour de chaque année à partir de 1970
    static int[] MakeYears() {
        var t = new int[200];
        for (int y = 0; y < 200; y++) t[y] = DaysFromCivil(1970 + y, 1, 1);
        return t;
    }
    static long YearOf(int days) {
        int y = days / 366;
        while (YearStart[y + 1] <= days) y++;
        return 1970 + y;
    }

    // ------------------------------------------------------------------------------------------------ sous-chaînes
    // Lignes d'un bloc de chaînes qui contiennent l'aiguille (2 octets au moins) : les octets du bloc sont parcourus
    // d'un trait, par mots de 8 octets ; un mot est candidat si, à une même position, il porte le premier octet de
    // l'aiguille et le mot décalé de sa longueur moins un porte le dernier. Une occurrence compte si elle tient dans
    // une ligne, et une ligne compte une fois.
    const ulong ONES = 0x0101010101010101, HIGHS = 0x8080808080808080;

    static ulong ZeroBytes(ulong x) => ~(((x & ~HIGHS) + ~HIGHS) | x) & HIGHS;  // bit de poids fort de chaque octet nul de x

    static int SearchBlock(byte* buf, ulong nbytes, int* len, ReadOnlySpan<byte> needle, int* rows) {
        uint m = (uint)needle.Length;
        int r = 0, k = 0;
        ulong rowEnd = nbytes != 0 ? (ulong)len[0] : 0;
        byte c0 = needle[0], c1 = needle[(int)m - 1];
        ulong first = ONES * c0, last = ONES * c1;
        ulong stop = nbytes >= m ? nbytes - m + 1 : 0;  // positions de départ possibles : [0, stop)
        for (ulong i = 0; i < stop;) {
            ulong cand, next = i + 8;
            int shift = 3;  // un bit candidat par octet du mot : rang du bit / 8
            if (SearchStep > 0 && i + SearchStep + m - 1 <= nbytes) {
                // niveau spécialisé : 64 positions d'un coup, un bit candidat par position
                cand = SearchCandidates(buf + i, m, c0, c1);
                if (cand == 0) { i += SearchStep; continue; }
                next = i + SearchStep; shift = 0;
            } else if (i + 8 <= stop) {  // les deux mots sont dans le bloc
                cand = ZeroBytes((*(ulong*)(buf + i) ^ first) | (*(ulong*)(buf + i + m - 1) ^ last));
                if (cand == 0) { i += 8; continue; }
            } else {
                cand = 0;
                for (ulong j = i; j < stop; j++)
                    if (buf[j] == c0 && buf[j + m - 1] == c1) cand |= 0x80UL << (int)(8 * (j - i));
            }
            for (; cand != 0; cand &= cand - 1) {
                ulong at = i + ((ulong)BitOperations.TrailingZeroCount(cand) >> shift);
                if (!new ReadOnlySpan<byte>(buf + at + 1, (int)m - 2).SequenceEqual(needle.Slice(1, (int)m - 2))) continue;
                while (rowEnd <= at) rowEnd += (ulong)len[++r];
                if (at + m <= rowEnd) { rows[k++] = r; next = rowEnd; break; }  // la suite de la ligne est sautée
            }
            i = next;
        }
        return k;
    }
    /// Longueurs d'un bloc de chaînes (dans len) ; rend le nombre de ses octets.
    static ulong BlockLengths(in Col c, long b, int* len) {
        int n = (int)c.dir[b].count;
        Unpack(c, b, 0, n, len);
        ulong total = 0;
        for (int i = 0; i < n; i++) total += (ulong)len[i];
        return total;
    }

    // ------------------------------------------------------------------------------------------------ dix premiers
    struct Top { public uint count, len; public long ikey; public ulong pos; }
    struct Top10 {
        public fixed byte raw[10 * 24];
        public int n;
        Top* T => (Top*)Unsafe.AsPointer(ref raw[0]);

        /// Ordre : compte décroissant, entier croissant, chaîne croissante.
        static bool Before(in Top a, in Top b, byte* bytes) {
            if (a.count != b.count) return a.count > b.count;
            if (a.ikey != b.ikey) return a.ikey < b.ikey;
            return new ReadOnlySpan<byte>(bytes + a.pos, (int)a.len).SequenceCompareTo(new ReadOnlySpan<byte>(bytes + b.pos, (int)b.len)) < 0;
        }
        public void Add(Top x, byte* bytes) {
            Top* t = T;
            if (n == 10 && !Before(x, t[9], bytes)) return;
            int i = n < 10 ? n++ : 9;
            for (; i > 0 && Before(x, t[i - 1], bytes); i--) t[i] = t[i - 1];
            t[i] = x;
        }
        public Top Get(int i) => T[i];
    }

    // ================================================================================================ T1 (TPC-H Q1)
    public struct Agg1 { public long qty, bas, discPrice, charge, disc, count, pad0, pad1; }  // un groupe de T1

    static class T1 {
        static Col ship, rf, ls, qty, ext, disc, tax;
        static readonly Counter ctr = new();
        static int cut;
        static Agg1* agg;  // six groupes par fil

        public static void Open() {
            ship = Olap.Open("lineitem", "l_shipdate"); rf = Olap.Open("lineitem", "l_returnflag");
            ls = Olap.Open("lineitem", "l_linestatus"); qty = Olap.Open("lineitem", "l_quantity");
            ext = Olap.Open("lineitem", "l_extendedprice"); disc = Olap.Open("lineitem", "l_discount");
            tax = Olap.Open("lineitem", "l_tax");
            cut = DaysFromCivil(1998, 9, 2);
            agg = (Agg1*)HugeAlloc((nuint)(MAXT * 6 * sizeof(Agg1)));
        }
        static void Task(int tid) {
            Scratch* s = scratch[tid];
            Agg1* local = stackalloc Agg1[6];
            new Span<Agg1>(local, 6).Clear();
            for (long b; (b = ctr.Take()) >= 0;) {
                Entry* e = ship.dir + b;
                if (e->min > cut) continue;    // bloc exclu par sa carte de zones
                bool all = e->max <= cut;      // bloc retenu en entier : le filtre n'est pas évalué
                for (int st = 0, count = (int)e->count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(rf, b, st, n, s->a);
                    Unpack(ls, b, st, n, s->b);
                    Unpack(qty, b, st, n, s->c);
                    Unpack(ext, b, st, n, s->d);
                    Unpack(disc, b, st, n, s->e);
                    Unpack(tax, b, st, n, s->f);
                    T1Expr(s->d, s->e, s->f, s->a, s->b, s->x, s->y, s->g, n);
                    int* dates = null;
                    if (!all) { Unpack(ship, b, st, n, s->pos); dates = s->pos; }
                    T1Aggregate(local, s->g, s->c, s->d, s->e, s->x, s->y, dates, cut, n, s->sel);
                }
            }
            for (int g = 0; g < 6; g++) agg[tid * 6 + g] = local[g];
        }
        public static void Run() {
            ctr.Set(ship.nblocks);
            pool.Run(Task);
            for (uint g = 0; g < 6; g++) {
                Agg1 a = default;
                for (int t = 0; t < NT; t++) {
                    Agg1* x = agg + t * 6 + g;
                    a.qty += x->qty; a.bas += x->bas; a.discPrice += x->discPrice; a.charge += x->charge; a.disc += x->disc;
                    a.count += x->count;
                }
                if (a.count == 0) continue;
                Emit(rf.Dict(g / 2)); Emit("|"u8); Emit(ls.Dict(g % 2));
                Emit("|"u8); Emit(a.qty); Emit("|"u8); Emit(a.bas); Emit("|"u8); Emit(a.discPrice); Emit("|"u8); Emit(a.charge);
                Emit("|"u8); Emit(a.disc); Emit("|"u8); Emit(a.count); Emit("\n"u8);
            }
        }
    }

    // ================================================================================================ T6 (TPC-H Q6)
    static class T6 {
        static Col ship, disc, qty, ext;
        static readonly Counter ctr = new();
        static int lo, hi;
        static readonly long[] sum = new long[MAXT * 8];

        public static void Open() {
            ship = Olap.Open("lineitem", "l_shipdate"); disc = Olap.Open("lineitem", "l_discount");
            qty = Olap.Open("lineitem", "l_quantity"); ext = Olap.Open("lineitem", "l_extendedprice");
            lo = DaysFromCivil(1994, 1, 1); hi = DaysFromCivil(1995, 1, 1);
        }
        static void Task(int tid) {
            Scratch* s = scratch[tid];
            long total = 0;
            for (long b; (b = ctr.Take()) >= 0;) {
                Entry* e = ship.dir + b;
                if (e->max < lo || e->min >= hi) continue;
                for (int st = 0, count = (int)e->count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(ship, b, st, n, s->a);
                    int k = SelBetween(s->a, n, lo, hi - 1, (uint)st, s->pos);
                    if (k == 0) continue;
                    UnpackSel(disc, b, s->pos, k, s->b);
                    int k2 = KeepBetween(s->b, s->pos, s->b, k, 5, 7, s->sel, s->c);
                    if (k2 == 0) continue;
                    UnpackSel(qty, b, s->sel, k2, s->d);
                    int k3 = KeepBetween(s->d, s->sel, s->c, k2, int.MinValue, 2399, s->sel2, s->e);
                    if (k3 == 0) continue;
                    UnpackSel(ext, b, s->sel2, k3, s->f);
                    for (int i = 0; i < k3; i++) total += (long)s->f[i] * s->e[i];
                }
            }
            sum[tid * 8] = total;
        }
        public static void Run() {
            ctr.Set(ship.nblocks);
            pool.Run(Task);
            long total = 0;
            for (int t = 0; t < NT; t++) total += sum[t * 8];
            Emit(total); Emit("\n"u8);
        }
    }

    // ================================================================================================ T9 (TPC-H Q9)
    // 1. part : noms qui contiennent « green » -> ensemble de pièces (table et filtre de Bloom) ;
    // 2. partsupp : lignes de ces pièces -> (pièce, fournisseur) -> coût ; 3. supplier -> nation ;
    // 4. lineitem : lignes de ces pièces, montant et nation, réparties par commande ;
    // 5. orders : (commande, date) réparties de même ; 6. par partition : table des lignes de lineitem, sondée par les
    //    commandes ; agrégat par nation et année.
    struct T9Tuple { public int okey, nation; public long amount; }
    struct T9Order { public int okey, date; }
    struct T9Row { public uint name; public long year, sum; }

    /// Positions (dans le bloc) et clés des lignes d'un vecteur dont la clé est dans l'ensemble (filtre, puis table).
    static int Semi(in Map set, in Bloom filter, int* key, int n, int st, int* pos, int* outp) {
        int k = 0;
        for (int i = 0; i < n; i++) {
            ulong h = Hash64((ulong)key[i]);
            if (filter.Test(h) && set.Find(key[i], h) != null) { pos[k] = st + i; outp[k++] = key[i]; }
        }
        return k;
    }

    static class T9 {
        static Col pPartkey, pName, psPartkey, psSuppkey, psCost, sSuppkey, sNationkey, nNationkey, nName, lPartkey, lSuppkey,
            lOrderkey, lQty, lExt, lDisc, oOrderkey, oOrderdate;
        static readonly Counter ctr = new();
        static List* l1, l2;  // listes des fils
        static Map part, ps, supp;
        static Map* agg;
        static Bloom fpart;

        public static void Open() {
            pPartkey = Olap.Open("part", "p_partkey"); pName = Olap.Open("part", "p_name");
            psPartkey = Olap.Open("partsupp", "ps_partkey"); psSuppkey = Olap.Open("partsupp", "ps_suppkey");
            psCost = Olap.Open("partsupp", "ps_supplycost"); sSuppkey = Olap.Open("supplier", "s_suppkey");
            sNationkey = Olap.Open("supplier", "s_nationkey"); nNationkey = Olap.Open("nation", "n_nationkey");
            nName = Olap.Open("nation", "n_name"); lPartkey = Olap.Open("lineitem", "l_partkey");
            lSuppkey = Olap.Open("lineitem", "l_suppkey"); lOrderkey = Olap.Open("lineitem", "l_orderkey");
            lQty = Olap.Open("lineitem", "l_quantity"); lExt = Olap.Open("lineitem", "l_extendedprice");
            lDisc = Olap.Open("lineitem", "l_discount"); oOrderkey = Olap.Open("orders", "o_orderkey");
            oOrderdate = Olap.Open("orders", "o_orderdate");
            l1 = (List*)HugeAlloc((nuint)(MAXT * sizeof(List))); l2 = (List*)HugeAlloc((nuint)(MAXT * sizeof(List)));
            agg = (Map*)HugeAlloc((nuint)(MAXT * sizeof(Map)));
        }
        static void PartTask(int tid) {
            Scratch* s = scratch[tid];
            l1[tid].Init(arena + tid);
            for (long b; (b = ctr.Take()) >= 0;) {
                ulong nbytes = BlockLengths(pName, b, s->len);
                int k = SearchBlock(pName.aux + pName.dir[b].auxOff, nbytes, s->len, "green"u8, s->rows);
                for (int i = 0; i < k; i += VEC) {
                    int n = Math.Min(k - i, VEC);
                    UnpackSel(pPartkey, b, s->rows + i, n, s->a);
                    for (int j = 0; j < n; j++) l1[tid].Push(s->a[j]);
                }
            }
        }
        static void PsTask(int tid) {
            Scratch* s = scratch[tid];
            l1[tid].Init(arena + tid);
            l2[tid].Init(arena + tid);
            for (long b; (b = ctr.Take()) >= 0;)
                for (int st = 0, count = (int)psPartkey.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(psPartkey, b, st, n, s->a);
                    int k = Semi(part, fpart, s->a, n, st, s->pos, s->b);
                    if (k == 0) continue;
                    UnpackSel(psSuppkey, b, s->pos, k, s->c);
                    UnpackSel(psCost, b, s->pos, k, s->d);
                    for (int i = 0; i < k; i++) {
                        l1[tid].Push((long)s->b[i] << 32 | (long)s->c[i]);
                        l2[tid].Push(s->d[i]);
                    }
                }
        }
        static void LineTask(int tid) {
            Scratch* s = scratch[tid];
            Parts* p = parts + tid;
            p->Init(arena + tid, (uint)sizeof(T9Tuple));
            for (long b; (b = ctr.Take()) >= 0;)
                for (int st = 0, count = (int)lPartkey.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(lPartkey, b, st, n, s->a);
                    int k = Semi(part, fpart, s->a, n, st, s->pos, s->b);
                    if (k == 0) continue;
                    UnpackSel(lSuppkey, b, s->pos, k, s->c);
                    UnpackSel(lOrderkey, b, s->pos, k, s->d);
                    UnpackSel(lQty, b, s->pos, k, s->e);
                    UnpackSel(lExt, b, s->pos, k, s->f);
                    UnpackSel(lDisc, b, s->pos, k, s->g);
#if SPECIAL
                    for (int i = 0; i < k; i++) {  // les cases des deux tables sont préchargées pour tout le vecteur
                        Prefetch(ps.cells + (Hash64((ulong)((long)s->b[i] << 32 | (long)s->c[i])) & ps.mask));
                        Prefetch(supp.cells + (Hash64((ulong)s->c[i]) & supp.mask));
                    }
#endif
                    for (int i = 0; i < k; i++) {
                        long cost = ps.Find((long)s->b[i] << 32 | (long)s->c[i])->val;
                        long nation = supp.Find(s->c[i])->val;
                        T9Tuple* t = (T9Tuple*)p->Push(PartOf(Hash64((ulong)s->d[i])));
                        t->okey = s->d[i]; t->nation = (int)nation;
                        t->amount = (long)s->f[i] * (100 - s->g[i]) - cost * s->e[i];
                    }
                }
            p->Close();
        }
        static void OrdersTask(int tid) {
            Scratch* s = scratch[tid];
            Parts* p = parts2 + tid;
            p->Init(arena + tid, (uint)sizeof(T9Order));
            for (long b; (b = ctr.Take()) >= 0;)
                for (int st = 0, count = (int)oOrderkey.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(oOrderkey, b, st, n, s->a);
                    Unpack(oOrderdate, b, st, n, s->b);
                    HashKeys(s->a, n, s->h);
                    for (int i = 0; i < n; i++) {
                        T9Order* t = (T9Order*)p->Push(PartOf(s->h[i]));
                        t->okey = s->a[i]; t->date = s->b[i];
                    }
                }
            p->Close();
        }
        static void JoinTask(int tid) {
            Arena* a = arena + tid;
            Map total = default;
            total.Init(a, 1024);
            for (long k; (k = ctr.Take()) >= 0;) {
                ulong n = PartsCount(parts, NT, k);
                if (n == 0) continue;
                T9Tuple* tu = a->Array<T9Tuple>(n);
                int* next = a->Array<int>(n);
                Map m = default;  // commande -> rang de son dernier tuple ; next chaîne les tuples d'une même commande
                m.Init(a, Pow2For(n));
                int i = 0;
                for (int th = 0; th < NT; th++)
                    for (PChunk* c = parts[th].head[k]; c != null; c = c->next)
                        for (T9Tuple* t = (T9Tuple*)(c + 1), end = (T9Tuple*)((byte*)(c + 1) + c->used); t < end; t++) {
                            Cell* cell = m.Upsert(t->okey, out bool fresh);
                            tu[i] = *t;
                            next[i] = fresh ? -1 : (int)cell->val;
                            cell->val = i++;
                        }
                for (int th = 0; th < NT; th++)
                    for (PChunk* c = parts2[th].head[k]; c != null; c = c->next)
                        for (T9Order* o = (T9Order*)(c + 1), end = (T9Order*)((byte*)(c + 1) + c->used); o < end; o++) {
#if SPECIAL
                            if (o + AHEAD < end) Prefetch(m.cells + (Hash64((ulong)o[AHEAD].okey) & m.mask));
#endif
                            Cell* cell = m.Find(o->okey);
                            if (cell == null) continue;
                            long year = YearOf(o->date);
                            for (int j = (int)cell->val; j >= 0; j = next[j])
                                total.Upsert((long)tu[j].nation << 16 | year)->val += tu[j].amount;
                        }
            }
            agg[tid] = total;
        }
        public static void Run() {
            Arena* a0 = arena;
            Scratch* s = scratch[0];
            ctr.Set(pName.nblocks);
            pool.Run(PartTask);
            ulong n = 0;
            for (int t = 0; t < NT; t++) n += l1[t].n;
            part.Init(a0, Pow2For(n));
            fpart.Init(a0, n);
            for (int t = 0; t < NT; t++)
                for (ulong i = 0; i < l1[t].n; i++) {
                    part.Upsert(l1[t].v[i]);
                    fpart.Add(Hash64((ulong)l1[t].v[i]));
                }
            ctr.Set(psPartkey.nblocks);
            pool.Run(PsTask);
            n = 0;
            for (int t = 0; t < NT; t++) n += l1[t].n;
            ps.Init(a0, Pow2For(n));
            for (int t = 0; t < NT; t++)
                for (ulong i = 0; i < l1[t].n; i++) ps.Upsert(l1[t].v[i])->val = l2[t].v[i];
            supp.Init(a0, Pow2For(sSuppkey.nrows));
            for (long b = 0; b < (long)sSuppkey.nblocks; b++)
                for (int st = 0, count = (int)sSuppkey.dir[b].count; st < count; st += VEC) {
                    int m = Math.Min(count - st, VEC);
                    Unpack(sSuppkey, b, st, m, s->a);
                    Unpack(sNationkey, b, st, m, s->b);
                    for (int i = 0; i < m; i++) supp.Upsert(s->a[i])->val = s->b[i];
                }
            ctr.Set(lPartkey.nblocks);
            pool.Run(LineTask);
            ctr.Set(oOrderkey.nblocks);
            pool.Run(OrdersTask);
            ctr.Set(NPART);
            pool.Run(JoinTask);
            // fusion ; nation -> nom ; tri par nom puis année décroissante
            Map total = default;
            total.Init(a0, 1024);
            for (int t = 0; t < NT; t++)
                for (ulong j = 0; j <= agg[t].mask; j++)
                    if (agg[t].cells[j].key != -1) total.Upsert(agg[t].cells[j].key)->val += agg[t].cells[j].val;
            Map nat = default;
            nat.Init(a0, 64);
            int nn = (int)nNationkey.nrows;
            Unpack(nNationkey, 0, 0, nn, s->a);
            Unpack(nName, 0, 0, nn, s->b);
            for (int i = 0; i < nn; i++) nat.Upsert(s->a[i])->val = s->b[i];
            var rows = new T9Row[total.count];
            int nr = 0;
            for (ulong j = 0; j <= total.mask; j++)
                if (total.cells[j].key != -1)
                    rows[nr++] = new T9Row { name = (uint)nat.Find(total.cells[j].key >> 16)->val, year = total.cells[j].key & 0xFFFF, sum = total.cells[j].val };
            System.Array.Sort(rows, (x, y) => {
                int c = nName.Dict(x.name).SequenceCompareTo(nName.Dict(y.name));
                return c != 0 ? c : y.year.CompareTo(x.year);
            });
            foreach (T9Row r in rows) {
                Emit(nName.Dict(r.name)); Emit("|"u8); Emit(r.year); Emit("|"u8); Emit(r.sum); Emit("\n"u8);
            }
        }
    }

    // ================================================================================================ T18 (TPC-H Q18)
    struct KQ { public int key, qty; }
    struct T18Row { public long okey, cust, date, price, sum; public ulong namePos; public int nameLen; }

    static class T18 {
        static Col lOrderkey, lQty, oOrderkey, oCustkey, oOrderdate, oTotalprice, cCustkey, cName;
        static readonly Counter ctr = new();
        static List* l1, l2, l3, l4;
        static Map big, cust;
        static Map* sums;
        static Bloom fbig, fcust;

        public static void Open() {
            lOrderkey = Olap.Open("lineitem", "l_orderkey"); lQty = Olap.Open("lineitem", "l_quantity");
            oOrderkey = Olap.Open("orders", "o_orderkey"); oCustkey = Olap.Open("orders", "o_custkey");
            oOrderdate = Olap.Open("orders", "o_orderdate"); oTotalprice = Olap.Open("orders", "o_totalprice");
            cCustkey = Olap.Open("customer", "c_custkey"); cName = Olap.Open("customer", "c_name");
            List* l = (List*)HugeAlloc((nuint)(4 * MAXT * sizeof(List)));
            l1 = l; l2 = l + MAXT; l3 = l + 2 * MAXT; l4 = l + 3 * MAXT;
            sums = (Map*)HugeAlloc((nuint)(MAXT * sizeof(Map)));
        }
        static void ScatterTask(int tid) {  // lineitem réparti par commande
            Scratch* s = scratch[tid];
            Parts* p = parts + tid;
            p->Init(arena + tid, (uint)sizeof(KQ));
            for (long b; (b = ctr.Take()) >= 0;)
                for (int st = 0, count = (int)lOrderkey.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(lOrderkey, b, st, n, s->a);
                    Unpack(lQty, b, st, n, s->b);
                    HashKeys(s->a, n, s->h);
                    for (int i = 0; i < n; i++) {
                        KQ* t = (KQ*)p->Push(PartOf(s->h[i]));
                        t->key = s->a[i]; t->qty = s->b[i];
                    }
                }
            p->Close();
        }
        static void AggTask(int tid) {  // une partition : somme par commande ; garde celles de plus de 300 unités
            Arena* a = arena + tid;
            l1[tid].Init(a);
            for (long k; (k = ctr.Take()) >= 0;) {
                Map m = default;
                m.Init(a, Pow2Start(PartsCount(parts, NT, k)));
                for (int th = 0; th < NT; th++)
                    for (PChunk* c = parts[th].head[k]; c != null; c = c->next)
                        for (KQ* t = (KQ*)(c + 1), end = (KQ*)((byte*)(c + 1) + c->used); t < end; t++) {
#if SPECIAL
                            if (t + AHEAD < end) Prefetch(m.cells + (Hash64((ulong)t[AHEAD].key) & m.mask));
#endif
                            m.Upsert(t->key)->val += t->qty;
                        }
                for (ulong j = 0; j <= m.mask; j++)
                    if (m.cells[j].key != -1 && m.cells[j].val > 30000) l1[tid].Push(m.cells[j].key);
            }
        }
        static void OrdersTask(int tid) {  // commandes retenues : client, date, prix
            Scratch* s = scratch[tid];
            l1[tid].Init(arena + tid); l2[tid].Init(arena + tid); l3[tid].Init(arena + tid); l4[tid].Init(arena + tid);
            for (long b; (b = ctr.Take()) >= 0;)
                for (int st = 0, count = (int)oOrderkey.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(oOrderkey, b, st, n, s->a);
                    int k = Semi(big, fbig, s->a, n, st, s->pos, s->b);
                    if (k == 0) continue;
                    UnpackSel(oCustkey, b, s->pos, k, s->c);
                    UnpackSel(oOrderdate, b, s->pos, k, s->d);
                    UnpackSel(oTotalprice, b, s->pos, k, s->e);
                    for (int i = 0; i < k; i++) {
                        l1[tid].Push(s->b[i]); l2[tid].Push(s->c[i]); l3[tid].Push(s->d[i]); l4[tid].Push(s->e[i]);
                    }
                }
        }
        static void CustTask(int tid) {  // clients de ces commandes : position et longueur de leur nom
            Scratch* s = scratch[tid];
            l1[tid].Init(arena + tid); l2[tid].Init(arena + tid); l3[tid].Init(arena + tid);
            for (long b; (b = ctr.Take()) >= 0;) {
                ulong pos = cName.dir[b].auxOff;
                for (int st = 0, count = (int)cCustkey.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(cCustkey, b, st, n, s->a);
                    Unpack(cName, b, st, n, s->b);
                    for (int i = 0; i < n; i++) {
                        ulong h = Hash64((ulong)s->a[i]);
                        if (fcust.Test(h) && cust.Find(s->a[i], h) != null) {
                            l1[tid].Push(s->a[i]); l2[tid].Push((long)pos); l3[tid].Push(s->b[i]);
                        }
                        pos += (ulong)s->b[i];
                    }
                }
            }
        }
        static void SumTask(int tid) {  // lineitem des commandes retenues : somme des quantités
            Scratch* s = scratch[tid];
            Map m = default;
            m.Init(arena + tid, 1024);
            for (long b; (b = ctr.Take()) >= 0;)
                for (int st = 0, count = (int)lOrderkey.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(lOrderkey, b, st, n, s->a);
                    int k = Semi(big, fbig, s->a, n, st, s->pos, s->b);
                    if (k == 0) continue;
                    UnpackSel(lQty, b, s->pos, k, s->c);
                    for (int i = 0; i < k; i++) m.Upsert(s->b[i])->val += s->c[i];
                }
            sums[tid] = m;
        }
        public static void Run() {
            Arena* a0 = arena;
            // 1. et 2. agrégation de lineitem par commande ; 3. commandes de plus de 300 unités
            ctr.Set(lOrderkey.nblocks);
            pool.Run(ScatterTask);
            ctr.Set(NPART);
            pool.Run(AggTask);
            ulong n = 0;
            for (int t = 0; t < NT; t++) n += l1[t].n;
            big.Init(a0, Pow2For(n));
            fbig.Init(a0, n);
            for (int t = 0; t < NT; t++)
                for (ulong i = 0; i < l1[t].n; i++) {
                    big.Upsert(l1[t].v[i]);
                    fbig.Add(Hash64((ulong)l1[t].v[i]));
                }
            // 4. leurs lignes dans orders
            ctr.Set(oOrderkey.nblocks);
            pool.Run(OrdersTask);
            var rows = new T18Row[n];
            int nr = 0;
            cust.Init(a0, Pow2For(n));
            fcust.Init(a0, n);
            for (int t = 0; t < NT; t++)
                for (ulong i = 0; i < l1[t].n; i++) {
                    rows[nr++] = new T18Row { okey = l1[t].v[i], cust = l2[t].v[i], date = l3[t].v[i], price = l4[t].v[i] };
                    cust.Upsert(l2[t].v[i]);
                    fcust.Add(Hash64((ulong)l2[t].v[i]));
                }
            // 5. leurs clients ; 6. leurs lignes dans lineitem
            ctr.Set(cCustkey.nblocks);
            pool.Run(CustTask);
            Map name = default;  // client -> rang dans les listes
            name.Init(a0, Pow2For(n));
            List pos = default, len = default;
            pos.Init(a0); len.Init(a0);
            for (int t = 0; t < NT; t++)
                for (ulong i = 0; i < l1[t].n; i++) {
                    name.Upsert(l1[t].v[i])->val = (long)pos.n;
                    pos.Push(l2[t].v[i]); len.Push(l3[t].v[i]);
                }
            ctr.Set(lOrderkey.nblocks);
            pool.Run(SumTask);
            for (int i = 0; i < nr; i++) {
                for (int t = 0; t < NT; t++) {
                    Cell* c = sums[t].Find(rows[i].okey);
                    if (c != null) rows[i].sum += c->val;
                }
                long j = name.Find(rows[i].cust)->val;
                rows[i].namePos = (ulong)pos.v[j];
                rows[i].nameLen = (int)len.v[j];
            }
            System.Array.Sort(rows, 0, nr, System.Collections.Generic.Comparer<T18Row>.Create((x, y) => {  // prix décroissant, date, commande
                if (x.price != y.price) return y.price.CompareTo(x.price);
                if (x.date != y.date) return x.date.CompareTo(y.date);
                return x.okey.CompareTo(y.okey);
            }));
            for (int i = 0; i < nr && i < 100; i++) {
                ref T18Row r = ref rows[i];
                Emit(new ReadOnlySpan<byte>(cName.aux + r.namePos, r.nameLen));
                Emit("|"u8); Emit(r.cust); Emit("|"u8); Emit(r.okey); Emit("|"u8); Emit(r.date); Emit("|"u8); Emit(r.price);
                Emit("|"u8); Emit(r.sum); Emit("\n"u8);
            }
        }
    }

    // ================================================================================================ C4
    static class C4 {
        static Col uid;
        static readonly Counter ctr = new();
        static readonly ulong[] count = new ulong[MAXT * 8];
        static readonly int[] minus1 = new int[MAXT * 16];

        public static void Open() { uid = Olap.Open("hits", "UserID"); }
        static void ScatterTask(int tid) {
            Scratch* s = scratch[tid];
            Parts* p = parts + tid;
            p->Init(arena + tid, 8);
            for (long b; (b = ctr.Take()) >= 0;) {
                long* v = (long*)uid.Words(b);  // 64 bits : valeurs telles quelles
                for (int st = 0, cnt = (int)uid.dir[b].count; st < cnt; st += VEC) {
                    int n = Math.Min(cnt - st, VEC);
                    HashLongs(v + st, n, s->h);
                    for (int i = 0; i < n; i++) *(long*)p->Push(PartOf(s->h[i])) = v[st + i];
                }
            }
            p->Close();
        }
        static void CountTask(int tid) {
            ulong total = 0;
            int seen = 0;
            for (long k; (k = ctr.Take()) >= 0;) {
                Map m = default;
                m.Init(arena + tid, Pow2Start(PartsCount(parts, NT, k)));
                for (int th = 0; th < NT; th++)
                    for (PChunk* c = parts[th].head[k]; c != null; c = c->next)
                        for (long* t = (long*)(c + 1), end = (long*)((byte*)(c + 1) + c->used); t < end; t++) {
#if SPECIAL
                            if (t + AHEAD < end) Prefetch(m.cells + (Hash64((ulong)t[AHEAD]) & m.mask));
#endif
                            if (*t == -1) seen = 1;  // la valeur qui marque les cases vides est comptée à part
                            else m.Upsert(*t);
                        }
                total += m.count;
            }
            count[tid * 8] = total;
            minus1[tid * 16] = seen;
        }
        public static void Run() {
            ctr.Set(uid.nblocks);
            pool.Run(ScatterTask);
            ctr.Set(NPART);
            pool.Run(CountTask);
            ulong total = 0;
            int seen = 0;
            for (int t = 0; t < NT; t++) { total += count[t * 8]; seen |= minus1[t * 16]; }
            Emit(total + (ulong)seen); Emit("\n"u8);
        }
    }

    // ================================================================================================ agrégations par chaîne
    // C12, C16, C33, C36 : les lignes retenues sont hachées, réparties, puis agrégées partition par partition ; chaque
    // fil garde ses dix premiers groupes.
    struct STuple { public ulong hash; public long ikey; public ulong pos; public uint len, pad; }

    static class CS {
        static Col str, uid, counter, date, dch, refresh;
        static readonly Counter ctr = new();
        static int mode;  // 12, 16, 33, 36
        static int lo, hi;
        static Top10* top;

        public static void Open(int m) {
            mode = m;
            str = Olap.Open("hits", mode == 12 || mode == 16 ? "SearchPhrase" : "URL");
            if (mode == 16) uid = Olap.Open("hits", "UserID");
            if (mode == 36) {
                counter = Olap.Open("hits", "CounterID"); date = Olap.Open("hits", "EventDate");
                dch = Olap.Open("hits", "DontCountHits"); refresh = Olap.Open("hits", "IsRefresh");
                lo = DaysFromCivil(2013, 7, 1); hi = DaysFromCivil(2013, 7, 31);
            }
            top = (Top10*)HugeAlloc((nuint)(MAXT * sizeof(Top10)));
        }
        static void ScatterTask(int tid) {
            Scratch* s = scratch[tid];
            Parts* p = parts + tid;
            p->Init(arena + tid, (uint)sizeof(STuple));
            byte* bytes = str.aux;
            for (long b; (b = ctr.Take()) >= 0;) {
                if (mode == 36) {  // cartes de zones : compteur et date
                    Entry* ec = counter.dir + b, ed = date.dir + b;
                    if (ec->min > 62 || ec->max < 62 || ed->max < lo || ed->min > hi) continue;
                }
                long* u = mode == 16 ? (long*)uid.Words(b) : null;
                ulong pos = str.dir[b].auxOff;
                for (int st = 0, count = (int)str.dir[b].count; st < count; st += VEC) {
                    int n = Math.Min(count - st, VEC);
                    Unpack(str, b, st, n, s->a);  // longueurs
                    for (int i = 0; i < n; i++) { s->x[i] = (long)pos; pos += (ulong)s->a[i]; }
                    int k;
                    if (mode == 36) {
                        Unpack(counter, b, st, n, s->b);
                        k = SelBetween(s->b, n, 62, 62, (uint)st, s->pos);
                        if (k == 0) continue;
                        UnpackSel(date, b, s->pos, k, s->c);
                        UnpackSel(dch, b, s->pos, k, s->d);
                        UnpackSel(refresh, b, s->pos, k, s->e);
                        int k2 = 0;
                        for (int i = 0; i < k; i++) {
                            int j = s->pos[i] - st;
                            s->sel[k2] = j;
                            if (s->c[i] >= lo && s->c[i] <= hi && s->d[i] == 0 && s->e[i] == 0 && s->a[j] > 0) k2++;
                        }
                        k = k2;
                    } else if (mode == 12) {
                        k = SelBetween(s->a, n, 1, int.MaxValue, 0, s->sel);
                    } else {
                        for (int i = 0; i < n; i++) s->sel[i] = i;
                        k = n;
                    }
                    for (int j = 0; j < k; j++) {
                        int i = s->sel[j];
                        s->h[j] = HashBytes(bytes + s->x[i], (uint)s->a[i]);
                    }
                    if (u != null)
                        for (int j = 0; j < k; j++) {
                            ulong h = Hash64(s->h[j] ^ ((ulong)u[st + s->sel[j]] * K2));
                            s->h[j] = h != 0 ? h : 1;
                        }
                    for (int j = 0; j < k; j++) {
                        int i = s->sel[j];
                        STuple* t = (STuple*)p->Push(PartOf(s->h[j]));
                        t->hash = s->h[j]; t->ikey = u != null ? u[st + i] : 0; t->pos = (ulong)s->x[i]; t->len = (uint)s->a[i];
                    }
                }
            }
            p->Close();
        }
        static void AggTask(int tid) {
            Top10 best = default;
            for (long k; (k = ctr.Take()) >= 0;) {
                SMap m = default;
                m.Init(arena + tid, Pow2Start(PartsCount(parts, NT, k)), str.aux);
                for (int th = 0; th < NT; th++)
                    for (PChunk* c = parts[th].head[k]; c != null; c = c->next)
                        for (STuple* t = (STuple*)(c + 1), end = (STuple*)((byte*)(c + 1) + c->used); t < end; t++) {
#if SPECIAL
                            if (t + AHEAD < end) {  // à AHEAD tuples : la case et les octets du tuple ; à mi-distance : les octets de la case
                                Prefetch(m.cells + (t[AHEAD].hash & m.mask));
                                Prefetch(m.bytes + t[AHEAD].pos);
                                SCell* near = m.cells + (t[AHEAD / 2].hash & m.mask);
                                if (near->hash == t[AHEAD / 2].hash) Prefetch(m.bytes + near->pos);
                            }
#endif
                            m.Add(t->hash, t->ikey, t->pos, t->len);
                        }
                for (ulong j = 0; j <= m.mask; j++)
                    if (m.cells[j].hash != 0)
                        best.Add(new Top { count = m.cells[j].count, len = m.cells[j].len, ikey = m.cells[j].ikey, pos = m.cells[j].pos }, str.aux);
            }
            top[tid] = best;
        }
        public static void Run() {
            ctr.Set(str.nblocks);
            pool.Run(ScatterTask);
            ctr.Set(NPART);
            pool.Run(AggTask);
            Top10 all = default;
            for (int t = 0; t < NT; t++)
                for (int i = 0; i < top[t].n; i++) all.Add(top[t].Get(i), str.aux);
            for (int i = 0; i < all.n; i++) {
                Top x = all.Get(i);
                if (mode == 16) { Emit(x.ikey); Emit("|"u8); }
                Emit(new ReadOnlySpan<byte>(str.aux + x.pos, (int)x.len)); Emit("|"u8); Emit((ulong)x.count); Emit("\n"u8);
            }
        }
    }

    // ================================================================================================ C20
    static class C20 {
        static Col url;
        static readonly Counter ctr = new();
        static readonly ulong[] count = new ulong[MAXT * 8];

        public static void Open() { url = Olap.Open("hits", "URL"); }
        static void Task(int tid) {
            Scratch* s = scratch[tid];
            ulong total = 0;
            for (long b; (b = ctr.Take()) >= 0;) {
                ulong nbytes = BlockLengths(url, b, s->len);
                total += (ulong)SearchBlock(url.aux + url.dir[b].auxOff, nbytes, s->len, "google"u8, s->rows);
            }
            count[tid * 8] = total;
        }
        public static void Run() {
            ctr.Set(url.nblocks);
            pool.Run(Task);
            ulong total = 0;
            for (int t = 0; t < NT; t++) total += count[t * 8];
            Emit(total); Emit("\n"u8);
        }
    }

    // ================================================================================================ principal
    static int Main(string[] args) {
        if (args.Length < 4) Die("usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]");
        string q = args[0];
        NT = int.Parse(args[1], CultureInfo.InvariantCulture);
        int reps = int.Parse(args[2], CultureInfo.InvariantCulture);
        dataDir = args[3];
        bool print = args.Length > 4 && args[4] == "--print";
        if (NT < 1 || NT > MAXT) Die("nombre de fils");
        arena = (Arena*)HugeAlloc((nuint)(MAXT * sizeof(Arena)));
        new Span<Arena>(arena, MAXT).Clear();
        scratch = (Scratch**)HugeAlloc((nuint)(MAXT * sizeof(Scratch*)));
        parts = (Parts*)HugeAlloc((nuint)(MAXT * sizeof(Parts)));
        parts2 = (Parts*)HugeAlloc((nuint)(MAXT * sizeof(Parts)));
        for (int t = 0; t < NT; t++) {
            scratch[t] = (Scratch*)HugeAlloc((nuint)sizeof(Scratch));
            parts[t].Create();
            parts2[t].Create();
        }
        Action run;
        switch (q) {
            case "t1": T1.Open(); run = T1.Run; break;
            case "t6": T6.Open(); run = T6.Run; break;
            case "t9": T9.Open(); run = T9.Run; break;
            case "t18": T18.Open(); run = T18.Run; break;
            case "c4": C4.Open(); run = C4.Run; break;
            case "c12": case "c16": case "c33": case "c36": CS.Open(int.Parse(q.AsSpan(1), CultureInfo.InvariantCulture)); run = CS.Run; break;
            case "c20": C20.Open(); run = C20.Run; break;
            default: Die("requête inconnue"); return 2;
        }
        pool.Start(NT);
        using var stdout = Console.OpenStandardOutput();
        for (int r = 0; r < reps; r++) {
            for (int t = 0; t < NT; t++) arena[t].Reset();
            resLen = 0;
            long t0 = Stopwatch.GetTimestamp();
            run();
            double dt = Stopwatch.GetElapsedTime(t0).TotalSeconds;
            string line = string.Create(CultureInfo.InvariantCulture, $"RESULT;{q};{Level};{NT};{r};{dt:F6};{Fnv1a(res.AsSpan(0, resLen)):x16}\n");
            stdout.Write(System.Text.Encoding.ASCII.GetBytes(line));
            if (print && r == reps - 1) stdout.Write(res, 0, resLen);
            stdout.Flush();
        }
        return 0;
    }
}
