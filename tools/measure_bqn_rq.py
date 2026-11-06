#!/usr/bin/env python3
"""Mesures de la remarque sur BQN (plan : docs/BQN.md, section 5.4), machine 27 (Emerald Rapids, même modèle que la
machine 26 de l'ajout ; results/hw/machine27).

Cellules (sortie results/raw_bqn_rq/<implémentation>.jsonl, étiquette « bqn_rq »), appariées sur la même machine :
* bqn et bqn_er (constructions publiées : cible Cascade Lake et native) : les 11 cellules que la copie change (K1 aos
  et soa, K4 branchless_unsorted, K6 tuned et mt sur Q6 et Q1, K7 natural, K9 natural, tuned et mt) et deux témoins
  inchangés (K1 natural, K5 tuned) ;
* bqn_rq et bqn_er_rq (copie bench/bqn_rq/ms.bqn, mêmes binaires) : les mêmes 13 cellules, plus K9 tuned_flat et
  mt_flat (somme de contrôle hors chrono seule).
Répétitions : celles de results/calib.json (« bqn|… » ; tuned_flat et mt_flat prennent celles de tuned et mt).
Échauffement 3 (JIT de CBQN). 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe) ; règle de vol du pilote.
Usage : measure_bqn_rq.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_bqn_rq")
PASSES = 7
SEED = 20261106 + 2700
WARM = 3

CHANGED = [("k1", "aos", "energy"), ("k1", "soa", "energy"), ("k4", "branchless_unsorted", ""),
           ("k6", "tuned", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"),
           ("k7", "natural", ""), ("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")]
CONTROLS = [("k1", "natural", "energy"), ("k5", "tuned", "")]
FLAT = [("k9", "tuned_flat", ""), ("k9", "mt_flat", "")]
CELLS = {
    "bqn": CHANGED + CONTROLS,
    "bqn_rq": CHANGED + CONTROLS + FLAT,
    "bqn_er": CHANGED + CONTROLS,
    "bqn_er_rq": CHANGED + CONTROLS + FLAT,
}
CALIB_VARIANT = {"tuned_flat": "tuned", "mt_flat": "mt"}


def jobs(calib):
    out = []
    for impl, keys in CELLS.items():
        for k, v, p in keys:
            reps = calib[f"bqn|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps))
    return out


def driver(impl, k, v, p, reps):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(WARM), "--tag", "bqn_rq",
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
        return
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur BQN : début, {len(js)} cellules, {len(js) * PASSES} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            driver(impl, k, v, p, reps)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur BQN : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque sur BQN : fin\n")


if __name__ == "__main__":
    main()
