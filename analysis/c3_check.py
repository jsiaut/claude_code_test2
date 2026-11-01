#!/usr/bin/env python3
"""Remarque sur C3 (plan : docs/C3.md, section 3), poussé avant les mesures.

Classement publié : errata de la matrice de C3 (C4, E2, E5 et D4 à 0,5 sous les deux règles ; F4 à 1 en règle v1),
déjà inscrits dans analysis/capabilities.py. Rien des mesures n'entre dans le classement publié.
Scénarios (analyse globale de la v3 rejouée, mêmes tirages), à partir du classement publié (corrections transférées,
latences de D3 remesurées) :
* Avant : la matrice d'avant les errata (doit reproduire le scénario « Avant » de results/nim_check.json).
* Errata : la matrice publiée (le nouveau classement publié).
* S-D3 : errata, plus D3 = 0,5.
* S-K5, S-thr, S-al : errata, plus K5 tuned en arbre (c3_k5 / c3_ref), K9 mt par pthread_create (c3_thr / c3_ref),
  K9 tuned et mt alignés (c3_al / c3_ref) ; règle du pont de analysis/transfer_check.py, et transfert seul (-T).
* S-max : errata, plus --optlevel=max sur toutes les mesures de C3 du score (c3_max / c3_ref, transfert seul).
* S-K5+thr (et -T) : S-K5 et S-thr ensemble.
Information : c3_ref / c sur les clés témoins, comparé aux données principales.
Sorties : results/c3_check.json, results/report_c3.md."""
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

sys.path.insert(0, os.path.join(ROOT, "tools"))
from measure_c3 import SCORE  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_c3")
LANG = "c3"
LIMIT = 0.25
ERRATA = {"C4": 0.5, "E2": 0.5, "E5": 0.5, "D4": 0.5, "F4": 1}   # règle v1 (MATRIX) ; v2 : surcharge F4 = 1 inchangée
BEFORE = {"C4": 0, "E2": 1, "E5": 1, "D4": 0, "F4": 0.5}
K5T, K9T, K9M = ("k5", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", "")
WIT = [K5T, K9T, K9M]


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "c3":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return d, bad


def gm(procs):
    return math.exp(proc_logs(procs).mean())


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
            "prec_c3": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de C3 (règle v1) remplacées le temps du calcul ; la matrice est restaurée ensuite."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def main():
    m = v2.MATRIX[LANG]
    assert {c: m[c][0] for c in ERRATA} == ERRATA, "errata absents de analysis/capabilities.py"
    assert v2.V2_OVERRIDES[(LANG, "F4")][0] == 1 and not any((LANG, c) in v2.V2_OVERRIDES for c in ("C4", "E2", "E5", "D4"))
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 700)
    R = lambda new, old, k: ratio(raw[new][k], raw[old][k], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_k5 = {K5T: R("c3_k5", "c3_ref", K5T)}
    r_thr = {K9M: R("c3_thr", "c3_ref", K9M)}
    r_al = {k: R("c3_al", "c3_ref", k) for k in (K9T, K9M)}
    r_max = {k: R("c3_max", "c3_ref", k) for k in SCORE}
    r_eq = {k: R("c3_ref", "c", k) for k in WIT}
    yl = [(proc_logs(raw["c3_max"][k]).mean() - proc_logs(raw["c3_ref"][k]).mean()) for k in SCORE]
    max_gm = math.exp(float(np.mean(yl)))
    main_eq = {kk(k): gm(data[LANG][k]) / gm(data["c"][k]) for k in WIT}
    transfer = {}

    def bridged(key, r, new_impl, label):
        t_main = gm(data[LANG][key])
        trf = t_main * r
        br = gm(data["c"][key]) * gm(raw[new_impl][key]) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        used = (br / t_main) if use else r
        transfer[f"{label} {kk(key)}"] = {"c3_main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br,
                                          "gap": gap, "bridge_used": use, "ratio": r, "ratio_used": used,
                                          "c_main_ms": 1e3 * gm(data["c"][key])}
        return used

    k5_b = {K5T: bridged(K5T, r_k5[K5T]["ratio"], "c3_k5", "S-K5")}
    k5_t = {K5T: r_k5[K5T]["ratio"]}
    thr_b = {K9M: bridged(K9M, r_thr[K9M]["ratio"], "c3_thr", "S-thr")}
    thr_t = {K9M: r_thr[K9M]["ratio"]}
    al_b = {k: bridged(k, r_al[k]["ratio"], "c3_al", "S-al") for k in (K9T, K9M)}
    al_t = {k: r_al[k]["ratio"] for k in (K9T, K9M)}
    max_t = {k: r_max[k]["ratio"] for k in SCORE}
    plans = {"Avant": (data, BEFORE), "Errata": (data, None), "S-D3": (data, {"D3": 0.5}),
             "S-K5": (scaled(data, k5_b), None), "S-K5-T": (scaled(data, k5_t), None),
             "S-thr": (scaled(data, thr_b), None), "S-thr-T": (scaled(data, thr_t), None),
             "S-al": (scaled(data, al_b), None), "S-al-T": (scaled(data, al_t), None),
             "S-max": (scaled(data, max_t), None),
             "S-K5+thr": (scaled(data, {**k5_b, **thr_b}), None), "S-K5+thr-T": (scaled(data, {**k5_t, **thr_t}), None)}
    out = {"bad": bad, "times_ms": times, "r_k5": {kk(k): r for k, r in r_k5.items()},
           "r_thr": {kk(k): r for k, r in r_thr.items()}, "r_al": {kk(k): r for k, r in r_al.items()},
           "r_max": {kk(k): r for k, r in r_max.items()}, "max_gm": max_gm, "r_eq": {kk(k): r for k, r in r_eq.items()},
           "main_eq": main_eq, "transfer": transfer, "scenarios": {}}
    for name, (d, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, cells)
        print(f"{name} : C3 {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, D {z['D'][LANG]:.1f}, "
              f"rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "nim_check.json")))["scenarios"]["Avant"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant les errata = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(ROOT, "results", "c3_check.json"), "w"), indent=1, default=float)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur C3 : rapports appariés et scénarios\n",
         "Plan : `docs/C3.md`. Mesures : `results/raw_c3/` (machine 13, 7 processus par cellule). Code :",
         "`analysis/c3_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le publié d'avant les errata (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    for lab, dd in (("c3_k5 / c3_ref", o["r_k5"]), ("c3_thr / c3_ref", o["r_thr"]), ("c3_al / c3_ref", o["r_al"]),
                    ("c3_max / c3_ref", o["r_max"])):
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", f"`--optlevel=max` / -O3, moyenne géométrique des {len(o['r_max'])} clés : {f(o['max_gm'], 3)}.\n",
          "## C3 et C sur les clés témoins (information)\n",
          "| Clé | C, hôte (ms) | C3, hôte (ms) | C3 / C, hôte [IC 95 %] | C3 / C, données principales |", "|---|---|---|---|---|"]
    for k, r in o["r_eq"].items():
        L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 2)} [{f(r['ci'][0], 2)}–"
                 f"{f(r['ci'][1], 2)}] | {f(o['main_eq'][k], 2)} |")
    L += ["", "## Report sur les données principales (transfert ou pont par le C de la campagne)\n",
          "| Clé | C3 (données principales) | Transfert | Pont | Écart | Retenu |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        L.append(f"| {k} | {f(b['c3_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de C3 | C | E | D | K5 | K9 | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['Ek'].get('k5'), 3)} | {f(z['Ek'].get('k9'), 3)} | {f(z['exp21'][LANG], 2)} | {z['pos']} | "
                 f"{z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_c3.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
