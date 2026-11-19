#!/bin/sh
# Sonde de BQN : base.sh (première sonde, lignes étiquetées ici) et recherches d'absence (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/bqn.txt
cd "$(dirname "$0")" && mkdir -p bin
sh base.sh > bin/base.out 2>/dev/null
sh audit/run.sh > bin/audit.out 2>/dev/null
python3 - bin/base.out bin/audit.out <<'PY'
import sys
base = [l.rstrip("\n") for l in open(sys.argv[1]) if l.startswith(("CAP;", "NOTE;"))]
srch = {l.split(";")[1]: l.rstrip("\n").split(";", 2)[2] for l in open(sys.argv[2]) if l.startswith("SEARCHTXT;")}
over = {l.split(";")[1]: l.rstrip("\n").split(";", 2)[2] for l in open(sys.argv[2]) if l.startswith("OVERRIDE;")}
# classe de la preuve de chaque ligne de base.sh : exécutée (fait observé), échec (comportement contraire mesuré),
# ou rien (déclarative : la recherche d'absence la remplace)
fail = {"A6", "B3", "B4", "E6", "A3"}
declarative = {"A2", "A4", "B2", "C1", "C2", "C5", "D1", "D2", "D3", "D4", "D5", "E2", "E3", "E4", "E5", "E7", "F2"}
for l in base:
    if not l.startswith("CAP;"):
        print(l); continue
    _, c, v, ev = l.split(";", 3)
    if c in over:
        print(f"CAP;{c};{v};{over[c]} ; {ev}"); continue
    if c in declarative:
        txt = srch.get(c, "")
        print(f"CAP;{c};{v};{txt} ; {ev}" if txt else f"CAP;{c};{v};{ev}")
    elif c in fail:
        extra = (" ; " + srch[c]) if c in srch else ""
        print(f"CAP;{c};{v};[échec] {ev}{extra}")
    else:
        print(f"CAP;{c};{v};[exécutée] {ev}")
PY
