#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte d'Ada (GNAT 16, options du banc : -O3 -gnat2022
# -march=native) ; lwt et cachelines aux commits de l'index d'Alire, sous /opt/open/ada. Écrit results/open/probes/ada.txt.
set -e
cd "$(dirname "$0")"
export PATH=/opt/gcc-16/bin:$PATH
A=/opt/open/ada
CL=$A/ada-cachelines/src
mkdir -p /tmp/ada_open && cp probe.adb tid.c /tmp/ada_open/ && cd /tmp/ada_open
gcc -O2 -c tid.c -o tid.o
gnatmake-16 -q -O3 -gnat2022 probe.adb -o probe -aI$A/parasail/lwt -aI$CL -aI$CL/alignment/128 -aI$CL/linux/common \
  -aI$CL/linux/x86_64 -aI$CL/platform_common -cargs -march=native -largs tid.o -lgomp -pthread
R=$(./probe)
cd - >/dev/null
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/ada.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Ada : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(gnatmake-16 --version | head -1)"
echo "CAP;C5;1;lwt 1.2.0;[exécutée] $(r C5 lwt)"
echo "NOTE;C5;note publiée 0 (boucles parallèles d'Ada 2022 non implémentées par GNAT) ; boucle parallèle par tranches (Par_Range_Loop, Par_Iterator_Loop), réduction par sommes partielles indexées par la tranche, motif de ses exemples : 1"
echo "CAP;D3;1;cachelines 0.1.0;[exécutée] $(r D3 cachelines)"
echo "NOTE;D3;note publiée 0 ; constante de ligne (Destructive_Interference_Size) et type générique bourré et aligné (Cachelines.Padded, groupes) : 1"
} > $OUT
cat $OUT
