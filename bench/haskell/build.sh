#!/bin/sh
# GHC 9.14.1, backend LLVM (-fllvm, LLVM 18) -O2 : le générateur natif (NCG) de 9.14.1 calcule
# faux les vecteurs 256/512 bits (vérifié, voir docs/FINDINGS.md) ; RTS multi-thread.
# Correction de la remarque sur Haskell (docs/HASKELL.md), reportée le 21 novembre (v4, point 4 :
# docs/V4_CONVERGE.md, 4.1) : mode « release » annoncé par docs/NATURAL.md, ni -fno-full-laziness (les NOINLINE et les
# IORef du harnais suffisent contre le partage entre répétitions) ni -fno-omit-yields (sans justification).
set -e
cd "$(dirname "$0")"
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : macros de sizes.h (préprocesseur C de GHC, qui garde
# les numéros de ligne), valeurs des variables MS_* ou publiées par défaut
cat > sizes.h <<EOF
/* Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
   publiées. */
#define MS_N1 ${MS_N1:-4194304}
#define MS_N5 ${MS_N5:-2048}
#define MS_INNER5 ${MS_INNER5:-65536}
#define MS_N6 ${MS_N6:-16777216}
#define MS_N7 ${MS_N7:-16777216}
#define MS_K7_LOG2 ${MS_K7_LOG2:-20}
#define MS_K8_LONG ${MS_K8_LONG:-20}
#define MS_K8_REQ ${MS_K8_REQ:-10}
#define MS_M9 ${MS_M9:-2048}
EOF
/opt/ghc/bin/ghc -O2 -fllvm -mavx512f -mfma -mbmi2 -threaded -rtsopts -outputdir obj Ms.hs -o ms
