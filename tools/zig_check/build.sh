#!/bin/sh
# Vérifications préalables de la remarque sur Zig (docs/ZIG.md, section 2). Construit, dans le répertoire donné :
# le pilote C commun avec les noyaux K4/K9 naturels de Zig compilés par 0.15.2, 0.16.0, 0.17.0 et master, et ceux de C
# compilés par le clang de Zig 0.17 et par clang 23 ; l'IR non optimisé de Zig 0.17 passé au pipeline -O3 de son clang ;
# les mesures du coût de lancement des threads. Toolchains : /opt/zig-0.15.2, /opt/zig-0.16.0, /opt/zig (0.17.0),
# /opt/zig-master (0.18.0-dev.753+1420479be), clang-23.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?répertoire de sortie}"
mkdir -p "$OUT" && cd "$OUT"
clang-23 -O2 -c "$SRC/drv.c" -o drv.o
/opt/zig-0.15.2/zig build-obj "$SRC/kern.zig" -O ReleaseFast -mcpu native -fPIC -femit-bin=z0152.o
/opt/zig-0.16.0/zig build-obj "$SRC/kern.zig" -O ReleaseFast -mcpu native -fPIC -femit-bin=z0160.o
/opt/zig/zig build-obj "$SRC/kern.zig" -O fast -mcpu native -fPIC -femit-bin=z0170.o --verbose-llvm-ir=z0170_unopt.ll
/opt/zig-master/zig build-obj "$SRC/kern.zig" -O fast -mcpu native -fPIC -femit-bin=zmaster.o
/opt/zig/zig cc -O3 -march=native -fPIC -c "$SRC/kern.c" -o c_zigcc0170.o
clang-23 -std=c23 -O3 -march=native -c "$SRC/kern.c" -o c_clang23.o
/opt/zig/zig cc -O3 -march=native -fPIC -c z0170_unopt.ll -o ir_through_clang22.o
for o in z0152 z0160 z0170 zmaster c_zigcc0170 c_clang23; do clang-23 drv.o $o.o -o drv_$o; done
/opt/zig/zig build-exe "$SRC/sp.zig" -O fast -mcpu native -femit-bin=sp_zig
/opt/zig/zig build-exe "$SRC/sp.zig" -O fast -mcpu native -lc -femit-bin=sp_zig_libc
/opt/zig/zig build-exe "$SRC/grp.zig" -O fast -mcpu native -femit-bin=grp_zig
clang-23 -O2 -pthread "$SRC/sp.c" -o sp_c
