# Sensibilité « sans SIMD explicite » : sorties de analysis/nosimd_check.py

Plan : docs/NOSIMD.md (sections 2 et 3, poussées avant les calculs). Le classement publié ne change pas.

Témoin : écart maximal 0.0e+00 avec results/c3_check.json, « Errata ».

## Rang (position par rang espéré) et score ponctuel

| Langage | Publié | Contrôle sans mt | S-scalaire | S-scalaire-Mojo | S-symétrique | S-noyaux-scalaires | S-importées |
|---|---|---|---|---|---|---|---|
| C | 1 (80,0) | 1 (80,5) | 5 (63,8) | 5 (63,8) | 3 (80,7) | 1 (77,6) | 1 (80,0) |
| C++ | 2 (76,6) | 2 (77,9) | 6 (62,4) | 6 (62,4) | 1 (80,9) | 3 (73,0) | 2 (76,6) |
| Odin | 3 (72,6) | 3 (74,0) | 7 (58,5) | 7 (58,5) | 2 (77,5) | 2 (70,9) | 3 (72,6) |
| Zig | 4 (72,7) | 4 (74,2) | 9 (60,0) | 9 (60,0) | 4 (77,4) | 7 (68,3) | 4 (72,7) |
| C3 | 5 (71,2) | 5 (72,4) | 11 (55,8) | 11 (55,8) | 5 (74,7) | 5 (69,0) | 5 (71,2) |
| Nim | 6 (69,7) | 7 (70,6) | 8 (58,8) | 8 (58,8) | 6 (73,7) | 6 (68,5) | 13 (57,2) |
| Rust | 7 (70,5) | 6 (71,6) | 10 (57,1) | 10 (57,1) | 8 (71,7) | 8 (68,1) | 6 (70,5) |
| D | 8 (72,6) | 8 (74,1) | 12 (58,6) | 12 (58,6) | 7 (74,8) | 9 (70,4) | 7 (72,6) |
| Ada | 9 (71,7) | 9 (73,8) | 4 (65,1) | 4 (65,1) | 9 (72,2) | 4 (72,9) | 11 (62,3) |
| Chapel | 10 (66,1) | 10 (65,9) | 1 (67,8) | 1 (67,8) | 12 (66,1) | 10 (63,9) | 8 (66,1) |
| Fortran | 11 (66,1) | 11 (66,4) | 2 (68,2) | 2 (68,2) | 10 (70,2) | 11 (63,2) | 9 (66,1) |
| Julia | 12 (64,3) | 12 (64,9) | 3 (66,5) | 3 (66,5) | 11 (69,2) | 12 (63,2) | 10 (64,3) |
| Mojo | 13 (62,8) | 13 (63,3) | 13 (46,0) | 13 (45,9) | 13 (57,0) | 13 (57,8) | 12 (62,8) |
| C# | 14 (56,0) | 14 (57,2) | 14 (43,7) | 14 (43,7) | 14 (54,5) | 14 (50,3) | 14 (56,0) |
| Java | 15 (47,2) | 15 (47,9) | 15 (36,9) | 15 (36,9) | 15 (50,4) | 15 (44,8) | 15 (47,2) |
| Go | 16 (43,0) | 16 (42,4) | 16 (36,8) | 16 (36,8) | 16 (46,7) | 16 (40,1) | 16 (43,0) |
| Haskell | 17 (35,5) | 17 (35,8) | 17 (26,8) | 17 (26,8) | 17 (32,7) | 17 (30,0) | 17 (35,5) |
| OCaml | 18 (24,7) | 18 (25,1) | 18 (25,6) | 18 (25,6) | 18 (26,9) | 18 (24,9) | 18 (24,7) |
| JavaScript | 19 (14,7) | 19 (14,8) | 19 (15,1) | 19 (15,1) | 19 (19,1) | 19 (14,4) | 19 (14,7) |
| Python | 20 (10,0) | 20 (10,0) | 20 (10,0) | 20 (10,0) | 20 (10,3) | 20 (10,0) | 20 (10,0) |
| Lua | 21 (4,0) | 21 (4,1) | 21 (4,1) | 21 (4,1) | 21 (4,8) | 21 (4,1) | 21 (4,0) |

