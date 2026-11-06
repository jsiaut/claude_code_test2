#!/bin/sh
# Sonde de BQN (CBQN 0.12.0, binaire du banc publié : /opt/cbqn-cl) : probe.bqn (cas exécutés). Sortie : results/probes/bqn.txt
cd "$(dirname "$0")" && /opt/cbqn-cl/bin/BQN probe.bqn
