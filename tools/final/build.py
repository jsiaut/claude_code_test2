#!/usr/bin/env python3
"""v4, campagne finale (docs/V4_FINAL.md, 5 et 6) : constructions dans /dev/shm/msbuild/<langage>/f_<construction>_<jeu>.

Constructions (docs/V4_FINAL.md, 5) : pub (bench/<langage>, mode publié), cv (bench/<langage>_cv, mode publié), chk et
unc (bench/<langage> dans les modes R1 et R1' : MS_MODE de build.sh ; Julia, sans construction, par l'option de son
lanceur, comme au point 3), cv_chk et cv_unc (la copie dans ces modes). Jeux de tailles (tools/sizes/sizes.py, SETS) :
pub, small, large. Langages compilés : paramètres MS_* du jeu passés à build.sh (sans eux, la taille publiée) ; langages
sans construction : constantes de taille substituées dans la copie (tools/sizes/patches.py : PATCHES, ou CV_PATCHES pour
les copies _cv), puis build.sh (vérification de syntaxe).

Chaque construction part des fichiers suivis par git, qui doivent être identiques à ceux du dernier commit (une source
modifiée et non commitée est refusée) ; elle garde l'empreinte de ses entrées (.source_hash) et n'est refaite que si
elles changent ou si /dev/shm a été vidé (redémarrage). Empreintes SHA-256 des fichiers exécutés (binaires ELF et, pour
eux, de leur section .text ; IL de C#, classes de Java ; source et lanceur des langages sans construction) :
results/final/work/builds.jsonl, une ligne par construction faite, avec la machine et l'identifiant de démarrage.

Usage : build.py [--jobs N] [--langs a,b] [--only pub,cv,...] [--sets pub,small,large] [--list] [--footprint]"""
import argparse, concurrent.futures as cf, hashlib, json, os, shutil, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "sizes"))
import sizes as S  # noqa: E402
import patches as P  # noqa: E402

BUILD_ROOT = "/dev/shm/msbuild"
WORK = os.path.join(ROOT, "results", "final", "work")
LANGS = ["c", "cpp", "rust", "zig", "odin", "c3", "d", "nim", "ada", "fortran", "chapel", "mojo", "swift", "fpc", "go",
         "csharp", "java", "haskell", "ocaml", "python", "lua", "php", "bqn", "js", "julia"]
CHK = ["c", "cpp", "fortran", "zig", "c3", "d", "chapel", "fpc"]          # R1 (docs/V4_EQUAL.md, 3.1)
UNC = ["swift", "ada", "nim", "odin", "julia", "mojo", "go", "ocaml", "d"]   # R1' (3.1 et écart 5.2)
CV_CHK = ["cpp", "d"]                                                     # R2 dans le mode R1
CV_UNC = ["nim", "mojo", "swift", "go", "ocaml", "d"]                     # R2 dans le mode R1'
INTERP = {"python", "lua", "php", "bqn", "js", "julia"}
SETS = ["pub", "small", "large"]
MAIN = {"python": "ms.py", "lua": "ms.lua", "php": "ms.php", "bqn": "ms.bqn", "js": "ms.js", "julia": "ms.jl"}
_lock = threading.Lock()


def constructions(lang):
    return ["pub", "cv"] + [c for c, lst in (("chk", CHK), ("unc", UNC), ("cv_chk", CV_CHK), ("cv_unc", CV_UNC))
                            if lang in lst]


def source_dir(lang, cons):
    return os.path.join("bench", lang + ("_cv" if cons.startswith("cv") else ""))


def mode_of(cons):
    return {"chk": "chk", "unc": "unc", "cv_chk": "chk", "cv_unc": "unc"}.get(cons)


def build_dir(lang, cons, sset):
    return os.path.join(BUILD_ROOT, lang, f"f_{cons}_{sset}")


def tracked(src):
    out = subprocess.run(["git", "-C", ROOT, "ls-files", src], capture_output=True, text=True, check=True).stdout.split()
    if not out:
        raise SystemExit(f"{src} : aucun fichier suivi par git")
    dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", src], capture_output=True, text=True,
                           check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{src} : fichiers modifiés et non commités, construction refusée\n{dirty}")
    return [os.path.relpath(os.path.join(ROOT, f), os.path.join(ROOT, src)) for f in out]


def boot_id():
    return open("/proc/sys/kernel/random/boot_id").read().strip()


def machine():
    p = "/dev/shm/ms_final_machine"
    return open(p).read().strip() if os.path.exists(p) else None


def input_hash(lang, cons, sset):
    src = source_dir(lang, cons)
    h = hashlib.sha256(f"{cons}|{sset}|{mode_of(cons)}\n".encode())
    for f in sorted(tracked(src)):
        h.update(f.encode() + b"\0" + open(os.path.join(ROOT, src, f), "rb").read())
    if lang in INTERP and sset != "pub":
        h.update(repr(P.CV_PATCHES[lang] if cons.startswith("cv") else P.PATCHES[lang]).encode())
    return h.hexdigest()


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def text_sha(path):
    with tempfile.NamedTemporaryFile(dir="/dev/shm") as t:
        r = subprocess.run(["objcopy", "-O", "binary", "--only-section=.text", path, t.name], capture_output=True)
        return sha(t.name) if r.returncode == 0 else None


