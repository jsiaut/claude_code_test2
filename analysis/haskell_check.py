#!/usr/bin/env python3
"""Remarque sur Haskell (plan : docs/HASKELL.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 19 (results/raw_haskell, étiquette « haskell »), reportés sur les données publiées de
Haskell ; analyse globale de la v3 rejouée (mêmes tirages) pour chaque scénario du plan (3.5) :
* Avant : le classement publié d'avant (B2 = B3 = A7 = 0) ; doit reproduire results/go_check.json (G-E).
* H-opt : options seules : r(haskell_rel / haskell_ref) pour les 4 clés dont le code change, r(haskell_fix /
  haskell_ref) pour les autres ; latences de K8 naturel × r(haskell_rel / haskell_ref).
* H-code : toutes les clés et les latences × r(haskell_fix / haskell_ref), matrice d'avant.
* H-M : errata B2 = B3 = A7 = 1/2 seuls.
* H-E (classement publié) : H-code et les errata.
* H-E-P (information) : H-E, mais chaque clé reportée par la règle du pont de analysis/transfer_check.py (C du même
  hôte au-delà de 25 % d'écart) et la règle de sens (le facteur retenu ne va pas contre le rapport mesuré).
* Sensibilités (sur H-E, en min(1, r) par rapport à H-E) : S-N1 (6 clés et latences × r(haskell_n1 / haskell_fix)),
  S-cases (C2 = 1/2, E7 = 1, F2 = 1/2), S-tout (les deux).
Report du classement publié : transfert seul (temps publié × rapport du même hôte), pour les temps comme pour les
latences (plan 3.2 : la correction touche les 36 clés, et le rapport de Haskell à C d'un même binaire change d'un
modèle d'hôte à l'autre ; le pont importerait cet écart comme une correction).
Les corrections publiées des autres langages (results/transfers.json) sont appliquées, puis K9 de la machine 16, comme
dans le calcul publié ; celles de Haskell en sont retirées pour le calcul, puis les rapports de H-E y sont écrits
(« ratios » ; « ratios_k9h » pour K9 ; « lat_ratios » pour les latences de K8 naturel). Les rapports de la réplication
(« replication_ratios », « replication_lat_ratios ») vont dans results/haskell_check.json. Sorties :
results/haskell_check.json, results/report_haskell.md ; results/transfers.json (Haskell)."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

RAW = os.environ.get("HS_RAW", os.path.join(ROOT, "results", "raw_haskell"))
TAG = os.environ.get("HS_TAG", "haskell")
OUT = os.environ.get("HS_OUT", os.path.join(ROOT, "results"))  # essai : sorties ailleurs, transferts non écrits
LANG = "haskell"
LIMIT = 0.25
CODE = [("k1", "soa", "energy"), ("k5", "tuned", ""), K8N, ("k8", "tuned", "")]
K9_KEYS = [("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")]
N1 = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
      ("k5", "natural", ""), K8N, ("k9", "natural", "")]
ERRATA = {"B2": 0.5, "B3": 0.5, "A7": 0.5}
BEFORE = {"B2": 0, "B3": 0, "A7": 0}
CASES = {"C2": 0.5, "E7": 1, "F2": 0.5}
LATCOLS = ["p50", "p90", "p99", "p99,9", "max"]


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, lat, bad = defaultdict(dict), defaultdict(list), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != TAG:
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            if key == K8N and r.get("lat"):
                lat[r["lang"]].append(r["lat"])
    return d, lat, bad


def gm(procs):
    return math.exp(proc_logs(procs).mean())


def lat_med(procs):
    """Estimateur de D3 : médiane, sur toutes les répétitions de tous les processus, de chaque colonne."""
    return np.median(np.vstack([np.asarray(p, float) for p in procs if len(p)]), axis=0)


def lat_ratio(new, old, rng, nb=2000):
    r = lat_med(new) / lat_med(old)
    bs = np.array([lat_med([new[i] for i in rng.integers(0, len(new), len(new))]) /
                   lat_med([old[i] for i in rng.integers(0, len(old), len(old))]) for _ in range(nb)])
    return {"ratio": r.tolist(), "ci_lo": np.quantile(bs, 0.025, axis=0).tolist(),
            "ci_hi": np.quantile(bs, 0.975, axis=0).tolist(), "old_us": (lat_med(old) / 1e3).tolist(),
            "new_us": (lat_med(new) / 1e3).tolist(), "n_new": len(new), "n_old": len(old)}


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
            "prec_h": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def scaled_lat(lat, r):
    out = {l: dict(v) for l, v in lat.items()}
    out[LANG][K8N] = v2.scale_lat(lat[LANG][K8N], r)
    return out


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de Haskell remplacées le temps du calcul."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def published_data():
    """Données du calcul publié, sans les corrections de Haskell : transferts des autres langages, K9 de la machine 16
    (et les corrections de K9 des autres langages), latences de la machine 11 (et les corrections de latence des
    autres langages)."""
    data, lat, *_ = v2.dataset_main(transfers=False, k9h=None)
    tr = json.load(open(os.path.join(ROOT, "results", "transfers.json")))
    for lang, keys in tr["ratios"].items():
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    for lang, r in tr.get("lat_ratios", {}).items():
        if lang != LANG and K8N in lat.get(lang, {}):
            lat[lang][K8N] = v2.scale_lat(lat[lang][K8N], r)
    v2.apply_k9h(data, "common", skip=(LANG,))
    v2.align_lat(data, lat)
    return data, lat, tr


def main():
    m = v2.MATRIX[LANG]
    assert {c: m[c][0] for c in ERRATA} == ERRATA, "errata B2, B3, A7 absents de analysis/capabilities.py"
    data, lat, tr = published_data()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, rawlat, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 600)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    keys = sorted(raw["haskell_ref"])
    r_fix = {k: ratio(raw["haskell_fix"][k], raw["haskell_ref"][k], rng) for k in keys}
    r_rel = {k: ratio(raw["haskell_rel"][k], raw["haskell_ref"][k], rng) for k in CODE}
    r_n1 = {k: ratio(raw["haskell_n1"][k], raw["haskell_fix"][k], rng) for k in N1}
    l_fix = lat_ratio(rawlat["haskell_fix"], rawlat["haskell_ref"], rng)
    l_rel = lat_ratio(rawlat["haskell_rel"], rawlat["haskell_ref"], rng)
    l_n1 = lat_ratio(rawlat["haskell_n1"], rawlat["haskell_fix"], rng)
    transfer = {}

    def bridged(label, key, base, r, new_procs, sens):
        """Facteur appliqué au temps publié : transfert (temps × base × r) ou pont par le C du même hôte au-delà de 25 %
        d'écart. Correction (sens faux) : règle de sens (pas contre r) ; sensibilité : plafonné à base."""
        t_main = gm(data[LANG][key])
        trf = t_main * base * r
        if key not in raw.get("c", {}):  # sans témoin du même hôte (essai sur la validation) : transfert
            return base * r
        br = gm(data["c"][key]) * gm(new_procs) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        f = (br if use else trf) / t_main
        if sens:
            used = min(base, f)
        else:
            used = min(1.0, f) if r < 1 else max(1.0, f)
        transfer[label] = {"key": kk(key), "main_ms": 1e3 * t_main, "base": base, "transfer_ms": 1e3 * trf,
                           "bridge_ms": 1e3 * br, "gap": gap, "bridge_used": use, "ratio": r, "factor": f,
                           "factor_used": used, "c_main_ms": 1e3 * gm(data["c"][key]),
                           "c_here_ms": 1e3 * gm(raw["c"][key])}
        return used

    fix_t = {k: r_fix[k]["ratio"] for k in keys}
    fix_b = {k: bridged(f"pont {kk(k)}", k, 1.0, r_fix[k]["ratio"], raw["haskell_fix"][k], False) for k in keys}
    opt_t = dict(fix_t)
    for k in CODE:
        opt_t[k] = r_rel[k]["ratio"]
    n1_t = dict(fix_t)
    for k in N1:
        n1_t[k] = fix_t[k] * min(1.0, r_n1[k]["ratio"])
    lat_fix = l_fix["ratio"]
    lat_opt = l_rel["ratio"]
    lat_n1 = [a * min(1.0, b) for a, b in zip(lat_fix, l_n1["ratio"])]
    plans = {"Avant": (data, lat, BEFORE),
             "H-opt": (scaled(data, opt_t), scaled_lat(lat, lat_opt), BEFORE),
             "H-code": (scaled(data, fix_t), scaled_lat(lat, lat_fix), BEFORE),
             "H-M": (data, lat, None),
             "H-E": (scaled(data, fix_t), scaled_lat(lat, lat_fix), None),
             "H-E-P": (scaled(data, fix_b), scaled_lat(lat, lat_fix), None),
             "S-N1": (scaled(data, n1_t), scaled_lat(lat, lat_n1), None),
             "S-cases": (scaled(data, fix_t), scaled_lat(lat, lat_fix), CASES),
             "S-tout": (scaled(data, n1_t), scaled_lat(lat, lat_n1), CASES)}
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()},
           "r_rel": {kk(k): r for k, r in r_rel.items()}, "r_n1": {kk(k): r for k, r in r_n1.items()},
           "lat_fix": l_fix, "lat_rel": l_rel, "lat_n1": l_n1, "transfer": transfer,
           "published_ratios": {kk(k): v for k, v in fix_t.items()}, "bridge_ratios": {kk(k): v for k, v in fix_b.items()},
           "published_lat_ratios": lat_fix,
           "replication_ratios": {"|".join(k): r["ratio"] for k, r in r_fix.items()},
           "replication_lat_ratios": lat_fix, "scenarios": {}}
    for name, (d, lt, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : Haskell {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "go_check.json")))["scenarios"]["G-E"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(OUT, "haskell_check.json"), "w"), indent=1, default=float)
    if OUT != os.path.join(ROOT, "results"):
        report(out)
        return
    # classement publié (3.2) : rapports de H-E inscrits dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in fix_t.items() if k not in K9_KEYS}
    tr.setdefault("ratios_k9h", {})[LANG] = {"|".join(k): v for k, v in fix_t.items() if k in K9_KEYS}
    tr.setdefault("lat_ratios", {})[LANG] = lat_fix
    note = (" ; Haskell : docs/HASKELL.md (3.2), results/raw_haskell, machine 19, results/haskell_check.json (K9 : "
            "ratios_k9h ; latences de K8 naturel : lat_ratios)")
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(os.path.join(ROOT, "results", "transfers.json"), "w"), indent=1)
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur Haskell : rapports appariés et scénarios\n",
         "Plan : `docs/HASKELL.md`. Mesures : `results/raw_haskell/` (machine 19, 7 processus par cellule, 4 pour K7",
         "naturel). Code : `analysis/haskell_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    for lab, dd in (("fix / ref", o["r_fix"]), ("rel / ref (options seules)", o["r_rel"]),
                    ("n1 / fix (sensibilité)", o["r_n1"])):
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", "## Latences de K8 naturel (médianes de toutes les répétitions, µs)\n",
          "| Rapport | " + " | ".join(LATCOLS) + " |", "|---|" + "---|" * len(LATCOLS)]
    for lab, x in (("fix / ref", o["lat_fix"]), ("rel / ref", o["lat_rel"]), ("n1 / fix", o["lat_n1"])):
        L.append(f"| {lab} : ancien | " + " | ".join(f(v, 0) for v in x["old_us"]) + " |")
        L.append(f"| {lab} : nouveau | " + " | ".join(f(v, 0) for v in x["new_us"]) + " |")
        L.append(f"| {lab} : rapport [IC 95 %] | " + " | ".join(
            f"{f(r, 3)} [{f(a, 2)}–{f(b, 2)}]" for r, a, b in zip(x["ratio"], x["ci_lo"], x["ci_hi"])) + " |")
    L += ["", "## Pont par le C de clang (information : scénario H-E-P ; le classement publié reporte par transfert)\n",
          "| Rapport | Clé | Haskell publié | Base | Transfert | Pont | Écart | Retenu | Facteur appliqué |",
          "|---|---|---|---|---|---|---|---|---|"]
    for lab, b in o["transfer"].items():
        L.append(f"| {lab} | {b['key']} | {f(b['main_ms'], 2)} ms | {f(b['base'], 3)} | {f(b['transfer_ms'], 2)} ms | "
                 f"{f(b['bridge_ms'], 2)} ms | {f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} | "
                 f"{f(b['factor_used'], 3)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Haskell | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:18]))
        L.append(f"**{name}** : {top}.\n")
    L.append("## Rapports reportés sur la réplication (machine 3)\n")
    L.append(", ".join(f"{k.replace('|', ':').rstrip(':')} {f(r, 3)}" for k, r in sorted(o["replication_ratios"].items()))
             + ".")
    L.append("\nLatences de K8 naturel : " + ", ".join(f"{c} {f(r, 3)}" for c, r in zip(LATCOLS, o["replication_lat_ratios"]))
             + ".")
    open(os.path.join(OUT, "report_haskell.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
