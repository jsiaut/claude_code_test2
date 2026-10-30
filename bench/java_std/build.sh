#!/bin/sh
# Copie standard de bench/java (docs/CONFRONTATION.md) : sans jdk.incubator.vector
set -e
cd "$(dirname "$0")"
/opt/jdk27/bin/javac --release 27 -d classes Ms.java 2>&1 | grep -v "Picked up" || true
