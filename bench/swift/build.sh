#!/bin/sh
# Swift 6.4.2 (swift-6.4.2-RELEASE, LLVM de la chaîne) — mode release -O (vérifications de bornes et de débordement
# conservées), module entier, mode de langage Swift 6, cible native
set -e
cd "$(dirname "$0")"
/opt/swift/usr/bin/swiftc -swift-version 6 -O -wmo -target-cpu native -parse-as-library -o ms ms.swift
