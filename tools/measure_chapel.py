#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Chapel (plan : docs/CHAPEL.md, section 3), sur l'hôte Emerald Rapids
actuel (machine 8). Sensibilité et correction de la confrontation : aucune de ces mesures n'entre dans le classement
publié.

* chapel_ref : source de la campagne (bench/chapel/ms.chpl) compilé pour l'hôte par le script du banc ; chapel_exp :
  formes de la remarque (Q1 en intrinsèques importées, K5 et K1 aos/soa avec l'attribut de boucle, K7 naturel en une
  recherche) ; chapel_std2 : copie standard de la confrontation corrigée (K5 et K1 aos/soa en sommes partielles) ;
  c (clang) : témoin du même hôte.
* 7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
  fixe). Répétitions de results/calib.json (clé de l'implémentation d'origine), échauffement de 2.
  Sortie : results/raw_chapel/<implémentation>.jsonl, étiquette « chapel ».
Usage : measure_chapel.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_chapel")
PASSES = 7
SEED = 20261030 + 100
Q1T, Q1M, K5T = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k5", "tuned", "")
K1A, K1S, K7N = ("k1", "aos", "energy"), ("k1", "soa", "energy"), ("k7", "natural", "")
K9T, Q6T, K7T = ("k9", "tuned", ""), ("k6", "tuned", "q6"), ("k7", "tuned", "")
CHANGED = [Q1T, Q1M, K5T, K1A, K1S, K7N]
CONTROLS = [K9T, Q6T, K7T]
CELLS = {"chapel_ref": CHANGED + CONTROLS, "chapel_exp": CHANGED + CONTROLS, "chapel_std2": [K5T, K1A, K1S],
         "c": CHANGED}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "chapel" if impl.startswith("chapel") else impl
        for k, v, p in keys:
            out.append((impl, k, v, p, calib[f"{base}|{k}|{v}|{p}"]["reps"]))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Chapel : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", "2", "--tag", "chapel",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=900)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Chapel : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Chapel : fin\n")


if __name__ == "__main__":
    main()
