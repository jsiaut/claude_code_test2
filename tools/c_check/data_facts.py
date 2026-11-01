#!/usr/bin/env python3
"""Remarque sur C (docs/C.md, section 2) : faits tirés du classement publié (results/summary_v3.json,
results/cpp_check.json), de la confrontation recalculée (results/confrontation_current.json) et des données
principales (results/raw, Cascade Lake). Sortie : results/c_check/data_facts.txt."""
import collections, glob, json, math, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = []
S = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))
R = S["results"]
P = json.load(open(os.path.join(ROOT, "results", "cpp_check.json")))["scenarios"]["Publié"]

L.append("# Place publiée de C (results/summary_v3.json, results/cpp_check.json « Publié »)")
r = R["c"]
L.append(f"score {r['MS']:.2f} ; ensemble de rangs simultané {r['rank_set']} ; rang dans 90 % des variantes "
         f"{r['ua_rank_90']} ; groupe {r['tier']} (avec {', '.join(sorted(l for l in S['tiers'][0] if l != 'c'))}) ; "
         f"1er dans {100 * P['first']['c']:.1f} % des variantes ; devant Odin dans {100 * (1 - P['prec_cpp']['odin']) if False else 0:.0f}")
L[-1] = L[-1].rsplit(" ; devant Odin", 1)[0]
L.append(f"rang espéré : C {P['exp21']['c']:.2f}, Odin {P['exp21']['odin']:.2f}, C++ {P['exp21']['cpp']:.2f} ; "
         f"C++ devant C dans {100 * P['prec_cpp']['c']:.0f} % des variantes")
L.append(f"annexe C par gcc : {R['c_gcc']['MS']:.2f} points (données principales), {R['c_gcc']['MS_m3']:.2f} sur la machine 3, "
         f"où C++ est 1er des langages classés ({R['cpp']['MS_m3']:.2f}) et C 2e ({R['c']['MS_m3']:.2f})")

L.append("\n# Pilier contrôle selon la règle (C et les cinq premiers en règle v1)")
v1 = sorted(((R[l]["C_v1"], l) for l in R if R[l].get("rank_main")), reverse=True)
L.append("règle v1 : " + ", ".join(f"{l} {v:.1f}" for v, l in v1[:6]) + f" ; C : v2 {r['C_v2']:.1f}, v1 {r['C_v1']:.1f}")
cf = json.load(open(os.path.join(ROOT, "results", "confrontation_current.json")))["scenarios"]
for n in ("B", "C"):
    z = cf[n]
    order = z.get("order18") or z.get("order21")
    L.append(f"confrontation, scénario {n} : ordre {', '.join(order[:6])} ; contrôle de C {z['C']['c']:.1f}, score de C "
             f"{z['ms0']['c']:.1f}")

L.append("\n# K9 dans les données principales (Cascade Lake) : C++ (g++) contre C par gcc, même boucle k9_rows "
         "(results/c_check/k9_code.txt) ; seul le harnais diffère (grilles réallouées, fils std::jthread contre pthread)")
d = collections.defaultdict(list)
for f in glob.glob(os.path.join(ROOT, "results", "raw", "*.jsonl")):
    for line in open(f):
        x = json.loads(line)
        if x.get("returncode") == 0 and x["kernel"] == "k9" and x["lang"] in ("cpp", "c_gcc", "c"):
            d[(x["lang"], x["variant"])].append(statistics.median(y["sec"] for y in x["reps"]))
gm = lambda v: math.exp(sum(math.log(t) for t in v) / len(v))  # noqa: E731
for v in ("tuned", "mt", "natural"):
    a, b, c = d[("cpp", v)], d[("c_gcc", v)], d[("c", v)]
    L.append(f"{v} : C++ {[round(1e3 * t, 2) for t in a]} ms ; C par gcc {[round(1e3 * t, 2) for t in b]} ms ; "
             f"C {[round(1e3 * t, 2) for t in c]} ms ; C++ / C par gcc = {gm(a) / gm(b):.3f}"
             + (" (formes naturelles différentes : vector<vector> contre tableau 2D)" if v == "natural" else ""))

L.append("\n# Relectures : documents de remarque par langage (docs/*.md)")
names = {"ADA": "ada", "FORTRAN": "fortran", "MOJO": "mojo", "JULIA": "julia", "CHAPEL": "chapel", "CSHARP": "csharp",
         "DLANG": "d", "RUST": "rust", "NIM": "nim", "C3": "c3", "ODIN": "odin", "CPP": "cpp", "ZIG": "zig"}
have = sorted(v for k, v in names.items() if os.path.exists(os.path.join(ROOT, "docs", f"{k}.md")))
top13 = [l for l in P["order21"][:13]]
L.append(f"langages relus ({len(have)}) : {', '.join(have)} ; parmi les 13 premiers, non relus : "
         f"{', '.join(l for l in top13 if l not in have)}")
meth = open(os.path.join(ROOT, "docs", "METHODOLOGY.md")).read().splitlines()
L.append("docs/METHODOLOGY.md, préambule : " + " ".join(meth[2:4]))

out = os.path.join(ROOT, "results", "c_check", "data_facts.txt")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write("\n".join(L) + "\n")
print("\n".join(L))
