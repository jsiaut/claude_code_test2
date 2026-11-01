#!/usr/bin/env python3
"""Remarque sur Nim (plan : docs/NIM.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 12 (results/raw_nim, étiquette « nim »), reportés sur les données principales de Nim ;
analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario, à partir du classement publié (corrections
transférées des autres langages, latences de D3 remesurées) :
* Avant (= publié) : aucune donnée de Nim ne change.
* S-Q1, S-Q1-T : Q1 tuned et mt en intrinsèques (nim_q1 / nim_ref ; règle du pont de analysis/transfer_check.py, et
  transfert seul).
* S-K9, S-K9-T : K9 naturel en ref array[M9, array[M9, float]] (nim_nat / nim_ref).
* S-K8, S-K8-T : arène de K8 sans vérification de débordement (nim_k8 / nim_ref).
* S-tout, S-tout-T : les trois cumulés.
Information : gcc 16 (nim_gcc / nim_ref), Nim 2.4.0 (nim_240 / nim_ref), nim_ref / c et nim_q1 / c sur les clés témoins.
Aucune correction n'est publiée : results/transfers.json ne change pas.
Sorties : results/nim_check.json, results/report_nim.md."""
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

RAW = os.path.join(ROOT, "results", "raw_nim")
LANG = "nim"
LIMIT = 0.25
Q1T, Q1M, Q1N, Q6T = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k6", "natural", "q1"), ("k6", "tuned", "q6")
K9N, K9T, K8T, K8N = ("k9", "natural", ""), ("k9", "tuned", ""), ("k8", "tuned", ""), ("k8", "natural", "")
K4N, K4B, K5N, K5T = ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), ("k5", "tuned", "")
WIT = [Q1T, Q1M, Q6T, K9N, K8T, K4N, K4B]


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "nim":
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
            "prec_nim": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def main(suffix=""):
    """suffix : sorties results/nim_check<suffix>.json et report_nim<suffix>.md (« _current » : état actuel)."""
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 300)
    R = lambda new, old, k: ratio(raw[new][k], raw[old][k], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_q1 = {k: R("nim_q1", "nim_ref", k) for k in (Q1T, Q1M, Q1N, Q6T)}
    r_nat = {k: R("nim_nat", "nim_ref", k) for k in (K9N, K9T)}
    r_k8 = {k: R("nim_k8", "nim_ref", k) for k in (K8T, K8N)}
    r_gcc = {k: R("nim_gcc", "nim_ref", k) for k in (K4N, K4B, K5N, K8T)}
    r_240 = {k: R("nim_240", "nim_ref", k) for k in (K8N, K8T)}
    r_eq = {k: R("nim_ref", "c", k) for k in WIT}
    r_q1c = {k: R("nim_q1", "c", k) for k in (Q1T, Q1M)}
    main_eq = {kk(k): gm(data[LANG][k]) / gm(data["c"][k]) for k in WIT}
    transfer = {}

    def bridged(key, r, new_impl, label):
        t_main = gm(data[LANG][key])
        trf = t_main * r
        br = gm(data["c"][key]) * gm(raw[new_impl][key]) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        used = (br / t_main) if use else r
        transfer[f"{label} {kk(key)}"] = {"nim_main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br,
                                          "gap": gap, "bridge_used": use, "ratio": r, "ratio_used": used,
                                          "c_main_ms": 1e3 * gm(data["c"][key])}
        return used

    q1_b = {k: bridged(k, r_q1[k]["ratio"], "nim_q1", "S-Q1") for k in (Q1T, Q1M)}
    q1_t = {k: r_q1[k]["ratio"] for k in (Q1T, Q1M)}
    k9raw = v2.load_k9h_raw()
    if v2.load_k9h() and K9N in k9raw.get("nim_nat_k9h", {}) and K9N in k9raw.get("nim_k9h", {}):
        # harnais commun de K9 (docs/K9.md, 3.5) : K9 de Nim vient de la machine 16, et la forme naturelle de la
        # remarque y est mesurée dans la même campagne (nim_nat_k9h / nim_k9h, même hôte, même harnais)
        r9 = ratio(k9raw["nim_nat_k9h"][K9N], k9raw["nim_k9h"][K9N], np.random.default_rng(v3.SEED + 3100))["ratio"]
        t9 = gm(data[LANG][K9N])
        transfer[f"S-K9 {kk(K9N)}"] = {"nim_main_ms": 1e3 * t9, "transfer_ms": 1e3 * t9 * r9, "bridge_ms": 1e3 * t9 * r9,
                                       "gap": 0.0, "bridge_used": False, "ratio": r9, "ratio_used": r9,
                                       "c_main_ms": 1e3 * gm(data["c"][K9N]), "k9h": True}
        k9_b = k9_t = {K9N: r9}
    else:
        k9_b = {K9N: bridged(K9N, r_nat[K9N]["ratio"], "nim_nat", "S-K9")}
        k9_t = {K9N: r_nat[K9N]["ratio"]}
    k8_b = {K8T: bridged(K8T, r_k8[K8T]["ratio"], "nim_k8", "S-K8")}
    k8_t = {K8T: r_k8[K8T]["ratio"]}
    plans = {"Avant": data, "S-Q1": scaled(data, q1_b), "S-Q1-T": scaled(data, q1_t),
             "S-K9": scaled(data, k9_b), "S-K9-T": scaled(data, k9_t), "S-K8": scaled(data, k8_b),
             "S-K8-T": scaled(data, k8_t), "S-tout": scaled(data, {**q1_b, **k9_b, **k8_b}),
             "S-tout-T": scaled(data, {**q1_t, **k9_t, **k8_t})}
    out = {"bad": bad, "times_ms": times, "r_q1": {kk(k): r for k, r in r_q1.items()},
           "r_nat": {kk(k): r for k, r in r_nat.items()}, "r_k8": {kk(k): r for k, r in r_k8.items()},
           "r_gcc": {kk(k): r for k, r in r_gcc.items()}, "r_240": {kk(k): r for k, r in r_240.items()},
           "r_eq": {kk(k): r for k, r in r_eq.items()}, "r_q1c": {kk(k): r for k, r in r_q1c.items()},
           "main_eq": main_eq, "transfer": transfer, "scenarios": {}}
    for name, d in plans.items():
        z = out["scenarios"][name] = summary(cf.scenario(d, lat, langs, footprint, c3, "main"))
        print(f"{name} : Nim {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, "
              f"D {z['D'][LANG]:.1f}, K6 {z['Ek'].get('k6', float('nan')):.3f}, rang espéré {z['exp21'][LANG]:.2f} "
              f"({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", f"nim_check{suffix}.json"), "w"), indent=1, default=float)
    report(out, suffix)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o, suffix=""):
    L = ["# Remarque sur Nim : rapports appariés et scénarios\n",
         "Plan : `docs/NIM.md`. Mesures : `results/raw_nim/` (machine 12, 7 processus par cellule). Code :",
         "`analysis/nim_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    for lab, dd in (("nim_q1 / nim_ref", o["r_q1"]), ("nim_nat / nim_ref", o["r_nat"]), ("nim_k8 / nim_ref", o["r_k8"]),
                    ("nim_gcc / nim_ref", o["r_gcc"]), ("nim_240 / nim_ref", o["r_240"]), ("nim_q1 / c", o["r_q1c"])):
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Nim et C sur les clés témoins (information)\n",
          "| Clé | C, hôte (ms) | Nim, hôte (ms) | Nim / C, hôte [IC 95 %] | Nim / C, données principales |", "|---|---|---|---|---|"]
    for k, r in o["r_eq"].items():
        L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 2)} [{f(r['ci'][0], 2)}–"
                 f"{f(r['ci'][1], 2)}] | {f(o['main_eq'][k], 2)} |")
    L += ["", "## Report sur les données principales (transfert ou pont par le C de la campagne)\n",
          "| Clé | Nim (données principales) | Transfert | Pont | Écart | Retenu |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        L.append(f"| {k} | {f(b['nim_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Nim | C | E | D | K6 | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['Ek'].get('k6'), 3)} | {f(z['exp21'][LANG], 2)} | {z['pos']} | "
                 f"{z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", f"report_nim{suffix}.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
