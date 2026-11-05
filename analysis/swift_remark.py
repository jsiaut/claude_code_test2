#!/usr/bin/env python3
"""Remarque sur Swift (plan : docs/SWIFT.md, section 5.3, poussé avant les mesures).

Mesures de la machine 24 (Emerald Rapids, du même modèle que les machines 3, 11 et 16 ; results/raw_swift_er,
étiquette « swift_er ») : swift_er et c_er (constructions natives, comme les binaires recompilés sur la machine 3),
swift et c (binaires publiés, Cascade Lake), swift_ub (K4 natural_w_unsorted, K8 natural_ub). Le classement publié
(R-E) prend les errata D4 et E4 de la grille (analysis/capabilities.py, capabilities_v2.py) et le pont des clés venues
d'Emerald Rapids par la machine 24 (analysis/analyze_v2.py, ADDED_ER, BRIDGE_ER). Analyse globale de la v3 rejouée
(mêmes tirages ; ceux de Swift isolés) pour chaque scénario du plan :
* Avant : grille et pont d'avant la remarque ; doit reproduire S-E de results/swift_check.json à l'identique.
* R-D4, R-E4, R-grille (D4 et E4), R-pont (pont de la machine 24 seul), R-E (publié : R-grille + R-pont).
* R-E4-0, R-D4-½ (lectures de la remarque), R-K7 (K7 naturel relié par le facteur de K7 optimisé du C), R-UB (K8
  naturel × min(1, r(natural_ub / natural))), R-hôte (clés de la machine 1 par le facteur d'hôte médian des autres
  langages, comme S-hôte), R-Ou, R-cases-bas, R-cases-haut (sensibilités de l'ajout appliquées à R-E).
Information : rapports Swift / C de chaque cellule sur la machine 24 et sur la machine 23 ; Q1 avec le code de Cascade
Lake ; K4 avec &+= ; latences de K8.
Sorties : results/swift_remark.json, results/report_swift_remark.md."""
import contextlib, glob, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import capabilities_v2 as c2  # noqa: E402
import confrontation as cf  # noqa: E402
import swift_check as sc  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from fortran_check import ratio  # noqa: E402
from python_check import kk, gm, lat_ratio, LATCOLS, f  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_swift_er")
TAG = "swift_er"
LANG = "swift"
OLD_GRID = {"D4": (0.0, 0.0), "E4": (0.0, 0.0)}  # grille d'avant la remarque (v1, v2)
K7N, K7T = ("k7", "natural", ""), ("k7", "tuned", "")
K4N, K4W = ("k4", "natural_unsorted", ""), ("k4", "natural_w_unsorted", "")
K8UB = ("k8", "natural_ub", "")
Q1T = ("k6", "tuned", "q1")


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


@contextlib.contextmanager
def grid(cells):
    """Cases de Swift remplacées le temps du calcul : {cap: (v1, v2)} (v2 par une surcharge de la règle v2)."""
    saved = {}
    try:
        for cap, (a, b) in (cells or {}).items():
            saved[cap] = (v2.MATRIX[LANG][cap], c2.V2_OVERRIDES.get((LANG, cap)))
            v2.MATRIX[LANG][cap] = (a, saved[cap][0][1])
            if b == a:
                c2.V2_OVERRIDES.pop((LANG, cap), None)
            else:
                c2.V2_OVERRIDES[(LANG, cap)] = (b, "scénario")
        yield
    finally:
        for cap, (m, o) in saved.items():
            v2.MATRIX[LANG][cap] = m
            if o is None:
                c2.V2_OVERRIDES.pop((LANG, cap), None)
            else:
                c2.V2_OVERRIDES[(LANG, cap)] = o


def run(data, lat, langs, footprint, c3, cells=None):
    with grid(cells):
        return sc.summary(cf.scenario(data, lat, langs, footprint, c3, "main"), list(RANKED))


def dataset(er):
    """Données publiées avec le pont de la machine 24 (er) ou celui de la machine 23 seul (avant la remarque)."""
    v2.BRIDGE_ER = er
    try:
        data, lat, *_ = v2.dataset_main(transfers=True)
        v2.align_lat(data, lat)
        return data, lat
    finally:
        v2.BRIDGE_ER = True


