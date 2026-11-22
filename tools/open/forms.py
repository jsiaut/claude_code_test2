#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 5 à 7) : relevé des formes du plafond ouvert, pour la campagne et l'analyse.

Lit les fichiers bench/<langage>_op/op_variants (noyau variante paramètre ; cellule ; bibliothèque), les formes d'accès
du point 5 (results/cost/cost.json, « access » : la forme la plus rapide du point 4, K1 et K3 : la plus rapide des formes
publiées), les bibliothèques nommées par le dossier (results/open/decisions.json, « nommees » : 3.3 c) et les variantes
de la copie bench/c_cv. Écrit results/open/forms.json :
* forms : une entrée par forme op_* (langage, bibliothèque, nommée ou non, cellule, clé de la forme, clé de la forme
  d'accès de la cellule) ;
* access : par (langage, cellule) touché, la clé de la forme d'accès, mesurée dans les constructions op et cv (témoin) ;
* c_witness : par cellule touchée, la forme de C de la cellule (forme d'accès de C) et sa construction (pub si c'est
  une variante publiée, cv sinon), mesurée comme témoin d'hôte (calcul 6).
Usage : forms.py"""
import glob, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "results", "open", "forms.json")
CELLS = ["K1", "K3", "K4", "K5", "Q6", "Q1", "Q6 mt", "Q1 mt", "K7", "K8", "K9", "K9 mt"]


def variants(path):
    out = set()
    for line in open(path):
        f = line.split("#")[0].split()
        if len(f) >= 2:
            out.add((f[0], f[1], f[2] if len(f) > 2 else ""))
    return out


def main():
    access = json.load(open(os.path.join(ROOT, "results", "cost", "cost.json")))["access"]
    dec = json.load(open(os.path.join(ROOT, "results", "open", "decisions.json")))
    c_cv = variants(os.path.join(ROOT, "bench", "c_cv", "cv_variants"))
    forms, acc = [], {}
    for path in sorted(glob.glob(os.path.join(ROOT, "bench", "*_op", "op_variants"))):
        lang = os.path.basename(os.path.dirname(path))[:-3]
        named = {x["nom"] for x in dec.get(lang, {}).get("nommees", [])}
        for line in open(path):
            if line.startswith("#") or not line.strip():
                continue
            kvp, cell, lib = (x.strip() for x in line.split(";"))
            f = kvp.split()
            key = "|".join([f[0], f[1], f[2] if len(f) > 2 else ""])
            assert cell in CELLS, (lang, cell)
            a = access[lang][cell][0]
            assert a.split("|")[0] == f[0], (lang, cell, a, key)
            forms.append({"lang": lang, "lib": lib, "named": lib in named, "cell": cell, "key": key, "access": a})
            acc.setdefault(lang, {})[cell] = a
    cells = sorted({x["cell"] for x in forms}, key=CELLS.index)
    cw = {}
    for c in cells:
        k = access["c"][c][0]
        kk = tuple(k.split("|"))
        cw[c] = {"key": k, "build": "cv" if kk in c_cv else "pub"}
    out = {"forms": forms, "access": acc, "c_witness": cw,
           "counts": {"forms": len(forms), "langs": len(acc), "pairs": sum(len(v) for v in acc.values()),
                      "cells": len(cells), "named_forms": sum(x["named"] for x in forms)}}
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"]))


if __name__ == "__main__":
    main()
