#!/usr/bin/env python3
"""Remarque sur C# (plan : docs/CSHARP.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 9 (results/raw_csharp, étiquette « csharp »), reportés sur les données principales
de C# ; analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario :
* Publié : rien ne change (doit redonner 54,77 points et la 14e place).
* S-E7 : E7 = 1.
* S-P1, S-P2, S-N11 (transfert seul, même code) : clés × r(csharp_full | csharp_steady | csharp_net11 / csharp).
* S1 (règle du pont de analysis/transfer_check.py) et S1-T (transfert seul) : K4 sans branchement, Q1 tuned et mt,
  K8 tuned × min(1, r(csharp_exp / csharp)).
* S1-R : S1-T, et le K8 tuned des autres langages classés × r(c_gcc_exp / c_gcc) si < 1.
* S1-P1 : clés de S1 × min(1, r_full, r_exp, r_exp_full) ; les autres clés × r_full.
* S-pool, S-pool-T : K6 mt (Q6, Q1) et K9 mt × min(1, r(mt_pool / mt)) (rapports dans csharp_exp).
* S-nat, S-nat-T : K1 naturel et permuté, K6 naturel Q6 et Q1 × r(csharp_nat2 / csharp), empreinte de csharp_nat2 ;
  S-K1 et S-K6 (transfert seul) : ses deux moitiés.
* S-max, S-max-T : S1-P1 + S-pool + S-nat + E7 = 1.
* S-K4 : K4 retiré du plafond pour tous les langages ; S-K4simd (unilatéral) : K4 sans branchement de C# remplacé par
  son SIMD explicite.
Sorties : results/csharp_check.json, results/report_csharp.md."""
import glob, json, math, os, statistics, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_csharp")
LANG = "csharp"
LIMIT = 0.25
N1 = 4194304
ALL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
       ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
       ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""),
       ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), ("k5", "tuned", ""), ("k6", "natural", "q6"),
       ("k6", "tuned", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"),
       ("k7", "natural", ""), ("k7", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", ""), ("k9", "natural", ""),
       ("k9", "tuned", ""), ("k9", "mt", "")]
STEADY = [("k1", "natural", "energy"), ("k1", "aos", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"),
          ("k3", "sw_padded", ""), ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""),
          ("k5", "natural", ""), ("k5", "tuned", ""), ("k6", "natural", "q6"), ("k6", "tuned", "q6"),
          ("k6", "natural", "q1"), ("k6", "mt", "q6"), ("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")]
K4B, Q1T, Q1M, K8T = ("k4", "branchless_unsorted", ""), ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k8", "tuned", "")
Q6M, K9M = ("k6", "mt", "q6"), ("k9", "mt", "")
K1N, K1P, Q6N, Q1N = ("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k6", "natural", "q6"), \
    ("k6", "natural", "q1")
S1_KEYS = [K4B, Q1T, Q1M, K8T]
POOL = {Q6M: ("k6", "mt_pool", "q6"), Q1M: ("k6", "mt_pool", "q1"), K9M: ("k9", "mt_pool", "")}
NAT = [K1N, K1P, Q6N, Q1N]
CONTROLS = {"csharp_exp": [("k9", "tuned", ""), ("k6", "tuned", "q6")], "csharp_nat2": [("k1", "aos", "energy")]}
K4S = ("k4", "simd_unsorted", "")


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad, fp = defaultdict(dict), [], defaultdict(list)
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") == "csharp_fp" and r.get("returncode") == 0 and "mem" in r.get("meta", {}):
                _kind, p1, p2 = r["meta"]["mem"].split(";")
                fp[r["lang"]].append((int(p2) - int(p1)) / N1)
                continue
            if r.get("tag") != "csharp":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return d, bad, fp


def gm(procs):
    return math.exp(proc_logs(procs).mean())


def gm_ratio_ci(raw, new, old, keys, rng, nb=2000):
    """Moyenne géométrique des rapports par clé ; IC par bootstrap des processus dans chaque clé (90 % et 95 %)."""
    logs = {k: (proc_logs(raw[new][k]), proc_logs(raw[old][k])) for k in keys}
    point = math.exp(np.mean([yn.mean() - yo.mean() for yn, yo in logs.values()]))
    bs = []
    for _ in range(nb):
        bs.append(math.exp(np.mean([yn[rng.integers(0, len(yn), len(yn))].mean()
                                    - yo[rng.integers(0, len(yo), len(yo))].mean() for yn, yo in logs.values()])))
    return {"gm": point, "ci90": [float(np.quantile(bs, 0.05)), float(np.quantile(bs, 0.95))],
            "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))], "n_keys": len(keys)}


def summary(s):
    i = RANKED.index(LANG)
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    pos = order.index(LANG)
    nb = {}
    if pos > 0:
        nb["devant"] = (order[pos - 1], float(s["prec"][i, RANKED.index(order[pos - 1])]))
    if pos < len(order) - 1:
        nb["derrière"] = (order[pos + 1], float(s["prec"][i, RANKED.index(order[pos + 1])]))
    ahead = order[pos - 1] if pos > 0 else None
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "E": {l: s["E"][l] for l in RANKED},
            "D": {l: s["D"][l] for l in RANKED}, "C": {l: s["C"][l] for l in RANKED},
            "Ek": s["Ek"][LANG], "pos": pos + 1, "neighbours": nb,
            "gap_ahead": (s["ms0"][ahead] - s["ms0"][LANG]) if ahead else None, "ahead": ahead,
            "min_prec_top13": float(min(s["prec"][RANKED.index(l), i] for l in order[:13] if l != LANG)),
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors, others=None):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    for lang, fs in (others or {}).items():
        for key, r in fs.items():
            if key in d.get(lang, {}):
                d[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    return d


def run(data, lat, langs, footprint, c3, cells=None, e_drop=()):
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main", e_drop=e_drop))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def main():
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad, fp = load_raw()
    rng = np.random.default_rng(v3.SEED + 90)
    R = lambda new, old, k_new, k_old=None: ratio(raw[new][k_new], raw[old][k_old or k_new], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in d.items()} for impl, d in raw.items()}
    r_full = {k: R("csharp_full", "csharp", k) for k in ALL}
    r_steady = {k: R("csharp_steady", "csharp", k) for k in STEADY}
    r_net11 = {k: R("csharp_net11", "csharp", k) for k in ALL}
    r_exp = {k: R("csharp_exp", "csharp", k) for k in S1_KEYS}
    r_exp_full = {k: R("csharp_exp_full", "csharp", k) for k in S1_KEYS}
    r_pool = {k: R("csharp_exp", "csharp_exp", POOL[k], k) for k in POOL}
    r_nat = {k: R("csharp_nat2", "csharp", k) for k in NAT}
    r_ctrl = {f"{impl}|{kk(k)}": R(impl, "csharp", k) for impl, ks in CONTROLS.items() for k in ks}
    r_k4simd = R("csharp_exp", "csharp", K4S, K4B)
    r_c8 = {"clang": R("c_exp", "c", K8T), "gcc": R("c_gcc_exp", "c_gcc", K8T)}
    agg = {"P1": gm_ratio_ci(raw, "csharp_full", "csharp", ALL, rng),
           "P2": gm_ratio_ci(raw, "csharp_steady", "csharp", STEADY, rng),
           "N11": gm_ratio_ci(raw, "csharp_net11", "csharp", ALL, rng)}
    fp_bpp = {impl: statistics.median(v) for impl, v in fp.items()}

    # report sur les données principales : transfert, pont par le C du même hôte, rapport retenu
    transfer = {}

    def bridged(key, r, new_impl, new_key):
        t_main = gm(data[LANG][key])
        tr = t_main * r
        br = gm(data["c"][key]) * gm(raw[new_impl][new_key]) / gm(raw["c"][key])
        gap = tr / br - 1
        use = abs(gap) > LIMIT
        used = (br / t_main) if use else r
        transfer[kk(key) + ("" if new_key == key else " (" + new_key[1] + ")")] = {
            "csharp_main_ms": 1e3 * t_main, "transfer_ms": 1e3 * tr, "bridge_ms": 1e3 * br, "gap": gap,
            "bridge_used": use, "ratio": r, "ratio_used": used, "c_main_ms": 1e3 * gm(data["c"][key])}
        return used

    s1_b = {k: min(1.0, bridged(k, r_exp[k]["ratio"], "csharp_exp", k)) for k in S1_KEYS}
    s1_t = {k: min(1.0, r_exp[k]["ratio"]) for k in S1_KEYS}
    pool_b = {k: min(1.0, bridged(k, r_pool[k]["ratio"], "csharp_exp", POOL[k])) for k in POOL}
    pool_t = {k: min(1.0, r_pool[k]["ratio"]) for k in POOL}
    nat_b = {k: bridged(k, r_nat[k]["ratio"], "csharp_nat2", k) for k in NAT}
    nat_t = {k: r_nat[k]["ratio"] for k in NAT}
    p1 = {k: r_full[k]["ratio"] for k in ALL}
    p2 = {k: r_steady[k]["ratio"] for k in STEADY}
    n11 = {k: r_net11[k]["ratio"] for k in ALL}
    s1p1 = dict(p1)
    for k in S1_KEYS:
        s1p1[k] = min(1.0, r_full[k]["ratio"], r_exp[k]["ratio"], r_exp_full[k]["ratio"])
    fp_nat = dict(footprint)
    fp_nat[LANG] = round(fp_bpp.get("csharp_nat2", 64.0), 2)
    others8 = {}
    if r_c8["gcc"]["ratio"] < 1:
        others8 = {l: {K8T: r_c8["gcc"]["ratio"]} for l in RANKED if l != LANG}

    def combine(*ds):
        """Produit des rapports clé par clé : protocole ou forme, threads du pool, code naturel (effets indépendants)."""
        out = {}
        for d_ in ds:
            for k, v in d_.items():
                out[k] = out.get(k, 1.0) * v
        return out

    smax_t = combine(s1p1, pool_t, nat_t)
    base_b = dict(p1)
    base_b.update({k: min(1.0, r_full[k]["ratio"], s1_b[k], r_exp_full[k]["ratio"]) for k in S1_KEYS})
    smax_b = combine(base_b, pool_b, nat_b)
    plans = {
        "Publié": (data, None, footprint, (), None),
        "S-E7": (data, {"E7": 1}, footprint, (), None),
        "S-P1": (scaled(data, p1), None, footprint, (), None),
        "S-P2": (scaled(data, p2), None, footprint, (), None),
        "S-N11": (scaled(data, n11), None, footprint, (), None),
        "S1": (scaled(data, s1_b), None, footprint, (), None),
        "S1-T": (scaled(data, s1_t), None, footprint, (), None),
        "S1-R": (scaled(data, s1_t, others8), None, footprint, (), None),
        "S1-P1": (scaled(data, s1p1), None, footprint, (), None),
        "S-pool": (scaled(data, pool_b), None, footprint, (), None),
        "S-pool-T": (scaled(data, pool_t), None, footprint, (), None),
        "S-nat": (scaled(data, nat_b), None, fp_nat, (), None),
        "S-nat-T": (scaled(data, nat_t), None, fp_nat, (), None),
        "S-K1": (scaled(data, {k: nat_t[k] for k in (K1N, K1P)}), None, fp_nat, (), None),
        "S-K6": (scaled(data, {k: nat_t[k] for k in (Q6N, Q1N)}), None, footprint, (), None),
        "S-max": (scaled(data, smax_b), {"E7": 1}, fp_nat, (), None),
        "S-max-T": (scaled(data, smax_t), {"E7": 1}, fp_nat, (), None),
        "S-K4": (data, None, footprint, ("k4",), None),
        "S-K4simd": (scaled(data, {K4B: r_k4simd["ratio"]}), None, footprint, (), None),
    }
    out = {"bad": bad, "times_ms": times, "footprint": {k: v for k, v in fp.items()}, "footprint_median": fp_bpp,
           "r_full": {kk(k): r for k, r in r_full.items()}, "r_steady": {kk(k): r for k, r in r_steady.items()},
           "r_net11": {kk(k): r for k, r in r_net11.items()}, "r_exp": {kk(k): r for k, r in r_exp.items()},
           "r_exp_full": {kk(k): r for k, r in r_exp_full.items()}, "r_pool": {kk(k): r for k, r in r_pool.items()},
           "r_nat": {kk(k): r for k, r in r_nat.items()}, "r_controls": r_ctrl, "r_k4simd": r_k4simd, "r_c8": r_c8,
           "aggregate": agg, "transfer": transfer, "used": {
               "S1": {kk(k): v for k, v in s1_b.items()}, "S1-T": {kk(k): v for k, v in s1_t.items()},
               "S1-P1": {kk(k): v for k, v in s1p1.items() if k in S1_KEYS},
               "S-pool": {kk(k): v for k, v in pool_b.items()}, "S-pool-T": {kk(k): v for k, v in pool_t.items()},
               "S-nat": {kk(k): v for k, v in nat_b.items()}, "S-nat-T": {kk(k): v for k, v in nat_t.items()},
               "S-max": {kk(k): v for k, v in smax_b.items() if v != p1.get(k)},
               "S-max-T": {kk(k): v for k, v in smax_t.items() if v != p1.get(k)},
               "S1-R K8 des autres": r_c8["gcc"]["ratio"] if others8 else None}, "scenarios": {}}
    if "--ratios-only" in sys.argv:  # contrôle léger pendant les mesures : pas d'analyse globale
        for lab, dd in (("P1", r_full), ("P2", r_steady), ("N11", r_net11), ("exp", r_exp), ("exp_full", r_exp_full),
                        ("pool", r_pool), ("nat", r_nat)):
            print(lab, {kk(k): round(r["ratio"], 3) for k, r in dd.items()})
        print("témoins", {k: round(r["ratio"], 3) for k, r in r_ctrl.items()}, "K4 SIMD", round(r_k4simd["ratio"], 3),
              "K8 C", {k: round(r["ratio"], 3) for k, r in r_c8.items()}, "agrégats",
              {k: round(a["gm"], 3) for k, a in agg.items()}, "empreinte", fp_bpp)
        return
    for name, (d, cells, fpr, drop, _) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, fpr, c3, cells, drop)
        print(f"{name} : C# {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}, "
              f"devant : {z['ahead']} (+{z['gap_ahead']:.1f}), min. des 13 premiers devant C# "
              f"{100 * z['min_prec_top13']:.0f} %", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "csharp_check.json"), "w"), indent=1, default=float)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur C# : rapports appariés et scénarios\n",
         "Plan : `docs/CSHARP.md`. Mesures : `results/raw_csharp/` (machine 9, 7 processus par cellule). Code :",
         "`analysis/csharp_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         "## Protocole et version (moyenne géométrique des rapports par clé)\n",
         "| Comparaison | Clés | Rapport | IC 90 % | IC 95 % |", "|---|---|---|---|---|"]
    names = {"P1": "FullOpts dès le premier appel / protocole (P1/P0)",
             "P2": "120 échauffements / protocole (P2/P0)", "N11": ".NET 11 RC3 / .NET 10 (P0)"}
    for k, a in o["aggregate"].items():
        L.append(f"| {names[k]} | {a['n_keys']} | {f(a['gm'], 3)} | {f(a['ci90'][0], 3)}–{f(a['ci90'][1], 3)} | "
                 f"{f(a['ci95'][0], 3)}–{f(a['ci95'][1], 3)} |")
    L += ["", "## Rapports par clé (nouveau / binaire de la campagne en P0, même hôte)\n",
          "| Clé | P0 (ms) | P1 | P2 | .NET 11 |", "|---|---|---|---|---|"]
    for k, r in o["r_full"].items():
        st = o["r_steady"].get(k)
        L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['ratio'], 3)} ({f(r['ci'][0], 2)}–{f(r['ci'][1], 2)}) | "
                 + (f"{f(st['ratio'], 3)} ({f(st['ci'][0], 2)}–{f(st['ci'][1], 2)})" if st else "—") + " | "
                 f"{f(o['r_net11'][k]['ratio'], 3)} ({f(o['r_net11'][k]['ci'][0], 2)}–{f(o['r_net11'][k]['ci'][1], 2)}) |")
    L += ["", "## Formes de la remarque, threads du pool, autres choix de code naturel\n",
          "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|---|"]
    for lab, dd in (("csharp_exp / csharp (P0)", o["r_exp"]), ("csharp_exp_full / csharp (P1 sur P0)", o["r_exp_full"]),
                    ("mt_pool / mt (csharp_exp)", o["r_pool"]), ("csharp_nat2 / csharp", o["r_nat"]),
                    ("témoins", o["r_controls"]), ("K4 SIMD / sans branchement", {"k4": o["r_k4simd"]}),
                    ("K8 en pile explicite (C)", o["r_c8"])):
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "Empreinte de K1 (octets par particule, méthode en deux points) : "
          + "; ".join(f"{impl} {f(v, 2)}" for impl, v in o["footprint_median"].items()) + ".\n",
          "## Report sur les données principales (transfert ou pont par le C de clang)\n",
          "| Clé | C# (données principales) | Transfert | Pont | Écart | Retenu |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        L.append(f"| {k} | {f(b['csharp_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de C# | C | E | D | Rang espéré | Place | Rang 90 % | Devant C# (écart) | Min. des 13 premiers devant C# |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | "
                 f"{NAMES.get(z['ahead'], z['ahead'])} ({f(z['gap_ahead'])}) | {f(100 * z['min_prec_top13'], 0)} % |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:16]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_csharp.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
