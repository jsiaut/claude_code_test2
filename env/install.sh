#!/bin/sh
# Installe les chaînes de compilation et d'exécution des 25 langages du banc, aux versions de env/toolchains.txt et aux
# chemins que lisent les build.sh, puis les données du banc. Pour Ubuntu 24.04 (x86-64), en root, avec un accès au
# réseau ; écrit et vérifié sur l'image des sessions Claude Code dans le cloud (24 novembre 2026).
#
# Usage : sh env/install.sh              tout (les chaînes déjà en place sont sautées)
#         sh env/install.sh zig go       seulement ces étapes
#         sh env/install.sh --list       liste des étapes
#
# Durée : environ 1 h 30 sur 4 cœurs, dont 35 min pour GCC et 20 min pour Chapel ; disque : environ 35 Gio, dont
# 12 pour LLVM 23 et 5 d'archives dans /opt/dl (empreintes SHA-256 vérifiées), effaçables ensuite. Sources compilées :
# /opt/src. Après l'installation : sh tools/versions.sh > env/toolchains.txt
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
DL=/opt/dl
SRC=/opt/src
J=$(nproc)
export DEBIAN_FRONTEND=noninteractive
mkdir -p "$DL" "$SRC"

say() { printf '== %s\n' "$*"; }

# fetch <url> <fichier dans /opt/dl> <sha256> : télécharge si absent, vérifie l'empreinte
fetch() {
  [ -f "$DL/$2" ] || curl -fL --retry 4 --retry-delay 5 -o "$DL/$2.part" "$1"
  [ -f "$DL/$2" ] || mv "$DL/$2.part" "$DL/$2"
  got=$(sha256sum "$DL/$2" | cut -d' ' -f1)
  [ "$got" = "$3" ] || { rm -f "$DL/$2"; echo "$2 : empreinte $got, attendue $3 (archive effacée)" >&2; exit 1; }
}

# has <texte> <commande...> : vrai si la commande répond et que sa sortie contient le texte
has() {
  want=$1; shift
  out=$("$@" 2>&1) || return 1
  case "$out" in *"$want"*) return 0 ;; *) return 1 ;; esac
}

# ---------------------------------------------------------------------------------------------------- paquets
step_apt() {
  say "paquets du système"
  if [ ! -f /usr/share/keyrings/llvm.gpg ]; then
    curl -fsSL https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /usr/share/keyrings/llvm.gpg
  fi
  for v in 21 22; do
    echo "deb [signed-by=/usr/share/keyrings/llvm.gpg] http://apt.llvm.org/noble/ llvm-toolchain-noble-$v main"
  done > /etc/apt/sources.list.d/llvm.list
  apt-get update -q
  apt-get install -y -q --no-install-recommends \
    build-essential cmake ninja-build git curl ca-certificates gnupg xz-utils unzip pkg-config tzdata \
    python3 python3-venv libpython3-dev \
    libgmp-dev libmpfr-dev libmpc-dev zlib1g-dev gnat-13 \
    llvm-18 clang-18 llvm-21-dev llvm-22-dev clang-22 libclang-22-dev libclang-cpp22-dev \
    libxml2-dev libsqlite3-dev libffi-dev libedit-dev libncurses-dev libcurl4-openssl-dev libzstd-dev libz3-dev \
    libicu74 libnuma1
}

