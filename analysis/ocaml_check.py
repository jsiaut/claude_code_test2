#!/usr/bin/env python3
"""Remarque sur OCaml (plan : docs/OCAML.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 20 (results/raw_ocaml, étiquette « ocaml »), reportés sur les données publiées
d'OCaml ; analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario du plan (3.5) :
* Avant : le classement publié d'avant (D5 = 1) ; doit reproduire results/haskell_check.json (H-E).
* O-code : les clés dont le code chronométré change (Q6 tuned et mt, K1 aos, K8 tuned) × r(ocaml_fix / ocaml_ref),
  par transfert ; D5 = 1.
* O-M : erratum D5 = 1/2 seul. O-E (classement publié) : les deux.
* O-E-P (information) : O-E, clés reportées par la règle du pont de analysis/transfer_check.py et la règle de sens.
* Sensibilités (sur O-E, en min(1, r) par rapport à O-E) : S-Q6m, S-K8v, S-K7p, S-K9fa, S-K5, S-mesures, S-cases
  (E7 = 1/2), S-tout.
Les autres clés ne changent que d'horloge : leur rapport ocaml_fix / ocaml_ref est un contrôle, non reporté (plan 3.2).
Les corrections publiées des autres langages (results/transfers.json : ratios, ratios_k9h, lat_ratios) sont appliquées
comme dans le calcul publié ; celles d'OCaml en sont retirées pour le calcul, puis les rapports d'O-E y sont écrits
(« ratios »). Les rapports de la réplication (« replication_ratios ») vont dans results/ocaml_check.json.
Sorties : results/ocaml_check.json, results/report_ocaml.md ; results/transfers.json (OCaml).
Variables (essai) : OC_RAW, OC_TAG, OC_OUT (sorties ailleurs, transferts non écrits)."""
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

