#!/bin/sh
# Free Pascal 3.2.2 (fpc, générateur de code propre à FPC) — niveau -O3 (le plus haut sans « effets de bord
# inattendus » selon fpc -h : -O4 réordonne les champs des classes et contracte en FMA, results/fpc_check/facts.txt),
# jeu d'instructions, optimisation et FPU de la cible (COREAVX2 / AVX2 : FPC 3.2.2 ne connaît pas l'AVX-512),
# traitement vectoriel -Sv (seule l'unité msvec s'en sert)
set -e
cd "$(dirname "$0")"
/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -vew -B -FU. -FE. -oms ms.pas
