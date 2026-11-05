#!/bin/sh
# Copie de sensibilité de bench/swift (docs/SWIFT.md, plan 3.5) : mêmes options que bench/swift/build.sh
set -e
cd "$(dirname "$0")"
/opt/swift/usr/bin/swiftc -swift-version 6 -O -wmo -target-cpu native -parse-as-library -o ms ms.swift
