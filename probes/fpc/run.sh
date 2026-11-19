#!/bin/sh
# Sonde de FreePascal : base.sh (première sonde, lignes étiquetées ici) puis audit de la grille (audit/, docs/V4_PLAN.md
# 2.1). Sortie : results/probes/fpc.txt
cd "$(dirname "$0")" && mkdir -p bin
sh base.sh > bin/base.out 2>/dev/null
sh audit/run.sh > bin/audit.out 2>/dev/null
python3 - bin/base.out bin/audit.out <<'PY'
import sys
base = [l.rstrip("\n") for l in open(sys.argv[1]) if l.startswith(("CAP;", "NOTE;"))]
audit = [l.rstrip("\n") for l in open(sys.argv[2]) if l.startswith(("CAP;", "NOTE;"))]
replaced = {l.split(";")[1] for l in audit if l.startswith("CAP;")}
v2 = {"D4": ("1", " ; ½ en v1"), "F4": ("1", " ; ½ en v1")}
fail = {"C4"}   # le comportement contraire est mesuré : contraction sans réassociation
for l in base:
    if l.startswith("CAP;"):
        _, c, v, ev = l.split(";", 3)
        if c in replaced: continue
        if c in v2: v, ev = v2[c][0], ev + v2[c][1]
        print(f"CAP;{c};{v};{'[échec] ' if c in fail else '[exécutée] '}{ev}")
    else:
        print(l)
for l in audit: print(l)
PY