# ---------------------------------------------------------------------------------------------------- GCC 16
# C++ (g++), Fortran (gfortran), Ada (gnat), et C en seconde chaîne (gcc). Compilé depuis l'archive officielle, sans
# amorçage en trois étapes (le compilateur produit est le même ; ses bibliothèques sont compilées par lui-même).
# Les binaires du banc chargent les bibliothèques d'exécution de ce GCC (libstdc++, libgfortran, libgomp), inscrites
# en tête des chemins de l'éditeur de liens dynamique : celles d'Ubuntu 24.04 (GCC 14) n'ont pas les symboles de C++26.
step_gcc16() {
  if has "16.2.0" /opt/gcc-16/bin/gcc-16 --version && has "16.2.0" /opt/gcc-16/bin/gnatmake-16 --version \
     && [ -f /etc/ld.so.conf.d/000-gcc-16.conf ]; then return; fi
  say "GCC 16.2.0 (c, c++, fortran, ada) : environ 40 min"
  fetch https://ftp.gnu.org/gnu/gcc/gcc-16.2.0/gcc-16.2.0.tar.xz gcc-16.2.0.tar.xz \
    e6738e29597f733270731aa90600f37ffdc045079dfc27ec7e8192cc81085c3e
  rm -rf "$SRC/gcc-16.2.0" "$SRC/gcc-16-build"
  tar -C "$SRC" -xf "$DL/gcc-16.2.0.tar.xz"
  mkdir "$SRC/gcc-16-build"
  (cd "$SRC/gcc-16-build" && ../gcc-16.2.0/configure --prefix=/opt/gcc-16 --program-suffix=-16 \
    --enable-languages=c,c++,fortran,ada --disable-multilib --disable-bootstrap > configure.log 2>&1 \
    && make -j"$J" > make.log 2>&1 && make install > install.log 2>&1)
  rm -rf "$SRC/gcc-16-build" "$SRC/gcc-16.2.0"
  echo /opt/gcc-16/lib64 > /etc/ld.so.conf.d/000-gcc-16.conf
  ldconfig
}

# ---------------------------------------------------------------------------------------------------- LLVM 23 (C)
# clang 23.1.5, archive officielle du projet LLVM : le dépôt apt.llvm.org ne garde que la dernière construction de la
# branche 23 (23.1.6 depuis le 16 novembre 2026). Sert au C, à Nim (compilateur C de sa sortie), à C3 et à CBQN.
step_llvm23() {
  if has "clang version 23.1.5" clang-23 --version; then return; fi
  say "LLVM 23.1.5 (clang-23)"
  fetch https://github.com/llvm/llvm-project/releases/download/llvmorg-23.1.5/LLVM-23.1.5-Linux-X64.tar.xz \
    LLVM-23.1.5-Linux-X64.tar.xz f72edb0b36580ece7f52e23858f00c18fad4e87395ea7ad05d7e55c39f8fc78a
  rm -rf /opt/llvm-23
  mkdir /opt/llvm-23
  tar -C /opt/llvm-23 --strip-components=1 -xf "$DL/LLVM-23.1.5-Linux-X64.tar.xz"
  ln -sf /opt/llvm-23/bin/clang /usr/local/bin/clang-23
}

# ---------------------------------------------------------------------------------------------------- archives binaires
# untar <archive> <répertoire> [composants à retirer] : remplace le répertoire par le contenu de l'archive
untar() {
  rm -rf "$2"
  mkdir -p "$2"
  tar -C "$2" --strip-components="${3:-1}" -xf "$DL/$1"
}

step_zig() {
  if has "0.17.0" /opt/zig/zig version; then return; fi
  say "Zig 0.17.0"
  fetch https://ziglang.org/download/0.17.0/zig-x86_64-linux-0.17.0.tar.xz zig-x86_64-linux-0.17.0.tar.xz \
    1cbe9df9f27e6b78d14ccbca43b6703a404ef79ef1c463de901d7f088d4e2026
  untar zig-x86_64-linux-0.17.0.tar.xz /opt/zig
}

step_go() {
  if has "go1.27.3" /opt/go127/bin/go version; then return; fi
  say "Go 1.27.3"
  fetch https://go.dev/dl/go1.27.3.linux-amd64.tar.gz go1.27.3.linux-amd64.tar.gz \
    65efbc80fdc1fa2cd2631cad5b481777a68e8725f34e89f50fc6ac714e379b40
  untar go1.27.3.linux-amd64.tar.gz /opt/go127
}

step_node() {
  if has "v26.12.1" /opt/node26/bin/node --version; then return; fi
  say "Node.js 26.12.1"
  fetch https://nodejs.org/dist/v26.12.1/node-v26.12.1-linux-x64.tar.xz node-v26.12.1-linux-x64.tar.xz \
    6170b2d474e1c626f43cff3adc118df9fe3b573258a4fc3d850c8dbc6b079bbd
  untar node-v26.12.1-linux-x64.tar.xz /opt/node26
}

