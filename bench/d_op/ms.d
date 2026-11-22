// Implémentation D (LDC 1.43 / druntime-Phobos 2.113, sans paquet tiers). Voir docs/SPEC.md.
// Correction de la remarque sur D (docs/DLANG.md), reportée le 21 novembre (v4, point 4 : docs/V4_CONVERGE.md, 4.1) :
// Q1 optimisé écrit comme dans les autres langages à types vectoriels portables (même algorithme que la référence C),
// marqué « Remarque D : » ; harnais commun de K9 (docs/K9.md).
import core.atomic;
import core.memory : GC;
import core.simd;
import core.stdc.stdlib : aligned_alloc, free, malloc; mixin(import("sizes.inc"));
import core.thread;
import core.sync.barrier : Barrier;
import core.stdc.string : memcpy;
import core.time : MonoTime;
import ldc.attributes : llvmFastMathFlag;
import ldc.intrinsics : llvm_prefetch;
import ldc.simd : loadUnaligned, storeUnaligned, greaterOrEqualMask;
import ldc.gccbuiltins_x86 : __builtin_ia32_psadbw512;
import std.algorithm : sort;
import std.concurrency;
import std.conv : to;
import std.format : format;
import std.process : environment;
import std.stdio : writefln, writeln, stdout;
import std.array : split;
static import std.file;

alias float16 = __vector(float[16]);
alias double8 = __vector(double[8]);
alias int16 = __vector(int[16]);
alias long8 = __vector(long[8]);

// ------------------------------------------------------------------ harnais
__gshared int WARMUP = 1;
__gshared string DATA = "/opt/msdata";

T[] load(T)(string name) {
    auto raw = cast(ubyte[]) std.file.read(DATA ~ "/" ~ name);
    auto p = cast(ubyte*) aligned_alloc(64, (raw.length + 63) & ~63UL); // copie alignée sur une ligne de cache
    p[0 .. raw.length] = raw[];
    return (cast(T*) p)[0 .. raw.length / T.sizeof];
}
void result(string k, string v, string p, int rep, double sec, string chk) {
    writefln("RESULT;%s;%s;%s;%d;%.9f;%s", k, v, p, rep, sec, chk);
    stdout.flush();
}
double secs(MonoTime t0) { return (MonoTime.currTime - t0).total!"nsecs" * 1e-9; }

// ------------------------------------------------------------------ K1
enum N1 = SIZE_N1;
struct Particle {
    float x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density;
}
pragma(inline, false) double k1Natural(const Particle[] ps) {
    double e = 0;
    foreach (ref p; ps) e += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz);
    return e;
}
pragma(inline, false) double k1AoS(const Particle[] ps) {
    double[8] acc = 0;
    for (size_t i = 0; i < ps.length; i += 8)
        static foreach (k; 0 .. 8) {{
            auto q = &ps[i + k];
            acc[k] += 0.5f * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz);
        }}
    double e = 0;
    foreach (a; acc) e += a;
    return e;
}
// SoA : colonnes séparées + vecteurs __vector(float[16]) (core.simd) ; contraction FMA autorisée
@llvmFastMathFlag("contract") pragma(inline, false)
double k1SoA(const(float)* vx, const(float)* vy, const(float)* vz, const(float)* m, size_t n) {
    double8 a0 = 0, a1 = 0;
    float16 h = 0.5f;
    for (size_t i = 0; i < n; i += 16) {
        float16 x = *cast(float16*)(vx + i), y = *cast(float16*)(vy + i), z = *cast(float16*)(vz + i), w = *cast(float16*)(m + i);
        float16 e = h * w * (z * z + (y * y + x * x));
        float[16] ea = e.array;
        double8 lo, hi;
        static foreach (k; 0 .. 8) { lo.array[k] = ea[k]; hi.array[k] = ea[k + 8]; }
        a0 += lo;
        a1 += hi;
    }
    double8 s = a0 + a1;
    double r = 0;
    foreach (x; s.array) r += x;
    return r;
}
// v4, point 6 (piste ouverte, op_soa) : k1SoA, chargements non alignés (core.simd.loadUnaligned), pour les champs du
// conteneur SOA de soa, alloués par le GC (alignés sur 16 octets)
@llvmFastMathFlag("contract") pragma(inline, false)
double k1SoAU(const(float)* vx, const(float)* vy, const(float)* vz, const(float)* m, size_t n) {
    double8 a0 = 0, a1 = 0;
    float16 h = 0.5f;
    for (size_t i = 0; i < n; i += 16) {
        float16 x = loadUnaligned!float16(cast(float16*)(vx + i)), y = loadUnaligned!float16(cast(float16*)(vy + i));
        float16 z = loadUnaligned!float16(cast(float16*)(vz + i)), w = loadUnaligned!float16(cast(float16*)(m + i));
        float16 e = h * w * (z * z + (y * y + x * x));
        float[16] ea = e.array;
        double8 lo, hi;
        static foreach (k; 0 .. 8) { lo.array[k] = ea[k]; hi.array[k] = ea[k + 8]; }
        a0 += lo;
        a1 += hi;
    }
    double8 s = a0 + a1;
    double r = 0;
    foreach (x; s.array) r += x;
    return r;
}
// Empreinte K1 (D2a) : octets vivants du tas du GC après une collecte complète, et RSS courant
long liveNow() {
    GC.collect();
    return cast(long) GC.stats().usedSize;
}
long rssNow() {
    import std.stdio : File; // readText se fie à la taille du fichier, nulle sous /proc : on lit une ligne
    try return File("/proc/self/statm").readln().split()[1].to!long * 4096;
    catch (Exception) return 0;
}

