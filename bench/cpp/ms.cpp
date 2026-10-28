// Implémentation C++26 (GCC 16 / libstdc++) des noyaux de docs/SPEC.md.
// « natural » : conteneurs et idiomes de la bibliothèque standard (vector, unordered_map,
// unique_ptr, vector<vector>, mutex + condition_variable). « tuned » : std::simd (C++26),
// std::atomic avec ordres explicites, alignas, std::pmr, extensions GCC documentées.
#include <algorithm>
#include <array>
#include <atomic>
#include <barrier>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <fstream>
#include <memory>
#include <memory_resource>
#include <mutex>
#include <new>
#include <queue>
#include <simd>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_map>
#include <vector>

namespace ss = std::simd;
using std::size_t;

// ------------------------------------------------------------------ harnais
static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static uint64_t now_ns() {
    return (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
static int warmup_count() { const char *w = std::getenv("WARMUP"); return w ? std::atoi(w) : 1; }
static void result(std::string_view k, std::string_view v, std::string_view p, int rep, double sec, const std::string &chk) {
    std::printf("RESULT;%.*s;%.*s;%.*s;%d;%.9f;%s\n", (int)k.size(), k.data(), (int)v.size(), v.data(), (int)p.size(), p.data(), rep, sec, chk.c_str());
    std::fflush(stdout);
}
template <class... A> static std::string fmt(const char *f, A... a) {
    char b[128];
    std::snprintf(b, sizeof b, f, a...);
    return b;
}
// allocateur aligné sur 64 octets (operator new aligné, C++17)
template <class T> struct Aligned64 {
    using value_type = T;
    Aligned64() = default;
    template <class U> Aligned64(const Aligned64<U> &) {}
    T *allocate(size_t n) { return static_cast<T *>(::operator new(n * sizeof(T), std::align_val_t{64})); }
    void deallocate(T *p, size_t) { ::operator delete(p, std::align_val_t{64}); }
    bool operator==(const Aligned64 &) const = default;
};
template <class T> using avec = std::vector<T, Aligned64<T>>;
template <class T> static avec<T> load(const std::string &name) {
    const char *d = std::getenv("MS_DATA");
    std::ifstream f(std::string(d ? d : "/opt/msdata") + "/" + name, std::ios::binary | std::ios::ate);
    if (!f) { std::perror(name.c_str()); std::exit(1); }
    size_t bytes = (size_t)f.tellg();
    avec<T> v(bytes / sizeof(T));
    f.seekg(0);
    f.read(reinterpret_cast<char *>(v.data()), (std::streamsize)bytes);
    return v;
}
template <class T> static void opaque(T &x) { asm volatile("" : "+r"(x) : : "memory"); }
// rend une valeur observable (empêche l'élimination d'un appel « pure » dont le résultat serait mort)
template <class T> static void keep(const T &x) { asm volatile("" : : "g"(x) : "memory"); }

// ------------------------------------------------------------------ K1
constexpr size_t N1 = 1 << 22;
struct Particle { float x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density; };
static_assert(sizeof(Particle) == 64);

[[gnu::noinline]] static double k1_natural(const std::vector<Particle> &ps) {
    double e = 0;
    for (const auto &p : ps) e += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz);
    return e;
}
// AoS optimisé : calcul f32, 8 accumulateurs f64 (ILP), vectorisé par le compilateur (même code que C)
[[gnu::noinline]] static double k1_aos(const Particle *__restrict p, size_t n) {
    double acc[8] = {};
    for (size_t i = 0; i < n; i += 8)
        for (int k = 0; k < 8; k++) {
            const Particle &q = p[i + k];
            acc[k] += (double)(0.5f * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz));
        }
    double e = 0;
    for (double a : acc) e += a;
    return e;
}
// SoA optimisé : std::simd (16 × f32), conversion f64 et 4 accumulateurs
[[gnu::noinline]] static double k1_soa(const float *vx, const float *vy, const float *vz, const float *m, size_t n) {
    using F = ss::vec<float, 16>;
    using D = ss::vec<double, 8>;
    D a0 = 0, a1 = 0, a2 = 0, a3 = 0;
    const F h = 0.5f;
    for (size_t i = 0; i < n; i += 32) {
        for (int u = 0; u < 2; u++) {
            size_t j = i + 16 * (size_t)u;
            F x = ss::unchecked_load<F>(vx + j, 16, ss::flag_aligned), y = ss::unchecked_load<F>(vy + j, 16, ss::flag_aligned);
            F z = ss::unchecked_load<F>(vz + j, 16, ss::flag_aligned), w = ss::unchecked_load<F>(m + j, 16, ss::flag_aligned);
            F e = h * w * (x * x + y * y + z * z);
            ss::vec<double, 16> ed = e;
            auto [lo, hi] = ss::chunk<8>(ed);
            if (u == 0) { a0 += lo; a1 += hi; } else { a2 += lo; a3 += hi; }
        }
    }
    return ss::reduce((a0 + a1) + (a2 + a3));
}
static void run_k1(std::string_view v, int reps) {
    if (v == "footprint0") return result("k1", v, "energy", 0, 0, "0");
    auto raw = load<Particle>("k1_particles.f32");
    const int W = warmup_count();
    if (v == "soa") {
        std::array<avec<float>, 16> f;
        for (int k = 0; k < 16; k++) {
            f[k].resize(N1);
            for (size_t i = 0; i < N1; i++) f[k][i] = reinterpret_cast<const float *>(&raw[i])[k];
        }
        raw = {};
        for (int r = -W; r < reps; r++) {
            double t0 = now();
            double e = k1_soa(f[3].data(), f[4].data(), f[5].data(), f[9].data(), N1);
            double t1 = now();
            if (r >= 0) result("k1", v, "energy", r, t1 - t0, fmt("%.6f", e));
        }
        return;
    }
    if (v == "aos") {
        for (int r = -W; r < reps; r++) {
            double t0 = now();
            double e = k1_aos(raw.data(), N1);
            double t1 = now();
            if (r >= 0) result("k1", v, "energy", r, t1 - t0, fmt("%.6f", e));
        }
        return;
    }
    // natural : std::vector<Particle> (valeurs contiguës : le parcours reste séquentiel même mélangé)
    std::vector<Particle> ps(raw.begin(), raw.end());
    raw = {};
    if (v == "footprint") return result("k1", v, "energy", 0, 0, fmt("%.6f", k1_natural(ps)));
    if (v == "natural_shuffled") {
        auto perm = load<uint32_t>("k1_perm.u32");
        std::vector<Particle> s;
        s.reserve(N1);
        for (uint32_t j : perm) s.push_back(ps[j]);
        ps = std::move(s);
    }
    for (int r = -W; r < reps; r++) {
        double t0 = now();
        double e = k1_natural(ps);
        double t1 = now();
        if (r >= 0) result("k1", v, "energy", r, t1 - t0, fmt("%.6f", e));
    }
}

