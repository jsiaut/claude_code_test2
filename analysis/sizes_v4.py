#!/usr/bin/env python3
"""v4, point 2 : analyse des trois tailles (docs/V4_SIZES.md, section 8, fixée avant les mesures ; écart 4.1).

La méthode v3 (même graine, 20 000 variantes, mêmes poids, grille v2 corrigée par le point 1) appliquée aux seules
données de la machine 30 (results/sizes/raw, tools/sizes/campaign.py) :
1. Hôte : la taille publiée de chaque noyau.
2. Trois tailles : pour chacun des sept noyaux à trois tailles, chaque cellule du plafond (E) et du code par défaut
   (D1, et les parts de D2 et D3 tirées de K1 et de K8) est calculée à chaque taille, avec ses propres références
   (frontière des langages à cette taille ; bornes physiques du niveau de mémoire où tiennent les données, mesurées
   sur l'hôte : results/hw/machine30), puis moyennée (en logarithme) sur les trois tailles, à poids égaux au centre ;
   dans les variantes, les poids des tailles sont tirés comme les autres poids (Dirichlet autour de l'égalité,
   concentration 20, dans la moitié des variantes ; uniforme dans l'autre), par un générateur à part, pour que les
   autres tirages restent ceux de « Hôte ».
3. Une taille à la fois, en sensibilité : colonnes « petite », « publiée », « grande » du tableau de la section 3
   (pour K5 : publiée 2^11, 2^15, 2^21).
Pour chaque calcul : scores, rangs espérés, rang plausible (90 %), étages indicatifs (règle v3 sans sa condition de
réplication, comme analysis/audit3.py), et les langages dont le rang change de plus de deux places entre « Hôte » et
« Trois tailles ».
Mise en œuvre de la méthode sur une seule campagne : tous les langages y sont mesurés de la même façon, donc aucun
n'est « ajouté » par un pont (v2.ADDED vide : mêmes réservoirs de résidus et même générateur pour tous) ; les bornes
physiques sont celles de la machine 30 dans les quatre calculs ; empreintes (D2) et grille (C) restent celles du
classement publié. Une cellule manquante (hors mémoire, durée, échec) prend le temps admissible le plus lent des
autres langages à cette taille (section 6). Contrôle des anciens binaires (écart 4.1 : Odin, Chapel, Go) : rapport
des temps nouveau / ancien par cellule à la taille publiée ; au-delà de 5 %, l'écart est publié et les calculs sont
refaits avec les anciens binaires à la taille publiée.
Sorties : results/sizes/analysis.json, results/report_sizes.md. Variables : BOOT (2000), UA (20000)."""
import glob, json, math, os, re, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ROOT, NAMES, CATEGORIES, c_cells, c_score, c_vector, ranks_of, dirichlet  # noqa: E402
from analyze_v3 import Arrays3, build_pools, needed_keys, references, MAIN, K1N, K1S, K2_SIZES  # noqa: E402
from audit3 import tiers  # noqa: E402

B = int(os.environ.get("BOOT", "2000"))
U = int(os.environ.get("UA", "20000"))
RAW = os.path.join(ROOT, "results", "sizes", "raw")
HW = os.path.join(ROOT, "results", "hw", "machine30")
SIZED = ["k1", "k4", "k5", "k6", "k7", "k8", "k9"]
# colonnes du tableau de la section 3 : taille de chaque noyau dans les positions petite, publiée, grande
POS = {k: ["small", "pub", "large"] for k in SIZED}
POS["k5"] = ["pub", "l2", "l3"]
POS_NAMES = ["petite", "publiée", "grande"]
# paramètres de taille par taille (tools/sizes/sizes.py)
PARAMS = {"k1": {"small": 1 << 14, "pub": 1 << 22, "large": 1 << 24},
          "k4": {"small": 1 << 20, "pub": 1 << 24, "large": 1 << 28},
          "k5": {"pub": (2048, 1 << 16), "l2": (1 << 15, 1 << 12), "l3": (1 << 21, 1 << 6)},
          "k6": {"small": 1 << 16, "pub": 1 << 24, "large": 1 << 26},
          "k9": {"small": 1 << 8, "pub": 1 << 11, "large": 1 << 13}}
