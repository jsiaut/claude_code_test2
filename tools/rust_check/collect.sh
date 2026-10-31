#!/bin/sh
# Remarque sur Rust (docs/RUST.md, section 2) : preuves des vérifications faites avant le plan. Écrit results/rust_check/*.txt.
# Prérequis : rustc 1.99.1 (LLVM 23.1.1), clang-23, objdump.
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
T=$ROOT/tools/rust_check
OUT=$ROOT/results/rust_check
W=$ROOT/.work/rust/collect
mkdir -p "$OUT" "$W"
RF="--edition 2024 -C opt-level=3 -C codegen-units=1"

# 1. Chaînes
{ rustc -vV; echo; clang-23 --version | head -1; } > "$OUT/versions.txt"

# 2. K9 naturel : formes, instructions vectorielles par fonction, boucle de la forme du banc sans vérifications
rustc $RF -C target-cpu=native --crate-type=lib --emit=obj -o "$W/k9.o" "$T/k9forms.rs"
objdump -d --no-show-raw-insn "$W/k9.o" > "$W/k9.s"
{ echo "Formes de K9 naturel (tools/rust_check/k9forms.rs), options du banc, cible native (machine 11)."
  echo "f_bench : forme du banc (Vec<Vec<f64>>, double indexation) ; f_unchecked : idem avec get_unchecked (aucune vérification) ;"
  echo "f_rowslices : lignes liées une fois en &[f64] ; f_fixedrows : Vec<[f64; M9]> ; f_flat : Vec<f64> plat."
  for f in f_bench f_unchecked f_rowslices f_fixedrows f_flat; do
    awk "/${f}.*>:\$/{p=1;next} p&&/^\$/{exit} p" "$W/k9.s" > "$W/$f.s"
    echo "$f : $(grep -c -E '\s(v\w+pd)\s.*%[yz]mm' "$W/$f.s") instructions vectorielles sur des doubles (ymm/zmm) ; $(grep -c -E '\sv\w+sd\s' "$W/$f.s") scalaires"
  done
  echo; echo "Boucle interne de f_unchecked (sans vérification de bornes) : les pointeurs de lignes sont relus après chaque écriture"
  cat "$W/f_unchecked.s"; } > "$OUT/k9_forms.txt"

# 3. Q1 optimisé : boucle chaude pour Cascade Lake (code des données principales) et pour l'hôte, Rust et C
sed 's/cnt\[g\] += m.count_ones() as i64;/cnt[g] += _popcnt32(m as i32) as i64;/' "$ROOT/bench/rust/ms.rs" > "$W/ms_pop.rs"
for cpu in cascadelake native; do
  rustc $RF -C target-cpu=$cpu --emit=asm -o "$W/rust_ref_$cpu.s" "$ROOT/bench/rust/ms.rs" 2>/dev/null
  rustc $RF -C target-cpu=$cpu --emit=asm -o "$W/rust_pop_$cpu.s" "$W/ms_pop.rs" 2>/dev/null
  march=$cpu; [ $cpu = native ] && march=native
  clang-23 -std=c23 -O3 -march=$march -pthread -S -o "$W/c_$cpu.s" "$ROOT/bench/c/ms.c"
done
{ echo "Q1 optimisé : boucles de q1_tuned (tools/rust_check/loops.py). La boucle interne est celle des 16 lignes (la plus courte des deux"
  echo "grandes) ; « écritures pile » = vidages de registres. rust_ref : m.count_ones() (banc) ; rust_pop : _popcnt32(m as i32)."
  for cpu in cascadelake native; do
    python3 "$T/loops.py" q1_tuned "$W/rust_ref_$cpu.s" "$W/rust_pop_$cpu.s" "$W/c_$cpu.s"
  done; } > "$OUT/q1_asm.txt"

# 4. K7 optimisé : préchargement dans chaque implémentation, et sonde _MM_HINT_ET0
{ echo "Préchargement de K7 optimisé dans les sources du banc :"
  grep -n -E "_mm_prefetch|__builtin_prefetch|@prefetch|prefetch_write_data|prefetchw\(|llvm_prefetch\(|Prefetch \(|for_write|Sse.Prefetch|prefetch\(c_ptrTo" \
    "$ROOT"/bench/c/ms.c "$ROOT"/bench/cpp/ms.cpp "$ROOT"/bench/rust/ms.rs "$ROOT"/bench/zig/ms.zig "$ROOT"/bench/odin/ms.odin \
    "$ROOT"/bench/c3/ms.c3 "$ROOT"/bench/nim/ms.nim "$ROOT"/bench/d/ms.d "$ROOT"/bench/ada/ms.adb "$ROOT"/bench/mojo/ms.mojo \
    "$ROOT"/bench/csharp/Program.cs "$ROOT"/bench/chapel/ms.chpl | sed "s|$ROOT/||"
  echo; echo "Sonde tools/rust_check/et0.rs (Rust stable 1.99.1, sans attribut de fonctionnalité) :"
  for cpu in native cascadelake; do
    rustc --edition 2024 -C opt-level=3 -C target-cpu=$cpu --crate-type=lib --emit=obj -o "$W/et0_$cpu.o" "$T/et0.rs"
    echo "cible $cpu :"; objdump -d --no-show-raw-insn "$W/et0_$cpu.o" | grep -E ">:|prefetch"
  done; } > "$OUT/prefetch.txt"

# 5. K8 naturel : latences par processus et vol de temps (campagne principale et machine 3)
python3 "$T/k8_steal.py" > "$OUT/k8_steal.txt"
echo "écrit : $(ls "$OUT")"
