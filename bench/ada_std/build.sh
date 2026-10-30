#!/bin/sh
# Copie standard de bench/ada (docs/CONFRONTATION.md) : mêmes options, plus la largeur de vecteur 512 bits (permise par
# le plan, section 4.1 : elle remplace celle que le type vectoriel GCC de 512 bits imposait dans la version d'origine).
set -e
cd "$(dirname "$0")"
export PATH=/opt/gcc-16/bin:$PATH
gnatmake-16 -q -O3 -gnat2022 -gnatwa -gnatwI ms.adb -o ms -cargs -march=native -mprefer-vector-width=512 -largs -pthread
rm -f *.ali *.o