CONTROL = ["odin", "chapel", "go"]


# ------------------------------------------------------------------ données
def load_campaign():
    """{(construction, taille): {langage: {clé: [processus]}}}, latences de K8 de même, et inventaire des échecs.
    Un processus est retenu s'il a fini sans erreur, sans dépassement de mémoire ni de durée, et si toutes ses
    sommes de contrôle sont justes ; il est représenté par la médiane de ses répétitions (statistique de la v3).
    Compte aussi les enregistrements par modèle de processeur et par passe (section 5 : un seul modèle attendu)."""
    data, lat, failures, steal = defaultdict(lambda: defaultdict(dict)), defaultdict(lambda: defaultdict(dict)), [], []
    models = defaultdict(lambda: defaultdict(int))
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            models[r.get("cpu_model", "?")][r.get("pass")] += 1
            key = (r["kernel"], r["variant"], r["param"])
            tag = (r["build"], r["size"])
            ok = (not r.get("failed_calibration") and r.get("returncode") == 0 and not r.get("oom")
                  and not r.get("timeout") and r.get("n", 0) > 0 and r.get("oks") == ["True"])
            if not ok:
                # hors mémoire : la sentinelle du pilote (13 Gio) ou la limite du groupe de contrôle (13,35 Gio), dont
                # le noyau tue le processus par SIGKILL (code -9) sans que le pilote ait dépassé sa durée (4.1)
                fc = r.get("failed_calibration") or {}
                rc = r.get("returncode", fc.get("returncode"))
                to = bool(r.get("timeout") or fc.get("timeout"))
                failures.append({"lang": r["lang"], "build": r["build"], "size": r["size"], "key": key,
                                 "pass": r.get("pass"), "oom": bool(r.get("oom") or fc.get("oom") or (rc == -9 and not to)),
                                 "timeout": to, "returncode": rc, "oks": r.get("oks"),
                                 "absent": r["lang"] == "bqn" and key[0] == "k10"})
                continue
            if r.get("steal_frac", 0) > 0.05:
                steal.append((r["lang"], r["size"], key, r["steal_frac"]))
            data[tag][r["lang"]].setdefault(key, []).append([r["median"]])
            if key == v3.K8N:
                lat[tag][r["lang"]].setdefault(key, []).append(r.get("lat", []))
    return data, lat, failures, steal, {m: dict(ps) for m, ps in models.items()}


def position_data(data, lat, pos, build="new"):
    """Données d'une position (0 petite, 1 publiée, 2 grande) : chaque noyau à trois tailles à sa taille de la
    position, les autres (K2, K3, K10) à leur taille."""
    d, lt = defaultdict(dict), defaultdict(dict)
    for (b, size), dl in data.items():
        if b != build:
            continue
        for l, keys in dl.items():
            for key, procs in keys.items():
                k = key[0]
                if (k in SIZED and POS[k][pos] == size) or (k not in SIZED and size == "pub"):
                    d[l][key] = procs
    for (b, size), ll in lat.items():
        if b != build:
            continue
        for l, keys in ll.items():
            if POS["k8"][pos] == size:
                lt[l].update(keys)
    return d, lt


