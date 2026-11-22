#!/bin/sh
# v4, point 6 : sondes de la grille ouverte, C et C++ (hwloc, F2). Écrit results/open/probes/c.txt et cpp.txt.
set -e
cd "$(dirname "$0")" && mkdir -p bin
OUT=../../../results/open/probes
V=$(dpkg-query -W -f '${Version}' libhwloc-dev)
clang-23 -std=c23 -O3 -march=native -pthread -o bin/f2_c hwloc_f2.c -lhwloc
/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native -pthread -x c++ -o bin/f2_cpp hwloc_f2.c -lhwloc
for l in c cpp; do
  r=$(bin/f2_$l | grep '^RESULT;F2;' | cut -d';' -f3-)
  {
    echo "# Grille ouverte (docs/V4_OPEN.md, 4), $l : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34"
    echo "CAP;F2;1;hwloc 2.10.0 (libhwloc-dev $V);[exécutée] $r"
    echo "NOTE;F2;note publiée 0 ; hwloc place mémoire et fils sur les nœuds NUMA (politique et emplacement relus) : 1, comme si l'API était livrée"
  } > $OUT/$l.txt
  cat $OUT/$l.txt
done
