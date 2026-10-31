#!/bin/sh
# Copie corrigée de la remarque sur D (docs/DLANG.md) : mêmes options que bench/d (LDC 1.43.0, LLVM 21.1.8)
set -e
cd "$(dirname "$0")"
/opt/ldc/bin/ldc2 -O3 -release -mcpu=native -of=ms ms.d
