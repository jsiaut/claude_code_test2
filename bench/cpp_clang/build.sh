#!/bin/sh
# Remarque sur C++ : source de cpp_intr compilée par clang++ 23 (libstdc++ de GCC 16)
set -e
cd "$(dirname "$0")"
clang++-23 -std=c++26 -O3 -march=native -pthread -Wall --gcc-toolchain=/opt/gcc-16 -o ms ../cpp_intr/ms.cpp
