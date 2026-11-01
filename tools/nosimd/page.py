#!/usr/bin/env python3
"""Page partageable « SIMD explicite et classement » (docs/page/simd.html) : prose fixe, chiffres lus dans
results/nosimd_check.json (sensibilité, docs/NOSIMD.md). Remplace le marqueur <!--CONTENT--> du gabarit
docs/page/simd.template.html."""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NAMES = {"c": "C", "cpp": "C++", "csharp": "C#", "java": "Java", "zig": "Zig", "odin": "Odin", "julia": "Julia",
         "ada": "Ada", "fortran": "Fortran", "js": "JavaScript", "python": "Python", "haskell": "Haskell", "c3": "C3",
         "d": "D", "rust": "Rust", "chapel": "Chapel", "nim": "Nim", "mojo": "Mojo", "go": "Go", "ocaml": "OCaml",
         "lua": "Lua"}
COLS = [("Publié", "Publié"), ("Contrôle sans mt", "Sans mt"), ("S-scalaire", "S-scalaire"),
        ("S-symétrique", "S-symétrique"), ("S-noyaux-scalaires", "Noyaux scalaires"), ("S-importées", "Sans importées")]
REPO = "https://github.com/jsiaut/claude_code_test2/blob/claude/great-goodall-49iwdz/"


def nbsp(text):
    """Typographie française dans les nœuds de texte : espace insécable avant ; : ! ? » % et après «."""
    text = re.sub(r" ([;:!?»%])", "\u00a0\\1", text)
    return text.replace("« ", "«\u00a0")


def fr(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def chip(c):
    label = {"S": "S", "V": "V", "P": "P", "M": "M", "V+P": "V+P"}[c]
    cls = {"S": "s", "V": "v", "P": "p", "M": "m", "V+P": "v"}[c]
    return f'<span class="chip {cls}">{label}</span>'


C1 = {"cpp": 1, "zig": 1, "odin": 1, "c3": 1, "d": 1, "mojo": 1, "csharp": 1, "c": 0.5, "rust": 0.5, "java": 0.5,
      "go": 0.5, "haskell": 0.5, "nim": 0, "ada": 0.5}
CLASS_ORDER = ["cpp", "zig", "odin", "c3", "d", "mojo", "csharp", "c", "rust", "java", "go", "haskell", "nim", "ada"]
CLASS_COLS = [("k1:aos:energy", "K1 aos"), ("k1:soa:energy", "K1 soa"), ("k5:tuned", "K5"), ("k6:tuned:q6", "Q6"),
              ("k6:tuned:q1", "Q1"), ("k9:tuned", "K9")]


def class_table(o):
    head = "".join(f"<th>{lbl}</th>" for _, lbl in CLASS_COLS)
    rows = []
    for l in CLASS_ORDER:
        cl = o["class"].get(l, {})
        cells = "".join(f"<td>{chip(cl.get(k, 'S'))}</td>" for k, _ in CLASS_COLS)
        rows.append(f'<tr><td class="lang">{NAMES[l]}</td><td class="num">{fr(C1[l], 1) if C1[l] % 1 else C1[l]}</td>'
                    f"{cells}</tr>")
    rest = "Julia, Chapel, Fortran, JavaScript, Python, OCaml, Lua"
    rows.append(f'<tr><td class="lang">{rest}</td><td class="num">0 ou 0,5</td>'
                + "".join(f"<td>{chip('S')}</td>" for _ in CLASS_COLS) + "</tr>")
    return (f'<div class="scroll"><table><thead><tr><th>Variante optimisée</th><th class="num">C1</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def results_table(o):
    S = o["scenarios"]
    pub = S["Publié"]
    head = "".join(f'<th class="num">{html.escape(lbl)}</th>' for _, lbl in COLS)
    rows = []
    for l in pub["order21"]:
        cells = []
        for key, _ in COLS:
            z = S[key]
            mv = z["moves"][l]
            mark = ""
            if key != "Publié" and mv:
                mark = (f'<span class="mv up">▲{-mv}</span>' if mv < 0 else f'<span class="mv down">▼{mv}</span>')
            cells.append(f'<td class="num">{z["pos"][l]}<span class="sc"> ({fr(z["ms0"][l])})</span>{mark}</td>')
        rows.append(f'<tr><td class="lang">{NAMES[l]}</td>{"".join(cells)}</tr>')
    return (f'<div class="scroll"><table><thead><tr><th>Langage</th>{head}</tr></thead><tbody>{"".join(rows)}'
            '</tbody></table></div>')


def spear_row(o):
    S = o["scenarios"]
    items = []
    for key, lbl in COLS[1:]:
        z = S[key]
        top3 = ", ".join(NAMES[l] for l in z["order21"][:3])
        items.append(f"<li><strong>{html.escape(lbl)}</strong> : {fr(z['spearman_vs_published'], 3)} ; trois premiers : "
                     f"{top3}.</li>")
    return ('<p class="prose">Corrélation de rang (Spearman) avec le publié, et trois premiers, par scénario :</p>'
            '<ul class="prose">' + "".join(items) + "</ul>")


def main():
    o = json.load(open(os.path.join(ROOT, "results", "nosimd_check.json")))
    tpl = open(os.path.join(ROOT, "docs", "page", "simd.template.html"), encoding="utf-8").read()
    body = open(os.path.join(ROOT, "docs", "page", "simd.body.html"), encoding="utf-8").read()
    S = o["scenarios"]
    sub = {
        "{{RESULTS_SECTION}}": open(os.path.join(ROOT, "docs", "page", "simd.results.html"), encoding="utf-8").read(),
        "{{DECIDED_SIMD}}": open(os.path.join(ROOT, "docs", "page", "simd.decided.html"), encoding="utf-8").read().strip(),
    }
    for k, v in sub.items():
        body = body.replace(k, v)
    sub = {
        "{{CLASS_TABLE}}": class_table(o),
        "{{CHIP_S}}": chip("S"), "{{CHIP_V}}": chip("V"), "{{CHIP_P}}": chip("P"), "{{CHIP_M}}": chip("M"),
        "{{REPO}}": REPO,
        "{{RESULTS_TABLE}}": results_table(o),
        "{{SPEARMAN}}": spear_row(o),
        "{{MOJO_SUB}}": f"Mojo reste {S['S-scalaire-Mojo']['pos']['mojo']}e ({fr(S['S-scalaire-Mojo']['ms0']['mojo'])} "
                        f"points au lieu de {fr(S['S-scalaire']['ms0']['mojo'])})",
    }
    for k, v in sub.items():
        body = body.replace(k, v)
    assert "{{" not in body, "marqueur non remplacé"
    body = re.sub(r">([^<]+)<", lambda m: ">" + nbsp(m.group(1)) + "<", body)
    out = tpl.replace("<!--CONTENT-->", body)
    open(os.path.join(ROOT, "docs", "page", "simd.html"), "w", encoding="utf-8").write(out)


if __name__ == "__main__":
    main()
