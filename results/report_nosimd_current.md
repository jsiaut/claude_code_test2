# Sensibilité « sans SIMD explicite » : sorties de analysis/nosimd_check.py

Plan : docs/NOSIMD.md (sections 2 et 3, poussées avant les calculs). Le classement publié ne change pas.

Témoin : écart maximal 0.0e+00 avec results/php_check.json, « P-E ».

## Rang (position par rang espéré) et score ponctuel

| Langage | Publié | Contrôle sans mt | S-scalaire | S-scalaire-Mojo | S-symétrique | S-noyaux-scalaires | S-importées |
|---|---|---|---|---|---|---|---|
| C | 1 (80,0) | 1 (80,4) | 5 (63,8) | 5 (63,8) | 2 (80,6) | 1 (77,6) | 1 (80,0) |
| Odin | 2 (74,0) | 2 (74,5) | 6 (59,1) | 6 (59,1) | 1 (77,7) | 2 (71,7) | 2 (74,0) |
| C++ | 3 (77,1) | 3 (77,6) | 7 (62,3) | 7 (62,3) | 3 (80,4) | 3 (73,0) | 3 (77,1) |
| C3 | 4 (71,6) | 5 (72,3) | 10 (55,9) | 10 (55,9) | 5 (74,8) | 4 (69,0) | 5 (71,6) |
| Zig | 5 (72,3) | 4 (73,5) | 9 (58,7) | 9 (58,7) | 4 (74,8) | 8 (68,1) | 4 (72,3) |
| Rust | 6 (70,0) | 7 (70,3) | 11 (56,3) | 11 (56,3) | 8 (69,7) | 7 (68,0) | 6 (70,0) |
| Nim | 7 (69,3) | 9 (69,5) | 8 (58,1) | 8 (58,1) | 6 (70,9) | 6 (68,3) | 14 (56,9) |
| D | 8 (72,7) | 6 (74,1) | 12 (57,5) | 12 (57,5) | 7 (72,7) | 9 (70,3) | 7 (72,7) |
| Ada | 9 (71,1) | 8 (73,3) | 4 (64,8) | 4 (64,8) | 9 (70,5) | 5 (72,8) | 12 (61,8) |
| Chapel | 10 (65,7) | 10 (65,2) | 1 (67,2) | 1 (67,2) | 12 (65,2) | 10 (63,8) | 8 (65,7) |
| Fortran | 11 (65,4) | 11 (66,1) | 2 (68,0) | 2 (68,0) | 10 (69,9) | 11 (63,2) | 9 (65,4) |
| Swift | 12 (66,5) | 12 (66,4) | 13 (48,2) | 13 (48,2) | 13 (61,7) | 13 (63,6) | 10 (66,5) |
| Julia | 13 (62,4) | 13 (63,1) | 3 (64,8) | 3 (64,8) | 11 (67,2) | 12 (63,0) | 11 (62,4) |
| Mojo | 14 (62,3) | 14 (63,2) | 14 (45,0) | 14 (44,9) | 14 (55,0) | 14 (57,7) | 13 (62,3) |
| C# | 15 (54,9) | 15 (56,2) | 16 (43,0) | 16 (43,0) | 15 (53,1) | 15 (50,3) | 15 (54,9) |
| FreePascal | 16 (48,1) | 16 (48,4) | 15 (43,3) | 15 (43,3) | 16 (50,7) | 16 (48,8) | 16 (48,1) |
| Java | 17 (47,2) | 17 (48,3) | 17 (37,1) | 17 (37,1) | 17 (50,2) | 17 (45,2) | 17 (47,2) |
| Go | 18 (45,4) | 18 (45,6) | 18 (37,5) | 18 (37,5) | 18 (46,5) | 18 (40,1) | 18 (45,4) |
| Haskell | 19 (41,3) | 19 (41,8) | 19 (31,1) | 19 (31,1) | 19 (38,9) | 19 (37,7) | 19 (41,3) |
| OCaml | 20 (23,9) | 20 (24,2) | 20 (24,7) | 20 (24,7) | 20 (27,9) | 20 (24,6) | 20 (23,9) |
| BQN | 21 (17,7) | 21 (18,5) | 21 (18,8) | 21 (18,8) | 21 (21,3) | 21 (19,1) | 21 (17,7) |
| PHP | 22 (16,6) | 22 (16,6) | 22 (16,7) | 22 (16,7) | 23 (17,6) | 23 (16,2) | 22 (16,6) |
| JavaScript | 23 (15,6) | 23 (15,7) | 23 (16,0) | 23 (16,0) | 22 (19,9) | 22 (16,1) | 23 (15,6) |
| Python | 24 (11,8) | 24 (11,8) | 24 (11,9) | 24 (11,9) | 24 (12,1) | 24 (11,9) | 24 (11,8) |
| Lua | 25 (5,4) | 25 (5,5) | 25 (5,6) | 25 (5,6) | 25 (6,2) | 25 (5,7) | 25 (5,4) |

