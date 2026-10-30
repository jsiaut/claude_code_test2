#!/usr/bin/env python3
"""Mesures de la confrontation (plan : docs/CONFRONTATION.md, section 4.5), sur l'hôte Cascade Lake actuel.

Plan apparié : pour chaque clé touchée par la restriction, la variante d'origine (bench/<langage>) et sa réécriture
standard (bench/<langage>_std), 7 processus chacune, en 7 passes ; dans chaque passe, toutes les tâches dans un ordre
tiré au hasard (graine fixe). Répétitions figées par results/calib.json (clé d'origine), échauffement de 10 répétitions
pour les JIT et de 2 sinon. Sortie : results/raw_conf/<implémentation>.jsonl, étiquette « conf ».
Usage : measure_conf.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_conf")
PASSES = 7
SEED = 20261030
JIT = {"java"}
# clés touchées (section 4.2 du plan, plus l'ajout consigné le 30/10 : Fortran K6 tuned Q6 et Q1)
KEYS = {
    "c": [("k1", "soa", "energy"), ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k5", "tuned", ""),
          ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"), ("k7", "tuned", ""), ("k9", "mt", "")],
    "cpp": [("k7", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", "")],
    "nim": [("k1", "soa", "energy"), ("k5", "tuned", ""), ("k7", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", "")],
    "d": [("k1", "soa", "energy"), ("k5", "tuned", ""), ("k7", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", "")],
    "ada": [("k5", "tuned", ""), ("k6", "tuned", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"),
            ("k7", "tuned", ""), ("k9", "tuned", ""), ("k9", "mt", "")],
    "fortran": [("k1", "soa", "energy"), ("k5", "tuned", ""), ("k6", "tuned", "q6"), ("k6", "tuned", "q1")],
    "chapel": [("k1", "aos", "energy"), ("k1", "soa", "energy"), ("k5", "tuned", ""), ("k7", "tuned", "")],
    "go": [("k1", "soa", "energy"), ("k5", "tuned", ""), ("k6", "tuned", "q6"), ("k6", "mt", "q6")],
    "java": [("k1", "soa", "energy"), ("k5", "tuned", ""), ("k6", "tuned", "q6"), ("k6", "tuned", "q1"),
             ("k6", "mt", "q6"), ("k6", "mt", "q1")],
}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for lang, keys in KEYS.items():
        for k, v, p in keys:
            reps = calib[f"{lang}|{k}|{v}|{p}"]["reps"]
            for impl in (lang, lang + "_std"):
                out.append((impl, lang, k, v, p, reps))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"confrontation : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, lang, k, v, p, reps in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", "10" if lang in JIT else "2", "--tag", "conf",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"confrontation : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "confrontation : fin\n")


if __name__ == "__main__":
    main()
