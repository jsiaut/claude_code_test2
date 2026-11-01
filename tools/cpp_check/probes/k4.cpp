// Sonde K4 (remarque sur C++) : les deux noyaux de bench/cpp/ms.cpp, à l'identique, pour comparer le code de g++ 16
// et de clang++ 23 à celui de bench/c/ms.c.
#include <cstdint>
#include <vector>
[[gnu::noinline]] uint64_t k4_natural(const std::vector<uint8_t> &v) {
    uint64_t s = 0;
    for (uint8_t x : v)
        if (x >= 128) s += x;
    return s;
}
[[gnu::noinline]] uint64_t k4_branchless(const std::vector<uint8_t> &v) {
    uint64_t s = 0;
    for (uint8_t x : v) s += (uint64_t)x * (x >> 7);
    return s;
}
