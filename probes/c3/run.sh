#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/src/c3c/build/c3c compile probe.c3 -O3 -o bin/probe && bin/probe
