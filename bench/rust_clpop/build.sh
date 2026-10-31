#!/bin/sh
# Sensibilité de la remarque sur Rust (docs/RUST.md) : Q1 optimisé avec _popcnt32, compilé pour Cascade Lake.
set -e
cd "$(dirname "$0")"
rustc --edition 2024 -C opt-level=3 -C target-cpu=cascadelake -C codegen-units=1 -o ms ms.rs
