#!/usr/bin/env python3
"""Remarque sur FreePascal (plan : docs/FPC.md, section 5, poussé avant les mesures).

Mesures de la machine 26 (Emerald Rapids, du même modèle que la machine 25 de l'ajout ; results/raw_fpc_rq, étiquette
« fpc_rq ») : le binaire publié (fpc), la 3.2.4-rc2 (fpc_rc2), la branche main (fpc_main, fpc_main_mieux,
fpc_main_scal), les formes de la remarque avec la 3.2.2 (fpc_len, fpc_mieux), K5 en assembleur (fpc_asm,
fpc_main_asm, information) et les témoins C (c, c_er, information). Le classement publié (R-E) prend les errata C2, E4
et F4 de la grille (analysis/capabilities.py, capabilities_v2.py) ; ses données ne changent pas. Les sensibilités
appliquent aux données publiées de FreePascal les rapports r(copie / fpc) de la machine 26, cellule par cellule
(latences de K8 naturel colonne par colonne pour la rc2 et main). Analyse globale de la v3 rejouée (mêmes tirages ;
ceux de FreePascal isolés) pour chaque scénario du plan (5.5) :
* Avant : grille d'avant la remarque (C2 0, E4 1, F4 1) ; doit reproduire F-E de results/fpc_check.json à l'identique.
* R-C2 (Avant, C2 ½), R-E (publié), R-len-K5, R-len, R-mieux, R-mieux-ptr, R-mieux-len, R-rem-3, R-rem-C2-3, R-rc2,
  R-main, R-main-grille, R-main-mieux, R-main-mieux-grille.
* Hors plan, information (ajoutés après avoir vu les latences) : R-rc2-t, R-main-t, R-main-mieux-grille-t, les mêmes
  sans le transfert des latences de K8 naturel.
Information : FreePascal / C sur la machine 26 (témoins) et sur la machine 25 ; K5 en assembleur face au C natif ;
rapports de chaque copie à fpc.
Sorties : results/fpc_remark.json, results/report_fpc_remark.md."""
import contextlib, glob, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import capabilities_v2 as c2  # noqa: E402
import confrontation as cf  # noqa: E402
import fpc_check as fc  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from fortran_check import ratio  # noqa: E402
from python_check import kk, gm, lat_ratio, LATCOLS, f  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_fpc_rq")
TAG = "fpc_rq"
LANG = "fpc"
OLD_GRID = {"C2": (0.0, 0.0), "E4": (1.0, 1.0), "F4": (1.0, 1.0)}  # grille d'avant la remarque (v1, v2)
C2_ONLY = dict(OLD_GRID, C2=(0.5, 0.5))
MAIN_GRID = {"C5": (1.0, 1.0), "D5": (1.0, 1.0)}  # grille de main, en plus des errata (5.5)
K2S = ["16384", "262144", "8388608"]
SCORE = ([("k1", v, "energy") for v in ("natural", "aos", "soa", "natural_shuffled")]
         + [("k2", "tuned", s) for s in K2S]
         + [("k3", v, "") for v in ("rmw_packed", "rmw_padded", "sw_packed", "sw_padded")]
         + [("k4", v, "") for v in ("natural_unsorted", "natural_sorted", "branchless_unsorted")]
         + [("k6", v, q) for v in ("natural", "tuned", "mt") for q in ("q6", "q1")]
         + [("k7", v, "") for v in ("natural", "tuned")]
         + [("k8", v, "") for v in ("natural", "tuned")]
         + [("k5", v, "") for v in ("natural", "tuned")] + [("k9", v, "") for v in ("natural", "tuned", "mt")])
LEN = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
       ("k4", "natural_sorted", ""), ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"),
       ("k7", "natural", "")]
K4B, K4P = ("k4", "branchless_unsorted", ""), ("k4", "branchless_ptr", "")
K5N, K5T, K8T = ("k5", "natural", ""), ("k5", "tuned", ""), ("k8", "tuned", "")
K1S = ("k1", "soa", "energy")
MIEUX = [K4B, K5T, K8T]
SCAL = [K1S, K5T]
COPIES = ["fpc_rc2", "fpc_main", "fpc_len", "fpc_mieux", "fpc_main_mieux", "fpc_main_scal", "fpc_asm", "fpc_main_asm"]
# rapports de la remarque (FreePascal / C, son Emerald Rapids, clang 18) pour la table d'information
REMARK_FC = {"k4:natural_unsorted": 44, "k5:natural": 2.05, "k5:tuned": 8.2, "k7:natural": 13, "k8:natural": 1.35,
             "k8:tuned": 1.13, "k9:natural": 2.6, "k9:tuned": 2.2}


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
    """Cases de FreePascal remplacées le temps du calcul : {cap: (v1, v2)} (v2 par une dérogation de la règle v2)."""
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
        return fc.summary(cf.scenario(data, lat, langs, footprint, c3, "main"), list(RANKED))


