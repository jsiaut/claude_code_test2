#!/usr/bin/env python3
"""v4, point 3 : analyse des conditions égales (docs/V4_EQUAL.md, section 8, fixée avant les mesures ; écarts 5.1 et
5.2).

La méthode v3 du calcul « Hôte » du point 2 (analysis/sizes_v4.py : même graine, 20 000 variantes, mêmes poids, grille
v2 corrigée par le point 1) appliquée aux seules données de la campagne du point 3 (results/equal/raw,
tools/equal/campaign.py, machine 32), avec les bornes physiques de cet hôte (results/hw/machine32). Chaque calcul part
de la base (construction pub : binaires publiés, taille publiée) et remplace directement les cellules qu'une règle
change par celles qui sont mesurées dans le nouveau mode ou la nouvelle forme, sans report de rapport :
1. Hôte : la base.
2. R1 : les cellules naturelles (K1 natural et natural_shuffled, K4 natural_unsorted, K5, K6 Q6 et Q1, K7, K8 et ses
   latences, K9) des 8 langages de R1, mesurées dans le mode vérifié (construction chk) ; elles servent au code par
   défaut (D1, D2, D3) et, là où la variante naturelle entre dans le plafond (K4 à K9), au plafond.
3. R1' (sensibilité) : de même pour les 9 langages de R1' (construction unc ; D compris, écart 5.2).
4. R2 : K9 natural des 13 langages imbriqués remplacé par K9 natural_flat (construction eq, mode publié).
5. R3 : plafond de K4 au meilleur de natural_unsorted, branchless_unsorted et tuned (construction eq). La nouvelle
   cellule est tirée comme les autres (mêmes réservoirs de résidus que K4) par un générateur à part, pour que les
   tirages des autres cellules et des variantes ne changent pas.
6. R4 : cellule de K3 du plafond égale à min(1, b3 / t) dans toutes les variantes (normalisations « frontière » et
   « bornes », estimateurs « mean » et « min ») : les temps de K3 sont relevés à b3 au moins, et la référence de K3
   vaut b3 dans les deux normalisations. b3 : moyenne des mesures du début et de la fin de la campagne
   (results/equal/k3_ref_start.txt et k3_ref_end.txt ; chacune, moyenne des médianes de ses deux exécutions).
7. Toutes : R1, R2 (K9 contigu dans le mode R1 pour C++ et D : construction eq_chk), R3 et R4.
8. Toutes, R1' au lieu de R1 : R1', R2 (K9 contigu dans le mode R1' pour Nim, Mojo, Swift, Go, OCaml et D :
   construction eq_unc), R3 et R4.
Pour chaque calcul : scores, rangs espérés, rang plausible (90 %), étages indicatifs (règle v3 sans sa condition de
réplication), langages dont le rang change de plus de deux places par rapport à « Hôte ». En descriptif : le rapport
des temps de chaque nouvelle cellule à sa référence (moyennes géométriques des médianes de processus), et la
comparaison du calcul « Hôte » de la machine 31 (point 2) avec celui de la machine 32.
Une cellule manquante de la base prend le temps admissible le plus lent des autres langages (comme au point 2) ; une
nouvelle cellule manquante laisse la cellule de la base, et le rapport la signale.
Sorties : results/equal/analysis.json, results/report_equal.md. Variables : BOOT (2000), UA (20000)."""
import glob, json, math, os, re, sys
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

sys.path.insert(0, os.path.join(ROOT, "tools", "equal"))
import campaign as Cm  # noqa: E402  (constructions, cellules naturelles)

RAW = os.path.join(ROOT, "results", "equal", "raw")
HW = os.path.join(ROOT, "results", "hw", "machine32")
OUT = os.path.join(ROOT, "results", "equal", "analysis.json")
REPORT = os.path.join(ROOT, "results", "report_equal.md")
NESTED = ["cpp", "java", "js", "python", "d", "rust", "nim", "mojo", "go", "ocaml", "lua", "swift", "php"]  # 3.2
NAT_KEYS = [(k, v, q) for k, lst in Cm.NATURAL.items() for v, q in lst]
K9N, K9F, K4T = ("k9", "natural", ""), ("k9", "natural_flat", ""), ("k4", "tuned", "")
K3K = [("k3", "sw_padded", ""), ("k3", "rmw_padded", "")]
K4K = [("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")]
R3_SEED = v3.SEED + 3303  # générateur de la cellule K4 tuned (calculs R3, Toutes)
CALCS = ["Hôte", "R1", "R1'", "R2", "R3", "R4", "Toutes", "Toutes, R1'"]


