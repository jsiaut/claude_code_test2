#!/usr/bin/env python3
"""Remarque sur Go (plan : docs/GO.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 18 (results/raw_go, étiquette « go »), reportés sur les données publiées de Go ;
analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario du plan (3.5) :
* Avant : le classement publié d'avant ; doit reproduire results/java_check.json (J-E).
* G-K5, G-K5-T : clés archsimd (K5 tuned, K1 soa, Q6 tuned et mt) × r(go_fix / go_ref), règle du pont de
  analysis/transfer_check.py, rapport retenu plafonné à 1 (transfert seul).
* G-pre, G-pre-T : clés publiées depuis Emerald Rapids sans archsimd (K5 naturel ; K9 naturel, tuned et mt) ×
  r(go_noexp / go_ref), même règle, sans plafond (transfert seul).
* G-E (classement publié), G-E-T : les deux.
* Sensibilités (sur G-E, en min(1, r) par rapport à G-E) : S-K5r, S-K9v, S-Q1, S-K8, S-mesures (S-mesures-T).
Les corrections publiées des autres langages (results/transfers.json) sont appliquées, puis K9 de la machine 16, comme
dans le calcul publié ; celles de Go en sont retirées pour le calcul, puis les rapports de G-E y sont écrits (« ratios »
pour K5, K1 et K6 ; « ratios_k9h » pour K9). Les rapports de la réplication (« replication_ratios ») vont dans
results/go_check.json. Sorties : results/go_check.json, results/report_go.md ; results/transfers.json (Go)."""
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

RAW = os.path.join(ROOT, "results", "raw_go")
LANG = "go"
LIMIT = 0.25
K5T, K5N = ("k5", "tuned", ""), ("k5", "natural", "")
K1S = ("k1", "soa", "energy")
Q6T, Q6M, Q1T, Q1M = ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q1")
K9N, K9T, K9M, K8T = ("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", ""), ("k8", "tuned", "")
ARCHSIMD = [K5T, K1S, Q6T, Q6M]
EMR_KEYS = [K5N, K9N, K9T, K9M]
K9_KEYS = [K9N, K9T, K9M]
# sensibilités : nom -> (clé publiée, (copie, clé) de la forme nouvelle, (copie, clé) de la base, même hôte)
SENS = {"k5_tuned_r": (K5T, ("go_exp", ("k5", "tuned_r", "")), ("go_exp", K5T)),
        "k9_tuned_vec": (K9T, ("go_exp", ("k9", "tuned_vec", "")), ("go_noexp", K9T)),
        "k9_mt_vec": (K9M, ("go_exp", ("k9", "mt_vec", "")), ("go_noexp", K9M)),
        "q1_tuned_1p": (Q1T, ("go_exp", ("k6", "tuned_1p", "q1")), ("go_noexp", Q1T)),
        "q1_mt_1p": (Q1M, ("go_exp", ("k6", "mt_1p", "q1")), ("go_noexp", Q1M)),
        "k8_tuned_it": (K8T, ("go_noexp", ("k8", "tuned_it", "")), ("go_noexp", K8T))}
PLAN = {"S-K5r": ["k5_tuned_r"], "S-K9v": ["k9_tuned_vec", "k9_mt_vec"], "S-Q1": ["q1_tuned_1p", "q1_mt_1p"],
        "S-K8": ["k8_tuned_it"], "S-mesures": list(SENS)}


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "go":
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
            "prec_g": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def published_data():
    """Données du calcul publié, sans les corrections de Go : transferts des autres langages, puis K9 de la machine 16
    (et les corrections de K9 des autres langages)."""
    data, lat, *_ = v2.dataset_main(transfers=False, k9h=None)
    tr = json.load(open(os.path.join(ROOT, "results", "transfers.json")))
    for lang, keys in tr["ratios"].items():
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    v2.apply_k9h(data, "common", skip=(LANG,))
    v2.align_lat(data, lat)
    return data, lat, tr