// ------------------------------------------------------------------ K2
[[gnu::noinline]] static uint32_t k2_chase(const uint32_t *a, long h) {
    uint32_t i = 0;
    for (long k = 0; k < h; k++) i = a[i];
    return i;
}
static void run_k2(std::string_view v, int reps, std::string_view p) {
    auto a = load<uint32_t>("k2_chase_" + std::string(p) + ".u32");
    for (int r = -warmup_count(); r < reps; r++) {
        double t0 = now();
        uint32_t i = k2_chase(a.data(), 4200000);
        double t1 = now();
        if (r >= 0) result("k2", v, p, r, t1 - t0, std::to_string(i));
    }
}

// ------------------------------------------------------------------ K3
constexpr long ITER3 = 1L << 25;
struct alignas(128) PaddedCounter { std::atomic<uint64_t> v{0}; };
static void run_k3(std::string_view v, int reps) {
    const bool padded = v.ends_with("padded"), rmw = v.starts_with("rmw");
    std::printf("META;k3_mechanism;%s\n", rmw ? "std::atomic::fetch_add(memory_order_relaxed) (lock add)"
                                              : "std::atomic load/store memory_order_relaxed (mov)");
    std::printf("META;hardware_destructive_interference_size;%zu\n", std::hardware_destructive_interference_size);
    std::array<std::atomic<uint64_t>, 4> packed{};
    std::array<PaddedCounter, 4> pad{};
    auto ctr = [&](int t) -> std::atomic<uint64_t> & { return padded ? pad[t].v : packed[t]; };
    for (int r = -warmup_count(); r < reps; r++) {
        for (int t = 0; t < 4; t++) ctr(t).store(0);
        double t0 = now();
        {
            std::array<std::jthread, 4> th;
            for (int t = 0; t < 4; t++)
                th[t] = std::jthread([&c = ctr(t), rmw] {
                    if (rmw)
                        for (long i = 0; i < ITER3; i++) c.fetch_add(1, std::memory_order_relaxed);
                    else
                        for (long i = 0; i < ITER3; i++) c.store(c.load(std::memory_order_relaxed) + 1, std::memory_order_relaxed);
                });
        }  // join
        double t1 = now();
        uint64_t s = 0;
        for (int t = 0; t < 4; t++) s += ctr(t).load();
        if (r >= 0) result("k3", v, "4x2^25", r, t1 - t0, std::to_string(s));
    }
}

