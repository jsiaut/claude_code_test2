#!/bin/sh
# Remarque sur Chapel (docs/CHAPEL.md, section 2) : sondes compilées par Chapel 2.10.0 (LLVM 22), cas qui échouent et IR.
# Sorties : results/chapel_check/probes.txt et results/chapel_check/ir.txt. Binaires dans un dossier temporaire.
cd "$(dirname "$0")"
ROOT=$(cd ../.. && pwd)
OUT=$ROOT/results/chapel_check
B=$(mktemp -d)
export CHPL_HOME=/opt/src/chapel CHPL_LLVM=system CHPL_LLVM_CONFIG=/usr/bin/llvm-config-22 CHPL_TARGET_CPU=native
export CHPL_COMM=none CHPL_RE2=none CHPL_GMP=none CHPL_UNWIND=none CHPL_LIB_PIC=none
C=$CHPL_HOME/bin/linux64-x86_64/chpl
mkdir -p "$OUT"
{
  echo "# Sondes de la remarque sur Chapel ($($C --version | head -1), hôte : $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2))"
  echo "## Avertissements de --warn-unstable (probes.chpl)"
  $C --fast --warn-unstable probes.chpl -o $B/probes 2>&1 | grep -i unstable
  echo "## Exécution"
  $B/probes
  for p in intrin_imm intrin_pause; do
    echo "## $p.chpl (doit échouer)"
    $C --fast $p.chpl -o $B/$p 2>&1 | grep -i -E "error|undefined" | sed "s#$B##; s#/tmp/[^ :]*##" | head -3
    [ -x $B/$p ] && echo "binaire produit (inattendu)"
  done
} > "$OUT/probes.txt" 2>&1
{
  echo "# IR LLVM de axpy (y[i] += a * x[i]) : métadonnées d'aliasing et de boucle"
  for p in foreach_ir for_ir; do
    $C --fast $p.chpl --llvm-print-ir axpy --llvm-print-ir-stage full -o $B/$p > $B/$p.ll 2>&1
    echo "## $p.chpl : $(grep -o 'llvm.loop.parallel_accesses\|!noalias\|!alias.scope\|llvm.access.group' $B/$p.ll | sort | uniq -c | tr -s ' ' | tr '\n' ';')"
  done
} > "$OUT/ir.txt" 2>&1
rm -rf "$B"
cat "$OUT/probes.txt" "$OUT/ir.txt"
