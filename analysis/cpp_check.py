#!/usr/bin/env python3
"""Remarque sur C++ (plan : docs/CPP.md, section 3), poussé avant les mesures.

Classement publié : erratum C1 de C++ (0,5 en règle v1 ; en règle v2, surcharge à 1 par vector_size, comme C) et
remesure de D2 et D4 pour les 25 implémentations (results/raw_d24, clés à part lues par D2 et D4 ; analysis/analyze_v2.py,
apply_d24 ; analysis/analyze_v3.py, Arrays3.dt). Tout le reste est sensibilité ou information.
Rapports appariés (machine 15, results/raw_cpp) : moyenne géométrique des médianes de processus, intervalle par bootstrap.
Scénarios (analyse globale de la v3 rejouée, mêmes tirages) :
* Avant (doit reproduire le scénario Publié de results/odin_check.json), P-C1 (erratum seul), P-D24 (remesure seule),
  Publié (les deux).
* Sensibilités, depuis le Publié, par transfert seul des rapports cpp_x / cpp_ref sur les données de C++ (clés de la
  campagne et clés remesurées de D2 et D4) : S-clang-K4, S-clang, S-intr, S-K8, S-K9, S-remarque ; pour S-clang et
  S-remarque, les latences de K8 naturel de C++ (D3) sont multipliées, colonne par colonne, par le rapport des médianes
  regroupées cpp_x / cpp_ref. Information : S-clang-K4-pont (K4 de C++ = K4 de C des données principales x
  cpp_clang / c_ref) ; I-K9-C (K9 de C x c_k9 / c_ref) ; I-K9-maj (mêmes rapports pour C, C par gcc, Chapel et Ada, et
  pour K9 tuned et mt de Fortran) ; rapports du même hôte cpp_ref, cpp_clang et cpp_all contre c_ref (sans score).
Sorties : results/cpp_check.json, results/report_cpp.md."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N, D24_KEYS  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "tools"))
from measure_cpp import SCORE, INTR, K9  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_cpp")
LANG = "cpp"
K4 = [("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")]
K8T = ("k8", "tuned", "")
K9M = ("k9", "mt", "")
C_KEYS = [k for k in SCORE if k != ("k8", "tuned_alloc", "")]
OLD_C1 = (1, "std::simd C++26 (bench K1/K5/K6)")  # note v1 de C1 avant l'erratum du 1er novembre
ONCE = {"c": K9, "c_gcc": K9, "chapel": K9, "ada": K9, "fortran": K9[1:]}  # grilles de K9 allouées une fois


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, lat, bad = defaultdict(dict), defaultdict(list), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "cpp":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            if key == K8N and r.get("lat"):
                lat[r["lang"]].append(r["lat"])
    return d, lat, bad


def gm(procs):
    return math.exp(proc_logs(procs).mean())


def lat_ratio(lat, new, old):
    """Rapport, colonne par colonne (p50, p90, p99, p99,9, max), des médianes regroupées sur toutes les répétitions."""
    a, b = np.vstack([np.asarray(p, float) for p in lat[new]]), np.vstack([np.asarray(p, float) for p in lat[old]])
    return (np.median(a, axis=0) / np.median(b, axis=0)).tolist()


def scaled(data, factors):
    """Copie des données ; factors : {implémentation: {clé de la campagne: rapport}}. La clé remesurée de D2 ou D4
    correspondante, si elle existe, reçoit le même rapport."""
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for l, fk in factors.items():
        for key, r in fk.items():
            for k2 in (key, D24_KEYS.get(key)):
                if k2 is not None and k2 in data[l]:
                    d[l][k2] = [[t * r for t in p] for p in data[l][k2]]
    return d


def scaled_lat(lat, cols):
    out = {l: dict(v) for l, v in lat.items()}
    out[LANG][K8N] = [[[x * cols[i] for i, x in enumerate(rep)] for rep in proc] for proc in lat[LANG][K8N]]
    return out


def summary(s):
    i = RANKED.index(LANG)
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    pos = order.index(LANG)
    S0, A = s["S0"], s["A"]
    parts = {l: {"MS": s["ms0"][l], "C": s["C"][l], "E": s["E"][l], "D": s["D"][l], "Ek": s["Ek"][l],
                 "D_parts": {k: float(S0[k][A.idx[l]]) for k in ("D1", "D2", "D3", "D4")}}
             for l in RANKED + list(ANNEX) if l in A.idx}
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "pos": pos + 1, "parts": parts,
            "prec_cpp": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def run(data, lat, langs, footprint, c3, erratum=True):
    """Scénario avec ou sans l'erratum C1 (règle v1 à 0,5 et surcharge v2 à 1) ; la matrice est restaurée ensuite."""
    saved_v1, saved_o = v2.MATRIX[LANG]["C1"], v2.V2_OVERRIDES.get((LANG, "C1"))
    try:
        if not erratum:
            v2.MATRIX[LANG]["C1"] = OLD_C1
            v2.V2_OVERRIDES.pop((LANG, "C1"), None)
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        v2.MATRIX[LANG]["C1"] = saved_v1
        if saved_o is not None:
            v2.V2_OVERRIDES[(LANG, "C1")] = saved_o


