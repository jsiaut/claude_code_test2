#!/bin/sh
# Mêmes sources que bench/fortran, compilées par LLVM Flang 23 (-O3 -march=native -fopenmp, OpenMP 5.0) ;
# noyaux tuned avec en plus -mprefer-vector-width=512.
set -e
cd "$(dirname "$0")"
S=../fortran
flang-23 -O3 -march=native -mprefer-vector-width=512 -fopenmp -fopenmp-version=50 -c $S/tuned.f90 -o tuned.o
flang-23 -O3 -march=native -fopenmp -fopenmp-version=50 -o ms $S/ms.f90 tuned.o
rm -f *.mod *.o
