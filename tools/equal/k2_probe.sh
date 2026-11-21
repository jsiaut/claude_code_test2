#!/bin/sh
# v4, point 3 (docs/V4_EQUAL.md, 3.5) : sonde du mécanisme des deux régimes de K2 à 8 Mio, descriptive.
# K2 tuned du C publié (bench/c), 8 Mio, 5 répétitions par processus ; 20 processus par condition, conditions
# alternées : « aslr » (adresses aléatoires, par défaut), « fixe » (setarch -R), « thp » (GLIBC_TUNABLES
# glibc.malloc.hugetlb=1 : malloc marque ses régions MADV_HUGEPAGE ; pages géantes de l'hôte en mode madvise).
# Pour chaque processus : médiane des répétitions (s) et AnonHugePages relevé pendant l'exécution (Kio).
# Sortie : results/equal/k2_probe.txt
cd "$(dirname "$0")/../.."
OUT=results/equal/k2_probe.txt
{ echo "# tools/equal/k2_probe.sh, $(date -u '+%Y-%m-%d %H:%M UTC'), $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2)"
  echo "# condition processus médiane_s AnonHugePages_kio"; } > $OUT
for i in $(seq 1 20); do
  for c in aslr fixe thp; do
    case $c in
      aslr) pre="";;
      fixe) pre="setarch -R";;
      thp) pre="env GLIBC_TUNABLES=glibc.malloc.hugetlb=1";;
    esac
    MS_DATA=/opt/msdata WARMUP=1 $pre bench/c/ms k2 tuned 5 8388608 > /dev/shm/k2p.out &
    pid=$!
    sleep 0.4
    ahp=$(awk '/AnonHugePages/ {print $2}' /proc/$pid/smaps_rollup 2>/dev/null)
    wait $pid
    med=$(awk -F';' '/^RESULT/ {print $6}' /dev/shm/k2p.out | sort -g | awk '{t[NR]=$1} END {print t[int((NR+1)/2)]}')
    echo "$c $i $med ${ahp:-?}" >> $OUT
  done
done
rm -f /dev/shm/k2p.out
echo "sonde écrite dans $OUT"
