#!/usr/bin/env python3
"""Ajout de FreePascal (plan : docs/FPC.md, section 3, poussé avant les mesures).

Mesures de la machine 25 (Emerald Rapids, du même modèle que les machines 3, 11 et 16 ; results/raw_fpc, étiquette
« fpc ») : fpc, le C publié (c, Cascade Lake), le C natif (c_er), le second témoin (c_gcc_cl, binaire publié de
c_gcc) et les copies fpc_exp, fpc_scal, fpc_o2. FreePascal entre dans les données publiées par le pont du C
(analysis/analyze_v2.py, ADDED et ADDED_ER : chaque processus × G(C publié) / G(C machine 25), clé par clé, avec la
construction du C qui a produit chaque donnée publiée ; latences de K8 naturel colonne par colonne). Analyse globale
de la v3 rejouée (mêmes tirages ; ceux de FreePascal isolés) pour chaque scénario du plan (3.5) :
* Avant : FreePascal retiré ; doit reproduire R-E de results/swift_remark.json (classement publié d'avant) à
  l'identique.
* F-E (classement publié) : FreePascal ajouté (pont, grille, empreinte, C3 mesurée).
* F-direct (information) : temps de la machine 25 sans pont pour les clés de la machine 1 ; pont gardé pour K5, K9 et
  les latences de K8 naturel (sources Emerald Rapids).
* F-hôte : clés de la machine 1 × la médiane, sur ces clés, des facteurs du C ; F-gcc : clés de la machine 1 reliées
  par le second témoin (c_gcc publié / c_gcc_cl machine 25).
* F-scal (K1 soa et K5 tuned × r(fpc_scal / fpc)), F-O2 (9 cellules naturelles × r(fpc_o2 / fpc)), F-K7cls, F-K8cls
  (temps et latences), F-K9dyn (rapports de fpc_exp) : rapports appliqués tels qu'ils sont mesurés.
* F-cases-bas (A3 = E2 = E4 = F4 = 1/2), F-cases-haut (A4 = B2 = E7 = 1, C4 = 1/2), F-tout-bas (F-cases-bas, F-scal,
  F-O2, F-K8cls, F-K9dyn), F-tout-haut (F-cases-haut, F-K7cls).
* Hors plan, information (ajouté après avoir vu les facteurs du pont, docs/FPC.md 4.4) : F-K7tab, K7 naturel relié par
  le facteur de K7 optimisé du C (table plate, comme TDictionary) au lieu de celui de sa table chaînée (comme R-K7 de
  la remarque sur Swift).
Information : rapport FreePascal / C de chaque cellule sur la machine 25 ; K10 ; facteurs du pont par clé avec les deux
témoins ; clés écartées par la borne physique.
Sorties : results/fpc_check.json, results/report_fpc.md."""
import glob, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import capabilities_v2 as c2  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from fortran_check import ratio  # noqa: E402
from python_check import kk, gm, lat_ratio, LATCOLS, f  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_fpc")
TAG = "fpc"
LANG = "fpc"
NATURAL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
           ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"), ("k7", "natural", ""),
           ("k8", "natural", ""), ("k9", "natural", "")]
