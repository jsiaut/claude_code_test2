#!/bin/sh
# Remarque sur C3 (docs/C3.md) : même source que c3_ref, avec --optlevel=max (pipeline O3 de LLVM, mathématiques
# flottantes strictes, comme -O3 ; sensibilité).
set -e
cd "$(dirname "$0")"
/opt/src/c3c/build/c3c compile ../c3/ms.c3 -O3 --optlevel=max --x86cpu=native -o ms
