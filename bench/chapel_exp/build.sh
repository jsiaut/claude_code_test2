#!/bin/sh
# Copie de la remarque sur Chapel (docs/CHAPEL.md) : deux binaires, compilés pour le CPU de l'hôte comme bench/chapel ;
# pas de binaire --no-ieee-float (K5 tuned et K1 aos/soa portent l'attribut de boucle).
set -e
cd "$(dirname "$0")"
export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native
export CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
CHPL=$CHPL_HOME/bin/linux64-x86_64/chpl
V512='-Xclang -target-feature -Xclang -prefer-256-bit'
$CHPL --fast ms.chpl -o ms_nat
$CHPL --fast --ccflags "$V512" ms.chpl -o ms_tuned
