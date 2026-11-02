#!/usr/bin/env python3
"""Mesures de la remarque sur Go (plan : docs/GO.md, section 3.4), machine 18 (Emerald Rapids, results/hw/machine18).

Cellules (sortie results/raw_go/<implémentation>.jsonl, étiquette « go ») :
* go_ref (le code publié, GOEXPERIMENT=simd) : les 36 clés de Go ;
* go_noexp (les variantes sans archsimd, compilées sans GOEXPERIMENT) : les 32 clés sans archsimd, et K8 tuned_it ;
* go_fix (ClearAVXUpperBits après les parties vectorielles) : les 4 clés archsimd (K1 soa, K5 tuned, Q6 tuned et mt) ;
* go_exp (sensibilités archsimd) : K5 tuned (forme corrigée, base) et tuned_r, K9 tuned_vec et mt_vec, Q1 tuned_1p et
  mt_1p ;
* go_nopre (binaire de go_ref, GODEBUG=asyncpreemptoff=1, information) : K1, K5, K7, K8 et K9 naturels, K9 tuned ;
* c (binaire de la campagne) : témoin du même hôte pour la règle du pont, sur les 11 clés reportées.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json (variante d'origine) ; échauffements de la campagne (2 pour K5, 1 sinon) ;
règle de vol du pilote. Usage : measure_go.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_go")
PASSES = 7
SEED = 20261102 + 400
ARCHSIMD = [("k1", "soa", "energy"), ("k5", "tuned", ""), ("k6", "tuned", "q6"), ("k6", "mt", "q6")]


def all_keys():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    keys = []
    for k in calib:
        lang, ker, var, par = k.split("|")
        if lang == "go" and ker not in ("k10", "fp"):
            keys.append((ker, var, par))
    return sorted(keys)


ALL = all_keys()
NOEXP = [k for k in ALL if k not in ARCHSIMD] + [("k8", "tuned_it", "")]
EXP = [("k5", "tuned", ""), ("k5", "tuned_r", ""), ("k9", "tuned_vec", ""), ("k9", "mt_vec", ""),
       ("k6", "tuned_1p", "q1"), ("k6", "mt_1p", "q1")]
NOPRE = [("k1", "natural", "energy"), ("k5", "natural", ""), ("k7", "natural", ""), ("k8", "natural", ""),
         ("k9", "natural", ""), ("k9", "tuned", "")]
C_BRIDGE = [("k5", "tuned", ""), ("k5", "natural", ""), ("k1", "soa", "energy"), ("k6", "tuned", "q6"), ("k6", "mt", "q6"),
            ("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", ""), ("k6", "tuned", "q1"), ("k6", "mt", "q1"),
            ("k8", "tuned", "")]
CELLS = {"go_ref": ALL, "go_noexp": NOEXP, "go_fix": ARCHSIMD, "go_exp": EXP, "go_nopre": NOPRE, "c": C_BRIDGE}
# variantes propres aux copies : répétitions de la variante d'origine
CALIB_VARIANT = {"tuned_it": "tuned", "tuned_r": "tuned", "tuned_vec": "tuned", "mt_vec": "mt", "tuned_1p": "tuned",
                 "mt_1p": "mt"}


def warmup(impl, k):
    return 2 if k == "k5" else 1


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "go"
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="go"):
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
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Go : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Go : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Go : fin\n")


if __name__ == "__main__":
    main()