# ------------------------------------------------------------------ données
def load():
    """{construction: {langage: {clé: [processus]}}}, latences de K8 de même, échecs, vol de temps, modèles. Un
    processus est retenu s'il a fini sans erreur, sans dépassement de mémoire ni de durée, et si toutes ses sommes de
    contrôle sont justes ; il est représenté par la médiane de ses répétitions (statistique de la v3)."""
    data, lat = defaultdict(lambda: defaultdict(dict)), defaultdict(lambda: defaultdict(dict))
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
                                 "oom": bool(r.get("oom") or fc.get("oom")), "timeout": bool(r.get("timeout") or fc.get("timeout")),
                                 "returncode": r.get("returncode", fc.get("returncode")), "oks": r.get("oks"),
                                 "stderr": (r.get("stderr") or fc.get("stderr") or "")[-300:]})
                continue
            if r.get("steal_frac", 0) > 0.05:
                steal.append((r["lang"], r["build"], key, r["steal_frac"]))
            data[r["build"]][r["lang"]].setdefault(key, []).append([r["median"]])
            if key == K8N:
                lat[r["build"]][r["lang"]].setdefault(key, []).append(r.get("lat", []))
    return data, lat, failures, steal, {m: dict(ps) for m, ps in models.items()}


def b3_value():
    """b3 en secondes et ses mesures (médianes des 16 décalages, en ms, par exécution)."""
    vals = {}
    for which in ("start", "end"):
        p = os.path.join(ROOT, "results", "equal", f"k3_ref_{which}.txt")
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
    parts = [float(np.mean(v)) for v in vals.values()]
    return 1e-3 * float(np.mean(parts)), vals


def hw32():
    saved = S.HW
    S.HW = HW
    try:
        return S.hw_numbers()
    finally:
        S.HW = saved


def gm(procs):
    return math.exp(float(np.mean(np.log([float(np.median(p)) for p in procs]))))


# ------------------------------------------------------------------ calculs
def scenario_data(data, lat, langs, calc):
    """Base et substitutions d'un calcul : (cellules, latences, nouvelles cellules manquantes)."""
    d = {l: dict(data["pub"].get(l, {})) for l in langs}
    lt = {l: dict(lat["pub"].get(l, {})) for l in langs}
    missing = []

    def sub(l, build, pairs):
        for tk, sk in pairs:
            procs = data.get(build, {}).get(l, {}).get(sk)
            if not procs:
                missing.append([l, build, "|".join(sk)])
                continue
            d[l][tk] = procs
            if tk == K8N:
                lp = lat.get(build, {}).get(l, {}).get(K8N)
                if lp:
                    lt[l][K8N] = lp
                else:
                    missing.append([l, build, "latences de K8"])

    if calc in ("R1", "Toutes"):
        for l in Cm.CHK:
            sub(l, "chk", [(k, k) for k in NAT_KEYS])
    if calc in ("R1'", "Toutes, R1'"):
        for l in Cm.UNC:
            sub(l, "unc", [(k, k) for k in NAT_KEYS])
    if calc in ("R2", "Toutes", "Toutes, R1'"):
        for l in NESTED:
            b = "eq"
            if calc == "Toutes" and l in Cm.EQ_CHK:
                b = "eq_chk"
            elif calc == "Toutes, R1'" and l in Cm.EQ_UNC:
                b = "eq_unc"
            sub(l, b, [(K9N, K9F)])
    return d, lt, missing


