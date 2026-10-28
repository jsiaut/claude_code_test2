#!/bin/sh
# C3 0.8.5_1 (LLVM 23.1.5) — -O3 (optimisé, sans vérifications), --x86cpu=native
set -e
cd "$(dirname "$0")"
/opt/src/c3c/build/c3c compile ms.c3 -O3 --x86cpu=native -o ms
