#!/bin/sh
# Julia 1.13.3 (LLVM 20.1.8) : compilation JIT ; rien à construire
/opt/julia/bin/julia --startup-file=no -e 'Base.include(Module(), ARGS[1]) ' /dev/null 2>/dev/null; true
