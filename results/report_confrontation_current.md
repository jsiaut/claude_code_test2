# Confrontation avec le « Banc de sympathie mécanique » : résultats

Plan : `docs/CONFRONTATION.md`. Calcul : `analysis/confrontation.py`. Rangs sur les 18 langages communs.

## Test 2 : rapports appariés (réécriture standard / origine, même hôte)

| Langage | Mesure | Origine (ms) | Standard (ms) | Rapport [IC 95 %] | Hôte / données principales |
|---|---|---|---|---|---|
| C | k1:soa:energy | 5,85 | 5,65 | 0,97 [0,94–0,99] | 0,75 |
| C | k3:sw_padded: | 80,28 | 81,14 | 1,01 [0,99–1,02] | 1,34 |
| C | k3:rmw_padded: | 251,06 | 250,42 | 1,00 [0,91–1,09] | 1,11 |
| C | k5:tuned: | 6,28 | 6,58 | 1,05 [0,92–1,21] | 1,60 |
| C | k6:tuned:q1 | 27,10 | 51,28 | 1,89 [1,61–2,19] | 0,84 |
| C | k6:mt:q6 | 5,70 | 5,61 | 0,98 [0,82–1,19] | 0,67 |
| C | k6:mt:q1 | 9,07 | 15,47 | 1,71 [1,46–1,98] | 0,67 |
| C | k7:tuned: | 358,62 | 439,00 | 1,22 [1,14–1,32] | 0,78 |
| C | k9:mt: | 10,51 | 9,39 | 0,89 [0,83–0,96] | 0,79 |
| C++ | k7:tuned: | 380,86 | 419,85 | 1,10 [0,96–1,29] | 0,79 |
| C++ | k9:tuned: | 27,86 | 28,57 | 1,03 [0,94–1,16] | 0,77 |
| C++ | k9:mt: | 14,81 | 14,95 | 1,01 [0,96–1,06] | 0,76 |
| Nim | k1:soa:energy | 5,92 | 5,59 | 0,94 [0,91–0,98] | 0,80 |
| Nim | k5:tuned: | 6,64 | 9,08 | 1,37 [1,22–1,53] | 1,39 |
| Nim | k7:tuned: | 384,21 | 463,68 | 1,21 [1,11–1,32] | 0,78 |
| Nim | k9:tuned: | 27,86 | 27,44 | 0,98 [0,94–1,03] | 0,76 |
| Nim | k9:mt: | 13,07 | 10,08 | 0,77 [0,71–0,84] | 0,79 |
| D | k1:soa:energy | 5,51 | 5,57 | 1,01 [0,95–1,07] | 0,76 |
| D | k5:tuned: | 7,11 | 8,52 | 1,20 [1,05–1,36] | 1,58 |
| D | k7:tuned: | 401,26 | 380,65 | 0,95 [0,88–1,03] | 0,82 |
| D | k9:tuned: | 27,43 | 26,32 | 0,96 [0,93–0,99] | 0,74 |
| D | k9:mt: | 12,79 | 13,32 | 1,04 [0,98–1,11] | 0,70 |
| Ada | k5:tuned: | 7,02 | 8,19 | 1,17 [1,04–1,30] | 1,42 |
| Ada | k6:tuned:q6 | 15,97 | 15,26 | 0,96 [0,92–0,99] | 0,80 |
| Ada | k6:tuned:q1 | 48,40 | 37,45 | 0,77 [0,67–0,89] | 0,84 |
| Ada | k6:mt:q6 | 16,19 | 16,99 | 1,05 [0,95–1,16] | 1,66 |
| Ada | k6:mt:q1 | 20,40 | 15,73 | 0,77 [0,72–0,83] | 0,65 |
| Ada | k7:tuned: | 381,36 | 500,36 | 1,31 [1,16–1,48] | 0,73 |
| Ada | k9:tuned: | 36,17 | 37,98 | 1,05 [0,88–1,22] | 0,96 |
| Ada | k9:mt: | 20,14 | 19,88 | 0,99 [0,91–1,06] | 0,86 |
| Fortran | k1:soa:energy | 5,66 | 5,53 | 0,98 [0,94–1,01] | 0,76 |
| Fortran | k5:tuned: | 8,86 | 8,76 | 0,99 [0,91–1,07] | 1,61 |
| Fortran | k6:tuned:q6 | 14,46 | 15,78 | 1,09 [1,03–1,15] | 0,64 |
| Fortran | k6:tuned:q1 | 36,97 | 42,59 | 1,15 [1,01–1,34] | 0,78 |
| Chapel | k1:aos:energy | 33,93 | 33,36 | 0,98 [0,92–1,05] | 0,67 |
| Chapel | k1:soa:energy | 5,08 | 5,32 | 1,05 [0,94–1,19] | — |
| Chapel | k5:tuned: | 5,02 | 8,89 | 1,77 [1,52–2,06] | — |
| Chapel | k7:tuned: | 363,76 | 463,50 | 1,27 [1,16–1,40] | 0,77 |
| Go | k1:soa:energy | 5,67 | 8,39 | 1,48 [1,31–1,68] | 0,75 |
| Go | k5:tuned: | 10,72 | 96,48 | 9,00 [6,98–11,32] | 0,57 |
| Go | k6:tuned:q6 | 16,04 | 40,58 | 2,53 [2,12–3,11] | 0,80 |
| Go | k6:mt:q6 | 5,19 | 15,87 | 3,05 [2,52–3,54] | 0,67 |
| Java | k1:soa:energy | 5,87 | 8,96 | 1,53 [1,35–1,72] | 0,67 |
| Java | k5:tuned: | 11,74 | 57,24 | 4,87 [4,14–6,04] | 1,69 |
| Java | k6:tuned:q6 | 15,83 | 123,16 | 7,78 [7,30–8,27] | 0,61 |
| Java | k6:tuned:q1 | 69,14 | 603,70 | 8,73 [8,18–9,35] | 0,78 |
| Java | k6:mt:q6 | 6,55 | 32,04 | 4,89 [4,48–5,34] | 0,68 |
| Java | k6:mt:q1 | 22,99 | 193,50 | 8,42 [7,74–9,23] | 0,75 |

