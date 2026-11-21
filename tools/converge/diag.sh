#!/bin/sh
# v4, point 4 (docs/V4_CONVERGE.md, 4) : diagnostic des écarts sans explication, à machine au repos.
# Sorties : results/converge/diag/{k9.txt, harnais.txt, chapel_q6.txt}. Constructions dans /dev/shm.
set -e
cd "$(dirname "$0")/../.."
OUT=results/converge/diag
mkdir -p "$OUT" /dev/shm/diag
clang-23 -O3 -march=native -o /dev/shm/diag/k9_diag tools/converge/k9_diag.c -lpthread
cc -O2 -o /dev/shm/diag/pecount tools/pecount.c
hdr() { echo "# $1 ; $(date -u '+%Y-%m-%d %H:%M UTC') ; $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2-) ; modèle $(grep -m1 -E '^model\s' /proc/cpuinfo | cut -d: -f2 | tr -d ' ')"; }
# 1. K9 en C : forme de la boucle, décalage des grilles dans leur page, distance entre grilles, pages géantes, fils
{ hdr "tools/converge/k9_diag.c (clang-23 -O3 -march=native), 9 répétitions, médiane (s)"
  for f in auto v512 v256 scal; do for off in 0 16 32 64; do for th in 1 4; do
    /dev/shm/diag/k9_diag $f $off 0 0 $th 9 | grep '^RESULT'; done; done; done
  for f in auto v512; do for gap in 64 2048; do for th in 1 4; do
    /dev/shm/diag/k9_diag $f 64 $gap 0 $th 9 | grep '^RESULT'; done; done; done
  for f in auto v512; do for th in 1 4; do /dev/shm/diag/k9_diag $f 64 0 1 $th 9 | grep '^RESULT'; done; done
  echo "# reprises : décalage 0, un fil, trois fois chaque forme (variation de l'hôte d'une exécution à l'autre)"
  for i in 1 2 3; do for f in auto v512 v256 scal; do /dev/shm/diag/k9_diag $f 0 0 0 1 9 | grep '^RESULT'; done; done
} > "$OUT/k9.txt"
# 2. harnais de K9 : source publiée de Rust (grilles réallouées à chaque répétition) et sa copie au harnais commun
python3 -c "
import sys; sys.path.insert(0, 'tools/equal')
import build as B
B.ensure('rust', 'pub'); B.build('rust_k9h', 'pub')"
{ hdr "K9 de Rust, binaire publié (ancien harnais) et copie bench/rust_k9h (harnais commun), 7 répétitions, pecount"
  for b in rust rust_k9h; do for v in tuned mt; do
    t=$(MS_DATA=/opt/msdata /dev/shm/diag/pecount -o /dev/shm/diag/pe.json -- /dev/shm/msbuild/$b/pub/run k9 $v 7 \
        | awk -F';' '/^RESULT/ {print $6}' | sort -g | tr '\n' ' ')
    pf=$(python3 -c "import json; d=json.load(open('/dev/shm/diag/pe.json')); c=d.get('counts', d); print(c.get('page_faults'))")
    echo "$b $v : temps (s) $t; défauts de page du processus $pf"; done; done
} > "$OUT/harnais.txt"
# 3. Q6 de Chapel selon le nombre de fils de son runtime
python3 -c "
import sys; sys.path.insert(0, 'tools/equal')
import build as B
B.ensure('chapel', 'pub')"
{ hdr "K6 Q6 de Chapel (binaire publié), CHPL_RT_NUM_THREADS_PER_LOCALE = 1 ou 4, 9 répétitions"
  for th in 1 4; do for v in tuned mt; do
    t=$(CHPL_RT_NUM_THREADS_PER_LOCALE=$th MS_DATA=/opt/msdata /dev/shm/msbuild/chapel/pub/run k6 $v 9 q6 \
        | awk -F';' '/^RESULT/ {print $6}' | sort -g | tr '\n' ' ')
    echo "fils du runtime $th, $v : temps (s) $t"; done; done
} > "$OUT/chapel_q6.txt"
echo "diagnostic écrit dans $OUT"
