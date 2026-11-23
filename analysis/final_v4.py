#!/usr/bin/env python3
"""v4, campagne finale : le classement de la v4 (docs/V4_FINAL.md, section 8, fixée avant les mesures).

La méthode v3 (même graine, 20 000 variantes, même rééchantillonnage, mêmes tirages des poids, des normalisations et du
jugement de la grille) sur les seules données de la campagne finale (results/final/raw, tools/final/campaign.py), avec
les bornes physiques des machines qui ont mesuré (médiane, quantité par quantité, de leurs caractérisations :
results/hw/machine<N>). Un moteur unique (three) calcule tous les calculs à partir des trois positions de taille du
point 2 (petite, publiée, grande ; pour K5 : 2^11, 2^15, 2^21) : chaque cellule du plafond et du code par défaut est
calculée à chaque position avec ses propres références, puis moyennée en logarithme avec les poids des tailles (calcul
« Final » : égaux au centre, tirés dans les variantes ; une taille seule : poids 1 à cette position). Les tirages des
variantes (configuration, rééchantillonnage, poids, jugement de la grille) viennent du même générateur, avancé de la
même façon pour tous les calculs : ils sont identiques d'un calcul à l'autre.

Calcul « Final » (section 8) :
* plafond : à chaque taille, chaque cellule prend la meilleure forme admise (C1 : variantes publiées et formes du relevé
  results/converge/forms.json, écrites dans la copie _cv ou présentes dans la base), la variante naturelle y entrant
  dans son mode R1 (huit langages) et, pour K9, sous sa forme contiguë (R2, treize langages ; mode R1 pour C++ et D) ;
* K3 (R4) : chaque processus de K3 est ramené au b3 de référence (moyenne de toutes les mesures de b3) par le rapport
  t x b3 / b3 de son groupe (moyenne des mesures faites juste avant et juste après le groupe de K3 de sa passe, sur sa
  machine) ; les temps sont relevés à b3 au moins et la référence de K3 vaut b3 : la cellule vaut min(1, b3 / t) ;
* code par défaut : D1 et D2 (part de K1) à trois tailles avec R1 et R2 ; D3 (latences de K8 naturel, sept processus)
  à trois tailles ; D4 (K2, sept processus) à sa taille ; empreinte de K1 et grille inchangées ;
* chaque cellule nouvelle (forme absente de la base) est tirée par son propre générateur (graine fixée par la clé, le
  langage et la position), dans les réservoirs de résidus de son noyau bâtis sur la base de la position ;
* cellule manquante de la base : temps admissible le plus lent des autres langages (variantes communes ; point 2) ;
  forme manquante : absente de son ensemble, signalée.
Sensibilités et décomposition (section 8, 1 à 6) : Base, trois tailles ; sans les tailles (taille publiée seule, qui
est aussi « une taille à la fois : publiée »), sans R1, sans R2, sans C1, sans R4 ; R1' au lieu de R1 ; une taille à la
fois (petite, grande) ; sélection indépendante ; D3 et D4 sur trois processus. Comparaisons : classement publié (tête
du README, results/audit3.json) et « Convergent, avec R4 » du point 4 (results/converge/analysis.json).
Sorties : results/final/analysis.json, results/report_final.md. Variables : BOOT (2000), UA (20000), FINAL_RAW (données
d'essai), FINAL_OUT (répertoire de sortie d'essai)."""
import copy, glob, importlib.util, json, math, os, re, sys, zlib
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sizes_v4 as SZ  # noqa: E402  (positions, bornes, résumé d'un calcul, cellules manquantes)
import converge_v4 as CV  # noqa: E402  (relevé des formes, cellules du plafond)
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
from analyze_v2 import RANKED, ROOT, NAMES, CATEGORIES, c_cells, c_score, c_vector, ranks_of, dirichlet  # noqa: E402
from analyze_v3 import (Arrays3, build_pools, needed_keys, references, MAIN, K1N, K1S, K2_SIZES, K8N, E_V2,  # noqa: E402
                        proc_logs, klass)

_spec = importlib.util.spec_from_file_location("fbuild", os.path.join(ROOT, "tools", "final", "build.py"))
FB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FB)

B = int(os.environ.get("BOOT", "2000"))
U = int(os.environ.get("UA", "20000"))
FIN = os.path.join(ROOT, "results", "final")
RAW = os.environ.get("FINAL_RAW", os.path.join(FIN, "raw"))
B3F = os.path.join(os.path.dirname(RAW), "b3.jsonl")
OUTD = os.environ.get("FINAL_OUT", FIN)
OUT = os.path.join(OUTD, "analysis.json")
REPORT = os.path.join(OUTD, "report_final.md") if "FINAL_OUT" in os.environ else os.path.join(ROOT, "results",
                                                                                               "report_final.md")
