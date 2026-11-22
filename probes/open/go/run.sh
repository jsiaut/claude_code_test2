#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Go (go 1.27.3, GOAMD64=v4 comme le banc) ; modules
# du cache /opt/open/go (go.mod et go.sum de ce dossier). Écrit results/open/probes/go.txt.
set -e
cd "$(dirname "$0")"
export GOPATH=/opt/open/go/gopath GOMODCACHE=/opt/open/go/gopath/pkg/mod GOCACHE=/opt/open/go/cache GOTOOLCHAIN=local
export GOFLAGS=-mod=mod GOAMD64=v4
/opt/go127/bin/go build -o /tmp/go_open_probe .
R=$(/tmp/go_open_probe)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/go.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Go : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/go127/bin/go version)"
echo "CAP;C5;0.5;github.com/samber/lo/parallel v1.53.0;[exécutée] $(r C5 lo/parallel)"
echo "NOTE;C5;note publiée 0 ; Map, ForEach, Times en parallèle, mais une goroutine par élément, sans découpage en tranches ni réduction : limitée, ½"
echo "CAP;D3;1;github.com/templexxx/cpu v0.1.1;[exécutée] $(r D3 templexxx/cpu)"
echo "NOTE;D3;note publiée 0 ; constante de ligne de cache par architecture, utilisable comme longueur de bourrage : 1, comme std.atomic.cache_line de Zig"
echo "CAP;F1;1;gonum.org/v1/gonum/mat v0.17.0;[exécutée] $(r F1 gonum/mat)"
echo "NOTE;F1;note publiée ½ ([M][N]T fixe) ; matrice dense contiguë de dimensions connues à l'exécution : 1"
echo "CAP;F2;1;github.com/benjojo/numa (révision 1058a77);[exécutée] $(r F2 benjojo/numa)"
echo "NOTE;F2;note publiée 0 ; placement des fils sur un nœud et politique mémoire posée et relue (set/get_mempolicy) : 1"
} > $OUT
cat $OUT
