#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5) : FPC 3.2.2, options de bench/fpc, boucles naturelles bornées par Length(x) - 1 (symbole LEN de bench/fpc_rq/ms.pas)
set -e
cd "$(dirname "$0")"
/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -dLEN -vew -B -FU. -FE. -oms ../fpc_rq/ms.pas
