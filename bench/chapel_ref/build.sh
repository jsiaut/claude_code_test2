#!/bin/sh
# Remarque sur Chapel (docs/CHAPEL.md) : le source de la campagne (../chapel/ms.chpl), compilé par le script de
# bench/chapel pour le CPU de l'hôte courant (le runtime installé n'accepte que CHPL_TARGET_CPU=native).
set -e
cd "$(dirname "$0")"
cp ../chapel/ms.chpl ms.chpl
export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native
export CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
CHPL=$CHPL_HOME/bin/linux64-x86_64/chpl
V512='-Xclang -target-feature -Xclang -prefer-256-bit'
$CHPL --fast ms.chpl -o ms_nat
$CHPL --fast --ccflags "$V512" ms.chpl -o ms_tuned
$CHPL --fast --no-ieee-float --ccflags "$V512" ms.chpl -o ms_fm
rm -f ms.chpl
