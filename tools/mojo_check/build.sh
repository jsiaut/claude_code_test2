#!/bin/sh
# Remarque sur Mojo (docs/MOJO.md, section 2) : sondes compilées par Mojo 1.2.0 (2016d0cd), code machine et IR.
# Sorties : results/mojo_check/probes.txt et results/mojo_check/binaries.txt. Binaires dans un dossier temporaire.
set -e
cd "$(dirname "$0")"
ROOT=$(cd ../.. && pwd)
OUT=$ROOT/results/mojo_check
B=$(mktemp -d)
MOJO=/opt/mojo-venv/bin/mojo
mkdir -p "$OUT"
for f in probes noalias2 b4; do
  $MOJO build $f.mojo -o $B/$f 2>&1 | grep -v Crashpad || true
  $MOJO build $f.mojo --emit asm -o $B/$f.s 2>&1 | grep -v Crashpad || true
done
$MOJO build probes.mojo --emit llvm -o $B/probes.ll 2>&1 | grep -v Crashpad || true
gcc -O2 -shared -fPIC -o $B/malloc_count.so malloc_count.c -ldl 2>/dev/null
{
  echo "# Sondes de la remarque sur Mojo ($($MOJO --version 2>&1 | grep -v Crashpad))"
  $B/probes 2>&1 | grep -v Crashpad
  echo "## E5, transfert d'une écriture à une lecture (noalias2.mojo) : fwd_plain, fwd_noalias"
  $B/noalias2 2>&1 | grep -v Crashpad
  echo "## B4 : allocations comptées par malloc_count.so (LD_PRELOAD), N = 0 puis 1000"
  for m in none lit fmt task; do
    for n in 0 1000; do
      echo "$m N=$n : $(LD_PRELOAD=$B/malloc_count.so $B/b4 $m $n 2>&1 >/dev/null | grep ALLOCS)"
    done
  done
} > "$OUT/probes.txt"
fn() { awk -v pat="$2" 'index($0, pat) && /:$/ {f=1} f {print} f && /^\.Lfunc_end/ {exit}' "$1" | grep -v -E '^\s*\.(cfi|p2align|prefalign|type|size)'; }
{
  echo "# Code machine et IR des sondes (mojo build --emit asm / --emit llvm)"
  echo "## E5 : boucle a[i] += b[0] (b[0] relu à chaque tour dans les deux versions)"
  fn $B/probes.s 'probes::add_plain('; fn $B/probes.s 'probes::add_noalias('
  echo "## E5 : a[0] = 1 ; b[0] = 2 ; return a[0] (la version noalias rend la constante)"
  fn $B/noalias2.s 'noalias2::fwd_plain('; fn $B/noalias2.s 'noalias2::fwd_noalias('
  echo "## D5 : llvm_intrinsic[\"llvm.x86.sse2.pause\"] et fence()"
  fn $B/probes.s 'probes::spin_hint()'; fn $B/probes.s 'probes::full_fence()'
  echo "## D5 : SpinWaiter.wait() dans le runtime (libKGENCompilerRTShared.so)"
  L=/opt/mojo-venv/lib/python3.13/site-packages/modular/lib/libKGENCompilerRTShared.so
  A=$(nm -D --defined-only $L | awk '/KGEN_CompilerRT_AsyncRT_SpinWaiter_Wait$/{print $1}')
  objdump -d --no-show-raw-insn --start-address=0x$A --stop-address=$(printf "0x%x" $((0x$A + 0x25))) $L | tail -n +7
  echo "## C4 : IR (non optimisé) de fma_reassoc"
  grep -n "llvm.fma" $B/probes.ll | head -3
  echo "## Chaîne de passes de Mojo 1.2.0 (Mojo/lib/Compiler/ObjectCompiler/LLVMPassesPipeline.cpp, tag mojo/v1.2.0)"
  (cd /opt/src/modular && git show mojo/v1.2.0:Mojo/lib/Compiler/ObjectCompiler/LLVMPassesPipeline.cpp | grep -n -E "addPass\((SLPVectorizer|VectorCombine|LoopVectorize)" ; echo "occurrences de LoopVectorizePass : $(git show mojo/v1.2.0:Mojo/lib/Compiler/ObjectCompiler/LLVMPassesPipeline.cpp | grep -c LoopVectorizePass)")
  echo "## K9 naturel, binaire de la campagne (bench/mojo/ms) : début de la boucle chaude"
  objdump -d --no-show-raw-insn $ROOT/bench/mojo/ms | awk '/k9_natural.*>:$/{f=1} f{print} f&&/^$/{exit}' | sed -n 48,104p | cut -c1-90
  echo "## K4 en SIMD explicite (bench/mojo_exp/ms) : boucle"
  objdump -d --no-show-raw-insn $ROOT/bench/mojo_exp/ms | awk '/k4_simd.*>:$/{f=1} f{print} f&&/^$/{exit}' | sed -n 16,34p | cut -c1-90
} > "$OUT/binaries.txt"
rm -rf "$B"
echo "écrit : $OUT/probes.txt, $OUT/binaries.txt"
