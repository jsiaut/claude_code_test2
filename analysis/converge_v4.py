#!/usr/bin/env python3
"""v4, point 4 : analyse de la convergence (docs/V4_CONVERGE.md, section 8, fixée avant les mesures ; écarts 4.1 et
4.2).

La méthode v3 du calcul « Hôte » des points 2 et 3 (analysis/equal_v4.py : même graine, 20 000 variantes, mêmes poids,
grille v2 corrigée par le point 1) appliquée aux seules données de la campagne du point 4 (results/converge/raw,
tools/converge/campaign.py), avec les bornes physiques de son hôte (results/hw/machine33). Les formes viennent du relevé
(results/converge/forms.json, tools/converge/inventory.py) : chaque cellule d'une forme écrite (construction cv) ou
présente (construction pub) s'ajoute à l'ensemble « meilleur de » de sa cellule du plafond (K4, K5, Q6, Q1, Q6 mt,
Q1 mt, K7, K8, K9, K9 mt). Ses tirages suivent ceux des autres cellules du même noyau (mêmes réservoirs de résidus, bâtis
sur la base), chacun par un générateur à part (graine fixée par la cellule et le langage), pour que les tirages des
autres cellules et des variantes ne changent pas, et qu'une cellule soit tirée de la même façon dans tous les calculs.
Calculs :
1. Hôte : la base (construction pub : source publiée corrigée, cellules du score).
2. Convergent : toutes les formes admises (C1) : variantes publiées, K4 tuned de R3, formes du catalogue, formes
   propres au runtime.
3. Par noyau (information) : « Convergent » sur K4, K5, K6, K7, K8 ou K9 seul.
4. Remarques (information) : la base et les seules formes trouvées par la remarque du langage (relevé, « R »).
5. Convergent, sélection indépendante (sensibilité) : pour chaque langage et chaque cellule du plafond, la forme la plus
   rapide sur la passe 0 seule (moyenne géométrique des médianes de processus), estimée sur les passes 1 et 2 seules ;
   la cellule du plafond ne contient plus que cette forme (clé à part, tirée par son propre générateur).
6. Convergent, avec R4 (information) : K3 rapporté à b3 de cette campagne (comme au point 3 : temps de K3 relevés à b3
   au moins, référence de K3 égale à b3).
Information hors plan : « Hôte, source non corrigée » (contrôle de l'erratum, écart 4.1, 2) : les cellules que la
correction de la base change, mesurées sur la source du commit ea2da12 (construction old), à la place de celles de la
base.
Pour chaque calcul : scores, rangs espérés, rang plausible (90 %), étages indicatifs (règle v3 sans sa condition de
réplication), langages dont le rang change de plus de deux places par rapport à « Hôte » ; en descriptif, pour chaque
cellule du plafond et chaque langage, la forme retenue par « Convergent » (estimation ponctuelle) et son rapport à la
meilleure forme publiée ; les rapports old / pub des cellules corrigées.
Une cellule manquante de la base prend le temps admissible le plus lent des autres langages (comme aux points 2 et 3) ;
une nouvelle cellule manquante est absente de son ensemble, et le rapport la signale.
Sorties : results/converge/analysis.json, results/report_converge.md. Variables : BOOT (2000), UA (20000)."""
import copy, glob, json, math, os, re, sys, zlib
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sizes_v4 as S  # noqa: E402  (bornes physiques, résumé d'un calcul, cellules manquantes)
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ROOT, NAMES  # noqa: E402
from analyze_v3 import E_V2, K8N, build_pools, needed_keys, proc_logs, klass  # noqa: E402

RAW = os.path.join(ROOT, "results", "converge", "raw")
HW = os.path.join(ROOT, "results", "hw", "machine33")
FORMS = os.path.join(ROOT, "results", "converge", "forms.json")
OUT = os.path.join(ROOT, "results", "converge", "analysis.json")
REPORT = os.path.join(ROOT, "results", "report_converge.md")
CV_SEED = v3.SEED + 4404   # générateurs des nouvelles cellules (graine complétée par la cellule et le langage)
SEL_SEED = v3.SEED + 4405  # générateurs des cellules du calcul 5
# cellule du plafond -> (noyau, rang du groupe dans E_V2)
CEIL = {"K4": ("k4", 0), "K5": ("k5", 0), "Q6": ("k6", 0), "Q1": ("k6", 1), "Q6 mt": ("k6", 2), "Q1 mt": ("k6", 3),
        "K7": ("k7", 0), "K8": ("k8", 0), "K9": ("k9", 0), "K9 mt": ("k9", 1)}
