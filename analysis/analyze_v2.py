#!/usr/bin/env python3
"""Analyse v2 (plan pré-enregistré : docs/ANALYSIS_V2.md ; précisions d'implémentation : sa section 8).

Entrées
  * données retenues par l'analyse v1 (analyze.final_data) pour K1-K4 et K6-K9, mesurées sur la machine 1 ;
  * K5 : results/raw_v2, étiquette v2_k5 (machine 3), qui remplace toutes les données de K5 ;
  * réplication v2_m3 et relevé des pages géantes v2_thp (machine 3) ;
  * empreinte (results/footprint.json), vectorisation mesurée (results/vectorization.json),
    matrices de capacités v1 (capabilities.py) et v2 (capabilities_v2.py).
Sorties : results/summary_v2.json, results/report_v2.md, results/charts/v2_*.svg.
Variables d'environnement : BOOT (tirages bootstrap, 2000), UA (tirages de l'analyse globale, 20000).
"""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import final_data, E_MEASURES as E_V1, D1_MEASURES as D1_V1, K2_SIZES, RANKED, ANNEX, ROOT, BOUNDS  # noqa: E402
from capabilities import MATRIX, CATEGORIES, M  # noqa: E402
from capabilities_v2 import V2_OVERRIDES, V2_DROP  # noqa: E402

B = int(os.environ.get("BOOT", "2000"))
U = int(os.environ.get("UA", "20000"))
SEED = 20261029
WEIGHTS = {"C": 0.35, "E": 0.40, "D": 0.25}
DW = {"D1": 0.5, "D2": 0.15, "D3": 0.15, "D4": 0.2}
NR = len(RANKED)

# K10 hors score (choix 3) : retiré de E et de D1
E_V2 = {k: v for k, v in E_V1.items() if k != "k10"}
D1_V2 = {k: v for k, v in D1_V1.items() if k != "k10"}
K1N, K1S = ("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy")
K8N = ("k8", "natural", "")

# Bornes physiques, alternative de normalisation de E (plan, section 3), par mesure (noyau, indice)
BW1, BW4 = 10e9, 61e9
EBOUND = {
    ("k1", 0): 4 * 4 * 4194304 / BW1,
    ("k3", 0): 2 ** 25 * 5 / 3.2e9,
    ("k4", 0): 16777216 / BW1,
    ("k5", 0): 2 * 2 * 2048 * 65536 / 182e9,
    ("k6", 0): 10 * 16777216 / BW1, ("k6", 1): 13 * 16777216 / BW1,
    ("k6", 2): 10 * 16777216 / BW4, ("k6", 3): 13 * 16777216 / BW4,
    ("k9", 0): 4 * 2 * 8 * 2048 * 2048 / 8.84e9, ("k9", 1): 4 * 2 * 8 * 2048 * 2048 / 43.3e9,
}
# Contrôle de vraisemblance des données de la machine 3 (même règle que v1 : temps < 0,9 x borne = calcul sauté).
# K5 : débit FMA crête le plus haut mesuré sur la machine 3 (232 Gflop/s). Réplication : bornes de la machine 1
# rendues généreuses (bande passante 50 Go/s sur 1 thread, 200 Go/s sur 4 ; 3,9 GHz pour K3), pour ne signaler
# qu'un travail sauté, pas un cache plus grand.
BOUNDS_M3 = {}
for key, b in BOUNDS.items():
    k = key[0]
    if k == "k5":
        BOUNDS_M3[key] = 2 * 2048 * 65536 / 232e9
    elif k == "k3":
        BOUNDS_M3[key] = b * 3.3 / 3.9
    elif key[1] == "mt":
        BOUNDS_M3[key] = b * BW4 / 200e9
    else:
        BOUNDS_M3[key] = b * BW1 / 50e9

# Regroupement par backend (profil « langage et implémentation »)
BACKEND = {
    "GCC": ["c_gcc", "cpp", "fortran", "ada"],
    "LLVM": ["c", "fortran_flang", "rust", "zig", "odin", "c3", "d", "nim", "chapel", "julia", "mojo", "haskell"],
    "natif, autre": ["go", "ocaml"],
    "JIT ou VM": ["java", "csharp", "js", "js_bun", "luajit"],
    "interprète": ["python", "lua"],
}