def fill_missing(d, langs, keys):
    """Section 6 : une cellule manquante prend le temps admissible le plus lent des autres langages. Seules les
    variantes communes (tools/driver.py, PLAN) sont concernées : une variante propre à un langage (extra_variants)
    n'existe pas pour les autres, qui ne la reçoivent pas. Et seules les cellules du score (needed_keys, comme en
    v3) : K10, hors score depuis la v2, n'est pas rempli (BQN n'a pas de K10 : ni threads ni coroutines)."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from driver import PLAN
    common = {(k, v, q) for k, lst in PLAN.items() for v, q in lst} & needed_keys()
    filled = []
    for key in sorted(k for k in keys if k in common):
        have = [l for l in langs if d.get(l, {}).get(key)]
        if not have or len(have) == len(langs):
            continue
        slow = max(have, key=lambda l: np.mean(np.log([np.median(p) for p in d[l][key]])))
        for l in langs:
            if not d.get(l, {}).get(key):
                d[l][key] = [list(p) for p in d[slow][key]]
                filled.append((l, key, slow))
    return filled


def campaign_keys(data):
    keys = set()
    for dl in data.values():
        for keys_l in dl.values():
            keys.update(keys_l)
    return keys


# ------------------------------------------------------------------ bornes physiques de la machine 30
def hw_numbers():
    """Bande passante en lecture sur 1 thread selon la taille (bw), STREAM triad sur 4 threads, pic FMA et fréquence
    (tools/hwprobe.c compilé en -O3 sur l'hôte, results/hw/machine30)."""
    bw = []
    for line in open(os.path.join(HW, "bw.txt")):
        m = re.match(r"bw:\s+(\d+) KiB\s+([\d.]+) GB/s", line)
        if m:
            bw.append((int(m.group(1)) * 1024, float(m.group(2)) * 1e9))
    stream4 = []
    for line in open(os.path.join(HW, "stream.txt")):
        m = re.search(r"stream: T=(\d)\s+(\w+)\s+([\d.]+) GB/s", line)
        if m and m.group(1) == "4" and m.group(2) == "triad":  # triad : la figure de mérite de STREAM
            stream4.append(float(m.group(3)) * 1e9)
    peak = []
    for line in open(os.path.join(HW, "peak.txt")):
        m = re.search(r"([\d.]+) GFLOP/s", line)
        if m:
            peak.append(float(m.group(1)) * 1e9)
    freq = [float(m.group(1)) * 1e9 for line in open(os.path.join(HW, "freq.txt"))
            for m in [re.search(r"freq: ([\d.]+) GHz", line)] if m]
    return {"bw": sorted(bw), "stream4": max(stream4), "peak": max(peak), "freq": max(freq)}


def bw1(hw, size):
    """Bande passante sur 1 thread du plus petit volume mesuré qui contient size (le plus grand volume au-delà)."""
    for s, b in hw["bw"]:
        if s >= size:
            return b
    return hw["bw"][-1][1]


def bw4(hw, size):
    """Sur 4 threads : 4 fois la bande passante d'un quart du volume tant que ce quart tient dans le L2 d'un cœur
    (2 Mio), STREAM sur 4 threads au-delà."""
    return 4 * bw1(hw, size / 4) if size / 4 <= 2 << 20 else hw["stream4"]


def ebounds(hw, pos):
    """Bornes physiques des mesures de E (mêmes volumes que EBOUND du classement publié), à la taille de la position."""
    n1, n4 = PARAMS["k1"][POS["k1"][pos]], PARAMS["k4"][POS["k4"][pos]]
    n5, inner5 = PARAMS["k5"][POS["k5"][pos]]
    n6, m9 = PARAMS["k6"][POS["k6"][pos]], PARAMS["k9"][POS["k9"][pos]]
    g9 = 2 * 8 * m9 * m9
    return {
        ("k1", 0): 16 * n1 / bw1(hw, 16 * n1),
        ("k3", 0): 2 ** 25 * 5 / hw["freq"],
        ("k4", 0): n4 / bw1(hw, n4),
        # K5 : calcul seul dans le L1, comme EBOUND (2 x 2 x n x INNER / pic) ; au-delà, aussi la bande passante
        ("k5", 0): max(4 * n5 * inner5 / hw["peak"], 0 if 8 * n5 <= 48 << 10 else 8 * n5 * inner5 / bw1(hw, 8 * n5)),
        ("k6", 0): 10 * n6 / bw1(hw, 10 * n6), ("k6", 1): 13 * n6 / bw1(hw, 13 * n6),
        ("k6", 2): 10 * n6 / bw4(hw, 10 * n6), ("k6", 3): 13 * n6 / bw4(hw, 13 * n6),
        ("k9", 0): 4 * g9 / bw1(hw, g9), ("k9", 1): 4 * g9 / bw4(hw, g9),
    }


# ------------------------------------------------------------------ calculs
def summarize(s, langs):
    order = sorted(langs, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    idx = {l: i for i, l in enumerate(RANKED)}
    return {"order": order, "exp": {l: s["exp21"][l] for l in langs}, "rank90": {l: s["rank90"][l] for l in langs},
            "first": {l: s["first"][l] for l in langs}, "ms0": {l: s["ms0"][l] for l in langs},
            "E": {l: s["E"][l] for l in langs}, "D": {l: s["D"][l] for l in langs}, "C": {l: s["C"][l] for l in langs},
            "tiers": tiers(order, s["prec"], idx)}


def single(d, lt, langs, footprint, c3, eb):
    """Méthode v3 inchangée (confrontation.scenario, règle « main ») sur une position, bornes de la machine 30."""
    saved = v3.EBOUND
    v3.EBOUND = eb
    try:
        return cf.scenario(d, lt, langs, footprint, c3, "main")
    finally:
        v3.EBOUND = saved


def scores_sizes(As, r, cfg, C, footprint, refs, ebs, wS, wE=None, wD=None, wP=None):
    """scores3 de la v3, chaque cellule de E, D1, D2 (part de K1) et D3 calculée à chaque position avec ses propres
    références puis moyennée en logarithme avec les poids wS ; K3 et D4 (une seule taille) pris à la position publiée."""
    est = cfg["est"]
    A1 = As[1]
    kernels = list(A1.e_meas)
    wE = wE or {k: 1 / len(kernels) for k in kernels}
    wD, wP = wD or v3.DW, wP or v3.WEIGHTS
    pos_of = lambda k: range(3) if k in SIZED else [1]  # noqa: E731
    wpos = lambda k, p: wS[p] if k in SIZED else 1.0  # noqa: E731
    n = len(A1.langs)
    lnE, ek = np.zeros(n), {}
    with np.errstate(all="ignore"):
        for k, ms in A1.e_meas.items():
            lr = []
            for i, ks in enumerate(ms):
                cell = np.zeros(n)
                for p in pos_of(k):
                    t = As[p].best(est, ks, r)
                    if cfg["enorm"] == "bounds" and (k, i) in ebs[p]:
                        v = np.log(np.minimum(1.0, ebs[p][(k, i)] / t))
                    else:
                        v = np.log(refs[p][est]["tstar"][(k, i)] / t)
                    cell = cell + wpos(k, p) * v
                lr.append(cell)
            ek[k] = np.mean(lr, axis=0)
            lnE += wE[k] * ek[k]
        E = 100 * np.exp(lnE)
        d1k = []
        for k, lst in A1.d1_meas.items():
            lr = []
            for i, ks in lst:
                cell = np.zeros(n)
                for p in pos_of(k):
                    ref = refs[p][est]
                    t = As[p].best(est, ks, r)
                    cell = cell + wpos(k, p) * np.log((ref["tstar"][(k, i)] if cfg["d1ref"] == "tstar" else ref["nat"][(k, i)]) / t)
                lr.append(cell)
            d1k.append(np.mean(lr, axis=0))
        D1 = np.exp(np.mean(d1k, axis=0))
        a = np.array([min(1.0, 64.0 / footprint[l]) if footprint.get(l) else np.nan for l in A1.langs])
        lbb = sum(wS[p] * np.log(np.minimum(1.0, As[p].dt(est, K1N, r) / As[p].dt(est, K1S, r))) for p in range(3))
        bb = np.exp(lbb)
        D2 = np.where(np.isnan(a), bb, np.sqrt(a * bb))
        l3 = np.zeros(n)
        for p in range(3):
            ref = refs[p][est]
            p50, p999, mx = As[p].lat[r, :, 0], As[p].lat[r, :, 1], As[p].lat[r, :, 2]
            if cfg["d3"] == "abs":
                d3 = np.sqrt((ref["d3_abs"][0] / p999) * (ref["d3_abs"][1] / mx))
            else:
                d3 = np.sqrt((ref["d3_rel"][0] / (p999 / p50)) * (ref["d3_rel"][1] / (mx / p50)))
            l3 = l3 + wS[p] * np.log(d3)
        D3 = np.exp(l3)
        l4 = []
        ref1 = refs[1][est]
        for s in K2_SIZES:
            t = A1.dt(est, ("k2", "tuned", s), r)
            refv = ref1["k2_best"][s] if cfg["d4"] == "best" else ref1["k2_c"][s]
            l4.append(np.log(np.minimum(1.0, refv / t)))
        D4 = np.exp(np.mean(l4, axis=0))
        D = 100 * (wD["D1"] * D1 + wD["D2"] * D2 + wD["D3"] * D3 + wD["D4"] * D4)
        if cfg["agg"] == "arith":
            MS = wP["C"] * C + wP["E"] * E + wP["D"] * D
        else:
            MS = np.exp(wP["C"] * np.log(C) + wP["E"] * np.log(E) + wP["D"] * np.log(D))
    return {"E": E, "D": D, "MS": MS, "D1": D1, "D2": D2, "D3": D3, "D4": D4, "Ek": {k: np.exp(v) for k, v in ek.items()}}


def three_sizes(host, pos_data, langs, footprint, c3, ebs):
    """Calcul 2. Les tirages des variantes (configuration, rééchantillonnage, poids) sont ceux de « Hôte » : le
    générateur principal passe d'abord par les tirages de résidus de la position publiée de « Hôte », comme dans
    confrontation.scenario ; les résidus de chaque position ont leur propre générateur."""
    rng = np.random.default_rng(v3.SEED)
    keys = sorted(needed_keys())
    Arrays3(host[0], host[1], langs, B, rng, build_pools(host[0], langs, keys))  # avance rng comme « Hôte »
    As, refs = [], []
    for p, (d, lt) in enumerate(pos_data):
        A = Arrays3(d, lt, langs, B, np.random.default_rng(v3.SEED + 4100 + p), build_pools(d, langs, keys))
        As.append(A)
        refs.append({e: references(A, e) for e in ("mean", "min")})
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    C0 = c_vector(c_score(c_cells("v2", c3), catw0), langs)
    w0 = np.full(3, 1 / 3)
    S0 = scores_sizes(As, 0, MAIN, C0, footprint, refs, ebs, w0)
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
        wP = {"C": wp[0], "E": wp[1], "D": wp[2]}
        wE = dict(zip(kernels, dirichlet(rng, 20 * np.full(len(kernels), 1 / len(kernels)))))
        wD = dict(zip(("D1", "D2", "D3", "D4"), dirichlet(rng, 20 * np.array([v3.DW[k] for k in ("D1", "D2", "D3", "D4")]))))
        catw = dict(zip(cat_names, dirichlet(rng, 20 * np.array([catw0[c] for c in cat_names]))))
        prng = np.random.default_rng(int(rng.integers(2 ** 63)))
        C = c_vector(c_score(c_cells(cfg["crule"], c3, rng=prng, noise=0.10), catw), langs)
        wS = dirichlet(srng, 20 * w0) if srng.random() < 0.5 else dirichlet(srng, [1, 1, 1])
        S_u = scores_sizes(As, b, cfg, C, footprint, refs, ebs, wS, wE=wE, wD=wD, wP=wP)
        r_ = ranks_of(S_u["MS"][rk])
        prec += r_[:, None] < r_[None, :]
        first[int(np.argmin(r_))] += 1
        ranks[u] = r_
    prec /= U
    exp21 = {a: 1 + sum(prec[RANKED.index(b_), RANKED.index(a)] for b_ in RANKED if b_ != a) for a in RANKED}
    ms0 = {l: float(S0["MS"][As[1].idx[l]]) for l in langs}
    return {"exp21": exp21, "ms0": ms0, "prec": prec,
            "first": {RANKED[j]: float(first[j] / U) for j in range(NR)},
            "rank90": {RANKED[j]: [int(np.quantile(ranks[:, j], 0.05)), int(np.quantile(ranks[:, j], 0.95))]
                       for j in range(NR)},
            "E": {l: float(S0["E"][As[1].idx[l]]) for l in langs}, "D": {l: float(S0["D"][As[1].idx[l]]) for l in langs},
            "C": {l: float(C0[As[1].idx[l]]) for l in langs},
            "Ek": {l: {k: float(S0["Ek"][k][As[1].idx[l]]) for k in S0["Ek"]} for l in langs}}


def control(data):
    """Écart 4.1 : rapport des temps nouveau / ancien (moyennes géométriques des médianes de processus) par cellule."""
    out = {}
    for l in CONTROL:
        new, old = data.get(("new", "pub"), {}).get(l, {}), data.get(("old", "pub"), {}).get(l, {})
        for key in sorted(set(new) & set(old)):
            a = math.exp(np.mean(np.log([np.median(p) for p in new[key]])))
            b = math.exp(np.mean(np.log([np.median(p) for p in old[key]])))
            out[f"{l}|{'|'.join(key)}"] = {"new": a, "old": b, "ratio": a / b, "over5": abs(a / b - 1) > 0.05}
    return out


def run_all(data, lat, langs, footprint, c3, hw, build_pub="new"):
    ebs = [ebounds(hw, p) for p in range(3)]
    pos = [position_data(data, lat, p) for p in range(3)]
    if build_pub == "old":  # contrôle : anciens binaires à la taille publiée, là où elle se trouve
        for l in CONTROL:
            for key, procs in data.get(("old", "pub"), {}).get(l, {}).items():
                k = key[0]
                pos[POS[k].index("pub") if k in SIZED else 1][0][l][key] = procs
            if lat.get(("old", "pub"), {}).get(l):
                pos[POS["k8"].index("pub")][1][l].update(lat[("old", "pub")][l])
    host_d, host_lt = defaultdict(dict), defaultdict(dict)
    for l in langs:  # Hôte : la taille publiée de chaque noyau (K5 compris)
        for p in range(3):
            for key, procs in pos[p][0].get(l, {}).items():
                k = key[0]
                if (k in SIZED and POS[k][p] == "pub") or (k not in SIZED and p == 1):
                    host_d[l][key] = procs
        host_lt[l] = dict(pos[1][1].get(l, {}))
    keys = campaign_keys(data)
    filled = {"Hôte": fill_missing(host_d, langs, keys)}
    for p in range(3):
        filled[POS_NAMES[p]] = fill_missing(pos[p][0], langs, keys)
    eb_host = ebounds(hw, 1)
    eb_host[("k5", 0)] = ebs[0][("k5", 0)]  # Hôte : K5 à sa taille publiée (position petite du tableau)
    res = {"Hôte": summarize(single(host_d, host_lt, langs, footprint, c3, eb_host), langs)}
    res["Trois tailles"] = summarize(three_sizes((host_d, host_lt), pos, langs, footprint, c3, ebs), langs)
    for p in range(3):
        res[f"Taille {POS_NAMES[p]}"] = summarize(single(pos[p][0], pos[p][1], langs, footprint, c3, ebs[p]), langs)
    h, t = res["Hôte"], res["Trois tailles"]
    moved = {l: (h["order"].index(l) + 1, t["order"].index(l) + 1) for l in langs
             if abs(h["order"].index(l) - t["order"].index(l)) > 2}
    return {"results": res, "moved_more_than_2": moved, "filled": {k: [list(map(str, x)) for x in v] for k, v in filled.items()},
            "bounds": {POS_NAMES[p]: {f"{k}#{i}": b for (k, i), b in ebs[p].items()} for p in range(3)}}


def main():
    v2.ADDED.clear()  # une seule campagne : aucun langage relié par un pont
    data, lat, failures, steal, models = load_campaign()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    hw = hw_numbers()
    langs = [l for l in RANKED]
    out = run_all(data, lat, langs, footprint, c3, hw)
    out["hw"] = {k: v for k, v in hw.items() if k != "bw"} | {"bw": hw["bw"]}
    out["failures"] = failures
    out["steal_over_5pct"] = steal
    out["cpu_models"] = models
    out["control"] = control(data)
    over = {k: v for k, v in out["control"].items() if v["over5"]}
    if over:
        out["with_old_binaries"] = run_all(data, lat, langs, footprint, c3, hw, build_pub="old")
    published = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))["results"]
    out["published"] = {l: {"MS": published[l]["MS"]} for l in RANKED if l in published}
    json.dump(out, open(os.path.join(ROOT, "results", "sizes", "analysis.json"), "w"), indent=1, default=float)
    report(out)