void runK1(string v, int reps) {
    if (v == "footprint0") { result("k1", v, "energy", 0, 0, "0"); return; }
    auto raw = load!float("k1_particles.f32");
    if (v == "footprint_raw") { result("k1", v, "energy", 0, 0, "0"); return; }
    long m1, r1;
    if (v == "footprint") { m1 = liveNow(); r1 = rssNow(); } // P1 : tampon brut chargé
    auto ps = new Particle[N1]; // tableau dynamique géré par le GC (valeurs contiguës)
    foreach (i; 0 .. N1) ps[i] = *cast(Particle*)&raw[16 * i];
    if (v == "footprint") { // P2 : collection construite, tampon brut encore vivant
        const m2 = liveNow(), r2 = rssNow();
        writefln("META;mem;live;%d;%d\nMETA;rss;%d;%d\nMETA;raw0;%s", m1, m2, r1, r2, raw[0]);
    }
    if (v == "footprint") { free(raw.ptr); result("k1", v, "energy", 0, 0, format("%.6f", k1Natural(ps))); return; }
    if (v == "soa") {
        float*[16] c;
        foreach (k; 0 .. 16) {
            c[k] = cast(float*) aligned_alloc(64, N1 * 4);
            foreach (i; 0 .. N1) c[k][i] = raw[16 * i + k];
        }
        foreach (r; -WARMUP .. reps) {
            auto t0 = MonoTime.currTime;
            double e = k1SoA(c[3], c[4], c[5], c[9], N1);
            auto dt = secs(t0);
            if (r >= 0) result("k1", v, "energy", r, dt, format("%.6f", e));
        }
        return;
    }
    // v4, point 6 (docs/V4_OPEN.md, 5 ; piste ouverte) : op_soa, les particules dans un conteneur SOA!Particle de soa
    // 0.2.0 (un tableau dynamique par champ, rempli par l'affectation d'éléments du conteneur), la boucle d'énergie de
    // la forme d'accès soa (k1SoA) sur ses champs vx, vy, vz et mass.
    if (v == "op_soa") {
        import soa : SOA;
        import std.traits : FieldNameTuple;
        SOA!Particle s;
        static foreach (f; FieldNameTuple!Particle)
            __traits(getMember, s, f) = new float[N1];
        foreach (i; 0 .. N1) s[i] = *cast(Particle*)&raw[16 * i];
        // les tableaux du GC ne sont alignés que sur 16 octets : la boucle de k1SoA, chargements non alignés (k1SoAU)
        foreach (r; -WARMUP .. reps) {
            auto t0 = MonoTime.currTime;
            double e = k1SoAU(s.vx.ptr, s.vy.ptr, s.vz.ptr, s.mass.ptr, N1);
            auto dt = secs(t0);
            if (r >= 0) result("k1", v, "energy", r, dt, format("%.6f", e));
        }
        return;
    }
    if (v == "natural_shuffled") {
        auto perm = load!uint("k1_perm.u32");
        auto s = new Particle[N1];
        foreach (i, j; perm) s[i] = ps[j];
        ps = s;
    }
    bool aos = v == "aos";
    foreach (r; -WARMUP .. reps) {
        auto t0 = MonoTime.currTime;
        double e = aos ? k1AoS(ps) : k1Natural(ps);
        auto dt = secs(t0);
        if (r >= 0) result("k1", v, "energy", r, dt, format("%.6f", e));
    }
}

// ------------------------------------------------------------------ K2
pragma(inline, false) uint k2Chase(const uint[] a, size_t h) {
    uint i = 0;
    foreach (_; 0 .. h) i = a.ptr[i];
    return i;
}
void runK2(string v, int reps, string p) {
    auto a = load!uint("k2_chase_" ~ p ~ ".u32");
    foreach (r; -WARMUP .. reps) {
        auto t0 = MonoTime.currTime;
        uint i = k2Chase(a, 4200000);
        auto dt = secs(t0);
        if (r >= 0) result("k2", v, p, r, dt, i.to!string);
    }
}

// ------------------------------------------------------------------ K3
enum ITER3 = 1 << 25;
align(128) struct Padded { shared ulong v; }
align(64) struct Packed4 { shared ulong[4] v; }
void runK3(string v, int reps) {
    bool rmw = v[0 .. 3] == "rmw", padded = v[$ - 6 .. $] == "padded";
    writeln("META;k3_mechanism;", rmw ? "atomicFetchAdd!(MemoryOrder.raw) (lock xadd)" : "atomicLoad/atomicStore!(MemoryOrder.raw) (mov)");
    auto pad = new Padded[4];
    auto pk = new Packed4;
    foreach (r; -WARMUP .. reps) {
        shared(ulong)*[4] ctr;
        foreach (t; 0 .. 4) { ctr[t] = padded ? &pad[t].v : &pk.v[t]; atomicStore(*ctr[t], 0UL); }
        auto t0 = MonoTime.currTime;
        // un délégué créé dans une boucle capture le cadre de la fonction, pas la variable de
        // l'itération : on passe par une fonction pour obtenir un cadre (une fermeture) par thread
        static Thread mk(shared(ulong)* c, bool rmw) {
            return new Thread({
                if (rmw) foreach (_; 0 .. ITER3) atomicFetchAdd!(MemoryOrder.raw)(*c, 1);
                else foreach (_; 0 .. ITER3) atomicStore!(MemoryOrder.raw)(*c, atomicLoad!(MemoryOrder.raw)(*c) + 1);
            }).start();
        }
        Thread[4] th;
        foreach (t; 0 .. 4) th[t] = mk(ctr[t], rmw);
        foreach (t; th) t.join();
        auto dt = secs(t0);
        ulong s = 0;
        foreach (c; ctr) s += atomicLoad(*c);
        if (r >= 0) result("k3", v, "4x2^25", r, dt, s.to!string);
    }
}

