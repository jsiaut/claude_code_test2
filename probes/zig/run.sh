#!/bin/sh
# Sonde de Zig : probe.zig et probe_f4.zig (premières sondes) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/zig.txt
cd "$(dirname "$0")" && mkdir -p bin
/opt/zig/zig build-exe -O ReleaseFast -mcpu native -femit-bin=bin/probe probe.zig && bin/probe 2>&1 | grep -E "^CAP;(A2|A3|A4|A5|D3);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
/opt/zig/zig build-exe -O fast -mcpu native -femit-bin=bin/probe_f4 probe_f4.zig && bin/probe_f4 2>&1 | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
