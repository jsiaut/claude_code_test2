#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur C3 (plan : docs/C3.md, section 3), sur l'hôte Emerald Rapids actuel
(machine 13). Rien de ces mesures n'entre dans le classement publié : sensibilités et information.

Implémentations (même hôte, appariées par passe), sortie results/raw_c3/<implémentation>.jsonl, étiquette « c3 » :
* c3_ref : source de la campagne (bench/c3/ms.c3) recompilé sur l'hôte, options du banc (-O3) : référence des paires ;
* c3_max : même source, -O3 --optlevel=max (pipeline O3 de LLVM, mathématiques flottantes strictes) ;
* c3_k5 : K5 tuned, réduction finale en arbre (swizzle) ;
* c3_thr : K9 mt, fils lancés par posix::pthread_create (sans l'attente du démarrage de Thread.create) ;
* c3_al : K9, accès alignés à 64 octets dans k9_rows (tuned et mt) ;
* c : binaire C de bench/c (compilé pour Cascade Lake), témoin des ponts.
c3_ref et c3_max couvrent toutes les mesures de C3 qui entrent dans le score (E, D1, D2, K8 naturel, K2 pour D4).
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json ; échauffements des données principales (1 ; 2 pour K5). Règle de vol du
pilote (processus refait au-delà de 2 % de la capacité des 4 vCPU, deux fois au plus).
Usage : measure_c3.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_c3")
PASSES = 7
SEED = 20261101 + 700
K5T, K9T, K9M = ("k5", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", "")
SCORE = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
         ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
         ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""),
         ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), K5T, ("k6", "natural", "q6"), ("k6", "tuned", "q6"),
         ("k6", "mt", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k7", "natural", ""),
         ("k7", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", ""), ("k8", "tuned_alloc", ""),
         ("k9", "natural", ""), K9T, K9M]
CELLS = {"c3_ref": SCORE, "c3_max": SCORE, "c3_k5": [K5T], "c3_thr": [K9M], "c3_al": [K9T, K9M], "c": [K5T, K9T, K9M]}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "c3"
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C3 : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "c3",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C3 : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque C3 : fin\n")


if __name__ == "__main__":
    main()
