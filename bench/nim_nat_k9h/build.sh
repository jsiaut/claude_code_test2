#!/bin/sh
# Sensibilité de la remarque sur Nim (docs/NIM.md) : K9 naturel en ref array[M9, array[M9, float]] ; mêmes options que bench/nim.
set -e
cd "$(dirname "$0")"
/opt/nim/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 \
  --passC:"-march=native" --threads:on --mm:orc --hints:off --warnings:off --nimcache:./nimcache -o:ms ms.nim
