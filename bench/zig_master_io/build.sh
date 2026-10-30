#!/bin/sh
# Vérification (docs/ZIG.md) : source de bench/zig_io compilée par Zig 0.18.0-dev.753+1420479be. Mêmes options.
set -e
cd "$(dirname "$0")"
/opt/zig-master/zig build-exe ../zig_io/ms.zig -O fast -mcpu native -femit-bin=ms 2>&1
