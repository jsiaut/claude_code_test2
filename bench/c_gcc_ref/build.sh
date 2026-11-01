#!/bin/sh
# Remarque sur C : source C de la campagne, gcc 16, options de l'annexe c_gcc
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/gcc-16 -std=c23 -O3 -march=native -pthread -o ms ../c/ms.c
