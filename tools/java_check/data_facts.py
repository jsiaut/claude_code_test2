#!/usr/bin/env python3
"""Faits de la remarque sur Java tirés des données publiées (docs/JAVA.md, section 2) : temps par clé (Java, C, C#),
rapports sur Cascade Lake et sur la machine 3, piliers de Java et de C#, K10 (campagne et remesure à 9 processus),
empreinte de K1 et sa décomposition. Sortie : results/java_check/facts.txt."""
import glob, json, math, os, statistics, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import analyze_v2 as v2  # noqa: E402
from analyze_v3 import proc_logs  # noqa: E402


def gm(p):
    return 1e3 * math.exp(proc_logs(p).mean())


def k10(folder):
    res = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "results", folder, "*.jsonl"))):
        lang = os.path.basename(f)[:-6]
        per = defaultdict(list)
        for line in open(f):
            r = json.loads(line)
            if r.get("kernel") == "k10":
                ts = [x["sec"] for x in r["reps"] if x.get("ok")]
                if ts:
                    per[r["variant"]].append(1e3 * statistics.median(ts))
        if per.get("tuned"):
            res[lang] = (statistics.median(per["tuned"]), len(per["tuned"]))
    return sorted(res.items(), key=lambda kv: kv[1][0])


def main():
    L = []
    d, *_ = v2.dataset_main()
    L.append("# Données publiées (K5 : machine 3 ; K9 : machine 16, harnais commun ; autres : Cascade Lake)")
    L.append("clé ; Java ; C ; C# (ms, moyenne géométrique des médianes de processus)")
    for key in sorted(set(d["java"])):
        row = [f"{gm(d[l][key]):.2f}" if key in d[l] else "-" for l in ("java", "c", "csharp")]
        L.append(f"{':'.join(x for x in key if x)} ; " + " ; ".join(row))
    k1 = d["java"][("k1", "natural_shuffled", "energy")], d["java"][("k1", "natural", "energy")]
    L.append(f"K1 permuté / naturel (Java) : {gm(k1[0]) / gm(k1[1]):.2f}")
    k7 = ("k7", "tuned", "")
    L.append(f"K7 tuned Java / C, Cascade Lake : {gm(d['java'][k7]) / gm(d['c'][k7]):.2f}")
    m3, *_ = v2.load_raw("v2_m3")
    L.append(f"K7 tuned Java / C, machine 3 : {gm(m3['java'][k7]) / gm(m3['c'][k7]):.2f}")
    s = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))["results"]
    for l in ("java", "csharp", "go"):
        z = s[l]
        L.append(f"{l} : contrôle {z['C_v2']:.2f}, plafond {z['E']:.2f}, défaut {z['D']:.2f}, score {z['MS']:.2f}")
    j, c = s["java"], s["csharp"]
    L.append(f"écart C# - Java : {c['MS'] - j['MS']:.2f} points, dont contrôle {0.35 * (c['C_v2'] - j['C_v2']):.2f}, "
             f"plafond {0.40 * (c['E'] - j['E']):.2f}, défaut {0.25 * (c['D'] - j['D']):.2f}")
    fp = json.load(open(os.path.join(ROOT, "results", "footprint.json")))["java"]
    n, cap = 1 << 22, 10
    while cap < n:
        cap += cap >> 1
    L.append(f"K1, empreinte publiée : {fp:.2f} o par particule ; objet 8 + 64 = 72 o ; tableau de références de "
             f"l'ArrayList : capacité {cap} (croissance de 1,5 à partir de 10), {4 * cap / n:.2f} o par particule "
             f"(dont 4 o de référence) ; total {72 + 4 * cap / n:.2f} o")
    for folder, lab in (("raw", "campagne"), ("raw_post", "remesure à 9 processus")):
        top = k10(folder)
        L.append(f"K10 tuned, {lab} (médiane des médianes de processus, ms) : "
                 + ", ".join(f"{l} {t:.1f} ({n})" for l, (t, n) in top[:8]))
    out = os.path.join(ROOT, "results", "java_check", "facts.txt")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
