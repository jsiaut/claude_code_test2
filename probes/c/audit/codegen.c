/* Code produit, lu par run.sh (clang-23 -std=c23 -O3 -march=native -S et -emit-llvm). */
#include <stdatomic.h>
#include <stdint.h>
#include <immintrin.h>
typedef float v8f __attribute__((vector_size(32)));
void st_release(_Atomic uint64_t *a) { atomic_store_explicit(a, 1, memory_order_release); }
void st_seqcst(_Atomic uint64_t *a) { atomic_store_explicit(a, 1, memory_order_seq_cst); }
uint64_t add_relaxed(_Atomic uint64_t *a) { return atomic_fetch_add_explicit(a, 1, memory_order_relaxed); }
void spin(_Atomic uint64_t *f) { while (atomic_load_explicit(f, memory_order_acquire) == 0) _mm_pause(); atomic_thread_fence(memory_order_seq_cst); }
void axpy(float *restrict a, const float *restrict b, long n) { for (long i = 0; i < n; i++) a[i] += 2 * b[i]; }
void ext(uint64_t);
uint64_t hinted(uint64_t x) { uint64_t r = x; if (__builtin_expect(x == 7, 0)) { ext(x); r = x * 5; } return r + 1; }
uint64_t unhinted(uint64_t x) { uint64_t r = x; if (x == 9) { ext(x); r = x * 7; } return r + 3; }
void pf(const void *p) { __builtin_prefetch(p, 0, 3); }
__m512i tern(__m512i a, __m512i b, __m512i c) { return _mm512_ternarylogic_epi32(a, b, c, 0x96); }
v8f vadd(v8f a, v8f b) { return a + b; }
float sum_plain(const float *a, long n) { float s = 0; for (long i = 0; i < n; i++) s += a[i]; return s; }
float sum_reassoc(const float *a, long n) {
#pragma clang fp reassociate(on)
  float s = 0; for (long i = 0; i < n; i++) s += a[i]; return s;
}
float idx(const float *a, long i) { return a[i]; }
