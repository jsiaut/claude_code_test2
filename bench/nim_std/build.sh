#!/bin/sh
# Copie standard de bench/nim (docs/CONFRONTATION.md) : mêmes options, plus la largeur de vecteur 512 bits (permise par
# le plan, section 4.1 : elle remplace celle que les intrinsèques AVX-512 imposaient dans la version d'origine).
set -e
cd "$(dirname "$0")"
/opt/nim/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 \
  --passC:"-march=native -mprefer-vector-width=512" --threads:on --mm:orc --hints:off --warnings:off \
  --nimcache:./nimcache -o:ms ms.nim
