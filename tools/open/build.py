#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 5.2 et 6) : constructions de la campagne de la piste ouverte, dans
/dev/shm/msbuild/<langage>/<nom>, par l'outil du point 4 (tools/converge/build.py) : « pub » (bench/<langage>),
« cv » (bench/<langage>_cv) et, en plus, « op » (bench/<langage>_op : formes op_* et bibliothèques liées). Chaque
construction part des fichiers suivis par git et garde l'empreinte de ses sources.
Usage : build.py <langage> <nom>"""
import importlib.util, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("cvbuild", os.path.join(ROOT, "tools", "converge", "build.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)
_files_of = B.files_of


def files_of(lang, name):
    if name != "op":
        return _files_of(lang, name)
    src = os.path.join("bench", lang + "_op")
    ls = subprocess.run(["git", "-C", ROOT, "ls-files", src], capture_output=True, text=True, check=True).stdout.split()
    return {os.path.relpath(os.path.join(ROOT, f), os.path.join(ROOT, src)): open(os.path.join(ROOT, f), "rb").read()
            for f in ls if os.path.basename(f) != "ms"}


B.files_of = files_of
build_dir, ensure, build = B.build_dir, B.ensure, B.build

if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]))
