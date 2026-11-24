#!/bin/sh
# C23, clang 23.1.5 (LLVM) — optimisation maximale pour la machine cible
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=chk : mode R1, vérifications activées par l'option documentée
# (-fsanitize=array-bounds -fsanitize-trap=array-bounds) ; sans MS_MODE, la commande publiée.
# v5 (docs/V5.md, S2). MS_CC=gcc : la même source par gcc 16.2.0, mêmes options ; mode vérifié : l'option équivalente
# de gcc. Sans MS_CC, clang : la chaîne de référence, commande inchangée.
case "${MS_CC:-clang}" in
  clang) CC=clang-23; CHK="-fsanitize=array-bounds -fsanitize-trap=array-bounds" ;;
  gcc) CC=/opt/gcc-16/bin/gcc-16; CHK="-fsanitize=bounds -fsanitize-trap=bounds" ;;
  *) echo "MS_CC=$MS_CC : compilateur inconnu" >&2; exit 2 ;;
esac
case "${MS_MODE:-}" in
  "") MODE="" ;;
  chk) MODE=$CHK ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
# v4, point 2 (docs/V4_SIZES.md) : tailles redéfinies à la construction par les variables MS_* (tools/sizes/build.py)
DEFS=$(env | grep -E '^MS_(N1|N4|N5|INNER5|N6|N7|K7_LOG2|K7_NB|K8_LONG|K8_REQ|M9)=' | sed 's/^/-D/' | tr '\n' ' ')
$CC -std=c23 -O3 -march=native -Wall -Wextra -pthread $DEFS $MODE -o ms ms.c
