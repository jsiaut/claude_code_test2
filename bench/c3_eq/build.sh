#!/bin/sh
# C3 0.8.5_1 (LLVM 23.1.5) — -O3 (optimisé, sans vérifications), --x86cpu=native
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=chk : mode R1, vérifications activées par l'option documentée
# (--safe=yes) ; sans MS_MODE, la commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  chk) MODE=--safe=yes ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut
cat > sizes.c3 <<EOF
// Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
// publiées.
module ms;
const SIZE_N1 = ${MS_N1:-4194304};
const SIZE_INNER5 = ${MS_INNER5:-65536};
const SIZE_N6 = ${MS_N6:-16777216};
const SIZE_K7_LOG2 = ${MS_K7_LOG2:-20};
const SIZE_K8_LONG = ${MS_K8_LONG:-20};
const SIZE_K8_REQ = ${MS_K8_REQ:-10};
const SIZE_M9 = ${MS_M9:-2048};
EOF
/opt/src/c3c/build/c3c compile ms.c3 sizes.c3 -O3 $MODE --x86cpu=native -o ms
