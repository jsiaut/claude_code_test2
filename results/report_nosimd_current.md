# Sensibilité « sans SIMD explicite » : sorties de analysis/nosimd_check.py

Plan : docs/NOSIMD.md (sections 2 et 3, poussées avant les calculs). Le classement publié ne change pas.

Témoin : écart maximal 0.0e+00 avec results/python_check.json, « P-E ».

## Rang (position par rang espéré) et score ponctuel

| Langage | Publié | Contrôle sans mt | S-scalaire | S-scalaire-Mojo | S-symétrique | S-noyaux-scalaires | S-importées |
|---|---|---|---|---|---|---|---|
| C | 1 (80,0) | 1 (80,4) | 5 (63,8) | 5 (63,8) | 2 (80,7) | 1 (77,6) | 1 (80,0) |
| Odin | 2 (74,0) | 2 (74,5) | 6 (59,1) | 6 (59,1) | 1 (77,8) | 2 (71,7) | 2 (74,0) |
| C++ | 3 (77,1) | 3 (77,6) | 7 (62,4) | 7 (62,4) | 3 (80,5) | 3 (73,0) | 3 (77,1) |
| Zig | 4 (72,3) | 4 (73,5) | 9 (58,7) | 9 (58,7) | 4 (74,9) | 7 (68,1) | 4 (72,3) |
| C3 | 5 (71,6) | 5 (72,3) | 10 (55,9) | 10 (55,9) | 5 (74,9) | 4 (69,0) | 5 (71,6) |
| Rust | 6 (70,0) | 7 (70,3) | 11 (56,3) | 11 (56,3) | 8 (69,8) | 8 (68,0) | 6 (70,0) |
| Nim | 7 (69,3) | 8 (69,5) | 8 (58,1) | 8 (58,1) | 6 (71,0) | 6 (68,3) | 13 (56,9) |
| D | 8 (72,7) | 6 (74,1) | 12 (57,5) | 12 (57,5) | 7 (72,8) | 9 (70,3) | 7 (72,7) |
| Ada | 9 (71,1) | 9 (73,3) | 4 (64,9) | 4 (64,9) | 9 (70,6) | 5 (72,8) | 11 (61,8) |
| Chapel | 10 (65,7) | 10 (65,2) | 1 (67,2) | 1 (67,2) | 11 (65,3) | 10 (63,8) | 8 (65,7) |
| Fortran | 11 (65,4) | 11 (66,1) | 2 (68,0) | 2 (68,0) | 10 (70,0) | 11 (63,2) | 9 (65,4) |
| Julia | 12 (62,4) | 12 (63,1) | 3 (64,8) | 3 (64,8) | 12 (67,3) | 12 (63,0) | 10 (62,4) |
| Mojo | 13 (62,3) | 13 (63,2) | 13 (45,0) | 13 (44,9) | 13 (55,0) | 13 (57,7) | 12 (62,3) |
| C# | 14 (54,9) | 14 (56,2) | 14 (43,0) | 14 (43,0) | 14 (53,1) | 14 (50,3) | 14 (54,9) |
| Java | 15 (47,2) | 15 (48,3) | 16 (37,1) | 16 (37,1) | 15 (50,3) | 15 (45,2) | 15 (47,2) |
| Go | 16 (45,4) | 16 (45,6) | 15 (37,5) | 15 (37,5) | 16 (46,5) | 16 (40,2) | 16 (45,4) |
| Haskell | 17 (41,3) | 17 (41,8) | 17 (31,1) | 17 (31,1) | 17 (39,0) | 17 (37,7) | 17 (41,3) |
| OCaml | 18 (23,9) | 18 (24,2) | 18 (24,7) | 18 (24,7) | 18 (28,0) | 18 (24,6) | 18 (23,9) |
| JavaScript | 19 (15,6) | 19 (15,7) | 19 (16,0) | 19 (16,0) | 19 (19,9) | 19 (16,1) | 19 (15,6) |
| Python | 20 (11,8) | 20 (11,8) | 20 (11,9) | 20 (11,9) | 20 (12,1) | 20 (11,9) | 20 (11,8) |
| Lua | 21 (3,9) | 21 (4,0) | 21 (4,0) | 21 (4,0) | 21 (4,6) | 21 (4,1) | 21 (3,9) |

