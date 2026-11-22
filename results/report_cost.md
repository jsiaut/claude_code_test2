# v4, point 5 : le coût d'accès au plafond — résultats

*Plan : `docs/V4_COST.md` (sections 3 à 5, fixées avant le comptage ; règles de lecture et écarts datés : sections 8 et 10). Généré par `analysis/cost_v4.py` à partir de `results/cost/counts.json` (`tools/cost/count.py`, relevé `tools/cost/regions.py`), de la campagne du point 4 (machine 33) et de `results/cost/compile.txt`. Le classement de tête du README ne change pas au point 5.*

Contrôle : le calcul « Convergent, avec R4 » refait ici est identique à celui du point 4 (même ordre : oui ; écart maximal des rangs espérés 0.00e+00, des scores au centre 0.00e+00).

## Calcul 2 : par langage

L/N : moyenne géométrique sur les 12 cellules du rapport des lignes de la forme d'accès à celles du code naturel ; parts pondérées par les lignes ; atteintes : cellules à 0,9 ou plus de la frontière.

| Langage | L/N | Lignes ajoutées | Sans vérif. (abs.) | Sans vérif. (marg.) | Archi. | Non portables | Atteintes | Indice d'accès |
|---|---|---|---|---|---|---|---|---|
| Mojo | 2,33 | 189 | 0,16 | 0,16 | 0,00 | 0 | 8 | 0,497 |
| Odin | 3,73 | 318 | 0,50 | 0,50 | 0,00 | 0 | 8 | 0,402 |
| C3 | 3,70 | 476 | 1,00 | 0,00 | 0,00 | 0 | 8 | 0,314 |
| C++ | 3,45 | 295 | 1,00 | 0,00 | 0,02 | 1 | 7 | 0,285 |
| Julia | 6,45 | 1020 | 0,87 | 0,87 | 0,00 | 0 | 5 | 0,271 |
| Swift | 3,20 | 411 | 0,33 | 0,33 | 0,00 | 0 | 4 | 0,243 |
| Java | 4,81 | 313 | 0,00 | 0,00 | 0,00 | 0 | 3 | 0,240 |
| Nim | 6,88 | 560 | 0,39 | 0,39 | 0,19 | 9 | 8 | 0,239 |
| Zig | 3,71 | 391 | 1,00 | 0,01 | 0,00 | 0 | 6 | 0,239 |
| Rust | 5,14 | 549 | 0,39 | 0,39 | 0,16 | 9 | 8 | 0,218 |
| Chapel | 3,82 | 329 | 1,00 | 0,16 | 0,47 | 8 | 8 | 0,169 |
| C# | 3,66 | 253 | 0,27 | 0,27 | 0,03 | 6 | 3 | 0,168 |
| Ada | 3,62 | 568 | 0,50 | 0,50 | 0,05 | 6 | 5 | 0,164 |
| D | 5,39 | 375 | 1,00 | 0,06 | 0,00 | 1 | 5 | 0,163 |
| C | 3,52 | 318 | 1,00 | 0,00 | 0,25 | 9 | 9 | 0,160 |
| Fortran | 1,87 | 120 | 1,00 | 0,00 | 0,00 | 0 | 3 | 0,130 |
| Go | 2,61 | 262 | 0,00 | 0,00 | 0,12 | 7 | 3 | 0,116 |
| FreePascal | 4,16 | 722 | 1,00 | 0,03 | 0,00 | 0 | 1 | 0,056 |
| Haskell | 2,35 | 156 | 0,25 | 0,25 | 0,00 | 0 | 1 | 0,052 |
| JavaScript | 3,33 | 147 | 0,00 | 0,00 | 0,00 | 0 | 0 | 0,000 |
| Python | 1,47 | 180 | 0,00 | 0,00 | 0,00 | 0 | 0 | 0,000 |
| OCaml | 2,42 | 171 | 0,19 | 0,19 | 0,00 | 0 | 0 | 0,000 |
| Lua | 1,30 | 31 | 0,00 | 0,00 | 0,00 | 0 | 0 | 0,000 |
| BQN | 1,50 | 22 | 0,00 | 0,00 | 0,00 | 0 | 0 | 0,000 |
| PHP | 1,79 | 245 | 0,00 | 0,00 | 0,00 | 0 | 0 | 0,000 |

## Calcul 3 : corrélations de rang (Spearman, 25 langages)

| Quantité | Catégorie C | Catégorie E | Pilier contrôle | Plafond (avec R4) |
|---|---|---|---|---|
| L/N (moyenne géométrique) | 0,54 | 0,59 | 0,58 | 0,60 |
| lignes ajoutées | 0,55 | 0,66 | 0,65 | 0,58 |
| part sans vérification (absolue) | 0,64 | 0,70 | 0,76 | 0,78 |
| part sans vérification (marginale) | 0,37 | 0,51 | 0,34 | 0,24 |
| part propre à une architecture | 0,45 | 0,45 | 0,44 | 0,54 |
| cellules non portables | 0,47 | 0,47 | 0,46 | 0,52 |
| indice d'accès | 0,69 | 0,68 | 0,71 | 0,73 |

## Calculs 4 et 5 : scénario « Accès » et sensibilités (à côté du classement)

Places ; « Convergent, avec R4 » : le calcul du point 4 ; « Accès » : chaque capacité des catégories C et E vaut l'indice d'accès ; (a) à (f) : sensibilités (section 5 du plan ; (f) : 3.3).

| Langage | Publié | Convergent, avec R4 | Accès | (a) | (b) | (c) | (d) | (e) | (f) | Indice |
|---|---|---|---|---|---|---|---|---|---|---|
| Zig | 5 | 2 | 1 | 2 | 2 | 1 | 1 | 5 | 1 | 0,239 |
| C++ | 3 | 1 | 2 | 1 | 1 | 3 | 2 | 3 | 2 | 0,285 |
| Odin | 2 | 5 | 3 | 5 | 5 | 2 | 3 | 1 | 3 | 0,402 |
| C | 1 | 3 | 4 | 3 | 4 | 4 | 4 | 8 | 4 | 0,160 |
| C3 | 4 | 4 | 5 | 4 | 3 | 5 | 5 | 2 | 5 | 0,314 |
| Nim | 7 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 0,239 |
| Rust | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 0,218 |
| D | 8 | 8 | 8 | 9 | 8 | 8 | 9 | 12 | 8 | 0,163 |
| Chapel | 10 | 9 | 9 | 8 | 9 | 9 | 8 | 10 | 9 | 0,169 |
| Mojo | 14 | 13 | 10 | 10 | 10 | 11 | 10 | 4 | 10 | 0,497 |
| Fortran | 11 | 11 | 11 | 11 | 11 | 12 | 11 | 14 | 11 | 0,130 |
| Ada | 9 | 10 | 12 | 12 | 12 | 13 | 12 | 15 | 12 | 0,164 |
| Swift | 12 | 14 | 13 | 13 | 14 | 10 | 13 | 11 | 13 | 0,243 |
| Julia | 13 | 12 | 14 | 14 | 13 | 14 | 14 | 9 | 14 | 0,271 |
| C# | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 16 | 15 | 0,168 |
| Java | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 13 | 16 | 0,240 |
| Go | 18 | 17 | 17 | 17 | 18 | 17 | 17 | 17 | 17 | 0,116 |
| FreePascal | 16 | 18 | 18 | 18 | 17 | 18 | 18 | 19 | 18 | 0,056 |
| Haskell | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 18 | 19 | 0,052 |
| OCaml | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 21 | 20 | 0,000 |
| BQN | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 22 | 21 | 0,000 |
| JavaScript | 23 | 22 | 22 | 22 | 22 | 22 | 22 | 20 | 22 | 0,000 |
| PHP | 22 | 23 | 23 | 23 | 23 | 23 | 23 | 25 | 23 | 0,000 |
| Python | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 23 | 24 | 0,000 |
| Lua | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 24 | 25 | 0,000 |

