#!/bin/sh
# Sonde de C : audit de la grille (audit/, docs/V4_PLAN.md 2.1), qui remplace la première sonde (probe.c, conservée).
# Sortie : results/probes/c.txt
exec sh "$(dirname "$0")/audit/run.sh"
