#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/mojo-venv/bin/mojo build probe.mojo -o bin/probe && bin/probe && /opt/mojo-venv/bin/mojo build probe_errata.mojo -o bin/probe_errata && bin/probe_errata
