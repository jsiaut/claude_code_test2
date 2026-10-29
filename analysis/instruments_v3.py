#!/usr/bin/env python3
"""Analyse des compteurs du noyau et du pilote de contrôle du bruit (plan : docs/INSTRUMENTS_V3.md).
Entrées : results/raw_v3/instruments_count.jsonl, instruments_alloc.jsonl, noise_pilot.jsonl.
Sorties : results/summary_instruments_v3.json, results/report_instruments_v3.md."""
import json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_v2 import NAMES, ROOT, fr, spearman  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_v3")
SEED = 20261029 + 600
NAMES = dict(NAMES, c_gcc="C (gcc)", fortran_flang="Fortran (flang)", js_bun="JS (Bun)", luajit="LuaJIT")
ORDER = ["c", "c_gcc", "cpp", "rust", "zig", "odin", "c3", "d", "nim", "ada", "fortran", "fortran_flang", "chapel",
         "julia", "mojo", "csharp", "java", "go", "haskell", "ocaml", "js", "js_bun", "python", "lua", "luajit"]
CELL_NAMES = {"k1:natural:energy": "K1 naturel", "k3:sw_padded:": "K3 écrivain unique", "k6:natural:q1": "K6 Q1 naturel",
              "k7:natural:": "K7 naturel", "k8:natural:": "K8 naturel", "k8:tuned:": "K8 tuned", "k9:natural:": "K9 naturel"}


def load(name):
    path = os.path.join(RAW, name)
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


def valid(r):
    return (r["rc"] == 0 and not r["timed_out"] and r["counts"] and len(r["reps"]) == r["reps_asked"]
            and all(x["ok"] is True for x in r["reps"]))


def per_rep(records):
    """Méthode des deux points : comptes par répétition = (c(R2) − c(R1)) / (R2 − R1)."""
    by = defaultdict(dict)
    bad = []
    for r in records:
        key = (r["lang"], f"{r['kernel']}:{r['variant']}:{r['param']}")
        if not valid(r):
            bad.append({"lang": r["lang"], "cell": key[1], "reps": r["reps_asked"], "rc": r["rc"], "timed_out": r["timed_out"]})
            continue
        by[key][r["reps_asked"]] = r
    out = {}
    for key, runs in by.items():
        if len(runs) < 2:
            continue
        r1, r2 = sorted(runs)[:2]
        a, b = runs[r1], runs[r2]
        names = set(a["counts"]) & set(b["counts"])
        d = {n: (b["counts"][n] - a["counts"][n]) / (r2 - r1) for n in names}
        t = float(np.median([x["sec"] for x in a["reps"] + b["reps"]]))
        d["time_per_rep_s"] = t
        if "task_clock_ns" in d:
            d["cpu_per_rep_s"] = d["task_clock_ns"] / 1e9
            d["cpu_over_wall"] = d["cpu_per_rep_s"] / t if t > 0 else None
        out[key] = d
    return out, bad


