#!/bin/sh
# Mojo 1.2.0 (compilateur open source depuis le 2026-08-18) — mojo build (optimisé par défaut, CPU hôte)
set -e
cd "$(dirname "$0")"
# Tailles et répertoire des données redéfinissables (v4, point 2 : docs/V4_SIZES.md) ; sans variable MS_*, le
# binaire publié
DEFS=$(env | grep -E '^MS_(N1|INNER5|N6|K7_LOG2|K8_LONG|K8_REQ|M9|DATA_DIR)=' | sed 's/^/-D /' | tr '\n' ' ')
/opt/mojo-venv/bin/mojo build $DEFS ms.mojo -o ms 2>&1 | grep -v Crashpad
