#!/usr/bin/env python3
"""Remarque sur Odin (plan : docs/ODIN.md, section 3), poussé avant les mesures.

Classement publié : erratum C2 = 1 en règle v2 (surcharge inscrite dans analysis/capabilities_v2.py). Le plan y
ajoutait la correction du banc (noyaux isolés de la boucle de mesure : rapports odin_fix / odin_ref sur les 14 clés dont
le noyau était inliné), reportée sur les données principales par la règle du pont de analysis/transfer_check.py.
Écart au plan, décidé après avoir vu les rapports (docs/ODIN.md, 4.2) : la correction n'est pas reportée. Les boucles
chaudes des noyaux isolés sont celles du binaire de la campagne, au renommage des registres près
(tools/odin_check/codegen.py, results/odin_check/codegen.txt), sauf K1 aos (attribut retiré), K5 naturel (vérification
de bornes restée dans la boucle) et la boucle externe de K9 naturel ; à code identique, un rapport mesuré sur un autre
processeur ne porte qu'un effet de placement propre à ce processeur, et le temps mesuré sur la machine de référence
reste le meilleur estimateur. Les reports par transfert seul et par la règle du plan sont calculés en information ;
results/transfers.json ne reçoit rien d'Odin. Les corrections publiées des autres langages sont appliquées.
Scénarios (analyse globale de la v3 rejouée, mêmes tirages) :
* Avant : sans l'erratum (doit reproduire le scénario Errata de results/c3_check.json) ; Publié : avec l'erratum.
* Information : Fix-T (Publié, plus la correction par transfert seul sur les 14 clés), Fix-T sans K4, Fix-pont (plan)
  (Publié, plus la correction par la règle du pont : le classement publié que prévoyait le plan).
* S-Q1 : Publié, plus Q1 tuned et mt x odin_q1 / odin_fix (règle du pont) ; S-agg : Publié, plus les 27 clés x
  odin_agg / odin_fix (transfert seul) ; S-Q1+agg : les deux.
* H-fm (information, hors règle) : Publié avec C4 = 1 ; H-tout : S-Q1+agg avec C4 = 1.
Sorties : results/odin_check.json, results/report_odin.md."""
import glob, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
from fortran_check import ratio  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "tools"))
from measure_odin import SCORE, FIX_KEYS, Q1T, Q1M  # noqa: E402

RAW = os.path.join(ROOT, "results", "raw_odin")
LANG = "odin"
LIMIT = 0.25
TRANSFER_ONLY = {("k9", "natural", ""), ("k1", "aos", "energy")}


def kk(k):
    return ":".join(x for x in k if x)


def load_raw():
    d, bad = defaultdict(dict), []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("tag") != "odin":
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
    return d, bad


