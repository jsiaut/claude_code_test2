#!/bin/sh
# Mojo 1.2.0 (compilateur open source depuis le 2026-08-18) — mojo build (optimisé par défaut, CPU hôte)
set -e
cd "$(dirname "$0")"
/opt/mojo-venv/bin/mojo build ms.mojo -o ms 2>&1 | grep -v Crashpad
