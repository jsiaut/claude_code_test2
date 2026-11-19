#!/bin/sh
# Audit de la grille, D par LDC 1.43 (compilateur du banc, -O3 -mcpu=native). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin/o3 bin/bc
L=/opt/ldc/bin/ldc2
V=$($L --version | head -1 | grep -o '([0-9.]*)' | tr -d '()')
$L -O3 -mcpu=native -of=bin/audit audit.d && bin/audit > bin/audit.out 2>&1
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$L -O3 -mcpu=native -c -output-s -output-ll -od=bin/o3 codegen.d
$L -O3 -mcpu=native -boundscheck=on -c -output-s -od=bin/bc codegen.d
fa() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/o3/codegen.s; }
fb() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/bc/codegen.s; }
ir() { awk -v f="@$1\\\\(" '$0 ~ "^define" && $0 ~ f {print; on=1; next} on && /^}/ {exit} on' bin/o3/codegen.ll; }
lay() { fa $1 | grep -E '^\s+(j[a-z]+|call|ret)' | awk '{print $1}' | tr '\n' ' '; }
err() { $L -c -of=bin/x.o "$1" 2>&1 | grep -o 'Error: .*' | head -1; }
echo "CAP;B1;0.5;[exécutée] $(fact B1) ; [échec] new dans une fonction @nogc : $(err fail_nogc.d) : le GC est le défaut, évitable par @nogc ou -betterC"
echo "NOTE;B4;[échec] les mêmes constructions dans une fonction @nogc sont refusées à la compilation (fail_nogc.d)"
echo "CAP;C2;1;[exécutée] $(fact C2) ; $(fa tern | grep -c vpternlogd) vpternlogd dans tern (module ldc.gccbuiltins_x86, livré avec LDC ; ½ en v1)"
echo "CAP;C4;1;[exécutée] @fastmath (ldc.attributes), par fonction : $(ir sum_fast | grep -c 'fadd fast') fadd fast (vectorisés) dans sum_fast contre $(ir sum_plain | grep -c 'fadd fast') dans sum_plain ($(ir sum_plain | grep -c 'fadd float') fadd stricts) ; ½ en v1"
echo "CAP;D2;1;[exécutée] core.atomic à MemoryOrder explicite, code produit : rel = $(fa st_release | grep -cE '^\s+movq') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; seq = $(fa st_seqcst | grep -c xchg) xchg ; atomicFetchAdd raw = $(fa add_relaxed | grep -c lock) instruction lock"
echo "CAP;D5;1;[exécutée] core.atomic.pause et atomicFence : $(fa spin | grep -cw pause) pause et $(fa spin | grep -cE 'mfence|lock[[:space:]]+or') barrière dans spin"
echo "CAP;E1;1;[exécutée] -output-s : $(wc -l < bin/o3/codegen.s) lignes d'assembleur, $(fa axpy | grep -cE 'vfmadd|vmulps|vaddps') instructions vectorielles flottantes dans axpy"
echo "CAP;E3;1;[exécutée] core.builtins.expect(x == 7, false) : disposition [ $(lay hinted)] contre [ $(lay unhinted)] sans indication, $(ir hinted | grep -c '!prof') poids dans l'IR ; NOTE E3"
echo "NOTE;E3;[exécutée] core.builtins.unlikely(x == 10), enveloppe inline de expect : $(ir hinted_unl | grep -c '!prof') poids, disposition [ $(lay hinted_unl)] comme sans indication (l'indication est perdue sous LDC -O3)"
echo "CAP;E4;1;[exécutée] core.simd.prefetch!(false, 3) : $(fa pf | grep -c prefetcht0) prefetcht0 dans pf"
echo "CAP;E5;1;[exécutée] @restrict (ldc.attributes) : $(ir axpy | head -1 | grep -o noalias | wc -l) attributs noalias dans l'IR de axpy ; ½ en v1"
echo "CAP;E6;1;[exécutée] avec -boundscheck=on, a[i] : $(fb idx_checked | grep -c _d_arraybounds) appel à _d_arraybounds_index ; a.ptr[i] : $(fb idx_unchecked | grep -c _d_arraybounds) (contrôle par expression ; -boundscheck=off|safeonly en global)"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans l'asm, fib60 = $(fa fib60 | grep -c 1548008755920) constante immédiate et $(fa fib60 | grep -c call) appel ; gsum instanciée en $(grep -cE '^_D7codegen__T4gsumT[a-z]Z.*:$' bin/o3/codegen.s) fonctions (float et double)"
S=$(python3 ../../../tools/grid_audit/search.py d A6 F1 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A6;0;[recherche] motif A6 dans druntime, Phobos et ldc de LDC $V : $(n A6 3) ligne de code, $(n A6 4) mention ($(n A6 6))"
echo "CAP;F1;0.5;[exécutée] $(fact F1) ; [échec] float[n][3] avec n connu à l'exécution : $(err fail_md.d) ; [recherche] motif F1 : $(n F1 3) lignes de code ($(n F1 6)) : tableaux de tableaux (double[][]) et makeMultidimensionalArray de std.experimental.allocator, qui alloue chaque ligne à part ; aucun tableau multidimensionnel contigu de taille dynamique"
echo "CAP;F2;0;[recherche] motif F2 dans druntime, Phobos et ldc de LDC $V : $(n F2 3) lignes de code ($(n F2 6)) : fonctions de locale du C, SCNuMAX, compteurs num*, la_symbind de l'éditeur de liens, constantes d'entrelacement de Windows ; aucune liaison mbind, set_mempolicy ou NUMA"
