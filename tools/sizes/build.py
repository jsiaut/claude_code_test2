#!/usr/bin/env python3
"""v4, point 2 : constructions des tailles non publiées (docs/V4_SIZES.md).

Usage : build.py <langage> [<jeu>...] (jeux : small, large ; tools/sizes/sizes.py, SETS).
Copie bench/<langage> (sources, build.sh, run) dans /dev/shm/msbuild/<langage>/<jeu>, puis :
* langages compilés : lance build.sh avec les paramètres de taille du jeu dans l'environnement (MS_N1=…) ; chaque
  build.sh les passe au compilateur (redéfinition de constantes, fichier de constantes généré, option de
  configuration), et sans eux construit la taille publiée ;
* langages interprétés ou à JIT sans construction (INTERP) : remplace dans la copie les constantes de taille du source
  publié par celles du jeu (tools/sizes/patches.py) ; le source publié ne change pas."""
import os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sizes as S  # noqa: E402

BUILD_ROOT = "/dev/shm/msbuild"
INTERP = {"python", "lua", "php", "bqn", "js", "julia"}
SKIP = {"obj", "bin", "classes", "target", "zig-out", ".zig-cache", "zig-cache", "build", "out", "__pycache__", "layout",
        "nimcache", "dist-newstyle", ".build", "_build"}


def build_dir(lang, name):
    return os.path.join(BUILD_ROOT, lang, name)


def source_hash(lang):
    """Empreinte des sources de bench/<langage> (fichiers copiés par build), pour refaire une construction périmée."""
    import hashlib
    h = hashlib.sha256()
    src = os.path.join(S.ROOT, "bench", lang)
    for f in sorted(os.listdir(src)):
        p = os.path.join(src, f)
        if f in SKIP or not os.path.isfile(p) or (os.access(p, os.X_OK) and f not in ("build.sh", "run") and "." not in f):
            continue
        h.update(f.encode() + b"\0" + open(p, "rb").read())
    return h.hexdigest()


def ensure_build(lang, name):
    """Construction du jeu name, refaite si les sources ont changé depuis (empreinte dans .source_hash)."""
    d = build_dir(lang, name)
    stamp = os.path.join(d, ".source_hash")
    if not (os.path.exists(stamp) and open(stamp).read() == source_hash(lang)):
        build(lang, name)
        open(stamp, "w").write(source_hash(lang))
    return d


def build(lang, name):
    src = os.path.join(S.ROOT, "bench", lang)
    dst = build_dir(lang, name)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for f in os.listdir(src):
        p = os.path.join(src, f)
        if f in SKIP or (os.path.isfile(p) and os.access(p, os.X_OK) and f not in ("build.sh", "run") and "." not in f):
            continue  # binaires et répertoires de construction : refaits
        (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, os.path.join(dst, f))
    if lang in INTERP:
        import patches
        main = os.path.join(dst, patches.PATCHES[lang][0])
        text = open(main, encoding="utf-8").read()
        open(main, "w", encoding="utf-8").write(patches.apply(lang, text, S.set_params(name)))
        return dst
    env = dict(os.environ)
    env.update({k: str(v) for k, v in S.set_params(name).items()})
    env["MS_SIZE_SET"] = name
    env["MS_DATA_DIR"] = S.view_dir(name)  # langages qui fixent le répertoire des données à la compilation (Mojo)
    r = subprocess.run(["sh", os.path.join(dst, "build.sh")], env=env, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
        raise SystemExit(f"construction {lang}/{name} : code {r.returncode}")
    return dst


if __name__ == "__main__":
    lang = sys.argv[1]
    for name in (sys.argv[2:] or list(S.SETS)):
        print(build(lang, name))
