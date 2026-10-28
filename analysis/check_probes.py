#!/usr/bin/env python3
"""Confronte les sondes exécutées (results/probes/<langage>.txt, lignes CAP;<id>;<valeur>;<preuve>) à la
matrice du pilier C (analysis/capabilities.py). Toute divergence est listée : la matrice doit être
corrigée ou la divergence expliquée. Écrit results/probes/summary.md."""
import glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX, M  # noqa: E402


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
            n += 1
            ok = mv == "mesuré" or mv == val
            rows.append(f"| {lang} | {cap} | {val:g} | {mv} | {'' if ok else 'DIVERGENCE'} | {ev[:110]} |")
            if not ok:
                diffs.append((lang, cap, val, mv, ev))
    out = ["| Langage | Capacité | Sonde | Matrice | | Preuve exécutée |", "|---|---|---|---|---|---|"] + rows
    open(os.path.join(ROOT, "results", "probes", "summary.md"), "w").write("\n".join(out) + "\n")
    print(f"{n} lignes de sonde, {len(diffs)} divergences")
    for d in diffs:
        print("  ", d[0], d[1], "sonde", d[2], "matrice", d[3], "|", d[4][:150])


if __name__ == "__main__":
    main()
