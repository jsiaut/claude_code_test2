#!/usr/bin/env python3
"""Graphiques SVG de l'analyse v2, sans dépendance : rangs et leurs incertitudes, carte plafond / code par défaut.
Entrée : results/summary_v2.json. Sorties : results/charts/v2_ranks.svg, results/charts/v2_map.svg."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_v2 import NAMES, RANKED, ROOT  # noqa: E402

STYLE = """<style>
  svg { --surface: #fcfcfb; --ink: #0b0b0b; --ink2: #52514e; --muted: #898781; --grid: #e1e0d9; --axis: #c3c2b7;
        --s1: #2a78d6; --band: #b7d3f6; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  @media (prefers-color-scheme: dark) {
    svg { --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #898781; --grid: #2c2c2a; --axis: #383835;
          --s1: #3987e5; --band: #184f95; }
  }
  .bg { fill: var(--surface); } .t1 { fill: var(--ink); font-size: 15px; font-weight: 600; }
  .t2 { fill: var(--ink2); font-size: 12px; } .lab { fill: var(--ink); font-size: 12px; }
  .tick { fill: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
  .grid { stroke: var(--grid); stroke-width: 1; } .axis { stroke: var(--axis); stroke-width: 1; }
  .band { fill: var(--band); } .ua { stroke: var(--ink2); stroke-width: 2; stroke-linecap: round; }
  .dot { fill: var(--s1); stroke: var(--surface); stroke-width: 2; }
  .dot2 { fill: var(--muted); stroke: var(--surface); stroke-width: 2; }
  .sep { stroke: var(--axis); stroke-width: 1; }
</style>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ranks_svg(o, path):
    R = o["results"]
    langs = sorted(RANKED, key=lambda l: R[l]["rank"])
    n = len(langs)
    W, L, Rm, T, row = 760, 130, 30, 92, 24
    H = T + n * row + 46
    X = lambda r: L + (r - 1) * (W - L - Rm) / (n - 1)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Rangs v2 et leurs incertitudes">', STYLE, f'<rect class="bg" width="{W}" height="{H}"/>',
           f'<text class="t1" x="16" y="26">Rang de chaque langage, et ce que l\'incertitude permet de dire</text>',
           f'<text class="t2" x="16" y="46">Point : configuration principale v2. Bande : ensemble simultané à 95 % '
           f'(mesures seules). Trait : 5–95 % de l\'analyse globale.</text>']
    # légende
    lx = 16
    out.append(f'<rect class="band" x="{lx}" y="60" width="26" height="12" rx="2"/>'
               f'<text class="t2" x="{lx + 32}" y="70">mesures seules</text>')
    lx += 150
    out.append(f'<line class="ua" x1="{lx}" x2="{lx + 26}" y1="66" y2="66"/>'
               f'<text class="t2" x="{lx + 32}" y="70">analyse globale (méthode, poids, jugements)</text>')
    lx += 330
    out.append(f'<circle class="dot" cx="{lx + 6}" cy="66" r="5"/><text class="t2" x="{lx + 18}" y="70">rang v2</text>')
    for r in range(1, n + 1):
        if r in (1, 5, 10, 15, 20) or r == n:
            out.append(f'<line class="grid" x1="{X(r):.1f}" x2="{X(r):.1f}" y1="{T - 6}" y2="{T + n * row}"/>')
            out.append(f'<text class="tick" x="{X(r):.1f}" y="{T + n * row + 18}" text-anchor="middle">{r}</text>')
    out.append(f'<text class="t2" x="{(L + W - Rm) / 2:.0f}" y="{T + n * row + 38}" text-anchor="middle">'
               f'rang (1 = le plus de mechanical sympathy mesurée)</text>')
    prev_group = None
    for i, l in enumerate(langs):
        r = R[l]
        y = T + i * row + row / 2
        if prev_group is not None and r["group"] != prev_group:
            out.append(f'<line class="sep" x1="16" x2="{W - Rm}" y1="{y - row / 2:.1f}" y2="{y - row / 2:.1f}"/>')
        prev_group = r["group"]
        lo, hi = r["rank_set"]
        tip = (f'{NAMES[l]} : rang {r["rank"]}, ensemble simultané {lo}–{hi}, analyse globale '
               f'{r["ua_rank_90"][0]}–{r["ua_rank_90"][1]}, groupe {r["group"]}')
        out.append(f'<g><title>{esc(tip)}</title>')
        out.append(f'<text class="lab" x="{L - 12}" y="{y + 4:.1f}" text-anchor="end">{esc(NAMES[l])}</text>')
        out.append(f'<rect class="band" x="{X(lo) - 6:.1f}" y="{y - 7:.1f}" width="{X(hi) - X(lo) + 12:.1f}" height="14" rx="4"/>')
        a, b = r["ua_rank_90"]
        out.append(f'<line class="ua" x1="{X(a):.1f}" x2="{X(b):.1f}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(f'<circle class="dot" cx="{X(r["rank"]):.1f}" cy="{y:.1f}" r="5"/></g>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))