LANGS = list(RANKED)
SIZED, POS, POS_NAMES = SZ.SIZED, SZ.POS, SZ.POS_NAMES
NAT_KEYS = [K1N, K1S, ("k4", "natural_unsorted", ""), ("k5", "natural", ""), ("k6", "natural", "q6"),
            ("k6", "natural", "q1"), ("k7", "natural", ""), K8N, ("k9", "natural", "")]
K9N, K9F = ("k9", "natural", ""), ("k9", "natural_flat", "")
K3K = [("k3", "sw_padded", ""), ("k3", "rmw_padded", "")]
K2K = [("k2", "tuned", s) for s in K2_SIZES]
CEIL = CV.CEIL
NEW_SEED = v3.SEED + 4500  # générateurs des cellules nouvelles (complétés par la clé, le langage et la position)
SEL_SEED = v3.SEED + 4501  # générateurs des cellules de la sélection indépendante
FINAL = "Final"
CALCS = [FINAL, "Base, trois tailles", "Sans les tailles (taille publiée seule)", "Sans R1", "Sans R2", "Sans C1",
         "Sans R4", "R1' au lieu de R1", "Taille petite", "Taille grande", "Sélection indépendante",
         "D3 et D4 sur trois processus", "Sur les seules mesures"]


# ------------------------------------------------------------------ données
class Data:
    """Mesures de la campagne : data[(construction, taille)][langage][clé] = [[médiane d'un processus]] ; pour chaque
    processus aussi sa passe et sa copie (bypass), et les latences de K8 naturel (lat)."""

    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(dict))
        self.bypass = defaultdict(lambda: defaultdict(dict))
        self.lat = defaultdict(lambda: defaultdict(dict))
        self.k3 = defaultdict(lambda: defaultdict(dict))  # (construction, taille) -> langage -> clé -> [(passe, boot)]
        self.failures, self.skipped, self.steal = [], [], []
        self.models, self.machines = defaultdict(lambda: defaultdict(int)), defaultdict(set)

    def procs(self, cons, size, lang, key):
        return self.data.get((cons, size), {}).get(lang, {}).get(key)


def load():
    F = Data()
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            key = (r["kernel"], r["variant"], r["param"])
            tag = (r["construction"], r["size"])
            F.models[r.get("cpu_model", "?")][r.get("pass")] += 1
            F.machines[(r["pass"], r["kernel"], r["size"])].add(r.get("machine"))
            if r.get("skipped"):
                F.skipped.append({"lang": r["lang"], "construction": r["construction"], "size": r["size"],
                                  "key": key, "pass": r["pass"], "status": r["skipped"]})
                continue
            ok = (r.get("returncode") == 0 and not r.get("oom") and not r.get("timeout") and r.get("n", 0) > 0
                  and r.get("oks") == ["True"])
            if not ok:
                F.failures.append({"lang": r["lang"], "construction": r["construction"], "size": r["size"], "key": key,
                                   "pass": r["pass"], "oom": bool(r.get("oom")), "timeout": bool(r.get("timeout")),
                                   "returncode": r.get("returncode"), "oks": r.get("oks"),
                                   "stderr": (r.get("stderr") or "")[-300:]})
                continue
            if r.get("steal_frac", 0) > 0.05:
                F.steal.append((r["lang"], r["construction"], r["size"], key, r["steal_frac"]))
            m = r["median"]
            F.data[tag][r["lang"]].setdefault(key, []).append([m])
            F.bypass[tag][r["lang"]].setdefault(key, []).append((r["pass"], m, r.get("copy", 0)))
            if key[0] == "k3":
                F.k3[tag][r["lang"]].setdefault(key, []).append((r["pass"], r.get("boot_id")))
            if key == K8N:
                F.lat[tag][r["lang"]].setdefault(key, []).append((r.get("copy", 0), r.get("lat", [])))
    return F


def b3_values():
    """b3 de référence (s) et b3 de chaque groupe de K3, par (passe, démarrage) : moyenne des mesures avant et après."""
    recs = [json.loads(l) for l in open(B3F)] if os.path.exists(B3F) else []
    if not recs:
        return None, {}, []
    ref = 1e-3 * float(np.mean([r["b3_ms"] for r in recs]))
    groups = defaultdict(list)
    for r in recs:
        if r.get("pass") is not None and "groupe K3" in r["label"]:
            groups[(r["pass"], r["boot_id"])].append(r["b3_ms"])
    return ref, {k: 1e-3 * float(np.mean(v)) for k, v in groups.items()}, recs


def k3_normalized(F, b3ref, b3g):
    """Temps de K3 ramenés au b3 de référence : t x b3 / b3 du groupe (R4, b3 par groupe : docs/V4_FINAL.md, 6)."""
    out = defaultdict(lambda: defaultdict(dict))
    for tag, dl in F.data.items():
        if tag[1] != "pub":
            continue
        for l, keys in dl.items():
            for key, procs in keys.items():
                if key[0] != "k3":
                    continue
                tags = F.k3[tag][l][key]
                out[tag][l][key] = [[p[0] * b3ref / b3g[(ps, boot)]] for p, (ps, boot) in zip(procs, tags)]
    return out


