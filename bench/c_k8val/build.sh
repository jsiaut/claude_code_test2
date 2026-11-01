#!/bin/sh
# Remarque sur C : arène de K8 construite par une récursion à un seul état passé par valeur, clang 23
set -e
cd "$(dirname "$0")"
clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread -o ms ms.c