Replis et pénalités : mojo k6:mt:q6 : même travail sur un thread (tuned) ; mojo k6:mt:q1 : même travail sur un thread (tuned) ; mojo k9:mt: : même travail sur un thread (tuned) ; fortran k6:mt:q6 : même travail sur un thread (tuned) ; fortran k6:mt:q1 : même travail sur un thread (tuned) ; fortran k9:mt: : même travail sur un thread (natural) ; mojo k3 : pénalité : temps admissible le plus lent des 18 (python) ; fortran k3 : pénalité : temps admissible le plus lent des 18 (python).

## Scénarios

| Langage | Leur rang | A publié | B (C_R) | C (E_R) | D (C_R + E_R) | C A→R | E A→R |
|---|---|---|---|---|---|---|---|
| C | 11,0 | 1 | 5 | 1 | 5 | 91,7 → 64,0 | 85,3 → 80,7 |
| C++ | 3,5 | 2 | 2 | 2 | 2 | 92,4 → 76,8 | 78,7 → 77,7 |
| Odin | 2,0 | 3 | 1 | 3 | 1 | 81,5 → 81,5 | 78,6 → 78,7 |
| C3 | 5,0 | 4 | 4 | 4 | 4 | 73,1 → 71,9 | 82,5 → 82,6 |
| Zig | 1,0 | 5 | 3 | 5 | 3 | 87,2 → 87,2 | 70,7 → 70,8 |
| Nim | 10,0 | 6 | 7 | 7 | 7 | 76,1 → 68,8 | 72,9 → 70,3 |
| Ada | 7,0 | 7 | 9 | 8 | 9 | 80,6 → 65,4 | 78,1 → 75,1 |
| Rust | 6,0 | 8 | 6 | 6 | 6 | 73,6 → 72,3 | 79,6 → 79,7 |
| D | 3,5 | 9 | 8 | 9 | 8 | 87,1 → 77,6 | 74,7 → 73,5 |
| Chapel | 9,0 | 10 | 10 | 10 | 11 | 61,8 → 56,9 | 80,2 → 72,1 |
| Fortran | 14,0 | 11 | 13 | 12 | 14 | 65,3 → 49,9 | 74,7 → 32,6 |
| Julia | 13,0 | 12 | 11 | 11 | 10 | 73,3 → 72,2 | 66,6 → 66,7 |
| Mojo | 15,0 | 13 | 12 | 14 | 13 | 70,5 → 69,7 | 67,9 → 29,9 |
| C# | 8,0 | 14 | 14 | 13 | 12 | 68,8 → 68,8 | 56,2 → 56,3 |
| Java | 12,0 | 15 | 15 | 15 | 15 | 41,5 → 38,2 | 57,6 → 37,9 |
| Go | 17,0 | 16 | 16 | 16 | 16 | 48,7 → 42,9 | 38,5 → 28,6 |
| JavaScript | 18,0 | 17 | 17 | 17 | 17 | 11,6 → 11,6 | 12,4 → 12,4 |
| Python | 16,0 | 18 | 18 | 18 | 18 | 24,4 → 24,4 | 0,5 → 0,5 |

