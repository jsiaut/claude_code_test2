#!/usr/bin/env python3
"""Fiche chiffrée par langage (aide à la rédaction des justifications du README, section 5).

Lit results/summary.json (après analyze.py), les données retenues, results/footprint.json,
results/vectorization.json et le rusage des processus. Écrit results/facts.md.
"""
import glob, json, os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import final_data, point, RANKED, ANNEX, E_MEASURES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def t(data, l, k, v, p=""):
    procs = data.get(l, {}).get((k, v, p))
    return point(procs) if procs else None


def ms(x):
    return "—" if x is None else (f"{x * 1e3:.3g} ms" if x < 10 else f"{x:.3g} s")


def ratio(a, b):
    return "—" if not a or not b else f"{a / b:.2g}"


def cpu_ratio():
    single = {("k1", "natural"), ("k4", "natural_unsorted"), ("k5", "natural"), ("k5", "tuned"), ("k7", "natural"),
              ("k8", "natural"), ("k9", "natural"), ("k6", "natural"), ("k1", "soa")}
    out = {}
    for f in glob.glob(os.path.join(ROOT, "results", "raw", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if (r["kernel"], r["variant"]) in single and r.get("returncode") == 0 and r["wall"] > 0:
                out.setdefault(r["lang"], []).append((r["utime"] + r["stime"]) / r["wall"])
    return {l: statistics.median(v) for l, v in out.items()}


def main():
    s = json.load(open(os.path.join(ROOT, "results", "summary.json")))
    res, tstar = s["results"], s["tstar"]
    data, lat, *_ = final_data()
    fp = json.load(open(os.path.join(ROOT, "results", "footprint.json"))) if os.path.exists(
        os.path.join(ROOT, "results", "footprint.json")) else {}
    vec = json.load(open(os.path.join(ROOT, "results", "vectorization.json"))) if os.path.exists(
        os.path.join(ROOT, "results", "vectorization.json")) else {}
    cr = cpu_ratio()
    order = sorted([l for l in RANKED if res.get(l, {}).get("MS") is not None], key=lambda l: -res[l]["MS"])
    lines = ["# Fiches chiffrées (générées par analysis/facts.py)", ""]
    for i, l in enumerate(order + [a for a in ANNEX if a in res]):
        r = res[l]
        rank = f"{i + 1}" if l in order else "annexe"
        lines.append(f"## {rank}. {l}")
        if r.get("MS") is not None:
            lines.append(f"* MS {r['MS']:.1f} ; C {r['C']:.1f} (rang {r.get('rank_C', '—')}) ; E {r['E']:.1f} (rang {r.get('rank_E', '—')}) ; "
                         f"D {r['D']:.1f} (rang {r.get('rank_D', '—')}) ; rang Dirichlet {r.get('rank_median', '—')} {r.get('rank_90', '')} ; "
                         f"cellules 0,5 {r.get('rank_halves_90', '')} ; noyau retiré {r.get('rank_drop_kernel', '')}")
        else:
            lines.append(f"* C {r.get('C')}, E {r.get('E')}, D {r.get('D')}")
        ek = r.get("E_kernels", {})
        lines.append("* E par noyau (t*/t) : " + ", ".join(f"{k} {v:.2f}" for k, v in ek.items() if v is not None))
        dp = r.get("D_parts", {})
        lines.append("* D : " + ", ".join(f"{k} {v:.2f}" for k, v in dp.items() if v is not None))
        d = lambda k, v, p="": t(data, l, k, v, p)
        lines.append(f"* K1 natural {ms(d('k1', 'natural', 'energy'))}, shuffled {ms(d('k1', 'natural_shuffled', 'energy'))} "
                     f"(×{ratio(d('k1', 'natural_shuffled', 'energy'), d('k1', 'natural', 'energy'))}), aos {ms(d('k1', 'aos', 'energy'))}, "
                     f"soa {ms(d('k1', 'soa', 'energy'))} ; empreinte {fp.get(l, '—')} o/particule")
        lines.append(f"* K3 rmw_packed {ms(d('k3', 'rmw_packed'))}, rmw_padded {ms(d('k3', 'rmw_padded'))}, sw_packed {ms(d('k3', 'sw_packed'))}, "
                     f"sw_padded {ms(d('k3', 'sw_padded'))} (faux partage ×{ratio(d('k3', 'rmw_packed'), d('k3', 'rmw_padded'))})")
        lines.append(f"* K4 natural non trié {ms(d('k4', 'natural_unsorted'))}, trié {ms(d('k4', 'natural_sorted'))}, sans branchement "
                     f"{ms(d('k4', 'branchless_unsorted'))} ; vectorisation mesurée C3 = {vec.get(ANNEX.get(l, l) if l not in vec else l, '—')}")
        lines.append(f"* K5 natural {ms(d('k5', 'natural'))}, tuned {ms(d('k5', 'tuned'))} (×{ratio(d('k5', 'natural'), d('k5', 'tuned'))})")
        lines.append(f"* K6 Q6 natural/tuned/mt {ms(d('k6', 'natural', 'q6'))} / {ms(d('k6', 'tuned', 'q6'))} / {ms(d('k6', 'mt', 'q6'))} ; "
                     f"Q1 {ms(d('k6', 'natural', 'q1'))} / {ms(d('k6', 'tuned', 'q1'))} / {ms(d('k6', 'mt', 'q1'))}")
        lines.append(f"* K7 natural {ms(d('k7', 'natural'))}, tuned {ms(d('k7', 'tuned'))} (×{ratio(d('k7', 'natural'), d('k7', 'tuned'))})")
        lk = lat.get(l, {}).get(("k8", "natural", ""))
        tail = ""
        if lk:
            p50, p999, mx = (statistics.median([x[j] for x in lk]) for j in (0, 3, 4))
            tail = f" ; latence p50 {p50 / 1e3:.3g} µs, p99.9 {p999 / 1e3:.3g} µs, max {mx / 1e3:.3g} µs (p99.9/p50 {p999 / p50:.1f})"
        lines.append(f"* K8 natural {ms(d('k8', 'natural'))}, tuned {ms(d('k8', 'tuned'))}, tuned_alloc {ms(d('k8', 'tuned_alloc'))}{tail}")
        lines.append(f"* K9 natural {ms(d('k9', 'natural'))}, tuned {ms(d('k9', 'tuned'))}, mt {ms(d('k9', 'mt'))}")
        lines.append(f"* K10 natural {ms(d('k10', 'natural'))}, tuned {ms(d('k10', 'tuned'))} (×{ratio(d('k10', 'natural'), d('k10', 'tuned'))})")
        k2 = [t(data, l, "k2", "tuned", sz) for sz in ("16384", "262144", "8388608", "268435456")]
        lines.append("* K2 ns/saut 16K/256K/8M/256M : " + " / ".join("—" if x is None else f"{x / 4.2e6 * 1e9:.3g}" for x in k2))
        lines.append(f"* (CPU utilisateur + système) / mural, noyaux mono-thread : {cr.get(l, float('nan')):.2f}")
        lines.append("")
    open(os.path.join(ROOT, "results", "facts.md"), "w").write("\n".join(lines))
    print("results/facts.md écrit")


if __name__ == "__main__":
    main()
