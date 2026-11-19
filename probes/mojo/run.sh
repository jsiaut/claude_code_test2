#!/bin/sh
# Sonde de Mojo : probe.mojo et probe_errata.mojo (premières sondes) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/mojo.txt
M=/opt/mojo-venv/bin/mojo
cd "$(dirname "$0")" && mkdir -p bin && $M build probe.mojo -o bin/probe > /dev/null 2>&1 && bin/probe | grep -E "^CAP;(D2|E3);" | sed "s/^CAP;D2;/NOTE;D2;/; s/^CAP;E3;/NOTE;E3;/; s/^\(NOTE;[A-Z0-9]*;\)[0-9.]*;/\1[exécutée] /"
$M build probe_errata.mojo -o bin/probe_errata > /dev/null 2>&1 && bin/probe_errata | grep -E "^CAP;(A4|A5|C4|D5|E5);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
