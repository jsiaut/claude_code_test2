#!/bin/sh
# Remarque sur Julia (docs/JULIA.md, section 2) : les cinq variantes de K10 tuned, une par processus, 4 répétitions ;
# V1 (capture, attente active sans yield) se bloque : tuée par SIGKILL au bout de 40 s.
# Sortie : results/julia_check/k10_variants.txt
cd "$(dirname "$0")/../.."
OUT=results/julia_check/k10_variants.txt
mkdir -p results/julia_check
echo "# K10 tuned, variantes (tools/julia_check/k10_variants.jl), Julia $(/opt/julia/bin/julia --version | cut -d' ' -f3), -t 4" > $OUT
for v in V0 V1 V2 V3 V4; do
  timeout -s KILL 40 /opt/julia/bin/julia -O3 -t 4 --startup-file=no tools/julia_check/k10_variants.jl $v 4 >> $OUT 2>&1
  rc=$?
  [ $rc -ne 0 ] && echo "$v : arrêté au bout de 40 s (code $rc, SIGKILL) : bloqué" >> $OUT
done
cat $OUT
