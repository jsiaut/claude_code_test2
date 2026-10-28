#!/usr/bin/env python3
"""Remesure des mesures instables (règle du journal de docs/METHODOLOGY.md, 2026-10-28 18:28) :
K5 tuned et K10 tuned, toutes les implémentations, 9 processus en 9 passes d'ordre aléatoire,
sur la machine d'après redémarrage. Sortie : results/raw_post/<langage>.jsonl, étiquette post_noisy."""
import os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_post")
LANGS = ["ada", "c", "c3", "c_gcc", "chapel", "cpp", "csharp", "d", "fortran", "fortran_flang", "go", "haskell",
         "java", "js", "js_bun", "julia", "lua", "luajit", "mojo", "nim", "ocaml", "odin", "python", "python_ft", "rust", "zig"]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}
PASSES = 9


def main():
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    for p in range(PASSES):
        jobs = [(l, k) for l in LANGS for k in ("k5", "k10") if not (l == "python_ft" and k == "k5")]
        random.Random(20261028 + 100 + p).shuffle(jobs)
        for l, k in jobs:
            with open(os.path.join(OUT, f"{l}.log"), "a") as lf:
                subprocess.run([sys.executable, os.path.join(ROOT, "tools", "driver.py"), l, "--kernels", k, "--variants", "tuned",
                                "--procs", "1", "--warmup", "3" if l in JIT else "1", "--tag", "post_noisy",
                                "--out", os.path.join(OUT, f"{l}.jsonl")], stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remesure K5/K10 tuned : passe {p + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {p + 1}/{PASSES}", flush=True)


if __name__ == "__main__":
    main()
