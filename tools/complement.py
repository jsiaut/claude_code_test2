#!/usr/bin/env python3
"""Passe complémentaire (écart consigné dans docs/METHODOLOGY.md).

Après les 3 passes, toute mesure dont le coefficient de variation entre processus dépasse 10 % reçoit
6 processus supplémentaires. Ils sont exécutés en 6 tours, et à chaque tour les mesures concernées
passent dans un ordre tiré au hasard (graine fixe). La règle s'applique à tous les langages de la même
façon et réduit l'incertitude là où le phénomène mesuré est instable (placement des threads, GC).
Les mesures invalides et l'empreinte (fp) sont exclues.
"""
import glob, json, os, random, statistics, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JIT = {"java", "csharp", "js", "js_bun", "julia", "luajit"}
CV_MAX, EXTRA = 0.10, 6


def candidates():
    procs = {}
    for f in glob.glob(os.path.join(ROOT, "results", "raw", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r["kernel"] == "fp" or not r.get("reps") or any(x["ok"] is not True for x in r["reps"]):
                continue
            procs.setdefault((r["lang"], r["kernel"], r["variant"], r["param"]), []).append(
                statistics.median(x["sec"] for x in r["reps"]))
    out = []
    for k, ms in procs.items():
        if len(ms) >= 2:
            cv = statistics.pstdev(ms) / statistics.mean(ms)
            if cv > CV_MAX:
                out.append((k, cv, len(ms)))
    return out


def main():
    cands = candidates()
    print(f"{len(cands)} mesures avec CV > {CV_MAX:.0%}")
    for (l, k, v, p), cv, n in sorted(cands, key=lambda c: -c[1]):
        print(f"  {l:14s} {k:4s} {v:20s} {p:10s} CV={cv:.0%} n={n}")
    if "--dry" in sys.argv:
        return
    for rnd in range(EXTRA):
        order = list(cands)
        random.Random(1000 + rnd).shuffle(order)
        for (l, k, v, p), cv, n in order:
            with open(os.path.join(ROOT, "results", "log", f"{l}.log"), "a") as lf:
                subprocess.run([sys.executable, os.path.join(ROOT, "tools", "driver.py"), l, "--kernels", k, "--variants", v,
                                "--params", p, "--procs", "1", "--warmup", "3" if l in JIT else "1", "--tag", "complement",
                                "--out", os.path.join(ROOT, "results", "raw", f"{l}.jsonl")],
                               stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
        with open(os.path.join(ROOT, "results", "campaign.log"), "a") as f:
            f.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"complément : tour {rnd + 1}/{EXTRA} terminé ({len(order)} mesures)\n")


if __name__ == "__main__":
    main()
