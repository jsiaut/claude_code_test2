// Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de D (LDC 1.43), cas positifs. run.sh y ajoute le code
// produit, les échecs et les recherches d'absence.
import std.stdio, std.parallelism, std.algorithm, std.range, std.file, std.conv;
import core.memory, core.thread, core.atomic, core.cpuid, core.simd;
import core.sys.linux.sched, core.sys.linux.unistd;
import std.experimental.allocator.building_blocks.region : Region;
import std.experimental.allocator.mallocator : Mallocator;
import ldc.gccbuiltins_x86;

struct Part { float x, y, z; ubyte m; }
struct Inl { uint n; float[16] a; }
struct Line { align(64) ulong v; }
extern (C) int sched_getcpu();
extern (C) long syscall(long, ...);

T gsum(T)(const T[] x) { T s = 0; foreach (v; x) s += v; return s; }
ulong fib(ulong n) { ulong a = 0, b = 1; foreach (_; 0 .. n) { auto t = a + b; a = b; b = t; } return a; }

int tid() { return cast(int) syscall(186); }
pragma(inline, false) int delegate(int) mkdg(int k) { return (int x) => x * k; } // fermeture qui s'échappe
pragma(inline, false) int[] mklit() { return [1, 2, 3]; }
pragma(inline, false) Thread mkThread(int t, ulong* po, int* tp)
{
    return new Thread({ ulong s2 = 0; foreach (i; t * 1000 .. (t + 1) * 1000) s2 += i; *po = s2; *tp = tid(); });
}

