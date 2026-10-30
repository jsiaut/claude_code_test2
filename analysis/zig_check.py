#!/usr/bin/env python3
"""Vérification de la remarque sur Zig (plan : docs/ZIG.md, section 3.3, poussé avant les mesures ; ce code est poussé
avant son premier calcul sur les mesures nouvelles).

Rapports appariés mesurés sur la machine 5 (results/raw_zig, tools/measure_zig.py) : zig_master, zig_io et
zig_master_io contre zig (Zig 0.17.0). Ils sont transférés aux processus de Zig des données principales, puis l'analyse
globale de la v3 est rejouée (analysis/confrontation.py : mêmes 20 000 variantes, même graine). Tous les scénarios
portent la correction de F4 (matrice v1, analysis/capabilities.py).

A'    : classement publié, avec la seule correction de F4.
S1    : Zig 0.18.0-dev (les 27 clés du score ; C3 de Zig = celle mesurée pour zig_master).
S1-K5 : S1 sans transfert pour K5 (données principales de K5 prises sur la machine 3).
S2    : S1, avec Io.Group pour les 5 clés à threads (zig_master_io).
S3    : Zig 0.17 avec Io.Group pour les 5 clés à threads (zig_io).
Témoin : rapport Zig/C sur les 5 clés de C, sur la machine 5 et dans les données principales.
Sorties : results/zig_check.json et results/report_zig.md. Variables : BOOT (2000), UA (20000)."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, c_cells  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from measure_zig import SCORE_KEYS, THREAD_KEYS, C_KEYS  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_zig")
NEW = ("zig_master", "zig_io", "zig_master_io")


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "zig":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return d, bad


def ratio(new, old, rng, nb=2000):
    yo, yn = proc_logs(old), proc_logs(new)
    bs = [math.exp(yn[rng.integers(0, len(yn), len(yn))].mean() - yo[rng.integers(0, len(yo), len(yo))].mean())
          for _ in range(nb)]
    return {"ratio": float(math.exp(yn.mean() - yo.mean())), "ci": [float(np.quantile(bs, 0.025)),
                                                                   float(np.quantile(bs, 0.975))],
            "n_new": len(yn), "n_old": len(yo), "old_ms": 1e3 * math.exp(yo.mean()), "new_ms": 1e3 * math.exp(yn.mean())}


def scaled(data, factors):
    """Copie des données principales, processus de Zig multipliés par le rapport de chaque clé."""
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d["zig"][key] = [[t * r for t in p] for p in data["zig"][key]]
    return d


def summary(s, lang="zig"):
    i = RANKED.index(lang)
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    pos = order.index(lang)
    nb = {}
    if pos > 0:
        nb["devant"] = (order[pos - 1], float(s["prec"][i, RANKED.index(order[pos - 1])]))
    if pos < len(order) - 1:
        nb["derrière"] = (order[pos + 1], float(s["prec"][i, RANKED.index(order[pos + 1])]))
    A = s["A"]
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "E": {l: s["E"][l] for l in RANKED},
            "D": {l: s["D"][l] for l in RANKED}, "C": {l: s["C"][l] for l in RANKED},
            "D1": {l: float(s["S0"]["D1"][A.idx[l]]) for l in RANKED},
            "Ek_zig": s["Ek"][lang], "pos": pos + 1, "neighbours": nb,
            "prec_zig": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != lang}}


def main():
    assert v2.MATRIX["zig"]["F4"][0] == 1, "correction de F4 absente de la matrice v1"
    data, lat, *_ = v2.dataset_main()
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 30)
    ratios = {impl: {key: ratio(raw[impl][key], raw["zig"][key], rng) for key in raw.get(impl, {})} for impl in NEW}
    missing = [(impl, k) for impl, keys in (("zig_master", SCORE_KEYS), ("zig_io", THREAD_KEYS),
                                            ("zig_master_io", THREAD_KEYS)) for k in keys if k not in ratios[impl]]
    assert not missing, f"cellules manquantes : {missing}"
    witness = {}
    for key in C_KEYS:
        here = math.exp(proc_logs(raw["zig"][key]).mean() - proc_logs(raw["c"][key]).mean())
        main_ = math.exp(proc_logs(data["zig"][key]).mean() - proc_logs(data["c"][key]).mean())
        witness[":".join(key)] = {"zig_over_c_here": here, "zig_over_c_main": main_,
                                  "zig_here_ms": 1e3 * math.exp(proc_logs(raw["zig"][key]).mean()),
                                  "c_here_ms": 1e3 * math.exp(proc_logs(raw["c"][key]).mean()),
                                  "zig_main_ms": 1e3 * math.exp(proc_logs(data["zig"][key]).mean()),
                                  "c_main_ms": 1e3 * math.exp(proc_logs(data["c"][key]).mean())}
    host = {":".join(k): 1e3 * math.exp(proc_logs(raw["zig"][k]).mean()) / (1e3 * math.exp(proc_logs(data["zig"][k]).mean()))
            for k in SCORE_KEYS}
    c3m = dict(c3)
    c3m["zig"] = c3["zig_master"]
    rm = {k: r["ratio"] for k, r in ratios["zig_master"].items()}
    plans = {
        "A'": (data, c3),
        "S1": (scaled(data, rm), c3m),
        "S1-K5": (scaled(data, {k: (1.0 if k[0] == "k5" else r) for k, r in rm.items()}), c3m),
        "S2": (scaled(data, {**rm, **{k: ratios["zig_master_io"][k]["ratio"] for k in THREAD_KEYS}}), c3m),
        "S3": (scaled(data, {k: ratios["zig_io"][k]["ratio"] for k in THREAD_KEYS}), c3),
    }
    out = {"bad": bad, "c3": {"zig": c3["zig"], "zig_master": c3["zig_master"]},
           "C_v1_zig": {name: float(v2.c_score(c_cells("v1", c), {k: w for k, (w, _) in v2.CATEGORIES.items()})["zig"])
                        for name, c in (("0.17", c3), ("master", c3m))},
           "ratios": {impl: {":".join(k): r for k, r in rs.items()} for impl, rs in ratios.items()},
           "witness_c": witness, "host_vs_main_zig": host, "scenarios": {}}
    for name, (d, c3x) in plans.items():
        s = cf.scenario(d, lat, langs, footprint, c3x, "main")
        out["scenarios"][name] = summary(s)
        z = out["scenarios"][name]
        print(f"{name} : Zig {z['ms0']['zig']:.1f} points, rang espéré {z['exp21']['zig']:.2f} ({z['pos']}e), "
              f"rang 90 % {z['rank90']['zig']}", flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "zig_check.json"), "w"), indent=1, default=float)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    S = o["scenarios"]
    L = ["# Remarque sur Zig : rapports appariés et scénarios\n",
         "Plan : `docs/ZIG.md`. Mesures : `results/raw_zig/` (machine 5, 7 processus par cellule). Code :",
         "`analysis/zig_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".\n",
         f"Vectorisation mesurée de la boucle chaude (C3, règle v1) : Zig 0.17 {f(o['c3']['zig'], 1)}, Zig master "
         f"{f(o['c3']['zig_master'], 1)}. Contrôle de Zig en règle v1 : {f(o['C_v1_zig']['0.17'])} avec 0.17, "
         f"{f(o['C_v1_zig']['master'])} avec master (F4 corrigée dans les deux).\n",
         "## Rapports appariés (nouvelle implémentation / Zig 0.17, machine 5)\n",
         "| Clé | Zig 0.17 (ms) | master | IC 95 % | 0.17 + Io.Group | master + Io.Group |", "|---|---|---|---|---|---|"]
    R = o["ratios"]
    for k in [":".join(x) for x in SCORE_KEYS]:
        m = R["zig_master"][k]
        io = R["zig_io"].get(k)
        mio = R["zig_master_io"].get(k)
        L.append(f"| {k} | {f(m['old_ms'], 2)} | {f(m['ratio'], 3)} | {f(m['ci'][0], 3)}–{f(m['ci'][1], 3)} | "
                 f"{f(io['ratio'], 3) if io else '—'} | {f(mio['ratio'], 3) if mio else '—'} |")
    L += ["", "## Témoin du même hôte : Zig 0.17 / C\n", "| Clé | Zig (ms) | C (ms) | Zig/C ici | Zig/C données principales |",
          "|---|---|---|---|---|"]
    for k, w in o["witness_c"].items():
        L.append(f"| {k} | {f(w['zig_here_ms'], 2)} | {f(w['c_here_ms'], 2)} | {f(w['zig_over_c_here'], 2)} | "
                 f"{f(w['zig_over_c_main'], 2)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Zig | Plafond E | D1 | Contrôle C | Rang espéré | Place | Rang 90 % | Devance le suivant |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in S.items():
        nb = z["neighbours"].get("derrière")
        L.append(f"| {name} | {f(z['ms0']['zig'])} | {f(z['E']['zig'])} | {f(100 * z['D1']['zig'], 1)} | "
                 f"{f(z['C']['zig'])} | {f(z['exp21']['zig'], 2)} | {z['pos']} | {z['rank90']['zig'][0]}–"
                 f"{z['rank90']['zig'][1]} | {NAMES[nb[0]] + ' ' + f(100 * nb[1], 0) + ' %' if nb else '—'} |")
    for name in S:
        z = S[name]
        L.append(f"\n**{name}** : " + ", ".join(f"{i + 1}. {NAMES[l]} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                                              for i, l in enumerate(z["order21"][:10])) + ".")
    text = "\n".join(L) + "\n"
    open(os.path.join(ROOT, "results", "report_zig.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
