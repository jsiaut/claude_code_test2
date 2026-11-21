#!/bin/sh
# Go 1.27.3 — GOAMD64=v4 (AVX-512 autorisé), GOEXPERIMENT=simd (simd/archsimd)
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=unc : mode R1', sans vérifications (-gcflags=-B) ; sans MS_MODE, la
# commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  unc) MODE=-gcflags=-B ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
[ -f go.mod ] || /opt/go127/bin/go mod init ms >/dev/null 2>&1
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut
cat > sizes.go <<EOF
// Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
// publiées.

package main

const (
	sizeN1     = ${MS_N1:-4194304}
	sizeInner5 = ${MS_INNER5:-65536}
	sizeN6     = ${MS_N6:-16777216}
	sizeK7Log2 = ${MS_K7_LOG2:-20}
	sizeK8Long = ${MS_K8_LONG:-20}
	sizeK8Req  = ${MS_K8_REQ:-10}
	sizeM9     = ${MS_M9:-2048}
)
EOF
GOAMD64=v4 GOEXPERIMENT=simd /opt/go127/bin/go build $MODE -o ms ms.go sizes.go