// ------------------------------------------------------------------ réserve de fils (v4, point 4)
// v4, point 4 (docs/V4_CONVERGE.md, 3.3, mt_pool) : réserve de quatre fils de travail, le fil principal compris. Les
// trois autres (core.thread) sont créés une fois par processus, avant l'échauffement ; à chaque appel, une barrière
// (core.sync.barrier) les réveille, chacun traite son quart (0 pour le fil principal), et une seconde barrière attend
// leur fin. Entre deux appels, ils attendent, bloqués, à la première. Le travail passe par un pointeur de fonction et
// un pointeur de données, écrits avant la première barrière (aucune fermeture allouée par appel).
__gshared Barrier poolStart, poolDone;
__gshared void function(void*, int) poolFn;
__gshared void* poolData;
__gshared bool poolQuit;
__gshared Thread[3] poolTh;
void poolWorker(int t) {
    for (;;) {
        poolStart.wait();
        if (poolQuit) return;
        poolFn(poolData, t);
        poolDone.wait();
    }
}
void startPool() {
    static Thread mk(int t) { return new Thread({ poolWorker(t); }).start(); }
    poolStart = new Barrier(4);
    poolDone = new Barrier(4);
    foreach (t; 1 .. 4) poolTh[t - 1] = mk(t);
}
void runPool(void function(void*, int) fn, void* data) {
    poolFn = fn;
    poolData = data;
    poolStart.wait();
    fn(data, 0);
    poolDone.wait();
}
void stopPool() {
    poolQuit = true;
    poolStart.wait();
    foreach (t; poolTh) t.join();
}

// ------------------------------------------------------------------ K4
pragma(inline, false) ulong k4Natural(const ubyte[] v) { ulong s = 0; foreach (x; v) if (x >= 128) s += x; return s; }
pragma(inline, false) ulong k4Branchless(const ubyte[] v) { ulong s = 0; foreach (x; v) s += cast(ulong) x * (x >> 7); return s; }
// v4, point 3 (docs/V4_EQUAL.md, R3) : variante tuned, SIMD explicite (vecteurs de core.simd, masque non signé de
// ldc.simd, vpsadbw de ldc.gccbuiltins_x86) : masque v >= 128, octets hors masque à zéro, sommes de 8 octets en
// entiers de 64 bits.
pragma(inline, false) ulong k4Tuned(const ubyte[] v) {
    alias ubyte64 = __vector(ubyte[64]);
    alias byte64 = __vector(byte[64]);
    long8 acc = 0;
    ubyte64 lim = 128;
    byte64 zero = 0;
    size_t i = 0;
    const n = v.length;
    for (; i + 64 <= n; i += 64) {
        ubyte64 x = loadUnaligned!ubyte64(v.ptr + i);
        ubyte64 y = x & cast(ubyte64) greaterOrEqualMask!ubyte64(x, lim);
        acc += __builtin_ia32_psadbw512(cast(byte64) y, zero);
    }
    ulong s = 0;
    foreach (k; 0 .. 8) s += acc[k];
    for (; i < n; i++) if (v[i] >= 128) s += v[i];
    return s;
}
// v4, point 4 (docs/V4_CONVERGE.md, 3.3, K4 swar) : octets traités par mots de 64 bits. Le bit de poids fort de chaque
// octet, ramené au bit 0 de l'octet et multiplié par 0xFF, donne un masque d'octet qui garde les octets >= 128 ; les
// octets gardés sont sommés par paires dans quatre voies de 16 bits. Exactitude pour toute donnée : une voie reçoit au
// plus 2 × 255 = 510 par mot, donc au plus 128 × 510 = 65 280 < 2^16 en 128 mots ; les voies sont vidées dans la somme
// de 64 bits toutes les 128 mots (et à la fin). Aucun branchement sur les données (le reste, < 8 octets, par produit).
pragma(inline, false) ulong k4Swar(const ubyte[] v) {
    enum ulong ONES = 0x0101010101010101UL, LO = 0x00FF00FF00FF00FFUL;
    const n = v.length;
    const(ubyte)* p = v.ptr;
    ulong s = 0;
    size_t i = 0;
    while (i + 8 <= n) {
        const size_t end = i + 128 * 8 <= n ? i + 128 * 8 : n - (n - i) % 8;
        ulong acc = 0;
        for (; i < end; i += 8) {
            ulong w;
            memcpy(&w, p + i, 8);
            const ulong y = w & (((w >> 7) & ONES) * 0xFF);
            acc += (y & LO) + ((y >> 8) & LO);
        }
        acc = (acc & 0x0000FFFF0000FFFFUL) + ((acc >> 16) & 0x0000FFFF0000FFFFUL); // deux voies de 32 bits
        s += (acc & 0xFFFFFFFFUL) + (acc >> 32);
    }
    for (; i < n; i++) s += cast(ulong) p[i] * (p[i] >> 7);
    return s;
}
void runK4(string v, int reps) {
    auto d = load!ubyte("k4_bytes.u8");
    if (v == "natural_sorted") sort(d);
    bool bl = v == "branchless_unsorted", tu = v == "tuned", sw = v == "swar";
    foreach (r; -WARMUP .. reps) {
        auto t0 = MonoTime.currTime;
        ulong s = tu ? k4Tuned(d) : sw ? k4Swar(d) : bl ? k4Branchless(d) : k4Natural(d);
        auto dt = secs(t0);
        if (r >= 0) result("k4", v, "16M", r, dt, s.to!string);
    }
}

