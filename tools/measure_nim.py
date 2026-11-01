#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Nim (plan : docs/NIM.md, section 3), sur l'hôte Emerald Rapids actuel
(machine 12). Rien n'entre dans le classement publié : sensibilités et information.

Implémentations (même hôte, appariées par passe) :
* nim_ref : source de la campagne (bench/nim/ms.nim) recompilé sur l'hôte, options du banc (référence des paires) ;
* nim_q1 : Q1 optimisé en intrinsèques AVX-512 importées (algorithme de la référence C) ;
* nim_nat : K9 naturel en ref array[M9, array[M9, float]] ; nim_k8 : arène de K8 sans vérification de débordement ;
* nim_gcc : source de la campagne compilé vers gcc 16 ; nim_240 : par Nim 2.4.0 (information) ;
* c (binaire de bench/c, compilé pour Cascade Lake) : témoin des ponts.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json ; échauffements des données principales (1 ; 2 pour K5).
Sortie : results/raw_nim/<implémentation>.jsonl, étiquette « nim ».
Usage : measure_nim.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_nim")
PASSES = 7
SEED = 20261101 + 500
Q1T, Q1M, Q1N, Q6T = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k6", "natural", "q1"), ("k6", "tuned", "q6")
K9N, K9T, K8T, K8N = ("k9", "natural", ""), ("k9", "tuned", ""), ("k8", "tuned", ""), ("k8", "natural", "")
K4N, K4B, K5N, K5T = ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), ("k5", "tuned", "")
CELLS = {"nim_ref": [Q1T, Q1M, Q1N, Q6T, K9N, K9T, K8T, K8N, K4N, K4B, K5N, K5T],
         "nim_q1": [Q1T, Q1M, Q1N, Q6T], "nim_nat": [K9N, K9T], "nim_k8": [K8T, K8N],
         "nim_gcc": [K4N, K4B, K5N, K8T], "nim_240": [K8N, K8T],
         "c": [Q1T, Q1M, Q6T, K9N, K8T, K4N, K4B]}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "nim"
        for k, v, p in keys:
            out.append((impl, k, v, p, calib[f"{base}|{k}|{v}|{p}"]["reps"], 2 if k == "k5" else 1))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Nim : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "nim",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Nim : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Nim : fin\n")


if __name__ == "__main__":
    main()
