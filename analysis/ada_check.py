#!/usr/bin/env python3
"""Vérification de la remarque sur Ada (plan : docs/ADA.md, section 3.3, poussé avant les mesures ; ce code est poussé
avant son premier calcul sur les mesures nouvelles).

Rapports appariés mesurés sur la machine 5 (results/raw_ada, tools/measure_ada.py) : ada_fix (sept noyaux tuned hors
ligne) contre ada (binaire de la campagne). Ils sont transférés aux processus d'Ada des données principales, puis
l'analyse globale de la v3 est rejouée (analysis/confrontation.py : mêmes 20 000 variantes, même graine). Tous les
scénarios portent les trois errata de la matrice (E5, C1, B4 d'Ada).

A-E   : classement publié avec les errata de la matrice seuls.
S1    : A-E, plus les rapports des 12 clés dont le code change, K5 forcé à 1 (données de K5 prises sur la machine 3).
S1-K5 : S1 avec le transfert de K5.
S1-27 : rapports des 27 clés (les 15 autres servent de témoin : leur source ne change pas).
Témoin : rapport Ada/C compilé par GCC sur 6 clés, sur la machine 5 et dans les données principales.
Sorties : results/ada_check.json, results/report_ada.md et results/transfers.json (rapports de S1, que
analysis/analyze_v2.dataset_main applique ensuite au classement publié : décision 2 du plan)."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, CATEGORIES, c_cells, c_score  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from measure_ada import SCORE_KEYS, FIX_KEYS, GCC_KEYS  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_ada")
LANG = "ada"


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "ada":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return d, bad


def ratio(new, old, rng, nb=2000):
    yo, yn = proc_logs(old), proc_logs(new)
    bs = [math.exp(yn[rng.integers(0, len(yn), len(yn))].mean() - yo[rng.integers(0, len(yo), len(yo))].mean())
          for _ in range(nb)]
    return {"ratio": float(math.exp(yn.mean() - yo.mean())), "ci": [float(np.quantile(bs, 0.025)),
                                                                   float(np.quantile(bs, 0.975))],
            "n_new": len(yn), "n_old": len(yo), "old_ms": 1e3 * math.exp(yo.mean()), "new_ms": 1e3 * math.exp(yn.mean())}


def scaled(data, factors):
    """Copie des données principales, processus d'Ada multipliés par le rapport de chaque clé."""
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def summary(s):
    i = RANKED.index(LANG)
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    pos = order.index(LANG)
    nb = {}
    if pos > 0:
        nb["devant"] = (order[pos - 1], float(s["prec"][i, RANKED.index(order[pos - 1])]))
    if pos < len(order) - 1:
        nb["derrière"] = (order[pos + 1], float(s["prec"][i, RANKED.index(order[pos + 1])]))
    A = s["A"]
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "E": {l: s["E"][l] for l in RANKED},
            "D": {l: s["D"][l] for l in RANKED}, "C": {l: s["C"][l] for l in RANKED},
            "D1": {l: float(s["S0"]["D1"][A.idx[l]]) for l in RANKED},
            "Ek": s["Ek"][LANG], "pos": pos + 1, "neighbours": nb,
            "prec_lang": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def main():
    m = v2.MATRIX[LANG]
    assert (m["E5"][0], m["C1"][0], m["B4"][0]) == (1, 0.5, 0.5), "errata absents de la matrice v1"
    assert v2.V2_OVERRIDES[(LANG, "C1")][0] == 1, "erratum C1 absent de la règle v2"
    data, lat, *_ = v2.dataset_main(transfers=False)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    missing = [(impl, k) for impl, keys in (("ada", SCORE_KEYS), ("ada_fix", SCORE_KEYS), ("c_gcc", GCC_KEYS))
               for k in keys if k not in raw.get(impl, {})]
    assert not missing, f"cellules manquantes : {missing}"
    rng = np.random.default_rng(v3.SEED + 40)
    ratios = {k: ratio(raw["ada_fix"][k], raw["ada"][k], rng) for k in SCORE_KEYS}
    rk = {k: r["ratio"] for k, r in ratios.items()}
    witness = {}
    for key in GCC_KEYS:
        g = math.exp(proc_logs(raw["c_gcc"][key]).mean())
        witness[":".join(key)] = {"ada_here_ms": 1e3 * math.exp(proc_logs(raw["ada"][key]).mean()),
                                  "fix_here_ms": 1e3 * math.exp(proc_logs(raw["ada_fix"][key]).mean()),
                                  "gcc_here_ms": 1e3 * g,
                                  "ada_main_ms": 1e3 * math.exp(proc_logs(data[LANG][key]).mean()),
                                  "gcc_main_ms": 1e3 * math.exp(proc_logs(data["c_gcc"][key]).mean())}
    s1 = {k: (1.0 if k[0] == "k5" else rk[k]) for k in FIX_KEYS}
    plans = {"A-E": data, "S1": scaled(data, s1), "S1-K5": scaled(data, {k: rk[k] for k in FIX_KEYS}),
             "S1-27": scaled(data, rk)}
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    out = {"bad": bad, "C_ada": {r: float(c_score(c_cells(r, c3), catw0)[LANG]) for r in ("v1", "v2")},
           "ratios": {":".join(k): r for k, r in ratios.items()}, "fix_keys": [":".join(k) for k in FIX_KEYS],
           "witness_gcc": witness, "scenarios": {}}
    for name, d in plans.items():
        s = cf.scenario(d, lat, langs, footprint, c3, "main")
        out["scenarios"][name] = summary(s)
        z = out["scenarios"][name]
        print(f"{name} : Ada {z['ms0'][LANG]:.1f} points, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), "
              f"rang 90 % {z['rank90'][LANG]}", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "ada_check.json"), "w"), indent=1, default=float)
    json.dump({"source": "docs/ADA.md (décision 2) ; rapports appariés de results/raw_ada, machine 5 ; "
                         "results/ada_check.json", "ratios": {LANG: {"|".join(k): r for k, r in s1.items()
                                                                     if k[0] != "k5"}}},
              open(os.path.join(ROOT, "results", "transfers.json"), "w"), indent=1)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    S = o["scenarios"]
    L = ["# Remarque sur Ada : rapports appariés et scénarios\n",
         "Plan : `docs/ADA.md`. Mesures : `results/raw_ada/` (machine 5, 7 processus par cellule). Code :",
         "`analysis/ada_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         f"Contrôle d'Ada avec les errata (E5, C1, B4) : {f(o['C_ada']['v2'])} en règle v2, {f(o['C_ada']['v1'])} en "
         f"règle v1.\n",
         "## Rapports appariés (ada_fix / ada, machine 5)\n",
         "| Clé | Ada (ms) | Ada corrigé (ms) | Rapport | IC 95 % | Code changé |", "|---|---|---|---|---|---|"]
    for k, r in o["ratios"].items():
        L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–"
                 f"{f(r['ci'][1], 3)} | {'oui' if k in o['fix_keys'] else 'non (témoin)'} |")
    L += ["", "## Témoin du même hôte : C compilé par GCC\n",
          "| Clé | Ada (ms) | Ada corrigé (ms) | C par GCC (ms) | Ada corrigé / GCC | Ada / GCC données principales |",
          "|---|---|---|---|---|---|"]
    for k, w in o["witness_gcc"].items():
        L.append(f"| {k} | {f(w['ada_here_ms'], 2)} | {f(w['fix_here_ms'], 2)} | {f(w['gcc_here_ms'], 2)} | "
                 f"{f(w['fix_here_ms'] / w['gcc_here_ms'], 2)} | {f(w['ada_main_ms'] / w['gcc_main_ms'], 2)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score d'Ada | Plafond E | D1 | Contrôle C | Rang espéré | Place | Rang 90 % | Devance le suivant |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        nb = z["neighbours"].get("derrière")
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['E'][LANG])} | {f(100 * z['D1'][LANG], 1)} | "
                 f"{f(z['C'][LANG])} | {f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–"
                 f"{z['rank90'][LANG][1]} | {NAMES[nb[0]] + ' ' + f(100 * nb[1], 0) + ' %' if nb else '—'} |")
    for name in S:
        z = S[name]
        L.append(f"\n**{name}** : " + ", ".join(f"{i + 1}. {NAMES[l]} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                                              for i, l in enumerate(z["order21"][:12])) + ".")
    text = "\n".join(L) + "\n"
    open(os.path.join(ROOT, "results", "report_ada.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
