#!/bin/sh
# Copie de sensibilité (docs/FPC.md, plan) : le source de bench/fpc sans le traitement vectoriel -Sv (-dSCALAR) :
# K1 soa et K5 tuned en scalaire ; tout le reste est identique (vérifié : sans expression vectorielle, -Sv ne change
# pas un octet du binaire)
set -e
cd "$(dirname "$0")"
/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -dSCALAR -vew -B -FU. -FE. -oms ../fpc/ms.pas
