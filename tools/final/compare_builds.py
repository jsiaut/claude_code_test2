#!/usr/bin/env python3
"""Campagne (docs/METHOD.md, 6) : compare les empreintes des constructions d'une machine à l'autre.

Lit builds.jsonl du répertoire de travail de la campagne (une ligne par construction faite, avec machine et démarrage) ; pour chaque
construction (langage, construction, jeu), compare la dernière construction de chaque démarrage à la première de la
campagne : fichiers identiques, sections .text identiques (seuls diffèrent identifiant de construction, chemins ou
tables), ou code différent. Sortie : builds_compare.txt dans le répertoire de la campagne (results/final, ou
MS_CAMPAIGN_DIR)."""
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CAMPAIGN = os.path.join(ROOT, os.environ.get("MS_CAMPAIGN_DIR", os.path.join("results", "final")))
SRC = os.path.join(CAMPAIGN, "work", "builds.jsonl")
OUT = os.path.join(CAMPAIGN, "builds_compare.txt")


def main():
    recs = [json.loads(l) for l in open(SRC)] if os.path.exists(SRC) else []
    first, last = {}, {}
    for r in recs:
        k = (r["lang"], r["construction"], r["set"])
        first.setdefault(k, r)
        last[(k, r["boot_id"])] = r
    lines, counts = [], {"identiques": 0, "texte identique": 0, "différents": 0}
    for (k, boot), r in sorted(last.items()):
        f = first[k]
        if r is f or boot == f["boot_id"]:
            continue
        a, b = f["files"], r["files"]
        if a == b:
            verdict = "identiques"
        elif set(a) == set(b) and all(a[x][1] is not None and a[x][1] == b[x][1] for x in a):
            verdict = "texte identique"
        else:
            verdict = "différents"
        counts[verdict] += 1
        lines.append(f"{k[0]:8} {k[1]:7} {k[2]:6} machine {f['machine']} -> {r['machine']} : {verdict}")
    with open(OUT, "w") as g:
        g.write("# Empreintes des constructions : première construction de la campagne contre celles des démarrages "
                "suivants\n")
        g.write(f"# {len(recs)} constructions enregistrées ; comparaisons : {counts}\n")
        g.write("\n".join(lines) + ("\n" if lines else ""))
    print(f"{len(lines)} comparaisons : {counts} ({OUT})")


if __name__ == "__main__":
    main()
