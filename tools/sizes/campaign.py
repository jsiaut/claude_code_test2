#!/usr/bin/env python3
"""v4, point 2 : campagne des trois tailles (docs/V4_SIZES.md, sections 6 et 7, écart 4.1).

Trois passes. Dans chaque passe, l'ordre des groupes (noyau, taille) est tiré au hasard (graine 20261119 + passe),
puis celui des blocs (langage, construction) dans chaque groupe ; un bloc exécute un processus par variante. Les
données d'une taille non publiée sont produites au début de leur groupe et effacées à la fin (/dev/shm).
* Répétitions fixées par une exécution de calibration avant le premier processus de la cellule (une répétition) :
  environ 3 s par processus, au moins 3 et au plus 10 000 ; une seule si une répétition dépasse 300 s.
* Échauffement : 1 répétition ; langages à JIT (ceux de la campagne de référence : Java, C#, JavaScript, Julia) au
  moins 3 répétitions et au moins une seconde.
* Un processus qui dépasse 13 Gio de mémoire résidente (groupe de processus) est tué : cellule « hors mémoire ».
* Vol de temps de la machine virtuelle supérieur à 5 % du temps disponible : processus refait une fois.
* Contrôle de l'écart 4.1 : Odin, Chapel et Go sont aussi mesurés à la taille publiée avec leurs anciens binaires
  (source publié, commit OLD_COMMIT), construits dans /dev/shm/msbuild/<langage>/old.
Sortie : results/sizes/raw/<langage>.jsonl (une ligne par processus), results/sizes/calib.json,
results/sizes/campaign.log. Reprise : un processus déjà enregistré (passe, langage, construction, noyau, taille,
variante, paramètre) n'est pas refait.

Usage : campaign.py [--passes 0,1,2] [--langs c,rust,...] [--groups k1:small,k2:pub,...] [--dry]"""
import argparse, json, math, os, random, signal, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sizes as S  # noqa: E402
import build as B  # noqa: E402
from validate import extra_variants  # noqa: E402

ROOT = S.ROOT
sys.path.insert(0, os.path.join(ROOT, "tools"))
import driver as D  # noqa: E402  (PLAN des noyaux, sommes de contrôle de la taille publiée, vol de temps)

LANGS = ["c", "cpp", "rust", "zig", "odin", "c3", "d", "nim", "ada", "fortran", "chapel", "mojo", "swift", "fpc", "go",
         "csharp", "java", "haskell", "ocaml", "python", "lua", "php", "bqn", "js", "julia"]
CONTROL = ["odin", "chapel", "go"]   # écart 4.1 : instructions identiques, disposées autrement
OLD_COMMIT = "f0168b7"               # dernier commit avant le changement du code (sources publiées)
JIT = {"java", "csharp", "js", "julia"}
SIZED = ["k1", "k4", "k5", "k6", "k7", "k8", "k9"]
SINGLE = ["k2", "k3", "k10"]
MEM_CAP_KB = 13 * 1024 * 1024
EXP_SIZES = json.load(open(os.path.join(ROOT, "results", "sizes", "expected.json")))
RAW = os.path.join(ROOT, "results", "sizes", "raw")
CALIB = os.path.join(ROOT, "results", "sizes", "calib.json")
LOG = os.path.join(ROOT, "results", "sizes", "campaign.log")


