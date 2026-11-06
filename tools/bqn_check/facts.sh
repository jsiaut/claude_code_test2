#!/bin/sh
# Faits relevés pour l'ajout de BQN (docs/BQN.md, 2.4) : chaîne CBQN, choix d'implémentation et essais chronométrés
# sur la machine courante. Sortie : results/bqn_check/facts.txt
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SRC=/home/user/dzaima/cbqn
mkdir -p "$ROOT/results/bqn_check"
{
echo "== 0. chaîne"
for b in /opt/cbqn-cl/bin/BQN /opt/cbqn/bin/BQN /opt/cbqn-o3/bin/BQN; do echo "$b : $($b --version | tr '\n' ' ')"; done
sha256sum /opt/cbqn-cl/bin/BQN /opt/cbqn/bin/BQN /opt/cbqn-o3/bin/BQN
for b in /opt/cbqn-cl/bin/BQN /opt/cbqn/bin/BQN /opt/cbqn-o3/bin/BQN; do
  objdump -d --no-show-raw-insn "$b" > /tmp/bqn_facts_dis.$$
  echo "$b : instructions à registres zmm $(grep -c zmm /tmp/bqn_facts_dis.$$), ymm $(grep -c ymm /tmp/bqn_facts_dis.$$), xmm $(grep -c xmm /tmp/bqn_facts_dis.$$) ; opérations sur les masques k $(grep -cE '\{k[1-7]\}|kmov' /tmp/bqn_facts_dis.$$) ; vpcompressb/w (VBMI2) $(grep -cE 'vpcompress[bw]' /tmp/bqn_facts_dis.$$), gf2p8 (GFNI) $(grep -c gf2p8 /tmp/bqn_facts_dis.$$)"
  rm -f /tmp/bqn_facts_dis.$$
done
if [ -d "$SRC/.git" ]; then
  echo "étiquette v0.12.0 : $(git -C $SRC rev-parse 'v0.12.0^{commit}') ($(git -C $SRC log -1 --format=%ci 'v0.12.0^{commit}'))"
  git -C $SRC submodule status | sed 's/^/sous-module : /'
  echo "JIT : $(grep -n 'define JIT_START 2' $SRC/src/vm/vm.h | head -1)"
  echo "GC : $(grep -n '#define ENABLE_GC' $SRC/src/README.md | head -1) ; $(grep -n 'gc disable' $SRC/docs/commands.md | head -1)"
  echo "•math.Sum sur f64 : $(grep -n 'si_sum_f64' $SRC/src/builtins/fold.c | head -1)"
  echo "•bit._cast : $(grep -n "t=='f'" $SRC/src/builtins/bit.c | head -1)"
  echo "allocateur : $(grep -n '#define MM 1' $SRC/src/core/h.h | head -1) ; $(grep -n -A1 'static u64 mm_round' $SRC/src/opt/mm_buddy.h | tr '\n' ' ')"
  echo "options de construction : $(grep -n 'TL;DR' $SRC/README.md | head -1)"
fi
/opt/cbqn-cl/bin/BQN "$ROOT/tools/bqn_check/src/facts.bqn" /opt/msdata   # binaire du banc publié (bench/bqn/run)
} > "$ROOT/results/bqn_check/facts.txt" 2>&1
echo "écrit : results/bqn_check/facts.txt"
