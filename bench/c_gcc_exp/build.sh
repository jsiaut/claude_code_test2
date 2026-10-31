#!/bin/sh
# Même source que bench/c_exp, compilée par GCC 16.2 comme bench/c_gcc : -O3 -march=native
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/gcc-16 -std=c23 -O3 -march=native -pthread -o ms ../c_exp/ms.c
