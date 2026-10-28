#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/ghc/bin/ghc -O2 -outputdir bin -o bin/probe Probe.hs >/dev/null && bin/probe
