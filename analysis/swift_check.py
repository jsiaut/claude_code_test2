#!/usr/bin/env python3
"""Ajout de Swift (plan : docs/SWIFT.md, section 3, poussé avant les mesures).

Mesures de la machine 23 (Cascade Lake, du même modèle que l'hôte des données principales ; results/raw_swift,
étiquette « swift ») : Swift et le C de la campagne (témoin du pont), swift_exp (K8 natural_fl) et swift_ou
(-Ounchecked). Swift entre dans les données publiées par le pont du C (analysis/analyze_v2.py, bridge_added : chaque
processus × G(C publié) / G(C machine 23), clé par clé ; latences de K8 naturel colonne par colonne). Analyse globale de
la v3 rejouée (mêmes tirages ; ceux de Swift isolés) pour chaque scénario du plan (3.5) :
* Avant : Swift retiré ; doit reproduire L-E de results/lua_check.json (classement publié d'avant) à l'identique.
* S-E (classement publié) : Swift ajouté (pont, grille, empreinte, C3 mesurée).
* S-direct (information) : temps de la machine 23 sans pont pour les clés de la machine 1 (même modèle) ; pont gardé
  pour K5, K9 et les latences de K8 naturel (sources Emerald Rapids).
* S-K8fl : K8 naturel (temps et latences) × r(natural_fl / natural, swift_exp) ; S-Ou : les 9 cellules naturelles
  × r(swift_ou / swift) ; sensibilités en min(1, r).
* S-cases-bas (A2 = C5 = F4 = 1/2, D3 = 0), S-cases-haut (C2 = E3 = E5 = 1), S-tout-bas (= S-cases-bas),
  S-tout-haut (S-K8fl, S-Ou et S-cases-haut).
Information : rapport Swift / C de chaque cellule sur la machine 23 ; K10 ; clés écartées par la borne physique.
Sorties : results/swift_check.json, results/report_swift.md."""
import copy, glob, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from fortran_check import ratio  # noqa: E402
from python_check import kk, gm, lat_ratio, LATCOLS, f  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_swift")
TAG = "swift"
LANG = "swift"
NATURAL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
           ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"), ("k7", "natural", ""),
           ("k8", "natural", ""), ("k9", "natural", "")]
K8FL = ("k8", "natural_fl", "")
CASES_LOW = {"A2": 0.5, "C5": 0.5, "F4": 0.5, "D3": 0.0}
CASES_HIGH = {"C2": 1.0, "E3": 1.0, "E5": 1.0}
OTHER_MODEL = ("k5", "k9")  # clés dont la source publiée est un Emerald Rapids (machines 3 et 16)


def load_raw():
    d, lat, bad = defaultdict(dict), defaultdict(dict), []
    for fn in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(fn):
            r = json.loads(line)
            if r.get("tag") != TAG:
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], kk(key), r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            if r["kernel"] == "k8" and r.get("lat"):
                lat[r["lang"]].setdefault(key, []).append(r["lat"])
    return d, lat, bad


def summary(s, langs_ranked):
    i = langs_ranked.index(LANG) if LANG in langs_ranked else None
    order = sorted(langs_ranked, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    out = {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
           "ms0": {l: s["ms0"][l] for l in langs_ranked}, "E": {l: s["E"][l] for l in langs_ranked},
           "D": {l: s["D"][l] for l in langs_ranked}, "C": {l: s["C"][l] for l in langs_ranked},
           "prec_next": {a: float(s["prec"][langs_ranked.index(a), langs_ranked.index(b)]) for a, b in zip(order, order[1:])}}
    if i is not None:
        pos = order.index(LANG)
        nb = {}
        if pos > 0:
            nb["devant"] = (order[pos - 1], float(s["prec"][i, langs_ranked.index(order[pos - 1])]))
        if pos < len(order) - 1:
            nb["derrière"] = (order[pos + 1], float(s["prec"][i, langs_ranked.index(order[pos + 1])]))
        out.update({"pos": pos + 1, "neighbours": nb, "Ek": s["Ek"][LANG], "Dk": s.get("Dk", {}).get(LANG),
                    "prec_l": {l: float(s["prec"][i, langs_ranked.index(l)]) for l in langs_ranked if l != LANG}})
    return out


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de Swift remplacées le temps du calcul."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"), list(RANKED))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def without_swift(data, lat, langs, footprint, c3):
    """Avant : Swift retiré de RANKED (liste partagée par tous les modules) et des données, le temps du calcul."""
    RANKED.remove(LANG)
    try:
        d = {l: v for l, v in data.items() if l != LANG}
        lt = {l: v for l, v in lat.items() if l != LANG}
        return summary(cf.scenario(d, lt, [l for l in langs if l != LANG], footprint, c3, "main"), list(RANKED))
    finally:
        RANKED.append(LANG)


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def with_lat(lat, r):
    out = {l: dict(v) for l, v in lat.items()}
    out[LANG][K8N] = v2.scale_lat(lat[LANG][K8N], r)
    return out


