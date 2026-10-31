#!/bin/sh
# Remarque sur D (docs/DLANG.md) : source de la campagne compilé par la chaîne officielle prébuild de LDC 1.43.0
# (LLVM 22.1.8, /opt/ldc143), mêmes options. Information.
set -e
cd "$(dirname "$0")"
/opt/ldc143/bin/ldc2 -O3 -release -mcpu=native -od=. -of=ms ../d/ms.d
