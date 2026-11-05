#!/usr/bin/env python3
"""Mesures de l'ajout de Swift (plan : docs/SWIFT.md, section 3.4), machine 23 (Cascade Lake, du même modèle que l'hôte
des données principales, results/hw/machine23).

Cellules (sortie results/raw_swift/<implémentation>.jsonl, étiquette « swift ») :
* swift (bench/swift) et c (binaire de la campagne, témoin du pont) : les 31 cellules du classement et de K10 (K1 : 4
  variantes ; K2 tuned à 16 Kio, 256 Kio et 8 Mio ; K3 : 4 ; K4 : 3 ; K5 : 2 ; K6 : 6 ; K7 : 2 ; K8 : 2 ; K9 : 3 ;
  K10 : 2) ;
* swift_exp (sensibilité S-K8fl) : K8 natural et natural_fl (même binaire) ;
* swift_ou (sensibilité S-Ou, -Ounchecked) : les 9 cellules naturelles du score (K1 natural et natural_shuffled, K4
  natural_unsorted, K5 natural, K6 natural q6 et q1, K7 natural, K8 natural, K9 natural).
Répétitions : celles de results/calib.json pour c ; pour swift, la règle du pilote (tools/driver.py : 3 s divisées
par le temps d'une répétition, entre 3 et 10 ; 2 au-delà de 5 s), appliquée au temps d'une répétition de calibration
mesuré au début (écrit dans results/calib.json sous « swift|… ») ; swift_exp et swift_ou prennent celles de la cellule
de swift d'origine. Échauffement : 1 (compilé à l'avance). 7 passes ; dans chaque passe, toutes les cellules dans un
ordre tiré au hasard (graine fixe) ; règle de vol du pilote.
Empreinte de K1 (3 processus, étiquette post_fp2, results/raw_post/swift.jsonl) à la fin.
Usage : measure_swift.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_swift")
PASSES = 7
SEED = 20261105 + 2000

K2S = ["16384", "262144", "8388608"]
ALL = ([("k1", v, "energy") for v in ("natural", "aos", "soa", "natural_shuffled")]
       + [("k2", "tuned", s) for s in K2S]
       + [("k3", v, "") for v in ("rmw_packed", "rmw_padded", "sw_packed", "sw_padded")]
       + [("k4", v, "") for v in ("natural_unsorted", "natural_sorted", "branchless_unsorted")]
       + [("k5", v, "") for v in ("natural", "tuned")]
       + [("k6", v, q) for v in ("natural", "tuned", "mt") for q in ("q6", "q1")]
       + [("k7", v, "") for v in ("natural", "tuned")]
       + [("k8", v, "") for v in ("natural", "tuned")]
       + [("k9", v, "") for v in ("natural", "tuned", "mt")]
       + [("k10", v, "") for v in ("natural", "tuned")])
NATURAL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
           ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"), ("k7", "natural", ""),
           ("k8", "natural", ""), ("k9", "natural", "")]
CELLS = {
    "swift": ALL,
    "c": ALL,
    "swift_exp": [("k8", "natural", ""), ("k8", "natural_fl", "")],
    "swift_ou": NATURAL,
}
CALIB_VARIANT = {"natural_fl": "natural"}


def rule(t):
    """Règle de calibration de tools/driver.py."""
    reps = max(3, min(10, int(3.0 / max(t, 1e-6))))
    return 2 if t > 5.0 else reps


def calibrate():
    """Une répétition de chaque cellule de swift (échauffement 1), répétitions écrites dans results/calib.json."""
    path = os.path.join(ROOT, "results", "calib.json")
    calib = json.load(open(path))
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import driver
    for k, v, p in ALL:
        key = f"swift|{k}|{v}|{p}"
        if key in calib:
            continue
        rec = driver.run_one("swift", k, v, p, 1, 1, 3600)
        t = rec["reps"][0]["sec"] if rec.get("reps") else 10.0
        calib[key] = {"reps": rule(t), "procs": PASSES, "t_cal": t}
        print(f"calibration {key} t={t:.4f} reps={calib[key]['reps']}", flush=True)
        with open(path + ".tmp", "w") as cf:
            json.dump(calib, cf, indent=0, sort_keys=True)
        os.replace(path + ".tmp", path)
    return calib


def jobs(calib):
    out = []
    for impl, keys in CELLS.items():
        for k, v, p in keys:
            base = "c" if impl == "c" else "swift"
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, 1))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="swift"):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", tag,
            "--out", os.path.join(out_dir, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(out_dir, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--dry" in sys.argv:
        n = sum(len(v) for v in CELLS.values())
        print(f"{n} cellules, {PASSES} passes : {n * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "ajout de Swift : calibration\n")
    log.flush()
    calib = calibrate()
    js = jobs(calib)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"ajout de Swift : début, {len(js)} cellules, {len(js) * PASSES} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"ajout de Swift : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    # empreinte de K1 (D2a, méthode en deux points de analysis/footprint.py)
    post = os.path.join(ROOT, "results", "raw_post")
    for _ in range(3):
        driver("swift", "fp", "footprint", "energy", 1, 1, out_dir=post, tag="post_fp2")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "ajout de Swift : fin\n")


if __name__ == "__main__":
    main()
