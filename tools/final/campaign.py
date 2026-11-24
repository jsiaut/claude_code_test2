#!/usr/bin/env python3
"""v4, campagne finale (docs/V4_FINAL.md, 5 à 7) : étalonnage et validation, puis trois passes.

Constructions : tools/final/build.py (/dev/shm/msbuild/<langage>/f_<construction>_<jeu>), toutes faites et contrôlées
avant la première mesure. Groupes : (noyau, taille), 21 pour les sept noyaux à trois tailles, plus K2 et K3 à leur
taille. Machine : numéro inscrit dans /dev/shm/ms_final_machine par tools/final/machine.sh après la caractérisation
(un redémarrage le perd : le pilote refuse alors de mesurer) ; chaque enregistrement porte ce numéro et l'identifiant de
démarrage du noyau (boot_id).

* calibrate : chaque cellule à chaque taille, un processus, une répétition (échauffement : 3 répétitions pour les
  langages à JIT, 1 sinon), dans l'ordre des groupes de la passe 0 ; fixe les répétitions (environ 3 s, au moins 3, au
  plus 10 000 ; une au-delà de 300 s) et l'échauffement (JIT : au moins 3 et au moins une seconde), vérifie les sommes
  de contrôle de la taille (results/sizes/expected.json ; taille publiée : tools/driver.py). Statut d'une cellule :
  ok, checksum (fausse), error (code de retour), oom (sentinelle de 13 Gio ou tuée par le noyau), timeout.
* run : trois passes ; ordre des groupes tiré au hasard (graine SEED + passe), puis, dans chaque groupe, ordre des blocs
  (langage, construction, copie) tiré par une graine propre au groupe. K2 et K8 naturel : trois copies dans la passe 0,
  deux dans les passes 1 et 2 (sept processus). Règle de la section 6 : un groupe d'une passe est mesuré sur une seule
  machine ; s'il a des enregistrements d'un autre démarrage et n'est pas terminé, ils sont mis à part
  (work/discarded) et le groupe est refait en entier. b3 (tools/k3_align.c, deux exécutions) est mesuré juste avant et
  juste après chaque groupe de K3. Vol de temps au-delà de 5 % : processus refait une fois. Sentinelle de mémoire (plus
  grand VmRSS du groupe de processus, 13 Gio). Modèle du processeur vérifié avant chaque processus.
* b3 <étiquette> : une mesure de b3 hors groupe (début, fin).
Écritures dans results/final/work ; tools/final/save_progress.sh les recopie dans results/final et les pousse.

Usage : campaign.py calibrate|run|b3 [--passes 0,1,2] [--langs a,b] [--groups k1:small,...] [--dry] [étiquette]"""
import argparse, json, math, os, random, re, shutil, signal, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "sizes"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("fbuild", os.path.join(HERE, "build.py"))
FB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FB)
import sizes as S  # noqa: E402
import driver as D  # noqa: E402  (PLAN, sommes de contrôle de la taille publiée, vol de temps)
from validate import checksum_ok  # noqa: E402  (tolérances de la spécification, règle des 2^53)
from final_v4 import needed_keys  # noqa: E402  (cellules du score)

LANGS = FB.LANGS
SIZED = ["k1", "k4", "k5", "k6", "k7", "k8", "k9"]
SINGLE = ["k2", "k3"]
NATURAL = {"k1": [("natural", "energy"), ("natural_shuffled", "energy")], "k4": [("natural_unsorted", "")],
           "k5": [("natural", "")], "k6": [("natural", "q6"), ("natural", "q1")], "k7": [("natural", "")],
           "k8": [("natural", "")], "k9": [("natural", "")]}
NEEDED = needed_keys()
JIT = {"java", "csharp", "js", "julia"}
MEM_CAP_KB = 13 * 1024 * 1024
SEED = 20261123
EXP_SIZES = json.load(open(os.path.join(ROOT, "results", "sizes", "expected.json")))
WORK = os.path.join(ROOT, "results", "final", "work")
RAW = os.path.join(WORK, "raw")
DISC = os.path.join(WORK, "discarded")
CALIB = os.path.join(WORK, "calib.json")
CALREC = os.path.join(WORK, "calib.jsonl")
B3 = os.path.join(WORK, "b3.jsonl")
LOG = os.path.join(WORK, "campaign.log")


