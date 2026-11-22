#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Swift (Swift 6.4.2, -Ounchecked -target-cpu native
# par le manifeste) ; dépendances résolues par SwiftPM (Package.resolved), construction hors du dépôt.
# Écrit results/open/probes/swift.txt.
set -e
cd "$(dirname "$0")"
export PATH=/opt/swift/usr/bin:$PATH
swift build -c release --scratch-path /opt/open/swift/build 2>&1 | grep -E "error" || true
R=$(/opt/open/swift/build/release/probe)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/swift.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Swift : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(swift --version 2>&1 | head -1)"
echo "CAP;B2;0.5;swift-memory-allocation (révision 8742a8c);[exécutée] $(r B2 swift-memory-allocation)"
echo "NOTE;B2;note publiée ½ ; protocole d'allocateur (Memory.Allocator.Protocol) et arène remise à zéro d'un coup, mais d'octets bruts liés à la main (bindMemory) : ni objets Swift (classes), ni collections de la bibliothèque standard ; aucune version publiée (branche main) : limitée, ½, comme Foreign.Marshal.Pool de Haskell"
echo "CAP;F1;1;Matft 1.0.1;[exécutée] $(r F1 Matft)"
echo "NOTE;F1;note publiée ½ (InlineArray imbriqués de taille fixe) ; tableau multidimensionnel contigu de dimensions connues à l'exécution : 1"
} > $OUT
cat $OUT
