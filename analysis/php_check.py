#!/usr/bin/env python3
"""Ajout de PHP (plan : docs/PHP.md, section 3, poussé avant les mesures).

Mesures de la machine 28 (Emerald Rapids, du même modèle que les machines 3, 11 et 16 ; results/raw_php, étiquette
« php ») : php (PHP 8.5.12, OPcache et JIT tracing), php_def (la CLI par défaut, sans OPcache ni JIT), le C publié (c,
Cascade Lake), le C natif (c_er) et le second témoin (c_gcc_cl, binaire publié de c_gcc). PHP entre dans les données
publiées par le pont du C (analysis/analyze_v2.py, ADDED et ADDED_ER : chaque processus × G(C publié) / G(C machine
28), clé par clé, avec la construction du C qui a produit chaque donnée publiée : c pour les clés de la machine 1, K9
et les latences de K8 naturel, c_er pour K5 et la réplication ; PHP n'a qu'un binaire). Analyse globale de la v3
rejouée (mêmes tirages ; ceux de PHP isolés) pour chaque scénario du plan (3.5) :
* Avant : PHP retiré ; doit reproduire R-E de results/bqn_remark.json (classement publié d'avant) à l'identique.
* P-E (classement publié) : PHP ajouté (pont, grille, empreinte mesurée, C3 mesurée).
* P-direct (information) : temps de la machine 28 sans pont pour les clés de la machine 1 ; pont gardé pour K5, K9 et
  les latences de K8 naturel (sources Emerald Rapids).
* P-hôte : clés de la machine 1 × la médiane, sur ces clés, des facteurs du C ; P-gcc : clés de la machine 1 reliées
  par le second témoin (c_gcc publié / c_gcc_cl machine 28).
* P-défaut (9 cellules naturelles × r(php_def / php)), P-K1arr (K1 naturel et mélangé × r(tableaux associatifs /
  objets)) : rapports appliqués tels qu'ils sont mesurés ; P-C3 (C3 = 0).
* P-cases-bas (A1, A2, A3, A4, A7, B5, E6, F1 et D1 = 0), P-cases-haut (E1 = 1, C5 = B3 = 1/2), P-tout-bas
  (P-cases-bas, P-défaut, P-K1arr, P-C3), P-tout-haut (P-cases-haut).
* P-K7tab (information) : K7 naturel relié par le facteur de K7 optimisé du C (table plate) au lieu de celui de sa
  table chaînée.
* Écart au plan, décidé après avoir vu les données (docs/PHP.md 4.2) : à K2 8 Mio, l'hôte est bimodal ; le pont de
  cette clé prend la médiane des médianes de processus des deux côtés (analyze_v2.BRIDGE_MEDIAN), pour le témoin c comme
  pour le second témoin de P-gcc. P-E-plan (information) : le pont du plan (moyennes géométriques) sur cette clé.
Information : rapport PHP / C de chaque cellule sur la machine 28 (aux deux témoins) ; facteurs du pont par clé avec
les deux témoins ; clés écartées par la borne physique.
Sorties : results/php_check.json, results/report_php.md."""
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
from python_check import kk, gm, LATCOLS, f  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_php")
TAG = "php"
LANG = "php"
NATURAL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
           ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"), ("k7", "natural", ""),
           ("k8", "natural", ""), ("k9", "natural", "")]
K1N, K1S = ("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy")
K1A, K1AS = ("k1", "natural_arr", "energy"), ("k1", "natural_arr_shuffled", "energy")
K7N, K7T = ("k7", "natural", ""), ("k7", "tuned", "")
# cases que seule la FFI tient, mises à 0 comme une FFI vers le C, et D1 (des processus, pas des fils)
CASES_LOW = {"A1": 0.0, "A2": 0.0, "A3": 0.0, "A4": 0.0, "A7": 0.0, "B5": 0.0, "E6": 0.0, "F1": 0.0, "D1": 0.0}
CASES_HIGH = {"E1": 1.0, "C5": 0.5, "B3": 0.5}
M1 = ("k1", "k2", "k3", "k4", "k6", "k7", "k8")  # clés dont la source publiée est la machine 1 (Cascade Lake)
ER_KEYS = ("k5",)  # clés reliées par le C natif (machine 3)


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
    """Scénario avec des cases de PHP remplacées le temps du calcul (aucune de ces cases n'a de dérogation v2)."""
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


def without_php(data, lat, langs, footprint, c3):
    """Avant : PHP retiré de RANKED (liste partagée par tous les modules) et des données, le temps du calcul."""
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


def replaced(data, new):
    """PHP avec certaines clés remplacées par des processus donnés."""
    d = {l: v for l, v in data.items()}
    d[LANG] = {k: (new[k] if k in new else v) for k, v in data[LANG].items()}
    return d


