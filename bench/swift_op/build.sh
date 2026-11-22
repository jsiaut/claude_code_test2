#!/bin/sh
# Swift 6.4.2 (swift-6.4.2-RELEASE, LLVM de la chaîne) — mode release -O (vérifications de bornes et de débordement
# conservées), module entier, mode de langage Swift 6, cible native
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=unc : mode R1', sans vérifications (-Ounchecked) ; sans MS_MODE, la
# commande publiée.
case "${MS_MODE:-}" in
  "") OPT=-O ;;
  unc) OPT=-Ounchecked ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut
cat > sizes.swift <<EOF
// Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
// publiées.
let SIZE_N1 = ${MS_N1:-4194304}
let SIZE_INNER5 = ${MS_INNER5:-65536}
let SIZE_N6 = ${MS_N6:-16777216}
let SIZE_N7 = ${MS_N7:-16777216}
let SIZE_K7_LOG2 = ${MS_K7_LOG2:-20}
let SIZE_K8_LONG = ${MS_K8_LONG:-20}
let SIZE_K8_REQ = ${MS_K8_REQ:-10}
let SIZE_M9 = ${MS_M9:-2048}
EOF
# v4, point 6 (docs/V4_OPEN.md, 5.2) : l'arène (swift-memory-allocation, révision 8742a8c, trait MemoryAllocatorArena)
# et ses dépendances sont construites par SwiftPM hors du dépôt (deps/Package.swift ; release : -O et module entier ;
# -target-cpu native pour toutes les cibles), puis ms est compilé par la commande publiée, leurs modules (-I) et leurs
# objets en plus.
B=/opt/open/swift/build_op
PATH=/opt/swift/usr/bin:$PATH swift build -c release --package-path deps --scratch-path $B \
  -Xswiftc -target-cpu -Xswiftc native >/dev/null
R=$B/release
/opt/swift/usr/bin/swiftc -swift-version 6 $OPT -wmo -target-cpu native -parse-as-library -I $R -o ms ms.swift sizes.swift \
  "$R"/*.o
