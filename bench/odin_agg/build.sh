#!/bin/sh
# Remarque sur Odin (docs/ODIN.md) : source corrigé (bench/odin_fix/ms.odin) compilé avec -o:aggressive (pipeline O3 de
# LLVM au lieu de O2 ; sensibilité).
set -e
cd "$(dirname "$0")"
/opt/src/odin/odin build ../odin_fix/ms.odin -file -o:aggressive -microarch:native -out:ms
