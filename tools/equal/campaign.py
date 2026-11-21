#!/usr/bin/env python3
"""v4, point 3 : campagne des conditions égales (docs/V4_EQUAL.md, sections 4, 6 et 7 ; écart 5.1).

Trois passes. Dans chaque passe, l'ordre des groupes (un par noyau, K1 à K9 ; K10, hors score, n'est pas mesuré) est
tiré au hasard (graine 20261121 + passe), puis celui des blocs (langage, construction) dans chaque groupe ; un bloc
exécute un processus par cellule. Constructions (tools/equal/build.py, /dev/shm/msbuild/<langage>/<construction>),
toutes faites avant la première mesure :
* pub : source publié, mode publié ; les cellules du score à la taille publiée (base « Hôte » refaite sur l'hôte de la
  campagne, écart 5.1) ;
* eq : copie bench/<langage>_eq, mode publié ; K4 tuned (R3) et K9 natural_flat (R2), selon son fichier eq_variants ;
* chk et unc : source publié dans les modes R1 et R1' (MS_MODE de build.sh ; Julia : option de son lanceur) ; les
  cellules naturelles (K1 natural et natural_shuffled, K4 natural_unsorted, K5 natural, K6 natural Q6 et Q1, K7
  natural, K8 natural avec ses latences, K9 natural) ;
* eq_chk (C++, D) et eq_unc (Nim, Mojo, Swift, Go, OCaml, D) : K9 natural_flat de la copie dans ces modes.
Comme au point 2 (tools/sizes/campaign.py) : répétitions fixées par une exécution de calibration avant le premier
processus de la cellule (environ 3 s par processus, au moins 3 et au plus 10 000 ; une seule au-delà de 300 s),
échauffement d'une répétition (langages à JIT : au moins 3 et au moins une seconde), processus refait une fois si le
vol de temps de la machine virtuelle dépasse 5 %, sentinelle de mémoire (plus grand VmRSS du groupe de processus,
13 Gio). Le modèle du processeur est vérifié avant chaque processus : s'il change, la campagne s'arrête (section 5).
Sortie : results/equal/work/raw/<langage>.jsonl (une ligne par processus), calib.json, campaign.log ;
tools/equal/save_progress.sh les recopie dans results/equal et les pousse à la fin de chaque groupe. Reprise : un
processus déjà enregistré (passe, langage, construction, noyau, variante, paramètre) n'est pas refait.

Usage : campaign.py [--passes 0,1,2] [--langs c,rust,...] [--kernels k1,...] [--dry]"""
import argparse, json, math, os, random, signal, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import build as B  # noqa: E402
import driver as D  # noqa: E402  (PLAN des noyaux, sommes de contrôle de la taille publiée, vol de temps)
from analyze_v3 import needed_keys  # noqa: E402  (cellules du score)

LANGS = ["c", "cpp", "rust", "zig", "odin", "c3", "d", "nim", "ada", "fortran", "chapel", "mojo", "swift", "fpc", "go",
         "csharp", "java", "haskell", "ocaml", "python", "lua", "php", "bqn", "js", "julia"]
KERNELS = ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9"]
CHK = ["c", "cpp", "fortran", "zig", "c3", "d", "chapel", "fpc"]               # R1 (3.1)
# R1' (3.1). D y est aussi : son mode publié (-release) garde les vérifications du code @safe, dont les modèles de
# Phobos instanciés dans le programme (893 appels au gestionnaire de dépassement dans le binaire publié, 177 avec
# -boundscheck=off ; results/equal/builds.txt), et le tableau 3.1 lui donne un mode R1' (écart daté dans le plan).
UNC = ["swift", "ada", "nim", "odin", "julia", "mojo", "go", "ocaml", "d"]
EQ_CHK = ["cpp", "d"]                                                          # R2 dans le mode R1
EQ_UNC = ["nim", "mojo", "swift", "go", "ocaml", "d"]                          # R2 dans le mode R1'
NATURAL = {"k1": [("natural", "energy"), ("natural_shuffled", "energy")], "k4": [("natural_unsorted", "")],
           "k5": [("natural", "")], "k6": [("natural", "q6"), ("natural", "q1")], "k7": [("natural", "")],
           "k8": [("natural", "")], "k9": [("natural", "")]}
NEEDED = needed_keys()
JIT = {"java", "csharp", "js", "julia"}
MEM_CAP_KB = 13 * 1024 * 1024
SEED = 20261121
WORK = os.path.join(ROOT, "results", "equal", "work")
RAW = os.path.join(WORK, "raw")
CALIB = os.path.join(WORK, "calib.json")
LOG = os.path.join(WORK, "campaign.log")


