#!/usr/bin/env python3
"""Génère docs/CAPABILITIES.md à partir de analysis/capabilities.py, des reclassements de la règle v2
(analysis/capabilities_v2.py), des sondes exécutées (results/probes/*.txt) et de results/vectorization.json (C3)."""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX, CATEGORIES, LABELS, M  # noqa: E402
from capabilities_v2 import V2_OVERRIDES  # noqa: E402

ORDER = ["c", "cpp", "rust", "zig", "odin", "c3", "d", "nim", "ada", "fortran", "chapel", "mojo", "swift", "fpc", "go",
         "csharp", "java", "julia", "haskell", "ocaml", "js", "python", "lua", "bqn", "php"]
SHORT = {"c": "C", "cpp": "C++", "rust": "Rust", "zig": "Zig", "odin": "Odin", "c3": "C3", "d": "D", "nim": "Nim",
         "ada": "Ada", "fortran": "Fortran", "chapel": "Chapel", "mojo": "Mojo", "go": "Go", "csharp": "C#",
         "java": "Java", "julia": "Julia", "haskell": "Haskell", "ocaml": "OCaml", "js": "JS", "python": "Python",
         "lua": "Lua", "swift": "Swift", "fpc": "FPC", "bqn": "BQN", "php": "PHP"}


def main():
    vf = os.path.join(ROOT, "results", "vectorization.json")
    c3 = json.load(open(vf)) if os.path.exists(vf) else {}
    sym = {1: "●", 0.5: "◐", 0: "○", 1.0: "●", 0.0: "○"}
    out = ["# Matrice de capacités (pilier C)", "",
           "● = 1 (présente, documentée, vérifiée) · ◐ = 0,5 (partielle : expérimentale, propre à un compilateur, "
           "livrée hors norme ou limitée, ou seulement par les types C que définit une FFI livrée avec la chaîne) · "
           "○ = 0 (absente, ou seulement par une bibliothèque tierce, ou en appelant par une FFI du code C non "
           "intrinsèque).",
           "**Une seule règle pour la libc et les FFI** (`analysis/capabilities_v2.py`) : compte ce que la chaîne livre, "
           "y compris les intrinsèques et builtins du compilateur que le langage importe par sa FFI (Nim, Chapel, C3, "
           "Odin) ; ne compte pas l'appel de code C ordinaire par une FFI (la libc pour Rust, JavaScript, PHP ou BQN), "
           "sauf pour C et C++, dont la libc est la bibliothèque système.",
           "Le tableau donne la note de la règle v1 ; « ◐→● » marque une case que la règle v2 (score central) reclasse. "
           "C3 est **mesurée** sur le code machine de la boucle chaude de K4 et de K9 en natural "
           "(`results/vectorization.json`, mesure faite pendant la v3 ; la règle v2 ne compte pas C3). Les "
           "justifications et preuves de chaque cellule suivent le tableau ; l'état de preuve (sonde exécutée, "
           "mesure ou lecture des sources) est décompté à la fin.", "",
           "| Capacité | " + " | ".join(SHORT[l] for l in ORDER) + " |",
           "|---|" + "---|" * len(ORDER)]
    for cat, (w, caps) in CATEGORIES.items():
        out.append(f"| **{cat}** ({int(w * 100)} %) |" + " |" * len(ORDER))
        for c in caps:
            cells = []
            for l in ORDER:
                v = c3.get(l) if MATRIX[l][c] == M else MATRIX[l][c][0]
                s = sym.get(v, "?") if v is not None else "?"
                o = V2_OVERRIDES.get((l, c))
                if o and MATRIX[l][c] != M and o[0] != v:
                    s += "→" + sym.get(o[0], "?")
                cells.append(s)
            out.append(f"| {c} {LABELS[c]} | " + " | ".join(cells) + " |")
    out += ["", "## Justifications", ""]
    for l in ORDER:
        out.append(f"### {SHORT[l]}")
        out.append("")
        for cat, (w, caps) in CATEGORIES.items():
            items = []
            for c in caps:
                if MATRIX[l][c] == M:
                    v = c3.get(l)
                    items.append(f"{c} = {v if v is not None else '?'} (mesuré)")
                else:
                    v, why = MATRIX[l][c]
                    items.append(f"{c} = {v} ({why})")
            out.append(f"* **{cat}** : " + " ; ".join(items))
        out.append("")
    probed, tags = {}, {}
    for fn in glob.glob(os.path.join(ROOT, "results", "probes", "*.txt")):
        for line in open(fn, errors="replace"):
            p = line.rstrip("\n").split(";", 3)
            if len(p) == 4 and p[0] == "CAP":
                lang = os.path.basename(fn)[:-4]
                probed.setdefault(lang, set()).add(p[1])
                for t in ("exécutée", "échec", "recherche"):
                    if f"[{t}]" in p[3]:
                        tags.setdefault(lang, {}).setdefault(t, set()).add(p[1])
    out += ["## État de preuve", "",
            "Case **sondée** : une ligne `CAP` d'une sonde exécutée (`results/probes/<langage>.txt`), confrontée à la "
            "matrice par `analysis/check_probes.py` ; **mesurée** : C3 ; **lue** : justifiée par la seule lecture des "
            "sources ou de la documentation. Depuis l'audit de la grille (v4, point 1 : `docs/HISTORY.md` ; norme de "
            "preuve : `docs/METHOD.md`, 7), chaque preuve porte sa classe : **[exécutée]** (un programme se sert de la capacité "
            "et imprime un fait observable), **[échec]** (forme canonique refusée, ou comportement contraire mesuré), "
            "**[recherche]** (fouille des sources livrées ou de l'API publique avec un motif fixé d'avance, chaque "
            "résultat examiné). Une case peut porter plusieurs classes.", "",
            "| Langage | sondées | [exécutée] | [échec] | [recherche] | mesurées | lues |", "|---|---|---|---|---|---|---|"]
    tot = [0] * 6
    for l in ORDER:
        meas = {c for c, v in MATRIX[l].items() if v == M}
        pr = (probed.get(l, set()) & set(MATRIX[l])) - meas
        tg = tags.get(l, {})
        row = [len(pr), len(tg.get("exécutée", set()) & pr), len(tg.get("échec", set()) & pr),
               len(tg.get("recherche", set()) & pr), len(meas), len(MATRIX[l]) - len(pr) - len(meas)]
        tot = [a + b for a, b in zip(tot, row)]
        out.append(f"| {SHORT[l]} | " + " | ".join(str(x) for x in row) + " |")
    n = len(ORDER) * len(MATRIX[ORDER[0]])
    out.append(f"| **Total** | {tot[0]} | {tot[1]} | {tot[2]} | {tot[3]} | {tot[4]} | {tot[5]} ({100 * tot[5] / n:.0f} % des {n} cases) |")
    open(os.path.join(ROOT, "docs", "CAPABILITIES.md"), "w").write("\n".join(out) + "\n")
    print("docs/CAPABILITIES.md écrit")


if __name__ == "__main__":
    main()
