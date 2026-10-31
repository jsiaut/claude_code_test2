#!/bin/sh
# Copie standard corrigée (docs/CHAPEL.md, docs/CONFRONTATION.md) : un seul binaire, compilé comme ms_tuned de l'original
# (--fast, vecteurs 512 bits autorisés), sans --no-ieee-float ; il sert à toutes les variantes mesurées de la copie.
set -e
cd "$(dirname "$0")"
export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native
export CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
CHPL=$CHPL_HOME/bin/linux64-x86_64/chpl
V512='-Xclang -target-feature -Xclang -prefer-256-bit'
$CHPL --fast --ccflags "$V512" ms.chpl -o ms_tuned