// ------------------------------------------------------------------ K4
[[gnu::noinline]] static uint64_t k4_natural(const std::vector<uint8_t> &v) {
    uint64_t s = 0;
    for (uint8_t x : v)
        if (x >= 128) s += x;
    return s;
}
[[gnu::noinline]] static uint64_t k4_branchless(const std::vector<uint8_t> &v) {
    uint64_t s = 0;
    for (uint8_t x : v) s += (uint64_t)x * (x >> 7);
    return s;
}
static void run_k4(std::string_view v, int reps) {
    auto a = load<uint8_t>("k4_bytes.u8");
    std::vector<uint8_t> d(a.begin(), a.end());
    if (v == "natural_sorted") std::ranges::sort(d);  // hors chrono
    const bool bl = v == "branchless_unsorted";
    for (int r = -warmup_count(); r < reps; r++) {
        double t0 = now();
        uint64_t s = bl ? k4_branchless(d) : k4_natural(d);
        double t1 = now();
        if (r >= 0) result("k4", v, "16M", r, t1 - t0, std::to_string(s));
    }
}

// ------------------------------------------------------------------ K5
constexpr int N5 = 2048, INNER5 = 1 << 16;
[[gnu::noinline]] static float k5_natural(const float *a, const float *b, int n) {
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}
// std::simd : 4 accumulateurs de 16 f32 (réassociation explicite), chargements alignés
[[gnu::noinline]] static float k5_tuned(const float *a, const float *b, int n) {
    using F = ss::vec<float, 16>;
    F s0 = 0.f, s1 = 0.f, s2 = 0.f, s3 = 0.f;
    for (int i = 0; i < n; i += 64) {
        s0 += ss::unchecked_load<F>(a + i, 16, ss::flag_aligned) * ss::unchecked_load<F>(b + i, 16, ss::flag_aligned);
        s1 += ss::unchecked_load<F>(a + i + 16, 16, ss::flag_aligned) * ss::unchecked_load<F>(b + i + 16, 16, ss::flag_aligned);
        s2 += ss::unchecked_load<F>(a + i + 32, 16, ss::flag_aligned) * ss::unchecked_load<F>(b + i + 32, 16, ss::flag_aligned);
        s3 += ss::unchecked_load<F>(a + i + 48, 16, ss::flag_aligned) * ss::unchecked_load<F>(b + i + 48, 16, ss::flag_aligned);
    }
    return ss::reduce((s0 + s1) + (s2 + s3));
}
static void run_k5(std::string_view v, int reps) {
    auto a = load<float>("k5_a.f32"), b = load<float>("k5_b.f32");
    const bool tuned = v == "tuned";
    for (int r = -warmup_count(); r < reps; r++) {
        float d = 0;
        double t0 = now();
        for (int it = 0; it < INNER5; it++) {
            const float *pa = a.data();
            opaque(pa);
            d = tuned ? k5_tuned(pa, b.data(), N5) : k5_natural(pa, b.data(), N5);
            keep(d);
        }
        double t1 = now();
        if (r >= 0) result("k5", v, "2048x65536", r, t1 - t0, fmt("%.4f", d));
    }
}

