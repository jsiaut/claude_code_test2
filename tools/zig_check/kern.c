// Noyaux K4 et K9 naturels de bench/c/ms.c, inchangés (sauf static).
#include <stdint.h>
#include <stddef.h>
enum { M9 = 2048 };
__attribute__((noinline)) uint64_t k4_natural(const uint8_t *v, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++)
        if (v[i] >= 128) s += v[i];
    return s;
}
__attribute__((noinline)) uint64_t k4_branchless(const uint8_t *v, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) s += (uint64_t)v[i] * (v[i] >> 7);
    return s;
}
__attribute__((noinline)) void k9_natural(double (*in)[M9], double (*out)[M9]) {
    for (int i = 1; i < M9 - 1; i++)
        for (int j = 1; j < M9 - 1; j++)
            out[i][j] = 0.25 * (((in[i - 1][j] + in[i + 1][j]) + in[i][j - 1]) + in[i][j + 1]);
}
