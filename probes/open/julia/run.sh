#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Julia (julia 1.13.3 -O3 -t 4, comme le banc) ;
# paquets de l'environnement /opt/open/julia/env (Manifest.toml dans results/open/lock/julia). Écrit results/open/probes/julia.txt.
set -e
cd "$(dirname "$0")"
export JULIA_DEPOT_PATH=/opt/open/julia/depot
R=$(/opt/julia/bin/julia -O3 -t 4 --startup-file=no --project=/opt/open/julia/env probe.jl 2>&1)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
OUT=../../../results/open/probes/julia.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Julia : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(/opt/julia/bin/julia --version)"
echo "CAP;B2;0.5;Bumper 0.7.2;[exécutée] $(r B2 Bumper)"
echo "NOTE;B2;note publiée ½ ; arène à pointeur de tableaux de types isbits, libérée à la sortie du bloc ; ni objets du tas ni structures mutables : limitée, ½, comme Foreign.Marshal.Pool de Haskell"
echo "CAP;C1;0.5;VectorizationBase 0.21.74;[exécutée] $(r C1 VectorizationBase)"
echo "NOTE;C1;note publiée ½ ; types vectoriels Vec{W,T} portables (LLVM), mais l'API utilisateur n'est pas stable de son propre aveu et le paquet se dit déprécié à partir de Julia 1.11 (README : « Looking for new maintainers, otherwise deprecated in Julia 1.11 ») : ½"
echo "CAP;D4;1;ThreadPinningCore 0.4.5;[exécutée] $(r D4 ThreadPinningCore)"
echo "NOTE;D4;note publiée ½ (JULIA_EXCLUSIVE=1, épinglage global) ; fil par fil, posé et relu : 1"
echo "CAP;F2;1;NUMA 0.1.1;[exécutée] $(r F2 NUMA)"
echo "NOTE;F2;note publiée ½ (Distributed, SharedArrays : processus) ; API de libnuma (numa_set_membind…) et tableaux alloués sur un nœud choisi, nœud des pages relu : 1"
} > $OUT
cat $OUT