// ------------------------------------------------------------------ K6
constexpr size_t N6 = 1 << 24;
struct Cols {
    avec<int32_t> sd, pr;
    avec<uint8_t> q, d, t, rf, ls;
};
using Q1Acc = std::array<std::array<int64_t, 5>, 6>;  // count, qty, price, disc_price, charge

[[gnu::noinline]] static int64_t q6_natural(const Cols &c, size_t lo, size_t hi) {
    int64_t s = 0;
    for (size_t i = lo; i < hi; i++)
        if (c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24) s += (int64_t)c.pr[i] * c.d[i];
    return s;
}
[[gnu::noinline]] static void q1_natural(const Cols &c, size_t lo, size_t hi, Q1Acc &acc) {
    for (size_t i = lo; i < hi; i++) {
        if (c.sd[i] <= 10471) {
            auto &a = acc[c.rf[i] * 2 + c.ls[i]];
            int64_t p = c.pr[i], dp = p * (100 - c.d[i]);
            a[0] += 1;
            a[1] += c.q[i];
            a[2] += p;
            a[3] += dp;
            a[4] += dp * (100 + c.t[i]);
        }
    }
}
using I16 = ss::vec<int32_t, 16>;
using U8x16 = ss::vec<uint8_t, 16>;
static I16 ld32(const int32_t *p) { return ss::unchecked_load<I16>(p, 16); }
static I16 ld8(const uint8_t *p) { return I16(ss::unchecked_load<U8x16>(p, 16)); }
// Q6 std::simd : prédicat en masque, produit 32 bits, accumulateur 32 bits vidé tous les 256 pas
[[gnu::noinline]] static int64_t q6_tuned(const Cols &c, size_t lo, size_t hi) {
    int64_t s = 0;
    size_t i = lo;
    while (i + 16 <= hi) {
        I16 acc = 0;
        size_t end = std::min(hi - (hi - i) % 16, i + 256 * 16);
        for (; i < end; i += 16) {
            I16 sd = ld32(&c.sd[i]), d = ld8(&c.d[i]), q = ld8(&c.q[i]), p = ld32(&c.pr[i]);
            auto m = (sd >= 8766) && (sd < 9131) && (d >= 5) && (d <= 7) && (q < 24);
            acc += ss::select(m, p * d, I16(0));
        }
        s += ss::reduce(ss::vec<int64_t, 16>(acc));
    }
    return s + q6_natural(c, i, hi);
}
// Q1 std::simd : 16 lignes par pas, agrégation masquée par groupe ; accumulateurs 32 bits
// vidés tous les 4096 lignes, colonne charge en 64 bits.
[[gnu::noinline]] static void q1_tuned(const Cols &c, size_t lo, size_t hi, Q1Acc &acc) {
    using L16 = ss::vec<int64_t, 16>;
    size_t i = lo;
    while (i + 16 <= hi) {
        std::array<I16, 6> aq{}, ap{}, adp{};
        std::array<L16, 6> ach{};
        std::array<int64_t, 6> cnt{};
        size_t end = std::min(hi - (hi - i) % 16, i + 4096);
        for (; i < end; i += 16) {
            auto pass = ld32(&c.sd[i]) <= 10471;
            I16 g = ld8(&c.rf[i]) * 2 + ld8(&c.ls[i]);
            I16 q = ld8(&c.q[i]), p = ld32(&c.pr[i]);
            I16 dp = p * (100 - ld8(&c.d[i]));
            L16 ch = L16(dp) * L16(100 + ld8(&c.t[i]));
            for (int k = 0; k < 6; k++) {
                auto m = pass && (g == k);
                cnt[k] += ss::reduce_count(m);
                aq[k] += ss::select(m, q, I16(0));
                ap[k] += ss::select(m, p, I16(0));
                adp[k] += ss::select(m, dp, I16(0));
                ach[k] += ss::select(ss::mask<int64_t, 16>(m), ch, L16(0));
            }
        }
        for (int k = 0; k < 6; k++) {
            acc[k][0] += cnt[k];
            acc[k][1] += ss::reduce(aq[k]);
            acc[k][2] += ss::reduce(L16(ap[k]));
            acc[k][3] += ss::reduce(L16(adp[k]));
            acc[k][4] += ss::reduce(ach[k]);
        }
    }
    if (i < hi) q1_natural(c, i, hi, acc);
}
static void run_k6(std::string_view v, int reps, std::string_view p) {
    Cols c{load<int32_t>("k6_shipdate.i32"), load<int32_t>("k6_extendedprice.i32"), load<uint8_t>("k6_quantity.u8"),
           load<uint8_t>("k6_discount.u8"),  load<uint8_t>("k6_tax.u8"),            load<uint8_t>("k6_returnflag.u8"),
           load<uint8_t>("k6_linestatus.u8")};
    const bool q1 = p == "q1";
    for (int r = -warmup_count(); r < reps; r++) {
        Q1Acc acc{};
        int64_t s6 = 0;
        double t0 = now();
        if (v == "mt") {
            std::array<Q1Acc, 4> part{};
            std::array<int64_t, 4> p6{};
            {
                std::array<std::jthread, 4> th;
                for (int t = 0; t < 4; t++)
                    th[t] = std::jthread([&, t] {
                        size_t lo = N6 * t / 4, hi = N6 * (t + 1) / 4;
                        if (q1) q1_tuned(c, lo, hi, part[t]); else p6[t] = q6_tuned(c, lo, hi);
                    });
            }
            for (int t = 0; t < 4; t++) {
                s6 += p6[t];
                for (int g = 0; g < 6; g++) for (int k = 0; k < 5; k++) acc[g][k] += part[t][g][k];
            }
        } else if (v == "tuned") {
            if (q1) q1_tuned(c, 0, N6, acc); else s6 = q6_tuned(c, 0, N6);
        } else {
            if (q1) q1_natural(c, 0, N6, acc); else s6 = q6_natural(c, 0, N6);
        }
        double t1 = now();
        if (q1) for (auto &g : acc) for (int64_t x : g) s6 += x;
        if (r >= 0) result("k6", v, p, r, t1 - t0, std::to_string(s6));
    }
}