## Résumé par scénario

| Scénario | Spearman / publié | 1er (part) | Places gagnées (+) ou perdues (−) par rapport au publié |
|---|---|---|---|
| Publié | 1,000 | C (50 %) | aucune |
| Contrôle sans mt | 0,995 | C (48 %) | D +2, Nim -2, Zig +1, Ada +1, C3 -1, Rust -1 |
| S-scalaire | 0,834 | Chapel (45 %) | Julia +10, Fortran +9, Chapel +9, C3 -6, Ada +5, Rust -5, C -4, C++ -4, Zig -4, Odin -4, D -4, C# -1, Nim -1, Swift -1, FreePascal +1 |
| S-scalaire-Mojo | 0,834 | Chapel (45 %) | Julia +10, Fortran +9, Chapel +9, C3 -6, Ada +5, Rust -5, C -4, C++ -4, Zig -4, Odin -4, D -4, C# -1, Nim -1, Swift -1, FreePascal +1 |
| S-symétrique | 0,992 | Odin (30 %) | Julia +2, Rust -2, Chapel -2, C -1, Zig +1, Odin +1, Fortran +1, JavaScript +1, C3 -1, D +1, Nim +1, Swift -1, PHP -1 |
| S-noyaux-scalaires | 0,988 | C (48 %) | Ada +4, Zig -3, Julia +1, JavaScript +1, D -1, Rust -1, Nim +1, Swift -1, PHP -1 |
| S-importées | 0,970 | C (51 %) | Nim -7, Ada -3, Julia +2, Fortran +2, Chapel +2, Swift +2, Zig +1, C3 -1, D +1, Mojo +1 |

## Plafond E par scénario

| Langage | Publié | Contrôle sans mt | S-scalaire | S-scalaire-Mojo | S-symétrique | S-noyaux-scalaires | S-importées |
|---|---|---|---|---|---|---|---|
| C | 85,2 | 86,3 | 44,4 | 44,4 | 79,4 | 79,3 | 85,2 |
| Odin | 80,0 | 81,2 | 42,2 | 42,2 | 80,8 | 74,2 | 80,0 |
| C++ | 80,1 | 81,3 | 42,8 | 42,8 | 81,3 | 69,7 | 80,1 |
| C3 | 83,5 | 85,2 | 43,9 | 43,9 | 84,0 | 76,9 | 83,5 |
| Zig | 70,3 | 73,2 | 35,9 | 35,9 | 68,8 | 59,6 | 70,3 |
| Rust | 77,8 | 78,6 | 43,4 | 43,4 | 70,1 | 72,8 | 77,8 |
| Nim | 72,4 | 72,8 | 44,0 | 44,0 | 68,6 | 69,9 | 41,3 |
| D | 79,2 | 82,7 | 41,0 | 41,0 | 73,2 | 73,2 | 79,2 |
| Ada | 76,8 | 82,3 | 61,0 | 61,0 | 70,3 | 81,2 | 53,7 |
| Chapel | 79,5 | 78,3 | 82,8 | 82,8 | 71,2 | 74,7 | 79,5 |
| Fortran | 73,0 | 74,5 | 78,9 | 78,9 | 76,5 | 67,4 | 73,0 |
| Swift | 80,3 | 80,3 | 34,7 | 34,7 | 65,6 | 73,3 | 80,3 |
| Julia | 62,3 | 64,2 | 67,9 | 67,9 | 66,4 | 64,0 | 62,3 |
| Mojo | 67,0 | 69,3 | 23,5 | 23,3 | 44,9 | 55,5 | 67,0 |
| C# | 53,6 | 57,0 | 23,8 | 23,8 | 45,6 | 42,1 | 53,6 |
| FreePascal | 36,3 | 37,1 | 24,4 | 24,4 | 40,9 | 38,1 | 36,3 |
| Java | 56,5 | 59,4 | 31,0 | 31,0 | 59,4 | 51,6 | 56,5 |
| Go | 44,5 | 45,1 | 24,6 | 24,6 | 42,6 | 31,5 | 44,5 |
| Haskell | 46,2 | 47,5 | 20,8 | 20,8 | 38,0 | 37,2 | 46,2 |
| OCaml | 19,4 | 20,0 | 21,2 | 21,2 | 26,8 | 21,1 | 19,4 |
| BQN | 12,5 | 14,3 | 15,1 | 15,1 | 19,5 | 15,8 | 12,5 |
| PHP | 4,5 | 4,6 | 4,9 | 4,9 | 6,5 | 3,6 | 4,5 |
| JavaScript | 12,2 | 12,4 | 13,1 | 13,1 | 21,1 | 13,3 | 12,2 |
| Python | 0,6 | 0,6 | 0,7 | 0,7 | 1,1 | 0,8 | 0,6 |
| Lua | 1,3 | 1,6 | 1,7 | 1,7 | 3,0 | 2,0 | 1,3 |

