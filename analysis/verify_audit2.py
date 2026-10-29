#!/usr/bin/env python3
"""Recalcul des affirmations chiffrées du second audit (docs/AUDIT2_2026-10-29.md) à partir des données du dépôt.
Lit results/summary_v2.json, results/raw (v1), results/raw_v2 (K5 et machine 3). Sortie : results/verify_audit2.txt.
Chaque bloc cite le paragraphe de l'audit qu'il vérifie."""
import json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
from analyze_v2 import E_V2, RANKED, ROOT, NAMES, spearman  # noqa: E402
from analyze_v3 import klass  # noqa: E402

OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


def inversions(r1, r2, ls):
    return sum(1 for i, a in enumerate(ls) for b in ls[i + 1:] if (r1[a] - r1[b]) * (r2[a] - r2[b]) < 0)


def main():
    o = json.load(open(os.path.join(ROOT, "results", "summary_v2.json")))
    R = o["results"]

    say("## § 4.3.1 : position du score MS dans son intervalle à 95 % (v2)")
    pos = {l: (R[l]["MS"] - R[l]["MS_ci"][0]) / (R[l]["MS_ci"][1] - R[l]["MS_ci"][0]) for l in RANKED}
    say(f"moyenne {np.mean(list(pos.values())):.2f} ; minimum {min(pos.values()):.2f} ({min(pos, key=pos.get)}) ; "
        f"C {pos['c']:.2f} ; au-dessus de 0,5 : {sum(p > 0.5 for p in pos.values())} sur {len(pos)}")

    say("\n## § 4.3.4 : accord entre la machine 1 (rang v2) et la machine 3")
    r1 = {l: R[l]["rank"] for l in RANKED}
    r3 = o["replication"]["ranking_m3"]
    order = sorted(RANKED, key=r1.get)
    for n in (21, 13, 9):
        ls = order[:n]
        rho, _ = spearman([r1[l] for l in ls], [r3[l] for l in ls])
        say(f"{n} premiers : Spearman {rho:.2f}, paires inversées {inversions(r1, r3, ls)} sur {n * (n - 1) // 2}")
    inv_all = [(a, b) for i, a in enumerate(order) for b in order[i + 1:] if (r1[a] - r1[b]) * (r3[a] - r3[b]) < 0]
    say(f"inversions hors des 13 premiers : {sum(1 for a, b in inv_all if r1[b] > 13)}")
    say("haut du classement, machine 3 : " + ", ".join(f"{NAMES[l]} {r3[l]}" for l in order[:9]))

    say("\n## § 4.3.5 : part de la variance de MS expliquée par chaque pilier, 13 premiers (R², v2)")
    top = order[:13]
    ms = np.array([R[l]["MS"] for l in top])
    for p in ("C", "E", "D"):
        x = np.array([R[l][p] for l in top])
        say(f"{p} : {np.corrcoef(x, ms)[0, 1] ** 2:.2f}")

    say("\n## § 4.6 : déplacement maximal par choix pris isolément ; K10 réintégré")
    dec = o["decomposition"]
    base = dec["v2"]
    for name, rk in dec.items():
        if name == "v2":
            continue
        shift = max(abs(rk[l] - base[l]) for l in RANKED)
        moved13 = sum(1 for l in order[:13] if rk[l] != base[l])
        first = min(RANKED, key=rk.get)
        say(f"{name} : déplacement maximal {shift}, {moved13} des 13 premiers bougent, premier : {NAMES[first]}")

    say("\n## § 4.2.3 : coupures de régime établi (v2)")
    cuts = o["steady_cuts"]
    fast = [c for c in cuts if c["after"] < c["before"]]
    by = defaultdict(lambda: [0, 0])
    for c in cuts:
        by[klass(c["lang"])][0 if c["after"] < c["before"] else 1] += 1
    say(f"{len(cuts)} coupures : {len(fast)} accélérations, {len(cuts) - len(fast)} ralentissements ; K5 : "
        f"{sum(1 for c in cuts if c['key'][0] == 'k5')}")
    for k, (a, b) in sorted(by.items()):
        say(f"  {k} : {a + b} coupures, {b} ralentissements")

    data, lat, invalid, sus, bridge, v1_k5, (k5, *_rest) = v2.dataset_main()

    say("\n## § 4.3.1 : biais de la frontière (bootstrap hiérarchique, 1 000 tirages, sans coupure de régime établi)")
    rng = np.random.default_rng(20261029 + 7)

    def med_of_meds(procs, boot):
        if not boot:
            return float(np.median([np.median(p) for p in procs]))
        pick = rng.integers(0, len(procs), size=len(procs))
        return float(np.median([np.median(np.asarray(procs[j])[rng.integers(0, len(procs[j]), size=len(procs[j]))])
                                for j in pick]))
    for k, meas in E_V2.items():
        for i, keys in enumerate(meas):
            ls = [l for l in RANKED if any(key in data.get(l, {}) for key in keys)]
            best = lambda l, boot: min(med_of_meds(data[l][key], boot) for key in keys if key in data[l])  # noqa: E731
            obs = {l: best(l, False) for l in ls}
            leader = min(obs, key=obs.get)
            tb, keep = [], 0
            for _ in range(1000):
                bl = {l: best(l, True) for l in ls}
                m = min(bl.values())
                tb.append(m)
                keep += bl[leader] == m
            P = sorted({len(data[l][key]) for l in ls for key in keys if key in data[l]})
            say(f"{k}:{i} ({P[0]}–{P[-1]} processus) : t* {1e3 * obs[leader]:.2f} ms ({NAMES[leader]}), médiane bootstrap "
                f"{1e3 * np.median(tb):.2f} ms, P(t*_b < t*) {np.mean(np.array(tb) < obs[leader]):.2f}, "
                f"P(le tenant garde 1) {keep / 1000:.2f}")

    say("\n## § 4.1.2 et § 4.2.2 : K5 sur la machine 3, médiane et extrêmes des médianes de processus (9 processus)")
    for var in ("natural", "tuned"):
        rows = []
        for l in k5:
            key = ("k5", var, "")
            if key in k5[l]:
                m = [float(np.median(p)) for p in k5[l][key]]
                rows.append((float(np.median(m)), l, min(m), max(m)))
        say(f"{var} : " + " ; ".join(f"{NAMES.get(l, l)} {1e3 * m:.2f} ({1e3 * a:.2f}–{1e3 * b:.2f})"
                                     for m, l, a, b in sorted(rows)))
    say("\nK5 natural sur la machine 1 (données v1, 2 ou 3 processus) : " + " ; ".join(
        f"{NAMES.get(l, l)} {1e3 * float(np.median([np.median(p) for p in v1_k5[l][('k5', 'natural', '')]])):.1f}"
        for l in sorted(v1_k5, key=lambda l: float(np.median([np.median(p) for p in v1_k5[l][('k5', 'natural', '')]])))
        if ("k5", "natural", "") in v1_k5[l]))

    say("\n## § 4.3.4 : corrélation de rang entre machines, mesure par mesure (21 langages classés, moyenne des "
        "logarithmes des médianes de processus)")
    m3, *_r = v2.load_raw("v2_m3")
    rows = []
    for key in sorted({k for l in data for k in data[l]}):
        ls = [l for l in RANKED if key in data.get(l, {}) and key in m3.get(l, {})]
        if len(ls) < 5 or key[0] == "k5":
            continue
        a = [np.mean(np.log([np.median(p) for p in data[l][key]])) for l in ls]
        b = [np.mean(np.log([np.median(p) for p in m3[l][key]])) for l in ls]
        rows.append((spearman(a, b)[0], ":".join(key)))
    rows.sort()
    say(f"{len(rows)} mesures, médiane {np.median([r[0] for r in rows]):.2f} ; les plus basses : "
        + " ; ".join(f"{k} {r:.2f}" for r, k in rows[:8]))
    open(os.path.join(ROOT, "results", "verify_audit2.txt"), "w").write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
