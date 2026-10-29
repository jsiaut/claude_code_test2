// hwprobe.c — caractérisation matérielle sans PMU (la VM n'expose pas de compteurs
// matériels : "no PMU driver, software events only"). Toutes les mesures sont des
// micro-expériences chronométrées par TSC (constant_tsc, nonstop_tsc ; 2,8 GHz sur les machines 1 et 2,
// 2,1 GHz sur la machine 3). Les colonnes « cycles » de lat et peak supposent 2,8 GHz : sur la machine 3, lire les ns.
//
// Sous-commandes :
//   freq    : fréquence effective (chaîne de 1e9 additions dépendantes = 1 cycle/add)
//   lat     : latence de chargement dépendant selon la taille du working set
//   lathp   : idem avec madvise(MADV_HUGEPAGE)
//   bw      : bande passante lecture (somme AVX-512) selon la taille, 1 thread
//   stream  : STREAM copy/scale/add/triad sur 3x128 Mo, 1 et 4 threads
//   peak    : débit FMA (scalaire, AVX2, AVX-512) -> FLOP/cycle
//   fs      : faux partage, 2 et 4 threads, distances 8..256 octets
//   c2c     : latence de transfert de ligne entre paires de CPU (ping-pong)
//   bp      : pénalité de mauvaise prédiction de branchement
//   tlb     : accès aléatoires à 1 ligne par page 4 Ko, avec/sans THP
//   sys     : coût d'un appel système minimal (getppid par syscall(), sans vDSO)
//   pf      : coût d'un défaut de page mineur (premier accès à une page anonyme de 4 Kio, sans THP)
#define _GNU_SOURCE
#include <immintrin.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <time.h>
#include <x86intrin.h>

static double tsc_ghz;
static inline uint64_t rdtsc_s(void) { unsigned a; _mm_lfence(); uint64_t t = __rdtscp(&a); _mm_lfence(); return t; }
static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + ts.tv_nsec * 1e-9; }
static void calib(void) {
    double t0 = now(); uint64_t c0 = rdtsc_s();
    while (now() - t0 < 0.2) {}
    double t1 = now(); uint64_t c1 = rdtsc_s();
    tsc_ghz = (c1 - c0) / (t1 - t0) / 1e9;
}
static void pin(int cpu) { cpu_set_t s; CPU_ZERO(&s); CPU_SET(cpu, &s); pthread_setaffinity_np(pthread_self(), sizeof s, &s); }
static uint64_t xs = 88172645463325252ull;
static inline uint64_t xr(void) { xs ^= xs << 13; xs ^= xs >> 7; xs ^= xs << 17; return xs; }
static void *amalloc(size_t n, int huge) {
    void *p = mmap(NULL, n, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); exit(1); }
    madvise(p, n, huge ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);
    memset(p, 0, n);
    return p;
}

// ---------- freq : 1e9 additions dépendantes (latence add = 1 cycle) ----------
static void t_freq(void) {
    for (int k = 0; k < 3; k++) {
        // 20 additions dépendantes par itération : le coût de la boucle (branchement pris)
        // devient négligeable et la chaîne impose exactement 1 cycle cœur par addition.
        // Additions registre-registre : depuis Golden Cove (machine 3), le renommage replie les chaînes
        // d'additions d'un immédiat (add $1), qui ne mesurent plus la fréquence (11 à 22 additions par ns).
        uint64_t x = 0, one = 1, n = 1000000000ull;
        double t0 = now(); uint64_t c0 = rdtsc_s();
        for (uint64_t i = 0; i < n / 20; i++)
            __asm__ volatile("add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\t"
                             "add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\t"
                             "add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\t"
                             "add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0" : "+r"(x) : "r"(one));
        uint64_t c1 = rdtsc_s(); double t1 = now();
        printf("freq: %.3f GHz effectifs (TSC %.3f GHz, ratio cycles/TSC=%.3f) x=%llu\n",
               n / (t1 - t0) / 1e9, tsc_ghz, (double)n / (c1 - c0), (unsigned long long)x);
    }
}

