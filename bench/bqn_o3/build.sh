#!/bin/sh
# Copie de sensibilité (docs/BQN.md, plan) : CBQN 0.12.0 construit par la cible par défaut du makefile (make o3 :
# -O3, Singeli pour le x86-64 de base, sans -march=native), clang 23, sans replxx, installé dans /opt/cbqn-o3 ;
# même source que bench/bqn. Vérification syntaxique seulement.
set -e
cd "$(dirname "$0")"
/opt/cbqn-o3/bin/BQN -p '1+1' > /dev/null
