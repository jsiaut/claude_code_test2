#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Python (CPython 3.15.2 avec GIL, comme le banc),
# environnement virtuel /opt/open/python (requirements.txt dans results/open/lock/python). Écrit results/open/probes/python.txt.
set -e
cd "$(dirname "$0")"
R=$(/opt/open/python/bin/python probe.py)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/python.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Python : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/open/python/bin/python --version)"
echo "CAP;C5;0.5;dask 2026.8.0;[exécutée] $(r C5 dask)"
echo "NOTE;C5;note publiée ½ (multiprocessing.Pool.map) ; tableaux et tâches répartis sur un ordonnanceur à fils, parallèles seulement quand le calcul de chaque bloc rend le GIL (NumPy), ou sur des processus (données copiées) : limitée, ½, inchangée"
echo "CAP;D2;1;atomics 1.0.3;[exécutée] $(r D2 atomics)"
echo "NOTE;D2;note publiée 0 ; entiers atomiques à ordre mémoire explicite par opération (RELAXED, ACQUIRE, RELEASE, ACQ_REL, SEQ_CST), ordre invalide refusé : 1"
echo "CAP;F1;1;numpy 2.5.5 (nommée);[exécutée] $(r F1 numpy)"
echo "NOTE;F1;note publiée ½ (memoryview.cast(shape=…)) ; tableau à n dimensions contigu, de forme connue à l'exécution, vues sans copie : 1"
} > $OUT
cat $OUT
