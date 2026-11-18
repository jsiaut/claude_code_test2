#!/usr/bin/env python3
"""Troisième remarque générale (plan : docs/AUDIT3_RESPONSE.md, sections 1 et 2, poussées avant ce calcul).

Sans remesure, sur les données du classement publié (analyse globale de la v3 rejouée, mêmes tirages) :
* Publié : contrôle, doit reproduire P-E de results/php_check.json ;
* M-mesures : poids du contrôle nul au centre et dans chaque variante (plafond et code par défaut renormalisés) ;
  étages indicatifs par la règle v3 sans sa condition de réplication (paires ordonnées dans au moins 95 % des tirages) ;
* substitutions : les clés mesurées par chaque implémentation en annexe remplacent celles de la chaîne classée (même
  grille), une à la fois ;
* les trois quantités du plan v3, par langage (plafond, code naturel, contrôle v2 et v1), avec leur rang ;
* les variantes des remarques, relues dans leurs sorties ;
* l'état de preuve de la grille : cases sondées (results/probes/*.txt), mesurées (C3) ou lues, par langage et par
  catégorie.
Sorties : results/audit3.json, results/report_audit3.md."""
import glob, json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import confrontation as cf  # noqa: E402
import php_check as pc  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from capabilities import M  # noqa: E402
from python_check import f  # noqa: E402

ANNEX_NAMES = {"c_gcc": "C par GCC 16", "fortran_flang": "Fortran par flang", "luajit": "LuaJIT",
               "js_bun": "JavaScript par Bun", "python_ft": "CPython sans GIL"}


def measures_only(wp):
    s = wp[1] + wp[2]
    return {"C": 0.0, "E": wp[1] / s, "D": wp[2] / s}


def tiers(order, prec, idx, level=0.95):
    """Frontières entre i et i + 1 : toutes les paires de part et d'autre ordonnées dans au moins level des tirages."""
    cuts = [i for i in range(1, len(order))
            if all(prec[idx[a], idx[b]] >= level for a in order[:i] for b in order[i:])]
    bounds = [0] + cuts + [len(order)]
    return [order[bounds[j]:bounds[j + 1]] for j in range(len(bounds) - 1)]


def run(data, lat, langs, footprint, c3, wmap=None):
    s = cf.scenario(data, lat, langs, footprint, c3, "main", wmap=wmap)
    z = pc.summary(s, list(RANKED))
    idx = {l: i for i, l in enumerate(RANKED)}
    z["tiers"] = tiers(z["order21"], s["prec"], idx)
    z["prec_full"] = {a: {b: float(s["prec"][idx[a], idx[b]]) for b in RANKED} for a in RANKED}
    return z


def substituted(data, lat, annex):
    lang = ANNEX[annex]
    d = {l: v for l, v in data.items()}
    d[lang] = {**data[lang], **data[annex]}
    lt = {l: v for l, v in lat.items()}
    if lat.get(annex):
        lt[lang] = {**lat.get(lang, {}), **lat[annex]}
    return d, lt


def evidence():
    sys.path.insert(0, os.path.join(ROOT, "analysis"))
    from capabilities import MATRIX
    probed = {}
    for fn in glob.glob(os.path.join(ROOT, "results", "probes", "*.txt")):
        lang = os.path.basename(fn)[:-4]
        for line in open(fn, errors="replace"):
            p = line.rstrip("\n").split(";", 3)
            if len(p) == 4 and p[0] == "CAP":
                probed.setdefault(lang, set()).add(p[1])
    out = {}
    for l in RANKED:
        cells = MATRIX[l]
        meas = {c for c, v in cells.items() if v == M}
        pr = (probed.get(l, set()) & set(cells)) - meas
        out[l] = {"sondées": sorted(pr), "mesurées": sorted(meas),
                  "lues": sorted(c for c in cells if c not in pr and c not in meas)}
    return out


