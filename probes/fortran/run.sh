#!/bin/sh
# Sonde de Fortran : probe.f90, probe_errata.f90 et probe_f2.f90 (premières sondes) puis audit de la grille (audit/,
# docs/V4_PLAN.md 2.1). Sortie : results/probes/fortran.txt
G=/opt/gcc-16/bin/gfortran-16
cd "$(dirname "$0")" && mkdir -p bin && $G -O2 probe.f90 -o bin/probe -J bin && bin/probe | grep -E "^CAP;(A5|B5|C5);" | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
$G -O2 -fpack-derived -fopenmp -fopenmp-allocators probe_errata.f90 -o bin/probe_errata -J bin && bin/probe_errata > bin/probe_errata.out
grep -E "^CAP;(A3|B2);" bin/probe_errata.out | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
grep -E "^CAP;A4;" bin/probe_errata.out | sed "s/^CAP;A4;[0-9.]*;/CAP;A4;1;[exécutée] /; s/\$/ (directives OpenMP livrées avec gfortran ; ½ en v1)/"
$G -O2 -fcoarray=lib probe_f2.f90 -o bin/probe_f2 -lcaf_shmem -J bin && bin/probe_f2 | sed "s/^\(CAP;[A-Z0-9]*;[0-9.]*;\)/\1[exécutée] /"
exec sh audit/run.sh