def machines_hw(F):
    """Bornes physiques : médiane, quantité par quantité, des caractérisations des machines qui ont mesuré."""
    ms = sorted({m for v in F.machines.values() for m in v if m is not None}, key=lambda x: int(x))
    hws = []
    for m in ms:
        saved = SZ.HW
        SZ.HW = os.path.join(ROOT, "results", "hw", f"machine{m}")
        try:
            hws.append(SZ.hw_numbers())
        finally:
            SZ.HW = saved
    if not hws:
        raise SystemExit("aucune machine dans les enregistrements")
    sizes = sorted(set.intersection(*[{s for s, _ in h["bw"]} for h in hws]))
    bw = [(s, float(np.median([dict(h["bw"])[s] for h in hws]))) for s in sizes]
    hw = {"bw": bw}
    for q in ("stream4", "peak", "freq"):
        hw[q] = float(np.median([h[q] for h in hws]))
    return hw, ms


# ------------------------------------------------------------------ données d'une position et d'un calcul
def size_of(key, p):
    k = key[0]
    return POS[k][p] if k in SIZED else "pub"


def position(F, p, calc, k3n):
    """(d, lt, src, missing) d'une position : la base (construction pub), K3 de R4, puis les substitutions du calcul.
    src[l][clé] = (construction, taille, clé source), pour la sélection indépendante."""
    d, lt, src, missing = defaultdict(dict), defaultdict(dict), defaultdict(dict), []
    three = calc == "D3 et D4 sur trois processus"
    for (cons, size), dl in F.data.items():
        if cons != "pub":
            continue
        for l, keys in dl.items():
            for key, procs in keys.items():
                if size_of(key, p) != size:
                    continue
                if three and (key[0] == "k2" or key == K8N):
                    procs = [[m] for ps, m, c in F.bypass[(cons, size)][l][key] if c == 0]
                d[l][key] = procs
                src[l][key] = (cons, size, key)
    for l in LANGS:
        lp = F.lat.get(("pub", POS["k8"][p]), {}).get(l, {}).get(K8N)
        if lp:
            lt[l][K8N] = [x for c, x in lp if not three or c == 0]
    r4 = calc not in ("Base, trois tailles", "Sans R4")
    if r4:
        for l, keys in k3n.get(("pub", "pub"), {}).items():
            for key, procs in keys.items():
                d[l][key] = procs

    def sub(l, cons, tk, sk):
        size = size_of(tk, p)
        procs = F.procs(cons, size, l, sk)
        if not procs:
            missing.append([l, cons, "|".join(sk), size])
            return
        if three and tk == K8N:
            procs = [[m] for ps, m, c in F.bypass[(cons, size)][l][sk] if c == 0]
        d[l][tk] = procs
        src[l][tk] = (cons, size, sk)
        if tk == K8N:
            lp = F.lat.get((cons, size), {}).get(l, {}).get(K8N)
            if lp:
                lt[l][K8N] = [x for c, x in lp if not three or c == 0]
            else:
                missing.append([l, cons, "latences de K8", size])

    mode = None if calc in ("Base, trois tailles", "Sans R1") else ("unc" if calc == "R1' au lieu de R1" else "chk")
    if mode:
        for l in (FB.CHK if mode == "chk" else FB.UNC):
            for k in NAT_KEYS:
                sub(l, mode, k, k)
    if calc not in ("Base, trois tailles", "Sans R2"):
        for l in nested():
            cons = "cv"
            if mode == "chk" and l in FB.CV_CHK:
                cons = "cv_chk"
            elif mode == "unc" and l in FB.CV_UNC:
                cons = "cv_unc"
            sub(l, cons, K9N, K9F)
    return d, lt, src, missing


_NESTED = None


def nested():
    """Les 13 langages à grille imbriquée : ceux dont la copie _cv déclare K9 natural_flat (R2)."""
    global _NESTED
    if _NESTED is None:
        _NESTED = []
        for l in LANGS:
            p = os.path.join(ROOT, "bench", l + "_cv", "cv_variants")
            if os.path.exists(p) and any(line.split()[:2] == ["k9", "natural_flat"] for line in open(p)):
                _NESTED.append(l)
    return _NESTED


def additions(F, fc, p, d):
    """Cellules nouvelles d'une position (C1) : {clé: {langage: processus}}, leur cellule du plafond, les manquantes."""
    add, ceil_of, missing = defaultdict(dict), {}, []
    for l in LANGS:
        for build, key, ceil, form, rq in fc.get(l, []):
            size = size_of(key, p)
            if build == "pub" and key in d.get(l, {}):
                continue  # forme présente : déjà dans la base
            procs = F.procs("cv", size, l, key) or F.procs(build, size, l, key)
            ceil_of[key] = ceil
            if not procs:
                missing.append([l, build, "|".join(key), size])
                continue
            add[key][l] = procs
    return add, ceil_of, missing


