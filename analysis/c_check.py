#!/usr/bin/env python3
"""Remarque sur C (plan : docs/C.md, section 3), poussé avant les mesures.

Classement publié : errata de la règle v1, A3 = ½ et C2 = ½ pour C et pour C++ (analysis/capabilities.py), avec en
règle v2 des surcharges à 1 (analysis/capabilities_v2.py) ; le score principal ne change pas.
Rapports appariés (machine 16, results/raw_c) : moyenne géométrique des médianes de processus, intervalle par bootstrap ;
K8 naturel, au code inchangé, sert de témoin.
Scénarios (analyse globale de la v3 rejouée, mêmes tirages) :
* Avant (doit reproduire le scénario Publié de results/cpp_check.json), Publié (errata).
* S-K8-val, S-K8-it, S-K8 : K8 tuned de C x c_k8val / c_ref, c_k8it / c_ref, ou la meilleure des deux (transfert sur
  les données de C). Information : I-K8-gcc, les mêmes rapports sous gcc pour l'annexe C par gcc.
* I-K9-CL : K9 tuned et mt de C, C par gcc, Chapel, Ada et Fortran (grilles allouées une fois) x la pénalité du harnais
  mesurée sur Cascade Lake à code égal (C++ / C par gcc dans les données principales, tuned et mt).
* R-v1 : pilier contrôle en règle v1 partout (surcharges v2 et retrait de C3 suspendus le temps du calcul) ; R-ISO : la
  règle du « Banc » (analysis/standard_rule.py).
* Tableau de la remarque : T1 = C++ avec le K4 de clang++ (rapports du pont de results/cpp_check.json) ; T2 = T1 et
  I-K9-CL ; T3 = T2 et S-K8.
Sorties : results/c_check.json, results/report_c.md. Usage : c_check.py [--report] (--report : rapport seul, à partir
de results/c_check.json)."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_c")
K8T, K8N = ("k8", "tuned", ""), ("k8", "natural", "")
K9T, K9M = ("k9", "tuned", ""), ("k9", "mt", "")
K4 = [("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")]
ONCE = ["c", "c_gcc", "chapel", "ada", "fortran"]  # grilles de K9 (tuned et mt) allouées une fois
# errata de la règle v1 : (langage, capacité) -> (note v1 d'avant, texte d'avant)
OLD_V1 = {("c", "A3"): (1, "champs de bits standard ; packed par attribut (sonde)"),
          ("c", "C2"): (1, "immintrin.h (bench K5/K1/K6)"),
          ("cpp", "A3"): (1, "champs de bits ; packed par attribut (sonde)"),
          ("cpp", "C2"): (1, "immintrin.h")}


def kk(k):
    return ":".join(x for x in k if x)


def gm(procs):
    return math.exp(proc_logs(procs).mean())


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "c_rem":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return d, bad


def scaled(data, factors):
    """Copie des données ; factors : {implémentation: {clé: rapport}}."""
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for l, fk in factors.items():
        for key, r in fk.items():
            d[l][key] = [[t * r for t in p] for p in data[l][key]]
    return d


def merge(*fs):
    out = defaultdict(dict)
    for f in fs:
        for l, fk in f.items():
            for k, r in fk.items():
                out[l][k] = out[l].get(k, 1.0) * r
    return out


def summary(s):
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    i = RANKED.index("c")
    S0, A = s["S0"], s["A"]
    parts = {l: {"MS": s["ms0"][l], "C": s["C"][l], "E": s["E"][l], "D": s["D"][l], "Ek": s["Ek"][l],
                 "D_parts": {k: float(S0[k][A.idx[l]]) for k in ("D1", "D2", "D3", "D4")}}
             for l in RANKED + list(ANNEX) if l in A.idx}
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "pos": order.index("c") + 1, "parts": parts,
            "prec_c": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != "c"},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def run(data, lat, langs, footprint, c3, erratum=True, crule="main", v1_only=False):
    """Scénario avec ou sans les errata de la règle v1 ; v1_only : pilier contrôle en règle v1 partout (surcharges v2 et
    retrait de C3 suspendus) ; la matrice et les surcharges sont restaurées ensuite."""
    saved_m = {k: v2.MATRIX[k[0]][k[1]] for k in OLD_V1}
    saved_o = dict(v2.V2_OVERRIDES)
    saved_drop = set(v2.V2_DROP)
    try:
        if not erratum:
            for (l, cap), old in OLD_V1.items():
                v2.MATRIX[l][cap] = old
                v2.V2_OVERRIDES.pop((l, cap), None)
        if v1_only:
            v2.V2_OVERRIDES.clear()
            v2.V2_DROP.clear()
        return summary(cf.scenario(data, lat, langs, footprint, c3, crule))
    finally:
        for (l, cap), v in saved_m.items():
            v2.MATRIX[l][cap] = v
        v2.V2_OVERRIDES.clear()
        v2.V2_OVERRIDES.update(saved_o)
        v2.V2_DROP.clear()
        v2.V2_DROP.update(saved_drop)


def control_v1(c3):
    """Pilier contrôle en règle v1 (poids par défaut), avec les errata (après) et sans (avant)."""
    catw0 = {cat: w for cat, (w, _) in v2.CATEGORIES.items()}
    after = v2.c_score(v2.c_cells("v1", c3), catw0)
    saved = {k: v2.MATRIX[k[0]][k[1]] for k in OLD_V1}
    try:
        for (l, cap), old in OLD_V1.items():
            v2.MATRIX[l][cap] = old
        before = v2.c_score(v2.c_cells("v1", c3), catw0)
    finally:
        for (l, cap), v in saved.items():
            v2.MATRIX[l][cap] = v
    return {"before": before, "after": after}


def main():
    for (l, cap) in OLD_V1:
        assert v2.MATRIX[l][cap][0] == 0.5 and v2.V2_OVERRIDES.get((l, cap), (None,))[0] == 1, (l, cap)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    if "--report" in sys.argv:  # refait le rapport à partir des scénarios déjà calculés
        out = json.load(open(os.path.join(ROOT, "results", "c_check.json")))
        out["control_v1"] = control_v1(c3)
        json.dump(out, open(os.path.join(ROOT, "results", "c_check.json"), "w"), indent=1, default=float)
        report(out)
        return
    current = "--current" in sys.argv  # état actuel (harnais commun de K9, docs/K9.md) : sorties *_current
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 1000)
    R = lambda new, old, k: ratio(raw[new][k], raw[old][k], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r = {f"{new} / {old}": {k: R(new, old, k) for k in (K8T, K8N)}
         for new, old in (("c_k8val", "c_ref"), ("c_k8it", "c_ref"), ("c_gcc_k8val", "c_gcc_ref"), ("c_gcc_k8it", "c_gcc_ref"),
                          ("c_gcc_ref", "c_ref"))}
    val, it = r["c_k8val / c_ref"][K8T]["ratio"], r["c_k8it / c_ref"][K8T]["ratio"]
    gval, git = r["c_gcc_k8val / c_gcc_ref"][K8T]["ratio"], r["c_gcc_k8it / c_gcc_ref"][K8T]["ratio"]
    # pénalité du harnais de K9 sur Cascade Lake, à code égal (k9_rows identique : results/c_check/k9_code.txt)
    pen = {k: gm(data["cpp"][k]) / gm(data["c_gcc"][k]) for k in (K9T, K9M)}
    k9cl = {l: dict(pen) for l in ONCE if l in data}
    k8 = {"c": {K8T: min(val, it)}}
    bridge = json.load(open(os.path.join(ROOT, "results", "cpp_check.json")))["bridge_k4"]
    t1 = {"cpp": {k: bridge[kk(k)] for k in K4}}
    plans = {"Avant": dict(erratum=False), "Publié": {},
             "S-K8-val": dict(d=scaled(data, {"c": {K8T: val}})), "S-K8-it": dict(d=scaled(data, {"c": {K8T: it}})),
             "S-K8": dict(d=scaled(data, k8)), "I-K8-gcc": dict(d=scaled(data, {"c_gcc": {K8T: min(gval, git)}})),
             "I-K9-CL": dict(d=scaled(data, k9cl)), "R-v1": dict(v1_only=True), "R-ISO": dict(crule="R"),
             "T1": dict(d=scaled(data, t1)), "T2": dict(d=scaled(data, merge(t1, k9cl))),
             "T3": dict(d=scaled(data, merge(t1, k9cl, k8)))}
    if current:  # K9 au harnais commun pour toutes les implémentations : I-K9-CL et T2 n'ont plus d'objet
        plans = {"Publié": {}, "S-K8-val": plans["S-K8-val"], "S-K8-it": plans["S-K8-it"], "S-K8": plans["S-K8"],
                 "R-v1": plans["R-v1"], "R-ISO": plans["R-ISO"], "T1": plans["T1"],
                 "T1+S-K8": dict(d=scaled(data, merge(t1, k8)))}
        pen = {}
    out = {"bad": bad, "times_ms": times, "ratios": {n: {kk(k): v for k, v in dd.items()} for n, dd in r.items()},
           "k9_penalty_cl": {kk(k): v for k, v in pen.items()}, "k8_frontier_ms": None, "scenarios": {},
           "control_v1": control_v1(c3), "current": current}
    for name, kw in plans.items():
        z = out["scenarios"][name] = run(kw.get("d", data), lat, langs, footprint, c3, erratum=kw.get("erratum", True),
                                         crule=kw.get("crule", "main"), v1_only=kw.get("v1_only", False))
        p = z["parts"]
        print(f"{name} : C {p['c']['MS']:.2f} ({z['exp21']['c']:.2f}, {z['pos']}e, 1er {100 * z['first']['c']:.0f} %), "
              f"C++ {p['cpp']['MS']:.2f} ({z['exp21']['cpp']:.2f}), Odin {p['odin']['MS']:.2f} ({z['exp21']['odin']:.2f}) ; "
              f"tête : {', '.join(z['order21'][:4])}", flush=True)
    # état actuel : le classement publié après l'ajout de BQN (results/bqn_check.json, « B-E » ; avant lui,
    # fpc_remark.json, « R-E », fpc_check.json, « F-E », swift_remark.json, « R-E »,
    # swift_check.json, « S-E », lua_check.json, « L-E », python_check.json, « P-E », js_check.json, « J-E », ocaml_check.json, « O-E », haskell_check.json, « H-E »,
    # go_check.json, « G-E »,
    # java_check.json, « J-E », et k9_check.json, « Publié »)
    ref = (json.load(open(os.path.join(ROOT, "results", "bqn_check.json")))["scenarios"]["B-E"] if current else
           json.load(open(os.path.join(ROOT, "results", "cpp_check.json")))["scenarios"]["Publié"])
    av = out["scenarios"]["Publié" if current else "Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario {'Publié à results/bqn_check.json (B-E)' if current else 'Avant au publié d avant la remarque'}"
          f" = {out['check_before']:.2e}")
    # frontière de K8 dans le publié : meilleur temps (moyenne géométrique) parmi les langages classés
    best = {l: min(gm(data[l][k]) for k in (K8N, K8T, ("k8", "tuned_alloc", "")) if k in data.get(l, {}))
            for l in RANKED if l in data}
    lf = min(best, key=best.get)
    out["k8_frontier_ms"] = {"lang": lf, "ms": 1e3 * best[lf], "c_tuned_ms": 1e3 * gm(data["c"][K8T]),
                             "c_tuned_s_k8_ms": 1e3 * gm(data["c"][K8T]) * min(val, it)}
    suffix = "_current" if current else ""
    json.dump(out, open(os.path.join(ROOT, "results", f"c_check{suffix}.json"), "w"), indent=1, default=float)
    report(out, suffix)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o, suffix=""):
    INFO = {"I-K8-gcc", "I-K9-CL", "R-v1", "R-ISO", "T1", "T2", "T3"}
    L = ["# Remarque sur C : rapports appariés et scénarios\n",
         "Plan : `docs/C.md`. Mesures : `results/raw_c/` (machine 16, 7 processus par cellule). Code : `analysis/c_check.py`.",
         "Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         (f"Contrôle : le scénario Publié reproduit results/bqn_check.json, B-E (écart maximal {o['check_before']:.1e}).\n"
          if o.get("current") else
          f"Contrôle : le scénario Avant reproduit le publié d'avant la remarque (écart maximal {o['check_before']:.1e}).\n"),
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    for n, dd in o["ratios"].items():
        for k, x in dd.items():
            L.append(f"| {n} | {k}{' (témoin)' if k == 'k8:natural' else ''} | {f(x['old_ms'], 1)} | {f(x['new_ms'], 1)} | "
                     f"{f(x['ratio'], 3)} | {f(x['ci'][0], 3)}–{f(x['ci'][1], 3)} |")
    fr = o["k8_frontier_ms"]
    L += ["", f"Frontière de K8 dans le publié : {NAMES.get(fr['lang'], fr['lang'])}, {f(fr['ms'], 1)} ms ; K8 tuned de C "
          f"{f(fr['c_tuned_ms'], 1)} ms, {f(fr['c_tuned_s_k8_ms'], 1)} ms avec la meilleure forme (S-K8).",
          ("Pénalité du harnais de K9 sur Cascade Lake, à code égal (C++ / C par gcc) : "
           + " ; ".join(f"{k} {f(v, 3)}" for k, v in o["k9_penalty_cl"].items()) + ".\n") if o["k9_penalty_cl"] else
          "État actuel : K9 au harnais commun pour toutes les implémentations (docs/K9.md), K5 et K1 soa de Java corrigés et "
          "F1 de Java à ½ (docs/JAVA.md), K5 et K9 de Go corrigés (docs/GO.md), options et K1, K5, K8 de Haskell corrigés et "
          "B2, B3, A7 de Haskell à ½ (docs/HASKELL.md), Q6, K1 aos, K7 et K8 d'OCaml corrigés et D5 d'OCaml à ½ "
          "(docs/OCAML.md), K7 de JavaScript corrigé et E1, A4, E6 de JavaScript à 1, ½, ½ (docs/JAVASCRIPT.md), K3, K6 "
          "mt, K9 mt et K8 naturel de Python corrigés et B1, F3 de Python à 1, ½ (docs/PYTHON.md), K3, K4, Q6 et K8 "
          "naturel de Lua corrigés et B3, B4 de Lua à ½ (docs/LUA.md), Swift ajouté (docs/SWIFT.md), puis D4 et E4 de "
          "Swift corrigés et son pont par la machine 24 (docs/SWIFT.md, 5), FreePascal ajouté (docs/FPC.md), puis C2, E4 "
          "et F4 de FreePascal corrigés (docs/FPC.md, 5), BQN ajouté (docs/BQN.md) ; Publié = results/bqn_check.json "
          "(B-E).\n",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Statut | C | C++ | Odin | Rang espéré de C | Place de C | C 1er | C devant C++ | C devant Odin | Tête |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        p = z["parts"]
        st = "avant" if name == "Avant" else "publié" if name == "Publié" else "info" if name in INFO else "sensibilité"
        L.append(f"| {name} | {st} | {f(p['c']['MS'], 2)} | {f(p['cpp']['MS'], 2)} | {f(p['odin']['MS'], 2)} | "
                 f"{f(z['exp21']['c'], 2)} | {z['pos']} | {f(100 * z['first']['c'], 0)} % | {f(100 * z['prec_c']['cpp'], 0)} % | "
                 f"{f(100 * z['prec_c']['odin'], 0)} % | {', '.join(NAMES.get(l, l) for l in z['order21'][:4])} |")
    av, pu = o["scenarios"].get("Avant"), o["scenarios"]["Publié"]
    if av is None:  # état actuel : pas de comparaison avant / après les errata
        av = pu
    L += ["", "## Classement publié : avant et après les errata\n",
          "| Langage | Score | Contrôle v1 | Rang espéré avant → après | 1er avant → après |", "|---|---|---|---|---|"]
    for l in pu["order21"]:
        cv = o["control_v1"]
        L.append(f"| {NAMES.get(l, l)} | {f(pu['parts'][l]['MS'], 2)} | {f(cv['before'][l])} → {f(cv['after'][l])} | "
                 f"{f(av['exp21'][l], 2)} → {f(pu['exp21'][l], 2)} | "
                 f"{f(100 * av['first'][l], 0)} % → {f(100 * pu['first'][l], 0)} % |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:8]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", f"report_c{suffix}.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
