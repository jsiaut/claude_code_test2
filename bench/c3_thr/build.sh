#!/bin/sh
# Remarque sur C3 (docs/C3.md) : copie de bench/c3/ms.c3 modifiée (voir l'en-tête du source), options du banc.
set -e
cd "$(dirname "$0")"
/opt/src/c3c/build/c3c compile ms.c3 -O3 --x86cpu=native -o ms