def c_factor(data, raw23, key):
    return gm(data["c"][key]) / gm(raw23["c"][key])


def main():
    assert RANKED[-1] == LANG, "Swift doit être le dernier de RANKED (tirages isolés)"
    raw, rawlat, bad = load_raw()
    raw23, rawlat23, _ = sc.load_raw()
    data, lat = dataset(True)
    data0, lat0 = dataset(False)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2400)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    # rapports Swift / C : machine 24 (constructions natives et binaires publiés) et machine 23
    r_er = {kk(k): ratio(raw["swift_er"][k], raw["c_er"][k], rng) for k in sorted(raw["swift_er"]) if k in raw["c_er"]}
    r_pub = {kk(k): ratio(raw["swift"][k], raw["c"][k], rng) for k in sorted(raw["swift"]) if k in raw["c"]}
    r_23 = {kk(k): ratio(raw23[LANG][k], raw23["c"][k], rng) for k in sorted(raw23[LANG]) if k in raw23["c"]}
    lat_er = {"swift_us": (np.array(v2._lat_cols(rawlat["swift"][K8N])) / 1e3).tolist(),
              "c_us": (np.array(v2._lat_cols(rawlat["c"][K8N])) / 1e3).tolist(),
              "ratio": lat_ratio(rawlat["swift"][K8N], rawlat["c"][K8N], rng)}
    lat_23 = lat_ratio(rawlat23[LANG][K8N], rawlat23["c"][K8N], rng)
    # pont : valeurs publiées de Swift avant et après (clés venues d'Emerald Rapids)
    bridge = {}
    for k in sorted(data[LANG]):
        if k[0] in ("k5", "k9"):
            bridge[kk(k)] = {"c_pub_ms": 1e3 * gm(data["c"][k]), "swift_avant_ms": 1e3 * gm(data0[LANG][k]),
                             "swift_apres_ms": 1e3 * gm(data[LANG][k])}
    lat_bridge = {"c_pub_us": (np.array(v2._lat_cols(lat["c"][K8N])) / 1e3).tolist(),
                  "swift_avant_us": (np.array(v2._lat_cols(lat0[LANG][K8N])) / 1e3).tolist(),
                  "swift_apres_us": (np.array(v2._lat_cols(lat[LANG][K8N])) / 1e3).tolist()}
    # information : K4 avec &+=, K8 en UniqueBox (swift_ub), Q1 avec le code de Cascade Lake
    r_k4w = ratio(raw["swift_ub"][K4W], raw["swift_ub"][K4N], rng)
    r_k4w_c = ratio(raw["swift_ub"][K4W], raw["c_er"][K4N], rng) if K4N in raw["c_er"] else None
    r_ub = ratio(raw["swift_ub"][K8UB], raw["swift_ub"][K8N], rng)
    l_ub = lat_ratio(rawlat["swift_ub"][K8UB], rawlat["swift_ub"][K8N], rng)
    r_ub_c = ratio(raw["swift_ub"][K8UB], raw["c"][K8N], rng)
    # sensibilités
    f7 = c_factor(data, raw23, K7T) / c_factor(data, raw23, K7N)  # facteur de la table plate au lieu de la chaînée
    d_k7 = sc.scaled(data, {K7N: f7})
    ub = {K8N: min(1.0, r_ub["ratio"])}
    lat_ub = [min(1.0, x) for x in l_ub["ratio"]]
    hf, htable = sc.host_factors()
    dh = {l: v for l, v in data.items()}
    dh[LANG] = {k: ([[t * hf["machine 1"] for t in p] for p in raw23[LANG][k]] if sc.source(k) == "machine 1" else v)
                for k, v in data[LANG].items()}
    sens23 = json.load(open(os.path.join(ROOT, "results", "swift_check.json")))["sens_factors"]
    ou = {tuple(x if x != "" else "" for x in (k.split(":") + [""])[:3]): v for k, v in sens23["S-Ou"].items()}
    ou = {(k[0], k[1], k[2]): v for k, v in ou.items()}
    low = {c: (v, v) for c, v in sc.CASES_LOW.items()}
    high = {c: (v, v) for c, v in sc.CASES_HIGH.items()}
    plans = {
        "R-D4": (data0, lat0, {"E4": OLD_GRID["E4"]}),
        "R-E4": (data0, lat0, {"D4": OLD_GRID["D4"]}),
        "R-grille": (data0, lat0, None),
        "R-pont": (data, lat, OLD_GRID),
        "R-E": (data, lat, None),
        "R-E4-0": (data, lat, {"E4": (0.0, 0.0)}),
        "R-D4-½": (data, lat, {"D4": (0.5, 0.5)}),
        "R-K7": (d_k7, lat, None),
        "R-UB": (sc.scaled(data, ub), sc.with_lat(lat, lat_ub), None),
        "R-hôte": (dh, lat, None),
        "R-Ou": (sc.scaled(data, ou), lat, None),
        "R-cases-bas": (data, lat, low),
        "R-cases-haut": (data, lat, high),
    }
    out = {"bad": bad, "times_ms": times, "r_er": r_er, "r_pub": r_pub, "r_23": r_23, "lat_er": lat_er,
           "lat_23": lat_23, "bridge": bridge, "lat_bridge": lat_bridge,
           "bridge_sus": sorted({(l, kk(k), t, b) for l, k, t, b in v2.BRIDGE_SUS}),
           "r_k4w": r_k4w, "r_k4w_c": r_k4w_c, "r_ub": r_ub, "lat_ub": l_ub, "r_ub_c": r_ub_c,
           "k7_factors": {"natural": c_factor(data, raw23, K7N), "tuned": c_factor(data, raw23, K7T), "R-K7": f7},
           "host_factors": hf, "scenarios": {}}
    av = out["scenarios"]["Avant"] = run(data0, lat0, langs, footprint, c3, OLD_GRID)
    ref = json.load(open(os.path.join(ROOT, "results", "swift_check.json")))["scenarios"]["S-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant (S-E) = {out['check_before']:.2e}", flush=True)
    for name, (d, lt, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : Swift {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    re_ = out["scenarios"]["R-E"]
    out["shift"] = {l: re_["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
    json.dump(out, open(os.path.join(ROOT, "results", "swift_remark.json"), "w"), indent=1, default=float)
    report(out)


def report(o):
    S = o["scenarios"]
    L = ["# Remarque sur Swift : pont par la machine 24 (Emerald Rapids), errata et scénarios", "",
         "Plan : `docs/SWIFT.md`, section 5. Mesures : `results/raw_swift_er/` (machine 24, Emerald Rapids, 7 processus "
         "par cellule). Code : `analysis/swift_remark.py`. Processus rejetés : "
         + (", ".join(f"{a} {b}" for a, b, _ in o["bad"]) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant (grille et pont d'avant la remarque) reproduit S-E de `results/swift_check.json` "
         f"(écart maximal {o['check_before']:.1e}).", "",
         "## Swift / C : machine 24 (constructions natives) et machine 23 (Cascade Lake)", "",
         "| Cellule | Swift ER (ms) | C ER (ms) | Swift / C, machine 24 [IC 95 %] | Swift / C, machine 23 [IC 95 %] |",
         "|---|---|---|---|---|"]
    for k, r in sorted(o["r_er"].items()):
        r23 = o["r_23"].get(k)
        L.append(f"| {k} | {f(r['new_ms'], 3)} | {f(r['old_ms'], 3)} | {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–"
                 f"{f(r['ci'][1], 3)}] | " + (f"{f(r23['ratio'], 3)} [{f(r23['ci'][0], 3)}–{f(r23['ci'][1], 3)}]"
                                             if r23 else "—") + " |")
    L += ["", "Binaires publiés (Cascade Lake) exécutés sur la machine 24 (pont de K9 et des latences de K8 ; Q1 pour "
          "information) :", "", "| Cellule | Swift (ms) | C (ms) | Swift / C [IC 95 %] |", "|---|---|---|---|"]
    for k, r in sorted(o["r_pub"].items()):
        L.append(f"| {k} | {f(r['new_ms'], 3)} | {f(r['old_ms'], 3)} | {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–"
                 f"{f(r['ci'][1], 3)}] |")
    le = o["lat_er"]
    L += ["", "Latences de K8 naturel (µs, médianes de toutes les répétitions) :", "",
          "| | " + " | ".join(LATCOLS) + " |", "|---|" + "---|" * 5,
          "| Swift, machine 24 (binaire publié) | " + " | ".join(f(x, 1) for x in le["swift_us"]) + " |",
          "| C, machine 24 (binaire publié) | " + " | ".join(f(x, 1) for x in le["c_us"]) + " |",
          "| Swift / C, machine 24 | " + " | ".join(f(x, 2) for x in le["ratio"]["ratio"]) + " |",
          "| Swift / C, machine 23 | " + " | ".join(f(x, 2) for x in o["lat_23"]["ratio"]) + " |",
          "", "## Le pont, avant et après (valeurs publiées de Swift)", "",
          "| Clé | C publié (ms) | Swift, pont de la machine 23 (ms) | Swift, pont de la machine 24 (ms) |",
          "|---|---|---|---|"]
    for k, b in sorted(o["bridge"].items()):
        L.append(f"| {k} | {f(b['c_pub_ms'], 3)} | {f(b['swift_avant_ms'], 3)} | {f(b['swift_apres_ms'], 3)} |")
    lb = o["lat_bridge"]
    L += ["", "| Latences de K8 (µs) | " + " | ".join(LATCOLS) + " |", "|---|" + "---|" * 5,
          "| C publié | " + " | ".join(f(x, 1) for x in lb["c_pub_us"]) + " |",
          "| Swift, pont de la machine 23 | " + " | ".join(f(x, 1) for x in lb["swift_avant_us"]) + " |",
          "| Swift, pont de la machine 24 | " + " | ".join(f(x, 1) for x in lb["swift_apres_us"]) + " |", "",
          "## Information", "",
          f"* K4 naturel avec `&+=` (`swift_ub`, cible cascadelake) / avec `+=` : {f(o['r_k4w']['ratio'], 3)} "
          f"[{f(o['r_k4w']['ci'][0], 3)}–{f(o['r_k4w']['ci'][1], 3)}] ({f(o['r_k4w']['new_ms'], 2)} contre "
          f"{f(o['r_k4w']['old_ms'], 2)} ms)" + (f" ; / C natif : {f(o['r_k4w_c']['ratio'], 3)}" if o["r_k4w_c"] else "") + ".",
          f"* K8 naturel en `UniqueBox` / classe : {f(o['r_ub']['ratio'], 3)} [{f(o['r_ub']['ci'][0], 3)}–"
          f"{f(o['r_ub']['ci'][1], 3)}] ; / C (binaire publié) : {f(o['r_ub_c']['ratio'], 3)} ; latences "
          + ", ".join(f"{c} {f(x, 2)}" for c, x in zip(LATCOLS, o["lat_ub"]["ratio"])) + ".",
          f"* Facteurs du pont de K7 (C publié / C machine 23) : naturel {f(o['k7_factors']['natural'], 3)}, optimisé "
          f"{f(o['k7_factors']['tuned'], 3)} ; R-K7 multiplie K7 naturel de Swift par {f(o['k7_factors']['R-K7'], 3)}.",
          "", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)", "",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |", "|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        L.append(f"| {name} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | "
                 f"{f(z['D'][LANG], 1)} | {f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} |")
    re_ = S["R-E"]
    nb = re_["neighbours"]
    L += ["", "Voisins dans R-E : " + " ; ".join(f"{k} {NAMES[v[0]]} (Swift devant dans {f(100 * v[1], 0)} % des "
                                                f"variantes)" for k, v in nb.items()) + ".", "",
          "## Classement : avant la remarque et publié (R-E)", "",
          "| Place | Avant | rang espéré | R-E | rang espéré | score R-E |", "|---|---|---|---|---|---|"]
    av = S["Avant"]
    for i, (a, b) in enumerate(zip(av["order21"], re_["order21"])):
        L.append(f"| {i + 1} | {NAMES[a]} | {f(av['exp21'][a], 2)} | {NAMES[b]} | {f(re_['exp21'][b], 2)} | "
                 f"{f(re_['ms0'][b], 1)} |")
    open(os.path.join(ROOT, "results", "report_swift_remark.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
