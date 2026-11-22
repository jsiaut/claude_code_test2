#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 3.3 et 3.4) : écrit results/open/list.md à partir des réponses des registres
(results/open/registry/<langage>.json, tools/open/registry.py) et des décisions de l'examen
(results/open/decisions.json : pour chaque langage et chaque case, la bibliothèque retenue et la raison du refus de
chacune des bibliothèques mieux classées ; bibliothèques nommées par le dossier ; cellules du plafond attribuées).
Le rang et la statistique de chaque bibliothèque sont recopiés des réponses, pas des décisions."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "results", "open", "registry")
DEC = os.path.join(ROOT, "results", "open", "decisions.json")
OUT = os.path.join(ROOT, "results", "open", "list.md")
ORDER = ["c", "odin", "cpp", "c3", "zig", "rust", "nim", "d", "ada", "chapel", "fortran", "swift", "julia", "mojo",
         "csharp", "fpc", "java", "go", "haskell", "ocaml", "bqn", "js", "php", "python", "lua"]
NAMES = {"c": "C", "odin": "Odin", "cpp": "C++", "c3": "C3", "zig": "Zig", "rust": "Rust", "nim": "Nim", "d": "D",
         "ada": "Ada", "chapel": "Chapel", "fortran": "Fortran", "swift": "Swift", "julia": "Julia", "mojo": "Mojo",
         "csharp": "C#", "fpc": "FreePascal", "java": "Java", "go": "Go", "haskell": "Haskell", "ocaml": "OCaml",
         "bqn": "BQN", "js": "JavaScript", "php": "PHP", "python": "Python", "lua": "Lua"}
REGISTRES = {"c": "archive d'Ubuntu 24.04", "cpp": "archive d'Ubuntu 24.04", "c3": "dépôt vendor de c3lang",
             "rust": "crates.io", "nim": "nimble (liste nim-lang/packages)", "d": "dub", "ada": "Alire (index)",
             "chapel": "Mason (registre)", "fortran": "index des paquets de fortran-lang.org",
             "swift": "Swift Package Index", "julia": "General", "mojo": "paquets de Modular et canal modular-community",
             "csharp": "NuGet", "fpc": "fppkg", "java": "Maven Central", "go": "modules (pkg.go.dev)",
             "haskell": "Hackage", "ocaml": "opam", "js": "npm", "php": "Packagist", "python": "PyPI",
             "lua": "LuaRocks"}


def fmt_stat(s):
    if isinstance(s, dict):
        return f"{s.get('first') or '?'} → {s.get('latest') or '?'}"
    if isinstance(s, (int, float)):
        return f"{s:,}".replace(",", " ")
    return str(s)


