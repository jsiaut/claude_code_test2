#!/usr/bin/env python3
"""Pilote de mesure (voir docs/METHODOLOGY.md).

Pour chaque (langage, noyau, variante, paramètre) : P processus indépendants,
chacun exécutant WARMUP répétitions non mesurées puis R répétitions mesurées
(le programme chronomètre lui-même la section de calcul). Le pilote enregistre :
  * les lignes RESULT / LAT / META émises,
  * rusage du processus fils via os.wait4 (pic RSS, temps CPU user/sys),
  * le temps « steal » de l'hyperviseur (/proc/stat) pendant l'exécution,
  * la validité du résultat par rapport aux sommes de contrôle attendues.
Sortie : results/raw/<langage>.jsonl (une ligne JSON par processus).

Usage : driver.py LANG [--kernels k1,k2] [--procs 3] [--quick]
"""
import argparse, json, os, subprocess, tempfile, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = json.load(open(os.path.join(ROOT, "results", "expected.json")))

K2_SIZES = ["16384", "65536", "262144", "524288", "2097152", "8388608", "16777216", "33554432", "67108864", "268435456"]
PLAN = {
    "k1": [("natural", "energy"), ("aos", "energy"), ("soa", "energy"), ("natural_shuffled", "energy")],
    "k2": [("tuned", s) for s in K2_SIZES],
    "k3": [("rmw_packed", ""), ("rmw_padded", ""), ("sw_packed", ""), ("sw_padded", "")],
    "k4": [("natural_unsorted", ""), ("natural_sorted", ""), ("branchless_unsorted", "")],
    "k5": [("natural", ""), ("tuned", "")],
    "k6": [(v, q) for v in ("natural", "tuned", "mt") for q in ("q6", "q1")],
    "k7": [("natural", ""), ("tuned", "")],
    "k8": [("natural", ""), ("tuned", "")],
    "k9": [("natural", ""), ("tuned", ""), ("mt", "")],
    "k10": [("natural", ""), ("tuned", "")],
    "fp": [("footprint", "energy"), ("footprint0", "energy")],
}
TOL = {"k1": 1e-6, "k5": 1e-3, "k9": 1e-9}
CLK_TCK = os.sysconf("SC_CLK_TCK")
NCPU = os.cpu_count()


def steal_ticks():
    with open("/proc/stat") as f:
        parts = f.readline().split()
    return int(parts[8])  # cpu user nice system idle iowait irq softirq steal


def check(kernel, param, chk):
    key = f"{kernel}:{param}" if kernel in ("k2", "k6") else kernel
    exp = EXPECTED.get(key)
    if exp is None:
        return None
    if kernel in TOL:
        try:
            a, b = float(chk), float(exp)
        except ValueError:
            return False
        return abs(a - b) <= TOL[kernel] * abs(b)
    return chk.strip() == exp


