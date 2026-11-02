#define _POSIX_C_SOURCE 200809L
#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec*1e-9;}
__attribute__((noinline)) static float k5u(const float *restrict a, const float *restrict b, int n) {
    __m512 s0 = _mm512_setzero_ps(), s1 = s0, s2 = s0, s3 = s0;
    for (int i = 0; i < n; i += 64) {
        s0 = _mm512_fmadd_ps(_mm512_loadu_ps(a + i), _mm512_loadu_ps(b + i), s0);
        s1 = _mm512_fmadd_ps(_mm512_loadu_ps(a + i + 16), _mm512_loadu_ps(b + i + 16), s1);
        s2 = _mm512_fmadd_ps(_mm512_loadu_ps(a + i + 32), _mm512_loadu_ps(b + i + 32), s2);
        s3 = _mm512_fmadd_ps(_mm512_loadu_ps(a + i + 48), _mm512_loadu_ps(b + i + 48), s3);
    }
    return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));
}
int main(int argc, char **argv) {
    int off = atoi(argv[1]); /* décalage en octets */
    int n = 2048;
    char *pa = aligned_alloc(64, n * 4 + 128), *pb = aligned_alloc(64, n * 4 + 128);
    float *a = (float *)(pa + off), *b = (float *)(pb + off);
    FILE *f = fopen("/opt/msdata/k5_a.f32", "rb"); fread(a, 4, n, f); fclose(f);
    f = fopen("/opt/msdata/k5_b.f32", "rb"); fread(b, 4, n, f); fclose(f);
    volatile float sink; double best = 1e9, t[40];
    for (int r = -3; r < 31; r++) {
        double t0 = now(); float d = 0;
        for (int it = 0; it < 65536; it++) { __asm__ volatile("" : "+r"(a)); d = k5u(a, b, n); }
        double t1 = now(); sink = d;
        if (r >= 0) t[r] = (t1 - t0) * 1e3;
    }
    /* médiane */
    for (int i = 0; i < 31; i++) for (int j = i + 1; j < 31; j++) if (t[j] < t[i]) { double x = t[i]; t[i] = t[j]; t[j] = x; }
    printf("C décalage %d : médiane %.3f ms (min %.3f) somme %.4f\n", off, t[15], t[0], sink);
    return 0;
}
