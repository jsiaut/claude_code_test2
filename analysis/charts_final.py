#!/usr/bin/env python3
"""Graphique SVG du classement publié (calcul « Final » de la v6 : docs/METHOD.md, docs/V5_2.md, docs/V5_4.md,
docs/V6.md) : rang espéré sur les 20 000 variantes, rang plausible (90 %), score moyen sur ces variantes (il fixe
l'ordre). Un astérisque marque le langage classé, par exception, avec sa version de développement.
Entrée : results/final/analysis.json (ou FINAL_OUT/analysis.json). Sortie : results/charts/classement_v4.svg."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from final_v4 import DEV_LANG, NAMES, ROOT  # noqa: E402

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

SRC = os.path.join(os.environ.get("FINAL_OUT", os.path.join(ROOT, "results", "final")), "analysis.json")
DST = os.environ.get("FINAL_CHART", os.path.join(ROOT, "results", "charts", "classement_v4.svg"))


MICRO = {"6/207": "Emerald Rapids", "6/173": "Granite Rapids"}  # famille/modèle du processeur -> nom


def fr(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def ranking_svg(f, path, machines, models, dev=None):
    order = f["order"]
    n = len(order)
    W, L, Rm, T, row = 760, 118, 70, 74, 24
    H = T + n * row + 46 + (20 if dev else 0)
    name = lambda l: NAMES[l] + ("*" if dev and l == DEV_LANG else "")  # noqa: E731
    X = lambda r: L + (r - 1) * (W - L - Rm) / (n - 1)  # noqa: E731
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Classement de la v6 et plage de rang plausible">', STYLE,
           f'<rect class="bg" width="{W}" height="{H}"/>',
           '<text class="t1" x="16" y="26">Classement de la v6</text>',
           '<text class="t2" x="16" y="46">Point : rang espéré sur 20 000 variantes de l\'analyse (poids, méthodes, '
           'jugements, bruit, poids des tailles).</text>',
           '<text class="t2" x="16" y="62">Trait : rang dans 90 % de ces variantes. À droite : score moyen sur ces variantes. '
           f'Machine{"s" if len(machines) > 1 else ""} {", ".join(machines)} ({", ".join(models)}).</text>']
    for r in (1, 5, 10, 15, 20, 25):
        out.append(f'<line class="grid" x1="{X(r):.1f}" x2="{X(r):.1f}" y1="{T - 4}" y2="{T + n * row}"/>')
        out.append(f'<text class="tick" x="{X(r):.1f}" y="{T + n * row + 18}" text-anchor="middle">{r}</text>')
    out.append(f'<text class="t2" x="{(L + W - Rm) / 2:.0f}" y="{T + n * row + 38}" text-anchor="middle">rang</text>')
    if dev:
        ver = esc(dev["version"].split("+")[0])
        out.append(f'<text class="t2" x="16" y="{T + n * row + 58}">* {NAMES[DEV_LANG]} : par exception, version de '
                   f'développement {ver} ; les 19 autres, dernière version stable.</text>')
    for i, l in enumerate(order):
        y = T + i * row + row / 2
        a, b = f["rank90"][l]
        tip = f"{i + 1}. {name(l)} : rang espéré {fr(f['exp'][l], 2)}, rang plausible {a}–{b}, score {fr(f['ms_mean'][l])}"
        out.append(f'<g><title>{esc(tip)}</title>'
                   f'<rect x="16" y="{y - row / 2:.1f}" width="{W - 32}" height="{row}" fill="transparent"/>'
                   f'<text class="lab" x="{L - 12}" y="{y + 4:.1f}" text-anchor="end">{i + 1}. {esc(name(l))}</text>'
                   f'<line class="ua" x1="{X(a):.1f}" x2="{X(b):.1f}" y1="{y:.1f}" y2="{y:.1f}"/>'
                   f'<circle class="dot" cx="{X(f["exp"][l]):.1f}" cy="{y:.1f}" r="5"/>'
                   f'<text class="tick" x="{W - 16}" y="{y + 4:.1f}" text-anchor="end">{fr(f["ms_mean"][l])}</text></g>')
    out.append("</svg>")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("\n".join(out))


def main():
    o = json.load(open(SRC))
    models = sorted({MICRO.get("/".join(m.split()[0].split("/")[:2]), m.split()[0]) for m in o["cpu_models"]})
    ranking_svg(o["results"]["Final"], DST, o["machines"], models, o.get("zig_dev"))
    print(DST)


if __name__ == "__main__":
    main()
