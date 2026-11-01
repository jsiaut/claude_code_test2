#!/bin/sh
# Remarque sur C++ (docs/CPP.md) : source de la campagne, g++ 16, options du banc (référence des rapports)
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native -pthread -Wall -Wno-interference-size -o ms ../cpp/ms.cpp
