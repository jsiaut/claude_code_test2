#!/bin/sh
# Remarque sur C++ : source C, grilles de K9 réallouées à chaque répétition, clang 23
set -e
cd "$(dirname "$0")"
clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread -o ms ms.c
