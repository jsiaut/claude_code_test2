#!/bin/sh
# Audit de la grille, Ada par GNAT 16.2 (compilateur du banc, -O3 -march=native). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
export PATH=/opt/gcc-16/bin:$PATH
V=$(gcc-16 --version | head -1 | awk '{print $NF}')
(cd bin && gnatmake-16 -q -O3 -gnat2022 -march=native ../audit.adb -o audit -largs -pthread > /dev/null 2>&1 && ./audit > audit.out 2>&1)
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
(cd bin && gcc-16 -S -O3 -gnat2022 -march=native -o cg.s ../cg.adb > /dev/null 2>&1 && gcc-16 -S -O3 -gnat2022 -march=native -ffast-math -o cg_fast.s ../cg.adb > /dev/null 2>&1)
fa() { awk -v f="^$1:" '$0 ~ f {on=1; next} on && /\.size/ {exit} on' bin/${2:-cg.s}; }
lay() { fa $1 | grep -E '^\s+(call|j[a-z]+|ret)' | awk '{print $1}' | tr '\n' ' '; }
echo "CAP;C2;1;[exécutée] __builtin_ia32_pternlogd512_mask importé (convention Intrinsic) sur un type vectoriel (Machine_Attribute vector_type) : $(fa tern | grep -c vpternlogd) vpternlogd dans tern ; ½ en v1"
echo "CAP;C4;0.5;[exécutée] option globale -ffast-math : $(fa sum_plain cg_fast.s | grep -E vaddps | grep -cE '[yz]mm') vaddps ymm/zmm (somme vectorisée) contre $(fa sum_plain | grep -c vaddss) vaddss sans l'option ; [recherche] contrôle local : NOTE C4"
echo "CAP;D2;1;[exécutée] builtins __atomic_* à ordre explicite importés (Intrinsic), code produit : Release = $(fa st_release | grep -cE '^\s+movq') mov et $(fa st_release | grep -cE 'xchg|mfence') xchg ; Seq_Cst = $(fa st_seqcst | grep -c xchg) xchg ; fetch_add Relaxed = $(fa add_relaxed | grep -c lock) instruction lock ; ½ en v1 (Ada standard : seq_cst seulement)"
echo "CAP;D5;1;[exécutée] __atomic_thread_fence et __builtin_ia32_pause importés : $(fa spin | grep -cE 'rep nop|pause') pause (rep nop) et $(fa spin | grep -cE 'mfence|lock orq') barrière dans spin ; ½ en v1"
echo "CAP;E1;1;[exécutée] gcc-16 -S : $(wc -l < bin/cg.s) lignes d'assembleur pour le paquetage Cg"
echo "CAP;E3;1;[exécutée] GNAT.Branch_Prediction.Likely (unité livrée, __builtin_likely) : disposition [ $(lay hinted)] contre [ $(lay unhinted)] sans indication (appel ramené dans le chemin chaud) ; ½ en v1"
echo "CAP;E4;1;[exécutée] __builtin_prefetch importé : $(fa pf | grep -c prefetcht0) prefetcht0 dans pf ; ½ en v1"
echo "CAP;E6;1;[exécutée] A (I) : $(fa idx_checked | grep -c call) appel au contrôle d'indice (__gnat_rcheck_CE_Index_Check) ; sous pragma Suppress (Index_Check) : $(fa idx_unchecked | grep -c call)"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans l'asm, sq_const = $(fa sq_const | grep -c 1522756) constante immédiate et $(fa sq_const | grep -c call) appel"
S=$(python3 ../../../tools/grid_audit/search.py ada A6 C4 D3 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "NOTE;C4;[recherche] motif C4 dans adainclude et le manuel de GNAT (gnat_rm.info) $V : $(n C4 3) entrées ($(n C4 6)) : GNAT.Generic_Fast_Math_Functions (fonctions élémentaires) et pragma Fast_Math, pragma de configuration qui ne touche que la multiplication complexe ; aucun contrôle local de la réassociation"
echo "CAP;A6;0;[recherche] motif A6 dans adainclude et gnat_rm.info $V : $(n A6 3) entrée, $(n A6 4) mention ($(n A6 6))"
echo "CAP;C5;0;[échec] boucle parallel for d'Ada 2022 : $(cd bin && gcc-16 -c -gnat2022 ../fail_par.adb 2>&1 | head -1 | cut -d: -f4- | sed 's/^ //') ; le manuel de GNAT note « Feature unimplemented » pour les morceaux des itérateurs et réductions parallèles"
echo "CAP;D3;0;[recherche] motif D3 dans adainclude et gnat_rm.info $V : $(n D3 3) entrée, $(n D3 4) mention ($(n D3 6))"
echo "CAP;F2;0;[recherche] motif F2 dans adainclude et gnat_rm.info $V : $(n F2 3) entrée, $(n F2 4) mentions ($(n F2 6)) ; annexe E : pragma Remote_Call_Interface accepté (fail_rci compile), mais « GNAT itself supports programs with only a single partition » (gnat_rm.info, 10.2(24)) : le PCS est dans PolyORB, produit séparé, et gnatdist est absent de la chaîne ($(ls /opt/gcc-16/bin | grep -ciE 'gnatdist|polyorb') binaire)"