def variants_from_remarks():
    def g(name):
        return json.load(open(os.path.join(ROOT, "results", name)))["scenarios"]
    spec = [("Zig 0.18-dev (préversion)", "zig", "zig_check.json", "S1", "actuel"),
            ("C++ avec le K4 de clang++", "cpp", "c_check_current.json", "T1", "actuel"),
            ("C# sous .NET 11 (préversion)", "csharp", "csharp_check_current.json", "S-N11", "actuel"),
            ("PHP, CLI par défaut (ni OPcache ni JIT)", "php", "php_check.json", "P-défaut", "actuel"),
            ("PHP, stencil compilé par le JIT de 8.3", "php", "php_remark.json", "R-K9-83", "actuel"),
            ("Swift -Ounchecked (sans vérifications)", "swift", "swift_check.json", "S-Ou", "5 novembre, 22 langages"),
            ("FreePascal 3.2.4-rc2", "fpc", "fpc_remark.json", "R-rc2", "6 novembre, 23 langages"),
            ("FreePascal, branche main", "fpc", "fpc_remark.json", "R-main", "6 novembre, 23 langages")]
    out = []
    for label, lang, fn, key, state in spec:
        z = g(fn)[key]
        order = z.get("order21") or sorted(z["exp21"], key=z["exp21"].get)
        out.append({"variante": label, "langage": lang, "score": z["ms0"][lang], "rang_espere": z["exp21"][lang],
                    "place": order.index(lang) + 1, "n": len(order), "source": f"{fn} : {key}", "etat": state})
    return out