K3K = [("k3", "sw_padded", ""), ("k3", "rmw_padded", "")]
KERNELS_E = ["k4", "k5", "k6", "k7", "k8", "k9"]
CALCS = ["Hôte", "Convergent"] + [f"Convergent, {k.upper()} seul" for k in KERNELS_E] + [
    "Remarques", "Convergent, sélection indépendante", "Convergent, avec R4", "Hôte, source non corrigée"]


# ------------------------------------------------------------------ données
def load():
    """{construction: {langage: {clé: [processus]}}} (un processus : [médiane de ses répétitions]), la même chose
    avec la passe de chaque processus, latences de K8, échecs, vol de temps, modèles. Un processus est retenu s'il a
    fini sans erreur, sans dépassement de mémoire ni de durée, et si toutes ses sommes de contrôle sont justes."""
    data, bypass = defaultdict(lambda: defaultdict(dict)), defaultdict(lambda: defaultdict(dict))
    lat = defaultdict(lambda: defaultdict(dict))
    failures, steal, models = [], [], defaultdict(lambda: defaultdict(int))
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            models[r.get("cpu_model", "?")][r.get("pass")] += 1
            key = (r["kernel"], r["variant"], r["param"])
            ok = (not r.get("failed_calibration") and r.get("returncode") == 0 and not r.get("oom")
                  and not r.get("timeout") and r.get("n", 0) > 0 and r.get("oks") == ["True"])
            if not ok:
                fc = r.get("failed_calibration") or {}
                failures.append({"lang": r["lang"], "build": r["build"], "key": key, "pass": r.get("pass"),
                                 "oom": bool(r.get("oom") or fc.get("oom")),
                                 "timeout": bool(r.get("timeout") or fc.get("timeout")),
                                 "returncode": r.get("returncode", fc.get("returncode")), "oks": r.get("oks"),
                                 "stderr": (r.get("stderr") or fc.get("stderr") or "")[-300:]})
                continue
            if r.get("steal_frac", 0) > 0.05:
                steal.append((r["lang"], r["build"], key, r["steal_frac"]))
            data[r["build"]][r["lang"]].setdefault(key, []).append([r["median"]])
            bypass[r["build"]][r["lang"]].setdefault(key, []).append((r["pass"], r["median"]))
            if key == K8N:
                lat[r["build"]][r["lang"]].setdefault(key, []).append(r.get("lat", []))
    return data, bypass, lat, failures, steal, {m: dict(ps) for m, ps in models.items()}


def forms_cells(langs):
    """{langage: [(construction, clé, cellule du plafond, forme, remarque)]} des formes écrites ou présentes."""
    js = json.load(open(FORMS))["langs"]
    out = {}
    for l in langs:
        rows = []
        for form, x in sorted(js.get(l, {}).items()):
            if x["status"] not in ("écrite", "présente"):
                continue
            for c in x["cells"]:
                key = tuple(c)
                rows.append(("cv" if x["status"] == "écrite" else "pub", key, x["ceiling"], form, bool(x["remarque"])))
        out[l] = rows
    return out


def b3_value():
    """b3 en secondes et ses mesures (médianes des 16 décalages, en ms, par exécution)."""
    vals = {}
    for which in ("start", "end"):
        p = os.path.join(ROOT, "results", "converge", f"k3_ref_{which}.txt")
        if not os.path.exists(p):
            continue
        runs, cur = [], []
        for line in open(p):
            m = re.match(r"décalage\s+(\d+) octets :\s+([\d.]+) ms", line)
            if m:
                cur.append(float(m.group(2)))
            elif line.startswith("---") and cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        assert all(len(r) == 16 for r in runs), (which, [len(r) for r in runs])
        vals[which] = [float(np.median(r)) for r in runs]
    if not vals:
        return None, vals
    parts = [float(np.mean(v)) for v in vals.values()]
    return 1e-3 * float(np.mean(parts)), vals


def hw_numbers():
    saved = S.HW
    S.HW = HW
    try:
        return S.hw_numbers()
    finally:
        S.HW = saved


def gm(procs):
    return math.exp(float(np.mean(np.log([float(np.median(p)) for p in procs]))))