def report(o):
    R = o["results"]
    names = ["Hôte", "Trois tailles", "Taille petite", "Taille publiée", "Taille grande"]
    L = ["# v4, point 2 : trois tailles par noyau — résultats", "",
         "*Plan : `docs/V4_SIZES.md` (sections 6 à 8, écart 4.1). Généré par `analysis/sizes_v4.py` à partir de "
         "`results/sizes/raw` (machine 30). Le classement de tête du README ne change pas au point 2 (section 9).*", "",
         "## Classements", "",
         "| Langage | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    order = R["Trois tailles"]["order"]
    for l in order:
        cells = []
        for n in names:
            r = R[n]
            cells.append(f"{r['order'].index(l) + 1} ({r['exp'][l]:.2f} ; {r['ms0'][l]:.1f})")
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", "Chaque case : place (rang espéré ; score au centre). Ordre des lignes : « Trois tailles ».", "",
          "## Étages indicatifs (paires ordonnées dans au moins 95 % des variantes)", ""]
    for n in names:
        L.append(f"* {n} : " + " | ".join(", ".join(NAMES[l] for l in t) for t in R[n]["tiers"]))
    L += ["", "## Rangs qui bougent de plus de deux places entre « Hôte » et « Trois tailles »", ""]
    if o["moved_more_than_2"]:
        for l, (a, b) in sorted(o["moved_more_than_2"].items(), key=lambda x: x[1][1]):
            L.append(f"* {NAMES[l]} : {a}e → {b}e")
    else:
        L.append("* aucun")
    L += ["", "## Cellules manquantes (temps le plus lent des autres langages)", ""]
    for n, lst in o["filled"].items():
        L.append(f"* {n} : " + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]}" for x in lst) if lst else "aucune"))
    L += ["", "## Contrôle des anciens binaires (Odin, Chapel, Go, taille publiée)", "",
          "| Cellule | nouveau / ancien |", "|---|---|"]
    for k, v in sorted(o["control"].items()):
        L.append(f"| {k} | {v['ratio']:.3f}{' **> 5 %**' if v['over5'] else ''} |")
    fl = o["failures"]
    cells = lambda sel: sorted({(f["lang"], f["key"][0], f["size"], f["key"][1], f["key"][2]) for f in fl if sel(f)})
    absent, oom = cells(lambda f: f["absent"]), cells(lambda f: f["oom"] and not f["absent"])
    other = cells(lambda f: not f["oom"] and not f["absent"])
    fmt = lambda lst: ", ".join(f"{NAMES.get(l, l)} {k} {z} {v}{' ' + q if q else ''}" for l, k, z, v, q in lst) or "aucune"
    cm = o["cpu_models"]
    L += ["", "Processeur des enregistrements (section 5) : " + " ; ".join(
        f"{m} ({sum(ps.values())} enregistrements ; passes {', '.join(str(p) for p in sorted(ps, key=str))})"
        for m, ps in cm.items()) + (" — **plusieurs modèles : passes touchées à refaire**" if len(cm) > 1 else "") + "."]
    L += ["", f"Processus écartés : {len(fl)} (toutes passes) ; vol de temps > 5 % après reprise : "
          f"{len(o['steal_over_5pct'])}.", "",
          f"* hors mémoire ({len(oom)} cellules) : {fmt(oom)}",
          f"* absentes par conception, hors score (K10 de BQN : ni threads ni coroutines) : {fmt(absent)}",
          f"* autres échecs ({len(other)} cellules) : {fmt(other)}", ""]
    open(os.path.join(ROOT, "results", "report_sizes.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
