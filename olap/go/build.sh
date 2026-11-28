#!/bin/sh
# v7 : le banc OLAP en Go (go 1.27.3, GOAMD64=v4), niveau portable (olap_p) et niveau spécialisé (olap_s :
# simd/archsimd, paquet expérimental, GOEXPERIMENT=simd). unpack_gen.go est engendré par gen_unpack.go.
set -e
cd "$(dirname "$0")"
GO=/opt/go127/bin/go
GOAMD64=v4 $GO build -o olap_p .
if [ -f special.go ]; then GOAMD64=v4 GOEXPERIMENT=simd $GO build -o olap_s .; fi
