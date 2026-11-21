#!/bin/sh
# v4, point 3 : construit une copie ou un mode dans /dev/shm/msbuild/<langage>/<construction> et exécute des variantes
# (somme de contrôle comparée à celle de la taille publiée). Usage : try.sh <langage> <eq|chk|unc|eq_chk|eq_unc> noyau:variante[:param]...
set -e
cd "$(dirname "$0")/../.."
L=$1; B=$2; shift 2
python3 tools/equal/build.py "$L" "$B" > /dev/null
D=/dev/shm/msbuild/$L/$B
for kv in "$@"; do
  k=${kv%%:*}; rest=${kv#*:}; v=${rest%%:*}; p=""; [ "$rest" != "$v" ] && p=${rest#*:}
  out=$(cd $D && MS_DATA=/opt/msdata WARMUP=1 ./run $k $v 3 $p 2>&1 | grep "^RESULT" | sort -t';' -k6 -g | head -1)
  chk=$(echo "$out" | cut -d';' -f7); t=$(echo "$out" | cut -d';' -f6)
  ok=$(python3 -c "import sys; sys.path.insert(0,'tools'); import driver as D; print(D.check('$k', '$p', '$chk'))")
  echo "$L/$B $k $v $p : t=$t chk=$chk ok=$ok"
done