// ------------------------------------------------------------------ K7
constexpr size_t N7 = 1 << 24;
struct Agg { uint32_t count = 0; uint64_t sum = 0; };
struct Slot7 { uint32_t key, count; uint64_t sum; };  // 16 octets, 4 par ligne
static void run_k7(std::string_view v, int reps) {
    auto keys = load<uint32_t>("k7_keys.u32"), vals = load<uint32_t>("k7_vals.u32");
    for (int r = -warmup_count(); r < reps; r++) {
        uint64_t nk = 0, ws = 0;
        double t0, t1;
        if (v == "natural") {
            t0 = now();
            std::unordered_map<uint32_t, Agg> m;
            for (size_t i = 0; i < N7; i++) {
                auto &e = m[keys[i]];
                e.count++;
                e.sum += vals[i];
            }
            t1 = now();
            for (const auto &[k, e] : m) { nk++; ws += e.sum * ((k & 1023) + 1); }
        } else {  // adressage ouvert, sondage linéaire, hachage de Fibonacci, lots préchargés
            constexpr int LOG = 21, BATCH = 16;
            constexpr uint32_t CAP = 1u << LOG;
            t0 = now();
            avec<Slot7> tab(CAP);  // value-initialisée (mise à zéro)
            for (size_t i = 0; i < N7; i += BATCH) {
                uint32_t h[BATCH];
                for (int b = 0; b < BATCH; b++) {
                    h[b] = (keys[i + b] * 0x9E3779B1u) >> (32 - LOG);
                    __builtin_prefetch(&tab[h[b]], 1, 0);
                }
                for (int b = 0; b < BATCH; b++) {
                    uint32_t k = keys[i + b], s = h[b];
                    while (tab[s].count && tab[s].key != k) s = (s + 1) & (CAP - 1);
                    tab[s].key = k;
                    tab[s].count++;
                    tab[s].sum += vals[i + b];
                }
            }
            t1 = now();
            for (const auto &s : tab)
                if (s.count) { nk++; ws += s.sum * ((s.key & 1023) + 1); }
        }
        if (r >= 0) result("k7", v, "16M/1M", r, t1 - t0, fmt("%llu:%llu", (unsigned long long)nk, (unsigned long long)ws));
    }
}