step_julia() {
  if has "1.13.3" /opt/julia/bin/julia --version; then return; fi
  say "Julia 1.13.3"
  fetch https://julialang-s3.julialang.org/bin/linux/x64/1.13/julia-1.13.3-linux-x86_64.tar.gz \
    julia-1.13.3-linux-x86_64.tar.gz 5c61cb4b40332cb5a3504e7779e2f5dac093caa4a1116ded19f01413f85c63e4
  untar julia-1.13.3-linux-x86_64.tar.gz /opt/julia
}

step_nim() {
  if has "2.2.12" /opt/nim/bin/nim --version; then return; fi
  say "Nim 2.2.12"
  fetch https://nim-lang.org/download/nim-2.2.12-linux_x64.tar.xz nim-2.2.12-linux_x64.tar.xz \
    7df1611449a6842af69322aa2c1206942982650a5f6bc0d37bc8ec109932f638
  untar nim-2.2.12-linux_x64.tar.xz /opt/nim
}

# OpenJDK 27.0.1.0.3 : construction d'Oracle sous GPL (jdk.java.net, archives)
step_jdk() {
  if has "27.0.1.0.3" /opt/jdk27/bin/java -version; then return; fi
  say "OpenJDK 27.0.1.0.3"
  fetch https://download.java.net/java/GA/jdk27.0.1.0.3/b14170c9b2de463d9b89442c6db3e384/1/GPL/openjdk-27.0.1.0.3_linux-x64_bin.tar.gz \
    openjdk-27.0.1.0.3_linux-x64_bin.tar.gz 256199399aaddc6d66919b5de90794b4263e4ab312aa56692cb63b70a0abef41
  untar openjdk-27.0.1.0.3_linux-x64_bin.tar.gz /opt/jdk27
}

step_dotnet() {
  if has "10.0.403" /opt/dotnet/dotnet --version; then return; fi
  say ".NET SDK 10.0.403"
  fetch https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.403/dotnet-sdk-10.0.403-linux-x64.tar.gz \
    dotnet-sdk-10.0.403-linux-x64.tar.gz cd7224fe8e8ba57c15f1601439ff8785a1a72b54ae5c89dd5302a32dcfbddf18
  untar dotnet-sdk-10.0.403-linux-x64.tar.gz /opt/dotnet 0
}

step_swift() {
  if has "Swift version 6.4.2" /opt/swift/usr/bin/swiftc --version; then return; fi
  say "Swift 6.4.2"
  fetch https://download.swift.org/swift-6.4.2-release/ubuntu2404/swift-6.4.2-RELEASE/swift-6.4.2-RELEASE-ubuntu24.04.tar.gz \
    swift-6.4.2-RELEASE-ubuntu24.04.tar.gz 2e9ebec040ad459dd89a6d093a02d8314939135104850fae4d5c0f174fb3ba8c
  untar swift-6.4.2-RELEASE-ubuntu24.04.tar.gz /opt/swift
}

# ---------------------------------------------------------------------------------------------------- sources
# clone <dépôt> <répertoire> <étiquette ou commit> : sources à une révision donnée, sans l'historique
clone() {
  rm -rf "$2"
  git init -q "$2"
  git -C "$2" fetch -q --depth 1 "$1" "$3"
  git -C "$2" checkout -q FETCH_HEAD
}

# Odin dev-2026-10 (84bc3fc), compilé contre LLVM 22, la version que choisit son script quand elle est installée
step_odin() {
  if has "dev-2026-10:84bc3fc" /opt/src/odin/odin version; then return; fi
  say "Odin dev-2026-10"
  clone https://github.com/odin-lang/Odin "$SRC/odin" dev-2026-10
  (cd "$SRC/odin" && LLVM_CONFIG=llvm-config-22 make release-native > build.log 2>&1)
}

