#!/bin/sh
# Sonde de Rust : probe.rs (première sonde) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1). Sortie : results/probes/rust.txt
cd "$(dirname "$0")" && mkdir -p bin && rustc --edition 2024 -O -C target-cpu=native -o bin/probe probe.rs && bin/probe | grep -E "^CAP;(A5|E2);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
