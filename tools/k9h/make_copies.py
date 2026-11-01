#!/usr/bin/env python3
"""Harnais commun de K9 (docs/K9.md, plan) : copies bench/<implémentation>_k9h dont seule la fonction qui fait tourner
K9 change (grilles allouées une fois par processus, réinitialisées hors chrono ; code chronométré inchangé). La fonction
d'origine est remplacée en entier par tools/k9h/new/<nom>.txt (repères : tools/k9h/spec.py). Les annexes qui compilent
ou lancent la source d'un autre répertoire pointent vers la copie de ce répertoire. Puis chaque copie est compilée.
Usage : make_copies.py [--no-build]"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spec import FUNCS  # noqa: E402

B = os.path.join(ROOT, "bench")
SKIP = {"ms", "bin", "obj", "nimcache", "classes", ".zig-cache", "zig-cache"}  # produits de compilation, refaits
# copie -> (répertoire d'origine, fonction remplacée (clé de FUNCS) ou None, remplacements dans build.sh / run)
COPIES = {
    "cpp_k9h": ("cpp", "cpp", []),
    "csharp_k9h": ("csharp", "csharp", []),
    "csharp_exp_k9h": ("csharp_exp", "csharp_exp", []),
    "java_k9h": ("java", "java", []),
    "zig_k9h": ("zig", "zig", []),
    "zig_master_k9h": ("zig_master", None, [("build.sh", "../zig/ms.zig", "../zig_k9h/ms.zig")]),
    "odin_k9h": ("odin", "odin", []),
    "julia_k9h": ("julia", "julia", []),
    "js_k9h": ("js", "js", []),
    "js_bun_k9h": ("js_bun", None, [("run", "../js/ms.js", "../js_k9h/ms.js")]),
    "python_k9h": ("python", "python", []),
    "python_ft_k9h": ("python_ft", None, [("run", "../python/ms.py", "../python_k9h/ms.py"),
                                          ("build.sh", "../python/ms.py", "../python_k9h/ms.py")]),
    "haskell_k9h": ("haskell", "haskell", []),
    "c3_k9h": ("c3", "c3", []),
    "d_k9h": ("d", "d", []),
    "rust_k9h": ("rust", "rust", []),
    "rust_nat_k9h": ("rust_nat", "rust_nat", []),
    "nim_k9h": ("nim", "nim", []),
    "nim_nat_k9h": ("nim_nat", "nim_nat", []),
    "mojo_k9h": ("mojo", "mojo", []),
    "go_k9h": ("go", "go", []),
    "ocaml_k9h": ("ocaml", "ocaml", []),
    "lua_k9h": ("lua", "lua", []),
    "luajit_k9h": ("luajit", "luajit", []),
    "fortran_fix_k9h": ("fortran_fix", "fortran_fix", []),
    # flang : la source d'origine de bench/fortran (l'annexe n'a pas la correction NOINLINE), copiée ici
    "fortran_flang_k9h": ("fortran_flang", "fortran", [("build.sh", "S=../fortran", "S=.")]),
}


def patch_function(path, key):
    src, a, b = FUNCS[key]
    s = open(path, encoding="utf-8").read()
    assert s.count(a) == 1, (path, a)
    i = s.index(a)
    j = s.index(b, i)
    new = open(os.path.join(ROOT, "tools", "k9h", "new", f"{key}.txt"), encoding="utf-8").read()
    if new.endswith("\n") and not s[i:j].endswith("\n"):
        new = new[:-1]
    open(path, "w", encoding="utf-8").write(s[:i] + new + s[j:])


def main():
    for dst, (src, key, reps) in COPIES.items():
        d = os.path.join(B, dst)
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(os.path.join(B, src), d, ignore=lambda _dir, names: [n for n in names if n in SKIP])
        if dst == "fortran_flang_k9h":  # sources de bench/fortran copiées à côté du script de compilation
            for f in ("ms.f90", "tuned.f90"):
                shutil.copy(os.path.join(B, "fortran", f), os.path.join(d, f))
        if key:
            patch_function(os.path.join(d, FUNCS[key][0].split("/", 1)[1]), key)
        for fname, o, n in reps:
            p = os.path.join(d, fname)
            s = open(p, encoding="utf-8").read()
            assert s.count(o) >= 1, (dst, fname, o)
            open(p, "w", encoding="utf-8").write(s.replace(o, n))
        print(f"{dst} <- {src}" + (f" (fonction {key})" if key else ""), flush=True)
    if "--no-build" in sys.argv:
        return
    # ordre : les sources partagées avant les annexes qui les compilent
    for dst in COPIES:
        bs = os.path.join(B, dst, "build.sh")
        r = subprocess.run(["bash", bs], capture_output=True, text=True, timeout=3600)
        print(f"build {dst}: {r.returncode}" + ("" if r.returncode == 0 else "\n" + (r.stdout + r.stderr)[-3000:]),
              flush=True)


if __name__ == "__main__":
    main()
