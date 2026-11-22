#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Haskell (GHC 9.14.1, options du banc :
# -O2 -fllvm -mavx512f -mfma -mbmi2 -threaded) ; paquets construits par cabal dans le store /opt/open/haskell/store,
# pris par sa base de paquets. Écrit results/open/probes/haskell.txt.
set -e
cd "$(dirname "$0")"
DB=/opt/open/haskell/store/ghc-9.14.1-c6c3/package.db
mkdir -p /tmp/hs_open
/opt/ghc/bin/ghc -O2 -fllvm -mavx512f -mfma -mbmi2 -threaded -rtsopts -package-db $DB -package parallel \
  -package atomic-primops -package mmap -package primitive -package bytestring -package directory -package filepath \
  -outputdir /tmp/hs_open Probe.hs -o /tmp/hs_open_probe >/dev/null
R=$(/tmp/hs_open_probe +RTS -N4 -s 2>&1)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
sp=$(echo "$R" | grep "SPARKS:" | sed 's/^ *//')
OUT=../../../results/open/probes/haskell.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Haskell : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/ghc/bin/ghc --version)"
echo "CAP;C5;1;parallel 3.3.0.0;[exécutée] $(r C5 parallel) ; RTS : $sp"
echo "NOTE;C5;note publiée ½ (par# de ghc-prim ; parallel non livré) ; stratégies d'évaluation parallèle (parMap, parListChunk), étincelles converties sur 4 capacités : 1"
echo "CAP;D2;0.5;atomic-primops 0.8.8;[exécutée] $(r D2 atomic-primops)"
echo "NOTE;D2;note publiée ½ ; opérations atomiques (CAS, ajout) séquentiellement cohérentes et barrières explicites, mais aucun ordre mémoire choisi par opération : ½, inchangée"
echo "CAP;F4;1;mmap 0.5.9;[exécutée] $(r F4 mmap)"
echo "NOTE;F4;note publiée 0 ; fichier projeté (mmapFileForeignPtr) et relu comme Word32 sans copie : 1"
} > $OUT
cat $OUT
