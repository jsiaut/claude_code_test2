// Latence d'une chaîne dépendante sur la machine de mesure : vaddss contre vfmadd231ss, en cycles (fréquence par une chaîne
// d'imul, 3 cycles). clang-23 -O2 -march=native -o addfma tools/addfma.c. Sortie : results/hw/machine3/addfma.txt
#include <stdio.h>
#include <stdint.h>
#include <time.h>
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
int main(void){
  for (int k = 0; k < 5; k++) {
    const long N = 50000000;
    uint64_t y = 3, m = 1;
    double t0 = now();
    for (long i = 0; i < N / 10; i++)
      __asm__ volatile("imul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0\n\t"
                       "imul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0" : "+r"(y) : "r"(m));
    double t1 = now();
    double ghz = 3.0 * N / (t1 - t0) / 1e9;   // imul : 3 cycles
    float x = 1.0f, b = 1e-7f, c = 1.0f;
    double t2 = now();
    for (long i = 0; i < N / 10; i++)
      __asm__ volatile("vaddss %1,%0,%0\n\tvaddss %1,%0,%0\n\tvaddss %1,%0,%0\n\tvaddss %1,%0,%0\n\tvaddss %1,%0,%0\n\t"
                       "vaddss %1,%0,%0\n\tvaddss %1,%0,%0\n\tvaddss %1,%0,%0\n\tvaddss %1,%0,%0\n\tvaddss %1,%0,%0" : "+x"(x) : "x"(b));
    double t3 = now();
    double t4 = now();
    for (long i = 0; i < N / 10; i++)
      __asm__ volatile("vfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0\n\t"
                       "vfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0\n\tvfmadd231ss %1,%2,%0" : "+x"(x) : "x"(b), "x"(c));
    double t5 = now();
    printf("fréquence %.2f GHz ; vaddss %.2f cycles ; vfmadd231ss %.2f cycles (x=%g)\n", ghz,
           (t3 - t2) * ghz * 1e9 / N, (t5 - t4) * ghz * 1e9 / N, x);
  }
}
