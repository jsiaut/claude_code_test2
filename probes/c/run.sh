#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && clang-23 -std=c23 -O2 -march=native -pthread -fopenmp -o bin/probe probe.c && bin/probe
