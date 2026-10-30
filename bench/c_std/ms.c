// Copie « standard » de bench/c/ms.c pour la confrontation (docs/CONFRONTATION.md, section 4) : le code des
// noyaux n'utilise que la norme ISO C23 et sa bibliothèque. Chaque changement est marqué « standard : ».
// Le harnais (chronométrage POSIX, barrières asm, noinline, lecture de la RSS) est exempté, comme dans le plan.
#define _GNU_SOURCE
#include <stdatomic.h>
#include <threads.h>   // standard : threads C11 au lieu des threads POSIX
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// ------------------------------------------------------------------ harnais
static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + (double)t.tv_nsec * 1e-9;
}
static uint64_t now_ns(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}
static const char *data_dir(void) {
    const char *d = getenv("MS_DATA");
    return d ? d : "/opt/msdata";
}
static void *load(const char *name, size_t *bytes) {
    char path[4096];
    snprintf(path, sizeof path, "%s/%s", data_dir(), name);
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(1); }
    fseek(f, 0, SEEK_END);
    size_t n = (size_t)ftell(f);
    fseek(f, 0, SEEK_SET);
    void *p = aligned_alloc(64, (n + 63) & ~(size_t)63);
    if (fread(p, 1, n, f) != n) { perror("fread"); exit(1); }
    fclose(f);
    if (bytes) *bytes = n;
    return p;
}
static int warmup_count(void) {
    const char *w = getenv("WARMUP");
    return w ? atoi(w) : 1;
}
static void result(const char *k, const char *v, const char *p, int rep, double sec, const char *chk) {
    printf("RESULT;%s;%s;%s;%d;%.9f;%s\n", k, v, p, rep, sec, chk);
    fflush(stdout);
}
#define BARRIER(p) __asm__ volatile("" : : "r"(p) : "memory")
// rend une valeur observable : sans cela, gcc élimine les appels « pure » dont le résultat est écrasé
#define KEEP(x) __asm__ volatile("" : : "g"(x) : "memory")

// ------------------------------------------------------------------ K1
enum { N1 = 1 << 22 };
typedef struct {
    float x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density;
} Particle;

// Code « naturel » : boucle simple, accumulation double.
__attribute__((noinline)) static double k1_natural(const Particle *p, size_t n) {
    double e = 0;
    for (size_t i = 0; i < n; i++)
        e += 0.5 * p[i].mass * (p[i].vx * p[i].vx + p[i].vy * p[i].vy + p[i].vz * p[i].vz);
    return e;
}
// AoS optimisé : calcul f32, 8 accumulateurs double (ILP), le compilateur vectorise.
__attribute__((noinline)) static double k1_aos(const Particle *restrict p, size_t n) {
    double acc[8] = {0};
    for (size_t i = 0; i < n; i += 8)
        for (int k = 0; k < 8; k++) {
            const Particle *q = &p[i + k];
            acc[k] += (double)(0.5f * q->mass * (q->vx * q->vx + q->vy * q->vy + q->vz * q->vz));
        }
    double e = 0;
    for (int k = 0; k < 8; k++) e += acc[k];
    return e;
}
// SoA optimisé, f32 -> f64 pour l'accumulation.
// standard : 32 sommes partielles explicites (les 4 x 8 voies double de la version AVX-512), sans intrinsèques ;
// le compilateur les vectorise.
__attribute__((noinline)) static double k1_soa(const float *restrict vx, const float *restrict vy,
                                               const float *restrict vz, const float *restrict m, size_t n) {
    double acc[32] = {0};
    for (size_t i = 0; i < n; i += 32)
        for (int k = 0; k < 32; k++) {
            size_t j = i + (size_t)k;
            float v2 = vx[j] * vx[j] + vy[j] * vy[j] + vz[j] * vz[j];
            acc[k] += (double)(0.5f * m[j] * v2);
        }
    double e = 0;
    for (int k = 0; k < 32; k++) e += acc[k];
    return e;
}

// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)
static long rss_now(void) {
    long size = 0, res = 0;
    FILE *f = fopen("/proc/self/statm", "r");
    if (f) {
        if (fscanf(f, "%ld %ld", &size, &res) != 2) res = 0;
        fclose(f);
    }
    return res * 4096;
}