// ------------------------------------------------------------------ K5
enum INNER5 = SIZE_INNER5;
pragma(inline, false) float k5Natural(const float[] a, const float[] b) {
    float s = 0;
    foreach (i; 0 .. a.length) s += a[i] * b[i];
    return s;
}
@llvmFastMathFlag("contract") pragma(inline, false)
float k5Tuned(const(float)* a, const(float)* b, size_t n) {
    float16 s0 = 0, s1 = 0, s2 = 0, s3 = 0;
    for (size_t i = 0; i < n; i += 64) {
        s0 += *cast(float16*)(a + i) * *cast(float16*)(b + i);
        s1 += *cast(float16*)(a + i + 16) * *cast(float16*)(b + i + 16);
        s2 += *cast(float16*)(a + i + 32) * *cast(float16*)(b + i + 32);
        s3 += *cast(float16*)(a + i + 48) * *cast(float16*)(b + i + 48);
    }
    float16 s = (s0 + s1) + (s2 + s3);
    float r = 0;
    foreach (x; s.array) r += x;
    return r;
}
__gshared const(float)* sinkA;
void runK5(string v, int reps) {
    auto a = load!float("k5_a.f32"), b = load!float("k5_b.f32");
    bool tuned = v == "tuned";
    foreach (r; -WARMUP .. reps) {
        float d = 0;
        auto t0 = MonoTime.currTime;
        foreach (_; 0 .. INNER5) {
            atomicStore!(MemoryOrder.raw)(*cast(shared)&sinkA, cast(shared) a.ptr); // barrière d'optimisation
            auto pa = cast(const(float)*) atomicLoad!(MemoryOrder.raw)(*cast(shared)&sinkA);
            d = tuned ? k5Tuned(pa, b.ptr, a.length) : k5Natural(pa[0 .. a.length], b);
        }
        auto dt = secs(t0);
        if (r >= 0) result("k5", v, "2048x65536", r, dt, format("%.4f", d));
    }
}