// ---------- lat : pointer chasing ----------
static void t_lat(int huge) {
    size_t sizes[] = {8 << 10, 16 << 10, 24 << 10, 32 << 10, 48 << 10, 64 << 10, 128 << 10, 256 << 10, 512 << 10,
                      768 << 10, 1 << 20, 1536 << 10, 2 << 20, 4 << 20, 8 << 20, 16 << 20, 24 << 20, 32 << 20,
                      48 << 20, 64 << 20, 128 << 20, 256 << 20, 512 << 20, 1024u << 20};
    for (size_t s = 0; s < sizeof sizes / sizeof *sizes; s++) {
        size_t S = sizes[s], nodes = S / 64;
        uint64_t *a = amalloc(S, huge);
        uint32_t *p = malloc(nodes * 4);
        for (size_t i = 0; i < nodes; i++) p[i] = i;
        for (size_t i = nodes - 1; i > 0; i--) { size_t j = xr() % i; uint32_t t = p[i]; p[i] = p[j]; p[j] = t; }
        for (size_t k = 0; k < nodes; k++) a[8 * k] = (uint64_t)(uintptr_t)&a[8 * p[k]];
        free(p);
        uint64_t *q = a; size_t H = 1 << 24;
        for (size_t i = 0; i < nodes * 2 && i < H; i++) q = (uint64_t *)*q;  // échauffement
        double best = 1e30;
        for (int r = 0; r < 3; r++) {
            uint64_t c0 = rdtsc_s();
            for (size_t i = 0; i < H; i++) q = (uint64_t *)*q;
            uint64_t c1 = rdtsc_s();
            double ns = (c1 - c0) / tsc_ghz / H;
            if (ns < best) best = ns;
        }
        printf("lat%s: %8zu KiB  %7.2f ns  %6.1f cycles  (%p)\n", huge ? "hp" : "", S >> 10, best, best * 2.8, (void *)q);
        munmap(a, S);
    }
}

// ---------- bw : lecture séquentielle vectorisée ----------
__attribute__((noinline)) static uint64_t sum_u32(const uint32_t *a, size_t n) {
    __m512i s0 = _mm512_setzero_si512(), s1 = s0, s2 = s0, s3 = s0;
    for (size_t i = 0; i < n; i += 64) {
        s0 = _mm512_add_epi32(s0, _mm512_load_si512(a + i));
        s1 = _mm512_add_epi32(s1, _mm512_load_si512(a + i + 16));
        s2 = _mm512_add_epi32(s2, _mm512_load_si512(a + i + 32));
        s3 = _mm512_add_epi32(s3, _mm512_load_si512(a + i + 48));
    }
    return (uint64_t)_mm512_reduce_add_epi32(_mm512_add_epi32(_mm512_add_epi32(s0, s1), _mm512_add_epi32(s2, s3)));
}
static void t_bw(void) {
    size_t sizes[] = {16 << 10, 32 << 10, 64 << 10, 256 << 10, 512 << 10, 1 << 20, 2 << 20, 4 << 20, 8 << 20,
                      16 << 20, 32 << 20, 64 << 20, 256 << 20, 1024u << 20};
    for (size_t s = 0; s < sizeof sizes / sizeof *sizes; s++) {
        size_t S = sizes[s], n = S / 4;
        uint32_t *a = amalloc(S, 0);
        for (size_t i = 0; i < n; i++) a[i] = (uint32_t)i;
        size_t reps = (1u << 30) / S; if (reps < 3) reps = 3;
        uint64_t x = 0; double best = 1e30;
        for (int r = 0; r < 5; r++) {
            uint64_t c0 = rdtsc_s();
            // barrière : sans elle, le compilateur calcule la somme une fois et la multiplie par reps
            for (size_t k = 0; k < reps; k++) { __asm__ volatile("" : "+r"(a) : : "memory"); x += sum_u32(a, n); }
            uint64_t c1 = rdtsc_s();
            double sec = (c1 - c0) / tsc_ghz / 1e9;
            if (sec < best) best = sec;
        }
        printf("bw: %8zu KiB  %7.2f GB/s  %6.2f B/cycle (x=%llu)\n", S >> 10, (double)S * reps / best / 1e9,
               (double)S * reps / (best * 2.8e9), (unsigned long long)x);
        munmap(a, S);
    }
}

