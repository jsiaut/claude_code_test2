// v4, point 4 (docs/V4_CONVERGE.md, 4) : diagnostic de K9 (M = 2048, 4 itérations de Jacobi, comme bench/c).
// Usage : k9_diag <forme> <décalage> <écart> <géantes> <fils> <répétitions>
//   forme    : auto (la boucle de bench/c, vectorisée par le compilateur), v512 (8 f64 explicites), v256 (4 f64),
//              scal (la même boucle, vectorisation interdite)
//   décalage : position de la grille d'entrée dans sa page de 4 Kio (octets) ; la grille de sortie a le même décalage
//              plus <écart> octets, d'où une distance entre les deux grilles égale à <écart> modulo 4 Kio
//   géantes  : 1 = madvise(MADV_HUGEPAGE) sur la zone, 0 = rien (hôte en mode madvise)
//   fils     : 1, ou 4 (quatre fils créés à chaque itération, comme la variante mt de bench/c)
// Sortie : une ligne par répétition (temps des 4 itérations, s), puis la médiane et la somme de contrôle.
#define _GNU_SOURCE
#include <immintrin.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>

enum { M9 = 2048, IT9 = 4 };
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }
static void init(double *g) {
    for (int i = 0; i < M9; i++)
        for (int j = 0; j < M9; j++) g[(size_t)i * M9 + j] = (double)((i * 31 + j * 17) % 1024) / 1024.0;
}
__attribute__((noinline)) static void rows_auto(const double *restrict in, double *restrict out, int r0, int r1) {
    for (int i = r0; i < r1; i++) {
        const double *restrict up = in + (size_t)(i - 1) * M9, *restrict mid = in + (size_t)i * M9, *restrict dn = in + (size_t)(i + 1) * M9;
        double *restrict o = out + (size_t)i * M9;
        for (int j = 1; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
__attribute__((noinline)) static void rows_v512(const double *in, double *out, int r0, int r1) {
    const __m512d q = _mm512_set1_pd(0.25);
    for (int i = r0; i < r1; i++) {
        const double *up = in + (size_t)(i - 1) * M9, *mid = in + (size_t)i * M9, *dn = in + (size_t)(i + 1) * M9;
        double *o = out + (size_t)i * M9;
        int j = 1;
        for (; j + 8 <= M9 - 1; j += 8) {
            __m512d s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up + j), _mm512_loadu_pd(dn + j)),
                                                    _mm512_loadu_pd(mid + j - 1)), _mm512_loadu_pd(mid + j + 1));
            _mm512_storeu_pd(o + j, _mm512_mul_pd(q, s));
        }
        for (; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
__attribute__((noinline)) static void rows_v256(const double *in, double *out, int r0, int r1) {
    const __m256d q = _mm256_set1_pd(0.25);
    for (int i = r0; i < r1; i++) {
        const double *up = in + (size_t)(i - 1) * M9, *mid = in + (size_t)i * M9, *dn = in + (size_t)(i + 1) * M9;
        double *o = out + (size_t)i * M9;
        int j = 1;
        for (; j + 4 <= M9 - 1; j += 4) {
            __m256d s = _mm256_add_pd(_mm256_add_pd(_mm256_add_pd(_mm256_loadu_pd(up + j), _mm256_loadu_pd(dn + j)),
                                                    _mm256_loadu_pd(mid + j - 1)), _mm256_loadu_pd(mid + j + 1));
            _mm256_storeu_pd(o + j, _mm256_mul_pd(q, s));
        }
        for (; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
__attribute__((noinline)) static void rows_scal(const double *restrict in, double *restrict out, int r0, int r1) {
    for (int i = r0; i < r1; i++) {
        const double *restrict up = in + (size_t)(i - 1) * M9, *restrict mid = in + (size_t)i * M9, *restrict dn = in + (size_t)(i + 1) * M9;
        double *restrict o = out + (size_t)i * M9;
#pragma clang loop vectorize(disable) interleave(disable)
        for (int j = 1; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
typedef void (*RowsFn)(const double *, double *, int, int);
typedef struct { RowsFn f; const double *in; double *out; int r0, r1; } Arg;
static void *worker(void *v) { Arg *a = v; a->f(a->in, a->out, a->r0, a->r1); return NULL; }
static int cmpd(const void *a, const void *b) { double x = *(const double *)a, y = *(const double *)b; return (x > y) - (x < y); }

int main(int argc, char **argv) {
    if (argc != 7) { fprintf(stderr, "usage : k9_diag forme décalage écart géantes fils répétitions\n"); return 2; }
    RowsFn f = !strcmp(argv[1], "v512") ? rows_v512 : !strcmp(argv[1], "v256") ? rows_v256 : !strcmp(argv[1], "scal") ? rows_scal : rows_auto;
    size_t off = strtoul(argv[2], 0, 10), gap = strtoul(argv[3], 0, 10);
    int huge = atoi(argv[4]), nth = atoi(argv[5]), reps = atoi(argv[6]);
    size_t n = (size_t)M9 * M9, bytes = n * 8, span = 2 * bytes + 3 * 4096 + (2u << 20);
    char *z = mmap(NULL, span + (2u << 20), PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (z == MAP_FAILED) { perror("mmap"); return 1; }
    char *base = (char *)(((uintptr_t)z + (2u << 20) - 1) & ~(uintptr_t)((2u << 20) - 1));  // aligné sur 2 Mio
    if (huge && madvise(base, span, MADV_HUGEPAGE)) perror("madvise");
    double *a = (double *)(base + off), *b = (double *)(base + bytes + 4096 + off + gap);
    printf("META;adresses;entrée %% 4096 = %zu ; sortie %% 4096 = %zu ; distance %% 4096 = %zu\n",
           (size_t)((uintptr_t)a % 4096), (size_t)((uintptr_t)b % 4096), (size_t)(((uintptr_t)b - (uintptr_t)a) % 4096));
    double *t = malloc(sizeof(double) * reps), chk = 0;
    for (int r = -1; r < reps; r++) {
        init(a); memcpy(b, a, bytes);
        double *in = a, *out = b, t0 = now();
        for (int it = 0; it < IT9; it++) {
            if (nth == 1) f(in, out, 1, M9 - 1);
            else {
                pthread_t th[4]; Arg arg[4];
                for (int k = 0; k < 4; k++) {
                    arg[k] = (Arg){f, in, out, 1 + (M9 - 2) * k / 4, 1 + (M9 - 2) * (k + 1) / 4};
                    pthread_create(&th[k], NULL, worker, &arg[k]);
                }
                for (int k = 0; k < 4; k++) pthread_join(th[k], NULL);
            }
            double *x = in; in = out; out = x;
        }
        double dt = now() - t0;
        if (r >= 0) t[r] = dt;
        chk = 0;
        for (size_t k = 0; k < n; k++) chk += in[k];
    }
    qsort(t, reps, sizeof *t, cmpd);
    printf("RESULT;%s;off=%zu;gap=%zu;huge=%d;threads=%d;median=%.6f;min=%.6f;max=%.6f;chk=%.15e\n", argv[1], off, gap, huge, nth,
           t[reps / 2], t[0], t[reps - 1], chk);
    return 0;
}
