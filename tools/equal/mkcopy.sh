#!/bin/sh
# v4, point 3 (docs/V4_EQUAL.md, 4) : copie bench/<langage>_eq des fichiers suivis de bench/<langage> (sources,
# build.sh, run), à laquelle s'ajoutent les variantes k4 tuned et k9 natural_flat (liste : eq_variants).
set -e
cd "$(dirname "$0")/../.."
L=$1
[ -d bench/${L}_eq ] && { echo "bench/${L}_eq existe déjà"; exit 1; }
git ls-files "bench/$L" | while read -r f; do
  rel=${f#bench/$L/}; mkdir -p "bench/${L}_eq/$(dirname "$rel")"; cp -p "$f" "bench/${L}_eq/$rel"; done
echo "bench/${L}_eq"
