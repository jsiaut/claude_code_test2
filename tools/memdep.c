// Dépendance par la mémoire sur la machine de mesure : un compteur incrémenté 2^25 fois, en cycles par incrément.
// (a) chargement, incrément, rangement séparés (code de GCC pour K3 sw) ; (b) incq en mémoire (code de clang) ;
// (c) lock incq (K3 rmw) ; (d) incq en mémoire déroulé 16 fois, comme le code de clang. Fréquence par une chaîne d'imul (3 cycles). Sortie : results/hw/machine3/memdep.txt
// clang-23 -O2 -march=native -o memdep tools/memdep.c
#include <stdint.h>
#include <stdio.h>
#include <time.h>
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
int main(void) {
    static volatile uint64_t cell[16] __attribute__((aligned(128)));
    uint64_t *c = (uint64_t *)&cell[0];
    const long N = 1L << 25;
    for (int k = 0; k < 5; k++) {
        uint64_t y = 3, m = 1;
        double t0 = now();
        for (long i = 0; i < N / 10; i++)
            __asm__ volatile("imul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0\n\t"
                             "imul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0\n\timul %1,%0" : "+r"(y) : "r"(m));
        double ghz = 3.0 * N / (now() - t0) / 1e9;
        double a0 = now();
        for (long i = 0; i < N; i++) __asm__ volatile("mov (%0),%%rdx\n\tinc %%rdx\n\tmov %%rdx,(%0)" : : "r"(c) : "rdx", "memory");
        double a1 = now();
        for (long i = 0; i < N; i++) __asm__ volatile("incq (%0)" : : "r"(c) : "memory");
        double b1 = now();
        for (long i = 0; i < N; i++) __asm__ volatile("lock incq (%0)" : : "r"(c) : "memory");
        double c1 = now();
        for (long i = 0; i < N / 16; i++)  // déroulé 16 fois, comme clang
            __asm__ volatile("incq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\t"
                             "incq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)\n\tincq (%0)"
                             : : "r"(c) : "memory");
        double d1 = now();
        printf("déroulé 16 fois : incq mémoire %.2f cycles (%.1f ms)\n", (d1 - c1) * ghz * 1e9 / N, 1e3 * (d1 - c1));
        printf("fréquence %.2f GHz ; mov/inc/mov %.2f cycles (%.1f ms) ; incq mémoire %.2f cycles (%.1f ms) ; lock incq %.2f cycles (%.1f ms)\n",
               ghz, (a1 - a0) * ghz * 1e9 / N, 1e3 * (a1 - a0), (b1 - a1) * ghz * 1e9 / N, 1e3 * (b1 - a1),
               (c1 - b1) * ghz * 1e9 / N, 1e3 * (c1 - b1));
    }
    return (int)(cell[0] & 1);
}
