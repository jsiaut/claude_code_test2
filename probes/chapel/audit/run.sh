#!/bin/sh
# Audit de la grille, Chapel 2.10 (compilateur du banc, --fast, CHPL_COMM=none, qthreads). Lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
C=$CHPL_HOME/bin/linux64-x86_64/chpl
V=$($C --version | head -1 | awk '{print $3}')
$C --fast audit.chpl -o bin/audit > /dev/null 2>&1 && bin/audit --memTrack > bin/audit.out 2>&1
$C --fast --checks audit.chpl -o bin/audit_chk > /dev/null 2>&1
grep -v "^FACT;" bin/audit.out | grep "^CAP"
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
objdump -d --no-show-raw-insn bin/audit > bin/audit.dis; objdump -d --no-show-raw-insn bin/audit_chk > bin/audit_chk.dis
fo() { awk -v f="<$1>:" '$0 ~ f {on=1; next} on && /^$/ {exit} on' bin/${2:-audit.dis}; }
echo "CAP;D2;1;[exécutée] atomic avec memoryOrder explicite, code produit : release = $(fo st_release | grep -cE 'movq?\s+.0x1,') mov et $(fo st_release | grep -cE 'xchg|mfence') xchg ; seqCst = $(fo st_seqcst | grep -c xchg) xchg ; fetchAdd relaxed = $(fo add_relaxed | grep -c lock) instruction lock"
echo "CAP;D4;0.5;[exécutée] $(fact D4) ; variables de l'exécutif (QT_WORKER_UNIT, CHPL_RT_NUM_THREADS_PER_LOCALE, doc/rst/usingchapel/tasks.rst), pas d'API pour épingler une tâche"
echo "CAP;D5;0.5;[exécutée] atomicFence : $(fo fence_it | grep -cE 'mfence|lock or') barrière dans fence_it ; aucune indication pause (motif D5 : NOTE D5)"
echo "CAP;E1;1;[exécutée] binaire natif par LLVM : objdump donne $(wc -l < bin/audit.dis) lignes ; --llvm-print-ir pour l'IR"
echo "CAP;E4;0.5;[exécutée] prefetch du module package Prefetch : $(fo pf | grep -c prefetcht0) prefetcht0 dans pf (module « package », hors des modules standard)"
echo "CAP;E6;1;[exécutée] build --fast --checks : garr[i] = $(fo idx_arr audit_chk.dis | grep -c chpl_error) appels à chpl_error (bornes) ; p[i] sur un c_ptr : $(fo idx_ptr audit_chk.dis | grep -c call) appel (contrôle par expression) ; --no-checks en global"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans le binaire, f20 = $(fo f20 | grep -c '0x1a6d') constante immédiate et $(fo f20 | grep -c call) appel"
S=$(python3 ../../../tools/grid_audit/search.py chapel A3 A6 C1 D3 D5 E2 E3 F4)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A3;0;[recherche] motif A3 dans modules de Chapel $V : $(n A3 3) déclarations publiques ($(n A3 6)) : mises à jour « packed » de StencilDist, copies « Packed » de LinearAlgebraJama, constantes HDF5, MPI et NetCDF ; ni record compacté ni champs de bits"
echo "CAP;A6;0;[recherche] motif A6 dans modules de Chapel $V : $(n A6 3) déclaration publique, $(n A6 4) mention ($(n A6 6))"
echo "CAP;C1;0;[recherche] motif C1 dans modules de Chapel $V : $(n C1 3) déclaration publique, $(n C1 4) mention ($(n C1 6)) : aucun type vectoriel (les tuples ne sont vectorisés que par paires, bench)"
echo "CAP;D3;0;[recherche] motif D3 dans modules de Chapel $V : $(n D3 3) déclarations publiques ($(n D3 6)) : LocRADCache des distributions (faux positif de « dcache ») et cachePaddedLocales de CopyAggregation (arrondi du nombre de locales) ; aucune constante ni type de bourrage"
echo "NOTE;D5;[recherche] motif D5 dans modules de Chapel $V : $(n D5 3) déclarations publiques ($(n D5 6))"
echo "CAP;E2;0;[recherche] motif E2 dans modules de Chapel $V : $(n E2 3) déclaration publique, $(n E2 4) mention ($(n E2 6)) ; aucun assembleur en ligne"
echo "CAP;E3;0;[recherche] motif E3 dans modules de Chapel $V : $(n E3 3) déclaration publique ($(n E3 6)), un commentaire « likely unnecessary » ; aucune indication de branchement"
echo "CAP;F4;0;[recherche] motif F4 dans modules de Chapel $V : $(n F4 3) déclarations publiques ($(n F4 6)) : ioHintSet.mmap (indication de lecture de IO) et constantes QIO_METHOD_MMAP, NC_MMAP ; aucune projection rendue au programme"
