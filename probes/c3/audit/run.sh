#!/bin/sh
# Audit de la grille, C3 0.8.5 (compilateur du banc, --x86cpu=native). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin/o3 bin/o1 bin/relaxed
C=/opt/src/c3c/build/c3c
N=--x86cpu=native
V=$($C --version | head -1 | awk '{print $NF}')
$C compile audit.c3 -O3 $N -o bin/audit > /dev/null && bin/audit > bin/audit.out 2>&1
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$C compile-only codegen.c3 -O3 $N --emit-asm --emit-llvm --no-obj --asm-out bin/o3 --llvm-out bin/o3 > /dev/null
$C compile-only codegen.c3 -O1 $N --emit-asm --no-obj --asm-out bin/o1 > /dev/null
$C compile-only codegen.c3 -O3 $N --fp-math=relaxed --emit-llvm --no-obj --llvm-out bin/relaxed > /dev/null
fa() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/o3/codegen.s; }
f1() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/o1/codegen.s; }
ir() { awk -v f="@$1\\\\(" '$0 ~ "^define" && $0 ~ f {print; on=1; next} on && /^}/ {exit} on' "$2"; }
lay() { fa $1 | grep -E '^\s+(j[a-z]+|call|ret)' | awk '{print $1}' | tr '\n' ' '; }
P=../../../tools/c3_check/probes
asmt() { if $C compile $P/$1.c3 -O3 $N -o bin/x > bin/x.log 2>&1; then echo "accepté"; else echo "refusé ($(grep -o 'error: [^.]*' bin/x.log | head -1))"; fi; }
echo "CAP;C2;0.5;[échec] intrinsèques de LLVM par extern @cname, mécanisme que la bibliothèque livrée n'emploie pas : llvm.x86.sse2.pause lié ($(fa relax | grep -cw pause) pause dans relax), llvm.x86.bmi.pext.32 non reconnu ($($C compile c2_scalar.c3 -O3 $N -o bin/x 2>&1 | grep -c 'undefined reference') références non résolues à l'édition de liens), llvm.x86.avx512.pternlog.d.512 ($($C compile c2_vec.c3 -O3 $N -o bin/x 2>&1 | grep -o 'Cannot select: intrinsic' | head -1) : les vecteurs passent par l'ABI C) ; les builtins \$\$ sont génériques"
echo "CAP;C4;0.5;[exécutée] option globale --fp-math=relaxed : $(ir sum_plain bin/relaxed/codegen.ll | grep -c 'fadd reassoc') fadd reassoc (vectorisés) dans sum_plain contre $(ir sum_plain bin/o3/codegen.ll | grep -c 'fadd reassoc') sans l'option ($(ir sum_plain bin/o3/codegen.ll | grep -c 'fadd float') fadd stricts) ; [recherche] contrôle local : NOTE C4"
echo "CAP;D2;1;[exécutée] Atomic{ulong} à AtomicOrdering explicite, code produit : RELEASE = $(fa st_release | grep -cE '^\s+movq') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; SEQ_CONSISTENT = $(fa st_seqcst | grep -c xchg) xchg ; add RELAXED = $(fa add_relaxed | grep -c lock) instruction lock"
echo "CAP;D5;0.5;[exécutée] thread::fence(SEQ_CONSISTENT) : $(fa spin | grep -cE 'mfence|lock[[:space:]]+or') barrière et $(fa spin | grep -cw pause) pause dans spin ; [recherche] indication d'attente active : NOTE D5 (pause seulement par extern @cname vers llvm.x86.sse2.pause, voir C2)"
echo "CAP;E1;1;[exécutée] --emit-asm : $(wc -l < bin/o3/codegen.s) lignes d'assembleur, $(fa axpy | grep -cE 'vfmadd|vmulps|vaddps|vmulss|vaddss') instructions flottantes dans axpy"
echo "CAP;E2;0.5;[exécutée] $(fact E2) ; bloc asm avec vaddps sur zmm : $(asmt asm_vaddps) ; [échec] vfmadd231ps : $(asmt asm_fma) ; pause : $(asmt asm_pause) ; mfence : $(asmt asm_mfence) ; vmovaps depuis la mémoire : $(asmt asm_vecload) ; asm(\"pause\") en chaîne : $(asmt asm_string), sans opérandes"
echo "CAP;E3;1;[exécutée] @unlikely(x == 7) : disposition [ $(lay hinted)] contre [ $(lay unhinted)] sans indication (appel sorti du chemin chaud)"
echo "CAP;E4;1;[exécutée] @prefetch(p, VERY_NEAR) : $(fa pf | grep -c prefetcht0) prefetcht0 dans pf"
echo "CAP;E5;0.5;[exécutée] @noalias : sur le 1er paramètre (axpy), noalias posé sur %0 ($(ir axpy bin/o3/codegen.ll | head -1 | grep -c 'ptr noalias nofree captures(none) %0')) ; [échec] sur le 2e paramètre (axpy2), noalias posé encore sur %0 ($(ir axpy2 bin/o3/codegen.ll | head -1 | grep -c 'ptr noalias nofree captures(none) %0')) et pas sur %1 ($(ir axpy2 bin/o3/codegen.ll | head -1 | grep -o 'noalias[^,]*%1' | wc -l)) : attribut expérimental, mal placé"
echo "CAP;E6;1;[exécutée] en -O1 (mode sûr), a[i] : $(f1 idx_checked | grep -cE 'cmpq[[:space:]]+%rsi, %rdx') comparaison à la longueur et $(f1 idx_checked | grep -c panicf) appels à la panique (bornes, alignement) ; a.ptr[i] : $(f1 idx_unchecked | grep -cE 'cmpq[[:space:]]+%rsi, %rdx') comparaison à la longueur, seul le contrôle d'alignement reste ($(f1 idx_unchecked | grep -c panicf) appel) : contrôle des bornes par expression ; -O3 retire toutes les vérifications"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans l'asm, fib60 = $(fa fib60 | grep -c 1548008755920) constante immédiate et $(fa fib60 | grep -c call) appel ; gsum instanciée en $(grep -cE '^codegen\.gsum\$[a-z]+\$:' bin/o3/codegen.s) fonctions (float et double)"
S=$(python3 ../../../tools/grid_audit/search.py c3 A6 C4 C5 D3 D5 F1 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A6;0;[recherche] motif A6 dans lib/std $V : $(n A6 3) déclaration publique, $(n A6 4) mention ($(n A6 6))"
echo "NOTE;C4;[recherche] motif C4 dans lib/std $V : $(n C4 3) déclaration publique, $(n C4 4) mention ($(n C4 6)) : ni attribut ni macro de réassociation locale"
echo "CAP;C5;0;[recherche] motif C5 dans lib/std $V : $(n C5 3) déclarations publiques ($(n C5 6)) : ParallelHash de std::crypto::keccak (hachage à plusieurs fils) et FixedThreadPool (déprécié), une réserve de tâches ; aucune boucle ni réduction parallèle"
echo "CAP;D3;0;[recherche] motif D3 dans lib/std $V : $(n D3 3) déclarations publiques ($(n D3 6)) : clés sysctl HW_CACHELINE et HW_L*CACHESIZE de macOS (std::os::darwin, std::threads::os) ; rien sous Linux, plate-forme de l'étude, ni type de bourrage"
echo "NOTE;D5;[recherche] motif D5 dans lib/std $V : $(n D5 3) déclaration publique ($(n D5 6)) : thread::fence ; aucune indication pause"
echo "CAP;F1;0.5;[exécutée] $(fact F1) ; Slice2d de std::core::array, vue 2D sur un tableau fixe ; [échec] float[n][3] avec n connu à l'exécution : $(printf 'module md;\nimport std::io;\nfn void main(String[] a) { int n = (int)a.len + 3; float[n][3] m; io::printn(m[0][0]); }\n' > bin/md.c3; $C compile bin/md.c3 -O3 -o bin/x 2>&1 | grep -o 'error: [^.]*' | head -1) ; [recherche] motif F1 : $(n F1 3) déclaration publique (CFMutableArray.appendArray, faux positif)"
echo "CAP;F2;0;[recherche] motif F2 dans lib/std $V : $(n F2 3) déclaration publique ($(n F2 6)) : xkb_compose_table_new_from_locale (Wayland), faux positif"
