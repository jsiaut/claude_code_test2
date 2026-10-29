#!/usr/bin/env python3
"""Compteurs du noyau et contrôle du bruit (plan : docs/INSTRUMENTS_V3.md, poussé avant ces mesures).

Sous-commandes :
  count : passe de comptage (appels système, défauts de page, changements de contexte, migrations, temps CPU),
          méthode des deux points, 7 mesures, toutes les implémentations -> results/raw_v3/instruments_count.jsonl
  alloc : uprobes sur malloc, calloc, realloc et free de la libc, mêmes deux points
          -> results/raw_v3/instruments_alloc.jsonl
  noise : pilote de contrôle du bruit, protocoles A, B et C -> results/raw_v3/noise_pilot.jsonl
Prérequis : /opt/pecount (tools/pecount.c), tracefs monté sur /sys/kernel/tracing, root."""
import json, os, random, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import driver  # noqa: E402

OUT = os.path.join(ROOT, "results", "raw_v3")
LOG = os.path.join(ROOT, "results", "campaign.log")
PECOUNT = "/opt/pecount"
LIBC = "/lib/x86_64-linux-gnu/libc.so.6"
RANKED = ["ada", "c", "c3", "chapel", "cpp", "csharp", "d", "fortran", "go", "haskell", "java", "js", "julia", "lua",
          "mojo", "nim", "ocaml", "odin", "python", "rust", "zig"]
ANNEX = ["c_gcc", "fortran_flang", "js_bun", "luajit"]
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}
CELLS = [("k1", "natural", "energy"), ("k3", "sw_padded", ""), ("k6", "natural", "q1"), ("k7", "natural", ""),
         ("k8", "natural", ""), ("k8", "tuned", ""), ("k9", "natural", "")]
ALLOC_CELLS = [("k1", "natural", "energy"), ("k6", "natural", "q1"), ("k7", "natural", ""), ("k8", "tuned", ""),
               ("k9", "natural", "")]
EXCLUDED = {("haskell", "k7", "natural", "")}
SYSCALLS = ["futex", "mmap", "munmap", "madvise", "brk", "mprotect", "mremap", "clone", "clone3", "sched_yield",
            "nanosleep", "clock_nanosleep", "read", "write", "openat", "ioctl", "epoll_wait", "membarrier",
            "rt_sigprocmask", "getrusage"]
CALIB = json.load(open(os.path.join(ROOT, "results", "calib.json")))


def log(msg):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + msg + "\n")


def libc_offsets():
    out = subprocess.run(["readelf", "-Ws", LIBC], capture_output=True, text=True).stdout
    offs = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[7] in ("malloc@@GLIBC_2.2.5", "calloc@@GLIBC_2.2.5", "realloc@@GLIBC_2.2.5",
                                    "free@@GLIBC_2.2.5"):
            offs[f[7].split("@")[0]] = "0x" + f[1]
    return offs


def two_points(lang, key):
    """R1 et R2 de la méthode des deux points, d'après le temps par répétition de la calibration."""
    k, v, p = key
    t = CALIB.get(f"{lang}|{k}|{v}|{p}", {}).get("t_cal", 1.0)
    if t > 10:
        return 1, 2, t
    d = max(2, min(30, round(1.0 / max(t, 1e-6))))
    r1 = max(1, d // 2)
    return r1, r1 + d, t


def run_counted(lang, key, reps, warmup, extra, timeout, prefix=(), env_extra=None):
    k, v, p = key
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        jpath = tf.name
    cmd = list(prefix) + [PECOUNT, "-o", jpath] + extra + ["--", os.path.join(ROOT, "bench", lang, "run"), k, v,
                                                            str(reps)] + ([p] if p else [])
    env = dict(os.environ, WARMUP=str(warmup), MS_DATA=os.environ.get("MS_DATA", "/opt/msdata"))
    env.update(env_extra or {})
    t0 = time.time()
    try:
        pr = subprocess.run(cmd, cwd=os.path.join(ROOT, "bench", lang), env=env, capture_output=True, text=True,
                            timeout=timeout)
        out, rc, timed_out = pr.stdout, pr.returncode, False
    except subprocess.TimeoutExpired as e:
        out, rc, timed_out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), -1, True
        subprocess.run(["pkill", "-f", f"bench/{lang}/"], capture_output=True)
    wall = time.time() - t0
    try:
        counts = json.load(open(jpath))
    except (OSError, ValueError):
        counts = {"rc": rc, "counts": {}}
    os.unlink(jpath)
    reps_out = []
    for line in out.splitlines():
        f = line.strip().split(";")
        if f[0] == "RESULT" and len(f) >= 7:
            reps_out.append({"rep": int(f[4]), "sec": float(f[5]), "ok": driver.check(k, p, f[6])})
    return {"lang": lang, "kernel": k, "variant": v, "param": p, "reps_asked": reps, "warmup": warmup,
            "rc": counts.get("rc", rc), "timed_out": timed_out, "wall": wall, "counts": counts.get("counts", {}),
            "reps": reps_out}


