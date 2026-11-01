#!/bin/sh
# Odin dev-2026-10 (LLVM 22) — -o:speed, -microarch:native
set -e
cd "$(dirname "$0")"
/opt/src/odin/odin build ms.odin -file -o:speed -microarch:native -out:ms