Rangs espérés, rang plausible (90 %), score au centre :

| Langage | Convergent, avec R4 : rang espéré | plausible | score | Accès : rang espéré | plausible | score |
|---|---|---|---|---|---|---|
| Zig | 2,87 | 1–6 | 78,7 | 2,83 | 1–6 | 73,3 |
| C++ | 2,45 | 1–6 | 81,9 | 2,97 | 1–6 | 74,4 |
| Odin | 5,39 | 2–9 | 75,0 | 3,60 | 1–8 | 72,4 |
| C | 2,88 | 1–7 | 80,6 | 3,98 | 1–8 | 72,1 |
| C3 | 5,19 | 2–9 | 73,5 | 4,32 | 2–7 | 70,3 |
| Nim | 5,50 | 2–9 | 74,5 | 4,94 | 1–8 | 70,0 |
| Rust | 6,51 | 3–10 | 73,3 | 7,21 | 4–11 | 67,7 |
| D | 7,18 | 3–11 | 75,2 | 9,17 | 6–13 | 66,4 |
| Chapel | 9,59 | 5–14 | 69,0 | 9,57 | 5–14 | 65,3 |
| Mojo | 12,20 | 9–14 | 67,3 | 10,23 | 6–14 | 64,6 |
| Fortran | 11,13 | 7–14 | 67,3 | 11,14 | 7–14 | 63,4 |
| Ada | 11,06 | 7–14 | 70,7 | 11,56 | 8–14 | 64,5 |
| Swift | 12,30 | 9–14 | 67,0 | 11,85 | 8–14 | 63,2 |
| Julia | 11,18 | 8–14 | 67,7 | 11,97 | 8–14 | 61,6 |
| C# | 14,87 | 13–16 | 62,3 | 15,14 | 14–16 | 57,1 |
| Java | 16,31 | 15–18 | 55,3 | 16,05 | 15–18 | 54,1 |
| Go | 17,30 | 16–18 | 51,1 | 17,27 | 16–18 | 49,0 |
| FreePascal | 17,39 | 15–19 | 49,3 | 17,45 | 15–19 | 46,1 |
| Haskell | 18,72 | 18–19 | 44,7 | 18,78 | 18–19 | 41,8 |
| OCaml | 20,25 | 20–22 | 23,2 | 20,23 | 20–22 | 22,2 |
| BQN | 21,44 | 20–23 | 16,7 | 21,59 | 20–23 | 15,5 |
| JavaScript | 22,13 | 21–24 | 16,4 | 22,12 | 21–24 | 15,7 |
| PHP | 22,33 | 20–23 | 16,7 | 22,19 | 20–23 | 16,2 |
| Python | 24,09 | 23–25 | 12,3 | 24,12 | 23–25 | 11,2 |
| Lua | 24,73 | 24–25 | 5,8 | 24,72 | 24–25 | 5,8 |

Plus de deux places par rapport à « Convergent, avec R4 » :

* Accès : Mojo 13 → 10
* (a) part marginale : Mojo 13 → 10
* (b) sans part sans vérification : Mojo 13 → 10
* (c) seuil 0,8 : Odin 5 → 2, Swift 14 → 10, Ada 10 → 13
* (d) forme la plus courte à 10 % : Mojo 13 → 10
* (e) grille entière remplacée : Odin 5 → 1, Mojo 13 → 4, Zig 2 → 5, C 3 → 8, Julia 12 → 9, Swift 14 → 11, D 8 → 12, Java 16 → 13, Fortran 11 → 14, Ada 10 → 15
* (f) lexèmes : Mojo 13 → 10

Sensibilités, plus de deux places par rapport à « Accès » :

* (a) part marginale : aucun
* (b) sans part sans vérification : aucun
* (c) seuil 0,8 : Swift 13 → 10
* (d) forme la plus courte à 10 % : aucun
* (e) grille entière remplacée : C3 5 → 2, Mojo 10 → 4, Zig 1 → 5, C 4 → 8, Julia 14 → 9, D 8 → 12, Java 16 → 13, Fortran 11 → 14, Ada 12 → 15
* (f) lexèmes : aucun

Étages indicatifs (règle v3 sans sa condition de réplication) :

* Convergent, avec R4 : C++, Zig, C, C3, Odin, Nim, Rust, D, Chapel, Ada, Fortran, Julia, Mojo, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Accès : Zig, C++, Odin, C, C3, Nim, Rust, D, Chapel, Mojo, Fortran, Ada, Swift, Julia, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

## Compilation pour aarch64 et riscv64 (3.5)

Prévision : le fichier compile hors x86 si et seulement si l'examen statique n'y trouve aucune ligne propre à une architecture. Une cible n'est interprétée que si la compilation de contrôle (x86_64, même outil) passe.

| Langage | Contrôle x86_64 | aarch64 | riscv64 | Prévision | Accord |
|---|---|---|---|---|---|
| C | compile | refus | refus | refus | aarch64 oui, riscv64 oui |
| C++ | refus | refus | refus | refus | – |
| Zig | compile | compile | compile | compile | aarch64 oui, riscv64 oui |
| Odin | compile | compile | compile | compile | aarch64 oui, riscv64 oui |
| Fortran | compile | compile | compile | compile | aarch64 oui, riscv64 oui |
| C3 | compile | compile | compile | compile | aarch64 oui, riscv64 oui |
| D | compile | refus | refus | refus | aarch64 oui, riscv64 oui |
| Nim | compile | refus | refus | refus | aarch64 oui, riscv64 oui |
| Mojo | compile | compile | compile | compile | aarch64 oui, riscv64 oui |
| Go | compile | refus | refus | refus | aarch64 oui, riscv64 oui |

Premières erreurs :

