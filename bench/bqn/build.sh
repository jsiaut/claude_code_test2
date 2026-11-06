#!/bin/sh
# BQN : CBQN 0.12.0 (dernière version publiée, étiquette v0.12.0 de github.com/dzaima/CBQN), clang 23, sans replxx
# (édition de ligne du REPL), version=0.12.0 ; docs/BQN.md, 2.1. Le README recommande make o3n (-O3 -march=native)
# pour une construction locale ; pour les clés venues de la machine 1, la construction est celle qu'y donnerait
# make o3n, pour la cible Cascade Lake : make o3 target_from_cc=1 f=-march=cascadelake (Singeli en AVX2, BMI2 et
# AVX-512 F/BW/CD/DQ/VL/VNNI, déduits des macros du compilateur), installée dans /opt/cbqn-cl. La construction native
# de la machine 26 (make o3n, /opt/cbqn) sert à K5 et à la réplication : bench/bqn_er. Le banc est interprété (avec le
# JIT de CBQN) : vérification syntaxique seulement.
set -e
cd "$(dirname "$0")"
/opt/cbqn-cl/bin/BQN -p '1+1' > /dev/null
