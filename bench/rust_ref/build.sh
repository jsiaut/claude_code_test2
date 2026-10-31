#!/bin/sh
# Remarque sur Rust (docs/RUST.md) : source de la campagne (bench/rust/ms.rs) recompilé sur l'hôte avec les options du banc (Rust 1.99.1, LLVM 23.1.1), référence des mesures appariées.
set -e
cd "$(dirname "$0")"
rustc --edition 2024 -C opt-level=3 -C target-cpu=native -C codegen-units=1 -o ms ../rust/ms.rs
