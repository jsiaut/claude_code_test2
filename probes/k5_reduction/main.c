#include <stdio.h>
#include <time.h>
float dot(const float *a, const float *b, int n);
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
int main(void) {
    static float a[2048], b[2048];
    for (int i = 0; i < 2048; i++) { a[i] = 1.0f / (i + 1); b[i] = (float)(i % 7); }
    double best = 1e9; float s = 0;
    for (int r = 0; r < 5; r++) {
        double t0 = now();
        for (int k = 0; k < 65536; k++) { s += dot(a, b, 2048); __asm__ volatile("" : : : "memory"); }
        double t = now() - t0; if (t < best) best = t;
    }
    printf("%.1f ms (s=%g)\n", 1e3 * best, s);
}
