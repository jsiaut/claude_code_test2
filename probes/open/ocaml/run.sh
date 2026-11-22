#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte d'OCaml (OCaml 5.5.2 + flambda, ocamlopt -O3 comme le
# banc) ; bibliothèques construites par dune 3.25.0 dans l'espace /opt/open/ocaml/ws, talons C compilés pour le
# processeur hôte (c_flags -O2 -march=native, 5.2 du plan). Écrit results/open/probes/ocaml.txt.
set -e
cd "$(dirname "$0")"
W=/opt/open/ocaml/ws
export PATH=/opt/open/ocaml/bin:/opt/ocaml/bin:$PATH
mkdir -p $W/probe && cp probe.ml stubs.c dune $W/probe/
rm -f $W/dune
cat > $W/dune-workspace <<'EOD'
(lang dune 3.0)
(env (_ (c_flags (:standard -O2 -march=native)) (flags (:standard -w -a))))
EOD
(cd $W && dune build --profile release ./probe/probe.exe 2>/dev/null)
B=$W/_build/default/probe/probe.exe
R=$($B)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
fn() { objdump -d --no-show-raw-insn $B | awk -v f="$1" '$0 ~ "^[0-9a-f]+ <"f">:" {on=1; next} /^[0-9a-f]+ </ {on=0} on'; }
popc_stub=$(fn caml_int_popcnt_tagged_to_untagged | grep -cE "[[:space:]]popcnt" || true)
popc_soft=$(fn caml_int_popcnt_tagged_to_untagged | grep -c "__popcountdi2" || true)
csel=$(fn caml_csel_value | grep -cE "cmov" || true)
call=$(objdump -d --no-show-raw-insn $B | awk '/^[0-9a-f]+ <camlDune__exe__Probe[.]entry>:/ {on=1; next} /^[0-9a-f]+ </ {on=0} on' | grep -oE "call +[0-9a-f]+ <caml_int_popcnt[a-z_]*>" | head -1)
OUT=../../../results/open/probes/ocaml.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), OCaml : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, OCaml $(ocamlopt -version)"
echo "CAP;C2;0.5;ocaml_intrinsics_kernel v0.17.3;[exécutée] $(r C2 ocaml_intrinsics_kernel) ; code machine : popc appelle le talon C ($call) ; le talon compte $popc_stub popcnt et $popc_soft appel à __popcountdi2 ; caml_csel_value : $csel cmov"
echo "NOTE;C2;note publiée 0 ; instructions de la cible (popcnt, cmov, lzcnt, min/max…) atteintes par des externes [@@noalloc] : sur OCaml 5.5.2, chaque usage est un appel C non inliné (seul le compilateur de Jane Street, OxCaml, les remplace par l'instruction) ; ni SIMD ni intrinsèques vectorielles : limitée, ½ ; talons C compilés pour le processeur hôte (-march=native), sans quoi popcnt devient __popcountdi2, logiciel"
echo "CAP;C5;1;domainslib 0.5.2;[exécutée] $(r C5 domainslib)"
echo "NOTE;C5;note publiée 0 (Domainslib est tiers) ; boucles et réductions parallèles (parallel_for, parallel_for_reduce, parallel_scan) sur une réserve de domaines : 1"
echo "CAP;D4;1;processor 0.2;[exécutée] $(r D4 processor)"
echo "NOTE;D4;note publiée 0 ; affinité du fil courant posée et relue (Affinity.set_ids, get_ids), topologie (Query) : 1"
} > $OUT
cat $OUT
