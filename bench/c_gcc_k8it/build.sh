#!/bin/sh
# Remarque sur C : source de c_k8it, gcc 16
set -e
cd "$(dirname "$0")"
/opt/gcc-16/bin/gcc-16 -std=c23 -O3 -march=native -pthread -o ms ../c_k8it/ms.c
