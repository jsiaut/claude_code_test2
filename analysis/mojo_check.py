#!/usr/bin/env python3
"""Remarque sur Mojo (plan : docs/MOJO.md, section 3), poussé avant les mesures.

Scénarios (analyse globale de la v3 rejouée, mêmes tirages, données principales avec les corrections transférées) :
* Avant : le classement publié avant la remarque (A4, A5, C4, D5 et E5 de Mojo d'avant les errata).
* M-E, classement publié : errata A4 = 1, A5 = 1, C4 = 0,5, D5 = 1, E5 = 1 (section 2). Aucune donnée ne change.
* S-B4 : M-E avec B4 = 0,5, la note que propose la remarque (je garde 1, section 2).
* S-K4 : M-E sans K4 dans le plafond E (poids nul), pour tous les langages (K4 naturel reste dans le code par défaut D1).
* S-K4-B4 : les deux.
Diagnostics (results/raw_mojo, machine 6, 7 processus par cellule) : rapports -D ASSERT=none / défaut ; K4 en SIMD
explicite à chaud et caches vidés, face à K4 sans branchement de Mojo et au C de clang du même hôte.
Sorties : results/mojo_check.json, results/report_mojo.md."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_mojo")
LANG = "mojo"
ERRATA = {"A4": 1, "A5": 1, "C4": 0.5, "D5": 1, "E5": 1}
BEFORE = {"A4": 0.5, "A5": 0.5, "C4": 0, "D5": 0.5, "E5": 0.5}
K4N, K4S, K4B = ("k4", "natural_unsorted", ""), ("k4", "natural_sorted", ""), ("k4", "branchless_unsorted", "")
K9N, Q1N, Q6N = ("k9", "natural", ""), ("k6", "natural", "q1"), ("k6", "natural", "q6")
SIMD, SIMD_COLD = ("k4", "simd_unsorted", ""), ("k4", "simd_cold", "")


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "mojo":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return d, bad


def gm_ms(procs):
    return 1e3 * math.exp(proc_logs(procs).mean())


def summary(s):
    i = RANKED.index(LANG)
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    pos = order.index(LANG)
    nb = {}
    if pos > 0:
        nb["devant"] = (order[pos - 1], float(s["prec"][i, RANKED.index(order[pos - 1])]))
    if pos < len(order) - 1:
        nb["derrière"] = (order[pos + 1], float(s["prec"][i, RANKED.index(order[pos + 1])]))
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "E": {l: s["E"][l] for l in RANKED},
            "D": {l: s["D"][l] for l in RANKED}, "C": {l: s["C"][l] for l in RANKED},
            "Ek": s["Ek"][LANG], "pos": pos + 1, "neighbours": nb,
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def run(data, lat, langs, footprint, c3, cells=None, e_drop=()):
    """Scénario avec des cases de Mojo remplacées le temps du calcul (matrice partagée, restaurée ensuite)."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main", e_drop=e_drop))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def main(suffix=""):
    m = v2.MATRIX[LANG]
    assert {c: m[c][0] for c in ERRATA} == ERRATA and m["B4"][0] == 1, "errata absents"
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 60)
    times = {impl: {":".join(k): gm_ms(p) for k, p in d.items()} for impl, d in raw.items()}
    diag = {f"noassert/défaut {':'.join(k)}": ratio(raw["mojo_noassert"][k], raw["mojo"][k], rng)
            for k in (K4N, K4B, K9N, Q1N, Q6N)}
    diag["simd chaud / sans branchement (mojo_exp)"] = ratio(raw["mojo_exp"][SIMD], raw["mojo_exp"][K4B], rng)
    diag["simd chaud / clang sans branchement"] = ratio(raw["mojo_exp"][SIMD], raw["c"][K4B], rng)
    diag["simd caches vidés / simd chaud"] = ratio(raw["mojo_exp"][SIMD_COLD], raw["mojo_exp"][SIMD], rng)
    diag["naturel trié / non trié (mojo)"] = ratio(raw["mojo"][K4S], raw["mojo"][K4N], rng)
    diag["noassert K9 naturel / clang K9 naturel"] = ratio(raw["mojo_noassert"][K9N], raw["c"][K9N], rng)
    diag["noassert Q1 naturel / clang Q1 naturel"] = ratio(raw["mojo_noassert"][Q1N], raw["c"][Q1N], rng)
    diag["témoin : sans branchement mojo_exp / mojo"] = ratio(raw["mojo_exp"][K4B], raw["mojo"][K4B], rng)
    main_ms = {l: {":".join(k): gm_ms(data[l][k]) for k in (K4N, K4B, K9N, Q1N, Q6N) if k in data[l]}
               for l in ("mojo", "c", "c_gcc")}
    plans = {"Avant": (BEFORE, ()), "M-E": (None, ()), "S-B4": ({"B4": 0.5}, ()),
             "S-K4": (None, ("k4",)), "S-K4-B4": ({"B4": 0.5}, ("k4",))}
    out = {"bad": bad, "times_ms": times, "diag": diag, "main_ms": main_ms, "scenarios": {}}
    for name, (cells, e_drop) in plans.items():
        z = out["scenarios"][name] = run(data, lat, langs, footprint, c3, cells, e_drop)
        print(f"{name} : Mojo {z['ms0'][LANG]:.1f} points, contrôle {z['C'][LANG]:.1f}, rang espéré "
              f"{z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", f"mojo_check{suffix}.json"), "w"), indent=1, default=float)
    report(out, suffix)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o, suffix=""):
    S = o["scenarios"]
    L = ["# Remarque sur Mojo : diagnostics et scénarios\n",
         "Plan : `docs/MOJO.md`. Mesures : `results/raw_mojo/` (machine 6, 7 processus par cellule). Code :",
         "`analysis/mojo_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         "## Temps (moyenne géométrique des médianes par processus, ms)\n",
         "| Implémentation | Clé | Temps (ms) |", "|---|---|---|"]
    for impl, d in o["times_ms"].items():
        for k, t in sorted(d.items()):
            L.append(f"| {impl} | {k} | {f(t, 2)} |")
    L += ["", "## Rapports (même hôte, IC 95 % par rééchantillonnage des processus)\n", "| Rapport | Valeur | IC 95 % |",
          "|---|---|---|"]
    for k, r in o["diag"].items():
        L.append(f"| {k} | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Données principales (ms)\n", "| Langage | " + " | ".join(o["main_ms"]["mojo"]) + " |",
          "|---|" + "---|" * len(o["main_ms"]["mojo"])]
    for l, d in o["main_ms"].items():
        L.append(f"| {l} | " + " | ".join(f(d.get(k), 2) for k in o["main_ms"]["mojo"]) + " |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Mojo | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        nb = z["neighbours"]
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in nb.items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in S.items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", f"report_mojo{suffix}.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
