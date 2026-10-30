"""Données de l'étude « Banc de sympathie mécanique » (pré-enregistrée le 22/09/2026, mesures des 22 et
23/09/2026), fournie par l'utilisateur le 30/10/2026. Transcription des seuls chiffres utilisés par la
confrontation (docs/CONFRONTATION.md), pour les 18 langages communs aux deux études.

Contrôle : banc_score(BANC_WEIGHTS) redonne leur score S publié au dixième près (vérifié par check()).
"""
import numpy as np

# Principes, dans l'ordre de leur grille, et poids = nombre de sources primaires qui les énoncent
PRINCIPLES = ["P1 accès prévisible", "P2 layout", "P3 SoA", "P4 faux partage", "P5 concurrence", "P6 batching/E-S",
              "P7 allocation", "P8 SIMD/ILP", "P9 branchements", "P10 hiérarchie mémoire", "P11 transparence",
              "P12 threads/topologie", "P13 hétérogène", "P14 files bornées"]
BANC_WEIGHTS = np.array([8, 6, 3, 5, 5, 5, 4, 4, 2, 5, 6, 7, 1, 3], float)

# Niveaux 0 à 4 (0 absent ; 1 seulement par des moyens non standard ; 2 standard partiel ; 3 premier ordre ;
# 4 premier ordre et imposé ou appliqué par défaut). Versions : Zig 0.16, Odin dev-2026-09, C++26 (GCC 16.1),
# D (LDC 1.43), C3 0.8, Rust 1.95, Ada 2022 (GNAT 16.1), C# 14 / .NET 10, Chapel 2.9, Nim 2.2, C23 (GCC 16.1),
# Java 25, Julia 1.13, Fortran 2023 (gfortran 13.3), Mojo 1.1, Python 3.14, Go 1.27, JavaScript (Node 26).
BANC_GRID = {
    "zig": [3, 4, 3, 4, 2, 2, 4, 3, 3, 4, 3, 4, 2, 3],
    "odin": [3, 3, 4, 2, 3, 2, 3, 3, 3, 3, 2, 4, 0, 3],
    "cpp": [4, 2, 2, 4, 3, 3, 3, 3, 3, 1, 3, 3, 1, 0],
    "d": [3, 3, 2, 2, 2, 3, 2, 3, 2, 3, 3, 4, 1, 2],
    "c3": [3, 3, 2, 2, 3, 2, 4, 3, 3, 3, 2, 3, 0, 2],
    "rust": [3, 3, 2, 2, 4, 2, 2, 2, 3, 3, 4, 2, 1, 2],
    "ada": [3, 4, 2, 2, 2, 2, 3, 1, 0, 0, 4, 3, 0, 3],
    "csharp": [3, 2, 2, 0, 3, 4, 1, 2, 2, 3, 2, 3, 0, 3],
    "chapel": [4, 2, 2, 0, 3, 3, 2, 2, 0, 1, 2, 4, 1, 2],
    "nim": [3, 3, 2, 2, 3, 3, 2, 1, 2, 0, 2, 3, 0, 2],
    "c": [3, 2, 2, 2, 3, 3, 2, 1, 1, 1, 3, 2, 1, 0],
    "java": [2, 2, 2, 1, 3, 4, 1, 1, 0, 0, 2, 3, 0, 4],
    "julia": [4, 0, 2, 0, 3, 2, 1, 2, 2, 1, 2, 3, 1, 2],
    "fortran": [4, 2, 2, 0, 2, 2, 2, 2, 4, 0, 2, 2, 1, 0],
    "mojo": [3, 2, 2, 0, 2, 0, 2, 3, 3, 4, 2, 1, 1, 0],
    "python": [2, 2, 2, 0, 0, 4, 0, 0, 0, 2, 0, 4, 0, 3],
    "go": [3, 0, 2, 0, 2, 2, 1, 1, 0, 0, 3, 2, 0, 3],
    "js": [2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 0, 2, 0, 2],
}
# Score S publié et rang publié parmi leurs 29 candidats (langages et DSL)
BANC_S = {"zig": 81.2, "odin": 71.5, "cpp": 68.4, "d": 68.4, "c3": 66.8, "rust": 66.4, "ada": 60.2, "csharp": 58.6,
          "chapel": 57.8, "nim": 55.9, "c": 52.3, "java": 49.6, "julia": 48.4, "fortran": 47.3, "mojo": 46.1,
          "python": 39.5, "go": 38.7, "js": 28.9}
BANC_RANK29 = {"zig": 1, "odin": 2, "cpp": 3, "d": 3, "c3": 5, "rust": 6, "ada": 7, "csharp": 8, "chapel": 9,
               "nim": 10, "c": 13, "java": 14, "julia": 15, "fortran": 16, "mojo": 17, "python": 21, "go": 22, "js": 27}
# Leur variante « extensions et instable comptés comme standard » : seul le top 10 est publié
BANC_EXT_TOP10 = ["zig", "cpp", "odin", "d", "rust", "c3", "c", "chapel", "ada", "csharp"]
COMMON = list(BANC_S)


def banc_score(weights, grid=BANC_GRID):
    w = np.asarray(weights, float)
    return {l: float(np.dot(w, g) / (4 * w.sum()) * 100) for l, g in grid.items()}


def check():
    s = banc_score(BANC_WEIGHTS)
    bad = {l: (round(s[l], 2), BANC_S[l]) for l in BANC_S if abs(s[l] - BANC_S[l]) > 0.051}
    if bad:
        raise SystemExit(f"transcription de la grille incohérente avec S : {bad}")


if __name__ == "__main__":
    check()
    print("grille transcrite : S recalculé = S publié pour les 18 langages")
