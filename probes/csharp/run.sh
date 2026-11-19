#!/bin/sh
# Sonde de C# : audit de la grille (audit/, docs/V4_PLAN.md 2.1), qui reprend les quatre cas de la première sonde
# (base.sh). Sortie : results/probes/csharp.txt
cd "$(dirname "$0")" && sh audit/run.sh