// ---------- stream ----------
typedef struct { double *a, *b, *c; size_t lo, hi; int op, cpu; pthread_barrier_t *bar; } sarg;
static void *stream_w(void *v) {
    sarg *s = v; pin(s->cpu);
    double *a = s->a, *b = s->b, *c = s->c, q = 3.0;
    pthread_barrier_wait(s->bar);
    switch (s->op) {
    case 0: for (size_t i = s->lo; i < s->hi; i++) c[i] = a[i]; break;
    case 1: for (size_t i = s->lo; i < s->hi; i++) b[i] = q * c[i]; break;
    case 2: for (size_t i = s->lo; i < s->hi; i++) c[i] = a[i] + b[i]; break;
    case 3: for (size_t i = s->lo; i < s->hi; i++) a[i] = b[i] + q * c[i]; break;
    }
    pthread_barrier_wait(s->bar);
    return NULL;
}
static void t_stream(void) {
    size_t n = 16u << 20;  // 16M doubles = 128 Mo par tableau
    double *a = amalloc(n * 8, 0), *b = amalloc(n * 8, 0), *c = amalloc(n * 8, 0);
    for (size_t i = 0; i < n; i++) { a[i] = 1; b[i] = 2; c[i] = 0; }
    const char *nm[] = {"copy", "scale", "add", "triad"};
    const double bytes[] = {16, 16, 24, 24};
    for (int T = 1; T <= 4; T *= 2) for (int op = 0; op < 4; op++) {
        double best = 1e30;
        for (int r = 0; r < 5; r++) {
            pthread_barrier_t bar; pthread_barrier_init(&bar, NULL, T + 1);
            pthread_t th[4]; sarg sa[4];
            for (int t = 0; t < T; t++) { sa[t] = (sarg){a, b, c, n * t / T, n * (t + 1) / T, op, t, &bar}; pthread_create(&th[t], NULL, stream_w, &sa[t]); }
            pthread_barrier_wait(&bar); double t0 = now();
            pthread_barrier_wait(&bar); double t1 = now();
            for (int t = 0; t < T; t++) pthread_join(th[t], NULL);
            pthread_barrier_destroy(&bar);
            if (t1 - t0 < best) best = t1 - t0;
        }
        printf("stream: T=%d %-5s %7.2f GB/s (comptage STREAM, sans RFO)\n", T, nm[op], bytes[op] * n / best / 1e9);
    }
}

