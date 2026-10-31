#!/usr/bin/env python3
"""Remarque sur Rust (docs/RUST.md, section 2) : latences de K8 naturel par processus dans la campagne principale
(machine 1, results/raw) et dans la réplication de la machine 3 (results/raw_v2, étiquette v2_m3), vol de temps de
chaque processus, corrélation de rang entre le vol et la queue. Écrit sur la sortie standard."""
import glob, json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MALLOC = ["c", "c_gcc", "cpp", "rust", "zig", "nim", "ada", "fortran", "odin", "c3"]


def rank(x):
    x = np.asarray(x, float)
    r = np.empty(len(x))
    r[np.argsort(x, kind="mergesort")] = np.arange(len(x))
    for v in np.unique(x):
        m = x == v
        if m.sum() > 1:
            r[m] = r[m].mean()
    return r


def rho(a, b):
    return float(np.corrcoef(rank(a), rank(b))[0, 1])


def procs(pattern, tag=None):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, pattern))):
        for line in open(f):
            r = json.loads(line)
            if (r["kernel"], r["variant"], r["param"]) != ("k8", "natural", "") or not r.get("lat"):
                continue
            if tag is not None and r.get("tag") != tag:
                continue
            lat = np.array(r["lat"], float) / 1e3
            out.append((r["lang"], r.get("proc"), r.get("steal_frac") or 0.0, lat))
    return out


main = procs("results/raw/*.jsonl")
print("Campagne principale (machine 1, Cascade Lake), K8 naturel : un processus par ligne (médianes sur ses répétitions)")
print("langage        proc  vol (% de 4 vCPU)  p50 (µs)  p99,9 (µs)  max (µs)")
for l, p, s, lat in sorted(main, key=lambda t: (t[0], t[1])):
    if l in MALLOC:
        print(f"{l:14s} {p:4d}  {100 * s:16.2f}  {np.median(lat[:, 0]):8.1f}  {np.median(lat[:, 3]):10.1f}  {np.median(lat[:, 4]):8.0f}")
print()
print("Médianes sur toutes les répétitions (estimateur de D3, analyze_v2.lat_rows) :")
for l in ["rust", "c"]:
    allr = np.vstack([lat for ll, _, _, lat in main if ll == l])
    print(f"  {l:5s} {len(allr)} répétitions : p50 {np.median(allr[:, 0]):.1f} µs, p99,9 {np.median(allr[:, 3]):.1f} µs, max {np.median(allr[:, 4]):.0f} µs")
print()
for name, langs in (("10 langages qui passent par malloc", MALLOC), ("sans Odin ni C3", [l for l in MALLOC if l not in ("odin", "c3")]),
                    ("tous les processus", sorted({t[0] for t in main}))):
    s = [t for t in main if t[0] in langs]
    a = [t[2] for t in s]
    print(f"rho(vol, p99,9) = {rho(a, [np.median(t[3][:, 3]) for t in s]):.2f} ; rho(vol, max) = "
          f"{rho(a, [np.median(t[3][:, 4]) for t in s]):.2f} ; {len(s)} processus ({name})")
top = sorted((t for t in main if t[0] in MALLOC), key=lambda t: -t[2])[:3]
print("vols les plus élevés (langages malloc) :", ", ".join(f"{l} p{p} {100 * s:.2f} %" for l, p, s, _ in top))
top = sorted(main, key=lambda t: -t[2])[:3]
print("vols les plus élevés (tous) :", ", ".join(f"{l} p{p} {100 * s:.2f} %" for l, p, s, _ in top))
print()
print("Réplication de la machine 3 (Emerald Rapids, results/raw_v2, v2_m3), un processus par langage :")
for l, p, s, lat in sorted(procs("results/raw_v2/*.jsonl", "v2_m3"), key=lambda t: t[0]):
    if l in MALLOC:
        print(f"  {l:8s} vol {100 * s:.2f} % ; p50 {np.median(lat[:, 0]):.1f} ; p99,9 {np.median(lat[:, 3]):.1f} ; max {np.median(lat[:, 4]):.0f} µs")
