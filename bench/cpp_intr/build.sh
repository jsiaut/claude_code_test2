#!/bin/sh
# Remarque sur C++ : noyaux std::simd remplacés par la forme de C (intrinsèques), g++ 16
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native -pthread -Wall -Wno-interference-size -o ms ms.cpp
