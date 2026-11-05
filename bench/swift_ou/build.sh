#!/bin/sh
# Sensibilité S-Ou (docs/SWIFT.md, plan 3.5) : le source de bench/swift compilé en -Ounchecked (option documentée qui
# retire les vérifications de bornes et de débordement), au lieu du mode release -O
set -e
cd "$(dirname "$0")"
/opt/swift/usr/bin/swiftc -swift-version 6 -Ounchecked -wmo -target-cpu native -parse-as-library -o ms ../swift/ms.swift
