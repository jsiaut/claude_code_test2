// Pilote commun : mêmes données, même chronométrage, seul le noyau change. Usage : drv k4n|k4b|k9n reps
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
enum { N4 = 1 << 24, M9 = 2048 };
uint64_t k4_natural(const uint8_t *v, size_t n);
uint64_t k4_branchless(const uint8_t *v, size_t n);
void k9_natural(double (*in)[M9], double (*out)[M9]);
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static int cmp(const void *a, const void *b) { double x = *(const double *)a, y = *(const double *)b; return (x > y) - (x < y); }
int main(int argc, char **argv) {
    const char *k = argv[1];
    int reps = atoi(argv[2]);
    double *t = malloc(sizeof(double) * reps);
    double chk = 0;
    if (k[1] == '4') {
        uint8_t *v = aligned_alloc(64, N4);
        FILE *f = fopen("/opt/msdata/k4_bytes.u8", "rb");
        if (!f || fread(v, 1, N4, f) != N4) return 1;
        fclose(f);
        for (int r = -1; r < reps; r++) {
            double t0 = now();
            uint64_t s = k[2] == 'b' ? k4_branchless(v, N4) : k4_natural(v, N4);
            double t1 = now();
            if (r >= 0) t[r] = t1 - t0;
            chk = (double)s;
        }
    } else {
        double *a = aligned_alloc(64, (size_t)M9 * M9 * 8), *b = aligned_alloc(64, (size_t)M9 * M9 * 8);
        for (int r = -1; r < reps; r++) {
            for (int i = 0; i < M9; i++)
                for (int j = 0; j < M9; j++) a[(size_t)i * M9 + j] = (double)((i * 31 + j * 17) % 1024) / 1024.0;
            memcpy(b, a, (size_t)M9 * M9 * 8);
            double *in = a, *out = b;
            double t0 = now();
            for (int it = 0; it < 4; it++) {
                k9_natural((double (*)[M9])in, (double (*)[M9])out);
                double *x = in; in = out; out = x;
            }
            double t1 = now();
            if (r >= 0) t[r] = t1 - t0;
            chk = 0;
            for (size_t q = 0; q < (size_t)M9 * M9; q++) chk += in[q];
        }
    }
    qsort(t, reps, sizeof(double), cmp);
    printf("%s min %.3f med %.3f ms chk %.15g\n", k, 1e3 * t[0], 1e3 * t[reps / 2], chk);
    return 0;
}
