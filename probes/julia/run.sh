#!/bin/sh
# Sonde de Julia : probe.jl et probe_errata.jl (premières sondes) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/julia.txt
J="/opt/julia/bin/julia --startup-file=no"
cd "$(dirname "$0")" && $J probe.jl | grep -E "^CAP;(A2|A5|F4);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
$J probe_errata.jl | grep -E "^CAP;(B2|D3|E3);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /; s/^CAP;E3;0;\[exécutée\] /CAP;E3;0;[échec] /"
exec sh audit/run.sh