// ---------- peak FMA ----------
static void t_peak(void) {
    const long N = 100000000;
    {   // AVX-512 : 12 accumulateurs indépendants (latence 4 x 2 ports + marge)
        __m512 acc[12]; for (int k = 0; k < 12; k++) acc[k] = _mm512_set1_ps(k);
        __m512 m = _mm512_set1_ps(1.0000001f), ad = _mm512_set1_ps(1e-7f);
        uint64_t c0 = rdtsc_s();
        for (long i = 0; i < N; i++)
            for (int k = 0; k < 12; k++) acc[k] = _mm512_fmadd_ps(acc[k], m, ad);
        uint64_t c1 = rdtsc_s();
        float s = 0; for (int k = 0; k < 12; k++) s += _mm512_reduce_add_ps(acc[k]);
        double cyc = (c1 - c0) * (2.8 / tsc_ghz);
        printf("peak: AVX-512 FMA f32 : %.2f FMA-instr/cycle, %.1f FLOP/cycle, %.1f GFLOP/s @%.2f GHz (s=%g)\n",
               N * 12.0 / cyc, N * 12.0 * 32 / cyc, N * 12.0 * 32 / ((c1 - c0) / tsc_ghz), tsc_ghz, s);
    }
    {
        __m256 acc[12]; for (int k = 0; k < 12; k++) acc[k] = _mm256_set1_ps(k);
        __m256 m = _mm256_set1_ps(1.0000001f), ad = _mm256_set1_ps(1e-7f);
        uint64_t c0 = rdtsc_s();
        for (long i = 0; i < N; i++)
            for (int k = 0; k < 12; k++) acc[k] = _mm256_fmadd_ps(acc[k], m, ad);
        uint64_t c1 = rdtsc_s();
        float s = 0; for (int k = 0; k < 12; k++) { float t[8]; _mm256_storeu_ps(t, acc[k]); for (int j = 0; j < 8; j++) s += t[j]; }
        double cyc = (c1 - c0) * (2.8 / tsc_ghz);
        printf("peak: AVX2 FMA f32    : %.2f FMA-instr/cycle, %.1f FLOP/cycle (s=%g)\n", N * 12.0 / cyc, N * 12.0 * 16 / cyc, s);
    }
    {
        float acc[12]; for (int k = 0; k < 12; k++) acc[k] = k;
        uint64_t c0 = rdtsc_s();
        for (long i = 0; i < N; i++)
            for (int k = 0; k < 12; k++) __asm__ volatile("vfmadd213ss %1, %1, %0" : "+x"(acc[k]) : "x"(acc[(k + 1) % 12]));
        uint64_t c1 = rdtsc_s();
        double cyc = (c1 - c0) * (2.8 / tsc_ghz);
        printf("peak: scalaire FMA f32: %.2f FMA-instr/cycle, %.1f FLOP/cycle (acc0=%g)\n", N * 12.0 / cyc, N * 12.0 * 2 / cyc, acc[0]);
    }
    {   // latence FMA (chaîne dépendante)
        __m512 x = _mm512_set1_ps(1.0f), m = _mm512_set1_ps(1.0000001f), ad = _mm512_set1_ps(1e-7f);
        uint64_t c0 = rdtsc_s();
        for (long i = 0; i < N; i++) x = _mm512_fmadd_ps(x, m, ad);
        uint64_t c1 = rdtsc_s();
        printf("peak: latence FMA zmm : %.2f cycles (x=%g)\n", (c1 - c0) * (2.8 / tsc_ghz) / N, _mm512_reduce_add_ps(x));
    }
}

// ---------- fs : faux partage ----------
typedef struct { volatile uint64_t *p; long n; int cpu; pthread_barrier_t *bar; } farg;
static void *fs_w(void *v) {
    farg *f = v; pin(f->cpu);
    pthread_barrier_wait(f->bar);
    for (long i = 0; i < f->n; i++) *f->p = *f->p + 1;
    pthread_barrier_wait(f->bar);
    return NULL;
}
static void t_fs(void) {
    uint8_t *mem = aligned_alloc(4096, 4096);
    long n = 1 << 26;
    int dists[] = {8, 16, 32, 64, 128, 256};
    for (int T = 2; T <= 4; T += 2) for (size_t d = 0; d < 6; d++) {
        double best = 1e30;
        for (int r = 0; r < 3; r++) {
            memset(mem, 0, 4096);
            pthread_barrier_t bar; pthread_barrier_init(&bar, NULL, T + 1);
            pthread_t th[4]; farg fa[4];
            for (int t = 0; t < T; t++) { fa[t] = (farg){(volatile uint64_t *)(mem + t * dists[d]), n, t, &bar}; pthread_create(&th[t], NULL, fs_w, &fa[t]); }
            pthread_barrier_wait(&bar); double t0 = now();
            pthread_barrier_wait(&bar); double t1 = now();
            for (int t = 0; t < T; t++) pthread_join(th[t], NULL);
            if (t1 - t0 < best) best = t1 - t0;
        }
        printf("fs: T=%d distance=%3d o : %6.2f ns/incr/thread  (%.2f cycles)\n", T, dists[d], best / n * 1e9, best / n * 2.8e9);
    }
}