def main():
    assert RANKED[-1] == LANG, "Swift doit être le dernier de RANKED (tirages isolés)"
    raw, rawlat, bad = load_raw()
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    assert LANG in c3 and LANG in footprint, "C3 et empreinte de Swift d'abord (tools/c3_measure.py, analysis/footprint.py)"
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2000)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    # rapports de la machine 23 et facteurs du pont
    r_sw_c = {kk(k): ratio(raw[LANG][k], raw["c"][k], rng) for k in sorted(raw[LANG]) if k in raw["c"]}
    bridge = {}
    for k in sorted(data[LANG]):
        bridge[kk(k)] = {"c_pub_ms": 1e3 * gm(data["c"][k]), "c_23_ms": 1e3 * gm(raw["c"][k]),
                         "swift_23_ms": 1e3 * gm(raw[LANG][k]), "swift_pub_ms": 1e3 * gm(data[LANG][k]),
                         "factor": gm(data["c"][k]) / gm(raw["c"][k])}
    lat_bridge = {"c_pub_us": (np.array(v2._lat_cols(lat["c"][K8N])) / 1e3).tolist(),
                  "c_23_us": (np.array(v2._lat_cols(rawlat["c"][K8N])) / 1e3).tolist(),
                  "swift_23_us": (np.array(v2._lat_cols(rawlat[LANG][K8N])) / 1e3).tolist(),
                  "swift_pub_us": (np.array(v2._lat_cols(lat[LANG][K8N])) / 1e3).tolist()}
    # sensibilités (min(1, r))
    r_k8fl = ratio(raw["swift_exp"][K8FL], raw["swift_exp"][K8N], rng)
    l_k8fl = lat_ratio(rawlat["swift_exp"][K8FL], rawlat["swift_exp"][K8N], rng)
    r_ou = {k: ratio(raw["swift_ou"][k], raw[LANG][k], rng) for k in NATURAL}
    fl = {K8N: min(1.0, r_k8fl["ratio"])}
    lat_fl = [min(1.0, x) for x in l_k8fl["ratio"]]
    ou = {k: min(1.0, r_ou[k]["ratio"]) for k in NATURAL}
    both = dict(ou)
    both[K8N] = ou[K8N] * fl[K8N]
    # S-direct : temps de la machine 23 pour les clés de la machine 1 (même modèle), pont gardé ailleurs
    dd = {l: v for l, v in data.items()}
    dd[LANG] = {k: ([list(p) for p in raw[LANG][k]] if k[0] not in OTHER_MODEL else v) for k, v in data[LANG].items()}
    plans = {
        "S-E": (data, lat, None),
        "S-direct": (dd, lat, None),
        "S-K8fl": (scaled(data, fl), with_lat(lat, lat_fl), None),
        "S-Ou": (scaled(data, ou), lat, None),
        "S-cases-bas": (data, lat, CASES_LOW),
        "S-cases-haut": (data, lat, CASES_HIGH),
        "S-tout-bas": (data, lat, CASES_LOW),
        "S-tout-haut": (scaled(data, both), with_lat(lat, lat_fl), CASES_HIGH),
    }
    out = {"bad": bad, "times_ms": times, "r_swift_c": r_sw_c, "bridge": bridge, "lat_bridge": lat_bridge,
           "bridge_sus": [(l, kk(k), t, b) for l, k, t, b in v2.BRIDGE_SUS],
           "r_k8fl": r_k8fl, "lat_k8fl": l_k8fl, "r_ou": {kk(k): r for k, r in r_ou.items()},
           "sens_factors": {"S-K8fl": {kk(k): v for k, v in fl.items()}, "S-K8fl-lat": lat_fl,
                            "S-Ou": {kk(k): v for k, v in ou.items()}},
           "c3": c3[LANG], "footprint": footprint[LANG], "scenarios": {}}
    av = out["scenarios"]["Avant"] = without_swift(data, lat, langs, footprint, c3)
    ref = json.load(open(os.path.join(ROOT, "results", "lua_check.json")))["scenarios"]["L-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED if l != LANG)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant (L-E) = {out['check_before']:.2e}", flush=True)
    for name, (d, lt, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : Swift {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    se = out["scenarios"]["S-E"]
    out["shift"] = {l: se["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
    json.dump(out, open(os.path.join(ROOT, "results", "swift_check.json"), "w"), indent=1, default=float)
    report(out)


def report(o):
    S = o["scenarios"]
    se, av = S["S-E"], S["Avant"]
    L = ["# Ajout de Swift : pont par le C et scénarios\n",
         "Plan : `docs/SWIFT.md`. Mesures : `results/raw_swift/` (machine 23, Cascade Lake, 7 processus par cellule). Code :",
         "`analysis/swift_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant (Swift retiré) reproduit le classement publié d'avant (écart maximal "
         f"{o['check_before']:.1e}).\n",
         "## Swift / C sur la machine 23 et pont vers les données publiées\n",
         "| Cellule | Swift (ms) | C (ms) | Swift / C [IC 95 %] | C publié (ms) | facteur du pont | Swift publié (ms) |",
         "|---|---|---|---|---|---|---|"]
    for k, r in o["r_swift_c"].items():
        b = o["bridge"].get(k)
        L.append(f"| {k} | {f(r['new_ms'], 3)} | {f(r['old_ms'], 3)} | {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)}] | "
                 + (f"{f(b['c_pub_ms'], 3)} | {f(b['factor'], 3)} | {f(b['swift_pub_ms'], 3)} |" if b else "— | — | — |"))
    lb = o["lat_bridge"]
    L += ["", "Latences de K8 naturel (µs, médianes de toutes les répétitions) :", "",
          "| | " + " | ".join(LATCOLS) + " |", "|---" * (len(LATCOLS) + 1) + "|"]
    for name, key in (("Swift, machine 23", "swift_23_us"), ("C, machine 23", "c_23_us"), ("C publié", "c_pub_us"),
                      ("Swift publié", "swift_pub_us")):
        L.append(f"| {name} | " + " | ".join(f(x, 1) for x in lb[key]) + " |")
    if o["bridge_sus"]:
        L += ["", "Clés reliées écartées par la borne physique : " + ", ".join(f"{k} ({t:.2e} s)" for _, k, t, _ in o["bridge_sus"])]
    L += ["", f"Empreinte de K1 : {f(o['footprint'], 2)} octets par particule ; C3 mesurée : {f(o['c3'], 1)}.", "",
          "## Sensibilités (même hôte)\n",
          f"* K8 naturel, `natural_fl` / `natural` (swift_exp) : {f(o['r_k8fl']['ratio'], 3)} "
          f"[{f(o['r_k8fl']['ci'][0], 3)}–{f(o['r_k8fl']['ci'][1], 3)}] ; latences "
          + ", ".join(f"{c} {f(x, 2)}" for c, x in zip(LATCOLS, o["lat_k8fl"]["ratio"])) + ".",
          "* `-Ounchecked` / `-O` (cellules naturelles) : "
          + " ; ".join(f"{k} {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)}]" for k, r in o["r_ou"].items()) + ".", "",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |", "|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        if name == "Avant":
            continue
        L.append(f"| {name} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | {f(z['D'][LANG], 1)} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} |")
    nb = se["neighbours"]
    L += ["", "Voisins dans S-E : " + " ; ".join(f"{k} {NAMES[l]} (Swift devant dans {f(100 * p, 0)} % des variantes)"
                                                  for k, (l, p) in nb.items()) + ".", "",
          "## Classement : avant et avec Swift (S-E)\n",
          "| Place | Avant | rang espéré | Avec Swift | rang espéré | écart du rang espéré |", "|---|---|---|---|---|---|"]
    for i in range(len(se["order21"])):
        a = av["order21"][i] if i < len(av["order21"]) else None
        b = se["order21"][i]
        L.append(f"| {i + 1} | {NAMES[a] if a else '—'} | {f(av['exp21'][a], 2) if a else '—'} | {NAMES[b]} | "
                 f"{f(se['exp21'][b], 2)} | {f(o['shift'].get(b), 2) if b != LANG else '—'} |")
    open(os.path.join(ROOT, "results", "report_swift.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
