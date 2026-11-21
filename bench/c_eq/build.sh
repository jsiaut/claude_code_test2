#!/bin/sh
# C23, clang 23.1.5 (LLVM) — optimisation maximale pour la machine cible
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=chk : mode R1, vérifications activées par l'option documentée
# (-fsanitize=array-bounds -fsanitize-trap=array-bounds) ; sans MS_MODE, la commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  chk) MODE="-fsanitize=array-bounds -fsanitize-trap=array-bounds" ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
# v4, point 2 (docs/V4_SIZES.md) : tailles redéfinies à la construction par les variables MS_* (tools/sizes/build.py)
DEFS=$(env | grep -E '^MS_(N1|N4|N5|INNER5|N6|N7|K7_LOG2|K7_NB|K8_LONG|K8_REQ|M9)=' | sed 's/^/-D/' | tr '\n' ' ')
clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread $DEFS $MODE -o ms ms.c