* C, aarch64 : `/opt/zig/lib/include/immintrin.h:14:2: error: "This header is only meant to be used on x86 and x64 architecture"`
* C, riscv64 : `/opt/zig/lib/include/immintrin.h:14:2: error: "This header is only meant to be used on x86 and x64 architecture"`
* C++, aarch64 : `ms.cpp:22:10: fatal error: 'simd' file not found`
* C++, riscv64 : `ms.cpp:22:10: fatal error: 'simd' file not found`
* C++, x86_64 : `ms.cpp:22:10: fatal error: 'simd' file not found`
* D, aarch64 : `LLVM ERROR: Do not know how to split the result of this operator!`
* D, riscv64 : `LLVM ERROR: Do not know how to split the result of this operator!`
* Nim, aarch64 : `/opt/zig/lib/include/immintrin.h:14:2: error: "This header is only meant to be used on x86 and x64 architecture"`
* Nim, riscv64 : `/opt/zig/lib/include/immintrin.h:14:2: error: "This header is only meant to be used on x86 and x64 architecture"`
* Go, aarch64 : `./ms.go:97:17: undefined: archsimd.BroadcastFloat64x8`
* Go, riscv64 : `./ms.go:97:17: undefined: archsimd.BroadcastFloat64x8`

## Julia, Q1 `tuned_v` : IR écrit par un générateur (section 8)

IR dans la source : 321 lignes de code ; générateur (`tools/converge/gen_julia_ir.py`) : 213.
* Q1 (`tuned_v q1`) : L = 344, N = 9, s = 0,97 ; avec le générateur à la place de l'IR, L = 236, s = 0,96.

## Calcul 1 : par langage et par cellule

Forme d'accès (calcul principal), L et N (lignes de code de la forme et de la référence naturelle), s, parts sans vérification (absolue ; marginale), lignes propres à une architecture (X), rapport frontière / langage (« atteinte » à 0,9 ou plus).

### C

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 24 | 6 | 18 | 0,75 | 1,00 ; 0,00 | 10 | 0,98 |
| K3 | `sw_padded` | 18 | 18 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 0,97 |
| K4 | `tuned` | 14 | 6 | 8 | 0,57 | 1,00 ; 0,00 | 6 | 0,97 |
| K5 | `tuned` | 10 | 5 | 5 | 0,50 | 1,00 ; 0,00 | 6 | 0,94 |
| Q6 | `tuned_v q6` | 24 | 7 | 17 | 0,71 | 1,00 ; 0,00 | 12 | 0,92 |
| Q1 | `tuned q1` | 53 | 13 | 40 | 0,75 | 1,00 ; 0,00 | 24 | 0,94 |
| Q6 mt | `mt_pool_v q6` | 77 | 7 | 70 | 0,91 | 1,00 ; 0,00 | 12 | 0,91 |
| Q1 mt | `mt q1` | 72 | 13 | 59 | 0,82 | 1,00 ; 0,00 | 24 | 0,90 |
| K7 | `tuned` | 18 | 11 | 7 | 0,39 | 1,00 ; 0,00 | 0 | 0,90 |
| K8 | `tuned_it` | 38 | 10 | 28 | 0,74 | 1,00 ; 0,00 | 0 | 0,59 |
| K9 | `tuned_v` | 15 | 5 | 10 | 0,67 | 1,00 ; 0,00 | 5 | 0,95 |
| K9 mt | `mt_pool_v` | 61 | 5 | 56 | 0,92 | 1,00 ; 0,00 | 5 | 0,80 |

### C++

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 24 | 6 | 18 | 0,75 | 1,00 ; 0,00 | 0 | 0,98 |
| K3 | `sw_padded` | 15 | 15 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 1,00 |
| K4 | `tuned` | 16 | 6 | 10 | 0,62 | 1,00 ; 0,00 | 6 | 0,90 |
| K5 | `tuned` | 11 | 5 | 6 | 0,55 | 1,00 ; 0,00 | 0 | 1,00 |
| Q6 | `tuned q6` | 25 | 6 | 19 | 0,76 | 1,00 ; 0,00 | 0 | 0,91 |
| Q1 | `tuned q1` | 50 | 13 | 37 | 0,74 | 1,00 ; 0,00 | 0 | 0,79 |
| Q6 mt | `mt_pool q6` | 64 | 6 | 58 | 0,91 | 1,00 ; 0,00 | 0 | 0,79 |
| Q1 mt | `mt_pool q1` | 89 | 13 | 76 | 0,85 | 1,00 ; 0,00 | 0 | 0,67 |
| K7 | `tuned` | 18 | 7 | 11 | 0,61 | 1,00 ; 0,00 | 0 | 0,98 |
| K8 | `tuned_val` | 14 | 8 | 6 | 0,43 | 1,00 ; 0,00 | 0 | 1,00 |
| K9 | `tuned_v` | 17 | 6 | 11 | 0,65 | 1,00 ; 0,00 | 0 | 0,95 |
| K9 mt | `mt_pool_v` | 49 | 6 | 43 | 0,88 | 1,00 ; 0,00 | 0 | 0,75 |

### C#

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 22 | 17 | 5 | 0,23 | 0,77 ; 0,77 | 0 | 1,00 |
| K3 | `sw_padded` | 15 | 15 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,97 |
| K4 | `tuned` | 19 | 2 | 17 | 0,89 | 0,05 ; 0,05 | 2 | 0,96 |
| K5 | `tuned` | 22 | 2 | 20 | 0,91 | 0,95 ; 0,95 | 0 | 0,81 |
| Q6 | `tuned q6` | 27 | 8 | 19 | 0,70 | 0,07 ; 0,07 | 1 | 0,81 |
| Q1 | `tuned q1` | 57 | 13 | 44 | 0,77 | 0,09 ; 0,09 | 3 | 0,62 |
| Q6 mt | `mt_pool q6` | 35 | 8 | 27 | 0,77 | 0,06 ; 0,06 | 1 | 0,48 |
| Q1 mt | `mt q1` | 71 | 13 | 58 | 0,82 | 0,07 ; 0,07 | 3 | 0,52 |
| K7 | `tuned` | 17 | 6 | 11 | 0,65 | 0,82 ; 0,82 | 1 | 0,76 |
| K8 | `tuned_it` | 41 | 3 | 38 | 0,93 | 0,05 ; 0,05 | 0 | 0,39 |
| K9 | `tuned` | 15 | 9 | 6 | 0,40 | 0,93 ; 0,93 | 0 | 0,75 |
| K9 mt | `mt_pool` | 17 | 9 | 8 | 0,47 | 0,88 ; 0,88 | 0 | 0,40 |

