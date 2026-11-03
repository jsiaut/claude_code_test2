#!/usr/bin/env python3
"""Remarque sur JavaScript (plan : docs/JAVASCRIPT.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 21 (results/raw_js, étiquette « js »), reportés sur les données publiées de
JavaScript (Node.js 26.12.1) ; analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario du plan (3.5) :
* Avant : le classement publié d'avant (E1 = 1/2, A4 = E6 = 0) ; doit reproduire results/ocaml_check.json (O-E, avec la
  correction de K7 d'OCaml du 3 novembre au soir).
* J-code : K7 tuned × r(js_fix / js_ref), par transfert (la seule clé dont le code publié change) ; grille d'avant.
* J-M : errata E1 = 1, A4 = 1/2, E6 = 1/2 seuls. J-E (classement publié) : les deux.
* J-E-P (information) : J-E, K7 reporté par la règle du pont de analysis/transfer_check.py et la règle de sens.
* Sensibilités (sur J-E, en min(1, r) par rapport à js_ref, même hôte) : S-Q6m (Q6 tuned et mt), S-K9v (K9 tuned et
  mt), S-K8s (K8 naturel, temps et latences : site d'allocation distinct pour l'arbre longue durée), S-K8it (K8 tuned
  itératif), S-K5d (K5 tuned en f64), S-K1d (K1 soa en f64), S-mesures (toutes), S-cases (C1, E2, A1, A2, A7 = 1/2),
  S-tout.
Information : K5 tuned et K9 tuned, dont le code ne change pas, sous js_fix / js_ref (contrôle) ; Q1 tuned et naturel
sous Node.js 22 / Node.js 26 (js_n22 / js_ref, même source).
Les corrections publiées des autres langages (results/transfers.json : ratios, ratios_k9h, lat_ratios) sont appliquées
comme dans le calcul publié ; celles de JavaScript en sont retirées pour le calcul, puis le rapport de J-E y est écrit
(« ratios »). Le rapport de la réplication (« replication_ratios ») va dans results/js_check.json.
Sorties : results/js_check.json, results/report_js.md ; results/transfers.json (JavaScript).
Variables (essai) : JS_RAW, JS_TAG, JS_OUT (sorties ailleurs, transferts non écrits)."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

RAW = os.environ.get("JS_RAW", os.path.join(ROOT, "results", "raw_js"))
TAG = os.environ.get("JS_TAG", "js")
OUT = os.environ.get("JS_OUT", os.path.join(ROOT, "results"))
LANG = "js"
LIMIT = 0.25
LATCOLS = ["p50", "p90", "p99", "p99,9", "max"]
K7T = ("k7", "tuned", "")
Q6T, Q6M = ("k6", "tuned", "q6"), ("k6", "mt", "q6")
K9T, K9M = ("k9", "tuned", ""), ("k9", "mt", "")
K8T, K5T, K1S = ("k8", "tuned", ""), ("k5", "tuned", ""), ("k1", "soa", "energy")
Q1T, Q1N = ("k6", "tuned", "q1"), ("k6", "natural", "q1")
CORR = [K7T]
CONTROLS = [K5T, K9T]
SENS = {"q6_tuned_m": (Q6T, ("js_exp", ("k6", "tuned_m", "q6")), ("js_ref", Q6T)),
        "q6_mt_m": (Q6M, ("js_exp", ("k6", "mt_m", "q6")), ("js_ref", Q6M)),
        "k9_tuned_v": (K9T, ("js_exp", ("k9", "tuned_v", "")), ("js_ref", K9T)),
        "k9_mt_v": (K9M, ("js_exp", ("k9", "mt_v", "")), ("js_ref", K9M)),
        "k8_natural_s": (K8N, ("js_exp", ("k8", "natural_s", "")), ("js_ref", K8N)),
        "k8_tuned_it": (K8T, ("js_exp", ("k8", "tuned_it", "")), ("js_ref", K8T)),
        "k5_tuned_f64": (K5T, ("js_exp", ("k5", "tuned_f64", "")), ("js_ref", K5T)),
        "k1_soa_f64": (K1S, ("js_exp", ("k1", "soa_f64", "energy")), ("js_ref", K1S))}
PLAN = {"S-Q6m": ["q6_tuned_m", "q6_mt_m"], "S-K9v": ["k9_tuned_v", "k9_mt_v"], "S-K8s": ["k8_natural_s"],
        "S-K8it": ["k8_tuned_it"], "S-K5d": ["k5_tuned_f64"], "S-K1d": ["k1_soa_f64"], "S-mesures": list(SENS)}
LAT_SENS = "k8_natural_s"  # la sensibilité qui porte aussi les latences de K8 naturel
ERRATA = {"E1": 1, "A4": 0.5, "E6": 0.5}
BEFORE = {"E1": 0.5, "A4": 0, "E6": 0}
CASES = {"C1": 0.5, "E2": 0.5, "A1": 0.5, "A2": 0.5, "A7": 0.5}


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, lat, bad = defaultdict(dict), defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != TAG:
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            if r["kernel"] == "k8" and r.get("lat"):
                lat[r["lang"]].setdefault(key, []).append(r["lat"])
    return d, lat, bad


def gm(procs):
    return math.exp(proc_logs(procs).mean())


def lat_med(procs):
    """Estimateur de D3 : médiane, sur toutes les répétitions de tous les processus, de chaque colonne."""
    return np.median(np.vstack([np.asarray(p, float) for p in procs if len(p)]), axis=0)


def lat_ratio(new, old, rng, nb=2000):
    r = lat_med(new) / lat_med(old)
    bs = np.array([lat_med([new[i] for i in rng.integers(0, len(new), len(new))]) /
                   lat_med([old[i] for i in rng.integers(0, len(old), len(old))]) for _ in range(nb)])
    return {"ratio": r.tolist(), "ci_lo": np.quantile(bs, 0.025, axis=0).tolist(),
            "ci_hi": np.quantile(bs, 0.975, axis=0).tolist(), "old_us": (lat_med(old) / 1e3).tolist(),
            "new_us": (lat_med(new) / 1e3).tolist(), "n_new": len(new), "n_old": len(old)}


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
            "prec_j": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def scaled_lat(lat, r):
    out = {l: dict(v) for l, v in lat.items()}
    out[LANG][K8N] = v2.scale_lat(lat[LANG][K8N], r)
    return out


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de JavaScript remplacées le temps du calcul."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def published_data():
    """Données du calcul publié, sans les corrections de JavaScript : transferts des autres langages, K9 de la
    machine 16 (et les corrections de K9 des autres langages), latences de la machine 11 (et les corrections de latence
    des autres)."""
    data, lat, *_ = v2.dataset_main(transfers=False, k9h=None)
    tr = json.load(open(os.path.join(ROOT, "results", "transfers.json")))
    for lang, keys in tr["ratios"].items():
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    for lang, r in tr.get("lat_ratios", {}).items():
        if lang != LANG and K8N in lat.get(lang, {}):
            lat[lang][K8N] = v2.scale_lat(lat[lang][K8N], r)
    v2.apply_k9h(data, "common", skip=(LANG,))
    v2.align_lat(data, lat)
    return data, lat, tr


def main():
    m = v2.MATRIX[LANG]
    assert {c: m[c][0] for c in ERRATA} == ERRATA, "errata E1, A4, E6 absents de analysis/capabilities.py"
    data, lat, tr = published_data()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, rawlat, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 800)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_fix = {k: ratio(raw["js_fix"][k], raw["js_ref"][k], rng) for k in CORR + CONTROLS}
    r_sens = {n: ratio(raw[nc][nk], raw[bc][bk], rng) for n, (_, (nc, nk), (bc, bk)) in SENS.items()}
    r_n22 = {k: ratio(raw["js_n22"][k], raw["js_ref"][k], rng) for k in (Q1T, Q1N) if k in raw.get("js_n22", {})}
    l_s = lat_ratio(rawlat["js_exp"][("k8", "natural_s", "")], rawlat["js_ref"][K8N], rng)
    transfer = {}

    def bridged(label, key, r, new_procs):
        """Pont par le C du même hôte au-delà de 25 % d'écart, et règle de sens (information, scénario J-E-P)."""
        t_main = gm(data[LANG][key])
        trf = t_main * r
        if key not in raw.get("c", {}):  # sans témoin du même hôte (essai sur la validation) : transfert
            return r
        br = gm(data["c"][key]) * gm(new_procs) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        f = (br if use else trf) / t_main
        used = min(1.0, f) if r < 1 else max(1.0, f)
        transfer[label] = {"key": kk(key), "main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br,
                           "gap": gap, "bridge_used": use, "ratio": r, "factor": f, "factor_used": used,
                           "c_main_ms": 1e3 * gm(data["c"][key]), "c_here_ms": 1e3 * gm(raw["c"][key])}
        return used

    fix_t = {k: r_fix[k]["ratio"] for k in CORR}
    fix_b = {k: bridged(f"pont {kk(k)}", k, r_fix[k]["ratio"], raw["js_fix"][k]) for k in CORR}
    sens_t = {n: fix_t.get(key, 1.0) * min(1.0, r_sens[n]["ratio"]) for n, (key, _, _) in SENS.items()}
    lat_s = [min(1.0, x) for x in l_s["ratio"]]

    def with_sens(names):
        f = dict(fix_t)
        for n in names:
            f[SENS[n][0]] = sens_t[n]
        return f

    def lat_for(names):
        return scaled_lat(lat, lat_s) if LAT_SENS in names else lat

    plans = {"Avant": (data, lat, BEFORE), "J-code": (scaled(data, fix_t), lat, BEFORE), "J-M": (data, lat, None),
             "J-E": (scaled(data, fix_t), lat, None), "J-E-P": (scaled(data, fix_b), lat, None)}
    for name, names in PLAN.items():
        plans[name] = (scaled(data, with_sens(names)), lat_for(names), None)
    plans["S-cases"] = (scaled(data, fix_t), lat, CASES)
    plans["S-tout"] = (scaled(data, with_sens(PLAN["S-mesures"])), lat_for(PLAN["S-mesures"]), CASES)
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()}, "r_sens": r_sens,
           "r_n22": {kk(k): r for k, r in r_n22.items()}, "lat_s": l_s, "transfer": transfer,
           "published_ratios": {kk(k): v for k, v in fix_t.items()},
           "bridge_ratios": {kk(k): v for k, v in fix_b.items()}, "sens_factors": sens_t, "sens_lat": lat_s,
           "replication_ratios": {"|".join(k): v for k, v in fix_t.items()}, "scenarios": {}}
    for name, (d, lt, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : JavaScript {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "ocaml_check.json")))["scenarios"]["O-E"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(OUT, "js_check.json"), "w"), indent=1, default=float)
    report(out)
    if OUT != os.path.join(ROOT, "results"):
        return
    # classement publié (3.2) : rapport de J-E inscrit dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in fix_t.items()}
    note = " ; JavaScript : docs/JAVASCRIPT.md (3.2), results/raw_js, machine 21, results/js_check.json"
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(os.path.join(ROOT, "results", "transfers.json"), "w"), indent=1)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur JavaScript : rapports appariés et scénarios\n",
         "Plan : `docs/JAVASCRIPT.md`. Mesures : `results/raw_js/` (machine 21, 7 processus par cellule). Code :",
         "`analysis/js_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte) : js_fix / js_ref\n",
         "Clé corrigée (reportée) en gras ; les deux autres ont le même code dans les deux copies (contrôle).\n",
         "| Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|"]
    corr = {kk(k) for k in CORR}
    for k, r in o["r_fix"].items():
        b = "**" if k in corr else ""
        L.append(f"| {b}{k}{b} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {b}{f(r['ratio'], 3)}{b} | "
                 f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Sensibilités (forme nouvelle / js_ref, même hôte)\n",
          "| Sensibilité | Clé | Base (ms) | Forme nouvelle (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|---|"]
    for n, r in o["r_sens"].items():
        L.append(f"| {n} | {kk(SENS[n][0])} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                 f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    x = o["lat_s"]
    L += ["", "## Latences de K8 naturel (médianes de toutes les répétitions, µs) : natural_s / natural\n",
          "| | " + " | ".join(LATCOLS) + " |", "|---|" + "---|" * len(LATCOLS),
          "| natural (js_ref) | " + " | ".join(f(v, 0) for v in x["old_us"]) + " |",
          "| natural_s (js_exp) | " + " | ".join(f(v, 0) for v in x["new_us"]) + " |",
          "| rapport [IC 95 %] | " + " | ".join(f"{f(r, 3)} [{f(a, 2)}–{f(b, 2)}]"
                                              for r, a, b in zip(x["ratio"], x["ci_lo"], x["ci_hi"])) + " |"]
    if o["r_n22"]:
        L += ["", "## Information : Node.js 22.22.0 / Node.js 26.12.1 (même source, même hôte)\n",
              "| Clé | Node 26 (ms) | Node 22 (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|"]
        for k, r in o["r_n22"].items():
            L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Pont par le C de clang (information : scénario J-E-P ; le classement publié reporte par transfert)\n",
          "| Rapport | Clé | JavaScript publié | Transfert | Pont | Écart | Retenu | Facteur appliqué |",
          "|---|---|---|---|---|---|---|---|"]
    for lab, b in o["transfer"].items():
        L.append(f"| {lab} | {b['key']} | {f(b['main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} | {f(b['factor_used'], 3)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de JavaScript | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][14:21], start=14))
        L.append(f"**{name}** : {top}.\n")
    L.append("## Rapports reportés sur la réplication (machine 3)\n")
    L.append(", ".join(f"{k.replace('|', ':').rstrip(':')} {f(r, 3)}" for k, r in sorted(o["replication_ratios"].items()))
             + ".")
    open(os.path.join(OUT, "report_js.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
