#!/bin/sh
# Copie standard de bench/c (docs/CONFRONTATION.md) : mêmes options, plus la largeur de vecteur 512 bits (permise par
# le plan, section 4.1 : elle remplace la largeur que les intrinsèques AVX-512 imposaient dans la version d'origine).
set -e
cd "$(dirname "$0")"
clang-23 -std=c23 -O3 -march=native -mprefer-vector-width=512 -Wall -Wextra -o ms ms.c
