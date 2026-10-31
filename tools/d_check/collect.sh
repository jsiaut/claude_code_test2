#!/bin/sh
# Remarque sur D (docs/DLANG.md, section 2) : preuves des vérifications faites avant le plan. Écrit results/d_check/*.txt.
# Prérequis : /opt/ldc (LDC 1.43.0 compilé depuis les sources, LLVM 21.1.8), /opt/ldc143 (paquet officiel, LLVM 22.1.8),
# clang++-23, un clone partiel de ldc-developers/ldc au tag v1.43.0 dans $LDCSRC (défaut /home/user/ldc-developers/ldc).
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$ROOT/results/d_check
W=$ROOT/.work/d/collect
LDCSRC=${LDCSRC:-/home/user/ldc-developers/ldc}
mkdir -p "$OUT" "$W"
OPT="-O3 -release -mcpu=native"

# 1. Chaînes : version, LLVM lié, script de construction, CHANGELOG officiel
{ echo "== /opt/ldc (chaîne du classement)"; /opt/ldc/bin/ldc2 --version | head -3; ldd /opt/ldc/bin/ldc2 | grep -i llvm || true
  echo "== /opt/src/build-ldc.sh"; grep -o "cmake .*LLVM_CONFIG=[^ ]*" /opt/src/build-ldc.sh || true
  echo "== /opt/ldc143 (paquet officiel ldc2-1.43.0-linux-x86_64.tar.xz, SHA-256 35805db60f47fd1a162b2035da84d96beec37e6d1e7b1edf60498a90acfaedce)"
  /opt/ldc143/bin/ldc2 --version | head -3
  echo "== CHANGELOG.md, tag v1.43.0 ($(git -C "$LDCSRC" log -1 --format=%h))"; grep -n "LLVM 22\|prebuilt packages use" "$LDCSRC/CHANGELOG.md" | head -3
  echo "== -release (driver/cl_options.cpp et ldc2 --help)"; grep -n -A3 'release("release"' "$LDCSRC/driver/cl_options.cpp"
  /opt/ldc/bin/ldc2 --help | grep -A1 -E "^\s+--release" ; } > "$OUT/versions.txt"

# 2. Q1 optimisé : code machine de la campagne et de la copie corrigée
count() { awk "/^_D2ms7q1TunedF[^:]*:/,/.Lfunc_end/" "$1" > "$W/q1.s"
  echo "$2 : $(grep -c -E '^\s+v' "$W/q1.s") instructions vectorielles ; ymm $(grep -c ymm "$W/q1.s") ; zmm $(grep -c zmm "$W/q1.s") ; vpmovzxbd $(grep -c vpmovzxbd "$W/q1.s") ; vpmuldq $(grep -c vpmuldq "$W/q1.s")"; }
/opt/ldc/bin/ldc2 $OPT -output-s -of="$W/d.s" "$ROOT/bench/d/ms.d"
/opt/ldc/bin/ldc2 $OPT -output-s -of="$W/dfix.s" "$ROOT/bench/d_fix/ms.d"
{ count "$W/d.s" "campagne (bench/d, six passes masquées par bloc)"; count "$W/dfix.s" "copie corrigée (bench/d_fix, une passe en core.simd)"; } > "$OUT/q1_asm.txt"

# 3. Stencil naturel : boucle de la campagne, métadonnées TBAA, forme rectangulaire, contre-épreuve C++
/opt/ldc/bin/ldc2 $OPT -output-ll -of="$W/d.ll" "$ROOT/bench/d/ms.d"
/opt/ldc/bin/ldc2 $OPT -output-s -of="$W/dnat.s" "$ROOT/bench/d_nat/ms.d"
{ echo "== k9Natural (campagne, double[][]) : boucle interne"
  awk '/^_D2ms9k9NaturalFAAdQdZv:/,/.Lfunc_end/' "$W/d.s" | grep -E "^\s+(v|mov|cmp|j)" | head -40
  echo "== métadonnées !tbaa dans l'IR de LDC (ms.d entier) : $(grep -c '!tbaa' "$W/d.ll")"
  echo "== k9Natural en double[M][] (bench/d_nat) : instructions vectorielles $(awk '/^_D2ms9k9Natural[^:]*:/,/.Lfunc_end/' "$W/dnat.s" | grep -c -E 'v(add|mul)pd')"
  for fl in "" -fno-strict-aliasing; do clang++-23 -O3 -march=native $fl -S -o "$W/st.s" "$ROOT/tools/d_check/stencil.cpp"
    echo "== C++ vector<vector<double>>, clang++ 23 -O3 $fl : $(grep -c -E 'v(add|mul)pd' "$W/st.s") instructions vectorielles, $(grep -c -E 'v(add|mul)sd' "$W/st.s") scalaires"; done
  } > "$OUT/stencil.txt"

# 4. Sonde : core.builtins, core.simd.prefetch, champs de bits natifs
( cd "$W" && /opt/ldc/bin/ldc2 $OPT -of=probe "$ROOT/tools/d_check/probe.d" && ./probe > probe.out
  /opt/ldc/bin/ldc2 -O0 -output-ll -of=p0.ll "$ROOT/tools/d_check/probe.d"
  /opt/ldc/bin/ldc2 $OPT -output-ll -of=p.ll "$ROOT/tools/d_check/probe.d"
  /opt/ldc/bin/ldc2 $OPT -output-s -of=p.s "$ROOT/tools/d_check/probe.d" )
{ echo "sortie : $(cat "$W/probe.out")  (somme, BF.sizeof, champs a et b, expect)"
  echo "llvm.expect à -O0 : $(grep -c 'llvm.expect' "$W/p0.ll") ; llvm.prefetch à -O3 : $(grep -c 'llvm.prefetch' "$W/p.ll") ; prefetcht0 : $(grep -c prefetcht0 "$W/p.s")"
  D=$(dirname "$(find /opt/ldc/include -name builtins.d -path '*core*' | head -1)")
  echo "== $D/builtins.d"; grep -n -E "alias expect|bool likely|bool unlikely" "$D/builtins.d"
  echo "== $D/simd.d"; grep -n -E "void prefetch|llvm_prefetch\(" "$D/simd.d"
  echo "== $D/internal/newaa.d (tableau associatif)"; sed -n 2p "$D/internal/newaa.d"; grep -n "new Entry!(K, V)(key, value)" "$D/internal/newaa.d" | head -2
  } > "$OUT/druntime.txt"
echo "preuves écrites dans $OUT"
