#!/bin/sh
# Copie standard de bench/cpp (docs/CONFRONTATION.md) : mêmes options.
# C++26, GCC 16.2 (g++-16, libstdc++ avec std::simd), -O3 -march=native
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native -pthread -Wall -Wno-interference-size -o ms ms.cpp
