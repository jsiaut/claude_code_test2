#!/bin/sh
# Annexe Valhalla : compile et exécute K1V avec le JDK EA (JEP 401)
cd "$(dirname "$0")" && unset JAVA_TOOL_OPTIONS && mkdir -p bin && /opt/jdk-valhalla/bin/javac --release 27 --enable-preview -d bin K1V.java 2>&1 | grep -v "preview\|Note:" ; /opt/jdk-valhalla/bin/java --enable-preview -Xmx8g -cp bin K1V "$@"
