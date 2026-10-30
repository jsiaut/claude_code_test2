#!/bin/sh
# Vérifications préalables de la remarque sur Ada (docs/ADA.md, section 2), dans le répertoire donné : E5 (aliasing des
# paramètres, rapports de vectorisation de GCC), C1 (types vectoriels GCC), D2 (synchronisation des atomiques), B4
# (allocation de la pile secondaire, tracée par gdb). GNAT 16.2 (/opt/gcc-16).
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?répertoire de sortie}"
mkdir -p "$OUT" && cd "$OUT" && cp "$SRC"/*.ad? .
export PATH=/opt/gcc-16/bin:$PATH
for f in e5b e5c; do
  gcc-16 -c -O3 -gnat2022 -march=native -fopt-info-vec-optimized=$f.vec.txt $f.adb
  gcc-16 -c -O3 -gnat2022 -gnatp -march=native -fopt-info-vec-optimized=$f.gnatp.vec.txt $f.adb
done
gcc-16 -c -O3 -gnat2022 -march=native c1.adb
gcc-16 -c -O3 -gnat2022 -march=native d2.adb
gnatmake-16 -q -O0 -g -gnat2022 b4.adb -o b4
