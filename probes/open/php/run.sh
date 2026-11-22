#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de PHP (PHP 8.5.12 avec les réglages du banc) ;
# paquets Composer de /opt/open/php (composer.lock dans results/open/lock/php). Écrit results/open/probes/php.txt.
set -e
cd "$(dirname "$0")"
PHPOPT="-d memory_limit=-1 -d opcache.enable_cli=1 -d opcache.jit=tracing -d opcache.file_update_protection=0"  # bench/php/run
R=$(/opt/php85/bin/php $PHPOPT probe.php 2>&1)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/php.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), PHP : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/php85/bin/php -v | head -1) ; options : $PHPOPT"
echo "CAP;C5;0.5;amphp/parallel-functions 2.0.0;[exécutée] $(r C5 amphp/parallel-functions)"
echo "NOTE;C5;note publiée 0 ; parallelMap répartit le calcul sur des processus (amphp/parallel, sans l'extension parallel en ZTS), données et résultats copiés par sérialisation : limitée, ½, comme multiprocessing.Pool.map de Python"
echo "CAP;F1;1;rindow/rindow-math-matrix 2.2.0;[exécutée] $(r F1 rindow/rindow-math-matrix)"
echo "NOTE;F1;note publiée ½ (tableaux de la FFI ; tableaux PHP imbriqués) ; NDArray de forme connue à l'exécution sur un tampon linéaire : 1 (pilote PHP ; ses opérations ne sont pas compilées)"
} > $OUT
cat $OUT
