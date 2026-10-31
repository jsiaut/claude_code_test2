#!/usr/bin/env python3
"""Mesures de la vérification de la remarque sur C# (plan : docs/CSHARP.md, section 3), sur l'hôte Emerald Rapids
actuel (machine 9). Sensibilités et informations : aucune de ces mesures n'entre dans le classement publié.

Implémentations (toutes sur le même hôte, appariées par passe) :
* csharp : binaire de la campagne, protocole des données principales (P0 : 3 échauffements ; 10 pour K5, comme la
  remesure v2 de K5) ;
* csharp_full : même binaire, compilation à niveaux désactivée (P1 : optimisation complète dès le premier appel) ;
* csharp_steady : même binaire et mêmes réglages, 120 échauffements (P2 : régime établi, niveau 1 avec PGO dynamique),
  sur les 16 clés dont la méthode chaude atteint le niveau 1 en 120 appels (section 2) ;
* csharp_net11 : même binaire exécuté par le runtime .NET 11 RC3 (préversion), protocole P0 ;
* csharp_exp : formes de la remarque (K4 sans branchement déroulé, Q1 en variables locales, K8 itératif), SIMD
  explicite de K4 et threads du pool (mt_pool), protocole P0 ; csharp_exp_full : la même copie en P1 ;
* csharp_nat2 : autres choix de code naturel (K1 : struct dans List<T> ; K6 : colonnes en paramètres), P0 ;
* c (clang, binaire de la campagne) : témoin du même hôte sur les 26 clés transférées ; c_exp, c_gcc, c_gcc_exp :
  K8 tuned récursif et itératif, par clang et par GCC.
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json (clé de l'implémentation d'origine). Empreinte de K1 (csharp et csharp_nat2,
3 processus chacun) après les passes. Sortie : results/raw_csharp/<implémentation>.jsonl, étiquette « csharp ».
Usage : measure_csharp.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_csharp")
PASSES = 7
SEED = 20261031 + 200
ALL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"),
       ("k1", "soa", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
       ("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""),
       ("k4", "branchless_unsorted", ""), ("k5", "natural", ""), ("k5", "tuned", ""), ("k6", "natural", "q6"),
       ("k6", "tuned", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q6"), ("k6", "mt", "q1"),
       ("k7", "natural", ""), ("k7", "tuned", ""), ("k8", "natural", ""), ("k8", "tuned", ""), ("k9", "natural", ""),
       ("k9", "tuned", ""), ("k9", "mt", "")]
STEADY = [("k1", "natural", "energy"), ("k1", "aos", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"),
          ("k3", "sw_padded", ""), ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""),
          ("k5", "natural", ""), ("k5", "tuned", ""), ("k6", "natural", "q6"), ("k6", "tuned", "q6"),
          ("k6", "natural", "q1"), ("k6", "mt", "q6"), ("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")]
EXP = [("k4", "branchless_unsorted", ""), ("k4", "simd_unsorted", ""), ("k6", "tuned", "q1"), ("k6", "mt", "q1"),
       ("k6", "mt", "q6"), ("k6", "mt_pool", "q6"), ("k6", "mt_pool", "q1"), ("k8", "tuned", ""), ("k9", "mt", ""),
       ("k9", "mt_pool", ""), ("k9", "tuned", ""), ("k6", "tuned", "q6")]
EXP_FULL = [("k4", "branchless_unsorted", ""), ("k6", "tuned", "q1"), ("k6", "mt", "q1"), ("k8", "tuned", "")]
NAT2 = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k6", "natural", "q6"),
        ("k6", "natural", "q1"), ("k1", "aos", "energy")]
K8T = [("k8", "tuned", "")]
CELLS = {"csharp": ALL, "csharp_full": ALL, "csharp_steady": STEADY, "csharp_net11": ALL, "csharp_exp": EXP,
         "csharp_exp_full": EXP_FULL, "csharp_nat2": NAT2, "c": ALL, "c_exp": K8T, "c_gcc": K8T, "c_gcc_exp": K8T}
BASE = {"c_exp": "c", "c_gcc_exp": "c_gcc", "c_gcc": "c_gcc", "c": "c"}
# variantes propres aux copies : répétitions de la variante d'origine
CALIB_VARIANT = {"simd_unsorted": "branchless_unsorted", "mt_pool": "mt"}


def warmup(impl, k):
    """Échauffements des données principales : 1 (2 pour K5) en compilé, 3 (10 pour K5) en C# ; 120 en régime établi."""
    if not impl.startswith("csharp"):
        return 2 if k == "k5" else 1
    if impl == "csharp_steady":
        return 120
    return 10 if k == "k5" else 3


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = BASE.get(impl, "csharp")
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, tag="csharp"):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", tag,
            "--out", os.path.join(OUT, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=1800)


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C# : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque C# : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    for impl in ("csharp", "csharp_nat2"):  # empreinte de K1 (D2a), méthode en deux points de analysis/footprint.py
        for _ in range(3):
            driver(impl, "fp", "footprint", "energy", 1, 1, tag="csharp_fp")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque C# : fin\n")


if __name__ == "__main__":
    main()
