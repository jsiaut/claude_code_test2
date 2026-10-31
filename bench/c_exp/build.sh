#!/bin/sh
# Copie de la remarque sur C# (docs/CSHARP.md) : mêmes options que bench/c (clang 23.1.5)
set -e
cd "$(dirname "$0")"
clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread -o ms ms.c