static void run_k1(const char *variant, int reps) {
    size_t bytes;
    if (!strcmp(variant, "footprint0") || !strcmp(variant, "footprint_raw")) { result("k1", variant, "energy", 0, 0, "0"); return; }
    long m1 = !strcmp(variant, "footprint") ? rss_now() : 0; // P1 : avant la lecture (la collection naturelle est le tableau lu)
    Particle *src = load("k1_particles.f32", &bytes);
    char chk[64], par[] = "energy";
    int W = warmup_count();
    if (!strcmp(variant, "footprint")) {
        // la collection naturelle en C est déjà ce tableau de structs ; P2 : après la lecture
        long m2 = rss_now();
        printf("META;mem;rss;%ld;%ld\nMETA;rss;%ld;%ld\n", m1, m2, m1, m2);
        snprintf(chk, sizeof chk, "%.6f", k1_natural(src, N1));
        result("k1", variant, par, 0, 0, chk);
        return;
    }
    if (!strcmp(variant, "soa")) {
        float *f[16];
        for (int k = 0; k < 16; k++) {
            f[k] = aligned_alloc(64, N1 * sizeof(float));
            for (size_t i = 0; i < N1; i++) f[k][i] = ((float *)&src[i])[k];
        }
        free(src);
        for (int r = -W; r < reps; r++) {
            double t0 = now();
            double e = k1_soa(f[3], f[4], f[5], f[9], N1);
            double t1 = now();
            snprintf(chk, sizeof chk, "%.6f", e);
            if (r >= 0) result("k1", variant, par, r, t1 - t0, chk);
        }
        return;
    }
    if (!strcmp(variant, "natural_shuffled")) {
        uint32_t *perm = load("k1_perm.u32", NULL);
        Particle *s = aligned_alloc(64, N1 * sizeof(Particle));
        for (size_t j = 0; j < N1; j++) s[j] = src[perm[j]];
        free(src); free(perm);
        src = s;
    }
    for (int r = -W; r < reps; r++) {
        double t0 = now();
        double e = !strcmp(variant, "aos") ? k1_aos(src, N1) : k1_natural(src, N1);
        double t1 = now();
        snprintf(chk, sizeof chk, "%.6f", e);
        if (r >= 0) result("k1", variant, par, r, t1 - t0, chk);
    }
}

// ------------------------------------------------------------------ K2
__attribute__((noinline)) static uint32_t k2_chase(const uint32_t *a, long h) {
    uint32_t i = 0;
    for (long k = 0; k < h; k++) i = a[i];
    return i;
}
static void run_k2(const char *variant, int reps, const char *param) {
    char name[64], chk[32];
    snprintf(name, sizeof name, "k2_chase_%s.u32", param);
    uint32_t *a = load(name, NULL);
    long H = 4200000;
    for (int r = -warmup_count(); r < reps; r++) {
        double t0 = now();
        uint32_t i = k2_chase(a, H);
        double t1 = now();
        snprintf(chk, sizeof chk, "%u", i);
        if (r >= 0) result("k2", variant, param, r, t1 - t0, chk);
    }
}

// ------------------------------------------------------------------ K3
enum { ITER3 = 1 << 25 };
typedef struct { _Atomic uint64_t *c; int rmw; } K3Arg;
static int k3_worker(void *v) {  // standard : signature de thrd_start_t
    K3Arg *a = v;
    _Atomic uint64_t *c = a->c;
    if (a->rmw)
        for (long i = 0; i < ITER3; i++) atomic_fetch_add_explicit(c, 1, memory_order_relaxed);
    else
        for (long i = 0; i < ITER3; i++)
            atomic_store_explicit(c, atomic_load_explicit(c, memory_order_relaxed) + 1, memory_order_relaxed);
    return 0;
}
static void run_k3(const char *variant, int reps) {
    int padded = strstr(variant, "padded") != NULL, rmw = !strncmp(variant, "rmw", 3);
    _Atomic uint64_t *mem = aligned_alloc(128, 4 * 128);
    size_t stride = padded ? 16 : 1;  // en uint64 : 128 o ou 8 o
    printf("META;k3_mechanism;%s\n", rmw ? "atomic_fetch_add relaxed (lock xadd)" : "atomic_load/store relaxed (mov)");
    char chk[32];
    for (int r = -warmup_count(); r < reps; r++) {
        for (int t = 0; t < 4; t++) atomic_store(&mem[t * stride], 0);
        thrd_t th[4];  // standard : threads.h
        K3Arg arg[4];
        double t0 = now();
        for (int t = 0; t < 4; t++) { arg[t].c = &mem[t * stride]; arg[t].rmw = rmw; thrd_create(&th[t], k3_worker, &arg[t]); }
        for (int t = 0; t < 4; t++) thrd_join(th[t], NULL);
        double t1 = now();
        uint64_t s = 0;
        for (int t = 0; t < 4; t++) s += atomic_load(&mem[t * stride]);
        snprintf(chk, sizeof chk, "%llu", (unsigned long long)s);
        if (r >= 0) result("k3", variant, "4x2^25", r, t1 - t0, chk);
    }
}

