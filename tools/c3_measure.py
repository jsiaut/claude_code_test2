#!/usr/bin/env python3
"""Capacité C3 (auto-vectorisation) mesurée, et non déclarée : on profile K4 natural_unsorted et
K9 natural avec tools/sampler.c, on désassemble la boucle chaude (analysis/hotloop.py) et on
regarde si elle contient des instructions SIMD empaquetées.
C3 = 1 si les deux boucles chaudes sont vectorisées, 0,5 si une seule l'est, 0 sinon.
Sorties : results/vectorization/<langage>_<noyau>.txt et results/vectorization.json."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import hotloop  # noqa: E402

LANGS = ["c", "cpp", "csharp", "java", "zig", "odin", "julia", "ada", "fortran", "js", "python", "haskell",
         "c3", "d", "rust", "chapel", "nim", "mojo", "go", "ocaml", "lua", "c_gcc", "fortran_flang", "luajit", "js_bun"]
KERNELS = [("k4", "natural_unsorted", ""), ("k9", "natural", "")]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}


def main():
    outdir = os.path.join(ROOT, "results", "vectorization")
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for lang in (sys.argv[1:] or LANGS):
        flags = []
        for k, v, p in KERNELS:
            prefix = os.path.join(outdir, f"{lang}_{k}")
            env = dict(os.environ, WARMUP="3" if lang in JIT else "1")
            # assez de répétitions pour que le noyau domine le chargement des données (profil > 0,3 s)
            reps = "60" if k == "k4" else "20"
            cmd = ["/opt/sampler", "-f", "4000", "-o", prefix, "--", os.path.join(ROOT, "bench", lang, "run"), k, v, reps] + ([p] if p else [])
            subprocess.run(cmd, cwd=os.path.join(ROOT, "bench", lang), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    hotloop.main(prefix)
                except Exception as e:  # noqa: BLE001
                    print("erreur", e)
            text = buf.getvalue()
            open(prefix + ".txt", "w").write(text)
            vec = "'vectorized': True" in text.splitlines()[0] if text else False
            flags.append(vec)
            print(lang, k, "vectorisée" if vec else "scalaire", text.splitlines()[0][:150] if text else "")
        res[lang] = (1.0 if all(flags) else 0.5 if any(flags) else 0.0)
    path = os.path.join(ROOT, "results", "vectorization.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(res)
    json.dump(old, open(path, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
