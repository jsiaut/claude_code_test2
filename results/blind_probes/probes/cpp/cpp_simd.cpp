#include <simd>
#include <cstdio>
namespace sd = std::simd;
int main(){
#ifdef __cpp_lib_simd
  std::printf("__cpp_lib_simd=%ld\n", (long)__cpp_lib_simd);
#else
  std::printf("__cpp_lib_simd undefined\n");
#endif
  sd::vec<float, 8> a(2.0f), b([](int i){ return float(i); });
  auto c = a * b + a;
  std::printf("std::simd ok c[7]=%g sum=%g size=%d\n", (double)c[7], (double)sd::reduce(c), (int)c.size());
}
