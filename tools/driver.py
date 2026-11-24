#!/usr/bin/env python3
"""Validation rapide d'une implémentation, à la taille publiée, et définitions communes au pilote de la campagne.

Usage : driver.py LANG [--kernels k1,k4] [--variants natural,tuned] [--params q1,16384] [--warmup N] [--timeout S]

Construire d'abord sur place (bench/<langage>/build.sh). Pour chaque cellule (noyau, variante, paramètre) du langage,
celles du plan commun (PLAN), ses variantes propres (bench/<langage>/extra_variants) et ses formes du catalogue
(cv_variants), un processus exécute
l'échauffement puis une répétition ; le programme chronomètre lui-même sa section de calcul (docs/SPEC.md, 0) et sa
somme de contrôle est comparée à results/expected.json, calculé par l'implémentation C. Une ligne par cellule ; code
de retour 1 si une cellule échoue. Rien n'est écrit dans le dépôt. K10 (hors score, plus mesuré) et l'empreinte de K1
(fp) ne sont exécutés que sur demande (--kernels k10,fp).

Le pilote de la campagne (tools/final/campaign.py) et l'analyse (analysis/final_v4.py) reprennent d'ici PLAN, les
variantes communes à tous les langages, check, les sommes de contrôle de la taille publiée, et le relevé du vol de
temps de l'hyperviseur. Les autres tailles : tools/sizes/validate.py.
"""
import argparse, json, os, subprocess, sys, tempfile, threading, time

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
    "fp": [("footprint", "energy"), ("footprint_raw", "energy"), ("footprint0", "energy")],
}
SCORED = ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9"]
TOL = {"k1": 1e-6, "k5": 1e-3, "k9": 1e-9}
CLK_TCK = os.sysconf("SC_CLK_TCK")
NCPU = os.cpu_count()


def steal_ticks():
    with open("/proc/stat") as f:
        parts = f.readline().split()
    return int(parts[8])  # cpu user nice system idle iowait irq softirq steal


def check(kernel, param, chk):
    """Somme de contrôle de la taille publiée : True ou False, None si aucune valeur n'est attendue."""
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


def extra_variants(lang, name="extra_variants"):
    """Variantes propres à un langage : bench/<langage>/extra_variants (« k8 tuned_alloc ») ; name="cv_variants" :
    ses formes du catalogue."""
    extra = {}
    ef = os.path.join(ROOT, "bench", lang, name)
    if os.path.exists(ef):
        for line in open(ef):
            f = line.split()
            if len(f) >= 2:
                extra.setdefault(f[0], []).append((f[1], f[2] if len(f) > 2 else ""))
    return extra


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
    rec = {"lang": lang, "kernel": kernel, "variant": variant, "param": param, "reps": [], "lat": [], "meta": {},
           "returncode": proc.returncode, "wall": wall, "steal_ticks": steal_ticks() - s0,
           "stderr": err.decode(errors="replace")[-2000:], "maxrss_kb": ru.ru_maxrss}
    for line in out.decode(errors="replace").splitlines():
        f = line.strip().split(";")
        if f[0] == "RESULT" and len(f) >= 7:
            ok = check(kernel, param, f[6]) if kernel != "fp" else True
            rec["reps"].append({"rep": int(f[4]), "sec": float(f[5]), "chk": f[6], "ok": ok})
        elif f[0] == "LAT" and len(f) >= 7:
            rec["lat"].append([int(float(x)) for x in f[2:7]])
        elif f[0] == "META" and len(f) >= 3:
            rec["meta"][f[1]] = ";".join(f[2:])
    return rec


def main():
    ap = argparse.ArgumentParser(description="Validation rapide d'une implémentation (un processus, une répétition).")
    ap.add_argument("lang")
    ap.add_argument("--kernels", default=",".join(SCORED))
    ap.add_argument("--variants", default="", help="ne garder que ces variantes")
    ap.add_argument("--params", default="", help="ne garder que ces paramètres (ex. q1, 16384)")
    ap.add_argument("--warmup", type=int, default=int(os.environ.get("WARMUP", "1")))
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    vfilter = set(a.variants.split(",")) if a.variants else None
    extra, cv = extra_variants(a.lang), extra_variants(a.lang, "cv_variants")
    bad = 0
    for kernel in a.kernels.split(","):
        for variant, param in PLAN[kernel] + extra.get(kernel, []) + cv.get(kernel, []):
            if vfilter and variant not in vfilter:
                continue
            if a.params and param not in a.params.split(","):
                continue
            rec = run_one(a.lang, kernel, variant, param, 1, a.warmup, a.timeout)
            secs = [r["sec"] for r in rec["reps"]]
            oks = {r["ok"] for r in rec["reps"]}
            good = rec["returncode"] == 0 and bool(secs) and oks <= {True}
            bad += not good
            med = sorted(secs)[len(secs) // 2] if secs else float("nan")
            print(f"{a.lang:10s} {kernel:4s} {variant:20s} {param:10s} n={len(secs)} t={med:.6f}s ok={sorted(map(str, oks))} "
                  f"rc={rec['returncode']} {'' if good else 'ÉCHEC'}"
                  + (f" ERR:{rec['stderr'][-300:]}" if rec["returncode"] != 0 else ""), flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
