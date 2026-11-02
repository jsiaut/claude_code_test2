#!/usr/bin/env python3
"""Sensibilité « sans SIMD explicite » (plan : docs/NOSIMD.md, sections 2 et 3, poussé avant les calculs).

Analyse globale de la v3 rejouée (mêmes tirages) à partir de l'état publié (corrections transférées, latences de D3
remesurées) ; les variantes retirées le sont au niveau des temps simulés (NaN, que le minimum ignore), si bien que les
tirages ne changent pas d'un scénario à l'autre :
* Publié : témoin, doit reproduire le scénario « Avant » de results/nim_check.json.
* Contrôle sans mt : K6 mt Q6, K6 mt Q1 et K9 mt sortent de E pour tous.
* S-scalaire : variantes V, P et M retirées (table 2.1), mesures mt retirées, Q1 en blocs de D rétabli.
* S-scalaire-Mojo : idem, K1 aos de Mojo compté SIMD (K1 prend sa variante naturelle).
* S-symétrique : K1 aos seul, K5, Q6, Q1 et K9 en naturel seul, mesures mt retirées.
* S-noyaux-scalaires : E réduit à K3, K4, K7 et K8 (e_drop).
* S-importées : variantes M retirées (K1 soa et K5 tuned de Nim, K5 tuned d'Ada).
Le classement publié ne change pas. Sorties : results/nosimd_check.json, results/report_nosimd.md."""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, E_V2  # noqa: E402

K1A, K1S, K1N = ("k1", "aos", "energy"), ("k1", "soa", "energy"), ("k1", "natural", "energy")
K5N, K5T = ("k5", "natural", ""), ("k5", "tuned", "")
Q6N, Q6T, Q6M = ("k6", "natural", "q6"), ("k6", "tuned", "q6"), ("k6", "mt", "q6")
Q1N, Q1T, Q1M = ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q1")
K9N, K9T, K9M = ("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")

# Table 2.1 de docs/NOSIMD.md : variantes du plafond écrites en SIMD explicite (les autres sont scalaires).
# V : types vectoriels du langage ; P : intrinsèques de la plateforme (chaîne standard) ; M : intrinsèques importées.
_ALLV = {K1S: "V", K5T: "V", Q6T: "V", Q1T: "V", K9T: "V"}
CLASS = {
    "c": {K1S: "P", K5T: "P", Q1T: "P"},
    "cpp": {K1S: "V", K5T: "V", Q6T: "V", Q1T: "V"},
    "zig": dict(_ALLV), "odin": dict(_ALLV), "c3": dict(_ALLV), "mojo": dict(_ALLV),
    "rust": {K1S: "P", K5T: "P", Q1T: "P"},
    "d": {K1S: "V", K5T: "V", Q1T: "V", K9T: "V"},
    "csharp": {**_ALLV, Q1T: "V+P"},
    "java": {K1S: "V", K5T: "V", Q6T: "V", Q1T: "V"},
    "go": {K1S: "P", K5T: "P", Q6T: "P"},
    "haskell": {K1S: "V", K5T: "V", K9T: "V"},
    "nim": {K1S: "M", K5T: "M"},
    "ada": {K5T: "M"},
}
E_NOMT = {k: [m for m in ms if not any(key[1] == "mt" for key in m)] for k, ms in E_V2.items()}
E_SYM = {**E_NOMT, "k1": [[K1A]], "k5": [[K5N]], "k6": [[Q6N], [Q1N]], "k9": [[K9N]]}
SCALAR_KERNELS = ("k3", "k4", "k7", "k8")


def kk(k):
    return ":".join(x for x in k if x)


def base(lang):
    return ANNEX.get(lang, lang)


def nan_cell(A, lang, key):
    if lang in A.idx:
        for est in ("mean", "min"):
            A.t[(est, key)][:, A.idx[lang]] = np.nan


def copy_cell(A, lang, dst, src):
    j = A.idx[lang]
    for est in ("mean", "min"):
        A.t[(est, dst)][:, j] = A.t[(est, src)][:, j]


def scale_cell(A, lang, key, r):
    j = A.idx[lang]
    for est in ("mean", "min"):
        A.t[(est, key)][:, j] *= r


