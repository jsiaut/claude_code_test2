#!/bin/sh
# Caractérisation d'une machine avant qu'elle mesure (docs/METHOD.md, 6 ; lancée par tools/final/machine.sh),
# sur une machine au repos. Usage : tools/sizes/hwchar.sh [répertoire de sortie] (par défaut results/hw/machine31).
# * tools/hwprobe.c, compilé sur l'hôte : fréquence, latences (jusqu'à 1 Gio, pages de 4 Kio et pages géantes),
#   bandes passantes par taille, STREAM, pic de calcul, TLB, appel système, défaut de page ;
# * chaîne de pointeurs de K2 (implémentation C, variante tuned, 5 répétitions) aux dix tailles publiées et à 512 Mio,
#   1 Gio et 2 Gio (données produites par tools/gendata.c dans /dev/shm, une taille à la fois) : situe le L3 effectif.
set -e
cd "$(dirname "$0")/../.."
OUT=${1:-results/hw/machine31}
mkdir -p "$OUT" /dev/shm/msbuild
H=/dev/shm/msbuild/hwprobe
gcc -O3 -march=native -pthread tools/hwprobe.c -o $H  # -O3 : en -O2, GCC 13 garde les accumulateurs de peak en mémoire
{ echo "# gcc -O3 -march=native -pthread tools/hwprobe.c ($(gcc --version | head -1)), $(date -u '+%Y-%m-%d %H:%M UTC')"
  grep -m1 "model name" /proc/cpuinfo; grep -m1 -E "^model\s" /proc/cpuinfo; grep -m1 "stepping" /proc/cpuinfo
  grep -m1 "cpu MHz" /proc/cpuinfo; grep -m1 "cache size" /proc/cpuinfo; grep -m1 "microcode" /proc/cpuinfo
  nproc; free -b | head -2; uname -r; } > "$OUT/host.txt"
lscpu > "$OUT/lscpu.txt"
for m in freq lat lathp bw stream peak tlb sys pf; do $H $m > "$OUT/$m.txt" 2>&1; done
# chaîne de K2 jusqu'à 2 Gio
[ -x bench/c/ms ] || sh bench/c/build.sh
D=/dev/shm/ms_k2_char
G=tools/sizes/gendata
[ -x $G ] || gcc -O2 -o $G tools/gendata.c
echo "# K2 tuned (bench/c), 4 200 000 sauts dépendants par répétition, 5 répétitions : taille (octets), ns par saut (min, médiane)" > "$OUT/k2_chain.txt"
for S in 16384 65536 262144 524288 2097152 8388608 16777216 33554432 67108864 268435456 536870912 1073741824 2147483648; do
  if [ -f /opt/msdata/k2_chase_$S.u32 ]; then DIR=/opt/msdata; else
    rm -rf $D; mkdir -p $D; $G $D --only k2 --k2 $S > /dev/null; DIR=$D; fi
  MS_DATA=$DIR WARMUP=1 bench/c/run k2 tuned 5 $S | awk -F';' '/^RESULT/ {print $6}' | sort -g > /dev/shm/msbuild/k2t
  awk -v S=$S '{t[NR] = $1} END {printf "%12d  %8.2f  %8.2f\n", S, t[1] / 4200000 * 1e9, t[3] / 4200000 * 1e9}' \
    /dev/shm/msbuild/k2t >> "$OUT/k2_chain.txt"
done
rm -rf $D
echo "caractérisation écrite dans $OUT"
