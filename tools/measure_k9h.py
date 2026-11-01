#!/usr/bin/env python3
"""Mesures du harnais commun de K9 (plan : docs/K9.md, section 3), machine 16 (Emerald Rapids, results/hw/machine16).

Cellules (sortie results/raw_k9h/<implémentation>.jsonl, étiquette « k9h ») :
* ancien harnais : les 26 implémentations classées et annexes, telles que publiées (Ada : ada_fix ; Fortran :
  fortran_fix, corrections publiées comprises), K9 natural, tuned et mt ;
* harnais commun : leurs copies bench/<implémentation>_k9h (tools/k9h/make_copies.py), pour les variantes dont le
  harnais change (toutes, sauf tuned et mt de Fortran, flang, JavaScript et Bun, qui allouaient déjà une fois ; C,
  C par gcc, Chapel et Ada allouaient une fois dans les trois) ;
* copies de sensibilité, harnais commun seulement : rust_nat_k9h et nim_nat_k9h (naturel), csharp_exp_k9h (mt et
  mt_pool), zig_master_k9h (les trois).
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json (clés du langage d'origine) ; échauffements de la campagne (3 pour les JIT,
1 sinon) ; règle de vol du pilote (processus refait au-delà de 2 % de la capacité des 4 vCPU, deux fois au plus).
Usage : measure_k9h.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_k9h")
PASSES = 7
SEED = 20261101 + 2000
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}
V3 = ("natural", "tuned", "mt")
OLD = ["c", "c_gcc", "chapel", "ada_fix", "cpp", "csharp", "java", "zig", "odin", "julia", "fortran_fix", "js", "python",
       "haskell", "c3", "d", "rust", "nim", "mojo", "go", "ocaml", "lua", "fortran_flang", "luajit", "js_bun", "python_ft"]
NEW_ALL = ["cpp", "csharp", "java", "zig", "odin", "julia", "python", "haskell", "c3", "d", "rust", "nim", "mojo", "go",
           "ocaml", "lua", "luajit", "python_ft"]
NEW_NAT = ["fortran_fix", "js", "fortran_flang", "js_bun"]
SENS = {"rust_nat_k9h": ["natural"], "nim_nat_k9h": ["natural"], "csharp_exp_k9h": ["mt", "mt_pool"],
        "zig_master_k9h": list(V3)}
BASE = {"ada_fix": "ada", "fortran_fix": "fortran", "rust_nat": "rust", "nim_nat": "nim", "csharp_exp": "csharp",
        "mojo_noassert": "mojo", "zig_master": "zig"}


def base_lang(impl):
    b = impl[:-4] if impl.endswith("_k9h") else impl
    return BASE.get(b, b)


def cells():
    c = [(i, v) for i in OLD for v in V3]
    c += [(f"{i}_k9h", v) for i in NEW_ALL for v in V3]
    c += [(f"{i}_k9h", "natural") for i in NEW_NAT]
    c += [(i, v) for i, vs in SENS.items() for v in vs]
    return c


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, v in cells():
        b = base_lang(impl)
        reps = calib[f"{b}|k9|{'mt' if v == 'mt_pool' else v}|"]["reps"]
        out.append((impl, v, reps, 3 if b in JIT else 1))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        for j in js:
            print(*j)
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"harnais de K9 : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, v, reps, w in order:
            args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", "k9", "--variants", v,
                    "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", "k9h",
                    "--out", os.path.join(OUT, f"{impl}.jsonl")]
            with open(os.path.join(OUT, f"{impl}.log"), "a") as lf:
                subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"harnais de K9 : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "harnais de K9 : fin\n")


if __name__ == "__main__":
    main()