# ------------------------------------------------------------------ chargement
def load_raw(tag):
    """Mesures de results/raw_v2 portant l'étiquette tag : (données, latences par processus, témoins, invalides, enregistrements)."""
    data, lat, wit, invalid, recs = defaultdict(dict), defaultdict(dict), defaultdict(dict), [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "raw_v2", "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != tag:
                continue
            recs.append(r)
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                invalid.append((r["lang"], key, r.get("returncode"), [x["chk"] for x in reps][:1]))
                continue
            data[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            lat[r["lang"]].setdefault(key, []).append(r.get("lat", []))
            wit[r["lang"]].setdefault(key, []).append(r.get("witness", {}))
    return data, lat, wit, invalid, recs


def load_lat_v1():
    """Latences de K8 natural de la campagne, par processus (l'analyse v1 les mettait toutes ensemble)."""
    lat = defaultdict(list)
    for f in glob.glob(os.path.join(ROOT, "results", "raw", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            reps = r.get("reps", [])
            if (r["kernel"], r["variant"], r["param"]) != K8N:
                continue
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                continue
            lat[r["lang"]].append((r.get("proc"), r.get("ts"), [x["sec"] for x in reps], r.get("lat", [])))
    return lat


def sanity(data, bounds):
    flags = []
    for lang, d in data.items():
        for key, bound in bounds.items():
            if key in d and float(np.median([np.median(p) for p in d[key]])) < 0.9 * bound:
                flags.append((lang, key))
    for lang, key in flags:
        del data[lang][key]
    return flags


# ------------------------------------------------------------------ régime établi (choix 1)
def steady(xs):
    """Rupture de niveau unique dans log(t) : critère BIC (n-2)·ln(RSS0/RSS1) > 3·ln n et écart des médianes > 20 %,
    au moins 3 répétitions de chaque côté, processus d'au moins 6 répétitions. Renvoie (indice de coupure, m1, m2)."""
    n = len(xs)
    if n < 6:
        return None
    y = np.log(np.asarray(xs, float))
    rss0 = float(((y - y.mean()) ** 2).sum())
    if rss0 <= 0:
        return None
    best, cut = None, None
    for c in range(3, n - 2):
        a, b = y[:c], y[c:]
        r = float(((a - a.mean()) ** 2).sum() + ((b - b.mean()) ** 2).sum())
        if best is None or r < best:
            best, cut = r, c
    m1, m2 = float(np.median(xs[:cut])), float(np.median(xs[cut:]))
    bic = math.inf if best <= 0 else (n - 2) * math.log(rss0 / best)
    if bic > 3 * math.log(n) and max(m1, m2) / min(m1, m2) > 1.2:
        return cut, m1, m2
    return None


def apply_steady(data, lat=None):
    """Garde le dernier segment de chaque processus ; coupe les latences de K8 au même endroit."""
    cuts = []
    for lang, d in data.items():
        for key, procs in d.items():
            for j, p in enumerate(procs):
                s = steady(p)
                if s:
                    cuts.append({"lang": lang, "key": list(key), "proc": j, "n": len(p), "cut": s[0],
                                 "before": s[1], "after": s[2]})
                    procs[j] = p[s[0]:]
                    if lat is not None and key in lat.get(lang, {}) and len(lat[lang][key][j]) == len(p):
                        lat[lang][key][j] = lat[lang][key][j][s[0]:]
    return cuts


# ------------------------------------------------------------------ estimateurs et bootstrap hiérarchique
def stats_rows(procs, nb, rng):
    """Ligne 0 : estimation ponctuelle ; lignes 1..nb : tirages bootstrap (processus, puis répétitions).
    Renvoie (médiane des médianes, minimum des médianes), chacun de forme (nb + 1,)."""
    meds0 = np.array([np.median(p) for p in procs])
    med, mn = np.empty(nb + 1), np.empty(nb + 1)
    med[0], mn[0] = np.median(meds0), meds0.min()
    if nb:
        P = len(procs)
        pools = np.empty((P, nb))
        for j, p in enumerate(procs):
            x = np.asarray(p, float)
            pools[j] = np.median(x[rng.integers(0, len(x), size=(nb, len(x)))], axis=1)
        meds = pools[rng.integers(0, P, size=(nb, P)), rng.integers(0, nb, size=(nb, P))]
        med[1:], mn[1:] = np.median(meds, axis=1), meds.min(axis=1)
    return med, mn


def lat_rows(lprocs, nb, rng):
    """D3 : médianes, sur toutes les répétitions, de p50, p99,9 et max (ligne 0) ; bootstrap des processus puis des
    répétitions (lignes 1..nb). Renvoie un tableau (nb + 1, 3)."""
    arrs = [np.asarray(p, float) for p in lprocs if len(p)]
    out = np.empty((nb + 1, 3))
    allr = np.vstack(arrs)
    out[0] = np.median(allr[:, [0, 3, 4]], axis=0)
    for b in range(1, nb + 1):
        pick = rng.integers(0, len(arrs), size=len(arrs))
        rows = np.vstack([arrs[j][rng.integers(0, len(arrs[j]), size=len(arrs[j]))] for j in pick])
        out[b] = np.median(rows[:, [0, 3, 4]], axis=0)
    return out


class Arrays:
    """Temps (estimateur x ligne x implémentation) pour toutes les mesures du score v2."""

    def __init__(self, data, lat, langs, nb, rng, e_meas=E_V2, d1_meas=D1_V2):
        self.langs, self.nb, self.e_meas, self.d1_meas = langs, nb, e_meas, d1_meas
        self.idx = {l: i for i, l in enumerate(langs)}
        self.ranked = np.array([self.idx[l] for l in RANKED if l in self.idx])
        keys = set()
        for ms in e_meas.values():
            for ks in ms:
                keys.update(ks)
        for lst in d1_meas.values():
            for _, ks in lst:
                keys.update(ks)
        keys.update([K1N, K1S] + [("k2", "tuned", s) for s in K2_SIZES])
        self.t = {}  # (estimateur, clé) -> (nb + 1, n)
        for key in sorted(keys):
            med = np.full((nb + 1, len(langs)), np.nan)
            mn = np.full((nb + 1, len(langs)), np.nan)
            for l in langs:
                procs = data.get(l, {}).get(key)
                if procs:
                    med[:, self.idx[l]], mn[:, self.idx[l]] = stats_rows(procs, nb, rng)
            self.t[("med", key)], self.t[("min", key)] = med, mn
        self.lat = np.full((nb + 1, len(langs), 3), np.nan)
        for l in langs:
            lp = lat.get(l, {}).get(K8N)
            if lp and any(len(p) for p in lp):
                self.lat[:, self.idx[l], :] = lat_rows(lp, nb, rng)

    def best(self, est, keys, r):
        """Meilleur temps parmi les variantes admissibles (NaN si aucune)."""
        arr = np.vstack([self.t[(est, k)][r] for k in keys])
        with np.errstate(all="ignore"):
            out = np.nanmin(np.where(np.isnan(arr), np.inf, arr), axis=0)
        out[np.isinf(out)] = np.nan
        return out


# ------------------------------------------------------------------ pilier C
def c_cells(rule, c3, rng=None, noise=0.0):
    """Valeurs des cellules par langage de base : {lang: {cap: valeur}} (C3 retiré en v2)."""
    out = {}
    for l in RANKED:
        cells = {}
        for cat, (_, caps) in CATEGORIES.items():
            for cap in caps:
                if rule == "v2" and cap in V2_DROP:
                    continue
                v = MATRIX[l][cap]
                if v == M:
                    cells[cap] = c3.get(l, 0)  # mesurée : pas de bruit de jugement
                    continue
                v = V2_OVERRIDES[(l, cap)][0] if rule == "v2" and (l, cap) in V2_OVERRIDES else v[0]
                if rng is not None and rng.random() < noise:
                    v = 0.5 if v in (0, 1) else (0.0 if rng.random() < 0.5 else 1.0)
                cells[cap] = v
        out[l] = cells
    return out


def c_score(cells, catw):
    res = {}
    for l, cs in cells.items():
        tot = 0.0
        for cat, (_, caps) in CATEGORIES.items():
            vals = [cs[c] for c in caps if c in cs]
            tot += catw[cat] * sum(vals) / len(vals)
        res[l] = 100 * tot
    return res


def c_vector(cdict, langs):
    return np.array([cdict[ANNEX.get(l, l)] for l in langs])


# ------------------------------------------------------------------ score
MAIN = {"est": "med", "enorm": "frontier", "d3": "abs", "d4": "best", "d1ref": "tstar", "agg": "arith", "crule": "v2"}


def scores(A, r, cfg, C, footprint, wE=None, wD=None, wP=None):
    """Piliers E, D et score MS pour toutes les implémentations, ligne r des tableaux, configuration cfg."""
    est, rk = cfg["est"], A.ranked
    kernels = list(A.e_meas)
    wE = wE or {k: 1 / len(kernels) for k in kernels}
    wD, wP = wD or DW, wP or WEIGHTS
    n = len(A.langs)
    # E
    tstar, lnE, ek = {}, np.zeros(n), {}
    with np.errstate(all="ignore"):
        for k, ms in A.e_meas.items():
            lr = []
            for i, ks in enumerate(ms):
                t = A.best(est, ks, r)
                tstar[(k, i)] = np.nanmin(t[rk])
                if cfg["enorm"] == "bounds" and (k, i) in EBOUND:
                    lr.append(np.log(np.minimum(1.0, EBOUND[(k, i)] / t)))
                else:
                    lr.append(np.log(tstar[(k, i)] / t))
            ek[k] = np.mean(lr, axis=0)
            lnE += wE[k] * ek[k]
        E = 100 * np.exp(lnE)
        # D1
        d1k = []
        for k, lst in A.d1_meas.items():
            lr = []
            for i, ks in lst:
                t = A.best(est, ks, r)
                ref = tstar[(k, i)] if cfg["d1ref"] == "tstar" else np.nanmin(t[rk])
                lr.append(np.log(ref / t))
            d1k.append(np.mean(lr, axis=0))
        D1 = np.exp(np.mean(d1k, axis=0))
        # D2
        a = np.array([min(1.0, 64.0 / footprint[l]) if footprint.get(l) else np.nan for l in A.langs])
        bb = np.minimum(1.0, A.t[(est, K1N)][r] / A.t[(est, K1S)][r])
        D2 = np.where(np.isnan(a), bb, np.sqrt(a * bb))
        # D3
        p50, p999, mx = A.lat[r, :, 0], A.lat[r, :, 1], A.lat[r, :, 2]
        if cfg["d3"] == "abs":
            D3 = np.sqrt((np.nanmin(p999[rk]) / p999) * (np.nanmin(mx[rk]) / mx))
        else:
            D3 = np.sqrt((np.nanmin((p999 / p50)[rk]) / (p999 / p50)) * (np.nanmin((mx / p50)[rk]) / (mx / p50)))
        # D4
        l4 = []
        for s in K2_SIZES:
            t = A.t[(est, ("k2", "tuned", s))][r]
            ref = np.nanmin(t[rk]) if cfg["d4"] == "best" else t[A.idx["c"]]
            l4.append(np.log(np.minimum(1.0, ref / t)))
        D4 = np.exp(np.mean(l4, axis=0))
        D = 100 * (wD["D1"] * D1 + wD["D2"] * D2 + wD["D3"] * D3 + wD["D4"] * D4)
        if cfg["agg"] == "arith":
            MS = wP["C"] * C + wP["E"] * E + wP["D"] * D
        else:
            MS = np.exp(wP["C"] * np.log(C) + wP["E"] * np.log(E) + wP["D"] * np.log(D))
    return {"E": E, "D": D, "MS": MS, "D1": D1, "D2": D2, "D3": D3, "D4": D4,
            "Ek": {k: np.exp(v) for k, v in ek.items()}, "tstar": tstar}


def ranks_of(ms_ranked):
    """Rang (1 = meilleur) de chaque langage classé ; NaN en dernier."""
    order = np.argsort(-np.nan_to_num(ms_ranked, nan=-1e9), kind="stable")
    rk = np.empty(len(ms_ranked), int)
    rk[order] = np.arange(1, len(ms_ranked) + 1)
    return rk


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 3:
        return None, int(ok.sum())

    def rank(v):
        o = np.argsort(v, kind="stable")
        r = np.empty(len(v))
        r[o] = np.arange(len(v), dtype=float)
        for u in np.unique(v):  # rangs moyens pour les ex aequo
            m = v == u
            r[m] = r[m].mean()
        return r
    rx, ry = rank(x[ok]), rank(y[ok])
    if rx.std() == 0 or ry.std() == 0:
        return None, int(ok.sum())
    return float(np.corrcoef(rx, ry)[0, 1]), int(ok.sum())


def dirichlet(rng, alpha):
    g = rng.gamma(np.asarray(alpha, float))
    return g / g.sum()


# ------------------------------------------------------------------ jeux de données
def dataset_main():
    """Données de la configuration principale : v1 sans K5 ni K10, plus K5 de v2_k5."""
    data, _lat_flat, _rss, invalid, sus, bridge = final_data()
    for l in data:
        for key in [k for k in data[l] if k[0] in ("k5", "k10")]:
            del data[l][key]
    v1_k5 = defaultdict(dict)  # pour la décomposition : K5 tel que l'analyse v1 l'utilisait
    d_old, *_ = final_data()
    for l in d_old:
        for key, procs in d_old[l].items():
            if key[0] == "k5":
                v1_k5[l][key] = procs
    k5, k5lat, k5wit, k5inv, k5recs = load_raw("v2_k5")
    k5_sus = sanity(k5, {k: v for k, v in BOUNDS_M3.items() if k[0] == "k5"})
    for l in k5:
        for key, procs in k5[l].items():
            data[l][key] = procs
    lat = defaultdict(dict)
    for l, procs in load_lat_v1().items():
        lat[l][K8N] = [p[3] for p in procs]
        # alignement des latences sur les processus retenus par final_data (mêmes processus, même ordre de fichier)
    return data, lat, invalid, sus, bridge, v1_k5, (k5, k5wit, k5inv, k5_sus, k5recs)


def align_lat(data, lat):
    """Les latences par processus doivent correspondre aux processus de temps (même nombre, même ordre)."""
    for l in list(lat):
        if K8N in lat[l] and K8N in data.get(l, {}) and len(lat[l][K8N]) != len(data[l][K8N]):
            lat[l][K8N] = [x for x in lat[l][K8N] if len(x)]
            if len(lat[l][K8N]) != len(data[l][K8N]):
                raise SystemExit(f"latences de K8 non alignées pour {l}")


def main():
    rng = np.random.default_rng(SEED)
    import copy
    data, lat, invalid, sus, bridge, v1_k5, (k5, k5wit, k5inv, k5_sus, k5recs) = dataset_main()
    align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw_data, raw_lat = copy.deepcopy(data), copy.deepcopy(lat)
    cuts = apply_steady(data, lat)
    k5_steady = copy.deepcopy(k5)
    apply_steady(k5_steady)

    # ---------------- configuration principale : estimation ponctuelle et bootstrap
    A = Arrays(data, lat, langs, B, rng)
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    C_main = c_vector(c_score(c_cells("v2", c3), catw0), langs)
    C_v1 = c_vector(c_score(c_cells("v1", c3), catw0), langs)
    S0 = scores(A, 0, MAIN, C_main, footprint)
    rk = A.ranked
    ms_boot = np.empty((B, NR))
    e_boot, d_boot = np.empty((B, len(langs))), np.empty((B, len(langs)))
    for b in range(1, B + 1):
        S = scores(A, b, MAIN, C_main, footprint)
        ms_boot[b - 1], e_boot[b - 1], d_boot[b - 1] = S["MS"][rk], S["E"], S["D"]
    ms0 = S0["MS"][rk]
    rank_boot = np.array([ranks_of(x) for x in ms_boot])

    # ---------------- ensembles de confiance simultanés (Mogstad, Romano, Shaikh et Wilhelm, 2024)
    dhat = ms0[:, None] - ms0[None, :]
    dstar = ms_boot[:, :, None] - ms_boot[:, None, :]
    sig = dstar.std(axis=0, ddof=1)
    np.fill_diagonal(sig, np.inf)
    tmax = np.nanmax(np.abs(dstar - dhat[None]) / sig[None], axis=(1, 2))
    crit = float(np.quantile(tmax, 0.95))
    ahead = (dhat - crit * sig) > 0  # ahead[j, k] : j devant k, significatif
    rset = [(1 + int(ahead[:, j].sum()), NR - int(ahead[j, :].sum())) for j in range(NR)]

    # ---------------- analyse d'incertitude globale
    prec = np.zeros((NR, NR))
    ua_ranks = np.empty((U, NR), int)
    opts = {"est": ["med", "min"], "enorm": ["frontier", "bounds"], "d3": ["abs", "rel"], "d4": ["best", "c"],
            "d1ref": ["tstar", "best_natural"], "agg": ["arith", "geo"], "crule": ["v2", "v1"]}
    kernels = list(E_V2)
    cat_names = list(CATEGORIES)
    for u in range(U):
        cfg = {k: v[int(rng.integers(len(v)))] for k, v in opts.items()}
        b = int(rng.integers(1, B + 1))
        if rng.random() < 0.5:
            wp = dirichlet(rng, 20 * np.array([0.35, 0.40, 0.25]))
        else:
            wp = dirichlet(rng, [1, 1, 1])
        wP = {"C": wp[0], "E": wp[1], "D": wp[2]}
        we = dirichlet(rng, 20 * np.full(len(kernels), 1 / len(kernels)))
        wE = dict(zip(kernels, we))
        wd = dirichlet(rng, 20 * np.array([DW[k] for k in ("D1", "D2", "D3", "D4")]))
        wD = dict(zip(("D1", "D2", "D3", "D4"), wd))
        wc = dirichlet(rng, 20 * np.array([catw0[c] for c in cat_names]))
        catw = dict(zip(cat_names, wc))
        prng = np.random.default_rng(int(rng.integers(2 ** 63)))
        C = c_vector(c_score(c_cells(cfg["crule"], c3, rng=prng, noise=0.10), catw), langs)
        S = scores(A, b, cfg, C, footprint, wE=wE, wD=wD, wP=wP)
        r_ = ranks_of(S["MS"][rk])
        ua_ranks[u] = r_
        prec += r_[:, None] < r_[None, :]
    prec /= U

    # ---------------- groupes : égalité si ensembles simultanés recouvrants, ou ordre non établi dans 90 % des tirages
    order = list(np.argsort(-ms0, kind="stable"))

    def overlap(j, k):
        return not (rset[j][1] < rset[k][0] or rset[k][1] < rset[j][0])

    def tied(j, k):
        return overlap(j, k) or max(prec[j, k], prec[k, j]) < 0.90

    def make_groups(tie):
        """Une frontière sépare les positions i et i + 1 de l'ordre principal seulement si aucun langage au-dessus
        n'est à égalité avec un langage au-dessous."""
        gs, cur = [], [order[0]]
        for pos in range(1, NR):
            if any(tie(j, k) for j in order[:pos] for k in order[pos:]):
                cur.append(order[pos])
            else:
                gs.append(cur)
                cur = [order[pos]]
        gs.append(cur)
        return gs
    groups = make_groups(tied)
    groups_meas = make_groups(overlap)

    # ---------------- résultats par langage
    res = {}
    for i, l in enumerate(langs):
        res[l] = {"C": float(C_main[i]), "C_v1": float(C_v1[i]), "E": float(S0["E"][i]), "D": float(S0["D"][i]),
                  "MS": float(S0["MS"][i]),
                  "D_parts": {k: float(S0[k][i]) for k in ("D1", "D2", "D3", "D4")},
                  "E_kernels": {k: float(v[i]) for k, v in S0["Ek"].items()},
                  "E_ci": [float(np.nanquantile(e_boot[:, i], 0.025)), float(np.nanquantile(e_boot[:, i], 0.975))],
                  "D_ci": [float(np.nanquantile(d_boot[:, i], 0.025)), float(np.nanquantile(d_boot[:, i], 0.975))]}
    for j, l in enumerate(RANKED):
        rr = res[l]
        rr["MS_ci"] = [float(np.quantile(ms_boot[:, j], 0.025)), float(np.quantile(ms_boot[:, j], 0.975))]
        rr["rank"] = int(order.index(j) + 1)
        rr["rank_set"] = list(rset[j])
        rr["boot_rank_90"] = [int(np.quantile(rank_boot[:, j], 0.05)), int(np.quantile(rank_boot[:, j], 0.95))]
        ur = ua_ranks[:, j]
        rr["ua_rank_median"] = float(np.median(ur))
        rr["ua_rank_90"] = [int(np.quantile(ur, 0.05)), int(np.quantile(ur, 0.95))]
        rr["P1"], rr["P3"], rr["P10"] = (float((ur == 1).mean()), float((ur <= 3).mean()), float((ur <= 10).mean()))
        br = rank_boot[:, j]
        rr["boot_rank_median"] = float(np.median(br))
        rr["boot_P1"], rr["boot_P3"], rr["boot_P10"] = (float((br == 1).mean()), float((br <= 3).mean()),
                                                         float((br <= 10).mean()))
        rr["group"] = next(g for g, members in enumerate(groups) if j in members) + 1
        rr["group_meas"] = next(g for g, members in enumerate(groups_meas) if j in members) + 1

    # ---------------- profils par principe (configuration principale, estimations ponctuelles)
    cells_v2 = c_cells("v2", c3)
    prof = {}
    for i, l in enumerate(langs):
        ek = {k: float(v[i]) for k, v in S0["Ek"].items()}

        def ratio(k, j):
            t = A.best("med", E_V2[k][j], 0)[i]
            return float(S0["tstar"][(k, j)] / t)
        base = ANNEX.get(l, l)
        p = {"disposition": [ek["k1"], float(S0["D2"][i])],
             "SIMD": [ek["k5"], ek["k4"], c3.get(l, c3.get(base, 0))],
             "hiérarchie mémoire": [float(S0["D4"][i]), ratio("k9", 0)],
             "concurrence": [ek["k3"], ratio("k6", 2), ratio("k6", 3), ratio("k9", 1)],
             "allocation et prévisibilité": [ek["k8"], float(S0["D3"][i])],
             "analytique": [ratio("k6", 0), ratio("k6", 1), ek["k7"]]}
        prof[l] = {k: (None if any(v is None or not np.isfinite(v) for v in vs) else 100 * float(np.mean(vs)))
                   for k, vs in p.items()}
        for cat, (_, caps) in CATEGORIES.items():
            vals = [cells_v2[base][c] for c in caps if c in cells_v2[base]]
            prof[l]["capacités " + cat] = 100 * sum(vals) / len(vals)

    # ---------------- front de Pareto sur (C, E, D)
    pareto = []
    for l in RANKED:
        a = (res[l]["C"], res[l]["E"], res[l]["D"])
        dom = any(all(x >= y for x, y in zip((res[m]["C"], res[m]["E"], res[m]["D"]), a)) and
                  any(x > y for x, y in zip((res[m]["C"], res[m]["E"], res[m]["D"]), a)) for m in RANKED if m != l)
        if not dom:
            pareto.append(l)

    # ---------------- poids effectifs (part de variance de MS expliquée linéairement par chaque pilier)
    eff = {}
    for name in ("C", "E", "D"):
        x = np.array([res[l][name] for l in RANKED])
        y = np.array([res[l]["MS"] for l in RANKED])
        eff[name] = float(np.corrcoef(x, y)[0, 1] ** 2)
    tot = sum(eff.values())
    eff = {k: {"R2": v, "part": v / tot} for k, v in eff.items()}

    # ---------------- bimodalité (après régime établi) et coupures
    bimodal = []
    for l in langs:
        for key, procs in data.get(l, {}).items():
            if len(procs) >= 2:
                meds = [float(np.median(p)) for p in procs]
                if max(meds) / min(meds) > 1.25:
                    bimodal.append({"lang": l, "key": list(key), "ratio": max(meds) / min(meds), "n": len(procs)})

    # ---------------- décomposition : la configuration principale, un choix ramené à v1 à la fois
    decomp = {}
    def rank_dict(ms, langs_):
        o = sorted([l for l in RANKED if l in langs_], key=lambda l: -ms[langs_.index(l)])
        return {l: o.index(l) + 1 for l in o}
    decomp["v2"] = rank_dict(list(S0["MS"]), langs)
    for name, cfgd, Cv in [("D3 relatif à p50", {"d3": "rel"}, C_main), ("D4 rapporté à C", {"d4": "c"}, C_main),
                           ("pilier C v1 (avec C3)", {"crule": "v1"}, C_v1), ("minimum des processus", {"est": "min"}, C_main),
                           ("bornes physiques", {"enorm": "bounds"}, C_main), ("agrégation géométrique", {"agg": "geo"}, C_main),
                           ("D1 rapporté au meilleur naturel", {"d1ref": "best_natural"}, C_main)]:
        S = scores(A, 0, {**MAIN, **cfgd}, Cv, footprint)
        decomp[name] = rank_dict(list(S["MS"]), langs)
    A_raw = Arrays(raw_data, raw_lat, langs, 0, rng)
    decomp["sans régime établi"] = rank_dict(list(scores(A_raw, 0, MAIN, C_main, footprint)["MS"]), langs)
    d_k5 = copy.deepcopy(data)
    for l in d_k5:
        for key in [k for k in d_k5[l] if k[0] == "k5"]:
            del d_k5[l][key]
        for key, procs in v1_k5.get(l, {}).items():
            d_k5[l][key] = copy.deepcopy(procs)
    apply_steady({l: {k: v for k, v in d.items() if k[0] == "k5"} for l, d in d_k5.items()})
    A_k5 = Arrays(d_k5, lat, langs, 0, rng)
    decomp["K5 d'avant (machines 1 et 2)"] = rank_dict(list(scores(A_k5, 0, MAIN, C_main, footprint)["MS"]), langs)
    d_k10 = copy.deepcopy(data)
    d_v1, *_ = final_data()
    for l in d_k10:
        for key, procs in d_v1.get(l, {}).items():
            if key[0] == "k10":
                d_k10[l][key] = copy.deepcopy(procs)
    apply_steady({l: {k: v for k, v in d.items() if k[0] == "k10"} for l, d in d_k10.items()})
    A_k10 = Arrays(d_k10, lat, langs, 0, rng, e_meas=E_V1, d1_meas=D1_V1)
    decomp["avec K10"] = rank_dict(list(scores(A_k10, 0, MAIN, C_main, footprint)["MS"]), langs)

    # ---------------- langage et implémentation : couples, et K4 / K8 par backend
    couples = {}
    for a_, b_ in [("c", "c_gcc"), ("fortran", "fortran_flang"), ("lua", "luajit"), ("js", "js_bun"), ("python", "python_ft")]:
        couples[f"{a_}|{b_}"] = {x: {k: res[x][k] for k in ("C", "E", "D", "MS", "E_kernels", "D_parts")} if x in res else None
                                 for x in (a_, b_)}
    backend = {g: {l: {"k4": res[l]["E_kernels"].get("k4"), "k8": res[l]["E_kernels"].get("k8")} for l in ls if l in res}
               for g, ls in BACKEND.items()}

    # ---------------- témoin d'environnement (K5, machine 3)
    witness = witness_analysis(k5_steady, k5wit, langs, data, lat, footprint, C_main, rng, res)

    # ---------------- réplication sur la machine 3
    repl = replication(data, langs, footprint, C_main, k5_steady, rng, res, groups, order)

    # ---------------- pages géantes
    thp = thp_table()

    out = {"config": MAIN, "B": B, "U": U, "results": res, "groups": [[RANKED[j] for j in g] for g in groups],
           "groups_meas": [[RANKED[j] for j in g] for g in groups_meas],
           "mogstad_crit": crit, "precedence": {RANKED[j]: {RANKED[k]: float(prec[j, k]) for k in range(NR)} for j in range(NR)},
           "profiles": prof, "pareto": pareto, "effective_weights": eff, "steady_cuts": cuts, "bimodal": bimodal,
           "decomposition": decomp, "couples": couples, "backend": backend, "witness": witness, "replication": repl, "thp": thp,
           "k5_invalid": k5inv, "k5_below_bound": k5_sus, "invalid_v1": invalid, "bridge_k3": bridge,
           "tstar": {f"{k}:{i}": float(v) for (k, i), v in S0["tstar"].items()},
           "k5_processes": {l: {f"{k[1]}": len(v) for k, v in d.items()} for l, d in k5.items()}}
    json.dump(out, open(os.path.join(ROOT, "results", "summary_v2.json"), "w"), indent=1, default=str)
    report(out)


def witness_analysis(k5, k5wit, langs, data, lat, footprint, C_main, rng, res):
    out = {"per_impl": {}, "pooled": {}}
    pooled_t, pooled_w = defaultdict(list), defaultdict(list)
    allw = []
    for l, d in k5.items():
        for key, procs in d.items():
            meds = [float(np.median(p)) for p in procs]
            ws = k5wit[l][key]
            g = [w.get("gflops", np.nan) for w in ws]
            rho, n = spearman(g, meds)
            out["per_impl"][f"{l}:{key[1]}"] = {"rho_gflops": rho, "n": n}
            mref = float(np.median(meds))
            for m, w in zip(meds, ws):
                pooled_t["t"].append(m / mref)
                for f in ("gflops", "ghz", "lat2M_ns", "lat32M_ns", "bw_GBps"):
                    pooled_w[f].append(w.get(f, np.nan))
                allw.append((l, key, w.get("gflops", np.nan)))
    for f, ws in pooled_w.items():
        rho, n = spearman(ws, pooled_t["t"])
        out["pooled"][f] = {"rho": rho, "n": n}
    gs = np.array([x[2] for x in allw], float)
    if np.isfinite(gs).sum() >= 10:
        thr = float(np.nanquantile(gs, 0.10))
        out["decile_threshold_gflops"] = thr
        out["witness_range"] = {f: [float(np.nanmin(v)), float(np.nanmedian(v)), float(np.nanmax(v))]
                                for f, v in ((f, np.array(pooled_w[f], float)) for f in pooled_w)}
        # sensibilité : processus du décile le plus lent du témoin retirés
        d2 = {l: dict(dd) for l, dd in data.items()}
        dropped = 0
        for l, d in k5.items():
            for key, procs in d.items():
                ws = k5wit[l][key]
                keep = [p for p, w in zip(procs, ws) if not (w.get("gflops", np.inf) < thr)]
                dropped += len(procs) - len(keep)
                if keep:
                    d2[l][key] = keep
        A2 = Arrays(d2, lat, langs, 0, rng)
        catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
        S = scores(A2, 0, MAIN, C_main, footprint)
        o = sorted(RANKED, key=lambda l: -S["MS"][langs.index(l)])
        out["sensitivity"] = {"dropped": dropped,
                              "rank_changes": {l: [res[l]["rank"], o.index(l) + 1] for l in RANKED
                                               if res[l]["rank"] != o.index(l) + 1}}
    return out


def replication(data, langs, footprint, C_main, k5_steady, rng, res, groups, order):
    m3, m3lat, _w, m3inv, m3recs = load_raw("v2_m3")
    if not m3:
        return {"status": "pas de données"}
    m3_sus = sanity(m3, BOUNDS_M3)
    lat3 = defaultdict(dict)
    for l in m3lat:
        if K8N in m3lat[l] and K8N in m3[l]:
            lat3[l][K8N] = m3lat[l][K8N]
    apply_steady(m3, lat3)
    # corrélation de rang par mesure, machine 1 contre machine 3
    per_key = {}
    keys = sorted({k for d in m3.values() for k in d})
    for key in keys:
        x, y, ls = [], [], []
        for l in langs:
            if key in data.get(l, {}) and key in m3.get(l, {}):
                x.append(float(np.median([np.median(p) for p in data[l][key]])))
                y.append(float(np.median([np.median(p) for p in m3[l][key]])))
                ls.append(l)
        rho, n = spearman(x, y)
        per_key[":".join(key)] = {"rho": rho, "n": n, "speed_ratio_median": float(np.median(np.array(x) / np.array(y))) if x else None}
    # classement v2 recalculé avec les seules données de la machine 3
    d3m = {l: dict(m3.get(l, {})) for l in langs}
    for l in langs:
        for key, procs in k5_steady.get(l, {}).items():
            d3m[l][key] = procs
    A3 = Arrays(d3m, lat3, langs, 0, rng)
    S = scores(A3, 0, MAIN, C_main, footprint)
    ms = {l: float(S["MS"][langs.index(l)]) for l in RANKED}
    complete = [l for l in RANKED if np.isfinite(ms[l])]
    o = sorted(complete, key=lambda l: -ms[l])
    r3 = {l: o.index(l) + 1 for l in o}
    rho, n = spearman([res[l]["rank"] for l in complete], [r3[l] for l in complete])
    # un langage change de groupe si son rang sur la machine 3 sort des rangs qu'occupe son groupe v2
    span = {}
    for members in groups:
        rs = [res[RANKED[j]]["rank"] for j in members]
        for j in members:
            span[RANKED[j]] = (min(rs), max(rs))
    changes = {l: {"group_span_v2": list(span[l]), "rank_m3": r3[l]} for l in complete
               if not span[l][0] <= r3[l] <= span[l][1]}
    return {"per_key": per_key, "ranking_m3": r3, "MS_m3": ms, "E_m3": {l: float(S["E"][langs.index(l)]) for l in RANKED},
            "D_m3": {l: float(S["D"][langs.index(l)]) for l in RANKED},
            "rho_ranking": rho, "n": n, "max_shift": max(abs(res[l]["rank"] - r3[l]) for l in complete) if complete else None,
            "group_changes": changes, "invalid": m3inv, "below_bound": m3_sus,
            "incomplete": [l for l in RANKED if l not in complete]}


def thp_table():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "raw_v2", "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") == "v2_thp":
                out[r["lang"]] = {"anon_huge_kb_max": r.get("anon_huge_kb_max"), "maxrss_kb": r.get("maxrss_kb"),
                                  "median_s": float(np.median([x["sec"] for x in r["reps"]])) if r.get("reps") else None}
    return out


# ------------------------------------------------------------------ rapport
NAMES = {"c": "C", "cpp": "C++", "csharp": "C#", "java": "Java", "zig": "Zig", "odin": "Odin", "julia": "Julia",
         "ada": "Ada", "fortran": "Fortran", "js": "JavaScript", "python": "Python", "haskell": "Haskell", "c3": "C3",
         "d": "D", "rust": "Rust", "chapel": "Chapel", "nim": "Nim", "mojo": "Mojo", "go": "Go", "ocaml": "OCaml",
         "lua": "Lua", "c_gcc": "C (gcc)", "fortran_flang": "Fortran (flang)", "luajit": "LuaJIT", "js_bun": "JS (Bun)",
         "python_ft": "Python (sans GIL)"}


def fr(x, d=1):
    return "—" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{d}f}".replace(".", ",")


def report(o):
    R = o["results"]
    L = []
    L.append("## Classement v2 (configuration principale)\n")
    L.append("| Groupe | Rang | Langage | MS [IC 95 %] | C | E [IC 95 %] | D [IC 95 %] | Ensemble simultané à 95 % | "
             "Rang, analyse globale [5–95 %] | P(1er) | P(3 premiers) | P(10 premiers) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for l in sorted(RANKED, key=lambda l: R[l]["rank"]):
        r = R[l]
        L.append(f"| {r['group']} | {r['rank']} | {NAMES[l]} | {fr(r['MS'])} [{fr(r['MS_ci'][0])}–{fr(r['MS_ci'][1])}] | "
                 f"{fr(r['C'])} | {fr(r['E'])} [{fr(r['E_ci'][0])}–{fr(r['E_ci'][1])}] | "
                 f"{fr(r['D'])} [{fr(r['D_ci'][0])}–{fr(r['D_ci'][1])}] | {r['rank_set'][0]}–{r['rank_set'][1]} | "
                 f"{fr(r['ua_rank_median'], 0)} [{r['ua_rank_90'][0]}–{r['ua_rank_90'][1]}] | "
                 f"{fr(100 * r['P1'], 0)} % | {fr(100 * r['P3'], 0)} % | {fr(100 * r['P10'], 0)} % |")
    L.append(f"\nValeur critique des ensembles simultanés : {fr(o['mogstad_crit'], 2)}.\n")
    L.append("Groupes (règle du plan : ensembles simultanés recouvrants, ou ordre établi dans moins de 90 % des tirages "
             "de l'analyse globale) : " + " ; ".join(f"{i + 1}. " + ", ".join(NAMES[l] for l in g)
                                                     for i, g in enumerate(o["groups"])) + ".\n")
    L.append("Groupes de mesure seule (ensembles simultanés recouvrants) : " + " ; ".join(
        f"{i + 1}. " + ", ".join(NAMES[l] for l in g) for i, g in enumerate(o["groups_meas"])) + ".\n")
    L.append("## Incertitude de mesure seule (configuration principale, bootstrap)\n")
    L.append("| Langage | Rang médian | Rang [5–95 %] | P(1er) | P(3 premiers) | P(10 premiers) |")
    L.append("|---|---|---|---|---|---|")
    for l in sorted(RANKED, key=lambda l: R[l]["rank"]):
        r = R[l]
        L.append(f"| {NAMES[l]} | {fr(r['boot_rank_median'], 0)} | {r['boot_rank_90'][0]}–{r['boot_rank_90'][1]} | "
                 f"{fr(100 * r['boot_P1'], 0)} % | {fr(100 * r['boot_P3'], 0)} % | {fr(100 * r['boot_P10'], 0)} % |")
    L.append("")
    L.append("## Décomposition : rang v2, puis un choix ramené à sa version v1\n")
    names = list(o["decomposition"])
    L.append("| Langage | " + " | ".join(names) + " |")
    L.append("|---|" + "---|" * len(names))
    for l in sorted(RANKED, key=lambda l: R[l]["rank"]):
        L.append(f"| {NAMES[l]} | " + " | ".join(str(o["decomposition"][n].get(l, "—")) for n in names) + " |")
    L.append("\n## Profils par principe (0–100, configuration principale)\n")
    pk = list(next(iter(o["profiles"].values())))
    L.append("| Langage | " + " | ".join(pk) + " |")
    L.append("|---|" + "---|" * len(pk))
    for l in sorted(o["profiles"], key=lambda l: R[l].get("rank", 99)):
        L.append(f"| {NAMES[l]} | " + " | ".join(fr(o['profiles'][l][k], 0) for k in pk) + " |")
    L.append(f"\nFront de Pareto sur (C, E, D) : {', '.join(NAMES[l] for l in o['pareto'])}.\n")
    L.append("Poids effectifs (R² de chaque pilier avec MS, puis part) : "
             + ", ".join(f"{k} {fr(v['R2'], 2)} ({fr(100 * v['part'], 0)} %)" for k, v in o["effective_weights"].items()) + ".\n")
    # langage et implémentation
    L.append("## Langage et implémentation\n")
    L.append("| Couple | C | E | D | MS | K4 | K5 | K8 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for pair, d in o["couples"].items():
        for x, v in d.items():
            if v:
                ek = v["E_kernels"]
                L.append(f"| {NAMES[x]} | {fr(v['C'])} | {fr(v['E'])} | {fr(v['D'])} | {fr(v['MS'])} | "
                         f"{fr(ek.get('k4'), 2)} | {fr(ek.get('k5'), 2)} | {fr(ek.get('k8'), 2)} |")
    L.append("\nK4 et K8 (score E du noyau) par backend :\n")
    for g, d in o["backend"].items():
        L.append(f"* {g} : " + ", ".join(f"{NAMES[l]} {fr(v['k4'], 2)} / {fr(v['k8'], 2)}" for l, v in d.items()))
    # régime établi, bimodalité
    cuts = o["steady_cuts"]
    byk = defaultdict(int)
    for c in cuts:
        byk[c["key"][0]] += 1
    L.append(f"\n## Régime établi et bimodalité\n\nProcessus coupés par la détection de rupture : {len(cuts)} "
             f"(par noyau : {', '.join(f'{k} {v}' for k, v in sorted(byk.items()))}). Mesures dont les médianes de "
             f"processus s'écartent de plus de 25 % : {len(o['bimodal'])}.\n")
    k5c = [c for c in cuts if c["key"][0] == "k5"]
    if k5c:
        L.append("Coupures sur K5 : " + "; ".join(f"{NAMES.get(c['lang'], c['lang'])} {c['key'][1]} processus {c['proc']} "
                                                  f"({fr(1e3 * c['before'], 2)} → {fr(1e3 * c['after'], 2)} ms après {c['cut']} répétitions)"
                                                  for c in k5c) + ".\n")
    # témoin
    w = o["witness"]
    if w.get("pooled"):
        L.append("## Témoin d'environnement (K5, machine 3)\n")
        L.append("Corrélation de rang entre le témoin et le temps du processus (rapporté à la médiane de sa mesure), "
                 "sur tous les processus : " + ", ".join(f"{k} {fr(v['rho'], 2)} (n = {v['n']})" for k, v in w["pooled"].items()) + ".\n")
        if w.get("witness_range"):
            L.append("Plage du témoin (min, médiane, max) : " + ", ".join(
                f"{k} {fr(a, 1)} / {fr(b, 1)} / {fr(c, 1)}" for k, (a, b, c) in w["witness_range"].items()) + ".\n")
        if w.get("sensitivity"):
            s = w["sensitivity"]
            ch = s["rank_changes"]
            L.append(f"Sans les processus du décile le plus lent du témoin ({s['dropped']} processus) : "
                     + ("aucun rang ne change." if not ch else ", ".join(f"{NAMES[l]} {a} → {b}" for l, (a, b) in ch.items()) + ".") + "\n")
    # réplication
    r = o["replication"]
    if r.get("per_key"):
        L.append("## Réplication sur la machine 3 (un processus par mesure)\n")
        L.append(f"Classement v2 recalculé avec les seules données de la machine 3 : corrélation de Spearman "
                 f"{fr(r['rho_ranking'], 2)} avec le classement v2 (n = {r['n']}), plus grand déplacement {r['max_shift']} rangs. "
                 + ("Langages qui sortent de leur groupe : " + ", ".join(
                     f"{NAMES[l]} (rang {v['rank_m3']}, groupe v2 aux rangs {v['group_span_v2'][0]}–{v['group_span_v2'][1]})"
                     for l, v in r["group_changes"].items()) + "." if r["group_changes"] else "Aucun langage ne sort de son groupe.") + "\n")
        L.append("| Langage | Rang v2 | Rang machine 3 | MS machine 3 |")
        L.append("|---|---|---|---|")
        for l in sorted(RANKED, key=lambda l: R[l]["rank"]):
            L.append(f"| {NAMES[l]} | {R[l]['rank']} | {r['ranking_m3'].get(l, '—')} | {fr(r['MS_m3'].get(l))} |")
        L.append("\n| Mesure | Spearman (machine 1 contre 3) | n | rapport des temps (1 / 3) |")
        L.append("|---|---|---|---|")
        for k, v in sorted(r["per_key"].items()):
            L.append(f"| {k} | {fr(v['rho'], 2)} | {v['n']} | {fr(v['speed_ratio_median'], 2)} |")
        L.append("")
    # pages géantes
    if o["thp"]:
        L.append("## Pages géantes (K1 natural, machine 3, politique madvise)\n")
        L.append("| Implémentation | AnonHugePages max (Mio) | pic RSS (Mio) |")
        L.append("|---|---|---|")
        for l, v in sorted(o["thp"].items(), key=lambda kv: -(kv[1]["anon_huge_kb_max"] or 0)):
            L.append(f"| {NAMES.get(l, l)} | {fr((v['anon_huge_kb_max'] or 0) / 1024, 0)} | {fr((v['maxrss_kb'] or 0) / 1024, 0)} |")
        L.append("")
    open(os.path.join(ROOT, "results", "report_v2.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
