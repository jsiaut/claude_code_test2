#!/bin/sh
# Copie de sensibilité (docs/FPC.md, plan) : le source de bench/fpc compilé dans le mode « release » du fpc.cfg livré
# (-dRELEASE : -O2 -Xs) au lieu de -O3 ; mêmes options de cible et -Sv
set -e
cd "$(dirname "$0")"
/opt/fpc/bin/fpc -n -dRELEASE @/opt/fpc/etc/fpc.cfg -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -vew -B -FU. -FE. -oms ../fpc/ms.pas