def d_q1_ratio():
    tr = json.load(open(os.path.join(ROOT, "results", "transfers.json")))
    return tr["ratios"]["d"]["k6|tuned|q1"]


def patch_scalar(mojo_aos=False):
    r_d = d_q1_ratio()

    def patch(A):
        for l in A.langs:
            for key in CLASS.get(base(l), {}):
                if base(l) == "d" and key == Q1T:
                    continue
                nan_cell(A, l, key)
        scale_cell(A, "d", Q1T, 1 / r_d)  # Q1 en blocs d'avant la correction du 31/10 (forme scalaire)
        if mojo_aos:
            copy_cell(A, "mojo", K1A, K1N)
    return patch


def patch_imported(A):
    for l in A.langs:
        for key, cls in CLASS.get(base(l), {}).items():
            if cls == "M":
                nan_cell(A, l, key)


def chosen(A, lang):
    """Variante retenue par E (ligne 0, estimateur 'mean') pour chaque mesure."""
    j = A.idx[lang]
    out = {}
    for k, ms in A.e_meas.items():
        for i, ks in enumerate(ms):
            vals = [(A.t[("mean", key)][0, j], key) for key in ks]
            vals = [(v, key) for v, key in vals if np.isfinite(v)]
            out[f"{k}#{i}"] = (key_name(min(vals)[1]), 1e3 * min(vals)[0]) if vals else (None, None)
    return out


def key_name(key):
    return key[1] + (f" {key[2]}" if key[0] == "k6" else "")


def spearman(a, b):
    ls = list(a)
    ra = np.argsort(np.argsort([a[l] for l in ls]))
    rb = np.argsort(np.argsort([b[l] for l in ls]))
    return float(np.corrcoef(ra, rb)[0, 1])


def summary(s):
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    A = s["A"]
    tstar = {f"{k}#{i}": 1e3 * v for (k, i), v in s["refs"]["mean"]["tstar"].items()}
    return {"order21": order, "pos": {l: order.index(l) + 1 for l in RANKED}, "exp21": s["exp21"],
            "rank90": s["rank90"], "first": s["first"], "ms0": {l: s["ms0"][l] for l in RANKED},
            "E": {l: s["E"][l] for l in RANKED}, "D": {l: s["D"][l] for l in RANKED},
            "C": {l: s["C"][l] for l in RANKED}, "Ek": {l: s["Ek"][l] for l in RANKED},
            "tstar_ms": tstar, "tstar_src": s["tstar_src"], "e_meas": {k: [[kk(x) for x in m] for m in ms]
                                                                       for k, ms in A.e_meas.items()},
            "chosen": {l: chosen(A, l) for l in RANKED}}


def main():
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    plans = {
        "Publié": {},
        "Contrôle sans mt": {"e_meas": E_NOMT},
        "S-scalaire": {"e_meas": E_NOMT, "patch": patch_scalar()},
        "S-scalaire-Mojo": {"e_meas": E_NOMT, "patch": patch_scalar(mojo_aos=True)},
        "S-symétrique": {"e_meas": E_SYM},
        "S-noyaux-scalaires": {"e_drop": tuple(k for k in E_V2 if k not in SCALAR_KERNELS)},
        "S-importées": {"patch": patch_imported},
    }
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    suffix = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--suffix=")), "")
    out = {"class": {l: {kk(k): c for k, c in d.items()} for l, d in CLASS.items()}, "d_q1_ratio": d_q1_ratio(),
           "scenarios": {}}
    for name, kw in plans.items():
        if only and name not in only:
            continue
        z = out["scenarios"][name] = summary(cf.scenario(data, lat, langs, footprint, c3, "main", **kw))
        top = ", ".join(f"{NAMES[l]} {z['ms0'][l]:.1f}" for l in z["order21"][:6])
        print(f"{name} : {top}", flush=True)
    pub = out["scenarios"].get("Publié")
    if pub:
        # témoin : le publié du 1er novembre au matin (results/nim_check.json, « Avant ») ; avec un suffixe (état actuel),
        # le publié après la remarque sur Go (results/go_check.json, « G-E » ; avant elle, java_check.json, « J-E »,
        # k9_check.json, c_check.json, cpp_check.json et odin_check.json, « Publié », et c3_check.json, « Errata »)
        src = ("go_check.json", "G-E") if suffix else ("nim_check.json", "Avant")
        ref = json.load(open(os.path.join(ROOT, "results", src[0])))["scenarios"][src[1]]
        gap = max(max(abs(pub["ms0"][l] - ref["ms0"][l]), abs(pub["exp21"][l] - ref["exp21"][l])) for l in RANKED)
        out["check_published"] = {"max_gap": gap, "ok": gap < 1e-9, "ref": f"results/{src[0]}, « {src[1]} »"}
        print(f"Contrôle du témoin : écart maximal {gap:.2e} avec le scénario « {src[1]} » de results/{src[0]}")
        for name, z in out["scenarios"].items():
            z["spearman_vs_published"] = spearman(z["exp21"], pub["exp21"])
            z["moves"] = {l: z["pos"][l] - pub["pos"][l] for l in RANKED}
    if not only:
        json.dump(out, open(os.path.join(ROOT, "results", f"nosimd_check{suffix}.json"), "w"), indent=1, default=float)
        report(out, suffix)