### Java

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 20 | 13 | 7 | 0,35 | 0,00 ; 0,00 | 0 | 0,97 |
| K3 | `sw_padded` | 15 | 15 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,95 |
| K4 | `tuned` | 22 | 1 | 21 | 0,95 | 0,00 ; 0,00 | 0 | 0,85 |
| K5 | `tuned` | 19 | 1 | 18 | 0,95 | 0,00 ; 0,00 | 0 | 0,71 |
| Q6 | `tuned q6` | 23 | 6 | 17 | 0,74 | 0,00 ; 0,00 | 0 | 0,85 |
| Q1 | `tuned_v q1` | 75 | 9 | 66 | 0,88 | 0,00 ; 0,00 | 0 | 0,84 |
| Q6 mt | `mt q6` | 35 | 6 | 29 | 0,83 | 0,00 ; 0,00 | 0 | 0,59 |
| Q1 mt | `mt_pool_v q1` | 99 | 9 | 90 | 0,91 | 0,00 ; 0,00 | 0 | 0,72 |
| K7 | `rq_iso` | 13 | 6 | 7 | 0,54 | 0,00 ; 0,00 | 0 | 0,75 |
| K8 | `tuned_it` | 30 | 3 | 27 | 0,90 | 0,00 ; 0,00 | 0 | 0,51 |
| K9 | `natural` | 7 | 7 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,98 |
| K9 mt | `mt_pool_v` | 38 | 7 | 31 | 0,82 | 0,00 ; 0,00 | 0 | 0,62 |

### Zig

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 26 | 5 | 21 | 0,81 | 1,00 ; 0,00 | 0 | 0,88 |
| K3 | `sw_padded` | 19 | 19 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 0,94 |
| K4 | `tuned` | 24 | 7 | 17 | 0,71 | 1,00 ; 0,00 | 0 | 1,00 |
| K5 | `tuned` | 13 | 5 | 8 | 0,62 | 1,00 ; 0,00 | 0 | 0,82 |
| Q6 | `tuned q6` | 14 | 7 | 7 | 0,50 | 1,00 ; 0,00 | 0 | 0,96 |
| Q1 | `tuned q1` | 41 | 14 | 27 | 0,66 | 1,00 ; 0,00 | 0 | 1,00 |
| Q6 mt | `mt_pool q6` | 83 | 7 | 76 | 0,92 | 1,00 ; 0,01 | 0 | 0,87 |
| Q1 mt | `mt_pool q1` | 110 | 14 | 96 | 0,87 | 1,00 ; 0,01 | 0 | 0,93 |
| K7 | `tuned` | 21 | 8 | 13 | 0,62 | 1,00 ; 0,00 | 0 | 0,89 |
| K8 | `tuned_it` | 56 | 19 | 37 | 0,66 | 1,00 ; 0,00 | 0 | 0,77 |
| K9 | `tuned` | 21 | 7 | 14 | 0,67 | 1,00 ; 0,00 | 0 | 0,93 |
| K9 mt | `mt_pool` | 82 | 7 | 75 | 0,91 | 1,00 ; 0,01 | 0 | 0,73 |

### Odin

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 23 | 5 | 18 | 0,78 | 0,87 ; 0,87 | 0 | 0,67 |
| K3 | `sw_padded` | 24 | 24 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,96 |
| K4 | `tuned` | 20 | 5 | 15 | 0,75 | 0,00 ; 0,00 | 0 | 0,97 |
| K5 | `tuned` | 11 | 5 | 6 | 0,55 | 1,00 ; 1,00 | 0 | 0,93 |
| Q6 | `tuned q6` | 15 | 7 | 8 | 0,53 | 1,00 ; 1,00 | 0 | 0,90 |
| Q1 | `tuned_v q1` | 37 | 14 | 23 | 0,62 | 1,00 ; 1,00 | 0 | 0,99 |
| Q6 mt | `mt_pool q6` | 66 | 7 | 59 | 0,89 | 0,29 ; 0,29 | 0 | 0,98 |
| Q1 mt | `mt_pool_v q1` | 88 | 14 | 74 | 0,84 | 0,47 ; 0,47 | 0 | 1,00 |
| K7 | `tuned` | 22 | 8 | 14 | 0,64 | 0,00 ; 0,00 | 0 | 0,84 |
| K8 | `tuned_it` | 51 | 13 | 38 | 0,75 | 0,80 ; 0,80 | 0 | 0,70 |
| K9 | `tuned` | 14 | 4 | 10 | 0,71 | 0,86 ; 0,86 | 0 | 0,94 |
| K9 mt | `mt_pool` | 57 | 4 | 53 | 0,93 | 0,28 ; 0,28 | 0 | 0,81 |

### Julia

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 8 | 7 | 1 | 0,12 | 0,38 ; 0,38 | 0 | 0,99 |
| K3 | `sw_padded` | 17 | 17 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,96 |
| K4 | `tuned` | 32 | 9 | 23 | 0,72 | 0,50 ; 0,50 | 0 | 0,90 |
| K5 | `tuned_v` | 51 | 7 | 44 | 0,86 | 0,96 ; 0,96 | 0 | 0,87 |
| Q6 | `tuned_v q6` | 62 | 9 | 53 | 0,85 | 0,74 ; 0,74 | 0 | 0,94 |
| Q1 | `tuned_v q1` | 344 | 9 | 335 | 0,97 | 0,94 ; 0,94 | 0 | 0,98 |
| Q6 mt | `mt_pool_v q6` | 67 | 9 | 58 | 0,87 | 0,69 ; 0,69 | 0 | 0,49 |
| Q1 mt | `mt_pool_v q1` | 349 | 9 | 340 | 0,97 | 0,93 ; 0,93 | 0 | 0,85 |
| K7 | `tuned_pf` | 24 | 6 | 18 | 0,75 | 0,75 ; 0,75 | 0 | 0,84 |
| K8 | `tuned_it` | 35 | 11 | 24 | 0,69 | 0,63 ; 0,63 | 0 | 0,68 |
| K9 | `tuned_v` | 66 | 5 | 61 | 0,92 | 0,98 ; 0,98 | 0 | 0,56 |
| K9 mt | `mt_pool_v` | 68 | 5 | 63 | 0,93 | 0,96 ; 0,96 | 0 | 0,30 |

