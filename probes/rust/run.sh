#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && rustc --edition 2024 -O -C target-cpu=native -o bin/probe probe.rs && bin/probe