K7N, K7C, K7T = ("k7", "natural", ""), ("k7", "natural_cls", ""), ("k7", "tuned", "")
K8C = ("k8", "natural_cls", "")
K9N, K9D = ("k9", "natural", ""), ("k9", "natural_dyn", "")
SCAL = [("k1", "soa", "energy"), ("k5", "tuned", "")]
CASES_LOW = {"A3": 0.5, "E2": 0.5, "E4": 0.5, "F4": 0.5}
CASES_HIGH = {"A4": 1.0, "B2": 1.0, "C4": 0.5, "E7": 1.0}
M1 = ("k1", "k2", "k3", "k4", "k6", "k7", "k8")  # clés dont la source publiée est la machine 1 (Cascade Lake)


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
    """Scénario avec des cases de FreePascal remplacées le temps du calcul (aucune n'a de dérogation v2)."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            assert (LANG, cap) not in c2.V2_OVERRIDES, cap
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"), list(RANKED))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def without_fpc(data, lat, langs, footprint, c3):
    """Avant : FreePascal retiré de RANKED (liste partagée par tous les modules) et des données, le temps du calcul."""
    RANKED.remove(LANG)
    try:
        d = {l: v for l, v in data.items() if l != LANG}
        lt = {l: v for l, v in lat.items() if l != LANG}
        return summary(cf.scenario(d, lt, [l for l in langs if l != LANG], footprint, c3, "main"), list(RANKED))
    finally:
        RANKED.append(LANG)


def scaled(data, factors):
    d = {l: v for l, v in data.items()}
    d[LANG] = {k: [list(p) for p in v] for k, v in data[LANG].items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def with_lat(lat, r):
    out = {l: dict(v) for l, v in lat.items()}
    out[LANG][K8N] = v2.scale_lat(lat[LANG][K8N], r)
    return out


def replaced(data, new):
    """FreePascal avec certaines clés remplacées par des processus donnés."""
    d = {l: v for l, v in data.items()}
    d[LANG] = {k: (new[k] if k in new else v) for k, v in data[LANG].items()}
    return d


def main():
    assert RANKED[-1] == LANG, "FreePascal doit être le dernier de RANKED (tirages isolés)"
    raw, rawlat, bad = load_raw()
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    assert LANG in c3 and LANG in footprint, "C3 et empreinte de FreePascal d'abord (tools/c3_measure.py, analysis/footprint.py)"
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2500)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    # rapports de la machine 25 (au C de la même construction que la donnée publiée) et facteurs du pont
    wit = {k: ("c_er" if k[0] == "k5" else "c") for k in raw[LANG]}
    r_fpc_c = {kk(k): ratio(raw[LANG][k], raw[wit[k]][k], rng) for k in sorted(raw[LANG]) if k in raw[wit[k]]}
    bridge = {}
    for k in sorted(data[LANG]):
        w = wit.get(k, "c")
        b = {"witness": w, "c_pub_ms": 1e3 * gm(data["c"][k]), "c_25_ms": 1e3 * gm(raw[w][k]),
             "fpc_25_ms": 1e3 * gm(raw[LANG][k]), "fpc_pub_ms": 1e3 * gm(data[LANG][k]),
             "factor": gm(data["c"][k]) / gm(raw[w][k])}
        if k[0] in M1 and k in raw.get("c_gcc_cl", {}) and k in data.get("c_gcc", {}):
            b["factor_gcc"] = gm(data["c_gcc"][k]) / gm(raw["c_gcc_cl"][k])
        bridge[kk(k)] = b
    lat_bridge = {"c_pub_us": (np.array(v2._lat_cols(lat["c"][K8N])) / 1e3).tolist(),
                  "c_25_us": (np.array(v2._lat_cols(rawlat["c"][K8N])) / 1e3).tolist(),
                  "fpc_25_us": (np.array(v2._lat_cols(rawlat[LANG][K8N])) / 1e3).tolist(),
                  "fpc_pub_us": (np.array(v2._lat_cols(lat[LANG][K8N])) / 1e3).tolist()}
    # contrôles du pont entre modèles : F-direct, F-hôte, F-gcc (clés de la machine 1)
    m1 = [k for k in data[LANG] if k[0] in M1 and k in raw[LANG] and k in raw["c"]]
    hf = float(np.median([gm(data["c"][k]) / gm(raw["c"][k]) for k in m1]))
    d_direct = replaced(data, {k: [list(p) for p in raw[LANG][k]] for k in m1})
    d_host = replaced(data, {k: [[t * hf for t in p] for p in raw[LANG][k]] for k in m1})
    d_gcc = replaced(data, {k: [[t * bridge[kk(k)]["factor_gcc"] for t in p] for p in raw[LANG][k]]
                            for k in m1 if "factor_gcc" in bridge[kk(k)]})
    # sensibilités : rapports des copies, appliqués tels qu'ils sont mesurés (sur le même hôte)
    r_scal = {k: ratio(raw["fpc_scal"][k], raw[LANG][k], rng) for k in SCAL}
    r_o2 = {k: ratio(raw["fpc_o2"][k], raw[LANG][k], rng) for k in NATURAL}
    r_k7 = ratio(raw["fpc_exp"][K7C], raw["fpc_exp"][K7N], rng)
    r_k8 = ratio(raw["fpc_exp"][K8C], raw["fpc_exp"][K8N], rng)
    l_k8 = lat_ratio(rawlat["fpc_exp"][K8C], rawlat["fpc_exp"][K8N], rng)
    r_k9 = ratio(raw["fpc_exp"][K9D], raw["fpc_exp"][K9N], rng)
    scal = {k: r["ratio"] for k, r in r_scal.items()}
    o2 = {k: r["ratio"] for k, r in r_o2.items()}
    low = dict(scal)
    low.update(o2)
    low[K8N] = o2[K8N] * r_k8["ratio"]
    low[K9N] = o2[K9N] * r_k9["ratio"]
    plans = {
        "F-E": (data, lat, None),
        "F-direct": (d_direct, lat, None),
        "F-hôte": (d_host, lat, None),
        "F-gcc": (d_gcc, lat, None),
        "F-scal": (scaled(data, scal), lat, None),
        "F-O2": (scaled(data, o2), lat, None),
        "F-K7cls": (scaled(data, {K7N: r_k7["ratio"]}), lat, None),
        "F-K8cls": (scaled(data, {K8N: r_k8["ratio"]}), with_lat(lat, l_k8["ratio"]), None),
        "F-K9dyn": (scaled(data, {K9N: r_k9["ratio"]}), lat, None),
        "F-cases-bas": (data, lat, CASES_LOW),
        "F-cases-haut": (data, lat, CASES_HIGH),
        "F-tout-bas": (scaled(data, low), with_lat(lat, l_k8["ratio"]), CASES_LOW),
        "F-tout-haut": (scaled(data, {K7N: r_k7["ratio"]}), lat, CASES_HIGH),
    }
    # hors plan, information (docs/FPC.md, 4.4) : K7 naturel au facteur de la table plate du C (K7 optimisé)
    f7 = bridge[kk(K7T)]["factor"] / bridge[kk(K7N)]["factor"]
    plans["F-K7tab"] = (scaled(data, {K7N: f7}), lat, None)
    k7_pub = {l: 1e3 * gm(data[l][K7N]) for l in RANKED if K7N in data.get(l, {})}
    out = {"bad": bad, "times_ms": times, "r_fpc_c": r_fpc_c, "bridge": bridge, "lat_bridge": lat_bridge,
           "bridge_sus": sorted({(l, kk(k), t, b) for l, k, t, b in v2.BRIDGE_SUS}), "host_factor": hf,
           "r_scal": {kk(k): r for k, r in r_scal.items()}, "r_o2": {kk(k): r for k, r in r_o2.items()},
           "r_k7cls": r_k7, "r_k8cls": r_k8, "lat_k8cls": l_k8, "r_k9dyn": r_k9,
           "k7_factors": {"natural": bridge[kk(K7N)]["factor"], "tuned": bridge[kk(K7T)]["factor"], "F-K7tab": f7},
           "k7_published_ms": k7_pub, "c3": c3[LANG], "footprint": footprint[LANG], "scenarios": {}}
    av = out["scenarios"]["Avant"] = without_fpc(data, lat, langs, footprint, c3)
    ref = json.load(open(os.path.join(ROOT, "results", "swift_remark.json")))["scenarios"]["R-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED if l != LANG)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant (R-E) = {out['check_before']:.2e}", flush=True)
    for name, (d, lt, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : FreePascal {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    fe = out["scenarios"]["F-E"]
    out["shift"] = {l: fe["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
    json.dump(out, open(os.path.join(ROOT, "results", "fpc_check.json"), "w"), indent=1, default=float)
    report(out)


def report(o):
    S = o["scenarios"]
    fe, av = S["F-E"], S["Avant"]
    L = ["# Ajout de FreePascal : pont par le C et scénarios\n",
         "Plan : `docs/FPC.md`. Mesures : `results/raw_fpc/` (machine 25, Emerald Rapids, 7 processus par cellule). Code :",
         "`analysis/fpc_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant (FreePascal retiré) reproduit le classement publié d'avant (écart maximal "
         f"{o['check_before']:.1e}).\n",
         "## FreePascal / C sur la machine 25 et pont vers les données publiées\n",
         "Témoin de chaque clé : le C de la construction des données publiées (`c`, Cascade Lake ; `c_er` pour K5). "
         "Facteur gcc : second témoin (`c_gcc` publié / `c_gcc_cl` sur la machine 25).\n",
         "| Cellule | FreePascal (ms) | C (ms) | FreePascal / C [IC 95 %] | C publié (ms) | facteur du pont | facteur gcc | "
         "FreePascal publié (ms) |", "|---|---|---|---|---|---|---|---|"]
    for k, r in o["r_fpc_c"].items():
        b = o["bridge"].get(k)
        L.append(f"| {k} | {f(r['new_ms'], 3)} | {f(r['old_ms'], 3)} | {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)}] | "
                 + (f"{f(b['c_pub_ms'], 3)} | {f(b['factor'], 3)} | {f(b.get('factor_gcc'), 3)} | {f(b['fpc_pub_ms'], 3)} |"
                    if b else "— | — | — | — |"))
    lb = o["lat_bridge"]
    kf = o["k7_factors"]
    L += ["", f"Facteur d'hôte unique de F-hôte (médiane des facteurs du C sur les clés de la machine 1) : "
          f"{f(o['host_factor'], 3)}.", "",
          f"K7 naturel (hors plan, F-K7tab) : facteur de la table chaînée du C {f(kf['natural'], 2)}, de sa table plate "
          f"(K7 optimisé) {f(kf['tuned'], 2)}. Temps publiés de K7 naturel (machine 1 ; FreePascal relié) : "
          + " ; ".join(f"{NAMES[l]} {f(t / 1e3, 2)} s" for l, t in sorted(o["k7_published_ms"].items(), key=lambda x: x[1])) + ".", "",
          "Latences de K8 naturel (µs, médianes de toutes les répétitions) :", "",
          "| | " + " | ".join(LATCOLS) + " |", "|---" * (len(LATCOLS) + 1) + "|"]
    for name, key in (("FreePascal, machine 25", "fpc_25_us"), ("C, machine 25", "c_25_us"), ("C publié", "c_pub_us"),
                      ("FreePascal publié", "fpc_pub_us")):
        L.append(f"| {name} | " + " | ".join(f(x, 1) for x in lb[key]) + " |")
    if o["bridge_sus"]:
        L += ["", "Clés reliées écartées par la borne physique : " + ", ".join(f"{l} {k} ({t:.2e} s)" for l, k, t, _ in o["bridge_sus"])]
    L += ["", f"Empreinte de K1 : {f(o['footprint'], 2)} octets par particule ; C3 mesurée : {f(o['c3'], 1)}.", "",
          "## Sensibilités (rapports sur le même hôte, appliqués tels quels)\n",
          "* sans `-Sv` (`fpc_scal` / `fpc`) : " + " ; ".join(f"{k} {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)}]"
                                                              for k, r in o["r_scal"].items()) + ".",
          "* mode `RELEASE` du `fpc.cfg` (`fpc_o2` / `fpc`) : " + " ; ".join(
              f"{k} {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)}]" for k, r in o["r_o2"].items()) + ".",
          f"* K7 naturel, valeurs de classe (`natural_cls` / `natural`, fpc_exp) : {f(o['r_k7cls']['ratio'], 3)} "
          f"[{f(o['r_k7cls']['ci'][0], 3)}–{f(o['r_k7cls']['ci'][1], 3)}].",
          f"* K8 naturel, nœuds de classe : {f(o['r_k8cls']['ratio'], 3)} [{f(o['r_k8cls']['ci'][0], 3)}–"
          f"{f(o['r_k8cls']['ci'][1], 3)}] ; latences " + ", ".join(f"{c} {f(x, 2)}" for c, x in zip(LATCOLS, o["lat_k8cls"]["ratio"])) + ".",
          f"* K9 naturel, `array of array of Double` : {f(o['r_k9dyn']['ratio'], 3)} [{f(o['r_k9dyn']['ci'][0], 3)}–"
          f"{f(o['r_k9dyn']['ci'][1], 3)}].", "",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |", "|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        if name == "Avant":
            continue
        L.append(f"| {name} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | {f(z['D'][LANG], 1)} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} |")
    nb = fe["neighbours"]
    L += ["", "Voisins dans F-E : " + " ; ".join(f"{k} {NAMES[l]} (FreePascal devant dans {f(100 * p, 0)} % des variantes)"
                                                  for k, (l, p) in nb.items()) + ".", "",
          "## Classement : avant et avec FreePascal (F-E)\n",
          "| Place | Avant | rang espéré | Avec FreePascal | rang espéré | écart du rang espéré |", "|---|---|---|---|---|---|"]
    for i in range(len(fe["order21"])):
        a = av["order21"][i] if i < len(av["order21"]) else None
        b = fe["order21"][i]
        L.append(f"| {i + 1} | {NAMES[a] if a else '—'} | {f(av['exp21'][a], 2) if a else '—'} | {NAMES[b]} | "
                 f"{f(fe['exp21'][b], 2)} | {f(o['shift'].get(b), 2) if b != LANG else '—'} |")
    open(os.path.join(ROOT, "results", "report_fpc.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
