#!/bin/sh
# Sonde de C3 : probe.c3 (première sonde) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1). Sortie : results/probes/c3.txt
cd "$(dirname "$0")" && mkdir -p bin && /opt/src/c3c/build/c3c compile probe.c3 -O3 -o bin/probe > /dev/null && bin/probe | grep -E "^CAP;(A2|A3|A5);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
