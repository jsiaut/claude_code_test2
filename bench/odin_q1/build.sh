#!/bin/sh
# Remarque sur Odin (docs/ODIN.md) : copie de bench/odin/ms.odin modifiée (voir l'en-tête du source), options du banc.
set -e
cd "$(dirname "$0")"
/opt/src/odin/odin build ms.odin -file -o:speed -microarch:native -out:ms
