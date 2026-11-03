#!/bin/sh
# Remarque sur Haskell (docs/HASKELL.md) : mode « release » annoncé par docs/NATURAL.md (ghc -O2 -fllvm ; LLVM 18,
# le générateur natif de 9.14.1 calcule faux les vecteurs 256/512 bits et refuse la FMA large), options de la cible et
# RTS multi-thread ; ni -fno-full-laziness (les NOINLINE et les IORef du harnais suffisent contre le partage entre
# répétitions) ni -fno-omit-yields (ajoutée sans justification ; aucune variante mesurée n'en a besoin).
set -e
cd "$(dirname "$0")"
/opt/ghc/bin/ghc -O2 -fllvm -mavx512f -mfma -mbmi2 -threaded -rtsopts -outputdir obj Ms.hs -o ms