// ------------------------------------------------------------------ K8
struct Node8 { int64_t v; std::unique_ptr<Node8> l, r; };
static std::unique_ptr<Node8> t8_build(int depth, int64_t &counter) {
    auto n = std::make_unique<Node8>();
    n->v = counter++;
    if (depth > 0) { n->l = t8_build(depth - 1, counter); n->r = t8_build(depth - 1, counter); }
    return n;
}
static int64_t t8_sum(const Node8 *n) { return n ? n->v + t8_sum(n->l.get()) + t8_sum(n->r.get()) : 0; }
// tuned : nœuds indexés dans un vecteur réutilisé
struct ANode { int64_t v; int32_t l, r; };
static int32_t a8_build(std::vector<ANode> &a, int32_t &top, int depth, int64_t &counter) {
    int32_t i = top++;
    a[i].v = counter++;
    if (depth > 0) { int32_t l = a8_build(a, top, depth - 1, counter); a[i].l = l; a[i].r = a8_build(a, top, depth - 1, counter); }
    else a[i].l = a[i].r = -1;
    return i;
}
static int64_t a8_sum(const std::vector<ANode> &a, int32_t i) { return i < 0 ? 0 : a[i].v + a8_sum(a, a[i].l) + a8_sum(a, a[i].r); }
// tuned_alloc : nœuds à pointeurs alloués dans une std::pmr::monotonic_buffer_resource réinitialisée
struct PNode { int64_t v; PNode *l, *r; };
static PNode *p8_build(std::pmr::polymorphic_allocator<PNode> &al, int depth, int64_t &counter) {
    PNode *n = al.allocate(1);
    n->v = counter++;
    if (depth > 0) { n->l = p8_build(al, depth - 1, counter); n->r = p8_build(al, depth - 1, counter); }
    else n->l = n->r = nullptr;
    return n;
}
static int64_t p8_sum(const PNode *n) { return n ? n->v + p8_sum(n->l) + p8_sum(n->r) : 0; }
static void run_k8(std::string_view v, int reps) {
    constexpr int Q = 16384, D = 10;
    int64_t cnt = 0;
    auto longlived = t8_build(20, cnt);
    const int64_t lsum = t8_sum(longlived.get());
    std::vector<uint64_t> lat(Q);
    std::vector<ANode> arena(2047);
    alignas(64) static std::byte buf[2047 * sizeof(PNode) + 4096];
    std::pmr::monotonic_buffer_resource mono(buf, sizeof buf, std::pmr::null_memory_resource());
    std::pmr::polymorphic_allocator<PNode> al(&mono);
    for (int r = -warmup_count(); r < reps; r++) {
        int64_t total = 0;
        double t0 = now();
        for (int q = 0; q < Q; q++) {
            uint64_t a = now_ns();
            int64_t c = q, s;
            if (v == "tuned") { int32_t top = 0; int32_t root = a8_build(arena, top, D, c); s = a8_sum(arena, root); }
            else if (v == "tuned_alloc") { mono.release(); s = p8_sum(p8_build(al, D, c)); }
            else { auto t = t8_build(D, c); s = t8_sum(t.get()); }  // libération récursive par ~unique_ptr
            total += s;
            lat[q] = now_ns() - a;
        }
        double t1 = now();
        if (r >= 0) {
            result("k8", v, "16384x2047", r, t1 - t0, std::to_string(total + lsum));
            std::ranges::sort(lat);
            std::printf("LAT;%.*s;%llu;%llu;%llu;%llu;%llu\n", (int)v.size(), v.data(), (unsigned long long)lat[Q / 2],
                        (unsigned long long)lat[Q * 9 / 10], (unsigned long long)lat[Q * 99 / 100], (unsigned long long)lat[Q * 999 / 1000],
                        (unsigned long long)lat[Q - 1]);
        }
    }
}