def log(msg):
    line = time.strftime("%Y-%m-%dT%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def cpu_model():
    """Modèle de l'hôte (famille, modèle, pas, nom) : la section 5 exige le même modèle pendant toute la campagne."""
    info = {}
    for line in open("/proc/cpuinfo"):
        if ":" in line:
            k, v = (x.strip() for x in line.split(":", 1))
            info.setdefault(k, v)
        if not line.strip() and info:
            break
    return f"{info.get('cpu family')}/{info.get('model')}/{info.get('stepping')} {info.get('model name')}"


def old_build(lang):
    """Ancien binaire (source publié, OLD_COMMIT) dans /dev/shm/msbuild/<langage>/old."""
    d = B.build_dir(lang, "old")
    stamp = os.path.join(d, ".commit")
    if os.path.exists(stamp) and open(stamp).read() == OLD_COMMIT:
        return d
    subprocess.run(["rm", "-rf", d], check=True)
    os.makedirs(d)
    tar = subprocess.run(["git", "-C", ROOT, "archive", OLD_COMMIT, f"bench/{lang}"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "--strip-components=2", "-C", d], input=tar, check=True)
    r = subprocess.run(["sh", os.path.join(d, "build.sh")], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"ancien binaire {lang} : {r.stderr[-2000:]}")
    open(stamp, "w").write(OLD_COMMIT)
    return d


def runner_dir(lang, build, kernel, size):
    if build == "old":
        return old_build(lang)
    name = S.set_of(kernel, size) if kernel in SIZED else None
    return os.path.join(ROOT, "bench", lang) if name is None else B.ensure_build(lang, name)


def check(kernel, size, param, chk):
    if kernel not in SIZED or size == "pub":
        return D.check(kernel, param, chk)
    exp = EXP_SIZES.get(f"{kernel}:{size}" + (f":{param}" if kernel == "k6" else ""))
    if exp is None:
        return None
    if kernel in D.TOL:
        try:
            return abs(float(chk) - float(exp)) <= D.TOL[kernel] * abs(float(exp))
        except ValueError:
            return False
    return chk.strip() == exp


def oom_victim():
    """Dans le processus mesuré, avant exec : premier tué en cas de manque de mémoire du groupe de processus (la limite
    du groupe, page cache et /dev/shm compris, est atteinte avant 13 Gio : section 6, « que le noyau tue »)."""
    with open("/proc/self/oom_score_adj", "w") as f:
        f.write("1000")


def tree_rss_kb(pgid):
    total = 0
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            if os.getpgid(int(p)) != pgid:
                continue
            for line in open(f"/proc/{p}/status"):
                if line.startswith("VmRSS:"):
                    total += int(line.split()[1])
        except (OSError, ProcessLookupError):
            pass
    return total


def run_one(lang, build, kernel, size, variant, param, reps, warmup, timeout):
    d = runner_dir(lang, build, kernel, size)
    cmd = [os.path.join(d, "run"), kernel, variant, str(reps)] + ([param] if param else [])
    env = S.environ(kernel, size) if kernel in SIZED else dict(os.environ, MS_DATA="/opt/msdata")
    for k in S.PUBLISHED:
        env.pop(k, None)
    env["WARMUP"] = str(warmup)
    s0, t0 = D.steal_ticks(), time.time()
    box = {"rss": 0, "oom": False, "timeout": False}
    with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
        proc = subprocess.Popen(cmd, stdout=fo, stderr=fe, env=env, cwd=d, start_new_session=True,
                                preexec_fn=oom_victim)
        stop = threading.Event()

        def watch():
            while not stop.wait(0.2):
                rss = tree_rss_kb(proc.pid)
                box["rss"] = max(box["rss"], rss)
                if rss > MEM_CAP_KB:
                    box["oom"] = True
                    os.killpg(proc.pid, signal.SIGKILL)
                    return
                if time.time() - t0 > timeout:
                    box["timeout"] = True
                    os.killpg(proc.pid, signal.SIGKILL)
                    return

        th = threading.Thread(target=watch, daemon=True)
        th.start()
        _, status, ru = os.wait4(proc.pid, 0)
        stop.set()
        th.join()
        try:
            os.killpg(proc.pid, signal.SIGKILL)  # restes éventuels du groupe
        except ProcessLookupError:
            pass
        rc = os.waitstatus_to_exitcode(status)
        fo.seek(0); out = fo.read()
        fe.seek(0); err = fe.read()
    wall = time.time() - t0
    rec = {"lang": lang, "build": build, "kernel": kernel, "size": size, "variant": variant, "param": param,
           "reps": [], "lat": [], "meta": {}, "returncode": rc, "wall": wall, "steal_ticks": D.steal_ticks() - s0,
           "stderr": err.decode(errors="replace")[-2000:], "maxrss_kb": ru.ru_maxrss, "tree_rss_kb": box["rss"],
           "oom": box["oom"], "timeout": box["timeout"], "utime": ru.ru_utime, "stime": ru.ru_stime,
           "warmup": warmup, "reps_asked": reps}
    for line in out.decode(errors="replace").splitlines():
        f = line.strip().split(";")
        if f[0] == "RESULT" and len(f) >= 7:
            rec["reps"].append({"rep": int(f[4]), "sec": float(f[5]), "chk": f[6], "ok": check(kernel, size, param, f[6])})
        elif f[0] == "LAT" and len(f) >= 7:
            rec["lat"].append([int(float(x)) for x in f[2:7]])
        elif f[0] == "META" and len(f) >= 3:
            rec["meta"][f[1]] = ";".join(f[2:])
    rec["steal_frac"] = rec["steal_ticks"] / max(1e-9, wall * D.CLK_TCK * D.NCPU)
    compact(rec)
    return rec


def compact(rec):
    """Jusqu'à 10 000 répétitions par processus à la petite taille : au-delà de 100, on garde les temps triés résumés
    par leurs quantiles (disque limité) et l'ensemble des verdicts de contrôle ; la médiane par processus est exacte."""
    reps = rec["reps"]
    secs = sorted(r["sec"] for r in reps)
    rec["n"] = len(secs)
    rec["oks"] = sorted({str(r["ok"]) for r in reps})
    rec["chks"] = sorted({r["chk"] for r in reps})[:3]
    if secs:
        n = len(secs)
        rec["median"] = secs[n // 2] if n % 2 else 0.5 * (secs[n // 2 - 1] + secs[n // 2])
        rec["quantiles"] = {q: secs[min(n - 1, int(q * n))] for q in (0.0, 0.1, 0.25, 0.75, 0.9)} | {1.0: secs[-1]}
        rec["mean"] = sum(secs) / n
    if len(reps) > 100:
        rec["reps"] = []
        rec["reps_compacted"] = True


def load_calib():
    return json.load(open(CALIB)) if os.path.exists(CALIB) else {}


def save_calib(c):
    with open(CALIB + ".tmp", "w") as f:
        json.dump(c, f, indent=0, sort_keys=True)
    os.replace(CALIB + ".tmp", CALIB)


def calibrate(lang, build, kernel, size, variant, param):
    """Répétitions et échauffement d'une cellule, fixés une fois pour toutes (première passe)."""
    key = f"{lang}|{build}|{kernel}|{size}|{variant}|{param}"
    calib = load_calib()
    if key in calib:
        return calib[key]
    rec = run_one(lang, build, kernel, size, variant, param, 1, 3 if lang in JIT else 1, 4 * 3600)
    t = rec["reps"][0]["sec"] if rec["reps"] else None
    if t is None:
        c = {"reps": 1, "warmup": 1, "t_cal": None, "failed": True, "oom": rec["oom"], "timeout": rec["timeout"],
             "returncode": rec["returncode"], "stderr": rec["stderr"][-500:]}
    else:
        reps = 1 if t > 300 else max(3, min(10000, int(3.0 / max(t, 1e-7))))
        warm = max(3, math.ceil(1.0 / max(t, 1e-7))) if lang in JIT else 1
        c = {"reps": reps, "warmup": warm, "t_cal": t}
    calib = load_calib()
    calib[key] = c
    save_calib(calib)
    return c


def done_set():
    done = set()
    if os.path.isdir(RAW):
        for f in os.listdir(RAW):
            for line in open(os.path.join(RAW, f)):
                r = json.loads(line)
                done.add((r["pass"], r["lang"], r["build"], r["kernel"], r["size"], r["variant"], r["param"]))
    return done


def groups():
    g = [(k, s) for k in SIZED for s in S.ORDER[k]] + [(k, "pub") for k in SINGLE]
    return g


def variants(lang, kernel):
    return D.PLAN[kernel] + extra_variants(lang).get(kernel, [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passes", default="0,1,2")
    ap.add_argument("--langs", default=",".join(LANGS))
    ap.add_argument("--groups", default="")
    ap.add_argument("--dry", action="store_true", help="liste les blocs sans rien exécuter")
    a = ap.parse_args()
    langs = a.langs.split(",")
    gsel = set(a.groups.split(",")) if a.groups else None
    os.makedirs(RAW, exist_ok=True)
    model = cpu_model()
    try:  # le pilote, pas la victime (baisser demande un droit que le bac à sable peut refuser)
        with open("/proc/self/oom_score_adj", "w") as f:
            f.write("-900")
    except OSError:
        pass
    if not a.dry:  # toutes les constructions avant la première mesure (aucune compilation pendant un groupe)
        for lang in langs:
            for name in S.SETS:
                B.ensure_build(lang, name)
        for lang in CONTROL:
            if lang in langs:
                old_build(lang)
        log("constructions prêtes")
    for p in [int(x) for x in a.passes.split(",")]:
        gl = [g for g in groups() if gsel is None or f"{g[0]}:{g[1]}" in gsel]
        rnd = random.Random(20261119 + p)
        rnd.shuffle(gl)
        log(f"passe {p} : {len(gl)} groupes ; processeur : {model}")
        for gi, (kernel, size) in enumerate(gl):
            blocks = [(l, "new") for l in langs]
            if size == "pub":
                blocks += [(l, "old") for l in CONTROL if l in langs]
            rnd.shuffle(blocks)
            done = done_set()
            todo = [(l, b, v, q) for l, b in blocks for v, q in variants(l, kernel)
                    if (p, l, b, kernel, size, v, q) not in done]
            if a.dry:
                print(p, kernel, size, len(todo), "processus")
                continue
            if not todo:
                continue
            if kernel in SIZED:
                S.ensure_data(kernel, size)
            t_g = time.time()
            for lang, build, variant, param in todo:
                c = calibrate(lang, build, kernel, size, variant, param)
                if c.get("failed"):
                    rec = {"lang": lang, "build": build, "kernel": kernel, "size": size, "variant": variant,
                           "param": param, "reps": [], "failed_calibration": c}
                else:
                    timeout = min(4 * 3600, 600 + 3 * (c["reps"] + c["warmup"]) * c["t_cal"])
                    for attempt in range(2):
                        rec = run_one(lang, build, kernel, size, variant, param, c["reps"], c["warmup"], timeout)
                        rec["attempt"] = attempt
                        if rec["steal_frac"] <= 0.05:
                            break
                rec.update({"pass": p, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "cpu_model": cpu_model()})
                with open(os.path.join(RAW, f"{lang}.jsonl"), "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(f"p{p} {kernel}:{size} {lang}/{build} {variant} {param} n={rec.get('n', 0)}"
                      f" med={rec.get('median', float('nan')):.6g}s ok={rec.get('oks')}"
                      f" oom={rec.get('oom')} rc={rec.get('returncode')}", flush=True)
            if kernel in SIZED and size != "pub":
                S.drop_data(kernel, size)
            log(f"passe {p} groupe {gi + 1}/{len(gl)} {kernel}:{size} {len(todo)} processus {time.time() - t_g:.0f}s")


if __name__ == "__main__":
    main()
