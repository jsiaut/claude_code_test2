// v7 (docs/V7.md ; olap/SPEC.md) : le banc OLAP en Java. Même architecture que la référence (olap/c/olap.c), écrite
// avec les moyens du langage : mémoire hors tas (API FFM de java.lang.foreign) pour les colonnes, les arènes, les
// tables et les tampons de partition, lue par adresses brutes ; vecteurs de travail en tableaux du tas ; fils
// persistants (moniteur, wait et notifyAll). Les primitives qui ont deux niveaux sont dans la classe Level, compilée
// depuis Portable.java ou depuis Special.java.
//
// Usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]
import static java.lang.foreign.ValueLayout.ADDRESS;
import static java.lang.foreign.ValueLayout.JAVA_BYTE;
import static java.lang.foreign.ValueLayout.JAVA_INT;
import static java.lang.foreign.ValueLayout.JAVA_INT_UNALIGNED;
import static java.lang.foreign.ValueLayout.JAVA_LONG;
import static java.lang.foreign.ValueLayout.JAVA_LONG_UNALIGNED;

import java.io.IOException;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.invoke.MethodHandle;
import java.nio.channels.FileChannel;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Arrays;
import java.util.concurrent.atomic.AtomicLong;

public final class Olap {
    static final int PBITS = 10;          // bits de partition
    static final int VEC = 2048;          // lignes d'un vecteur
    static final int CHUNK = 16384;       // octets utiles d'un morceau de tampon de partition
    static final int BLOCK = 65536;       // lignes d'un bloc : un morceau
    static final int NPART = 1 << PBITS;  // partitions des grandes tables
    static final int MAXT = 64;           // fils au plus
    static final long ARENA_BLOCK = 32L << 20, HUGE_PAGE = 1L << 21;
    static final long K1 = 0x9E3779B97F4A7C15L, K2 = 0xC2B2AE3D27D4EB4FL;

    static void die(String msg) {
        System.err.println("olap : " + msg);
        System.exit(2);
    }

    // ------------------------------------------------------------------------------------------------ mémoire brute
    // Un segment qui couvre tout l'espace d'adressage : les adresses sont des long, lus et écrits sans autre borne.
    static final MemorySegment MEM = MemorySegment.NULL.reinterpret(Long.MAX_VALUE);

    static long getLong(long a) { return MEM.get(JAVA_LONG_UNALIGNED, a); }
    static int getInt(long a) { return MEM.get(JAVA_INT_UNALIGNED, a); }
    static byte getByte(long a) { return MEM.get(JAVA_BYTE, a); }
    static void putLong(long a, long v) { MEM.set(JAVA_LONG_UNALIGNED, a, v); }
    static void putInt(long a, int v) { MEM.set(JAVA_INT_UNALIGNED, a, v); }
    static void fill(long a, long n, byte v) { MEM.asSlice(a, n).fill(v); }
    static boolean same(long a, long b, long n) { return MemorySegment.mismatch(MEM, a, a + n, MEM, b, b + n) < 0; }
    /** Ordre des chaînes d'octets, comme memcmp puis la longueur. */
    static int compare(long a, long na, long b, long nb) {
        final long n = Math.min(na, nb), d = MemorySegment.mismatch(MEM, a, a + n, MEM, b, b + n);
        return d < 0 ? Long.compare(na, nb) : Integer.compare(getByte(a + d) & 0xFF, getByte(b + d) & 0xFF);
    }

    // Toute la mémoire hors tas vient du système par zones alignées sur 2 Mio et signalées comme pages larges.
    static final MethodHandle ALIGNED_ALLOC, MADVISE;
    static {
        final Linker linker = Linker.nativeLinker();
        ALIGNED_ALLOC = linker.downcallHandle(linker.defaultLookup().find("aligned_alloc").orElseThrow(),
                FunctionDescriptor.of(ADDRESS, JAVA_LONG, JAVA_LONG));
        MADVISE = linker.downcallHandle(linker.defaultLookup().find("madvise").orElseThrow(),
                FunctionDescriptor.of(JAVA_INT, ADDRESS, JAVA_LONG, JAVA_INT));
    }
    static long hugeAlloc(long n) {
        n = (n + HUGE_PAGE - 1) & -HUGE_PAGE;
        try {
            final MemorySegment p = (MemorySegment) ALIGNED_ALLOC.invokeExact(HUGE_PAGE, n);
            if (p.address() == 0) die("mémoire");
            final int unused = (int) MADVISE.invokeExact(p, n, 14);  // MADV_HUGEPAGE
            return p.address();
        } catch (Throwable t) {
            throw new IllegalStateException(t);
        }
    }

    // ------------------------------------------------------------------------------------------------ arènes
    // Une arène par fil : allocation par déplacement d'un pointeur, remise à zéro à chaque exécution ; la mémoire est
    // gardée d'une répétition à l'autre. En-tête d'un bloc (64 octets) : suivant, capacité, octets pris.
    static final long[] arenaFirst = new long[MAXT], arenaCur = new long[MAXT];

    static long alloc(int tid, long n) {
        n = (n + 63) & -64;
        for (;;) {
            final long b = arenaCur[tid];
            if (b != 0 && getLong(b + 16) + n <= getLong(b + 8)) {
                final long used = getLong(b + 16);
                putLong(b + 16, used + n);
                return b + 64 + used;
            }
            final long next = b != 0 ? getLong(b) : 0;
            if (next != 0 && getLong(next + 8) >= n) {
                arenaCur[tid] = next;
                putLong(next + 16, 0);
                continue;
            }
            final long cap = Math.max(n, ARENA_BLOCK - 64), nb = hugeAlloc(64 + cap);
            putLong(nb + 8, cap);
            putLong(nb + 16, 0);
            putLong(nb, next);
            if (b != 0) putLong(b, nb); else arenaFirst[tid] = nb;
            arenaCur[tid] = nb;
        }
    }
    static void arenaReset(int tid) {
        arenaCur[tid] = arenaFirst[tid];
        if (arenaCur[tid] != 0) putLong(arenaCur[tid] + 16, 0);
    }

    // ------------------------------------------------------------------------------------------------ fils persistants
    interface Task { void run(int tid); }

    /** Les fils sont créés une fois et attendent, bloqués, entre deux phases. */
    static final class Pool {
        int n = 1, pending;
        long generation;
        Task task;

        void start(int threads) {
            n = threads;
            for (int i = 1; i < n; i++) {
                final int tid = i;
                final Thread t = new Thread(() -> worker(tid));
                t.setDaemon(true);
                t.start();
            }
        }
        private void worker(int tid) {
            long seen = 0;
            try {
                for (;;) {
                    final Task t;
                    synchronized (this) {
                        while (generation == seen) wait();
                        seen = generation;
                        t = task;
                    }
                    t.run(tid);
                    synchronized (this) {
                        if (--pending == 0) notifyAll();
                    }
                }
            } catch (InterruptedException e) {
                throw new IllegalStateException(e);
            }
        }
        /** Exécute t sur tous les fils (le fil principal est le fil 0) et attend la fin de tous. */
        void run(Task t) {
            try {
                if (n > 1) synchronized (this) {
                    task = t;
                    pending = n - 1;
                    generation++;
                    notifyAll();
                }
                t.run(0);
                if (n > 1) synchronized (this) {
                    while (pending > 0) wait();
                }
            } catch (InterruptedException e) {
                throw new IllegalStateException(e);
            }
        }
    }
    static final Pool pool = new Pool();