def gm(procs):
    return math.exp(proc_logs(procs).mean())


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
            "prec_odin": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def run(data, lat, langs, footprint, c3, c2=True, c4=None):
    """Scénario : surcharge v2 de C2 présente ou retirée, C4 (règle v1, sans surcharge v2) remplacé le temps du
    calcul ; la matrice est restaurée ensuite."""
    saved_o = v2.V2_OVERRIDES.get((LANG, "C2"))
    saved_c4 = v2.MATRIX[LANG]["C4"]
    try:
        if not c2:
            v2.V2_OVERRIDES.pop((LANG, "C2"), None)
        if c4 is not None:
            v2.MATRIX[LANG]["C4"] = (c4, saved_c4[1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        if saved_o is not None:
            v2.V2_OVERRIDES[(LANG, "C2")] = saved_o
        v2.MATRIX[LANG]["C4"] = saved_c4


def main():
    assert v2.V2_OVERRIDES.get((LANG, "C2"), (None,))[0] == 1, "erratum C2 (v2) absent de analysis/capabilities_v2.py"
    assert v2.MATRIX[LANG]["C2"][0] == 0.5 and (LANG, "C4") not in v2.V2_OVERRIDES
    data, lat, *_ = v2.dataset_main(transfers=False)
    tpath = os.path.join(ROOT, "results", "transfers.json")
    tr = json.load(open(tpath))
    for lang, keys in tr["ratios"].items():  # corrections publiées des autres langages, sans celles d'Odin
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 800)
    R = lambda new, old, k: ratio(raw[new][k], raw[old][k], rng)  # noqa: E731
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_fix = {k: R("odin_fix", "odin_ref", k) for k in SCORE}
    r_q1 = {k: R("odin_q1", "odin_fix", k) for k in (Q1T, Q1M)}
    r_agg = {k: R("odin_agg", "odin_fix", k) for k in SCORE}
    r_eq = {k: R("odin_ref", "c", k) for k in FIX_KEYS + [Q1T, Q1M]}
    agg_gm = math.exp(float(np.mean([proc_logs(raw["odin_agg"][k]).mean() - proc_logs(raw["odin_fix"][k]).mean()
                                     for k in SCORE])))
    ctl_gm = math.exp(float(np.mean([proc_logs(raw["odin_fix"][k]).mean() - proc_logs(raw["odin_ref"][k]).mean()
                                     for k in SCORE if k not in FIX_KEYS])))
    main_eq = {kk(k): gm(data[LANG][k]) / gm(data["c"][k]) for k in FIX_KEYS + [Q1T, Q1M]}
    transfer = {}

    def bridged(base, key, r, new_impl, label, transfer_only=False):
        t_main = gm(base[LANG][key])
        trf = t_main * r
        br = gm(base["c"][key]) * gm(raw[new_impl][key]) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT and not transfer_only
        used = (br / t_main) if use else r
        transfer[f"{label} {kk(key)}"] = {"odin_main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br,
                                          "gap": gap, "bridge_used": use, "transfer_only": transfer_only, "ratio": r,
                                          "ratio_used": used, "c_main_ms": 1e3 * gm(base["c"][key])}
        return used

    fix_b = {k: bridged(data, k, r_fix[k]["ratio"], "odin_fix", "Fix", k in TRANSFER_ONLY) for k in FIX_KEYS}
    fix_t = {k: r_fix[k]["ratio"] for k in FIX_KEYS}
    pub = data  # publié : l'erratum seul, sans report de la correction du banc (écart au plan, docs/ODIN.md 4.2)
    q1_b = {k: bridged(pub, k, r_q1[k]["ratio"], "odin_q1", "S-Q1") for k in (Q1T, Q1M)}
    agg_t = {k: r_agg[k]["ratio"] for k in SCORE}
    q1agg = dict(agg_t)
    for k, r in q1_b.items():
        q1agg[k] = q1agg[k] * r
    plans = {"Avant": (data, False, None), "Publié": (pub, True, None),
             "Fix-T": (scaled(data, fix_t), True, None),
             "Fix-T sans K4": (scaled(data, {k: r for k, r in fix_t.items() if k[0] != "k4"}), True, None),
             "Fix-pont (plan)": (scaled(data, fix_b), True, None),
             "S-Q1": (scaled(pub, q1_b), True, None), "S-agg": (scaled(pub, agg_t), True, None),
             "S-Q1+agg": (scaled(pub, q1agg), True, None), "H-fm": (pub, True, 1),
             "H-tout": (scaled(pub, q1agg), True, 1)}
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()},
           "fix_keys": [kk(k) for k in FIX_KEYS], "r_q1": {kk(k): r for k, r in r_q1.items()},
           "r_agg": {kk(k): r for k, r in r_agg.items()}, "agg_gm": agg_gm, "control_gm": ctl_gm,
           "r_eq": {kk(k): r for k, r in r_eq.items()}, "main_eq": main_eq, "transfer": transfer,
           "ratios_transfer": {kk(k): v for k, v in fix_t.items()},
           "ratios_plan": {kk(k): v for k, v in fix_b.items()}, "scenarios": {}}
    for name, (d, c2, c4) in plans.items():
        z = out["scenarios"][name] = run(d, lat, langs, footprint, c3, c2=c2, c4=c4)
        po = z["prec_odin"]
        print(f"{name} : Odin {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.1f}, D {z['D'][LANG]:.1f}, "
              f"rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e ; C++ {z['exp21']['cpp']:.2f}), devant C++ "
              f"{100 * po['cpp']:.0f} %, devant Zig {100 * po['zig']:.0f} %", flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "c3_check.json")))["scenarios"]["Errata"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant la remarque = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(ROOT, "results", "odin_check.json"), "w"), indent=1, default=float)
    assert LANG not in tr["ratios"], "results/transfers.json ne doit rien recevoir d'Odin (docs/ODIN.md, 4.2)"
    report(out)


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def report(o):
    L = ["# Remarque sur Odin : rapports appariés et scénarios\n",
         "Plan : `docs/ODIN.md`. Mesures : `results/raw_odin/` (machine 14, 7 processus par cellule). Code :",
         "`analysis/odin_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le publié d'avant la remarque (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte)\n", "| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |",
         "|---|---|---|---|---|---|"]
    for k, r in o["r_fix"].items():
        lab = "odin_fix / odin_ref" + (" (corrigée)" if k in o["fix_keys"] else " (témoin)")
        L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                 f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    for lab, dd in (("odin_q1 / odin_fix", o["r_q1"]), ("odin_agg / odin_fix", o["r_agg"])):
        for k, r in dd.items():
            L.append(f"| {lab} | {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 3)} | "
                     f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    L += ["", f"Témoins (13 clés non corrigées), odin_fix / odin_ref en moyenne géométrique : {f(o['control_gm'], 3)}.",
          f"`-o:aggressive` / `-o:speed`, moyenne géométrique des {len(o['r_agg'])} clés : {f(o['agg_gm'], 3)}.\n",
          "## Odin et C sur les clés témoins du pont (information)\n",
          "| Clé | C, hôte (ms) | Odin, hôte (ms) | Odin / C, hôte [IC 95 %] | Odin / C, données principales |",
          "|---|---|---|---|---|"]
    for k, r in o["r_eq"].items():
        L.append(f"| {k} | {f(r['old_ms'], 2)} | {f(r['new_ms'], 2)} | {f(r['ratio'], 2)} [{f(r['ci'][0], 2)}–"
                 f"{f(r['ci'][1], 2)}] | {f(o['main_eq'][k], 2)} |")
    L += ["", "## Report sur les données principales (transfert ou pont par le C de la campagne)\n",
          "Lignes « Fix » : information seulement, la correction du banc n'est pas reportée (écart au plan, `docs/ODIN.md`",
          "4.2) ; la colonne « Règle du plan » donne ce que la règle du pont aurait retenu (scénario « Fix-pont (plan) »).",
          "Lignes S-Q1 : règle du plan (sensibilité).\n",
          "| Clé | Odin (données principales) | Transfert | Pont | Écart | Règle du plan |", "|---|---|---|---|---|---|"]
    for k, b in o["transfer"].items():
        how = "transfert seul (fixé d'avance)" if b["transfer_only"] else ("pont" if b["bridge_used"] else "transfert")
        L.append(f"| {k} | {f(b['odin_main_ms'], 2)} ms | {f(b['transfer_ms'], 2)} ms | {f(b['bridge_ms'], 2)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {how} ({f(b['ratio_used'], 3)}) |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score d'Odin | C | E | D | Rang espéré (C++) | Place | Rang 90 % | Devant C++ | Devant Zig | C 1er |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        po = z["prec_odin"]
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG])} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} ({f(z['exp21']['cpp'], 2)}) | {z['pos']} | "
                 f"{z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {f(100 * po['cpp'], 0)} % | {f(100 * po['zig'], 0)} % | "
                 f"{f(100 * z['first']['c'], 0)} % |")
    L.append("")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][:14]))
        L.append(f"**{name}** : {top}.\n")
    open(os.path.join(ROOT, "results", "report_odin.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
