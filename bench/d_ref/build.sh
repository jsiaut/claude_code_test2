#!/bin/sh
# Remarque sur D (docs/DLANG.md) : source de la campagne (bench/d/ms.d) recompilé sur l hôte avec les options du banc,
# référence des mesures appariées (LDC 1.43.0 compilé depuis les sources, LLVM 21.1.8).
set -e
cd "$(dirname "$0")"
/opt/ldc/bin/ldc2 -O3 -release -mcpu=native -od=. -of=ms ../d/ms.d