| Scénario | Spearman | Kendall | Σd² | part de C | rang de C |
|---|---|---|---|---|---|
| A | 0,76 | 0,56 | 236,5 | 42 % | 1 |
| B | 0,85 | 0,68 | 143,5 | 25 % | 5 |
| C | 0,78 | 0,61 | 210,5 | 48 % | 1 |
| D | 0,87 | 0,69 | 125,5 | 29 % | 5 |

Sensibilité (K3 retiré du plafond de Mojo et de Fortran, configuration de référence), scénario C : Spearman 0,80, rang de C 1.

Sensibilité (K3 retiré du plafond de Mojo et de Fortran, configuration de référence), scénario D : Spearman 0,87, rang de C 6.

## Test 3 : leur S comme quatrième pilier

| w | Spearman avec leur ordre | avec mon score de référence | P(C premier) | rang de C | 5 premiers |
|---|---|---|---|---|---|
| 0,00 | 0,76 | 1,00 | 0,93 | 1,0 | C, C++, Odin, Ada, Zig |
| 0,05 | 0,80 | 0,99 | 0,88 | 1,0 | C, C++, Odin, Zig, Ada |
| 0,10 | 0,81 | 0,98 | 0,76 | 1,0 | C, C++, Zig, Odin, D |
| 0,15 | 0,81 | 0,98 | 0,57 | 1,0 | C, C++, Zig, Odin, D |
| 0,20 | 0,82 | 0,98 | 0,33 | 2,0 | C++, C, Zig, Odin, D |
| 0,25 | 0,85 | 0,97 | 0,16 | 3,0 | C++, Zig, C, Odin, D |
| 0,30 | 0,87 | 0,95 | 0,06 | 4,0 | C++, Zig, Odin, C, D |
| 0,35 | 0,88 | 0,94 | 0,02 | 4,0 | Zig, C++, Odin, C, D |
| 0,40 | 0,92 | 0,92 | 0,01 | 6,0 | Zig, C++, Odin, D, C3 |
| 0,45 | 0,93 | 0,90 | 0,00 | 7,0 | Zig, C++, Odin, D, C3 |
| 0,50 | 0,94 | 0,90 | 0,00 | 7,0 | Zig, C++, Odin, D, C3 |
| 0,55 | 0,96 | 0,88 | 0,00 | 8,0 | Zig, C++, Odin, D, C3 |
| 0,60 | 0,96 | 0,88 | 0,00 | 8,0 | Zig, C++, Odin, D, C3 |
| 0,65 | 0,96 | 0,88 | 0,00 | 8,0 | Zig, Odin, C++, D, C3 |
| 0,70 | 0,97 | 0,87 | 0,00 | 8,0 | Zig, Odin, C++, D, C3 |
| 0,75 | 0,97 | 0,84 | 0,00 | 10,0 | Zig, Odin, C++, D, C3 |
| 0,80 | 0,97 | 0,84 | 0,00 | 10,0 | Zig, Odin, C++, D, C3 |
| 0,85 | 0,99 | 0,79 | 0,00 | 11,0 | Zig, Odin, C++, D, C3 |
| 0,90 | 0,99 | 0,78 | 0,00 | 11,0 | Zig, Odin, C++, D, C3 |
| 0,95 | 1,00 | 0,77 | 0,00 | 11,0 | Zig, Odin, C++, D, C3 |
| 1,00 | 1,00 | 0,76 | 0,00 | 11,0 | Zig, Odin, C++, D, C3 |

Seuils : P(C premier) < 0,5 à partir de w = 0,20 ; ordre plus proche du leur à partir de w = 0,45 ; Spearman avec leur ordre ≥ 0,95 à partir de w = 0,55.

## Test 4 : accord des deux grilles

