#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/mojo-venv/bin/mojo build probe.mojo -o bin/probe && bin/probe
