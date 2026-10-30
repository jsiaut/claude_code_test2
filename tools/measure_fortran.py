#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Fortran (plan : docs/FORTRAN.md, section 3), sur l'hôte Cascade Lake
actuel (machine 5).

Plan apparié : Fortran (bench/fortran, binaire de la campagne) et sa copie corrigée (bench/fortran_fix : noyaux de
ms.f90 non inlinés, comme ceux du banc C) sur les 27 clés qui entrent dans le score ; la copie de sensibilité
(bench/fortran_exp : en plus, K5 tuned et l'arène de K8 réécrits) sur ces 2 clés ; C compilé par GCC (bench/c_gcc)
sur 4 clés, en témoin du même hôte. 7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans
un ordre tiré au hasard (graine fixe). Répétitions figées par results/calib.json (clé de l'implémentation d'origine),
échauffement de 2 répétitions. Sortie : results/raw_fortran/<implémentation>.jsonl, étiquette « fortran ».
Usage : measure_fortran.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from analyze_v3 import needed_keys  # noqa: E402

OUT = os.path.join(ROOT, "results", "raw_fortran")
PASSES = 7
SEED = 20261030 + 70
SCORE_KEYS = sorted(needed_keys())  # les 27 clés du score
# clés dont le code change dans bench/fortran_fix (noyaux de ms.f90 hors ligne) ; les 16 autres servent de témoin
FIX_KEYS = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k2", "tuned", "16384"),
            ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"), ("k4", "branchless_unsorted", ""),
            ("k4", "natural_unsorted", ""), ("k5", "natural", ""), ("k6", "natural", "q1"), ("k6", "natural", "q6"),
            ("k9", "natural", "")]
EXP_KEYS = [("k5", "tuned", ""), ("k8", "tuned", "")]
GCC_KEYS = [("k4", "branchless_unsorted", ""), ("k4", "natural_unsorted", ""), ("k5", "tuned", ""), ("k8", "tuned", "")]
CELLS = {"fortran": SCORE_KEYS, "fortran_fix": SCORE_KEYS, "fortran_exp": EXP_KEYS, "c_gcc": GCC_KEYS}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "fortran" if impl.startswith("fortran") else impl
        for k, v, p in keys:
            if f"{base}|{k}|{v}|{p}" not in calib:  # variante absente de l'implémentation (Fortran : pas de tuned_alloc)
                continue
            out.append((impl, k, v, p, calib[f"{base}|{k}|{v}|{p}"]["reps"]))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Fortran : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", "2", "--tag", "fortran",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Fortran : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Fortran : fin\n")


if __name__ == "__main__":
    main()