def decompose(z, a, b):
    """Écart de score a − b : contrôle et défauts linéaires ; plafond réparti par noyau au prorata des écarts de log."""
    W, DW = v3.WEIGHTS, v3.DW
    A, B = z["parts"][a], z["parts"][b]
    out = {"total": A["MS"] - B["MS"], "contrôle": W["C"] * (A["C"] - B["C"])}
    lg = {k: math.log(A["Ek"][k] / B["Ek"][k]) for k in A["Ek"]}
    tot = sum(lg.values())
    for k, v in lg.items():
        out["E " + k] = W["E"] * (A["E"] - B["E"]) * (v / tot if tot else 0.0)
    for k in DW:
        out[k] = W["D"] * 100 * DW[k] * (A["D_parts"][k] - B["D_parts"][k])
    return out


def main():
    assert v2.MATRIX[LANG]["C1"][0] == 0.5, "erratum C1 (v1) absent de analysis/capabilities.py"
    assert v2.V2_OVERRIDES.get((LANG, "C1"), (None,))[0] == 1, "surcharge v2 de C1 absente de analysis/capabilities_v2.py"
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    data0, lat, *_ = v2.dataset_main(transfers=True, d24=False)
    v2.align_lat(data0, lat)
    data24, lat24, *_ = v2.dataset_main(transfers=True, d24=True)
    v2.align_lat(data24, lat24)
    langs = [l for l in RANKED + list(ANNEX) if l in data0]
    raw, rlat, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 900)
    R = lambda new, old, k: ratio(raw[new][k], raw[old][k], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r = {"cpp_clang": {k: R("cpp_clang", "cpp_ref", k) for k in SCORE},
         "cpp_all": {k: R("cpp_all", "cpp_ref", k) for k in SCORE},
         "cpp_intr": {k: R("cpp_intr", "cpp_ref", k) for k in INTR},
         "cpp_k8": {K8T: R("cpp_k8", "cpp_ref", K8T)},
         "cpp_k9": {k: R("cpp_k9", "cpp_ref", k) for k in K9},
         "c_k9": {k: R("c_k9", "c_ref", k) for k in K9}}
    eq = {impl: {k: R(impl, "c_ref", k) for k in C_KEYS} for impl in ("cpp_ref", "cpp_clang", "cpp_all")}
    eq_gm = {impl: math.exp(float(np.mean([math.log(v["ratio"]) for v in dd.values()]))) for impl, dd in eq.items()}
    lat_r = {impl: lat_ratio(rlat, impl, "cpp_ref") for impl in ("cpp_clang", "cpp_all")}
    T = lambda impl, keys: {k: r[impl][k]["ratio"] for k in keys}  # noqa: E731
    pub = data24
    pont = {k: gm(pub["c"][k]) * eq["cpp_clang"][k]["ratio"] / gm(pub[LANG][k]) for k in K4}
    ck9 = T("c_k9", K9)
    plans = {
        "Avant": (data0, lat, False), "P-C1": (data0, lat, True), "P-D24": (data24, lat24, False),
        "Publié": (pub, lat24, True),
        "S-clang-K4": (scaled(pub, {LANG: T("cpp_clang", K4)}), lat24, True),
        "S-clang-K4-pont": (scaled(pub, {LANG: pont}), lat24, True),
        "S-clang": (scaled(pub, {LANG: T("cpp_clang", SCORE)}), scaled_lat(lat24, lat_r["cpp_clang"]), True),
        "S-intr": (scaled(pub, {LANG: T("cpp_intr", INTR)}), lat24, True),
        "S-K8": (scaled(pub, {LANG: T("cpp_k8", [K8T])}), lat24, True),
        "S-K9": (scaled(pub, {LANG: T("cpp_k9", K9)}), lat24, True),
        "S-remarque": (scaled(pub, {LANG: T("cpp_all", SCORE)}), scaled_lat(lat24, lat_r["cpp_all"]), True),
        "I-K9-C": (scaled(pub, {"c": ck9}), lat24, True),
        "I-K9-maj": (scaled(pub, {l: {k: ck9[k] for k in ks} for l, ks in ONCE.items()}), lat24, True)}
    out = {"bad": bad, "times_ms": times, "ratios": {impl: {kk(k): v for k, v in dd.items()} for impl, dd in r.items()},
           "same_host": {impl: {kk(k): v for k, v in dd.items()} for impl, dd in eq.items()}, "same_host_gm": eq_gm,
           "lat_ratios": lat_r, "bridge_k4": {kk(k): v for k, v in pont.items()},
           "k9_effect": {"c_k9/c_ref mt": r["c_k9"][K9M], "cpp_k9/cpp_ref mt": r["cpp_k9"][K9M]}, "scenarios": {}}
    k9c, k9p = r["c_k9"][K9M]["ci"], r["cpp_k9"][K9M]["ci"]
    out["k9_established"] = bool(k9c[0] > 1 or k9c[1] < 1 or k9p[0] > 1 or k9p[1] < 1)
    for name, (d, lt, err) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, erratum=err)
        p = z["parts"][LANG]
        print(f"{name} : C++ {p['MS']:.2f} points (C {p['C']:.1f}, E {p['E']:.1f}, D {p['D']:.1f}), rang espéré "
              f"{z['exp21'][LANG]:.2f} ({z['pos']}e), devant C {100 * z['prec_cpp']['c']:.0f} %, devant Odin "
              f"{100 * z['prec_cpp']['odin']:.0f} % ; C {z['ms0']['c']:.2f} ({z['exp21']['c']:.2f})", flush=True)
    pubz = out["scenarios"]["Publié"]
    out["decomposition"] = {f"{a}-cpp": decompose(pubz, a, LANG) for a in ("c", "c_gcc")}
    out["decomposition_avant"] = {f"{a}-cpp": decompose(out["scenarios"]["Avant"], a, LANG) for a in ("c", "c_gcc")}
    ref = json.load(open(os.path.join(ROOT, "results", "odin_check.json")))["scenarios"]["Publié"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant la remarque = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(ROOT, "results", "cpp_check.json"), "w"), indent=1, default=float)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur C++ : rapports appariés et scénarios\n",
         "Plan : `docs/CPP.md`. Mesures : `results/raw_cpp/` et `results/raw_d24/` (machine 15, 7 processus par cellule).",
         "Code : `analysis/cpp_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le publié d'avant la remarque (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    labels = {"cpp_clang": "cpp_clang / cpp_ref", "cpp_all": "cpp_all / cpp_ref", "cpp_intr": "cpp_intr / cpp_ref",
              "cpp_k8": "cpp_k8 / cpp_ref", "cpp_k9": "cpp_k9 / cpp_ref", "c_k9": "c_k9 / c_ref"}
    for impl, dd in o["ratios"].items():
        for k, x in dd.items():
            L.append(f"| {labels[impl]} | {k} | {f(x['old_ms'], 2)} | {f(x['new_ms'], 2)} | {f(x['ratio'], 3)} | "
                     f"{f(x['ci'][0], 3)}–{f(x['ci'][1], 3)} |")
    L += ["", "Latences de K8 naturel (rapports des médianes regroupées p50, p90, p99, p99,9, max) : "
          + " ; ".join(f"{impl} / cpp_ref {', '.join(f(v, 3) for v in cols)}" for impl, cols in o["lat_ratios"].items()) + ".",
          f"Effet de la pratique d'allocation de K9 établi (intervalle de K9 mt hors de 1) : {'oui' if o['k9_established'] else 'non'}.\n",
          "## C++ et C sur le même hôte (information, sans score)\n",
          "| Clé | C (clang 23) | C++ g++ / C | C++ clang++ / C | C++ remarque / C |", "|---|---|---|---|---|"]
    for k in o["same_host"]["cpp_ref"]:
        a, b, c = (o["same_host"][impl][k] for impl in ("cpp_ref", "cpp_clang", "cpp_all"))
        L.append(f"| {k} | {f(a['old_ms'], 2)} ms | {f(a['ratio'], 2)} [{f(a['ci'][0], 2)}–{f(a['ci'][1], 2)}] | "
                 f"{f(b['ratio'], 2)} [{f(b['ci'][0], 2)}–{f(b['ci'][1], 2)}] | {f(c['ratio'], 2)} [{f(c['ci'][0], 2)}–"
                 f"{f(c['ci'][1], 2)}] |")
    L.append("| moyenne géométrique | | " + " | ".join(f(o["same_host_gm"][i], 3) for i in ("cpp_ref", "cpp_clang", "cpp_all"))
             + " |")
    L += ["", "K4 par le pont (information, S-clang-K4-pont) : rapport appliqué au K4 de C++ = "
          + " ; ".join(f"{k} {f(v, 3)}" for k, v in o["bridge_k4"].items()) + ".\n",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de C++ | C | E | D | Rang espéré | Place | Rang 90 % | Devant C | Devant Odin | 1er | C : score (rang) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        p = z["parts"][LANG]
        L.append(f"| {name} | {f(p['MS'], 2)} | {f(p['C'])} | {f(p['E'])} | {f(p['D'])} | {f(z['exp21'][LANG], 2)} | "
                 f"{z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {f(100 * z['prec_cpp']['c'], 0)} % | "
                 f"{f(100 * z['prec_cpp']['odin'], 0)} % | {f(100 * z['first'][LANG], 0)} % | {f(z['ms0']['c'], 2)} "
                 f"({f(z['exp21']['c'], 2)}) |")
    av, pu = o["scenarios"]["Avant"], o["scenarios"]["Publié"]
    L += ["", "## Effet du publié (erratum C1 et remesure de D2 et D4) sur les 21 langages classés\n",
          "| Langage | Score avant → après | Rang espéré avant → après | D2 avant → après | D4 avant → après |",
          "|---|---|---|---|---|"]
    for l in pu["order21"]:
        a, b = av["parts"][l], pu["parts"][l]
        L.append(f"| {NAMES.get(l, l)} | {f(a['MS'], 2)} → {f(b['MS'], 2)} | {f(av['exp21'][l], 2)} → {f(pu['exp21'][l], 2)} | "
                 f"{f(a['D_parts']['D2'], 3)} → {f(b['D_parts']['D2'], 3)} | {f(a['D_parts']['D4'], 3)} → "
                 f"{f(b['D_parts']['D4'], 3)} |")
    L += ["", "## Décomposition de l'écart à C (points ; plafond réparti par noyau au prorata des écarts de log)\n"]
    for lab, dd in (("Publié", o["decomposition"]), ("Avant", o["decomposition_avant"])):
        for pair, d in dd.items():
            L.append(f"* {lab}, {pair} : " + " ; ".join(f"{k} {f(v, 2)}" for k, v in d.items()) + ".")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_cpp.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
