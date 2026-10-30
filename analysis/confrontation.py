#!/usr/bin/env python3
"""Confrontation avec le « Banc de sympathie mécanique » (plan : docs/CONFRONTATION.md, poussé avant ce code et avant
ses données nouvelles).

Test 1 : pilier C sous leur règle du standard (analysis/standard_rule.py).
Test 2 : plafond E sous leur restriction de code, par transfert des rapports appariés mesurés sur l'hôte actuel
         (results/raw_conf, tools/measure_conf.py).
Scénarios A (publié), B (C_R), C (E_R), D (C_R et E_R) : score de référence et rang espéré sur l'analyse globale de
la v3 (mêmes tirages, même graine), comparés à leur ordre sur les 18 langages communs.
Test 3 : leur S comme quatrième pilier. Test 4 : accord des deux grilles.
Sorties : results/confrontation.json, results/report_confrontation.md. Variables : BOOT (2000), UA (20000),
DRAWS3 (2000)."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
from analyze_v2 import E_V2, RANKED, ANNEX, ROOT, CATEGORIES, NAMES, c_cells, c_score, c_vector, ranks_of, dirichlet  # noqa: E402
from analyze_v3 import Arrays3, build_pools, needed_keys, references, scores3, MAIN, proc_logs  # noqa: E402
from banc_data import BANC_GRID, BANC_WEIGHTS, BANC_S, COMMON, BANC_EXT_TOP10, check  # noqa: E402
from standard_rule import R_OVERRIDES, c_cells_r  # noqa: E402
from measure_conf import KEYS as CONF_KEYS  # noqa: E402

B = int(os.environ.get("BOOT", "2000"))
U = int(os.environ.get("UA", "20000"))
DRAWS3 = int(os.environ.get("DRAWS3", "2000"))
RAW = os.path.join(ROOT, "results", "raw_conf")
L18 = list(COMMON)
K3KEYS = [("k3", "sw_padded", ""), ("k3", "rmw_padded", "")]
NO_THREADS = ("mojo", "fortran")  # pas de threads admissibles (plan, section 4.4)
SAME_CODE = {"c3": "macros publiques comp_* : code machine identique des noyaux K6 (rapport 1 par construction)"}
CLASSES = [0.0, 0.25, 0.5, 1.0]


# ------------------------------------------------------------------ données de la confrontation
def load_conf():
    conf, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "conf":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            conf[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return conf, bad


def paired_ratios(conf, data, rng, nb=2000):
    out = {}
    for lang, keys in CONF_KEYS.items():
        for key in keys:
            o, s = conf.get(lang, {}).get(key), conf.get(lang + "_std", {}).get(key)
            if not o or not s:
                out[(lang, key)] = None
                continue
            yo, ys = proc_logs(o), proc_logs(s)
            r = float(math.exp(ys.mean() - yo.mean()))
            bs = [math.exp(ys[rng.integers(0, len(ys), len(ys))].mean() - yo[rng.integers(0, len(yo), len(yo))].mean())
                  for _ in range(nb)]
            main = data.get(lang, {}).get(key)
            host = float(math.exp(yo.mean() - proc_logs(main).mean())) if main else None
            out[(lang, key)] = {"ratio": r, "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
                                "n_orig": len(yo), "n_std": len(ys), "orig_now_ms": 1e3 * math.exp(yo.mean()),
                                "std_now_ms": 1e3 * math.exp(ys.mean()), "host_vs_main": host}
    return out


def point(procs):
    return math.exp(proc_logs(procs).mean())


def rule_data(data, ratios):
    """Données principales sous leur restriction : rapports appariés transférés, repli à un thread et pénalité de K3."""
    dR = {l: {k: [list(p) for p in v] for k, v in d.items()} for l, d in data.items()}
    for (l, key), r in ratios.items():
        if r is not None:
            dR[l][key] = [[t * r["ratio"] for t in p] for p in data[l][key]]
    notes = {}
    for l in NO_THREADS:
        for mt, singles in ((("k6", "mt", "q6"), [("k6", "natural", "q6"), ("k6", "tuned", "q6")]),
                            (("k6", "mt", "q1"), [("k6", "natural", "q1"), ("k6", "tuned", "q1")]),
                            (("k9", "mt", ""), [("k9", "natural", ""), ("k9", "tuned", "")])):
            best = min(singles, key=lambda k: point(dR[l][k]))
            dR[l][mt] = [list(p) for p in dR[l][best]]
            notes[f"{l} {':'.join(mt)}"] = f"même travail sur un thread ({best[1]})"
    k3best = {l: min(point(dR[l][k]) for k in K3KEYS if k in dR[l]) for l in L18 if l not in NO_THREADS}
    worst = max(k3best, key=k3best.get)
    for l in NO_THREADS:
        for k in K3KEYS:
            dR[l][k] = [list(p) for p in dR[worst][k]]
        notes[f"{l} k3"] = f"pénalité : temps admissible le plus lent des 18 ({worst})"
    return dR, notes, worst


# ------------------------------------------------------------------ pilier C
def noisy_r(base, prng, noise=0.10):
    """Bruit de jugement des cellules sous leur règle : avec la probabilité noise, une classe voisine."""
    out = {}
    for l, cs in base.items():
        d = {}
        for cap, v in cs.items():
            if prng.random() < noise:
                i = CLASSES.index(v) if v in CLASSES else 2
                i = min(len(CLASSES) - 1, max(0, i + (1 if prng.random() < 0.5 else -1)))
                v = CLASSES[i]
            d[cap] = v
        out[l] = d
    return out


# ------------------------------------------------------------------ scénarios
def scenario(data, lat, langs, footprint, c3, crule, e_meas=None):
    """Rejoue l'analyse v3 (même graine, mêmes tirages) sur data, avec la règle crule : 'main' (v2/v1) ou 'R'.
    e_meas : mesures du plafond E (par défaut celles de la v3 ; docs/MOJO.md, scénario sans K4)."""
    rng = np.random.default_rng(v3.SEED)
    keys = sorted(needed_keys())
    pools = build_pools(data, langs, keys)
    A = Arrays3(data, lat, langs, B, rng, pools, e_meas=e_meas or E_V2)
    refs = {e: references(A, e) for e in ("mean", "min")}
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    base_r = c_cells_r(c3)
    C0 = c_vector(c_score(base_r if crule == "R" else c_cells("v2", c3), catw0), langs)
    S0 = scores3(A, 0, MAIN, C0, footprint, refs)
    ms_boot = np.empty((B, len(langs)))
    for b in range(1, B + 1):
        ms_boot[b - 1] = scores3(A, b, MAIN, C0, footprint, refs)["MS"]
    opts = {"est": ["mean", "min"], "enorm": ["frontier", "bounds"], "d3": ["abs", "rel"], "d4": ["best", "c"],
            "d1ref": ["tstar", "best_natural"], "agg": ["arith", "geo"], "crule": ["v2", "v1"]}
    kernels, cat_names = list(A.e_meas), list(CATEGORIES)
    rk = A.ranked
    NR = len(RANKED)
    prec = np.zeros((NR, NR))
    first = np.zeros(NR)
    ranks = np.empty((U, NR), np.int16)
    for u in range(U):
        cfg = {k: v[int(rng.integers(len(v)))] for k, v in opts.items()}
        b = int(rng.integers(1, B + 1))
        wp = dirichlet(rng, 20 * np.array([0.35, 0.40, 0.25])) if rng.random() < 0.5 else dirichlet(rng, [1, 1, 1])
        wP = {"C": wp[0], "E": wp[1], "D": wp[2]}
        wE = dict(zip(kernels, dirichlet(rng, 20 * np.full(len(kernels), 1 / len(kernels)))))
        wD = dict(zip(("D1", "D2", "D3", "D4"), dirichlet(rng, 20 * np.array([v3.DW[k] for k in ("D1", "D2", "D3", "D4")]))))
        catw = dict(zip(cat_names, dirichlet(rng, 20 * np.array([catw0[c] for c in cat_names]))))
        prng = np.random.default_rng(int(rng.integers(2 ** 63)))
        if crule == "R":
            C = c_vector(c_score(noisy_r(base_r, prng), catw), langs)
        else:
            C = c_vector(c_score(c_cells(cfg["crule"], c3, rng=prng, noise=0.10), catw), langs)
        S_u = scores3(A, b, cfg, C, footprint, refs, wE=wE, wD=wD, wP=wP)
        r_ = ranks_of(S_u["MS"][rk])
        prec += r_[:, None] < r_[None, :]
        first[int(np.argmin(r_))] += 1
        ranks[u] = r_
    prec /= U
    idx = {l: RANKED.index(l) for l in L18}
    exp18 = {a: 1 + sum(prec[idx[b], idx[a]] for b in L18 if b != a) for a in L18}
    ms0 = {l: float(S0["MS"][A.idx[l]]) for l in langs}
    order18 = sorted(L18, key=lambda l: (exp18[l], -ms0[l]))
    exp21 = {a: 1 + sum(prec[RANKED.index(b), RANKED.index(a)] for b in RANKED if b != a) for a in RANKED}
    tstar_src = {}
    for k, ms in A.e_meas.items():
        for i, ks in enumerate(ms):
            t = A.best("mean", ks, 0)
            j = int(np.nanargmin(np.where(np.isin(np.arange(len(langs)), rk), t, np.nan)))
            tstar_src[f"{k}#{i}"] = langs[j]
    return {"A": A, "refs": refs, "S0": S0, "C0": C0, "ms_boot": ms_boot, "ms0": ms0, "exp18": exp18,
            "order18": order18, "exp21": exp21, "prec": prec, "tstar_src": tstar_src,
            "first": {RANKED[j]: float(first[j] / U) for j in range(NR)},
            "rank90": {RANKED[j]: [int(np.quantile(ranks[:, j], 0.05)), int(np.quantile(ranks[:, j], 0.95))]
                       for j in range(NR)},
            "E": {l: float(S0["E"][A.idx[l]]) for l in langs}, "D": {l: float(S0["D"][A.idx[l]]) for l in langs},
            "C": {l: float(C0[A.idx[l]]) for l in langs}, "Ek": {l: {k: float(S0["Ek"][k][A.idx[l]]) for k in S0["Ek"]}
                                                                  for l in langs}}


# ------------------------------------------------------------------ comparaisons
def avg_ranks(values, higher_better=True):
    """Rangs moyens (ex aequo partagés), 1 = meilleur."""
    ls = list(values)
    v = np.array([values[l] for l in ls], float) * (1 if higher_better else -1)
    order = np.argsort(-v, kind="stable")
    r = np.empty(len(ls))
    i = 0
    while i < len(ls):
        j = i
        while j + 1 < len(ls) and v[order[j + 1]] == v[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return {l: float(r[k]) for k, l in enumerate(ls)}


def kendall(r1, r2, ls):
    c = d = 0
    for i, a in enumerate(ls):
        for b in ls[i + 1:]:
            s = np.sign(r1[a] - r1[b]) * np.sign(r2[a] - r2[b])
            c += s > 0
            d += s < 0
    return (c - d) / (len(ls) * (len(ls) - 1) / 2)


def compare(order18, banc_rank):
    mine = {l: i + 1 for i, l in enumerate(order18)}
    rho = float(np.corrcoef([mine[l] for l in L18], [banc_rank[l] for l in L18])[0, 1])
    d2 = {l: (mine[l] - banc_rank[l]) ** 2 for l in L18}
    tot = sum(d2.values())
    return {"rank": mine, "spearman": rho, "kendall": float(kendall(mine, banc_rank, L18)), "sum_d2": tot,
            "share": {l: d2[l] / tot for l in L18}}


# ------------------------------------------------------------------ test 3
def banc_draw(rng):
    w = dirichlet(rng, 20 * BANC_WEIGHTS / BANC_WEIGHTS.sum())
    out = {}
    for l in L18:
        g = np.array(BANC_GRID[l], float)
        flip = rng.random(len(g)) < 0.10
        step = np.where(rng.random(len(g)) < 0.5, -1.0, 1.0)
        g = np.clip(g + flip * step, 0, 4)
        out[l] = float(np.dot(w, g) / 4 * 100)
    return out


def test3(scA, banc_rank):
    rng = np.random.default_rng(v3.SEED + 30)
    A = scA["A"]
    ms0 = scA["ms0"]
    msb = scA["ms_boot"]
    draws = [(msb[(d % B)], banc_draw(rng)) for d in range(DRAWS3)]
    mine_order = {l: r for r, l in enumerate(sorted(L18, key=lambda l: -ms0[l]), 1)}
    rows, thr = [], {"p_c_first_below_half": None, "closer_to_theirs": None, "rho_theirs_095": None}
    for w in [round(0.05 * i, 2) for i in range(21)]:
        comb0 = {l: (1 - w) * ms0[l] + w * BANC_S[l] for l in L18}
        rk = avg_ranks(comb0)
        rho_t = float(np.corrcoef([rk[l] for l in L18], [banc_rank[l] for l in L18])[0, 1])
        rho_m = float(np.corrcoef([rk[l] for l in L18], [mine_order[l] for l in L18])[0, 1])
        first = 0
        for msr, sd in draws:
            comb = {l: (1 - w) * msr[A.idx[l]] + w * sd[l] for l in L18}
            first += max(comb, key=comb.get) == "c"
        pc = first / len(draws)
        top = sorted(L18, key=lambda l: -comb0[l])[:5]
        rows.append({"w": w, "rho_theirs": rho_t, "rho_mine": rho_m, "p_c_first": pc, "top5": top,
                     "rank_c": rk["c"], "rank_zig": rk["zig"]})
        if thr["p_c_first_below_half"] is None and pc < 0.5:
            thr["p_c_first_below_half"] = w
        if thr["closer_to_theirs"] is None and rho_t > rho_m:
            thr["closer_to_theirs"] = w
        if thr["rho_theirs_095"] is None and rho_t >= 0.95:
            thr["rho_theirs_095"] = w
    return {"rows": rows, "thresholds": thr}


# ------------------------------------------------------------------ test 4
MAPPING = {0: ["A1", "F1"], 1: ["A2", "A3", "A4", "A5", "A7", "A8"], 2: ["A6"], 3: ["D3"], 4: ["D2", "D5"],
           6: ["B1", "B2", "B3", "B4"], 7: ["C1", "C2", "C4"], 8: ["E3"], 9: ["E4"], 10: ["E1", "E2", "E5", "E6"],
           11: ["C5", "D1", "D4", "F2"]}  # indice du principe (0 = P1) -> mes capacités
SINGLE = [2, 3, 8, 9]


def test4(c3):
    from banc_data import PRINCIPLES
    cv2, cR = c_cells("v2", c3), c_cells_r(c3)
    per = {}
    for p, caps in MAPPING.items():
        theirs = [BANC_GRID[l][p] for l in L18]
        res = {}
        for name, cells in (("v2", cv2), ("R", cR)):
            mine = [float(np.mean([cells[l][c] for c in caps])) for l in L18]
            rho, _ = v2.spearman(theirs, mine)
            res[name] = rho
        per[PRINCIPLES[p]] = {"caps": caps, "rho_v2": res["v2"], "rho_R": res["R"]}
    wsum = sum(BANC_WEIGHTS[p] for p in MAPPING)
    overall = {}
    theirs_s = [sum(BANC_WEIGHTS[p] * BANC_GRID[l][p] / 4 for p in MAPPING) / wsum for l in L18]
    for name, cells in (("v2", cv2), ("R", cR)):
        mine = [sum(BANC_WEIGHTS[p] * np.mean([cells[l][c] for c in caps]) for p, caps in MAPPING.items()) / wsum
                for l in L18]
        overall[name] = v2.spearman(theirs_s, mine)[0]
    dis, single_ok, single_n = [], 0, 0
    for p, caps in MAPPING.items():
        for l in L18:
            mine = float(np.mean([cR[l][c] for c in caps]))
            diff = BANC_GRID[l][p] / 4 - mine
            if p in SINGLE:
                single_n += 1
                single_ok += abs(diff) < 0.5
            if abs(diff) >= 0.5:
                dis.append({"principle": PRINCIPLES[p], "lang": l, "theirs": BANC_GRID[l][p], "mine_R": mine,
                            "caps": caps, "cells": {c: cR[l][c] for c in caps}})
    return {"per_principle": per, "overall": overall, "disagreements": dis,
            "single_agree_share": single_ok / single_n, "single_n": single_n}


# ------------------------------------------------------------------ principal
def main():
    check()
    data, lat, *_ = v2.dataset_main()
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    conf, bad = load_conf()
    ratios = paired_ratios(conf, data, np.random.default_rng(v3.SEED + 20))
    dR, notes, k3worst = rule_data(data, ratios)
    banc_rank = avg_ranks(BANC_S)
    sc = {}
    for name, d, crule in (("A", data, "main"), ("B", data, "R"), ("C", dR, "main"), ("D", dR, "R")):
        sc[name] = scenario(d, lat, langs, footprint, c3, crule)
        print(f"scénario {name} calculé", flush=True)
    # sensibilité : K3 retiré du plafond de Mojo et de Fortran (configuration de référence, scénarios C et D)
    sens = {}
    for name in ("C", "D"):
        s = sc[name]
        ms = dict(s["ms0"])
        for l in NO_THREADS:
            ek = [math.log(v) for k, v in s["Ek"][l].items() if k != "k3"]
            e = 100 * math.exp(np.mean(ek))
            ms[l] = ms[l] + v3.WEIGHTS["E"] * (e - s["E"][l])
        order = sorted(L18, key=lambda l: -ms[l])
        sens[name] = compare(order, banc_rank)
    out = {"bad_conf": bad, "ratios": {f"{l}|{':'.join(k)}": v for (l, k), v in ratios.items()}, "rule_notes": notes,
           "k3_worst": k3worst, "same_code": SAME_CODE, "banc_rank18": banc_rank, "scenarios": {}, "k3_dropped": sens}
    for name, s in sc.items():
        cmp_ = compare(s["order18"], banc_rank)
        cmp_ref = compare(sorted(L18, key=lambda l: -s["ms0"][l]), banc_rank)
        out["scenarios"][name] = {"order18": s["order18"], "exp18": s["exp18"], "ms0": {l: s["ms0"][l] for l in L18},
                                  "E": {l: s["E"][l] for l in L18}, "C": {l: s["C"][l] for l in L18},
                                  "D": {l: s["D"][l] for l in L18}, "Ek": {l: s["Ek"][l] for l in L18},
                                  "cmp": cmp_, "cmp_ref": cmp_ref, "tstar_src": s["tstar_src"],
                                  "exp21": s["exp21"]}
    out["test3"] = test3(sc["A"], banc_rank)
    out["test4"] = test4(c3)
    json.dump(out, open(os.path.join(ROOT, "results", "confrontation.json"), "w"), indent=1, default=float)
    report(out)


def f(x, d=2):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    S = o["scenarios"]
    L = ["# Confrontation avec le « Banc de sympathie mécanique » : résultats\n",
         "Plan : `docs/CONFRONTATION.md`. Calcul : `analysis/confrontation.py`. Rangs sur les 18 langages communs.\n"]
    L.append("## Test 2 : rapports appariés (réécriture standard / origine, même hôte)\n")
    L.append("| Langage | Mesure | Origine (ms) | Standard (ms) | Rapport [IC 95 %] | Hôte / données principales |")
    L.append("|---|---|---|---|---|---|")
    for k, v in o["ratios"].items():
        l, key = k.split("|")
        if v is None:
            L.append(f"| {NAMES.get(l, l)} | {key} | — | — | non mesuré | — |")
            continue
        L.append(f"| {NAMES.get(l, l)} | {key} | {f(v['orig_now_ms'])} | {f(v['std_now_ms'])} | {f(v['ratio'])} "
                 f"[{f(v['ci'][0])}–{f(v['ci'][1])}] | {f(v['host_vs_main'])} |")
    L.append("\nReplis et pénalités : " + " ; ".join(f"{k} : {v}" for k, v in o["rule_notes"].items()) + ".\n")
    if o["bad_conf"]:
        L.append(f"Processus écartés (somme de contrôle ou code de retour) : {len(o['bad_conf'])}.\n")
    L.append("## Scénarios\n")
    L.append("| Langage | Leur rang | A publié | B (C_R) | C (E_R) | D (C_R + E_R) | C A→R | E A→R |")
    L.append("|---|---|---|---|---|---|---|---|")
    for l in sorted(L18, key=lambda l: S["A"]["cmp"]["rank"][l]):
        L.append(f"| {NAMES[l]} | {f(o['banc_rank18'][l], 1)} | {S['A']['cmp']['rank'][l]} | {S['B']['cmp']['rank'][l]} | "
                 f"{S['C']['cmp']['rank'][l]} | {S['D']['cmp']['rank'][l]} | {f(S['A']['C'][l], 1)} → {f(S['D']['C'][l], 1)} | "
                 f"{f(S['A']['E'][l], 1)} → {f(S['D']['E'][l], 1)} |")
    L.append("")
    L.append("| Scénario | Spearman | Kendall | Σd² | part de C | rang de C |")
    L.append("|---|---|---|---|---|---|")
    for name in "ABCD":
        c = S[name]["cmp"]
        L.append(f"| {name} | {f(c['spearman'])} | {f(c['kendall'])} | {f(c['sum_d2'], 1)} | {f(100 * c['share']['c'], 0)} % | "
                 f"{c['rank']['c']} |")
    for name, c in o["k3_dropped"].items():
        L.append(f"\nSensibilité (K3 retiré du plafond de Mojo et de Fortran, configuration de référence), scénario {name} : "
                 f"Spearman {f(c['spearman'])}, rang de C {c['rank']['c']}.")
    t3 = o["test3"]
    L.append("\n## Test 3 : leur S comme quatrième pilier\n")
    L.append("| w | Spearman avec leur ordre | avec mon score de référence | P(C premier) | rang de C | 5 premiers |")
    L.append("|---|---|---|---|---|---|")
    for r in t3["rows"]:
        L.append(f"| {f(r['w'])} | {f(r['rho_theirs'])} | {f(r['rho_mine'])} | {f(r['p_c_first'])} | {f(r['rank_c'], 1)} | "
                 f"{', '.join(NAMES[x] for x in r['top5'])} |")
    th = t3["thresholds"]
    L.append(f"\nSeuils : P(C premier) < 0,5 à partir de w = {f(th['p_c_first_below_half'])} ; ordre plus proche du leur à "
             f"partir de w = {f(th['closer_to_theirs'])} ; Spearman avec leur ordre ≥ 0,95 à partir de w = "
             f"{f(th['rho_theirs_095'])}.")
    t4 = o["test4"]
    L.append("\n## Test 4 : accord des deux grilles\n")
    L.append("| Leur principe | Mes capacités | Spearman (mes notes v2) | Spearman (sous leur règle) |")
    L.append("|---|---|---|---|")
    for p, v in t4["per_principle"].items():
        L.append(f"| {p} | {', '.join(v['caps'])} | {f(v['rho_v2'])} | {f(v['rho_R'])} |")
    L.append(f"\nAccord d'ensemble (11 principes communs, leurs poids) : {f(t4['overall']['v2'])} avec mes notes v2, "
             f"{f(t4['overall']['R'])} sous leur règle. Correspondances à une capacité : {f(100 * t4['single_agree_share'], 0)} % "
             f"des {t4['single_n']} cellules diffèrent de moins de 0,5.\n")
    L.append("Désaccords (|leur niveau / 4 − ma note sous leur règle| ≥ 0,5) :\n")
    for d in t4["disagreements"]:
        L.append(f"* {d['principle']}, {NAMES[d['lang']]} : eux {d['theirs']}/4, moi {f(d['mine_R'])} "
                 f"({', '.join(f'{c} {f(v)}' for c, v in d['cells'].items())})")
    text = "\n".join(L) + "\n"
    open(os.path.join(ROOT, "results", "report_confrontation.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
