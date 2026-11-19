#!/bin/sh
# Free Pascal 3.2.2 (fpc, générateur de code propre à FPC) — niveau -O3 (le plus haut sans « effets de bord
# inattendus » selon fpc -h : -O4 réordonne les champs des classes et contracte en FMA, results/fpc_check/facts.txt),
# jeu d'instructions, optimisation et FPU de la cible (COREAVX2 / AVX2 : FPC 3.2.2 ne connaît pas l'AVX-512),
# traitement vectoriel -Sv (seule l'unité msvec s'en sert)
set -e
cd "$(dirname "$0")"
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : macros de sizes.inc, valeurs des variables MS_* ou
# publiées par défaut
cat > sizes.inc <<EOF
{ Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
  publiées. }
{\$define MS_N1:=${MS_N1:-4194304}}{\$define MS_N4:=${MS_N4:-16777216}}{\$define MS_INNER5:=${MS_INNER5:-65536}}
{\$define MS_N6:=${MS_N6:-16777216}}{\$define MS_N7:=${MS_N7:-16777216}}{\$define MS_K7_LOG2:=${MS_K7_LOG2:-20}}
{\$define MS_K8_LONG:=${MS_K8_LONG:-20}}{\$define MS_K8_REQ:=${MS_K8_REQ:-10}}{\$define MS_M9:=${MS_M9:-2048}}
EOF
/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv -vew -B -FU. -FE. -oms ms.pas
