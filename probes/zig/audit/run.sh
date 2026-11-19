#!/bin/sh
# Audit de la grille, Zig 0.17 (compilateur du banc). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
Z=/opt/zig/zig
V=$($Z version)
$Z build-exe -O ReleaseFast -mcpu native -femit-bin=bin/audit audit.zig && bin/audit > bin/audit.out 2>&1
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$Z build-obj -O ReleaseFast -mcpu native -fno-emit-bin -femit-asm=bin/codegen.s -femit-llvm-ir=bin/codegen.ll codegen.zig
$Z build-obj -O ReleaseSafe -mcpu native -fno-emit-bin -femit-asm=bin/codegen_safe.s codegen.zig
fa() { awk -v f="codegen.$1:" '$0 == f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/codegen.s; }
fs() { awk -v f="codegen.$1:" '$0 == f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/codegen_safe.s; }
ir() { awk -v f="@codegen.$1\\\\(" '$0 ~ "^define" && $0 ~ f {print; on=1; next} on && /^}/ {exit} on' bin/codegen.ll; }
echo "CAP;D2;1;[exécutée] @atomicStore/@atomicRmw à ordre explicite, code produit : .release = $(fa st_release | grep -cE '^\s+mov') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; .seq_cst = $(fa st_seqcst | grep -c xchg) xchg ; .monotonic (fetch_add) = $(fa add_relaxed | grep -c lock) instruction lock"
echo "CAP;D5;0.5;[exécutée] std.atomic.spinLoopHint : $(fa spin | grep -cw pause) pause dans spin ; [échec] @fence : $($Z build-exe -femit-bin=bin/x fail_fence.zig 2>&1 | grep -o "error: [^']*'@fence'" | head -1) (retiré du langage ; barrière seulement par une opération atomique seq_cst ou par asm)"
echo "CAP;C4;1;[exécutée] @setFloatMode(.optimized) par portée : $(ir sum_opt | grep -c 'fadd fast') fadd fast dans l'IR de sum_opt contre $(ir sum_plain | grep -c 'fadd fast') dans sum_plain ($(ir sum_plain | grep -c 'fadd float') fadd stricts) ; pas de réduction vectorielle en 0.17 ($(fa sum_opt | grep -E vaddps | grep -cE '%[yz]mm|[yz]mm') vaddps ymm/zmm), le vectoriseur de boucles étant coupé"
echo "CAP;E1;1;[exécutée] -femit-asm : $(wc -l < bin/codegen.s) lignes d'assembleur, $(fa axpy | grep -cE 'vfmadd|vmulss|vaddss|vmulps|vaddps') instructions flottantes dans axpy"
lay() { fa $1 | grep -E '^\s+(j[a-z]+|call|ret)' | awk '{print $1}' | tr '\n' ' '; }
echo "CAP;E3;1;[exécutée] @branchHint(.unlikely) : poids $(ir hinted | grep -o '!prof ![0-9]*' | head -1 | cut -d'!' -f3 | xargs -I{} grep '^!{} = ' bin/codegen.ll | grep -o 'i32 [0-9]*, i32 [0-9]*') dans l'IR ; disposition [ $(lay hinted)] contre [ $(lay unhinted)] sans indication (appel sorti du chemin chaud)"
echo "NOTE;E3;[exécutée] @branchHint(.cold) sans effet visible en ReleaseFast -mcpu native : $(ir hinted_cold | grep -c '!prof') poids, disposition [ $(lay hinted_cold)] comme sans indication"
echo "CAP;E4;1;[exécutée] @prefetch : $(fa pf | grep -c prefetcht0) prefetcht0 dans pf"
echo "CAP;E5;1;[exécutée] paramètres noalias : $(ir axpy | head -1 | grep -o noalias | wc -l) attributs noalias dans l'IR de axpy"
echo "CAP;E6;1;[exécutée] en ReleaseSafe, s[i] : $(fs idx_checked | grep -c outOfBounds) appel à la panique outOfBounds ; sous @setRuntimeSafety(false) : $(fs idx_unchecked | grep -c outOfBounds) (contrôle par portée)"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans l'asm, fib60 = $(fa fib60 | grep -c 1548008755920) constante immédiate et $(fa fib60 | grep -c call) appel ; gsum instanciée en $(grep -cE '^codegen.gsum__[a-z_0-9]*:$' bin/codegen.s) fonctions (f32 et f64)"
echo "CAP;F1;0.5;[exécutée] $(fact F1) ; [échec] [n][3]f32 avec n connu à l'exécution : $($Z build-exe -femit-bin=bin/x fail_md.zig 2>&1 | grep -o 'error: [^,]*' | head -1)"
# Contre-épreuve C2 : nom d'intrinsèque LLVM en fonction externe
if $Z build-exe -O ReleaseFast -mcpu native -femit-bin=bin/llvm_intr -femit-asm=bin/llvm_intr.s llvm_intr.zig > bin/llvm_intr.log 2>&1; then r=$(bin/llvm_intr 2>&1); else r="refusé : $(grep -o 'error: .*' bin/llvm_intr.log | head -1)"; fi
echo "NOTE;C2;[exécutée] extern fn @\"llvm.x86.avx512.pternlog.d.512\" (nom d'intrinsèque LLVM déclaré comme fonction externe, mécanisme que Zig ne documente pas et que sa bibliothèque n'emploie pas) : 12 ^ 10 ^ 1 = $r ; $(grep -c vpternlogd bin/llvm_intr.s 2>/dev/null || echo ?) vpternlogd"
# Recherches d'absence dans lib/std de Zig $V
S=$(python3 ../../../tools/grid_audit/search.py zig C2 C5 F1 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "SEARCHES;$S" > bin/searches.txt
echo "CAP;C2;0.5;[recherche] motif C2 dans lib/std $V : $(n C2 3) déclarations publiques ($(n C2 6)) : bits de fonctionnalités CPUID (std/c.zig, std/Target/x86.zig), contextes de registres du débogueur, constantes ELF et Linux, constructeur d'IR LLVM du compilateur (std/zig/llvm), sélection d'un CRC ; aucune fonction intrinsèque ; [exécutée] asm volatile (E2) donne accès aux instructions de la cible (d'où ½) ; contre-épreuve : NOTE C2"
echo "CAP;C5;0;[recherche] motif C5 dans lib/std $V : $(n C5 3) déclarations publiques ($(n C5 6)) : hachages parallèles de std.crypto (blake3, kangarootwelve) et blocs AES entrelacés ; aucune boucle ni réduction parallèle ; std.Io.Group (async, concurrent) lance des tâches, du parallélisme de tâches comme std.Thread (D1)"
echo "NOTE;F1;[recherche] motif F1 dans lib/std $V : $(n F1 3) déclaration publique ($(n F1 6)) : Stringify.endArray, faux positif ; aucun type multidimensionnel"
echo "CAP;F2;0;[recherche] motif F2 dans lib/std $V : $(n F2 3) déclarations publiques ($(n F2 6)) : EnumArray (faux positif de « numa »), BPF_F_NUMA_NODE et l'assistant get_numa_node_id de eBPF (programmes BPF du noyau) ; aucune construction de localité ou de distribution pour la mémoire ou les fils du programme"
