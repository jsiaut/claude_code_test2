#!/bin/sh
# Copie de la remarque sur BQN (docs/BQN.md, 5.4) : bench/bqn_rq/ms.bqn avec la construction native (/opt/cbqn)
set -e
cd "$(dirname "$0")"
/opt/cbqn/bin/BQN -p '1+1' > /dev/null