### Ada

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 36 | 8 | 28 | 0,78 | 0,53 ; 0,53 | 0 | 0,60 |
| K3 | `sw_padded` | 57 | 57 | 0 | 0,00 | 1,00 ; 1,00 | 0 | 1,00 |
| K4 | `tuned` | 35 | 10 | 25 | 0,71 | 0,03 ; 0,03 | 4 | 0,89 |
| K5 | `tuned` | 32 | 8 | 24 | 0,75 | 0,84 ; 0,84 | 2 | 0,69 |
| Q6 | `tuned_v q6` | 63 | 10 | 53 | 0,84 | 0,56 ; 0,56 | 6 | 0,89 |
| Q1 | `tuned_v q1` | 114 | 17 | 97 | 0,85 | 0,61 ; 0,61 | 10 | 0,97 |
| Q6 mt | `mt_pool_v q6` | 128 | 10 | 118 | 0,92 | 0,27 ; 0,27 | 6 | 0,92 |
| Q1 mt | `mt_pool_v q1` | 179 | 17 | 162 | 0,91 | 0,39 ; 0,39 | 10 | 0,91 |
| K7 | `tuned` | 35 | 21 | 14 | 0,40 | 0,77 ; 0,77 | 0 | 0,95 |
| K8 | `tuned` | 28 | 27 | 1 | 0,04 | 0,82 ; 0,82 | 0 | 0,85 |
| K9 | `tuned` | 10 | 8 | 2 | 0,20 | 1,00 ; 1,00 | 0 | 0,75 |
| K9 mt | `mt_pool` | 52 | 8 | 44 | 0,85 | 0,19 ; 0,19 | 0 | 0,63 |

### Fortran

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 25 | 8 | 17 | 0,68 | 1,00 ; 0,00 | 0 | 1,00 |
| K3 | `sw_padded` | 20 | 20 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 0,99 |
| K4 | `swar` | 25 | 9 | 16 | 0,64 | 1,00 ; 0,00 | 0 | 0,78 |
| K5 | `rq_acc16` | 13 | 4 | 9 | 0,69 | 1,00 ; 0,00 | 0 | 0,61 |
| Q6 | `tuned q6` | 12 | 8 | 4 | 0,33 | 1,00 ; 0,00 | 0 | 0,87 |
| Q1 | `tuned q1` | 34 | 18 | 16 | 0,47 | 1,00 ; 0,00 | 0 | 0,66 |
| Q6 mt | `mt q6` | 23 | 8 | 15 | 0,65 | 1,00 ; 0,00 | 0 | 0,91 |
| Q1 mt | `mt q1` | 45 | 18 | 27 | 0,60 | 1,00 ; 0,00 | 0 | 0,67 |
| K7 | `tuned_oa` | 19 | 28 | -9 | 0,00 | 1,00 ; 0,00 | 0 | 0,86 |
| K8 | `tuned_val` | 32 | 31 | 1 | 0,03 | 1,00 ; 0,00 | 0 | 0,85 |
| K9 | `natural` | 7 | 7 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 0,80 |
| K9 mt | `mt` | 31 | 7 | 24 | 0,77 | 1,00 ; 0,00 | 0 | 0,59 |

### JavaScript

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 11 | 11 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,16 |
| K3 | `rmw_padded` | 24 | 24 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,17 |
| K4 | `tuned` | 18 | 1 | 17 | 0,94 | 0,00 ; 0,00 | 0 | 0,09 |
| K5 | `rq_f64` | 9 | 1 | 8 | 0,89 | 0,00 ; 0,00 | 0 | 0,03 |
| Q6 | `tuned_s q6` | 12 | 5 | 7 | 0,58 | 0,00 ; 0,00 | 0 | 0,21 |
| Q1 | `natural q1` | 9 | 9 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,08 |
| Q6 mt | `mt_pool_s q6` | 40 | 5 | 35 | 0,88 | 0,00 ; 0,00 | 0 | 0,10 |
| Q1 mt | `mt q1` | 40 | 9 | 31 | 0,78 | 0,00 ; 0,00 | 0 | 0,06 |
| K7 | `tuned` | 8 | 5 | 3 | 0,38 | 0,00 ; 0,00 | 0 | 0,21 |
| K8 | `tuned_it` | 20 | 2 | 18 | 0,90 | 0,00 ; 0,00 | 0 | 0,19 |
| K9 | `rq_slide` | 10 | 6 | 4 | 0,40 | 0,00 ; 0,00 | 0 | 0,24 |
| K9 mt | `rq_slide_mt` | 30 | 6 | 24 | 0,80 | 0,00 ; 0,00 | 0 | 0,21 |

### Python

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 4 | 13 | -9 | 0,00 | 0,00 ; 0,00 | 0 | 0,00 |
| K3 | `sw_padded` | 37 | 37 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,04 |
| K4 | `tuned` | 3 | 6 | -3 | 0,00 | 0,00 ; 0,00 | 0 | 0,01 |
| K5 | `tuned` | 1 | 5 | -4 | 0,00 | 0,00 ; 0,00 | 0 | 0,00 |
| Q6 | `rq_cols q6` | 19 | 7 | 12 | 0,63 | 0,00 ; 0,00 | 0 | 0,02 |
| Q1 | `tuned q1` | 12 | 13 | -1 | 0,00 | 0,00 ; 0,00 | 0 | 0,00 |
| Q6 mt | `rq_cols_mt q6` | 82 | 7 | 75 | 0,91 | 0,00 ; 0,00 | 0 | 0,02 |
| Q1 mt | `mt_pool q1` | 74 | 13 | 61 | 0,82 | 0,00 ; 0,00 | 0 | 0,00 |
| K7 | `tuned_oa` | 18 | 8 | 10 | 0,56 | 0,00 ; 0,00 | 0 | 0,02 |
| K8 | `tuned_val` | 13 | 13 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,01 |
| K9 | `natural` | 5 | 5 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,01 |
| K9 mt | `mt` | 44 | 5 | 39 | 0,89 | 0,00 ; 0,00 | 0 | 0,01 |

### Haskell

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 23 | 8 | 15 | 0,65 | 0,35 ; 0,35 | 0 | 0,79 |
| K3 | `rmw_padded` | 20 | 20 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,33 |
| K4 | `tuned` | 33 | 3 | 30 | 0,91 | 0,09 ; 0,09 | 0 | 0,47 |
| K5 | `tuned` | 15 | 7 | 8 | 0,53 | 0,20 ; 0,20 | 0 | 0,80 |
| Q6 | `tuned q6` | 10 | 10 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,55 |
| Q1 | `tuned q1` | 19 | 17 | 2 | 0,11 | 0,16 ; 0,16 | 0 | 0,44 |
| Q6 mt | `mt q6` | 12 | 10 | 2 | 0,17 | 0,00 ; 0,00 | 0 | 0,20 |
| Q1 mt | `mt q1` | 21 | 17 | 4 | 0,19 | 0,14 ; 0,14 | 0 | 0,31 |
| K7 | `tuned` | 23 | 7 | 16 | 0,70 | 0,43 ; 0,43 | 0 | 0,92 |
| K8 | `tuned_it` | 46 | 7 | 39 | 0,85 | 0,41 ; 0,41 | 0 | 0,68 |
| K9 | `tuned` | 24 | 8 | 16 | 0,67 | 0,42 ; 0,42 | 0 | 0,59 |
| K9 mt | `mt` | 32 | 8 | 24 | 0,75 | 0,31 ; 0,31 | 0 | 0,27 |

