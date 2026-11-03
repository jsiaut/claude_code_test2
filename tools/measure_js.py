#!/usr/bin/env python3
"""Mesures de la remarque sur JavaScript (plan : docs/JAVASCRIPT.md, section 3.4), machine 21 (Emerald Rapids,
results/hw/machine21).

Cellules (sortie results/raw_js/<implémentation>.jsonl, étiquette « js ») :
* js_ref (le code publié, Node.js 26.12.1) : K7 tuned (correction), les clés de base des sensibilités (Q6 tuned et mt,
  K9 tuned et mt, K8 naturel et tuned, K5 tuned, K1 soa) et Q1 tuned et naturel (information, Node 22) ;
* js_fix (correction publiée : K7 tuned en cases de 16 octets) : K7 tuned, et K5 tuned et K9 tuned, dont le code ne
  change pas (contrôle) ;
* js_exp (sensibilités) : K6 tuned_m et mt_m (Q6), K9 tuned_v et mt_v, K8 natural_s et tuned_it, K5 tuned_f64,
  K1 soa_f64 ;
* js_n22 (le source de js_ref sous Node.js 22.22.0) : Q1 tuned et naturel (information) ;
* c (binaire de la campagne) : K7 tuned, témoin du même hôte pour le pont (information).
7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe). Répétitions de
results/calib.json (variante d'origine pour les variantes nouvelles) ; échauffements de la campagne (2 pour K5,
1 sinon) ; règle de vol du pilote. Usage : measure_js.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_js")
PASSES = 7
SEED = 20261103 + 700

K7T = ("k7", "tuned", "")
BASES = [("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k9", "tuned", ""), ("k9", "mt", ""), ("k8", "natural", ""),
         ("k8", "tuned", ""), ("k5", "tuned", ""), ("k1", "soa", "energy")]
Q1 = [("k6", "tuned", "q1"), ("k6", "natural", "q1")]
EXP = [("k6", "tuned_m", "q6"), ("k6", "mt_m", "q6"), ("k9", "tuned_v", ""), ("k9", "mt_v", ""), ("k8", "natural_s", ""),
       ("k8", "tuned_it", ""), ("k5", "tuned_f64", ""), ("k1", "soa_f64", "energy")]
CELLS = {"js_ref": [K7T] + BASES + Q1, "js_fix": [K7T, ("k5", "tuned", ""), ("k9", "tuned", "")], "js_exp": EXP,
         "js_n22": Q1, "c": [K7T]}
CALIB_VARIANT = {"tuned_m": "tuned", "mt_m": "mt", "tuned_v": "tuned", "mt_v": "mt", "natural_s": "natural",
                 "tuned_it": "tuned", "tuned_f64": "tuned", "soa_f64": "soa"}


def warmup(impl, k):
    return 2 if k == "k5" else 1


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "js"
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="js"):
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque JavaScript : début, {len(js)} cellules, {n} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque JavaScript : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque JavaScript : fin\n")


if __name__ == "__main__":
    main()
