// K3 sur la machine 3 : la boucle de GCC pour l'écrivain unique (mov, inc, mov, non déroulée) aux mêmes 16 décalages
// que tools/k3_align.c. clang-23 -O2 -march=native -o k3_align_mov tools/k3_align_mov.c
#include <stdint.h>
#include <stdio.h>
#include <time.h>
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static uint64_t cell[64] __attribute__((aligned(4096)));
__attribute__((noinline)) static void f0(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 0,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f4(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 4,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f8(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 8,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f12(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 12,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f16(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 16,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f20(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 20,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f24(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 24,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f28(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 28,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f32(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 32,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f36(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 36,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f40(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 40,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f44(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 44,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f48(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 48,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f52(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 52,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f56(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 56,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
__attribute__((noinline)) static void f60(uint64_t *c, long n) {
    __asm__ volatile(".p2align 6\n\t.skip 60,0x90\n"
                     "1:\n\tmov (%0), %%rdx\n\tinc %%rdx\n\tmov %%rdx, (%0)\n\t"
                     "dec %1\n\tjnz 1b" : "+r"(c), "+r"(n) : : "rdx", "memory");
}
typedef void (*F)(uint64_t *, long);
int main(void) {
    F fs[] = {f0, f4, f8, f12, f16, f20, f24, f28, f32, f36, f40, f44, f48, f52, f56, f60};
    int ks[] = {0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60};
    for (int i = 0; i < 16; i++) {
        double best = 1e9;
        for (int r = 0; r < 3; r++) { double t0 = now(); fs[i](cell, 1L << 25); double t = 1e3 * (now() - t0); if (t < best) best = t; }
        printf("mov/inc/mov, décalage %2d octets : %6.1f ms\n", ks[i], best);
    }
    return (int)(cell[0] & 1);
}
