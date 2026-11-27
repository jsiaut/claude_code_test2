#!/usr/bin/env python3
"""Constructions de la campagne (docs/METHOD.md, 6) dans /dev/shm/msbuild/<langage>/f_<construction>_<jeu>.

Une source par langage (bench/<langage>), construite dans chaque mode : pub (mode publié), chk et unc (modes R1 et R1' :
MS_MODE de build.sh ; Julia, sans construction, par l'option de son lanceur), et pour C, gcc et gcc_chk (la même source
par gcc 16 : MS_CC de build.sh). Sous MS_DEV=1 seulement, pour Zig, dev et dev_chk (la même source par sa version de
développement : MS_ZIG de build.sh ; docs/V5_2.md, 3). Sous MS_GOFIX=1 seulement, pour Go, wit et wit_unc : le témoin de
sa remesure (docs/V5_4.md, 3.2), construit à partir de la source de la campagne (WITNESS : un commit), prise dans
l'historique de git et non dans l'arbre de travail. Sans ces variables, le plan est celui de la campagne publiée.
Jeux de tailles (tools/sizes/sizes.py, SETS) : pub, small, large. Langages compilés :
paramètres MS_* du jeu passés à build.sh (sans eux, la taille publiée) ; langages sans construction : constantes de
taille substituées dans la copie de la construction (tools/sizes/patches.py), puis build.sh (vérification de syntaxe).

Les enregistrements de la campagne portent une étiquette qui dit d'où vient la cellule (CELLS : pub, cv, chk, unc,
cv_chk, cv_unc, gcc, gcc_cv, gcc_chk, dev, dev_cv, dev_chk, wit, wit_cv, wit_unc, wit_cv_unc) ; plusieurs étiquettes
partagent une construction (BUILD_OF).

Chaque construction part des fichiers suivis par git, qui doivent être identiques à ceux du dernier commit (une source
modifiée et non commitée est refusée) ; elle garde l'empreinte de ses entrées (.source_hash) et n'est refaite que si
elles changent ou si /dev/shm a été vidé (redémarrage). Empreintes SHA-256 des fichiers exécutés (binaires ELF et, pour
eux, de leur section .text ; IL de C#, classes de Java ; source et lanceur des langages sans construction) :
builds.jsonl du répertoire de travail de la campagne, une ligne par construction faite, avec la machine et
l'identifiant de démarrage.

Répertoire de la campagne : results/final, ou celui de la variable MS_CAMPAIGN_DIR (une campagne en cours s'écrit à
part de celle qui est publiée).

Usage : build.py [--jobs N] [--langs a,b] [--only pub,chk,...] [--sets pub,small,large] [--list] [--footprint]"""
import argparse, concurrent.futures as cf, hashlib, json, os, shutil, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "sizes"))
import sizes as S  # noqa: E402
import patches as P  # noqa: E402

BUILD_ROOT = "/dev/shm/msbuild"
CAMPAIGN = os.path.join(ROOT, os.environ.get("MS_CAMPAIGN_DIR", os.path.join("results", "final")))
WORK = os.path.join(CAMPAIGN, "work")
LANGS = ["c", "cpp", "rust", "zig", "odin", "c3", "d", "nim", "ada", "fortran", "chapel", "mojo", "swift", "fpc", "go",
         "csharp", "java", "haskell", "ocaml", "julia"]
CHK = ["c", "cpp", "fortran", "zig", "c3", "d", "chapel", "fpc"]          # R1 (docs/METHOD.md, 5)
UNC = ["swift", "ada", "nim", "odin", "julia", "mojo", "go", "ocaml", "d"]   # R1' (3.1 et écart 5.2)
CV_CHK = ["cpp", "d"]                                                     # R2 dans le mode R1
CV_UNC = ["nim", "mojo", "swift", "go", "ocaml", "d"]                     # R2 dans le mode R1'
GCC = ["c"]                                                               # C aussi par gcc (docs/V5.md, S2)
DEV = ["zig"] if os.environ.get("MS_DEV") else []                         # version de développement (docs/V5_2.md, 3)
GOFIX = ["go"] if os.environ.get("MS_GOFIX") else []                      # témoin de la remesure de Go (docs/V5_4.md)
WITNESS = {"go": "861d62564995b71cff4e65e5e836a899edcd527c"}              # source du témoin : celle de la campagne
BUILD_OF = {"cv": "pub", "cv_chk": "chk", "cv_unc": "unc", "gcc_cv": "gcc", "dev_cv": "dev", "wit_cv": "wit",
            "wit_cv_unc": "wit_unc"}  # étiquette -> construction
