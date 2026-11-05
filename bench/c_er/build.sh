#!/bin/sh
# Remarque sur Swift (docs/SWIFT.md, section 5) : le source de bench/c compilé pour l'hôte Emerald Rapids, par les
# options de bench/c/build.sh ; identique octet pour octet au binaire recompilé sur la machine 3 (empreinte ca4eeb97…,
# results/hw/machine3/binaries.txt), dont viennent K5 publié et la réplication
set -e
cd "$(dirname "$0")"
clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread -o ms ../c/ms.c