void main()
{
    // A1
    auto v = new Part[8];
    foreach (ref e; v) e = Part(1, 2, 3, 4);
    auto stride = cast(size_t) &v[1] - cast(size_t) &v[0];
    auto raw = (cast(ubyte*) v.ptr)[0 .. 4];
    writefln("CAP;A1;1;[exécutée] Part[] : pas de %d o = Part.sizeof %d ; les 4 premiers octets du tampon sont le float x en ligne : %(%02x %)", stride, Part.sizeof, raw);
    // A7, A8
    writefln("CAP;A7;1;[exécutée] struct { uint n; float[16] a; } : %d o, Inl.a.offsetof = %d (tableau en ligne)", Inl.sizeof, Inl.a.offsetof);
    auto b8 = new ubyte[1000]; auto h16 = new short[1000];
    writefln("CAP;A8;1;[exécutée] ubyte/short/float : %d/%d/%d o ; ubyte[] de 1000 éléments : %d o, short[] : %d o", ubyte.sizeof, short.sizeof, float.sizeof, b8.length * ubyte.sizeof, h16.length * short.sizeof);
    // B1 (½ : ramasse-miettes par défaut, évitable par @nogc)
    auto c0 = GC.profileStats().numCollections;
    foreach (i; 0 .. 200) { auto junk = new ubyte[1 << 20]; junk[0] = 1; }
    GC.collect();
    auto c1 = GC.profileStats().numCollections;
    writefln("FACT;B1;new et tableaux dynamiques passent par le ramasse-miettes de druntime : %d collectes pendant 200 allocations de 1 Mio (GC.profileStats)", c1 - c0);
    // B2 (½ : std.experimental.allocator)
    ubyte[4096] store;
    import std.experimental.allocator.building_blocks.null_allocator : NullAllocator;
    auto region = Region!NullAllocator(store[]);
    auto blk = cast(ulong[]) region.allocate(100 * ulong.sizeof);
    bool inside = blk.ptr >= cast(void*) store.ptr && blk.ptr < cast(void*) store.ptr + 4096;
    writefln("CAP;B2;0.5;[exécutée] std.experimental.allocator : Region sur un tampon de pile -> bloc dans le tampon = %s ; module expérimental (std.experimental), hors du GC par défaut", inside);
    // B3
    float[1024] local; local[0] = 1;
    float marker = local[0];
    auto ds = cast(long) &marker - cast(long) local.ptr;
    auto dh = cast(long) b8.ptr - cast(long) local.ptr;
    writefln("CAP;B3;1;[exécutée] float[1024] local à %d o d'une autre variable locale, à %d o du tas : sur la pile ; struct et tableaux statiques sont des valeurs", ds < 0 ? -ds : ds, dh < 0 ? -dh : dh);
    // B4 (½ : allocations cachées du langage)
    auto st0 = GC.stats().allocatedInCurrentThread;
    auto dg = mkdg(3);
    auto st1 = GC.stats().allocatedInCurrentThread;
    int[] lit = mklit();
    auto st2 = GC.stats().allocatedInCurrentThread;
    string s = "ab"; s ~= to!string(dg(lit[2]));
    auto st3 = GC.stats().allocatedInCurrentThread;
    writefln("CAP;B4;0.5;[exécutée] octets alloués par le GC, mesurés par GC.stats : fermeture rendue par une fonction %d o, littéral de tableau [1, 2, 3] rendu %d o, concaténation ~= %d o (%s) : allocations cachées du langage ; @nogc les interdit (NOTE B4)", st1 - st0, st2 - st1, st3 - st2, s);
    // B5
    uint[8] buf;
    uint* mp = buf.ptr; mp[3] = 42;
    ubyte* bp = cast(ubyte*) buf.ptr; *cast(uint*)(bp + 16) = 7;
    writefln("CAP;B5;1;[exécutée] uint* : mp[3] = 42 -> buf[3] = %d ; écriture par décalage d'octets -> buf[4] = %d", buf[3], buf[4]);
    // C1
    float8 va = [1, 2, 3, 4, 5, 6, 7, 8];
    float8 vb = va + va;
    writefln("CAP;C1;1;[exécutée] core.simd float8 : (a + a)[7] = %s, opérateurs vectoriels du langage", vb.array[7]);
    // C2
    int16 a16 = 12, b16 = 10, c16 = 1;
    int16 r16 = __builtin_ia32_pternlogd512(a16, b16, c16, 0x96);
    writefln("FACT;C2;ldc.gccbuiltins_x86.__builtin_ia32_pternlogd512 : 12 ^ 10 ^ 1 = %d", r16.array[0]);
    // C5
    auto ids = new int[1000];
    foreach (i, ref e; parallel(ids, 50)) e = tid();
    auto nthreads = ids.dup.sort.uniq.walkLength;
    auto red = taskPool.reduce!"a + b"(iota(0, 1_000_000L));
    writefln("CAP;C5;1;[exécutée] std.parallelism : foreach parallèle sur %d fils distincts (gettid), taskPool.reduce = %d (attendu 499999500000)", nthreads, red);
    // D1
    ulong[4] parts; int[4] tids;
    Thread[4] th;
    foreach (t; 0 .. 4) { th[t] = mkThread(t, &parts[t], &tids[t]); th[t].start(); }
    foreach (t; th) t.join();
    writefln("CAP;D1;1;[exécutée] core.thread : 4 fils, %d identifiants de fil (gettid) distincts, somme %d (attendu 7998000)", tids.dup.sort.uniq.walkLength, parts[].sum);
    // D3
    writefln("CAP;D3;1;[exécutée] std.parallelism.cacheLineSize = %d, core.cpuid.dataCaches()[0].lineSize = %d", cacheLineSize, dataCaches()[0].lineSize);
    // D4
    cpu_set_t set; CPU_SET(1, &set);
    auto ra = sched_setaffinity(0, cpu_set_t.sizeof, &set);
    writefln("CAP;D4;1;[exécutée] core.sys.linux.sched.sched_setaffinity (liaison livrée avec druntime ; ½ en v1) : retour %d, sched_getcpu = %d", ra, sched_getcpu());
    // E2
    int ex;
    asm { mov EAX, 41; add EAX, 1; mov ex, EAX; }
    writefln("CAP;E2;1;[exécutée] asm { mov EAX, 41; add EAX, 1; mov ex, EAX; } (assembleur en ligne du langage) : %d", ex);
    // E7
    enum F60 = fib(60);
    writefln("FACT;E7;enum F60 = fib(60) évalué par CTFE = %d ; gsum!float = %s, gsum!double = %s", F60, gsum([1.5f, 2.5f]), gsum([1.5, 2.25]));
    // F1
    float[4][3] m;
    auto rows = new float[4][](5); // dimension externe à l'exécution, interne fixée
    writefln("FACT;F1;float[4][3] contigu : &m[1][0] - &m[0][3] = %d o, sizeof = %d o ; new float[4][](5) : &r[1][0] - &r[0][3] = %d o", cast(size_t) &m[1][0] - cast(size_t) &m[0][3], m.sizeof, cast(size_t) &rows[1][0] - cast(size_t) &rows[0][3]);
    // F3
    uint um = uint.max; int im = int.max; ubyte c250 = 250;
    writefln("CAP;F3;1;[exécutée] uint.max + 1 = %d, int.max + 1 = %d, ubyte 250 + 10 = %d (arithmétique modulaire définie)", cast(uint)(um + 1), im + 1, cast(ubyte)(c250 + 10));
}