def seed_of(base, key, lang):
    return [base, zlib.crc32("|".join(key).encode()), zlib.crc32(lang.encode())]


# ------------------------------------------------------------------ calculs
def additions(data, fc, langs, kernels=None, remark_only=False):
    """Nouvelles cellules d'un calcul : {clé: {langage: processus}}, et leur cellule du plafond. Les cellules des formes
    présentes déjà dans la base ne s'ajoutent pas (elles y sont)."""
    add, ceil_of, missing = defaultdict(dict), {}, []
    for l in langs:
        for build, key, ceil, form, rq in fc.get(l, []):
            if kernels and CEIL[ceil][0] not in kernels:
                continue
            if remark_only and not rq:
                continue
            if build == "pub" and key in data["pub"].get(l, {}):
                continue
            procs = data.get("cv", {}).get(l, {}).get(key) or data.get(build, {}).get(l, {}).get(key)
            if not procs:
                missing.append([l, build, "|".join(key)])
                continue
            assert ceil_of.get(key, ceil) == ceil, (key, ceil_of.get(key), ceil)
            ceil_of[key] = ceil
            add[key][l] = procs
    return add, ceil_of, missing


def e_meas_with(ceil_of, sel=None):
    """E_V2 (même ordre des noyaux et des groupes : les poids tirés ne changent pas), chaque nouvelle clé ajoutée au
    groupe de sa cellule du plafond ; avec sel, chaque groupe remplacé par la clé de sélection du calcul 5."""
    e = copy.deepcopy(E_V2)
    if sel is not None:
        for ceil, (k, gi) in CEIL.items():
            e[k][gi] = [sel[ceil]]
        return e
    for key in sorted(ceil_of):
        k, gi = CEIL[ceil_of[key]]
        if key not in e[k][gi]:
            e[k][gi] = e[k][gi] + [key]
    return e


def fill_patch(d, langs, add):
    """Remplit les temps simulés des nouvelles clés : estimation ponctuelle et tirages dans les réservoirs du noyau de
    la cellule (bâtis sur la base du calcul, comme dans Arrays3), un générateur par cellule et par langage."""
    def patch(A):
        pools = build_pools(d, langs, sorted(needed_keys()))
        for key in sorted(add):
            mean = np.full((A.nb + 1, len(langs)), np.nan)
            mn = np.full((A.nb + 1, len(langs)), np.nan)
            for l, procs in add[key].items():
                y = proc_logs(procs)
                j = A.idx[l]
                mean[0, j], mn[0, j] = math.exp(y.mean()), math.exp(y.min())
                if A.nb:
                    g = np.random.default_rng(seed_of(CV_SEED if not key[1].startswith("sel ") else SEL_SEED, key, l))
                    pool = pools[(key[0], klass(l))]
                    draws = y.mean() + pool[g.integers(0, len(pool), size=(A.nb, len(y)))]
                    mean[1:, j], mn[1:, j] = np.exp(draws.mean(axis=1)), np.exp(draws.min(axis=1))
            A.t[("mean", key)], A.t[("min", key)] = mean, mn
    return patch


def r4_patch(b3):
    """Temps de K3 relevés à b3 au moins : avec la référence b3, la cellule vaut min(1, b3 / t)."""
    def patch(A):
        for est in ("mean", "min"):
            for k in K3K:
                A.t[(est, k)] = np.maximum(A.t[(est, k)], b3)
    return patch


def selection(data, bypass, fc, langs):
    """Calcul 5 : clé de sélection par cellule du plafond, et ses processus (passes 1 et 2) par langage ; le choix (passe
    0) est rendu pour le rapport."""
    sel_keys = {ceil: (k, "sel " + ceil, "") for ceil, (k, gi) in CEIL.items()}
    add, chosen = defaultdict(dict), {}
    for l in langs:
        cand = defaultdict(list)  # cellule -> [(construction, clé)]
        for ceil, (k, gi) in CEIL.items():
            for key in E_V2[k][gi]:
                cand[ceil].append(("pub", key))
        for build, key, ceil, form, rq in fc.get(l, []):
            b = "cv" if key in bypass.get("cv", {}).get(l, {}) else build
            if (b, key) not in cand[ceil]:
                cand[ceil].append((b, key))
        for ceil, lst in cand.items():
            best = None
            for b, key in lst:
                p0 = [m for p, m in bypass.get(b, {}).get(l, {}).get(key, []) if p == 0]
                if not p0:
                    continue
                t0 = math.exp(float(np.mean(np.log(p0))))
                if best is None or t0 < best[0]:
                    best = (t0, b, key)
            if best is None:
                continue
            _, b, key = best
            later = [[m] for p, m in bypass[b][l][key] if p in (1, 2)]
            if later:
                add[sel_keys[ceil]][l] = later
                chosen[f"{l}|{ceil}"] = [b, "|".join(key)]
    return sel_keys, add, chosen


