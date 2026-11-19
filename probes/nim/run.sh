#!/bin/sh
# Sonde de Nim : probe.nim (première sonde) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1). Sortie : results/probes/nim.txt
cd "$(dirname "$0")" && mkdir -p bin && /opt/nim/bin/nim c -d:release --hints:off --cc:clang --clang.exe:clang-23 -o:bin/probe probe.nim && bin/probe | grep -E "^CAP;(A2|A3|A4|A5|F4);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
