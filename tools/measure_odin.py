#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Odin (plan : docs/ODIN.md, section 3), sur l'hôte Emerald Rapids actuel
(machine 13). La correction du banc (odin_fix / odin_ref) entre dans le classement publié ; le reste est sensibilité.

Implémentations (même hôte, appariées par passe), sortie results/raw_odin/<implémentation>.jsonl, étiquette « odin » :
* odin_ref : source de la campagne (bench/odin/ms.odin) recompilé sur l'hôte, options du banc (-o:speed) ;
* odin_fix : les 14 noyaux #force_no_inline, comme les noinline du banc C (correction publiée) ;
* odin_q1 : odin_fix, et Q1 tuned compte chaque groupe par card(simd.extract_msbs(m)) (sensibilité) ;
* odin_agg : source de odin_fix compilé avec -o:aggressive (pipeline O3 de LLVM ; sensibilité) ;
* c : binaire C de bench/c (compilé pour Cascade Lake), témoin des ponts.
odin_ref, odin_fix et odin_agg couvrent toutes les mesures d'Odin qui entrent dans le score.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json ; échauffements des données principales (1 ; 2 pour K5). Règle de vol du
pilote (processus refait au-delà de 2 % de la capacité des 4 vCPU, deux fois au plus).
Usage : measure_odin.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_odin")
PASSES = 7
SEED = 20261101 + 800
K5T, K9T, K9M = ("k5", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", "")
Q1T, Q1M = ("k6", "tuned", "q1"), ("k6", "mt", "q1")
SCORE = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
         ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
         ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""),
         ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), K5T, ("k6", "natural", "q6"), ("k6", "tuned", "q6"),
         ("k6", "mt", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k7", "natural", ""),
         ("k7", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", ""), ("k8", "tuned_alloc", ""),
         ("k9", "natural", ""), K9T, K9M]
# clés dont le noyau était inliné dans le binaire de la campagne (results/odin_check/inlining.txt) : correction publiée
FIX_KEYS = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
            ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
            ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), K5T,
            ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k9", "natural", "")]
CELLS = {"odin_ref": SCORE, "odin_fix": SCORE, "odin_agg": SCORE, "odin_q1": [Q1T, Q1M], "c": FIX_KEYS + [Q1T, Q1M]}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "odin"
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Odin : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "odin",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Odin : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Odin : fin\n")


if __name__ == "__main__":
    main()
