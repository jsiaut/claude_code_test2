#!/usr/bin/env python3
"""Mesures faites après le redémarrage de la VM (écart consigné dans docs/METHODOLOGY.md).

* fp : empreinte K1 par pic RSS (footprint, footprint_raw, footprint0), 3 processus par variante.
  Méthode invalide pour 8 langages (le pic du chargement masque la collection) : conservée pour la
  trace, remplacée par fp2.
* fp2 : empreinte K1 en deux points dans le processus (tools/patch_footprint_mem.py), 3 processus
  par langage, ordre tiré au hasard (graine fixe). Indépendante de la vitesse de la machine (octets).
* k3b : remesure de K3 pour Haskell (binaire corrigé) et pour C (pont), 3 processus à la suite,
  en alternant les deux langages.
* annex : mesures descriptives, hors classement, sur la machine d'après redémarrage :
  - effet de BUN_OPTIONS=--smol (hérité de l'environnement pendant la campagne) sur l'annexe Bun,
    K1 natural, K8 natural et empreinte, avec et sans la variable, en alternance ;
  - Valhalla (JEP 401, build EA) : K1 avec un tableau d'objets valeur, comparé au Java standard
    mesuré dans les mêmes conditions.
Sortie : results/raw_post/<langage>.jsonl, jamais mêlée à results/raw/.
"""
import os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_post")
LANGS = ["ada", "c", "c3", "c_gcc", "chapel", "cpp", "csharp", "d", "fortran", "fortran_flang", "go", "haskell",
         "java", "js", "js_bun", "julia", "lua", "luajit", "mojo", "nim", "ocaml", "odin", "python", "rust", "zig"]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}


def drive(lang, kernel, variants, procs, tag):
    with open(os.path.join(OUT, f"{lang}.log"), "a") as lf:
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "driver.py"), lang, "--kernels", kernel,
                        "--variants", variants, "--procs", str(procs), "--warmup", "3" if lang in JIT else "1",
                        "--tag", tag, "--out", os.path.join(OUT, f"{lang}.jsonl")],
                       stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, check=False)


def log(msg):
    with open(os.path.join(ROOT, "results", "campaign.log"), "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + msg + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    what = sys.argv[1:] or ["fp", "k3b"]
    if "fp" in what:
        jobs = [(l, v) for l in LANGS for v in ("footprint", "footprint_raw", "footprint0") for _ in range(3)]
        random.Random(20261028).shuffle(jobs)
        log(f"post-redémarrage : empreinte K1, {len(jobs)} processus")
        for i, (l, v) in enumerate(jobs):
            drive(l, "fp", v, 1, "post_fp")
            if i % 25 == 0:
                print(f"fp {i}/{len(jobs)}", flush=True)
        log("post-redémarrage : empreinte K1 terminée")
    if "fp2" in what:  # méthode en deux points (tools/patch_footprint_mem.py), 3 processus par langage
        jobs = [l for l in LANGS for _ in range(3)]
        random.Random(20261029).shuffle(jobs)
        log(f"post-redémarrage : empreinte K1 en deux points, {len(jobs)} processus")
        for i, l in enumerate(jobs):
            drive(l, "fp", "footprint", 1, "post_fp2")
        log("post-redémarrage : empreinte K1 en deux points terminée")
    if "k3b" in what:
        log("post-redémarrage : K3 haskell + pont C")
        for p in range(3):
            for l in ("c", "haskell"):
                drive(l, "k3", "rmw_packed,rmw_padded,sw_packed,sw_padded", 1, "post_k3")
            print(f"k3 {p + 1}/3", flush=True)
        log("post-redémarrage : K3 terminé")
    if "annex" in what:
        log("post-redémarrage : annexes (Bun --smol, Valhalla)")
        for p in range(3):
            for smol in (True, False):
                env = dict(os.environ)
                if smol:
                    env["BUN_OPTIONS"] = "--smol"
                else:
                    env.pop("BUN_OPTIONS", None)
                tag = "smol" if smol else "nosmol"
                for k, v in (("k1", "natural"), ("k8", "natural"), ("fp", "footprint")):
                    with open(os.path.join(OUT, "js_bun_smol.log"), "a") as lf:
                        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "driver.py"), "js_bun", "--kernels", k,
                                        "--variants", v, "--procs", "1", "--warmup", "3", "--tag", tag,
                                        "--out", os.path.join(OUT, "js_bun_smol.jsonl")],
                                       stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, env=env, check=False)
            drive("java", "k1", "natural,natural_shuffled", 1, "post_valhalla_ref")
            with open(os.path.join(OUT, "java_valhalla.txt"), "a") as f:
                for args in (["array", "5"], ["array", "5", "shuffled"], ["list", "5"], ["list", "5", "shuffled"]):
                    r = subprocess.run([os.path.join(ROOT, "bench", "java_valhalla", "run.sh")] + args,
                                       capture_output=True, text=True, cwd=ROOT)
                    f.write(f"# pass {p} args {' '.join(args)}\n{r.stdout}{r.stderr[-500:]}\n")
            print(f"annex {p + 1}/3", flush=True)
        log("post-redémarrage : annexes terminées")


if __name__ == "__main__":
    main()
