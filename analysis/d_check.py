#!/usr/bin/env python3
"""Remarque sur D (plan : docs/DLANG.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 10 (results/raw_d, étiquette « d »), reportés sur les données principales de D ;
analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario :
* Avant : le classement publié avant la remarque (E3 et E4 de D à 0,5 en règle v1, Q1 de la campagne).
* D-E : errata E3 = E4 = 1 en règle v1. D-Q1, D-Q1-T : Q1 corrigé (règle du pont de analysis/transfer_check.py ;
  transfert seul), sans les errata.
* D-EQ (classement publié) : errata et Q1 corrigé (règle du pont) ; D-EQ-T : errata et Q1 par transfert seul.
* S-512 : D-EQ, et K6 tuned et mt Q6 et Q1, K4 sans branchement, K1 aos × min(1, r(d_512 / d_fix)) (transfert).
* S-nat : D-EQ, et K9 naturel × r(d_nat / d_ref) (règle du pont).
* S-L22 (information) : D-EQ, et les 24 autres clés × r(d_l22 / d_ref) (transfert ; Q1 garde sa correction).
* S-tout : D-EQ + S-512 + S-nat.
* S-nat-T et S-tout-T (écart au plan, décidé après avoir vu les données) : K9 naturel par transfert seul.
Information : latence de K8 naturel avec --DRT-gcopt=fork:1 (d_gc / d_ref).
Les corrections publiées des autres langages (results/transfers.json) sont appliquées ; celles de D en sont retirées
pour le calcul, puis les rapports de Q1 de D-EQ y sont écrits.
Sorties : results/d_check.json, results/report_d.md ; results/transfers.json (rapports de D)."""
import glob, json, math, os, statistics, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_d")
LANG = "d"
LIMIT = 0.25
ALL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
       ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
       ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""),
       ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), ("k5", "tuned", ""), ("k6", "natural", "q6"),
       ("k6", "tuned", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"),
       ("k7", "natural", ""), ("k7", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", ""), ("k9", "natural", ""),
       ("k9", "tuned", ""), ("k9", "mt", "")]
Q1T, Q1M, Q1N = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k6", "natural", "q1")
Q6T, Q6M, K4B, K1A = ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k4", "branchless_unsorted", ""), ("k1", "aos", "energy")
K9N, K9T, K5T, K8N = ("k9", "natural", ""), ("k9", "tuned", ""), ("k5", "tuned", ""), ("k8", "natural", "")
FIX = [Q1T, Q1M]
CONTROLS = [Q1N, Q6T, K9T, K5T, Q6M, K4B, K1A]
K512 = [Q6T, Q6M, Q1T, Q1M, K4B, K1A]
ERRATA = {"E3": 1, "E4": 1}
BEFORE = {"E3": 0.5, "E4": 0.5}


def kk(k):
    return ":".join(x for x in k if x)


# Une compilation de sonde (probes/d) a tourné pendant la première passe, de 15:02:36 à 15:02:46 environ (docs/DLANG.md,
# section 4) : les processus dont la durée recoupe cette fenêtre sont écartés, règle fixée avant de voir les résultats.
PROBE_WINDOW = ("2026-10-31T15:02:36", "2026-10-31T15:02:46")


def overlaps_probe(r):
    from datetime import datetime, timedelta
    end = datetime.fromisoformat(r["ts"]) + timedelta(seconds=1)  # horodatage à la seconde : marge d'une seconde
    start = end - timedelta(seconds=r["wall"] + 1)
    lo, hi = (datetime.fromisoformat(x) for x in PROBE_WINDOW)
    return start <= hi and end >= lo


def load_raw():
    d, bad, lat = defaultdict(dict), [], defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "d":
                continue
            if overlaps_probe(r):
                bad.append((r["lang"], (r["kernel"], r["variant"], r["param"]), "sonde concurrente"))
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            if r.get("lat"):
                lat[r["lang"]].setdefault(key, []).extend(r["lat"])
    return d, bad, lat


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
            "prec_d": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de D (règle v1) remplacées le temps du calcul ; la matrice est restaurée ensuite."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def lat_stats(rows):
    """Médianes, sur les répétitions, de p50, p99,9 et du maximum (ns)."""
    return {"p50": statistics.median(r[0] for r in rows), "p999": statistics.median(r[3] for r in rows),
            "max": statistics.median(r[4] for r in rows)}


def main():
    m = v2.MATRIX[LANG]
    assert {c: m[c][0] for c in ERRATA} == ERRATA, "errata E3 et E4 absents de analysis/capabilities.py"
    data, lat, *_ = v2.dataset_main(transfers=False)
    tpath = os.path.join(ROOT, "results", "transfers.json")
    tr = json.load(open(tpath))
    for lang, keys in tr["ratios"].items():  # corrections publiées des autres langages, sans celles de D
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad, rlat = load_raw()
    rng = np.random.default_rng(v3.SEED + 100)
    R = lambda new, old, k: ratio(raw[new][k], raw[old][k], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_fix = {k: R("d_fix", "d_ref", k) for k in FIX + CONTROLS}
    r_512 = {k: R("d_512", "d_fix", k) for k in K512}
    r_nat = {k: R("d_nat", "d_ref", k) for k in (K9N, K9T)}
    r_l22 = {k: R("d_l22", "d_ref", k) for k in ALL}
    yl = [(proc_logs(raw["d_l22"][k]).mean() - proc_logs(raw["d_ref"][k]).mean()) for k in ALL]
    l22_gm = math.exp(float(np.mean(yl)))
    gc = {"d_ref": lat_stats(rlat["d_ref"][K8N]), "d_gc": lat_stats(rlat["d_gc"][K8N]),
          "time_ratio": R("d_gc", "d_ref", K8N)}
    transfer = {}

    def bridged(key, r, new_impl):
        t_main = gm(data[LANG][key])
        trf = t_main * r
        br = gm(data["c"][key]) * gm(raw[new_impl][key]) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        used = (br / t_main) if use else r
        transfer[kk(key)] = {"d_main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br, "gap": gap,
                             "bridge_used": use, "ratio": r, "ratio_used": used, "c_main_ms": 1e3 * gm(data["c"][key])}
        return used

    q1_b = {k: bridged(k, r_fix[k]["ratio"], "d_fix") for k in FIX}
    q1_t = {k: r_fix[k]["ratio"] for k in FIX}
    nat_b = {K9N: bridged(K9N, r_nat[K9N]["ratio"], "d_nat")}
    s512 = dict(q1_b)
    for k in K512:
        s512[k] = s512.get(k, 1.0) * min(1.0, r_512[k]["ratio"])
    l22 = {k: r_l22[k]["ratio"] for k in ALL if k not in FIX}
    l22.update(q1_b)
    plans = {"Avant": (data, BEFORE), "D-E": (data, None), "D-Q1": (scaled(data, q1_b), BEFORE),
             "D-Q1-T": (scaled(data, q1_t), BEFORE), "D-EQ": (scaled(data, q1_b), None),
             "D-EQ-T": (scaled(data, q1_t), None), "S-512": (scaled(data, s512), None),
             "S-nat": (scaled(data, {**q1_b, **nat_b}), None), "S-L22": (scaled(data, l22), None),
             "S-tout": (scaled(data, {**s512, **nat_b}), None),
             # écart au plan (décidé après avoir vu le pont de K9 naturel, qui se trompe entre Emerald Rapids et Cascade
             # Lake comme pour Chapel) : K9 naturel par transfert seul
             "S-nat-T": (scaled(data, {**q1_b, K9N: r_nat[K9N]["ratio"]}), None),
             "S-tout-T": (scaled(data, {**s512, K9N: r_nat[K9N]["ratio"]}), None)}
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()},
           "r_512": {kk(k): r for k, r in r_512.items()}, "r_nat": {kk(k): r for k, r in r_nat.items()},
           "r_l22": {kk(k): r for k, r in r_l22.items()}, "l22_gm": l22_gm, "gc": gc, "transfer": transfer,
           "published_ratios": {kk(k): v for k, v in q1_b.items()}, "scenarios": {}}
    for name, (d, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, cells)
        print(f"{name} : D {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, D {z['D'][LANG]:.1f}, "
              f"rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "d_check.json"), "w"), indent=1, default=float)
    # classement publié (décision 1) : rapports de Q1 de D-EQ inscrits dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in q1_b.items()}
    note = " ; D : docs/DLANG.md (3.2), results/raw_d, machine 10, results/d_check.json"
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(tpath, "w"), indent=1)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur D : rapports appariés et scénarios\n",
         "Plan : `docs/DLANG.md`. Mesures : `results/raw_d/` (machine 10, 7 processus par cellule). Code :",
         "`analysis/d_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         "## Rapports appariés\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|---|"]
    for lab, dd in (("d_fix / d_ref", o["r_fix"]), ("d_512 / d_fix", o["r_512"]), ("d_nat / d_ref", o["r_nat"]),
                    ("d_l22 / d_ref", o["r_l22"])):
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    g = o["gc"]
    L += ["", f"LLVM 22.1.8 / 21.1.8 (moyenne géométrique des 26 clés) : {f(o['l22_gm'], 3)}.\n",
          f"K8 naturel, latences (médianes des répétitions) : défaut p99,9 {f(g['d_ref']['p999'] / 1e6, 2)} ms, max "
          f"{f(g['d_ref']['max'] / 1e6, 1)} ms ; `--DRT-gcopt=fork:1` p99,9 {f(g['d_gc']['p999'] / 1e6, 2)} ms, max "
          f"{f(g['d_gc']['max'] / 1e6, 1)} ms ; temps total × {f(g['time_ratio']['ratio'], 2)}.\n",
          "## Report sur les données principales (transfert ou pont par le C de clang)\n",
          "| Clé | D (données principales) | Transfert | Pont | Écart | Retenu |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        L.append(f"| {k} | {f(b['d_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de D | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |", "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_d.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
