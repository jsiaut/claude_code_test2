#!/bin/sh
# Zig 0.17.0 (LLVM 22.1.8) — -O fast (ex-ReleaseFast), -mcpu native
set -e
cd "$(dirname "$0")"
/opt/zig/zig build-exe ms.zig -O fast -mcpu native -femit-bin=ms 2>&1