// ------------------------------------------------------------------ K6
enum N6 = SIZE_N6;
struct Cols { int[] sd, pr; ubyte[] q, d, t, rf, ls; }
alias Q1Acc = long[5][6];
pragma(inline, false) long q6Natural(const ref Cols c, size_t lo, size_t hi) {
    long s = 0;
    foreach (i; lo .. hi)
        if (c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24) s += cast(long) c.pr[i] * c.d[i];
    return s;
}
// Q6 optimisé : prédicat sans branchement sur pointeurs bruts (vectorisé par LLVM)
pragma(inline, false) long q6Tuned(const ref Cols c, size_t lo, size_t hi) {
    const(int)* sd = c.sd.ptr, pr = c.pr.ptr;
    const(ubyte)* d = c.d.ptr, q = c.q.ptr;
    long s = 0;
    foreach (i; lo .. hi) {
        int m = (cast(uint)(sd[i] - 8766) < 365u) & (cast(ubyte)(d[i] - 5) <= 2) & (q[i] < 24);
        s += cast(long)(pr[i] * d[i]) & -cast(long) m;
    }
    return s;
}
pragma(inline, false) void q1Natural(const ref Cols c, size_t lo, size_t hi, ref Q1Acc acc) {
    foreach (i; lo .. hi) {
        if (c.sd[i] <= 10471) {
            int g = c.rf[i] * 2 + c.ls[i];
            long p = c.pr[i], dp = p * (100 - c.d[i]);
            acc[g][0] += 1; acc[g][1] += c.q[i]; acc[g][2] += p; acc[g][3] += dp; acc[g][4] += dp * (100 + c.t[i]);
        }
    }
}
// Remarque D : Q1 optimisé, même algorithme que la référence C (une passe, 16 lignes par itération, agrégation
// masquée par groupe) en types vectoriels portables de core.simd, comme C++, Zig, Odin, C3, Mojo et C# ; accumulateurs
// 32 bits vidés toutes les 4096 lignes, colonne « charge » en 64 bits (lignes paires et impaires).
alias ubyte16v = __vector(ubyte[16]);
pragma(inline, true) int16 ld8(const(ubyte)* p) {
    int[16] a; // élargissement 8 -> 32 bits (vpmovzxbd) ; écrire v.array[k] dans une fonction inline fait planter LDC 1.43
    foreach (k; 0 .. 16) a[k] = p[k];
    return loadUnaligned!int16(a.ptr);
}
pragma(inline, true) int16 ld32(const(int)* p) { return loadUnaligned!int16(p); }
pragma(inline, true) long sum16(int16 v) { long s = 0; foreach (k; 0 .. 16) s += v.array[k]; return s; }
pragma(inline, true) long sum8(long8 v) { long s = 0; foreach (k; 0 .. 8) s += v.array[k]; return s; }
pragma(inline, false) void q1Tuned(const ref Cols c, size_t lo, size_t hi, ref Q1Acc acc) {
    const(int)* sd = c.sd.ptr, pr = c.pr.ptr;
    const(ubyte)* q = c.q.ptr, d = c.d.ptr, t = c.t.ptr, rf = c.rf.ptr, ls = c.ls.ptr;
    const int16 lim = 10471, c100 = 100;
    size_t i = lo;
    while (i + 16 <= hi) {
        int16[6] aq = 0, ap = 0, adp = 0, cnt = 0;
        long8[6] ace = 0, aco = 0;
        size_t end = i + 4096 <= hi ? i + 4096 : hi - (hi - i) % 16;
        for (; i < end; i += 16) {
            int16 pass = ld32(sd + i) <= lim;
            int16 vg = ld8(rf + i) * 2 + ld8(ls + i);
            int16 vq = ld8(q + i), vd = ld8(d + i), vt = ld8(t + i) + c100, vp = ld32(pr + i);
            int16 vdp = vp * (c100 - vd);
            long8 dp64 = cast(long8) vdp, t64 = cast(long8) vt;
            long8 che = ((dp64 << 32) >> 32) * ((t64 << 32) >> 32); // lignes paires (vpmuldq)
            long8 cho = (dp64 >> 32) * (t64 >> 32);                  // lignes impaires
            static foreach (g; 0 .. 6) {{
                int16 m = pass & (vg == int16(g));
                cnt[g] -= m;
                aq[g] += vq & m; ap[g] += vp & m; adp[g] += vdp & m;
                long8 m64 = cast(long8) m;
                ace[g] += che & ((m64 << 32) >> 32);
                aco[g] += cho & (m64 >> 32);
            }}
        }
        foreach (g; 0 .. 6) {
            long8 ch = ace[g] + aco[g]; // variable nommée : « sum8(ace[g] + aco[g]) » dans un += fait planter LDC 1.43
            acc[g][0] += sum16(cnt[g]); acc[g][1] += sum16(aq[g]); acc[g][2] += sum16(ap[g]);
            acc[g][3] += sum16(adp[g]); acc[g][4] += sum8(ch);
        }
    }
    if (i < hi) q1Natural(c, i, hi, acc); // reste éventuel (< 16 lignes)
}
long fold(ref Q1Acc a) { long s = 0; foreach (row; a) foreach (x; row) s += x; return s; }
// v4, point 4 (docs/V4_CONVERGE.md, 3.3, K6 Q6 tuned_v ; forme de la frontière, Zig) : blocs de 16 lignes en vecteurs
// de core.simd : colonnes élargies en i32, prédicat par comparaisons, produit prix × remise en i32, sélection (et
// logique avec le masque), accumulation en i64 (voies paires et impaires, comme la charge de q1Tuned). Exactitude pour
// toute donnée de la spécification (docs/SPEC.md, K6) : prix <= 50 000 et remise <= 10, donc produit <= 500 000 <
// 2^31 ; une voie de 64 bits reçoit au plus N6 / 16 produits. La variante tuned publiée est scalaire sans branchement.
pragma(inline, false) long q6TunedV(const ref Cols c, size_t lo, size_t hi) {
    const(int)* sd = c.sd.ptr, pr = c.pr.ptr;
    const(ubyte)* d = c.d.ptr, q = c.q.ptr;
    const int16 d0 = 8766, d1 = 9131, r0 = 5, r1 = 7, q0 = 24;
    long8 a0 = 0, a1 = 0;
    size_t i = lo;
    for (; i + 16 <= hi; i += 16) {
        int16 vsd = ld32(sd + i), vd = ld8(d + i), vq = ld8(q + i), vp = ld32(pr + i);
        int16 m = (vsd >= d0) & (vsd < d1) & (vd >= r0) & (vd <= r1) & (vq < q0);
        long8 p64 = cast(long8)((vp * vd) & m);
        a0 += (p64 << 32) >> 32; // lignes paires
        a1 += p64 >> 32;         // lignes impaires
    }
    long8 a = a0 + a1; // variable nommée (voir sum8 plus haut)
    return sum8(a) + q6Natural(c, i, hi); // reste (< 16 lignes)
}
// mt_pool, mt_pool_v (v4, point 4) : un quart par fil de la réserve ; mt_pool exécute la forme de la variante mt
// publiée (q6Tuned, q1Tuned, déjà la forme tuned_v de Q1), mt_pool_v la forme tuned_v de Q6.
struct K6Pool { const(Cols)* c; bool q1, vec; long[4] res; }
void k6PoolJob(void* data, int t) {
    auto j = cast(K6Pool*) data;
    const size_t lo = N6 / 4 * t, hi = N6 / 4 * (t + 1);
    if (j.q1) { Q1Acc a; q1Tuned(*j.c, lo, hi, a); j.res[t] = fold(a); }
    else j.res[t] = j.vec ? q6TunedV(*j.c, lo, hi) : q6Tuned(*j.c, lo, hi);
}
void runK6(string v, int reps, string p) {
    auto c = Cols(load!int("k6_shipdate.i32"), load!int("k6_extendedprice.i32"), load!ubyte("k6_quantity.u8"), load!ubyte("k6_discount.u8"),
                  load!ubyte("k6_tax.u8"), load!ubyte("k6_returnflag.u8"), load!ubyte("k6_linestatus.u8"));
    bool q1 = p == "q1";
    const bool pl = v == "mt_pool" || (v == "mt_pool_v" && !q1);
    if (pl) startPool();
    foreach (r; -WARMUP .. reps) {
        auto t0 = MonoTime.currTime;
        long s = 0;
        if (pl) {
            auto j = K6Pool(&c, q1, v == "mt_pool_v");
            runPool(&k6PoolJob, &j);
            foreach (x; j.res) s += x;
        } else if (v == "tuned_v" && !q1) {
            s = q6TunedV(c, 0, N6);
        } else if (v == "mt") {
            long[4] part;
            static Thread mk(Cols* c, size_t lo, size_t hi, bool q1, long* res) {
                return new Thread({
                    if (q1) { Q1Acc a; q1Tuned(*c, lo, hi, a); *res = fold(a); } else *res = q6Tuned(*c, lo, hi);
                }).start();
            }
            Thread[4] th;
            foreach (t; 0 .. 4) th[t] = mk(&c, N6 / 4 * t, N6 / 4 * (t + 1), q1, &part[t]);
            foreach (t; th) t.join();
            foreach (x; part) s += x;
        } else if (v == "tuned") {
            if (q1) { Q1Acc a; q1Tuned(c, 0, N6, a); s = fold(a); } else s = q6Tuned(c, 0, N6);
        } else {
            if (q1) { Q1Acc a; q1Natural(c, 0, N6, a); s = fold(a); } else s = q6Natural(c, 0, N6);
        }
        auto dt = secs(t0);
        if (r >= 0) result("k6", v, p, r, dt, s.to!string);
    }
    if (pl) stopPool();
}

