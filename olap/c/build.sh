#!/bin/sh
# v7 : référence C du banc OLAP. clang 23 (LLVM), C23, optimisation maximale pour la machine cible, comme bench/c.
# Deux binaires de la même source : olap_p (niveau portable) et olap_s (niveau spécialisé, -DSPECIAL).
# MS_CC=gcc : la même source par gcc 16.
set -e
cd "$(dirname "$0")"
case "${MS_CC:-clang}" in
  clang) CC=clang-23 ;;
  gcc) CC=/opt/gcc-16/bin/gcc-16 ;;
  *) echo "MS_CC=$MS_CC : compilateur inconnu" >&2; exit 2 ;;
esac
$CC -std=c23 -O3 -march=native -Wall -Wextra -pthread -o olap_p olap.c
if [ -f olap_special.h ]; then $CC -std=c23 -O3 -march=native -Wall -Wextra -pthread -DSPECIAL -o olap_s olap.c; fi
