#!/bin/sh
# Go 1.27.3 — GOAMD64=v4 (AVX-512 autorisé), GOEXPERIMENT=simd (simd/archsimd)
set -e
cd "$(dirname "$0")"
[ -f go.mod ] || /opt/go127/bin/go mod init ms >/dev/null 2>&1
GOAMD64=v4 GOEXPERIMENT=simd /opt/go127/bin/go build -o ms ms.go
