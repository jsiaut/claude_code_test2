#!/bin/sh
# Sonde de D : probe.d et probe_errata.d (premières sondes) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/d.txt
cd "$(dirname "$0")" && mkdir -p bin && /opt/ldc/bin/ldc2 -O3 -mcpu=native -of=bin/probe probe.d && bin/probe > bin/probe.out; grep -E "^CAP;(A2|A4|A5|F4);" bin/probe.out | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"; grep "^CAP;A3;" bin/probe.out | sed "s/^CAP;A3;[0-9.]*;/NOTE;A3;[exécutée] /"
/opt/ldc/bin/ldc2 -O3 -mcpu=native -of=bin/probe_errata probe_errata.d && bin/probe_errata | grep -E "^CAP;A3;" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
