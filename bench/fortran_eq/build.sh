#!/bin/sh
# Fortran 2018 + OpenMP 5, gfortran 16.2 : -O3 -march=native -fopenmp ;
# noyaux tuned (tuned.f90) avec en plus -mprefer-vector-width=512.
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=chk : mode R1, vérifications activées par l'option documentée
# (-fcheck=bounds) ; sans MS_MODE, la commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  chk) MODE=-fcheck=bounds ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
FC=/opt/gcc-16/bin/gfortran-16
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut ; module
# de constantes seulement (sizes.f90), compilé pour son .mod, sans objet à lier.
cat > sizes.f90 <<EOF
! Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
! publiées.
module ms_sizes
  implicit none
  integer, parameter :: SIZE_N1 = ${MS_N1:-4194304}, SIZE_INNER5 = ${MS_INNER5:-65536}
  integer, parameter :: SIZE_N6 = ${MS_N6:-16777216}, SIZE_N7 = ${MS_N7:-16777216}
  integer, parameter :: SIZE_K7_LOG2 = ${MS_K7_LOG2:-20}, SIZE_K7_NB = ${MS_K7_NB:-1048573}
  integer, parameter :: SIZE_K8_LONG = ${MS_K8_LONG:-20}, SIZE_K8_REQ = ${MS_K8_REQ:-10}, SIZE_M9 = ${MS_M9:-2048}
end module
EOF
$FC -c sizes.f90 -o sizes.o
$FC -O3 -march=native -mprefer-vector-width=512 -fopenmp $MODE -c tuned.f90 -o tuned.o
$FC -O3 -march=native -fopenmp $MODE -o ms ms.f90 tuned.o
rm -f *.mod *.o
