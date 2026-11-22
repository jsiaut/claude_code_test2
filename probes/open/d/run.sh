#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de D (LDC 1.43.0, options du banc -O3 -release
# -mcpu=native) ; sources des bibliothèques aux étiquettes de dub, sous /opt/open/d. Écrit results/open/probes/d.txt.
set -e
cd "$(dirname "$0")"
L=/opt/open/d
/opt/ldc/bin/ldc2 -O3 -release -mcpu=native -d -I$L/soa-d/source -I$L/mir-algorithm/source -I$L/mir-core/source -i \
  -od=/tmp/d_open_obj -of=/tmp/d_open_probe probe.d
R=$(/tmp/d_open_probe)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/d.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), D : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/ldc/bin/ldc2 --version | head -1)"
echo "CAP;A6;1;soa 0.2.0;[exécutée] $(r A6 soa)"
echo "NOTE;A6;note publiée 0 ; type SoA engendré à la compilation (un tableau par champ), accès par élément et par champ, tranches et intervalles : 1, comme std.MultiArrayList de Zig"
echo "CAP;F1;1;mir-algorithm 3.22.5;[exécutée] $(r F1 mir-algorithm)"
echo "NOTE;F1;note publiée ½ (tableaux statiques de tableaux statiques) ; tranche multidimensionnelle contiguë de dimensions connues à l'exécution : 1"
} > $OUT
cat $OUT
