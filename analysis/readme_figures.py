#!/usr/bin/env python3
"""Chiffres du README tirés de l'analyse v3 : part des variantes où chaque langage est premier (même analyse globale,
même graine que analysis/analyze_v3.py, rejouée par analysis/confrontation.py), R² du score sur le pilier contrôle
parmi les langages classés devant C# (les 13 premiers jusqu'au 5 novembre, 14 depuis l'ajout de Swift), plage des
probabilités de devancer le voisin parmi eux, part minimale des variantes où ils devancent C#.
Sortie : results/readme_figures.json."""
import json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT  # noqa: E402
from charts_v3 import final_order  # noqa: E402


def main():
    o = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))
    order, exp = final_order(o)
    R = o["results"]
    top = order[:order.index("csharp")]
    r2 = float(np.corrcoef([R[l]["MS"] for l in top], [R[l]["C_v2"] for l in top])[0, 1] ** 2)
    P = o["precedence"]
    neigh = [P[a][b] for a, b in zip(top[:-1], top[1:])]
    data, lat, *_ = v2.dataset_main()
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    s = cf.scenario(data, lat, langs, footprint, c3, "main")
    check = max(abs(s["exp21"][l] - exp[l]) for l in RANKED)
    out = {"first": s["first"], "n_top": len(top), "r2_control_top": r2, "neighbour_range_top": [min(neigh), max(neigh)],
           "min_top_ahead_of_csharp": min(P[l]["csharp"] for l in top), "check_exp_rank_max_diff": check}
    json.dump(out, open(os.path.join(ROOT, "results", "readme_figures.json"), "w"), indent=1)
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items() if k != "first"}))
    print("premiers :", {l: round(v, 3) for l, v in sorted(s["first"].items(), key=lambda x: -x[1]) if v > 0.005})


if __name__ == "__main__":
    main()
