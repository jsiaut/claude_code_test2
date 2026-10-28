#!/bin/sh
# Nim 2.2.12 -> C -> clang 23 (-O3 -march=native) ; -d:release (vérifications à l'exécution conservées)
set -e
cd "$(dirname "$0")"
/opt/nim/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 \
  --passC:"-march=native" --threads:on --mm:orc --hints:off --warnings:off --nimcache:./nimcache -o:ms ms.nim