RAW = os.environ.get("OC_RAW", os.path.join(ROOT, "results", "raw_ocaml"))
TAG = os.environ.get("OC_TAG", "ocaml")
OUT = os.environ.get("OC_OUT", os.path.join(ROOT, "results"))
LANG = "ocaml"
LIMIT = 0.25
Q6T, Q6M = ("k6", "tuned", "q6"), ("k6", "mt", "q6")
K1A, K8T = ("k1", "aos", "energy"), ("k8", "tuned", "")
K7T, K9T, K9M, K5T = ("k7", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", ""), ("k5", "tuned", "")
CORR = [Q6T, Q6M, K1A, K8T]
SENS = {"q6_tuned_m": (Q6T, ("ocaml_exp", ("k6", "tuned_m", "q6")), ("ocaml_fix", Q6T)),
        "q6_mt_m": (Q6M, ("ocaml_exp", ("k6", "mt_m", "q6")), ("ocaml_fix", Q6M)),
        "k8_tuned_val": (K8T, ("ocaml_exp", ("k8", "tuned_val", "")), ("ocaml_fix", K8T)),
        "k7_tuned_p": (K7T, ("ocaml_exp", ("k7", "tuned_p", "")), ("ocaml_fix", K7T)),
        "k9_tuned_fa": (K9T, ("ocaml_exp", ("k9", "tuned_fa", "")), ("ocaml_fix", K9T)),
        "k9_mt_fa": (K9M, ("ocaml_exp", ("k9", "mt_fa", "")), ("ocaml_fix", K9M)),
        "k5_tuned_8": (K5T, ("ocaml_exp", ("k5", "tuned_8", "")), ("ocaml_fix", K5T))}
PLAN = {"S-Q6m": ["q6_tuned_m", "q6_mt_m"], "S-K8v": ["k8_tuned_val"], "S-K7p": ["k7_tuned_p"],
        "S-K9fa": ["k9_tuned_fa", "k9_mt_fa"], "S-K5": ["k5_tuned_8"], "S-mesures": list(SENS)}
ERRATA = {"D5": 0.5}
BEFORE = {"D5": 1}
CASES = {"E7": 0.5}


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad = defaultdict(dict), []
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
            "prec_o": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases d'OCaml remplacées le temps du calcul."""
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
    """Données du calcul publié, sans les corrections d'OCaml : transferts des autres langages, K9 de la machine 16 (et
    les corrections de K9 des autres langages), latences de la machine 11 (et les corrections de latence des autres)."""
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
    assert {c: m[c][0] for c in ERRATA} == ERRATA, "erratum D5 absent de analysis/capabilities.py"
    data, lat, tr = published_data()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 700)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    keys = sorted(raw["ocaml_ref"])
    r_fix = {k: ratio(raw["ocaml_fix"][k], raw["ocaml_ref"][k], rng) for k in keys}
    r_sens = {n: ratio(raw[nc][nk], raw[bc][bk], rng) for n, (_, (nc, nk), (bc, bk)) in SENS.items()}
    transfer = {}

    def bridged(label, key, r, new_procs):
        """Pont par le C du même hôte au-delà de 25 % d'écart, et règle de sens (information, scénario O-E-P)."""
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
    fix_b = {k: bridged(f"pont {kk(k)}", k, r_fix[k]["ratio"], raw["ocaml_fix"][k]) for k in CORR}
    sens_t = {}
    for n, (key, _, _) in SENS.items():
        sens_t[n] = fix_t.get(key, 1.0) * min(1.0, r_sens[n]["ratio"])

    def with_sens(names):
        f = dict(fix_t)
        for n in names:
            f[SENS[n][0]] = sens_t[n]
        return f

    plans = {"Avant": (data, BEFORE), "O-code": (scaled(data, fix_t), BEFORE), "O-M": (data, None),
             "O-E": (scaled(data, fix_t), None), "O-E-P": (scaled(data, fix_b), None)}
    for name, names in PLAN.items():
        plans[name] = (scaled(data, with_sens(names)), None)
    plans["S-cases"] = (scaled(data, fix_t), CASES)
    plans["S-tout"] = (scaled(data, with_sens(PLAN["S-mesures"])), CASES)
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()}, "r_sens": r_sens,
           "transfer": transfer, "published_ratios": {kk(k): v for k, v in fix_t.items()},
           "bridge_ratios": {kk(k): v for k, v in fix_b.items()}, "sens_factors": sens_t,
           "replication_ratios": {"|".join(k): fix_t[k] for k in CORR}, "scenarios": {}}
    for name, (d, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, cells)
        print(f"{name} : OCaml {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "haskell_check.json")))["scenarios"]["H-E"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(OUT, "ocaml_check.json"), "w"), indent=1, default=float)
    report(out)
    if OUT != os.path.join(ROOT, "results"):
        return
    # classement publié (3.2) : rapports d'O-E inscrits dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in fix_t.items()}
    note = " ; OCaml : docs/OCAML.md (3.2), results/raw_ocaml, machine 20, results/ocaml_check.json"
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(os.path.join(ROOT, "results", "transfers.json"), "w"), indent=1)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur OCaml : rapports appariés et scénarios\n",
         "Plan : `docs/OCAML.md`. Mesures : `results/raw_ocaml/` (machine 20, 7 processus par cellule). Code :",
         "`analysis/ocaml_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte) : ocaml_fix / ocaml_ref\n",
         "Clés corrigées (reportées) en gras ; les autres ne changent que d'horloge (contrôle, non reportées).\n",
         "| Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|"]
    corr = {kk(k) for k in CORR}
    for k, r in o["r_fix"].items():
        b = "**" if k in corr else ""
        L.append(f"| {b}{k}{b} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {b}{f(r['ratio'], 3)}{b} | "
                 f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Sensibilités (forme nouvelle / ocaml_fix, même hôte)\n",
          "| Sensibilité | Clé | Base (ms) | Forme nouvelle (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|---|"]
    for n, r in o["r_sens"].items():
        L.append(f"| {n} | {kk(SENS[n][0])} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                 f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Pont par le C de clang (information : scénario O-E-P ; le classement publié reporte par transfert)\n",
          "| Rapport | Clé | OCaml publié | Transfert | Pont | Écart | Retenu | Facteur appliqué |",
          "|---|---|---|---|---|---|---|---|"]
    for lab, b in o["transfer"].items():
        L.append(f"| {lab} | {b['key']} | {f(b['main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} | {f(b['factor_used'], 3)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score d'OCaml | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][13:20], start=13))
        L.append(f"**{name}** : {top}.\n")
    L.append("## Rapports reportés sur la réplication (machine 3)\n")
    L.append(", ".join(f"{k.replace('|', ':').rstrip(':')} {f(r, 3)}" for k, r in sorted(o["replication_ratios"].items()))
             + ".")
    open(os.path.join(OUT, "report_ocaml.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
