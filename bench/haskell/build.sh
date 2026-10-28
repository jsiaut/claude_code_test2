#!/bin/sh
# GHC 9.14.1, backend LLVM (-fllvm, LLVM 18) -O2 : le générateur natif (NCG) de 9.14.1 calcule
# faux les vecteurs 256/512 bits (vérifié, voir docs/FINDINGS.md) ; -fno-full-laziness évite que
# les calculs purs soient partagés entre répétitions ; RTS multi-thread.
set -e
cd "$(dirname "$0")"
/opt/ghc/bin/ghc -O2 -fllvm -mavx512f -mfma -mbmi2 -fno-full-laziness -threaded -rtsopts -fno-omit-yields -outputdir obj Ms.hs -o ms
