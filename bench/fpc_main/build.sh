#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5) : branche main, instantané officiel 3.3.1-21612-gc58603b8dd du 2026/11/04 (/opt/fpc-main), options de bench/fpc ; même code, sauf le type __m128 dans msvec (symbole M128) : main refuse -Sv sur array[0..3] of Single
set -e
cd "$(dirname "$0")"
/opt/fpc-main/lib/fpc/3.3.1/ppcx64 -n @/opt/fpc-main/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -dM128 -vew -B -FU. -FE. -oms ../fpc_rq/ms.pas
