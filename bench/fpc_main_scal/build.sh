#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5) : branche main (comme bench/fpc_main), K1 soa et K5 tuned en scalaire, sans -Sv (symbole SCALAR, comme bench/fpc_scal)
set -e
cd "$(dirname "$0")"
/opt/fpc-main/lib/fpc/3.3.1/ppcx64 -n @/opt/fpc-main/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -dSCALAR -vew -B -FU. -FE. -oms ../fpc_rq/ms.pas