def main():
    assert RANKED[-1] == LANG, "FreePascal doit être le dernier de RANKED (tirages isolés)"
    raw, rawlat, bad = load_raw()
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2600)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    base = raw[LANG]
    # rapports de chaque copie au binaire publié, sur le même hôte
    r = {c: {k: ratio(raw[c][k], base[k if k != K4P else K4B], rng) for k in sorted(raw.get(c, {}))} for c in COPIES}
    lat_r = {c: lat_ratio(rawlat[c][K8N], rawlat[LANG][K8N], rng) for c in ("fpc_rc2", "fpc_main")}
    # information : FreePascal / C sur la machine 26, à côté de la machine 25 (results/fpc_check.json)
    m25 = json.load(open(os.path.join(ROOT, "results", "fpc_check.json")))["r_fpc_c"]
    r_fc = {}
    for wit in ("c", "c_er"):
        for k in sorted(raw.get(wit, {})):
            e = {"m26": ratio(base[k], raw[wit][k], rng), "m25": m25.get(kk(k), {}).get("ratio"),
                 "remark": REMARK_FC.get(kk(k)), "witness": wit}
            if k in raw.get("fpc_mieux", {}):
                e["mieux_m26"] = ratio(raw["fpc_mieux"][k], raw[wit][k], rng)
            if k in raw.get("fpc_len", {}):
                e["len_m26"] = ratio(raw["fpc_len"][k], raw[wit][k], rng)
            if k in raw.get("fpc_main", {}):
                e["main_m26"] = ratio(raw["fpc_main"][k], raw[wit][k], rng)
            r_fc[kk(k)] = e
    asm = {c: ratio(raw[c][K5T], raw["c_er"][K5T], rng) for c in ("fpc_asm", "fpc_main_asm", LANG, "fpc_mieux",
                                                                  "fpc_main_mieux")}
    # facteurs des scénarios
    rv = lambda c, k: r[c][k]["ratio"]  # noqa: E731
    f_len = {k: rv("fpc_len", k) for k in LEN}
    f_mieux = {k: rv("fpc_mieux", k) for k in MIEUX}
    f_mieux_ptr = {**f_mieux, K4B: rv("fpc_mieux", K4P)}
    f_rc2 = {k: rv("fpc_rc2", k) for k in SCORE}
    f_main = {k: rv("fpc_main", k) for k in SCORE}
    best, best_src = {}, {}
    for k in SCORE:
        cand = {"fpc_main": rv("fpc_main", k)}
        if k in raw.get("fpc_main_mieux", {}):
            cand["fpc_main_mieux"] = rv("fpc_main_mieux", k)
        if k == K4B and K4P in raw.get("fpc_main_mieux", {}):
            cand["fpc_main_mieux:branchless_ptr"] = rv("fpc_main_mieux", K4P)
        if k in SCAL and k in raw.get("fpc_main_scal", {}):
            cand["fpc_main_scal"] = rv("fpc_main_scal", k)
        src = min(cand, key=cand.get)
        best[k], best_src[kk(k)] = cand[src], src
    l_rc2, l_main = lat_r["fpc_rc2"]["ratio"], lat_r["fpc_main"]["ratio"]
    plans = {
        "R-C2": (data, lat, C2_ONLY),
        "R-E": (data, lat, None),
        "R-len-K5": (fc.scaled(data, {K5N: f_len[K5N]}), lat, None),
        "R-len": (fc.scaled(data, f_len), lat, None),
        "R-mieux": (fc.scaled(data, f_mieux), lat, None),
        "R-mieux-ptr": (fc.scaled(data, f_mieux_ptr), lat, None),
        "R-mieux-len": (fc.scaled(data, {**f_len, **f_mieux}), lat, None),
        "R-rem-3": (fc.scaled(data, f_mieux), lat, OLD_GRID),
        "R-rem-C2-3": (fc.scaled(data, f_mieux), lat, C2_ONLY),
        "R-rc2": (fc.scaled(data, f_rc2), fc.with_lat(lat, l_rc2), None),
        "R-main": (fc.scaled(data, f_main), fc.with_lat(lat, l_main), None),
        "R-main-grille": (fc.scaled(data, f_main), fc.with_lat(lat, l_main), MAIN_GRID),
        "R-main-mieux": (fc.scaled(data, best), fc.with_lat(lat, l_main), None),
        "R-main-mieux-grille": (fc.scaled(data, best), fc.with_lat(lat, l_main), MAIN_GRID),
        # hors plan, information (ajoutés après avoir vu les latences, docs/FPC.md 5.9) : temps seuls, latences de K8
        # naturel publiées gardées (les queues p99,9 et max de la rc2 et de main sortent plus hautes, très dispersées)
        "R-rc2-t": (fc.scaled(data, f_rc2), lat, None),
        "R-main-t": (fc.scaled(data, f_main), lat, None),
        "R-main-mieux-grille-t": (fc.scaled(data, best), lat, MAIN_GRID),
    }
    out = {"bad": bad, "times_ms": times, "r": {c: {kk(k): v for k, v in d.items()} for c, d in r.items()},
           "lat_r": lat_r, "r_fpc_c": r_fc, "asm": asm, "best_src": best_src,
           "factors": {"len": {kk(k): v for k, v in f_len.items()}, "mieux": {kk(k): v for k, v in f_mieux.items()},
                       "mieux_ptr": {kk(k): v for k, v in f_mieux_ptr.items()},
                       "main_best": {kk(k): v for k, v in best.items()}},
           "scenarios": {}}
    av = out["scenarios"]["Avant"] = run(data, lat, langs, footprint, c3, OLD_GRID)
    ref = json.load(open(os.path.join(ROOT, "results", "fpc_check.json")))["scenarios"]["F-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant (F-E) = {out['check_before']:.2e}", flush=True)
    for name, (d, lt, cells) in plans.items():
        cells = dict(MAIN_GRID) if cells is MAIN_GRID else cells
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : FreePascal {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    re_ = out["scenarios"]["R-E"]
    out["shift"] = {l: re_["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
    out["shift_ms"] = {l: re_["ms0"][l] - av["ms0"][l] for l in RANKED if l != LANG}
    json.dump(out, open(os.path.join(ROOT, "results", "fpc_remark.json"), "w"), indent=1, default=float)
    report(out)


def ci(x, d=3):
    return f"{f(x['ratio'], d)} [{f(x['ci'][0], d)}–{f(x['ci'][1], d)}]"


def report(o):
    S = o["scenarios"]
    L = ["# Remarque sur FreePascal : errata, formes de la remarque, 3.2.4-rc2 et branche main", "",
         "Plan : `docs/FPC.md`, section 5. Mesures : `results/raw_fpc_rq/` (machine 26, Emerald Rapids, 7 processus par "
         "cellule). Code : `analysis/fpc_remark.py`. Processus rejetés : "
         + (", ".join(f"{a} {b}" for a, b, _ in o["bad"]) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant (grille d'avant la remarque) reproduit F-E de `results/fpc_check.json` (écart "
         f"maximal {o['check_before']:.1e}).", "",
         "## Rapports au binaire publié (machine 26)", "",
         "Moyennes géométriques des médianes de processus ; intervalles à 95 % par bootstrap. `branchless_ptr` est "
         "rapporté à `branchless_unsorted` du binaire publié.", "",
         "| Cellule | publié (ms) | 3.2.4-rc2 | main | Length (3.2.2) | mieux (3.2.2) | main, Length et mieux | main sans -Sv |",
         "|---|---|---|---|---|---|---|---|"]
    keys = SCORE + [K4P]
    for k in keys:
        key = kk(k)
        row = [key, f(o["times_ms"][LANG].get(kk(k if k != K4P else K4B)), 3)]
        for c in ("fpc_rc2", "fpc_main", "fpc_len", "fpc_mieux", "fpc_main_mieux", "fpc_main_scal"):
            x = o["r"].get(c, {}).get(key)
            row.append(ci(x) if x else "")
        L.append("| " + " | ".join(row) + " |")
    lr = o["lat_r"]
    L += ["", "Latences de K8 naturel (rapports, colonne par colonne) : " + " ; ".join(
        f"{c} " + ", ".join(f"{n} {f(x, 2)}" for n, x in zip(LATCOLS, lr[c]["ratio"])) for c in lr) + ".", "",
          "Meilleure forme sous main (R-main-mieux) : " + " ; ".join(
              f"{k} {s}" for k, s in o["best_src"].items() if s != "fpc_main") + " (les autres cellules : `fpc_main`).", "",
          "## FreePascal / C (information)", "",
          "| Cellule | témoin | machine 26 [IC 95 %] | machine 25 | remarque (clang 18) | formes de la remarque, machine 26 | main, machine 26 |",
          "|---|---|---|---|---|---|---|"]
    for k, e in o["r_fpc_c"].items():
        alt = e.get("mieux_m26") or e.get("len_m26")
        L.append(f"| {k} | {e['witness']} | {ci(e['m26'], 2)} | {f(e['m25'], 2)} | {f(e['remark'], 2)} | "
                 f"{ci(alt, 2) if alt else ''} | {ci(e['main_m26'], 2) if e.get('main_m26') else ''} |")
    a = o["asm"]
    L += ["", "K5 tuned face au C natif (`c_er`) : " + " ; ".join(
        f"{c} {ci(x, 2)}" for c, x in a.items()) + " (`fpc_asm`, `fpc_main_asm` : assembleur en ligne, hors des règles "
          "du banc).", "",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)", "",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |", "|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        label = f"{name} (hors plan)" if name.endswith("-t") else name
        L.append(f"| {label} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | "
                 f"{f(z['D'][LANG], 1)} | {f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} |")
    re_ = S["R-E"]
    nb = re_["neighbours"]
    L += ["", "Voisins dans R-E : " + " ; ".join(f"{k} {NAMES[l]} (FreePascal devant dans {f(100 * p, 0)} % des variantes)"
                                                 for k, (l, p) in nb.items()) + ".", "",
          "Écarts des autres langages entre Avant et R-E : rang espéré "
          + f"{f(min(o['shift'].values()), 3)} à {f(max(o['shift'].values()), 3)} ; score "
          + f"{f(min(o['shift_ms'].values()), 3)} à {f(max(o['shift_ms'].values()), 3)}.", ""]
    open(os.path.join(ROOT, "results", "report_fpc_remark.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
