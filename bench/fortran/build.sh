#!/bin/sh
# Fortran 2018 + OpenMP 5, gfortran 16.2 : -O3 -march=native -fopenmp ;
# noyaux tuned (tuned.f90) avec en plus -mprefer-vector-width=512.
set -e
cd "$(dirname "$0")"
FC=/opt/gcc-16/bin/gfortran-16
$FC -O3 -march=native -mprefer-vector-width=512 -fopenmp -c tuned.f90 -o tuned.o
$FC -O3 -march=native -fopenmp -o ms ms.f90 tuned.o
rm -f *.mod *.o
