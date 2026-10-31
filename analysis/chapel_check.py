#!/usr/bin/env python3
"""Remarque sur Chapel (plan : docs/CHAPEL.md, section 3), poussé avant les mesures.

Scénarios (analyse globale de la v3 rejouée, mêmes tirages, données principales avec les corrections transférées) :
* Avant : le classement publié avant la remarque (B2, C2 et E5 de Chapel à 0).
* C-E, classement publié : errata B2 = 0,5, C2 = 0,5, E5 = 0,5 (règles v1 et v2). Aucune donnée ne change.
* S-B3 : C-E avec B3 = 1 (la note que la remarque juge défendable ; je garde 0,5).
* S1 (sensibilité) : C-E, plus les rapports chapel_exp/chapel_ref (formes de la remarque) de Q1 tuned et mt, K5 tuned,
  K1 aos et soa, K7 naturel ; pour chaque clé, pont par le C de clang du même hôte quand le transfert s'en écarte de
  plus de 25 % (règle de analysis/transfer_check.py). S1-B3 : S1 avec B3 = 1.
* Confrontation, scénario C (données sous la règle du standard, docs/CONFRONTATION.md) dans l'état actuel du
  classement : avec les rapports de la copie standard d'origine (machine 4), puis avec ceux de la copie corrigée pour
  K5 tuned et K1 aos/soa (chapel_std2/chapel_ref, machine 8).
Sorties : results/chapel_check.json, results/report_chapel.md."""
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

RAW = os.path.join(ROOT, "results", "raw_chapel")
LANG = "chapel"
LIMIT = 0.25
Q1T, Q1M, K5T = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k5", "tuned", "")
K1A, K1S, K7N = ("k1", "aos", "energy"), ("k1", "soa", "energy"), ("k7", "natural", "")
K9T, Q6T, K7T = ("k9", "tuned", ""), ("k6", "tuned", "q6"), ("k7", "tuned", "")
CHANGED = [Q1T, Q1M, K5T, K1A, K1S, K7N]
CONTROLS = [K9T, Q6T, K7T]
STD_KEYS = [K5T, K1A, K1S]
ERRATA = {"B2": 0.5, "C2": 0.5, "E5": 0.5}


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "chapel":
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


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de Chapel remplacées le temps du calcul (matrice partagée, restaurée ensuite)."""
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
    assert {c: m[c][0] for c in ERRATA} == ERRATA and m["B3"][0] == 0.5, "errata absents"
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 80)
    times = {impl: {":".join(k): 1e3 * gm(p) for k, p in d.items()} for impl, d in raw.items()}
    ratios = {k: ratio(raw["chapel_exp"][k], raw["chapel_ref"][k], rng) for k in CHANGED + CONTROLS}
    std = {k: ratio(raw["chapel_std2"][k], raw["chapel_ref"][k], rng) for k in STD_KEYS}
    keep, bridges = {}, {}
    for k in CHANGED:
        r = ratios[k]["ratio"]
        transfer = gm(data[LANG][k]) * r
        bridge = gm(data["c"][k]) * gm(raw["chapel_exp"][k]) / gm(raw["c"][k])
        gap = transfer / bridge - 1
        use = abs(gap) > LIMIT
        keep[k] = (bridge / gm(data[LANG][k])) if use else r
        bridges[":".join(k)] = {"transfer_ms": 1e3 * transfer, "bridge_ms": 1e3 * bridge, "gap": gap, "bridge_used": use,
                                "ratio_used": keep[k], "chapel_main_ms": 1e3 * gm(data[LANG][k]),
                                "c_main_ms": 1e3 * gm(data["c"][k])}
    before = {c: 0 for c in ERRATA}
    plans = {"Avant": (data, before), "C-E": (data, None), "S-B3": (data, {"B3": 1}), "S1": (scaled(data, keep), None),
             "S1-B3": (scaled(data, keep), {"B3": 1})}
    out = {"bad": bad, "times_ms": times, "ratios": {":".join(k): r for k, r in ratios.items()},
           "conf_std": {":".join(k): r for k, r in std.items()}, "transfer": bridges, "scenarios": {}, "conf_C": {}}
    for name, (d, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, cells)
        print(f"{name} : Chapel {z['ms0'][LANG]:.1f} points, contrôle {z['C'][LANG]:.1f}, plafond {z['E'][LANG]:.1f}, "
              f"rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    # confrontation, scénario C : rapports d'origine, puis copie standard corrigée pour K5 tuned et K1 aos/soa
    conf, _ = cf.load_conf()
    r_old = cf.paired_ratios(conf, data, np.random.default_rng(v3.SEED + 20))
    r_new = dict(r_old)
    for k in STD_KEYS:
        r_new[(LANG, k)] = {**std[k], "erratum": "31/10, docs/CHAPEL.md"}
    for name, rr in (("origine", r_old), ("corrigé", r_new)):
        dR, _notes, _w = cf.rule_data(data, rr)
        s = cf.scenario(dR, lat, langs, footprint, c3, "main")
        o18 = s["order18"]
        out["conf_C"][name] = {"E": float(s["E"][LANG]), "ms0": float(s["ms0"][LANG]), "pos18": o18.index(LANG) + 1,
                               "exp18": float(s["exp18"][LANG]), "order18": o18,
                               "ratios": {":".join(k): (rr[(LANG, k)] or {}).get("ratio") for k in STD_KEYS}}
        print(f"confrontation C ({name}) : Chapel plafond {s['E'][LANG]:.1f}, score {s['ms0'][LANG]:.1f}, "
              f"{o18.index(LANG) + 1}e sur 18", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "chapel_check.json"), "w"), indent=1, default=float)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur Chapel : rapports appariés et scénarios\n",
         "Plan : `docs/CHAPEL.md`. Mesures : `results/raw_chapel/` (machine 8, 7 processus par cellule). Code :",
         "`analysis/chapel_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         "## Temps (moyenne géométrique des médianes par processus, ms)\n", "| Implémentation | Clé | Temps (ms) |",
         "|---|---|---|"]
    for impl, d in o["times_ms"].items():
        for k, t in sorted(d.items()):
            L.append(f"| {impl} | {k} | {f(t, 2)} |")
    L += ["", "## Rapports appariés (chapel_exp / chapel_ref)\n", "| Clé | Rapport | IC 95 % |", "|---|---|---|"]
    for k, r in o["ratios"].items():
        L.append(f"| {k} | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Copie standard corrigée (chapel_std2 / chapel_ref)\n", "| Clé | Rapport | IC 95 % |", "|---|---|---|"]
    for k, r in o["conf_std"].items():
        L.append(f"| {k} | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Report sur les données principales (transfert ou pont par le C de clang)\n",
          "| Clé | Chapel (données principales) | Transfert | Pont | Écart | Retenu |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        L.append(f"| {k} | {f(b['chapel_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Chapel | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L += ["", "## Confrontation, scénario C (règle du standard sur les données), état actuel du classement\n",
          "| Copie standard de Chapel | Rapports K5 tuned / K1 aos / K1 soa | Plafond E | Score | Place sur 18 |",
          "|---|---|---|---|---|"]
    for name, c in o["conf_C"].items():
        rs = " / ".join(f(c["ratios"][":".join(k)], 2) for k in STD_KEYS)
        L.append(f"| {name} | {rs} | {f(c['E'])} | {f(c['ms0'])} | {c['pos18']} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_chapel.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
