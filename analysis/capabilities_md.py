#!/usr/bin/env python3
"""Génère docs/CAPABILITIES.md à partir de analysis/capabilities.py (et de results/vectorization.json)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX, CATEGORIES, LABELS, M  # noqa: E402

ORDER = ["c", "cpp", "rust", "zig", "odin", "c3", "d", "nim", "ada", "fortran", "chapel", "mojo", "go",
         "csharp", "java", "julia", "haskell", "ocaml", "js", "python", "lua"]
SHORT = {"c": "C", "cpp": "C++", "rust": "Rust", "zig": "Zig", "odin": "Odin", "c3": "C3", "d": "D", "nim": "Nim",
         "ada": "Ada", "fortran": "Fortran", "chapel": "Chapel", "mojo": "Mojo", "go": "Go", "csharp": "C#",
         "java": "Java", "julia": "Julia", "haskell": "Haskell", "ocaml": "OCaml", "js": "JS", "python": "Python",
         "lua": "Lua"}


def main():
    vf = os.path.join(ROOT, "results", "vectorization.json")
    c3 = json.load(open(vf)) if os.path.exists(vf) else {}
    sym = {1: "●", 0.5: "◐", 0: "○", 1.0: "●", 0.0: "○"}
    out = ["# Matrice de capacités (pilier C)", "",
           "● = 1 (présente, documentée, vérifiée) · ◐ = 0,5 (partielle : expérimentale, propre à un compilateur, "
           "livrée hors norme ou limitée) · ○ = 0 (absente, ou seulement par une bibliothèque tierce ou une FFI).",
           "C3 est **mesurée** sur le code machine de la boucle chaude de K4 et de K9 en natural "
           "(`tools/c3_measure.py`). Les justifications et preuves de chaque cellule suivent le tableau.", "",
           "| Capacité | " + " | ".join(SHORT[l] for l in ORDER) + " |",
           "|---|" + "---|" * len(ORDER)]
    for cat, (w, caps) in CATEGORIES.items():
        out.append(f"| **{cat}** ({int(w * 100)} %) |" + " |" * len(ORDER))
        for c in caps:
            cells = []
            for l in ORDER:
                v = c3.get(l) if MATRIX[l][c] == M else MATRIX[l][c][0]
                cells.append(sym.get(v, "?") if v is not None else "?")
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
    open(os.path.join(ROOT, "docs", "CAPABILITIES.md"), "w").write("\n".join(out) + "\n")
    print("docs/CAPABILITIES.md écrit")


if __name__ == "__main__":
    main()