# C3 0.8.5 (d1b1e44), compilé contre LLVM 23.1.5
step_c3() {
  if has "d1b1e4451716a34e9c5eb46b78999ff92e71c3a1" "$SRC/c3c/build/c3c" --version; then return; fi
  say "C3 0.8.5"
  step_llvm23
  clone https://github.com/c3lang/c3c "$SRC/c3c" d1b1e4451716a34e9c5eb46b78999ff92e71c3a1
  cmake -S "$SRC/c3c" -B "$SRC/c3c/build" -G Ninja -DCMAKE_BUILD_TYPE=Release -DC3_FETCH_LLVM=OFF \
    -DLLVM_DIR=/opt/llvm-23/lib/cmake/llvm > "$SRC/c3c/cmake.log" 2>&1
  cmake --build "$SRC/c3c/build" -j "$J" > "$SRC/c3c/build.log" 2>&1
}

# Rust 1.99.1 par rustup (installé au besoin) ; devient la chaîne par défaut
step_rust() {
  if has "rustc 1.99.1" rustc --version; then return; fi
  say "Rust 1.99.1"
  if ! command -v rustup > /dev/null; then
    curl -fsSL https://sh.rustup.rs | sh -s -- -y --no-modify-path --default-toolchain none
    ln -sf "$HOME/.cargo/bin/rustup" "$HOME/.cargo/bin/rustc" /usr/local/bin/
  fi
  rustup toolchain install 1.99.1 --profile minimal
  rustup default 1.99.1
}

# Free Pascal 3.2.2 : archive officielle, installée par son install.sh (réponses : préfixe, ni EDI, ni documentation,
# ni démonstrations) ; configuration /opt/fpc/etc/fpc.cfg écrite par samplecfg
step_fpc() {
  if has "3.2.2" /opt/fpc/bin/fpc -iV && [ -f /opt/fpc/etc/fpc.cfg ]; then return; fi
  say "Free Pascal 3.2.2"
  fetch https://downloads.freepascal.org/fpc/dist/3.2.2/x86_64-linux/fpc-3.2.2.x86_64-linux.tar \
    fpc-3.2.2.x86_64-linux.tar 5adac308a5534b6a76446d8311fc340747cbb7edeaacfe6b651493ff3fe31e83
  untar fpc-3.2.2.x86_64-linux.tar "$SRC/fpc-install"
  rm -rf /opt/fpc
  (cd "$SRC/fpc-install" && printf '/opt/fpc\nn\nn\nn\ny\n' | bash install.sh > install.log 2>&1)
  mkdir -p /opt/fpc/etc
  /opt/fpc/lib/fpc/3.2.2/samplecfg /opt/fpc/lib/fpc/3.2.2 /opt/fpc/etc > /dev/null
  rm -rf "$SRC/fpc-install"
}

# Lua 5.5.1 : sources officielles, cible « linux » de son Makefile, compilateur C du système
step_lua() {
  if has "Lua 5.5.1" /opt/lua55/bin/lua -v; then return; fi
  say "Lua 5.5.1"
  fetch https://www.lua.org/ftp/lua-5.5.1.tar.gz lua-5.5.1.tar.gz \
    1c4b4068d67061f2a2231ad2b5422e77acea1487ea9890f6320af614f4373dce
  untar lua-5.5.1.tar.gz "$SRC/lua-5.5.1"
  (cd "$SRC/lua-5.5.1" && make linux > build.log 2>&1 && make install INSTALL_TOP=/opt/lua55 >> build.log 2>&1)
  rm -rf "$SRC/lua-5.5.1"
}

# Mojo 1.2.0 : paquet « mojo » de PyPI, dans un environnement virtuel du Python du système
step_mojo() {
  if has "Mojo 1.2.0" /opt/mojo-venv/bin/mojo --version; then return; fi
  say "Mojo 1.2.0"
  rm -rf /opt/mojo-venv
  /usr/bin/python3 -m venv /opt/mojo-venv
  /opt/mojo-venv/bin/pip install -q mojo==1.2.0
}

# CPython 3.15.2 : paquet python3.15 du dépôt deadsnakes, à cette version exacte (le dépôt ne garde que la dernière)
step_python() {
  if has "Python 3.15.2" python3.15 --version; then return; fi
  say "CPython 3.15.2"
  if [ ! -f /usr/share/keyrings/deadsnakes.gpg ]; then
    curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xF23C5A6CF475977595C89F51BA6932366A755776" \
      | gpg --dearmor -o /usr/share/keyrings/deadsnakes.gpg
  fi
  echo "deb [signed-by=/usr/share/keyrings/deadsnakes.gpg] https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu noble main" \
    > /etc/apt/sources.list.d/deadsnakes.list
  apt-get update -q
  apt-get install -y -q --no-install-recommends python3.15=3.15.2-1+noble1 libpython3.15-stdlib=3.15.2-1+noble1
}

