#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5) : branche main (comme bench/fpc_main), boucles naturelles par Length et noyaux optimisés mieux écrits (symboles M128, LEN, MIEUX)
set -e
cd "$(dirname "$0")"
/opt/fpc-main/lib/fpc/3.3.1/ppcx64 -n @/opt/fpc-main/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -dM128 -dLEN -dMIEUX -vew -B -FU. -FE. -oms ../fpc_rq/ms.pas
