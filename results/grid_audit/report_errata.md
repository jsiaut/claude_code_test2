# Audit de la grille : errata et sensibilité des cases discutables

Produit par `analysis/grid_audit_errata.py` (docs/V4_PLAN.md 2.3 ; docs/GRID_AUDIT.md, sections 3 et 4). Analyse globale de la v3 rejouée sur les données du classement publié, mêmes tirages.

Contrôle : le scénario Avant reproduit P-E de `results/php_check.json` (écart maximal 0.0e+00).

## Avant et après les errata

| Langage | Score avant | Score après | Écart | Place avant | Place après | Rang espéré avant | après |
|---|---|---|---|---|---|---|---|
| C | 79.96 | 79.96 | +0.00 | 1 | 1 | 2.20 | 2.20 |
| Odin | 74.02 | 74.02 | +0.00 | 2 | 2 | 3.17 | 3.17 |
| C++ | 77.12 | 77.12 | +0.00 | 3 | 3 | 3.79 | 3.79 |
| C3 | 71.64 | 71.64 | +0.00 | 4 | 4 | 5.11 | 5.11 |
| Zig | 72.30 | 72.30 | +0.00 | 5 | 5 | 5.14 | 5.13 |
| Rust | 69.95 | 69.95 | +0.00 | 6 | 6 | 6.97 | 6.96 |
| Nim | 69.30 | 69.30 | +0.00 | 7 | 7 | 7.16 | 7.17 |
| D | 72.65 | 72.65 | +0.00 | 8 | 8 | 7.19 | 7.19 |
| Ada | 71.06 | 71.06 | +0.00 | 9 | 9 | 8.30 | 8.30 |
| Chapel | 65.72 | 65.72 | +0.00 | 10 | 10 | 9.29 | 9.29 |
| Fortran | 65.44 | 65.44 | +0.00 | 11 | 11 | 10.85 | 10.85 |
| Swift | 66.45 | 66.45 | +0.00 | 12 | 12 | 10.86 | 10.86 |
| Julia | 62.36 | 62.36 | +0.00 | 13 | 13 | 12.15 | 12.15 |
| Mojo | 62.29 | 62.29 | +0.00 | 14 | 14 | 13.08 | 13.08 |
| C# | 54.88 | 54.88 | +0.00 | 15 | 15 | 15.30 | 15.30 |
| FreePascal | 48.06 | 48.06 | +0.00 | 16 | 16 | 16.73 | 16.74 |
| Java | 47.17 | 47.17 | +0.00 | 17 | 17 | 16.93 | 16.96 |
| Go | 45.37 | 45.37 | +0.00 | 18 | 18 | 17.12 | 17.14 |
| Haskell | 41.27 | 41.82 | +0.55 | 19 | 19 | 18.68 | 18.62 |
| OCaml | 23.92 | 23.92 | +0.00 | 20 | 20 | 20.31 | 20.31 |
| BQN | 17.72 | 17.72 | +0.00 | 21 | 21 | 21.17 | 21.17 |
| PHP | 16.56 | 16.56 | +0.00 | 22 | 22 | 22.32 | 22.32 |
| JavaScript | 15.63 | 15.63 | +0.00 | 23 | 23 | 22.34 | 22.34 |
| Python | 11.83 | 11.83 | +0.00 | 24 | 24 | 24.26 | 24.26 |
| Lua | 5.41 | 5.41 | +0.00 | 25 | 25 | 24.58 | 24.58 |

Étages : avant [14, 5, 6], après [14, 5, 6].

## Cases discutables : l'autre note, une à la fois (sur Après)

| Variante | Langages touchés : score (place) | Étages |
|---|---|---|
| Rust D4 et F4 à ½ (crate libc du sysroot, rustc_private) | Rust 69.95 → 70.91 (6e → 6e) ; places déplacées : Zig 5e → 4e, C3 4e → 5e | [14, 5, 6] |
| Zig C2 à 1 (extern fn au nom d'une intrinsèque de LLVM) | Zig 72.30 → 73.18 (5e → 4e) ; places déplacées : C3 4e → 5e | [14, 5, 6] |
| F2 à ½ par appel système brut (Odin, C, C++, Go, Zig, FreePascal) | C 79.96 → 80.40 (1e → 1e) ; C++ 77.12 → 77.56 (3e → 3e) ; Zig 72.30 → 72.74 (5e → 4e) ; Odin 74.02 → 74.46 (2e → 2e) ; Go 45.37 → 45.80 (18e → 18e) ; FreePascal 48.06 → 48.50 (16e → 16e) ; places déplacées : C3 4e → 5e | [14, 5, 6] |
| Nim E3 à 0 (clang, compilateur C du banc) | Nim 69.30 → 68.80 (7e → 8e) ; places déplacées : Fortran 11e → 12e, D 8e → 7e, Swift 12e → 11e | [14, 5, 6] |
| C B2 à 1 (obstack de la glibc) | C 79.96 → 80.66 (1e → 1e) | [14, 5, 6] |
| C et C++ F2 à ½ (trait d'allocateur OpenMP) | C 79.96 → 80.40 (1e → 1e) ; C++ 77.12 → 77.56 (3e → 3e) | [14, 5, 6] |
| B1 à ½ (C#, Java, Go, Lua : ramasse-miettes qu'on peut arrêter) | C# 54.88 → 55.58 (15e → 15e) ; Java 47.17 → 47.87 (17e → 17e) ; Go 45.37 → 46.07 (18e → 18e) ; Lua 5.41 → 6.11 (25e → 25e) | [14, 5, 6] |
| Java E6 à ½ (sun.misc.Unsafe) | Java 47.17 → 47.42 (17e → 17e) | [14, 5, 6] |
| Java F2 à ½ (-XX:+UseNUMA) | Java 47.17 → 47.61 (17e → 17e) | [14, 5, 6] |
| Toutes ensemble | C 79.96 → 81.10 (1e → 1e) ; C++ 77.12 → 77.56 (3e → 3e) ; C# 54.88 → 55.58 (15e → 15e) ; Java 47.17 → 48.56 (17e → 16e) ; Zig 72.30 → 73.62 (5e → 4e) ; Odin 74.02 → 74.46 (2e → 2e) ; Rust 69.95 → 70.91 (6e → 6e) ; Nim 69.30 → 68.80 (7e → 8e) ; Go 45.37 → 46.50 (18e → 18e) ; Lua 5.41 → 6.11 (25e → 25e) ; FreePascal 48.06 → 48.50 (16e → 17e) ; places déplacées : C3 4e → 5e, D 8e → 7e | [14, 5, 6] |
