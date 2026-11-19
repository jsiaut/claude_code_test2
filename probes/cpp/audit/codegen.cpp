// Code produit, lu par run.sh (g++-16 -std=c++26 -O3 -march=native -S ; -fopt-info-vec pour E5).
#include <atomic>
#include <cstdint>
#include <execution>
#include <numeric>
#include <vector>
#include <immintrin.h>
typedef float v8f __attribute__((vector_size(32)));
extern "C" {
void st_release(std::atomic<std::uint64_t> *a) { a->store(1, std::memory_order_release); }
void st_seqcst(std::atomic<std::uint64_t> *a) { a->store(1, std::memory_order_seq_cst); }
std::uint64_t add_relaxed(std::atomic<std::uint64_t> *a) { return a->fetch_add(1, std::memory_order_relaxed); }
void spin(std::atomic<std::uint64_t> *f) { while (f->load(std::memory_order_acquire) == 0) _mm_pause(); std::atomic_thread_fence(std::memory_order_seq_cst); }
void axpy_r(float *__restrict__ a, const float *__restrict__ b, long n) { for (long i = 0; i < n; i++) a[i] += 2 * b[i]; }
void axpy_p(float *a, const float *b, long n) { for (long i = 0; i < n; i++) a[i] += 2 * b[i]; }
void ext(std::uint64_t);
std::uint64_t hinted(std::uint64_t x) { std::uint64_t r = x; if (x == 7) [[unlikely]] { ext(x); r = x * 5; } return r + 1; }
std::uint64_t unhinted(std::uint64_t x) { std::uint64_t r = x; if (x == 9) { ext(x); r = x * 7; } return r + 3; }
std::uint64_t likelyh(std::uint64_t x) { std::uint64_t r = x; if (x == 11) [[likely]] { ext(x); r = x * 9; } return r + 4; }
void pf(const void *p) { __builtin_prefetch(p, 0, 3); }
__m512i tern(__m512i a, __m512i b, __m512i c) { return _mm512_ternarylogic_epi32(a, b, c, 0x96); }
v8f vadd(v8f a, v8f b) { return a + b; }
float sum_plain(const float *a, long n) { float s = 0; for (long i = 0; i < n; i++) s += a[i]; return s; }
float sum_reduce(const float *a, long n) { return std::reduce(std::execution::unseq, a, a + n, 0.0f); }
float idx(const std::vector<float> &v, long i) { return v[i]; }
float idx_at(const std::vector<float> &v, long i) { return v.at(i); }
}
consteval std::uint64_t fib(int n) { std::uint64_t a = 0, b = 1; for (int i = 0; i < n; i++) { auto t = a + b; a = b; b = t; } return a; }
extern "C" std::uint64_t fib60() { return fib(60); }
template <class T> [[gnu::noinline]] T gsum(const T *x, long n) { T s{}; for (long i = 0; i < n; i++) s += x[i]; return s; }
extern "C" double use_both(const float *a, const double *b, long n) { return gsum(a, n) + gsum(b, n); }
extern "C" float sum_omp(const float *a, long n) { float s = 0;
#pragma omp simd reduction(+:s)
  for (long i = 0; i < n; i++) s += a[i];
  return s; }
