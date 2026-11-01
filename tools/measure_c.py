#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur C (plan : docs/C.md, section 3), sur l'hôte Emerald Rapids actuel
(machine 16, results/hw/machine16). Sensibilités et informations seulement : rien de ce qui est mesuré ici n'entre
dans le classement publié.

Implémentations (même hôte, appariées par passe), sortie results/raw_c/<implémentation>.jsonl, étiquette « c_rem » ;
copies générées par tools/c_check/make_copies.py (c_ref vient de tools/cpp_check/make_copies.py) :
* c_ref       : source C de la campagne, clang 23, options du banc (identique à l'octet au binaire de la réplication) ;
* c_k8val     : arène de K8 construite par une récursion à un seul état passé par valeur, clang 23 ;
* c_k8it      : arène de K8 construite et sommée par itération (piles explicites), clang 23 ;
* c_gcc_ref, c_gcc_k8val, c_gcc_k8it : les mêmes sources, gcc 16, options de l'annexe c_gcc (c_gcc_ref est identique
  à l'octet au binaire de la réplication de c_gcc).
Clés : K8 tuned (la forme change) et K8 naturel (témoin : code inchangé). 7 processus par cellule, en 7 passes ; dans
chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe). Répétitions de results/calib.json (clés de
C) ; un échauffement. Règle de vol du pilote (processus refait au-delà de 2 % de la capacité des 4 vCPU, deux fois au
plus).
Usage : measure_c.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_c")
PASSES = 7
SEED = 20261101 + 1000
K8T, K8N = ("k8", "tuned", ""), ("k8", "natural", "")
IMPLS = ["c_ref", "c_k8val", "c_k8it", "c_gcc_ref", "c_gcc_k8val", "c_gcc_k8it"]
CELLS = {impl: [K8T, K8N] for impl in IMPLS}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    return [(impl, k, v, p, calib[f"c|{k}|{v}|{p}"]["reps"], 1) for impl, keys in CELLS.items() for k, v, p in keys]


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "c_rem",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque C : fin\n")


if __name__ == "__main__":
    main()