def log(msg):
    line = time.strftime("%Y-%m-%dT%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def cpu_model():
    """Modèle de l'hôte (famille, modèle, pas, nom) : un seul modèle pendant toute la campagne (section 5)."""
    info = {}
    for line in open("/proc/cpuinfo"):
        if ":" in line:
            k, v = (x.strip() for x in line.split(":", 1))
            info.setdefault(k, v)
        if not line.strip() and info:
            break
    return f"{info.get('cpu family')}/{info.get('model')}/{info.get('stepping')} {info.get('model name')}"


def variant_file(path):
    """{noyau: [(variante, paramètre)]} d'un fichier extra_variants ou eq_variants (« k4 tuned », « k1 x energy »)."""
    out = {}
    if os.path.exists(path):
        for line in open(path):
            f = line.split()
            if len(f) >= 2:
                out.setdefault(f[0], []).append((f[1], f[2] if len(f) > 2 else ""))
    return out


def builds_of(lang):
    b = ["pub"]
    if os.path.isdir(os.path.join(ROOT, "bench", lang + "_eq")):
        b.append("eq")
    b += [n for n, lst in (("chk", CHK), ("unc", UNC), ("eq_chk", EQ_CHK), ("eq_unc", EQ_UNC)) if lang in lst]
    return b


def cells(lang, build, kernel):
    """Cellules (variante, paramètre) d'un bloc."""
    if build == "pub":
        extra = variant_file(os.path.join(ROOT, "bench", lang, "extra_variants")).get(kernel, [])
        return [(v, q) for v, q in D.PLAN[kernel] + extra if (kernel, v, q) in NEEDED]
    if build == "eq":
        return variant_file(os.path.join(ROOT, "bench", lang + "_eq", "eq_variants")).get(kernel, [])
    if build in ("chk", "unc"):
        return NATURAL.get(kernel, [])
    if build in ("eq_chk", "eq_unc"):
        return [("natural_flat", "")] if kernel == "k9" else []
    raise ValueError(build)


def oom_victim():
    """Dans le processus mesuré, avant exec : premier tué en cas de manque de mémoire du groupe de processus."""
    with open("/proc/self/oom_score_adj", "w") as f:
        f.write("1000")


def tree_rss_kb(pgid):
    """Somme et plus grand VmRSS des processus du groupe ; la sentinelle compare le plus grand (point 2, écart 4.1)."""
    total = top = 0
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            if os.getpgid(int(p)) != pgid:
                continue
            for line in open(f"/proc/{p}/status"):
                if line.startswith("VmRSS:"):
                    v = int(line.split()[1])
                    total += v
                    top = max(top, v)
        except (OSError, ProcessLookupError):
            pass
    return total, top


def run_one(lang, build, kernel, variant, param, reps, warmup, timeout):
    d = B.build_dir(lang, build)
    cmd = [os.path.join(d, "run"), kernel, variant, str(reps)] + ([param] if param else [])
    env = {k: v for k, v in os.environ.items() if not k.startswith("MS_")}
    env["MS_DATA"] = "/opt/msdata"
    env["WARMUP"] = str(warmup)
    s0, t0 = D.steal_ticks(), time.time()
    box = {"rss": 0, "top": 0, "oom": False, "timeout": False}
    with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
        proc = subprocess.Popen(cmd, stdout=fo, stderr=fe, env=env, cwd=d, start_new_session=True,
                                preexec_fn=oom_victim)
        stop = threading.Event()

        def watch():
            while not stop.wait(0.2):
                rss, top = tree_rss_kb(proc.pid)
                box["rss"], box["top"] = max(box["rss"], rss), max(box["top"], top)
                if top > MEM_CAP_KB:
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
    rec = {"lang": lang, "build": build, "kernel": kernel, "size": "pub", "variant": variant, "param": param,
           "reps": [], "lat": [], "meta": {}, "returncode": rc, "wall": wall, "steal_ticks": D.steal_ticks() - s0,
           "stderr": err.decode(errors="replace")[-2000:], "maxrss_kb": ru.ru_maxrss, "tree_rss_kb": box["rss"],
           "proc_rss_kb": box["top"], "oom": box["oom"], "timeout": box["timeout"], "utime": ru.ru_utime,
           "stime": ru.ru_stime, "warmup": warmup, "reps_asked": reps}
    for line in out.decode(errors="replace").splitlines():
        f = line.strip().split(";")
        if f[0] == "RESULT" and len(f) >= 7:
            rec["reps"].append({"rep": int(f[4]), "sec": float(f[5]), "chk": f[6], "ok": D.check(kernel, param, f[6])})
        elif f[0] == "LAT" and len(f) >= 7:
            rec["lat"].append([int(float(x)) for x in f[2:7]])
        elif f[0] == "META" and len(f) >= 3:
            rec["meta"][f[1]] = ";".join(f[2:])
    rec["steal_frac"] = rec["steal_ticks"] / max(1e-9, wall * D.CLK_TCK * D.NCPU)
    compact(rec)
    return rec


def compact(rec):
    """Au-delà de 100 répétitions, on garde les temps résumés par leurs quantiles (disque limité) et l'ensemble des
    verdicts de contrôle ; la médiane par processus est exacte."""
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


def calibrate(lang, build, kernel, variant, param):
    """Répétitions et échauffement d'une cellule, fixés une fois pour toutes (première passe)."""
    key = f"{lang}|{build}|{kernel}|{variant}|{param}"
    calib = load_calib()
    if key in calib:
        return calib[key]
    rec = run_one(lang, build, kernel, variant, param, 1, 3 if lang in JIT else 1, 4 * 3600)
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
                done.add((r["pass"], r["lang"], r["build"], r["kernel"], r["variant"], r["param"]))
    return done


def save_progress():
    r = subprocess.run(["sh", os.path.join(HERE, "save_progress.sh")], capture_output=True, text=True)
    if r.returncode:
        log(f"enregistrement : code {r.returncode} {r.stderr[-300:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passes", default="0,1,2")
    ap.add_argument("--langs", default=",".join(LANGS))
    ap.add_argument("--kernels", default=",".join(KERNELS))
    ap.add_argument("--dry", action="store_true", help="liste les groupes sans rien construire ni exécuter")
    a = ap.parse_args()
    langs = a.langs.split(",")
    kernels = a.kernels.split(",")
    if not a.dry:
        os.makedirs(RAW, exist_ok=True)
    model = cpu_model()
    try:  # le pilote, pas la victime (baisser demande un droit que le bac à sable peut refuser)
        with open("/proc/self/oom_score_adj", "w") as f:
            f.write("-900")
    except OSError:
        pass
    if not a.dry:  # toutes les constructions avant la première mesure (aucune compilation pendant un groupe)
        for lang in langs:
            for b in builds_of(lang):
                B.ensure(lang, b)
        log(f"constructions prêtes ; processeur : {model}")
    for p in [int(x) for x in a.passes.split(",")]:
        gl = list(kernels)
        rnd = random.Random(SEED + p)
        rnd.shuffle(gl)
        (print if a.dry else log)(f"passe {p} : {len(gl)} groupes ; processeur : {model}")
        for gi, kernel in enumerate(gl):
            blocks = [(l, b) for l in langs for b in builds_of(l) if cells(l, b, kernel)]
            rnd.shuffle(blocks)
            done = done_set()
            todo = [(l, b, v, q) for l, b in blocks for v, q in cells(l, b, kernel)
                    if (p, l, b, kernel, v, q) not in done]
            if a.dry:
                print(p, kernel, len(blocks), "blocs", len(todo), "processus")
                continue
            if not todo:
                continue
            t_g = time.time()
            for lang, build, variant, param in todo:
                if cpu_model() != model:
                    log(f"le modèle du processeur a changé ({cpu_model()} au lieu de {model}) : arrêt (section 5)")
                    save_progress()
                    sys.exit(3)
                c = calibrate(lang, build, kernel, variant, param)
                if c.get("failed"):
                    rec = {"lang": lang, "build": build, "kernel": kernel, "size": "pub", "variant": variant,
                           "param": param, "reps": [], "failed_calibration": c}
                else:
                    timeout = min(4 * 3600, 600 + 3 * (c["reps"] + c["warmup"]) * c["t_cal"])
                    for attempt in range(2):
                        rec = run_one(lang, build, kernel, variant, param, c["reps"], c["warmup"], timeout)
                        rec["attempt"] = attempt
                        if rec["steal_frac"] <= 0.05:
                            break
                rec.update({"pass": p, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "cpu_model": cpu_model()})
                with open(os.path.join(RAW, f"{lang}.jsonl"), "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(f"p{p} {kernel} {lang}/{build} {variant} {param} n={rec.get('n', 0)}"
                      f" med={rec.get('median', float('nan')):.6g}s ok={rec.get('oks')}"
                      f" oom={rec.get('oom')} rc={rec.get('returncode')}", flush=True)
            log(f"passe {p} groupe {gi + 1}/{len(gl)} {kernel} {len(todo)} processus {time.time() - t_g:.0f}s")
            save_progress()
    (print if a.dry else log)("campagne finie")


if __name__ == "__main__":
    main()
