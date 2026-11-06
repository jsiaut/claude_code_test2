#!/usr/bin/env python3
"""Remarque sur BQN (plan : docs/BQN.md, section 5, poussé avant les mesures).

Mesures appariées de la machine 27 (results/raw_bqn_rq, étiquette « bqn_rq ») : les constructions publiées (bqn, cible
Cascade Lake ; bqn_er, native) et la copie bench/bqn_rq/ms.bqn (bqn_rq, bqn_er_rq), sur les cellules qu'elle change et
deux témoins. Rapports r(copie / publié), moyennes géométriques des médianes de processus, appliqués aux données
publiées de BQN (reliées par le pont), cellule par cellule.
Scénarios (analyse globale de la v3 rejouée, mêmes tirages) :
* Avant : le classement publié (grille d'avant : A3 = A6 = 1/2 ; sans correction) ; doit reproduire B-E de
  results/bqn_check.json à l'identique.
* R-grille (A3 = A6 = 0), R-K9 (somme de contrôle hors chrono : K9 natural, tuned_flat, mt_flat), R-K7 (K7 naturel en
  idiome de la documentation) : un erratum à la fois.
* R-E (publié) : les trois errata.
* R-blocs : R-E et les formes en blocs (K1 aos et soa, K4 branchless_unsorted, K6 tuned et mt, K9 tuned et mt).
* R-C5 (C5 = 1/2), R-blocs-C5 ; R-K7map (information : R-E sans l'erratum de K7) ; R-K7tab (information : R-E,
  K7 naturel relié par le facteur de la table plate du C, comme B-K7tab de docs/BQN.md 4.4).
Sorties : results/bqn_remark.json, results/report_bqn_remark.md ; puis, pour le classement publié, les rapports des
errata dans results/transfers.json (« ratios_added » : main pour la cible Cascade Lake, m3 pour la réplication)."""
import contextlib, glob, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import capabilities_v2 as c2  # noqa: E402
import confrontation as cf  # noqa: E402
import bqn_check as bc  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from fortran_check import ratio  # noqa: E402
from python_check import kk, gm, f  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_bqn_rq")
TAG = "bqn_rq"
LANG = "bqn"
K1A, K1S_, K1N = ("k1", "aos", "energy"), ("k1", "soa", "energy"), ("k1", "natural", "energy")
K4B = ("k4", "branchless_unsorted", "")
Q6T, Q1T, Q6M, Q1M = ("k6", "tuned", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1")
K7N = ("k7", "natural", "")
K9N, K9T, K9M = ("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")
K9TF, K9MF = ("k9", "tuned_flat", ""), ("k9", "mt_flat", "")
K5T = ("k5", "tuned", "")
BLOCKS = [K1A, K1S_, K4B, Q6T, Q1T, Q6M, Q1M, K9T, K9M]
CONTROLS = [K1N, K5T]
OLD_GRID = {"A3": (0.5, 0.5), "A6": (0.5, 0.5)}
C5_HALF = {"C5": (0.5, 0.5)}
PAIRS = {"main": ("bqn", "bqn_rq"), "m3": ("bqn_er", "bqn_er_rq")}


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


@contextlib.contextmanager
def grid(cells):
    """Cases de BQN remplacées le temps du calcul : {cap: (v1, v2)} (BQN n'a pas de dérogation v2)."""
    saved = {}
    try:
        for cap, (a, b) in (cells or {}).items():
            assert (LANG, cap) not in c2.V2_OVERRIDES and a == b, cap
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (a, saved[cap][1])
        yield
    finally:
        for cap, m in saved.items():
            v2.MATRIX[LANG][cap] = m


def run(data, lat, langs, footprint, c3, cells=None):
    with grid(cells):
        return bc.summary(cf.scenario(data, lat, langs, footprint, c3, "main"), list(RANKED))


def main():
    assert RANKED[-1] == LANG, "BQN doit être le dernier de RANKED (tirages isolés)"
    raw, bad = load_raw()
    v2.ADDED_RATIOS = {}  # données publiées d'avant la remarque : aucune correction de BQN
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    rng = np.random.default_rng(v3.SEED + 2700)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    # rapports appariés, par construction : copie / publié (tuned_flat et mt_flat face à tuned et mt)
    base_of = {K9TF: K9T, K9MF: K9M}
    r = {}
    for host, (pub, cop) in PAIRS.items():
        r[host] = {k: ratio(raw[cop][k], raw[pub][base_of.get(k, k)], rng) for k in sorted(raw.get(cop, {}))
                   if base_of.get(k, k) in raw.get(pub, {})}
    rv = lambda host, k: r[host][k]["ratio"]  # noqa: E731
    errata = {h: {K9N: rv(h, K9N), K9T: rv(h, K9TF), K9M: rv(h, K9MF), K7N: rv(h, K7N)} for h in PAIRS}
    k9_only = {k: v for k, v in errata["main"].items() if k[0] == "k9"}
    k7_only = {K7N: errata["main"][K7N]}
    blocs = {**errata["main"], **{k: rv("main", k) for k in BLOCKS}}  # K9 tuned et mt en bandes, somme hors chrono
    # information (B-K7tab de docs/BQN.md 4.4) : facteur de la table plate du C au lieu de celui de sa table chaînée
    f7 = json.load(open(os.path.join(ROOT, "results", "bqn_check.json")))["k7_factors"]["B-K7tab"]
    plans = {
        "R-grille": (data, lat, None),
        "R-K9": (bc.scaled(data, k9_only), lat, OLD_GRID),
        "R-K7": (bc.scaled(data, k7_only), lat, OLD_GRID),
        "R-E": (bc.scaled(data, errata["main"]), lat, None),
        "R-blocs": (bc.scaled(data, blocs), lat, None),
        "R-C5": (bc.scaled(data, errata["main"]), lat, C5_HALF),
        "R-blocs-C5": (bc.scaled(data, blocs), lat, C5_HALF),
        "R-K7map": (bc.scaled(data, k9_only), lat, None),
        "R-K7tab": (bc.scaled(data, {**errata["main"], K7N: errata["main"][K7N] * f7}), lat, None),
    }
    out = {"bad": bad, "times_ms": times, "r": {h: {kk(k): v for k, v in d.items()} for h, d in r.items()},
           "errata": {h: {kk(k): v for k, v in d.items()} for h, d in errata.items()},
           "blocs": {kk(k): v for k, v in blocs.items()}, "scenarios": {}}
    av = out["scenarios"]["Avant"] = run(data, lat, langs, footprint, c3, OLD_GRID)
    ref = json.load(open(os.path.join(ROOT, "results", "bqn_check.json")))["scenarios"]["B-E"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l]))
                              for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant (B-E) = {out['check_before']:.2e}", flush=True)
    for name, (d, lt, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : BQN {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    re_ = out["scenarios"]["R-E"]
    out["shift"] = {l: re_["exp21"][l] - av["exp21"][l] for l in RANKED if l != LANG}
    out["shift_ms"] = {l: re_["ms0"][l] - av["ms0"][l] for l in RANKED if l != LANG}
    json.dump(out, open(os.path.join(ROOT, "results", "bqn_remark.json"), "w"), indent=1, default=float)
    report(out)
    # classement publié (5.5) : rapports des errata inscrits dans les corrections transférées
    path = os.path.join(ROOT, "results", "transfers.json")
    tr = json.load(open(path))
    tr["ratios_added"] = {h: {LANG: {"|".join(k): v for k, v in errata[h].items()}} for h in PAIRS}
    note = (" ; BQN (langage ajouté, appliqués après le pont) : docs/BQN.md (5.3), results/raw_bqn_rq, machine 27, "
            "results/bqn_remark.json (ratios_added : main, cible Cascade Lake ; m3, réplication)")
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(path, "w"), indent=1)


def ci(x, d=3):
    return f"{f(x['ratio'], d)} [{f(x['ci'][0], d)}–{f(x['ci'][1], d)}]"


def report(o):
    S = o["scenarios"]
    re_, av = S["R-E"], S["Avant"]
    L = ["# Remarque sur BQN : errata, formes en blocs et scénarios\n",
         "Plan : `docs/BQN.md`, section 5. Mesures : `results/raw_bqn_rq/` (machine 27, Emerald Rapids, 7 processus par "
         "cellule). Code : `analysis/bqn_remark.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant (grille et données d'avant la remarque) reproduit B-E de `results/bqn_check.json` "
         f"(écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (machine 27)\n",
         "Moyennes géométriques des médianes de processus ; intervalles à 95 % par bootstrap. Cible Cascade Lake : `bqn_rq` / "
         "`bqn` (classement) ; native : `bqn_er_rq` / `bqn_er` (réplication). `tuned_flat` et `mt_flat` (somme de contrôle "
         "hors chrono, sans blocs) sont rapportés à `tuned` et `mt` publiés.\n",
         "| Cellule | publié (ms) | copie (ms) | rapport, cible Cascade Lake | rapport, natif |", "|---|---|---|---|---|"]
    for k, x in o["r"]["main"].items():
        y = o["r"]["m3"].get(k)
        L.append(f"| {k} | {f(x['old_ms'], 3)} | {f(x['new_ms'], 3)} | {ci(x)} | {ci(y) if y else '—'} |")
    L += ["", "Témoins inchangés (rapport attendu 1) : " + " ; ".join(
        f"{kk(k)} {ci(o['r']['main'][kk(k)])}" for k in CONTROLS if kk(k) in o["r"]["main"]) + ".", "",
          "Rapports des errata (classement) : " + " ; ".join(f"{k} {f(v, 3)}" for k, v in o["errata"]["main"].items())
          + ". Rapports de R-blocs : " + " ; ".join(f"{k} {f(v, 3)}" for k, v in o["blocs"].items()) + ".", "",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % | devant OCaml | devant JavaScript |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        pl = z.get("prec_l", {})
        L.append(f"| {name} | {f(z['ms0'][LANG], 2)} | {f(z['C'][LANG], 1)} | {f(z['E'][LANG], 2)} | "
                 f"{f(z['D'][LANG], 1)} | {f(z['exp21'][LANG], 2)} | {z['pos']}e | {z['rank90'][LANG]} | "
                 f"{f(100 * pl.get('ocaml', float('nan')), 0)} % | {f(100 * pl.get('js', float('nan')), 0)} % |")
    L += ["", "Plafond de BQN par noyau (estimation ponctuelle) : R-E " + " ; ".join(
        f"{k} {f(v, 2)}" for k, v in S["R-E"]["Ek"].items()) + " ; R-blocs " + " ; ".join(
        f"{k} {f(v, 2)}" for k, v in S["R-blocs"]["Ek"].items()) + ".", "",
          "## Classement : avant et après la remarque (R-E)\n",
          "| Place | Avant | rang espéré | R-E | rang espéré | écart du rang espéré | écart du score |",
          "|---|---|---|---|---|---|---|"]
    for i in range(len(re_["order21"])):
        a, b = av["order21"][i], re_["order21"][i]
        L.append(f"| {i + 1} | {NAMES[a]} | {f(av['exp21'][a], 2)} | {NAMES[b]} | {f(re_['exp21'][b], 2)} | "
                 f"{f(o['shift'].get(b), 2) if b != LANG else '—'} | {f(o['shift_ms'].get(b), 2) if b != LANG else '—'} |")
    open(os.path.join(ROOT, "results", "report_bqn_remark.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
