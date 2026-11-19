#!/bin/sh
# Sonde d'Odin : probe.odin (première sonde) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1). Sortie : results/probes/odin.txt
cd "$(dirname "$0")" && mkdir -p bin && /opt/src/odin/odin build . -o:speed -out:bin/probe && bin/probe | grep -E "^CAP;(A2|A3|A5);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
