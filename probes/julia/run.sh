#!/bin/sh
/opt/julia/bin/julia --startup-file=no "$(dirname "$0")/probe.jl"
