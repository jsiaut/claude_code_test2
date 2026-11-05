#!/bin/sh
# Remarque sur Swift (docs/SWIFT.md, section 5) : le source publié de bench/swift compilé pour l'hôte Emerald Rapids
# (mêmes options que bench/swift/build.sh : -O, module entier, mode Swift 6, cible native), comme les binaires
# recompilés sur la machine 3 dont viennent K5 publié et la réplication
set -e
cd "$(dirname "$0")"
cp ../swift/ms.swift ms.swift
/opt/swift/usr/bin/swiftc -swift-version 6 -O -wmo -target-cpu native -parse-as-library -o ms ms.swift
rm -f ms.swift
