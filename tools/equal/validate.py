#!/usr/bin/env python3
"""v4, point 3 (docs/V4_EQUAL.md, 4) : contrôles avant la campagne.

1. Binaires des modes (results/equal/builds.txt) : le source publié de chaque langage à mode (R1 ou R1') est construit
   dans un même répertoire sans MS_MODE puis avec, et les binaires sont comparés octet pour octet ; un mode qui donne
   le binaire publié n'aurait pas à être mesuré. Julia, sans construction, reçoit son mode par l'option de son lanceur.
2. Validation (results/equal/validation.txt) : toutes les constructions de la campagne (campaign.builds_of), puis
   chaque nouvelle cellule (toute construction autre que pub) exécutée une fois (une répétition après l'échauffement)
   à la taille publiée ; sa somme de contrôle doit être celle de la taille publiée (tools/driver.py, celle du C).

Usage : validate.py [modes|cells|all] [langage,...] [construction,...]"""
import os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402
import campaign as C  # noqa: E402

OUT_BUILDS = os.path.join(C.ROOT, "results", "equal", "builds.txt")
OUT_VALID = os.path.join(C.ROOT, "results", "equal", "validation.txt")
BINARIES = {"chapel": ["ms_nat", "ms_tuned", "ms_fm"]}


def mode_builds(langs):
    lines = [f"# Binaires des modes (tools/equal/validate.py modes), {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())},"
             f" {C.cpu_model()}",
             "# langage mode : fichier, octets différents du binaire publié construit dans le même répertoire"]
    work = "/dev/shm/modecmp"
    for lang in langs:
        modes = [m for m, lst in (("chk", C.CHK), ("unc", C.UNC)) if lang in lst]
        if not modes or lang == "julia":
            continue
        d = os.path.join(work, lang)
        hashes = {}
        for m in [""] + modes:
            shutil.rmtree(d, ignore_errors=True)
            for f in B.tracked(os.path.join("bench", lang)):
                os.makedirs(os.path.dirname(os.path.join(d, f)), exist_ok=True)
                shutil.copy2(os.path.join(C.ROOT, "bench", lang, f), os.path.join(d, f))
            env = {k: v for k, v in os.environ.items() if not k.startswith("MS_")}
            if m:
                env["MS_MODE"] = m
            r = subprocess.run(["sh", os.path.join(d, "build.sh")], env=env, capture_output=True, text=True)
            if r.returncode:
                raise SystemExit(f"{lang} {m or 'publié'} : code {r.returncode}\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
            for b in BINARIES.get(lang, ["ms"]):
                shutil.copy2(os.path.join(d, b), os.path.join(work, f"{lang}.{m or 'pub'}.{b}"))
        for m in modes:
            for b in BINARIES.get(lang, ["ms"]):
                a, z = os.path.join(work, f"{lang}.pub.{b}"), os.path.join(work, f"{lang}.{m}.{b}")
                n = len(subprocess.run(["cmp", "-l", a, z], capture_output=True, text=True).stdout.splitlines())
                lines.append(f"{lang} {m} : {b}, {n} octets différents" + (" (binaire publié)" if n == 0 else ""))
        print(lines[-1], flush=True)
    open(OUT_BUILDS, "w").write("\n".join(lines) + "\n")


def cells(langs, only_builds=None):
    """Valide les nouvelles cellules des langages donnés (constructions only_builds seulement, si donné). Pour une
    partie des langages, le résultat se fusionne avec le fichier existant : ses lignes des autres langages, ou des
    autres constructions, sont gardées, et la nouvelle exécution est datée dans l'en-tête."""
    t0 = time.time()
    for lang in langs:
        for b in C.builds_of(lang):
            B.ensure(lang, b)
        print(f"constructions {lang} : {' '.join(C.builds_of(lang))}", flush=True)
    lines = [f"# Validation des nouvelles cellules (tools/equal/validate.py cells), "
             f"{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}, {C.cpu_model()}",
             f"# constructions faites en {time.time() - t0:.0f} s ; une répétition après l'échauffement",
             "# langage construction noyau variante paramètre : temps (s), somme de contrôle, verdict"]
    bad = 0
    n = 0
    for lang in langs:
        for b in C.builds_of(lang):
            if b == "pub" or (only_builds and b not in only_builds):
                continue
            for k in C.KERNELS:
                for v, q in C.cells(lang, b, k):
                    rec = C.run_one(lang, b, k, v, q, 1, 3 if lang in C.JIT else 1, 3600)
                    ok = rec.get("oks") == ["True"] and rec["returncode"] == 0
                    bad += not ok
                    n += 1
                    t = f"{rec['median']:.4g}" if "median" in rec else "-"
                    line = (f"{lang} {b} {k} {v} {q or '-'} : {t} {','.join(rec.get('chks', [])) or '-'} "
                            f"{'juste' if ok else 'FAUX (code ' + str(rec['returncode']) + ') ' + rec['stderr'][-200:]}")
                    lines.append(line)
                    print(line, flush=True)
    partial = set(langs) != set(C.LANGS) or only_builds
    if partial and os.path.exists(OUT_VALID):
        new_keys = {tuple(l.split()[:5]) for l in lines if not l.startswith("#")}
        old = [l for l in open(OUT_VALID).read().splitlines() if l and not l.startswith("# ")
               and tuple(l.split()[:5]) not in new_keys]
        head = [l for l in open(OUT_VALID).read().splitlines() if l.startswith("# ") and " cellules, " not in l]
        body = old + [l for l in lines if not l.startswith("#")]
        head.append(f"# complément ({','.join(langs)}"
                    + (f" ; {','.join(only_builds)}" if only_builds else "") + f") : {lines[0][2:]}")
        lines = head + body
    body = [l for l in lines if not l.startswith("#")]
    bad = sum(not l.endswith(" juste") for l in body)
    lines.append(f"# {len(body)} cellules, {len(body) - bad} justes, {bad} fausses")
    open(OUT_VALID, "w").write("\n".join(lines) + "\n")
    return bad


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    langs = sys.argv[2].split(",") if len(sys.argv) > 2 else C.LANGS
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    if what in ("modes", "all"):
        mode_builds(langs)
    if what in ("cells", "all"):
        sys.exit(1 if cells(langs, only) else 0)
