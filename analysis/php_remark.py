#!/usr/bin/env python3
"""Remarque sur PHP (plan : docs/PHP.md, section 5, poussé avant les mesures ; ce code est écrit pendant la campagne,
avant tout résultat).

Mesures appariées de la machine 29 (results/raw_php_rq, étiquette « php_rq ») : le banc publié (php, PHP 8.5.12), la
copie bench/php_rq (K1 par indice, sans variable intermédiaire ; K1 après gc_disable()) et le banc publié sous 8.3.36,
8.4.27, 8.5.13RC1 et 8.6.0RC5 (K9 natural et tuned). Rapports r(cellule / cellule publiée de php), moyennes géométriques
des médianes de processus, intervalles à 95 % par bootstrap, appliqués aux processus publiés de PHP (reliés par le
pont), cellule par cellule.
Scénarios (analyse globale de la v3 rejouée, mêmes tirages) :
* Avant : le classement publié ; doit reproduire P-E de results/php_check.json à l'identique.
* R-K1idx (sensibilité) : K1 natural et natural_shuffled écrits par indice ($ps[$i]->vx).
* R-K1gc (information) : K1 natural et natural_shuffled après gc_disable().
* R-K9-83 (information) : K9 natural sous PHP 8.3.36, dont le JIT compile le stencil.
* R-tout (information) : R-K1gc et R-K9-83 ; R-tout-idx (information) : R-K1idx et R-K9-83.
Sorties : results/php_remark.json, results/report_php_remark.md. Le classement publié ne change pas."""
import glob, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import php_check as pc  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from fortran_check import ratio  # noqa: E402
from python_check import kk, gm, f  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_php_rq")
TAG = "php_rq"
LANG = "php"
K1N, K1S = ("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy")
K1I, K1IS = ("k1", "natural_idx", "energy"), ("k1", "natural_idx_shuffled", "energy")
K1G, K1GS = ("k1", "natural_gcoff", "energy"), ("k1", "natural_gcoff_shuffled", "energy")
K9N, K9T = ("k9", "natural", ""), ("k9", "tuned", "")
VERSIONS = {"php83": "8.3.36", "php84": "8.4.27", "php8513rc1": "8.5.13RC1", "php86rc5": "8.6.0RC5"}


def load_raw():
    d, bad = defaultdict(dict), []
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
    return d, bad


def run_parts(data, lat, langs, footprint, c3):
    """pc.run sans changement de case, plus les parties D1 à D4 du code par défaut de PHP (estimation ponctuelle)."""
    s = cf.scenario(data, lat, langs, footprint, c3, "main")
    z = pc.summary(s, list(RANKED))
    i = s["A"].idx[LANG]
    z["Dk"] = {k: float(s["S0"][k][i]) for k in ("D1", "D2", "D3", "D4")}
    return z


def main():
    assert RANKED[-1] == LANG, "PHP doit être le dernier de RANKED (tirages isolés)"
    raw, bad = load_raw()
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2900)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    pub = raw["php"]
    r = {"php_rq:" + kk(K1N): ratio(raw["php_rq"][K1N], pub[K1N], rng)}  # contrôle de la copie (attendu 1)
    for k, base in ((K1I, K1N), (K1IS, K1S), (K1G, K1N), (K1GS, K1S)):
        r["php_rq:" + kk(k)] = ratio(raw["php_rq"][k], pub[base], rng)
    for impl in VERSIONS:
        for k in (K9N, K9T):
            r[f"{impl}:{kk(k)}"] = ratio(raw[impl][k], pub[k], rng)
    rv = lambda name: r[name]["ratio"]  # noqa: E731
    idx = {K1N: rv("php_rq:" + kk(K1I)), K1S: rv("php_rq:" + kk(K1IS))}
    gco = {K1N: rv("php_rq:" + kk(K1G)), K1S: rv("php_rq:" + kk(K1GS))}
    k983 = {K9N: rv("php83:" + kk(K9N))}
    plans = {"R-K1idx": idx, "R-K1gc": gco, "R-K9-83": k983, "R-tout": {**gco, **k983}, "R-tout-idx": {**idx, **k983}}
    out = {"bad": bad, "times_ms": times, "r": r,
           "factors": {n: {kk(k): v for k, v in fac.items()} for n, fac in plans.items()}, "scenarios": {}}
    av = out["scenarios"]["Avant"] = run_parts(data, lat, langs, footprint, c3)
    ref = json.load(open(os.path.join(ROOT, "results", "php_check.json")))["scenarios"]["P-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié (P-E) = {out['check_before']:.2e}", flush=True)
    out["shift"], out["shift_ms"] = {}, {}
    for name, fac in plans.items():
        z = out["scenarios"][name] = run_parts(pc.scaled(data, fac), lat, langs, footprint, c3)
        out["shift"][name] = {l: z["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
        out["shift_ms"][name] = {l: z["ms0"][l] - av["ms0"][l] for l in RANKED if l != LANG}
        print(f"{name} : PHP {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}, "
              f"devant BQN {100 * z['prec_l']['bqn']:.0f} %, devant JavaScript {100 * z['prec_l']['js']:.0f} %", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "php_remark.json"), "w"), indent=1, default=float)
    report(out)


def ci(x, d=3):
    return f"{f(x['ratio'], d)} [{f(x['ci'][0], d)}–{f(x['ci'][1], d)}]"


def report(o):
    S = o["scenarios"]
    av = S["Avant"]
    L = ["# Remarque sur PHP : rapports appariés et scénarios\n",
         "Plan : `docs/PHP.md`, section 5. Mesures : `results/raw_php_rq/` (machine 29, Emerald Rapids, 7 processus par "
         "cellule). Code : `analysis/php_remark.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit P-E de `results/php_check.json` (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (machine 29)\n",
         "Moyennes géométriques des médianes de processus ; intervalles à 95 % par bootstrap. Chaque cellule est rapportée à "
         "la cellule du banc publié (`php`, PHP 8.5.12) : `natural` pour `natural_idx` et `natural_gcoff`, "
         "`natural_shuffled` pour leurs versions dans le désordre.\n",
         "| Cellule | publié (ms) | cellule (ms) | rapport [IC à 95 %] |", "|---|---|---|---|"]
    for name, x in o["r"].items():
        L.append(f"| {name} | {f(x['old_ms'], 1)} | {f(x['new_ms'], 1)} | {ci(x)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % | devant BQN | devant JavaScript | "
          "écart à BQN | plus grand écart de rang espéré des autres |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        pl = z["prec_l"]
        sh = o["shift"].get(name)
        big = max(sh.items(), key=lambda kv: abs(kv[1])) if sh else None
        L.append(f"| {name} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | "
                 f"{f(z['D'][LANG], 1)} | {f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} | "
                 f"{f(100 * pl['bqn'], 0)} % | {f(100 * pl['js'], 0)} % | {f(z['ms0']['bqn'] - z['ms0'][LANG], 2)} | "
                 + (f"{NAMES[big[0]]} {f(big[1], 2)}" if big else "—") + " |")
    L += ["", "Code par défaut de PHP par partie (D1 code naturel, D2 empreinte et désordre, D3 queues, D4 hiérarchie) : "
          + " ; ".join(f"{n} " + ", ".join(f"{k} {f(v, 3)}" for k, v in (z.get("Dk") or {}).items())
                       for n, z in S.items()) + "."]
    open(os.path.join(ROOT, "results", "report_php_remark.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