def main():
    data, lat, tr = published_data()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 500)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_fix = {k: ratio(raw["go_fix"][k], raw["go_ref"][k], rng) for k in ARCHSIMD}
    noexp_keys = [k for k in raw["go_ref"] if k not in ARCHSIMD and k in raw["go_noexp"]]
    r_pre = {k: ratio(raw["go_noexp"][k], raw["go_ref"][k], rng) for k in sorted(noexp_keys)}
    r_nopre = {k: ratio(raw["go_nopre"][k], raw["go_ref"][k], rng) for k in raw.get("go_nopre", {})}
    r_sens = {n: ratio(raw[nc][nk], raw[bc][bk], rng) for n, (_, (nc, nk), (bc, bk)) in SENS.items()}
    transfer = {}

    def bridged(label, key, base, r, new_procs, cap):
        """Facteur appliqué au temps publié : transfert (temps de G-E × r) ou pont par le C du même hôte au-delà de 25 %
        d'écart ; cap : plafond du facteur (1 pour une correction de code, base pour une sensibilité, None sinon)."""
        t_main = gm(data[LANG][key])
        trf = t_main * base * r
        br = gm(data["c"][key]) * gm(new_procs) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        f = (br if use else trf) / t_main
        used = f if cap is None else min(cap, f)
        transfer[label] = {"key": kk(key), "go_main_ms": 1e3 * t_main, "base": base, "transfer_ms": 1e3 * trf,
                           "bridge_ms": 1e3 * br, "gap": gap, "bridge_used": use, "ratio": r, "factor": f,
                           "factor_used": used, "c_main_ms": 1e3 * gm(data["c"][key]),
                           "c_here_ms": 1e3 * gm(raw["c"][key])}
        return used

    k5_b = {k: bridged(f"correction {kk(k)}", k, 1.0, r_fix[k]["ratio"], raw["go_fix"][k], 1.0) for k in ARCHSIMD}
    k5_t = {k: min(1.0, r_fix[k]["ratio"]) for k in ARCHSIMD}
    pre_b = {k: bridged(f"artefact {kk(k)}", k, 1.0, r_pre[k]["ratio"], raw["go_noexp"][k], None) for k in EMR_KEYS}
    pre_t = {k: r_pre[k]["ratio"] for k in EMR_KEYS}
    ge_b, ge_t = {**k5_b, **pre_b}, {**k5_t, **pre_t}
    sens_b, sens_t = {}, {}
    for n, (key, (nc, nk), _) in SENS.items():
        base_b, base_t = ge_b.get(key, 1.0), ge_t.get(key, 1.0)
        sens_b[n] = bridged(n, key, base_b, r_sens[n]["ratio"], raw[nc][nk], base_b)
        sens_t[n] = min(base_t, base_t * r_sens[n]["ratio"])

    def with_sens(names, base, s):
        f = dict(base)
        for n in names:
            f[SENS[n][0]] = s[n]
        return f

    plans = {"Avant": data, "G-K5": scaled(data, k5_b), "G-K5-T": scaled(data, k5_t), "G-pre": scaled(data, pre_b),
             "G-pre-T": scaled(data, pre_t), "G-E": scaled(data, ge_b), "G-E-T": scaled(data, ge_t)}
    for name, names in PLAN.items():
        plans[name] = scaled(data, with_sens(names, ge_b, sens_b))
    plans["S-mesures-T"] = scaled(data, with_sens(PLAN["S-mesures"], ge_t, sens_t))
    replication = {"|".join(k): r["ratio"] for k, r in r_pre.items()}
    replication.update({"|".join(k): min(1.0, r["ratio"]) for k, r in r_fix.items()})
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()},
           "r_pre": {kk(k): r for k, r in r_pre.items()}, "r_nopre": {kk(k): r for k, r in r_nopre.items()},
           "r_sens": r_sens, "sens_used": sens_b, "sens_transfer": sens_t, "transfer": transfer,
           "published_ratios": {kk(k): v for k, v in ge_b.items()}, "replication_ratios": replication, "scenarios": {}}
    for name, d in plans.items():
        z = out["scenarios"][name] = summary(cf.scenario(d, lat, langs, footprint, c3, "main"))
        print(f"{name} : Go {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, D {z['D'][LANG]:.1f}, "
              f"rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}", flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "java_check.json")))["scenarios"]["J-E"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(ROOT, "results", "go_check.json"), "w"), indent=1, default=float)
    # classement publié (3.2) : rapports de G-E inscrits dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in ge_b.items() if k not in K9_KEYS}
    tr.setdefault("ratios_k9h", {})[LANG] = {"|".join(k): v for k, v in ge_b.items() if k in K9_KEYS}
    note = " ; Go : docs/GO.md (3.2), results/raw_go, machine 18, results/go_check.json (K9 : ratios_k9h)"
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(os.path.join(ROOT, "results", "transfers.json"), "w"), indent=1)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur Go : rapports appariés et scénarios\n",
         "Plan : `docs/GO.md`. Mesures : `results/raw_go/` (machine 18, 7 processus par cellule). Code :",
         "`analysis/go_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    rows = [("go_fix / go_ref", o["r_fix"]), ("go_noexp / go_ref", o["r_pre"]), ("go_nopre / go_ref (information)",
                                                                                  o["r_nopre"])]
    for lab, dd in rows:
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    for n, r in o["r_sens"].items():
        _, (nc, nk), (bc, bk) = SENS[n]
        L.append(f"| {nc} {nk[1]} / {bc} {bk[1]} | {kk(bk)} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | "
                 f"{f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Report sur les données publiées (transfert ou pont par le C de clang)\n",
          "| Rapport | Clé | Go publié | Base (G-E) | Transfert | Pont | Écart | Retenu | Facteur appliqué |",
          "|---|---|---|---|---|---|---|---|---|"]
    for lab, b in o["transfer"].items():
        L.append(f"| {lab} | {b['key']} | {f(b['go_main_ms'], 2)} ms | {f(b['base'], 3)} | {f(b['transfer_ms'], 2)} ms | "
                 f"{f(b['bridge_ms'], 2)} ms | {f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} | "
                 f"{f(b['factor_used'], 3)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Go | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |", "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:17]))
        L.append(f"**{name}** : {top}.\n")
    L.append("## Rapports reportés sur la réplication (machine 3)\n")
    L.append(", ".join(f"{k.replace('|', ':').rstrip(':')} {f(r, 3)}" for k, r in sorted(o["replication_ratios"].items())) + ".")
    open(os.path.join(ROOT, "results", "report_go.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
