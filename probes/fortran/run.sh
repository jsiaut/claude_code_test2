#!/bin/sh
G=/opt/gcc-16/bin/gfortran-16
cd "$(dirname "$0")" && mkdir -p bin && $G -O2 probe.f90 -o bin/probe && bin/probe && \
  $G -O2 -fpack-derived -fopenmp -fopenmp-allocators probe_errata.f90 -o bin/probe_errata -J bin && bin/probe_errata && \
  $G -O2 -fcoarray=lib probe_f2.f90 -o bin/probe_f2 -lcaf_shmem && bin/probe_f2
