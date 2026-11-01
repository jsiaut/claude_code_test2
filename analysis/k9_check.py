#!/usr/bin/env python3
"""Harnais commun de K9 (plan : docs/K9.md, section 3), poussé avant les mesures.

Rapports appariés (machine 16, results/raw_k9h) : harnais commun / ancien, par implémentation et par variante (moyenne
géométrique des médianes de processus, intervalle par bootstrap) ; rapport de la machine 16 à Cascade Lake, à l'ancien
harnais ; rapports des copies de sensibilité à la copie au harnais commun de leur langage.
Scénarios (analyse globale de la v3 rejouée, mêmes tirages) :
* Avant : K9 de Cascade Lake (doit reproduire le scénario Publié de results/c_check.json) ;
* H-hôte : K9 de la machine 16, ancien harnais (information : effet de l'hôte seul) ;
* Publié : K9 de la machine 16, harnais commun (classement publié, analysis/analyze_v2.py, apply_k9h) ;
* I-CL : K9 de Cascade Lake multiplié par le rapport harnais commun / ancien de la machine 16 (information).
Sorties : results/k9_check.json, results/report_k9.md."""
import json, math, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402
from c_check import summary, scaled  # noqa: E402

V3 = v2.K9H_VARIANTS
SENS = {"rust_nat_k9h / rust_k9h": ("rust_nat_k9h", "rust_k9h", "natural"),
        "nim_nat_k9h / nim_k9h": ("nim_nat_k9h", "nim_k9h", "natural"),
        "csharp_exp_k9h mt_pool / mt": ("csharp_exp_k9h", "csharp_exp_k9h", ("mt_pool", "mt")),
        "zig_master_k9h / zig_k9h (naturel)": ("zig_master_k9h", "zig_k9h", "natural"),
        "zig_master_k9h / zig_k9h (tuned)": ("zig_master_k9h", "zig_k9h", "tuned"),
        "zig_master_k9h / zig_k9h (mt)": ("zig_master_k9h", "zig_k9h", "mt")}


def gm_ms(procs):
    return 1e3 * math.exp(proc_logs(procs).mean())