def noise_analysis(records, nb=2000):
    rng = np.random.default_rng(SEED)
    groups = defaultdict(list)
    rows = []
    for r in records:
        if not valid(r):
            continue
        y = math.log(float(np.median([x["sec"] for x in r["reps"]])))
        combo = f"{r['lang']}:{r['kernel']}:{r['variant']}:{r['param']}"
        groups[(combo, r["protocol"])].append(y)
        wall = max(r["wall"], 1e-9)
        rows.append({"combo": combo, "protocol": r["protocol"], "y": y,
                     "psi_cpu_some_per_s": r["psi_delta_us"].get("cpu_some", 0) / wall,
                     "psi_mem_some_per_s": r["psi_delta_us"].get("memory_some", 0) / wall,
                     "steal_per_s": r["steal_delta_ticks"].get("cpu", 0) / wall,
                     "context_switches": r["counts"].get("context_switches", 0),
                     "cpu_migrations": r["counts"].get("cpu_migrations", 0)})
    combos = sorted({c for c, _ in groups})
    res = {"combos": {}}
    boots = {p: [] for p in "BC"}
    for c in combos:
        ya = np.array(groups.get((c, "A"), []))
        entry = {}
        for p in "ABC":
            y = np.array(groups.get((c, p), []))
            entry[p] = {"n": len(y), "sd": float(np.std(y, ddof=1)) if len(y) > 1 else None,
                        "median_ms": 1e3 * math.exp(float(np.median(y))) if len(y) else None}
        for p in "BC":
            yp = np.array(groups.get((c, p), []))
            if len(ya) > 2 and len(yp) > 2:
                ratio = float(np.std(yp, ddof=1) / np.std(ya, ddof=1))
                bs = []
                for _ in range(nb):
                    ra = ya[rng.integers(0, len(ya), len(ya))]
                    rp = yp[rng.integers(0, len(yp), len(yp))]
                    sa = np.std(ra, ddof=1)
                    bs.append(np.std(rp, ddof=1) / sa if sa > 0 else np.nan)
                bs = np.array(bs)
                boots[p].append(np.log(bs))
                entry[f"ratio_{p}"] = {"value": ratio, "ci": [float(np.nanquantile(bs, 0.025)), float(np.nanquantile(bs, 0.975))]}
        res["combos"][c] = entry
    for p in "BC":
        vals = [res["combos"][c][f"ratio_{p}"]["value"] for c in combos if f"ratio_{p}" in res["combos"][c]]
        if vals:
            gm = float(np.exp(np.mean(np.log(vals))))
            stacked = np.exp(np.nanmean(np.vstack(boots[p]), axis=0))
            res[f"pooled_{p}"] = {"value": gm, "ci": [float(np.nanquantile(stacked, 0.025)), float(np.nanquantile(stacked, 0.975))],
                                  "reduces_noise": bool(gm < 0.7 and np.nanquantile(stacked, 0.975) < 1)}
    # lenteur d'un processus (écart à la moyenne de sa mesure et de son protocole) contre les indicateurs, protocole A
    mean = defaultdict(list)
    for r in rows:
        mean[(r["combo"], r["protocol"])].append(r["y"])
    mu = {k: float(np.mean(v)) for k, v in mean.items()}
    ra = [r for r in rows if r["protocol"] == "A"]
    res["indicators_A"] = {}
    for ind in ("psi_cpu_some_per_s", "psi_mem_some_per_s", "steal_per_s", "context_switches", "cpu_migrations"):
        x = [r[ind] for r in ra]
        y = [r["y"] - mu[(r["combo"], "A")] for r in ra]
        rho, n = spearman(x, y)
        res["indicators_A"][ind] = {"rho": rho, "n": n, "usable": bool(rho is not None and abs(rho) >= 0.5)}
    return res


def main():
    count, bad_count = per_rep(load("instruments_count.jsonl"))
    alloc, bad_alloc = per_rep(load("instruments_alloc.jsonl"))
    noise = noise_analysis(load("noise_pilot.jsonl"))
    out = {"count": {f"{l}|{c}": v for (l, c), v in count.items()},
           "alloc": {f"{l}|{c}": v for (l, c), v in alloc.items()},
           "invalid_count": bad_count, "invalid_alloc": bad_alloc, "noise": noise}
    json.dump(out, open(os.path.join(ROOT, "results", "summary_instruments_v3.json"), "w"), indent=1)
    report(count, alloc, noise, bad_count, bad_alloc)


def g(v, d=0):
    if v is None:
        return "—"
    if abs(v) >= 1e5:
        return f"{v:.2e}".replace(".", ",")
    return fr(v, d)


