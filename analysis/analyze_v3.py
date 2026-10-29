#!/usr/bin/env python3
"""Analyse v3 (plan pré-enregistré : docs/ANALYSIS_V3.md, poussé avant ce code et avant ses données nouvelles).

Changements par rapport à la v2 (analysis/analyze_v2.py, dont les chargements et le score sont repris) :
  * estimateur par cellule : moyenne des logarithmes des médianes de processus, sans coupure de régime établi ;
  * références fixes : frontière de E et de D1, références de D3 et de D4 calculées une fois, sur les estimations
    ponctuelles, et tenues fixes dans tous les tirages ;
  * bootstrap à résidus regroupés par noyau et par classe d'implémentation ;
  * étages (règle de la section 3), test bruit ou interaction pour la réplication (section 4), décomposition de la
    variance (section 5), expérience de disposition du code (section 6).
Sorties : results/summary_v3.json, results/report_v3.md.
Variables : BOOT (2000), UA (20000), NULLSIM (2000), PERM (2000).
"""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
from analyze_v2 import (E_V2, D1_V2, K1N, K1S, K8N, K2_SIZES, RANKED, ANNEX, ROOT, EBOUND, BOUNDS_M3, NAMES, fr,  # noqa: E402
                        c_cells, c_score, c_vector, ranks_of, spearman, dirichlet, lat_rows, steady, CATEGORIES)

B = int(os.environ.get("BOOT", "2000"))
U = int(os.environ.get("UA", "20000"))
NS = int(os.environ.get("NULLSIM", "2000"))
NPERM = int(os.environ.get("PERM", "2000"))
SEED = 20261029 + 3
NR = len(RANKED)
WEIGHTS = {"C": 0.35, "E": 0.40, "D": 0.25}
DW = {"D1": 0.5, "D2": 0.15, "D3": 0.15, "D4": 0.2}
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}
INTERP = {"python", "python_ft", "lua"}


def klass(l):
    return "interp" if l in INTERP else ("jit" if l in JIT else "aot")


def needed_keys(e_meas=E_V2, d1_meas=D1_V2):
    keys = set()
    for ms in e_meas.values():
        for ks in ms:
            keys.update(ks)
    for lst in d1_meas.values():
        for _, ks in lst:
            keys.update(ks)
    keys.update([K1N, K1S] + [("k2", "tuned", s) for s in K2_SIZES])
    return keys


def proc_logs(procs):
    return np.log(np.array([np.median(p) for p in procs], float))


def build_pools(data, langs, keys):
    """Réservoirs de résidus par (noyau, classe), fusionnés avec le noyau s'ils ont moins de 20 résidus."""
    pools, kpool = defaultdict(list), defaultdict(list)
    for l in langs:
        for key in keys:
            procs = data.get(l, {}).get(key)
            if not procs or len(procs) < 2:
                continue
            y = proc_logs(procs)
            P = len(y)
            r = (y - y.mean()) * math.sqrt(P / (P - 1))
            pools[(key[0], klass(l))].extend(r.tolist())
            kpool[key[0]].extend(r.tolist())
    out = {}
    for k in kpool:
        for c in ("aot", "jit", "interp"):
            pl = pools.get((k, c), [])
            out[(k, c)] = np.array(pl if len(pl) >= 20 else kpool[k], float)
    return out


class Arrays3:
    """Temps simulés par cellule : ligne 0 = estimation ponctuelle, lignes 1..nb = tirages à résidus regroupés.
    Deux estimateurs : 'mean' (moyenne des logarithmes des médianes de processus) et 'min' (minimum des médianes)."""

    def __init__(self, data, lat, langs, nb, rng, pools, e_meas=E_V2, d1_meas=D1_V2, shift=None):
        self.langs, self.nb, self.e_meas, self.d1_meas = langs, nb, e_meas, d1_meas
        self.idx = {l: i for i, l in enumerate(langs)}
        self.ranked = np.array([self.idx[l] for l in RANKED if l in self.idx])
        self.t, self.P = {}, {}
        for key in sorted(needed_keys(e_meas, d1_meas)):
            mean = np.full((nb + 1, len(langs)), np.nan)
            mn = np.full((nb + 1, len(langs)), np.nan)
            for l in langs:
                procs = data.get(l, {}).get(key)
                if not procs:
                    continue
                y = proc_logs(procs)
                j = self.idx[l]
                mean[0, j], mn[0, j] = math.exp(y.mean()), math.exp(y.min())
                self.P[(l, key)] = len(y)
                if nb:
                    pool = pools[(key[0], klass(l))]
                    draws = y.mean() + pool[rng.integers(0, len(pool), size=(nb, len(y)))]
                    mean[1:, j], mn[1:, j] = np.exp(draws.mean(axis=1)), np.exp(draws.min(axis=1))
            self.t[("mean", key)], self.t[("min", key)] = mean, mn
        self.lat = np.full((nb + 1, len(langs), 3), np.nan)
        for l in langs:
            lp = lat.get(l, {}).get(K8N)
            if lp and any(len(p) for p in lp):
                self.lat[:, self.idx[l], :] = lat_rows(lp, nb, rng)

    def best(self, est, keys, r):
        arr = np.vstack([self.t[(est, k)][r] for k in keys])
        with np.errstate(all="ignore"):
            out = np.nanmin(np.where(np.isnan(arr), np.inf, arr), axis=0)
        out[np.isinf(out)] = np.nan
        return out


MAIN = {"est": "mean", "enorm": "frontier", "d3": "abs", "d4": "best", "d1ref": "tstar", "agg": "arith", "crule": "v2"}


