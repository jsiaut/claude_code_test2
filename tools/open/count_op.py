#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 7, calcul 7) : comptage des lignes des formes op_*, par l'outil et les règles de
lecture du point 5 (tools/cost/count.py : lignes de code L, lexèmes T, lignes sans vérification U, lignes propres à
une architecture X), sur le relevé tools/open/regions_op.py. Les régions « cv:<nom> » sont celles du relevé du point 5
(tools/cost/regions.py), lues dans la copie _cv à l'empreinte qu'il nomme (git cat-file) et transposées dans la copie
_op par correspondance des lignes (difflib) ; une ligne sans correspondante est une erreur.
Sorties : results/open/counts_op.json, results/open/regions_op.md. Usage : count_op.py [--check]"""
import difflib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "cost"))
import count as C  # noqa: E402  (analyse d'un fichier : lex, portées, motifs)
import regions as R5  # noqa: E402  (relevé du point 5)
from regions_op import LANGS  # noqa: E402

OUT = os.path.join(ROOT, "results", "open")


def mapping(lang, f):
    """{ligne de la copie _cv du point 5 : ligne de la copie _op} (numérotées à partir de 1)."""
    blob = R5.LANGS[lang]["files"][f]
    cv = subprocess.run(["git", "-C", ROOT, "cat-file", "-p", blob], capture_output=True, text=True,
                        check=True).stdout.split("\n")
    op = open(os.path.join(ROOT, LANGS[lang]["dir"], f), encoding="utf-8").read().split("\n")
    sm = difflib.SequenceMatcher(None, cv, op, autojunk=False)
    m = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                m[i1 + k + 1] = j1 + k + 1
    return m


def regions_of(lang):
    """Régions de la forme, celles du point 5 transposées comprises : {nom: [(fichier, a, b)]}, et les erreurs."""
    L = LANGS[lang]
    regs, errs = dict(L["regions"]), []
    maps = {}
    for key, (entry, names) in L["forms"].items():
        for n in names:
            if not n.startswith("cv:") or n in regs:
                continue
            name = n[3:]
            spans = []
            for f, a, b in R5.LANGS[lang]["regions"][name]:
                mp = maps.setdefault(f, mapping(lang, f))
                lines = [mp.get(x) for x in range(a, b + 1)]
                if None in lines:
                    errs.append(f"{n} : ligne {f}:{a + lines.index(None)} sans correspondante dans la copie _op")
                    continue
                # intervalles contigus de la copie _op
                start = prev = lines[0]
                for x in lines[1:] + [None]:
                    if x is not None and x == prev + 1:
                        prev = x
                        continue
                    spans.append((f, start, prev))
                    if x is not None:
                        start = prev = x
            regs[n] = spans
    return regs, errs


def check():
    bad = 0
    for lang, L in LANGS.items():
        d = os.path.join(ROOT, L["dir"])
        errs = []
        for f, h in L["files"].items():
            if C.blob(os.path.join(d, f)) != h:
                errs.append(f"{f} : empreinte {C.blob(os.path.join(d, f))} au lieu de {h}")
        regs, e2 = regions_of(lang)
        errs += e2
        for key, (entry, names) in L["forms"].items():
            seen = {}
            for n in names:
                for f, a, b in regs.get(n, []):
                    for x in range(a, b + 1):
                        if (f, x) in seen:
                            errs.append(f"forme {key} : ligne {f}:{x} dans {seen[(f, x)]} et {n}")
                            break
                        seen[(f, x)] = n
            text = {f: open(os.path.join(d, f), encoding="utf-8").read().split("\n") for f in L["files"]}
            if not any(entry in text[f][x - 1] for (f, x) in seen):
                errs.append(f"forme {key} : fonction d'entrée {entry} absente de ses régions")
        print(f"{lang} : " + ("relevé conforme" if not errs else f"{len(errs)} erreur(s)"))
        for e in errs:
            print("   ", e)
        bad += len(errs)
    return bad


def count():
    res = {}
    md = ["# Régions des formes op_* (v4, point 6, calcul 7)", "",
          "*Écrit par `tools/open/count_op.py` à partir du relevé `tools/open/regions_op.py` (règles de lecture du "
          "point 5). Intervalles de lignes (bornes comprises) dans les copies `bench/<langage>_op` ; « cv: » : région "
          "du relevé du point 5, transposée.*", ""]
    for lang, L in LANGS.items():
        d = os.path.join(ROOT, L["dir"])
        A = {f: C.analyse_file(lang, os.path.join(d, f)) for f in L["files"]}
        regs, errs = regions_of(lang)
        assert not errs, errs
        forms = {}
        md += [f"## {lang}", ""]
        for key, (entry, names) in sorted(L["forms"].items()):
            fl = {}
            for n in names:
                for f, a, b in regs[n]:
                    fl.setdefault(f, set()).update(range(a - 1, b))
            Lc = T = U = X = 0
            for f, ls in fl.items():
                a = A[f]
                c = ls & a["code"]
                Lc += len(c)
                T += sum(a["tokens"][i] for i in c)
                U += len(c & a["unchecked"])
                X += len(c & a["arch"])
            forms[key] = {"entry": entry, "regions": names, "L": Lc, "T": T, "U": U, "X": X}
            md.append(f"* `{key}` (entrée `{entry}`) : " + " ; ".join(
                f"{n} " + ", ".join(f"{f}:{a}-{b}" for f, a, b in regs[n]) for n in names)
                + f" — L {Lc}, T {T}, U {U}, X {X}")
        md.append("")
        res[lang] = {"forms": forms}
    json.dump(res, open(os.path.join(OUT, "counts_op.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(OUT, "regions_op.md"), "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        sys.exit(1 if check() else 0)
    count()
