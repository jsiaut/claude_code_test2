#!/usr/bin/env python3
"""Remarque sur Java (plan : docs/JAVA.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 17 (results/raw_java, étiquette « java »), reportés sur les données publiées de Java ;
analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario du plan (3.5) :
* Avant : le classement publié d'avant (F1 = 0, sans correction) ; doit reproduire results/k9_check.json (Publié).
* J-F1 : erratum F1 = 1/2 seul. J-K5, J-K5-T : correction de K5 tuned et K1 soa seule (règle du pont de
  analysis/transfer_check.py ; transfert seul). J-E (classement publié), J-E-T : erratum et correction.
* Sensibilités (sur J-E ; rapports pris dans java_exp, forme nouvelle / variante d'origine, appliqués en min(1, r)) :
  S-Q1, S-pool, S-K9v, S-K7, S-K8, S-mesures (toutes ; S-mesures-T par transfert seul), S-cases (B3 = F2 = 1/2),
  S-libc-J (D3 = D4 = 1), S-tout.
Les corrections publiées des autres langages (results/transfers.json) sont appliquées, puis K9 de la machine 16
(harnais commun), comme dans le calcul publié ; celles de Java en sont retirées pour le calcul, puis les rapports de
J-E y sont écrits. Sorties : results/java_check.json, results/report_java.md ; results/transfers.json (Java)."""
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

RAW = os.path.join(ROOT, "results", "raw_java")
LANG = "java"
LIMIT = 0.25
K5T, K5N = ("k5", "tuned", ""), ("k5", "natural", "")
K1S, K1N = ("k1", "soa", "energy"), ("k1", "natural", "energy")
Q6T, Q6M, Q1T, Q1M = ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q1")
K9T, K9M = ("k9", "tuned", ""), ("k9", "mt", "")
K7N, K7T, K8T = ("k7", "natural", ""), ("k7", "tuned", ""), ("k8", "tuned", "")
FIX = [K5T, K1S]
WITNESS = [K5N, K1N, Q6T]
# sensibilités : nom -> (clé publiée, clé de la forme nouvelle dans java_exp)
SENS = {"q1_tuned_1p": (Q1T, ("k6", "tuned_1p", "q1")), "q1_mt_1p": (Q1M, ("k6", "mt_1p", "q1")),
        "q1_mt_pool": (Q1M, ("k6", "mt_pool", "q1")), "q1_mt_pool_1p": (Q1M, ("k6", "mt_pool_1p", "q1")),
        "q6_mt_pool": (Q6M, ("k6", "mt_pool", "q6")), "k9_mt_pool": (K9M, ("k9", "mt_pool", "")),
        "k9_tuned_vec": (K9T, ("k9", "tuned_vec", "")), "k9_mt_pool_vec": (K9M, ("k9", "mt_pool_vec", "")),
        "k7_tuned_batch": (K7T, ("k7", "tuned_batch", "")), "k7_tuned_iso": (K7T, ("k7", "tuned_iso", "")),
        "k7_natural_iso": (K7N, ("k7", "natural_iso", "")), "k8_tuned_it": (K8T, ("k8", "tuned_it", ""))}
PLAN = {"S-Q1": ["q1_tuned_1p", "q1_mt_1p"], "S-pool": ["q6_mt_pool", "q1_mt_pool", "k9_mt_pool"],
        "S-K9v": ["k9_tuned_vec", "k9_mt_pool_vec"], "S-K7": ["k7_tuned_batch", "k7_natural_iso"],
        "S-K8": ["k8_tuned_it"],
        "S-mesures": ["q1_tuned_1p", "q1_mt_pool_1p", "q6_mt_pool", "k9_tuned_vec", "k9_mt_pool_vec", "k7_tuned_batch",
                      "k7_natural_iso", "k8_tuned_it"]}
