#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5) : Free Pascal 3.2.4-rc2 (archive officielle de downloads.freepascal.org/fpc/beta, /opt/fpc-324rc2 ; le compilateur se nomme 3.2.4-rc1 [2026/08/16]), source et options de bench/fpc
set -e
cd "$(dirname "$0")"
/opt/fpc-324rc2/lib/fpc/3.2.4/ppcx64 -n @/opt/fpc-324rc2/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -vew -B -FU. -FE. -oms ../fpc/ms.pas
