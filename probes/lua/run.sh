#!/bin/sh
# Sonde de Lua : audit de la grille (audit/, docs/V4_PLAN.md 2.1), qui reprend les cas de la première sonde (base.sh).
# Sortie : results/probes/lua.txt
cd "$(dirname "$0")" && sh audit/run.sh
