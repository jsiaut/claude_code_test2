#!/usr/bin/env python3
"""v4, point 4 (docs/V4_CONVERGE.md, 5 et 4.1) : constructions dans /dev/shm/msbuild/<langage>/<nom>.
Noms : « pub » (source publiée corrigée bench/<langage>), « cv » (copie bench/<langage>_cv), « old » (source publiée au
commit ea2da12, sans les corrections : le code mesuré par les points 2 et 3, pour le contrôle de l'erratum). Chaque
construction part des fichiers suivis par git (git archive pour « old ») et garde l'empreinte de ses sources
(.source_hash), pour n'être refaite que si elles changent.
Usage : build.py <langage> <nom>"""
import hashlib, io, os, shutil, subprocess, sys, tarfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BUILD_ROOT = "/dev/shm/msbuild"
OLD_COMMIT = "ea2da12"


def build_dir(lang, name):
    return os.path.join(BUILD_ROOT, lang, name)


def files_of(lang, name):
    """{chemin relatif: contenu} des sources de la construction."""
    if name == "old":
        tar = subprocess.run(["git", "-C", ROOT, "archive", OLD_COMMIT, f"bench/{lang}"], capture_output=True,
                             check=True).stdout
        out = {}
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            for m in t.getmembers():
                if m.isfile():
                    out[os.path.relpath(m.name, f"bench/{lang}")] = t.extractfile(m).read()
        return out
    src = os.path.join("bench", lang + ("_cv" if name == "cv" else ""))
    ls = subprocess.run(["git", "-C", ROOT, "ls-files", src], capture_output=True, text=True, check=True).stdout.split()
    if name == "cv":  # copie pas encore suivie : ses fichiers sur disque
        d = os.path.join(ROOT, src)
        ls = ls or [os.path.join(src, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
    return {os.path.relpath(os.path.join(ROOT, f), os.path.join(ROOT, src)): open(os.path.join(ROOT, f), "rb").read()
            for f in ls if os.path.basename(f) not in ("ms", "ms_nat", "ms_tuned", "ms_fm")}


def source_hash(lang, name):
    h = hashlib.sha256()
    for f, data in sorted(files_of(lang, name).items()):
        h.update(f.encode()); h.update(data)
    return h.hexdigest()


def build(lang, name):
    dst = build_dir(lang, name)
    shutil.rmtree(dst, ignore_errors=True)
    files = files_of(lang, name)
    for f, data in files.items():
        os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
        open(os.path.join(dst, f), "wb").write(data)
        if f in ("build.sh", "run"):
            os.chmod(os.path.join(dst, f), 0o755)
    if "build.sh" in files:
        env = {k: v for k, v in os.environ.items() if not k.startswith("MS_")}
        r = subprocess.run(["sh", "build.sh"], cwd=dst, env=env, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"{lang} {name} : construction en échec\n{r.stdout[-3000:]}{r.stderr[-3000:]}")
    open(os.path.join(dst, ".source_hash"), "w").write(source_hash(lang, name))
    return dst


def ensure(lang, name):
    dst = build_dir(lang, name)
    p = os.path.join(dst, ".source_hash")
    if os.path.exists(p) and open(p).read() == source_hash(lang, name):
        return dst
    return build(lang, name)


if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]))