def main():
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    raw = v2.load_k9h_raw()
    rng = np.random.default_rng(v3.SEED + 3000)
    d_before, lat, *_ = v2.dataset_main(k9h=None)
    d_old, *_ = v2.dataset_main(k9h="old")
    d_new, *_ = v2.dataset_main(k9h="common")
    for d in (d_before, d_old, d_new):
        v2.align_lat(d, lat)
    langs = [l for l in RANKED + list(ANNEX) if l in d_new]
    pairs = {}
    for l in RANKED + list(ANNEX):
        for v in V3:
            key = ("k9", v, "")
            new, old = v2.k9h_source(l, v, "common"), v2.k9h_source(l, v, "old")
            if key not in raw.get(new, {}) or key not in raw.get(old, {}):
                continue
            x = {"new": new, "old": old, "n_old": len(raw[old][key]), "n_new": len(raw[new][key]),
                 "old_ms": gm_ms(raw[old][key]), "new_ms": gm_ms(raw[new][key]),
                 "cl_ms": gm_ms(d_before[l][key]) if key in d_before.get(l, {}) else None}
            if new != old:
                x.update({k: v for k, v in ratio(raw[new][key], raw[old][key], rng).items() if k in ("ratio", "ci")})
            x["host_over_cl_old"] = x["old_ms"] / x["cl_ms"] if x["cl_ms"] else None
            pairs.setdefault(l, {})[v] = x
    sens = {}
    for name, (a, b, v) in SENS.items():
        va, vb = (v if isinstance(v, tuple) else (v, v))
        ka, kb = ("k9", va, ""), ("k9", vb, "")
        if ka in raw.get(a, {}) and kb in raw.get(b, {}):
            sens[name] = ratio(raw[a][ka], raw[b][kb], rng)
    k9r = v2.k9h_ratios()
    d_icl = scaled(d_before, {l: dict(keys) for l, keys in k9r.items() if l in d_before})
    plans = {"Avant": d_before, "H-hôte": d_old, "Publié": d_new, "I-CL": d_icl}
    out = {"pairs": pairs, "sensitivity": sens, "scenarios": {}}
    for name, d in plans.items():
        z = out["scenarios"][name] = summary(cf.scenario(d, lat, langs, footprint, c3, "main"))
        top = ", ".join(f"{l} {z['ms0'][l]:.2f} ({z['exp21'][l]:.2f})" for l in z["order21"][:6])
        print(f"{name} : {top}", flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "c_check.json")))["scenarios"]["Publié"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant = {out['check_before']:.2e}")
    # frontière de K9 (meilleur temps parmi les langages classés) dans chaque jeu de données
    out["frontier"] = {}
    for name, d in plans.items():
        fr = {}
        for v in V3:
            key = ("k9", v, "")
            best = {l: gm_ms(d[l][key]) for l in RANKED if key in d.get(l, {})}
            lf = min(best, key=best.get)
            fr[v] = {"lang": lf, "ms": best[lf]}
        out["frontier"][name] = fr
    json.dump(out, open(os.path.join(ROOT, "results", "k9_check.json"), "w"), indent=1, default=float)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Harnais commun de K9 : rapports appariés et scénarios\n",
         "Plan : `docs/K9.md`. Mesures : `results/raw_k9h/` (machine 16, 7 processus par cellule). Code : "
         "`analysis/k9_check.py`.",
         f"Contrôle : le scénario Avant reproduit le publié d'avant (écart maximal {o['check_before']:.1e}).\n",
         "## K9 par implémentation (machine 16 ; Cascade Lake : données publiées d'avant)\n",
         "| Implémentation | Variante | Cascade Lake (ms) | Ancien harnais (ms) | Harnais commun (ms) | Commun / ancien | "
         "IC 95 % | Machine 16 / Cascade Lake (ancien) |",
         "|---|---|---|---|---|---|---|---|"]
    for l in RANKED + list(ANNEX):
        for v in V3:
            x = o["pairs"].get(l, {}).get(v)
            if not x:
                continue
            same = "ratio" not in x
            L.append(f"| {NAMES.get(l, l)} | {v} | {f(x['cl_ms'])} | {f(x['old_ms'])} | {f(x['new_ms'])} | "
                     f"{'inchangé' if same else f(x['ratio'], 3)} | {'' if same else f(x['ci'][0], 3) + '–' + f(x['ci'][1], 3)} | "
                     f"{f(x['host_over_cl_old'], 2)} |")
    L += ["", "## Copies de sensibilité (harnais commun, même campagne)\n", "| Rapport | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
          "|---|---|---|---|---|"]
    for n, x in o["sensitivity"].items():
        L.append(f"| {n} | {f(x['old_ms'])} | {f(x['new_ms'])} | {f(x['ratio'], 3)} | {f(x['ci'][0], 3)}–{f(x['ci'][1], 3)} |")
    L += ["", "## Frontière de K9 (meilleur temps des langages classés)\n", "| Scénario | Naturel | Tuned | mt |", "|---|---|---|---|"]
    for n, fr in o["frontier"].items():
        L.append(f"| {n} | " + " | ".join(f"{NAMES.get(fr[v]['lang'], fr[v]['lang'])} {f(fr[v]['ms'])} ms" for v in V3) + " |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Langage | " + " | ".join(o["scenarios"]) + " |", "|---|" + "---|" * len(o["scenarios"])]
    pub = o["scenarios"]["Publié"]
    for l in pub["order21"]:
        cells = []
        for n, z in o["scenarios"].items():
            cells.append(f"{z['order21'].index(l) + 1}e, {f(z['ms0'][l], 2)} ({f(z['exp21'][l], 2)} ; 1er {f(100 * z['first'][l], 0)} %)")
        L.append(f"| {NAMES.get(l, l)} | " + " | ".join(cells) + " |")
    L.append("")
    for n, z in o["scenarios"].items():
        L.append(f"**{n}** : " + ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                                            for i, l in enumerate(z["order21"][:10])) + ".\n")
    open(os.path.join(ROOT, "results", "report_k9.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
