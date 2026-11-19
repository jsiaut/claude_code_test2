#!/bin/sh
# Audit de la grille, FreePascal 3.2.2 (options du banc) : compléments exécutés, code produit et recherches dans
# l'interface des unités livrées (ppudump, tools/grid_audit/listings/fpc_symbols.py).
cd "$(dirname "$0")" && mkdir -p bin
FPC="/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2"
V=$(/opt/fpc/bin/fpc -iV)
$FPC -al -FUbin -FEbin -obin/audit audit.pas > /dev/null 2>&1 && bin/audit > bin/audit.out
grep "^CAP" bin/audit.out
S=$(cd ../../.. && python3 tools/grid_audit/search.py fpc A6 C5 D3 E3 E5 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "CAP;E1;1;[exécutée] fpc -al garde l'assembleur : $(wc -l < bin/audit.s) lignes pour audit.pas"
echo "CAP;A6;0;[recherche] motif A6 dans l'interface des unités livrées (RTL, rtl-*, fcl-* ; ppudump) de FPC $V : $(n A6 3) symbole"
echo "CAP;C5;0;[recherche] motif C5 dans l'interface des unités livrées de FPC $V : $(n C5 3) symboles ($(n C5 6)) : UnixCpMap (faux positif de « pmap ») ; aucune boucle parallèle ni réserve de tâches (mtprocs est un paquet de Lazarus)"
echo "CAP;D3;0;[recherche] motif D3 dans l'interface des unités livrées de FPC $V : $(n D3 3) symboles ($(n D3 6)) : sofSharedCache (SQLite) et FieldCacheControl (HTTP), faux positifs ; aucune constante ni type de bourrage"
echo "CAP;E3;0;[échec] Likely : Error: Identifier not found \"Likely\" (base.sh) ; [recherche] motif E3 dans l'interface des unités livrées : $(n E3 3) symboles ($(n E3 6)) : Expect des analyseurs SQL et JavaScript, faux positifs"
echo "CAP;E5;0;[échec] $(grep '^FACT;E5;' bin/audit.out | cut -d';' -f3-) ; [recherche] motif E5 : $(n E5 3) symboles ($(n E5 6)), faux positifs (restrictions XSD, bmUnrestricted) ; ni restrict ni règle de non-aliasing"
echo "CAP;F2;0;[recherche] motif F2 dans l'interface des unités livrées de FPC $V : $(n F2 3) symboles ($(n F2 6)) : be2of5interleaved (code-barre) et les numéros syscall_nr_mbind, syscall_nr_set_mempolicy, syscall_nr_get_mempolicy de l'unité Syscall, pour Do_SysCall (appel système brut : section 3 de docs/GRID_AUDIT.md)"