    /** Compteur de morceaux partagé : la seule opération atomique. */
    static final class Counter {
        final AtomicLong next = new AtomicLong();
        long n;
        void set(long count) { next.set(0); n = count; }
        int take() {
            final long i = next.getAndIncrement();
            return i < n ? (int) i : -1;
        }
    }

    // ------------------------------------------------------------------------------------------------ colonnes
    // Entrée du répertoire d'un bloc (40 octets) : minimum, maximum, position des valeurs, position des octets,
    // largeur, lignes.
    static final class Col {
        long nrows, nblocks, auxCount, dir, data, aux;

        long entry(int b) { return dir + 40L * b; }
        long min(int b) { return getLong(entry(b)); }
        long max(int b) { return getLong(entry(b) + 8); }
        long words(int b) { return data + getLong(entry(b) + 16); }
        long auxOff(int b) { return getLong(entry(b) + 24); }
        int width(int b) { return getInt(entry(b) + 32); }
        int count(int b) { return getInt(entry(b) + 36); }
        /** Entrée d'un dictionnaire : son adresse ; sa longueur est dictLen. */
        long dict(int code) { return aux + 4 * (auxCount + 1) + (getInt(aux + 4L * code) & 0xFFFFFFFFL); }
        long dictLen(int code) { return (getInt(aux + 4L * code + 4) & 0xFFFFFFFFL) - (getInt(aux + 4L * code) & 0xFFFFFFFFL); }
    }
    static String dataDir;

    static Col open(String table, String name) {
        final Col c = new Col();
        try (FileChannel f = FileChannel.open(Path.of(dataDir, table, name + ".msc"), StandardOpenOption.READ)) {
            final long size = f.size();
            final long base = hugeAlloc(size + 64);  // la colonne est lue en entier, en pages larges, avec 64 octets de marge
            fill(base + size, 64, (byte) 0);
            for (long off = 0; off < size;) {
                final long n = Math.min(size - off, 1L << 30);
                final var buf = MEM.asSlice(base + off, n).asByteBuffer();
                while (buf.hasRemaining()) if (f.read(buf) <= 0) die("lecture");
                off += n;
            }
            if (getInt(base) != 0x3143534D) die("format");  // « MSC1 »
            if (getInt(base + 12) != BLOCK) die("taille de bloc");
            c.nrows = getLong(base + 16);
            c.nblocks = getLong(base + 24);
            c.dir = base + getLong(base + 32);
            c.data = base + getLong(base + 40);
            c.aux = base + getLong(base + 48);
            c.auxCount = getLong(base + 56);
        } catch (IOException e) {
            die(e.toString());
        }
        return c;
    }

    // ------------------------------------------------------------------------------------------------ décodage
    /** Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 64. */
    static void unpack(Col c, int b, int start, int n, int[] out) {
        final int w = c.width(b), base = (int) c.min(b);
        if (w == 0) {
            Arrays.fill(out, 0, n, base);
            return;
        }
        Level.unpack(c.words(b) + (long) (start / 64) * w * 8, out, n, base, w);
    }
    /** Décode les valeurs du bloc b aux positions pos (lignes dans le bloc), dans l'ordre : out[i] est celle de pos[i]. */
    static void unpackSel(Col c, int b, int[] pos, int from, int n, int[] out) {
        final int w = c.width(b), base = (int) c.min(b);
        if (w == 0) {
            Arrays.fill(out, 0, n, base);
            return;
        }
        final long in = c.words(b), mask = (1L << w) - 1;
        for (int i = 0; i < n; i++) {
            final long bit = (long) pos[from + i] * w, a = in + (bit >>> 6 << 3);
            final int sh = (int) bit & 63;
            out[i] = (int) (((getLong(a) >>> sh) | (getLong(a + 8) << 1 << (63 - sh))) & mask) + base;
        }
    }

    // ------------------------------------------------------------------------------------------------ hachage
    static long hash64(long k) {
        k *= K1;
        return k ^ (k >>> 32);
    }
    /** Octets : deux voies de mots de 64 bits ; le dernier mot, incomplet, est masqué (8 octets lisibles après la fin). */
    static long hashBytes(long p, long n) {
        long h1 = K1 ^ n, h2 = K2;
        for (; n >= 16; n -= 16, p += 16) {
            h1 = (Long.rotateLeft(h1, 5) ^ getLong(p)) * K1;
            h2 = (Long.rotateLeft(h2, 5) ^ getLong(p + 8)) * K2;
        }
        if (n >= 8) {
            h1 = (Long.rotateLeft(h1, 5) ^ getLong(p)) * K1;
            p += 8;
            n -= 8;
        }
        if (n > 0) h2 = (Long.rotateLeft(h2, 5) ^ (getLong(p) & ((1L << (8 * n)) - 1))) * K2;
        long h = (h1 ^ Long.rotateLeft(h2, 32)) * K1;
        h ^= h >>> 32;
        return h != 0 ? h : 1;  // 0 marque une case vide
    }
    static int partOf(long h) { return (int) (h >>> (64 - PBITS)); }

    // ------------------------------------------------------------------------------------------------ table de hachage
    // Adressage ouvert, sondage linéaire, capacité en puissance de deux, clé et valeur dans la même case de 16 octets
    // (clé, valeur) ; doublement quand la table est à moitié pleine. Clés positives ou nulles ; -1 : case vide.
    static long pow2For(long n) {  // capacité pour n clés : au moins le double, 16 au moins
        long cap = 16;
        while (cap < 2 * n) cap *= 2;
        return cap;
    }
    /** Capacité de départ d'une table d'agrégation qui recevra n tuples ; elle double ensuite à la demande. */
    static long pow2Start(long n) { return pow2For(n / 8); }

    static final class Map {
        long cells, mask, count;
        boolean fresh;  // dit si le dernier upsert a créé la case
        final int tid;

        Map(int tid) { this.tid = tid; }
        Map(int tid, long cap) { this.tid = tid; init(cap); }
        void init(long cap) {
            mask = cap - 1;
            count = 0;
            cells = alloc(tid, cap * 16);
            fill(cells, cap * 16, (byte) 0xFF);
        }
        /** Adresse de la case de la clé, dont h est le hash64 ; 0 si elle manque. */
        long find(long key, long h) {
            for (long i = h & mask;; i = (i + 1) & mask) {
                final long c = cells + (i << 4), k = getLong(c);
                if (k == key) return c;
                if (k == -1) return 0;
            }
        }
        long find(long key) { return find(key, hash64(key)); }
        void grow() {
            final long old = cells, oldMask = mask, n = count;
            init(2 * (oldMask + 1));
            for (long j = 0; j <= oldMask; j++) {
                final long key = getLong(old + (j << 4));
                if (key != -1) {
                    long i = hash64(key) & mask;
                    while (getLong(cells + (i << 4)) != -1) i = (i + 1) & mask;
                    putLong(cells + (i << 4), key);
                    putLong(cells + (i << 4) + 8, getLong(old + (j << 4) + 8));
                }
            }
            count = n;
        }
        /** Adresse de la case de la clé, créée avec la valeur 0 si elle manquait (fresh le dit). */
        long upsert(long key) {
            if ((count + 1) * 2 > mask + 1) grow();
            for (long i = hash64(key) & mask;; i = (i + 1) & mask) {
                final long c = cells + (i << 4), k = getLong(c);
                if (k == key) { fresh = false; return c; }
                if (k == -1) {
                    putLong(c, key);
                    putLong(c + 8, 0);
                    count++;
                    fresh = true;
                    return c;
                }
            }
        }
        void add(long key, long v) {
            final long c = upsert(key) + 8;
            putLong(c, getLong(c) + v);
        }
        void set(long key, long v) { putLong(upsert(key) + 8, v); }
        long get(long key) { return getLong(find(key) + 8); }
    }

