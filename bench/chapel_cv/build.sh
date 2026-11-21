#!/bin/sh
# Chapel 2.10 (compilé depuis les sources, back-end LLVM 22) : chpl --fast, CPU natif.
# Trois binaires, car chpl compile tout le programme d'un seul bloc et ses options sont globales :
# ms_nat (options par défaut, variantes natural*), ms_tuned (vecteurs 512 bits autorisés) et
# ms_fm (idem + --no-ieee-float, pour les seules réductions flottantes réassociables).
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=chk : mode R1, vérifications activées par l'option documentée
# (--checks) ; sans MS_MODE, la commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  chk) MODE=--checks ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native
export CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
CHPL=$CHPL_HOME/bin/linux64-x86_64/chpl
# Tailles redéfinissables (v4, point 2 : docs/V4_SIZES.md) ; sans variable MS_*, les binaires publiés
DEFS=$(env | grep -E '^MS_(N1|INNER5|N6|N7|K7_LOG2|K8_LONG|K8_REQ|M9)=' | sed 's/^/-s/' | tr '\n' ' ')
$CHPL --fast $MODE $DEFS ms.chpl -o ms_nat
# chpl ne transmet pas -mprefer-vector-width à son générateur LLVM (vérifié : binaire inchangé) ;
# on retire la préférence 256 bits du CPU cible via un attribut de cible clang.
V512='-Xclang -target-feature -Xclang -prefer-256-bit'
$CHPL --fast $MODE $DEFS --ccflags "$V512" ms.chpl -o ms_tuned
# réductions flottantes réassociables (k1 aos/soa, k5 tuned) : en plus --no-ieee-float (global dans chpl)
$CHPL --fast $MODE $DEFS --no-ieee-float --ccflags "$V512" ms.chpl -o ms_fm
