#!/usr/bin/env python3
"""Mesures de la remarque sur Python (plan : docs/PYTHON.md, section 3.4), machine 22 (Cascade Lake, du même modèle que
l'hôte des données principales, results/hw/machine22).

Cellules (sortie results/raw_python/<implémentation>.jsonl, étiquette « python ») :
* python_ref (le code publié, CPython 3.15.2 par défaut) : K3 (quatre variantes), K6 mt (Q6, Q1) et K9 mt (bases de la
  correction), Q6 tuned et K8 naturel (bases des sensibilités), Q6 naturel (contrôle) ;
* python_fix (correction publiée : sous-interpréteurs) : K3, K6 mt, K9 mt, et Q6 naturel (code inchangé : contrôle) ;
* python_exp (sensibilités) : K6 tuned_c et mt_c (Q6 en colonnes), K8 natural_f (gc.freeze) ;
* python_ftfix (build sans GIL, K3 par une memoryview propre à chaque fil) : K3, K6 mt, K9 mt (sensibilité S-FT) ;
* c (binaire de la campagne) : K3 sw_padded et rmw_padded, K6 mt, K9 mt, témoin du même hôte pour le pont.
7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe). Répétitions de
results/calib.json (variante d'origine pour les variantes nouvelles ; python_ft pour python_ftfix) ; un échauffement ;
règle de vol du pilote. Usage : measure_python.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_python")
PASSES = 7
SEED = 20261105 + 900

K3 = [("k3", "rmw_packed", ""), ("k3", "rmw_padded", ""), ("k3", "sw_packed", ""), ("k3", "sw_padded", "")]
MT = [("k6", "mt", "q6"), ("k6", "mt", "q1"), ("k9", "mt", "")]
Q6T, Q6N, K8N = ("k6", "tuned", "q6"), ("k6", "natural", "q6"), ("k8", "natural", "")
CELLS = {"python_ref": K3 + MT + [Q6T, Q6N, K8N], "python_fix": K3 + MT + [Q6N],
         "python_exp": [("k6", "tuned_c", "q6"), ("k6", "mt_c", "q6"), ("k8", "natural_f", "")], "python_ftfix": K3 + MT,
         "c": [("k3", "sw_padded", ""), ("k3", "rmw_padded", "")] + MT}
CALIB_VARIANT = {"tuned_c": "tuned", "mt_c": "mt", "natural_f": "natural"}
CALIB_BASE = {"c": "c", "python_ftfix": "python_ft"}


def warmup(impl, k):
    return 1


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = CALIB_BASE.get(impl, "python")
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="python"):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", tag,
            "--out", os.path.join(out_dir, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(out_dir, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    n = len(js) * PASSES
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules, {PASSES} passes : {n} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Python : début, {len(js)} cellules, {n} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Python : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Python : fin\n")


if __name__ == "__main__":
    main()