    /** Filtre de Bloom par blocs, devant les sondes de semi-jointure : 16 bits par clé, deux bits dans un même mot. */
    static final class Bloom {
        final long bits, mask;
        Bloom(int tid, long nkeys) {
            long words = 64;
            while (words * 4 < nkeys) words *= 2;
            bits = alloc(tid, words * 8);
            fill(bits, words * 8, (byte) 0);
            mask = words - 1;
        }
        static long two(long h) { return 1L << (h & 63) | 1L << ((h >>> 6) & 63); }
        void add(long h) {
            final long a = bits + (((h >>> 12) & mask) << 3);
            putLong(a, getLong(a) | two(h));
        }
        boolean test(long h) {
            final long m = two(h);
            return (getLong(bits + (((h >>> 12) & mask) << 3)) & m) == m;
        }
    }

    // Même table pour des clés faites d'un entier et d'une chaîne. Case de 32 octets : hachage, entier, position de
    // la chaîne, longueur (32 bits), compte (32 bits). Hachage nul : case vide.
    static final class SMap {
        long cells, mask, n;
        final int tid;
        final long bytes;

        SMap(int tid, long bytes) { this.tid = tid; this.bytes = bytes; }
        void init(long cap) {
            mask = cap - 1;
            n = 0;
            cells = alloc(tid, cap * 32);
            fill(cells, cap * 32, (byte) 0);
        }
        void grow() {
            final long old = cells, oldMask = mask, count = n;
            init(2 * (oldMask + 1));
            for (long j = 0; j <= oldMask; j++) {
                final long o = old + (j << 5), hash = getLong(o);
                if (hash != 0) {
                    long i = hash & mask;
                    while (getLong(cells + (i << 5)) != 0) i = (i + 1) & mask;
                    MemorySegment.copy(MEM, o, MEM, cells + (i << 5), 32);
                }
            }
            n = count;
        }
        void add(long hash, long ikey, long pos, int len) {
            if ((n + 1) * 2 > mask + 1) grow();
            for (long i = hash & mask;; i = (i + 1) & mask) {
                final long c = cells + (i << 5), h = getLong(c);
                if (h == hash && getLong(c + 8) == ikey && getInt(c + 24) == len && same(bytes + getLong(c + 16), bytes + pos, len)) {
                    putInt(c + 28, getInt(c + 28) + 1);
                    return;
                }
                if (h == 0) {
                    putLong(c, hash);
                    putLong(c + 8, ikey);
                    putLong(c + 16, pos);
                    putInt(c + 24, len);
                    putInt(c + 28, 1);
                    n++;
                    return;
                }
            }
        }
    }

    // ------------------------------------------------------------------------------------------------ partitions
    // Tampons d'un fil : pour chaque partition, une liste de morceaux de CHUNK octets pris dans son arène. Morceau :
    // en-tête de 64 octets (suivant, octets pris sur 32 bits), puis les tuples. Le langage n'a pas d'écriture non
    // temporelle : la répartition est la même aux deux niveaux.
    static final class Parts {
        final long cur = hugeAlloc(4L * 8 * NPART), end = cur + 8L * NPART, head = end + 8L * NPART, tail = head + 8L * NPART;
        long tsize;
        final int tid;

        Parts(int tid) { this.tid = tid; }
        void init(long tupleSize) {
            fill(cur, 4L * 8 * NPART, (byte) 0);
            tsize = tupleSize;
        }
        long head(int k) { return getLong(head + ((long) k << 3)); }
        private long chunk(long k8) {
            final long c = alloc(tid, 64 + CHUNK), t = getLong(tail + k8);
            putLong(c, 0);
            putInt(c + 8, 0);
            if (t != 0) {
                putInt(t + 8, (int) (getLong(cur + k8) - t - 64));
                putLong(t, c);
            } else {
                putLong(head + k8, c);
            }
            putLong(tail + k8, c);
            putLong(end + k8, c + 64 + CHUNK / tsize * tsize);
            return c + 64;
        }
        /** Adresse du prochain tuple de la partition k. */
        long push(int k) {
            final long k8 = (long) k << 3;
            long t = getLong(cur + k8);
            if (t == getLong(end + k8)) t = chunk(k8);
            putLong(cur + k8, t + tsize);
            return t;
        }
        void close() {
            for (long k8 = 0; k8 < 8L * NPART; k8 += 8) {
                final long t = getLong(tail + k8);
                if (t != 0) putInt(t + 8, (int) (getLong(cur + k8) - t - 64));
            }
        }
    }
    static long partsCount(Parts[] ps, int k) {
        long n = 0;
        for (Parts p : ps)
            for (long c = p.head(k); c != 0; c = getLong(c)) n += getInt(c + 8) / p.tsize;
        return n;
    }

    // ------------------------------------------------------------------------------------------------ état des fils
    /** Vecteurs de travail d'un fil. Ceux de 32 bits ont 16 cases de marge pour les pas entiers du niveau spécialisé. */
    static final class Scratch {
        final int[] a = new int[VEC + 16], b = new int[VEC + 16], c = new int[VEC + 16], d = new int[VEC + 16], e = new int[VEC + 16],
                f = new int[VEC + 16], g = new int[VEC + 16], sel = new int[VEC + 16], sel2 = new int[VEC + 16], pos = new int[VEC + 16];
        final long[] x = new long[VEC], y = new long[VEC], h = new long[VEC];
        final int[] len = new int[BLOCK + 16], rows = new int[BLOCK + 16];
        final LongList l1 = new LongList(), l2 = new LongList(), l3 = new LongList(), l4 = new LongList();
        final Map map;
        Scratch(int tid) { map = new Map(tid); }
    }
    static int NT;
    static Scratch[] scratch;
    static Parts[] parts, parts2;

    /** Liste d'entiers de 64 bits d'un fil ; son tableau est gardé d'une exécution à l'autre. */
    static final class LongList {
        long[] v = new long[1024];
        int n;
        void push(long x) {
            if (n == v.length) v = Arrays.copyOf(v, 2 * n);
            v[n++] = x;
        }
    }

    // ------------------------------------------------------------------------------------------------ résultat
    static byte[] res = new byte[1 << 16];
    static int resLen;

    static void room(long n) {
        if (resLen + n > res.length) res = Arrays.copyOf(res, (int) Math.max(2L * res.length, resLen + n));
    }
    static void emit(String s) {
        room(s.length());
        for (int i = 0; i < s.length(); i++) res[resLen++] = (byte) s.charAt(i);
    }
    static void emit(long v) { emit(Long.toString(v)); }
    static void emitBytes(long addr, long n) {
        room(n);
        MemorySegment.copy(MEM, JAVA_BYTE, addr, res, resLen, (int) n);
        resLen += (int) n;
    }
    static long fnv1a(byte[] s, int n) {
        long h = 0xCBF29CE484222325L;
        for (int i = 0; i < n; i++) h = (h ^ (s[i] & 0xFF)) * 0x100000001B3L;
        return h;
    }

