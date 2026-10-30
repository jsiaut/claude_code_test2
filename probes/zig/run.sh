#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/zig/zig build-exe -O ReleaseFast -mcpu native -femit-bin=bin/probe probe.zig && bin/probe 2>&1 && /opt/zig/zig build-exe -O fast -mcpu native -femit-bin=bin/probe_f4 probe_f4.zig && bin/probe_f4 2>&1