def run_calc(calc, data, bypass, lat, fc, langs, footprint, c3, eb, b3, keys):
    d = {l: dict(data["pub"].get(l, {})) for l in langs}
    lt = {l: dict(lat["pub"].get(l, {})) for l in langs}
    missing, chosen = [], None
    if calc == "Hôte, source non corrigée":
        for l in langs:
            for key, procs in data.get("old", {}).get(l, {}).items():
                if key in d[l]:
                    d[l][key] = procs
                    if key == K8N and lat.get("old", {}).get(l, {}).get(K8N):
                        lt[l][K8N] = lat["old"][l][K8N]
                else:
                    missing.append([l, "old", "|".join(key)])
    filled = S.fill_missing(d, langs, keys)
    e_meas, patches = None, []
    if calc.startswith("Convergent") or calc == "Remarques":
        if calc == "Convergent, sélection indépendante":
            sel_keys, add, chosen = selection(data, bypass, fc, langs)
            e_meas = e_meas_with({}, sel=sel_keys)
        else:
            kern = None
            m = re.match(r"Convergent, (K\d) seul", calc)
            if m:
                kern = [m.group(1).lower()]
            add, ceil_of, missing = additions(data, fc, langs, kernels=kern, remark_only=(calc == "Remarques"))
            e_meas = e_meas_with(ceil_of)
        patches.append(fill_patch(d, langs, add))
    r4 = calc == "Convergent, avec R4"
    if r4:
        patches.append(r4_patch(b3))
    patch = (lambda A: [p(A) for p in patches]) if patches else None
    saved_eb, saved_ref = v3.EBOUND, cf.references
    v3.EBOUND = dict(eb)
    if r4:
        v3.EBOUND[("k3", 0)] = b3

        def references(A, est):
            ref = saved_ref(A, est)
            ref["tstar"][("k3", 0)] = b3
            return ref
        cf.references = references
    try:
        s = cf.scenario(d, lt, langs, footprint, c3, "main", e_meas=e_meas, patch=patch)
    finally:
        v3.EBOUND, cf.references = saved_eb, saved_ref
    out = S.summarize(s, langs)
    out["missing"] = missing
    out["filled"] = [list(map(str, x)) for x in filled]
    if chosen is not None:
        out["chosen"] = chosen
    return out


# ------------------------------------------------------------------ descriptif
def retained(data, fc, langs):
    """Pour chaque langage et cellule du plafond : la forme la plus rapide parmi les formes admises (estimation
    ponctuelle : moyenne géométrique des médianes de processus), la meilleure forme publiée, et leur rapport."""
    out = {}
    for l in langs:
        row = {}
        for ceil, (k, gi) in CEIL.items():
            pub = [(gm(data["pub"][l][key]), "pub", key) for key in E_V2[k][gi] if data["pub"].get(l, {}).get(key)]
            new = []
            for build, key, c, form, rq in fc.get(l, []):
                if c != ceil:
                    continue
                procs = data.get("cv", {}).get(l, {}).get(key) or data.get(build, {}).get(l, {}).get(key)
                if procs:
                    new.append((gm(procs), build, key, form, rq))
            if not pub and not new:
                continue
            bp = min(pub) if pub else None
            allf = [(t, b, key, "publiée", False) for t, b, key in pub] + new
            best = min(allf, key=lambda x: x[0])
            row[ceil] = {"best_published": bp[0] if bp else None,
                         "best_published_key": "|".join(bp[2]) if bp else None,
                         "retained": best[0], "retained_key": "|".join(best[2]), "retained_form": best[3],
                         "retained_remark": best[4], "ratio": best[0] / bp[0] if bp else None}
        out[l] = row
    return out


def erratum_ratios(data, langs):
    out = {}
    for l in langs:
        row = {}
        for key, procs in data.get("old", {}).get(l, {}).items():
            p = data["pub"].get(l, {}).get(key)
            if p:
                row["|".join(key)] = gm(procs) / gm(p)
        if row:
            out[l] = row
    return out


