#!/bin/sh
# C23, clang 23.1.5 (LLVM) — optimisation maximale pour la machine cible
set -e
cd "$(dirname "$0")"
clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread -o ms ms.c
