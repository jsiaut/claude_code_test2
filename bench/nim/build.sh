#!/bin/sh
# Nim 2.2.12 -> C -> clang 23 (-O3 -march=native) ; -d:release (vérifications à l'exécution conservées)
set -e
cd "$(dirname "$0")"
# Tailles redéfinissables (v4, point 2 : docs/V4_SIZES.md) ; sans variable MS_*, le binaire publié
DEFS=$(env | grep -E '^MS_(N1|N4|N5|INNER5|N6|N7|K7_LOG2|K7_NB|K8_LONG|K8_REQ|M9)=' | sed 's/^/-d:/' | tr '\n' ' ')
/opt/nim/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 \
  --passC:"-march=native" --threads:on --mm:orc --hints:off --warnings:off --nimcache:./nimcache $DEFS -o:ms ms.nim
