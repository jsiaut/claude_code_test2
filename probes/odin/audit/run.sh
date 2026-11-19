#!/bin/sh
# Audit de la grille, Odin dev-2026-10 (compilateur du banc). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
O=/opt/src/odin/odin
V=$($O version | awk '{print $NF}')
$O build main -o:speed -microarch:native -out:bin/audit && bin/audit > bin/audit.out 2>&1
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$O build codegen -build-mode:asm -o:speed -microarch:native -out:bin/codegen.s
$O build codegen -build-mode:llvm-ir -o:speed -microarch:native -out:bin/ir
fa() { awk -v f="$1:" '$0 == f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/codegen.s; }
ir() { awk -v f="@$1\\\\(" '$0 ~ "^define" && $0 ~ f {print; on=1; next} on && /^}/ {exit} on' bin/codegen.ll; }
lay() { fa $1 | grep -E '^\s+(j[a-z]+|call|ret)' | awk '{print $1}' | tr '\n' ' '; }
echo "CAP;C2;1;[exécutée] intrinsèque de LLVM importée par foreign _ et @(link_name = \"llvm.x86.avx512.pternlog.d.512\"), #const pour l'immédiat (mécanisme de core:simd/x86, livré) : $(fa tern | grep -c vpternlogd) vpternlogd dans tern ; ½ en v1"
echo "CAP;C4;0;[échec] @(fast_math = {.Allow_Reassoc}) et le jeu complet de drapeaux sont acceptés, mais l'IR de sum_fast porte $(ir sum_fast | grep -cE 'fadd (reassoc|fast)') fadd réassociable et $(ir sum_fast | grep -c 'fadd float') fadd strict, comme sum_plain ; aucune option globale (odin build -help) : pas de contrôle de la réassociation dans $V"
echo "CAP;D2;1;[exécutée] intrinsics.atomic_*_explicit, code produit : .Release = $(fa st_release | grep -cE '^\s+movq') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; .Seq_Cst = $(fa st_seqcst | grep -c xchg) xchg ; atomic_add .Relaxed = $(fa add_relaxed | grep -c lock) instruction lock"
echo "CAP;D3;0.5;[exécutée] $(fact D3), constante publique de base:runtime, mais propre aux cellules des tables (Map_Cell #align(MAP_CACHE_LINE_SIZE)) ; aucun type de bourrage général (NOTE D3)"
echo "CAP;D5;1;[exécutée] intrinsics.cpu_relax et atomic_thread_fence(.Seq_Cst) : $(fa spin | grep -cw pause) pause et $(fa spin | grep -cE 'mfence|lock[[:space:]]+or') barrière dans spin"
echo "CAP;E1;1;[exécutée] -build-mode:asm : $(wc -l < bin/codegen.s) lignes d'assembleur, $(fa axpy | grep -cE 'vfmadd|vmulps|vaddps|vmulss|vaddss') instructions flottantes dans axpy"
echo "CAP;E3;1;[exécutée] intrinsics.expect(x == 7, false) : disposition [ $(lay hinted)] contre [ $(lay unhinted)] sans indication (appel sorti du chemin chaud)"
echo "CAP;E4;1;[exécutée] intrinsics.prefetch_read_data : $(fa pf | grep -c prefetcht0) prefetcht0 dans pf"
echo "CAP;E5;1;[exécutée] paramètres #no_alias : $(ir axpy | head -1 | grep -o noalias | wc -l) attributs noalias dans l'IR de axpy"
echo "CAP;E6;1;[exécutée] s[i] : $(fa idx_checked | grep -c bounds_check_error) appel à runtime.bounds_check_error ; #no_bounds_check : $(fa idx_unchecked | grep -c bounds_check_error)"
echo "CAP;E7;0.5;[exécutée] procédures polymorphes monomorphisées : $(fact E7), $(grep -cE '^"codegen::gsum:proc' bin/codegen.s) fonctions gsum distinctes (f32, f64) dans l'asm ; [échec] exécution à la compilation : $($O build fail_ctfe -out:bin/x 2>&1 | grep -o "Error: .*constant" | head -1)"
echo "CAP;F1;0.5;[exécutée] $(fact F1) ; [échec] [n][3]f32 avec n connu à l'exécution : $($O build fail_md -out:bin/x 2>&1 | grep -o 'Error: Array count must be a constant integer' | head -1) ; matrix[R, C] et les procédures de core:math/linalg sont de taille fixe"
S=$(python3 ../../../tools/grid_audit/search.py odin C4 C5 D3 F1 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "NOTE;C4;[recherche] motif C4 dans core et base $V : $(n C4 3) déclarations publiques ($(n C4 6)) : Fast_Math_Flag et Fast_Math_Flags de base:runtime (les drapeaux de l'attribut), FP_Fast_Math_Mode de l'IR SPIR-V de core:rexcode"
echo "CAP;C5;0;[recherche] motif C5 dans core et base $V : $(n C5 3) déclarations publiques ($(n C5 6)) : constantes d'argon2id et de Windows ; core:thread.Pool (thread_pool.odin) est une réserve de tâches, sans boucle ni réduction parallèle"
echo "NOTE;D3;[recherche] motif D3 dans core et base $V : $(n D3 3) déclarations publiques ($(n D3 6)) : MAP_CACHE_LINE_LOG2, MAP_CACHE_LINE_SIZE et Map_Cell de base:runtime, une constante de comctl32 ; aucun type de bourrage général"
echo "NOTE;F1;[recherche] motif F1 dans core et base $V : $(n F1 3) déclarations publiques ($(n F1 6)), presque toutes de core:math/linalg sur matrix[N, M] de taille fixe ; aucun tableau multidimensionnel de taille dynamique"
echo "CAP;F2;0;[recherche] motif F2 dans core et base $V : $(n F2 3) déclarations publiques ($(n F2 6)) : entrelacements de l'AES et de core:simd, une locale de Foundation, et les numéros d'appels système SYS_mbind, SYS_set_mempolicy, SYS_get_mempolicy de core:sys/linux, sans procédure dédiée ; la politique NUMA passe par linux.syscall (NOTE F2 : section 3 de docs/GRID_AUDIT.md)"
