#!/usr/bin/env python3
"""Mesures de la remarque sur FreePascal (plan : docs/FPC.md, section 5.4), machine 26 (Emerald Rapids, du même modèle
que la machine 25 de l'ajout ; results/hw/machine26).

Cellules (sortie results/raw_fpc_rq/<implémentation>.jsonl, étiquette « fpc_rq ») :
* fpc (binaire publié, FPC 3.2.2), fpc_rc2 (3.2.4-rc2, même source) et fpc_main (branche main, même code, type __m128
  dans msvec) : les 29 cellules du score (K1 : 4 ; K2 tuned à 16 Kio, 256 Kio et 8 Mio ; K3 : 4 ; K4 : 3 ; K5 : 2 ;
  K6 : 6 ; K7 : 2 ; K8 : 2 ; K9 : 3) ;
* fpc_len (boucles naturelles bornées par Length) : les 8 cellules dont la boucle change (K1 natural et
  natural_shuffled, K4 natural_unsorted et natural_sorted, K5 natural, K6 natural q6 et q1, K7 natural) ;
* fpc_mieux (noyaux optimisés mieux écrits) : K4 branchless_unsorted et branchless_ptr, K5 tuned, K8 tuned ;
* fpc_main_mieux (main, les deux) : les 12 cellules de fpc_len et fpc_mieux ; fpc_main_scal (main sans -Sv) : K1 soa
  et K5 tuned ;
* information, hors des règles du banc : fpc_asm (K5 tuned en AVX2) et fpc_main_asm (K5 tuned en AVX-512) ;
* témoins, information : le C publié (c, Cascade Lake) sur K4 natural_unsorted et branchless_unsorted, K7 natural,
  K8 natural et tuned, K9 natural et tuned ; le C natif (c_er) sur K5 natural et tuned.
Répétitions : celles de results/calib.json (« fpc|… » pour toutes les constructions de FreePascal, branchless_ptr
prenant celles de branchless_unsorted ; « c|… » pour les témoins). Échauffement : 1. 7 passes ; dans chaque passe,
toutes les cellules dans un ordre tiré au hasard (graine fixe) ; règle de vol du pilote.
Usage : measure_fpc_rq.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_fpc_rq")
TAG = "fpc_rq"
PASSES = 7
SEED = 20261106 + 2600

K2S = ["16384", "262144", "8388608"]
M1 = ([("k1", v, "energy") for v in ("natural", "aos", "soa", "natural_shuffled")]
      + [("k2", "tuned", s) for s in K2S]
      + [("k3", v, "") for v in ("rmw_packed", "rmw_padded", "sw_packed", "sw_padded")]
      + [("k4", v, "") for v in ("natural_unsorted", "natural_sorted", "branchless_unsorted")]
      + [("k6", v, q) for v in ("natural", "tuned", "mt") for q in ("q6", "q1")]
      + [("k7", v, "") for v in ("natural", "tuned")]
      + [("k8", v, "") for v in ("natural", "tuned")])
SCORE = M1 + [("k5", v, "") for v in ("natural", "tuned")] + [("k9", v, "") for v in ("natural", "tuned", "mt")]
LEN = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
       ("k4", "natural_sorted", ""), ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"),
       ("k7", "natural", "")]
MIEUX = [("k4", "branchless_unsorted", ""), ("k4", "branchless_ptr", ""), ("k5", "tuned", ""), ("k8", "tuned", "")]
CELLS = {
    "fpc": SCORE,
    "fpc_rc2": SCORE,
    "fpc_main": SCORE,
    "fpc_len": LEN,
    "fpc_mieux": MIEUX,
    "fpc_main_mieux": LEN + MIEUX,
    "fpc_main_scal": [("k1", "soa", "energy"), ("k5", "tuned", "")],
    "fpc_asm": [("k5", "tuned", "")],
    "fpc_main_asm": [("k5", "tuned", "")],
    "c": [("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""), ("k7", "natural", ""),
          ("k8", "natural", ""), ("k8", "tuned", ""), ("k9", "natural", ""), ("k9", "tuned", "")],
    "c_er": [("k5", "natural", ""), ("k5", "tuned", "")],
}
CALIB_VARIANT = {"branchless_ptr": "branchless_unsorted"}
WITNESS = {"c", "c_er"}


def jobs(calib):
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl in WITNESS else "fpc"
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, 1))
    return out


def driver(impl, k, v, p, reps, w):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", TAG,
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur FreePascal : début, {len(js)} cellules, "
              f"{len(js) * PASSES} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur FreePascal : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque sur FreePascal : fin\n")


if __name__ == "__main__":
    main()