### C3

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 30 | 6 | 24 | 0,80 | 1,00 ; 0,00 | 0 | 0,98 |
| K3 | `sw_padded` | 27 | 27 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 1,00 |
| K4 | `tuned` | 21 | 6 | 15 | 0,71 | 1,00 ; 0,00 | 0 | 0,98 |
| K5 | `tuned` | 12 | 6 | 6 | 0,50 | 1,00 ; 0,00 | 0 | 0,79 |
| Q6 | `tuned q6` | 27 | 9 | 18 | 0,67 | 1,00 ; 0,00 | 0 | 0,96 |
| Q1 | `tuned_v q1` | 62 | 17 | 45 | 0,73 | 1,00 ; 0,00 | 0 | 1,00 |
| Q6 mt | `mt_pool q6` | 106 | 9 | 97 | 0,92 | 1,00 ; 0,00 | 0 | 0,80 |
| Q1 mt | `mt_pool q1` | 141 | 17 | 124 | 0,88 | 1,00 ; 0,00 | 0 | 0,95 |
| K7 | `tuned` | 24 | 15 | 9 | 0,38 | 1,00 ; 0,00 | 0 | 1,00 |
| K8 | `tuned_it` | 57 | 10 | 47 | 0,82 | 1,00 ; 0,00 | 0 | 0,68 |
| K9 | `tuned` | 22 | 10 | 12 | 0,55 | 1,00 ; 0,00 | 0 | 0,94 |
| K9 mt | `mt_pool` | 89 | 10 | 79 | 0,89 | 1,00 ; 0,00 | 0 | 0,77 |

### D

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 25 | 5 | 20 | 0,80 | 1,00 ; 0,08 | 0 | 0,93 |
| K3 | `sw_padded` | 16 | 16 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 1,00 |
| K4 | `tuned` | 19 | 1 | 18 | 0,95 | 1,00 ; 0,05 | 1 | 0,95 |
| K5 | `tuned` | 15 | 5 | 10 | 0,67 | 1,00 ; 0,27 | 0 | 0,75 |
| Q6 | `tuned_v q6` | 32 | 6 | 26 | 0,81 | 1,00 ; 0,09 | 0 | 0,89 |
| Q1 | `tuned q1` | 54 | 9 | 45 | 0,83 | 1,00 ; 0,06 | 0 | 0,78 |
| Q6 mt | `mt_pool_v q6` | 75 | 6 | 69 | 0,92 | 1,00 ; 0,05 | 0 | 0,88 |
| Q1 mt | `mt_pool q1` | 97 | 9 | 88 | 0,91 | 1,00 ; 0,04 | 0 | 0,76 |
| K7 | `tuned` | 16 | 5 | 11 | 0,69 | 1,00 ; 0,06 | 0 | 0,94 |
| K8 | `tuned_it` | 35 | 8 | 27 | 0,77 | 1,00 ; 0,03 | 0 | 0,63 |
| K9 | `tuned` | 16 | 5 | 11 | 0,69 | 1,00 ; 0,06 | 0 | 1,00 |
| K9 mt | `mt_pool` | 55 | 5 | 50 | 0,91 | 1,00 ; 0,04 | 0 | 0,80 |

### Rust

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 42 | 4 | 38 | 0,90 | 0,52 ; 0,52 | 12 | 0,96 |
| K3 | `sw_padded` | 22 | 22 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,96 |
| K4 | `tuned` | 26 | 4 | 22 | 0,85 | 0,85 ; 0,85 | 7 | 0,91 |
| K5 | `tuned` | 14 | 4 | 10 | 0,71 | 0,93 ; 0,93 | 7 | 0,75 |
| Q6 | `tuned_v q6` | 32 | 10 | 22 | 0,69 | 0,66 ; 0,66 | 13 | 1,00 |
| Q1 | `tuned q1` | 61 | 15 | 46 | 0,75 | 0,74 ; 0,74 | 24 | 0,86 |
| Q6 mt | `mt_pool_v q6` | 106 | 10 | 96 | 0,91 | 0,28 ; 0,28 | 13 | 0,95 |
| Q1 mt | `mt_pool q1` | 135 | 15 | 120 | 0,89 | 0,40 ; 0,40 | 24 | 0,93 |
| K7 | `tuned` | 24 | 6 | 18 | 0,75 | 0,04 ; 0,04 | 1 | 0,93 |
| K8 | `tuned_it` | 54 | 10 | 44 | 0,81 | 0,15 ; 0,15 | 0 | 0,73 |
| K9 | `tuned_v` | 52 | 10 | 42 | 0,81 | 0,62 ; 0,62 | 6 | 0,91 |
| K9 mt | `mt_pool` | 101 | 10 | 91 | 0,90 | 0,16 ; 0,16 | 0 | 0,73 |

### Chapel

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 7 | 5 | 2 | 0,29 | 1,00 ; 0,00 | 0 | 0,99 |
| K3 | `sw_padded` | 9 | 9 | 0 | 0,00 | 1,00 ; 0,00 | 0 | 0,96 |
| K4 | `tuned` | 26 | 5 | 21 | 0,81 | 1,00 ; 0,12 | 13 | 0,94 |
| K5 | `tuned_v` | 18 | 5 | 13 | 0,72 | 1,00 ; 0,33 | 12 | 0,75 |
| Q6 | `tuned_v q6` | 40 | 7 | 33 | 0,82 | 1,00 ; 0,20 | 27 | 0,93 |
| Q1 | `tuned_v q1` | 79 | 14 | 65 | 0,82 | 1,00 ; 0,16 | 49 | 0,75 |
| Q6 mt | `mt_pool_v q6` | 48 | 7 | 41 | 0,85 | 1,00 ; 0,17 | 27 | 1,00 |
| Q1 mt | `mt_pool_v q1` | 87 | 14 | 73 | 0,84 | 1,00 ; 0,15 | 49 | 0,93 |
| K7 | `tuned` | 18 | 10 | 8 | 0,44 | 1,00 ; 0,06 | 0 | 0,98 |
| K8 | `tuned_it` | 38 | 12 | 26 | 0,68 | 1,00 ; 0,00 | 0 | 0,81 |
| K9 | `tuned_v` | 26 | 4 | 22 | 0,85 | 1,00 ; 0,31 | 12 | 0,89 |
| K9 mt | `mt_pool_v` | 29 | 4 | 25 | 0,86 | 1,00 ; 0,31 | 12 | 1,00 |

