#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/go127/bin/go run probe.go