    // ------------------------------------------------------------------------------------------------ dates
    static int daysFromCivil(int y, int m, int d) {  // jours depuis le 1er janvier 1970
        if (m <= 2) y--;
        final int era = Math.floorDiv(y, 400), yoe = y - era * 400;
        final int doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
        return era * 146097 + yoe * 365 + yoe / 4 - yoe / 100 + doy - 719468;
    }
    static final int[] YEAR_START = new int[200];  // premier jour de chaque année à partir de 1970
    static {
        for (int y = 0; y < 200; y++) YEAR_START[y] = daysFromCivil(1970 + y, 1, 1);
    }
    static int yearOf(int days) {
        int y = days / 366;
        while (YEAR_START[y + 1] <= days) y++;
        return 1970 + y;
    }

    // ------------------------------------------------------------------------------------------------ sous-chaînes
    // Lignes d'un bloc de chaînes qui contiennent l'aiguille (2 octets au moins) : les octets du bloc sont parcourus
    // d'un trait, par mots de 8 octets ; un mot est candidat si, à une même position, il porte le premier octet de
    // l'aiguille et le mot décalé de sa longueur moins un porte le dernier. Une occurrence compte si elle tient dans
    // une ligne, et une ligne compte une fois.
    static final long ONES = 0x0101010101010101L, HIGHS = 0x8080808080808080L;

    static long zeroBytes(long x) {  // bit de poids fort de chaque octet nul de x, exactement
        return ~(((x & ~HIGHS) + ~HIGHS) | x) & HIGHS;
    }
    static int searchBlock(long buf, long nbytes, int[] len, byte[] needle, int[] rows) {
        final int m = needle.length;
        int r = 0, k = 0;
        long rowEnd = nbytes > 0 ? len[0] : 0;
        final byte c0 = needle[0], c1 = needle[m - 1];
        final long first = ONES * (c0 & 0xFF), last = ONES * (c1 & 0xFF);
        final long stop = nbytes >= m ? nbytes - m + 1 : 0;  // positions de départ possibles : [0, stop)
        for (long i = 0; i < stop;) {
            long cand, next = i + 8;
            int shift = 3;  // un bit candidat par octet du mot : rang du bit / 8
            if (Level.SEARCH_STEP > 0 && i + Level.SEARCH_STEP + m - 1 <= nbytes) {
                // niveau spécialisé : 64 positions d'un coup, un bit candidat par position
                cand = Level.searchCandidates(buf + i, m, c0, c1);
                if (cand == 0) { i += Level.SEARCH_STEP; continue; }
                next = i + Level.SEARCH_STEP;
                shift = 0;
            } else if (i + 8 <= stop) {  // les deux mots sont dans le bloc
                cand = zeroBytes((getLong(buf + i) ^ first) | (getLong(buf + i + m - 1) ^ last));
                if (cand == 0) { i += 8; continue; }
            } else {
                cand = 0;
                for (long j = i; j < stop; j++)
                    if (getByte(buf + j) == c0 && getByte(buf + j + m - 1) == c1) cand |= 0x80L << (8 * (j - i));
            }
            candidates:
            for (; cand != 0; cand &= cand - 1) {
                final long at = i + (Long.numberOfTrailingZeros(cand) >>> shift);
                for (int j = 1; j < m - 1; j++) if (getByte(buf + at + j) != needle[j]) continue candidates;
                while (rowEnd <= at) rowEnd += len[++r];
                if (at + m <= rowEnd) {  // la suite de la ligne est sautée
                    rows[k++] = r;
                    next = rowEnd;
                    break;
                }
            }
            i = next;
        }
        return k;
    }
    /** Longueurs d'un bloc de chaînes (dans len) ; rend le nombre de ses octets. */
    static long blockLengths(Col c, int b, int[] len) {
        final int n = c.count(b);
        unpack(c, b, 0, n, len);
        long total = 0;
        for (int i = 0; i < n; i++) total += len[i];
        return total;
    }
    static final byte[] GREEN = "green".getBytes(), GOOGLE = "google".getBytes();

    // ------------------------------------------------------------------------------------------------ dix premiers
    static final class Top10 {
        final int[] count = new int[10], len = new int[10];
        final long[] ikey = new long[10], pos = new long[10];
        int n;
        final long bytes;
        Top10(long bytes) { this.bytes = bytes; }

        /** Ordre : compte décroissant, entier croissant, chaîne croissante. */
        boolean before(int c, long k, long p, int l, int i) {
            if (c != count[i]) return Integer.compareUnsigned(c, count[i]) > 0;
            if (k != ikey[i]) return k < ikey[i];
            return compare(bytes + p, l, bytes + pos[i], len[i]) < 0;
        }
        void add(int c, int l, long k, long p) {
            if (n == 10 && !before(c, k, p, l, 9)) return;
            int i = n < 10 ? n++ : 9;
            for (; i > 0 && before(c, k, p, l, i - 1); i--) {
                count[i] = count[i - 1];
                len[i] = len[i - 1];
                ikey[i] = ikey[i - 1];
                pos[i] = pos[i - 1];
            }
            count[i] = c;
            len[i] = l;
            ikey[i] = k;
            pos[i] = p;
        }
    }

    interface Query { void run(); }

    // ================================================================================================ T1 (TPC-H Q1)
    // Agrégat d'un groupe : quantité, prix, prix remisé, prix taxé, remise, compte ; six groupes par fil.
    static final class T1 implements Query {
        final Col ship = open("lineitem", "l_shipdate"), rf = open("lineitem", "l_returnflag"), ls = open("lineitem", "l_linestatus"),
                qty = open("lineitem", "l_quantity"), ext = open("lineitem", "l_extendedprice"), disc = open("lineitem", "l_discount"),
                tax = open("lineitem", "l_tax");
        final Counter ctr = new Counter();
        final int cut = daysFromCivil(1998, 9, 2);
        final long[][] agg = new long[MAXT][];

