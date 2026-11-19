#!/bin/sh
# Audit de la grille, Fortran par gfortran 16.2 (compilateur du banc, -O3 -march=native -fopenmp). Lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
G=/opt/gcc-16/bin/gfortran-16
V=$($G --version | head -1 | awk '{print $NF}')
$G -O3 -march=native -fopenmp audit.f90 -o bin/audit -J bin && OMP_PLACES='{1}' OMP_PROC_BIND=true bin/audit > bin/audit.out 2>&1
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
(cd bin && $G -S -O3 -march=native -fopenmp ../cg.f90 -o cg.s -fopt-info-vec-optimized 2> cg_vec.txt && $G -S -O3 -march=native -fopenmp -fcheck=bounds ../cg.f90 -o cg_bc.s 2>/dev/null && /opt/gcc-16/bin/gcc-16 -S -O3 -march=native ../cg_c.c -o cg_c.s -fopt-info-vec-optimized 2> cg_c_vec.txt)
fa() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /\.size/ {exit} on' bin/${2:-cg.s}; }
S=$(python3 ../../../tools/grid_audit/search.py fortran A2 A6 C1 C2 D3 D5 E2 E3 E4 F4)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A2;0.5;[exécutée] $(fact A2) ; [recherche] motif A2 dans gfortran.info et omp_lib.f90 $V : $(n A2 3) entrées ($(n A2 6)), toutes sur bind(c) ; aucune fonction offsetof : décalages par arithmétique sur c_loc seulement, ordre garanti par bind(c) ou sequence"
echo "CAP;A6;0;[recherche] motif A6 dans gfortran.info et omp_lib.f90 $V : $(n A6 3) entrée, $(n A6 4) mention ($(n A6 6))"
echo "CAP;B4;0.5;[exécutée] -fcheck=array-temps : $(printf 'program t\n  real :: a(100)\n  a = 1\n  call s(a(1:100:2))\ncontains\n  subroutine s(x)\n    real :: x(50)\n    x(1) = 2\n  end subroutine\nend program\n' > bin/tmp.f90; $G -O2 -fcheck=array-temps bin/tmp.f90 -o bin/tmp 2>/dev/null && bin/tmp 2>&1 | grep -o 'An array temporary was created.*' | head -1) (section non contiguë passée à un argument de forme explicite : copie implicite sur le tas ou la pile)"
echo "CAP;C1;0;[recherche] motif C1 dans gfortran.info et omp_lib.f90 $V : $(n C1 3) entrées ($(n C1 6)) : options -fopenmp-simd et OpenMP SIMD ; aucun type vectoriel"
echo "CAP;C2;0;[recherche] motif C2 propre à Fortran (« intrinsic » y désigne les procédures de la norme) dans gfortran.info et omp_lib.f90 $V : $(n C2 3) entrée, $(n C2 4) mention ; [échec] un builtin de GCC lié par bind(c) reste un symbole externe : $($G fail_builtin.f90 -o bin/x 2>&1 | grep -o "undefined reference to \`__builtin_ia32_pause'" | head -1)"
echo "CAP;C4;1;[exécutée] !\$omp simd reduction(+:s) (OpenMP livré), par boucle : $(fa sum_simd | grep -E vaddps | grep -cE '[yz]mm') vaddps ymm/zmm dans sum_simd contre $(fa sum_plain | grep -c vaddss) vaddss dans sum_plain ; ½ en v1"
echo "CAP;D2;1;[exécutée] !\$omp atomic à clause d'ordre, code produit : write release = $(fa st_release | grep -cE '^\s+movq') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; write seq_cst = $(fa st_seqcst | grep -c xchg) xchg ; capture relaxed = $(fa add_relaxed | grep -c lock) instruction lock ; ½ en v1"
echo "CAP;D3;0;[recherche] motif D3 dans gfortran.info et omp_lib.f90 $V : $(n D3 3) entrée ; $(n D3 4) mentions ($(n D3 6)) : indications omp_sync_hint_contended et omp_atv_contended (contention des verrous et des allocateurs), pas de bourrage"
echo "CAP;D4;1;[exécutée] $(fact D4) (variables OMP_PLACES et OMP_PROC_BIND d'OpenMP, livré) ; ½ en v1"
echo "CAP;D5;0.5;[exécutée] !\$omp flush : $(fa flushit | grep -cE 'mfence|lock or') barrière dans flushit ; [recherche] indication d'attente active : motif D5, $(n D5 3) entrée, $(n D5 4) mention (le sous-programme SLEEP) : pas de pause"
echo "CAP;E1;1;[exécutée] gfortran -S : $(wc -l < bin/cg.s) lignes d'assembleur pour le module cg"
echo "CAP;E2;0;[recherche] motif E2 dans gfortran.info $V : $(n E2 3) entrée ; $(n E2 4) mentions ($(n E2 6)) : l'assembleur du compilateur et un exemple en C ; aucun assembleur en ligne en Fortran"
echo "CAP;E3;0;[recherche] motif E3 dans gfortran.info $V : $(n E3 3) entrée ; $(n E3 4) mentions, toutes en prose (« likely », « expect ») ; aucune indication de branchement"
echo "CAP;E4;0;[recherche] motif E4 dans gfortran.info et omp_lib.f90 $V : $(n E4 3) entrée, $(n E4 4) mention ($(n E4 6)) ; aucun préchargement explicite"
echo "CAP;E5;1;[exécutée] règle des arguments muets (pas d'alias) : axpy en Fortran : $(grep -c 'cg.f90:3[0-9].*optimized: loop vectorized' bin/cg_vec.txt) boucle vectorisée, $(grep -c 'cg.f90.*versioned.*aliasing' bin/cg_vec.txt) version pour alias ; la même boucle en C sur deux pointeurs : $(grep -c 'versioned for vectorization because of possible aliasing' bin/cg_c_vec.txt) version pour alias (-fopt-info-vec)"
echo "CAP;E6;1;[exécutée] a(i) sans option : $(fa idx | grep -c call) appel de vérification ; avec -fcheck=bounds (globale) : $(fa idx cg_bc.s | grep -c call) appels au rapport d'erreur : vérifications absentes par défaut"
echo "CAP;E7;0.5;[exécutée] $(fact E7), constante immédiate dans f15c ($(fa f15c | grep -c 1307674368000)) ; [échec] gabarits génériques (template, prévus après Fortran 2023) : $($G -c fail_template.f90 -o bin/x.o 2>&1 | grep -m1 -o 'Error: .*') ; interfaces génériques seulement (une procédure par type, écrite à la main)"
echo "CAP;F3;0.5;[exécutée] type unsigned, extension de gfortran 15 sous -funsigned : $($G -funsigned -O2 f3_unsigned.f90 -o bin/f3 2>/dev/null && bin/f3) ; [échec] sans l'option : $($G -O2 f3_unsigned.f90 -o bin/x 2>&1 | grep -m1 -o 'Error: .*') ; entiers signés sans arithmétique modulaire (débordement interdit)"
echo "CAP;F4;0;[recherche] motif F4 dans gfortran.info et omp_lib.f90 $V : $(n F4 3) entrée, $(n F4 4) mention ($(n F4 6)) ; mmap seulement par bind(c) vers la libc (FFI)"