def e_meas_with(keys_ceil):
    e = copy.deepcopy(E_V2)
    for key in sorted(keys_ceil):
        k, gi = CEIL[keys_ceil[key]]
        if key not in e[k][gi]:
            e[k][gi] = e[k][gi] + [key]
    return e


def seed_of(base, key, lang, p):
    return [base, zlib.crc32("|".join(key).encode()), zlib.crc32(lang.encode()), p]


def new_cells_patch(d, add, allkeys, p, base_seed):
    """Tableaux simulés des clés nouvelles d'une position : estimation ponctuelle, et tirages dans les réservoirs du
    noyau (bâtis sur la base de la position), un générateur par clé, langage et position ; NaN où la forme manque."""
    def patch(A):
        pools = build_pools(d, LANGS, sorted(needed_keys()))
        for key in sorted(allkeys):
            mean = np.full((A.nb + 1, len(LANGS)), np.nan)
            mn = np.full((A.nb + 1, len(LANGS)), np.nan)
            for l, procs in add.get(key, {}).items():
                y = proc_logs(procs)
                j = A.idx[l]
                mean[0, j], mn[0, j] = math.exp(y.mean()), math.exp(y.min())
                if A.nb:
                    g = np.random.default_rng(seed_of(base_seed, key, l, p))
                    pool = pools[(key[0], klass(l))]
                    draws = y.mean() + pool[g.integers(0, len(pool), size=(A.nb, len(y)))]
                    mean[1:, j], mn[1:, j] = np.exp(draws.mean(axis=1)), np.exp(draws.min(axis=1))
            A.t[("mean", key)], A.t[("min", key)] = mean, mn
    return patch


def r4_patch(b3):
    def patch(A):
        for est in ("mean", "min"):
            for k in K3K:
                A.t[(est, k)] = np.maximum(A.t[(est, k)], b3)
    return patch


def selection(F, fc, pos):
    """Sélection indépendante : pour chaque langage, cellule du plafond et position, la forme la plus rapide sur la
    passe 0 seule (moyenne géométrique des médianes de processus), estimée sur les passes 1 et 2 seules ; clé à part."""
    sel_keys = {ceil: (k, "sel " + ceil, "") for ceil, (k, gi) in CEIL.items()}
    adds, chosen = [], {}
    for p, (d, lt, src, _) in enumerate(pos):
        add = defaultdict(dict)
        for l in LANGS:
            cand = defaultdict(list)
            for ceil, (k, gi) in CEIL.items():
                for key in E_V2[k][gi]:
                    if key in src.get(l, {}):
                        cand[ceil].append(src[l][key])
            for build, key, ceil, form, rq in fc.get(l, []):
                size = size_of(key, p)
                b = "cv" if F.procs("cv", size, l, key) else build
                if (b, size, key) not in cand[ceil]:
                    cand[ceil].append((b, size, key))
            for ceil, lst in cand.items():
                best = None
                for b, size, key in lst:
                    rows = F.bypass.get((b, size), {}).get(l, {}).get(key, [])
                    p0 = [m for ps, m, c in rows if ps == 0]
                    if not p0:
                        continue
                    t0 = math.exp(float(np.mean(np.log(p0))))
                    if best is None or t0 < best[0]:
                        best = (t0, b, size, key)
                if best is None:
                    continue
                _, b, size, key = best
                later = [[m] for ps, m, c in F.bypass[(b, size)][l][key] if ps in (1, 2)]
                if later:
                    add[sel_keys[ceil]][l] = later
                    chosen[f"{l}|{ceil}|{POS_NAMES[p]}"] = [b, size, "|".join(key)]
        adds.append(add)
    e = copy.deepcopy(E_V2)
    for ceil, (k, gi) in CEIL.items():
        e[k][gi] = [sel_keys[ceil]]
    return e, adds, list(sel_keys.values()), chosen


# ------------------------------------------------------------------ moteur
def scores(As, r, cfg, C, footprint, refs, ebs, wS, wE=None, wD=None, wP=None):
    """scores3 de la v3 à trois positions (sizes_v4.scores_sizes) : chaque cellule de E, de D1, de D2 (part de K1) et
    de D3 à chaque position avec ses propres références, moyennée en logarithme avec les poids wS ; K3 et D4 (une seule
    taille) à la position publiée."""
    return SZ.scores_sizes(As, r, cfg, C, footprint, refs, ebs, wS, wE=wE, wD=wD, wP=wP)