def main():
    v2.ADDED.clear()  # une seule campagne : aucun langage relié par un pont
    data, bypass, lat, failures, steal, models = load()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    hw = hw_numbers()
    eb = S.ebounds(hw, 1)
    eb[("k5", 0)] = S.ebounds(hw, 0)[("k5", 0)]  # K5 à sa taille publiée (position « petite » du tableau du point 2)
    b3, b3_runs = b3_value()
    langs = list(RANKED)
    fc = forms_cells(langs)
    keys = S.campaign_keys({"pub": data["pub"]})
    calcs = [c for c in CALCS if c != "Convergent, avec R4" or b3 is not None]
    res = {c: run_calc(c, data, bypass, lat, fc, langs, footprint, c3, eb, b3, keys) for c in calcs}
    h = res["Hôte"]["order"]
    moved = {c: S.moved(h, res[c]["order"], langs) for c in calcs[1:]}
    out = {"results": res, "moved_more_than_2": moved, "b3": b3, "b3_runs_ms": b3_runs,
           "bounds": {f"{k}#{i}": v for (k, i), v in eb.items()}, "hw": {k: v for k, v in hw.items()},
           "retained": retained(data, fc, langs), "erratum": erratum_ratios(data, langs),
           "failures": failures, "steal_over_5pct": steal, "cpu_models": models}
    eq = json.load(open(os.path.join(ROOT, "results", "equal", "analysis.json")))["results"]["Hôte"]
    out["point3_host"] = {"order": eq["order"], "exp": eq["exp"], "ms0": eq["ms0"]}
    pub = json.load(open(os.path.join(ROOT, "results", "audit3.json")))["scenarios"]["Publié"]
    out["published"] = {"order": pub["order21"], "exp": pub["exp21"], "ms0": pub["ms0"], "tiers": pub["tiers"]}
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    report(out, calcs)


