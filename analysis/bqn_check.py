#!/usr/bin/env python3
"""Ajout de BQN (plan : docs/BQN.md, section 3, poussé avant les mesures).

Mesures de la machine 26 (Emerald Rapids, du même modèle que les machines 3, 11 et 16 ; results/raw_bqn, étiquette
« bqn ») : bqn (CBQN pour la cible Cascade Lake), bqn_er (construction native de la machine 26), bqn_o3 (cible par
défaut), le C publié (c, Cascade Lake), le C natif (c_er) et le second témoin (c_gcc_cl, binaire publié de c_gcc). BQN
entre dans les données publiées par le pont du C (analysis/analyze_v2.py, ADDED et ADDED_ER : chaque processus ×
G(C publié) / G(C machine 26), clé par clé, avec la construction du C qui a produit chaque donnée publiée et le binaire
BQN de la même cible : bqn et c pour les clés de la machine 1, K9 et les latences de K8 naturel, bqn_er et c_er pour
K5 et la réplication). Analyse globale de la v3 rejouée (mêmes tirages ; ceux de BQN isolés) pour chaque scénario du
plan (3.5) :
* Avant : BQN retiré ; doit reproduire R-E de results/fpc_remark.json (classement publié d'avant) à l'identique.
* B-E (classement publié) : BQN ajouté (pont, grille, empreinte de 128 o, C3 mesurée).
* B-direct (information) : temps de la machine 26 sans pont pour les clés de la machine 1 ; pont gardé pour K5, K9 et
  les latences de K8 naturel (sources Emerald Rapids).
* B-hôte : clés de la machine 1 × la médiane, sur ces clés, des facteurs du C ; B-gcc : clés de la machine 1 reliées
  par le second témoin (c_gcc publié / c_gcc_cl machine 26).
* B-natif (information) : clés de la machine 1, K9 et latences prises au binaire natif (bqn_er), même pont.
* B-o3 (9 cellules naturelles × r(bqn_o3 / binaire de la clé)), B-K1ns, B-K7arr, B-K8ns (temps et latences) : rapports
  appliqués tels qu'ils sont mesurés ; B-fp (empreinte mesurée par le tas) ; B-C3 (C3 = 0).
* B-cases-bas (A1 = A6 = A7 = B1 = E1 = 0), B-cases-haut (A8 = B1 = C4 = E1 = 1), B-tout-bas (B-cases-bas, B-o3,
  B-K1ns, B-K8ns, B-fp, B-C3), B-tout-haut (B-cases-haut, B-K7arr).
* Hors plan, information (ajouté pendant la campagne, avant tout résultat de BQN, docs/BQN.md 3.5) : B-K7tab, K7
  naturel relié par le facteur de K7 optimisé du C (table plate) au lieu de celui de sa table chaînée ; •HashMap est
  une table à adressage ouvert, comme TDictionary (F-K7tab de docs/FPC.md 4.4).
Information : rapport BQN / C de chaque cellule sur la machine 26 (les deux binaires) ; facteurs du pont par clé avec
les deux témoins ; clés écartées par la borne physique.
Sorties : results/bqn_check.json, results/report_bqn.md."""
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

RAW = os.path.join(ROOT, "results", "raw_bqn")
TAG = "bqn"
LANG = "bqn"
NATURAL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
           ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"), ("k7", "natural", ""),
           ("k8", "natural", ""), ("k9", "natural", "")]
K1N, K1S = ("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy")
K1NS, K1NSS = ("k1", "natural_ns", "energy"), ("k1", "natural_ns_shuffled", "energy")
K7N, K7A, K7T = ("k7", "natural", ""), ("k7", "natural_arr", ""), ("k7", "tuned", "")
K8NS = ("k8", "natural_ns", "")
CASES_LOW = {"A1": 0.0, "A6": 0.0, "A7": 0.0, "B1": 0.0, "E1": 0.0}
CASES_HIGH = {"A8": 1.0, "B1": 1.0, "C4": 1.0, "E1": 1.0}
M1 = ("k1", "k2", "k3", "k4", "k6", "k7", "k8")  # clés dont la source publiée est la machine 1 (Cascade Lake)
ER_KEYS = ("k5",)  # clés reliées par le binaire natif et le C natif (machine 3)


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
    """Scénario avec des cases de BQN remplacées le temps du calcul (aucune n'a de dérogation v2)."""
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


