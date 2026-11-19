#!/bin/sh
# Audit de la grille, C (clang 23, glibc ; options du banc : -std=c23 -O3 -march=native). Lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
CC="clang-23 -std=c23 -O3 -march=native"
V="clang $(clang-23 --version | head -1 | grep -o '[0-9]*\.[0-9]*\.[0-9]*' | head -1), $(ldd --version | head -1 | awk '{print $NF}')"
$CC -pthread -fopenmp -o bin/audit audit.c && bin/audit > bin/audit.out 2>&1
grep "^CAP" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$CC -S -o bin/codegen.s codegen.c && $CC -S -emit-llvm -o bin/codegen.ll codegen.c
fa() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/codegen.s; }
lay() { fa $1 | grep -E '^\s+(j[a-z]+|call|ret)' | awk '{print $1}' | tr '\n' ' '; }
echo "CAP;B2;0.5;[exécutée] $(fact B2) ; aucune interface d'allocateur (malloc et free seulement, pas d'allocateur passé aux fonctions de la bibliothèque) ; texte de la matrice à préciser (« arènes à écrire soi-même » : obstack existe)"
echo "CAP;C2;1;[exécutée] _mm512_ternarylogic_epi32 (<immintrin.h> livré avec clang) : $(fa tern | grep -c vpternlogd) vpternlogd dans tern ; ½ en v1"
echo "CAP;C4;1;[exécutée] #pragma clang fp reassociate(on), par bloc : $(fa sum_reassoc | grep -E vaddps | grep -cE '%[yz]mm') vaddps ymm/zmm dans sum_reassoc contre $(fa sum_plain | grep -c vaddss) vaddss dans sum_plain ; ½ en v1"
echo "CAP;D2;1;[exécutée] <stdatomic.h> à memory_order explicite, code produit : release = $(fa st_release | grep -cE '^\s+movq') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; seq_cst = $(fa st_seqcst | grep -c xchg) xchg ; fetch_add relaxed = $(fa add_relaxed | grep -c lock) instruction lock"
echo "CAP;D5;1;[exécutée] atomic_thread_fence (C11) et _mm_pause : $(fa spin | grep -cw pause) pause et $(fa spin | grep -cE 'mfence|lock[[:space:]]+or') barrière dans spin ; ½ en v1"
echo "CAP;E1;1;[exécutée] clang -S : $(wc -l < bin/codegen.s) lignes d'assembleur, $(fa axpy | grep -cE 'vfmadd|vmulps|vaddps') instructions vectorielles flottantes dans axpy"
echo "CAP;E3;1;[exécutée] __builtin_expect(x == 7, 0) : disposition [ $(lay hinted)] contre [ $(lay unhinted)] sans indication ; ½ en v1"
echo "CAP;E4;1;[exécutée] __builtin_prefetch : $(fa pf | grep -c prefetcht0) prefetcht0 dans pf ; ½ en v1"
echo "CAP;E5;1;[exécutée] restrict (C99) : $(grep -E '^define.*@axpy\(' bin/codegen.ll | grep -o noalias | wc -l) attributs noalias dans l'IR de axpy"
echo "CAP;E6;1;[exécutée] a[i] : $(fa idx | grep -c call) appel de vérification (aucune vérification de bornes dans le langage)"
echo "CAP;E7;0.5;[exécutée] $(fact E7) ; [échec] constexpr initialisé par un appel de fonction : $($CC -c -o bin/x.o fail_constexpr.c 2>&1 | grep -o 'error: .*' | head -1) : ni calcul arbitraire à la compilation ni génériques instanciés"
S=$(cd ../../.. && python3 tools/grid_audit/search.py c A6 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A6;0;[échec] __attribute__((soa)) : $($CC -Werror=unknown-attributes -c -o bin/x.o fail_soa.c 2>&1 | grep -o 'error: .*' | head -1) ; [recherche] motif A6 dans les en-têtes de la glibc ($V) et de clang : $(n A6 3) déclaration, $(n A6 4) mention"
echo "CAP;F2;0;[recherche] motif F2 dans les en-têtes de la glibc et de clang ($V) : $(n F2 3) déclarations ($(n F2 6)) : crochets de traçage des appels système mbind et set_mempolicy du sanitiseur, intrinsèques Hexagon d'entrelacement ; pas de mbind dans la glibc (libnuma, tierce, n'a pas ses en-têtes ici) ; le trait OpenMP omp_atk_partition (interleaved) est accepté, sans politique visible sur cet hôte à un nœud (NOTE F2)"
clang-23 -O2 -fopenmp omp_partition.c -o bin/omp_partition 2>/dev/null && echo "NOTE;F2;[exécutée] omp_init_allocator(omp_default_mem_space, {omp_atk_partition, omp_atv_interleaved}) avec libomp de clang : $(bin/omp_partition | sed 's/allocator=[0-9]* ptr=0x[0-9a-f]* //')"
