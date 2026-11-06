#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5), information hors des règles du banc : branche main, K5 tuned en assembleur en ligne AVX-512 (symboles M128, ASM512)
set -e
cd "$(dirname "$0")"
/opt/fpc-main/lib/fpc/3.3.1/ppcx64 -n @/opt/fpc-main/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -dM128 -dASM512 -vew -B -FU. -FE. -oms ../fpc_rq/ms.pas
