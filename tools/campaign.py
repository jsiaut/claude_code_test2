#!/usr/bin/env python3
"""Campagne finale (docs/METHODOLOGY.md, section 6).

Trois passes. Dans chaque passe, chaque bloc (langage, noyau) exécute UN processus de mesure
par variante (driver.py --pass N). L'ordre des blocs est tiré au hasard avec une graine fixe,
différente à chaque passe. Les trois processus d'une même mesure sont ainsi pris à des moments
différents, et la dérive temporelle de la machine (VM partagée) n'est pas confondue avec
l'identité du langage. La première passe fige le nombre de répétitions (results/calib.json).

Usage : campaign.py [--passes 0,1,2] [--langs c,rust,...]
"""
import argparse, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# langages classés (implémentation de référence de chaque langage)
LANGS = ["c", "cpp", "csharp", "java", "zig", "odin", "julia", "ada", "fortran", "js", "python", "haskell",
         "c3", "d", "rust", "chapel", "nim", "mojo", "go", "ocaml", "lua"]
# implémentations ou compilateurs alternatifs, mesurés à titre indicatif
ANNEX = ["c_gcc", "fortran_flang", "luajit", "js_bun", "python_ft"]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}
KERNELS = ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9", "k10", "fp"]
# CPython sans GIL : seul l'intérêt multi-thread justifie l'annexe (le code mono-thread est celui de python)
KERNELS_BY_LANG = {"python_ft": ["k3", "k6", "k9", "k10"]}


def log(msg):
    line = time.strftime("%Y-%m-%dT%H:%M:%S ") + msg
    print(line, flush=True)
    with open(os.path.join(ROOT, "results", "campaign.log"), "a") as f:
        f.write(line + "\n")


def hwfreq(tag):
    os.makedirs(os.path.join(ROOT, "results", "hw"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "hw", f"freq_{tag}.txt"), "w") as f:
        subprocess.run(["/opt/hwprobe", "freq"], stdout=f, stderr=subprocess.STDOUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passes", default="0,1,2")
    ap.add_argument("--langs", default=",".join(LANGS + ANNEX))
    a = ap.parse_args()
    langs = [l for l in a.langs.split(",") if os.path.exists(os.path.join(ROOT, "bench", l, "run"))]
    os.makedirs(os.path.join(ROOT, "results", "raw"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "results", "log"), exist_ok=True)
    for p in [int(x) for x in a.passes.split(",")]:
        hwfreq(f"pass{p}_start")
        blocks = [(l, k) for l in langs for k in KERNELS_BY_LANG.get(l, KERNELS)]
        random.Random(20261028 + p).shuffle(blocks)
        log(f"passe {p} : {len(blocks)} blocs")
        for i, (l, k) in enumerate(blocks):
            t0 = time.time()
            with open(os.path.join(ROOT, "results", "log", f"{l}.log"), "a") as lf:
                subprocess.run([sys.executable, os.path.join(ROOT, "tools", "driver.py"), l, "--kernels", k,
                                "--warmup", "3" if l in JIT else "1", "--pass", str(p),
                                "--out", os.path.join(ROOT, "results", "raw", f"{l}.jsonl")],
                               stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
            log(f"passe {p} bloc {i + 1}/{len(blocks)} {l} {k} {time.time() - t0:.0f}s")
        hwfreq(f"pass{p}_end")
    log("campagne terminée")


if __name__ == "__main__":
    main()