def campaign(name, cells, extra, timeout):
    out = os.path.join(OUT, f"instruments_{name}.jsonl")
    jobs = []
    for lang in RANKED + ANNEX:
        for key in cells:
            if (lang,) + key in EXCLUDED or f"{lang}|{key[0]}|{key[1]}|{key[2]}" not in CALIB:
                continue
            r1, r2, t = two_points(lang, key)
            for r in (r1, r2):
                jobs.append((lang, key, r, r1, r2))
    random.Random(20261029 + 400 + len(name)).shuffle(jobs)
    for i, (lang, key, r, r1, r2) in enumerate(jobs):
        warm = 3 if lang in JIT else 1
        if r2 - r1 == 1:  # mesure lente : échauffement réduit à 1
            warm = 1
        rec = run_counted(lang, key, r, warm, extra, timeout)
        rec.update({"r1": r1, "r2": r2, "tag": f"v3_instr_{name}"})
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        log(f"v3 : instruments {name}, {i + 1}/{len(jobs)} {lang} {':'.join(key)} R={r} {rec['wall']:.0f}s"
            + (" DÉPASSEMENT" if rec["timed_out"] else ""))


def read_psi():
    d = {}
    for res in ("cpu", "memory", "io"):
        try:
            for line in open(f"/proc/pressure/{res}"):
                f = line.split()
                d[f"{res}_{f[0]}"] = int(f[4].split("=")[1])
        except OSError:
            pass
    return d


def read_steal():
    d = {}
    for line in open("/proc/stat"):
        if line.startswith("cpu"):
            f = line.split()
            d[f[0]] = int(f[8])
    return d


def irq_affinity(target):
    """Déplace les interruptions déplaçables vers `target` ; renvoie l'état d'origine pour le restaurer."""
    saved = {}
    for irq in os.listdir("/proc/irq"):
        path = f"/proc/irq/{irq}/smp_affinity_list"
        if not os.path.exists(path):
            continue
        try:
            saved[path] = open(path).read().strip()
            with open(path, "w") as f:
                f.write(target)
        except OSError:
            pass
    return saved


def noise():
    out = os.path.join(OUT, "noise_pilot.jsonl")
    combos = [("c", ("k5", "tuned", "")), ("rust", ("k5", "tuned", "")), ("c", ("k2", "tuned", "8388608")),
              ("rust", ("k2", "tuned", "8388608")), ("c", ("k1", "soa", "energy"))]
    jobs = [(lang, key, proto, i) for lang, key in combos for proto in "ABC" for i in range(12)]
    rnd = random.Random(20261029 + 500)
    rnd.shuffle(jobs)
    os.sched_setaffinity(0, {0, 1, 2})
    saved = irq_affinity("0-2")
    moved = sum(1 for p in saved if open(p).read().strip() == "0-2")
    log(f"v3 : pilote du bruit, interruptions déplacées vers les CPU 0 à 2 : {moved} sur {len(saved)}")
    try:
        for n, (lang, key, proto, i) in enumerate(jobs):
            c = CALIB[f"{lang}|{key[0]}|{key[1]}|{key[2]}"]
            prefix = () if proto == "A" else ("taskset", "-c", "3", "chrt", "-f", "50")
            env_extra = {"MS_PAD": "x" * rnd.randrange(4096)} if proto == "C" else None
            p0, s0 = read_psi(), read_steal()
            rec = run_counted(lang, key, c["reps"], 1, [], 600, prefix=prefix, env_extra=env_extra)
            p1, s1 = read_psi(), read_steal()
            rec.update({"tag": "v3_noise", "protocol": proto, "index": i,
                        "psi_delta_us": {k: p1[k] - p0.get(k, 0) for k in p1},
                        "steal_delta_ticks": {k: s1[k] - s0.get(k, 0) for k in s1},
                        "pad": len(env_extra["MS_PAD"]) if env_extra else 0})
            with open(out, "a") as f:
                f.write(json.dumps(rec) + "\n")
            log(f"v3 : pilote du bruit, {n + 1}/{len(jobs)} {lang} {':'.join(key)} {proto} {rec['wall']:.1f}s")
    finally:
        for path, val in saved.items():
            try:
                with open(path, "w") as f:
                    f.write(val)
            except OSError:
                pass
        log("v3 : pilote du bruit, affinité des interruptions restaurée")


def main():
    if not os.path.ismount("/sys/kernel/tracing"):
        subprocess.run(["mount", "-t", "tracefs", "nodev", "/sys/kernel/tracing"], check=True)
    cmd = sys.argv[1]
    if cmd == "count":
        extra = []
        for s in SYSCALLS:
            extra += ["-t", f"syscalls/sys_enter_{s}"]
        campaign("count", CELLS, extra, 900)
    elif cmd == "alloc":
        offs = libc_offsets()
        extra = []
        for fn in ("malloc", "calloc", "realloc", "free"):
            extra += ["-u", f"{fn}={LIBC}:{offs[fn]}"]
        campaign("alloc", ALLOC_CELLS, extra, 120)
    elif cmd == "noise":
        noise()
    print(f"{cmd} terminé", flush=True)


if __name__ == "__main__":
    main()