| Leur principe | Mes capacités | Spearman (mes notes v2) | Spearman (sous leur règle) |
|---|---|---|---|
| P1 accès prévisible | A1, F1 | 0,83 | 0,83 |
| P2 layout | A2, A3, A4, A5, A7, A8 | 0,69 | 0,79 |
| P3 SoA | A6 | 1,00 | 1,00 |
| P4 faux partage | D3 | 0,58 | 0,56 |
| P5 concurrence | D2, D5 | 0,55 | 0,61 |
| P7 allocation | B1, B2, B3, B4 | 0,94 | 0,94 |
| P8 SIMD/ILP | C1, C2, C4 | 0,53 | 0,74 |
| P9 branchements | E3 | 0,48 | 0,61 |
| P10 hiérarchie mémoire | E4 | 0,57 | 0,82 |
| P11 transparence | E1, E2, E5, E6 | 0,62 | 0,49 |
| P12 threads/topologie | C5, D1, D4, F2 | 0,29 | 0,76 |

Accord d'ensemble (11 principes communs, leurs poids) : 0,74 avec mes notes v2, 0,81 sous leur règle. Correspondances à une capacité : 60 % des 72 cellules diffèrent de moins de 0,5.

Désaccords (|leur niveau / 4 − ma note sous leur règle| ≥ 0,5) :

* P1 accès prévisible, JavaScript : eux 2/4, moi 0,00 (A1 0,00, F1 0,00)
* P2 layout, Julia : eux 0/4, moi 0,75 (A2 1,00, A3 0,00, A4 0,50, A5 1,00, A7 1,00, A8 1,00)
* P2 layout, Go : eux 0/4, moi 0,67 (A2 1,00, A3 0,00, A4 0,50, A5 0,50, A7 1,00, A8 1,00)
* P3 SoA, C++ : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, D : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, C3 : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Rust : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Ada : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, C# : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Chapel : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Nim : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, C : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Java : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Julia : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Fortran : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Mojo : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Python : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, Go : eux 2/4, moi 0,00 (A6 0,00)
* P3 SoA, JavaScript : eux 2/4, moi 0,00 (A6 0,00)
* P4 faux partage, D : eux 2/4, moi 1,00 (D3 1,00)
* P4 faux partage, C3 : eux 2/4, moi 0,00 (D3 0,00)
* P4 faux partage, Rust : eux 2/4, moi 0,00 (D3 0,00)
* P4 faux partage, Ada : eux 2/4, moi 0,00 (D3 0,00)
* P4 faux partage, Nim : eux 2/4, moi 0,00 (D3 0,00)
* P4 faux partage, Julia : eux 0/4, moi 0,50 (D3 0,50)
* P5 concurrence, D : eux 2/4, moi 1,00 (D2 1,00, D5 1,00)
* P5 concurrence, Mojo : eux 2/4, moi 1,00 (D2 1,00, D5 1,00)
* P9 branchements, D : eux 2/4, moi 1,00 (E3 1,00)
* P9 branchements, C# : eux 2/4, moi 0,00 (E3 0,00)
* P9 branchements, Nim : eux 2/4, moi 1,00 (E3 1,00)
* P9 branchements, Julia : eux 2/4, moi 0,00 (E3 0,00)
* P9 branchements, Fortran : eux 4/4, moi 0,00 (E3 0,00)
* P10 hiérarchie mémoire, Julia : eux 1/4, moi 1,00 (E4 1,00)
* P10 hiérarchie mémoire, Python : eux 2/4, moi 0,00 (E4 0,00)
* P11 transparence, Odin : eux 2/4, moi 1,00 (E1 1,00, E2 1,00, E5 1,00, E6 1,00)
* P11 transparence, C3 : eux 2/4, moi 1,00 (E1 1,00, E2 1,00, E5 1,00, E6 1,00)
* P11 transparence, Nim : eux 2/4, moi 1,00 (E1 1,00, E2 1,00, E5 1,00, E6 1,00)
* P11 transparence, Mojo : eux 2/4, moi 1,00 (E1 1,00, E2 1,00, E5 1,00, E6 1,00)
* P12 threads/topologie, Zig : eux 4/4, moi 0,50 (C5 0,00, D1 1,00, D4 1,00, F2 0,00)
* P12 threads/topologie, Odin : eux 4/4, moi 0,50 (C5 0,00, D1 1,00, D4 1,00, F2 0,00)
* P12 threads/topologie, C3 : eux 3/4, moi 0,25 (C5 0,00, D1 1,00, D4 0,00, F2 0,00)
* P12 threads/topologie, Python : eux 4/4, moi 0,50 (C5 0,50, D1 0,50, D4 1,00, F2 0,00)