# GHC 9.14.1 : distribution binaire pour Ubuntu 24.04 ; -fllvm passe par LLVM 18 (opt, llc, clang du système)
step_ghc() {
  if has "version 9.14.1" /opt/ghc/bin/ghc --version; then return; fi
  say "GHC 9.14.1"
  fetch https://downloads.haskell.org/~ghc/9.14.1/ghc-9.14.1-x86_64-ubuntu24_04-linux.tar.xz \
    ghc-9.14.1-x86_64-ubuntu24_04-linux.tar.xz 530f0861d1d7b45476c158a9e68aa89987687aaf9939df7a15995c45726e2344
  untar ghc-9.14.1-x86_64-ubuntu24_04-linux.tar.xz "$SRC/ghc-bindist"
  rm -rf /opt/ghc
  (cd "$SRC/ghc-bindist" && ./configure --prefix=/opt/ghc LLC=llc-18 OPT=opt-18 LLVMAS=clang-18 > configure.log 2>&1 \
    && make install > install.log 2>&1)
  rm -rf "$SRC/ghc-bindist"
}

# OCaml 5.5.2 avec flambda (l'option -O3 du banc en dépend), sources officielles
step_ocaml() {
  if has "5.5.2" /opt/ocaml/bin/ocamlopt -version && has "flambda: true" /opt/ocaml/bin/ocamlopt -config; then return; fi
  say "OCaml 5.5.2 (flambda)"
  fetch https://github.com/ocaml/ocaml/releases/download/5.5.2/ocaml-5.5.2.tar.gz ocaml-5.5.2.tar.gz \
    bb3ffef5e4fce4f04915b9f254f570663311e1f227fd669aa87a5ef7de9a1523
  untar ocaml-5.5.2.tar.gz "$SRC/ocaml-5.5.2"
  rm -rf /opt/ocaml
  (cd "$SRC/ocaml-5.5.2" && ./configure --prefix=/opt/ocaml --enable-flambda > configure.log 2>&1 \
    && make -j"$J" > build.log 2>&1 && make install > install.log 2>&1)
  rm -rf "$SRC/ocaml-5.5.2"
}

# LDC 1.43.0 : sources officielles, compilées contre LLVM 21 du système avec DMD 2.113.0 ; /opt/ldc est l'arbre de
# construction (les paquets officiels de LDC embarquent LLVM 22)
step_ldc() {
  if has "based on DMD v2.113.0 and LLVM 21.1.8" /opt/ldc/bin/ldc2 --version; then return; fi
  say "LDC 1.43.0 (LLVM 21)"
  fetch https://github.com/ldc-developers/ldc/releases/download/v1.43.0/ldc-1.43.0-src.tar.gz ldc-1.43.0-src.tar.gz \
    d655aad0daf0ce9a17b2ffffb947bb79ec6968bc7fb88bc918316dbe78c616e7
  fetch https://downloads.dlang.org/releases/2.x/2.113.0/dmd.2.113.0.linux.tar.xz dmd.2.113.0.linux.tar.xz \
    b342ab8bd40cc0c46407692b31d7cd69661ff01da686234f426949e881727294
  untar ldc-1.43.0-src.tar.gz "$SRC/ldc"
  untar dmd.2.113.0.linux.tar.xz "$SRC/dmd2"
  rm -rf /opt/ldc
  mkdir /opt/ldc
  (cd /opt/ldc && cmake "$SRC/ldc" -G Ninja -DCMAKE_BUILD_TYPE=Release -DLLVM_CONFIG=/usr/bin/llvm-config-21 \
    -DD_COMPILER="$SRC/dmd2/linux/bin64/dmd" > cmake.log 2>&1 && ninja > build.log 2>&1)
}