def three(host, pos_dl, footprint, c3, ebs, e_meas=None, patches=None, wmode="three", b3=None, measures_only=False):
    """Un calcul. host : données qui avancent le générateur principal (les mêmes pour tous les calculs) ; pos_dl : [(d,
    lt)] des trois positions ; wmode : « three » (poids des tailles égaux au centre, tirés dans les variantes) ou une
    position (0, 1, 2) de poids 1 ; b3 : R4 (référence de K3) ; measures_only : poids de la grille à 0."""
    rng = np.random.default_rng(v3.SEED)
    keys = sorted(needed_keys())
    Arrays3(host[0], host[1], LANGS, B, rng, build_pools(host[0], LANGS, keys))  # avance rng de la même façon
    As, refs, ebs = [], [], [dict(e) for e in ebs]
    for p, (d, lt) in enumerate(pos_dl):
        A = Arrays3(d, lt, LANGS, B, np.random.default_rng(v3.SEED + 4100 + p), build_pools(d, LANGS, keys))
        if e_meas is not None:
            A.e_meas = e_meas
        for patch in (patches or [[], [], []])[p]:
            patch(A)
        As.append(A)
        rf = {e: references(A, e) for e in ("mean", "min")}
        if b3 is not None:
            for e in rf:
                rf[e]["tstar"][("k3", 0)] = b3
            ebs[p][("k3", 0)] = b3
        refs.append(rf)
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    C0 = c_vector(c_score(c_cells("v2", c3), catw0), LANGS)

    def wmap(w):
        if not measures_only:
            return {"C": w[0], "E": w[1], "D": w[2]}
        return {"C": 0.0, "E": w[1] / (w[1] + w[2]), "D": w[2] / (w[1] + w[2])}

    def wsz(srng_w):
        if wmode == "three":
            return srng_w
        w = np.zeros(3)
        w[wmode] = 1.0
        return w

    w0 = np.full(3, 1 / 3)
    S0 = scores(As, 0, MAIN, C0, footprint, refs, ebs, wsz(w0), wP=wmap(np.array([0.35, 0.40, 0.25])))
    opts = {"est": ["mean", "min"], "enorm": ["frontier", "bounds"], "d3": ["abs", "rel"], "d4": ["best", "c"],
            "d1ref": ["tstar", "best_natural"], "agg": ["arith", "geo"], "crule": ["v2", "v1"]}
    kernels, cat_names = list(As[1].e_meas), list(CATEGORIES)
    rk = As[1].ranked
    NR = len(RANKED)
    prec, first, ranks = np.zeros((NR, NR)), np.zeros(NR), np.empty((U, NR), np.int16)
    srng = np.random.default_rng(v3.SEED + 4200)  # poids des tailles : générateur à part
    for u in range(U):
        cfg = {k: v[int(rng.integers(len(v)))] for k, v in opts.items()}
        b = int(rng.integers(1, B + 1))
        wp = dirichlet(rng, 20 * np.array([0.35, 0.40, 0.25])) if rng.random() < 0.5 else dirichlet(rng, [1, 1, 1])
        wP = wmap(wp)
        wE = dict(zip(kernels, dirichlet(rng, 20 * np.full(len(kernels), 1 / len(kernels)))))
        wD = dict(zip(("D1", "D2", "D3", "D4"), dirichlet(rng, 20 * np.array([v3.DW[k] for k in ("D1", "D2", "D3", "D4")]))))
        catw = dict(zip(cat_names, dirichlet(rng, 20 * np.array([catw0[c] for c in cat_names]))))
        prng = np.random.default_rng(int(rng.integers(2 ** 63)))
        C = c_vector(c_score(c_cells(cfg["crule"], c3, rng=prng, noise=0.10), catw), LANGS)
        wS = dirichlet(srng, 20 * w0) if srng.random() < 0.5 else dirichlet(srng, [1, 1, 1])
        S_u = scores(As, b, cfg, C, footprint, refs, ebs, wsz(wS), wE=wE, wD=wD, wP=wP)
        r_ = ranks_of(S_u["MS"][rk])
        prec += r_[:, None] < r_[None, :]
        first[int(np.argmin(r_))] += 1
        ranks[u] = r_
    prec /= U
    idx = As[1].idx
    exp21 = {a: 1 + sum(prec[RANKED.index(b_), RANKED.index(a)] for b_ in RANKED if b_ != a) for a in RANKED}
    return {"exp21": exp21, "ms0": {l: float(S0["MS"][idx[l]]) for l in LANGS}, "prec": prec,
            "first": {RANKED[j]: float(first[j] / U) for j in range(NR)},
            "rank90": {RANKED[j]: [int(np.quantile(ranks[:, j], 0.05)), int(np.quantile(ranks[:, j], 0.95))]
                       for j in range(NR)},
            "E": {l: float(S0["E"][idx[l]]) for l in LANGS}, "D": {l: float(S0["D"][idx[l]]) for l in LANGS},
            "C": {l: float(C0[idx[l]]) for l in LANGS},
            "Ek": {l: {k: float(S0["Ek"][k][idx[l]]) for k in S0["Ek"]} for l in LANGS},
            "Dparts": {l: {q: float(S0[q][idx[l]]) for q in ("D1", "D2", "D3", "D4")} for l in LANGS},
            "tstar": [{f"{k}#{i}": v for (k, i), v in rf["mean"]["tstar"].items()} for rf in refs]}


