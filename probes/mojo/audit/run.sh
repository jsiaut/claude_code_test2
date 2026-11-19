#!/bin/sh
# Audit de la grille, Mojo 1.2 (mojo build, réglages par défaut comme au banc). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
M=/opt/mojo-venv/bin/mojo
V=$($M --version | awk '{print $2}')
$M build audit.mojo -o bin/audit > /dev/null 2>&1 && bin/audit > bin/audit.out 2>&1
grep "^CAP" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$M build codegen.mojo -o bin/codegen > /dev/null 2>&1 && bin/codegen > /dev/null && objdump -d --no-show-raw-insn bin/codegen > bin/codegen.dis
$M build checks.mojo -o bin/checks > /dev/null 2>&1 && objdump -d --no-show-raw-insn bin/checks > bin/checks.dis
fo() { awk -v f="<$1>:" '$0 ~ f {on=1; next} on && /^$/ {exit} on' bin/${2:-codegen.dis}; }
fm() { awk -v f="^[0-9a-f]+ <checks::$1\\\\[.*>:$" '$0 ~ f {on=1; next} on && /^$/ {exit} on' bin/checks.dis; }
lay() { fo $1 | grep -E '\s(j[a-z]+|call|ret)\b' | awk '{print $2}' | tr '\n' ' '; }
echo "CAP;B2;0.5;[exécutée] unsafe_alloc et free (std.memory.alloc) : allocation et libération à la main ; [recherche] interface d'allocateur : NOTE B2"
echo "CAP;B4;1;[exécutée] noalloc (structures, SIMD, fermeture capturante, boucle) : $(fo noalloc | grep -c call) appel dans le code produit, donc aucune allocation ; seules les tâches async allouent (remarque sur Mojo)"
echo "CAP;C2;1;[exécutée] $(fact C2), $(fo tern | grep -c vpternlogd) vpternlogd dans tern (llvm_intrinsic de std.sys) ; ½ en v1"
echo "CAP;D2;1;[exécutée] Atomic.store et fetch_add à Ordering explicite (std.atomic), code produit : RELEASE = $(fo st_release | grep -cE 'movq?\s+.0x1,') mov et $(fo st_release | grep -cE 'xchg|mfence') xchg ; SEQUENTIAL = $(fo st_seqcst | grep -c xchg) xchg ; fetch_add RELAXED = $(fo add_relaxed | grep -c lock) instruction lock"
echo "CAP;E1;1;[exécutée] binaire natif par LLVM : objdump donne $(wc -l < bin/codegen.dis) lignes"
echo "CAP;E3;1;[exécutée] unlikely (std.sys.intrinsics) : disposition [ $(lay hinted)] contre [ $(lay unhinted)] sans indication (appel sorti du chemin chaud)"
echo "CAP;E4;1;[exécutée] prefetch[PrefetchOptions().for_read().high_locality()] : $(fo pf | grep -c prefetcht0) prefetcht0 dans pf"
echo "CAP;E6;1;[exécutée] l[i] sur une List : $(fm idx_checked | grep -c _debug_assert_fail) appel à _debug_assert_fail (assertions actives par défaut) ; l.unsafe_get(i) : $(fm idx_unchecked | grep -c call) appel ; -D ASSERT=none en global"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans le binaire, fib60 = $(fo fib60 | grep -c 0x1686c8312d0) constante immédiate et $(fo fib60 | grep -c call) appel"
S=$(cd ../../.. && python3 tools/grid_audit/search.py mojo A3 A6 B2 C5 D3 D4 F1 F2 F4)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A3;0;[recherche] motif A3 dans std de Mojo $V : $(n A3 3) déclaration publique ; $(n A3 4) mentions (pack_bits, données « packed » non alignées, résultat « bitfield » d'une intrinsèque GPU) ; ni struct compactée ni champs de bits"
echo "CAP;A6;0;[recherche] motif A6 dans std de Mojo $V : $(n A6 3) déclaration publique, $(n A6 4) mention ($(n A6 6))"
echo "NOTE;B2;[recherche] motif B2 dans std de Mojo $V : $(n B2 3) déclaration publique ($(n B2 6)) : GBP_REGIONAL_INDICATOR, faux positif ; aucune interface d'allocateur ni arène"
echo "CAP;C5;0;[recherche] motif C5 dans std de Mojo $V : $(n C5 3) déclaration publique ($(n C5 6)) : parallelism_level (nombre de travailleurs) ; parallelize est dans max.algorithm (exemple de std/runtime/__init__.mojo), hors de std"
echo "CAP;D3;0;[recherche] motif D3 dans std de Mojo $V : $(n D3 3) déclaration publique ; $(n D3 4) mentions (étiquettes ReadDCache de prefetch)"
echo "CAP;D4;0;[recherche] motif D4 dans std de Mojo $V : $(n D4 3) déclaration publique ; $(n D4 4) mentions : _create_task(desired_worker_id), « intentionally not part of the public API », indication de travailleur et non de CPU"
echo "CAP;F1;0.5;[recherche] motif F1 dans std de Mojo $V : $(n F1 3) déclaration publique ($(n F1 6)) : aucun tableau multidimensionnel en std (LayoutTensor est dans MAX) ; Array[Array[T, N], M] fixe seulement"
echo "CAP;F2;0;[recherche] motif F2 dans std de Mojo $V : $(n F2 3) déclarations publiques ($(n F2 6)) : SIMD.interleave et deinterleave, faux positifs"
echo "CAP;F4;0;[recherche] motif F4 dans std de Mojo $V : $(n F4 3) déclaration publique, $(n F4 4) mention ($(n F4 6))"
