#!/usr/bin/env python3
"""Remarque sur C++ (docs/CPP.md, section 2) : faits tirés des données de la campagne (results/raw, Cascade Lake), de la
réplication (results/raw_v2, étiquette v2_m3, Emerald Rapids), des queues de K8 remesurées (results/raw_d3) et du
classement publié (results/summary_v3.json). Sortie : results/cpp_check/data_facts.txt."""
import collections, glob, json, math, os, statistics

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = []


def med(r):
    return statistics.median(x["sec"] for x in r["reps"])


def load(pattern, tag=None):
    recs = collections.defaultdict(list)
    for f in glob.glob(os.path.join(ROOT, pattern)):
        for line in open(f):
            r = json.loads(line)
            if r.get("returncode") != 0 or (tag is not None and r.get("tag") != tag):
                continue
            recs[(r["lang"], r["kernel"], r["variant"], r["param"])].append(r)
    return recs


def gm(rs):
    return math.exp(sum(math.log(med(r)) for r in rs) / len(rs))


main = load("results/raw/*.jsonl")
m3 = load("results/raw_v2/*.jsonl", "v2_m3")
o = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))
R = o["results"]

L.append("# Composantes du score publié (results/summary_v3.json)")
for l in ("c", "c_gcc", "cpp"):
    r = R[l]
    L.append(f"{l}: score {r['MS']:.2f} ; contrôle {r['C_v2']:.1f} ; plafond {r['E']:.1f} ; défaut {r['D']:.1f} ; noyaux du plafond "
             + ", ".join(f"{k} {v:.3f}" for k, v in r["E_kernels"].items()) + " ; D " + ", ".join(f"{k} {v:.3f}" for k, v in r["D_parts"].items()))

