#!/bin/sh
# Remarque sur FreePascal (docs/FPC.md, 5) : FPC 3.2.2, options de bench/fpc, trois noyaux optimisés mieux écrits (symbole MIEUX : K4 par masque, K5 par pointeurs, K8 en arène itérative) et la variante k4 branchless_ptr
set -e
cd "$(dirname "$0")"
/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -dMIEUX -vew -B -FU. -FE. -oms ../fpc_rq/ms.pas
