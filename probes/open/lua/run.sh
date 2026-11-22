#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Lua (Lua 5.5.1, interpréteur du banc) ; modules C
# construits par gcc -O2 aux étiquettes des rockspecs (lua-llthreads2 v0.1.6, vmsl v1.1) sous /opt/open/lua/lib.
# Écrit results/open/probes/lua.txt.
set -e
cd "$(dirname "$0")"
L=/opt/open/lua
gcc -O2 -fPIC -shared -I$L/include -DLLTHREAD_MODULE_NAME=llthreads2 $L/src/lua-llthreads2/src/*.c -o $L/lib/llthreads2.so -lpthread
gcc -O2 -fPIC -shared -I$L/include $L/src/vmsl/src/vector.c -o $L/lib/vectors.so -lm
gcc -O2 -fPIC -shared -I$L/include $L/src/vmsl/src/matrix.c -o $L/lib/matrix.so -lm
R=$(/opt/lua55/bin/lua probe.lua)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/lua.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Lua : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/lua55/bin/lua -v)"
echo "CAP;D1;0.5;lua-llthreads2 0.1.6;[exécutée] $(r D1 lua-llthreads2)"
echo "NOTE;D1;note publiée 0 (coroutines seulement) ; vrais fils système en parallèle, mais chacun dans son propre état Lua : données passées par copie (arguments et résultats), aucune mémoire partagée : limitée, ½, comme les processus de PHP"
echo "CAP;F1;1;vmsl 1.1;[exécutée] $(r F1 vmsl)"
echo "NOTE;F1;note publiée 0 ; matrice M×N sur un tampon double contigu, dimensions connues à l'exécution : 1 (deux dimensions seulement, comme les tableaux 2D de C)"
} > $OUT
cat $OUT
