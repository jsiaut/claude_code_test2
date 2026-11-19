#!/bin/sh
# API publique des bibliothèques livrées avec GHC 9.14.1 (paquets de démarrage du dépôt global, sans le compilateur
# ni ses outils : ghc, ghci, ghc-boot*, haddock*, Cabal*, ghc-toolchain…) : « :browse » de GHCi sur chaque module
# exposé, une ligne par ligne de déclaration, préfixée du nom du module. Sert à tools/grid_audit/search.py.
G=/opt/ghc/bin
PKGS="base ghc-prim ghc-internal ghc-experimental ghc-bignum ghc-heap ghc-compact array containers bytestring text stm
deepseq unix process directory filepath file-io os-string time template-haskell template-haskell-lift
template-haskell-quasiquoter mtl transformers parsec binary exceptions pretty semaphore-compat integer-gmp"
T=$(mktemp -d)
FL=""
for p in $PKGS; do
  FL="$FL -package $p"
  $G/ghc-pkg field $p exposed-modules --simple-output 2>/dev/null
done | tr ' ,' '\n\n' | grep -E '^[A-Z]' | sort -u > $T/mods
while read m; do printf 'putStrLn "### %s"\n:browse %s\n' "$m" "$m"; done < $T/mods > $T/script
$G/ghci -v0 -ignore-dot-ghci $FL < $T/script 2>/dev/null | awk '/^### /{m=$2; next} {print m ": " $0}'
rm -rf $T
