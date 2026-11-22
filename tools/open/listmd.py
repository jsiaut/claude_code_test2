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
         "classée est refusée avec sa raison. Aucune sonde, aucune forme n'a été écrite avant ce relevé.*", ""]
    summary = []
    for lang in ORDER:
        p = os.path.join(REG, f"{lang}.json")
        if not os.path.exists(p) or lang not in dec:
            continue
        reg = json.load(open(p, encoding="utf-8"))
        d = dec[lang]
        L.append(f"## {NAMES[lang]}")
        L.append("")
        L.append(f"Registre : {reg.get('registre') or d.get('registre', '')} ; statistique : "
                 f"{reg.get('statistique', '—')}.")
        L.append("")
        if d.get("note"):
            L += [d["note"], ""]
        L.append("| Case | Note publiée | Retenue | Rang | Statistique | Refusées avant elle |")
        L.append("|---|---|---|---|---|---|")
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
            L.append(f"| {case} | {v['note']} | {ch or 'aucune'} | {rk} | {st} | {' ; '.join(parts)} |")
            if ch:
                summary.append((lang, case, ch, "règle"))
        for nm in d.get("nommees", []):
            L.append("")
            L.append(f"Nommée par le dossier (3.3 c) : **{nm['nom']}**, pour {', '.join(nm['cases'])} "
                     f"({nm.get('raison', '')}).")
            for c in nm["cases"]:
                summary.append((lang, c, nm["nom"], "nommée"))
        if d.get("cellules"):
            L += ["", "Cellules du plafond attribuées (3.4) :", ""]
            for lib, cells in d["cellules"].items():
                L.append(f"* {lib} : {', '.join(cells) if cells else 'aucune'}")
        L.append("")
    L += ["## Récapitulatif", "", "| Langage | Case | Bibliothèque | Entrée |", "|---|---|---|---|"]
    for lang, case, lib, how in summary:
        L.append(f"| {NAMES[lang]} | {case} | {lib} | {how} |")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("écrit :", OUT, len(summary), "entrées")


if __name__ == "__main__":
    main()
