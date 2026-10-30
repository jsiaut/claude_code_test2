#!/usr/bin/env python3
"""Contrôle hors plan des transferts (décidé après avoir vu le témoin de Fortran, docs/FORTRAN.md, section 4) : pour
chaque clé corrigée qui a un témoin mesuré sur le même hôte (C compilé par GCC), on compare deux estimations du temps
corrigé dans les données principales :

* transfert (méthode du plan) : temps principal d'origine × (corrigé / origine, machine 5) ;
* pont par le témoin : temps principal du témoin × (corrigé / témoin, machine 5).

Les deux supposent qu'un facteur d'hôte s'annule : entre les deux versions du langage pour le transfert, entre la
version corrigée et le témoin pour le pont. Règle : quand le transfert s'écarte du pont de plus de 25 % (l'effet de
disposition le plus fort mesuré sur les clés témoins, dont le source ne change pas), le pont remplace le transfert dans
results/transfers.json. La règle s'applique à toutes les clés transférées qui ont un témoin (Ada et Fortran).
Le script calcule ensuite le classement avec les rapports retenus (ce que analyze_v3.py doit reproduire).
Ordre : ada_check.py, fortran_check.py, puis ce script, puis analyze_v3.py. Sortie : results/transfer_check.json."""
import json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
from analyze_v2 import ROOT  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402
import ada_check  # noqa: E402
import confrontation as cf  # noqa: E402
import fortran_check  # noqa: E402

LIMIT = 0.25


def gm(procs):
    return math.exp(proc_logs(procs).mean())


def main():
    data, *_ = v2.dataset_main(transfers=False)
    tpath = os.path.join(ROOT, "results", "transfers.json")
    tr = json.load(open(tpath))
    out = {"limit": LIMIT, "keys": {}}
    for lang, mod in (("ada", ada_check), ("fortran", fortran_check)):
        raw, _bad = mod.load_raw()
        fix = f"{lang}_fix"
        for k in tr["ratios"][lang]:
            key = tuple(k.split("|"))
            if key not in raw.get("c_gcc", {}):
                continue
            orig_main, w_main = gm(data[lang][key]), gm(data["c_gcc"][key])
            f5, o5, w5 = gm(raw[fix][key]), gm(raw[lang][key]), gm(raw["c_gcc"][key])
            transfer = orig_main * f5 / o5
            bridge = w_main * f5 / w5
            gap = transfer / bridge - 1
            use_bridge = abs(gap) > LIMIT
            out["keys"][f"{lang}|{k}"] = {"orig_main_ms": 1e3 * orig_main, "transfer_ms": 1e3 * transfer,
                                         "bridge_ms": 1e3 * bridge, "gap": gap, "ratio_plan": f5 / o5,
                                         "ratio_used": (bridge / orig_main) if use_bridge else f5 / o5,
                                         "bridge_used": use_bridge}
            if use_bridge:
                tr["ratios"][lang][k] = bridge / orig_main
            print(f"{lang:8s} {k:28s} transfert {1e3 * transfer:8.2f} ms, pont {1e3 * bridge:8.2f} ms, écart "
                  f"{100 * gap:+6.1f} %{'  -> pont' if use_bridge else ''}")
    suffix = " ; ponts par le témoin : results/transfer_check.json"
    if any(v["bridge_used"] for v in out["keys"].values()):
        if suffix not in tr["source"]:
            tr["source"] += suffix
        json.dump(tr, open(tpath, "w"), indent=1)
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in v2.RANKED + list(v2.ANNEX) if l in data]
    z = out["scenario"] = fortran_check.summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    print(f"Rapports retenus : Fortran {z['ms0']['fortran']:.1f} points, rang espéré {z['exp21']['fortran']:.2f} "
          f"({z['pos']}e), rang 90 % {z['rank90']['fortran']}")
    # S2 (sensibilité, docs/FORTRAN.md 3.4) refait sur les rapports retenus : formes de la remarque pour K5 et K8 tuned
    fc = json.load(open(os.path.join(ROOT, "results", "fortran_check.json")))
    d2 = fortran_check.scaled(data, {tuple(k.split(":")): e["ratio"] for k, e in fc["exp"].items()})
    z = out["scenario_S2"] = fortran_check.summary(cf.scenario(d2, lat, langs, footprint, c3, "main"))
    print(f"S2 sur les rapports retenus : Fortran {z['ms0']['fortran']:.1f} points, rang espéré "
          f"{z['exp21']['fortran']:.2f} ({z['pos']}e), rang 90 % {z['rank90']['fortran']}")
    json.dump(out, open(os.path.join(ROOT, "results", "transfer_check.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
