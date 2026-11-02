#!/bin/sh
# Copie standard de bench/go (docs/CONFRONTATION.md) : sans GOEXPERIMENT ; GOAMD64=v4 (choix de la cible) gardé.
set -e
cd "$(dirname "$0")"
[ -f go.mod ] || /opt/go127/bin/go mod init ms >/dev/null 2>&1
GOAMD64=v4 /opt/go127/bin/go build -o ms ms.go
