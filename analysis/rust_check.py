#!/usr/bin/env python3
"""Remarque sur Rust (plan : docs/RUST.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 11 (results/raw_rust, étiquette « rust »), reportés sur les données principales de
Rust ; latences de K8 naturel remesurées pour les 25 implémentations (results/raw_d3, étiquette « d3_m11 ») ; analyse
globale de la v3 rejouée (mêmes tirages) pour chaque scénario :
* Avant : le classement publié avant la remarque (latences de la campagne, K7 optimisé de la campagne).
* R-D3 : latences de D3 remesurées, seules. R-K7, R-K7-T : K7 optimisé corrigé, seul (règle du pont de
  analysis/transfer_check.py ; transfert seul). R-K7 est aussi le scénario « D3-ancien ».
* Publié : R-D3 et R-K7 (classement publié) ; Publié-T : R-D3 et R-K7-T.
* Sur Publié : S-K9 et S-K9-T (K9 naturel en Vec<[f64; M9]>), S-Q1 et S-Q1-T (_popcnt32, code de Cascade Lake), S-K8 et
  S-K8-T (arène écrite comme en C), S-libc-R (D3, D4 et F4 de Rust à 1), S-libc-FFI (idem pour tous les langages dont
  la chaîne livre une FFI sans C), S-tout et S-tout-T (S-K9, S-Q1, S-K8 et S-libc-R cumulés), D3-strict (latences
  remesurées sans les processus dont le vol dépasse 0,5 %).
Information : rust_ref / c sur les clés témoins (« à algorithme égal », même hôte) ; vol de temps et queues de K8.
Les corrections publiées des autres langages (results/transfers.json) sont appliquées ; puis le rapport de K7 retenu
pour Publié y est écrit pour Rust.
Sorties : results/rust_check.json, results/report_rust.md ; results/transfers.json (rapport de K7 de Rust)."""
import glob, json, math, os, statistics, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_rust")
RAW_D3 = os.path.join(ROOT, "results", "raw_d3")
LANG = "rust"
LIMIT = 0.25
K7T, K8T = ("k7", "tuned", ""), ("k8", "tuned", "")
K9N, K9T = ("k9", "natural", ""), ("k9", "tuned", "")
Q1T, Q1M, Q6T = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k6", "tuned", "q6")
K4B, K5T, K1A = ("k4", "branchless_unsorted", ""), ("k5", "tuned", ""), ("k1", "aos", "energy")
WIT = [K7T, K8T, K9N, K9T, Q1T, Q1M, Q6T, K4B, K5T, K1A]
MALLOC = ["c", "c_gcc", "cpp", "rust", "zig", "nim", "ada", "fortran", "odin", "c3"]
LIBC_CAPS = ("D3", "D4", "F4")
# Langages dont la chaîne livre un moyen d'appeler une fonction C sans écrire de C (plan, 3.3) ; C et C++ ont déjà la libc.
FFI = ["rust", "zig", "odin", "c3", "nim", "d", "ada", "fortran", "julia", "mojo", "chapel", "csharp", "java", "go",
       "haskell", "python"]
STRICT = 0.005


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad, steal = defaultdict(dict), [], defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "rust":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            steal[r["lang"]].setdefault(key, []).append(r.get("steal_frac") or 0.0)
    return d, bad, steal