def r3_patch(d, data, langs):
    """Ajoute aux temps simulés la cellule K4 tuned (construction eq), tirée comme dans Arrays3 (mêmes réservoirs de
    K4, construits sur les mêmes cellules que le calcul) avec son propre générateur."""
    def patch(A):
        pools = build_pools(d, langs, sorted(needed_keys()))
        g = np.random.default_rng(R3_SEED)
        mean = np.full((A.nb + 1, len(langs)), np.nan)
        mn = np.full((A.nb + 1, len(langs)), np.nan)
        for l in langs:
            procs = data.get("eq", {}).get(l, {}).get(K4T)
            if not procs:
                continue
            y = proc_logs(procs)
            j = A.idx[l]
            mean[0, j], mn[0, j] = math.exp(y.mean()), math.exp(y.min())
            if A.nb:
                pool = pools[("k4", klass(l))]
                draws = y.mean() + pool[g.integers(0, len(pool), size=(A.nb, len(y)))]
                mean[1:, j], mn[1:, j] = np.exp(draws.mean(axis=1)), np.exp(draws.min(axis=1))
        A.t[("mean", K4T)], A.t[("min", K4T)] = mean, mn
    return patch


def r4_patch(b3):
    """Temps de K3 relevés à b3 au moins : avec la référence b3, la cellule vaut min(1, b3 / t)."""
    def patch(A):
        for est in ("mean", "min"):
            for k in K3K:
                A.t[(est, k)] = np.maximum(A.t[(est, k)], b3)
    return patch


def run_calc(calc, data, lat, langs, footprint, c3, eb, b3, keys):
    d, lt, missing = scenario_data(data, lat, langs, calc)
    filled = S.fill_missing(d, langs, keys)
    r3, r4 = calc in ("R3", "Toutes", "Toutes, R1'"), calc in ("R4", "Toutes", "Toutes, R1'")
    e_meas, patches = None, []
    if r3:  # même ordre des noyaux qu'E_V2 : les poids tirés ne changent pas
        e_meas = {k: ([K4K + [K4T]] if k == "k4" else v) for k, v in E_V2.items()}
        patches.append(r3_patch(d, data, langs))
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
    return out


# ------------------------------------------------------------------ descriptif
def ratios(data, langs, b3, tstar_k3):
    """Rapports des temps des nouvelles cellules à leur référence (moyennes géométriques des médianes de processus)."""
    pub = data["pub"]
    out = {"R1": {}, "R1'": {}, "R2": {}, "R3": {}, "R4": {}}
    for name, build, lst in (("R1", "chk", Cm.CHK), ("R1'", "unc", Cm.UNC)):
        for l in lst:
            row = {}
            for key in NAT_KEYS:
                a, b = data.get(build, {}).get(l, {}).get(key), pub.get(l, {}).get(key)
                if a and b:
                    row["|".join(key)] = gm(a) / gm(b)
            out[name][l] = row
    for l in NESTED:
        row = {}
        b = pub.get(l, {}).get(K9N)
        a = data.get("eq", {}).get(l, {}).get(K9F)
        if a and b:
            row["eq"] = gm(a) / gm(b)
        for eb_, base in (("eq_chk", "chk"), ("eq_unc", "unc")):
            a, b = data.get(eb_, {}).get(l, {}).get(K9F), data.get(base, {}).get(l, {}).get(K9N)
            if a and b:
                row[eb_] = gm(a) / gm(b)
        out["R2"][l] = row
    for l in langs:
        a = data.get("eq", {}).get(l, {}).get(K4T)
        bs = [gm(pub[l][k]) for k in K4K if pub.get(l, {}).get(k)]
        if bs:
            out["R3"][l] = {"best2": min(bs), "tuned": gm(a) if a else None, "ratio": (gm(a) / min(bs)) if a else None}
    for l in langs:
        ts = [gm(pub[l][k]) for k in K3K if pub.get(l, {}).get(k)]
        if ts:
            t = min(ts)
            out["R4"][l] = {"t": t, "t_over_b3": t / b3, "cell_frontier": min(1.0, tstar_k3 / t),
                            "cell_r4": min(1.0, b3 / t)}
    return out


