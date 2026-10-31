#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/ldc/bin/ldc2 -O3 -mcpu=native -of=bin/probe probe.d && bin/probe && /opt/ldc/bin/ldc2 -O3 -mcpu=native -of=bin/probe_errata probe_errata.d && bin/probe_errata
