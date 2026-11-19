#!/usr/bin/env python3
"""Audit de la grille (docs/V4_PLAN.md, point 1) : confronte chaque ligne de sonde (results/probes/<langage>.txt,
CAP;<case>;<note>;<preuve>) à la note de la matrice sous la règle v1 (analysis/capabilities.py) et sous la règle v2
(analysis/capabilities_v2.py, score central), classe la preuve ([exécutée], [échec], [recherche], [mesurée] ou
déclarative) et liste les cases sans sonde. Écrit results/grid_audit/summary.md et results/grid_audit/summary.json."""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX, M  # noqa: E402
from capabilities_v2 import V2_OVERRIDES  # noqa: E402

TAGS = ["exécutée", "échec", "recherche", "mesurée"]
SKIP = {"k5_reduction", "trap_cost", "csharp_jitvec_disasm", "csharp_jitvec_tiered_disasm"}


def notes(lang, cap):
    cell = MATRIX[lang][cap]
    if cell == M:
        return "mesurée", "mesurée"
    v1 = cell[0]
    v2 = V2_OVERRIDES.get((lang, cap), (v1,))[0]
    return v1, v2


def main():
    probes = collections.defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "probes", "*.txt"))):
        lang = os.path.basename(f)[:-4]
        if lang in SKIP or lang not in MATRIX:
            continue
        for line in open(f, errors="replace"):
            p = line.rstrip("\n").split(";", 3)
            if len(p) == 4 and p[0] == "CAP":
                probes[lang][p[1]] = (float(p[2]), p[3])
    caps = sorted({c for v in MATRIX.values() for c in v})
    rows, out, div = [], {}, []
    tot = collections.Counter()
    for lang in MATRIX:
        cnt = collections.Counter()
        for cap in caps:
            v1, v2 = notes(lang, cap)
            if v1 == "mesurée":
                cnt["mesurée"] += 1
                continue
            if cap not in probes[lang]:
                cnt["sans sonde"] += 1
                continue
            val, ev = probes[lang][cap]
            tags = [t for t in TAGS if f"[{t}" in ev]
            cnt["déclarative" if not tags else "+".join(tags)] += 1
            cnt["sondée"] += 1
            if val != v2:
                div.append((lang, cap, val, v1, v2, ev))
        out[lang] = dict(cnt)
        tot.update(cnt)
        rows.append(f"| {lang} | {cnt['sondée']} | {cnt['mesurée']} | {cnt['sans sonde']} | {cnt['déclarative']} | "
                    + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items()) if k not in ("sondée", "mesurée", "sans sonde", "déclarative")) + " |")
    md = ["# Audit de la grille : état des sondes", "",
          "Produit par `analysis/grid_audit.py`. Une case est « sondée » si une ligne CAP de `results/probes/<langage>.txt` la "
          "note ; la preuve est classée par ses étiquettes ([exécutée], [échec], [recherche]) ; « déclarative » : ligne sans "
          "étiquette (sonde antérieure à l'audit). Divergence : note de la sonde différente de la note de la matrice sous la "
          "règle v2 (score central).", "",
          "| Langage | Sondées | Mesurées | Sans sonde | Déclaratives | Classes |", "|---|---|---|---|---|---|"] + rows
    md += ["", f"Total : {tot['sondée']} sondées, {tot['mesurée']} mesurées, {tot['sans sonde']} sans sonde, "
           f"{tot['déclarative']} déclaratives.", "", "## Divergences (sonde contre matrice v2)", ""]
    md += ["| Langage | Case | Sonde | v1 | v2 | Preuve |", "|---|---|---|---|---|---|"]
    md += [f"| {d[0]} | {d[1]} | {d[2]:g} | {d[3]:g} | {d[4]:g} | {d[5][:160]} |" for d in div]
    os.makedirs(os.path.join(ROOT, "results", "grid_audit"), exist_ok=True)
    open(os.path.join(ROOT, "results", "grid_audit", "summary.md"), "w").write("\n".join(md) + "\n")
    json.dump({"langs": out, "total": dict(tot), "divergences": [list(d[:5]) for d in div]},
              open(os.path.join(ROOT, "results", "grid_audit", "summary.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{tot['sondée']} sondées, {tot['mesurée']} mesurées, {tot['sans sonde']} sans sonde, {tot['déclarative']} déclaratives ; {len(div)} divergences (v2)")
    for d in div:
        print("  ", d[0], d[1], "sonde", d[2], "v1", d[3], "v2", d[4], "|", d[5][:140])


if __name__ == "__main__":
    main()
