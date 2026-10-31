#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur Rust (plan : docs/RUST.md, section 3), sur l'hôte Emerald Rapids actuel
(machine 11). Deux parties, entrelacées dans les mêmes passes :

1. Paires Rust (même hôte, appariées par passe), sortie results/raw_rust/<implémentation>.jsonl, étiquette « rust » :
   * rust_ref : source de la campagne (bench/rust/ms.rs) recompilé sur l'hôte (référence des paires) ;
   * rust_fix : K7 optimisé avec _MM_HINT_ET0 (correction publiée) ;
   * rust_nat : K9 naturel en Vec<[f64; M9]> ; rust_k8 : K8 optimisé en arène écrite comme en C (sensibilités) ;
   * rust_cl / rust_clpop : source de la campagne compilé pour Cascade Lake, sans et avec _popcnt32 (sensibilité Q1) ;
   * c : binaire C de bench/c (compilé pour Cascade Lake), témoin des ponts.
   Échauffements des données principales (1 ; 2 pour K5), répétitions de results/calib.json.
2. Remesure de D3 : K8 naturel, les 25 implémentations de la campagne, sortie results/raw_d3/<implémentation>.jsonl,
   étiquette « d3_m11 ». Échauffements de la campagne (3 pour les JIT, 1 sinon), répétitions de results/calib.json.

7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe).
Règle de vol du pilote (processus refait au-delà de 2 % de la capacité des 4 vCPU, deux fois au plus).
Usage : measure_rust.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_R = os.path.join(ROOT, "results", "raw_rust")
OUT_D3 = os.path.join(ROOT, "results", "raw_d3")
PASSES = 7
SEED = 20261031 + 400
K7T, K8T, K8N = ("k7", "tuned", ""), ("k8", "tuned", ""), ("k8", "natural", "")
K9N, K9T = ("k9", "natural", ""), ("k9", "tuned", "")
Q1T, Q1M, Q6T = ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k6", "tuned", "q6")
K4B, K5T, K1A = ("k4", "branchless_unsorted", ""), ("k5", "tuned", ""), ("k1", "aos", "energy")
WIT = [K7T, K8T, K9N, K9T, Q1T, Q1M, Q6T, K4B, K5T, K1A]
CELLS = {"rust_ref": WIT, "rust_fix": [K7T, K9T, Q6T, K1A], "rust_nat": [K9N, K9T], "rust_k8": [K8T, K8N],
         "rust_cl": [Q1T, Q1M], "rust_clpop": [Q1T, Q1M], "c": WIT}
D3_LANGS = ["ada", "c", "c3", "c_gcc", "chapel", "cpp", "csharp", "d", "fortran", "fortran_flang", "go", "haskell",
            "java", "js", "js_bun", "julia", "lua", "luajit", "mojo", "nim", "ocaml", "odin", "python", "rust", "zig"]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl == "c" else "rust"
        for k, v, p in keys:
            out.append(("rust", impl, k, v, p, calib[f"{base}|{k}|{v}|{p}"]["reps"], 2 if k == "k5" else 1))
    for l in D3_LANGS:
        out.append(("d3", l, "k8", "natural", "", calib[f"{l}|k8|natural|"]["reps"], 3 if l in JIT else 1))
    return out


def main():
    os.makedirs(OUT_R, exist_ok=True)
    os.makedirs(OUT_D3, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Rust : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for part, impl, k, v, p, reps, w in order:
            out = OUT_R if part == "rust" else OUT_D3
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "rust" if part == "rust" else "d3_m11",
                    "--out", os.path.join(out, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(out, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Rust : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Rust : fin\n")


if __name__ == "__main__":
    main()
