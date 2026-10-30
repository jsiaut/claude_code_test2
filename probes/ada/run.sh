#!/bin/sh
export PATH=/opt/gcc-16/bin:$PATH
cd "$(dirname "$0")" && mkdir -p bin && cd bin && gnatmake-16 -q -O2 -gnat2022 ../probe.adb -o probe && ./probe && gnatmake-16 -q -O3 -gnat2022 -march=native ../probe_errata.adb -o probe_errata && ./probe_errata
