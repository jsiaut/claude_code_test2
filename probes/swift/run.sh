#!/bin/sh
# Sonde de Swift : base.sh (première sonde, lignes étiquetées ici) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/swift.txt
cd "$(dirname "$0")"
sh base.sh > bin/base.out 2>/dev/null
sh audit/run.sh > bin/audit.out 2>/dev/null
python3 - bin/base.out bin/audit.out <<'PY'
import sys
base = [l.rstrip("\n") for l in open(sys.argv[1]) if l.startswith(("CAP;", "NOTE;"))]
audit = [l.rstrip("\n") for l in open(sys.argv[2]) if l.startswith(("CAP;", "NOTE;", "SED;"))]
replaced = {l.split(";")[1] for l in audit if l.startswith("CAP;")}
sed = {l.split(";")[1]: l.split(";", 3)[3] for l in audit if l.startswith("SED;")}
v2 = {"D4": ("1", " ; ½ en v1")}
fail = {"A3"}   # comportement contraire mesuré
for l in base:
    k, c = l.split(";")[0], l.split(";")[1]
    if k == "CAP" and c in replaced: continue
    if k == "CAP":
        _, c, v, ev = l.split(";", 3)
        tag = "[échec] " if c in fail else "[exécutée] "
        if c in v2: v, ev = v2[c][0], ev + v2[c][1]
        extra = (' ;' + sed[c]) if c in sed else ''
        print(f"CAP;{c};{v};{tag}{ev}{extra}")
    else:
        print(l)
for l in audit:
    if not l.startswith("SED;"): print(l)
PY
