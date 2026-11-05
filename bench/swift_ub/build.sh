#!/bin/sh
# Copie de sensibilité (remarque sur Swift, docs/SWIFT.md, section 5) : mêmes options que bench/swift/build.sh, cible
# fixée à cascadelake (le code des données publiées, compilé sur la machine 23 en cible native)
set -e
cd "$(dirname "$0")"
/opt/swift/usr/bin/swiftc -swift-version 6 -O -wmo -target-cpu cascadelake -parse-as-library -o ms ms.swift