def load_d3_procs():
    """Processus de la remesure de D3 : (implémentation, vol, latences par répétition), et les processus rejetés."""
    out, bad = [], []
    for f in sorted(glob.glob(os.path.join(RAW_D3, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != v2.D3_TAG:
                continue
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps) or not r.get("lat"):
                bad.append((r["lang"], r.get("returncode")))
                continue
            out.append((r["lang"], r.get("steal_frac") or 0.0, np.array(r["lat"], float), r.get("attempt", 0)))
    return out, bad


def load_d3_times(lang):
    """Temps de K8 naturel d'une implémentation dans la remesure de D3 (mêmes passes que les paires Rust)."""
    out = []
    for line in open(os.path.join(RAW_D3, f"{lang}.jsonl")):
        r = json.loads(line)
        reps = r.get("reps", [])
        if r.get("tag") == v2.D3_TAG and reps and r.get("returncode") in (0, None) and all(x["ok"] is True for x in reps):
            out.append([x["sec"] for x in reps])
    return out


def gm(procs):
    return math.exp(proc_logs(procs).mean())


def rank(x):
    x = np.asarray(x, float)
    r = np.empty(len(x))
    r[np.argsort(x, kind="mergesort")] = np.arange(len(x))
    for v in np.unique(x):
        m = x == v
        if m.sum() > 1:
            r[m] = r[m].mean()
    return r


def rho(a, b):
    return float(np.corrcoef(rank(a), rank(b))[0, 1]) if len(a) > 2 else None


def d3_table(lat):
    """Médianes (sur toutes les répétitions) de p50, p99,9 et max, et D3 dans la configuration principale (« abs »)."""
    st = {}
    for l, dd in lat.items():
        procs = [p for p in dd.get(K8N, []) if len(p)]
        if procs:
            allr = np.vstack([np.asarray(p, float) for p in procs])
            st[l] = {"p50": float(np.median(allr[:, 0])), "p999": float(np.median(allr[:, 3])),
                     "max": float(np.median(allr[:, 4])), "procs": len(procs), "reps": len(allr)}
    m999 = min(st[l]["p999"] for l in RANKED if l in st)
    mmax = min(st[l]["max"] for l in RANKED if l in st)
    for l in st:
        st[l]["D3"] = math.sqrt((m999 / st[l]["p999"]) * (mmax / st[l]["max"]))
    return st


def summary(s):
    i = RANKED.index(LANG)
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    pos = order.index(LANG)
    nb = {}
    if pos > 0:
        nb["devant"] = (order[pos - 1], float(s["prec"][i, RANKED.index(order[pos - 1])]))
    if pos < len(order) - 1:
        nb["derrière"] = (order[pos + 1], float(s["prec"][i, RANKED.index(order[pos + 1])]))
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "E": {l: s["E"][l] for l in RANKED},
            "D": {l: s["D"][l] for l in RANKED}, "C": {l: s["C"][l] for l in RANKED},
            "Ek": s["Ek"][LANG], "pos": pos + 1, "neighbours": nb,
            "prec_rust": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de la matrice remplacées le temps du calcul (règles v1 et v2) ; restaurées ensuite."""
    saved_m, saved_o = {}, {}
    try:
        for lang, caps in (cells or {}).items():
            for cap, val in caps.items():
                saved_m[(lang, cap)] = v2.MATRIX[lang][cap]
                v2.MATRIX[lang][cap] = (max(val, saved_m[(lang, cap)][0]), saved_m[(lang, cap)][1])
                if (lang, cap) in v2.V2_OVERRIDES:
                    saved_o[(lang, cap)] = v2.V2_OVERRIDES[(lang, cap)]
                    v2.V2_OVERRIDES[(lang, cap)] = (max(val, saved_o[(lang, cap)][0]), saved_o[(lang, cap)][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        for (lang, cap), v in saved_m.items():
            v2.MATRIX[lang][cap] = v
        for k, v in saved_o.items():
            v2.V2_OVERRIDES[k] = v


def main():
    data, lat_old, *_ = v2.dataset_main(transfers=False, d3=False)
    tpath = os.path.join(ROOT, "results", "transfers.json")
    tr = json.load(open(tpath))
    for lang, keys in tr["ratios"].items():  # corrections publiées des autres langages, sans celles de Rust
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    v2.align_lat(data, lat_old)
    lat_new = defaultdict(dict, {l: dict(dd) for l, dd in lat_old.items()})
    remeasured = v2.apply_d3(lat_new)
    lat_strict = defaultdict(dict, {l: dict(dd) for l, dd in lat_old.items()})
    v2.apply_d3(lat_strict, max_steal=STRICT)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad, steal = load_raw()
    d3p, d3bad = load_d3_procs()
    rng = np.random.default_rng(v3.SEED + 200)
    R = lambda new, old, k: ratio(raw[new][k], raw[old][k], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_fix = {k: R("rust_fix", "rust_ref", k) for k in (K7T, K9T, Q6T, K1A)}
    r_nat = {k: R("rust_nat", "rust_ref", k) for k in (K9N, K9T)}
    r_k8 = {K8T: R("rust_k8", "rust_ref", K8T)}
    # Écart au plan (cellules) : rust_ref n'a pas mesuré K8 naturel ; le témoin de rust_k8 est comparé au binaire Rust de
    # la remesure de D3 (bench/rust, mêmes passes, même hôte). Information seulement.
    r_k8[K8N] = ratio(raw["rust_k8"][K8N], load_d3_times("rust"), rng)
    r_pop = {k: R("rust_clpop", "rust_cl", k) for k in (Q1T, Q1M)}
    r_eq = {k: R("rust_ref", "c", k) for k in WIT}
    main_eq = {kk(k): gm(data[LANG][k]) / gm(data["c"][k]) for k in WIT}
    transfer = {}

    def bridged(key, r, new_impl, label):
        t_main = gm(data[LANG][key])
        trf = t_main * r
        br = gm(data["c"][key]) * gm(raw[new_impl][key]) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        used = (br / t_main) if use else r
        transfer[f"{label} {kk(key)}"] = {"rust_main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br,
                                          "gap": gap, "bridge_used": use, "ratio": r, "ratio_used": used,
                                          "c_main_ms": 1e3 * gm(data["c"][key])}
        return used

    k7_b = {K7T: bridged(K7T, r_fix[K7T]["ratio"], "rust_fix", "K7")}
    k7_t = {K7T: r_fix[K7T]["ratio"]}
    k9_b = {K9N: bridged(K9N, r_nat[K9N]["ratio"], "rust_nat", "S-K9")}
    k9_t = {K9N: r_nat[K9N]["ratio"]}
    q1_b = {k: bridged(k, r_pop[k]["ratio"], "rust_clpop", "S-Q1") for k in (Q1T, Q1M)}
    q1_t = {k: r_pop[k]["ratio"] for k in (Q1T, Q1M)}
    k8_b = {K8T: bridged(K8T, r_k8[K8T]["ratio"], "rust_k8", "S-K8")}
    k8_t = {K8T: r_k8[K8T]["ratio"]}
    libc_r = {LANG: {c: 1 for c in LIBC_CAPS}}
    libc_ffi = {l: {c: 1 for c in LIBC_CAPS} for l in FFI}
    plans = {
        "Avant": (data, lat_old, None),
        "R-D3": (data, lat_new, None),
        "R-K7": (scaled(data, k7_b), lat_old, None),
        "R-K7-T": (scaled(data, k7_t), lat_old, None),
        "Publié": (scaled(data, k7_b), lat_new, None),
        "Publié-T": (scaled(data, k7_t), lat_new, None),
        "S-K9": (scaled(data, {**k7_b, **k9_b}), lat_new, None),
        "S-K9-T": (scaled(data, {**k7_b, **k9_t}), lat_new, None),
        "S-Q1": (scaled(data, {**k7_b, **q1_b}), lat_new, None),
        "S-Q1-T": (scaled(data, {**k7_b, **q1_t}), lat_new, None),
        "S-K8": (scaled(data, {**k7_b, **k8_b}), lat_new, None),
        "S-K8-T": (scaled(data, {**k7_b, **k8_t}), lat_new, None),
        "S-libc-R": (scaled(data, k7_b), lat_new, libc_r),
        "S-libc-FFI": (scaled(data, k7_b), lat_new, libc_ffi),
        "S-tout": (scaled(data, {**k7_b, **k9_b, **q1_b, **k8_b}), lat_new, libc_r),
        "S-tout-T": (scaled(data, {**k7_t, **k9_t, **q1_t, **k8_t}), lat_new, libc_r),
        "D3-strict": (scaled(data, k7_b), lat_strict, None),
    }
    # queues de K8 : ancien et nouveau D3, vol de temps et queues dans la remesure
    t_old, t_new, t_strict = d3_table(lat_old), d3_table(lat_new), d3_table(lat_strict)
    mal = [p for p in d3p if p[0] in MALLOC]
    corr = {"malloc": {"n": len(mal), "rho_p999": rho([p[1] for p in mal], [np.median(p[2][:, 3]) for p in mal]),
                       "rho_max": rho([p[1] for p in mal], [np.median(p[2][:, 4]) for p in mal])},
            "tous": {"n": len(d3p), "rho_p999": rho([p[1] for p in d3p], [np.median(p[2][:, 3]) for p in d3p]),
                     "rho_max": rho([p[1] for p in d3p], [np.median(p[2][:, 4]) for p in d3p])}}
    steal_d3 = {"max": max(p[1] for p in d3p), "median": float(np.median([p[1] for p in d3p])),
                "above_strict": sorted((p[0], round(100 * p[1], 2)) for p in d3p if p[1] > STRICT),
                "redone": sum(1 for p in d3p if p[3] > 0)}
    procs_rust = [{"steal": p[1], "p50": float(np.median(p[2][:, 0])), "p999": float(np.median(p[2][:, 3])),
                   "max": float(np.median(p[2][:, 4]))} for p in d3p if p[0] in ("rust", "c")]
    out = {"bad": bad, "bad_d3": d3bad, "remeasured": remeasured, "times_ms": times,
           "r_fix": {kk(k): r for k, r in r_fix.items()}, "r_nat": {kk(k): r for k, r in r_nat.items()},
           "r_k8": {kk(k): r for k, r in r_k8.items()}, "r_pop": {kk(k): r for k, r in r_pop.items()},
           "r_eq": {kk(k): r for k, r in r_eq.items()}, "main_eq": main_eq, "transfer": transfer,
           "d3_old": t_old, "d3_new": t_new, "d3_strict": t_strict, "steal_corr_d3": corr, "steal_d3": steal_d3,
           "procs_rust_c": procs_rust, "published_ratios": {kk(k): v for k, v in k7_b.items()}, "scenarios": {}}
    for name, (d, lat, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, cells)
        print(f"{name} : Rust {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "rust_check.json"), "w"), indent=1, default=float)
    # classement publié (décision 1) : rapport de K7 de Publié inscrit dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in k7_b.items()}
    note = " ; Rust : docs/RUST.md (3.2), results/raw_rust, machine 11, results/rust_check.json"
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(tpath, "w"), indent=1)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur Rust : rapports appariés, remesure de D3 et scénarios\n",
         "Plan : `docs/RUST.md`. Mesures : `results/raw_rust/` et `results/raw_d3/` (machine 11, 7 processus par cellule).",
         "Code : `analysis/rust_check.py`. Processus rejetés : " + (str(len(o["bad"]) + len(o["bad_d3"])) if o["bad"] or o["bad_d3"] else "aucun") + ".\n",
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    for lab, dd in (("rust_fix / rust_ref", o["r_fix"]), ("rust_nat / rust_ref", o["r_nat"]),
                    ("rust_k8 / rust_ref", o["r_k8"]), ("rust_clpop / rust_cl", o["r_pop"])):
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Rust et C à algorithme égal (information)\n",
          "| Clé | C, hôte (ms) | Rust, hôte (ms) | Rust / C, hôte [IC 95 %] | Rust / C, données principales |", "|---|---|---|---|---|"]
    for k, r in o["r_eq"].items():
        L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 2)} [{f(r['ci'][0], 2)}–"
                 f"{f(r['ci'][1], 2)}] | {f(o['main_eq'][k], 2)} |")
    L += ["", "## Report sur les données principales (transfert ou pont par le C de la campagne)\n",
          "| Clé | Rust (données principales) | Transfert | Pont | Écart | Retenu |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        L.append(f"| {k} | {f(b['rust_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## D3 : latences de K8 naturel (médianes sur toutes les répétitions)\n",
          "| Langage | Processus (campagne → remesure) | p50 (µs) | p99,9 (µs) | max (µs) | D3 |", "|---|---|---|---|---|---|"]
    for l in RANKED:
        a, b = o["d3_old"].get(l), o["d3_new"].get(l)
        if a and b:
            L.append(f"| {NAMES.get(l, l)} | {a['procs']} → {b['procs']} | {f(a['p50'] / 1e3)} → {f(b['p50'] / 1e3)} | "
                     f"{f(a['p999'] / 1e3)} → {f(b['p999'] / 1e3)} | {f(a['max'] / 1e3, 0)} → {f(b['max'] / 1e3, 0)} | "
                     f"{f(a['D3'], 3)} → {f(b['D3'], 3)} |")
    c, s = o["steal_corr_d3"], o["steal_d3"]
    L += ["", f"Vol de temps dans la remesure : médiane {f(100 * s['median'], 2)} %, maximum {f(100 * s['max'], 2)} % ; "
          f"{s['redone']} processus refaits au-dessus de 2 % ; au-dessus de 0,5 % : "
          + (", ".join(f"{NAMES.get(l, l)} {f(v, 2)} %" for l, v in s["above_strict"]) or "aucun") + ".",
          f"Corrélation de rang entre le vol et la queue (processus des langages à malloc, n = {c['malloc']['n']}) : p99,9 "
          f"{f(c['malloc']['rho_p999'], 2)}, max {f(c['malloc']['rho_max'], 2)} ; tous (n = {c['tous']['n']}) : "
          f"{f(c['tous']['rho_p999'], 2)} et {f(c['tous']['rho_max'], 2)}.\n",
          "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Rust | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |", "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_rust.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