ERRATA = {"F1": 0.5}
BEFORE = {"F1": 0}
CASES = {"B3": 0.5, "F2": 0.5}
LIBC = {"D3": 1, "D4": 1}


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "java":
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
            "prec_j": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de Java (règle v1, dont dérive la v2) remplacées le temps du calcul."""
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
    """Données du calcul publié, sans les corrections de Java : transferts des autres langages, puis K9 de la machine 16."""
    data, lat, *_ = v2.dataset_main(transfers=False, k9h=None)
    tr = json.load(open(os.path.join(ROOT, "results", "transfers.json")))
    for lang, keys in tr["ratios"].items():
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    v2.apply_k9h(data, "common")
    v2.align_lat(data, lat)
    return data, lat, tr


def main():
    m = v2.MATRIX[LANG]
    assert {c: m[c][0] for c in ERRATA} == ERRATA, "erratum F1 absent de analysis/capabilities.py"
    data, lat, tr = published_data()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 400)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_fix = {k: ratio(raw["java_fix"][k], raw["java_ref"][k], rng) for k in FIX + WITNESS}
    r_sens = {n: ratio(raw["java_exp"][new], raw["java_exp"][old], rng) for n, (old, new) in SENS.items()}
    transfer = {}

    def bridged(label, key, r, new_procs):
        t_main = gm(data[LANG][key])
        trf = t_main * r
        br = gm(data["c"][key]) * gm(new_procs) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        used = (br / t_main) if use else r
        transfer[label] = {"key": kk(key), "java_main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br,
                           "gap": gap, "bridge_used": use, "ratio": r, "ratio_used": used,
                           "c_main_ms": 1e3 * gm(data["c"][key]), "c_here_ms": 1e3 * gm(raw["c"][key])}
        return used

    fix_b = {k: bridged(f"correction {kk(k)}", k, r_fix[k]["ratio"], raw["java_fix"][k]) for k in FIX}
    fix_t = {k: r_fix[k]["ratio"] for k in FIX}
    sens_b = {n: min(1.0, bridged(n, old, r_sens[n]["ratio"], raw["java_exp"][new])) for n, (old, new) in SENS.items()}
    sens_t = {n: min(1.0, r_sens[n]["ratio"]) for n in SENS}

    def with_sens(names, base, s):
        f = dict(base)
        for n in names:
            f[SENS[n][0]] = f.get(SENS[n][0], 1.0) * s[n]
        return f

    plans = {"Avant": (data, BEFORE), "J-F1": (data, None),
             "J-K5": (scaled(data, fix_b), BEFORE), "J-K5-T": (scaled(data, fix_t), BEFORE),
             "J-E": (scaled(data, fix_b), None), "J-E-T": (scaled(data, fix_t), None)}
    for name, names in PLAN.items():
        plans[name] = (scaled(data, with_sens(names, fix_b, sens_b)), None)
    plans["S-mesures-T"] = (scaled(data, with_sens(PLAN["S-mesures"], fix_t, sens_t)), None)
    plans["S-cases"] = (scaled(data, fix_b), CASES)
    plans["S-libc-J"] = (scaled(data, fix_b), LIBC)
    plans["S-tout"] = (scaled(data, with_sens(PLAN["S-mesures"], fix_b, sens_b)), {**CASES, **LIBC})
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()}, "r_sens": r_sens,
           "sens_used": sens_b, "sens_transfer": sens_t, "transfer": transfer,
           "published_ratios": {kk(k): v for k, v in fix_b.items()}, "scenarios": {}}
    for name, (d, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, cells)
        print(f"{name} : Java {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, D {z['D'][LANG]:.1f}, "
              f"rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "k9_check.json")))["scenarios"]["Publié"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(ROOT, "results", "java_check.json"), "w"), indent=1, default=float)
    # classement publié (3.2) : rapports de J-E inscrits dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in fix_b.items()}
    note = " ; Java : docs/JAVA.md (3.2), results/raw_java, machine 17, results/java_check.json"
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(os.path.join(ROOT, "results", "transfers.json"), "w"), indent=1)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur Java : rapports appariés et scénarios\n",
         "Plan : `docs/JAVA.md`. Mesures : `results/raw_java/` (machine 17, 7 processus par cellule). Code :",
         "`analysis/java_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|---|"]
    for k, r in o["r_fix"].items():
        lab = "java_fix / java_ref" + (" (témoin)" if k in [kk(x) for x in WITNESS] else "")
        L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                 f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    for n, r in o["r_sens"].items():
        old, new = SENS[n]
        L.append(f"| java_exp : {new[1]} / {old[1]} | {kk(old)} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | "
                 f"{f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Report sur les données publiées (transfert ou pont par le C de clang)\n",
          "| Rapport | Clé | Java publié | Transfert | Pont | Écart | Retenu (min(1, r) pour les sensibilités) |",
          "|---|---|---|---|---|---|---|"]
    for lab, b in o["transfer"].items():
        used = b["ratio_used"] if lab.startswith("correction") else min(1.0, b["ratio_used"])
        L.append(f"| {lab} | {b['key']} | {f(b['java_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | "
                 f"{f(b['bridge_ms'], 2)} ms | {f(100 * b['gap'], 1)} % | "
                 f"{'pont' if b['bridge_used'] else 'transfert'} ({f(used, 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Java | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:16]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_java.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
