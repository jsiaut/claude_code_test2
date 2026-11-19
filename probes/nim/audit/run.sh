#!/bin/sh
# Audit de la grille, Nim 2.2.12 (C par clang 23, options du banc). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
N=/opt/nim/bin/nim
V=$($N --version | head -1 | awk '{print $4}')
F="-d:release --threads:on --mm:orc --hints:off --warnings:off --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 --passC:-march=native"
$N c $F -d:nimAllocStats --nimcache:bin/nc_audit -o:bin/audit audit.nim > /dev/null && bin/audit > bin/audit.out 2>&1
grep -v "^FACT;" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out | cut -d";" -f3-; }
$N c $F --nimcache:bin/nc_cg -o:bin/codegen codegen.nim > /dev/null && bin/codegen > /dev/null && objdump -d --no-show-raw-insn bin/codegen > bin/codegen.dis
fo() { awk -v f="<$1>:" '$0 ~ f {on=1; next} on && /^$/ {exit} on' bin/codegen.dis; }
lay() { fo $1 | grep -E '\s(j[a-z]+|call|ret)\b' | awk '{print $2}' | tr '\n' ' '; }
echo "CAP;B2;0.5;[exécutée] $(fact B2) ; aucune interface d'allocateur sous --mm:orc (NOTE B2 : régions sous --mm:regions seulement)"
$N c --mm:regions --hints:off --nimcache:bin/nc_reg -o:bin/regions regions.nim > /dev/null 2>&1 && r=$(bin/regions) || r=échec
$N c --mm:orc --hints:off --nimcache:bin/nc_reg2 -o:bin/x regions.nim > bin/reg_orc.log 2>&1
echo "NOTE;B2;[exécutée] withRegion(MemRegion) sous --mm:regions, mode mémoire global livré (advopt.txt) : seq allouée dans la région, s[0] = $r ; [échec] sous --mm:orc, celui du banc : $(grep -o "Error: undeclared identifier: 'MemRegion'" bin/reg_orc.log)"
echo "CAP;C2;1;[exécutée] importc de _mm512_ternarylogic_epi32 depuis immintrin.h, compilé par clang 23 : tern(1) = 12 ^ 10 ^ 1 = 7, $(fo tern | grep -c vpternlogd) vpternlogd ; ½ en v1"
echo "CAP;C4;0.5;[exécutée] {.localPassC: \"-ffast-math\".} sur le module fastsum : $(fo sum_fast | grep -E 'vaddps' | grep -cE '[yz]mm') vaddps ymm/zmm dans sum_fast contre $(fo sum_plain | grep -E 'vaddps' | grep -cE '[yz]mm') dans sum_plain du module principal ($(fo sum_plain | grep -c vaddss) vaddss) : par module ou globalement (--passC), pas par opération"
$N c $F --passC:-fopenmp --passL:-fopenmp --nimcache:bin/nc_c5 -o:bin/c5 c5.nim > /dev/null 2>&1 && c5=$(bin/c5 | cut -d';' -f3-)
cat > bin/c5_chk.nim <<'NIM'
var ids: array[64, int]
for i in `||`(0, 63):
  ids[i] = i
