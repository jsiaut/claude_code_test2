#!/bin/sh
# Remarque sur Odin (docs/ODIN.md) : source de la campagne (bench/odin/ms.odin) recompilé sur l'hôte avec les options du
# banc (Odin dev-2026-10, -o:speed), référence des mesures appariées.
set -e
cd "$(dirname "$0")"
/opt/src/odin/odin build ../odin/ms.odin -file -o:speed -microarch:native -out:ms