// ------------------------------------------------------------------ K4
enum { N4 = 1 << 24 };
__attribute__((noinline)) static uint64_t k4_natural(const uint8_t *v, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++)
        if (v[i] >= 128) s += v[i];
    return s;
}
__attribute__((noinline)) static uint64_t k4_branchless(const uint8_t *v, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) s += (uint64_t)v[i] * (v[i] >> 7);
    return s;
}
static void run_k4(const char *variant, int reps) {
    uint8_t *v = load("k4_bytes.u8", NULL);
    if (!strcmp(variant, "natural_sorted")) {  // tri par comptage, hors chrono
        size_t cnt[256] = {0};
        for (size_t i = 0; i < N4; i++) cnt[v[i]]++;
        size_t k = 0;
        for (int b = 0; b < 256; b++) for (size_t c = 0; c < cnt[b]; c++) v[k++] = (uint8_t)b;
    }
    int bl = !strcmp(variant, "branchless_unsorted");
    char chk[32];
    for (int r = -warmup_count(); r < reps; r++) {
        double t0 = now();
        uint64_t s = bl ? k4_branchless(v, N4) : k4_natural(v, N4);
        double t1 = now();
        snprintf(chk, sizeof chk, "%llu", (unsigned long long)s);
        if (r >= 0) result("k4", variant, "16M", r, t1 - t0, chk);
    }
}

// ------------------------------------------------------------------ K5
enum { N5 = 2048, INNER5 = 1 << 16 };
__attribute__((noinline)) static float k5_natural(const float *a, const float *b, int n) {
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}
// standard : 64 sommes partielles explicites (les 4 accumulateurs de 16 voies de la version AVX-512), sans
// intrinsèques ; même ordre d'accumulation par voie, le compilateur les vectorise.
__attribute__((noinline)) static float k5_tuned(const float *restrict a, const float *restrict b, int n) {
    float s[64] = {0};
    for (int i = 0; i < n; i += 64)
        for (int k = 0; k < 64; k++) s[k] += a[i + k] * b[i + k];
    float t[16];
    for (int k = 0; k < 16; k++) t[k] = (s[k] + s[16 + k]) + (s[32 + k] + s[48 + k]);
    float d = 0;
    for (int k = 0; k < 16; k++) d += t[k];
    return d;
}
static void run_k5(const char *variant, int reps) {
    float *a = load("k5_a.f32", NULL), *b = load("k5_b.f32", NULL);
    int tuned = !strcmp(variant, "tuned");
    char chk[32];
    for (int r = -warmup_count(); r < reps; r++) {
        float d = 0;
        double t0 = now();
        for (int it = 0; it < INNER5; it++) {
            BARRIER(a);
            d = tuned ? k5_tuned(a, b, N5) : k5_natural(a, b, N5);
            KEEP(d);
        }
        double t1 = now();
        snprintf(chk, sizeof chk, "%.4f", d);
        if (r >= 0) result("k5", variant, "2048x65536", r, t1 - t0, chk);
    }
}

// ------------------------------------------------------------------ K6
enum { N6 = 1 << 24 };
typedef struct { int32_t *sd, *pr; uint8_t *q, *d, *t, *rf, *ls; } Cols;
typedef struct { int64_t a[6][5]; } Q1Acc;  // count, qty, price, disc_price, charge