def f(x, d=1):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}".replace(".", ",")


def report(o, suffix=""):
    S = o["scenarios"]
    pub = S["Publié"]
    names = list(S)
    L = ["# Sensibilité « sans SIMD explicite » : sorties de analysis/nosimd_check.py", "",
         "Plan : docs/NOSIMD.md (sections 2 et 3, poussées avant les calculs). Le classement publié ne change pas.", "",
         f"Témoin : écart maximal {o['check_published']['max_gap']:.1e} avec "
         f"{o['check_published'].get('ref', 'results/nim_check.json, « Avant »')}.", "",
         "## Rang (position par rang espéré) et score ponctuel", "",
         "| Langage | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for l in pub["order21"]:
        cells = [f"{S[n]['pos'][l]} ({f(S[n]['ms0'][l])})" for n in names]
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", "## Résumé par scénario", "",
          "| Scénario | Spearman / publié | 1er (part) | Places gagnées (+) ou perdues (−) par rapport au publié |",
          "|---|---|---|---|"]
    for n in names:
        z = S[n]
        first = max(z["first"], key=z["first"].get)
        mv = sorted(RANKED, key=lambda l: -abs(z["moves"][l]))
        moves = ", ".join(f"{NAMES[l]} {-z['moves'][l]:+d}" for l in mv if z["moves"][l]) or "aucune"
        L.append(f"| {n} | {f(z['spearman_vs_published'], 3)} | {NAMES[first]} ({f(100 * z['first'][first], 0)} %) | "
                 f"{moves} |")
    L += ["", "## Plafond E par scénario", "", "| Langage | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for l in pub["order21"]:
        L.append(f"| {NAMES[l]} | " + " | ".join(f(S[n]["E"][l]) for n in names) + " |")
    L += ["", "## Références t* (ms) et langage qui les fixe", ""]
    for n in names:
        z = S[n]
        L.append(f"* {n} : " + " ; ".join(f"{m} {f(z['tstar_ms'][m], 2)} ({NAMES.get(z['tstar_src'][m], z['tstar_src'][m])})"
                                         for m in z["tstar_ms"]))
    L += ["", "## Variante retenue par E dans S-scalaire (mesures vectorisables)", "",
          "| Langage | " + " | ".join(m for m in S["S-scalaire"]["chosen"]["c"] if m[:2] in ("k1", "k5", "k6", "k9")) + " |"]
    ms = [m for m in S["S-scalaire"]["chosen"]["c"] if m[:2] in ("k1", "k5", "k6", "k9")]
    L.append("|---|" + "---|" * len(ms))
    for l in pub["order21"]:
        ch = S["S-scalaire"]["chosen"][l]
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{ch[m][0]} {f(ch[m][1], 1)}" for m in ms) + " |")
    open(os.path.join(ROOT, "results", f"report_nosimd{suffix}.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
