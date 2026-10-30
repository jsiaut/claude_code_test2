#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Julia (plan : docs/JULIA.md, section 3), sur l'hôte Cascade Lake
actuel (machine 7). Sensibilité et diagnostics : aucune de ces mesures n'entre dans le classement publié.

* julia : source de la campagne (bench/julia/ms.jl) ; julia_exp : formes de la remarque (Q1 en une passe masquée, K7
  préchargé par lots, K8 spécialisé sur la profondeur, K10 sans capture) ; julia_c512 : source de la campagne avec
  -C native,-prefer-256-bit (K5 en 512 bits) ; c (clang) et c_gcc : témoins du même hôte.
* Clés dont le code change : K5 tuned (julia_c512), K6 tuned et mt Q1, K7 tuned, K8 tuned, K10 tuned (hors score) ;
  témoins dont le code ne change pas dans julia_exp : K9 tuned, K6 tuned Q6, K1 soa.
* 7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
  fixe). Répétitions de results/calib.json (clé de l'implémentation d'origine), échauffement de 2.
  Sortie : results/raw_julia/<implémentation>.jsonl, étiquette « julia ».
Usage : measure_julia.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_julia")
PASSES = 7
SEED = 20261030 + 90
K5T, Q1T, Q1M = ("k5", "tuned", ""), ("k6", "tuned", "q1"), ("k6", "mt", "q1")
K7T, K8T, K10T = ("k7", "tuned", ""), ("k8", "tuned", ""), ("k10", "tuned", "")
K9T, Q6T, K1S = ("k9", "tuned", ""), ("k6", "tuned", "q6"), ("k1", "soa", "energy")
CHANGED = [Q1T, Q1M, K7T, K8T, K10T]
CONTROLS = [K5T, K9T, Q6T, K1S]
CELLS = {"julia": [K5T] + CHANGED + [K9T, Q6T, K1S], "julia_exp": CHANGED + CONTROLS, "julia_c512": [K5T],
         "c": [K5T, Q1T, Q1M, K7T, K8T], "c_gcc": [K8T]}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "julia" if impl.startswith("julia") else impl
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Julia : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", "2", "--tag", "julia",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=900)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Julia : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Julia : fin\n")


if __name__ == "__main__":
    main()
