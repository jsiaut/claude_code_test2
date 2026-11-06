#!/bin/sh
# Second témoin du pont de FreePascal (docs/FPC.md, plan 3.2) : la source de bench/c compilée par GCC 16.2 en cible
# cascadelake, identique octet pour octet au binaire des données publiées de c_gcc (167a19fd…, compilé sur la
# machine 2 : results/hw/machine3/binaries.txt) ; bench/c_gcc contient la recompilation de la machine 3
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/gcc-16 -std=c23 -O3 -march=cascadelake -pthread -o ms ../c/ms.c