def references(A, est):
    """Références fixes, calculées sur la ligne 0 (estimations ponctuelles)."""
    rk = A.ranked
    ref = {"tstar": {}, "nat": {}, "k2_best": {}, "k2_c": {}}
    with np.errstate(all="ignore"):
        for k, ms in A.e_meas.items():
            for i, ks in enumerate(ms):
                ref["tstar"][(k, i)] = float(np.nanmin(A.best(est, ks, 0)[rk]))
        for k, lst in A.d1_meas.items():
            for i, ks in lst:
                ref["nat"][(k, i)] = float(np.nanmin(A.best(est, ks, 0)[rk]))
        for s in K2_SIZES:
            t = A.t[(est, ("k2", "tuned", s))][0]
            ref["k2_best"][s] = float(np.nanmin(t[rk]))
            ref["k2_c"][s] = float(t[A.idx["c"]])
        p50, p999, mx = A.lat[0, :, 0], A.lat[0, :, 1], A.lat[0, :, 2]
        ref["d3_abs"] = (float(np.nanmin(p999[rk])), float(np.nanmin(mx[rk])))
        ref["d3_rel"] = (float(np.nanmin((p999 / p50)[rk])), float(np.nanmin((mx / p50)[rk])))
    return ref


def scores3(A, r, cfg, C, footprint, refs, wE=None, wD=None, wP=None):
    est = cfg["est"]
    ref = refs[est]
    kernels = list(A.e_meas)
    wE = wE or {k: 1 / len(kernels) for k in kernels}
    wD, wP = wD or DW, wP or WEIGHTS
    n = len(A.langs)
    lnE, ek = np.zeros(n), {}
    with np.errstate(all="ignore"):
        for k, ms in A.e_meas.items():
            lr = []
            for i, ks in enumerate(ms):
                t = A.best(est, ks, r)
                if cfg["enorm"] == "bounds" and (k, i) in EBOUND:
                    lr.append(np.log(np.minimum(1.0, EBOUND[(k, i)] / t)))
                else:
                    lr.append(np.log(ref["tstar"][(k, i)] / t))
            ek[k] = np.mean(lr, axis=0)
            lnE += wE[k] * ek[k]
        E = 100 * np.exp(lnE)
        d1k = []
        for k, lst in A.d1_meas.items():
            lr = []
            for i, ks in lst:
                t = A.best(est, ks, r)
                lr.append(np.log((ref["tstar"][(k, i)] if cfg["d1ref"] == "tstar" else ref["nat"][(k, i)]) / t))
            d1k.append(np.mean(lr, axis=0))
        D1 = np.exp(np.mean(d1k, axis=0))
        a = np.array([min(1.0, 64.0 / footprint[l]) if footprint.get(l) else np.nan for l in A.langs])
        bb = np.minimum(1.0, A.t[(est, K1N)][r] / A.t[(est, K1S)][r])
        D2 = np.where(np.isnan(a), bb, np.sqrt(a * bb))
        p50, p999, mx = A.lat[r, :, 0], A.lat[r, :, 1], A.lat[r, :, 2]
        if cfg["d3"] == "abs":
            D3 = np.sqrt((ref["d3_abs"][0] / p999) * (ref["d3_abs"][1] / mx))
        else:
            D3 = np.sqrt((ref["d3_rel"][0] / (p999 / p50)) * (ref["d3_rel"][1] / (mx / p50)))
        l4 = []
        for s in K2_SIZES:
            t = A.t[(est, ("k2", "tuned", s))][r]
            refv = ref["k2_best"][s] if cfg["d4"] == "best" else ref["k2_c"][s]
            l4.append(np.log(np.minimum(1.0, refv / t)))
        D4 = np.exp(np.mean(l4, axis=0))
        D = 100 * (wD["D1"] * D1 + wD["D2"] * D2 + wD["D3"] * D3 + wD["D4"] * D4)
        if cfg["agg"] == "arith":
            MS = wP["C"] * C + wP["E"] * E + wP["D"] * D
        else:
            MS = np.exp(wP["C"] * np.log(C) + wP["E"] * np.log(E) + wP["D"] * np.log(D))
    return {"E": E, "D": D, "MS": MS, "D1": D1, "D2": D2, "D3": D3, "D4": D4, "Ek": {k: np.exp(v) for k, v in ek.items()}}


def own_gap(A, est, i):
    """Écart du langage à son propre meilleur code : moyenne géométrique de t_meilleur / t_naturel (mesures de D1)."""
    lr = []
    for k, lst in A.d1_meas.items():
        for j, ks in lst:
            tb = A.best(est, A.e_meas[k][j], 0)[i]
            tn = A.best(est, ks, 0)[i]
            lr.append(math.log(min(1.0, tb / tn)) if np.isfinite(tb) and np.isfinite(tn) else np.nan)
    return float(math.exp(np.mean(lr))) if lr and all(np.isfinite(lr)) else None


def bound_share(A, est, i):
    """Part de la borne physique : moyenne géométrique de min(1, borne / t) sur les mesures qui en ont une."""
    lr = []
    for (k, j), b in EBOUND.items():
        t = A.best(est, A.e_meas[k][j], 0)[i]
        if not np.isfinite(t):
            return None
        lr.append(math.log(min(1.0, b / t)))
    return float(math.exp(np.mean(lr)))