def run_one(lang, kernel, variant, param, reps, warmup, timeout):
    runner = os.path.join(ROOT, "bench", lang, "run")
    k = "k1" if kernel == "fp" else kernel
    cmd = [runner, k, variant, str(reps)] + ([param] if param else [])
    env = dict(os.environ, WARMUP=str(warmup), MS_DATA=os.environ.get("MS_DATA", "/opt/msdata"))
    s0, t0 = steal_ticks(), time.time()
    with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
        proc = subprocess.Popen(cmd, stdout=fo, stderr=fe, env=env, cwd=os.path.join(ROOT, "bench", lang))
        timer = threading.Timer(timeout, proc.kill)
        timer.start()
        _, status, ru = os.wait4(proc.pid, 0)
        timer.cancel()
        proc.returncode = os.waitstatus_to_exitcode(status)
        fo.seek(0); out = fo.read()
        fe.seek(0); err = fe.read()
    wall = time.time() - t0
    s1 = steal_ticks()
    rec = {"lang": lang, "kernel": kernel, "variant": variant, "param": param, "reps": [], "lat": [], "meta": {},
           "returncode": proc.returncode, "wall": wall, "steal_ticks": s1 - s0, "stderr": err.decode(errors="replace")[-2000:],
           "maxrss_kb": ru.ru_maxrss, "utime": ru.ru_utime, "stime": ru.ru_stime, "minflt": ru.ru_minflt,
           "nvcsw": ru.ru_nvcsw, "nivcsw": ru.ru_nivcsw}
    for line in out.decode(errors="replace").splitlines():
        f = line.strip().split(";")
        if f[0] == "RESULT" and len(f) >= 7:
            ok = check(kernel if kernel != "fp" else "fp", param, f[6]) if kernel != "fp" else True
            rec["reps"].append({"rep": int(f[4]), "sec": float(f[5]), "chk": f[6], "ok": ok})
        elif f[0] == "LAT" and len(f) >= 7:
            rec["lat"].append([int(float(x)) for x in f[2:7]])
        elif f[0] == "META" and len(f) >= 3:
            rec["meta"][f[1]] = ";".join(f[2:])
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lang")
    ap.add_argument("--kernels", default=",".join(PLAN.keys()))
    ap.add_argument("--variants", default="")
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--reps", type=int, default=0, help="0 = adaptatif")
    ap.add_argument("--warmup", type=int, default=int(os.environ.get("WARMUP", "1")))
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", default="")
    ap.add_argument("--quick", action="store_true", help="1 processus, 1 répétition (validation)")
    ap.add_argument("--params", default="", help="ne garder que ces paramètres (ex. q1, 16384)")
    ap.add_argument("--tag", default="", help="étiquette enregistrée dans chaque mesure (ex. complement)")
    ap.add_argument("--pass", dest="pass_", type=int, default=-1,
                    help="campagne : n'exécute que le processus d'indice PASS (les passes sont lancées à des moments "
                         "différents, dans un ordre aléatoire) ; le nombre de répétitions est figé par results/calib.json")
    a = ap.parse_args()
    calib_path = os.path.join(ROOT, "results", "calib.json")
    calib = json.load(open(calib_path)) if os.path.exists(calib_path) else {}
    outdir = os.path.join(ROOT, "results", "raw")
    os.makedirs(outdir, exist_ok=True)
    out = open(a.out or os.path.join(outdir, f"{a.lang}.jsonl"), "a")
    vfilter = set(a.variants.split(",")) if a.variants else None
    # variantes facultatives propres à un langage : fichier bench/<lang>/extra_variants ("k8 tuned_alloc")
    extra = {}
    ef = os.path.join(ROOT, "bench", a.lang, "extra_variants")
    if os.path.exists(ef):
        for line in open(ef):
            f = line.split()
            if len(f) >= 2:
                extra.setdefault(f[0], []).append((f[1], f[2] if len(f) > 2 else ""))
    for kernel in a.kernels.split(","):
        for variant, param in PLAN[kernel] + extra.get(kernel, []):
            if vfilter and variant not in vfilter:
                continue
            if a.params and param not in a.params.split(","):
                continue
            procs = 1 if a.quick or kernel == "fp" else a.procs
            reps = 1 if a.quick or kernel == "fp" else a.reps
            key = f"{a.lang}|{kernel}|{variant}|{param}"
            if reps == 0 and key in calib:  # répétitions figées par la première passe
                reps, procs = calib[key]["reps"], min(procs, calib[key]["procs"])
            elif reps == 0:  # calibration : 1 répétition pour estimer la durée
                cal = run_one(a.lang, kernel, variant, param, 1, a.warmup, a.timeout)
                t = cal["reps"][0]["sec"] if cal.get("reps") else 10.0
                reps = max(3, min(10, int(3.0 / max(t, 1e-6))))
                if t > 5.0:  # mesures très longues (langages interprétés) : 2 processus x 2 répétitions
                    reps, procs = 2, min(procs, 2)
                calib = json.load(open(calib_path)) if os.path.exists(calib_path) else {}
                calib[key] = {"reps": reps, "procs": procs, "t_cal": t}
                with open(calib_path + ".tmp", "w") as cf:
                    json.dump(calib, cf, indent=0, sort_keys=True)
                os.replace(calib_path + ".tmp", calib_path)
            passes = range(procs) if a.pass_ < 0 else ([a.pass_] if a.pass_ < procs else [])
            for p in passes:
                # steal de l'hyperviseur > 2 % du temps CPU disponible : mesure refaite (2 fois au plus)
                for attempt in range(3):
                    rec = run_one(a.lang, kernel, variant, param, reps, a.warmup, a.timeout)
                    steal_frac = rec["steal_ticks"] / max(1e-9, rec["wall"] * CLK_TCK * NCPU)
                    rec["steal_frac"] = steal_frac
                    rec["attempt"] = attempt
                    if steal_frac <= 0.02 or a.quick:
                        break
                rec["proc"] = p
                rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                if a.tag:
                    rec["tag"] = a.tag
                out.write(json.dumps(rec) + "\n")
                out.flush()
                secs = [r["sec"] for r in rec.get("reps", [])]
                oks = {r["ok"] for r in rec.get("reps", [])}
                med = sorted(secs)[len(secs) // 2] if secs else float("nan")
                print(f"{a.lang:10s} {kernel:4s} {variant:20s} {param:10s} p{p} n={len(secs)} med={med:.6f}s ok={oks} rc={rec.get('returncode')} {rec.get('error','')}"
                      + (f" ERR:{rec['stderr'][-300:]}" if rec.get("returncode") not in (0, None) else ""), flush=True)


if __name__ == "__main__":
    main()
