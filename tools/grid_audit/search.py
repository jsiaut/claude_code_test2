#!/usr/bin/env python3
"""Recherche d'absence de l'audit de la grille (docs/V4_PLAN.md, 2.1, classe [recherche]).

Usage : search.py <langage> <case> [<case>...]

Fouille les sources livrées de la bibliothèque standard du langage (ou la liste de ses API publiques, obtenue par
introspection ou par les documents de référence livrés avec la chaîne) avec le motif de la case, fixé d'avance dans
patterns.json. Chaque ligne trouvée est classée en déclaration publique (elle correspond aussi au motif de déclaration
publique du langage) ou en simple mention. Le détail va dans results/grid_audit/search/<langage>_<case>.txt ; la
sortie standard reçoit une ligne par case :
    SEARCH;<case>;<déclarations publiques>;<mentions>;<fichiers>;<chemin du détail>
Chaque résultat est ensuite examiné à la main ; l'examen est écrit dans la ligne CAP de la sonde."""
import collections
import json
import os
import re
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CFG = json.load(open(os.path.join(HERE, "patterns.json")))


def lines_of(lc):
    exts = tuple(lc.get("ext", []))
    excl = lc.get("exclude", [])

    def keep(name):
        return (not exts or name.endswith(exts)) and not any(e in name for e in excl)

    for r in lc.get("roots", []):
        r = os.path.expandvars(r)
        if r.endswith(".zip"):
            with zipfile.ZipFile(r) as z:
                for n in sorted(z.namelist()):
                    if keep(n):
                        for i, t in enumerate(z.read(n).decode("utf-8", "replace").splitlines(), 1):
                            yield n, i, t
        elif os.path.isfile(r):
            for i, t in enumerate(open(r, errors="replace").read().splitlines(), 1):
                yield r, i, t
        else:
            for d, subs, files in os.walk(r):
                subs.sort()
                for f in sorted(files):
                    p = os.path.join(d, f)
                    if keep(p):
                        for i, t in enumerate(open(p, errors="replace").read().splitlines(), 1):
                            yield p, i, t
    if "listing" in lc:
        out = subprocess.run(lc["listing"], shell=True, capture_output=True, text=True, cwd=ROOT).stdout
        for i, t in enumerate(out.splitlines(), 1):
            yield "<introspection>", i, t


def main():
    lang, caps = sys.argv[1], sys.argv[2:]
    lc = CFG["langs"][lang]
    pub = re.compile(lc["public"])
    version = subprocess.run(lc["version"], shell=True, capture_output=True, text=True).stdout.strip().splitlines()
    version = version[0] if version else "?"
    pats = {c: re.compile(lc.get("extra", {}).get(c, CFG["caps"][c]), re.I) for c in caps}
    hits = {c: [] for c in caps}
    for path, i, t in lines_of(lc):
        for c, p in pats.items():
            if p.search(t):
                hits[c].append((path, i, t.strip(), bool(pub.search(t))))
    for c in caps:
        h = hits[c]
        pubs = [x for x in h if x[3]]
        files = collections.Counter(x[0] for x in h)
        out = os.path.join("results", "grid_audit", "search", f"{lang}_{c}.txt")
        with open(os.path.join(ROOT, out), "w") as f:
            f.write(f"# Recherche d'absence : {lang}, case {c}\n# Chaîne : {version}\n")
            f.write(f"# Motif : {pats[c].pattern}\n# Déclaration publique : {lc['public']}\n")
            f.write(f"# {len(pubs)} déclarations publiques, {len(h) - len(pubs)} mentions, {len(files)} fichiers\n\n")
            f.write("## Déclarations publiques\n")
            for path, i, t, _ in pubs:
                f.write(f"{os.path.relpath(path, '/') if path.startswith('/') else path}:{i}: {t[:200]}\n")
            f.write("\n## Mentions, par fichier\n")
            for path, n in sorted(files.items()):
                f.write(f"{n:5d} {path}\n")
        print(f"SEARCH;{c};{len(pubs)};{len(h) - len(pubs)};{len(files)};{out}")


if __name__ == "__main__":
    main()
