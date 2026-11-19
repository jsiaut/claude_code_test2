# Troisième remarque générale : les mesures et la grille, séparément

Plan : `docs/AUDIT3_RESPONSE.md`. Code : `analysis/audit3.py`. Aucune mesure nouvelle.
Contrôle : le scénario Publié reproduit Après de `results/grid_audit/errata.json` (écart maximal 0.0e+00).

## Les trois quantités du plan v3, et le classement sur les seules mesures

Plafond E et code naturel D1 (sur 100, référence fixe) ; contrôle C, règle v2 (v1 entre parenthèses) ; rang de chaque quantité parmi les 25. M-mesures : poids du contrôle nul, au centre et dans les 20 000 variantes.

| Rang publié | Étage | Langage | Plafond (rang) | Code naturel D1 (rang) | Contrôle v2 (v1) (rang) | M-mesures : rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | C | 85,2 (1) | 19,0 (6) | 91,7 (74,2) (2) | 1,81 | 1 | 1–4 |
| 2 | 1 | Odin | 80,0 (5) | 21,3 (1) | 84,0 (81,3) (5) | 4,03 | 2 | 1–8 |
| 3 | 1 | C++ | 80,1 (4) | 17,9 (10) | 92,4 (79,1) (1) | 5,90 | 5 | 2–10 |
| 4 | 1 | C3 | 83,5 (2) | 19,0 (7) | 75,7 (77,7) (8) | 4,78 | 3 | 2–10 |
| 5 | 1 | Zig | 70,3 (12) | 20,2 (3) | 87,2 (83,2) (3) | 7,92 | 9 | 2–13 |
| 6 | 1 | Rust | 77,8 (8) | 18,2 (8) | 73,6 (73,1) (9) | 6,09 | 6 | 2–10 |
| 7 | 1 | Nim | 72,4 (11) | 20,0 (4) | 76,1 (73,4) (7) | 7,10 | 7 | 2–12 |
| 8 | 1 | D | 79,2 (7) | 15,9 (11) | 87,1 (78,9) (4) | 10,13 | 12 | 5–14 |
| 9 | 1 | Ada | 76,8 (9) | 13,2 (12) | 80,6 (71,7) (6) | 9,06 | 10 | 2–13 |
| 10 | 1 | Chapel | 79,5 (6) | 17,9 (9) | 61,8 (63,8) (16) | 5,42 | 4 | 1–10 |
| 11 | 1 | Fortran | 73,0 (10) | 19,6 (5) | 65,3 (59,2) (14) | 7,88 | 8 | 3–12 |
| 12 | 1 | Swift | 80,3 (3) | 7,6 (17) | 68,1 (64,1) (13) | 9,26 | 11 | 3–14 |
| 13 | 1 | Julia | 62,3 (14) | 20,9 (2) | 73,3 (68,9) (10) | 12,67 | 13 | 9–14 |
| 14 | 1 | Mojo | 67,0 (13) | 9,6 (15) | 70,5 (66,0) (11) | 13,27 | 14 | 11–14 |
| 15 | 2 | C# | 53,6 (16) | 9,1 (16) | 68,8 (65,8) (12) | 16,56 | 16 | 15–19 |
| 16 | 2 | FreePascal | 36,3 (19) | 5,0 (21) | 62,3 (58,5) (15) | 17,69 | 18 | 15–19 |
| 17 | 2 | Java | 56,5 (15) | 12,1 (14) | 42,7 (42,7) (18) | 15,76 | 15 | 15–18 |
| 18 | 2 | Go | 44,5 (18) | 12,3 (13) | 48,7 (44,9) (17) | 16,61 | 17 | 15–18 |
| 19 | 2 | Haskell | 46,2 (17) | 5,9 (19) | 41,5 (40,5) (19) | 18,13 | 19 | 17–19 |
| 20 | 3 | OCaml | 19,4 (20) | 7,0 (18) | 23,2 (23,2) (22) | 20,22 | 20 | 20–21 |
| 21 | 3 | BQN | 12,5 (21) | 5,1 (20) | 19,7 (21,2) (23) | 21,08 | 21 | 20–22 |
| 22 | 3 | PHP | 4,5 (23) | 1,5 (23) | 27,4 (25,9) (21) | 22,79 | 23 | 22–23 |
| 23 | 3 | JavaScript | 12,2 (22) | 4,5 (22) | 14,6 (14,6) (24) | 21,85 | 22 | 21–23 |
| 24 | 3 | Python | 0,6 (25) | 0,5 (25) | 29,7 (27,7) (20) | 25,00 | 25 | 25–25 |
| 25 | 3 | Lua | 1,3 (24) | 1,1 (24) | 6,8 (6,8) (25) | 24,00 | 24 | 24–24 |

