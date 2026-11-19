#!/bin/sh
# Audit de la grille, C++ (g++ 16.2, libstdc++, options du banc : -std=c++26 -O3 -march=native). Lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
G="/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native"
export LD_LIBRARY_PATH=/opt/gcc-16/lib64
V=$(/opt/gcc-16/bin/g++-16 --version | head -1 | awk '{print $NF}')
$G -pthread -fopenmp -Wno-interference-size -o bin/audit audit.cpp && bin/audit > bin/audit.out 2>&1
grep "^CAP" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$G -S -o bin/codegen.s codegen.cpp -fopt-info-vec-optimized 2> bin/codegen_vec.txt
$G -fopenmp-simd -S -o bin/codegen_simd.s codegen.cpp 2>/dev/null
fa() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /\.cfi_endproc/ {exit} on' bin/${2:-codegen.s}; }
lay() { fa $1 | grep -E '^[[:space:]]+(j[a-z]+|call|ret)' | awk '{print $1}' | tr '\n' ' '; }
echo "CAP;C1;1;[exécutée] vector_size(32) (extension documentée de g++) : $(fa vadd | grep -c vaddps) vaddps dans vadd ; std::simd de C++26 reste expérimental dans GCC 16 (bench K1, K5, K6) ; ½ en v1"
echo "CAP;C2;1;[exécutée] _mm512_ternarylogic_epi32 (<immintrin.h> livré avec g++) : $(fa tern | grep -c vpternlogd) vpternlogd dans tern ; ½ en v1"
echo "CAP;C4;1;[exécutée] #pragma omp simd reduction(+:s) (OpenMP SIMD, livré, -fopenmp-simd), par boucle : $(fa sum_omp codegen_simd.s | grep -E vaddps | grep -cE '%[yz]mm') vaddps ymm/zmm contre $(fa sum_plain | grep -c vaddss) vaddss pour la boucle ordinaire ; std::reduce(std::execution::unseq, …) autorise la réassociation, mais g++ 16 ne la vectorise pas ($(fa sum_reduce codegen_simd.s | grep -E vaddps | grep -cE '%[yz]mm') vaddps ymm/zmm) : texte de la matrice à préciser"
echo "CAP;D2;1;[exécutée] std::atomic à memory_order explicite, code produit : release = $(fa st_release | grep -cE '^[[:space:]]+movq') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; seq_cst = $(fa st_seqcst | grep -c xchg) xchg ; fetch_add relaxed = $(fa add_relaxed | grep -c lock) instruction lock"
echo "CAP;D5;1;[exécutée] std::atomic_thread_fence et _mm_pause : $(fa spin | grep -cE 'rep nop|pause') pause (rep nop) et $(fa spin | grep -cE 'mfence|lock or') barrière dans spin ; ½ en v1"
echo "CAP;E1;1;[exécutée] g++ -S : $(wc -l < bin/codegen.s) lignes d'assembleur"
echo "CAP;E3;1;[exécutée] [[likely]] (C++20) : disposition [ $(lay likelyh)] contre [ $(lay unhinted)] sans indication (appel ramené dans le chemin chaud ; g++ sort déjà l'appel du chemin chaud sans indication, [[unlikely]] donne [ $(lay hinted)])"
echo "CAP;E4;1;[exécutée] __builtin_prefetch : $(fa pf | grep -c prefetcht0) prefetcht0 dans pf ; ½ en v1"
echo "CAP;E5;1;[exécutée] __restrict__ (extension documentée de g++) : axpy_r « $(grep -c 'codegen.cpp:14.*optimized: loop vectorized' bin/codegen_vec.txt) boucle vectorisée », $(grep -c 'codegen.cpp:14.*versioned' bin/codegen_vec.txt) version pour alias ; sans : $(grep -c 'codegen.cpp:15.*versioned for vectorization because of possible aliasing' bin/codegen_vec.txt) version pour alias (-fopt-info-vec) ; ½ en v1"
echo "CAP;E6;1;[exécutée] v[i] : $(fa idx | grep -c call) appel ; v.at(i) : $(awk '/^idx_at:/,/\.size[[:space:]]+idx_at\.cold/' bin/codegen.s | grep -c __throw_out_of_range) appel à __throw_out_of_range_fmt (dans idx_at.cold) : contrôle par expression ; vérifications absentes par défaut"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans l'asm, fib60 = $(fa fib60 | grep -c 1548008755920) constante immédiate ; gsum instanciée en $(grep -cE '^_Z4gsumI[fd]E.*:$' bin/codegen.s) fonctions (float et double)"
S=$(cd ../../.. && python3 tools/grid_audit/search.py cpp A6 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A6;0;[échec] __attribute__((soa)) : $($G -Werror=attributes -c -o bin/x.o -x c++ fail_soa.cpp 2>&1 | grep -o 'error: .*' | head -1) ; [recherche] motif A6 dans les en-têtes de libstdc++ $V et de la glibc : $(n A6 3) déclaration, $(n A6 4) mention"
echo "CAP;F2;0;[recherche] motif F2 dans les en-têtes de libstdc++ $V et de la glibc : $(n F2 3) déclarations ($(n F2 6)) : std::locale, faux positifs ; aucune construction de localité ni de distribution (même constat que C, NOTE F2 de C pour le trait de partition d'OpenMP)"
