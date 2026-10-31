#!/bin/sh
# Copie corrigée de la remarque sur Rust (docs/RUST.md) : K7 optimisé avec _MM_HINT_ET0 (prefetchw) ; mêmes options que bench/rust.
set -e
cd "$(dirname "$0")"
rustc --edition 2024 -C opt-level=3 -C target-cpu=native -C codegen-units=1 -o ms ms.rs
