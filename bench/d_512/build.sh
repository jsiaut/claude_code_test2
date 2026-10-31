#!/bin/sh
# Remarque sur D (docs/DLANG.md) : copie corrigée (bench/d_fix/ms.d) et préférence 512 bits pour les boucles laissées au
# vectoriseur (option documentée, permise en tuned ; sensibilité, comme -prefer-256-bit pour Julia).
set -e
cd "$(dirname "$0")"
/opt/ldc/bin/ldc2 -O3 -release -mcpu=native -mattr=-prefer-256-bit -od=. -of=ms ../d_fix/ms.d
