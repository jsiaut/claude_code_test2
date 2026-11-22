#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de JavaScript (Node 26.12.1, comme le banc) ; modules
# de /opt/open/js (package-lock.json dans results/open/lock/js). Écrit results/open/probes/js.txt.
set -e
cd "$(dirname "$0")"
R=$(/opt/node26/bin/node --expose-gc probe.js)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/js.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), JavaScript : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, Node $(/opt/node26/bin/node --version)"
echo "CAP;B2;0.5;@protobufjs/pool 1.1.0;[exécutée] $(r B2 @protobufjs/pool)"
echo "NOTE;B2;note publiée 0 ; allocateur de tranches d'octets dans un bloc commun (Uint8Array), comme ArrayPool de C# : ni objets JavaScript, ni libération d'un coup ; limitée, ½"
echo "CAP;F1;1;ndarray 1.1.1;[exécutée] $(r F1 ndarray)"
echo "NOTE;F1;note publiée 0 ; tableau à n dimensions sur un tableau typé contigu, de forme connue à l'exécution, vues : 1"
} > $OUT
cat $OUT