def main():
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    out = {"scenarios": {}}
    pub = out["scenarios"]["Publié"] = run(data, lat, langs, footprint, c3)
    ref = json.load(open(os.path.join(ROOT, "results", "php_check.json")))["scenarios"]["P-E"]
    out["check"] = max(max(abs(pub["ms0"][l] - ref["ms0"][l]), abs(pub["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Publié à P-E = {out['check']:.2e}", flush=True)
    mm = out["scenarios"]["M-mesures"] = run(data, lat, langs, footprint, c3, wmap=measures_only)
    print("M-mesures : " + ", ".join(f"{i + 1}. {NAMES[l]} ({mm['exp21'][l]:.2f})" for i, l in enumerate(mm["order21"])),
          flush=True)
    print("M-mesures, étages indicatifs : " + str([len(t) for t in mm["tiers"]]), flush=True)
    out["substitutions"] = {}
    for annex in ANNEX:
        d, lt = substituted(data, lat, annex)
        z = run(d, lt, langs, footprint, c3)
        lang = ANNEX[annex]
        out["substitutions"][annex] = {"langage": lang, "score": z["ms0"][lang], "rang_espere": z["exp21"][lang],
                                       "place": z["order21"].index(lang) + 1, "rang90": z["rank90"][lang],
                                       "cles": len(data[annex]), "cles_langage": len(data[lang])}
        print(f"{ANNEX_NAMES[annex]} à la place de {NAMES[lang]} : {z['ms0'][lang]:.2f} points, rang espéré "
              f"{z['exp21'][lang]:.2f} ({z['order21'].index(lang) + 1}e)", flush=True)
    s3 = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))["results"]
    q = {}
    for l in RANKED:
        r = s3[l]
        q[l] = {"E": r["E"], "D": r["D"], "D1": r["D_parts"]["D1"], "own_gap": r.get("own_gap"), "C_v2": r["C_v2"],
                "C_v1": r["C_v1"], "MS": r["MS"]}
    for k in ("E", "D", "D1", "C_v2", "C_v1"):
        order = sorted(RANKED, key=lambda l: -q[l][k])
        for i, l in enumerate(order):
            q[l]["rang_" + k] = i + 1
    out["quantites"] = q
    out["variantes"] = variants_from_remarks()
    out["preuves"] = evidence()
    for name in ("Publié", "M-mesures"):
        out["scenarios"][name].pop("prec_full", None)
    json.dump(out, open(os.path.join(ROOT, "results", "audit3.json"), "w"), indent=1, default=float)
    report(out)


def report(o):
    pub, mm = o["scenarios"]["Publié"], o["scenarios"]["M-mesures"]
    q = o["quantites"]
    L = ["# Troisième remarque générale : les mesures et la grille, séparément\n",
         "Plan : `docs/AUDIT3_RESPONSE.md`. Code : `analysis/audit3.py`. Aucune mesure nouvelle.",
         f"Contrôle : le scénario Publié reproduit P-E de `results/php_check.json` (écart maximal {o['check']:.1e}).\n",
         "## Les trois quantités du plan v3, et le classement sur les seules mesures\n",
         "Plafond E et code naturel D1 (sur 100, référence fixe) ; contrôle C, règle v2 (v1 entre parenthèses) ; rang de "
         "chaque quantité parmi les 25. M-mesures : poids du contrôle nul, au centre et dans les 20 000 variantes.\n",
         "| Rang publié | Étage | Langage | Plafond (rang) | Code naturel D1 (rang) | Contrôle v2 (v1) (rang) | "
         "M-mesures : rang espéré | place | rang à 90 % |",
         "|---|---|---|---|---|---|---|---|---|"]
    tier_of = {l: j + 1 for j, t in enumerate(pub["tiers"]) for l in t}
    for i, l in enumerate(pub["order21"]):
        L.append(f"| {i + 1} | {tier_of[l]} | {NAMES[l]} | {f(q[l]['E'], 1)} ({q[l]['rang_E']}) | "
                 f"{f(100 * q[l]['D1'], 1)} ({q[l]['rang_D1']}) | {f(q[l]['C_v2'], 1)} ({f(q[l]['C_v1'], 1)}) "
                 f"({q[l]['rang_C_v2']}) | {f(mm['exp21'][l], 2)} | {mm['order21'].index(l) + 1} | "
                 f"{mm['rank90'][l][0]}–{mm['rank90'][l][1]} |")
    L += ["", "Étages publiés (règle v3) : " + " | ".join(", ".join(NAMES[l] for l in sorted(t)) for t in pub["tiers"]) + ".",
          "Étages de M-mesures (indicatifs : paires ordonnées dans au moins 95 % des tirages, sans la condition de "
          "réplication) : " + " | ".join(", ".join(NAMES[l] for l in sorted(t)) for t in mm["tiers"]) + ".", "",
          "## Substitutions (implémentations en annexe, mesurées dans la campagne principale)\n",
          "| Variante | à la place de | clés remplacées | score | rang espéré | place | rang à 90 % |", "|---|---|---|---|---|---|---|"]
    for a, z in o["substitutions"].items():
        L.append(f"| {ANNEX_NAMES[a]} | {NAMES[z['langage']]} ({f(pub['ms0'][z['langage']], 1)} ; "
                 f"{pub['order21'].index(z['langage']) + 1}e) | {z['cles']} sur {z['cles_langage']} | {f(z['score'], 1)} | "
                 f"{f(z['rang_espere'], 2)} | {z['place']}e | {z['rang90'][0]}–{z['rang90'][1]} |")
    L += ["", "## Variantes des remarques (relues dans leurs sorties)\n",
          "| Variante | score | rang espéré | place | état | source |", "|---|---|---|---|---|---|"]
    for v in o["variantes"]:
        L.append(f"| {v['variante']} | {f(v['score'], 1)} | {f(v['rang_espere'], 2)} | {v['place']}e sur {v['n']} | "
                 f"{v['etat']} | `results/{v['source']}` |")
    L += ["", "## État de preuve de la grille\n",
          "| Langage | sondées | mesurées | lues | cases lues |", "|---|---|---|---|---|"]
    tot = {"sondées": 0, "mesurées": 0, "lues": 0}
    for l in RANKED:
        e = o["preuves"][l]
        for k in tot:
            tot[k] += len(e[k])
        L.append(f"| {NAMES[l]} | {len(e['sondées'])} | {len(e['mesurées'])} | {len(e['lues'])} | "
                 f"{', '.join(e['lues']) if len(e['lues']) < 34 else 'toutes'} |")
    n = sum(tot.values())
    L.append(f"| **Total** | {tot['sondées']} | {tot['mesurées']} | {tot['lues']} | "
             f"{f(100 * (tot['sondées'] + tot['mesurées']) / n, 1)} % sondées ou mesurées |")
    open(os.path.join(ROOT, "results", "report_audit3.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