def main():
    v2.ADDED.clear()  # une seule campagne : aucun langage relié par un pont
    data, lat, failures, steal, models = load()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    hw = hw32()
    eb = S.ebounds(hw, 1)
    eb[("k5", 0)] = S.ebounds(hw, 0)[("k5", 0)]  # K5 à sa taille publiée (position « petite » du tableau du point 2)
    b3, b3_runs = b3_value()
    langs = list(RANKED)
    keys = S.campaign_keys({"pub": data["pub"]})
    res = {c: run_calc(c, data, lat, langs, footprint, c3, eb, b3, keys) for c in CALCS}
    h = res["Hôte"]["order"]
    moved = {c: S.moved(h, res[c]["order"], langs) for c in CALCS[1:]}
    tstar_k3 = min(gm(data["pub"][l][k]) for l in langs for k in K3K if data["pub"].get(l, {}).get(k))
    out = {"results": res, "moved_more_than_2": moved, "b3": b3, "b3_runs_ms": b3_runs,
           "bounds": {f"{k}#{i}": v for (k, i), v in eb.items()}, "hw": {k: v for k, v in hw.items()},
           "ratios": ratios(data, langs, b3, tstar_k3), "k3_frontier": tstar_k3,
           "failures": failures, "steal_over_5pct": steal, "cpu_models": models}
    m31 = json.load(open(os.path.join(ROOT, "results", "sizes", "analysis.json")))["results"]["Hôte"]
    out["machine31_host"] = {"order": m31["order"], "exp": m31["exp"], "ms0": m31["ms0"], "tiers": m31["tiers"]}
    out["moved_m31_m32"] = S.moved(m31["order"], h, langs)
    pub = json.load(open(os.path.join(ROOT, "results", "audit3.json")))["scenarios"]["Publié"]
    out["published"] = {"order": pub["order21"], "exp": pub["exp21"], "ms0": pub["ms0"], "tiers": pub["tiers"]}
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    report(out)