L.append("\n# Temps par processus (ms, médiane des répétitions), données principales (Cascade Lake)")
for key in (("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", ""), ("k1", "natural", "energy"),
            ("k1", "natural_shuffled", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"), ("k2", "tuned", "8388608"),
            ("k8", "natural", ""), ("k8", "tuned", ""), ("k8", "tuned_alloc", ""), ("k6", "tuned", "q1"), ("k6", "mt", "q1"),
            ("k6", "tuned", "q6"), ("k6", "natural", "q1"), ("k7", "natural", ""), ("k7", "tuned", "")):
    row = []
    for l in ("c", "c_gcc", "cpp"):
        rs = main.get((l,) + key, [])
        if rs:
            row.append(f"{l} {sorted(round(1e3 * med(r), 2) for r in rs)} (moy. géom. {1e3 * gm(rs):.2f})")
    L.append(f"{':'.join(x for x in key if x)} : " + " | ".join(row))

L.append("\n# K9 : temps (ms, médiane des processus) et défauts de page mineurs par processus (médiane)")
for label, recs in (("données principales (Cascade Lake)", main), ("réplication (Emerald Rapids, machine 3)", m3)):
    L.append(f"## {label}")
    for l in ("c", "c_gcc", "chapel", "ada", "cpp", "zig", "odin", "c3", "rust", "nim", "d", "julia", "csharp", "fortran", "mojo",
              "go", "java"):
        parts = []
        for v in ("natural", "tuned", "mt"):
            rs = recs.get((l, "k9", v, ""), [])
            if rs:
                parts.append(f"{v} {1e3 * statistics.median(med(r) for r in rs):.2f} ms ({statistics.median(r['minflt'] for r in rs):.0f})")
        if parts:
            L.append(f"{l:8s} " + " ; ".join(parts))

L.append("\n# Queue de latence de K8 naturel (remesure, results/raw_d3) : p99,9 par processus et médianes regroupées")
d3 = collections.defaultdict(list)
for f in glob.glob(os.path.join(ROOT, "results", "raw_d3", "*.jsonl")):
    for line in open(f):
        r = json.loads(line)
        if r["kernel"] == "k8" and r["variant"] == "natural":
            d3[r["lang"]].append(np.asarray(r["lat"], float))
for l in ("c", "c_gcc", "cpp"):
    arrs = d3[l]
    per = sorted(round(float(np.median(a[:, 3])) / 1e3) for a in arrs)
    allr = np.vstack(arrs)
    m = np.median(allr[:, [0, 3, 4]], axis=0) / 1e3
    worst = max(range(len(arrs)), key=lambda j: np.median(arrs[j][:, 3]))
    m2 = np.median(np.vstack([a for j, a in enumerate(arrs) if j != worst])[:, [0, 3, 4]], axis=0) / 1e3
    L.append(f"{l:6s} p99,9 par processus (µs) {per} ; regroupé : p50 {m[0]:.1f}, p99,9 {m[1]:.0f}, max {m[2]:.0f} µs ; "
             f"sans le processus au p99,9 le plus haut : p99,9 {m2[1]:.0f}, max {m2[2]:.0f} µs")

L.append("\n# « Ce qui est juste » : code naturel (ms, médiane des processus, Cascade Lake)")
for key in (("k1", "natural", "energy"), ("k6", "natural", "q1"), ("k9", "natural", "")):
    row = []
    for l in ("cpp", "c", "rust", "d"):
        rs = main.get((l,) + key, [])
        if rs:
            row.append(f"{l} {1e3 * statistics.median(med(r) for r in rs):.2f}")
    L.append(f"{':'.join(x for x in key if x)} : " + ", ".join(row))
for l in ("cpp", "c"):
    n, t = main[(l, "k7", "natural", "")], main[(l, "k7", "tuned", "")]
    L.append(f"K7 {l} : naturel {gm(n):.2f} s, table plate {gm(t) * 1e3:.0f} ms, rapport {gm(n) / gm(t):.1f}")

L.append("\n# Décomposition de l'écart de score (points ; contrôle et défauts : linéaire ; plafond : réparti par noyau au "
         "prorata des écarts de log, E étant la moyenne géométrique des 8 noyaux)")
W, DW = {"C": 0.35, "E": 0.40, "D": 0.25}, {"D1": 0.5, "D2": 0.15, "D3": 0.15, "D4": 0.2}


def decomp(a, b):
    A, B = R[a], R[b]
    out = {"total": A["MS"] - B["MS"], "contrôle": W["C"] * (A["C_v2"] - B["C_v2"])}
    lg = {k: math.log(A["E_kernels"][k] / B["E_kernels"][k]) / 8 for k in A["E_kernels"]}
    dE = W["E"] * (A["E"] - B["E"])
    for k, v in lg.items():
        out["E " + k] = dE * v / sum(lg.values())
    for k in DW:
        out[k] = W["D"] * 100 * DW[k] * (A["D_parts"][k] - B["D_parts"][k])
    return out


for a in ("c", "c_gcc"):
    L.append(f"{a} − cpp : " + " ; ".join(f"{k} {v:+.2f}" for k, v in decomp(a, "cpp").items()))
A = R["cpp"]
ek = dict(A["E_kernels"], k4=1.0)
e4 = 100 * math.exp(sum(math.log(v) for v in ek.values()) / 8)
L.append(f"C++ avec le score K4 de C (1,0) : plafond {e4:.1f}, score {W['C'] * A['C_v2'] + W['E'] * e4 + W['D'] * A['D']:.2f}")
k7c, k7p = gm(main[("c", "k7", "natural", "")]), gm(main[("cpp", "k7", "natural", "")])
d1 = A["D_parts"]["D1"] * math.exp(math.log(k7p / k7c) / 7)  # D1 : moyenne géométrique sur 7 noyaux
L.append(f"C++ avec le K7 naturel de C ({k7c:.2f} s au lieu de {k7p:.2f} s) : D1 {A['D_parts']['D1']:.3f} -> {d1:.3f}, "
         f"{W['D'] * 100 * DW['D1'] * (d1 - A['D_parts']['D1']):+.2f} point")

L.append("\n# Clés de D2 et D4 (K1 naturel et mélangé, K2 à trois tailles), données principales : processus par cellule et "
         "écart maximal entre processus d'une même cellule (rapport des médianes extrêmes)")
D24 = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k2", "tuned", "16384"), ("k2", "tuned", "262144"),
       ("k2", "tuned", "8388608")]
for l in sorted({k[0] for k in main if (k[1], k[2], k[3]) in D24}):
    cells = [(key, main[(l,) + key]) for key in D24 if main.get((l,) + key)]
    worst = max(cells, key=lambda c: max(med(r) for r in c[1]) / min(med(r) for r in c[1]))
    w = max(med(r) for r in worst[1]) / min(med(r) for r in worst[1])
    L.append(f"{l:14s} processus {[len(c[1]) for c in cells]} ; écart maximal {w:.2f} ({':'.join(x for x in worst[0] if x)})")

out = os.path.join(ROOT, "results", "cpp_check", "data_facts.txt")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write("\n".join(L) + "\n")
print("\n".join(L))