## Résumé par scénario

| Scénario | Spearman / publié | 1er (part) | Places gagnées (+) ou perdues (−) par rapport au publié |
|---|---|---|---|
| Publié | 1,000 | C (57 %) | aucune |
| Contrôle sans mt | 0,999 | C (47 %) | Rust +1, Nim -1 |
| S-scalaire | 0,736 | Chapel (43 %) | Julia +9, Fortran +9, Chapel +9, C3 -6, Zig -5, Ada +5, C -4, C++ -4, Odin -4, D -4, Rust -3, Nim -2 |
| S-scalaire-Mojo | 0,736 | Chapel (43 %) | Julia +9, Fortran +9, Chapel +9, C3 -6, Zig -5, Ada +5, C -4, C++ -4, Odin -4, D -4, Rust -3, Nim -2 |
| S-symétrique | 0,991 | C++ (29 %) | C -2, Chapel -2, C++ +1, Odin +1, Julia +1, Fortran +1, D +1, Rust -1 |
| S-noyaux-scalaires | 0,975 | C (50 %) | Ada +5, Zig -3, C++ -1, Odin +1, D -1, Rust -1 |
| S-importées | 0,956 | C (58 %) | Nim -7, Julia +2, Ada -2, Fortran +2, Chapel +2, D +1, Rust +1, Mojo +1 |

## Plafond E par scénario

| Langage | Publié | Contrôle sans mt | S-scalaire | S-scalaire-Mojo | S-symétrique | S-noyaux-scalaires | S-importées |
|---|---|---|---|---|---|---|---|
| C | 85,3 | 86,6 | 44,4 | 44,4 | 79,6 | 79,3 | 85,3 |
| C++ | 78,7 | 81,9 | 42,9 | 42,9 | 82,4 | 69,7 | 78,7 |
| Odin | 78,6 | 82,0 | 42,9 | 42,9 | 82,4 | 74,2 | 78,6 |
| Zig | 70,7 | 74,6 | 38,6 | 38,6 | 74,0 | 59,6 | 70,7 |
| C3 | 82,5 | 85,4 | 43,7 | 43,7 | 83,8 | 76,9 | 82,5 |
| Nim | 72,9 | 75,0 | 45,1 | 45,1 | 74,3 | 69,9 | 41,6 |
| Rust | 78,8 | 81,5 | 44,8 | 44,8 | 74,3 | 72,8 | 78,8 |
| D | 78,8 | 82,4 | 43,3 | 43,3 | 77,6 | 73,2 | 78,8 |
| Ada | 78,1 | 83,3 | 61,5 | 61,5 | 74,1 | 81,2 | 54,6 |
| Chapel | 80,2 | 79,7 | 84,1 | 84,1 | 73,1 | 74,7 | 80,2 |
| Fortran | 74,7 | 75,3 | 79,4 | 79,4 | 77,2 | 67,4 | 74,7 |
| Julia | 66,6 | 68,1 | 71,9 | 71,9 | 70,4 | 64,0 | 66,6 |
| Mojo | 67,9 | 69,2 | 25,7 | 25,5 | 49,4 | 55,5 | 67,9 |
| C# | 56,2 | 59,3 | 25,4 | 25,4 | 48,8 | 42,1 | 56,2 |
| Java | 57,6 | 59,2 | 31,6 | 31,6 | 60,8 | 51,6 | 57,6 |
| Go | 38,5 | 37,0 | 22,8 | 22,8 | 42,9 | 31,5 | 38,5 |
| Haskell | 37,0 | 37,9 | 15,2 | 15,2 | 28,3 | 23,3 | 37,0 |
| OCaml | 19,9 | 21,0 | 22,1 | 22,1 | 22,6 | 20,4 | 19,9 |
| JavaScript | 12,4 | 12,6 | 13,2 | 13,2 | 21,5 | 11,6 | 12,4 |
| Python | 0,5 | 0,6 | 0,6 | 0,6 | 1,0 | 0,6 | 0,5 |
| Lua | 1,2 | 1,5 | 1,5 | 1,5 | 2,7 | 1,4 | 1,2 |

## Références t* (ms) et langage qui les fixe

