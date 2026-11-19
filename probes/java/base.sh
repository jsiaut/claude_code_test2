#!/bin/sh
# Première sonde de Java (cinq cas, reprise par audit/ : run.sh).
cd "$(dirname "$0")" && unset JAVA_TOOL_OPTIONS && mkdir -p bin && /opt/jdk27/bin/javac -d bin Probe.java && /opt/jdk27/bin/java -Dstdout.encoding=UTF-8 -cp bin Probe