// ------------------------------------------------------------------ K7
struct Agg { uint count; ulong sum; }
struct Slot { uint key, count; ulong sum; }
void runK7(string v, int reps) {
    auto keys = load!uint("k7_keys.u32"), vals = load!uint("k7_vals.u32");
    foreach (r; -WARMUP .. reps) {
        ulong nk = 0, ws = 0;
        double dt;
        if (v == "natural") {
            auto t0 = MonoTime.currTime;
            Agg[uint] m; // tableau associatif intégré au langage
            foreach (i, k; keys) {
                if (auto e = k in m) { e.count++; e.sum += vals[i]; } else m[k] = Agg(1, vals[i]);
            }
            dt = secs(t0);
            nk = m.length;
            foreach (k, e; m) ws += e.sum * ((k & 1023) + 1);
        } else {
            enum LOG = SIZE_K7_LOG2 + 1, CAP = 1 << LOG;
            auto t0 = MonoTime.currTime;
            auto tab = cast(Slot*) aligned_alloc(64, CAP * Slot.sizeof);
            tab[0 .. CAP] = Slot.init;
            for (size_t i = 0; i < keys.length; i += 16) {
                uint[16] h;
                static foreach (b; 0 .. 16) {
                    h[b] = (keys[i + b] * 0x9E3779B1u) >> (32 - LOG);
                    llvm_prefetch(&tab[h[b]], 1, 3, 1);
                }
                static foreach (b; 0 .. 16) {{
                    uint k = keys[i + b], s = h[b];
                    while (tab[s].count != 0 && tab[s].key != k) s = (s + 1) & (CAP - 1);
                    tab[s].key = k; tab[s].count++; tab[s].sum += vals[i + b];
                }}
            }
            dt = secs(t0);
            foreach (ref e; tab[0 .. CAP]) if (e.count) { nk++; ws += e.sum * ((e.key & 1023) + 1); }
            free(tab);
        }
        if (r >= 0) result("k7", v, "16M/1M", r, dt, format("%d:%d", nk, ws));
    }
}

