#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Ada (plan : docs/ADA.md, section 3), sur l'hôte Cascade Lake actuel
(machine 5).

Plan apparié : Ada (bench/ada, binaire de la campagne) et sa copie corrigée (bench/ada_fix : sept noyaux tuned hors
ligne) sur les 27 clés qui entrent dans le score ; C compilé par GCC (bench/c_gcc) sur 6 clés, en témoin du même hôte.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions figées par results/calib.json (clé de l'implémentation d'origine), échauffement de 2 répétitions.
Sortie : results/raw_ada/<implémentation>.jsonl, étiquette « ada ». Usage : measure_ada.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from analyze_v3 import needed_keys  # noqa: E402

OUT = os.path.join(ROOT, "results", "raw_ada")
PASSES = 7
SEED = 20261030 + 60
SCORE_KEYS = sorted(needed_keys())  # les 27 clés du score
# clés dont le code change dans bench/ada_fix (noyaux tuned hors ligne) ; les 14 autres servent de témoin
FIX_KEYS = [("k1", "aos", "energy"), ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"),
            ("k2", "tuned", "8388608"), ("k5", "tuned", ""), ("k6", "tuned", "q6"), ("k6", "tuned", "q1"),
            ("k6", "mt", "q6"), ("k6", "mt", "q1"), ("k9", "tuned", ""), ("k9", "mt", "")]
GCC_KEYS = [("k6", "tuned", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"), ("k9", "tuned", ""),
            ("k9", "mt", "")]
CELLS = {"ada": SCORE_KEYS, "ada_fix": SCORE_KEYS, "c_gcc": GCC_KEYS}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "ada" if impl == "ada_fix" else impl
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Ada : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", "2", "--tag", "ada",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Ada : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Ada : fin\n")


if __name__ == "__main__":
    main()
