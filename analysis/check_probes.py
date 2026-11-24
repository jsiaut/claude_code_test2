#!/usr/bin/env python3
"""Confronte les sondes exécutées (results/probes/<langage>.txt, lignes CAP;<id>;<valeur>;<preuve>) à la
matrice du pilier C (analysis/capabilities.py ; classes de preuve : docs/METHOD.md, 7). Les sondes
impriment la note de la règle v2 (score central ; la ligne dit quand v1 diffère) : la comparaison se fait à la note
v2 (analysis/capabilities_v2.py), la note v1 est donnée à côté. Toute divergence est listée : la matrice doit être
corrigée ou la divergence expliquée. Écrit results/probes/summary.md."""
import glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX, M  # noqa: E402
from capabilities_v2 import V2_OVERRIDES  # noqa: E402


def main():
    rows, diffs, n = [], [], 0
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "probes", "*.txt"))):
        lang = os.path.basename(f)[:-4]
        for line in open(f, errors="replace"):
            p = line.rstrip("\n").split(";", 3)
            if len(p) < 4 or p[0] != "CAP":
                continue
            cap, val, ev = p[1], float(p[2]), p[3]
            cell = MATRIX.get(lang, {}).get(cap)
            mv = "mesuré" if cell == M else (cell[0] if cell else None)
            m2 = V2_OVERRIDES[(lang, cap)][0] if (lang, cap) in V2_OVERRIDES else mv
            n += 1
            ok = m2 == "mesuré" or m2 == val
            rows.append(f"| {lang} | {cap} | {val:g} | {m2} | {mv} | {'' if ok else 'DIVERGENCE'} | {ev[:110]} |")
            if not ok:
                diffs.append((lang, cap, val, m2, ev))
    out = ["| Langage | Capacité | Sonde | Matrice v2 | v1 | | Preuve |", "|---|---|---|---|---|---|---|"] + rows
    open(os.path.join(ROOT, "results", "probes", "summary.md"), "w").write("\n".join(out) + "\n")
    print(f"{n} lignes de sonde, {len(diffs)} divergences")
    for d in diffs:
        print("  ", d[0], d[1], "sonde", d[2], "matrice v2", d[3], "|", d[4][:150])


if __name__ == "__main__":
    main()
