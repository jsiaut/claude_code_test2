#!/bin/sh
# Relève les versions exactes des chaînes de compilation et d'exécution (env/toolchains.txt).
v() { printf '%-14s ' "$1"; shift; "$@" 2>&1 | head -1; }
v clang clang-23 --version
v gcc /opt/gcc-16/bin/gcc-16 --version
v g++ /opt/gcc-16/bin/g++-16 --version
v gfortran /opt/gcc-16/bin/gfortran-16 --version
v flang flang-23 --version
v gnat /opt/gcc-16/bin/gnatmake-16 --version
v rustc rustc --version
v zig /opt/zig/zig version
v odin sh -c 'ls /opt/src/odin >/dev/null; /opt/src/odin/odin version'
v c3c sh -c '/opt/src/c3c/build/c3c --version | grep -i "version" | head -1'
v ldc2 sh -c 'ls /opt/ldc/bin/ldc2 >/dev/null 2>&1 && /opt/ldc/bin/ldc2 --version || ldc2 --version'
v nim sh -c 'ls /opt/nim/bin/nim >/dev/null 2>&1 && /opt/nim/bin/nim --version || nim --version'
v julia /opt/julia/bin/julia --version
v chpl /opt/src/chapel/bin/linux64-x86_64/chpl --version
v mojo sh -c '/opt/mojo-venv/bin/mojo --version'
v go sh -c '/opt/go127/bin/go version 2>/dev/null || go version'
v java sh -c 'unset JAVA_TOOL_OPTIONS; /opt/jdk27/bin/java -version'
v dotnet /opt/dotnet/dotnet --version
v node /opt/node26/bin/node --version
v bun /root/.bun/bin/bun --version
v python3.15 python3.15 --version
v python3.15t python3.15t --version
v ghc sh -c 'ls /opt/ghc/bin/ghc >/dev/null 2>&1 && /opt/ghc/bin/ghc --version || ghc --version'
v ocamlopt sh -c '/opt/ocaml/bin/ocamlopt -version 2>/dev/null || ocamlopt -version'
v lua /opt/lua55/bin/lua -v
v luajit /opt/luajit/bin/luajit -v
v kernel uname -srvm
v cpu sh -c 'grep -m1 "model name" /proc/cpuinfo'