__attribute__((noinline)) static int64_t q6_natural(const Cols *c, size_t lo, size_t hi) {
    int64_t s = 0;
    for (size_t i = lo; i < hi; i++)
        if (c->sd[i] >= 8766 && c->sd[i] < 9131 && c->d[i] >= 5 && c->d[i] <= 7 && c->q[i] < 24)
            s += (int64_t)c->pr[i] * c->d[i];
    return s;
}
// Q6 optimisé : prédicat évalué sans branchement, entier 32 bits, vectorisable par le compilateur.
__attribute__((noinline)) static int64_t q6_tuned(const int32_t *restrict sd, const uint8_t *restrict d,
                                                  const uint8_t *restrict q, const int32_t *restrict pr, size_t lo, size_t hi) {
    int64_t s = 0;
    for (size_t i = lo; i < hi; i++) {
        uint32_t m = ((uint32_t)(sd[i] - 8766) < 365u) & ((uint8_t)(d[i] - 5) <= 2) & (q[i] < 24);
        s += (int64_t)(pr[i] * (int32_t)d[i]) & -(int64_t)m;
    }
    return s;
}
__attribute__((noinline)) static void q1_natural(const Cols *c, size_t lo, size_t hi, Q1Acc *acc) {
    for (size_t i = lo; i < hi; i++) {
        if (c->sd[i] <= 10471) {
            int g = c->rf[i] * 2 + c->ls[i];
            int64_t p = c->pr[i], dp = p * (100 - c->d[i]);
            acc->a[g][0] += 1;
            acc->a[g][1] += c->q[i];
            acc->a[g][2] += p;
            acc->a[g][3] += dp;
            acc->a[g][4] += dp * (100 + c->t[i]);
        }
    }
}
// Q1 optimisé : 16 lignes par itération, agrégation masquée par groupe (6 groupes), accumulateurs 32 bits par
// voie vidés tous les 4096 lignes, colonne charge en 64 bits.
// standard : le même découpage que la version AVX-512, écrit avec des tableaux de 16 voies que le compilateur
// vectorise, sans intrinsèques ni _pext_u32 ni __builtin_popcount.
__attribute__((noinline)) static void q1_tuned(const Cols *c, size_t lo, size_t hi, Q1Acc *acc) {
    size_t i = lo;
    while (i + 16 <= hi) {
        int32_t cnt[6][16] = {0}, aq[6][16] = {0}, ap[6][16] = {0}, adp[6][16] = {0};
        int64_t ach[6][16] = {0};
        size_t end = i + 4096 <= hi ? i + 4096 : hi - (hi - i) % 16;
        for (; i < end; i += 16) {
            int32_t pass[16], g[16], q[16], p[16], dp[16];
            int64_t ch[16];
            for (int l = 0; l < 16; l++) {
                pass[l] = -(int32_t)(c->sd[i + l] <= 10471);
                g[l] = c->rf[i + l] * 2 + c->ls[i + l];
                q[l] = c->q[i + l];
                p[l] = c->pr[i + l];
                dp[l] = p[l] * (100 - c->d[i + l]);
                ch[l] = (int64_t)dp[l] * (100 + c->t[i + l]);
            }
            for (int gg = 0; gg < 6; gg++)
                for (int l = 0; l < 16; l++) {
                    int32_t m = pass[l] & -(int32_t)(g[l] == gg);
                    cnt[gg][l] -= m;
                    aq[gg][l] += q[l] & m;
                    ap[gg][l] += p[l] & m;
                    adp[gg][l] += dp[l] & m;
                    ach[gg][l] += ch[l] & (int64_t)m;
                }
        }
        for (int gg = 0; gg < 6; gg++)
            for (int l = 0; l < 16; l++) {
                acc->a[gg][0] += cnt[gg][l];
                acc->a[gg][1] += aq[gg][l];
                acc->a[gg][2] += ap[gg][l];
                acc->a[gg][3] += adp[gg][l];
                acc->a[gg][4] += ach[gg][l];
            }
    }
    if (i < hi) q1_natural(c, i, hi, acc);  // reste éventuel (< 16 lignes)
}
typedef struct { const Cols *c; size_t lo, hi; int q1; int64_t s6; Q1Acc acc; } K6Arg;
static int k6_worker(void *v) {  // standard : signature de thrd_start_t
    K6Arg *a = v;
    if (a->q1) q1_tuned(a->c, a->lo, a->hi, &a->acc);
    else a->s6 = q6_tuned(a->c->sd, a->c->d, a->c->q, a->c->pr, a->lo, a->hi);
    return 0;
}
static void run_k6(const char *variant, int reps, const char *param) {
    Cols c = {load("k6_shipdate.i32", NULL), load("k6_extendedprice.i32", NULL), load("k6_quantity.u8", NULL),
              load("k6_discount.u8", NULL), load("k6_tax.u8", NULL), load("k6_returnflag.u8", NULL),
              load("k6_linestatus.u8", NULL)};
    int q1 = !strcmp(param, "q1");
    char chk[32];
    for (int r = -warmup_count(); r < reps; r++) {
        Q1Acc acc;
        memset(&acc, 0, sizeof acc);
        int64_t s6 = 0;
        double t0 = now();
        if (!strcmp(variant, "mt")) {
            thrd_t th[4];  // standard : threads.h
            K6Arg arg[4];
            for (int t = 0; t < 4; t++) {
                memset(&arg[t], 0, sizeof arg[t]);
                arg[t].c = &c; arg[t].lo = (size_t)N6 * t / 4; arg[t].hi = (size_t)N6 * (t + 1) / 4; arg[t].q1 = q1;
                thrd_create(&th[t], k6_worker, &arg[t]);
            }
            for (int t = 0; t < 4; t++) {
                thrd_join(th[t], NULL);
                s6 += arg[t].s6;
                for (int g = 0; g < 6; g++) for (int k = 0; k < 5; k++) acc.a[g][k] += arg[t].acc.a[g][k];
            }
        } else if (!strcmp(variant, "tuned")) {
            if (q1) q1_tuned(&c, 0, N6, &acc); else s6 = q6_tuned(c.sd, c.d, c.q, c.pr, 0, N6);
        } else {
            if (q1) q1_natural(&c, 0, N6, &acc); else s6 = q6_natural(&c, 0, N6);
        }
        double t1 = now();
        if (q1) for (int g = 0; g < 6; g++) for (int k = 0; k < 5; k++) s6 += acc.a[g][k];
        snprintf(chk, sizeof chk, "%lld", (long long)s6);
        if (r >= 0) result("k6", variant, param, r, t1 - t0, chk);
    }
}

