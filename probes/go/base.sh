#!/bin/sh
# Première sonde de Go (quatre cas, reprise par audit/ : run.sh).
cd "$(dirname "$0")" && mkdir -p bin && /opt/go127/bin/go run probe.go
