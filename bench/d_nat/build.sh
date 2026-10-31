#!/bin/sh
# Remarque sur D (docs/DLANG.md) : stencil naturel en double[M][], mêmes options que bench/d. Sensibilité.
set -e
cd "$(dirname "$0")"
/opt/ldc/bin/ldc2 -O3 -release -mcpu=native -od=. -of=ms ms.d
