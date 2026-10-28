#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none && $CHPL_HOME/bin/linux64-x86_64/chpl --fast probe.chpl -o bin/probe && bin/probe
