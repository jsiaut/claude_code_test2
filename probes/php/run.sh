#!/bin/sh
# Sonde de PHP : base.sh (première sonde, lignes étiquetées ici) puis audit de la grille (audit/, docs/V4_PLAN.md 2.1).
# Sortie : results/probes/php.txt
cd "$(dirname "$0")" && mkdir -p bin
sh base.sh > bin/base.out 2>/dev/null
sh audit/run.sh > bin/audit.out 2>/dev/null
python3 - bin/base.out bin/audit.out <<'PY'
import sys
base = [l.rstrip("\n") for l in open(sys.argv[1]) if l.startswith(("CAP;", "NOTE;"))]
aud = [l.rstrip("\n") for l in open(sys.argv[2])]
srch = {l.split(";")[1]: l.split(";", 2)[2] for l in aud if l.startswith("SEARCHTXT;")}
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in aud if l.startswith("FACT;")}
v2 = {"D4": ("1", " ; ½ en v1")}
# comportement contraire mesuré ou forme canonique refusée (audit.php, audit/run.sh), puis recherche d'absence
fail = {"B3", "C4", "E2", "E7"}
# lignes déclaratives : la recherche d'absence les précède
declarative = {"A6", "B2", "C1", "C2", "C5", "D2", "D3", "D5", "E3", "E4", "E5", "F2", "F4"}
for l in base:
    if not l.startswith("CAP;"):
        print(l); continue
    _, c, v, ev = l.split(";", 3)
    if c in v2: v, ev = v2[c][0], ev + v2[c][1]
    if c in fail:
        print(f"CAP;{c};{v};[échec] {fact[c]} ; {ev} ; {srch[c]}")
    elif c in declarative:
        print(f"CAP;{c};{v};{srch[c]} ; {ev}")
    else:
        print(f"CAP;{c};{v};[exécutée] {ev}")
if fact.get("JIT", "").endswith("non"):
    print("NOTE;JIT;le JIT n'était pas actif pendant l'audit : C4 à refaire")
PY
