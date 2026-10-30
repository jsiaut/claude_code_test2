#include <numeric>
#include <functional>
#include <cstddef>
extern "C" float dot_tr(const float* a, const float* b, std::size_t n) { return std::transform_reduce(a, a + n, b, 0.0f); }
extern "C" float dot_loop(const float* a, const float* b, std::size_t n) { float s = 0; for (std::size_t i = 0; i < n; ++i) s += a[i]*b[i]; return s; }