### Nim

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 35 | 2 | 33 | 0,94 | 0,54 ; 0,54 | 13 | 0,97 |
| K3 | `sw_padded` | 19 | 19 | 0 | 0,00 | 0,05 ; 0,05 | 0 | 0,99 |
| K4 | `tuned` | 21 | 3 | 18 | 0,86 | 0,05 ; 0,05 | 8 | 0,90 |
| K5 | `tuned` | 19 | 2 | 17 | 0,89 | 0,26 ; 0,26 | 6 | 0,95 |
| Q6 | `tuned_v q6` | 46 | 4 | 42 | 0,91 | 0,50 ; 0,50 | 18 | 0,97 |
| Q1 | `tuned_v q1` | 79 | 11 | 68 | 0,86 | 0,51 ; 0,51 | 26 | 0,92 |
| Q6 mt | `mt_pool_v q6` | 110 | 4 | 106 | 0,96 | 0,23 ; 0,23 | 18 | 0,95 |
| Q1 mt | `mt_pool_v q1` | 143 | 11 | 132 | 0,92 | 0,29 ; 0,29 | 26 | 0,61 |
| K7 | `tuned` | 25 | 9 | 16 | 0,64 | 0,68 ; 0,68 | 0 | 0,93 |
| K8 | `tuned_it` | 46 | 11 | 35 | 0,76 | 0,91 ; 0,91 | 0 | 0,62 |
| K9 | `tuned_v` | 27 | 9 | 18 | 0,67 | 0,74 ; 0,74 | 6 | 0,97 |
| K9 mt | `mt_pool_v` | 84 | 9 | 75 | 0,89 | 0,27 ; 0,27 | 6 | 0,78 |

### Mojo

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 20 | 6 | 14 | 0,70 | 0,30 ; 0,30 | 0 | 0,99 |
| K3 | `sw_padded` | 16 | 16 | 0 | 0,00 | 0,12 ; 0,12 | 0 | 1,00 |
| K4 | `tuned` | 18 | 7 | 11 | 0,61 | 0,17 ; 0,17 | 0 | 0,75 |
| K5 | `tuned` | 12 | 6 | 6 | 0,50 | 0,33 ; 0,33 | 0 | 0,92 |
| Q6 | `tuned q6` | 23 | 7 | 16 | 0,70 | 0,13 ; 0,13 | 0 | 0,95 |
| Q1 | `tuned_v q1` | 52 | 12 | 40 | 0,77 | 0,06 ; 0,06 | 0 | 0,92 |
| Q6 mt | `mt q6` | 34 | 7 | 27 | 0,79 | 0,09 ; 0,09 | 0 | 0,91 |
| Q1 mt | `mt_pool_v q1` | 66 | 12 | 54 | 0,82 | 0,05 ; 0,05 | 0 | 0,92 |
| K7 | `tuned` | 24 | 13 | 11 | 0,46 | 0,29 ; 0,29 | 0 | 0,95 |
| K8 | `tuned_val` | 20 | 30 | -10 | 0,00 | 0,35 ; 0,35 | 0 | 0,43 |
| K9 | `tuned` | 18 | 12 | 6 | 0,33 | 0,33 ; 0,33 | 0 | 0,86 |
| K9 mt | `mt` | 26 | 12 | 14 | 0,54 | 0,27 ; 0,27 | 0 | 0,55 |

### Go

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 32 | 8 | 24 | 0,75 | 0,00 ; 0,00 | 7 | 0,98 |
| K3 | `rmw_padded` | 30 | 26 | 4 | 0,13 | 0,00 ; 0,00 | 0 | 0,36 |
| K4 | `tuned` | 24 | 10 | 14 | 0,58 | 0,00 ; 0,00 | 4 | 0,97 |
| K5 | `tuned_v` | 20 | 8 | 12 | 0,60 | 0,00 ; 0,00 | 6 | 0,48 |
| Q6 | `tuned q6` | 33 | 10 | 23 | 0,70 | 0,00 ; 0,00 | 8 | 0,79 |
| Q1 | `tuned q1` | 27 | 15 | 12 | 0,44 | 0,00 ; 0,00 | 0 | 0,36 |
| Q6 mt | `mt q6` | 57 | 10 | 47 | 0,82 | 0,00 ; 0,00 | 8 | 0,69 |
| Q1 mt | `mt q1` | 60 | 15 | 45 | 0,75 | 0,00 ; 0,00 | 0 | 0,29 |
| K7 | `tuned` | 17 | 11 | 6 | 0,35 | 0,00 ; 0,00 | 0 | 0,80 |
| K8 | `tuned_it` | 55 | 19 | 36 | 0,65 | 0,00 ; 0,00 | 0 | 0,51 |
| K9 | `tuned_v` | 26 | 13 | 13 | 0,50 | 0,00 ; 0,00 | 8 | 0,96 |
| K9 mt | `mt_pool_v` | 39 | 13 | 26 | 0,67 | 0,00 ; 0,00 | 8 | 0,55 |

### OCaml

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 15 | 10 | 5 | 0,33 | 0,20 ; 0,20 | 0 | 0,32 |
| K3 | `rmw_padded` | 8 | 8 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,25 |
| K4 | `tuned` | 19 | 7 | 12 | 0,63 | 0,05 ; 0,05 | 0 | 0,11 |
| K5 | `tuned` | 9 | 4 | 5 | 0,56 | 0,11 ; 0,11 | 0 | 0,04 |
| Q6 | `tuned_s q6` | 9 | 7 | 2 | 0,22 | 0,22 ; 0,22 | 0 | 0,15 |
| Q1 | `tuned q1` | 14 | 9 | 5 | 0,36 | 0,64 ; 0,64 | 0 | 0,18 |
| Q6 mt | `mt_pool_s q6` | 53 | 7 | 46 | 0,87 | 0,04 ; 0,04 | 0 | 0,08 |
| Q1 mt | `mt q1` | 16 | 9 | 7 | 0,44 | 0,56 ; 0,56 | 0 | 0,15 |
| K7 | `tuned_oa` | 12 | 8 | 4 | 0,33 | 0,25 ; 0,25 | 0 | 0,40 |
| K8 | `tuned_it` | 44 | 7 | 37 | 0,84 | 0,32 ; 0,32 | 0 | 0,37 |
| K9 | `tuned` | 9 | 5 | 4 | 0,44 | 0,22 ; 0,22 | 0 | 0,29 |
| K9 mt | `mt_pool` | 49 | 5 | 44 | 0,90 | 0,04 ; 0,04 | 0 | 0,19 |

### Lua

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 12 | 15 | -3 | 0,00 | 0,00 ; 0,00 | 0 | 0,01 |
| K3 | `rmw_padded` | 7 | 7 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,04 |
| K4 | `swar` | 20 | 8 | 12 | 0,60 | 0,00 ; 0,00 | 0 | 0,00 |
| K5 | `tuned` | 7 | 5 | 2 | 0,29 | 0,00 ; 0,00 | 0 | 0,00 |
| Q6 | `rq_nest q6` | 12 | 8 | 4 | 0,33 | 0,00 ; 0,00 | 0 | 0,03 |
| Q1 | `natural q1` | 12 | 12 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,01 |
| Q6 mt | `rq_nest_mt q6` | 13 | 8 | 5 | 0,38 | 0,00 ; 0,00 | 0 | 0,00 |
| Q1 mt | `mt q1` | 15 | 12 | 3 | 0,20 | 0,00 ; 0,00 | 0 | 0,00 |
| K7 | `rq_pack` | 7 | 6 | 1 | 0,14 | 0,00 ; 0,00 | 0 | 0,06 |
| K8 | `tuned_val` | 10 | 7 | 3 | 0,30 | 0,00 ; 0,00 | 0 | 0,02 |
| K9 | `natural` | 7 | 7 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,02 |
| K9 mt | `rq_slide_mt` | 11 | 7 | 4 | 0,36 | 0,00 ; 0,00 | 0 | 0,00 |

