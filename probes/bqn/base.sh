#!/bin/sh
# Première sonde (conservée) ; run.sh la reprend, étiquette ses lignes et y ajoute l audit de la grille.
# Sonde de BQN (CBQN 0.12.0, binaire du banc publié : /opt/cbqn-cl) : probe.bqn (cas exécutés). Sortie : results/probes/bqn.txt
cd "$(dirname "$0")" && /opt/cbqn-cl/bin/BQN probe.bqn