def classify_processes(data):
    """Classement descriptif des processus (Barrett et al.) avec le critère de rupture de la v2."""
    out = defaultdict(lambda: defaultdict(int))
    for l, d in data.items():
        for key, procs in d.items():
            for p in procs:
                s = steady(p) if len(p) >= 6 else None
                c = "plat" if s is None else ("accélération" if s[2] < s[1] else "ralentissement")
                out[klass(l)][c] += 1
    return {k: dict(v) for k, v in out.items()}


def load_m3():
    m3, m3lat, _w, _inv, _recs = v2.load_raw("v2_m3")
    sus = v2.sanity(m3, BOUNDS_M3)
    lat3 = defaultdict(dict)
    for l in m3lat:
        if K8N in m3lat[l] and K8N in m3[l]:
            lat3[l][K8N] = m3lat[l][K8N]
    return m3, lat3, sus


def rank_dict(ms, langs):
    o = sorted([l for l in RANKED if l in langs and np.isfinite(ms[langs.index(l)])], key=lambda l: -ms[langs.index(l)])
    return {l: o.index(l) + 1 for l in o}


def agreement(r1, r2, top_order):
    """Spearman sur tous, sur les 13 et les 9 premiers de top_order ; paires inversées parmi les 13 premiers."""
    def sp(ls):
        rho, _ = spearman([r1[l] for l in ls], [r2[l] for l in ls])
        return rho
    t13, t9 = top_order[:13], top_order[:9]
    inv13 = sum(1 for i, a in enumerate(t13) for b in t13[i + 1:] if (r1[a] - r1[b]) * (r2[a] - r2[b]) < 0)
    return {"rho21": sp(top_order), "rho13": sp(t13), "rho9": sp(t9), "inv13": inv13}


# Tâches de l'expérience de disposition pendant lesquelles j'ai fait tourner un calcul de plus de 30 s (nice 19, sur
# un autre cœur) : deux calculs de cette analyse (16:01–16:07, tâches 4 à 9) et analysis/verify_audit2.py
# (16:14:50–16:15:25, tâches 17 et 18). Numéros dans la liste tirée par tools/layout_v3.py, à partir de 1.
LAYOUT_PERTURBED_JOBS = [4, 5, 6, 7, 8, 9, 17, 18]


def tiers_of(order, rank3, prec):
    """Section 3 : frontière entre i et i + 1 si aucune paire de part et d'autre n'est inversée sur la machine 3 et si
    chaque paire est ordonnée dans le même sens dans au moins 95 % des tirages de l'analyse globale."""
    boundaries = []
    for i in range(1, len(order)):
        above, below = order[:i], order[i:]
        no_inv = all(rank3[a] < rank3[b] for a in above for b in below)
        ua_ok = all(prec[RANKED.index(a), RANKED.index(b)] >= 0.95 for a in above for b in below)
        if no_inv and ua_ok:
            boundaries.append(i)
    tiers, start = [], 0
    for bnd in boundaries + [len(order)]:
        tiers.append(sorted(order[start:bnd], key=lambda l: NAMES[l]))
        start = bnd
    return tiers, boundaries


def layout_jobs():
    """Liste des tâches (implémentation, graine, processus) dans l'ordre tiré par tools/layout_v3.py."""
    import random
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import layout_v3
    jobs = [(impl, s, p) for impl in layout_v3.IMPLS for s in layout_v3.SEEDS for p in range(2)]
    random.Random(20261029 + 300).shuffle(jobs)
    return jobs


def f_stat(groups):
    n, k = sum(len(g) for g in groups), len(groups)
    grand = np.mean(np.concatenate(groups))
    msb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups) / (k - 1)
    msw = sum(((g - g.mean()) ** 2).sum() for g in groups) / (n - k)
    return msb, msw