// ---------- c2c : ping-pong ----------
static _Atomic uint64_t flag __attribute__((aligned(128)));
typedef struct { int cpu; long n; } carg;
static void *c2c_w(void *v) {
    carg *c = v; pin(c->cpu);
    for (long i = 0; i < c->n; i++) {
        while (atomic_load_explicit(&flag, memory_order_acquire) != 2 * (uint64_t)i + 1) _mm_pause();
        atomic_store_explicit(&flag, 2 * (uint64_t)i + 2, memory_order_release);
    }
    return NULL;
}
static void t_c2c(void) {
    long n = 200000;
    for (int a = 0; a < 4; a++) for (int b = 0; b < 4; b++) {
        if (a == b) continue;
        atomic_store(&flag, 0);
        pin(a);
        carg c = {b, n}; pthread_t th; pthread_create(&th, NULL, c2c_w, &c);
        uint64_t c0 = rdtsc_s();
        for (long i = 0; i < n; i++) {
            atomic_store_explicit(&flag, 2 * (uint64_t)i + 1, memory_order_release);
            while (atomic_load_explicit(&flag, memory_order_acquire) != 2 * (uint64_t)i + 2) _mm_pause();
        }
        uint64_t c1 = rdtsc_s();
        pthread_join(th, NULL);
        printf("c2c: cpu%d <-> cpu%d : aller-retour %.1f ns (un transfert ~ %.1f ns)\n", a, b, (c1 - c0) / tsc_ghz / n, (c1 - c0) / tsc_ghz / n / 2);
    }
}

// ---------- bp : branchement ----------
__attribute__((noinline)) static uint64_t bsum(const uint8_t *v, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        if (v[i] >= 128) { __asm__ volatile("" ::: "memory"); s += v[i]; }  // force un vrai branchement
    }
    return s;
}
static int cmpu8(const void *a, const void *b) { return *(const uint8_t *)a - *(const uint8_t *)b; }
static void t_bp(void) {
    size_t n = 1 << 24;
    uint8_t *v = malloc(n), *w = malloc(n);
    for (size_t i = 0; i < n; i++) v[i] = xr() >> 56;
    memcpy(w, v, n); qsort(w, n, 1, cmpu8);
    for (int r = 0; r < 3; r++) {
        uint64_t c0 = rdtsc_s(); uint64_t s1 = bsum(v, n); uint64_t c1 = rdtsc_s();
        uint64_t s2 = bsum(w, n); uint64_t c2 = rdtsc_s();
        double cu = (c1 - c0) * (2.8 / tsc_ghz) / n, cs = (c2 - c1) * (2.8 / tsc_ghz) / n;
        printf("bp: aléatoire %.2f cycles/elt, trié %.2f cycles/elt -> pénalité ~%.1f cycles/mauvaise prédiction (s=%llu,%llu)\n",
               cu, cs, (cu - cs) / 0.5, (unsigned long long)s1, (unsigned long long)s2);
    }
}

// ---------- sys : appel système minimal ----------
static void t_sys(void) {
    const int n = 1000000;
    for (int r = 0; r < 5; r++) {
        uint64_t c0 = rdtsc_s();
        long s = 0;
        for (int i = 0; i < n; i++) s += syscall(SYS_getppid);
        uint64_t c1 = rdtsc_s();
        printf("sys: getppid %.1f ns par appel (s=%ld)\n", (c1 - c0) / tsc_ghz / n, s);
    }
}