* Publié : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 36,15 (Rust) ; k9#1 10,78 (Chapel)
* Contrôle sans mt : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 36,15 (Rust)
* S-scalaire : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 4,68 (Chapel) ; k6#0 20,03 (Ada) ; k6#1 47,47 (Fortran) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 36,15 (Rust)
* S-scalaire-Mojo : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 4,68 (Chapel) ; k6#0 20,03 (Ada) ; k6#1 47,47 (Fortran) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 36,15 (Rust)
* S-symétrique : k1#0 38,04 (Mojo) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 77,08 (C++) ; k6#0 56,94 (Mojo) ; k6#1 74,85 (C++) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 36,24 (Fortran)
* S-noyaux-scalaires : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 36,15 (Rust) ; k9#1 10,78 (Chapel)
* S-importées : k1#0 7,21 (Ada) ; k3#0 58,22 (Chapel) ; k4#0 2,84 (C) ; k5#0 3,94 (C) ; k6#0 17,72 (Zig) ; k6#1 32,11 (C) ; k6#2 6,47 (Chapel) ; k6#3 12,42 (C3) ; k7#0 456,85 (C) ; k8#0 107,67 (Ada) ; k9#0 36,15 (Rust) ; k9#1 10,78 (Chapel)

## Variante retenue par E dans S-scalaire (mesures vectorisables)

| Langage | k1#0 | k5#0 | k6#0 | k6#1 | k9#0 |
|---|---|---|---|---|---|
| C | aos 38,4 | natural 158,1 | tuned q6 21,3 | natural q1 83,4 | natural 38,4 |
| C++ | aos 40,2 | natural 77,1 | natural q6 62,4 | natural q1 74,9 | tuned 36,2 |
| Odin | aos 40,3 | natural 77,7 | natural q6 63,3 | natural q1 121,0 | natural 36,3 |
| Zig | aos 41,9 | natural 80,0 | natural q6 67,1 | natural q1 77,7 | natural 40,2 |
| C3 | aos 40,3 | natural 79,1 | natural q6 63,4 | natural q1 108,9 | natural 37,5 |
| Nim | aos 38,8 | natural 81,4 | tuned q6 21,3 | natural q1 95,4 | tuned 36,6 |
| Rust | aos 40,4 | natural 83,7 | tuned q6 23,3 | natural q1 120,3 | tuned 36,2 |
| D | aos 43,7 | natural 84,3 | tuned q6 20,9 | natural q1 88,3 | natural 55,1 |
| Ada | soa 7,2 | natural 86,1 | tuned q6 20,0 | tuned q1 57,5 | tuned 37,8 |
| Chapel | soa 7,7 | tuned 4,7 | tuned q6 22,8 | tuned q1 48,5 | natural 38,9 |
| Fortran | soa 7,5 | tuned 5,5 | tuned q6 22,6 | tuned q1 47,5 | natural 36,2 |
| Julia | soa 8,0 | tuned 6,3 | tuned q6 21,4 | tuned q1 98,8 | natural 37,9 |
| Mojo | aos 38,0 | natural 161,2 | natural q6 56,9 | natural q1 227,3 | natural 265,5 |
| C# | aos 38,9 | natural 86,7 | natural q6 155,7 | natural q1 186,3 | natural 118,9 |
| Java | aos 42,3 | natural 141,9 | natural q6 111,0 | natural q1 111,5 | natural 39,7 |
| Go | aos 47,2 | natural 84,9 | natural q6 138,4 | tuned q1 86,3 | natural 113,9 |
| Haskell | aos 39,2 | natural 349,7 | tuned q6 70,5 | tuned q1 70,2 | natural 401,5 |
| OCaml | soa 12,3 | tuned 71,6 | natural q6 200,6 | tuned q1 214,5 | tuned 62,5 |
| JavaScript | soa 23,2 | tuned 149,9 | tuned q6 131,5 | natural q1 376,4 | tuned 93,7 |
| Python | soa 963,1 | tuned 3096,7 | natural q6 1833,8 | tuned q1 7941,8 | natural 1998,7 |
| Lua | soa 293,9 | natural 1742,4 | natural q6 627,0 | tuned q1 2215,7 | natural 821,6 |
