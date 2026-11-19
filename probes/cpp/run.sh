#!/bin/sh
# Sonde de C++ : audit de la grille (audit/, docs/V4_PLAN.md 2.1), qui remplace la première sonde (probe.cpp, conservée).
# Sortie : results/probes/cpp.txt
exec sh "$(dirname "$0")/audit/run.sh"
