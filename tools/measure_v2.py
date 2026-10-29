#!/usr/bin/env python3
"""Nouvelles mesures de l'analyse v2 (plan : docs/ANALYSIS_V2.md, section 2), sur la machine 3 (Emerald Rapids).

Chaque processus est précédé du témoin d'environnement (hwprobe witness).
  k5   K5 natural et tuned, toutes les implémentations : 9 processus en 9 passes, ordre tiré au hasard (graine fixe).
       Échauffement de 10 répétitions pour les JIT, 2 pour les autres. 20 répétitions mesurées, ou le nombre figé par
       results/calib.json si une répétition dépasse 1 s. Étiquette v2_k5 : ces données remplacent toutes les données
       de K5 dans l'analyse v2.
  thp  Pages géantes (descriptif) : K1 natural, un processus par implémentation, relevé de AnonHugePages. Étiquette
       v2_thp.
  m3   Réplication (descriptive) : une passe de K1-K4 et K6-K9, un processus par mesure, toutes les implémentations,
       répétitions de la campagne (results/calib.json), ordre des blocs tiré au hasard. Étiquette v2_m3.

Sortie : results/raw_v2/<implémentation>.jsonl (l'analyse v1 ne lit pas ce répertoire).
Usage : measure_v2.py [k5] [thp] [m3]   (par défaut les trois, dans cet ordre)"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_v2")
LANGS = ["ada", "c", "c3", "c_gcc", "chapel", "cpp", "csharp", "d", "fortran", "fortran_flang", "go", "haskell",
         "java", "js", "js_bun", "julia", "lua", "luajit", "mojo", "nim", "ocaml", "odin", "python", "rust", "zig"]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}
PASSES = 9
SEED = 20261029
M3_DEFAULT = ["k1", "k2", "k3", "k4", "k6", "k7", "k8", "k9"]
M3_KERNELS = {"python_ft": ["k3", "k6", "k9"]}


def driver(lang, args, lf):
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "driver.py"), lang, "--procs", "1",
                    "--out", os.path.join(OUT, f"{lang}.jsonl")] + args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)


def main():
    os.makedirs(OUT, exist_ok=True)
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    steps = sys.argv[1:] or ["k5", "thp", "m3"]
    if "k5" in steps:
        for p in range(PASSES):
            jobs = [(l, v) for l in LANGS for v in ("natural", "tuned")]
            random.Random(SEED + p).shuffle(jobs)
            for l, v in jobs:
                c = calib[f"{l}|k5|{v}|"]
                reps = c["reps"] if c["t_cal"] > 1.0 else 20
                with open(os.path.join(OUT, f"{l}.log"), "a") as lf:
                    driver(l, ["--kernels", "k5", "--variants", v, "--reps", str(reps),
                               "--warmup", "10" if l in JIT else "2", "--witness", "--tag", "v2_k5"], lf)
            log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"v2 : K5 natural et tuned, passe {p + 1}/{PASSES} terminée\n")
            log.flush()
            print(f"K5 passe {p + 1}/{PASSES}", flush=True)
    if "thp" in steps:
        jobs = list(LANGS)
        random.Random(SEED + 100).shuffle(jobs)
        for l in jobs:
            with open(os.path.join(OUT, f"{l}.log"), "a") as lf:
                driver(l, ["--kernels", "k1", "--variants", "natural", "--warmup", "3" if l in JIT else "1",
                           "--witness", "--thp", "--tag", "v2_thp"], lf)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "v2 : relevé des pages géantes (K1 natural) terminé\n")
        log.flush()
        print("THP terminé", flush=True)
    if "m3" in steps:
        blocks = [(l, k) for l in LANGS + ["python_ft"] for k in M3_KERNELS.get(l, M3_DEFAULT)]
        random.Random(SEED + 200).shuffle(blocks)
        for i, (l, k) in enumerate(blocks):
            t0 = time.time()
            with open(os.path.join(OUT, f"{l}.log"), "a") as lf:
                driver(l, ["--kernels", k, "--warmup", "3" if l in JIT else "1", "--pass", "0", "--witness",
                           "--tag", "v2_m3"], lf)
            log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"v2 : réplication, bloc {i + 1}/{len(blocks)} {l} {k} "
                      f"{time.time() - t0:.0f}s\n")
            log.flush()
        print("réplication terminée", flush=True)


if __name__ == "__main__":
    main()
