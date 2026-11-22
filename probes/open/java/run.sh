#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Java (OpenJDK 27, comme le banc ; accès natif
# permis pour JNA et Unsafe) ; jars du dépôt Maven local /opt/open/java/m2. Écrit results/open/probes/java.txt.
set -e
cd "$(dirname "$0")"
unset JAVA_TOOL_OPTIONS
M=/opt/open/java/m2
CP=$M/net/openhft/affinity/2026.2/affinity-2026.2.jar:$M/net/java/dev/jna/jna/5.5.0/jna-5.5.0.jar
CP=$CP:$M/net/java/dev/jna/jna-platform/5.5.0/jna-platform-5.5.0.jar:$M/org/slf4j/slf4j-api/2.0.17/slf4j-api-2.0.17.jar
CP=$CP:$M/org/tensorflow/ndarray/1.0.0/ndarray-1.0.0.jar
CP=$CP:$M/org/apache/ignite/ignite-numa-allocator/2.18.0/ignite-numa-allocator-2.18.0.jar
CP=$CP:$M/org/apache/ignite/ignite-core/2.18.0/ignite-core-2.18.0.jar:$M/org/jetbrains/annotations/16.0.3/annotations-16.0.3.jar
mkdir -p /tmp/java_open
/opt/jdk27/bin/javac -nowarn -XDsuppressNotes -cp $CP -d /tmp/java_open Probe.java 2>/dev/null
R=$(/opt/jdk27/bin/java -Dstdout.encoding=UTF-8 --enable-native-access=ALL-UNNAMED --sun-misc-unsafe-memory-access=allow \
  -cp /tmp/java_open:$CP Probe 2>/dev/null)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/java.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Java : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/jdk27/bin/java -version 2>&1 | head -1)"
echo "CAP;D4;1;net.openhft:affinity 2026.2;[exécutée] $(r D4 affinity)"
echo "NOTE;D4;note publiée 0 ; affinité d'un fil posée et relue (Affinity, AffinityLock) : 1"
echo "CAP;F1;1;org.tensorflow:ndarray 1.0.0;[exécutée] $(r F1 ndarray)"
echo "NOTE;F1;note publiée ½ (tableaux de tableaux ; FFM) ; tableau à n dimensions de forme connue à l'exécution, sur un tampon contigu, vues par indice : 1"
echo "CAP;F2;0.5;org.apache.ignite:ignite-numa-allocator 2.18.0;[exécutée] $(r F2 ignite-numa-allocator)"
echo "NOTE;F2;note publiée 0 ; mémoire hors tas liée à un nœud (politique bind relue dans numa_maps), mais adresses brutes seulement : ni tableaux ni objets du tas, ni placement des fils : limitée, ½"
} > $OUT
cat $OUT