def report(count, alloc, noise, bad_count, bad_alloc):
    L = ["# Compteurs du noyau et contrôle du bruit (plan : docs/INSTRUMENTS_V3.md)\n",
         "Comptes par répétition, méthode des deux points (le démarrage et l'échauffement s'annulent). Une valeur "
         "négative ou fractionnaire vient d'une activité qui n'est pas strictement proportionnelle au nombre de "
         "répétitions (ramasse-miettes, compilation à la volée, threads de fond).\n"]
    syscols = ["futex", "mmap", "munmap", "madvise", "brk", "mprotect", "clone3", "sched_yield", "write"]
    for cell, cname in CELL_NAMES.items():
        rows = [(l, count[(l, cell)]) for l in ORDER if (l, cell) in count]
        if not rows:
            continue
        L.append(f"## {cname} (`{cell}`)\n")
        L.append("| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | " +
                 " | ".join(f"`{s}`" for s in syscols) + " | Défauts de page | Changements de contexte | Migrations | "
                 "malloc + calloc + realloc | free |")
        L.append("|---" * (9 + len(syscols)) + "|")
        for l, d in rows:
            a = alloc.get((l, cell), {})
            nmal = sum(a.get(f"uprobe_{f}", 0) for f in ("malloc", "calloc", "realloc")) if a else None
            L.append(f"| {NAMES.get(l, l)} | {g(1e3 * d['time_per_rep_s'], 1)} | {g(d.get('cpu_over_wall'), 2)} | "
                     f"{g(d.get('syscalls'))} | " + " | ".join(g(d.get(f"sys_enter_{s}")) for s in syscols) +
                     f" | {g(d.get('page_faults'))} | {g(d.get('context_switches'))} | {g(d.get('cpu_migrations'))} | "
                     f"{g(nmal)} | {g(a.get('uprobe_free')) if a else '—'} |")
        L.append("")
    if bad_count or bad_alloc:
        L.append("## Exécutions écartées\n")
        for b in bad_count:
            L.append(f"* comptage : {NAMES.get(b['lang'], b['lang'])} {b['cell']} R={b['reps']} (code {b['rc']}"
                     + (", délai dépassé" if b["timed_out"] else "") + ")")
        for b in bad_alloc:
            L.append(f"* allocations : {NAMES.get(b['lang'], b['lang'])} {b['cell']} R={b['reps']} (code {b['rc']}"
                     + (", délai dépassé : trop d'appels pour une uprobe" if b["timed_out"] else "") + ")")
        L.append("")
    L.append("## Pilote de contrôle du bruit\n")
    L.append("Écart-type du logarithme des médianes de processus (12 processus par case). A : protocole de la campagne ; "
             "B : CPU 3, `SCHED_FIFO`, interruptions ailleurs ; C : B et taille d'environnement aléatoire.\n")
    L.append("| Mesure | Médiane A (ms) | σ A | σ B | σ C | B / A [IC 95 %] | C / A [IC 95 %] |")
    L.append("|---|---|---|---|---|---|---|")
    for c, e in noise["combos"].items():
        rb, rc_ = e.get("ratio_B"), e.get("ratio_C")
        L.append(f"| {c} | {g(e['A']['median_ms'], 2)} | {g(e['A']['sd'], 3)} | {g(e['B']['sd'], 3)} | {g(e['C']['sd'], 3)} | "
                 + (f"{g(rb['value'], 2)} [{g(rb['ci'][0], 2)}–{g(rb['ci'][1], 2)}]" if rb else "—") + " | "
                 + (f"{g(rc_['value'], 2)} [{g(rc_['ci'][0], 2)}–{g(rc_['ci'][1], 2)}]" if rc_ else "—") + " |")
    for p in "BC":
        pr = noise.get(f"pooled_{p}")
        if pr:
            L.append(f"\nMoyenne géométrique {p} / A : {g(pr['value'], 2)} [{g(pr['ci'][0], 2)}–{g(pr['ci'][1], 2)}] ; "
                     f"règle du plan (moins de 0,7, intervalle sous 1) : {'remplie' if pr['reduces_noise'] else 'non remplie'}.")
    L.append("\nIndicateurs de la lenteur d'un processus (protocole A, corrélation de rang ; règle du plan : |ρ| ≥ 0,5) :\n")
    for ind, v in noise["indicators_A"].items():
        L.append(f"* {ind} : ρ = {g(v['rho'], 2)} (n = {v['n']}) ; {'utilisable' if v['usable'] else 'non utilisable'}")
    text = "\n".join(L) + "\n"
    open(os.path.join(ROOT, "results", "report_instruments_v3.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
