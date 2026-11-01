#!/usr/bin/env python3
"""Remarque sur Odin (docs/ODIN.md, section 2) : chiffres tirés des données principales publiées (temps en moyenne
géométrique des médianes de processus). Sortie : results/odin_check/data_facts.txt."""
import math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import analyze_v2 as v2  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402

gm = lambda p: 1e3 * math.exp(proc_logs(p).mean())  # noqa: E731
d, *_ = v2.dataset_main(transfers=True)
TOP13 = ["c", "cpp", "odin", "zig", "c3", "nim", "rust", "d", "ada", "chapel", "fortran", "julia", "mojo"]
L = []
for k in (("k6", "tuned", "q1"), ("k6", "mt", "q1")):
    L.append(f"{':'.join(k)} : " + ", ".join(f"{l} {gm(d[l][k]):.1f} ms" for l in ("odin", "c", "zig", "c3", "cpp", "rust")))
rows = sorted((gm(d[l][("k7", "natural", "")]), l, gm(d[l][("k7", "tuned", "")])) for l in TOP13)
L.append("K7 naturel, 13 premiers (s ; rapport à leur table optimisée) : " +
         ", ".join(f"{i}. {l} {n / 1e3:.2f} ({n / t:.1f})" for i, (n, l, t) in enumerate(rows, 1)))
rows = sorted((gm(d[l][("k8", "natural", "")]), l) for l in TOP13)
L.append("K8 naturel, 13 premiers (s) : " + ", ".join(f"{l} {t / 1e3:.2f}" for t, l in rows))
open(os.path.join(ROOT, "results", "odin_check", "data_facts.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
