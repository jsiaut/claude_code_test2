#!/bin/sh
# Rust 1.99.1 stable — opt-level=3, target-cpu=native, 1 unité de codegen
set -e
cd "$(dirname "$0")"
rustc --edition 2024 -C opt-level=3 -C target-cpu=native -C codegen-units=1 -o ms ms.rs
