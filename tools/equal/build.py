#!/usr/bin/env python3
"""v4, point 3 (docs/V4_EQUAL.md, 4) : constructions des copies et des modes, dans /dev/shm/msbuild/<langage>/<nom>.

Noms : « eq » (copie bench/<langage>_eq, mode publié), « chk » et « unc » (source publié bench/<langage>, modes R1 et
R1'), « eq_chk » et « eq_unc » (la copie dans ces modes). Le mode est passé à build.sh par MS_MODE (chk ou unc) ;
sans MS_MODE, build.sh construit le mode publié, et le binaire publié ne change pas. Julia, sans construction,
reçoit son mode par l'option de son lanceur (run).
Usage : build.py <langage> <nom>"""
import os, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BUILD_ROOT = "/dev/shm/msbuild"


def build_dir(lang, name):
    return os.path.join(BUILD_ROOT, lang, name)


def tracked(src):
    """Fichiers suivis par git du répertoire source (sources, build.sh, run), chemins relatifs."""
    out = subprocess.run(["git", "-C", ROOT, "ls-files", src], capture_output=True, text=True, check=True).stdout
    return [os.path.relpath(os.path.join(ROOT, f), os.path.join(ROOT, src)) for f in out.split()]


def build(lang, name):
    src = os.path.join("bench", lang + ("_eq" if name.startswith("eq") else ""))
    mode = {"chk": "chk", "unc": "unc", "eq_chk": "chk", "eq_unc": "unc"}.get(name)
    dst = build_dir(lang, name)
    shutil.rmtree(dst, ignore_errors=True)
    files = tracked(src)
    for f in files:
        os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, src, f), os.path.join(dst, f))
    if lang == "julia" and mode == "unc":
        run = os.path.join(dst, "run")
        text = open(run).read()
        assert text.count("julia -O3") == 1
        open(run, "w").write(text.replace("julia -O3", "julia -O3 --check-bounds=no"))
    if "build.sh" in files:
        env = dict(os.environ)
        for k in list(env):
            if k.startswith("MS_"):
                env.pop(k)
        if mode:
            env["MS_MODE"] = mode
        r = subprocess.run(["sh", os.path.join(dst, "build.sh")], env=env, capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
            raise SystemExit(f"construction {lang}/{name} : code {r.returncode}")
    return dst


if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]))
