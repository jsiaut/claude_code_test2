#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur D (plan : docs/DLANG.md, section 3), sur l'hôte Emerald Rapids actuel
(machine 10). La correction de Q1 (d_fix / d_ref) entre dans le classement publié ; le reste est sensibilité ou
information.

Implémentations (même hôte, appariées par passe) :
* d_ref : source de la campagne (bench/d/ms.d) recompilé sur l'hôte, options du banc (référence des paires) ;
* d_fix : Q1 optimisé écrit comme dans les autres langages à types vectoriels portables (bench/d_fix) ;
* d_512 : d_fix avec -mattr=-prefer-256-bit ; d_nat : stencil naturel en double[M][] ;
* d_l22 : source de la campagne compilé par le paquet officiel de LDC 1.43.0 (LLVM 22.1.8) ;
* d_gc : binaire de d_ref, --DRT-gcopt=fork:1 ; c (clang, binaire de la campagne) : témoin du pont.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json ; échauffements des données principales (1 ; 2 pour K5).
Sortie : results/raw_d/<implémentation>.jsonl, étiquette « d ».
Usage : measure_d.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_d")
PASSES = 7
SEED = 20261031 + 300
ALL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
       ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
       ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""),
       ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), ("k5", "tuned", ""), ("k6", "natural", "q6"),
       ("k6", "tuned", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"),
       ("k7", "natural", ""), ("k7", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", ""), ("k9", "natural", ""),
       ("k9", "tuned", ""), ("k9", "mt", "")]
Q1T, Q1M, Q1N = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k6", "natural", "q1")
Q6T, Q6M, K4B, K1A = ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k4", "branchless_unsorted", ""), ("k1", "aos", "energy")
K9N, K9T, K5T, K8N = ("k9", "natural", ""), ("k9", "tuned", ""), ("k5", "tuned", ""), ("k8", "natural", "")
CELLS = {"d_ref": ALL, "d_l22": ALL, "d_fix": [Q1T, Q1M, Q1N, Q6T, K9T, K5T, Q6M, K4B, K1A],
         "d_512": [Q6T, Q6M, Q1T, Q1M, K4B, K1A], "d_nat": [K9N, K9T], "d_gc": [K8N],
         "c": [Q1T, Q1M, Q6T, Q6M, K4B, K1A, K9N]}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "d"
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque D : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "d",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque D : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque D : fin\n")


if __name__ == "__main__":
    main()
