#!/bin/sh
# Audit de la grille, Julia 1.13 (julia du banc, -O3, 4 fils). Imprime des lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin
J="/opt/julia/bin/julia --startup-file=no"
V=$($J --version | awk '{print $3}')
$J -t 4 -O3 audit.jl > bin/audit.out 2>&1
grep "^CAP" bin/audit.out
fact() { grep "^FACT;$1;" bin/audit.out bin/d4.out 2>/dev/null | head -1 | cut -d";" -f3-; }
JULIA_EXCLUSIVE=1 $J -t 4 d4.jl > bin/d4.out 2>&1
S=$(cd ../../.. && python3 tools/grid_audit/search.py julia A3 A4 A6 D4)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;A3;0;[recherche] motif A3 dans les noms publics de Base, Core et des bibliothèques standard de Julia $V (introspection, tools/grid_audit/listings/julia_names.jl) : $(n A3 3) nom ; ni struct compactée ni champs de bits"
echo "CAP;A4;0.5;[exécutée] $(fact A4) ; [recherche] motif A4 dans les noms publics : $(n A4 3) nom ($(n A4 6)) : aucun attribut d'alignement de type"
echo "CAP;A6;0;[recherche] motif A6 dans les noms publics : $(n A6 3) nom ; StructArrays est un paquet tiers"
echo "CAP;D4;0.5;[exécutée] $(grep '^FACT;D4;' bin/d4.out | cut -d';' -f3-) ; [recherche] motif D4 dans les noms publics : $(n D4 3) nom (Base.setcpuaffinity, qui vise une commande lancée) : épinglage global par JULIA_EXCLUSIVE, pas par fil"
$J -O3 e3.jl > bin/e3.out 2>&1
echo "NOTE;E3;[échec] llvm.expect.i1 par llvmcall en forme module avec alwaysinline (e3.jl) : $(grep '^FACT;E3;h_unl' bin/e3.out | cut -d';' -f3-) ; témoin sans indication : $(grep '^FACT;E3;h_non' bin/e3.out | cut -d';' -f3-)"
