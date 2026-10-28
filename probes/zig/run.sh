#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/zig/zig build-exe -O ReleaseFast -mcpu native -femit-bin=bin/probe probe.zig && bin/probe 2>&1
