#!/bin/sh
# K5 naturel sur la machine 3 : pourquoi GCC évite la chaîne de FMA et clang non. Même boucle s += a[i]*b[i].
# Compte des FMA scalaires dans la fonction, puis temps de 65 536 produits de 2 048 flottants (meilleur de 5).
cd "$(dirname "$0")" && G=/opt/gcc-16/bin
fma() { objdump -d --no-show-raw-insn "$1" | awk '/<dot[^>]*>:/{f=1;next} /^$/{f=0} f' | grep -cE "vfn?madd[0-9]+ss"; }
loop() { objdump -d --no-show-raw-insn "$1" | awk '/<dot[^>]*>:/,0' | grep -m3 -oE "vmulps|vmulss|vfmadd[0-9]+ss|vaddss" | tr '\n' ' '; }
clang-23 -O2 -c main.c -o main.o
for v in "gcc:-std=c23" "gcc:-std=gnu23" "gcc:-std=gnu23 --param avoid-fma-max-bits=0" "clang:-std=c23" \
         "clang:-std=c23 -ffp-contract=off" "clang:-std=c23 -mllvm -force-ordered-reductions"; do
  cc=${v%%:*}; fl=${v#*:}
  if [ $cc = gcc ]; then $G/gcc-16 -O3 -march=native $fl -c dot.c -o d.o; else clang-23 -O3 -march=native $fl -c dot.c -o d.o; fi
  clang-23 main.o d.o -o t && echo "$cc $fl : FMA $(fma d.o) ; boucle : $(loop d.o); $(./t)"
done
$G/g++-16 -std=c++26 -O3 -march=native -c dot.cpp -o a.o && echo "g++ -std=c++26 : FMA $(fma a.o) ; boucle : $(loop a.o)"
$G/gfortran-16 -O3 -march=native -c dot.f90 -o f.o && echo "gfortran : FMA $(fma f.o) ; boucle : $(loop f.o)"
rm -f *.o t
