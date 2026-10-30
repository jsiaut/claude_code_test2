#!/bin/sh
# Sondes de la remarque sur Fortran (docs/FORTRAN.md, section 2), gfortran 16.2 : A3 (-fpack-derived), A4 (alignement
# par OpenMP), B2 (allocateur OpenMP à traits), F2 (cotableaux en mémoire partagée, libcaf_shmem). Usage : run.sh DIR
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?répertoire de sortie}"
mkdir -p "$OUT" && cd "$OUT"
G=/opt/gcc-16/bin/gfortran-16
$G -O2 "$SRC/a3.f90" -o a3 && echo "A3 sans option : $(./a3)"
$G -O2 -fpack-derived "$SRC/a3.f90" -o a3p && echo "A3 avec -fpack-derived : $(./a3p)"
$G -O2 -fopenmp -fopenmp-allocators "$SRC/a4.f90" -o a4 && echo "A4 avec directives OpenMP : $(./a4)"
$G -O2 "$SRC/a4_none.f90" -o a4n && echo "A4 $(./a4n)"
$G -O2 -fopenmp -fopenmp-allocators "$SRC/b2.f90" -o b2 && echo "B2 (réserve de 1 Mio, sans repli) : $(./b2)"
$G -O2 -fcoarray=lib "$SRC/f2.f90" -o f2 -lcaf_shmem && echo "F2 (-fcoarray=lib -lcaf_shmem) : $(./f2)"
echo "libcaf livrées : $(ls /opt/gcc-16/lib/gcc/x86_64-pc-linux-gnu/16.2.0/ | grep caf | tr '\n' ' ')"
