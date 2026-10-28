#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/gcc-16/bin/gfortran-16 -O2 probe.f90 -o bin/probe && bin/probe
