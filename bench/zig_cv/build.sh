#!/bin/sh
# Zig 0.17.0 (LLVM 22.1.8) — -O fast (ex-ReleaseFast), -mcpu native
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=chk : mode R1, vérifications activées par l'option documentée (-O
# safe) ; sans MS_MODE, la commande publiée.
case "${MS_MODE:-}" in
  "") OPT=fast ;;
  chk) OPT=safe ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut
cat > sizes.zig <<EOF
// Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
// publiées.
pub const N1 = ${MS_N1:-4194304};
pub const INNER5 = ${MS_INNER5:-65536};
pub const N6 = ${MS_N6:-16777216};
pub const K7_LOG2 = ${MS_K7_LOG2:-20};
pub const K8_LONG = ${MS_K8_LONG:-20};
pub const K8_REQ = ${MS_K8_REQ:-10};
pub const M9 = ${MS_M9:-2048};
EOF
/opt/zig/zig build-exe ms.zig -O $OPT -mcpu native -femit-bin=ms 2>&1
