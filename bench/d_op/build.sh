#!/bin/sh
# LDC 1.43.0 (frontend D 2.113, LLVM 21.1.8) — mode release standard : -O3 -release, -mcpu=native
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=chk : mode R1, vérifications activées par l'option documentée
# (-boundscheck=on) ; MS_MODE=unc : mode R1', sans vérifications (-boundscheck=off) ; sans MS_MODE, la commande
# publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  chk) MODE=-boundscheck=on ;;
  unc) MODE=-boundscheck=off ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
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
# v4, point 6 (docs/V4_OPEN.md, 5.2) : la commande publiée, plus soa 0.2.0 (sources à l'étiquette de dub, -i)
/opt/ldc/bin/ldc2 -O3 -release $MODE -mcpu=native -J. -I/opt/open/d/soa-d/source -i -of=ms ms.d
