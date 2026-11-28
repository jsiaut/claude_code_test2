#!/bin/sh
# v7 : le banc OLAP en Rust (rustc 1.99.1, édition 2024), niveau portable (olap_p) et niveau spécialisé (olap_s).
set -e
cd "$(dirname "$0")"
FLAGS="--edition 2024 -C opt-level=3 -C target-cpu=native -C codegen-units=1 --check-cfg cfg(special)"
rustc $FLAGS -o olap_p olap.rs
if [ -f special.rs ]; then rustc $FLAGS --cfg special -o olap_s olap.rs; fi
