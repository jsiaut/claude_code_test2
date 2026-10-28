#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/src/odin/odin build . -o:speed -out:bin/probe && bin/probe