// ------------------------------------------------------------------ K9
constexpr int M9 = 2048, IT9 = 4;
static double k9_init(int i, int j) { return (double)((i * 31 + j * 17) % 1024) / 1024.0; }
// naturel : std::vector<std::vector<double>>
[[gnu::noinline]] static void k9_natural(const std::vector<std::vector<double>> &in, std::vector<std::vector<double>> &out) {
    for (int i = 1; i < M9 - 1; i++)
        for (int j = 1; j < M9 - 1; j++) out[i][j] = 0.25 * (((in[i - 1][j] + in[i + 1][j]) + in[i][j - 1]) + in[i][j + 1]);
}
[[gnu::noinline]] static void k9_rows(const double *__restrict in, double *__restrict out, int r0, int r1) {
    for (int i = r0; i < r1; i++) {
        const double *__restrict up = in + (size_t)(i - 1) * M9, *__restrict mid = in + (size_t)i * M9, *__restrict dn = in + (size_t)(i + 1) * M9;
        double *__restrict o = out + (size_t)i * M9;
        for (int j = 1; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
static void run_k9(std::string_view v, int reps) {
    for (int r = -warmup_count(); r < reps; r++) {
        double s = 0, t0, t1;
        if (v == "natural") {
            std::vector<std::vector<double>> a(M9, std::vector<double>(M9));
            for (int i = 0; i < M9; i++) for (int j = 0; j < M9; j++) a[i][j] = k9_init(i, j);
            auto b = a;
            t0 = now();
            for (int it = 0; it < IT9; it++) { k9_natural(a, b); std::swap(a, b); }
            t1 = now();
            for (const auto &row : a) for (double x : row) s += x;
        } else {
            avec<double> a((size_t)M9 * M9);
            for (int i = 0; i < M9; i++) for (int j = 0; j < M9; j++) a[(size_t)i * M9 + j] = k9_init(i, j);
            avec<double> b = a;
            double *in = a.data(), *out = b.data();
            t0 = now();
            for (int it = 0; it < IT9; it++) {
                if (v == "tuned") k9_rows(in, out, 1, M9 - 1);
                else {
                    std::array<std::jthread, 4> th;
                    for (int t = 0; t < 4; t++) th[t] = std::jthread(k9_rows, in, out, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4);
                }
                std::swap(in, out);
            }
            t1 = now();
            for (size_t k = 0; k < (size_t)M9 * M9; k++) s += in[k];
        }
        if (r >= 0) result("k9", v, "2048^2x4", r, t1 - t0, fmt("%.15e", s));
    }
}

// ------------------------------------------------------------------ K10
constexpr uint64_t M10 = 1 << 22;
constexpr size_t CAP10 = 1 << 14;
// naturel : file bornée std::queue (deque) + std::mutex + 2 std::condition_variable
struct BQueue {
    std::queue<uint64_t> q;
    std::mutex mu;
    std::condition_variable not_empty, not_full;
};
// tuned : anneau SPSC (Lamport + indices distants en cache), acquire/release, lignes séparées
struct Spsc {
    alignas(128) std::atomic<size_t> write_idx{0};
    alignas(128) size_t read_idx_cache = 0;  // côté producteur
    alignas(128) std::atomic<size_t> read_idx{0};
    alignas(128) size_t write_idx_cache = 0;  // côté consommateur
    alignas(128) std::array<uint64_t, CAP10> buf;
};
static void run_k10(std::string_view v, int reps) {
    const bool tuned = v == "tuned";
    for (int r = -warmup_count(); r < reps; r++) {
        uint64_t sum = 0;
        double t0, t1;
        if (tuned) {
            auto sq = std::make_unique<Spsc>();
            t0 = now();
            {
                std::jthread cons([&] {
                    size_t rd = 0;
                    uint64_t s = 0;
                    for (uint64_t k = 0; k < M10; k++) {
                        while (rd == sq->write_idx_cache) {
                            sq->write_idx_cache = sq->write_idx.load(std::memory_order_acquire);
                            if (rd == sq->write_idx_cache) __builtin_ia32_pause();
                        }
                        s += sq->buf[rd & (CAP10 - 1)];
                        sq->read_idx.store(++rd, std::memory_order_release);
                    }
                    sum = s;
                });
                std::jthread prod([&] {
                    size_t w = 0;
                    for (uint64_t x = 1; x <= M10; x++) {
                        while (w - sq->read_idx_cache == CAP10) {
                            sq->read_idx_cache = sq->read_idx.load(std::memory_order_acquire);
                            if (w - sq->read_idx_cache == CAP10) __builtin_ia32_pause();
                        }
                        sq->buf[w & (CAP10 - 1)] = x;
                        sq->write_idx.store(++w, std::memory_order_release);
                    }
                });
            }
            t1 = now();
        } else {
            BQueue bq;
            t0 = now();
            {
                std::jthread cons([&] {
                    uint64_t s = 0;
                    for (uint64_t k = 0; k < M10; k++) {
                        std::unique_lock lk(bq.mu);
                        bq.not_empty.wait(lk, [&] { return !bq.q.empty(); });
                        s += bq.q.front();
                        bq.q.pop();
                        lk.unlock();
                        bq.not_full.notify_one();
                    }
                    sum = s;
                });
                std::jthread prod([&] {
                    for (uint64_t x = 1; x <= M10; x++) {
                        std::unique_lock lk(bq.mu);
                        bq.not_full.wait(lk, [&] { return bq.q.size() < CAP10; });
                        bq.q.push(x);
                        lk.unlock();
                        bq.not_empty.notify_one();
                    }
                });
            }
            t1 = now();
        }
        if (r >= 0) result("k10", v, "2^22", r, t1 - t0, std::to_string(sum));
    }
}

// ------------------------------------------------------------------ main
int main(int argc, char **argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: %s kernel variant reps [param]\n", argv[0]); return 1; }
    std::string_view k = argv[1], v = argv[2], p = argc > 4 ? argv[4] : "";
    int reps = std::atoi(argv[3]);
    if (k == "k1") run_k1(v, reps);
    else if (k == "k2") run_k2(v, reps, p);
    else if (k == "k3") run_k3(v, reps);
    else if (k == "k4") run_k4(v, reps);
    else if (k == "k5") run_k5(v, reps);
    else if (k == "k6") run_k6(v, reps, p);
    else if (k == "k7") run_k7(v, reps);
    else if (k == "k8") run_k8(v, reps);
    else if (k == "k9") run_k9(v, reps);
    else if (k == "k10") run_k10(v, reps);
    else { std::fprintf(stderr, "kernel inconnu %s\n", argv[1]); return 1; }
}
