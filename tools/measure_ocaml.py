#!/usr/bin/env python3
"""Mesures de la remarque sur OCaml (plan : docs/OCAML.md, section 3.4), machine 20 (Emerald Rapids,
results/hw/machine20).

Cellules (sortie results/raw_ocaml/<implémentation>.jsonl, étiquette « ocaml ») :
* ocaml_ref (le code publié) et ocaml_fix (correction publiée : Q6 tuned, K1 aos, K8 tuned, horloge) : les 36 clés ;
* ocaml_exp (sensibilités) : K6 tuned_m et mt_m (Q6), K8 tuned_val, K7 tuned_p, K9 tuned_fa et mt_fa, K5 tuned_8 ;
* c (binaire de la campagne) : témoin du même hôte pour le pont (information), sur les 8 clés corrigées ou de
  sensibilité.
7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe). Répétitions de
results/calib.json (variante d'origine pour les variantes nouvelles) ; échauffements de la campagne (2 pour K5,
1 sinon) ; règle de vol du pilote. Usage : measure_ocaml.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_ocaml")
PASSES = 7
SEED = 20261103 + 600


def all_keys():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    keys = []
    for k in calib:
        lang, ker, var, par = k.split("|")
        if lang == "ocaml" and ker not in ("k10", "fp"):
            keys.append((ker, var, par))
    return sorted(keys)


ALL = all_keys()
EXP = [("k6", "tuned_m", "q6"), ("k6", "mt_m", "q6"), ("k8", "tuned_val", ""), ("k7", "tuned_p", ""),
       ("k9", "tuned_fa", ""), ("k9", "mt_fa", ""), ("k5", "tuned_8", "")]
C_BRIDGE = [("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k1", "aos", "energy"), ("k8", "tuned", ""), ("k7", "tuned", ""),
            ("k9", "tuned", ""), ("k9", "mt", ""), ("k5", "tuned", "")]
CELLS = {"ocaml_ref": ALL, "ocaml_fix": ALL, "ocaml_exp": EXP, "c": C_BRIDGE}
CALIB_VARIANT = {"tuned_m": "tuned", "mt_m": "mt", "tuned_val": "tuned", "tuned_p": "tuned", "tuned_fa": "tuned",
                 "mt_fa": "mt", "tuned_8": "tuned"}


def warmup(impl, k):
    return 2 if k == "k5" else 1


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "ocaml"
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="ocaml"):
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
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque OCaml : début, {len(js)} cellules, {n} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque OCaml : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque OCaml : fin\n")


if __name__ == "__main__":
    main()
