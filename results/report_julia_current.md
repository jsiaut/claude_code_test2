# Remarque sur Julia : rapports appariés et scénarios

Plan : `docs/JULIA.md`. Mesures : `results/raw_julia/` (machine 7, 7 processus par cellule). Code :
`analysis/julia_check.py`. Processus rejetés : aucun.

## Temps (moyenne géométrique des médianes par processus, ms)

| Implémentation | Clé | Temps (ms) |
|---|---|---|
| c | k5:tuned: | 6,44 |
| c | k6:mt:q1 | 9,20 |
| c | k6:tuned:q1 | 29,13 |
| c | k7:tuned: | 345,87 |
| c | k8:tuned: | 247,17 |
| c_gcc | k8:tuned: | 138,14 |
| julia | k10:tuned: | 440,04 |
| julia | k1:soa:energy | 5,96 |
| julia | k5:tuned: | 6,51 |
| julia | k6:mt:q1 | 29,03 |
| julia | k6:tuned:q1 | 81,27 |
| julia | k6:tuned:q6 | 16,31 |
| julia | k7:tuned: | 570,95 |
| julia | k8:tuned: | 303,76 |
| julia | k9:tuned: | 28,23 |
| julia_c512 | k5:tuned: | 6,33 |
| julia_exp | k10:tuned: | 17,90 |
| julia_exp | k1:soa:energy | 5,94 |
| julia_exp | k5:tuned: | 6,91 |
| julia_exp | k6:mt:q1 | 14,69 |
| julia_exp | k6:tuned:q1 | 42,68 |
| julia_exp | k6:tuned:q6 | 16,45 |
| julia_exp | k7:tuned: | 394,16 |
| julia_exp | k8:tuned: | 251,09 |
| julia_exp | k9:tuned: | 27,46 |

## Rapports appariés (julia_exp / julia ; K5 : julia_c512 / julia)

| Clé | Rapport | IC 95 % |
|---|---|---|
| k6:tuned:q1 | 0,525 | 0,453–0,596 |
| k6:mt:q1 | 0,506 | 0,445–0,580 |
| k7:tuned: | 0,690 | 0,594–0,821 |
| k8:tuned: | 0,827 | 0,710–0,929 |
| k10:tuned: | 0,041 | 0,028–0,063 |
| k5:tuned: | 1,062 | 0,825–1,381 |
| k9:tuned: | 0,973 | 0,938–1,008 |
| k6:tuned:q6 | 1,009 | 0,909–1,112 |
| k1:soa:energy | 0,997 | 0,924–1,083 |
| k5:tuned: (julia_c512) | 0,972 | 0,797–1,176 |

## Report sur les données principales (transfert ou pont par le C de clang)

| Clé | Julia (données principales) | Transfert | Pont | Écart | Retenu |
|---|---|---|---|---|---|
| k6:tuned:q1 | 98,82 ms | 51,90 ms | 47,05 ms | 10,3 % | transfert (0,525) |
| k6:mt:q1 | 34,53 ms | 17,48 ms | 21,47 ms | -18,6 % | transfert (0,506) |
| k7:tuned: | 731,08 ms | 504,71 ms | 520,63 ms | -3,1 % | transfert (0,690) |
| k8:tuned: | 347,23 ms | 287,02 ms | 269,84 ms | 6,4 % | transfert (0,827) |
| k5:tuned: | 6,29 ms | 6,12 ms | 3,87 ms | 58,2 % | pont (0,615) |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Julia | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 62,2 | 68,3 | 66,6 | 46,7 | 11,74 | 12 | 8–13 | devant Fortran 21 %; derrière Mojo 54 % |
| J-E | 64,0 | 73,3 | 66,6 | 46,7 | 11,25 | 12 | 7–13 | devant Fortran 30 %; derrière Mojo 63 % |
| S1 | 67,1 | 73,3 | 74,5 | 46,7 | 9,78 | 11 | 5–13 | devant Chapel 44 %; derrière Fortran 55 % |
| S1-K5 | 68,9 | 73,3 | 79,0 | 46,7 | 8,48 | 9 | 4–12 | devant Rust 39 %; derrière D 56 % |

**Avant** : 1. C (1,67, 80,1), 2. C++ (2,72, 77,0), 3. Odin (4,06, 72,3), 4. C3 (5,10, 71,0), 5. Zig (5,79, 71,5), 6. Nim (6,64, 69,5), 7. Ada (7,05, 71,6), 8. Rust (7,36, 69,4), 9. D (8,39, 71,0), 10. Chapel (8,94, 65,9), 11. Fortran (9,68, 66,3), 12. Julia (11,74, 62,2), 13. Mojo (11,98, 62,7), 14. C# (14,17, 54,8).

**J-E** : 1. C (1,67, 80,1), 2. C++ (2,72, 77,0), 3. Odin (4,07, 72,3), 4. C3 (5,13, 71,0), 5. Zig (5,80, 71,5), 6. Nim (6,66, 69,5), 7. Ada (7,09, 71,6), 8. Rust (7,41, 69,4), 9. D (8,43, 71,0), 10. Chapel (9,03, 65,9), 11. Fortran (9,78, 66,3), 12. Julia (11,25, 64,0), 13. Mojo (12,07, 62,7), 14. C# (14,19, 54,8).

**S1** : 1. C (1,67, 80,1), 2. C++ (2,74, 77,0), 3. Odin (4,10, 72,3), 4. C3 (5,18, 71,0), 5. Zig (5,91, 71,5), 6. Nim (6,80, 69,5), 7. Ada (7,23, 71,6), 8. Rust (7,53, 69,4), 9. D (8,64, 71,0), 10. Chapel (9,23, 65,9), 11. Julia (9,78, 67,1), 12. Fortran (10,03, 66,3), 13. Mojo (12,25, 62,7), 14. C# (14,19, 54,8).

**S1-K5** : 1. C (1,67, 80,0), 2. C++ (2,78, 77,0), 3. Odin (4,16, 72,2), 4. C3 (5,26, 70,9), 5. Zig (6,01, 71,4), 6. Nim (6,95, 69,5), 7. Ada (7,35, 71,5), 8. Rust (7,70, 69,3), 9. Julia (8,48, 68,9), 10. D (8,83, 70,9), 11. Chapel (9,41, 65,8), 12. Fortran (10,17, 66,2), 13. Mojo (12,31, 62,7), 14. C# (14,19, 54,7).

