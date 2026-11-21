#!/bin/sh
# Sondes de mode (v4, point 3 : docs/V4_EQUAL.md, 4). Chaque sonde (probe.*) lit un élément hors des bornes, dans un
# tableau alloué (« 1d ») et dans un tableau 2D de la forme du K9 naturel du langage (« 2d »). Elle est construite avec
# les options publiées du langage (bench/<langage>/build.sh) et, pour chaque mode, l'option que build.sh choisit pour
# MS_MODE (chk : R1 ; unc : R1'), lue dans son bloc « case » pour que sonde et banc ne divergent pas. Attendu : le
# mode R1 s'arrête, le mode R1' et le mode publié sans vérification ne s'arrêtent pas. Sortie : probes.txt.
cd "$(dirname "$0")"
S=$(pwd); R=$(cd ../../.. && pwd); W=/dev/shm/probes
rm -rf $W; mkdir -p $W
export PATH=/opt/gcc-16/bin:$PATH
modeopt() { # langage mode -> définit MODE et OPT comme build.sh
  MODE=""; OPT=""; MS_MODE=$2
  eval "$(sed -n '/^case "\${MS_MODE:-}" in/,/^esac/p' $R/bench/$1/build.sh)"
}
build() { # langage mode répertoire
  L=$1; M=$2; D=$3
  if [ $L = julia ]; then return 0; fi
  [ $M = pub ] && mm="" || mm=$M
  modeopt $L "$mm"
  (cd $D && case $L in
    c) clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread $MODE -o p probe.c ;;
    cpp) g++-16 -std=c++26 -O3 -march=native -pthread $MODE -o p probe.cpp ;;
    fortran) gfortran-16 -O3 -march=native -fopenmp $MODE -o p probe.f90 ;;
    zig) /opt/zig/zig build-exe probe.zig -O $OPT -mcpu native -femit-bin=p ;;
    c3) /opt/src/c3c/build/c3c compile probe.c3 -O3 $MODE --x86cpu=native -o p ;;
    d) /opt/ldc/bin/ldc2 -O3 -release $MODE -mcpu=native -of=p probe.d ;;
    chapel) (export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 \
               CHPL_TARGET_CPU=native CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
             $CHPL_HOME/bin/linux64-x86_64/chpl --fast $MODE probe.chpl -o p) ;;
    fpc) /opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv $MODE -vew -B -FU. -FE. -op probe.pas ;;
    swift) /opt/swift/usr/bin/swiftc -swift-version 6 $OPT -wmo -target-cpu native -o p probe.swift ;;
    ada) gnatmake-16 -q -O3 -gnat2022 -gnatwa -gnatwI $MODE probe.adb -o p -cargs -march=native ;;
    nim) /opt/nim/bin/nim c $OPT --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 --passC:"-march=native" \
           --threads:on --mm:orc --hints:off --warnings:off --nimcache:./nimcache -o:p probe.nim ;;
    odin) /opt/src/odin/odin build probe.odin -file -o:speed -microarch:native $MODE -out:p ;;
    mojo) /opt/mojo-venv/bin/mojo build $MODE probe.mojo -o p ;;
    go) GOAMD64=v4 GOEXPERIMENT=simd /opt/go127/bin/go build $MODE -o p probe.go ;;
    ocaml) /opt/ocaml/bin/ocamlopt -O3 $MODE probe.ml -o p ;;
  esac > build.log 2>&1)
  [ -x $D/p ]
}
run() { # langage mode répertoire cas -> « arrêt (code) : message » ou « passe : valeur »
  L=$1; M=$2; D=$3; C=$4
  [ $C = 1d ] && n=1000 || n=64
  case $L in
    chapel) set -- ./p --which=$C --n=$n ;;
    julia) [ $M = unc ] && cb="--check-bounds=no" || cb=""; set -- /opt/julia/bin/julia -O3 $cb --startup-file=no probe.jl $C $n ;;
    *) set -- ./p $C $n ;;
  esac
  out=$( { cd $D && timeout 60 "$@"; } 2>&1 ); rc=$?
  first=$(echo "$out" | grep -v '^\s*$' | head -1 | cut -c1-90)
  if [ $rc -eq 0 ]; then echo "passe : $first"; else echo "arrêt (code $rc) : $first"; fi
}
expect() { # langage mode cas -> arrêt | passe
  case "$1:$2:$3" in
    c:chk:1d) echo passe ;;  # accès par pointeur : -fsanitize=array-bounds ne connaît que les tableaux de taille connue
    *:chk:*) echo arrêt ;;
    *:unc:*) echo passe ;;
    c:pub:*|cpp:pub:*|fortran:pub:*|zig:pub:*|c3:pub:*|d:pub:*|chapel:pub:*|fpc:pub:*) echo passe ;;
    *) echo arrêt ;;
  esac
}
{
  echo "# Sondes de mode (results/equal/probes/run.sh), $(date -u +%Y-%m-%dT%H:%MZ), $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^ //')"
  echo "# langage mode cas : résultat [attendu] verdict"
  for spec in c:pub,chk cpp:pub,chk fortran:pub,chk zig:pub,chk c3:pub,chk d:pub,chk,unc chapel:pub,chk fpc:pub,chk \
              swift:pub,unc ada:pub,unc nim:pub,unc odin:pub,unc julia:pub,unc mojo:pub,unc go:pub,unc ocaml:pub,unc; do
    L=${spec%%:*}
    for M in $(echo ${spec#*:} | tr ',' ' '); do
      D=$W/$L/$M; mkdir -p $D; cp $S/probe.* $D/
      if ! build $L $M $D; then echo "$L $M : construction échouée : $(tail -3 $D/build.log | tr '\n' ' ')"; continue; fi
      for C in 1d 2d; do
        res=$(run $L $M $D $C); e=$(expect $L $M $C)
        case "$res" in "$e"*) v=conforme ;; *) v="NON CONFORME" ;; esac
        echo "$L $M $C : $res [$e] $v"
      done
    done
  done
} > probes.txt 2>&1
cat probes.txt
