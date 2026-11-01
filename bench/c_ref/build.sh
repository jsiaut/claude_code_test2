#!/bin/sh
# Remarque sur C++ : source C de la campagne, clang 23, options du banc (témoin du même hôte)
set -e
cd "$(dirname "$0")"
clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread -o ms ../c/ms.c
