#!/usr/bin/env python3
"""Vérification de la remarque sur Fortran (plan : docs/FORTRAN.md, section 3.4, poussé avant les mesures ; ce code est
poussé avant son premier calcul sur les mesures nouvelles).

Rapports appariés mesurés sur la machine 5 (results/raw_fortran, tools/measure_fortran.py) : fortran_fix (noyaux de
ms.f90 hors ligne) et fortran_exp (en plus, K5 tuned et arène de K8 réécrits) contre fortran (binaire de la campagne).
Ils sont transférés aux processus de Fortran des données principales (qui portent déjà les corrections d'Ada), puis
l'analyse globale de la v3 est rejouée (analysis/confrontation.py : mêmes 20 000 variantes, même graine). Tous les
scénarios portent les errata de la grille de Fortran (A3, A4, B2).

F-E   : classement publié avec les errata de la grille seuls.
S1    : F-E, plus les rapports des 11 clés dont le code change, K5 forcé à 1, et la C3 de Fortran mesurée sur fortran_fix.
S1-K5 : S1 avec le transfert de K5. S1-26 : les rapports des 26 clés (les 15 autres servent de témoin).
S2    : S1, plus K5 tuned et K8 tuned de fortran_exp (sensibilité, hors classement publié).
Témoin : rapport Fortran/C compilé par GCC sur 4 clés, sur la machine 5 et dans les données principales.
Sorties : results/fortran_check.json, results/report_fortran.md ; results/transfers.json (rapports de S1 ajoutés à ceux
d'Ada) et results/vectorization.json (C3 de Fortran : valeur de fortran_fix, ancienne valeur gardée sous
« fortran_campagne »), que l'analyse publiée lit ensuite."""
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
from measure_fortran import SCORE_KEYS, FIX_KEYS, EXP_KEYS, GCC_KEYS  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_fortran")
LANG = "fortran"


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "fortran":
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
    """Copie des données principales, processus de Fortran multipliés par le rapport de chaque clé."""
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
    assert (m["A3"][0], m["B2"][0]) == (0.5, 0.5) and v2.V2_OVERRIDES[(LANG, "A4")][0] == 1, "errata absents"
    data, lat, *_ = v2.dataset_main(transfers=False)
    tpath = os.path.join(ROOT, "results", "transfers.json")
    tr = json.load(open(tpath))
    for lang, keys in tr["ratios"].items():  # corrections déjà publiées (Ada), sans celles de Fortran
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    v2.align_lat(data, lat)
    vpath = os.path.join(ROOT, "results", "vectorization.json")
    c3 = json.load(open(vpath))
    c3_camp = dict(c3)
    c3_camp[LANG] = c3.get("fortran_campagne", c3[LANG])
    c3_fix = dict(c3_camp)
    c3_fix[LANG] = c3["fortran_fix"]
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    keys26 = [k for k in SCORE_KEYS if k in data[LANG]]
    missing = [(impl, k) for impl, keys in (("fortran", keys26), ("fortran_fix", keys26), ("fortran_exp", EXP_KEYS),
                                            ("c_gcc", GCC_KEYS)) for k in keys if k not in raw.get(impl, {})]
    assert not missing, f"cellules manquantes : {missing}"
    rng = np.random.default_rng(v3.SEED + 50)
    ratios = {k: ratio(raw["fortran_fix"][k], raw["fortran"][k], rng) for k in keys26}
    exp = {k: ratio(raw["fortran_exp"][k], raw["fortran"][k], rng) for k in EXP_KEYS}
    rk = {k: r["ratio"] for k, r in ratios.items()}
    witness = {}
    for key in GCC_KEYS:
        witness[":".join(key)] = {"orig_here_ms": 1e3 * math.exp(proc_logs(raw["fortran"][key]).mean()),
                                  "fix_here_ms": 1e3 * math.exp(proc_logs(raw["fortran_fix"][key]).mean()),
                                  "exp_here_ms": (1e3 * math.exp(proc_logs(raw["fortran_exp"][key]).mean())
                                                  if key in raw["fortran_exp"] else None),
                                  "gcc_here_ms": 1e3 * math.exp(proc_logs(raw["c_gcc"][key]).mean()),
                                  "orig_main_ms": 1e3 * math.exp(proc_logs(data[LANG][key]).mean()),
                                  "gcc_main_ms": 1e3 * math.exp(proc_logs(data["c_gcc"][key]).mean())}
    s1 = {k: (1.0 if k[0] == "k5" else rk[k]) for k in FIX_KEYS}
    plans = {"F-E": (data, c3_camp), "S1": (scaled(data, s1), c3_fix),
             "S1-K5": (scaled(data, {k: rk[k] for k in FIX_KEYS}), c3_fix), "S1-26": (scaled(data, rk), c3_fix),
             "S2": (scaled(data, {**s1, **{k: e["ratio"] for k, e in exp.items()}}), c3_fix)}
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    out = {"bad": bad, "C_fortran": {r: float(c_score(c_cells(r, c3_camp), catw0)[LANG]) for r in ("v1", "v2")},
           "C3": {"campagne": c3_camp[LANG], "fix": c3_fix[LANG]},
           "ratios": {":".join(k): r for k, r in ratios.items()}, "exp": {":".join(k): r for k, r in exp.items()},
           "fix_keys": [":".join(k) for k in FIX_KEYS], "witness_gcc": witness, "scenarios": {}}
    for name, (d, c3x) in plans.items():
        s = cf.scenario(d, lat, langs, footprint, c3x, "main")
        out["scenarios"][name] = summary(s)
        z = out["scenarios"][name]
        print(f"{name} : Fortran {z['ms0'][LANG]:.1f} points, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), "
              f"rang 90 % {z['rank90'][LANG]}", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "fortran_check.json"), "w"), indent=1, default=float)
    tr["ratios"][LANG] = {"|".join(k): r for k, r in s1.items() if k[0] != "k5"}
    tr["source"] = tr["source"] + " ; Fortran : docs/FORTRAN.md (3.4), results/raw_fortran, results/fortran_check.json"
    json.dump(tr, open(tpath, "w"), indent=1)
    c3["fortran_campagne"] = c3_camp[LANG]
    c3[LANG] = c3["fortran_fix"]
    json.dump(c3, open(vpath, "w"), indent=1, sort_keys=True)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    S = o["scenarios"]
    L = ["# Remarque sur Fortran : rapports appariés et scénarios\n",
         "Plan : `docs/FORTRAN.md`. Mesures : `results/raw_fortran/` (machine 5, 7 processus par cellule). Code :",
         "`analysis/fortran_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         "Classement publié : S1, sauf K4 sans branchement, reporté par le témoin du même hôte (écart au plan, décidé",
         "après ce calcul : `docs/FORTRAN.md`, 4.2 ; `analysis/transfer_check.py`, `results/transfer_check.json`).\n",
         f"Contrôle de Fortran avec les errata (A3, A4, B2) : {f(o['C_fortran']['v2'])} en règle v2, "
         f"{f(o['C_fortran']['v1'])} en règle v1. C3 (vectorisation mesurée) : {f(o['C3']['campagne'], 1)} avec le banc "
         f"de la campagne, {f(o['C3']['fix'], 1)} avec le banc corrigé.\n",
         "## Rapports appariés (fortran_fix / fortran, machine 5)\n",
         "| Clé | Fortran (ms) | Fortran corrigé (ms) | Rapport | IC 95 % | Code changé |", "|---|---|---|---|---|---|"]
    for k, r in o["ratios"].items():
        L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–"
                 f"{f(r['ci'][1], 3)} | {'oui' if k in o['fix_keys'] else 'non (témoin)'} |")
    L += ["", "## Sensibilité : formes de la remarque (fortran_exp / fortran)\n", "| Clé | Rapport | IC 95 % |", "|---|---|---|"]
    for k, r in o["exp"].items():
        L.append(f"| {k} | {f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Témoin du même hôte : C compilé par GCC\n",
          "| Clé | Fortran (ms) | Fortran corrigé (ms) | Sensibilité (ms) | C par GCC (ms) | Corrigé / GCC | Fortran / GCC données principales |",
          "|---|---|---|---|---|---|---|"]
    for k, w in o["witness_gcc"].items():
        L.append(f"| {k} | {f(w['orig_here_ms'], 2)} | {f(w['fix_here_ms'], 2)} | "
                 f"{f(w['exp_here_ms'], 2) if w['exp_here_ms'] else '—'} | {f(w['gcc_here_ms'], 2)} | "
                 f"{f(w['fix_here_ms'] / w['gcc_here_ms'], 2)} | {f(w['orig_main_ms'] / w['gcc_main_ms'], 2)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Fortran | Plafond E | D1 | Contrôle C | Rang espéré | Place | Rang 90 % | Devance le suivant |",
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
    open(os.path.join(ROOT, "results", "report_fortran.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
