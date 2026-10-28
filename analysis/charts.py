#!/usr/bin/env python3
"""Graphiques SVG sans dépendance : courbes K2 (latence par saut selon la taille) et barres des scores."""
import json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import final_data, point, RANKED  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZES = ["16384", "65536", "262144", "524288", "2097152", "8388608", "16777216", "33554432", "67108864", "268435456"]
LABELS = ["16K", "64K", "256K", "512K", "2M", "8M", "16M", "32M", "64M", "256M"]
PALETTE = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22",
           "#393b79", "#637939", "#8c6d31", "#843c39", "#7b4173", "#3182bd", "#e6550d", "#31a354", "#756bb1", "#636363", "#000000"]


def k2_svg(data, path):
    W, H, L, R, T, B = 900, 560, 70, 150, 30, 50
    langs = [l for l in RANKED if l in data and all(("k2", "tuned", s) in data[l] for s in SIZES)]
    ys = {l: [point(data[l][("k2", "tuned", s)]) / 4.2e6 * 1e9 for s in SIZES] for l in langs}
    lo, hi = math.log10(0.5), math.log10(max(max(v) for v in ys.values()) * 1.5)
    X = lambda i: L + i * (W - L - R) / (len(SIZES) - 1)
    Y = lambda v: T + (H - T - B) * (1 - (math.log10(v) - lo) / (hi - lo))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<text x="{L}" y="18" font-size="14">K2 : ns par saut dépendant selon la taille du tableau (échelle log)</text>']
    for e in range(int(math.floor(lo)), int(math.ceil(hi)) + 1):
        for m in (1, 2, 5):
            v = m * 10 ** e
            if lo <= math.log10(v) <= hi:
                out.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#eee"/>')
                out.append(f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{v:g}</text>')
    for i, lab in enumerate(LABELS):
        out.append(f'<text x="{X(i):.1f}" y="{H - B + 18}" text-anchor="middle">{lab}</text>')
    for k, l in enumerate(langs):
        c = PALETTE[k % len(PALETTE)]
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ys[l]))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{2.5 if l == "c" else 1.4}"/>')
        out.append(f'<text x="{W - R + 8}" y="{T + 14 * k + 10}" fill="{c}">{l}</text>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))


def bars_svg(summary, path):
    res = summary["results"]
    langs = sorted([l for l in RANKED if res.get(l, {}).get("MS") is not None], key=lambda l: -res[l]["MS"])
    W, row = 900, 26
    H = 60 + row * len(langs)
    L, R = 110, 40
    S = lambda v: (W - L - R) * v / 100
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           '<text x="10" y="18" font-size="14">Score MS = 0,35·C + 0,40·E + 0,25·D (contributions empilées)</text>',
           '<text x="10" y="36" fill="#1f77b4">■ C contrôle</text><text x="110" y="36" fill="#2ca02c">■ E efficacité plafond</text>'
           '<text x="270" y="36" fill="#ff7f0e">■ D défaut et transparence</text>']
    for i, l in enumerate(langs):
        y = 50 + i * row
        r = res[l]
        x = L
        for val, w, c in ((r["C"], 0.35, "#1f77b4"), (r["E"], 0.40, "#2ca02c"), (r["D"], 0.25, "#ff7f0e")):
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{S(val * w):.1f}" height="{row - 6}" fill="{c}"/>')
            x += S(val * w)
        out.append(f'<text x="{L - 8}" y="{y + 15}" text-anchor="end">{i + 1}. {l}</text>')
        out.append(f'<text x="{x + 6:.1f}" y="{y + 15}">{r["MS"]:.1f}</text>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))


def main():
    os.makedirs(os.path.join(ROOT, "results", "charts"), exist_ok=True)
    data, *_ = final_data()
    k2_svg(data, os.path.join(ROOT, "results", "charts", "k2.svg"))
    sp = os.path.join(ROOT, "results", "summary.json")
    if os.path.exists(sp):
        bars_svg(json.load(open(sp)), os.path.join(ROOT, "results", "charts", "scores.svg"))
    print("graphiques écrits dans results/charts/")


if __name__ == "__main__":
    main()
