#!/bin/sh
# Copie de la remarque sur Mojo (docs/MOJO.md) : bench/mojo plus K4 en SIMD explicite (variantes simd_unsorted
# et simd_cold, hors spécification : sensibilité seulement). Même compilation que bench/mojo.
set -e
cd "$(dirname "$0")"
/opt/mojo-venv/bin/mojo build ms.mojo -o ms 2>&1 | grep -v Crashpad