        void task(int tid) {
            final Scratch s = scratch[tid];
            final long[] local = new long[6 * 8];
            for (int b; (b = ctr.take()) >= 0;) {
                if (ship.min(b) > cut) continue;        // bloc exclu par sa carte de zones
                final boolean all = ship.max(b) <= cut;  // bloc retenu en entier : le filtre n'est pas évalué
                final int count = ship.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(rf, b, st, n, s.a);
                    unpack(ls, b, st, n, s.b);
                    unpack(qty, b, st, n, s.c);
                    unpack(ext, b, st, n, s.d);
                    unpack(disc, b, st, n, s.e);
                    unpack(tax, b, st, n, s.f);
                    final int[] a = s.a, bb = s.b, d = s.d, e = s.e, f = s.f, g = s.g;
                    final long[] x = s.x, y = s.y;
                    Level.t1Expr(d, e, f, a, bb, x, y, g, n);
                    if (!all) unpack(ship, b, st, n, s.pos);
                    Level.t1Aggregate(local, g, s.c, d, e, x, y, all ? null : s.pos, cut, n, s.sel);
                }
            }
            agg[tid] = local;
        }
        public void run() {
            ctr.set(ship.nblocks);
            pool.run(this::task);
            for (int g = 0; g < 6; g++) {
                final long[] a = new long[6];
                for (int t = 0; t < NT; t++)
                    for (int j = 0; j < 6; j++) a[j] += agg[t][8 * g + j];
                if (a[5] == 0) continue;
                emitBytes(rf.dict(g / 2), rf.dictLen(g / 2));
                emit("|");
                emitBytes(ls.dict(g % 2), ls.dictLen(g % 2));
                for (int j = 0; j < 6; j++) {
                    emit("|");
                    emit(a[j]);
                }
                emit("\n");
            }
        }
    }

    // ================================================================================================ T6 (TPC-H Q6)
    static final class T6 implements Query {
        final Col ship = open("lineitem", "l_shipdate"), disc = open("lineitem", "l_discount"), qty = open("lineitem", "l_quantity"),
                ext = open("lineitem", "l_extendedprice");
        final Counter ctr = new Counter();
        final int lo = daysFromCivil(1994, 1, 1), hi = daysFromCivil(1995, 1, 1);
        final long[] sum = new long[MAXT * 8];

        void task(int tid) {
            final Scratch s = scratch[tid];
            long total = 0;
            for (int b; (b = ctr.take()) >= 0;) {
                if (ship.max(b) < lo || ship.min(b) >= hi) continue;
                final int count = ship.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(ship, b, st, n, s.a);
                    final int k = Level.selBetween(s.a, n, lo, hi - 1, st, s.pos);
                    if (k == 0) continue;
                    unpackSel(disc, b, s.pos, 0, k, s.b);
                    final int k2 = Level.keepBetween(s.b, s.pos, s.b, k, 5, 7, s.sel, s.c);
                    if (k2 == 0) continue;
                    unpackSel(qty, b, s.sel, 0, k2, s.d);
                    final int k3 = Level.keepBetween(s.d, s.sel, s.c, k2, Integer.MIN_VALUE, 2399, s.sel2, s.e);
                    if (k3 == 0) continue;
                    unpackSel(ext, b, s.sel2, 0, k3, s.f);
                    final int[] price = s.f, d = s.e;
                    for (int i = 0; i < k3; i++) total += (long) price[i] * d[i];
                }
            }
            sum[tid * 8] = total;
        }
        public void run() {
            ctr.set(ship.nblocks);
            pool.run(this::task);
            long total = 0;
            for (int t = 0; t < NT; t++) total += sum[t * 8];
            emit(total);
            emit("\n");
        }
    }

    // ================================================================================================ T9 (TPC-H Q9)
    // 1. part : noms qui contiennent « green » -> ensemble de pièces (table et filtre de Bloom) ;
    // 2. partsupp : lignes de ces pièces -> (pièce, fournisseur) -> coût ; 3. supplier -> nation ;
    // 4. lineitem : lignes de ces pièces, montant et nation, réparties par commande ;
    // 5. orders : (commande, date) réparties de même ; 6. par partition : table des lignes de lineitem, sondée par les
    //    commandes ; agrégat par nation et année.
    // Tuple de lineitem (16 octets) : commande, nation (32 bits), montant. Tuple d'orders (8 octets) : commande, date.
    static int semi(Map set, Bloom filter, int[] key, int n, int st, int[] pos, int[] out) {
        int k = 0;
        for (int i = 0; i < n; i++) {
            final long h = hash64(key[i]);
            if (filter.test(h) && set.find(key[i], h) != 0) {
                pos[k] = st + i;
                out[k++] = key[i];
            }
        }
        return k;
    }
    static final class T9 implements Query {
        final Col pPartkey = open("part", "p_partkey"), pName = open("part", "p_name"), psPartkey = open("partsupp", "ps_partkey"),
                psSuppkey = open("partsupp", "ps_suppkey"), psCost = open("partsupp", "ps_supplycost"),
                sSuppkey = open("supplier", "s_suppkey"), sNationkey = open("supplier", "s_nationkey"),
                nNationkey = open("nation", "n_nationkey"), nName = open("nation", "n_name"), lPartkey = open("lineitem", "l_partkey"),
                lSuppkey = open("lineitem", "l_suppkey"), lOrderkey = open("lineitem", "l_orderkey"), lQty = open("lineitem", "l_quantity"),
                lExt = open("lineitem", "l_extendedprice"), lDisc = open("lineitem", "l_discount"), oOrderkey = open("orders", "o_orderkey"),
                oOrderdate = open("orders", "o_orderdate");
        final Counter ctr = new Counter();
        Map part, ps, supp;
        Bloom fpart;
        final Map[] agg = new Map[MAXT];

        void partTask(int tid) {
            final Scratch s = scratch[tid];
            s.l1.n = 0;
            for (int b; (b = ctr.take()) >= 0;) {
                final long nbytes = blockLengths(pName, b, s.len);
                final int k = searchBlock(pName.aux + pName.auxOff(b), nbytes, s.len, GREEN, s.rows);
                for (int i = 0; i < k; i += VEC) {
                    final int n = Math.min(k - i, VEC);
                    unpackSel(pPartkey, b, s.rows, i, n, s.a);
                    for (int j = 0; j < n; j++) s.l1.push(s.a[j]);
                }
            }
        }
        void psTask(int tid) {
            final Scratch s = scratch[tid];
            s.l1.n = 0;
            s.l2.n = 0;
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = psPartkey.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(psPartkey, b, st, n, s.a);
                    final int k = semi(part, fpart, s.a, n, st, s.pos, s.b);
                    if (k == 0) continue;
                    unpackSel(psSuppkey, b, s.pos, 0, k, s.c);
                    unpackSel(psCost, b, s.pos, 0, k, s.d);
                    for (int i = 0; i < k; i++) {
                        s.l1.push((long) s.b[i] << 32 | s.c[i]);
                        s.l2.push(s.d[i]);
                    }
                }
            }
        }
        void lineTask(int tid) {
            final Scratch s = scratch[tid];
            final Parts p = parts[tid];
            p.init(16);
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = lPartkey.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(lPartkey, b, st, n, s.a);
                    final int k = semi(part, fpart, s.a, n, st, s.pos, s.b);
                    if (k == 0) continue;
                    unpackSel(lSuppkey, b, s.pos, 0, k, s.c);
                    unpackSel(lOrderkey, b, s.pos, 0, k, s.d);
                    unpackSel(lQty, b, s.pos, 0, k, s.e);
                    unpackSel(lExt, b, s.pos, 0, k, s.f);
                    unpackSel(lDisc, b, s.pos, 0, k, s.g);
                    for (int i = 0; i < k; i++) {
                        final long cost = ps.get((long) s.b[i] << 32 | s.c[i]), nation = supp.get(s.c[i]);
                        final long t = p.push(partOf(hash64(s.d[i])));
                        putInt(t, s.d[i]);
                        putInt(t + 4, (int) nation);
                        putLong(t + 8, (long) s.f[i] * (100 - s.g[i]) - cost * s.e[i]);
                    }
                }
            }
            p.close();
        }
        void ordersTask(int tid) {
            final Scratch s = scratch[tid];
            final Parts p = parts2[tid];
            p.init(8);
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = oOrderkey.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(oOrderkey, b, st, n, s.a);
                    unpack(oOrderdate, b, st, n, s.b);
                    final int[] key = s.a, date = s.b;
                    final long[] h = s.h;
                    Level.hashKeys(key, n, h);
                    for (int i = 0; i < n; i++) {
                        final long t = p.push(partOf(h[i]));
                        putInt(t, key[i]);
                        putInt(t + 4, date[i]);
                    }
                }
            }
            p.close();
        }
        void joinTask(int tid) {
            final Map total = new Map(tid, 1024), m = scratch[tid].map;
            for (int k; (k = ctr.take()) >= 0;) {
                final long n = partsCount(parts, k);
                if (n == 0) continue;
                // tuples de la partition, recopiés ; next chaîne les tuples d'une même commande ; la table donne le dernier
                final long tu = alloc(tid, n * 16), next = alloc(tid, n * 4);
                m.init(pow2For(n));
                long i = 0;
                for (Parts p : parts)
                    for (long c = p.head(k); c != 0; c = getLong(c))
                        for (long t = c + 64, end = t + getInt(c + 8); t < end; t += 16, i++) {
                            final long cell = m.upsert(getInt(t));
                            putLong(tu + i * 16, getLong(t));
                            putLong(tu + i * 16 + 8, getLong(t + 8));
                            putInt(next + i * 4, m.fresh ? -1 : (int) getLong(cell + 8));
                            putLong(cell + 8, i);
                        }
                for (Parts p : parts2)
                    for (long c = p.head(k); c != 0; c = getLong(c))
                        for (long o = c + 64, end = o + getInt(c + 8); o < end; o += 8) {
                            final long cell = m.find(getInt(o));
                            if (cell == 0) continue;
                            final long year = yearOf(getInt(o + 4));
                            for (int j = (int) getLong(cell + 8); j >= 0; j = getInt(next + j * 4L)) {
                                final long t = tu + j * 16L;
                                total.add((long) getInt(t + 4) << 16 | year, getLong(t + 8));
                            }
                        }
            }
            agg[tid] = total;
        }
        public void run() {
            final Scratch s = scratch[0];
            ctr.set(pName.nblocks);
            pool.run(this::partTask);
            long n = 0;
            for (int t = 0; t < NT; t++) n += scratch[t].l1.n;
            part = new Map(0, pow2For(n));
            fpart = new Bloom(0, n);
            for (int t = 0; t < NT; t++)
                for (int i = 0; i < scratch[t].l1.n; i++) {
                    part.upsert(scratch[t].l1.v[i]);
                    fpart.add(hash64(scratch[t].l1.v[i]));
                }
            ctr.set(psPartkey.nblocks);
            pool.run(this::psTask);
            n = 0;
            for (int t = 0; t < NT; t++) n += scratch[t].l1.n;
            ps = new Map(0, pow2For(n));
            for (int t = 0; t < NT; t++)
                for (int i = 0; i < scratch[t].l1.n; i++) ps.set(scratch[t].l1.v[i], scratch[t].l2.v[i]);
            supp = new Map(0, pow2For(sSuppkey.nrows));
            for (int b = 0; b < sSuppkey.nblocks; b++) {
                final int count = sSuppkey.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int m = Math.min(count - st, VEC);
                    unpack(sSuppkey, b, st, m, s.a);
                    unpack(sNationkey, b, st, m, s.b);
                    for (int i = 0; i < m; i++) supp.set(s.a[i], s.b[i]);
                }
            }
            ctr.set(lPartkey.nblocks);
            pool.run(this::lineTask);
            ctr.set(oOrderkey.nblocks);
            pool.run(this::ordersTask);
            ctr.set(NPART);
            pool.run(this::joinTask);
            // fusion ; nation -> nom ; tri par nom puis année décroissante
            final Map total = new Map(0, 1024);
            for (int t = 0; t < NT; t++)
                for (long j = 0; j <= agg[t].mask; j++) {
                    final long c = agg[t].cells + (j << 4);
                    if (getLong(c) != -1) total.add(getLong(c), getLong(c + 8));
                }
            final Map nat = new Map(0, 64);
            final int nn = (int) nNationkey.nrows;
            unpack(nNationkey, 0, 0, nn, s.a);
            unpack(nName, 0, 0, nn, s.b);
            for (int i = 0; i < nn; i++) nat.set(s.a[i], s.b[i]);
            final long[][] rows = new long[(int) total.count][];  // code du nom, année, somme
            int nr = 0;
            for (long j = 0; j <= total.mask; j++) {
                final long c = total.cells + (j << 4), key = getLong(c);
                if (key != -1) rows[nr++] = new long[] {nat.get(key >> 16), key & 0xFFFF, getLong(c + 8)};
            }
            Arrays.sort(rows, (a, b) -> {
                final int c = compare(nName.dict((int) a[0]), nName.dictLen((int) a[0]), nName.dict((int) b[0]), nName.dictLen((int) b[0]));
                return c != 0 ? c : Long.compare(b[1], a[1]);
            });
            for (long[] r : rows) {
                emitBytes(nName.dict((int) r[0]), nName.dictLen((int) r[0]));
                emit("|");
                emit(r[1]);
                emit("|");
                emit(r[2]);
                emit("\n");
            }
        }
    }

    // ================================================================================================ T18 (TPC-H Q18)
    // Tuple de lineitem (8 octets) : commande, quantité.
    static final class T18 implements Query {
        final Col lOrderkey = open("lineitem", "l_orderkey"), lQty = open("lineitem", "l_quantity"), oOrderkey = open("orders", "o_orderkey"),
                oCustkey = open("orders", "o_custkey"), oOrderdate = open("orders", "o_orderdate"), oTotalprice = open("orders", "o_totalprice"),
                cCustkey = open("customer", "c_custkey"), cName = open("customer", "c_name");
        final Counter ctr = new Counter();
        Map big, cust;
        Bloom fbig, fcust;
        final Map[] sums = new Map[MAXT];

        void scatterTask(int tid) {  // lineitem réparti par commande
            final Scratch s = scratch[tid];
            final Parts p = parts[tid];
            p.init(8);
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = lOrderkey.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(lOrderkey, b, st, n, s.a);
                    unpack(lQty, b, st, n, s.b);
                    final int[] key = s.a, qty = s.b;
                    final long[] h = s.h;
                    Level.hashKeys(key, n, h);
                    for (int i = 0; i < n; i++) {
                        final long t = p.push(partOf(h[i]));
                        putInt(t, key[i]);
                        putInt(t + 4, qty[i]);
                    }
                }
            }
            p.close();
        }
        void aggTask(int tid) {  // une partition : somme par commande ; garde celles de plus de 300 unités
            final Scratch s = scratch[tid];
            final Map m = s.map;
            s.l1.n = 0;
            for (int k; (k = ctr.take()) >= 0;) {
                m.init(pow2Start(partsCount(parts, k)));
                for (Parts p : parts)
                    for (long c = p.head(k); c != 0; c = getLong(c))
                        for (long t = c + 64, end = t + getInt(c + 8); t < end; t += 8) m.add(getInt(t), getInt(t + 4));
                for (long j = 0; j <= m.mask; j++) {
                    final long c = m.cells + (j << 4);
                    if (getLong(c) != -1 && getLong(c + 8) > 30000) s.l1.push(getLong(c));
                }
            }
        }
        void ordersTask(int tid) {  // commandes retenues : client, date, prix
            final Scratch s = scratch[tid];
            s.l1.n = s.l2.n = s.l3.n = s.l4.n = 0;
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = oOrderkey.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(oOrderkey, b, st, n, s.a);
                    final int k = semi(big, fbig, s.a, n, st, s.pos, s.b);
                    if (k == 0) continue;
                    unpackSel(oCustkey, b, s.pos, 0, k, s.c);
                    unpackSel(oOrderdate, b, s.pos, 0, k, s.d);
                    unpackSel(oTotalprice, b, s.pos, 0, k, s.e);
                    for (int i = 0; i < k; i++) {
                        s.l1.push(s.b[i]);
                        s.l2.push(s.c[i]);
                        s.l3.push(s.d[i]);
                        s.l4.push(s.e[i]);
                    }
                }
            }
        }
        void custTask(int tid) {  // clients de ces commandes : position et longueur de leur nom
            final Scratch s = scratch[tid];
            s.l1.n = s.l2.n = s.l3.n = 0;
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = cCustkey.count(b);
                long pos = cName.auxOff(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(cCustkey, b, st, n, s.a);
                    unpack(cName, b, st, n, s.b);
                    for (int i = 0; i < n; i++) {
                        final long h = hash64(s.a[i]);
                        if (fcust.test(h) && cust.find(s.a[i], h) != 0) {
                            s.l1.push(s.a[i]);
                            s.l2.push(pos);
                            s.l3.push(s.b[i]);
                        }
                        pos += s.b[i];
                    }
                }
            }
        }
        void sumTask(int tid) {  // lineitem des commandes retenues : somme des quantités
            final Scratch s = scratch[tid];
            final Map m = new Map(tid, 1024);
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = lOrderkey.count(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(lOrderkey, b, st, n, s.a);
                    final int k = semi(big, fbig, s.a, n, st, s.pos, s.b);
                    if (k == 0) continue;
                    unpackSel(lQty, b, s.pos, 0, k, s.c);
                    for (int i = 0; i < k; i++) m.add(s.b[i], s.c[i]);
                }
            }
            sums[tid] = m;
        }
        public void run() {
            // 1. et 2. agrégation de lineitem par commande ; 3. commandes de plus de 300 unités
            ctr.set(lOrderkey.nblocks);
            pool.run(this::scatterTask);
            ctr.set(NPART);
            pool.run(this::aggTask);
            int n = 0;
            for (int t = 0; t < NT; t++) n += scratch[t].l1.n;
            big = new Map(0, pow2For(n));
            fbig = new Bloom(0, n);
            for (int t = 0; t < NT; t++)
                for (int i = 0; i < scratch[t].l1.n; i++) {
                    big.upsert(scratch[t].l1.v[i]);
                    fbig.add(hash64(scratch[t].l1.v[i]));
                }
            // 4. leurs lignes dans orders
            ctr.set(oOrderkey.nblocks);
            pool.run(this::ordersTask);
            final long[][] rows = new long[n][];  // commande, client, date, prix, somme, position du nom, longueur
            int nr = 0;
            cust = new Map(0, pow2For(n));
            fcust = new Bloom(0, n);
            for (int t = 0; t < NT; t++) {
                final Scratch s = scratch[t];
                for (int i = 0; i < s.l1.n; i++) {
                    rows[nr++] = new long[] {s.l1.v[i], s.l2.v[i], s.l3.v[i], s.l4.v[i], 0, 0, 0};
                    cust.upsert(s.l2.v[i]);
                    fcust.add(hash64(s.l2.v[i]));
                }
            }
            // 5. leurs clients ; 6. leurs lignes dans lineitem
            ctr.set(cCustkey.nblocks);
            pool.run(this::custTask);
            final Map name = new Map(0, pow2For(n));  // client -> rang dans les listes
            final LongList pos = new LongList(), len = new LongList();
            for (int t = 0; t < NT; t++) {
                final Scratch s = scratch[t];
                for (int i = 0; i < s.l1.n; i++) {
                    name.set(s.l1.v[i], pos.n);
                    pos.push(s.l2.v[i]);
                    len.push(s.l3.v[i]);
                }
            }
            ctr.set(lOrderkey.nblocks);
            pool.run(this::sumTask);
            for (int i = 0; i < nr; i++) {
                final long[] r = rows[i];
                for (int t = 0; t < NT; t++) {
                    final long c = sums[t].find(r[0]);
                    if (c != 0) r[4] += getLong(c + 8);
                }
                final int j = (int) name.get(r[1]);
                r[5] = pos.v[j];
                r[6] = len.v[j];
            }
            Arrays.sort(rows, 0, nr, (a, b) -> {  // prix décroissant, date, commande
                if (a[3] != b[3]) return Long.compare(b[3], a[3]);
                if (a[2] != b[2]) return Long.compare(a[2], b[2]);
                return Long.compare(a[0], b[0]);
            });
            for (int i = 0; i < nr && i < 100; i++) {
                final long[] r = rows[i];
                emitBytes(cName.aux + r[5], r[6]);
                for (int j : new int[] {1, 0, 2, 3, 4}) {
                    emit("|");
                    emit(r[j]);
                }
                emit("\n");
            }
        }
    }

    // ================================================================================================ C4
    static final class C4 implements Query {
        final Col uid = open("hits", "UserID");
        final Counter ctr = new Counter();
        final long[] count = new long[MAXT * 8], minus1 = new long[MAXT * 8];

        void scatterTask(int tid) {
            final long[] h = scratch[tid].h;
            final Parts p = parts[tid];
            p.init(8);
            for (int b; (b = ctr.take()) >= 0;) {
                final int count = uid.count(b);
                final long v = uid.words(b);  // 64 bits : valeurs telles quelles
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    final long vv = v + 8L * st;
                    Level.hashLongs(vv, n, h);
                    for (int i = 0; i < n; i++) putLong(p.push(partOf(h[i])), getLong(vv + 8L * i));
                }
            }
            p.close();
        }
        void countTask(int tid) {
            final Map m = scratch[tid].map;
            long total = 0, seen = 0;
            for (int k; (k = ctr.take()) >= 0;) {
                m.init(pow2Start(partsCount(parts, k)));
                for (Parts p : parts)
                    for (long c = p.head(k); c != 0; c = getLong(c))
                        for (long t = c + 64, end = t + getInt(c + 8); t < end; t += 8) {
                            final long x = getLong(t);
                            if (x == -1) seen = 1;  // la valeur qui marque les cases vides est comptée à part
                            else m.upsert(x);
                        }
                total += m.count;
            }
            count[tid * 8] = total;
            minus1[tid * 8] = seen;
        }
        public void run() {
            ctr.set(uid.nblocks);
            pool.run(this::scatterTask);
            ctr.set(NPART);
            pool.run(this::countTask);
            long total = 0, seen = 0;
            for (int t = 0; t < NT; t++) {
                total += count[t * 8];
                seen |= minus1[t * 8];
            }
            emit(Long.toUnsignedString(total + seen));
            emit("\n");
        }
    }

    // ================================================================================================ agrégations par chaîne
    // C12, C16, C33, C36 : les lignes retenues sont hachées, réparties, puis agrégées partition par partition ; chaque
    // fil garde ses dix premiers groupes. Tuple (32 octets) : hachage, entier, position, longueur (32 bits).
    static final class CS implements Query {
        final int mode;  // 12, 16, 33, 36
        final Col str, uid, counter, date, dch, refresh;
        final Counter ctr = new Counter();
        final int lo = daysFromCivil(2013, 7, 1), hi = daysFromCivil(2013, 7, 31);
        final Top10[] top = new Top10[MAXT];

        CS(int mode) {
            this.mode = mode;
            str = open("hits", mode == 12 || mode == 16 ? "SearchPhrase" : "URL");
            uid = mode == 16 ? open("hits", "UserID") : null;
            counter = mode == 36 ? open("hits", "CounterID") : null;
            date = mode == 36 ? open("hits", "EventDate") : null;
            dch = mode == 36 ? open("hits", "DontCountHits") : null;
            refresh = mode == 36 ? open("hits", "IsRefresh") : null;
        }
        void scatterTask(int tid) {
            final Scratch s = scratch[tid];
            final Parts p = parts[tid];
            p.init(32);
            final long bytes = str.aux;
            final int[] len = s.a, sel = s.sel;
            final long[] x = s.x, h = s.h;
            for (int b; (b = ctr.take()) >= 0;) {
                if (mode == 36 && (counter.min(b) > 62 || counter.max(b) < 62 || date.max(b) < lo || date.min(b) > hi)) continue;
                final int count = str.count(b);
                final long u = mode == 16 ? uid.words(b) : 0;
                long pos = str.auxOff(b);
                for (int st = 0; st < count; st += VEC) {
                    final int n = Math.min(count - st, VEC);
                    unpack(str, b, st, n, len);  // longueurs
                    for (int i = 0; i < n; i++) {
                        x[i] = pos;
                        pos += len[i];
                    }
                    int k;
                    if (mode == 36) {
                        unpack(counter, b, st, n, s.b);
                        k = Level.selBetween(s.b, n, 62, 62, st, s.pos);
                        if (k == 0) continue;
                        unpackSel(date, b, s.pos, 0, k, s.c);
                        unpackSel(dch, b, s.pos, 0, k, s.d);
                        unpackSel(refresh, b, s.pos, 0, k, s.e);
                        int k2 = 0;
                        for (int i = 0; i < k; i++) {
                            final int j = s.pos[i] - st;
                            sel[k2] = j;
                            if (s.c[i] >= lo && s.c[i] <= hi && s.d[i] == 0 && s.e[i] == 0 && len[j] > 0) k2++;
                        }
                        k = k2;
                    } else if (mode == 12) {
                        k = Level.selBetween(len, n, 1, Integer.MAX_VALUE, 0, sel);
                    } else {
                        for (int i = 0; i < n; i++) sel[i] = i;
                        k = n;
                    }
                    for (int j = 0; j < k; j++) h[j] = hashBytes(bytes + x[sel[j]], len[sel[j]]);
                    if (u != 0)
                        for (int j = 0; j < k; j++) {
                            final long v = hash64(h[j] ^ (getLong(u + 8L * (st + sel[j])) * K2));
                            h[j] = v != 0 ? v : 1;
                        }
                    for (int j = 0; j < k; j++) {
                        final int i = sel[j];
                        final long t = p.push(partOf(h[j]));
                        putLong(t, h[j]);
                        putLong(t + 8, u != 0 ? getLong(u + 8L * (st + i)) : 0);
                        putLong(t + 16, x[i]);
                        putInt(t + 24, len[i]);
                    }
                }
            }
            p.close();
        }
        void aggTask(int tid) {
            final Top10 best = new Top10(str.aux);
            final SMap m = new SMap(tid, str.aux);
            for (int k; (k = ctr.take()) >= 0;) {
                m.init(pow2Start(partsCount(parts, k)));
                for (Parts p : parts)
                    for (long c = p.head(k); c != 0; c = getLong(c))
                        for (long t = c + 64, end = t + getInt(c + 8); t < end; t += 32)
                            m.add(getLong(t), getLong(t + 8), getLong(t + 16), getInt(t + 24));
                for (long j = 0; j <= m.mask; j++) {
                    final long c = m.cells + (j << 5);
                    if (getLong(c) != 0) best.add(getInt(c + 28), getInt(c + 24), getLong(c + 8), getLong(c + 16));
                }
            }
            top[tid] = best;
        }
        public void run() {
            ctr.set(str.nblocks);
            pool.run(this::scatterTask);
            ctr.set(NPART);
            pool.run(this::aggTask);
            final Top10 all = new Top10(str.aux);
            for (int t = 0; t < NT; t++)
                for (int i = 0; i < top[t].n; i++) all.add(top[t].count[i], top[t].len[i], top[t].ikey[i], top[t].pos[i]);
            for (int i = 0; i < all.n; i++) {
                if (mode == 16) {
                    emit(all.ikey[i]);
                    emit("|");
                }
                emitBytes(str.aux + all.pos[i], all.len[i]);
                emit("|");
                emit(Integer.toUnsignedLong(all.count[i]));
                emit("\n");
            }
        }
    }

    // ================================================================================================ C20
    static final class C20 implements Query {
        final Col url = open("hits", "URL");
        final Counter ctr = new Counter();
        final long[] count = new long[MAXT * 8];

        void task(int tid) {
            final Scratch s = scratch[tid];
            long total = 0;
            for (int b; (b = ctr.take()) >= 0;) {
                final long nbytes = blockLengths(url, b, s.len);
                total += searchBlock(url.aux + url.auxOff(b), nbytes, s.len, GOOGLE, s.rows);
            }
            count[tid * 8] = total;
        }
        public void run() {
            ctr.set(url.nblocks);
            pool.run(this::task);
            long total = 0;
            for (int t = 0; t < NT; t++) total += count[t * 8];
            emit(total);
            emit("\n");
        }
    }

    // ================================================================================================ principal
    public static void main(String[] args) {
        if (args.length < 4) die("usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]");
        final String q = args[0];
        NT = Integer.parseInt(args[1]);
        final int reps = Integer.parseInt(args[2]);
        dataDir = args[3];
        final boolean print = args.length > 4 && args[4].equals("--print");
        if (NT < 1 || NT > MAXT) die("nombre de fils");
        scratch = new Scratch[NT];
        parts = new Parts[NT];
        parts2 = new Parts[NT];
        for (int t = 0; t < NT; t++) {
            scratch[t] = new Scratch(t);
            parts[t] = new Parts(t);
            parts2[t] = new Parts(t);
        }
        final Query query = switch (q) {
            case "t1" -> new T1();
            case "t6" -> new T6();
            case "t9" -> new T9();
            case "t18" -> new T18();
            case "c4" -> new C4();
            case "c12", "c16", "c33", "c36" -> new CS(Integer.parseInt(q.substring(1)));
            case "c20" -> new C20();
            default -> null;
        };
        if (query == null) die("requête inconnue");
        pool.start(NT);
        final StringBuilder line = new StringBuilder();
        for (int r = 0; r < reps; r++) {
            for (int t = 0; t < NT; t++) arenaReset(t);
            resLen = 0;
            final long t0 = System.nanoTime();
            query.run();
            final double dt = (System.nanoTime() - t0) * 1e-9;
            line.setLength(0);
            line.append(String.format(java.util.Locale.ROOT, "RESULT;%s;%s;%d;%d;%.6f;%016x%n", q, Level.LEVEL, NT, r, dt, fnv1a(res, resLen)));
            System.out.print(line);
            if (print && r == reps - 1) System.out.write(res, 0, resLen);
            System.out.flush();
        }
        System.exit(0);
    }
}
