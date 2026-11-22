#!/usr/bin/env bash
# v4, point 5 (docs/V4_COST.md, 3.5) : compilation de chaque copie bench/<langage>_cv pour aarch64 et riscv64 (Linux),
# après une compilation de contrôle pour x86_64 avec le même outil et les options les plus proches de la construction
# publiée (les cibles autres que x86_64 prennent le processeur de base de leur architecture). Langages : ceux qui ont
# une chaîne croisée hors ligne (section 2 du plan) : C (zig cc), C++ (zig c++ : libc++ de LLVM, contrôle attendu en
# refus faute de std::simd), Zig, Go, D (LDC), Odin, C3, Nim (C généré, compilé par zig cc), Fortran (flang-23) et Mojo.
# Compilation sans édition de liens (objets), sauf Go (go build). Les copies sont recopiées dans un répertoire
# temporaire : le dépôt n'est pas modifié. Sortie : results/cost/compile.txt, une ligne par langage et cible :
# langage, cible, « compile » ou « refus », première ligne d'erreur (séparateur : tabulation).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/results/cost/compile.txt"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ZIG=/opt/zig/zig GO=/opt/go127/bin/go LDC=/opt/ldc/bin/ldc2 ODIN=/opt/src/odin/odin C3C=/opt/src/c3c/build/c3c
NIM=/opt/nim/bin/nim FLANG=/usr/bin/flang-23 MOJO=/opt/mojo-venv/bin/mojo
export GOCACHE="$TMP/gocache" GOPATH="$TMP/gopath" GOFLAGS=-mod=mod GOTOOLCHAIN=local

mkdir -p "$(dirname "$OUT")"
{
  echo "# Écrit par tools/cost/xcompile.sh le $(date -u '+%Y-%m-%d %H:%M') UTC (docs/V4_COST.md, 3.5)."
  echo "# Outils : $($ZIG version 2>&1 | head -1) (zig) ; $($GO version 2>&1 | head -1) ;"\
       "$($LDC --version 2>&1 | head -1) ; $($ODIN version 2>&1 | head -1) ; $($C3C --version 2>&1 | head -1) ;"\
       "$($NIM --version 2>&1 | head -1) ; $($FLANG --version 2>&1 | head -1) ; $($MOJO --version 2>&1 | head -1)"
  echo "# langage	cible	résultat	première erreur"
} > "$OUT"

emit() { printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >> "$OUT"; }

# compile LANGAGE CIBLE COMMANDE : exécute la commande (bash -c) dans une copie fraîche de bench/LANGAGE_cv
compile() {
  local lang=$1 tgt=$2 cmd=$3 dir="$TMP/$1.$2" log="$TMP/$1.$2.log"
  rm -rf "$dir"
  cp -r "$ROOT/bench/${lang}_cv" "$dir"
  if (cd "$dir" && timeout 1800 bash -c "$cmd") > "$log" 2>&1; then
    emit "$lang" "$tgt" compile ""
  else
    local err
    err=$(grep -m1 -E 'error|Error|ERROR|erreur|fatal|Fatal|undefined|not supported|unsupported' "$log" \
          | tr '\t' ' ' | cut -c1-300)
    [ -n "$err" ] || err=$(tail -1 "$log" | tr '\t' ' ' | cut -c1-300)
    emit "$lang" "$tgt" refus "$err"
  fi
}

triple() { case $1 in x86_64) echo x86_64-linux-gnu ;; aarch64) echo aarch64-linux-gnu ;; riscv64) echo riscv64-linux-gnu ;; esac; }
native() { [ "$1" = x86_64 ] && echo "$2"; }

for t in x86_64 aarch64 riscv64; do
  tr=$(triple $t)
  # C : options de la construction publiée (clang-23), par zig cc (même clang que Zig)
  compile c $t "$ZIG cc -target $tr $(native $t -march=native) -std=c23 -O3 -pthread -c ms.c -o ms.o"
  # C++ : g++-16 et std::simd de libstdc++ dans la construction publiée ; zig c++ fournit la libc++ de LLVM
  compile cpp $t "$ZIG c++ -target $tr $(native $t -march=native) -std=c++26 -O3 -pthread -c ms.cpp -o ms.o"
  # Zig : mode publié (-O fast)
  zt=$(case $t in x86_64) echo x86_64-linux ;; aarch64) echo aarch64-linux ;; riscv64) echo riscv64-linux ;; esac)
  compile zig $t "$ZIG build-obj ms.zig -O fast -target $zt $(native $t '-mcpu native') -femit-bin=ms.o"
  # Go : GOEXPERIMENT=simd (simd/archsimd), GOAMD64=v4 pour x86_64 comme la construction publiée
  ga=$(case $t in x86_64) echo amd64 ;; aarch64) echo arm64 ;; riscv64) echo riscv64 ;; esac)
  compile go $t "env GOOS=linux GOARCH=$ga $(native $t GOAMD64=v4) GOEXPERIMENT=simd $GO build -o ms ms.go sizes.go"
  # D : LDC, -O3 -release
  compile d $t "$LDC -O3 -release -mtriple=$tr $(native $t -mcpu=native) -J. -c ms.d -of=ms.o"
  # Odin : -o:speed
  ot=$(case $t in x86_64) echo linux_amd64 ;; aarch64) echo linux_arm64 ;; riscv64) echo linux_riscv64 ;; esac)
  compile odin $t "$ODIN build ms.odin -file -o:speed -target:$ot $(native $t -microarch:native) -build-mode:obj -out:ms.o"
  # C3 : -O3, sans édition de liens
  ct=$(case $t in x86_64) echo linux-x64 ;; aarch64) echo linux-aarch64 ;; riscv64) echo linux-riscv64 ;; esac)
  compile c3 $t "$C3C compile-only ms.c3 sizes.c3 -O3 --target $ct $(native $t --x86cpu=native)"
  # Nim : C généré pour la cible, compilé par zig cc (enveloppe), sans édition de liens
  nc=$(case $t in x86_64) echo amd64 ;; aarch64) echo arm64 ;; riscv64) echo riscv64 ;; esac)
  printf '#!/bin/sh\nexec %s cc -target %s "$@"\n' "$ZIG" "$tr" > "$TMP/zigcc-$t"
  chmod +x "$TMP/zigcc-$t"
  compile nim $t "$NIM c -d:release --cpu:$nc --os:linux --cc:clang --clang.exe:$TMP/zigcc-$t \
    --clang.linkerexe:$TMP/zigcc-$t $(native $t '--passC:-march=native') --threads:on --mm:orc --hints:off \
    --warnings:off --nimcache:./nimcache --noLinking:on ms.nim"
  # Fortran : flang-23 (la construction publiée emploie gfortran-16), OpenMP
  ff="$FLANG --target=$tr $(native $t -march=native) -O3 -fopenmp"
  compile fortran $t "$ff -c sizes.f90 -o sizes.o && $ff -c tuned.f90 -o tuned.o && $ff -c ms.f90 -o ms.o"
  # Mojo : objet pour la cible
  mt=$(case $t in x86_64) echo x86_64-unknown-linux-gnu ;; aarch64) echo aarch64-unknown-linux-gnu ;;
       riscv64) echo riscv64-unknown-linux-gnu ;; esac)
  compile mojo $t "$MOJO build --target-triple $mt $(native $t '--target-cpu native') --emit object ms.mojo -o ms.o \
    2>&1 | grep -v Crashpad; test -s ms.o"
done
echo "écrit : $OUT"
