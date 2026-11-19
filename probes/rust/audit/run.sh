#!/bin/sh
# Audit de la grille, Rust (rustc stable du banc ; nightly pour la contre-épreuve). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
R="rustc --edition 2024 -O -C target-cpu=native"
V=$(rustc --version | cut -d' ' -f2)
$R -o bin/audit audit.rs && bin/audit > bin/audit.out
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$R --emit asm -o bin/codegen.s codegen.rs && $R --emit llvm-ir -o bin/codegen.ll codegen.rs
fn_asm() { awk -v f="$1" '$0 ~ "^"f":" {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/codegen.s; }
fn_ir() { awk -v f="@$1\\\\(" '$0 ~ "^define" && $0 ~ f {print; on=1; next} on && /^}/ {exit} on' bin/codegen.ll; }
rel=$(fn_asm st_release | grep -cE "^\s+mov"); relx=$(fn_asm st_release | grep -cE "xchg|mfence")
sc=$(fn_asm st_seqcst | grep -cE "xchg")
rx=$(fn_asm add_relaxed | grep -cE "lock")
echo "CAP;D2;1;[exécutée] Ordering explicite, code produit : store(Release) = $rel mov et $relx xchg/mfence ; store(SeqCst) = $sc xchg ; fetch_add(Relaxed) = $rx instruction lock"
echo "CAP;D5;1;[exécutée] std::hint::spin_loop et atomic::fence(SeqCst) : $(fn_asm spin | grep -cw pause) pause et $(fn_asm spin | grep -cE 'mfence|lock[[:space:]]+or') barrière (mfence ou lock or) dans spin()"
echo "CAP;C4;1;[exécutée] f32::algebraic_add (stable depuis 1.98), par opération : somme d'un &[f32] en $(fn_asm sum_alg | grep -E 'vaddps' | grep -cE '%[yz]mm') vaddps sur ymm/zmm (réassociée, vectorisée) contre $(fn_asm sum_plain | grep -E 'vaddps' | grep -cE '%[yz]mm') pour la somme ordinaire ($(fn_asm sum_plain | grep -c vaddss) vaddss en chaîne)"
echo "CAP;E1;1;[exécutée] rustc --emit asm : $(wc -l < bin/codegen.s) lignes d'assembleur lisibles, dont $(fn_asm axpy | grep -cE 'vfmadd|vmulps|vaddps') instructions vectorielles flottantes dans axpy"
echo "CAP;E3;1;[exécutée] std::hint::cold_path (stable depuis 1.95) : $(fn_ir hinted | grep -c 'branch_weights\|!prof') poids de branchement dans l'IR de hinted ; $(grep -c 'branch_weights' bin/codegen.ll) métadonnées branch_weights"
echo "CAP;E4;1;[exécutée] _mm_prefetch::<_MM_HINT_T0> (std::arch, stable) : $(fn_asm pf | grep -c prefetcht0) prefetcht0 dans pf"
echo "CAP;E5;1;[exécutée] &mut [f32] et &[f32] : $(fn_ir axpy | head -1 | grep -o noalias | wc -l) attributs noalias sur les paramètres de axpy dans l'IR"
echo "CAP;E6;1;[exécutée] a[i] : $(fn_asm idx_checked | grep -c panic_bounds_check) appel à panic_bounds_check ; get_unchecked : $(fn_asm idx_unchecked | grep -c panic_bounds_check)"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans l'asm, fib60 = $(fn_asm fib60 | grep -c 1548008755920) constante immédiate et $(fn_asm fib60 | grep -c call) appel ; gsum monomorphisée en $(grep -cE '^_R.*gsum.*:$' bin/codegen.s) fonctions (f32 et f64)"
# Échecs sur le canal stable (la note ½ ou 0 vient de là)
err() { $R -o bin/x "$1" 2>&1 | grep -oE "error\[E[0-9]+\][^\`]*\`?[^\`]*\`?" | head -1; }
echo "CAP;B2;0.5;[exécutée] #[global_allocator] stable (allocateur compteur de la sonde) ; [échec] Vec::new_in sur stable : $(err fail_newin.rs) ; allocator_api reste instable (nightly ci-dessous)"
echo "CAP;C1;0.5;[échec] std::simd sur stable : $(err fail_simd.rs) ; portable_simd reste instable (nightly ci-dessous)"
echo "CAP;F1;0.5;[exécutée] $(fact F1) ; [échec] tableau 2D de dimension connue à l'exécution : $(err fail_md.rs) ; aucun type multidimensionnel en std (pas de motif F1 public : NOTE F1)"
# Contre-épreuve nightly
rustc +nightly --edition 2024 -O -C target-cpu=native -o bin/nightly nightly.rs 2>/dev/null && bin/nightly | sed "s/^NIGHTLY;\([A-Z0-9]*\);/NOTE;\1;[exécutée, nightly $(rustc +nightly --version | cut -d' ' -f2)] /"
# Recherches d'absence dans std, core et alloc (sources de rust-src, même version que rustc)
S=$(python3 ../../../tools/grid_audit/search.py rust A3 A6 C5 D3 D4 F1 F2 F4)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A3;0.5;[exécutée] repr(packed) : size_of::<P>() = 5 (probe.rs) ; [recherche] motif A3 dans std/core/alloc $V : $(n A3 3) déclarations publiques ($(n A3 6)), Layout::repeat_packed et extend_packed (calcul de disposition sans bourrage), aucune de champs de bits"
echo "CAP;A6;0;[recherche] motif A6 dans std/core/alloc $V : $(n A6 3) déclaration publique, $(n A6 4) mention ($(n A6 6))"
echo "CAP;C5;0;[recherche] motif C5 dans std/core/alloc $V : $(n C5 3) déclarations publiques ($(n C5 6)) : available_parallelism et sa réexportation, qui comptent les cœurs ; aucune boucle ni réduction parallèle (std::thread::scope relève de D1)"
echo "CAP;D3;0;[recherche] motif D3 dans std/core/alloc $V : $(n D3 3) déclaration publique, $(n D3 4) mention en commentaire ($(n D3 6))"
echo "CAP;D4;0;[recherche] motif D4 dans std/core/alloc $V : $(n D4 3) déclaration publique ; $(n D4 4) mentions, toutes dans la documentation de available_parallelism ($(n D4 6)) ; le crate libc du sysroot n'est atteint que par #![feature(rustc_private)] sur nightly (NOTE D4)"
echo "NOTE;F1;[recherche] motif F1 dans std/core/alloc $V : $(n F1 3) déclaration publique ($(n F1 6))"
echo "CAP;F2;0;[recherche] motif F2 dans std/core/alloc $V : $(n F2 3) déclaration publique ; $(n F2 4) mentions (locale de texte, « interleave », « does not expose information on NUMA regions ») ($(n F2 6))"
echo "CAP;F4;0;[recherche] motif F4 dans std/core/alloc $V : $(n F4 3) déclaration publique ; $(n F4 4) mentions en commentaire (BorrowedFd et mmap, provenance des pointeurs) ($(n F4 6)) ; mmap seulement par le crate libc du sysroot sur nightly (NOTE F4) ou une FFI"
