#!/usr/bin/env python3
"""Effet des erreurs de fait de ma matrice trouvées par le second juge (notation à l'aveugle, vérifiées à la main) :

* C, D3 : __GCC_DESTRUCTIVE_SIZE (64) est prédéfini en mode C par clang 23 et gcc 16, et sysconf donne la taille de
  ligne (glibc) : 0,5 en règle v1 (hors norme mais livré), 1 en v2, 0,25 sous leur règle ;
* D, D3 : std.parallelism.cacheLineSize (Phobos) et core.cpuid.dataCaches (druntime) : 1 sous toutes les règles ;
* Odin, D3 : base:runtime.MAP_CACHE_LINE_SIZE, public mais propre aux tables : 0,5 ;
* Odin, C2 : core:simd/x86 ne couvre l'AVX-512 que par 8 procédures AVX-512F et 6 AVX-512BW : 0,5 ;
* Nim, C5 : l'itérateur || de system ne compile pas une réduction en -d:release (vérifié) : 0,5 en v2.
Recalcule le classement publié (scénario A) et le scénario D de la confrontation avec ces cinq cellules corrigées.
Sortie : results/blind_corrections.json."""
import json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import capabilities  # noqa: E402
import capabilities_v2  # noqa: E402
import standard_rule  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT  # noqa: E402
from banc_data import BANC_S  # noqa: E402

FIX = {  # (langage, capacité) : (v1, v2, leur règle, raison)
    ("c", "D3"): (0.5, 1, 0.25, "__GCC_DESTRUCTIVE_SIZE prédéfini (clang, gcc) ; sysconf(_SC_LEVEL1_DCACHE_LINESIZE)"),
    ("d", "D3"): (1, 1, 1, "std.parallelism.cacheLineSize ; core.cpuid.dataCaches"),
    ("odin", "D3"): (0.5, 0.5, 0.5, "base:runtime.MAP_CACHE_LINE_SIZE, propre aux tables"),
    ("odin", "C2"): (0.5, 0.5, 0.5, "core:simd/x86 : AVX-512 très partiel (8 + 6 procédures)"),
    ("nim", "C5"): (0.5, 0.5, 0.25, "itérateur || : une réduction ne compile pas en -d:release (vérifié)"),
}


def apply_fix():
    for (l, cap), (a, b, r, why) in FIX.items():
        capabilities.MATRIX[l][cap] = (a, why)
        v2.MATRIX[l][cap] = (a, why)
        capabilities_v2.V2_OVERRIDES[(l, cap)] = (b, why)
        v2.V2_OVERRIDES[(l, cap)] = (b, why)
        standard_rule.R_OVERRIDES[(l, cap)] = (r, why)


def main():
    apply_fix()
    data, lat, *_ = v2.dataset_main()
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    conf, _bad = cf.load_conf()
    ratios = cf.paired_ratios(conf, data, np.random.default_rng(v3.SEED + 20))
    dR, _n, _w = cf.rule_data(data, ratios)
    banc = cf.avg_ranks(BANC_S)
    out = {"fix": {f"{l}|{c}": v for (l, c), v in FIX.items()}}
    for name, d, rule in (("A_corrigé", data, "main"), ("D_corrigé", dR, "R")):
        s = cf.scenario(d, lat, langs, footprint, c3, rule)
        order21 = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
        out[name] = {"order21": order21, "exp21": s["exp21"], "ms0": {l: s["ms0"][l] for l in RANKED},
                     "C": {l: s["C"][l] for l in RANKED}, "order18": s["order18"], "cmp": cf.compare(s["order18"], banc)}
        print(name, ":", ", ".join(f"{i + 1}. {l} ({s['exp21'][l]:.2f})" for i, l in enumerate(order21)))
        print("   Spearman 18 avec leur ordre :", round(out[name]["cmp"]["spearman"], 3), "; rang de C :",
              out[name]["cmp"]["rank"]["c"])
    json.dump(out, open(os.path.join(ROOT, "results", "blind_corrections.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
