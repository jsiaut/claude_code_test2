#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 6) : b3, la boucle de référence de l'écrivain unique (tools/k3_align.c) à ses 16
# décalages dans une ligne de 64 octets, deux exécutions : la commande de tools/equal/k3_ref.sh (point 3), sortie dans
# results/open. Usage : k3_ref.sh <start|end> <machine> <moment> ; sortie : results/open/k3_ref_<start|end>.txt
cd "$(dirname "$0")/../.."
W=$1; M=$2; T=$3
clang-23 -O2 -march=native -o /dev/shm/k3_align tools/k3_align.c || exit 1
{ echo "# tools/k3_align.c (clang-23 -O2 -march=native), $M, $(date -u '+%Y-%m-%d %H:%M') UTC, $T"
  /dev/shm/k3_align; echo "--- deuxième exécution"; /dev/shm/k3_align; } > results/open/k3_ref_$W.txt
cat results/open/k3_ref_$W.txt