def without_bqn(data, lat, langs, footprint, c3):
    """Avant : BQN retiré de RANKED (liste partagée par tous les modules) et des données, le temps du calcul."""
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
    """BQN avec certaines clés remplacées par des processus donnés."""
    d = {l: v for l, v in data.items()}
    d[LANG] = {k: (new[k] if k in new else v) for k, v in data[LANG].items()}
    return d


def main():
    assert RANKED[-1] == LANG, "BQN doit être le dernier de RANKED (tirages isolés)"
    raw, rawlat, bad = load_raw()
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    fp_detail = json.load(open(os.path.join(ROOT, "results", "footprint_detail.json")))
    assert LANG in c3 and LANG in footprint, "C3 et empreinte de BQN d'abord (tools/c3_measure.py, analysis/footprint.py)"
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2600)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    # binaire et témoin de chaque clé (plan 3.2) : bqn et c, sauf K5 (bqn_er et c_er)
    own = {k: ("bqn_er" if k[0] in ER_KEYS else "bqn") for k in data[LANG]}
    wit = {k: ("c_er" if k[0] in ER_KEYS else "c") for k in data[LANG]}
    # rapports BQN / C de la machine 26 : chaque binaire à son témoin (cible Cascade Lake : c ; natif : c_er)
    r_cl = {kk(k): ratio(raw["bqn"][k], raw["c"][k], rng) for k in sorted(raw["bqn"]) if k in raw["c"]}
    r_er = {kk(k): ratio(raw["bqn_er"][k], raw["c_er"][k], rng) for k in sorted(raw["bqn_er"]) if k in raw["c_er"]}
    r_nat = {kk(k): ratio(raw["bqn_er"][k], raw["bqn"][k], rng) for k in sorted(raw["bqn_er"]) if k in raw["bqn"]}
    bridge = {}
    for k in sorted(data[LANG]):
        w, b0 = wit[k], own[k]
        b = {"witness": w, "binary": b0, "c_pub_ms": 1e3 * gm(data["c"][k]), "c_26_ms": 1e3 * gm(raw[w][k]),
             "bqn_26_ms": 1e3 * gm(raw[b0][k]), "bqn_pub_ms": 1e3 * gm(data[LANG][k]),
             "factor": gm(data["c"][k]) / gm(raw[w][k])}
        if k[0] in M1 and k in raw.get("c_gcc_cl", {}) and k in data.get("c_gcc", {}):
            b["factor_gcc"] = gm(data["c_gcc"][k]) / gm(raw["c_gcc_cl"][k])
        bridge[kk(k)] = b
    lat_bridge = {"c_pub_us": (np.array(v2._lat_cols(lat["c"][K8N])) / 1e3).tolist(),
                  "c_26_us": (np.array(v2._lat_cols(rawlat["c"][K8N])) / 1e3).tolist(),
                  "bqn_26_us": (np.array(v2._lat_cols(rawlat[LANG][K8N])) / 1e3).tolist(),
                  "bqn_er_26_us": (np.array(v2._lat_cols(rawlat["bqn_er"][K8N])) / 1e3).tolist(),
                  "bqn_pub_us": (np.array(v2._lat_cols(lat[LANG][K8N])) / 1e3).tolist()}
    # contrôles du pont entre modèles : B-direct, B-hôte, B-gcc (clés de la machine 1)
    m1 = [k for k in data[LANG] if k[0] in M1 and k in raw[LANG] and k in raw["c"]]
    hf = float(np.median([gm(data["c"][k]) / gm(raw["c"][k]) for k in m1]))
    d_direct = replaced(data, {k: [list(p) for p in raw[LANG][k]] for k in m1})
    d_host = replaced(data, {k: [[t * hf for t in p] for p in raw[LANG][k]] for k in m1})
    d_gcc = replaced(data, {k: [[t * bridge[kk(k)]["factor_gcc"] for t in p] for p in raw[LANG][k]]
                            for k in m1 if "factor_gcc" in bridge[kk(k)]})
    # B-natif (information) : clés de la machine 1 et K9 prises au binaire natif, au même facteur du pont ; latences de
    # K8 naturel × rapport bqn_er / bqn de la machine 26, colonne par colonne
    nat_keys = [k for k in data[LANG] if own[k] == "bqn" and k in raw["bqn_er"]]
    d_nat = replaced(data, {k: [[t * bridge[kk(k)]["factor"] for t in p] for p in raw["bqn_er"][k]] for k in nat_keys})
    l_nat = lat_ratio(rawlat["bqn_er"][K8N], rawlat[LANG][K8N], rng)
    # sensibilités : rapports sur le même hôte, appliqués tels qu'ils sont mesurés
    r_o3 = {k: ratio(raw["bqn_o3"][k], raw[own[k]][k], rng) for k in NATURAL}
    r_k1 = ratio(raw[LANG][K1NS], raw[LANG][K1N], rng)
    r_k1s = ratio(raw[LANG][K1NSS], raw[LANG][K1S], rng)
    r_k7 = ratio(raw[LANG][K7A], raw[LANG][K7N], rng)
    r_k8 = ratio(raw[LANG][K8NS], raw[LANG][K8N], rng)
    l_k8 = lat_ratio(rawlat[LANG][K8NS], rawlat[LANG][K8N], rng)
    o3 = {k: r["ratio"] for k, r in r_o3.items()}
    k1ns = {K1N: r_k1["ratio"], K1S: r_k1s["ratio"]}
    fp_heap = fp_detail[LANG]["measured"]
    fp_hi = {**footprint, LANG: fp_heap}
    c3_0 = {**c3, LANG: 0.0}
    low = dict(o3)
    for k, r in k1ns.items():
        low[k] = low.get(k, 1.0) * r
    low[K8N] = low.get(K8N, 1.0) * r_k8["ratio"]
    plans = {
        "B-E": (data, lat, None, footprint, c3),
        "B-direct": (d_direct, lat, None, footprint, c3),
        "B-hôte": (d_host, lat, None, footprint, c3),
        "B-gcc": (d_gcc, lat, None, footprint, c3),
        "B-natif": (d_nat, with_lat(lat, l_nat["ratio"]), None, footprint, c3),
        "B-o3": (scaled(data, o3), lat, None, footprint, c3),
        "B-K1ns": (scaled(data, k1ns), lat, None, footprint, c3),
        "B-K7arr": (scaled(data, {K7N: r_k7["ratio"]}), lat, None, footprint, c3),
        "B-K8ns": (scaled(data, {K8N: r_k8["ratio"]}), with_lat(lat, l_k8["ratio"]), None, footprint, c3),
        "B-fp": (data, lat, None, fp_hi, c3),
        "B-C3": (data, lat, None, footprint, c3_0),
        "B-cases-bas": (data, lat, CASES_LOW, footprint, c3),
        "B-cases-haut": (data, lat, CASES_HIGH, footprint, c3),
        "B-tout-bas": (scaled(data, low), with_lat(lat, l_k8["ratio"]), CASES_LOW, fp_hi, c3_0),
        "B-tout-haut": (scaled(data, {K7N: r_k7["ratio"]}), lat, CASES_HIGH, footprint, c3),
    }
    # hors plan, information (docs/BQN.md 3.5) : K7 naturel au facteur de la table plate du C (K7 optimisé)
    f7 = bridge[kk(K7T)]["factor"] / bridge[kk(K7N)]["factor"]
    plans["B-K7tab"] = (scaled(data, {K7N: f7}), lat, None, footprint, c3)
    k7_pub = {l: 1e3 * gm(data[l][K7N]) for l in RANKED if K7N in data.get(l, {})}
    out = {"bad": bad, "times_ms": times, "r_bqn_c": r_cl, "r_bqn_er_c_er": r_er, "r_native": r_nat,
           "bridge": bridge, "lat_bridge": lat_bridge, "lat_native": l_nat,
           "bridge_sus": sorted({(l, kk(k), t, b) for l, k, t, b in v2.BRIDGE_SUS}), "host_factor": hf,
           "r_o3": {kk(k): r for k, r in r_o3.items()}, "r_k1ns": r_k1, "r_k1ns_shuffled": r_k1s, "r_k7arr": r_k7,
           "r_k8ns": r_k8, "lat_k8ns": l_k8, "c3": c3[LANG], "footprint": footprint[LANG], "footprint_heap": fp_heap,
           "footprint_detail": fp_detail[LANG],
           "k7_factors": {"natural": bridge[kk(K7N)]["factor"], "tuned": bridge[kk(K7T)]["factor"], "B-K7tab": f7},
           "k7_published_ms": k7_pub, "scenarios": {}}
    av = out["scenarios"]["Avant"] = without_bqn(data, lat, langs, footprint, c3)
    ref = json.load(open(os.path.join(ROOT, "results", "fpc_remark.json")))["scenarios"]["R-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED if l != LANG)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant (R-E) = {out['check_before']:.2e}", flush=True)
    for name, (d, lt, cells, fp, c3s) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, fp, c3s, cells)
        print(f"{name} : BQN {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    be = out["scenarios"]["B-E"]
    out["shift"] = {l: be["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
    out["shift_ms"] = {l: be["ms0"][l] - av["ms0"][l] for l in RANKED if l != LANG}
    json.dump(out, open(os.path.join(ROOT, "results", "bqn_check.json"), "w"), indent=1, default=float)
    report(out)


def ci(r, d=3):
    return f"{f(r['ratio'], d)} [{f(r['ci'][0], d)}–{f(r['ci'][1], d)}]"


def report(o):
    S = o["scenarios"]
    be, av = S["B-E"], S["Avant"]
    L = ["# Ajout de BQN : pont par le C et scénarios\n",
         "Plan : `docs/BQN.md`. Mesures : `results/raw_bqn/` (machine 26, Emerald Rapids, 7 processus par cellule). Code :",
         "`analysis/bqn_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant (BQN retiré) reproduit le classement publié d'avant (écart maximal "
         f"{o['check_before']:.1e}).\n",
         "## BQN / C sur la machine 26 et pont vers les données publiées\n",
         "Chaque binaire face au C de sa cible : `bqn` (cible Cascade Lake) / `c` ; `bqn_er` (natif) / `c_er`. Témoin du "
         "pont : `c` pour les clés de la machine 1, K9 et les latences, `c_er` pour K5. Facteur gcc : second témoin "
         "(`c_gcc` publié / `c_gcc_cl` sur la machine 26). Natif / Cascade Lake : `bqn_er` / `bqn`.\n",
         "| Cellule | BQN (ms) | C (ms) | BQN / C [IC 95 %] | natif / C natif | natif / Cascade Lake | C publié (ms) | "
         "facteur du pont | facteur gcc | BQN publié (ms) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in o["r_bqn_c"].items():
        b = o["bridge"].get(k)
        re_, rn = o["r_bqn_er_c_er"].get(k), o["r_native"].get(k)
        L.append(f"| {k} | {f(r['new_ms'], 3)} | {f(r['old_ms'], 3)} | {ci(r)} | {ci(re_) if re_ else '—'} | "
                 f"{ci(rn) if rn else '—'} | "
                 + (f"{f(b['c_pub_ms'], 3)} | {f(b['factor'], 3)} | {f(b.get('factor_gcc'), 3)} | {f(b['bqn_pub_ms'], 3)} |"
                    if b else "— | — | — | — |"))
    lb = o["lat_bridge"]
    kf = o["k7_factors"]
    L += ["", f"Facteur d'hôte unique de B-hôte (médiane des facteurs du C sur les clés de la machine 1) : "
          f"{f(o['host_factor'], 3)}.", "",
          f"K7 naturel (hors plan, B-K7tab) : facteur de la table chaînée du C {f(kf['natural'], 2)}, de sa table plate "
          f"(K7 optimisé) {f(kf['tuned'], 2)}. Temps publiés de K7 naturel (machine 1 ; BQN relié) : "
          + " ; ".join(f"{NAMES[l]} {f(t / 1e3, 2)} s" for l, t in sorted(o["k7_published_ms"].items(), key=lambda x: x[1])) + ".", "",
          "Latences de K8 naturel (µs, médianes de toutes les répétitions) :", "",
          "| | " + " | ".join(LATCOLS) + " |", "|---" * (len(LATCOLS) + 1) + "|"]
    for name, key in (("BQN, machine 26", "bqn_26_us"), ("BQN natif, machine 26", "bqn_er_26_us"),
                      ("C, machine 26", "c_26_us"), ("C publié", "c_pub_us"), ("BQN publié", "bqn_pub_us")):
        L.append(f"| {name} | " + " | ".join(f(x, 1) for x in lb[key]) + " |")
    if o["bridge_sus"]:
        L += ["", "Clés reliées écartées par la borne physique : " + ", ".join(f"{l} {k} ({t:.2e} s)" for l, k, t, _ in o["bridge_sus"])]
    fd = o["footprint_detail"]
    L += ["", f"Empreinte de K1 : {f(o['footprint'], 2)} octets par particule retenus (taille de structure) ; mesure du tas "
          f"{f(o['footprint_heap'], 2)} ; RSS {f(fd.get('rss_bytes_per_particle'), 2)} (processus : "
          + ", ".join(f(x, 2) for x in fd.get("per_process", [])) + f"). C3 mesurée : {f(o['c3'], 1)}.", "",
          "## Sensibilités (rapports sur le même hôte, appliqués tels quels)\n",
          "* construction par défaut (`bqn_o3` / binaire de la clé) : " + " ; ".join(
              f"{k} {ci(r)}" for k, r in o["r_o3"].items()) + ".",
          f"* K1 en espaces de noms : `natural_ns` / `natural` {ci(o['r_k1ns'])} ; `natural_ns_shuffled` / "
          f"`natural_shuffled` {ci(o['r_k1ns_shuffled'])}.",
          f"* K7, idiome tableau (`natural_arr` / `natural`) : {ci(o['r_k7arr'])}.",
          f"* K8, nœuds en espaces de noms (`natural_ns` / `natural`) : {ci(o['r_k8ns'])} ; latences "
          + ", ".join(f"{c} {f(x, 2)}" for c, x in zip(LATCOLS, o["lat_k8ns"]["ratio"])) + ".",
          "* latences de K8 naturel, natif / Cascade Lake : " + ", ".join(
              f"{c} {f(x, 2)}" for c, x in zip(LATCOLS, o["lat_native"]["ratio"])) + ".", "",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |", "|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        if name == "Avant":
            continue
        L.append(f"| {name} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | {f(z['D'][LANG], 1)} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} |")
    nb = be["neighbours"]
    L += ["", "Voisins dans B-E : " + " ; ".join(f"{k} {NAMES[l]} (BQN devant dans {f(100 * p, 0)} % des variantes)"
                                                  for k, (l, p) in nb.items()) + ".", "",
          "Notes de E de BQN par noyau dans B-E (estimation ponctuelle) : "
          + " ; ".join(f"{k} {f(v, 2)}" for k, v in be["Ek"].items()) + ".", "",
          "## Classement : avant et avec BQN (B-E)\n",
          "| Place | Avant | rang espéré | Avec BQN | rang espéré | écart du rang espéré | écart du score |",
          "|---|---|---|---|---|---|---|"]
    for i in range(len(be["order21"])):
        a = av["order21"][i] if i < len(av["order21"]) else None
        b = be["order21"][i]
        L.append(f"| {i + 1} | {NAMES[a] if a else '—'} | {f(av['exp21'][a], 2) if a else '—'} | {NAMES[b]} | "
                 f"{f(be['exp21'][b], 2)} | {f(o['shift'].get(b), 2) if b != LANG else '—'} | "
                 f"{f(o['shift_ms'].get(b), 2) if b != LANG else '—'} |")
    open(os.path.join(ROOT, "results", "report_bqn.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
