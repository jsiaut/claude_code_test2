#!/bin/sh
# OpenJDK 27.0.1 (HotSpot C2, G1 par défaut) ; jdk.incubator.vector pour tuned
set -e
cd "$(dirname "$0")"
/opt/jdk27/bin/javac --release 27 --add-modules jdk.incubator.vector -d classes Ms.java 2>&1 | grep -v "incubat\|Picked up" || true
