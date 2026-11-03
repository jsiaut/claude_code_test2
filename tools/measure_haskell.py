#!/usr/bin/env python3
"""Mesures de la remarque sur Haskell (plan : docs/HASKELL.md, section 3.4), machine 19 (Emerald Rapids,
results/hw/machine19).

Cellules (sortie results/raw_haskell/<implémentation>.jsonl, étiquette « haskell ») :
* haskell_ref (le code et les options publiés, +RTS -N4) : les 36 clés de Haskell ;
* haskell_fix (correction publiée : mode release et quatre corrections du code, +RTS -N4) : les 36 clés ;
* haskell_rel (le code publié dans le mode release, +RTS -N4) : les 4 clés dont le code change (K1 soa, K5 tuned,
  K8 natural et tuned), pour séparer l'effet des options de celui du code ;
* haskell_n1 (binaire de haskell_fix, +RTS -N1, sensibilité) : K1 naturel et mélangé, K4 naturel non trié, K5, K8 et
  K9 naturels ;
* c (binaire de la campagne) : témoin du même hôte pour la règle du pont, sur les 36 clés.
7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe). K7 naturel (environ
50 s par répétition) n'est mesuré, pour haskell_ref et haskell_fix, que dans les passes 1 à 4 (4 processus). Répétitions
de results/calib.json ; échauffements de la campagne (2 pour K5, 1 sinon) ; règle de vol du pilote.
Usage : measure_haskell.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_haskell")
PASSES = 7
SEED = 20261103 + 500
K7N = ("k7", "natural", "")
K7N_PASSES = 4


def all_keys():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    keys = []
    for k in calib:
        lang, ker, var, par = k.split("|")
        if lang == "haskell" and ker not in ("k10", "fp"):
            keys.append((ker, var, par))
    return sorted(keys)


ALL = all_keys()
CODE = [("k1", "soa", "energy"), ("k5", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", "")]
N1 = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
      ("k5", "natural", ""), ("k8", "natural", ""), ("k9", "natural", "")]
CELLS = {"haskell_ref": ALL, "haskell_fix": ALL, "haskell_rel": CODE, "haskell_n1": N1, "c": ALL}


def warmup(impl, k):
    return 2 if k == "k5" else 1


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "haskell"
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{v}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="haskell"):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", tag,
            "--out", os.path.join(out_dir, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(out_dir, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)


def in_pass(job, pas):
    impl, k, v, p = job[:4]
    return not (impl != "c" and (k, v, p) == K7N and pas >= K7N_PASSES)


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    n = sum(in_pass(j, pas) for pas in range(PASSES) for j in js)
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules, {PASSES} passes : {n} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Haskell : début, {len(js)} cellules, {n} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = [j for j in js if in_pass(j, pas)]
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Haskell : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Haskell : fin\n")


if __name__ == "__main__":
    main()
