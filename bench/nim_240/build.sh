#!/bin/sh
# Information (remarque sur Nim, docs/NIM.md) : source de la campagne compilé par Nim 2.4.0 (paquet officiel) vers clang 23.
set -e
cd "$(dirname "$0")"
/opt/nim240/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 \
  --passC:"-march=native" --threads:on --mm:orc --hints:off --warnings:off --nimcache:./nimcache -o:ms ../nim/ms.nim