// ---------- pf : défaut de page mineur ----------
static void t_pf(void) {
    const size_t pages = 65536, n = pages * 4096;  // 256 Mio
    for (int r = 0; r < 5; r++) {
        char *p = mmap(NULL, n, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (p == MAP_FAILED) { perror("mmap"); exit(1); }
        madvise(p, n, MADV_NOHUGEPAGE);
        uint64_t c0 = rdtsc_s();
        for (size_t i = 0; i < pages; i++) p[i * 4096] = 1;
        uint64_t c1 = rdtsc_s();
        printf("pf: %.0f ns par défaut de page mineur (page de 4 Kio, mise à zéro comprise)\n", (c1 - c0) / tsc_ghz / pages);
        munmap(p, n);
    }
}

// ---------- tlb ----------
static void t_tlb(void) {
    size_t pages_list[] = {16, 64, 256, 1024, 1536, 2048, 4096, 16384, 65536, 262144};
    for (int huge = 0; huge <= 1; huge++)
        for (size_t s = 0; s < sizeof pages_list / sizeof *pages_list; s++) {
            size_t P = pages_list[s], S = P * 4096;
            uint8_t *a = amalloc(S, huge);
            uint32_t *p = malloc(P * 4);
            for (size_t i = 0; i < P; i++) p[i] = i;
            for (size_t i = P - 1; i > 0; i--) { size_t j = xr() % i; uint32_t t = p[i]; p[i] = p[j]; p[j] = t; }
            // un pointeur par page, à un décalage de ligne variable (évite les conflits d'ensemble)
            for (size_t k = 0; k < P; k++) {
                size_t off = (k * 64 * 7) % 4096, offn = (p[k] * 64 * 7) % 4096;
                *(uintptr_t *)(a + k * 4096 + off) = (uintptr_t)(a + (size_t)p[k] * 4096 + offn);
            }
            free(p);
            uintptr_t q = (uintptr_t)a; size_t H = 1 << 23;
            for (size_t i = 0; i < 2 * P; i++) q = *(uintptr_t *)q;
            uint64_t c0 = rdtsc_s();
            for (size_t i = 0; i < H; i++) q = *(uintptr_t *)q;
            uint64_t c1 = rdtsc_s();
            printf("tlb%s: %7zu pages (%8zu KiB) : %6.2f ns/accès (%p)\n", huge ? "-thp" : "", P, S >> 10, (c1 - c0) / tsc_ghz / H, (void *)q);
            munmap(a, S);
        }
}

// ---------- witness : témoin d'environnement court (~0,3 s avec l'étalonnage), lancé avant chaque processus mesuré ----------
// Médiane de 5 essais pour le calcul : débit FMA AVX-512 et fréquence effective (chaîne d'additions dépendantes).
// Puis latence d'un saut dépendant sur 2 Mio (frontière du L2 sur la machine 3) et sur 32 Mio (L3 partagé avec les
// autres locataires), et bande passante en lecture sur 64 Mio. Une ligne : witness;GFLOP/s;GHz;ns 2 Mio;ns 32 Mio;Go/s
static int cmpd(const void *a, const void *b) { double x = *(const double *)a, y = *(const double *)b; return (x > y) - (x < y); }
static double chase_ns(size_t S, size_t H) {
    size_t nodes = S / 64;
    uint64_t *a = amalloc(S, 0);
    uint32_t *p = malloc(nodes * 4);
    for (size_t i = 0; i < nodes; i++) p[i] = i;
    for (size_t i = nodes - 1; i > 0; i--) { size_t j = xr() % i; uint32_t t = p[i]; p[i] = p[j]; p[j] = t; }
    for (size_t k = 0; k < nodes; k++) a[8 * p[k]] = (uint64_t)(uintptr_t)&a[8 * p[(k + 1) % nodes]];
    free(p);
    uint64_t *q = a;
    for (size_t i = 0; i < nodes; i++) q = (uint64_t *)*q;
    uint64_t c0 = rdtsc_s();
    for (size_t i = 0; i < H; i++) q = (uint64_t *)*q;
    uint64_t c1 = rdtsc_s();
    __asm__ volatile("" : : "r"(q));
    munmap(a, S);
    return (c1 - c0) / tsc_ghz / H;
}
static void t_witness(void) {
    double g[5], f[5];
    __m512 acc[12]; for (int k = 0; k < 12; k++) acc[k] = _mm512_set1_ps(k);
    __m512 m = _mm512_set1_ps(1.0000001f), ad = _mm512_set1_ps(1e-7f);
    for (int t = 0; t < 5; t++) {
        const long N = 500000;
        uint64_t c0 = rdtsc_s();
        for (long i = 0; i < N; i++) {
            for (int k = 0; k < 12; k++) acc[k] = _mm512_fmadd_ps(acc[k], m, ad);
            __asm__ volatile("" : "+v"(acc[0]), "+v"(acc[1]), "+v"(acc[2]), "+v"(acc[3]), "+v"(acc[4]), "+v"(acc[5]),
                             "+v"(acc[6]), "+v"(acc[7]), "+v"(acc[8]), "+v"(acc[9]), "+v"(acc[10]), "+v"(acc[11]));
        }
        uint64_t c1 = rdtsc_s();
        g[t] = N * 12.0 * 32 / ((c1 - c0) / tsc_ghz);
        const long A = 4000000;  // additions registre-registre (voir t_freq)
        long x = 0, one = 1;
        c0 = rdtsc_s();
        for (long i = 0; i < A / 20; i++)
            __asm__ volatile("add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\t"
                             "add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\t"
                             "add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\t"
                             "add %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0\n\tadd %1, %0" : "+r"(x) : "r"(one));
        c1 = rdtsc_s();
        f[t] = A / ((c1 - c0) / tsc_ghz);
    }
    float fs = 0; for (int k = 0; k < 12; k++) fs += _mm512_reduce_add_ps(acc[k]);
    qsort(g, 5, sizeof g[0], cmpd);
    qsort(f, 5, sizeof f[0], cmpd);
    double l2 = chase_ns(2 << 20, 200000), l32 = chase_ns(32 << 20, 200000);
    size_t B = 64 << 20;
    uint32_t *b = amalloc(B, 0);
    for (size_t i = 0; i < B / 4; i++) b[i] = (uint32_t)i;
    uint64_t x = sum_u32(b, B / 4);
    uint64_t c0 = rdtsc_s();
    __asm__ volatile("" : "+r"(b) : : "memory");
    x += sum_u32(b, B / 4);
    uint64_t c1 = rdtsc_s();
    double bw = (double)B / ((c1 - c0) / tsc_ghz);
    munmap(b, B);
    printf("witness;%.1f;%.2f;%.2f;%.2f;%.2f;%g;%llu\n", g[2], f[2], l2, l32, bw, fs, (unsigned long long)x);
}

int main(int argc, char **argv) {
    calib();
    printf("TSC: %.4f GHz\n", tsc_ghz);
    for (int i = 1; i < argc; i++) {
        const char *c = argv[i];
        if (!strcmp(c, "freq")) t_freq();
        else if (!strcmp(c, "lat")) t_lat(0);
        else if (!strcmp(c, "lathp")) t_lat(1);
        else if (!strcmp(c, "bw")) t_bw();
        else if (!strcmp(c, "stream")) t_stream();
        else if (!strcmp(c, "peak")) t_peak();
        else if (!strcmp(c, "fs")) t_fs();
        else if (!strcmp(c, "c2c")) t_c2c();
        else if (!strcmp(c, "bp")) t_bp();
        else if (!strcmp(c, "tlb")) t_tlb();
        else if (!strcmp(c, "witness")) t_witness();
        else if (!strcmp(c, "sys")) t_sys();
        else if (!strcmp(c, "pf")) t_pf();
        else fprintf(stderr, "inconnu: %s\n", c);
        fflush(stdout);
    }
    return 0;
}
