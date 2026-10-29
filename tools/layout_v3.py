#!/usr/bin/env python3
"""Expérience de disposition du code (plan : docs/ANALYSIS_V3.md, section 6), sur la machine actuelle.

Pour C (clang), C (gcc) et Rust, huit dispositions du même code : sections par fonction et éditeur de liens lld avec
--randomize-section-padding=<graine>, graines 1 à 8. Pour chaque disposition, deux processus par mesure de K1 à K9
(répétitions de la campagne, results/calib.json), dans un ordre tiré au hasard (graine fixe). K10 est exclu.
Sortie : results/raw_v3/layout_<implémentation>.jsonl, étiquette v3_layout, champ meta.layout_seed.
Usage : layout_v3.py build | run"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_v3")
SEEDS = range(1, 9)
IMPLS = ["c", "c_gcc", "rust"]
KERNELS = ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9"]
GCC = "/opt/gcc-16/bin/gcc-16"


def build_cmd(impl, seed, out):
    lay = ["-ffunction-sections", "-fuse-ld=lld", f"-Wl,--randomize-section-padding={seed}"]
    if impl == "c":
        return ["clang-23", "-std=c23", "-O3", "-march=native", "-Wall", "-Wextra", "-pthread"] + lay + ["-o", out, "bench/c/ms.c"]
    if impl == "c_gcc":
        return [GCC, "-std=c23", "-O3", "-march=native", "-pthread"] + lay + ["-o", out, "bench/c/ms.c"]
    return ["rustc", "--edition", "2024", "-C", "opt-level=3", "-C", "target-cpu=native", "-C", "codegen-units=1",
            "-C", "link-arg=-fuse-ld=lld", "-C", f"link-arg=-Wl,--randomize-section-padding={seed}", "-o", out, "bench/rust/ms.rs"]


def binary(impl, seed):
    return os.path.join(ROOT, "bench", impl, "layout", f"ms_{seed}")


def build():
    for impl in IMPLS:
        os.makedirs(os.path.join(ROOT, "bench", impl, "layout"), exist_ok=True)
        for s in SEEDS:
            r = subprocess.run(build_cmd(impl, s, binary(impl, s)), cwd=ROOT, capture_output=True, text=True)
            print(impl, s, "rc", r.returncode, r.stderr.strip()[-200:] if r.returncode else "", flush=True)
            if r.returncode:
                sys.exit(1)


def run():
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    jobs = [(impl, s, p) for impl in IMPLS for s in SEEDS for p in range(2)]
    random.Random(20261029 + 300).shuffle(jobs)
    for i, (impl, s, p) in enumerate(jobs):
        t0 = time.time()
        env = dict(os.environ, MS_BIN=binary(impl, s))
        out = os.path.join(OUT, f"layout_{impl}.jsonl")
        with open(os.path.join(OUT, f"layout_{impl}.log"), "a") as lf:
            subprocess.run([sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", ",".join(KERNELS),
                            "--procs", "1", "--pass", "0", "--warmup", "1", "--tag", "v3_layout", "--out", out],
                           stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, env=env)
        # la graine de disposition est ajoutée aux enregistrements écrits par ce processus du pilote
        recs = [json.loads(l) for l in open(out)]
        for r in recs:
            if r.get("tag") == "v3_layout" and "layout_seed" not in r.get("meta", {}):
                r.setdefault("meta", {})["layout_seed"] = s
                r["layout_proc"] = p
        with open(out + ".tmp", "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in recs))
        os.replace(out + ".tmp", out)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"v3 : disposition, {i + 1}/{len(jobs)} {impl} graine {s} {time.time() - t0:.0f}s\n")
        log.flush()
    print("disposition terminée", flush=True)


if __name__ == "__main__":
    {"build": build, "run": run}[sys.argv[1]]()
