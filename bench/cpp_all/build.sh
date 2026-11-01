#!/bin/sh
# Remarque sur C++ : cpp_intr + cpp_k9 + cpp_k8, compilée par clang++ 23
set -e
cd "$(dirname "$0")"
clang++-23 -std=c++26 -O3 -march=native -pthread -Wall --gcc-toolchain=/opt/gcc-16 -o ms ms.cpp