echo ids[63]
NIM
$N c $F --passC:-fopenmp --passL:-fopenmp --nimcache:bin/nc_c5c -o:bin/x bin/c5_chk.nim > bin/c5_chk.log 2>&1
$N c $F --passC:-fopenmp --passL:-fopenmp --nimcache:bin/nc_c5r -o:bin/x c5_red.nim > bin/c5_red.log 2>&1
$N c $F --passC:-fopenmp --passL:-fopenmp --nimcache:bin/nc_c5r2 -o:bin/c5r2 c5_red2.nim > /dev/null 2>&1 && red=$(bin/c5r2)
echo "CAP;C5;0.5;[exécutée] $c5 ; [échec] le même corps avec les vérifications de -d:release : $(grep -o "error: use of undeclared label '[A-Z0-9_]*'" bin/c5_chk.log | head -1) (le saut d'erreur sort du bloc OpenMP) ; réduction(+:s) sur une variable Nim : $(grep -o "error: use of undeclared identifier 's'" bin/c5_red.log | head -1) (nom C décoré), qui marche avec {.exportc: \"s\".} : $red ; sous-ensemble du langage"
echo "CAP;D2;1;[exécutée] std/atomics à MemoryOrder explicite, code produit : moRelease = $(fo st_release | grep -cE 'movq?[[:space:]]+.0x1,') mov et $(fo st_release | grep -cE 'xchg|mfence') xchg ; moSequentiallyConsistent = $(fo st_seqcst | grep -c xchg) xchg ; fetchAdd moRelaxed = $(fo add_relaxed | grep -c lock) instruction lock"
echo "CAP;D4;1;[exécutée] $(fact D4) (std/typedthreads)"
echo "CAP;D5;1;[exécutée] cpuRelax (std/sysatomics) et fence(moSequentiallyConsistent) : $(fo spin | grep -cw pause) pause et $(fo spin | grep -cE 'mfence|lock or') barrière dans spin"
echo "CAP;E1;1;[exécutée] binaire natif par le C : objdump donne $(wc -l < bin/codegen.dis) lignes, $(fo axpy | grep -cE 'vfmadd|vmulps|vaddps') instructions vectorielles flottantes dans axpy ; le C généré reste lisible (nimcache)"
$N c -d:release --hints:off --cc:gcc --gcc.exe:/opt/gcc-16/bin/gcc-16 --gcc.linkerexe:/opt/gcc-16/bin/gcc-16 --nimcache:bin/nc_lk_gcc -o:bin/lk_gcc hints.nim > /dev/null 2>&1
$N c -d:release --hints:off --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 --nimcache:bin/nc_lk_clang -o:bin/lk_clang hints.nim > /dev/null 2>&1
lk() { objdump -d --no-show-raw-insn bin/lk_$1 | awk -v f="<$2>:" '$0 ~ f {on=1; next} on && /^$/ {exit} on' | grep -E '\s(j[a-z]+|call|ret)\b' | awk '{print $2}' | tr '\n' ' '; }
echo "CAP;E3;1;[exécutée] likely/unlikely (module system, __builtin_expect dans le C généré) : avec gcc 16, compilateur C par défaut de Nim, likely [ $(lk gcc h_lik)] contre [ $(lk gcc h_non)] sans indication (appel ramené dans le chemin chaud) ; avec clang 23, celui du banc, likely [ $(lk clang h_lik)] = unlikely [ $(lk clang h_unl)] : sans effet (le résultat passe par une variable NIM_BOOL) ; section 3 de docs/GRID_AUDIT.md"
echo "CAP;E4;1;[exécutée] importc de __builtin_prefetch : $(fo pf | grep -c prefetcht0) prefetcht0 dans pf ; ½ en v1"
echo "CAP;E5;1;[exécutée] paramètres {.noalias.} : $(grep -E '^N_LIB_PRIVATE N_NOINLINE\(void, axpy\)' bin/nc_cg/@mcodegen.nim.c | head -1 | grep -o NIM_NOALIAS | wc -l) NIM_NOALIAS (restrict) dans le prototype C de axpy"
echo "CAP;E6;1;[exécutée] a[i] sur une seq : $(fo idx_checked | grep -c raiseIndexError) appel à raiseIndexError ; sous {.push boundChecks: off.} : $(fo idx_unchecked | grep -c raiseIndexError)"
echo "CAP;E7;1;[exécutée] $(fact E7) ; dans le binaire, fib60 = $(fo fib60 | grep -c 0x1686c8312d0) constante immédiate et $(fo fib60 | grep -c call) appel ; gsum instanciée en $(grep -cE '^[0-9a-f]+ <gsum__[A-Za-z0-9_]*>:' bin/codegen.dis) fonctions (float32 et float64)"
S=$(python3 ../../../tools/grid_audit/search.py nim A6 C1 D3 F1 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A6;0;[recherche] motif A6 dans lib de Nim $V : $(n A6 3) déclaration publique, $(n A6 4) mention ($(n A6 6))"
echo "CAP;C1;0;[recherche] motif C1 dans lib de Nim $V : $(n C1 3) déclaration publique, $(n C1 4) mentions ($(n C1 6)) : aucun type vectoriel"
echo "CAP;D3;0;[recherche] motif D3 dans lib de Nim $V : $(n D3 3) déclarations publiques ($(n D3 6)) : SSL_CTRL_SET_SESS_CACHE_SIZE et SSL_CTRL_GET_SESS_CACHE_SIZE (OpenSSL), faux positifs ; aucune constante ni type de bourrage"
echo "CAP;F1;0.5;[exécutée] $(fact F1) ; [échec] array[n, array[3, float32]] avec n connu à l'exécution : $($N c --hints:off -o:bin/x fail_md.nim 2>&1 | grep -o 'Error: .*' | head -1) ; [recherche] motif F1 : $(n F1 3) déclaration publique ($(n F1 6))"
echo "CAP;F2;0;[recherche] motif F2 dans lib de Nim $V : $(n F2 3) déclarations publiques ($(n F2 6)) : liaisons de locale.h (Lconv, LC_*), faux positifs ; aucune construction NUMA ni de distribution"
