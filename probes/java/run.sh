#!/bin/sh
cd "$(dirname "$0")" && unset JAVA_TOOL_OPTIONS && mkdir -p bin && /opt/jdk27/bin/javac -d bin Probe.java && /opt/jdk27/bin/java -cp bin Probe
