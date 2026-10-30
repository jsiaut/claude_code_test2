#!/bin/sh
# Vérification (docs/ZIG.md) : Zig 0.17.0, threads de K3, K6 mt et K9 mt lancés par Io.Group. Mêmes options que bench/zig.
set -e
cd "$(dirname "$0")"
/opt/zig/zig build-exe ms.zig -O fast -mcpu native -femit-bin=ms 2>&1
