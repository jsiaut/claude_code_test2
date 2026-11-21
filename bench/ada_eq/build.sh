#!/bin/sh
# Ada 2022, GNAT 16.2 (gnatmake-16) : -O3 -march=native ; vérifications à l'exécution par défaut
# (les variantes tuned les suppriment localement par pragma Suppress).
set -e
cd "$(dirname "$0")"
export PATH=/opt/gcc-16/bin:$PATH
# Tailles (v4, point 2 : docs/V4_SIZES.md) : symboles du préprocesseur intégré de GNAT ($MS_N1…), valeurs des
# variables MS_*, ou publiées par défaut ; le préprocesseur garde les numéros de ligne.
DEFS="-gnateDMS_N1=${MS_N1:-4_194_304} -gnateDMS_INNER5=${MS_INNER5:-65_536} -gnateDMS_N6=${MS_N6:-16_777_216}"
DEFS="$DEFS -gnateDMS_N7=${MS_N7:-16_777_216} -gnateDMS_K7_LOG2=${MS_K7_LOG2:-20} -gnateDMS_K8_LONG=${MS_K8_LONG:-20}"
DEFS="$DEFS -gnateDMS_K8_REQ=${MS_K8_REQ:-10} -gnateDMS_M9=${MS_M9:-2048}"
gnatmake-16 -q -O3 -gnat2022 -gnatwa -gnatwI ms.adb -o ms -cargs -march=native $DEFS -largs -pthread
rm -f *.ali *.o
