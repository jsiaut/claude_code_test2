#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5), information hors des règles du banc : FPC 3.2.2, K5 tuned en assembleur en ligne AVX2 + FMA (symbole ASM)
set -e
cd "$(dirname "$0")"
/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -dASM -vew -B -FU. -FE. -oms ../fpc_rq/ms.pas