def executed_files(lang, dst, srcfiles):
    """Fichiers exécutés d'une construction : {chemin relatif : [sha256, sha256 de .text ou None]}."""
    out = {}
    if lang in INTERP:
        for f in (MAIN[lang], "run"):
            out[f] = [sha(os.path.join(dst, f)), None]
        return out
    for root, dirs, files in os.walk(dst):
        dirs[:] = [d for d in dirs if d not in ("obj", "nimcache", ".zig-cache", "zig-cache", "_build", ".build")]
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, dst)
            if rel in srcfiles or os.path.islink(p):
                continue
            with open(p, "rb") as fh:
                head = fh.read(4)
            if head == b"\x7fELF" and os.access(p, os.X_OK) and not f.endswith(".so"):
                out[rel] = [sha(p), text_sha(p)]
            elif (lang == "csharp" and f.endswith(".dll") and "/obj/" not in "/" + rel) or \
                    (lang == "java" and f.endswith(".class")):
                out[rel] = [sha(p), None]
    if not out:
        raise SystemExit(f"{lang} {dst} : aucun fichier exécuté trouvé")
    return out


def build(lang, cons, sset):
    src = source_dir(lang, cons)
    files = tracked(src)
    dst = build_dir(lang, cons, sset)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for f in files:
        os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, src, f), os.path.join(dst, f))
    mode = mode_of(cons)
    if lang in INTERP:
        if sset != "pub":
            main = os.path.join(dst, MAIN[lang])
            text = open(main, encoding="utf-8").read()
            fn = P.apply_cv if cons.startswith("cv") else P.apply
            open(main, "w", encoding="utf-8").write(fn(lang, text, S.set_params(sset)))
        if mode:
            if lang != "julia" or mode != "unc":
                raise SystemExit(f"{lang} : pas de mode {mode}")
            run = os.path.join(dst, "run")
            text = open(run).read()
            if text.count("julia -O3") != 1:
                raise SystemExit("julia : lanceur inattendu")
            open(run, "w").write(text.replace("julia -O3", "julia -O3 --check-bounds=no"))
    env = {k: v for k, v in os.environ.items() if not k.startswith("MS_")}
    if mode and lang not in INTERP:
        env["MS_MODE"] = mode
    if sset != "pub" and lang not in INTERP:
        env.update({k: str(v) for k, v in S.set_params(sset).items()})
        env["MS_SIZE_SET"] = sset
        env["MS_DATA_DIR"] = os.path.join(S.SHM, f"ms_view_{sset}") + "/"  # Mojo : répertoire des données compilé
    t0 = time.time()
    r = subprocess.run(["sh", os.path.join(dst, "build.sh")], cwd=dst, env=env, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"construction {lang}/{cons}/{sset} : code {r.returncode}\n{r.stdout[-3000:]}{r.stderr[-3000:]}")
    exe = executed_files(lang, dst, set(files))
    rec = {"lang": lang, "construction": cons, "set": sset, "mode": mode, "files": exe, "seconds": round(time.time() - t0, 1),
           "machine": machine(), "boot_id": boot_id(), "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    open(os.path.join(dst, ".source_hash"), "w").write(input_hash(lang, cons, sset))
    with _lock:
        os.makedirs(WORK, exist_ok=True)
        with open(os.path.join(WORK, "builds.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
    return rec


def ensure(lang, cons, sset):
    dst = build_dir(lang, cons, sset)
    p = os.path.join(dst, ".source_hash")
    if os.path.exists(p) and open(p).read() == input_hash(lang, cons, sset):
        return dst
    build(lang, cons, sset)
    return dst


def all_builds(langs, only=None, sets=SETS):
    return [(l, c, s) for l in langs for c in constructions(l) if only is None or c in only for s in sets]


def footprint():
    r = subprocess.run(["du", "-sb", BUILD_ROOT], capture_output=True, text=True)
    return int(r.stdout.split()[0]) if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--langs", default=",".join(LANGS))
    ap.add_argument("--only", default="")
    ap.add_argument("--sets", default=",".join(SETS))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--footprint", action="store_true")
    a = ap.parse_args()
    langs = a.langs.split(",")
    todo = all_builds(langs, set(a.only.split(",")) if a.only else None, a.sets.split(","))
    if a.list:
        for t in todo:
            print(*t)
        print(len(todo), "constructions")
        return
    for s in a.sets.split(","):
        if s != "pub":
            S.view_dir(s)  # liens de données des jeux (Mojo), créés avant les constructions parallèles
    by_lang = {}
    for t in todo:
        by_lang.setdefault(t[0], []).append(t)

    def one_lang(lst):  # les constructions d'un langage en série (caches de zig, dotnet, swift) ; langages en parallèle
        done = []
        for l, c, s in lst:
            ensure(l, c, s)
            done.append(f"{l}/{c}/{s}")
        return done

    t0 = time.time()
    errors = []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(one_lang, lst): l for l, lst in by_lang.items()}
        for fu in cf.as_completed(futs):
            try:
                print(f"{futs[fu]} : {len(fu.result())} constructions prêtes ({time.time() - t0:.0f} s)", flush=True)
            except SystemExit as e:
                errors.append(str(e))
                print(f"{futs[fu]} : ÉCHEC\n{e}", flush=True)
    if a.footprint:
        print(f"empreinte de {BUILD_ROOT} : {footprint()} octets")
    if errors:
        raise SystemExit(f"{len(errors)} langage(s) en échec")


if __name__ == "__main__":
    main()
