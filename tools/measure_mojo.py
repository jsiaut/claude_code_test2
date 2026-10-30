#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Mojo (plan : docs/MOJO.md, section 3), sur l'hôte Cascade Lake
actuel (machine 6). Diagnostics seulement : aucune de ces mesures n'entre dans le classement publié.

* mojo : binaire de la campagne (recompilé par son script inchangé, identique octet pour octet au binaire compilé
  sur la machine 2) ; mojo_noassert : même source compilée avec -D ASSERT=none ; mojo_exp : K4 en SIMD explicite
  (simd_unsorted ; simd_cold, caches vidés avant chaque répétition) et K4 sans branchement en témoin ; c : C par
  clang, témoin du même hôte.
* 7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
  fixe). Répétitions de results/calib.json (clé de l'implémentation d'origine ; pour simd_*, celle de K4 sans
  branchement), échauffement de 2. Sortie : results/raw_mojo/<implémentation>.jsonl, étiquette « mojo ».
Usage : measure_mojo.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_mojo")
PASSES = 7
SEED = 20261030 + 80
K4N, K4S, K4B = ("k4", "natural_unsorted", ""), ("k4", "natural_sorted", ""), ("k4", "branchless_unsorted", "")
K9N, Q1N, Q6N = ("k9", "natural", ""), ("k6", "natural", "q1"), ("k6", "natural", "q6")
SIMD, SIMD_COLD = ("k4", "simd_unsorted", ""), ("k4", "simd_cold", "")
CELLS = {"mojo": [K4N, K4S, K4B, K9N, Q1N, Q6N], "mojo_noassert": [K4N, K4B, K9N, Q1N, Q6N],
         "mojo_exp": [SIMD, SIMD_COLD, K4B], "c": [K4N, K4B, K9N, Q1N]}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "mojo" if impl.startswith("mojo") else impl
        for k, v, p in keys:
            cv = "branchless_unsorted" if v.startswith("simd") else v
            out.append((impl, k, v, p, calib[f"{base}|{k}|{cv}|{p}"]["reps"]))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Mojo : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", "2", "--tag", "mojo",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Mojo : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Mojo : fin\n")


if __name__ == "__main__":
    main()