## Résumé par scénario

| Scénario | Spearman / publié | 1er (part) | Places gagnées (+) ou perdues (−) par rapport au publié |
|---|---|---|---|
| Publié | 1,000 | C (49 %) | aucune |
| Contrôle sans mt | 0,996 | C (48 %) | D +2, Rust -1, Nim -1 |
| S-scalaire | 0,734 | Chapel (46 %) | Julia +9, Fortran +9, Chapel +9, Zig -5, Ada +5, C3 -5, Rust -5, C -4, C++ -4, Odin -4, D -4, Java -1, Nim -1, Go +1 |
| S-scalaire-Mojo | 0,734 | Chapel (46 %) | Julia +9, Fortran +9, Chapel +9, Zig -5, Ada +5, C3 -5, Rust -5, C -4, C++ -4, Odin -4, D -4, Java -1, Nim -1, Go +1 |
| S-symétrique | 0,994 | Odin (29 %) | Rust -2, C -1, Odin +1, Fortran +1, D +1, Chapel -1, Nim +1 |
| S-noyaux-scalaires | 0,979 | C (48 %) | Ada +4, Zig -3, Rust -2, C3 +1, D -1, Nim +1 |
| S-importées | 0,965 | C (50 %) | Nim -6, Julia +2, Ada -2, Fortran +2, Chapel +2, D +1, Mojo +1 |

## Plafond E par scénario

| Langage | Publié | Contrôle sans mt | S-scalaire | S-scalaire-Mojo | S-symétrique | S-noyaux-scalaires | S-importées |
|---|---|---|---|---|---|---|---|
| C | 85,2 | 86,3 | 44,4 | 44,4 | 79,6 | 79,3 | 85,2 |
| Odin | 80,0 | 81,2 | 42,2 | 42,2 | 81,0 | 74,2 | 80,0 |
| C++ | 80,1 | 81,3 | 42,8 | 42,8 | 81,5 | 69,7 | 80,1 |
| Zig | 70,3 | 73,2 | 35,9 | 35,9 | 68,9 | 59,6 | 70,3 |
| C3 | 83,5 | 85,2 | 43,9 | 43,9 | 84,2 | 76,9 | 83,5 |
| Rust | 77,8 | 78,6 | 43,4 | 43,4 | 70,3 | 72,8 | 77,8 |
| Nim | 72,4 | 72,8 | 44,0 | 44,0 | 68,8 | 69,9 | 41,3 |
| D | 79,2 | 82,7 | 41,0 | 41,0 | 73,4 | 73,2 | 79,2 |
| Ada | 76,8 | 82,3 | 61,0 | 61,0 | 70,4 | 81,2 | 53,7 |
| Chapel | 79,5 | 78,3 | 82,8 | 82,8 | 71,3 | 74,7 | 79,5 |
| Fortran | 73,0 | 74,5 | 78,9 | 78,9 | 76,7 | 67,4 | 73,0 |
| Julia | 62,3 | 64,2 | 67,9 | 67,9 | 66,5 | 64,0 | 62,3 |
| Mojo | 67,0 | 69,3 | 23,5 | 23,3 | 45,0 | 55,5 | 67,0 |
| C# | 53,6 | 57,0 | 23,8 | 23,8 | 45,7 | 42,1 | 53,6 |
| Java | 56,5 | 59,4 | 31,0 | 31,0 | 59,5 | 51,6 | 56,5 |
| Go | 44,5 | 45,1 | 24,6 | 24,6 | 42,6 | 31,5 | 44,5 |
| Haskell | 46,2 | 47,5 | 20,8 | 20,8 | 38,1 | 37,2 | 46,2 |
| OCaml | 19,4 | 20,0 | 21,2 | 21,2 | 26,9 | 21,1 | 19,4 |
| JavaScript | 12,2 | 12,4 | 13,1 | 13,1 | 21,1 | 13,3 | 12,2 |
| Python | 0,6 | 0,6 | 0,7 | 0,7 | 1,1 | 0,8 | 0,6 |
| Lua | 1,1 | 1,3 | 1,4 | 1,4 | 2,5 | 1,4 | 1,1 |