INTERP = {"julia"}  # sans construction : le source est exécuté tel quel
SETS = ["pub", "small", "large"]
MAIN = {"julia": "ms.jl"}
_lock = threading.Lock()


def constructions(lang):
    """Étiquettes des cellules d'un langage (une par origine de cellule : tools/final/campaign.py, cells)."""
    return ["pub", "cv"] + [c for c, lst in (("chk", CHK), ("unc", UNC), ("cv_chk", CV_CHK), ("cv_unc", CV_UNC),
                                             ("gcc", GCC), ("gcc_cv", GCC), ("gcc_chk", GCC),
                                             ("dev", DEV), ("dev_cv", DEV), ("dev_chk", DEV),
                                             ("wit", GOFIX), ("wit_cv", GOFIX), ("wit_unc", GOFIX),
                                             ("wit_cv_unc", GOFIX)) if lang in lst]


def builds(lang):
    """Constructions distinctes d'un langage."""
    out = []
    for c in constructions(lang):
        b = BUILD_OF.get(c, c)
        if b not in out:
            out.append(b)
    return out


def source_dir(lang):
    return os.path.join("bench", lang)


def mode_of(cons):
    return {"chk": "chk", "unc": "unc", "gcc_chk": "chk", "dev_chk": "chk",
            "wit_unc": "unc"}.get(BUILD_OF.get(cons, cons))


def witness(lang, cons):
    """Commit dont vient la source d'une construction du témoin (wit, wit_unc) ; None pour les autres."""
    return WITNESS[lang] if BUILD_OF.get(cons, cons).startswith("wit") else None


def witness_files(lang, commit):
    out = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", commit, "--", source_dir(lang)],
                         capture_output=True, text=True, check=True).stdout.split()
    if not out:
        raise SystemExit(f"{source_dir(lang)} : absent du commit {commit}")
    return [os.path.relpath(f, source_dir(lang)) for f in out]


def build_dir(lang, cons, sset):
    return os.path.join(BUILD_ROOT, lang, f"f_{BUILD_OF.get(cons, cons)}_{sset}")


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
    src = source_dir(lang)
    cons = BUILD_OF.get(cons, cons)
    h = hashlib.sha256(f"{cons}|{sset}|{mode_of(cons)}\n".encode())
    if witness(lang, cons):  # la source du témoin est fixée par son commit
        h.update(witness(lang, cons).encode())
        return h.hexdigest()
    for f in sorted(tracked(src)):
        h.update(f.encode() + b"\0" + open(os.path.join(ROOT, src, f), "rb").read())
    if lang in INTERP and sset != "pub":
        h.update(repr(P.PATCHES[lang]).encode())
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
            if (rel in srcfiles and not f.endswith(".class")) or os.path.islink(p):
                continue  # les .class publiés de Java sont suivis par git, et réécrits par javac
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
    src = source_dir(lang)
    dst = build_dir(lang, cons, sset)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    commit = witness(lang, cons)
    if commit:  # témoin : les fichiers du commit, avec leurs droits (git archive), et non ceux de l'arbre de travail
        files = witness_files(lang, commit)
        with tempfile.TemporaryDirectory(dir="/dev/shm") as t:
            ar = subprocess.run(["git", "-C", ROOT, "archive", commit, "--", src], capture_output=True, check=True)
            subprocess.run(["tar", "-x", "-C", t], input=ar.stdout, check=True)
            for f in files:
                os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
                shutil.copy2(os.path.join(t, src, f), os.path.join(dst, f))
    else:
        files = tracked(src)
        for f in files:
            os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, src, f), os.path.join(dst, f))
    mode = mode_of(cons)
    if lang in INTERP:
        if sset != "pub":
            main = os.path.join(dst, MAIN[lang])
            text = open(main, encoding="utf-8").read()
            open(main, "w", encoding="utf-8").write(P.apply(lang, text, S.set_params(sset)))
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
    if cons.startswith("gcc"):
        env["MS_CC"] = "gcc"
    if cons.startswith("dev"):
        env["MS_ZIG"] = "dev"
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
    return [(l, c, s) for l in langs for c in builds(l) if only is None or c in only for s in sets]


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
