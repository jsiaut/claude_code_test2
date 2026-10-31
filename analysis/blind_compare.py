#!/usr/bin/env python3
"""Notation à l'aveugle (docs/CONFRONTATION.md, addendum) : comparaison du second juge avec ma matrice et avec leur grille.
Écrit et poussé avant de lire les notes du juge.

Entrée : results/blind_notation.json (copie de la sortie du juge). Sorties : results/blind_compare.json et
results/report_blind.md.
(1) juge, règle A (v2), contre ma matrice v2 ; (2) juge, règle B (standard seul), contre ma table du test 1 ;
(3) juge, principes 0-4, contre leur grille. Mesures : accord exact, kappa de Cohen pondéré (poids linéaires),
et pour (3) accord à un niveau près."""
import json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_v2 import ROOT, NAMES, c_cells, spearman  # noqa: E402
from banc_data import BANC_GRID  # noqa: E402
from standard_rule import c_cells_r  # noqa: E402

LANGS = ["c", "cpp", "rust", "zig", "odin", "d", "nim", "csharp"]
ITEMS = ["C1", "C2", "C4", "C5", "D1", "D2", "D3", "D4", "D5", "E3", "E4"]
PRINC = {"P4": 3, "P5": 4, "P8": 7, "P9": 8, "P10": 9, "P12": 11}
CAT_A, CAT_B, CAT_P = [0.0, 0.5, 1.0], [0.0, 0.25, 0.5, 1.0], [0, 1, 2, 3, 4]


def kappa_w(x, y, cats):
    """Kappa de Cohen pondéré, poids linéaires |i - j| / (k - 1) sur les classes ordonnées cats."""
    k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    O = np.zeros((k, k))
    for a, b in zip(x, y):
        O[idx[a], idx[b]] += 1
    O /= O.sum()
    E = np.outer(O.sum(1), O.sum(0))
    W = np.abs(np.subtract.outer(np.arange(k), np.arange(k))) / (k - 1)
    den = (W * E).sum()
    return float(1 - (W * O).sum() / den) if den > 0 else None


def compare(pairs, cats, within=None):
    x, y = [p[0] for p in pairs], [p[1] for p in pairs]
    out = {"n": len(pairs), "exact": float(np.mean([a == b for a, b in pairs])), "kappa_w": kappa_w(x, y, cats),
           "spearman": spearman(x, y)[0]}
    if within is not None:
        out["within"] = float(np.mean([abs(a - b) <= within for a, b in pairs]))
    return out


def verdict(k1, k2, k3):
    """Critères du plan : règles si (1) ou (2) et (3) atteignent 0,6 ; juges aussi si une comparaison est sous 0,4."""
    ks = {"(1)": k1, "(2)": k2, "(3)": k3}
    if any(v is None for v in ks.values()):
        return "indéterminé"
    low = [n for n, v in ks.items() if v < 0.4]
    if low:
        return "tient aussi aux juges (H8) : kappa sous 0,4 en " + ", ".join(low)
    if max(k1, k2) >= 0.6 and k3 >= 0.6:
        return "tient aux règles, pas aux juges"
    return "tient aux règles en partie (kappa entre 0,4 et 0,6)"


