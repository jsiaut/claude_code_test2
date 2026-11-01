#!/bin/sh
# Remarque sur C3 (docs/C3.md) : source de la campagne (bench/c3/ms.c3) recompilé sur l'hôte avec les options du banc
# (C3 0.8.5_1, -O3), référence des mesures appariées.
set -e
cd "$(dirname "$0")"
/opt/src/c3c/build/c3c compile ../c3/ms.c3 -O3 --x86cpu=native -o ms