def log(msg):
    line = time.strftime("%Y-%m-%dT%H:%M:%S ") + msg
    print(line, flush=True)
    os.makedirs(WORK, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def cpu_model():
    info = {}
    for line in open("/proc/cpuinfo"):
        if ":" in line:
            k, v = (x.strip() for x in line.split(":", 1))
            info.setdefault(k, v)
        if not line.strip() and info:
            break
    return f"{info.get('cpu family')}/{info.get('model')}/{info.get('stepping')} {info.get('model name')}"


MODEL = "6/207/2"


def variant_file(path):
    out = {}
    if os.path.exists(path):
        for line in open(path):
            f = line.split()
            if len(f) >= 2:
                out.setdefault(f[0], []).append((f[1], f[2] if len(f) > 2 else ""))
    return out


def cells(lang, cons, kernel):
    """Cellules (variante, paramètre) d'une construction pour un noyau (docs/V4_FINAL.md, 5)."""
    if cons == "pub":
        extra = variant_file(os.path.join(ROOT, "bench", lang, "extra_variants")).get(kernel, [])
        return [(v, q) for v, q in D.PLAN[kernel] + extra if (kernel, v, q) in NEEDED]
    if cons == "cv":
        return variant_file(os.path.join(ROOT, "bench", lang + "_cv", "cv_variants")).get(kernel, [])
    if cons in ("chk", "unc"):
        return NATURAL.get(kernel, [])
    if cons in ("cv_chk", "cv_unc"):
        return [("natural_flat", "")] if kernel == "k9" else []
    raise ValueError(cons)


def copies(kernel, variant, p):
    """Processus d'une cellule dans la passe p : sept en tout pour K2 et K8 naturel (3, 2, 2), un sinon."""
    if kernel == "k2" or (kernel == "k8" and variant == "natural"):
        return 3 if p == 0 else 2
    return 1


def groups():
    return [(k, s) for k in SIZED for s in S.ORDER[k]] + [(k, "pub") for k in SINGLE]


def build_set(kernel, size):
    return (S.set_of(kernel, size) if kernel in SIZED else None) or "pub"


def runner_dir(lang, cons, kernel, size):
    return FB.build_dir(lang, cons, build_set(kernel, size))


def boot_id():
    return open("/proc/sys/kernel/random/boot_id").read().strip()


def machine():
    m = FB.machine()
    if m is None:
        raise SystemExit("machine non enregistrée (/dev/shm/ms_final_machine absent : redémarrage ?) : "
                         "lancer tools/final/machine.sh <numéro>")
    return m


def check(kernel, size, param, chk):
    if kernel not in SIZED or size == "pub":
        return D.check(kernel, param, chk)
    exp = EXP_SIZES.get(f"{kernel}:{size}" + (f":{param}" if kernel == "k6" else ""))
    return None if exp is None else checksum_ok(kernel, chk, exp)


def oom_victim():
    with open("/proc/self/oom_score_adj", "w") as f:
        f.write("1000")


def tree_rss_kb(pgid):
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


def compact(rec):
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


def run_one(lang, cons, kernel, size, variant, param, reps, warmup, timeout):
    d = runner_dir(lang, cons, kernel, size)
    cmd = [os.path.join(d, "run"), kernel, variant, str(reps)] + ([param] if param else [])
    env = S.environ(kernel, size) if kernel in SIZED else dict(os.environ, MS_DATA="/opt/msdata")
    for k in list(env):
        if k.startswith("MS_") and k != "MS_DATA":  # la taille est dans la construction (ou la copie)
            env.pop(k)
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
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        rc = os.waitstatus_to_exitcode(status)
        fo.seek(0); out = fo.read()
        fe.seek(0); err = fe.read()
    wall = time.time() - t0
    rec = {"lang": lang, "construction": cons, "kernel": kernel, "size": size, "variant": variant, "param": param,
           "reps": [], "lat": [], "meta": {}, "returncode": rc, "wall": wall, "steal_ticks": D.steal_ticks() - s0,
           "stderr": err.decode(errors="replace")[-2000:], "maxrss_kb": ru.ru_maxrss, "tree_rss_kb": box["rss"],
           "proc_rss_kb": box["top"], "oom": box["oom"] or rc == -9, "sentinel": box["oom"], "timeout": box["timeout"],
           "utime": ru.ru_utime, "stime": ru.ru_stime, "warmup": warmup, "reps_asked": reps}
    for line in out.decode(errors="replace").splitlines():
        f = line.strip().split(";")
        if f[0] == "RESULT" and len(f) >= 7:
            rec["reps"].append({"rep": int(f[4]), "sec": float(f[5]), "chk": f[6],
                                "ok": check(kernel, size, param, f[6])})
        elif f[0] == "LAT" and len(f) >= 7:
            rec["lat"].append([int(float(x)) for x in f[2:7]])
        elif f[0] == "META" and len(f) >= 3:
            rec["meta"][f[1]] = ";".join(f[2:])
    rec["steal_frac"] = rec["steal_ticks"] / max(1e-9, wall * D.CLK_TCK * D.NCPU)
    compact(rec)
    return rec


def status_of(rec):
    if rec["timeout"]:
        return "timeout"
    if rec["oom"]:
        return "oom"
    if rec["returncode"] != 0 or not rec["n"]:
        return "error"
    if rec["oks"] != ["True"]:
        return "checksum"
    return "ok"


def ckey(lang, cons, kernel, size, variant, param):
    return f"{lang}|{cons}|{kernel}|{size}|{variant}|{param}"


def load_json(path, default):
    return json.load(open(path)) if os.path.exists(path) else default


def save_calib(c):
    tmp = CALIB + ".tmp"
    json.dump(c, open(tmp, "w"), indent=0, sort_keys=True)
    os.replace(tmp, CALIB)


def check_host(m):
    model = cpu_model()
    if not model.startswith(MODEL + " "):
        raise SystemExit(f"modèle de processeur {model} : la campagne demande {MODEL} (docs/V4_FINAL.md, 6)")
    if FB.machine() != m:
        raise SystemExit("numéro de machine changé ou effacé pendant la campagne")


def ensure_builds(langs):
    for lang in langs:
        for cons in FB.constructions(lang):
            for sset in FB.SETS:
                d = FB.build_dir(lang, cons, sset)
                p = os.path.join(d, ".source_hash")
                if not (os.path.exists(p) and open(p).read() == FB.input_hash(lang, cons, sset)):
                    raise SystemExit(f"construction absente ou périmée : {d} (lancer tools/final/build.py)")


def selected_groups(gsel):
    return [g for g in groups() if gsel is None or f"{g[0]}:{g[1]}" in gsel]


def pass_order(p, gsel):
    gl = groups()
    random.Random(SEED + p).shuffle(gl)
    return [g for g in gl if gsel is None or f"{g[0]}:{g[1]}" in gsel]


def blocks_of(langs, kernel, size, p):
    """Blocs (langage, construction, copie) d'un groupe, dans l'ordre tiré pour la passe p."""
    bl = []
    for lang in LANGS:
        for cons in FB.constructions(lang):
            cl = cells(lang, cons, kernel)
            if not cl:
                continue
            for j in range(max(copies(kernel, v, p) for v, q in cl)):
                bl.append((lang, cons, j))
    random.Random(f"{SEED}:{p}:{kernel}:{size}").shuffle(bl)
    return [b for b in bl if b[0] in langs]


# ------------------------------------------------------------------ étalonnage et validation
def calibrate(langs, gsel, dry):
    m = None if dry else machine()
    if not dry:
        ensure_builds(langs)
    calib = load_json(CALIB, {})
    for kernel, size in pass_order(0, gsel):
        todo = [(l, c, v, q) for l in langs for c in FB.constructions(l) for v, q in cells(l, c, kernel)
                if ckey(l, c, kernel, size, v, q) not in calib]
        if dry:
            print(f"étalonnage {kernel}:{size} : {len(todo)} cellules")
            continue
        if not todo:
            continue
        if kernel in SIZED:
            S.ensure_data(kernel, size)
        t_g = time.time()
        for lang, cons, variant, param in todo:
            check_host(m)
            warm = 3 if lang in JIT else 1
            rec = run_one(lang, cons, kernel, size, variant, param, 1, warm, 4 * 3600)
            st = status_of(rec)
            t = rec["median"] if rec.get("n") else None
            c = {"status": st, "t_cal": t, "machine": m, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
            if t is not None:
                c["reps"] = 1 if t > 300 else max(3, min(10000, int(3.0 / max(t, 1e-7))))
                c["warmup"] = max(3, math.ceil(1.0 / max(t, 1e-7))) if lang in JIT else 1
            if st != "ok":
                c["detail"] = {"returncode": rec["returncode"], "chks": rec.get("chks"), "stderr": rec["stderr"][-600:],
                               "proc_rss_kb": rec["proc_rss_kb"]}
            calib[ckey(lang, cons, kernel, size, variant, param)] = c
            save_calib(calib)
            rec.update({"machine": m, "boot_id": boot_id(), "ts": c["ts"], "status": st})
            with open(CALREC, "a") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"étalonnage {kernel}:{size} {lang}/{cons} {variant} {param} : {st} t={t}", flush=True)
        if kernel in SIZED and size != "pub":
            S.drop_data(kernel, size)
        log(f"étalonnage {kernel}:{size} : {len(todo)} cellules, {time.time() - t_g:.0f} s")
        save_progress()
    if not dry:
        bad = {k: v for k, v in calib.items() if v["status"] in ("checksum", "error")}
        log(f"étalonnage : {len(calib)} cellules, {len(bad)} à corriger (somme de contrôle ou erreur), "
            f"{sum(v['status'] in ('oom', 'timeout') for v in calib.values())} hors mémoire ou hors durée")
        for k, v in sorted(bad.items()):
            print("  à corriger :", k, v["status"], v.get("detail", {}).get("chks"))


# ------------------------------------------------------------------ b3
K3_ALIGN = "/dev/shm/k3_align"


def b3(label, p=None, m=None):
    # Enregistre la médiane des 16 décalages de chaque exécution et les 16 temps eux-mêmes (« outputs ») ; depuis la
    # v4.1 (A2, docs/METHOD.md, 5), l'analyse prend le plus lent des 16, relu dans « outputs ».
    if not os.path.exists(K3_ALIGN):
        subprocess.run(["clang-23", "-O2", "-march=native", "-o", K3_ALIGN, os.path.join(ROOT, "tools", "k3_align.c")],
                       check=True)
    meds, texts = [], []
    for _ in range(2):
        out = subprocess.run([K3_ALIGN], capture_output=True, text=True, check=True).stdout
        ms = [float(x) for x in re.findall(r":\s+([0-9.]+) ms", out)]
        if len(ms) != 16:
            raise SystemExit(f"k3_align : sortie inattendue\n{out}")
        ms.sort()
        meds.append(0.5 * (ms[7] + ms[8]))
        texts.append(out)
    rec = {"label": label, "pass": p, "machine": m or FB.machine(), "boot_id": boot_id(),
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "medians_ms": meds, "b3_ms": sum(meds) / 2, "outputs": texts}
    os.makedirs(WORK, exist_ok=True)
    with open(B3, "a") as f:
        f.write(json.dumps(rec) + "\n")
    log(f"b3 {label} (passe {p}, machine {rec['machine']}) : {meds[0]:.2f} et {meds[1]:.2f} ms")
    return rec


# ------------------------------------------------------------------ passes
def read_raw():
    recs = []
    if os.path.isdir(RAW):
        for f in sorted(os.listdir(RAW)):
            for line in open(os.path.join(RAW, f)):
                recs.append(json.loads(line))
    return recs


def rkey(r):
    return (r["pass"], r["lang"], r["construction"], r["kernel"], r["size"], r["variant"], r["param"], r["copy"])


def discard_group(p, kernel, size, reason):
    """Met à part les enregistrements d'un groupe interrompu (section 6) ; renvoie leur nombre."""
    n = 0
    os.makedirs(DISC, exist_ok=True)
    for f in sorted(os.listdir(RAW)) if os.path.isdir(RAW) else []:
        keep, out = [], []
        for line in open(os.path.join(RAW, f)):
            r = json.loads(line)
            (out if (r["pass"], r["kernel"], r["size"]) == (p, kernel, size) else keep).append(line)
        if out:
            with open(os.path.join(DISC, f), "a") as g:
                for line in out:
                    r = json.loads(line)
                    r["discarded"] = reason
                    g.write(json.dumps(r) + "\n")
            tmp = os.path.join(RAW, f + ".tmp")
            with open(tmp, "w") as g:
                g.writelines(keep)
            os.replace(tmp, os.path.join(RAW, f))
            n += len(out)
    return n


def run(langs, passes, gsel, dry):
    m = None if dry else machine()
    calib = load_json(CALIB, {})
    if not dry:
        ensure_builds(langs)
    os.makedirs(RAW, exist_ok=True)
    total = 0
    for p in passes:
        gl = pass_order(p, gsel)
        if not dry:
            log(f"passe {p} : {len(gl)} groupes ; machine {m} ; processeur : {cpu_model()}")
        for gi, (kernel, size) in enumerate(gl):
            recs = [r for r in read_raw() if (r["pass"], r["kernel"], r["size"]) == (p, kernel, size)]
            done = {rkey(r) for r in recs}
            bl = blocks_of(langs, kernel, size, p)
            todo = [(l, c, j, v, q) for l, c, j in bl for v, q in cells(l, c, kernel) if j < copies(kernel, v, p)
                    and (p, l, c, kernel, size, v, q, j) not in done]
            total += len(todo)
            if dry:
                print(f"passe {p} groupe {gi + 1} {kernel}:{size} : {len(todo)} processus")
                continue
            if not todo:
                continue
            other = {r["boot_id"] for r in recs} - {boot_id()}
            if other:
                n = discard_group(p, kernel, size, f"groupe interrompu par un redémarrage (démarrage {sorted(other)})")
                log(f"passe {p} {kernel}:{size} : {n} enregistrements d'un autre démarrage mis à part ; groupe refait")
                todo = [(l, c, j, v, q) for l, c, j in bl for v, q in cells(l, c, kernel) if j < copies(kernel, v, p)]
            missing = [ckey(l, c, kernel, size, v, q) for l, c, j, v, q in todo
                       if ckey(l, c, kernel, size, v, q) not in calib]
            if missing:
                raise SystemExit(f"cellules non étalonnées : {missing[:5]}…")
            if kernel == "k3":
                b3("avant le groupe K3", p, m)
            if kernel in SIZED:
                S.ensure_data(kernel, size)
            t_g = time.time()
            for lang, cons, j, variant, param in todo:
                check_host(m)
                c = calib[ckey(lang, cons, kernel, size, variant, param)]
                if c["status"] != "ok":
                    rec = {"lang": lang, "construction": cons, "kernel": kernel, "size": size, "variant": variant,
                           "param": param, "reps": [], "skipped": c["status"], "n": 0}
                else:
                    timeout = min(4 * 3600, 600 + 3 * (c["reps"] + c["warmup"]) * c["t_cal"])
                    for attempt in range(2):
                        rec = run_one(lang, cons, kernel, size, variant, param, c["reps"], c["warmup"], timeout)
                        rec["attempt"] = attempt
                        if rec["steal_frac"] <= 0.05:
                            break
                rec.update({"pass": p, "copy": j, "machine": m, "boot_id": boot_id(),
                            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "cpu_model": cpu_model()})
                with open(os.path.join(RAW, f"{lang}.jsonl"), "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(f"p{p} {kernel}:{size} {lang}/{cons}#{j} {variant} {param} n={rec.get('n', 0)} "
                      f"med={rec.get('median', float('nan')):.6g}s ok={rec.get('oks')} "
                      f"{rec.get('skipped') or status_of(rec)}", flush=True)
            if kernel in SIZED and size != "pub":
                S.drop_data(kernel, size)
            if kernel == "k3":
                b3("après le groupe K3", p, m)
            log(f"passe {p} groupe {gi + 1}/{len(gl)} {kernel}:{size} : {len(todo)} processus, "
                f"{time.time() - t_g:.0f} s")
            save_progress()
    if dry:
        print(f"{total} processus")


def save_progress():
    subprocess.run(["sh", os.path.join(HERE, "save_progress.sh")], check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["calibrate", "run", "b3"])
    ap.add_argument("label", nargs="?", default="")
    ap.add_argument("--passes", default="0,1,2")
    ap.add_argument("--langs", default=",".join(LANGS))
    ap.add_argument("--groups", default="")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    langs = a.langs.split(",")
    gsel = set(a.groups.split(",")) if a.groups else None
    try:  # le pilote, pas la victime, si le groupe de processus manque de mémoire
        with open("/proc/self/oom_score_adj", "w") as f:
            f.write("-900")
    except OSError:
        pass
    if a.action == "calibrate":
        calibrate(langs, gsel, a.dry)
    elif a.action == "run":
        run(langs, [int(x) for x in a.passes.split(",")], gsel, a.dry)
    else:
        b3(a.label or "hors groupe")
        save_progress()


if __name__ == "__main__":
    main()
