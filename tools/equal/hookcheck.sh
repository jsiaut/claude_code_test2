#!/bin/sh
# v4, point 3 (docs/V4_EQUAL.md, 4) : contrôle des modes ajoutés aux build.sh. Construit chaque langage avec le
# build.sh du commit OLD (55ae9e6, le dernier avant l'ajout des modes) puis avec celui de l'arbre de travail, dans le
# même répertoire et sans MS_MODE ; compare les commandes du compilateur (trace sh -x) et les empreintes des binaires.
# Usage : hookcheck.sh [langage...] ; sortie sur la sortie standard (results/equal/hookcheck.txt).
cd "$(dirname "$0")/../.."
OLD=${OLD:-55ae9e6}
OUT=/dev/shm/hookcheck; mkdir -p $OUT
LANGS=${*:-c cpp fortran zig c3 d chapel fpc swift ada nim odin mojo go ocaml}
for L in $LANGS; do
  d=$OUT/$L
  for v in old new; do
    rm -rf $d; mkdir -p $d
    git archive $OLD bench/$L | tar -x --strip-components=2 -C $d
    [ $v = new ] && cp bench/$L/build.sh $d/build.sh
    rm -f $d/ms $d/ms_nat $d/ms_tuned $d/ms_fm
    (env -u MS_MODE sh -x $d/build.sh > $OUT/$L.$v.out 2>&1) || echo "$L $v: échec" 
    grep -E '^\+ .*(clang|g\+\+|gfortran|zig build|c3c compile|ldc2|chpl|fpc|swiftc|gnatmake|nim c|odin build|mojo build|go build|ocamlopt -O3)' $OUT/$L.$v.out | grep -v -- ' -version' > $OUT/$L.$v.cmd
    (cd $d && sha256sum ms ms_nat ms_tuned ms_fm 2>/dev/null) > $OUT/$L.$v.sha
  done
  c=$(cmp -s $OUT/$L.old.cmd $OUT/$L.new.cmd && echo same || echo DIFF)
  s=$(cmp -s $OUT/$L.old.sha $OUT/$L.new.sha && echo same || echo DIFF)
  echo "$L commandes=$c binaires=$s ($(wc -l < $OUT/$L.new.cmd) commandes, $(wc -l < $OUT/$L.new.sha) binaires)"
done
echo FIN
