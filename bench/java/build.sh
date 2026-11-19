#!/bin/sh
# OpenJDK 27.0.1 (HotSpot C2, G1 par défaut) ; jdk.incubator.vector pour tuned
set -e
cd "$(dirname "$0")"
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut ;
# constantes de compilation, recopiées par javac dans Ms.class (Sizes.class n'est pas chargée à l'exécution)
cat > Sizes.java <<EOF
// Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
// publiées.
final class Sizes {
    static final int N1 = ${MS_N1:-4194304}, INNER5 = ${MS_INNER5:-65536}, N6 = ${MS_N6:-16777216};
    static final int K7_LOG2 = ${MS_K7_LOG2:-20}, K8_LONG = ${MS_K8_LONG:-20}, K8_REQ = ${MS_K8_REQ:-10}, M9 = ${MS_M9:-2048};
}
EOF
/opt/jdk27/bin/javac --release 27 --add-modules jdk.incubator.vector -d classes Ms.java Sizes.java 2>&1 | grep -v "incubat\|Picked up" || true