# Chapel 2.10.0 : sources officielles, LLVM 22 du système, mêmes variables que bench/chapel/build.sh (le runtime est
# compilé pour le processeur de la machine)
step_chapel() {
  if has "chpl version 2.10.0" "$SRC/chapel/bin/linux64-x86_64/chpl" --version; then return; fi
  say "Chapel 2.10.0 (LLVM 22) : environ 20 min"
  fetch https://github.com/chapel-lang/chapel/releases/download/2.10.0/chapel-2.10.0.tar.gz chapel-2.10.0.tar.gz \
    55234b391e32757fbdcf78a4c9517a1f0f8075e4d73a68005fc4ac251ef6b5d4
  untar chapel-2.10.0.tar.gz "$SRC/chapel"
  (cd "$SRC/chapel" && export CHPL_HOME="$SRC/chapel" CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 \
    CHPL_TARGET_CPU=native CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none \
    && make -j"$J" > build.log 2>&1)
}

# CBQN 0.12.0 pour la cible Cascade Lake (celle de bench/bqn), compilé par clang 23, sans replxx
step_cbqn() {
  if has "CBQN 0.12.0" /opt/cbqn-cl/bin/BQN --version; then return; fi
  say "CBQN 0.12.0"
  step_llvm23
  clone https://github.com/dzaima/CBQN "$SRC/cbqn" v0.12.0
  (cd "$SRC/cbqn" && make o3 target_from_cc=1 f=-march=cascadelake CC=clang-23 version=0.12.0 REPLXX=0 > build.log 2>&1)
  mkdir -p /opt/cbqn-cl/bin
  cp "$SRC/cbqn/BQN" /opt/cbqn-cl/bin/BQN
}

# PHP 8.5.12 : sources officielles, construction « de production » de php-src avec les extensions dont le banc se sert
step_php() {
  if has "PHP 8.5.12" /opt/php85/bin/php --version; then return; fi
  say "PHP 8.5.12"
  fetch https://www.php.net/distributions/php-8.5.12.tar.xz php-8.5.12.tar.xz \
    08bc2eba2a588654ade1357174aa646b761556c862dda0678345ee29ed481209
  untar php-8.5.12.tar.xz "$SRC/php-8.5.12"
  rm -rf /opt/php85
  (cd "$SRC/php-8.5.12" && ./configure --prefix=/opt/php85 --enable-pcntl --enable-shmop --enable-sysvsem \
    --enable-sysvshm --with-ffi --disable-cgi --disable-phpdbg > configure.log 2>&1 \
    && make -j"$J" > build.log 2>&1 && make install > install.log 2>&1 \
    && cp php.ini-production /opt/php85/lib/php.ini)
  rm -rf "$SRC/php-8.5.12"
}

# ---------------------------------------------------------------------------------------------------- données
# Données du banc à la taille publiée (tools/gendata.c), vérifiées contre env/msdata.sha256 ; les autres tailles sont
# produites à la demande dans /dev/shm par tools/sizes/sizes.py
step_data() {
  if (cd /opt/msdata 2> /dev/null && sha256sum --quiet -c "$ROOT/env/msdata.sha256" > /dev/null 2>&1); then return; fi
  say "données du banc (/opt/msdata)"
  mkdir -p /opt/msdata
  gcc -O2 -o "$DL/gendata" "$ROOT/tools/gendata.c"
  "$DL/gendata" /opt/msdata 2> /dev/null
  (cd /opt/msdata && sha256sum --quiet -c "$ROOT/env/msdata.sha256")
}

STEPS="apt gcc16 llvm23 zig go node julia nim jdk dotnet swift odin c3 rust fpc lua mojo python ghc ocaml ldc chapel cbqn php data"

main() {
  if [ "${1:-}" = "--list" ]; then echo "$STEPS"; exit 0; fi
  for s in ${@:-$STEPS}; do
    case " $STEPS " in *" $s "*) ;; *) echo "étape inconnue : $s (étapes : $STEPS)" >&2; exit 2 ;; esac
    "step_$s"
  done
  say "terminé"
}

main "$@"; exit  # sur une ligne : le script peut être modifié pendant qu'il tourne
