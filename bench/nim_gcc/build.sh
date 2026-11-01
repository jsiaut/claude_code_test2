#!/bin/sh
# Information (remarque sur Nim, docs/NIM.md) : source de la campagne compilé par Nim 2.2.12 vers C puis gcc 16 (au lieu de clang 23).
set -e
cd "$(dirname "$0")"
/opt/nim/bin/nim c -d:release --cc:gcc --gcc.exe:/opt/gcc-16/bin/gcc-16 --gcc.linkerexe:/opt/gcc-16/bin/gcc-16 \
  --passC:"-march=native" --threads:on --mm:orc --hints:off --warnings:off --nimcache:./nimcache -o:ms ../nim/ms.nim
