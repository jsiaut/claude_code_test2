#include <simd>
#include <cstddef>
namespace sd = std::simd;
extern "C" float sum_simd(const float* v, std::size_t n) {
  sd::vec<float, 8> acc(0.0f); std::size_t i = 0;
  for (; i + 8 <= n; i += 8) acc += sd::unchecked_load<sd::vec<float, 8>>(v + i, 8);
  float s = sd::reduce(acc); for (; i < n; ++i) s += v[i]; return s; }
