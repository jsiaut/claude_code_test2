#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/gcc-16/bin/g++-16 -std=c++26 -O2 -march=native -pthread -Wno-interference-size -o bin/probe probe.cpp && bin/probe
