#!/bin/sh
# Audit de la grille, Swift 6 (swiftc du banc, -O -target-cpu native) : compléments exécutés, code produit, échecs et
# recherches (interfaces .swiftinterface de la bibliothèque standard et symboles de Foundation et Dispatch).
cd "$(dirname "$0")" && mkdir -p bin
SC=/opt/swift/usr/bin/swiftc
V=$($SC --version 2>&1 | head -1 | grep -o 'version [0-9.]*' | head -1)
$SC -swift-version 6 -O -target-cpu native -parse-as-library -o bin/audit audit.swift > /dev/null 2>&1 && bin/audit
$SC -swift-version 6 -O -target-cpu native -parse-as-library -module-name cg -emit-assembly -o bin/codegen.s codegen.swift > /dev/null 2>&1
fs() { awk -v f="^\\\\\$s2cg$1:" '$0 ~ f {on=1; next} on && /^\.Lfunc_end/ {exit} on' bin/codegen.s; }
echo "CAP;E1;1;[exécutée] swiftc -emit-assembly : $(wc -l < bin/codegen.s) lignes pour le module cg (et -emit-ir pour l'IR, run.sh de base)"
echo "CAP;E6;1;[exécutée] a[i] sur un Array en -O : $(fs 3idxySfSaySfG_SitF | grep -c ud2) ud2 (piège de bornes) ; withUnsafeBufferPointer { \$0[i] } : $(fs 4idxuySfSaySfG_SitF | grep -c ud2) : contrôle local par expression ; -Ounchecked en global"
echo "CAP;E7;0.5;[exécutée] gsum<T: AdditiveArithmetic> : $(grep -cE '^\$s2cg4gsum[A-Za-z0-9_]*_Tg5:' bin/codegen.s) spécialisations (Float, Double) produites par l'optimiseur à côté de la version générique ($(grep -cE '^\$s2cg4gsumyxSayxGs18AdditiveArithmeticRzlF:' bin/codegen.s)), spécialisation non garantie ; [échec] évaluation à la compilation : @const let f20 = fib(20) -> $($SC -swift-version 6 -o bin/x fail_const.swift 2>&1 | grep -o 'error: .*' | head -1)"
S=$(cd ../../.. && python3 tools/grid_audit/search.py swift A3 A6 B2 C4 E2 F2)
n() { echo "$S" | grep "^SEARCH;$1;" | cut -d';' -f"$2"; }
echo "SED;A3;; [recherche] motif A3 dans les interfaces livrées ($V) et les symboles de Foundation et Dispatch : $(n A3 3) déclaration publique ($(n A3 4) mentions internes, bitOffset)"
echo "CAP;A6;0;[recherche] motif A6 dans les interfaces livrées ($V) et les symboles de Foundation et Dispatch : $(n A6 3) déclaration, $(n A6 4) mention"
echo "NOTE;B2;[recherche] motif B2 : $(n B2 3) déclarations publiques ($(n B2 6)) ; aucune interface d'allocateur ni arène"
echo "CAP;C4;0;[recherche] motif C4 dans les interfaces livrées ($V) et les symboles de Foundation et Dispatch : $(n C4 3) déclaration ($(n C4 6)) : URL.Template.Value.associativeList, faux positif ; aucun contrôle de la réassociation (Relaxed est dans swift-numerics, paquet tiers)"
echo "CAP;E2;0;[échec] asm(\"addq \$1, %0\") : $($SC -swift-version 6 -o bin/x fail_asm.swift 2>&1 | grep -o 'error: .*' | head -1) ; [recherche] motif E2 : $(n E2 3) déclaration, $(n E2 4) mention"
echo "CAP;F2;0;[recherche] motif F2 dans les interfaces livrées ($V) et les symboles de Foundation et Dispatch : $(n F2 3) déclarations ($(n F2 6)), toutes sur la locale de texte (Locale, DateFormatter.locale…) ; aucune construction NUMA ni de distribution"