def main(suffix=""):
    b = json.load(open(os.path.join(ROOT, "results", "blind_notation.json")))
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    v2, rr = c_cells("v2", c3), c_cells_r(c3)
    cells = {(e["lang"], e["item"]): e for e in b["cells"]}
    pr = {(e["lang"], e["principle"]): e for e in b["principles"]}
    missing = [(l, i) for l in LANGS for i in ITEMS if (l, i) not in cells] + \
              [(l, p) for l in LANGS for p in PRINC if (l, p) not in pr]
    pa = [(float(cells[(l, i)]["rule_a"]), float(v2[l][i])) for l in LANGS for i in ITEMS if (l, i) in cells]
    pb = [(float(cells[(l, i)]["rule_b"]), float(rr[l][i])) for l in LANGS for i in ITEMS if (l, i) in cells]
    pp = [(int(pr[(l, p)]["level"]), BANC_GRID[l][j]) for l in LANGS for p, j in PRINC.items() if (l, p) in pr]
    res = {"missing": missing, "c1": compare(pa, CAT_A), "c2": compare(pb, CAT_B), "c3": compare(pp, CAT_P, within=1)}
    # repère : accord entre leur grille et ma matrice sur les mêmes principes (moyenne de mes cellules, règle B)
    mapping = {"P4": ["D3"], "P5": ["D2", "D5"], "P8": ["C1", "C2", "C4"], "P9": ["E3"], "P10": ["E4"],
               "P12": ["C5", "D1", "D4"]}
    res["ref_spearman_theirs_vs_mineR"] = spearman([BANC_GRID[l][PRINC[p]] for l in LANGS for p in PRINC],
                                                   [np.mean([rr[l][i] for i in mapping[p]]) for l in LANGS for p in PRINC])[0]
    res["verdict"] = verdict(res["c1"]["kappa_w"], res["c2"]["kappa_w"], res["c3"]["kappa_w"])
    res["per_lang"] = {l: {"a": float(np.mean([float(cells[(l, i)]["rule_a"]) == float(v2[l][i]) for i in ITEMS])),
                           "b": float(np.mean([float(cells[(l, i)]["rule_b"]) == float(rr[l][i]) for i in ITEMS])),
                           "p_within1": float(np.mean([abs(int(pr[(l, p)]["level"]) - BANC_GRID[l][j]) <= 1
                                                       for p, j in PRINC.items()]))}
                       for l in LANGS if all((l, i) in cells for i in ITEMS) and all((l, p) in pr for p in PRINC)}
    res["disagree_a"] = [{"lang": l, "item": i, "blind": cells[(l, i)]["rule_a"], "mine": v2[l][i],
                          "means": cells[(l, i)]["means"], "category": cells[(l, i)]["category"],
                          "evidence": cells[(l, i)]["evidence"]}
                         for l in LANGS for i in ITEMS if (l, i) in cells and float(cells[(l, i)]["rule_a"]) != float(v2[l][i])]
    res["disagree_b"] = [{"lang": l, "item": i, "blind": cells[(l, i)]["rule_b"], "mine": rr[l][i],
                          "means": cells[(l, i)]["means"], "category": cells[(l, i)]["category"]}
                         for l in LANGS for i in ITEMS if (l, i) in cells and float(cells[(l, i)]["rule_b"]) != float(rr[l][i])]
    res["disagree_p"] = [{"lang": l, "principle": p, "blind": pr[(l, p)]["level"], "theirs": BANC_GRID[l][j],
                          "justification": pr[(l, p)]["justification"]}
                         for l in LANGS for p, j in PRINC.items() if (l, p) in pr and int(pr[(l, p)]["level"]) != BANC_GRID[l][j]]
    # conséquence sur l'ordre des 8 langages : moyenne des cellules du juge sous chaque règle, et de ses principes
    res["order_blind_a"] = sorted(LANGS, key=lambda l: -np.mean([float(cells[(l, i)]["rule_a"]) for i in ITEMS]))
    res["order_blind_b"] = sorted(LANGS, key=lambda l: -np.mean([float(cells[(l, i)]["rule_b"]) for i in ITEMS]))
    res["order_blind_p"] = sorted(LANGS, key=lambda l: -np.mean([int(pr[(l, p)]["level"]) for p in PRINC]))
    json.dump(res, open(os.path.join(ROOT, "results", f"blind_compare{suffix}.json"), "w"), indent=1, default=float)
    report(res, suffix)


def f(x, d=2):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(r, suffix=""):
    L = ["# Notation à l'aveugle : comparaison du second juge\n",
         "Plan : `docs/CONFRONTATION.md`, addendum. Données du juge : `results/blind_notation.json`, notes "
         "`results/blind_notes.md`.\n",
         "| Comparaison | Cellules | Accord exact | Kappa pondéré | Spearman | À un niveau près |", "|---|---|---|---|---|---|"]
    for k, name in (("c1", "(1) juge règle A / ma matrice v2"), ("c2", "(2) juge règle B / ma table du test 1"),
                    ("c3", "(3) juge principes / leur grille")):
        c = r[k]
        L.append(f"| {name} | {c['n']} | {f(100 * c['exact'], 0)} % | {f(c['kappa_w'])} | {f(c['spearman'])} | "
                 f"{f(100 * c['within'], 0) + ' %' if 'within' in c else '—'} |")
    L.append(f"\nRepère : sur les mêmes principes et les mêmes 8 langages, Spearman entre leur grille et ma table du "
             f"test 1 : {f(r['ref_spearman_theirs_vs_mineR'])}.\n")
    L.append(f"**Verdict selon le critère fixé avant le lancement : l'écart {r['verdict']}.**\n")
    L.append("| Langage | Accord règle A | Accord règle B | Principes à un niveau près |")
    L.append("|---|---|---|---|")
    for l, v in r["per_lang"].items():
        L.append(f"| {NAMES[l]} | {f(100 * v['a'], 0)} % | {f(100 * v['b'], 0)} % | {f(100 * v['p_within1'], 0)} % |")
    L.append("\nOrdre des 8 langages selon le juge : règle A " + ", ".join(NAMES[l] for l in r["order_blind_a"]) +
             " ; règle B " + ", ".join(NAMES[l] for l in r["order_blind_b"]) + " ; principes " +
             ", ".join(NAMES[l] for l in r["order_blind_p"]) + ".\n")
    for key, title in (("disagree_a", "Désaccords (1), règle A"), ("disagree_b", "Désaccords (2), règle B")):
        L.append(f"## {title}\n")
        for d in r[key]:
            L.append(f"* {NAMES[d['lang']]} {d['item']} : juge {f(float(d['blind']))}, moi {f(float(d['mine']))} — "
                     f"{d['means']} ({d['category']})")
        L.append("")
    L.append("## Désaccords (3), leurs principes\n")
    for d in r["disagree_p"]:
        L.append(f"* {NAMES[d['lang']]} {d['principle']} : juge {d['blind']}, eux {d['theirs']} — {d['justification']}")
    if r["missing"]:
        L.append(f"\nCellules manquantes : {r['missing']}")
    text = "\n".join(L) + "\n"
    open(os.path.join(ROOT, "results", f"report_blind{suffix}.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