# ------------------------------------------------------------------ rapport
def report(o, calcs):
    R = o["results"]
    main_calcs = [c for c in calcs if " seul" not in c]
    L = ["# v4, point 4 : un code optimisé convergent — résultats", "",
         "*Plan : `docs/V4_CONVERGE.md` (sections 3 à 8, écarts 4.1 et 4.2). Généré par `analysis/converge_v4.py` à "
         "partir de `results/converge/raw` et du relevé des formes (`results/converge/forms.json`). Le classement de "
         "tête du README ne change pas au point 4 (section 9).*", ""]
    if o["b3"] is not None:
        L += [f"b3 = {1e3 * o['b3']:.2f} ms (médianes des 16 décalages : "
              + " ; ".join(f"{w} " + ", ".join(f"{x:.2f}" for x in v) for w, v in o["b3_runs_ms"].items()) + " ms).", ""]
    L += ["## Classements", "", "| Langage | " + " | ".join(main_calcs) + " |", "|---|" + "---|" * len(main_calcs)]
    for l in R["Hôte"]["order"]:
        cells = []
        for c in main_calcs:
            r = R[c]
            p = r["order"].index(l) + 1
            mark = "" if c == "Hôte" or abs(p - R["Hôte"]["order"].index(l) - 1) <= 2 else " **"
            cells.append(f"{p}{mark} ({r['exp'][l]:.2f} ; {r['ms0'][l]:.1f})")
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", "Chaque case : place (rang espéré ; score au centre) ; ** : plus de deux places d'écart avec « Hôte ». "
          "Ordre des lignes : « Hôte ».", "", "## Par noyau (information) : « Convergent » sur un seul noyau", "",
          "| Langage | Hôte | " + " | ".join(k.upper() for k in KERNELS_E) + " | Convergent |",
          "|---|---|" + "---|" * (len(KERNELS_E) + 1)]
    for l in R["Hôte"]["order"]:
        row = [f"{R['Hôte']['order'].index(l) + 1}"]
        for k in KERNELS_E:
            c = f"Convergent, {k.upper()} seul"
            row.append(f"{R[c]['order'].index(l) + 1} ({R[c]['exp'][l]:.2f})" if c in R else "–")
        row.append(f"{R['Convergent']['order'].index(l) + 1} ({R['Convergent']['exp'][l]:.2f})")
        L.append(f"| {NAMES[l]} | " + " | ".join(row) + " |")
    L += ["", "## Rangs plausibles (90 %)", "", "| Langage | " + " | ".join(main_calcs) + " |",
          "|---|" + "---|" * len(main_calcs)]
    for l in R["Hôte"]["order"]:
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{R[c]['rank90'][l][0]}–{R[c]['rank90'][l][1]}" for c in main_calcs)
                 + " |")
    L += ["", "## Rangs qui bougent de plus de deux places par rapport à « Hôte »", ""]
    for c in calcs[1:]:
        mv = o["moved_more_than_2"][c]
        L.append(f"* {c} : " + (", ".join(f"{NAMES[l]} {a}e → {b}e" for l, (a, b) in
                                         sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"))
    L += ["", "## Étages indicatifs (paires ordonnées dans au moins 95 % des variantes)", ""]
    for c in main_calcs:
        L.append(f"* {c} : " + " | ".join(", ".join(NAMES[l] for l in t) for t in R[c]["tiers"]))
    L += ["", "## Forme retenue par « Convergent », cellule par cellule (estimation ponctuelle)", "",
          "Chaque case : forme retenue (« publiée » : une variante publiée ; R : trouvée par la remarque du langage) et "
          "rapport de son temps à la meilleure forme publiée ; « – » : pas de cellule.", "",
          "| Langage | " + " | ".join(CEIL) + " |", "|---|" + "---|" * len(CEIL)]
    for l in R["Hôte"]["order"]:
        row = []
        for ceil in CEIL:
            x = o["retained"].get(l, {}).get(ceil)
            if not x:
                row.append("–")
                continue
            name = x["retained_form"] + (" R" if x["retained_remark"] else "")
            row.append(f"{name} {x['ratio']:.2f}" if x["ratio"] else name)
        L.append(f"| {NAMES[l]} | " + " | ".join(row) + " |")
    if "Convergent, sélection indépendante" in R:
        ch = R["Convergent, sélection indépendante"].get("chosen", {})
        L += ["", f"Sélection indépendante (calcul 5) : {len(ch)} choix faits sur la passe 0 (détail dans "
              "`results/converge/analysis.json`)."]
    E = o["erratum"]
    L += ["", "## Contrôle de l'erratum : source non corrigée / source corrigée (même hôte)", "",
          "| Langage | Cellules (rapport des temps) |", "|---|---|"]
    for l in R["Hôte"]["order"]:
        if l in E:
            L.append(f"| {NAMES[l]} | " + ", ".join(f"{k.replace('|', ' ').strip()} {v:.2f}" for k, v in sorted(E[l].items()))
                     + " |")
    P3 = o["point3_host"]
    L += ["", "## Réplication descriptive : « Hôte » du point 3 (machine 32, source non corrigée) et de ce point", "",
          "| Langage | point 3 | point 4 |", "|---|---|---|"]
    for l in R["Hôte"]["order"]:
        L.append(f"| {NAMES[l]} | {P3['order'].index(l) + 1} ({P3['exp'][l]:.2f}) | "
                 f"{R['Hôte']['order'].index(l) + 1} ({R['Hôte']['exp'][l]:.2f}) |")
    L += ["", "## Cellules", ""]
    for c in calcs:
        r = R[c]
        if r["missing"] or r["filled"]:
            L.append(f"* {c} : nouvelles cellules manquantes : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} {x[2]}" for x in r["missing"]) or "aucune")
                     + " ; cellules de la base manquantes (temps le plus lent des autres langages) : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]}" for x in r["filled"]) or "aucune"))
    cm, fl = o["cpu_models"], o["failures"]
    L += ["", "Processeur des enregistrements : " + " ; ".join(
        f"{m} ({sum(ps.values())} enregistrements ; passes {', '.join(str(p) for p in sorted(ps, key=str))})"
        for m, ps in cm.items()) + (" — **plusieurs modèles**" if len(cm) > 1 else "") + ".", "",
          f"Processus écartés : {len(fl)} (toutes passes) ; vol de temps > 5 % après reprise : "
          f"{len(o['steal_over_5pct'])}."]
    for f in fl:
        L.append(f"* {NAMES.get(f['lang'], f['lang'])} {f['build']} {' '.join(f['key'])} passe {f['pass']} : code "
                 f"{f['returncode']}, contrôles {f['oks']}{', hors mémoire' if f['oom'] else ''}"
                 f"{', durée' if f['timeout'] else ''}")
    open(REPORT, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
