#!/bin/sh
# Remarque sur Rust (docs/RUST.md) : source de la campagne compilé pour Cascade Lake (-C target-cpu=cascadelake), le code des données principales.
set -e
cd "$(dirname "$0")"
rustc --edition 2024 -C opt-level=3 -C target-cpu=cascadelake -C codegen-units=1 -o ms ../rust/ms.rs