def main():
    dec = json.load(open(DEC, encoding="utf-8"))
    L = ["# Liste de la piste ouverte (v4, point 6)", "",
         "*Relevé du 22 novembre 2026 (`docs/V4_OPEN.md`, 3.2 à 3.4 et 10). Requêtes et réponses :",
         "`results/open/registry/<langage>.json` (`tools/open/registry.py`) ; décisions : `results/open/decisions.json` ;",
         "ce fichier est écrit par `tools/open/listmd.py`. Pour chaque case, les bibliothèques sont examinées dans l'ordre",
         "de la statistique d'usage du registre ; la première admise (3.3 a) est retenue, et chaque bibliothèque mieux",
         "classée est refusée avec sa raison. Aucune sonde, aucune forme n'a été écrite avant ce relevé.*", "",
         "*Lecture de 3.3 d : une bibliothèque comble les cases dont la recherche la retient ; une bibliothèque nommée par",
         "le dossier (3.3 c), les cases que son API comble. Les cellules du plafond suivent l'écart 3 (`docs/V4_OPEN.md`,",
         "10) : une bibliothèque n'y est attribuée que si elle apporte un levier que la bibliothèque standard n'offre pas en",
         "entier et que son API fait le calcul de la cellule ou en remplace le conteneur.*", ""]
    summary = []
    for lang in ORDER:
        p = os.path.join(REG, f"{lang}.json")
        if not os.path.exists(p) or lang not in dec:
            continue
        reg = json.load(open(p, encoding="utf-8"))
        d = dec[lang]
        L.append(f"## {NAMES[lang]}")
        L.append("")
        L.append(f"Registre : {reg.get('registre') or REGISTRES.get(lang, '?')} ; statistique : "
                 f"{reg.get('statistique', '—')}.")
        L.append("")
        if d.get("note"):
            L += [d["note"], ""]
        L.append("| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |")
        L.append("|---|---|---|---|---|---|---|")
        vers = d.get("versions", {})
        for case, v in reg["cases"].items():
            dc = d.get("cases", {}).get(case, {})
            cands = v["candidates"]
            names = [c["name"] for c in cands]
            ch = dc.get("choix")
            if ch:
                rk = names.index(ch) + 1
                st = fmt_stat(cands[rk - 1].get("stat"))
            else:
                rk, st = "—", "—"
            ref = dc.get("refus", {})
            upto = (rk - 1) if isinstance(rk, int) else min(10, len(cands))
            parts = []
            for c in cands[:upto]:
                r = ref.get(c["name"], ref.get("*", "?"))
                parts.append(f"{c['name']} ({r})")
            if not cands:
                parts = [dc.get("vide", "aucune réponse")]
            L.append(f"| {case} | {v['note']} | {ch or 'aucune'} | {vers.get(ch, '—') if ch else '—'} | {rk} | {st} | "
                     f"{' ; '.join(parts)} |")
            if ch:
                summary.append((lang, case, ch, "règle"))
        for nm in d.get("nommees", []):
            L.append("")
            L.append(f"Nommée par le dossier (3.3 c) : **{nm['nom']}** ({vers.get(nm['nom'], '?')}), pour "
                     f"{', '.join(nm['cases'])} ({nm.get('raison', '')}).")
            for c in nm["cases"]:
                summary.append((lang, c, nm["nom"], "nommée"))
        if d.get("cellules"):
            L += ["", "Cellules du plafond attribuées (3.4) :", ""]
            why = d.get("raisons_cellules", {})
            forms = d.get("formes", {})
            for lib, cells in d["cellules"].items():
                L.append(f"* {lib} : **{', '.join(cells) if cells else 'aucune'}** ({why.get(lib, '?')})")
                for cell in cells:
                    L.append(f"  * {cell} : {forms.get(lib, {}).get(cell, '?')}")
        L.append("")
    L += ["## Récapitulatif", "", "| Langage | Case | Bibliothèque | Version | Entrée | Cellules du plafond |",
          "|---|---|---|---|---|---|"]
    ncell = 0
    for lang, case, lib, how in summary:
        cells = dec[lang].get("cellules", {}).get(lib, [])
        L.append(f"| {NAMES[lang]} | {case} | {lib} | {dec[lang].get('versions', {}).get(lib, '?')} | {how} | "
                 f"{', '.join(cells) if cells else '—'} |")
    pairs = sorted({(lang, lib, c) for lang, case, lib, how in summary
                    for c in dec[lang].get("cellules", {}).get(lib, [])})
    L += ["", f"{len(summary)} entrées (case comblée) ; {len(pairs)} couples (bibliothèque, cellule du plafond) "
          f"dans {len({(l, b) for l, b, c in pairs})} bibliothèques de {len({l for l, b, c in pairs})} langages."]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("écrit :", OUT, len(summary), "entrées")
    missing = [ln for ln in L if "(?)" in ln or "| ? |" in ln]
    if missing:
        print("raisons ou versions manquantes :", len(missing))
        for ln in missing[:20]:
            print("  ", ln[:160])


if __name__ == "__main__":
    main()
