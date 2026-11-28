#!/bin/sh
# v7 : le banc OLAP en Java (JDK 27), niveau portable (olap_p) et niveau spécialisé (olap_s : API vectorielle,
# module en incubation). olap_p et olap_s sont des lanceurs : la machine virtuelle, ses options, les classes.
# UnpackGen.java est engendré par GenUnpack.java (java GenUnpack.java).
set -e
cd "$(dirname "$0")"
unset JAVA_TOOL_OPTIONS
JDK=/opt/jdk27/bin
rm -rf classes_p classes_s
$JDK/javac --release 27 -Xlint:all,-restricted,-auxiliaryclass -d classes_p Olap.java Portable.java UnpackGen.java
$JDK/javac --release 27 -Xlint:all,-restricted,-auxiliaryclass,-incubating --add-modules jdk.incubator.vector -d classes_s Olap.java Special.java 2>&1 |
  grep -v 'incubat' || true
OPTS="-XX:+UseTransparentHugePages --enable-native-access=ALL-UNNAMED"
printf '#!/bin/sh\nunset JAVA_TOOL_OPTIONS\nexec %s/java %s -cp %s/classes_p Olap "$@"\n' "$JDK" "$OPTS" "$PWD" > olap_p
printf '#!/bin/sh\nunset JAVA_TOOL_OPTIONS\nexec %s/java %s --add-modules jdk.incubator.vector -cp %s/classes_s Olap "$@"\n' \
  "$JDK" "$OPTS" "$PWD" > olap_s
chmod +x olap_p olap_s
