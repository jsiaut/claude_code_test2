#!/bin/sh
# Copie de sensibilité (docs/FPC.md, plan) : le source de bench/fpc, mêmes options, avec -dEXP : variantes
# supplémentaires K7 natural_cls (valeurs de classe), K8 natural_cls (nœuds de classe), K9 natural_dyn (array of array)
set -e
cd "$(dirname "$0")"
/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -dEXP -vew -B -FU. -FE. -oms ../fpc/ms.pas
