#include <numeric>
#include <execution>
#include <cstddef>
extern "C" float sum_unseq(const float* v, std::size_t n) { return std::reduce(std::execution::unseq, v, v + n, 0.0f); }
extern "C" float sum_reduce(const float* v, std::size_t n) { return std::reduce(v, v + n, 0.0f); }
extern "C" float sum_acc(const float* v, std::size_t n) { return std::accumulate(v, v + n, 0.0f); }
