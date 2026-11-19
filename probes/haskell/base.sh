#!/bin/sh
# Première sonde de Haskell (trois cas, reprise par audit/ : run.sh).
cd "$(dirname "$0")" && mkdir -p bin && /opt/ghc/bin/ghc -O2 -outputdir bin -o bin/probe Probe.hs >/dev/null && bin/probe
