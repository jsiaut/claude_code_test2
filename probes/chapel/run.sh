#!/bin/sh
# Sonde de Chapel : probe.chpl et probe_errata.chpl (premières sondes) puis audit de la grille (audit/, docs/V4_PLAN.md
# 2.1). Sortie : results/probes/chapel.txt
cd "$(dirname "$0")" && mkdir -p bin && export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
$CHPL_HOME/bin/linux64-x86_64/chpl --fast probe.chpl -o bin/probe > /dev/null 2>&1 && bin/probe | grep -E "^CAP;(A2|A4|A5);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
$CHPL_HOME/bin/linux64-x86_64/chpl --fast probe_errata.chpl -o bin/probe_errata > /dev/null 2>&1 && bin/probe_errata | grep -E "^CAP;(B2|C2|B3|C4|E5);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /; s/\$/ ; preuves de la remarque sur Chapel : results\/chapel_check\/probes.txt et ir.txt (tools\/chapel_check\/build.sh : avertissements --warn-unstable, IR, échecs)/"
exec sh audit/run.sh
