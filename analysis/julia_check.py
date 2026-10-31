#!/usr/bin/env python3
"""Remarque sur Julia (plan : docs/JULIA.md, section 3), poussé avant les mesures.

Scénarios (analyse globale de la v3 rejouée, mêmes tirages, données principales avec les corrections transférées) :
* Avant : le classement publié avant la remarque (B2 et D3 de Julia à 0, D5 sans cas particulier en règle v2).
* J-E, classement publié : errata B2 = 0,5 et D3 = 0,5 (règles v1 et v2), D5 = 1 en règle v2. Aucune donnée ne change.
* S1 (sensibilité) : J-E, plus les rapports julia_exp/julia de K6 tuned et mt Q1, K7 tuned et K8 tuned (formes de la
  remarque) ; K5 à 1 (les données principales de K5 viennent de la machine 3). Pour chaque clé, pont par le témoin du
  même hôte (C par clang) quand le transfert s'en écarte de plus de 25 % (règle de analysis/transfer_check.py).
* S1-K5 : S1, plus le rapport julia_c512/julia de K5 tuned (option -C native,-prefer-256-bit).
Diagnostics (results/raw_julia, machine 7) : K10 tuned (hors score), témoins dont le code ne change pas.
Sorties : results/julia_check.json, results/report_julia.md."""
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

RAW = os.path.join(ROOT, "results", "raw_julia")
LANG = "julia"
LIMIT = 0.25
K5T, Q1T, Q1M = ("k5", "tuned", ""), ("k6", "tuned", "q1"), ("k6", "mt", "q1")
K7T, K8T, K10T = ("k7", "tuned", ""), ("k8", "tuned", ""), ("k10", "tuned", "")
K9T, Q6T, K1S = ("k9", "tuned", ""), ("k6", "tuned", "q6"), ("k1", "soa", "energy")
EXP_KEYS = [Q1T, Q1M, K7T, K8T]
CONTROLS = [K5T, K9T, Q6T, K1S]


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "julia":
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
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def run(data, lat, langs, footprint, c3, before=False):
    """Scénario ; before=True remet le temps du calcul les cases d'avant les errata (matrice partagée, restaurée)."""
    saved_m, saved_o = {}, None
    try:
        if before:
            for cap in ("B2", "D3"):
                saved_m[cap] = v2.MATRIX[LANG][cap]
                v2.MATRIX[LANG][cap] = (0, saved_m[cap][1])
            saved_o = v2.V2_OVERRIDES.pop((LANG, "D5"))
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        for cap, v in saved_m.items():
            v2.MATRIX[LANG][cap] = v
        if saved_o is not None:
            v2.V2_OVERRIDES[(LANG, "D5")] = saved_o


def main(suffix=""):
    """suffix : sorties results/julia_check<suffix>.json et report_julia<suffix>.md (« _current » : état actuel)."""
    m = v2.MATRIX[LANG]
    assert (m["B2"][0], m["D3"][0], m["D5"][0], v2.V2_OVERRIDES[(LANG, "D5")][0]) == (0.5, 0.5, 0.5, 1), "errata absents"
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 70)
    times = {impl: {":".join(k): 1e3 * gm(p) for k, p in d.items()} for impl, d in raw.items()}
    ratios = {k: ratio(raw["julia_exp"][k], raw["julia"][k], rng) for k in EXP_KEYS + [K10T] + CONTROLS}
    r512 = ratio(raw["julia_c512"][K5T], raw["julia"][K5T], rng)
    keep, bridges = {}, {}
    for k in EXP_KEYS + [K5T]:
        r = r512["ratio"] if k == K5T else ratios[k]["ratio"]
        new5 = raw["julia_c512" if k == K5T else "julia_exp"][k]
        transfer = gm(data[LANG][k]) * r
        bridge = gm(data["c"][k]) * gm(new5) / gm(raw["c"][k])
        gap = transfer / bridge - 1
        use = abs(gap) > LIMIT
        keep[k] = (bridge / gm(data[LANG][k])) if use else r
        bridges[":".join(k)] = {"transfer_ms": 1e3 * transfer, "bridge_ms": 1e3 * bridge, "gap": gap, "bridge_used": use,
                                "ratio_used": keep[k], "julia_main_ms": 1e3 * gm(data[LANG][k]),
                                "c_main_ms": 1e3 * gm(data["c"][k])}
    s1 = {k: keep[k] for k in EXP_KEYS}
    plans = {"Avant": (data, True), "J-E": (data, False), "S1": (scaled(data, s1), False),
             "S1-K5": (scaled(data, {**s1, K5T: keep[K5T]}), False)}
    out = {"bad": bad, "times_ms": times, "ratios": {":".join(k): r for k, r in ratios.items()},
           "ratio_c512_k5": r512, "transfer": bridges, "scenarios": {}}
    for name, (d, before) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, before)
        print(f"{name} : Julia {z['ms0'][LANG]:.1f} points, contrôle {z['C'][LANG]:.1f}, plafond {z['E'][LANG]:.1f}, "
              f"rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", f"julia_check{suffix}.json"), "w"), indent=1, default=float)
    report(out, suffix)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o, suffix=""):
    L = ["# Remarque sur Julia : rapports appariés et scénarios\n",
         "Plan : `docs/JULIA.md`. Mesures : `results/raw_julia/` (machine 7, 7 processus par cellule). Code :",
         "`analysis/julia_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         "## Temps (moyenne géométrique des médianes par processus, ms)\n", "| Implémentation | Clé | Temps (ms) |",
         "|---|---|---|"]
    for impl, d in o["times_ms"].items():
        for k, t in sorted(d.items()):
            L.append(f"| {impl} | {k} | {f(t, 2)} |")
    L += ["", "## Rapports appariés (julia_exp / julia ; K5 : julia_c512 / julia)\n", "| Clé | Rapport | IC 95 % |",
          "|---|---|---|"]
    for k, r in o["ratios"].items():
        L.append(f"| {k} | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    r = o["ratio_c512_k5"]
    L.append(f"| k5:tuned: (julia_c512) | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Report sur les données principales (transfert ou pont par le C de clang)\n",
          "| Clé | Julia (données principales) | Transfert | Pont | Écart | Retenu |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        L.append(f"| {k} | {f(b['julia_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Julia | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", f"report_julia{suffix}.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
