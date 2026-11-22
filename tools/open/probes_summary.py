#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 4) : relit les sorties des sondes (results/open/probes/<langage>.txt, lignes
CAP;case;note;bibliothèque;preuve) et les confronte au relevé (results/open/decisions.json). Écrit
results/open/grid_open.json : pour chaque (langage, case) comblée, la note publiée (v2), la note ouverte (la meilleure
des bibliothèques de la liste qui la comblent, règle et nommées) et la note réduite aux bibliothèques nommées par le
dossier (calcul 4 du plan) ; et results/open/probes/summary.md. Signale toute case comblée sans sonde, et toute sonde
hors du relevé."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX  # noqa: E402
from capabilities_v2 import V2_OVERRIDES  # noqa: E402

DEC = os.path.join(ROOT, "results", "open", "decisions.json")
PROBES = os.path.join(ROOT, "results", "open", "probes")
OUT = os.path.join(ROOT, "results", "open", "grid_open.json")
MD = os.path.join(PROBES, "summary.md")


def published(lang, case):
    if (lang, case) in V2_OVERRIDES:
        return V2_OVERRIDES[(lang, case)][0]
    return MATRIX[lang][case][0]


def main():
    dec = json.load(open(DEC, encoding="utf-8"))
    filled = {}
    for lang, d in dec.items():
        for case, x in d.get("cases", {}).items():
            if x.get("choix"):
                filled.setdefault((lang, case), {"regle": [], "nommees": []})["regle"].append(x["choix"])
        for nm in d.get("nommees", []):
            for case in nm["cases"]:
                filled.setdefault((lang, case), {"regle": [], "nommees": []})["nommees"].append(nm["nom"])
    caps = {}
    for f in sorted(os.listdir(PROBES)):
        if not f.endswith(".txt"):
            continue
        lang = f[:-4]
        for line in open(os.path.join(PROBES, f), encoding="utf-8"):
            if line.startswith("CAP;"):
                _, case, note, lib, proof = line.rstrip("\n").split(";", 4)
                caps.setdefault((lang, case), []).append((float(note), lib, proof))
    problems = []
    for key in filled:
        if key not in caps:
            problems.append(f"case comblée sans sonde : {key}")
    for key in caps:
        if key not in filled:
            problems.append(f"sonde hors du relevé : {key}")
    out, rows = {}, []
    for (lang, case), libs in sorted(filled.items()):
        pub = published(lang, case)
        lines = caps.get((lang, case), [])
        best = max([n for n, _, _ in lines], default=None)
        named = [n for n, lib, _ in lines if any(lib.split()[0] == nm.split()[0] for nm in libs["nommees"])]
        open_note = max(pub, best) if best is not None else pub
        named_note = max(pub, max(named)) if named else pub
        out.setdefault(lang, {})[case] = {"publiee": pub, "ouverte": open_note, "nommees": named_note,
                                          "sondes": [{"note": n, "bibliotheque": lib} for n, lib, _ in lines]}
        rows.append((lang, case, pub, open_note, named_note, " ; ".join(f"{lib} : {n:g}" for n, lib, _ in lines)))
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# Grille ouverte : notes des sondes (v4, point 6)", "",
         "*Écrit par `tools/open/probes_summary.py` à partir de `results/open/probes/<langage>.txt`. Note ouverte : la",
         "meilleure des bibliothèques de la liste qui comblent la case, jamais sous la note publiée (une sonde qui échoue",
         "laisse la note publiée) ; « nommées » : réduite aux bibliothèques nommées par le dossier (calcul 4).*", "",
         "| Langage | Case | Publiée | Ouverte | Nommées seules | Sondes |", "|---|---|---|---|---|---|"]
    for lang, case, pub, o, nm, s in rows:
        L.append(f"| {lang} | {case} | {pub:g} | {o:g} | {nm:g} | {s} |")
    up = sum(1 for r in rows if r[3] > r[2])
    L += ["", f"{len(rows)} cases comblées ; {up} relevées par la piste ouverte, {len(rows) - up} inchangées "
              f"(bibliothèque limitée à la note publiée)."]
    if problems:
        L += ["", "Écarts de couverture :", ""] + [f"* {p}" for p in problems]
    open(MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[-3:]))
    for p in problems:
        print("ÉCART", p)


if __name__ == "__main__":
    main()