def place_labels(pts, W, H, box):
    """Place chaque étiquette autour de son point sans chevauchement (premier emplacement libre)."""
    placed, res = [], {}
    occupied = [(x - 6, y - 6, x + 6, y + 6) for _, x, y, _ in pts]

    def free(b):
        if b[0] < box[0] or b[2] > box[2] or b[1] < box[1] or b[3] > box[3]:
            return False
        return not any(b[0] < o[2] and b[2] > o[0] and b[1] < o[3] and b[3] > o[1] for o in occupied + placed)
    for name, x, y, w in sorted(pts, key=lambda p: (p[2], p[1])):
        cands = [(x + 9, y + 4, "start"), (x - 9, y + 4, "end"), (x, y - 10, "middle"), (x, y + 18, "middle"),
                 (x + 8, y - 8, "start"), (x - 8, y - 8, "end"), (x + 8, y + 16, "start"), (x - 8, y + 16, "end"),
                 (x, y - 22, "middle"), (x, y + 30, "middle"), (x + 8, y - 20, "start"), (x - 8, y - 20, "end"),
                 (x + 8, y + 28, "start"), (x - 8, y + 28, "end")]
        for k in range(len(cands)):
            tx, ty, anchor = cands[k]
            x0 = tx if anchor == "start" else (tx - w if anchor == "end" else tx - w / 2)
            b = (x0, ty - 11, x0 + w, ty + 3)
            if free(b):
                placed.append(b)
                res[name] = (tx, ty, anchor)
                break
        else:
            tx, ty, anchor = cands[0]
            res[name] = (tx, ty, anchor)
    return res


def map_svg(o, path):
    R = o["results"]
    W, H, L, Rm, T, Bm = 760, 600, 64, 30, 108, 56
    dmax = max(100 * R[l]["D_parts"]["D1"] for l in RANKED)
    ytop = 5 * int(dmax * 1.15 / 5 + 1)
    X = lambda e: L + e / 100 * (W - L - Rm)
    Y = lambda d: T + (1 - d / ytop) * (H - T - Bm)
    pareto = set(o["pareto"])
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Carte plafond contre code par défaut">', STYLE, f'<rect class="bg" width="{W}" height="{H}"/>',
           '<text class="t1" x="16" y="26">Plafond (E) et code par défaut (D1)</text>',
           '<text class="t2" x="16" y="46">E : meilleur code écrit pour la machine, rapporté au meilleur temps de chaque '
           'mesure.</text>',
           '<text class="t2" x="16" y="63">D1 : code naturel, rapporté au même meilleur temps. Configuration principale v2.'
           '</text>']
    out.append('<circle class="dot" cx="22" cy="84" r="5"/><text class="t2" x="34" y="88">front de Pareto sur '
               '(contrôle C, plafond E, défaut D)</text>')
    out.append('<circle class="dot2" cx="352" cy="84" r="5"/><text class="t2" x="364" y="88">autres langages</text>')
    for v in range(0, 101, 20):
        out.append(f'<line class="grid" x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - Bm}"/>')
        out.append(f'<text class="tick" x="{X(v):.1f}" y="{H - Bm + 16}" text-anchor="middle">{v}</text>')
    for v in range(0, ytop + 1, 5):
        out.append(f'<line class="grid" x1="{L}" x2="{W - Rm}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/>')
        out.append(f'<text class="tick" x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    out.append(f'<line class="axis" x1="{L}" x2="{W - Rm}" y1="{H - Bm}" y2="{H - Bm}"/>')
    out.append(f'<text class="t2" x="{(L + W - Rm) / 2:.0f}" y="{H - 14}" text-anchor="middle">E, plafond (0–100)</text>')
    out.append(f'<text class="t2" transform="translate(18 {(T + H - Bm) / 2:.0f}) rotate(-90)" text-anchor="middle">'
               f'D1, code par défaut (sur 100)</text>')
    pts = [(l, X(R[l]["E"]), Y(100 * R[l]["D_parts"]["D1"]), 7.0 * len(NAMES[l])) for l in RANKED]
    labels = place_labels(pts, W, H, (L, T, W - Rm, H - Bm))
    for l, x, y, _ in pts:
        tip = f'{NAMES[l]} : E {R[l]["E"]:.1f}, D1 {100 * R[l]["D_parts"]["D1"]:.1f}, C {R[l]["C"]:.1f}, rang {R[l]["rank"]}'
        tx, ty, anchor = labels[l]
        lead = ""
        if abs(ty - 4 - y) > 14:
            lead = f'<line class="axis" x1="{x:.1f}" y1="{y:.1f}" x2="{tx:.1f}" y2="{ty - (4 if ty > y else 12):.1f}"/>'
        out.append(f'<g><title>{esc(tip)}</title>{lead}<circle class="{"dot" if l in pareto else "dot2"}" cx="{x:.1f}" '
                   f'cy="{y:.1f}" r="5"/><text class="lab" x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}">'
                   f'{esc(NAMES[l])}</text></g>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))


def main():
    o = json.load(open(os.path.join(ROOT, "results", "summary_v2.json")))
    os.makedirs(os.path.join(ROOT, "results", "charts"), exist_ok=True)
    ranks_svg(o, os.path.join(ROOT, "results", "charts", "v2_ranks.svg"))
    map_svg(o, os.path.join(ROOT, "results", "charts", "v2_map.svg"))


if __name__ == "__main__":
    main()
