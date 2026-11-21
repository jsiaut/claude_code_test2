#!/usr/bin/env python3
"""v4, point 3 : contrôle descriptif, hors plan (docs/V4_EQUAL.md, 11.6), écrit après la première exécution de
analysis/equal_v4.py.

Dans les calculs R1, R1', Toutes et « Toutes, R1' » du plan (section 8), la cellule K8 naturelle d'un langage dont le
mode change prend, avec ses temps, les latences de ses nouveaux processus (part D3 du code par défaut : p99,9 et
maximum de la latence d'une itération, rapportés aux meilleurs des 25 langages). Ces latences, le maximum surtout,
varient d'un processus à l'autre beaucoup plus que les temps. Ce contrôle refait ces quatre calculs en gardant les
latences de K8 des binaires publiés (les temps des nouvelles cellules sont substitués, pas les latences), pour montrer
ce qui, dans les déplacements, tient à ces latences. Il ne remplace pas les calculs du plan.

Sortie : results/equal/lat_check.txt. Variables : BOOT (2000), UA (20000), comme analysis/equal_v4.py."""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import equal_v4 as E  # noqa: E402
import sizes_v4 as S  # noqa: E402
import analyze_v2 as v2  # noqa: E402

OUT = os.path.join(E.ROOT, "results", "equal", "lat_check.txt")
CALCS = ["R1", "R1'", "Toutes", "Toutes, R1'"]


def main():
    v2.ADDED.clear()
    data, lat, _, _, _ = E.load()
    for b in list(lat):
        if b != "pub":
            lat[b] = {}  # aucune latence nouvelle : celles des binaires publiés restent (scenario_data)
    c3 = json.load(open(os.path.join(E.ROOT, "results", "vectorization.json")))
    fp = json.load(open(os.path.join(E.ROOT, "results", "footprint.json")))
    hw = E.hw32()
    eb = S.ebounds(hw, 1)
    eb[("k5", 0)] = S.ebounds(hw, 0)[("k5", 0)]
    b3, _ = E.b3_value()
    langs = list(E.RANKED)
    keys = S.campaign_keys({"pub": data["pub"]})
    plan = json.load(open(E.OUT))["results"]
    h = plan["Hôte"]["order"]
    L = [f"# Contrôle hors plan (analysis/equal_v4_lat.py), {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} :",
         "# calculs du plan refaits avec les latences de K8 des binaires publiés (temps substitués, latences gardées).",
         "# Par calcul : places (plan → contrôle) des langages dont la place diffère ; plus de deux places contre « Hôte »."]
    for c in CALCS:
        r = E.run_calc(c, data, lat, langs, fp, c3, eb, b3, keys)
        diff = [f"{E.NAMES[l]} {plan[c]['order'].index(l) + 1} → {r['order'].index(l) + 1}"
                for l in plan[c]["order"] if plan[c]["order"].index(l) != r["order"].index(l)]
        mv_p = S.moved(h, plan[c]["order"], langs)
        mv_c = S.moved(h, r["order"], langs)
        fmt = lambda mv: ", ".join(f"{E.NAMES[l]} {a}e → {b}e" for l, (a, b) in sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"  # noqa: E731
        L += [f"{c} : places qui diffèrent : {', '.join(diff) or 'aucune'}",
              f"  plus de deux places contre « Hôte », plan : {fmt(mv_p)}",
              f"  plus de deux places contre « Hôte », contrôle : {fmt(mv_c)}",
              "  ordre du contrôle : " + ", ".join(f"{E.NAMES[l]} {r['exp'][l]:.2f}" for l in r["order"])]
        print("\n".join(L[-4:]), flush=True)
    open(OUT, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
