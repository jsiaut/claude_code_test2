#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Zig (plan : docs/ZIG.md, section 3), sur l'hôte Cascade Lake actuel
(machine 5).

Plan apparié : Zig 0.17.0 (bench/zig, binaire de la campagne) et Zig 0.18.0-dev (bench/zig_master, même source) sur
les 27 clés qui entrent dans le score ; les deux copies où les threads de K3, K6 mt et K9 mt passent par Io.Group
(bench/zig_io en 0.17, bench/zig_master_io en master) sur ces 5 clés ; C (bench/c) sur 5 clés, en témoin du même hôte.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions figées par results/calib.json (clé de Zig, ou de C pour C), échauffement de 2 répétitions.
Sortie : results/raw_zig/<implémentation>.jsonl, étiquette « zig ». Usage : measure_zig.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from analyze_v3 import needed_keys  # noqa: E402

OUT = os.path.join(ROOT, "results", "raw_zig")
PASSES = 7
SEED = 20261030 + 50
SCORE_KEYS = sorted(needed_keys())  # les 27 clés du score
THREAD_KEYS = [("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k6", "mt", "q6"), ("k6", "mt", "q1"), ("k9", "mt", "")]
C_KEYS = [("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""), ("k5", "tuned", ""), ("k9", "natural", ""),
          ("k9", "mt", "")]
CELLS = {"zig": SCORE_KEYS, "zig_master": SCORE_KEYS, "zig_io": THREAD_KEYS, "zig_master_io": THREAD_KEYS, "c": C_KEYS}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "zig"
        for k, v, p in keys:
            out.append((impl, k, v, p, calib[f"{base}|{k}|{v}|{p}"]["reps"]))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Zig : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", "2", "--tag", "zig",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Zig : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Zig : fin\n")


if __name__ == "__main__":
    main()
