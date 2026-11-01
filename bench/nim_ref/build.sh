#!/bin/sh
# Remarque sur Nim (docs/NIM.md) : source de la campagne (bench/nim/ms.nim) recompilé sur l'hôte avec les options du banc (Nim 2.2.12 -> clang 23), référence des mesures appariées.
set -e
cd "$(dirname "$0")"
/opt/nim/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 \
  --passC:"-march=native" --threads:on --mm:orc --hints:off --warnings:off --nimcache:./nimcache -o:ms ../nim/ms.nim
