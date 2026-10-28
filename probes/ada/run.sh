#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && cd bin && PATH=/opt/gcc-16/bin:$PATH gnatmake-16 -q -O2 -gnat2022 ../probe.adb -o probe && ./probe
