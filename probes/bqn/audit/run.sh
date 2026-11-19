#!/bin/sh
# Audit de la grille, BQN (CBQN 0.12.0 du banc) : recherches d'absence dans la liste des valeurs système et de leurs
# membres (tools/grid_audit/listings/bqn_sys.bqn). Imprime des lignes SEARCHTXT (texte ajouté aux lignes de base.sh).
cd "$(dirname "$0")/../../.."
V=$(/opt/cbqn-cl/bin/BQN --version 2>&1 | head -1)
N=$(/opt/cbqn-cl/bin/BQN tools/grid_audit/listings/bqn_sys.bqn | wc -l)
S=$(python3 tools/grid_audit/search.py bqn A2 A3 A4 A6 B2 B3 C1 C2 C5 D1 D2 D3 D4 D5 E2 E3 E4 E5 E7 F2)
echo "$S" | while IFS=';' read k c pub men fil out; do
  echo "SEARCHTXT;$c;[recherche] motif $c dans les $N valeurs système de $V et leurs membres (•listSys, •ns.Keys) : $pub nom ($out)"
done
SYMS=$(nm /opt/cbqn-cl/bin/BQN 2>/dev/null | grep -oE '\b(evalJIT|compileAll|jit_enabled|mmX_allocS)\b' | sort -u | tr '\n' ' ')
OPTS=$(/opt/cbqn-cl/bin/BQN --help 2>&1 | grep -ciE 'jit|asm|disas|perf|dump')
echo "OVERRIDE;E1;[recherche] symboles du JIT dans le binaire livré (nm) : ${SYMS}(mémoire exécutable mmX) ; [échec] aucune option d'affichage du code produit ($OPTS option jit/asm/perf dans --help ; il faut reconstruire avec USE_PERF)"
