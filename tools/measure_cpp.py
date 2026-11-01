#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur C++ (plan : docs/CPP.md, section 3), sur l'hôte Emerald Rapids actuel
(machine 15, results/hw/machine15). Deux parties, mêlées au hasard dans chaque passe :

1. Copies de C++ et de C (sensibilités et informations, hors classement publié), sortie
   results/raw_cpp/<implémentation>.jsonl, étiquette « cpp » ; copies générées par tools/cpp_check/make_copies.py :
   * cpp_ref   : source de la campagne (bench/cpp/ms.cpp), g++ 16, options du banc (référence des rapports ; binaire
                 identique à l'octet à celui de la réplication sur Emerald Rapids, results/hw/machine3/binaries.txt) ;
   * cpp_clang : source de cpp_intr compilé par clang++ 23 (libstdc++ de GCC 16) ;
   * cpp_all   : cpp_intr + cpp_k9 + cpp_k8, compilé par clang++ 23 (les corrections 1 à 4 de la remarque) ;
   * cpp_intr  : K1 soa, K5 tuned, Q6 tuned et Q1 tuned dans la forme de C (intrinsèques AVX-512), g++ 16 ;
   * cpp_k9    : grilles de K9 allouées une seule fois, comme C, g++ 16 ;
   * cpp_k8    : arène de K8 tuned passée par pointeur brut, comme C, g++ 16 ;
   * c_ref     : source C de la campagne, clang 23, options du banc (témoin du même hôte ; binaire identique à l'octet à
                 celui de la réplication) ;
   * c_k9      : source C, grilles de K9 réallouées à chaque répétition (la pratique de la plupart des langages), clang 23.
   Répétitions de results/calib.json (clés de C++ pour les copies C++, de C pour les copies C) ; échauffements des
   données principales (1 ; 2 pour K5).
2. Remesure de D2 et D4 (publiée, comme celle de D3 pour la remarque sur Rust) : K1 naturel et mélangé, K2 à 16 Kio,
   256 Kio et 8 Mio, les 25 implémentations de la campagne (binaires de bench/, ceux de la remesure de D3), sortie
   results/raw_d24/<implémentation>.jsonl, étiquette « d24_m15 ». Échauffements de la campagne (3 pour les JIT, 1 sinon),
   répétitions de results/calib.json.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules des deux parties dans un ordre tiré au
hasard (graine fixe). Règle de vol du pilote (processus refait au-delà de 2 % de la capacité des 4 vCPU, deux fois au
plus).
Usage : measure_cpp.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_cpp")
OUT_D24 = os.path.join(ROOT, "results", "raw_d24")
PASSES = 7
SEED = 20261101 + 900
K5T = ("k5", "tuned", "")
K9 = [("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")]
SCORE = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
         ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
         ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""),
         ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), K5T, ("k6", "natural", "q6"), ("k6", "tuned", "q6"),
         ("k6", "mt", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k7", "natural", ""),
         ("k7", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", ""), ("k8", "tuned_alloc", "")] + K9
# clés des quatre noyaux std::simd (K1 soa, K5 tuned, Q6 tuned et mt, Q1 tuned et mt)
INTR = [("k1", "soa", "energy"), K5T, ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q1")]
CELLS = {"cpp_ref": SCORE, "cpp_clang": SCORE, "cpp_all": SCORE, "cpp_intr": INTR, "cpp_k9": K9,
         "cpp_k8": [("k8", "tuned", "")], "c_ref": [k for k in SCORE if k != ("k8", "tuned_alloc", "")], "c_k9": K9}
# partie 2 : clés de D2 (K1 naturel et mélangé) et de D4 (K2 aux trois tailles), les 25 implémentations de la campagne
D24_KEYS = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k2", "tuned", "16384"),
            ("k2", "tuned", "262144"), ("k2", "tuned", "8388608")]
D24_LANGS = ["ada", "c", "c3", "c_gcc", "chapel", "cpp", "csharp", "d", "fortran", "fortran_flang", "go", "haskell",
             "java", "js", "js_bun", "julia", "lua", "luajit", "mojo", "nim", "ocaml", "odin", "python", "rust", "zig"]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl.startswith("c_") else "cpp"
        for k, v, p in keys:
            out.append(("cpp", impl, k, v, p, calib[f"{base}|{k}|{v}|{p}"]["reps"], 2 if k == "k5" else 1))
    for l in D24_LANGS:
        for k, v, p in D24_KEYS:
            out.append(("d24", l, k, v, p, calib[f"{l}|{k}|{v}|{p}"]["reps"], 3 if l in JIT else 1))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(OUT_D24, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        n1 = sum(1 for j in js if j[0] == "cpp")
        print(f"{len(js)} cellules ({n1} copies, {len(js) - n1} remesure de D2 et D4) x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C++ : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for part, impl, k, v, p, reps, w in order:
            out = OUT if part == "cpp" else OUT_D24
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "cpp" if part == "cpp" else "d24_m15",
                    "--out", os.path.join(out, f"{impl}.jsonl")]
            if p:
                args += ["--params", p]
            with open(os.path.join(out, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C++ : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque C++ : fin\n")


if __name__ == "__main__":
    main()
