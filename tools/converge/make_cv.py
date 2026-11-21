#!/usr/bin/env python3
"""v4, point 4 (docs/V4_CONVERGE.md, 4.1, écart 1, et 5) : copies bench/<langage>_cv. Chacune part de la source publiée
corrigée (bench/<langage>) ; les variantes du point 3 y sont reportées : la différence entre la source publiée au commit
qui a créé bench/<langage>_eq et cette copie (K4 tuned, K9 natural_flat) est appliquée à la copie. Les formes du
catalogue sont écrites ensuite, à la main, et déclarées dans cv_variants.
Usage : make_cv.py [essai|créer] [langage,...]"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LANGS = ["c", "odin", "cpp", "c3", "zig", "rust", "nim", "d", "ada", "chapel", "fortran", "swift", "julia", "mojo",
         "csharp", "fpc", "java", "go", "haskell", "ocaml", "bqn", "php", "js", "python", "lua"]
SKIP = {"ms", "bin", "obj", "nimcache", "classes", ".zig-cache", "zig-cache", "ms_nat", "ms_tuned", "ms_fm"}


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, check=True).stdout


def tracked(d):
    return [os.path.relpath(f, d) for f in git("ls-files", d).split()]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "essai"
    langs = sys.argv[2].split(",") if len(sys.argv) > 2 else LANGS
    for lang in langs:
        src, eq, cv = f"bench/{lang}", f"bench/{lang}_eq", f"bench/{lang}_cv"
        notes = []
        if mode == "créer":
            shutil.rmtree(os.path.join(ROOT, cv), ignore_errors=True)
            for f in tracked(src):
                os.makedirs(os.path.dirname(os.path.join(ROOT, cv, f)), exist_ok=True)
                shutil.copy2(os.path.join(ROOT, src, f), os.path.join(ROOT, cv, f))
        for f in tracked(eq):
            if f in ("eq_variants", "build.sh"):  # build.sh : celui de la source corrigée (hooks des points 2 et 3 compris)
                continue
            c = git("log", "--diff-filter=A", "--format=%h", "--", f"{eq}/{f}").split()[-1]
            try:
                ref = git("show", f"{c}^:{src}/{f}")
            except subprocess.CalledProcessError:
                ref = ""
            new = open(os.path.join(ROOT, eq, f)).read()
            if ref == new:
                continue
            tmp = f"/dev/shm/cv_{lang}_{os.path.basename(f)}_ref"
            open(tmp, "w").write(ref)
            d = subprocess.run(["diff", "-u", "--label", f"a/{cv}/{f}", "--label", f"b/{cv}/{f}", tmp,
                                os.path.join(ROOT, eq, f)], capture_output=True, text=True).stdout
            pdir = os.path.join(ROOT, "results", "converge", "patches_cv")
            os.makedirs(pdir, exist_ok=True)
            p = os.path.join(pdir, f"{lang}_eq__{f.replace('/', '_')}.patch")
            open(p, "w").write(d)
            target = cv if mode == "créer" else src  # à blanc : sur la source corrigée, qui a le même contenu
            d2 = d.replace(f"a/{cv}/", f"a/{target}/").replace(f"b/{cv}/", f"b/{target}/")
            r = subprocess.run(["patch", "-p1", "--no-backup-if-mismatch", "-r", "-"] + (["--dry-run"] if mode != "créer" else []),
                               input=d2, cwd=ROOT, capture_output=True, text=True)
            notes.append(f"{f} : {d.count(chr(10) + '@@ ')} morceaux, " + ("appliqué" if r.returncode == 0 else
                         "ÉCHEC\n" + r.stdout[-400:]))
        if mode == "créer" and os.path.exists(os.path.join(ROOT, eq, "eq_variants")):
            shutil.copy2(os.path.join(ROOT, eq, "eq_variants"), os.path.join(ROOT, cv, "cv_variants"))
        print(f"{lang} : " + ("; ".join(notes) if notes else "aucune variante du point 3 à reporter"), flush=True)


if __name__ == "__main__":
    main()