### Swift

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 45 | 7 | 38 | 0,84 | 0,31 ; 0,31 | 0 | 0,94 |
| K3 | `sw_padded` | 20 | 20 | 0 | 0,00 | 0,10 ; 0,10 | 0 | 0,96 |
| K4 | `tuned` | 22 | 7 | 15 | 0,68 | 0,41 ; 0,41 | 0 | 0,67 |
| K5 | `tuned` | 17 | 5 | 12 | 0,71 | 0,35 ; 0,35 | 0 | 0,80 |
| Q6 | `tuned q6` | 43 | 17 | 26 | 0,60 | 0,37 ; 0,37 | 0 | 0,91 |
| Q1 | `tuned q1` | 85 | 25 | 60 | 0,71 | 0,46 ; 0,46 | 0 | 0,87 |
| Q6 mt | `mt_pool q6` | 79 | 17 | 62 | 0,78 | 0,23 ; 0,23 | 0 | 0,94 |
| Q1 mt | `mt_pool q1` | 120 | 25 | 95 | 0,79 | 0,33 ; 0,33 | 0 | 0,84 |
| K7 | `tuned` | 23 | 10 | 13 | 0,57 | 0,61 ; 0,61 | 0 | 0,86 |
| K8 | `tuned_it` | 53 | 19 | 34 | 0,64 | 0,25 ; 0,25 | 0 | 0,67 |
| K9 | `tuned` | 21 | 9 | 12 | 0,57 | 0,48 ; 0,48 | 0 | 0,85 |
| K9 mt | `mt_pool` | 53 | 9 | 44 | 0,83 | 0,19 ; 0,19 | 0 | 0,85 |

### FreePascal

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 44 | 10 | 34 | 0,77 | 1,00 ; 0,02 | 0 | 0,63 |
| K3 | `sw_padded` | 44 | 44 | 0 | 0,00 | 1,00 ; 0,07 | 0 | 1,00 |
| K4 | `swar` | 37 | 11 | 26 | 0,70 | 1,00 ; 0,00 | 0 | 0,19 |
| K5 | `tuned_v` | 54 | 10 | 44 | 0,81 | 1,00 ; 0,02 | 0 | 0,18 |
| Q6 | `tuned q6` | 43 | 11 | 32 | 0,74 | 1,00 ; 0,02 | 0 | 0,41 |
| Q1 | `tuned q1` | 88 | 19 | 69 | 0,78 | 1,00 ; 0,01 | 0 | 0,37 |
| Q6 mt | `mt_pool q6` | 148 | 11 | 137 | 0,93 | 1,00 ; 0,05 | 0 | 0,21 |
| Q1 mt | `mt_pool q1` | 201 | 19 | 182 | 0,91 | 1,00 ; 0,04 | 0 | 0,31 |
| K7 | `tuned` | 49 | 16 | 33 | 0,67 | 1,00 ; 0,04 | 0 | 0,80 |
| K8 | `tuned_it` | 80 | 40 | 40 | 0,50 | 1,00 ; 0,01 | 0 | 0,47 |
| K9 | `tuned` | 35 | 14 | 21 | 0,60 | 1,00 ; 0,00 | 0 | 0,46 |
| K9 mt | `mt_pool` | 118 | 14 | 104 | 0,88 | 1,00 ; 0,01 | 0 | 0,39 |

### BQN

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 2 | 2 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,07 |
| K3 | `sw_padded` | 3 | 3 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,03 |
| K4 | `natural_unsorted` | 1 | 1 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,14 |
| K5 | `tuned` | 1 | 1 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,10 |
| Q6 | `tuned q6` | 1 | 1 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,50 |
| Q1 | `tuned q1` | 7 | 9 | -2 | 0,00 | 0,00 ; 0,00 | 0 | 0,09 |
| Q6 mt | `mt q6` | 4 | 1 | 3 | 0,75 | 0,00 ; 0,00 | 0 | 0,08 |
| Q1 mt | `mt q1` | 10 | 9 | 1 | 0,10 | 0,00 ; 0,00 | 0 | 0,04 |
| K7 | `tuned` | 8 | 2 | 6 | 0,75 | 0,00 ; 0,00 | 0 | 0,19 |
| K8 | `tuned` | 11 | 3 | 8 | 0,73 | 0,00 ; 0,00 | 0 | 0,33 |
| K9 | `tuned` | 8 | 5 | 3 | 0,38 | 0,00 ; 0,00 | 0 | 0,13 |
| K9 mt | `mt` | 8 | 5 | 3 | 0,38 | 0,00 ; 0,00 | 0 | 0,04 |

### PHP

| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |
|---|---|---|---|---|---|---|---|---|
| K1 | `soa` | 25 | 24 | 1 | 0,04 | 0,00 ; 0,00 | 0 | 0,09 |
| K3 | `sw_padded` | 72 | 72 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,02 |
| K4 | `tuned` | 10 | 10 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,08 |
| K5 | `tuned` | 10 | 9 | 1 | 0,10 | 0,00 ; 0,00 | 0 | 0,02 |
| Q6 | `tuned_s q6` | 10 | 10 | 0 | 0,00 | 0,00 ; 0,00 | 0 | 0,12 |
| Q1 | `tuned q1` | 18 | 16 | 2 | 0,11 | 0,00 ; 0,00 | 0 | 0,07 |
| Q6 mt | `mt_pool_s q6` | 62 | 10 | 52 | 0,84 | 0,00 ; 0,00 | 0 | 0,06 |
| Q1 mt | `mt q1` | 70 | 16 | 54 | 0,77 | 0,00 ; 0,00 | 0 | 0,07 |
| K7 | `tuned_oa` | 22 | 9 | 13 | 0,59 | 0,00 ; 0,00 | 0 | 0,14 |
| K8 | `tuned` | 59 | 19 | 40 | 0,68 | 0,00 ; 0,00 | 0 | 0,09 |
| K9 | `tuned` | 15 | 20 | -5 | 0,00 | 0,00 ; 0,00 | 0 | 0,09 |
| K9 mt | `mt` | 107 | 20 | 87 | 0,81 | 0,00 ; 0,00 | 0 | 0,05 |

