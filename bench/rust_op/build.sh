#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 5.2) : la commande publiée (bench/rust/build.sh : rustc 1.99.1, -C opt-level=3
# -C target-cpu=native -C codegen-units=1), plus les --extern des crates de la piste ouverte. Les crates sont
# construites une fois par cargo (Cargo.toml de ce dossier, mêmes options) sous /opt/open/rust/target_op.
set -e
cd "$(dirname "$0")"
export CARGO_HOME=/opt/open/rust/cargo CARGO_TARGET_DIR=/opt/open/rust/target_op RUSTFLAGS="-C target-cpu=native"
cargo build --release --offline -q 2>/dev/null || cargo build --release --offline
D=$CARGO_TARGET_DIR/release/deps
ext() { ls -t $D/lib$1-*.rlib | head -1; }
rustc --edition 2024 -C opt-level=3 -C target-cpu=native -C codegen-units=1 -L dependency=$D \
  --extern bumpalo=$(ext bumpalo) --extern cache_padded=$(ext cache_padded) --extern crossbeam=$(ext crossbeam) \
  --extern libc=$(ext libc) -o ms ms.rs