def layout_analysis(exclude=(), perm=0, rng=None):
    """Section 6 : variance entre dispositions et entre processus d'une même disposition, par mesure.
    exclude : tâches (implémentation, graine, processus) écartées. perm > 0 : valeur p d'un test par permutation des
    graines (hors plan)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "raw_v3", "layout_*.jsonl"))):
        impl = os.path.basename(f)[len("layout_"):-len(".jsonl")]
        cells = defaultdict(lambda: defaultdict(list))
        for line in open(f):
            r = json.loads(line)
            reps = r.get("reps", [])
            if r.get("tag") != "v3_layout" or not reps or r.get("returncode") != 0 or any(x["ok"] is not True for x in reps):
                continue
            if "layout_seed" not in r.get("meta", {}):  # processus en cours d'écriture par l'outil de mesure
                continue
            if (impl, r["meta"]["layout_seed"], r.get("layout_proc")) in exclude:
                continue
            cells[":".join((r["kernel"], r["variant"], r["param"]))][r["meta"]["layout_seed"]].append(
                math.log(float(np.median([x["sec"] for x in reps]))))
        res = {}
        for key, by in cells.items():
            groups = [np.array(v) for v in by.values() if len(v) >= 1]
            n = sum(len(g) for g in groups)
            k = len(groups)
            if k < 2 or n - k < 1:
                continue
            msb, msw = f_stat(groups)
            n0 = (n - sum(len(g) ** 2 for g in groups) / n) / (k - 1)
            s2l = max(0.0, (msb - msw) / n0)
            means = [math.exp(g.mean()) for g in groups]
            res[key] = {"seeds": k, "n": n, "sd_layout": math.sqrt(s2l), "sd_proc": math.sqrt(msw),
                        "F": msb / msw if msw > 0 else None, "max_min": max(means) / min(means)}
            if perm and msw > 0:
                v, sizes = np.concatenate(groups), [len(g) for g in groups]
                cuts = np.cumsum(sizes)[:-1]
                hits = 0
                for _ in range(perm):
                    pm, pw = f_stat(np.split(rng.permutation(v), cuts))
                    hits += pw > 0 and pm / pw >= msb / msw - 1e-12
                res[key]["p_perm"] = (hits + 1) / (perm + 1)
        out[impl] = res
    return out


def main():
    rng = np.random.default_rng(SEED)
    data, lat, invalid, sus, bridge, v1_k5, (k5, k5wit, k5inv, k5_sus, k5recs) = v2.dataset_main()
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    keys = needed_keys()
    pools = build_pools(data, langs, keys)

    # ---------------- configuration principale : références fixes, résidus regroupés
    A = Arrays3(data, lat, langs, B, rng, pools)
    refs = {e: references(A, e) for e in ("mean", "min")}
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    C_main = c_vector(c_score(c_cells("v2", c3), catw0), langs)
    C_v1 = c_vector(c_score(c_cells("v1", c3), catw0), langs)
    S0 = scores3(A, 0, MAIN, C_main, footprint, refs)
    rk = A.ranked
    ms_boot, e_boot, d_boot = np.empty((B, NR)), np.empty((B, len(langs))), np.empty((B, len(langs)))
    comp_boot = {k: np.empty((B, len(langs))) for k in ("D1", "D2", "D3", "D4")}
    for b in range(1, B + 1):
        S = scores3(A, b, MAIN, C_main, footprint, refs)
        ms_boot[b - 1], e_boot[b - 1], d_boot[b - 1] = S["MS"][rk], S["E"], S["D"]
        for k in comp_boot:
            comp_boot[k][b - 1] = S[k]
    ms0 = S0["MS"][rk]
    order = list(np.argsort(-ms0, kind="stable"))
    main_rank = {RANKED[j]: order.index(j) + 1 for j in range(NR)}

    # Mogstad, Romano, Shaikh et Wilhelm (2024), sur ce bootstrap
    dhat = ms0[:, None] - ms0[None, :]
    dstar = ms_boot[:, :, None] - ms_boot[:, None, :]
    sig = dstar.std(axis=0, ddof=1)
    np.fill_diagonal(sig, np.inf)
    crit = float(np.quantile(np.nanmax(np.abs(dstar - dhat[None]) / sig[None], axis=(1, 2)), 0.95))
    ahead = (dhat - crit * sig) > 0
    rset = [(1 + int(ahead[:, j].sum()), NR - int(ahead[j, :].sum())) for j in range(NR)]

    # ---------------- analyse globale (mêmes options et poids que la v2)
    opts = {"est": ["mean", "min"], "enorm": ["frontier", "bounds"], "d3": ["abs", "rel"], "d4": ["best", "c"],
            "d1ref": ["tstar", "best_natural"], "agg": ["arith", "geo"], "crule": ["v2", "v1"]}
    kernels, cat_names = list(E_V2), list(CATEGORIES)
    prec = np.zeros((NR, NR))
    prec_q = {"E": np.zeros((NR, NR)), "D1": np.zeros((NR, NR))}
    ua_ranks = np.empty((U, NR), int)
    for u in range(U):
        cfg = {k: v[int(rng.integers(len(v)))] for k, v in opts.items()}
        b = int(rng.integers(1, B + 1))
        wp = dirichlet(rng, 20 * np.array([0.35, 0.40, 0.25])) if rng.random() < 0.5 else dirichlet(rng, [1, 1, 1])
        wP = {"C": wp[0], "E": wp[1], "D": wp[2]}
        wE = dict(zip(kernels, dirichlet(rng, 20 * np.full(len(kernels), 1 / len(kernels)))))
        wD = dict(zip(("D1", "D2", "D3", "D4"), dirichlet(rng, 20 * np.array([DW[k] for k in ("D1", "D2", "D3", "D4")]))))
        catw = dict(zip(cat_names, dirichlet(rng, 20 * np.array([catw0[c] for c in cat_names]))))
        prng = np.random.default_rng(int(rng.integers(2 ** 63)))
        C = c_vector(c_score(c_cells(cfg["crule"], c3, rng=prng, noise=0.10), catw), langs)
        S_u = scores3(A, b, cfg, C, footprint, refs, wE=wE, wD=wD, wP=wP)
        r_ = ranks_of(S_u["MS"][rk])
        ua_ranks[u] = r_
        prec += r_[:, None] < r_[None, :]
        for q in prec_q:
            rq = ranks_of(S_u[q][rk])
            prec_q[q] += rq[:, None] < rq[None, :]
    prec /= U
    for q in prec_q:
        prec_q[q] /= U

    # ---------------- réplication (machine 3) avec l'inférence v3
    m3, lat3, m3_sus = load_m3()
    d3m = {l: dict(m3.get(l, {})) for l in langs}
    for l in langs:
        for key, procs in k5.get(l, {}).items():
            d3m[l][key] = procs
    A3 = Arrays3(d3m, lat3, langs, 0, rng, pools)
    refs3 = {e: references(A3, e) for e in ("mean", "min")}
    S3 = scores3(A3, 0, MAIN, C_main, footprint, refs3)
    m3_rank = rank_dict(list(S3["MS"]), langs)
    main_order = [RANKED[j] for j in order]
    obs_agree = agreement(main_rank, m3_rank, main_order)

    # ---------------- étages (section 3 du plan)
    tiers, boundaries = tiers_of(main_order, m3_rank, prec)

    # ---------------- test bruit ou interaction (section 4)
    mu = {}
    for l in langs:
        for key in keys:
            procs = data.get(l, {}).get(key)
            if procs and key[0] != "k5":
                mu[(l, key)] = float(proc_logs(procs).mean())
    shift = {}
    for key in keys:
        if key[0] == "k5":
            continue
        diffs = [float(proc_logs(m3[l][key]).mean()) - mu[(l, key)] for l in langs
                 if (l, key) in mu and key in m3.get(l, {})]
        shift[key] = float(np.median(diffs)) if diffs else 0.0
    null, null_infl = [], {1.5: [], 2.0: []}
    for s in range(NS):
        d1s, d3s = defaultdict(dict), defaultdict(dict)
        for (l, key), m in mu.items():
            pool = pools[(key[0], klass(l))]
            P = len(data[l][key])
            d1s[l][key] = [[math.exp(m + pool[rng.integers(len(pool))])] for _ in range(P)]
            if key in m3.get(l, {}):
                d3s[l][key] = [[math.exp(m + shift[key] + pool[rng.integers(len(pool))])]]
        for l in langs:
            for key, procs in k5.get(l, {}).items():
                d1s[l][key] = procs
                d3s[l][key] = procs
        Asim1 = Arrays3(d1s, lat, langs, 0, rng, pools)
        Asim3 = Arrays3(d3s, lat, langs, 0, rng, pools)
        r1 = rank_dict(list(scores3(Asim1, 0, MAIN, C_main, footprint, {"mean": references(Asim1, "mean")})["MS"]), langs)
        r3 = rank_dict(list(scores3(Asim3, 0, MAIN, C_main, footprint, {"mean": references(Asim3, "mean")})["MS"]), langs)
        o1 = sorted(r1, key=r1.get)
        if len(r1) == NR and len(r3) == NR:
            null.append(agreement(r1, r3, o1))
        # hors plan, ajouté avant le calcul : bruit de la machine 3 multiplié par 1,5 et 2 (un seul processus, hôte
        # possiblement plus bruyant que la machine 1), sur un quart des simulations
        if s % 4 == 0:
            for f in null_infl:
                d3i = defaultdict(dict)
                for (l, key), m in mu.items():
                    if key in m3.get(l, {}):
                        pool = pools[(key[0], klass(l))]
                        d3i[l][key] = [[math.exp(m + shift[key] + f * pool[rng.integers(len(pool))])]]
                for l in langs:
                    for key, procs in k5.get(l, {}).items():
                        d3i[l][key] = procs
                Ai = Arrays3(d3i, lat, langs, 0, rng, pools)
                ri = rank_dict(list(scores3(Ai, 0, MAIN, C_main, footprint, {"mean": references(Ai, "mean")})["MS"]), langs)
                if len(ri) == NR and len(r1) == NR:
                    null_infl[f].append(agreement(r1, ri, o1))
    def summarize(sims):
        out_ = {}
        for stat in ("rho21", "rho13", "rho9", "inv13"):
            vals = np.array([x[stat] for x in sims], float)
            p = float((vals >= obs_agree[stat]).mean()) if stat == "inv13" else float((vals <= obs_agree[stat]).mean())
            out_[stat] = {"observed": obs_agree[stat], "null_median": float(np.median(vals)),
                          "null_5_95": [float(np.quantile(vals, 0.05)), float(np.quantile(vals, 0.95))], "p": p}
        return out_
    nullsum = summarize(null)
    nullsum_infl = {str(f): summarize(v) for f, v in null_infl.items() if v}

    # ---------------- décomposition de la variance (section 5)
    vdec, vdec13 = {}, {}
    top13 = [RANKED[j] for j in order][:13]
    for key, subset, target in [(k, None, vdec) for k in sorted(keys)] + [(k, top13, vdec13) for k in sorted(keys)]:
        if key[0] == "k5":
            continue
        ls = [l for l in (subset or langs) if (l, key) in mu and key in m3.get(l, {})]
        if len(ls) < 5:
            continue
        y1 = np.array([mu[(l, key)] for l in ls])
        y3 = np.array([float(proc_logs(m3[l][key]).mean()) for l in ls]) - shift[key]
        p1 = np.array([len(data[l][key]) for l in ls], float)
        s2 = float(np.mean([pools[(key[0], klass(l))].var() for l in ls]))
        dvar = float(np.var(y3 - y1, ddof=1))
        noise_d = s2 * float(np.mean(1 + 1 / p1))
        inter = max(0.0, (dvar - noise_d) / 4)
        avg = (y1 + y3) / 2
        lang = max(0.0, float(np.var(avg, ddof=1)) - s2 * float(np.mean((1 + 1 / p1) / 4)) - inter)
        tot = lang + inter + s2
        target[":".join(key)] = {"n": len(ls), "langage": lang / tot, "interaction": inter / tot, "processus": s2 / tot}

    # ---------------- résultats par langage : trois quantités, intervalles, positions
    res = {}
    for i, l in enumerate(langs):
        lo, hi = float(np.nanquantile(e_boot[:, i], 0.025)), float(np.nanquantile(e_boot[:, i], 0.975))
        d1lo, d1hi = float(np.nanquantile(comp_boot["D1"][:, i], 0.025)), float(np.nanquantile(comp_boot["D1"][:, i], 0.975))
        res[l] = {"C_v2": float(C_main[i]), "C_v1": float(C_v1[i]), "E": float(S0["E"][i]), "E_ci": [lo, hi],
                  "D1_ci": [100 * d1lo, 100 * d1hi],
                  "D": float(S0["D"][i]), "MS": float(S0["MS"][i]),
                  "D_parts": {k: float(S0[k][i]) for k in ("D1", "D2", "D3", "D4")},
                  "E_kernels": {k: float(v[i]) for k, v in S0["Ek"].items()},
                  "own_gap": own_gap(A, "mean", i), "bound_share": bound_share(A, "mean", i),
                  "E_m3": float(S3["E"][i]), "D1_m3": float(S3["D1"][i]), "MS_m3": float(S3["MS"][i]),
                  "E_kernels_m3": {k: float(v[i]) for k, v in S3["Ek"].items()}}
    for j, l in enumerate(RANKED):
        rr = res[l]
        x = ms_boot[:, j]
        lo, hi = float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))
        rr["MS_ci"] = [lo, hi]
        rr["ci_position"] = (rr["MS"] - lo) / (hi - lo) if hi > lo else None
        rr["rank_main"] = main_rank[l]
        rr["rank_m3"] = m3_rank.get(l)
        rr["rank_set"] = list(rset[j])
        ur = ua_ranks[:, j]
        rr["ua_rank_median"] = float(np.median(ur))
        rr["ua_rank_90"] = [int(np.quantile(ur, 0.05)), int(np.quantile(ur, 0.95))]
        rr["P1"], rr["P3"] = float((ur == 1).mean()), float((ur <= 3).mean())
        rr["tier"] = next(t for t, members in enumerate(tiers) if l in members) + 1

    # ---------------- hors plan, ajouté après le premier calcul (tout ce qui suit ne consomme plus l'aléa du plan)
    # position dans l'IC par composante, pour localiser l'asymétrie de MS
    ri = [A.idx[l] for l in RANKED]
    comp_pos = {}
    for k, (x0, xb) in [("E", (S0["E"], e_boot)), ("D", (S0["D"], d_boot))] + [(k, (S0[k], comp_boot[k])) for k in comp_boot]:
        ps = []
        for i in ri:
            lo_, hi_ = np.nanquantile(xb[:, i], 0.025), np.nanquantile(xb[:, i], 0.975)
            ps.append(float((x0[i] - lo_) / (hi_ - lo_)) if hi_ - lo_ > 1e-12 else np.nan)
        comp_pos[k] = {"mean": float(np.nanmean(ps)), "c": ps[RANKED.index("c")], "min": float(np.nanmin(ps)),
                       "max": float(np.nanmax(ps)), "n": int(np.sum(np.isfinite(ps)))}
    # étages par quantité mesurée (E, D1), même règle, précédences tirées des mêmes 20 000 tirages
    tiers_q = {}
    for q in ("E", "D1"):
        oq = sorted(RANKED, key=lambda l: -S0[q][A.idx[l]])
        tq, _bq = tiers_of(oq, rank_dict(list(S3[q]), langs), prec_q[q])
        tiers_q[q] = {"order": oq, "tiers": tq, "rank_m3": rank_dict(list(S3[q]), langs),
                      "precedence": {a: {b: float(prec_q[q][RANKED.index(a), RANKED.index(b)]) for b in RANKED} for a in RANKED}}
    # rangs compatibles avec les paires établies, paire par paire, avec le critère des étages : b est établi devant a
    # si b précède a dans au moins 95 % des tirages et sur la machine 3
    def established_ranks(pm, rank3):
        ix = {l: RANKED.index(l) for l in RANKED}
        return {a: [1 + sum(1 for b in RANKED if b != a and pm[ix[b], ix[a]] >= 0.95 and rank3[b] < rank3[a]),
                    NR - sum(1 for b in RANKED if b != a and pm[ix[a], ix[b]] >= 0.95 and rank3[a] < rank3[b])]
                for a in RANKED}
    est_ranks = {"MS": established_ranks(prec, m3_rank)}
    for q in ("E", "D1"):
        est_ranks[q] = established_ranks(prec_q[q], tiers_q[q]["rank_m3"])
    # accord entre machines sans K3, le noyau où la décomposition attribue l'écart au placement du code
    def ms_drop(S, drop):
        E_ = 100 * np.exp(np.mean([np.log(v) for k, v in S["Ek"].items() if k not in drop], axis=0))
        return E_, WEIGHTS["C"] * C_main + WEIGHTS["E"] * E_ + WEIGHTS["D"] * S["D"]
    without_k3 = {}
    for name, drop in (("tous les noyaux", ()), ("sans K3", ("k3",))):
        E1_, M1_ = ms_drop(S0, drop)
        E3_, M3_ = ms_drop(S3, drop)
        r1_, r3_ = rank_dict(list(M1_), langs), rank_dict(list(M3_), langs)
        e1_, e3_ = rank_dict(list(E1_), langs), rank_dict(list(E3_), langs)
        without_k3[name] = {"MS": agreement(r1_, r3_, sorted(r1_, key=r1_.get)),
                            "E": agreement(e1_, e3_, sorted(e1_, key=e1_.get)),
                            "rank_m1": r1_, "rank_m3": r3_}
    # Cascade Lake seul : K5 d'avant (machines 1 et 2, même modèle) à la place de K5 de la machine 3
    dcl = {l: {k: v for k, v in data.get(l, {}).items() if k[0] != "k5"} for l in langs}
    for l in langs:
        for key, procs in v1_k5.get(l, {}).items():
            dcl[l][key] = procs
    Acl = Arrays3(dcl, lat, langs, 0, rng, pools)
    Scl = scores3(Acl, 0, MAIN, C_main, footprint, {e: references(Acl, e) for e in ("mean", "min")})
    cascade = {"rank": rank_dict(list(Scl["MS"]), langs),
               "E": {l: float(Scl["E"][A.idx[l]]) for l in RANKED}, "D1": {l: float(100 * Scl["D1"][A.idx[l]]) for l in RANKED},
               "MS": {l: float(Scl["MS"][A.idx[l]]) for l in RANKED}}
    # disposition : test par permutation, et sensibilité sans les tâches perturbées par mes calculs
    jobs = layout_jobs()
    perturbed = {jobs[j - 1] for j in LAYOUT_PERTURBED_JOBS}
    lrng = np.random.default_rng(SEED + 6)
    layout = layout_analysis(perm=NPERM, rng=lrng)
    layout_clean = layout_analysis(exclude=perturbed)

    # sensibilité : médiane des médianes de processus (estimateur de la v2), mêmes données, références fixes
    data_med = {l: d for l, d in data.items()}
    Amed = v2.Arrays(data_med, lat, langs, 0, rng)
    Smed = v2.scores(Amed, 0, v2.MAIN, C_main, footprint)
    med_rank = rank_dict(list(Smed["MS"]), langs)

    out = {"config": MAIN, "B": B, "U": U, "NULLSIM": NS, "results": res, "tiers": tiers, "boundaries": boundaries,
           "main_order": main_order, "mogstad_crit": crit,
           "precedence": {RANKED[j]: {RANKED[k]: float(prec[j, k]) for k in range(NR)} for j in range(NR)},
           "replication": {"rank_m3": m3_rank, "agreement": obs_agree, "null": nullsum, "null_inflated": nullsum_infl,
                           "below_bound": m3_sus},
           "variance_decomposition": vdec, "variance_decomposition_top13": vdec13, "layout": layout,
           "layout_without_perturbed": layout_clean, "layout_perturbed_jobs": sorted(map(list, perturbed)),
           "ci_position_components": comp_pos, "tiers_by_quantity": tiers_q, "cascade_lake_only": cascade,
           "established_ranks": est_ranks, "agreement_without_k3": without_k3,
           "process_classes": classify_processes(data), "pools_sd": {f"{k}:{c}": float(v.std()) for (k, c), v in pools.items()},
           "rank_median_of_medians": med_rank,
           "ci_position_mean": float(np.mean([res[l]["ci_position"] for l in RANKED]))}
    json.dump(out, open(os.path.join(ROOT, "results", "summary_v3.json"), "w"), indent=1, default=str)
    report(out)


def report(o):
    R = o["results"]
    L = ["## Étages v3 (règle du plan : pas d'inversion sur la machine 3, ordre établi dans 95 % des tirages)\n"]
    for t, members in enumerate(o["tiers"]):
        L.append(f"{t + 1}. " + ", ".join(NAMES[l] for l in members))
    L.append("\n## Trois quantités, par langage (machine 1, sauf K5 sur la machine 3)\n")
    L.append("| Étage | Langage | Plafond E [IC 95 %] | E machine 3 | Part de la borne | Code naturel D1 | D1 machine 3 | "
             "Écart à son meilleur code | Contrôle C (v2 / v1) | MS [IC 95 %] | Position dans l'IC | Ensemble simultané | "
             "Rang global [5–95 %] | Rang machine 3 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for l in sorted(RANKED, key=lambda l: (R[l]["tier"], NAMES[l])):
        r = R[l]
        L.append(f"| {r['tier']} | {NAMES[l]} | {fr(r['E'])} [{fr(r['E_ci'][0])}–{fr(r['E_ci'][1])}] | {fr(r['E_m3'])} | "
                 f"{fr(100 * r['bound_share'], 0) if r['bound_share'] else '—'} % | {fr(100 * r['D_parts']['D1'])} | "
                 f"{fr(100 * r['D1_m3'])} | "
                 f"{fr(100 * r['own_gap'], 0) if r['own_gap'] else '—'} % | {fr(r['C_v2'])} / {fr(r['C_v1'])} | "
                 f"{fr(r['MS'])} [{fr(r['MS_ci'][0])}–{fr(r['MS_ci'][1])}] | {fr(r['ci_position'], 2)} | "
                 f"{r['rank_set'][0]}–{r['rank_set'][1]} | {fr(r['ua_rank_median'], 0)} [{r['ua_rank_90'][0]}–{r['ua_rank_90'][1]}] | "
                 f"{r['rank_m3']} |")
    L.append(f"\nPosition moyenne des estimations dans leur intervalle : {fr(o['ci_position_mean'], 2)} (0,78 en v2).")
    L.append("\nHors plan, par composante (moyenne sur les 21 langages ; C ; extrêmes) : " + " ; ".join(
        f"{k} {fr(v['mean'], 2)} (C {fr(v['c'], 2)} ; {fr(v['min'], 2)} à {fr(v['max'], 2)}"
        + (f", {v['n']} langages à intervalle non nul)" if v['n'] < len(RANKED) else ")")
        for k, v in o["ci_position_components"].items()) + ".\n")
    L.append("## Hors plan : étages par quantité mesurée (même règle ; précédences tirées des mêmes 20 000 tirages)\n")
    for q, lab_ in (("E", "plafond E"), ("D1", "code naturel D1")):
        d = o["tiers_by_quantity"][q]
        L.append(f"* {lab_} : " + " > ".join("{" + ", ".join(NAMES[l] for l in tt) + "}" for tt in d["tiers"]))
    L.append("\n## Hors plan : rangs compatibles avec les paires établies\n")
    L.append("Une paire est établie si elle est ordonnée dans le même sens dans au moins 95 % des tirages de l'analyse "
             "globale et sur la machine 3 (le critère des étages, appliqué paire par paire). Rang possible d'un langage : "
             "de 1 + le nombre de langages établis devant lui à 21 − le nombre de langages établis derrière lui.\n")
    L.append("| Langage | Composite MS | Plafond E | Code naturel D1 |")
    L.append("|---|---|---|---|")
    er = o["established_ranks"]
    for l in sorted(RANKED, key=lambda l: (er["MS"][l][0], er["MS"][l][1])):
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{er[q][l][0]}–{er[q][l][1]}" if er[q][l][0] != er[q][l][1]
                                                   else f"{er[q][l][0]}" for q in ("MS", "E", "D1")) + " |")
    L.append("\n## Hors plan : accord entre machines avec et sans K3\n")
    L.append("| Noyaux | MS : Spearman 21 / 13 / 9 premiers | MS : inversions dans les 13 premiers | E : Spearman 21 / 13 / 9 premiers | E : inversions dans les 13 premiers |")
    L.append("|---|---|---|---|---|")
    for name, d in o["agreement_without_k3"].items():
        L.append(f"| {name} | {fr(d['MS']['rho21'], 2)} / {fr(d['MS']['rho13'], 2)} / {fr(d['MS']['rho9'], 2)} | "
                 f"{d['MS']['inv13']} | {fr(d['E']['rho21'], 2)} / {fr(d['E']['rho13'], 2)} / {fr(d['E']['rho9'], 2)} | "
                 f"{d['E']['inv13']} |")
    cl = o["cascade_lake_only"]
    L.append("\n## Hors plan : Cascade Lake seul (K5 d'avant, machines 1 et 2), estimation ponctuelle\n")
    L.append(", ".join(f"{NAMES[l]} {r} (E {fr(cl['E'][l])}, D1 {fr(cl['D1'][l])})"
                       for l, r in sorted(cl["rank"].items(), key=lambda kv: kv[1])) + ".\n")
    L.append("## Réplication : bruit ou interaction ?\n")
    L.append("| Statistique | Observée | Hypothèse nulle : médiane [5–95 %] | p |")
    L.append("|---|---|---|---|")
    lab = {"rho21": "Spearman, 21 langages", "rho13": "Spearman, 13 premiers", "rho9": "Spearman, 9 premiers",
           "inv13": "Paires inversées parmi les 13 premiers"}
    for k, v in o["replication"]["null"].items():
        L.append(f"| {lab[k]} | {fr(v['observed'], 2)} | {fr(v['null_median'], 2)} [{fr(v['null_5_95'][0], 2)}–"
                 f"{fr(v['null_5_95'][1], 2)}] | {fr(v['p'], 3)} |")
    for f, d in o["replication"].get("null_inflated", {}).items():
        L.append(f"\nHors plan, bruit de la machine 3 multiplié par {f.replace('.', ',')} : " + " ; ".join(
            f"{lab[k]} p = {fr(v['p'], 3)} (médiane nulle {fr(v['null_median'], 2)})" for k, v in d.items()) + ".")
    for title, dd in (("tous les langages", o["variance_decomposition"]),
                      ("13 premiers (hors plan)", o["variance_decomposition_top13"])):
        L.append(f"\n## Décomposition de la variance entre les machines 1 et 3, {title} (part de chaque source)\n")
        L.append("| Mesure | n | Langage | Interaction langage × machine | Processus |")
        L.append("|---|---|---|---|---|")
        for k, v in dd.items():
            L.append(f"| {k} | {v['n']} | {fr(100 * v['langage'], 0)} % | {fr(100 * v['interaction'], 0)} % | {fr(100 * v['processus'], 0)} % |")
    if o["layout"]:
        L.append("\n## Disposition du code (machine actuelle) : écart-type entre dispositions et entre processus\n")
        L.append("σ : écarts-types du logarithme du temps. F : rapport des carrés moyens entre et dans les dispositions. "
                 "p : test par permutation des graines, 2 000 permutations (hors plan). Dernière colonne : F sans les "
                 "tâches " + ", ".join(f"{NAMES.get(i, i)} graine {s} processus {p}" for i, s, p in o["layout_perturbed_jobs"])
                 + ", pendant lesquelles deux calculs de cette analyse tournaient (hors plan).\n")
        L.append("| Implémentation | Mesure | Dispositions | σ dispositions | σ processus | F | p | Max / min des moyennes | F sans perturbation |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for impl, d in o["layout"].items():
            for k, v in sorted(d.items()):
                vc = o["layout_without_perturbed"].get(impl, {}).get(k, {})
                L.append(f"| {NAMES.get(impl, impl)} | {k} | {v['seeds']} | {fr(v['sd_layout'], 3)} | {fr(v['sd_proc'], 3)} | "
                         f"{fr(v['F'], 1) if v['F'] else '—'} | {fr(v['p_perm'], 3) if v.get('p_perm') else '—'} | "
                         f"{fr(v['max_min'], 2)} | {fr(vc['F'], 1) if vc.get('F') else '—'} |")
    L.append("\n## Processus classés (critère de rupture de la v2, descriptif)\n")
    for k, v in o["process_classes"].items():
        L.append(f"* {k} : " + ", ".join(f"{a} {b}" for a, b in v.items()))
    L.append("\nRangs avec l'estimateur de la v2 (médiane des médianes de processus, frontière recalculée, sans coupure "
             "de régime établi) : "
             + ", ".join(f"{NAMES[l]} {r}" for l, r in sorted(o["rank_median_of_medians"].items(), key=lambda kv: kv[1])) + ".\n")
    open(os.path.join(ROOT, "results", "report_v3.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
