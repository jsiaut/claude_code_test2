#!/usr/bin/env python3
"""Mesures de la remarque sur PHP (plan : docs/PHP.md, section 5.4), machine 29 (Emerald Rapids, même modèle que la
machine 28 de l'ajout ; results/hw/machine29).

Cellules (sortie results/raw_php_rq/<implémentation>.jsonl, étiquette « php_rq »), appariées sur la même machine :
* php (banc publié, PHP 8.5.12) : K1 natural et natural_shuffled, K9 natural et tuned (témoins des rapports) ;
* php_rq (copie bench/php_rq/ms.php, même binaire) : K1 natural (contrôle de la copie), natural_idx et
  natural_idx_shuffled (la boucle naturelle par indice, sans variable intermédiaire), natural_gcoff et
  natural_gcoff_shuffled (la boucle naturelle après gc_disable(), information) ;
* php83, php84, php8513rc1, php86rc5 (le banc publié sous PHP 8.3.36, 8.4.27, 8.5.13RC1, 8.6.0RC5 ;
  tools/php_remark/build.sh) : K9 natural et tuned (information).
Répétitions : celles de results/calib.json (« php|… » ; les variantes nouvelles prennent celles de natural et de
natural_shuffled). Échauffement 3 (JIT tracing), comme tools/measure_php.py. 7 passes ; dans chaque passe, toutes les
cellules dans un ordre tiré au hasard (graine fixe) ; règle de vol du pilote.
Usage : measure_php_rq.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_php_rq")
PASSES = 7
SEED = 20261107 + 2900
WARM = 3

K1 = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy")]
K9 = [("k9", "natural", ""), ("k9", "tuned", "")]
NEW = [("k1", "natural_idx", "energy"), ("k1", "natural_idx_shuffled", "energy"), ("k1", "natural_gcoff", "energy"),
       ("k1", "natural_gcoff_shuffled", "energy")]
CELLS = {
    "php": K1 + K9,
    "php_rq": [("k1", "natural", "energy")] + NEW,
    "php83": K9, "php84": K9, "php8513rc1": K9, "php86rc5": K9,
}
CALIB_VARIANT = {"natural_idx": "natural", "natural_idx_shuffled": "natural_shuffled", "natural_gcoff": "natural",
                 "natural_gcoff_shuffled": "natural_shuffled"}


def jobs(calib):
    out = []
    for impl, keys in CELLS.items():
        for k, v, p in keys:
            reps = calib[f"php|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps))
    return out


def driver(impl, k, v, p, reps):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(WARM), "--tag", "php_rq",
            "--out", os.path.join(OUT, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)


def main():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    js = jobs(calib)
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules, {PASSES} passes : {len(js) * PASSES} processus")
        for j in js:
            print(" ", j)
        return
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur PHP : début, {len(js)} cellules, {len(js) * PASSES} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            driver(impl, k, v, p, reps)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur PHP : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque sur PHP : fin\n")


if __name__ == "__main__":
    main()