def robust(key, ref, wit, own):
    """Facteur du pont d'une clé : G(référence) / G(témoin), ou, pour une clé de v2.BRIDGE_MEDIAN (hôte bimodal), le même
    rapport recentré par les médianes des médianes de processus du témoin et de PHP (analyze_v2.bridge_added)."""
    fct = gm(ref) / gm(wit)
    if (LANG, key) in v2.BRIDGE_MEDIAN:
        fct *= gm(wit) / v2._med_procs(wit) * v2._med_procs(own) / gm(own)
    return fct


def main():
    assert RANKED[-1] == LANG, "PHP doit être le dernier de RANKED (tirages isolés)"
    raw, rawlat, bad = load_raw()
    # P-E-plan (information) : le pont du plan, moyennes géométriques partout
    saved_bm = set(v2.BRIDGE_MEDIAN)
    v2.BRIDGE_MEDIAN.clear()
    data_plan, lat_plan, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data_plan, lat_plan)
    v2.BRIDGE_MEDIAN.update(saved_bm)
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    fp_detail = json.load(open(os.path.join(ROOT, "results", "footprint_detail.json")))
    assert LANG in c3 and LANG in footprint, "C3 et empreinte de PHP d'abord (tools/c3_measure.py, analysis/footprint.py)"
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2800)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    # témoin de chaque clé (plan 3.2) : c, sauf K5 (c_er) ; un seul binaire de PHP
    wit = {k: ("c_er" if k[0] in ER_KEYS else "c") for k in data[LANG]}
    r_c = {kk(k): ratio(raw[LANG][k], raw["c"][k], rng) for k in sorted(raw[LANG]) if k in raw["c"]}
    r_er = {kk(k): ratio(raw[LANG][k], raw["c_er"][k], rng) for k in sorted(raw[LANG]) if k in raw["c_er"]}
    bridge = {}
    for k in sorted(data[LANG]):
        w = wit[k]
        b = {"witness": w, "c_pub_ms": 1e3 * gm(data["c"][k]), "c_28_ms": 1e3 * gm(raw[w][k]),
             "php_28_ms": 1e3 * gm(raw[LANG][k]), "php_pub_ms": 1e3 * gm(data[LANG][k]),
             "factor": robust(k, data["c"][k], raw[w][k], raw[LANG][k]), "factor_plan": gm(data["c"][k]) / gm(raw[w][k])}
        if (LANG, k) in v2.BRIDGE_MEDIAN:
            b["c_28_med_ms"] = 1e3 * v2._med_procs(raw[w][k])
            b["php_28_med_ms"] = 1e3 * v2._med_procs(raw[LANG][k])
        if k[0] in M1 and k in raw.get("c_gcc_cl", {}) and k in data.get("c_gcc", {}):
            b["factor_gcc"] = robust(k, data["c_gcc"][k], raw["c_gcc_cl"][k], raw[LANG][k])
        bridge[kk(k)] = b
    lat_bridge = {"c_pub_us": (np.array(v2._lat_cols(lat["c"][K8N])) / 1e3).tolist(),
                  "c_28_us": (np.array(v2._lat_cols(rawlat["c"][K8N])) / 1e3).tolist(),
                  "php_28_us": (np.array(v2._lat_cols(rawlat[LANG][K8N])) / 1e3).tolist(),
                  "php_pub_us": (np.array(v2._lat_cols(lat[LANG][K8N])) / 1e3).tolist()}
    # contrôles du pont entre modèles : P-direct, P-hôte, P-gcc (clés de la machine 1)
    m1 = [k for k in data[LANG] if k[0] in M1 and k in raw[LANG] and k in raw["c"]]
    hf = float(np.median([bridge[kk(k)]["factor"] for k in m1]))
    d_direct = replaced(data, {k: [list(p) for p in raw[LANG][k]] for k in m1})
    d_host = replaced(data, {k: [[t * hf for t in p] for p in raw[LANG][k]] for k in m1})
    d_gcc = replaced(data, {k: [[t * bridge[kk(k)]["factor_gcc"] for t in p] for p in raw[LANG][k]]
                            for k in m1 if "factor_gcc" in bridge[kk(k)]})
    # sensibilités : rapports sur le même hôte, appliqués tels qu'ils sont mesurés
    r_def = {k: ratio(raw["php_def"][k], raw[LANG][k], rng) for k in NATURAL}
    r_k1 = ratio(raw[LANG][K1A], raw[LANG][K1N], rng)
    r_k1s = ratio(raw[LANG][K1AS], raw[LANG][K1S], rng)
    dflt = {k: r["ratio"] for k, r in r_def.items()}
    k1arr = {K1N: r_k1["ratio"], K1S: r_k1s["ratio"]}
    c3_0 = {**c3, LANG: 0.0}
    low = dict(dflt)
    for k, r in k1arr.items():
        low[k] = low.get(k, 1.0) * r
    f7 = bridge[kk(K7T)]["factor"] / bridge[kk(K7N)]["factor"]
    plans = {
        "P-E": (data, lat, None, footprint, c3),
        "P-direct": (d_direct, lat, None, footprint, c3),
        "P-hôte": (d_host, lat, None, footprint, c3),
        "P-gcc": (d_gcc, lat, None, footprint, c3),
        "P-défaut": (scaled(data, dflt), lat, None, footprint, c3),
        "P-K1arr": (scaled(data, k1arr), lat, None, footprint, c3),
        "P-C3": (data, lat, None, footprint, c3_0),
        "P-cases-bas": (data, lat, CASES_LOW, footprint, c3),
        "P-cases-haut": (data, lat, CASES_HIGH, footprint, c3),
        "P-tout-bas": (scaled(data, low), lat, CASES_LOW, footprint, c3_0),
        "P-tout-haut": (data, lat, CASES_HIGH, footprint, c3),
        "P-K7tab": (scaled(data, {K7N: f7}), lat, None, footprint, c3),
        "P-E-plan": (data_plan, lat_plan, None, footprint, c3),
    }
    k7_pub = {l: 1e3 * gm(data[l][K7N]) for l in RANKED if K7N in data.get(l, {})}
    out = {"bad": bad, "times_ms": times, "r_php_c": r_c, "r_php_c_er": r_er, "bridge": bridge,
           "lat_bridge": lat_bridge, "bridge_sus": sorted({(l, kk(k), t, b) for l, k, t, b in v2.BRIDGE_SUS}),
           "host_factor": hf, "r_def": {kk(k): r for k, r in r_def.items()}, "r_k1arr": r_k1, "r_k1arr_shuffled": r_k1s,
           "c3": c3[LANG], "footprint": footprint[LANG], "footprint_detail": fp_detail[LANG],
           "k7_factors": {"natural": bridge[kk(K7N)]["factor"], "tuned": bridge[kk(K7T)]["factor"], "P-K7tab": f7},
           "k7_published_ms": k7_pub, "scenarios": {}}
    av = out["scenarios"]["Avant"] = without_php(data, lat, langs, footprint, c3)
    ref = json.load(open(os.path.join(ROOT, "results", "bqn_remark.json")))["scenarios"]["R-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED if l != LANG)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant (R-E) = {out['check_before']:.2e}", flush=True)
    for name, (d, lt, cells, fp, c3s) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, fp, c3s, cells)
        print(f"{name} : PHP {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    pe = out["scenarios"]["P-E"]
    out["shift"] = {l: pe["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
    out["shift_ms"] = {l: pe["ms0"][l] - av["ms0"][l] for l in RANKED if l != LANG}
    json.dump(out, open(os.path.join(ROOT, "results", "php_check.json"), "w"), indent=1, default=float)
    report(out)


def ci(r, d=3):
    return f"{f(r['ratio'], d)} [{f(r['ci'][0], d)}–{f(r['ci'][1], d)}]"


def report(o):
    S = o["scenarios"]
    pe, av = S["P-E"], S["Avant"]
    L = ["# Ajout de PHP : pont par le C et scénarios\n",
         "Plan : `docs/PHP.md`. Mesures : `results/raw_php/` (machine 28, Emerald Rapids, 7 processus par cellule). Code :",
         "`analysis/php_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant (PHP retiré) reproduit le classement publié d'avant (écart maximal "
         f"{o['check_before']:.1e}).\n",
         "## PHP / C sur la machine 28 et pont vers les données publiées\n",
         "Un seul binaire de PHP, face aux deux C : `c` (cible Cascade Lake, témoin des clés de la machine 1, de K9 et des "
         "latences) et `c_er` (natif, témoin de K5 et de la réplication). Facteur gcc : second témoin (`c_gcc` publié / "
         "`c_gcc_cl` sur la machine 28).\n",
         "| Cellule | PHP (ms) | C (ms) | PHP / C [IC 95 %] | PHP / C natif | C publié (ms) | facteur du pont | "
         "facteur gcc | PHP publié (ms) |", "|---|---|---|---|---|---|---|---|---|"]
    for k, r in o["r_php_c"].items():
        b = o["bridge"].get(k)
        re_ = o["r_php_c_er"].get(k)
        L.append(f"| {k} | {f(r['new_ms'], 3)} | {f(r['old_ms'], 3)} | {ci(r)} | {ci(re_) if re_ else '—'} | "
                 + (f"{f(b['c_pub_ms'], 3)} | {f(b['factor'], 3)} | {f(b.get('factor_gcc'), 3)} | {f(b['php_pub_ms'], 3)} |"
                    if b else "— | — | — | — |"))
    lb = o["lat_bridge"]
    kf = o["k7_factors"]
    k2 = o["bridge"].get("k2:tuned:8388608", {})
    L += ["", f"Facteur d'hôte unique de P-hôte (médiane des facteurs du C sur les clés de la machine 1) : "
          f"{f(o['host_factor'], 3)}.", "",
          f"K2 à 8 Mio (hôte bimodal, écart au plan : docs/PHP.md 4.2) : médiane des médianes de processus du C "
          f"{f(k2.get('c_28_med_ms'), 1)} ms (moyenne géométrique {f(k2.get('c_28_ms'), 1)} ms), de PHP "
          f"{f(k2.get('php_28_med_ms'), 1)} ms (moyenne géométrique {f(k2.get('php_28_ms'), 1)} ms) ; facteur du pont "
          f"{f(k2.get('factor'), 3)} (plan : {f(k2.get('factor_plan'), 3)}).", "",
          f"K7 naturel (P-K7tab, information) : facteur de la table chaînée du C {f(kf['natural'], 2)}, de sa table plate "
          f"(K7 optimisé) {f(kf['tuned'], 2)}. Temps publiés de K7 naturel (machine 1 ; PHP relié) : "
          + " ; ".join(f"{NAMES[l]} {f(t / 1e3, 2)} s" for l, t in sorted(o["k7_published_ms"].items(), key=lambda x: x[1])) + ".", "",
          "Latences de K8 naturel (µs, médianes de toutes les répétitions) :", "",
          "| | " + " | ".join(LATCOLS) + " |", "|---" * (len(LATCOLS) + 1) + "|"]
    for name, key in (("PHP, machine 28", "php_28_us"), ("C, machine 28", "c_28_us"), ("C publié", "c_pub_us"),
                      ("PHP publié", "php_pub_us")):
        L.append(f"| {name} | " + " | ".join(f(x, 1) for x in lb[key]) + " |")
    if o["bridge_sus"]:
        L += ["", "Clés reliées écartées par la borne physique : " + ", ".join(f"{l} {k} ({t:.2e} s)" for l, k, t, _ in o["bridge_sus"])]
    fd = o["footprint_detail"]
    L += ["", f"Empreinte de K1 : {f(o['footprint'], 2)} octets par particule (tas de Zend, octets vivants) ; RSS "
          f"{f(fd.get('rss_bytes_per_particle'), 2)} (processus : " + ", ".join(f(x, 2) for x in fd.get("per_process", []))
          + f"). C3 mesurée : {f(o['c3'], 1)}.", "",
          "## Sensibilités (rapports sur le même hôte, appliqués tels quels)\n",
          "* la CLI par défaut, sans OPcache ni JIT (`php_def` / `php`) : " + " ; ".join(
              f"{k} {ci(r)}" for k, r in o["r_def"].items()) + ".",
          f"* K1 en tableaux associatifs : `natural_arr` / `natural` {ci(o['r_k1arr'])} ; `natural_arr_shuffled` / "
          f"`natural_shuffled` {ci(o['r_k1arr_shuffled'])}.", "",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |", "|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        if name == "Avant":
            continue
        L.append(f"| {name} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | {f(z['D'][LANG], 1)} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} |")
    nb = pe["neighbours"]
    L += ["", "Voisins dans P-E : " + " ; ".join(f"{k} {NAMES[l]} (PHP devant dans {f(100 * p, 0)} % des variantes)"
                                                  for k, (l, p) in nb.items()) + ".", "",
          "Notes de E de PHP par noyau dans P-E (estimation ponctuelle) : "
          + " ; ".join(f"{k} {f(v, 2)}" for k, v in pe["Ek"].items()) + ".", "",
          "## Classement : avant et avec PHP (P-E)\n",
          "| Place | Avant | rang espéré | Avec PHP | rang espéré | écart du rang espéré | écart du score |",
          "|---|---|---|---|---|---|---|"]
    for i in range(len(pe["order21"])):
        a = av["order21"][i] if i < len(av["order21"]) else None
        b = pe["order21"][i]
        L.append(f"| {i + 1} | {NAMES[a] if a else '—'} | {f(av['exp21'][a], 2) if a else '—'} | {NAMES[b]} | "
                 f"{f(pe['exp21'][b], 2)} | {f(o['shift'].get(b), 2) if b != LANG else '—'} | "
                 f"{f(o['shift_ms'].get(b), 2) if b != LANG else '—'} |")
    open(os.path.join(ROOT, "results", "report_php.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