## Références t* (ms) et langage qui les fixe

* Publié : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D) ; k9#1 3,83 (Chapel)
* Contrôle sans mt : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D)
* S-scalaire : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 4,68 (Chapel) ; k6#0 20,03 (Ada) ; k6#1 47,47 (Fortran) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 13,10 (C3)
* S-scalaire-Mojo : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 4,68 (Chapel) ; k6#0 20,03 (Ada) ; k6#1 47,47 (Fortran) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 13,10 (C3)
* S-symétrique : k1#0 38,04 (Mojo) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 77,08 (C++) ; k6#0 56,94 (Mojo) ; k6#1 74,85 (C++) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 13,10 (C3)
* S-noyaux-scalaires : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D) ; k9#1 3,83 (Chapel)
* S-importées : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 12,76 (D) ; k9#1 3,83 (Chapel)

## Variante retenue par E dans S-scalaire (mesures vectorisables)

| Langage | k1#0 | k5#0 | k6#0 | k6#1 | k9#0 |
|---|---|---|---|---|---|
| C | aos 38,4 | natural 158,1 | tuned q6 21,3 | natural q1 83,4 | natural 13,9 |
| Odin | aos 40,3 | natural 77,7 | natural q6 63,3 | natural q1 121,0 | natural 15,0 |
| C++ | aos 40,2 | natural 77,1 | natural q6 62,4 | natural q1 74,9 | tuned 13,5 |
| Zig | aos 41,9 | natural 80,0 | natural q6 67,1 | natural q1 77,7 | natural 25,7 |
| C3 | aos 40,3 | natural 79,1 | natural q6 63,4 | natural q1 108,9 | natural 13,1 |
| Rust | aos 40,4 | natural 83,7 | tuned q6 23,3 | natural q1 120,3 | tuned 17,0 |
| Nim | aos 38,8 | natural 81,4 | tuned q6 21,3 | natural q1 95,4 | tuned 16,4 |
| D | aos 43,7 | natural 84,3 | tuned q6 20,9 | natural q1 88,3 | natural 31,1 |
| Ada | soa 7,2 | natural 86,1 | tuned q6 20,0 | tuned q1 57,5 | tuned 14,7 |
| Chapel | soa 7,7 | tuned 4,7 | tuned q6 22,8 | tuned q1 48,5 | tuned 15,9 |
| Fortran | soa 7,5 | tuned 5,5 | tuned q6 22,6 | tuned q1 47,5 | natural 13,9 |
| Julia | soa 8,0 | tuned 6,3 | tuned q6 21,4 | tuned q1 98,8 | natural 21,6 |
| Mojo | aos 38,0 | natural 161,2 | natural q6 56,9 | natural q1 227,3 | natural 202,3 |
| C# | aos 38,9 | natural 86,7 | natural q6 155,7 | natural q1 186,3 | natural 71,9 |
| Java | aos 42,3 | natural 141,9 | natural q6 111,0 | natural q1 111,5 | natural 17,0 |
| Go | aos 47,2 | natural 86,8 | natural q6 138,4 | tuned q1 86,3 | tuned 21,9 |
| Haskell | aos 38,3 | natural 189,2 | tuned q6 60,2 | tuned q1 67,4 | natural 163,4 |
| OCaml | soa 12,3 | tuned 71,6 | tuned q6 112,5 | tuned q1 214,5 | tuned 48,1 |
| JavaScript | soa 23,2 | tuned 149,9 | tuned q6 131,5 | natural q1 376,4 | tuned 65,0 |
| Python | soa 963,1 | tuned 3096,7 | natural q6 1833,8 | tuned q1 7941,8 | natural 1558,9 |
| Lua | soa 293,9 | natural 1742,4 | natural q6 627,0 | tuned q1 2215,7 | natural 682,0 |
