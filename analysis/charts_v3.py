#!/usr/bin/env python3
"""Graphique SVG de l'analyse v3, sans dépendance : plafond E et code naturel D1 par langage, sur les deux machines,
groupés par étage. Entrée : results/summary_v3.json. Sortie : results/charts/v3_profiles.svg."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_v2 import NAMES, RANKED, ROOT  # noqa: E402
from charts_v2 import STYLE, esc  # noqa: E402


def fr(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def profiles_svg(o, path):
    R = o["results"]
    tiers = o["tiers"]
    rows = []  # (langage ou None pour un titre d'étage, étage)
    for t, members in enumerate(tiers):
        rows.append((None, t + 1))
        rows.extend((l, t + 1) for l in sorted(members, key=lambda l: -R[l]["E"]))
    W, L, Rm, T, row, head = 760, 112, 24, 118, 21, 20
    gap = 34
    pw = (W - L - Rm - gap) / 2
    panels = [("E", "Plafond E (0–100)", 100, [0, 25, 50, 75, 100], "E_ci", "E_m3", 1),
              ("D1", "Code naturel D1 (sur 100)", 25, [0, 5, 10, 15, 20, 25], "D1_ci", "D1_m3", 100)]
    ys, y = [], T
    for l, _t in rows:
        ys.append(y + (head if l is None else row) / 2)
        y += head if l is None else row
    H = y + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Plafond et code naturel par langage, sur deux machines">', STYLE,
           f'<rect class="bg" width="{W}" height="{H}"/>',
           '<text class="t1" x="16" y="26">Plafond et code naturel, par langage et par machine</text>',
           '<text class="t2" x="16" y="46">E : meilleur code écrit pour la machine ; D1 : code naturel. Chacun est '
           'rapporté au meilleur langage de chaque</text>',
           '<text class="t2" x="16" y="62">mesure, sur chaque machine. Étages : règle du plan v3, sans ordre à '
           "l'intérieur d'un étage. K5 vient de la machine 3.</text>"]
    out.append('<line class="ua" x1="16" x2="42" y1="84" y2="84"/><circle class="dot" cx="29" cy="84" r="5"/>'
               '<text class="t2" x="50" y="88">machine 1 (Cascade Lake) et son IC à 95 %</text>')
    out.append('<circle class="dot2" cx="330" cy="84" r="4.5"/><text class="t2" x="342" y="88">machine 3 (Emerald '
               'Rapids), un processus par mesure</text>')
    for p, (key, title, xmax, ticks, ci, m3, scale) in enumerate(panels):
        x0 = L + p * (pw + gap)
        X = lambda v, x0=x0, xmax=xmax: x0 + min(max(v, 0), xmax) / xmax * pw  # noqa: E731
        out.append(f'<text class="lab" x="{x0:.1f}" y="{T - 10}" font-weight="600">{esc(title)}</text>')
        for v in ticks:
            out.append(f'<line class="grid" x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 40}"/>')
            out.append(f'<text class="tick" x="{X(v):.1f}" y="{H - 24}" text-anchor="middle">{v}</text>')
        for (l, t), yy in zip(rows, ys):
            if l is None:
                continue
            r = R[l]
            v = r["E"] if key == "E" else 100 * r["D_parts"]["D1"]
            lo, hi = r[ci]
            v3 = r[m3] * scale
            tip = (f'{NAMES[l]}, étage {t} : {key} {fr(v)} [{fr(lo)}–{fr(hi)}] sur la machine 1, {fr(v3)} sur la '
                   f'machine 3')
            out.append(f'<g><title>{esc(tip)}</title>'
                       f'<rect x="{x0:.1f}" y="{yy - row / 2:.1f}" width="{pw:.1f}" height="{row}" fill="transparent"/>'
                       f'<line class="ua" x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{yy:.1f}" y2="{yy:.1f}"/>'
                       f'<circle class="dot2" cx="{X(v3):.1f}" cy="{yy:.1f}" r="4.5"/>'
                       f'<circle class="dot" cx="{X(v):.1f}" cy="{yy:.1f}" r="5"/></g>')
    first = True
    for (l, t), yy in zip(rows, ys):
        if l is None:
            if not first:
                out.append(f'<line class="sep" x1="16" x2="{W - Rm}" y1="{yy - head / 2:.1f}" y2="{yy - head / 2:.1f}"/>')
            out.append(f'<text class="tick" x="16" y="{yy + 4:.1f}">étage {t}</text>')
            first = False
        else:
            out.append(f'<text class="lab" x="{L - 12}" y="{yy + 4:.1f}" text-anchor="end">{esc(NAMES[l])}</text>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))


def main():
    o = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))
    os.makedirs(os.path.join(ROOT, "results", "charts"), exist_ok=True)
    profiles_svg(o, os.path.join(ROOT, "results", "charts", "v3_profiles.svg"))


if __name__ == "__main__":
    main()
