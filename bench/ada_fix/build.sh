#!/bin/sh
# Copie corrigée (docs/ADA.md) : même compilation que bench/ada.
# Ada 2022, GNAT 16.2 (gnatmake-16) : -O3 -march=native ; vérifications à l'exécution par défaut
# (les variantes tuned les suppriment localement par pragma Suppress).
set -e
cd "$(dirname "$0")"
export PATH=/opt/gcc-16/bin:$PATH
gnatmake-16 -q -O3 -gnat2022 -gnatwa -gnatwI ms.adb -o ms -cargs -march=native -largs -pthread
rm -f *.ali *.o