// ------------------------------------------------------------------ K8
class Node { long v; Node l, r; } // objet GC (allocation par défaut en D)
Node tBuild(int d, ref long c) {
    auto n = new Node;
    n.v = c++;
    if (d > 0) { n.l = tBuild(d - 1, c); n.r = tBuild(d - 1, c); }
    return n;
}
long tSum(Node n) { return n is null ? 0 : n.v + tSum(n.l) + tSum(n.r); }
struct ANode { long v; int l, r; }
int aBuild(ANode* a, ref int top, int d, ref long c) {
    int i = top++;
    a[i] = ANode(c++, -1, -1);
    if (d > 0) { int l = aBuild(a, top, d - 1, c); a[i].l = l; a[i].r = aBuild(a, top, d - 1, c); }
    return i;
}
long aSum(const(ANode)* a, int i) { return i < 0 ? 0 : a[i].v + aSum(a, a[i].l) + aSum(a, a[i].r); }
// v4, point 4 (docs/V4_CONVERGE.md, 3.3, K8 tuned_val ; forme de la frontière, Ada, et de bench/c_k8val) : l'état passe
// par valeur, l'indice du nœud en ordre préfixe (sa valeur : numéro de requête + indice) ; la fonction rend l'indice
// libre suivant. Même arène, mêmes liens et mêmes valeurs que aBuild ; somme récursive par les liens (aSum).
int avBuild(ANode* a, int i, int d, long q) {
    a[i].v = q + i;
    if (d > 0) {
        const int l = i + 1, r = avBuild(a, l, d - 1, q);
        a[i].l = l;
        a[i].r = r;
        return avBuild(a, r, d - 1, q);
    }
    a[i].l = a[i].r = -1;
    return i + 1;
}
// v4, point 4 (docs/V4_CONVERGE.md, 3.3, K8 tuned_it ; forme de bench/c_k8it, remarque sur C) : construction et somme
// itératives, piles explicites. La construction descend à gauche en empilant le sous-arbre droit de chaque nœud
// interne, puis le reprend à la feuille suivante : même ordre préfixe, mêmes liens et mêmes valeurs que aBuild. Les
// piles tiennent par construction : au plus une entrée par niveau à la construction, au plus profondeur + 1 à la somme.
static assert(SIZE_K8_REQ < 63, "piles de K8 tuned_it : 64 entrées");
struct K8Pend { int parent, depth; }
void aiBuild(ANode* a, int depth, long q) {
    K8Pend[64] stk = void;
    int sp = 0, top = 0, parent = -1, d = depth;
    bool right = false;
    for (;;) {
        const int i = top++;
        a[i].v = q + i;
        if (parent >= 0) { if (right) a[parent].r = i; else a[parent].l = i; }
        if (d > 0) {
            stk[sp++] = K8Pend(i, d - 1);
            parent = i; right = false; d = d - 1;
        } else {
            a[i].l = a[i].r = -1;
            if (sp == 0) break;
            sp--;
            parent = stk[sp].parent; d = stk[sp].depth; right = true;
        }
    }
}
long aiSum(const(ANode)* a, int root) {
    int[64] stk = void;
    int sp = 1;
    stk[0] = root;
    long s = 0;
    while (sp > 0) {
        const int i = stk[--sp];
        s += a[i].v;
        if (a[i].l >= 0) { stk[sp++] = a[i].r; stk[sp++] = a[i].l; }
    }
    return s;
}
__gshared Node keep;
void runK8(string v, int reps) {
    enum Q = 16384;
    bool tuned = v == "tuned";
    long c0 = 0;
    keep = tBuild(SIZE_K8_LONG, c0);
    long lsum = tSum(keep);
    auto lat = new long[Q];
    auto arena = cast(ANode*) malloc(ANode.sizeof * ((2 << SIZE_K8_REQ) - 1));
    foreach (r; -WARMUP .. reps) {
        long total = 0;
        auto t0 = MonoTime.currTime;
        foreach (q; 0 .. Q) {
            auto a = MonoTime.currTime;
            long c = q, s;
            if (tuned) { int top = 0; s = aSum(arena, aBuild(arena, top, SIZE_K8_REQ, c)); }
            else if (v == "tuned_val") { avBuild(arena, 0, SIZE_K8_REQ, c); s = aSum(arena, 0); }
            else if (v == "tuned_it") { aiBuild(arena, SIZE_K8_REQ, c); s = aiSum(arena, 0); }
            else s = tSum(tBuild(SIZE_K8_REQ, c));
            total += s;
            lat[q] = (MonoTime.currTime - a).total!"nsecs";
        }
        auto dt = secs(t0);
        if (r >= 0) {
            result("k8", v, "16384x2047", r, dt, (total + lsum).to!string);
            sort(lat);
            writefln("LAT;%s;%d;%d;%d;%d;%d", v, lat[Q / 2], lat[Q * 9 / 10], lat[Q * 99 / 100], lat[Q * 999 / 1000], lat[Q - 1]);
        }
    }
}

