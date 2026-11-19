#!/bin/sh
# Sonde d'Ada : probe.adb et probe_errata.adb (premières sondes) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/ada.txt
export PATH=/opt/gcc-16/bin:$PATH
cd "$(dirname "$0")" && mkdir -p bin && cd bin && gnatmake-16 -q -O2 -gnat2022 ../probe.adb -o probe > /dev/null && ./probe | grep -E "^CAP;(A2|A3|A5|D4);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
gnatmake-16 -q -O3 -gnat2022 -march=native ../probe_errata.adb -o probe_errata > /dev/null && ./probe_errata > probe_errata.out
grep -E "^CAP;(E5|B4);" probe_errata.out | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
grep -E "^CAP;C1;" probe_errata.out | sed "s/^CAP;C1;[0-9.]*;/CAP;C1;1;[exécutée] /; s/\$/ ; ½ en v1 (règle v2 : extension documentée de GNAT)/"
cd .. && exec sh audit/run.sh