## Références t* (ms) et langage qui les fixe

* Publié : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D) ; k9#1 3,83 (Chapel)
* Contrôle sans mt : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D)
* S-scalaire : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 4,68 (Chapel) ; k6#0 20,03 (Ada) ; k6#1 47,47 (Fortran) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 13,10 (C3)
* S-scalaire-Mojo : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 4,68 (Chapel) ; k6#0 20,03 (Ada) ; k6#1 47,47 (Fortran) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 13,10 (C3)
* S-symétrique : k1#0 38,04 (Mojo) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 77,08 (C++) ; k6#0 55,00 (BQN) ; k6#1 74,85 (C++) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 13,10 (C3)
* S-noyaux-scalaires : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D) ; k9#1 3,83 (Chapel)
* S-importées : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D) ; k9#1 3,83 (Chapel)

## Variante retenue par E dans S-scalaire (mesures vectorisables)

| Langage | k1#0 | k5#0 | k6#0 | k6#1 | k9#0 |
|---|---|---|---|---|---|
| C | aos 38,4 | natural 158,1 | tuned q6 21,3 | natural q1 83,4 | natural 13,9 |
| Odin | aos 40,3 | natural 77,7 | natural q6 63,3 | natural q1 121,0 | natural 15,0 |
| C++ | aos 40,2 | natural 77,1 | natural q6 62,4 | natural q1 74,9 | tuned 13,5 |
| C3 | aos 40,3 | natural 79,1 | natural q6 63,4 | natural q1 108,9 | natural 13,1 |
| Zig | aos 41,9 | natural 80,0 | natural q6 67,1 | natural q1 77,7 | natural 25,7 |
| Rust | aos 40,4 | natural 83,7 | tuned q6 23,3 | natural q1 120,3 | tuned 17,0 |
| Nim | aos 38,8 | natural 81,4 | tuned q6 21,3 | natural q1 95,4 | tuned 16,4 |
| D | aos 43,7 | natural 84,3 | tuned q6 20,9 | natural q1 88,3 | natural 31,1 |
| Ada | soa 7,2 | natural 86,1 | tuned q6 20,0 | tuned q1 57,5 | tuned 14,7 |
| Chapel | soa 7,7 | tuned 4,7 | tuned q6 22,8 | tuned q1 48,5 | tuned 15,9 |
| Fortran | soa 7,5 | tuned 5,5 | tuned q6 22,6 | tuned q1 47,5 | natural 13,9 |
| Swift | aos 38,9 | natural 79,1 | natural q6 69,6 | natural q1 121,6 | natural 66,6 |
| Julia | soa 8,0 | tuned 6,3 | tuned q6 21,4 | tuned q1 98,8 | natural 21,6 |
| Mojo | aos 38,0 | natural 161,2 | natural q6 56,9 | natural q1 227,3 | natural 202,3 |
| C# | aos 38,9 | natural 86,7 | natural q6 155,7 | natural q1 186,3 | natural 71,9 |
| FreePascal | aos 45,7 | natural 327,2 | tuned q6 36,9 | tuned q1 83,3 | tuned 27,3 |
| Java | aos 42,3 | natural 141,9 | natural q6 111,0 | natural q1 111,5 | natural 17,0 |
| Go | aos 47,2 | natural 86,8 | natural q6 138,4 | tuned q1 86,3 | tuned 21,9 |
| Haskell | aos 38,3 | natural 189,2 | tuned q6 60,2 | tuned q1 67,4 | natural 163,4 |
| OCaml | soa 12,3 | tuned 71,6 | tuned q6 112,5 | tuned q1 214,5 | tuned 48,1 |
| BQN | soa 96,0 | tuned 32,3 | tuned q6 28,5 | tuned q1 317,9 | tuned 105,2 |
| PHP | soa 83,5 | natural 184,4 | tuned q6 203,4 | tuned q1 384,2 | tuned 162,3 |
| JavaScript | soa 23,2 | tuned 149,9 | tuned q6 131,5 | natural q1 376,4 | tuned 65,0 |
| Python | soa 963,1 | tuned 3096,7 | natural q6 1833,8 | tuned q1 7941,8 | natural 1558,9 |
| Lua | soa 293,9 | natural 1742,4 | natural q6 627,0 | tuned q1 2215,7 | natural 682,0 |