// ------------------------------------------------------------------ K9
enum M9 = SIZE_M9;
double k9Init(size_t i, size_t j) { return ((i * 31 + j * 17) % 1024) / 1024.0; }
pragma(inline, false) void k9Natural(double[][] a, double[][] b) {
    foreach (i; 1 .. M9 - 1) foreach (j; 1 .. M9 - 1) b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1]);
}
// v4, point 3 (docs/V4_EQUAL.md, R2) : naturel en grille contiguë, double[] indexé i * M9 + j, même boucle
pragma(inline, false) void k9NaturalFlat(double[] a, double[] b) {
    foreach (i; 1 .. M9 - 1) foreach (j; 1 .. M9 - 1) b[i * M9 + j] = 0.25 * (((a[(i - 1) * M9 + j] + a[(i + 1) * M9 + j]) + a[i * M9 + j - 1]) + a[i * M9 + j + 1]);
}
pragma(inline, false) void k9Rows(const(double)* a, double* b, size_t r0, size_t r1) {
    double8 q4 = 0.25;
    foreach (i; r0 .. r1) {
        const(double)* up = a + (i - 1) * M9, mid = a + i * M9, dn = a + (i + 1) * M9;
        double* o = b + i * M9;
        size_t j = 1;
        for (; j + 8 <= M9 - 1; j += 8) {
            double8 val = q4 * (((loadUnaligned!double8(up + j) + loadUnaligned!double8(dn + j)) + loadUnaligned!double8(mid + j - 1)) + loadUnaligned!double8(mid + j + 1));
            storeUnaligned!double8(val, o + j);
        }
        for (; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
// mt_pool (v4, point 4) : un quart des lignes par fil de la réserve, chacun exécute k9Rows (déjà la forme tuned_v)
struct K9Pool { const(double)* a; double* b; }
void k9PoolJob(void* data, int t) {
    auto j = cast(K9Pool*) data;
    k9Rows(j.a, j.b, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4);
}
void runK9(string v, int reps) {
    // harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono
    double[][] na, nb;
    double* ga, gb;
    if (v == "natural") { na = new double[][](M9, M9); nb = new double[][](M9, M9); } // tableau de tableaux (idiome D)
    else { ga = cast(double*) aligned_alloc(64, M9 * M9 * 8); gb = cast(double*) aligned_alloc(64, M9 * M9 * 8); }
    const bool pl = v == "mt_pool";
    if (pl) startPool();
    foreach (r; -WARMUP .. reps) {
        double s = 0, dt;
        if (v == "natural") {
            auto a = na, b = nb;
            foreach (i; 0 .. M9) foreach (j; 0 .. M9) a[i][j] = b[i][j] = k9Init(i, j);
            auto t0 = MonoTime.currTime;
            foreach (_; 0 .. 4) { k9Natural(a, b); auto tmp = a; a = b; b = tmp; }
            dt = secs(t0);
            foreach (row; a) foreach (x; row) s += x;
        } else if (v == "natural_flat") {
            auto a = new double[](M9 * M9), b = new double[](M9 * M9);
            foreach (k; 0 .. M9 * M9) a[k] = b[k] = k9Init(k / M9, k % M9);
            auto t0 = MonoTime.currTime;
            foreach (_; 0 .. 4) { k9NaturalFlat(a, b); auto tmp = a; a = b; b = tmp; }
            dt = secs(t0);
            foreach (x; a) s += x;
        } else {
            auto a = ga, b = gb;
            foreach (k; 0 .. M9 * M9) a[k] = b[k] = k9Init(k / M9, k % M9);
            auto t0 = MonoTime.currTime;
            foreach (_; 0 .. 4) {
                if (v == "tuned") k9Rows(a, b, 1, M9 - 1);
                else if (pl) { auto j = K9Pool(a, b); runPool(&k9PoolJob, &j); }
                else {
                    static Thread mk(double* fa, double* fb, size_t r0, size_t r1) {
                        return new Thread({ k9Rows(fa, fb, r0, r1); }).start();
                    }
                    Thread[4] th;
                    foreach (t; 0 .. 4) th[t] = mk(a, b, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4);
                    foreach (t; th) t.join();
                }
                auto tmp = a; a = b; b = tmp;
            }
            dt = secs(t0);
            foreach (k; 0 .. M9 * M9) s += a[k];
        }
        if (r >= 0) result("k9", v, "2048^2x4", r, dt, format("%.15e", s));
    }
    if (pl) stopPool();
    if (v != "natural") { free(ga); free(gb); }
}

// ------------------------------------------------------------------ K10
enum M10 = 1 << 22, CAP10 = 1 << 14;
struct Spsc {
    align(128) shared size_t writeIdx;
    align(128) shared size_t readIdx;
    align(128) ulong[CAP10] buf;
}
void producerMsg(Tid owner) { foreach (x; 1 .. M10 + 1UL) send(owner, x); }
void runK10(string v, int reps) {
    foreach (r; -WARMUP .. reps) {
        ulong s = 0;
        auto t0 = MonoTime.currTime;
        if (v == "natural") { // std.concurrency : passage de messages entre threads (idiome D)
            setMaxMailboxSize(thisTid, CAP10, OnCrowding.block);
            spawn(&producerMsg, thisTid);
            foreach (_; 0 .. M10) s += receiveOnly!ulong();
        } else {
            auto q = cast(Spsc*) aligned_alloc(128, Spsc.sizeof);
            atomicStore(q.writeIdx, 0UL); atomicStore(q.readIdx, 0UL);
            ulong res;
            auto prod = new Thread({
                size_t w = 0, rc = 0;
                foreach (x; 1 .. M10 + 1UL) {
                    while (w - rc == CAP10) { rc = atomicLoad!(MemoryOrder.acq)(q.readIdx); if (w - rc == CAP10) pause(); }
                    q.buf[w & (CAP10 - 1)] = x;
                    atomicStore!(MemoryOrder.rel)(q.writeIdx, ++w);
                }
            });
            auto cons = new Thread({
                size_t rd = 0, wc = 0;
                ulong sum = 0;
                foreach (_; 0 .. M10) {
                    while (rd == wc) { wc = atomicLoad!(MemoryOrder.acq)(q.writeIdx); if (rd == wc) pause(); }
                    sum += q.buf[rd & (CAP10 - 1)];
                    atomicStore!(MemoryOrder.rel)(q.readIdx, ++rd);
                }
                res = sum;
            });
            cons.start(); prod.start(); prod.join(); cons.join();
            s = res;
            free(q);
        }
        auto dt = secs(t0);
        if (r >= 0) result("k10", v, "2^22", r, dt, s.to!string);
    }
}

void main(string[] args) {
    WARMUP = environment.get("WARMUP", "1").to!int;
    DATA = environment.get("MS_DATA", "/opt/msdata");
    string k = args[1], v = args[2], p = args.length > 4 ? args[4] : "";
    int reps = args[3].to!int;
    switch (k) {
        case "k1": runK1(v, reps); break;
        case "k2": runK2(v, reps, p); break;
        case "k3": runK3(v, reps); break;
        case "k4": runK4(v, reps); break;
        case "k5": runK5(v, reps); break;
        case "k6": runK6(v, reps, p); break;
        case "k7": runK7(v, reps); break;
        case "k8": runK8(v, reps); break;
        case "k9": runK9(v, reps); break;
        case "k10": runK10(v, reps); break;
        default: break;
    }
}

// ------------------------------------------------------------------ tailles
// v4, point 2 (docs/V4_SIZES.md) : sizes.inc, écrit par build.sh à partir des variables MS_* (sans elles, les valeurs
// publiées), est inséré à la compilation (import de chaîne, -J.) par le mixin ajouté au bout de la ligne de
// core.stdc.stdlib, en tête de fichier, pour ne pas décaler les numéros de ligne.
