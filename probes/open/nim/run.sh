#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Nim (nim 2.2.12, options du banc : -d:release,
# clang 23, -march=native, --threads:on, --mm:orc), bibliothèques de /opt/open/nim/pkgs. Écrit results/open/probes/nim.txt.
set -e
cd "$(dirname "$0")"
P=/opt/open/nim/pkgs/pkgs2
/opt/nim/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 --passC:"-march=native" \
  --threads:on --mm:orc --hints:off --warnings:off --NimblePath:$P --nimcache:/tmp/nimcache_open -o:/tmp/nim_open_probe probe.nim
R=$(/tmp/nim_open_probe)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
fma=$(objdump -d --no-show-raw-insn /tmp/nim_open_probe | awk '/^[0-9a-f]+ <c1dot>:/ {on=1; next} /^[0-9a-f]+ </ {on=0} on && /vfmadd[0-9]*ps/ && /%ymm/ {n++} END {print n+0}')
M=$(ls -d $P/mmops-*)/mmops.nim
n256=$(grep -c "mm256_" $M || true); n512=$(grep -c "mm512_" $M || true);
OUT=../../../results/open/probes/nim.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Nim : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/nim/bin/nim --version | head -1)"
echo "CAP;C1;0.5;mmops 0.1.1;[exécutée] $(r C1 mmops) ; code machine de c1dot : $fma vfmadd…ps sur ymm"
echo "NOTE;C1;note publiée 0 ; [recherche] mmops.nim : $n256 appels mm256_, $n512 mm512_ ; {.passC: \"-mavx2 -mfma\".} : types vectoriels à opérateurs, mais x86 AVX2 seulement, 256 bits seulement (ni AVX-512, ni NEON) : limitée, ½"
echo "CAP;F1;1;arraymancer 0.7.33;[exécutée] $(r F1 arraymancer)"
echo "NOTE;F1;note publiée ½ (array[M, array[N, T]] fixe) ; tenseur contigu de dimensions connues à l'exécution : 1"
} > $OUT
cat $OUT
