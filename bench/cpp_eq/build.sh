#!/bin/sh
# C++26, GCC 16.2 (g++-16, libstdc++ avec std::simd), -O3 -march=native
set -e
cd "$(dirname "$0")"
# Tailles redéfinissables (v4, point 2 : docs/V4_SIZES.md) ; sans variable MS_*, le binaire publié
DEFS=$(env | grep -E '^MS_(N1|N4|N5|INNER5|N6|N7|K7_LOG2|K7_NB|K8_LONG|K8_REQ|M9)=' | sed 's/^/-D/' | tr '\n' ' ')
/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native -pthread -Wall -Wno-interference-size $DEFS -o ms ms.cpp