// ------------------------------------------------------------------ K7
enum { N7 = 1 << 24 };
// Naturel en C (pas de table standard) : chaînage séparé à la K&R, un malloc par entrée.
typedef struct Node7 { uint32_t key; uint32_t count; uint64_t sum; struct Node7 *next; } Node7;
typedef struct { uint32_t key, count; uint64_t sum; } Slot7;  // 16 octets, 4 par ligne

static void k7_checksum(char *out, size_t n, uint64_t nkeys, uint64_t wsum) {
    snprintf(out, n, "%llu:%llu", (unsigned long long)nkeys, (unsigned long long)wsum);
}
static void run_k7(const char *variant, int reps) {
    uint32_t *keys = load("k7_keys.u32", NULL), *vals = load("k7_vals.u32", NULL);
    char chk[64];
    for (int r = -warmup_count(); r < reps; r++) {
        uint64_t nk = 0, ws = 0;
        double t0, t1;
        if (!strcmp(variant, "natural")) {
            enum { NB = 1048573 };  // nombre premier de seaux
            t0 = now();
            Node7 **tab = calloc(NB, sizeof *tab);
            for (size_t i = 0; i < N7; i++) {
                uint32_t k = keys[i];
                Node7 **pp = &tab[k % NB], *p = *pp;
                while (p && p->key != k) p = p->next;
                if (!p) { p = malloc(sizeof *p); p->key = k; p->count = 0; p->sum = 0; p->next = *pp; *pp = p; }
                p->count++;
                p->sum += vals[i];
            }
            t1 = now();
            for (size_t b = 0; b < NB; b++)
                for (Node7 *p = tab[b], *nx; p; p = nx) { nx = p->next; nk++; ws += p->sum * ((p->key & 1023) + 1); free(p); }
            free(tab);
        } else {  // tuned : adressage ouvert, sondage linéaire, hachage de Fibonacci, par lots
            // standard : sans __builtin_prefetch (C n'a pas de préchargement standard) ; le découpage en lots reste
            enum { LOG = 21, CAP = 1 << LOG, BATCH = 16 };
            t0 = now();
            Slot7 *tab = aligned_alloc(64, CAP * sizeof(Slot7));
            memset(tab, 0, CAP * sizeof(Slot7));
            for (size_t i = 0; i < N7; i += BATCH) {
                uint32_t h[BATCH];
                for (int b = 0; b < BATCH; b++) {
                    h[b] = (keys[i + b] * 0x9E3779B1u) >> (32 - LOG);
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
            for (size_t s = 0; s < CAP; s++)
                if (tab[s].count) { nk++; ws += tab[s].sum * ((tab[s].key & 1023) + 1); }
            free(tab);
        }
        k7_checksum(chk, sizeof chk, nk, ws);
        if (r >= 0) result("k7", variant, "16M/1M", r, t1 - t0, chk);
    }
}

// ------------------------------------------------------------------ K8
typedef struct Node8 { int64_t v; struct Node8 *l, *r; } Node8;
static Node8 *t8_build(int depth, int64_t *counter) {
    Node8 *n = malloc(sizeof *n);
    n->v = (*counter)++;
    if (depth > 0) { n->l = t8_build(depth - 1, counter); n->r = t8_build(depth - 1, counter); }
    else n->l = n->r = NULL;
    return n;
}
static int64_t t8_sum(const Node8 *n) { return n ? n->v + t8_sum(n->l) + t8_sum(n->r) : 0; }
static void t8_free(Node8 *n) { if (n) { t8_free(n->l); t8_free(n->r); free(n); } }
// version arène : nœuds dans un tableau réutilisé, enfants par index
typedef struct { int64_t v; int32_t l, r; } ANode;
static int32_t a8_build(ANode *a, int32_t *top, int depth, int64_t *counter) {
    int32_t i = (*top)++;
    a[i].v = (*counter)++;
    if (depth > 0) { int32_t l = a8_build(a, top, depth - 1, counter); a[i].l = l; a[i].r = a8_build(a, top, depth - 1, counter); }
    else a[i].l = a[i].r = -1;
    return i;
}
static int64_t a8_sum(const ANode *a, int32_t i) { return i < 0 ? 0 : a[i].v + a8_sum(a, a[i].l) + a8_sum(a, a[i].r); }
static int cmpu64(const void *x, const void *y) {
    uint64_t a = *(const uint64_t *)x, b = *(const uint64_t *)y;
    return (a > b) - (a < b);
}
static void run_k8(const char *variant, int reps) {
    enum { Q = 16384, D = 10 };
    int tuned = !strcmp(variant, "tuned");
    int64_t cnt = 0;
    Node8 *longlived = t8_build(20, &cnt);
    int64_t lsum = t8_sum(longlived);
    uint64_t *lat = malloc(Q * sizeof *lat);
    ANode *arena = malloc(sizeof(ANode) * 2047);
    char chk[64];
    for (int r = -warmup_count(); r < reps; r++) {
        int64_t total = 0;
        double t0 = now();
        for (int q = 0; q < Q; q++) {
            uint64_t a = now_ns();
            int64_t c = q, s;
            if (tuned) { int32_t top = 0; int32_t root = a8_build(arena, &top, D, &c); s = a8_sum(arena, root); }
            else { Node8 *t = t8_build(D, &c); s = t8_sum(t); t8_free(t); }
            total += s;
            lat[q] = now_ns() - a;
        }
        double t1 = now();
        snprintf(chk, sizeof chk, "%lld", (long long)(total + lsum));
        if (r >= 0) {
            result("k8", variant, "16384x2047", r, t1 - t0, chk);
            qsort(lat, Q, sizeof *lat, cmpu64);
            printf("LAT;%s;%llu;%llu;%llu;%llu;%llu\n", variant, (unsigned long long)lat[Q / 2], (unsigned long long)lat[Q * 9 / 10],
                   (unsigned long long)lat[Q * 99 / 100], (unsigned long long)lat[Q * 999 / 1000], (unsigned long long)lat[Q - 1]);
        }
    }
    t8_free(longlived);
}

// ------------------------------------------------------------------ K9
enum { M9 = 2048, IT9 = 4 };
static void k9_init(double *g) {
    for (int i = 0; i < M9; i++)
        for (int j = 0; j < M9; j++) g[(size_t)i * M9 + j] = (double)((i * 31 + j * 17) % 1024) / 1024.0;
}
// naturel : tableau 2D C99 (pointeur vers tableaux de M9 doubles), contigu
__attribute__((noinline)) static void k9_natural(double (*in)[M9], double (*out)[M9]) {
    for (int i = 1; i < M9 - 1; i++)
        for (int j = 1; j < M9 - 1; j++)
            out[i][j] = 0.25 * (((in[i - 1][j] + in[i + 1][j]) + in[i][j - 1]) + in[i][j + 1]);
}
__attribute__((noinline)) static void k9_rows(const double *restrict in, double *restrict out, int r0, int r1) {
    for (int i = r0; i < r1; i++) {
        const double *restrict up = in + (size_t)(i - 1) * M9, *restrict mid = in + (size_t)i * M9, *restrict dn = in + (size_t)(i + 1) * M9;
        double *restrict o = out + (size_t)i * M9;
        for (int j = 1; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
typedef struct { const double *in; double *out; int r0, r1; } K9Arg;
static int k9_worker(void *v) { K9Arg *a = v; k9_rows(a->in, a->out, a->r0, a->r1); return 0; }  // standard : thrd_start_t
static void run_k9(const char *variant, int reps) {
    size_t n = (size_t)M9 * M9;
    double *a = aligned_alloc(64, n * 8), *b = aligned_alloc(64, n * 8);
    char chk[64];
    for (int r = -warmup_count(); r < reps; r++) {
        k9_init(a); memcpy(b, a, n * 8);  // le bord de b = bord initial
        double *in = a, *out = b;
        double t0 = now();
        for (int it = 0; it < IT9; it++) {
            if (!strcmp(variant, "natural")) k9_natural((double (*)[M9])in, (double (*)[M9])out);
            else if (!strcmp(variant, "tuned")) k9_rows(in, out, 1, M9 - 1);
            else {
                thrd_t th[4];  // standard : threads.h
                K9Arg arg[4];
                for (int t = 0; t < 4; t++) {
                    arg[t] = (K9Arg){in, out, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4};
                    thrd_create(&th[t], k9_worker, &arg[t]);
                }
                for (int t = 0; t < 4; t++) thrd_join(th[t], NULL);
            }
            double *tmp = in; in = out; out = tmp;
        }
        double t1 = now();
        double s = 0;
        for (size_t k = 0; k < n; k++) s += in[k];
        snprintf(chk, sizeof chk, "%.15e", s);
        if (r >= 0) result("k9", variant, "2048^2x4", r, t1 - t0, chk);
    }
}

// K10 (hors score) : retiré de cette copie.

// ------------------------------------------------------------------ main
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s kernel variant reps [param]\n", argv[0]); return 1; }
    const char *k = argv[1], *v = argv[2], *p = argc > 4 ? argv[4] : "";
    int reps = atoi(argv[3]);
    if (!strcmp(k, "k1")) run_k1(v, reps);
    else if (!strcmp(k, "k2")) run_k2(v, reps, p);
    else if (!strcmp(k, "k3")) run_k3(v, reps);
    else if (!strcmp(k, "k4")) run_k4(v, reps);
    else if (!strcmp(k, "k5")) run_k5(v, reps);
    else if (!strcmp(k, "k6")) run_k6(v, reps, p);
    else if (!strcmp(k, "k7")) run_k7(v, reps);
    else if (!strcmp(k, "k8")) run_k8(v, reps);
    else if (!strcmp(k, "k9")) run_k9(v, reps);
    else { fprintf(stderr, "kernel inconnu %s\n", k); return 1; }
    return 0;
}
