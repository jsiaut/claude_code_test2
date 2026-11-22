#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Rust (rustc 1.99.1, -C target-cpu=native, release).
# Bibliothèques construites hors du dépôt (CARGO_HOME et CARGO_TARGET_DIR sous /opt/open/rust) ; hwlocality-sys lie
# libhwloc avec ses dépendances statiques (-ludev) : lien libudev.so privé dans /opt/open/rust/lib.
# Écrit results/open/probes/rust.txt (lignes CAP;case;note;bibliothèque;preuve et NOTE).
set -e
cd "$(dirname "$0")"
export CARGO_HOME=/opt/open/rust/cargo CARGO_TARGET_DIR=/opt/open/rust/target_probe
export RUSTFLAGS="-C target-cpu=native -L /opt/open/rust/lib"
mkdir -p /opt/open/rust/lib && ln -sf /usr/lib/x86_64-linux-gnu/libudev.so.1 /opt/open/rust/lib/libudev.so
cargo build --release --offline -q
B=$CARGO_TARGET_DIR/release/open_probe
R=$($B)
r() { echo "$R" | grep "^RESULT;$1;$2;" | cut -d';' -f4-; }
fma=$(objdump -d --no-show-raw-insn $B | awk '/^[0-9a-f]+ <c1_dot_entry>:/ {on=1; next} /^[0-9a-f]+ </ {on=0} on && /vfmadd[0-9]*ps/ && /%ymm/ {n++} END {print n+0}')
cord=$(cargo build --release --offline --example fail_cordyceps 2>&1 | grep -oE "error\[E[0-9]+\][^\n]*" | head -1)
OUT=../../../results/open/probes/rust.txt
{
echo "# Grille ouverte (docs/V4_OPEN.md, 4), Rust : sondes exécutées le $(date '+%Y-%m-%d %H:%M'), machine 34, $(rustc --version)"
echo "CAP;B2;1;bumpalo 3.20.4;[exécutée] $(r B2 bumpalo)"
echo "NOTE;B2;note publiée ½ ; arène de premier ordre pour tout T et pour les collections du crate (Vec, String, Box) sur rustc stable : 1 ; limite : les collections de std (HashMap…) ne la prennent pas sans allocator_api, instable"
echo "CAP;C1;1;fearless_simd 1.2.0;[exécutée] $(r C1 fearless_simd) ; code machine de c1_dot_entry : $fma vfmadd…ps sur ymm"
echo "NOTE;C1;note publiée ½ (std::simd instable) ; types vectoriels portables (f32x4 à f32x16, entiers, masques) sur SSE2, SSE4.2, AVX2, AVX-512, NEON et WebAssembly, choix du niveau à l'exécution : 1"
echo "CAP;C5;1;rayon 1.12.0;[exécutée] $(r C5 rayon)"
echo "NOTE;C5;note publiée 0 ; boucles et réductions parallèles (par_iter, par_chunks, sum, reduce) : 1"
echo "CAP;D3;1;cache-padded 1.3.0;[exécutée] $(r D3 cache-padded)"
echo "NOTE;D3;note publiée 0 ; type de bourrage à la ligne de cache (128 o sur x86-64) : 1 ; le crate se dit déprécié au profit de crossbeam-utils, qui offre le même type"
echo "NOTE;D3;cordyceps 0.3.5, retenue d'abord par la règle : [échec] use cordyceps::util::CachePadded -> $cord : son CachePadded est pub(crate), aucun levier public (correction du relevé, écart 6)"
echo "CAP;D3;1;crossbeam 0.8.5 (nommée);[exécutée] $(r D3 crossbeam)"
echo "CAP;D3;0.5;libc 0.2.191 (nommée);[exécutée] $(r D3 libc)"
echo "NOTE;D3;libc seule : ½, comme sysconf par le module Glibc de Swift (note publiée) : requête à l'exécution, ni constante ni type de bourrage"
echo "CAP;D4;1;core_affinity 0.8.3;[exécutée] $(r D4 core_affinity)"
echo "CAP;D4;1;libc 0.2.191 (nommée);[exécutée] $(r D4 libc)"
echo "NOTE;D4;note publiée 0 ; affinité d'un fil posée et relue : 1, comme sched_setaffinity en C"
echo "CAP;F1;1;ndarray 0.17.2;[exécutée] $(r F1 ndarray)"
echo "NOTE;F1;note publiée ½ (tableaux de tableaux de taille fixe) ; tableau multidimensionnel contigu de dimensions connues à l'exécution : 1"
echo "CAP;F2;1;hwlocality-sys 0.7.2;[exécutée] $(r F2 hwlocality-sys)"
echo "NOTE;F2;note publiée 0 ; placement NUMA de la mémoire (et des fils) par l'API de hwloc, appelée par la liaison du crate : 1"
echo "CAP;F4;1;memmap2 0.9.12;[exécutée] $(r F4 memmap2)"
echo "CAP;F4;1;libc 0.2.191 (nommée);[exécutée] $(r F4 libc)"
echo "NOTE;F4;note publiée 0 ; fichier projeté et lu comme &[u32] sans copie : 1"
} > $OUT
cat $OUT
