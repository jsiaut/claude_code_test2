#!/bin/sh
# Copie standard de bench/fortran (docs/CONFRONTATION.md) : tuned.f90 (k1_soa, k5_tuned, q6_tuned, q1_tuned, mesurés
# à partir de cette copie) est compilé SANS -fopenmp, avec -mprefer-vector-width=512 comme l'original ; ms.f90 (harnais,
# variantes naturelles et noyaux multi-threads, non mesurés à partir de cette copie) est compilé comme l'original.
set -e
cd "$(dirname "$0")"
FC=/opt/gcc-16/bin/gfortran-16
$FC -O3 -march=native -mprefer-vector-width=512 -c tuned.f90 -o tuned.o
$FC -O3 -march=native -fopenmp -o ms ms.f90 tuned.o
rm -f *.mod *.o
