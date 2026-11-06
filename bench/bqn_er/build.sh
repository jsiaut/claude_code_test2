#!/bin/sh
# BQN, construction native (docs/BQN.md, 2.1) : CBQN 0.12.0, make o3n (-O3 -march=native, Singeli détecté sur l'hôte :
# AVX2, BMI2 et AVX-512 dont VBMI2 et GFNI sur Emerald Rapids), clang 23, sans replxx, version=0.12.0, /opt/cbqn.
# Même source que bench/bqn. Vérification syntaxique seulement.
set -e
cd "$(dirname "$0")"
/opt/cbqn/bin/BQN -p '1+1' > /dev/null