# ------------------------------------------------------------------ rapport
def report(o):
    R = o["results"]
    f2 = lambda x: f"{x:.2f}"  # noqa: E731
    L = ["# v4, point 3 : des conditions égales — résultats", "",
         "*Plan : `docs/V4_EQUAL.md` (sections 3 à 8, écarts 5.1 et 5.2). Généré par `analysis/equal_v4.py` à partir "
         "de `results/equal/raw` (machine 32). Le classement de tête du README ne change pas au point 3 (section 9).*",
         "", f"b3 = {1e3 * o['b3']:.2f} ms (médianes des 16 décalages : début "
         + ", ".join(f"{x:.2f}" for x in o["b3_runs_ms"].get("start", [])) + " ms ; fin "
         + (", ".join(f"{x:.2f}" for x in o["b3_runs_ms"]["end"]) if "end" in o["b3_runs_ms"] else "**non mesurée**")
         + " ms). Frontière de K3 de la base (langage le plus rapide) : " + f"{1e3 * o['k3_frontier']:.2f} ms.", "",
         "## Classements", "",
         "| Langage | " + " | ".join(CALCS) + " |", "|---|" + "---|" * len(CALCS)]
    for l in R["Hôte"]["order"]:
        cells = []
        for c in CALCS:
            r = R[c]
            p = r["order"].index(l) + 1
            mark = "" if c == "Hôte" or abs(p - R["Hôte"]["order"].index(l) - 1) <= 2 else " **"
            cells.append(f"{p}{mark} ({r['exp'][l]:.2f} ; {r['ms0'][l]:.1f})")
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", "Chaque case : place (rang espéré ; score au centre) ; ** : plus de deux places d'écart avec « Hôte ». "
          "Ordre des lignes : « Hôte ».", "", "## Rangs plausibles (90 %)", "",
          "| Langage | " + " | ".join(CALCS) + " |", "|---|" + "---|" * len(CALCS)]
    for l in R["Hôte"]["order"]:
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{R[c]['rank90'][l][0]}–{R[c]['rank90'][l][1]}" for c in CALCS) + " |")
    L += ["", "## Rangs qui bougent de plus de deux places par rapport à « Hôte »", ""]
    for c in CALCS[1:]:
        mv = o["moved_more_than_2"][c]
        L.append(f"* {c} : " + (", ".join(f"{NAMES[l]} {a}e → {b}e" for l, (a, b) in
                                         sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"))
    L += ["", "## Étages indicatifs (paires ordonnées dans au moins 95 % des variantes)", ""]
    for c in CALCS:
        L.append(f"* {c} : " + " | ".join(", ".join(NAMES[l] for l in t) for t in R[c]["tiers"]))
    Q = o["ratios"]
    L += ["", "## Effet de chaque règle sur ses cellules (descriptif)", "",
          "Rapports des temps (moyennes géométriques des médianes de processus) ; au-dessus de 1, la nouvelle cellule "
          "est plus lente.", "", "### R1 et R1' : cellules naturelles, mode vérifié ou sans vérifications / mode publié",
          "", "| Langage | Règle | " + " | ".join(f"{k} {v}{' ' + q if q and q != 'energy' else ''}" for k, v, q in NAT_KEYS)
          + " | moyenne géom. |", "|---|---|" + "---|" * (len(NAT_KEYS) + 1)]
    for name in ("R1", "R1'"):
        for l, row in Q[name].items():
            vals = [row.get("|".join(k)) for k in NAT_KEYS]
            ok = [v for v in vals if v]
            L.append(f"| {NAMES[l]} | {name} | " + " | ".join(f2(v) if v else "–" for v in vals)
                     + f" | {math.exp(np.mean(np.log(ok))):.2f} |" if ok else f"| {NAMES[l]} | {name} | – |")
    L += ["", "### R2 : K9 naturel contigu / imbriqué", "",
          "| Langage | mode publié (eq / pub) | mode R1 (eq_chk / chk) | mode R1' (eq_unc / unc) |", "|---|---|---|---|"]
    for l, row in Q["R2"].items():
        L.append(f"| {NAMES[l]} | " + " | ".join(f2(row[k]) if k in row else "–" for k in ("eq", "eq_chk", "eq_unc")) + " |")
    L += ["", "### R3 : K4 tuned / meilleure des deux formes publiées", "",
          "| Langage | meilleure publiée (ms) | tuned (ms) | rapport |", "|---|---|---|---|"]
    for l in R["Hôte"]["order"]:
        x = Q["R3"].get(l)
        if x:
            L.append(f"| {NAMES[l]} | {1e3 * x['best2']:.2f} | " + (f"{1e3 * x['tuned']:.2f} | {x['ratio']:.2f}"
                                                                     if x["tuned"] else "– | –") + " |")
    L += ["", "### R4 : K3 (meilleur de sw_padded et rmw_padded) et b3", "",
          "| Langage | t (ms) | t / b3 | cellule « frontière » de la base | cellule R4 |", "|---|---|---|---|---|"]
    for l in R["Hôte"]["order"]:
        x = Q["R4"].get(l)
        if x:
            L.append(f"| {NAMES[l]} | {1e3 * x['t']:.2f} | {x['t_over_b3']:.2f} | {x['cell_frontier']:.3f} | "
                     f"{x['cell_r4']:.3f} |")
    M = o["machine31_host"]
    L += ["", "## Réplication descriptive : « Hôte » de la machine 31 (point 2) et de la machine 32", "",
          "| Langage | machine 31 | machine 32 |", "|---|---|---|"]
    for l in R["Hôte"]["order"]:
        L.append(f"| {NAMES[l]} | {M['order'].index(l) + 1} ({M['exp'][l]:.2f} ; {M['ms0'][l]:.1f}) | "
                 f"{R['Hôte']['order'].index(l) + 1} ({R['Hôte']['exp'][l]:.2f} ; {R['Hôte']['ms0'][l]:.1f}) |")
    mv = o["moved_m31_m32"]
    L += ["", "Plus de deux places d'écart : " + (", ".join(f"{NAMES[l]} {a}e → {b}e" for l, (a, b) in
                                                       sorted(mv.items(), key=lambda x: x[1][1])) or "aucun") + "."]
    L += ["", "## Cellules", ""]
    for c in CALCS:
        r = R[c]
        if r["missing"] or r["filled"]:
            L.append(f"* {c} : nouvelles cellules manquantes (cellule de la base gardée) : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} {x[2]}" for x in r["missing"]) or "aucune")
                     + " ; cellules de la base manquantes (temps le plus lent des autres langages) : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]}" for x in r["filled"]) or "aucune"))
    cm = o["cpu_models"]
    fl = o["failures"]
    L += ["", "Processeur des enregistrements (section 5) : " + " ; ".join(
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
