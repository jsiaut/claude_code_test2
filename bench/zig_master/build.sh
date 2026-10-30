#!/bin/sh
# Annexe : Zig 0.18.0-dev.753+1420479be (master du 29/10/2026, LLVM 23.1.4), vectoriseur de boucles réactivé.
# Même source que bench/zig (compilée telle quelle), mêmes options. Voir docs/ZIG.md.
set -e
cd "$(dirname "$0")"
/opt/zig-master/zig build-exe ../zig/ms.zig -O fast -mcpu native -femit-bin=ms 2>&1
