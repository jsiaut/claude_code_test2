#!/usr/bin/env python3
"""Analyse pré-enregistrée (docs/METHODOLOGY.md, sections 4 à 7).

Entrées : results/raw/*.jsonl (pilote), analysis/capabilities.py (pilier C),
results/vectorization.json (C3 mesuré), results/footprint.json (empreinte K1).
Sorties : results/summary.json et tableaux Markdown sur la sortie standard.
"""
import glob, json, math, os, random, statistics, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX, CATEGORIES, M  # noqa: E402

RANKED = ["c", "cpp", "csharp", "java", "zig", "odin", "julia", "ada", "fortran", "js", "python", "haskell",
          "c3", "d", "rust", "chapel", "nim", "mojo", "go", "ocaml", "lua"]
ANNEX = {"c_gcc": "c", "fortran_flang": "fortran", "luajit": "lua", "js_bun": "js", "python_ft": "python"}
N1 = 4194304
WEIGHTS = {"C": 0.35, "E": 0.40, "D": 0.25}


# ------------------------------------------------------------------ chargement
def load():
    """data[lang][(kernel, variant, param)] = liste de processus ; chaque processus = liste de secondes."""
    data, lat, rss, invalid = defaultdict(dict), defaultdict(dict), defaultdict(dict), []
    for f in glob.glob(os.path.join(ROOT, "results", "raw", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if r["kernel"] == "fp":
                rss[r["lang"]][r["variant"]] = r["maxrss_kb"]
                continue
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                invalid.append((r["lang"], key, r.get("returncode"), [x["chk"] for x in reps][:1]))
                continue
            data[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            if r.get("lat"):
                lat[r["lang"]].setdefault(key, []).extend(r["lat"])
    return data, lat, rss, invalid


def med(xs):
    return statistics.median(xs)


def point(procs):
    """Médiane inter-processus des médianes intra-processus."""
    return med([med(p) for p in procs])


def boot(procs, rng):
    """Bootstrap hiérarchique (Kalibera & Jones) : processus puis répétitions."""
    ps = [procs[rng.randrange(len(procs))] for _ in procs]
    return med([med([p[rng.randrange(len(p))] for _ in p]) for p in ps])


def geo(xs):
    xs = [x for x in xs if x is not None]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else None


# ------------------------------------------------------------------ mesures du pilier E
# chaque mesure : liste de (kernel, variant, param) admissibles ; t(L,m) = min sur les admissibles
E_MEASURES = {
    "k1": [[("k1", "aos", "energy"), ("k1", "soa", "energy")]],
    "k3": [[("k3", "sw_padded", ""), ("k3", "rmw_padded", "")]],
    "k4": [[("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")]],
    "k5": [[("k5", "natural", ""), ("k5", "tuned", "")]],
    "k6": [[("k6", "natural", "q6"), ("k6", "tuned", "q6")], [("k6", "natural", "q1"), ("k6", "tuned", "q1")],
           [("k6", "mt", "q6")], [("k6", "mt", "q1")]],
    "k7": [[("k7", "natural", ""), ("k7", "tuned", "")]],
    "k8": [[("k8", "natural", ""), ("k8", "tuned", ""), ("k8", "tuned_alloc", "")]],
    "k9": [[("k9", "natural", ""), ("k9", "tuned", "")], [("k9", "mt", "")]],
    "k10": [[("k10", "natural", ""), ("k10", "tuned", "")]],
}
# pilier D1 : variantes natural seulement, mêmes références t*(m)
D1_MEASURES = {
    "k1": [(0, [("k1", "natural", "energy")])], "k4": [(0, [("k4", "natural_unsorted", "")])],
    "k5": [(0, [("k5", "natural", "")])], "k6": [(0, [("k6", "natural", "q6")]), (1, [("k6", "natural", "q1")])],
    "k7": [(0, [("k7", "natural", "")])], "k8": [(0, [("k8", "natural", "")])], "k9": [(0, [("k9", "natural", "")])],
    "k10": [(0, [("k10", "natural", "")])],
}
K2_SIZES = ["16384", "262144", "8388608"]


def times(data, lang, keys, rng=None):
    """Meilleur temps (point ou tirage bootstrap) parmi les variantes admissibles présentes."""
    best = None
    for k in keys:
        procs = data.get(lang, {}).get(k)
        if procs:
            t = boot(procs, rng) if rng else point(procs)
            best = t if best is None else min(best, t)
    return best


def all_times(data, rng=None):
    """T[lang][kernel][i] = temps de la mesure i ; tstar[kernel][i] = min sur les langages classés."""
    T = {}
    for lang in list(data):
        T[lang] = {k: [times(data, lang, keys, rng) for keys in ms] for k, ms in E_MEASURES.items()}
    tstar = {k: [min((T[l][k][i] for l in RANKED if l in T and T[l][k][i] is not None), default=None)
                 for i in range(len(ms))] for k, ms in E_MEASURES.items()}
    return T, tstar


def pillar_e(T, tstar, lang):
    ks = {}
    for k in E_MEASURES:
        vals = [tstar[k][i] / T[lang][k][i] for i in range(len(E_MEASURES[k])) if T[lang][k][i]]
        ks[k] = geo(vals) if len(vals) == len(E_MEASURES[k]) else None
    return 100 * geo(list(ks.values())) if all(v is not None for v in ks.values()) else None, ks


def pillar_d(data, lat, rss, tstar, lang, rng=None, footprint=None, k8ref=None, k2ref=None):
    # D1 : efficacité du code naturel
    d1k = {}
    for k, ms in D1_MEASURES.items():
        vals = []
        for i, keys in ms:
            t = times(data, lang, keys, rng)
            vals.append(tstar[k][i] / t if t else None)
        d1k[k] = geo(vals) if all(v is not None for v in vals) else None
    d1 = geo(list(d1k.values())) if all(v is not None for v in d1k.values()) else None
    # D2 : coût de structure
    bpp = (footprint or {}).get(lang)
    a = min(1.0, 64.0 / bpp) if bpp else None
    tn, ts = times(data, lang, [("k1", "natural", "energy")], rng), times(data, lang, [("k1", "natural_shuffled", "energy")], rng)
    b = min(1.0, tn / ts) if tn and ts else None
    d2 = geo([a, b]) if a and b else (b if b else None)
    # D3 : prévisibilité (K8 natural)
    d3 = None
    L = lat.get(lang, {}).get(("k8", "natural", ""))
    if L and k8ref and all(x[0] > 0 for x in L):
        p50, p999, mx = med([x[0] for x in L]), med([x[3] for x in L]), med([x[4] for x in L])
        d3 = geo([k8ref[0] / (p999 / p50), k8ref[1] / (mx / p50)])
    # D4 : visibilité de la hiérarchie mémoire (K2)
    d4 = None
    if k2ref:
        vals = []
        for s in K2_SIZES:
            t = times(data, lang, [("k2", "tuned", s)], rng)
            vals.append(min(1.0, k2ref[s] / t) if t and k2ref.get(s) else None)
        d4 = geo(vals) if all(v is not None for v in vals) else None
    parts = {"D1": d1, "D2": d2, "D3": d3, "D4": d4}
    w = {"D1": 0.5, "D2": 0.15, "D3": 0.15, "D4": 0.2}
    if any(v is None for v in parts.values()):
        return None, parts
    return 100 * sum(w[k] * parts[k] for k in w), parts


def k8_ref(lat, langs):
    ratios = []
    for l in langs:
        L = lat.get(l, {}).get(("k8", "natural", ""))
        if L:
            p50, p999, mx = med([x[0] for x in L]), med([x[3] for x in L]), med([x[4] for x in L])
            ratios.append((p999 / p50, mx / p50))
    return (min(r[0] for r in ratios), min(r[1] for r in ratios)) if ratios else None


def pillar_c(lang, c3):
    tot = 0.0
    for cat, (w, caps) in CATEGORIES.items():
        vals = [(c3.get(lang, 0) if MATRIX[lang][c] == M else MATRIX[lang][c][0]) for c in caps]
        tot += w * sum(vals) / len(vals)
    return 100 * tot


# Bornes physiques (contrôle de vraisemblance) : octets à déplacer / meilleure bande passante mesurée
# (results/hw : 10 Go/s en DRAM sur 1 thread, 61 Go/s sur 4 threads), et opérations / débit FMA crête.
# Un temps inférieur à sa borne trahit un calcul sauté que la somme de contrôle ne voit pas.
BW1, BW4 = 10e9, 61e9
BOUNDS = {
    ("k1", "soa", "energy"): 4 * 4 * 4194304 / BW1, ("k1", "aos", "energy"): 64 * 4194304 / BW1,
    ("k1", "natural", "energy"): 64 * 4194304 / BW1, ("k5", "tuned", ""): 2 * 2048 * 65536 / 139e9,
    ("k5", "natural", ""): 2 * 2048 * 65536 / 139e9, ("k6", "tuned", "q6"): 10 * 16777216 / BW1,
    ("k6", "natural", "q6"): 10 * 16777216 / BW1, ("k6", "mt", "q6"): 10 * 16777216 / BW4,
    ("k6", "tuned", "q1"): 13 * 16777216 / BW1, ("k6", "mt", "q1"): 13 * 16777216 / BW4,
    ("k9", "tuned", ""): 4 * 2 * 8 * 2048 * 2048 / BW1, ("k9", "natural", ""): 4 * 2 * 8 * 2048 * 2048 / BW1,
    ("k9", "mt", ""): 4 * 2 * 8 * 2048 * 2048 / BW4, ("k4", "natural_unsorted", ""): 16777216 / BW1,
    ("k4", "branchless_unsorted", ""): 16777216 / BW1,
    # K3 : 2^25 incréments dépendants par thread, au mieux 1 par cycle à 3,3 GHz (même en registre)
    ("k3", "sw_padded", ""): 2 ** 25 / 3.3e9, ("k3", "sw_packed", ""): 2 ** 25 / 3.3e9,
    ("k3", "rmw_padded", ""): 2 ** 25 / 3.3e9, ("k3", "rmw_packed", ""): 2 ** 25 / 3.3e9,
}


def sanity(data):
    flags = []
    for lang, d in data.items():
        for key, bound in BOUNDS.items():
            if key in d:
                t = point(d[key])
                if t < 0.9 * bound:
                    flags.append((lang, key, t, bound))
    return flags


def main():
    data, lat, rss, invalid = load()
    # une mesure plus rapide que la physique ne le permet a sauté du calcul : invalide, comme une
    # somme de contrôle fausse (le résultat peut être juste sans que le travail ait été fait)
    sus = sanity(data)
    for lang, key, t, bound in sus:
        del data[lang][key]
        invalid.append((lang, key, "sous la borne physique", f"{t:.2e} s < {bound:.2e} s"))
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json"))) if os.path.exists(
        os.path.join(ROOT, "results", "vectorization.json")) else {}
    fpf = os.path.join(ROOT, "results", "footprint.json")
    footprint = json.load(open(fpf)) if os.path.exists(fpf) else {}
    T, tstar = all_times(data)
    k8r = k8_ref(lat, [l for l in RANKED if l in lat])
    k2r = {s: times(data, "c", [("k2", "tuned", s)]) for s in K2_SIZES}
    res = {}
    for lang in RANKED + list(ANNEX):
        if lang not in data and lang in ANNEX:
            continue
        e, ek = pillar_e(T, tstar, lang) if lang in T else (None, {})
        d, dp = pillar_d(data, lat, rss, tstar, lang, footprint=footprint, k8ref=k8r, k2ref=k2r) if lang in data else (None, {})
        base = ANNEX.get(lang, lang)
        c = pillar_c(base, c3) if base in MATRIX else None
        ms = WEIGHTS["C"] * c + WEIGHTS["E"] * e + WEIGHTS["D"] * d if None not in (c, e, d) else None
        res[lang] = {"C": c, "E": e, "D": d, "MS": ms, "E_kernels": ek, "D_parts": dp}
    # bootstrap des mesures -> IC des piliers E, D et du score
    rng = random.Random(12345)
    B = int(os.environ.get("BOOT", "200"))
    samples = defaultdict(list)
    for _ in range(B):
        Tb, tsb = all_times(data, rng)
        for lang in res:
            if lang not in Tb:
                continue
            e, _ = pillar_e(Tb, tsb, lang)
            d, _ = pillar_d(data, lat, rss, tsb, lang, rng=rng, footprint=footprint, k8ref=k8r, k2ref=k2r)
            c = res[lang]["C"]
            if None not in (e, d, c):
                samples[lang].append((c, e, d))
    for lang, ss in samples.items():
        for j, name in enumerate(["C", "E", "D"]):
            xs = sorted(s[j] for s in ss)
            res[lang][name + "_ci"] = (xs[int(0.025 * len(xs))], xs[int(0.975 * len(xs)) - 1])
    # Monte-Carlo de Dirichlet(1,1,1) sur les poids, combiné aux tirages bootstrap
    ranked = [l for l in RANKED if res.get(l, {}).get("MS") is not None]
    ranks = defaultdict(list)
    for it in range(10000):
        g = [rng.expovariate(1.0) for _ in range(3)]
        s = sum(g)
        wc, we, wd = g[0] / s, g[1] / s, g[2] / s
        sc = {}
        for l in ranked:
            c, e, d = samples[l][it % len(samples[l])] if samples.get(l) else (res[l]["C"], res[l]["E"], res[l]["D"])
            sc[l] = wc * c + we * e + wd * d
        order = sorted(ranked, key=lambda l: -sc[l])
        for i, l in enumerate(order):
            ranks[l].append(i + 1)
    for l in ranked:
        rs = sorted(ranks[l])
        res[l]["rank_median"] = rs[len(rs) // 2]
        res[l]["rank_90"] = (rs[int(0.05 * len(rs))], rs[int(0.95 * len(rs)) - 1])
    # robustesse 1 : chaque capacité notée 0,5 tirée au hasard à 0 ou 1 (subjectivité du pilier C)
    rank_halves = defaultdict(list)
    for it in range(2000):
        sc = {}
        for l in ranked:
            tot = 0.0
            for cat, (w, caps) in CATEGORIES.items():
                vals = []
                for c in caps:
                    v = c3.get(l, 0) if MATRIX[l][c] == M else MATRIX[l][c][0]
                    if v == 0.5:
                        v = float(rng.random() < 0.5)
                    vals.append(v)
                tot += w * sum(vals) / len(vals)
            sc[l] = WEIGHTS["C"] * 100 * tot + WEIGHTS["E"] * res[l]["E"] + WEIGHTS["D"] * res[l]["D"]
        for i, l in enumerate(sorted(ranked, key=lambda l: -sc[l])):
            rank_halves[l].append(i + 1)
    for l in ranked:
        rs = sorted(rank_halves[l])
        res[l]["rank_halves_90"] = (rs[int(0.05 * len(rs))], rs[int(0.95 * len(rs)) - 1])
    # robustesse 2 : pilier E recalculé en retirant chaque noyau tour à tour
    for l in ranked:
        rks = []
        for drop in E_MEASURES:
            sc = {}
            for m in ranked:
                ek = {k: v for k, v in res[m]["E_kernels"].items() if k != drop}
                e = 100 * geo(list(ek.values()))
                sc[m] = WEIGHTS["C"] * res[m]["C"] + WEIGHTS["E"] * e + WEIGHTS["D"] * res[m]["D"]
            rks.append(sorted(ranked, key=lambda m: -sc[m]).index(l) + 1)
        res[l]["rank_drop_kernel"] = (min(rks), max(rks))
    # classements par pilier
    for name in ("C", "E", "D"):
        for i, l in enumerate(sorted(ranked, key=lambda l: -res[l][name])):
            res[l]["rank_" + name] = i + 1
    out = {"results": res, "tstar": tstar, "invalid": invalid, "k8_ref": k8r, "k2_ref": k2r}
    json.dump(out, open(os.path.join(ROOT, "results", "summary.json"), "w"), indent=1, default=str)
    # tableau
    print("| Rang | Langage | MS | C (rang) | E [IC95] (rang) | D [IC95] (rang) | rang, poids de Dirichlet [5-95 %] | rang, cellules 0,5 tirées [5-95 %] | rang, un noyau retiré [min-max] |")
    print("|---|---|---|---|---|---|---|---|---|")
    for i, l in enumerate(sorted(ranked, key=lambda l: -res[l]["MS"])):
        r = res[l]
        eci, dci = r.get("E_ci", (0, 0)), r.get("D_ci", (0, 0))
        print(f"| {i + 1} | {l} | {r['MS']:.1f} | {r['C']:.1f} ({r['rank_C']}) | {r['E']:.1f} [{eci[0]:.1f}-{eci[1]:.1f}] ({r['rank_E']}) | "
              f"{r['D']:.1f} [{dci[0]:.1f}-{dci[1]:.1f}] ({r['rank_D']}) | {r['rank_median']} [{r['rank_90'][0]}-{r['rank_90'][1]}] | "
              f"[{r['rank_halves_90'][0]}-{r['rank_halves_90'][1]}] | [{r['rank_drop_kernel'][0]}-{r['rank_drop_kernel'][1]}] |")
    missing = [l for l in RANKED if l not in ranked]
    if missing:
        print("incomplets :", {l: {k: v for k, v in res.get(l, {}).items() if k in ("C", "E", "D")} for l in missing})
    if invalid:
        print("mesures invalides :", len(invalid), invalid[:10])
    print("contrôle de vraisemblance (temps < 0,9 x borne physique, exclus) :", sus if sus else "aucune anomalie")


if __name__ == "__main__":
    main()
