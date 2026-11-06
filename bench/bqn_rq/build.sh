#!/bin/sh
# Copie de la remarque sur BQN (docs/BQN.md, 5.4) : même binaire que bench/bqn (/opt/cbqn-cl) ; vérification de syntaxe
set -e
cd "$(dirname "$0")"
/opt/cbqn-cl/bin/BQN -p '1+1' > /dev/null
