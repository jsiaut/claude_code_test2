#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/ldc/bin/ldc2 -O3 -mcpu=native -of=bin/probe probe.d && bin/probe
