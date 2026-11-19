#!/bin/sh
# LDC 1.43.0 (frontend D 2.113, LLVM 21.1.8) — mode release standard : -O3 -release, -mcpu=native
set -e
cd "$(dirname "$0")"
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut
cat > sizes.inc <<EOF
// Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
// publiées.
enum SIZE_N1 = ${MS_N1:-4194304};
enum SIZE_INNER5 = ${MS_INNER5:-65536};
enum SIZE_N6 = ${MS_N6:-16777216};
enum SIZE_K7_LOG2 = ${MS_K7_LOG2:-20};
enum SIZE_K8_LONG = ${MS_K8_LONG:-20};
enum SIZE_K8_REQ = ${MS_K8_REQ:-10};
enum SIZE_M9 = ${MS_M9:-2048};
EOF
/opt/ldc/bin/ldc2 -O3 -release -mcpu=native -J. -of=ms ms.d
