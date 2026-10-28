#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/nim/bin/nim c -d:release --hints:off --cc:clang --clang.exe:clang-23 -o:bin/probe probe.nim && bin/probe
