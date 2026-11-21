#!/usr/bin/env python3
"""v4, point 4 (docs/V4_CONVERGE.md, 3.3 et 4.1, écart 1) : validation des copies bench/<langage>_cv. Chaque copie est
construite (tools/converge/build.py, construction « cv »), puis chaque cellule du score (celles de la source publiée,
tools/equal/campaign.py, cells), les trois variantes de K9 et les variantes de cv_variants sont exécutées une fois à
la taille publiée ; la somme de contrôle doit être celle de la taille publiée (tools/driver.py). Pour une partie des
langages, le résultat se fusionne avec le fichier existant (lignes des autres langages gardées). Sortie :
results/converge/validation_cv.txt. Usage : validate_cv.py [langage,...]"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "equal"))
import campaign as C  # noqa: E402
sys.path.insert(0, HERE)
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("cvbuild", os.path.join(HERE, "build.py"))
CB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CB)

OUT = os.path.join(ROOT, "results", "converge", "validation_cv.txt")


def cv_cells(lang, k):
    cells = list(C.cells(lang, "pub", k))
    if k == "k9":
        cells += [(v, "") for v in ("natural", "tuned", "mt") if (v, "") not in cells]
    for c in C.variant_file(os.path.join(ROOT, "bench", lang + "_cv", "cv_variants")).get(k, []):
        if c not in cells:
            cells.append(c)
    return cells


def main():
    langs = sys.argv[1].split(",") if len(sys.argv) > 1 else C.LANGS
    old = {}
    if os.path.exists(OUT):
        for line in open(OUT):
            if not line.startswith("#"):
                old.setdefault(line.split()[0], []).append(line.rstrip("\n"))
    new = {}
    bad = 0
    for lang in langs:
        t0 = time.time()
        CB.ensure(lang, "cv")
        print(f"construit {lang} en {time.time() - t0:.0f} s", flush=True)
        new[lang] = []
        for k in C.KERNELS:
            for v, q in cv_cells(lang, k):
                rec = C.run_one(lang, "cv", k, v, q, 1, 3 if lang in C.JIT else 1, 3600)
                ok = rec.get("oks") == ["True"] and rec["returncode"] == 0
                bad += not ok
                t = f"{rec['median']:.4g}" if "median" in rec else "-"
                line = (f"{lang} {k} {v} {q or '-'} : {t} {','.join(rec.get('chks', [])) or '-'} "
                        f"{'juste' if ok else 'FAUX (code ' + str(rec['returncode']) + ') ' + rec['stderr'][-200:]}")
                new[lang].append(line.replace("\n", " "))
                print(line, flush=True)
    order = [l for l in C.LANGS if l in old or l in new]
    body = [line for l in order for line in new.get(l, old.get(l, []))]
    nbad = sum("juste" not in line.split(" : ", 1)[1].split()[-1] for line in body)
    lines = [f"# Validation des copies _cv (tools/converge/validate_cv.py), dernière exécution "
             f"{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} ({','.join(langs)}), {C.cpu_model()}",
             "# langage noyau variante paramètre : temps (s), somme de contrôle, verdict"] + body
    lines.append(f"# {len(body)} cellules, {len(body) - nbad} justes, {nbad} fausses")
    open(OUT, "w").write("\n".join(lines) + "\n")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
