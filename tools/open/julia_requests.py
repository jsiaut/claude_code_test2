#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 3.1 et écart 4) : contrôle du classement de Julia par la statistique prévue au plan,
les requêtes du dernier mois aux serveurs de paquets (julialang-logs, package_requests_by_date.csv.gz : requêtes de
statut 200, tous clients, du 23 octobre au 21 novembre 2026), les noms venant de Registry.toml du registre General ;
le relevé (tools/open/registry.py) avait classé par les téléchargements du dernier mois que publie ecosyste.ms.
Usage : julia_requests.py <package_requests_by_date.csv.gz> <Registry.toml>.
Écrit results/open/registry/julia_requests.json : pour chaque case, les candidates avec les deux statistiques et les
deux rangs."""
import csv
import gzip
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "results", "open", "registry", "julia.json")
OUT = os.path.join(ROOT, "results", "open", "registry", "julia_requests.json")
D0, D1 = "2026-10-23", "2026-11-21"


def main(bydate, registry):
    names = {}
    for m in re.finditer(r'^([0-9a-f-]{36}) = \{ name = "([^"]+)"', open(registry, encoding="utf-8").read(), re.M):
        names[m.group(1)] = m.group(2)
    req = {}
    with gzip.open(bydate, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"] != "200" or not (D0 <= row["date"] <= D1):
                continue
            n = names.get(row["package_uuid"])
            if n:
                req[n] = req.get(n, 0) + int(row["request_count"])
    reg = json.load(open(REG, encoding="utf-8"))
    out = {"source": f"julialang-logs, package_requests_by_date.csv.gz, statut 200, du {D0} au {D1}",
           "cases": {}}
    changed = []
    for case, v in reg["cases"].items():
        rows = [{"name": c["name"], "rang_releve": i + 1, "stat_releve": c.get("stat"),
                 "requetes": req.get(c["name"], 0)} for i, c in enumerate(v["candidates"])]
        order = sorted(rows, key=lambda r: (-r["requetes"], r["rang_releve"]))
        for k, r in enumerate(order):
            r["rang_requetes"] = k + 1
        out["cases"][case] = order
        top_a = [r["name"] for r in sorted(rows, key=lambda r: r["rang_releve"])[:10]]
        top_b = [r["name"] for r in order[:10]]
        print(case, "dix premiers, relevé :", top_a)
        print(case, "dix premiers, requêtes :", top_b)
        if top_a != top_b:
            changed.append(case)
    out["cases_dont_les_dix_premiers_changent"] = changed
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("écrit :", OUT, "; cases changées :", changed)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
