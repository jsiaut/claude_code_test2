#!/bin/sh
# Odin dev-2026-10 (LLVM 22) — -o:speed, -microarch:native
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=unc : mode R1', sans vérifications (-no-bounds-check) ; sans MS_MODE,
# la commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  unc) MODE=-no-bounds-check ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
# Tailles redéfinissables (v4, point 2 : docs/V4_SIZES.md) ; sans variable MS_*, le binaire publié
DEFS=$(env | grep -E '^MS_(N1|N4|N5|INNER5|N6|N7|K7_LOG2|K7_NB|K8_LONG|K8_REQ|M9)=' | sed 's/^/-define:/' | tr '\n' ' ')
/opt/src/odin/odin build ms.odin -file -o:speed -microarch:native $MODE $DEFS -out:ms
