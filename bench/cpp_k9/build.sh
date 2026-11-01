#!/bin/sh
# Remarque sur C++ : grilles de K9 allouées une seule fois (comme C), g++ 16
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native -pthread -Wall -Wno-interference-size -o ms ms.cpp
