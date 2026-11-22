#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Mojo (Mojo 1.2.0, mojo build par défaut comme le
# banc) avec les paquets Mojo de max-core 26.7.0 (archive conda, /opt/open/mojo/maxcore). Écrit results/open/probes/mojo.txt.
set -e
cd "$(dirname "$0")"
M=/opt/open/mojo/maxcore/lib
/opt/mojo-venv/bin/mojo build -I $M/mojo -Xlinker -L$M -Xlinker -lAsyncRTMojoBindings -Xlinker -rpath -Xlinker $M \
  probe.mojo -o /tmp/mojo_open_probe
R=$(/tmp/mojo_open_probe)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/mojo.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Mojo : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/mojo-venv/bin/mojo --version)"
echo "CAP;C5;1;MAX 26.7.0 (nommée);[exécutée] $(r C5 MAX)"
echo "NOTE;C5;note publiée 0 ; boucle parallèle sur les cœurs (max.algorithm.functional.sync_parallelize, parallelize), réduction par résultats partiels : 1"
echo "CAP;D1;0.5;MAX 26.7.0 (nommée);[exécutée] $(r D1 MAX)"
echo "NOTE;D1;note publiée ½ (seulement runtime._asyncrt, privé) ; MAX donne des éléments de travail parallèles en mémoire partagée (fork-join), mais ni fil à créer ni à joindre : limitée, ½, inchangée"
echo "CAP;F1;1;MAX 26.7.0 (nommée);[exécutée] $(r F1 MAX)"
echo "NOTE;F1;note publiée ½ (pas de tableau multidimensionnel en std) ; LayoutTensor à disposition d'exécution (RuntimeLayout) sur un tampon contigu : 1 ; le compilateur signale LayoutTensor comme remplacé par TileTensor, du même paquet layout"
} > $OUT
cat $OUT
