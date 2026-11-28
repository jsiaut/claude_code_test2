#!/bin/sh
# Sonde d'OxCaml : audit de la grille (audit/, docs/V6_1.md 4.5). Sortie : results/probes/oxcaml.txt
cd "$(dirname "$0")" && sh audit/run.sh