Étages publiés (règle v3) : Ada, C, C3, Chapel, C++, D, Fortran, Julia, Mojo, Nim, Odin, Rust, Swift, Zig | C#, FreePascal, Go, Haskell, Java | BQN, JavaScript, Lua, OCaml, PHP, Python.
Étages de M-mesures (indicatifs : paires ordonnées dans au moins 95 % des tirages, sans la condition de réplication) : Ada, C, C3, Chapel, C++, D, Fortran, Julia, Mojo, Nim, Odin, Rust, Swift, Zig | C#, FreePascal, Go, Haskell, Java | BQN, JavaScript, OCaml, PHP | Lua | Python.

## Substitutions (implémentations en annexe, mesurées dans la campagne principale)

| Variante | à la place de | clés remplacées | score | rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|
| C par GCC 16 | C (80,0 ; 1e) | 36 sur 36 | 79,5 | 2,63 | 1e | 1–7 |
| Fortran par flang | Fortran (65,4 ; 11e) | 36 sur 36 | 61,0 | 12,75 | 13e | 10–15 |
| LuaJIT | Lua (5,4 ; 25e) | 32 sur 36 | 11,3 | 23,79 | 24e | 22–25 |
| JavaScript par Bun | JavaScript (15,6 ; 23e) | 36 sur 36 | 18,1 | 21,87 | 22e | 21–24 |
| CPython sans GIL | Python (11,8 ; 24e) | 13 sur 36 | 11,7 | 24,32 | 24e | 23–25 |

## Variantes des remarques (relues dans leurs sorties)

| Variante | score | rang espéré | place | état | source |
|---|---|---|---|---|---|
| Zig 0.18-dev (préversion) | 75,7 | 2,14 | 1e sur 25 | actuel | `results/zig_check.json : S1` |
| C++ avec le K4 de clang++ | 80,3 | 2,17 | 1e sur 25 | actuel | `results/c_check_current.json : T1` |
| C# sous .NET 11 (préversion) | 55,5 | 15,23 | 15e sur 25 | actuel | `results/csharp_check_current.json : S-N11` |
| PHP, CLI par défaut (ni OPcache ni JIT) | 16,3 | 22,39 | 23e sur 25 | actuel | `results/php_check.json : P-défaut` |
| PHP, stencil compilé par le JIT de 8.3 | 16,6 | 22,31 | 22e sur 25 | actuel | `results/php_remark.json : R-K9-83` |
| Swift -Ounchecked (sans vérifications) | 65,6 | 10,55 | 11e sur 22 | 5 novembre, 22 langages | `results/swift_check.json : S-Ou` |
| FreePascal 3.2.4-rc2 | 47,4 | 16,90 | 16e sur 23 | 6 novembre, 23 langages | `results/fpc_remark.json : R-rc2` |
| FreePascal, branche main | 47,6 | 16,78 | 16e sur 23 | 6 novembre, 23 langages | `results/fpc_remark.json : R-main` |

## État de preuve de la grille

| Langage | sondées | mesurées | lues | cases lues |
|---|---|---|---|---|
| C | 33 | 1 | 0 |  |
| C++ | 33 | 1 | 0 |  |
| C# | 33 | 1 | 0 |  |
| Java | 33 | 1 | 0 |  |
| Zig | 33 | 1 | 0 |  |
| Odin | 33 | 1 | 0 |  |
| Julia | 33 | 1 | 0 |  |
| Ada | 33 | 1 | 0 |  |
| Fortran | 33 | 1 | 0 |  |
| JavaScript | 33 | 1 | 0 |  |
| Python | 33 | 1 | 0 |  |
| Haskell | 33 | 1 | 0 |  |
| C3 | 33 | 1 | 0 |  |
| D | 33 | 1 | 0 |  |
| Rust | 33 | 1 | 0 |  |
| Chapel | 33 | 1 | 0 |  |
| Nim | 33 | 1 | 0 |  |
| Mojo | 33 | 1 | 0 |  |
| Go | 33 | 1 | 0 |  |
| OCaml | 33 | 1 | 0 |  |
| Lua | 33 | 1 | 0 |  |
| Swift | 33 | 1 | 0 |  |
| FreePascal | 33 | 1 | 0 |  |
| BQN | 33 | 1 | 0 |  |
| PHP | 33 | 1 | 0 |  |
| **Total** | 825 | 25 | 0 | 100,0 % sondées ou mesurées |