def summarize(s):
    out = SZ.summarize(s, LANGS)
    prec = s["prec"]
    order = out["order"]
    out["ahead_next"] = {a: float(prec[RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}
    # ajout du 23 novembre, après le premier calcul (sortie seulement, sans changement de calcul) : la matrice des
    # préséances, part des variantes où a passe devant b, pour décrire les étages
    out["prec_full"] = {a: {b: float(prec[RANKED.index(a), RANKED.index(b)]) for b in order} for a in order}
    out["tstar"] = s["tstar"]
    return out


def run_calc(calc, F, fc, footprint, c3, ebs, b3ref, k3n, host, keys):
    pos = [position(F, p, calc, k3n) for p in range(3)]
    filled, missing = {}, []
    for p, (d, lt, src, miss) in enumerate(pos):
        filled[POS_NAMES[p]] = SZ.fill_missing(d, LANGS, keys)
        missing += miss
    e_meas, patches, chosen = None, [[], [], []], None
    if calc == "Sélection indépendante":
        e_meas, adds, sel, chosen = selection(F, fc, pos)
        for p in range(3):
            patches[p].append(new_cells_patch(pos[p][0], adds[p], sel, p, SEL_SEED))
    elif calc not in ("Base, trois tailles", "Sans C1"):
        adds, allc = [], {}
        for p in range(3):
            add, ceil_of, miss = additions(F, fc, p, pos[p][0])
            adds.append(add)
            allc.update(ceil_of)
            missing += miss
        e_meas = e_meas_with(allc)
        for p in range(3):
            patches[p].append(new_cells_patch(pos[p][0], adds[p], allc, p, NEW_SEED))
    r4 = calc not in ("Base, trois tailles", "Sans R4")
    if r4:
        for p in range(3):
            patches[p].append(r4_patch(b3ref))
    wmode = {"Sans les tailles (taille publiée seule)": 1, "Taille petite": 0, "Taille grande": 2}.get(calc, "three")
    s = three(host, [(d, lt) for d, lt, src, miss in pos], footprint, c3, ebs, e_meas=e_meas, patches=patches,
              wmode=wmode, b3=b3ref if r4 else None, measures_only=(calc == "Sur les seules mesures"))
    out = summarize(s)
    out["missing"] = missing
    out["filled"] = {k: [[x[0], " ".join(x[1]).strip(), x[2]] for x in v] for k, v in filled.items()}
    if chosen is not None:
        out["chosen"] = chosen
    return out


# ------------------------------------------------------------------ descriptif
def gm(procs):
    return math.exp(float(np.mean(np.log([float(np.median(p)) for p in procs]))))


def retained(F, fc):
    """« Final » : pour chaque langage, cellule du plafond et taille, la forme la plus rapide (estimation ponctuelle),
    la meilleure forme publiée (mêmes substitutions R1 et R2 que « Final ») et leur rapport."""
    out = defaultdict(dict)
    for p in range(3):
        d, lt, src, _ = position(F, p, FINAL, {})
        for l in LANGS:
            for ceil, (k, gi) in CEIL.items():
                pub = [(gm(d[l][key]), key) for key in E_V2[k][gi] if d.get(l, {}).get(key)]
                new = []
                for build, key, c, form, rq in fc.get(l, []):
                    if c != ceil:
                        continue
                    procs = F.procs("cv", size_of(key, p), l, key) or F.procs(build, size_of(key, p), l, key)
                    if procs:
                        new.append((gm(procs), key, form))
                if not pub and not new:
                    continue
                bp = min(pub) if pub else None
                best = min([(t, key, "publiée") for t, key in pub] + new, key=lambda x: x[0])
                out[l][f"{ceil}|{POS_NAMES[p]}"] = {
                    "best_published": bp[0] if bp else None, "retained": best[0], "retained_key": "|".join(best[1]),
                    "retained_form": best[2], "ratio": best[0] / bp[0] if bp else None}
    return out


def spread(F):
    """Écart entre la passe la plus lente et la plus rapide de chaque cellule (moyennes géométriques par passe)."""
    out = []
    for (cons, size), dl in F.bypass.items():
        for l, keys in dl.items():
            for key, rows in keys.items():
                by = defaultdict(list)
                for ps, m, c in rows:
                    by[ps].append(m)
                if len(by) == 3:
                    g = [math.exp(float(np.mean(np.log(v)))) for v in by.values()]
                    out.append(max(g) / min(g))
    out = np.array(out)
    return {"cells": int(len(out)), "median": float(np.median(out)) if len(out) else None,
            "over_20pct": int((out > 1.2).sum())}


def main():
    v2.ADDED.clear()  # une seule campagne : aucun langage relié par un pont
    F = load()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    hw, machines = machines_hw(F)
    ebs = [SZ.ebounds(hw, p) for p in range(3)]
    b3ref, b3g, b3recs = b3_values()
    k3n = k3_normalized(F, b3ref, b3g)
    fc = CV.forms_cells(LANGS)
    keys = SZ.campaign_keys({k: v for k, v in F.data.items() if k[0] == "pub"})
    hd = position(F, 1, "Base, trois tailles", {})[0]  # avance du générateur principal : la base, taille publiée
    host = (copy.deepcopy(hd), position(F, 1, "Base, trois tailles", {})[1])
    SZ.fill_missing(host[0], LANGS, keys)
    calcs = CALCS
    res = {c: run_calc(c, F, fc, footprint, c3, ebs, b3ref, k3n, host, keys) for c in calcs}
    fin = res[FINAL]["order"]
    moved = {c: SZ.moved(fin, res[c]["order"], LANGS) for c in calcs[1:]}
    out = {"results": res, "moved_more_than_2": moved, "b3_ref": b3ref,
           "b3_groups": {f"{p}|{boot}": v for (p, boot), v in b3g.items()},
           "b3_records": [{k: v for k, v in r.items() if k != "outputs"} for r in b3recs],
           "machines": machines, "group_machines": {f"{p}|{k}|{s}": sorted(m for m in v if m is not None)
                                                    for (p, k, s), v in sorted(F.machines.items())},
           "bounds": [{f"{k}#{i}": v for (k, i), v in e.items()} for e in ebs], "hw": hw,
           "retained": retained(F, fc), "spread": spread(F), "failures": F.failures, "skipped": F.skipped,
           "steal_over_5pct": F.steal, "cpu_models": {m: dict(ps) for m, ps in F.models.items()}}
    pub = json.load(open(os.path.join(ROOT, "results", "audit3.json")))["scenarios"]["Publié"]
    out["published"] = {"order": pub["order21"], "exp": pub["exp21"], "ms0": pub["ms0"], "tiers": pub["tiers"]}
    cv4 = json.load(open(os.path.join(ROOT, "results", "converge", "analysis.json")))["results"]["Convergent, avec R4"]
    out["point4_r4"] = {"order": cv4["order"], "exp": cv4["exp"], "ms0": cv4["ms0"]}
    out["moved_vs_published"] = SZ.moved(out["published"]["order"], fin, LANGS)
    out["moved_vs_point4"] = SZ.moved(out["point4_r4"]["order"], fin, LANGS)
    os.makedirs(OUTD, exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    report(out, calcs)


# ------------------------------------------------------------------ rapport
def place(r, l):
    return r["order"].index(l) + 1


def report(o, calcs):
    R = o["results"]
    f = R[FINAL]
    L = ["# v4, campagne finale : le classement de la v4 — résultats", "",
         "*Plan : `docs/V4_FINAL.md` (section 8, fixée avant les mesures). Généré par `analysis/final_v4.py` à partir "
         "de `results/final/raw`, de `results/final/b3.jsonl` et du relevé des formes "
         "(`results/converge/forms.json`).*", "",
         f"Machines : {', '.join(o['machines'])} ; b3 de référence : {1e3 * o['b3_ref']:.2f} ms ; b3 des groupes de K3 : "
         + ", ".join(f"passe {k.split('|')[0]} {1e3 * v:.2f} ms" for k, v in sorted(o["b3_groups"].items())) + ".", "",
         "## Classement « Final »", "",
         "| Rang | Langage | Score | Rang espéré | Rang plausible | Devance le suivant | Plafond | Code par défaut | "
         "Contrôle |", "|---|---|---|---|---|---|---|---|---|"]
    for i, l in enumerate(f["order"]):
        ahead = f["ahead_next"].get(l)
        L.append(f"| {i + 1} | {NAMES[l]} | {f['ms0'][l]:.1f} | {f['exp'][l]:.2f} | {f['rank90'][l][0]}–"
                 f"{f['rank90'][l][1]} | {'—' if ahead is None else f'{100 * ahead:.0f} %'} | {f['E'][l]:.1f} | "
                 f"{f['D'][l]:.1f} | {f['C'][l]:.1f} |")
    L += ["", "Étages (paires ordonnées dans au moins 95 % des variantes) : "
          + " | ".join(", ".join(NAMES[l] for l in t) for t in f["tiers"]), "",
          "## Tous les calculs", "", "| Langage | " + " | ".join(calcs) + " | Publié | Point 4 (R4) |",
          "|---|" + "---|" * (len(calcs) + 2)]
    for l in f["order"]:
        cells = []
        for c in calcs:
            p = place(R[c], l)
            mark = "" if c == FINAL or abs(p - place(f, l)) <= 2 else " **"
            cells.append(f"{p}{mark} ({R[c]['exp'][l]:.2f})")
        cells.append(str(o["published"]["order"].index(l) + 1))
        cells.append(str(o["point4_r4"]["order"].index(l) + 1))
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", "Chaque case : place (rang espéré) ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : "
          "« Final ».", "", "## Rangs qui bougent de plus de deux places par rapport à « Final »", ""]
    for c in calcs[1:]:
        mv = o["moved_more_than_2"][c]
        L.append(f"* {c} : " + (", ".join(f"{NAMES[l]} {b}e (Final {a}e)" for l, (a, b) in
                                         sorted(mv.items(), key=lambda x: x[1][0])) or "aucun"))
    for name, mv in (("classement publié (v3)", o["moved_vs_published"]), ("point 4, avec R4", o["moved_vs_point4"])):
        L.append(f"* Final contre {name} : " + (", ".join(f"{NAMES[l]} {a}e → {b}e" for l, (a, b) in
                                                          sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"))
    L += ["", "## Plafond par noyau et parts du code par défaut (« Final », au centre)", "",
          "| Langage | " + " | ".join(k.upper() for k in E_V2) + " | D1 | D2 | D3 | D4 |",
          "|---|" + "---|" * (len(E_V2) + 4)]
    for l in f["order"]:
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{100 * f['Ek'][l][k]:.0f}" for k in E_V2) + " | "
                 + " | ".join(f"{100 * f['Dparts'][l][q]:.0f}" for q in ("D1", "D2", "D3", "D4")) + " |")
    L += ["", "## Forme retenue par « Final », cellule par cellule et taille par taille (estimation ponctuelle)", "",
          "Chaque case : forme retenue aux tailles petite / publiée / grande (« pub » : une variante publiée) ; rapport "
          "de son temps à la meilleure forme publiée, à la taille publiée.", "",
          "| Langage | " + " | ".join(CEIL) + " |", "|---|" + "---|" * len(CEIL)]
    for l in f["order"]:
        row = []
        for ceil in CEIL:
            xs = [o["retained"].get(l, {}).get(f"{ceil}|{n}") for n in POS_NAMES]
            if not any(xs):
                row.append("–")
                continue
            names = "/".join((x["retained_form"].replace("publiée", "pub") if x else "–") for x in xs)
            r = xs[1]["ratio"] if xs[1] and xs[1]["ratio"] else None
            row.append(names + (f" {r:.2f}" if r else ""))
        L.append(f"| {NAMES[l]} | " + " | ".join(row) + " |")
    sp = o["spread"]
    L += ["", "## Campagne", "", f"Écart entre la passe la plus lente et la plus rapide d'une cellule : médiane "
          f"{100 * (sp['median'] - 1):.1f} % ; {sp['over_20pct']} cellules sur {sp['cells']} au-delà de 20 %."
          if sp["median"] else "", "", "Machine de chaque groupe et de chaque passe :", ""]
    gm_ = defaultdict(list)
    for k, v in o["group_machines"].items():
        gm_["/".join(v)].append(k.replace("|", " "))
    for m, gl in gm_.items():
        L.append(f"* machine {m} : {len(gl)} groupes")
    L += ["", "## Cellules", ""]
    for c in calcs:
        r = R[c]
        nf = sum(len(v) for v in r["filled"].values())
        if r["missing"] or nf:
            L.append(f"* {c} : formes ou cellules substituées manquantes : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} {x[2]} ({x[3]})" for x in r["missing"]) or "aucune")
                     + " ; cellules de la base remplies (temps le plus lent des autres langages) : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} ({t})" for t, v in r["filled"].items() for x in v)
                        or "aucune"))
    cm = o["cpu_models"]
    L += ["", "Processeur des enregistrements : " + " ; ".join(
        f"{m} ({sum(ps.values())} enregistrements)" for m, ps in cm.items())
          + (" — **plusieurs modèles**" if len(cm) > 1 else "") + ".", "",
          f"Processus écartés : {len(o['failures'])} ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : "
          f"{len(o['skipped'])} ; vol de temps > 5 % après reprise : {len(o['steal_over_5pct'])}."]
    for x in o["failures"]:
        L.append(f"* {NAMES.get(x['lang'], x['lang'])} {x['construction']} {x['size']} {' '.join(x['key'])} passe "
                 f"{x['pass']} : code {x['returncode']}, contrôles {x['oks']}{', hors mémoire' if x['oom'] else ''}"
                 f"{', durée' if x['timeout'] else ''}")
    sk = defaultdict(set)
    for x in o["skipped"]:
        sk[(x["lang"], x["construction"], x["size"], " ".join(x["key"]))].add(x["status"])
    for (l, c, s, k), st in sorted(sk.items()):
        L.append(f"* non exécutée : {NAMES.get(l, l)} {c} {s} {k} ({', '.join(sorted(st))})")
    open(REPORT, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
