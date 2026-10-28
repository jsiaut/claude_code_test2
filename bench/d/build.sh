#!/bin/sh
# LDC 1.43.0 (frontend D 2.113, LLVM 21.1.8) — mode release standard : -O3 -release, -mcpu=native
set -e
cd "$(dirname "$0")"
/opt/ldc/bin/ldc2 -O3 -release -mcpu=native -of=ms ms.d
