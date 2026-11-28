#!/bin/sh
# v7 : le banc OLAP en Zig (0.18.0-dev.1298, LLVM 23 : la version de développement, comme dans le banc actuel),
# niveau portable (olap_p) et niveau spécialisé (olap_s) ; -O fast, -mcpu native.
set -e
cd "$(dirname "$0")"
ZIG=/opt/zig-dev/zig
$ZIG build-exe olap_p.zig -O fast -mcpu native -femit-bin=olap_p
$ZIG build-exe olap_s.zig -O fast -mcpu native -femit-bin=olap_s
rm -f olap_p.o olap_s.o
