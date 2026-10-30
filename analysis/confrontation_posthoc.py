#!/usr/bin/env python3
"""Contrôle hors plan de la confrontation, décidé après avoir vu les rapports appariés : les données principales de K5
viennent de la machine 3 (Emerald Rapids) et le rapport de K5 a été mesuré sur Cascade Lake. Le transfert est sûr
quand la boucle chaude reste la même (C, Fortran), incertain quand la réécriture change la nature du code (Nim et D
perdent la FMA ; Go, Java et Chapel passent au scalaire). Ici, le scénario D est recalculé avec les rapports de K5
forcés à 1 : si les conclusions tiennent, elles ne dépendent pas de ce transfert.
Sortie : results/confrontation_posthoc.json."""
import json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT  # noqa: E402
from banc_data import BANC_S  # noqa: E402


def main():
    data, lat, *_ = v2.dataset_main()
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    conf, _bad = cf.load_conf()
    ratios = cf.paired_ratios(conf, data, np.random.default_rng(v3.SEED + 20))
    for (l, key), r in ratios.items():
        if r is not None and key[0] == "k5":
            r["ratio"] = 1.0
    dR, _notes, _w = cf.rule_data(data, ratios)
    banc_rank = cf.avg_ranks(BANC_S)
    s = cf.scenario(dR, lat, langs, footprint, c3, "R")
    c = cf.compare(s["order18"], banc_rank)
    out = {"scenario": "D, rapports de K5 forcés à 1", "order18": s["order18"], "cmp": c,
           "E": {l: s["E"][l] for l in cf.L18}}
    json.dump(out, open(os.path.join(ROOT, "results", "confrontation_posthoc.json"), "w"), indent=1, default=float)
    print(f"D sans transfert de K5 : Spearman {c['spearman']:.3f}, Kendall {c['kendall']:.3f}, rang de C {c['rank']['c']}")
    print("ordre :", ", ".join(s["order18"]))


if __name__ == "__main__":
    main()
