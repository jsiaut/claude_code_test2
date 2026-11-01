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
| Avant | 62,5 | 68,3 | 66,6 | 47,8 | 11,73 | 12 | 9–13 | devant Fortran 23 %; derrière Mojo 57 % |
| J-E | 64,3 | 73,3 | 66,6 | 47,8 | 11,24 | 12 | 7–13 | devant Fortran 34 %; derrière Mojo 66 % |
| S1 | 67,4 | 73,3 | 74,5 | 47,8 | 9,89 | 11 | 6–13 | devant Chapel 42 %; derrière Fortran 60 % |
| S1-K5 | 69,2 | 73,3 | 79,0 | 47,8 | 8,64 | 10 | 4–12 | devant Ada 47 %; derrière Chapel 60 % |

**Avant** : 1. C (1,90, 80,0), 2. Odin (3,59, 73,5), 3. C++ (3,80, 76,6), 4. Zig (4,76, 72,7), 5. C3 (5,71, 71,2), 6. Nim (6,65, 69,7), 7. Rust (6,65, 70,5), 8. D (7,42, 72,6), 9. Ada (7,98, 71,7), 10. Chapel (8,72, 66,1), 11. Fortran (10,14, 66,1), 12. Julia (11,73, 62,5), 13. Mojo (12,12, 62,8), 14. C# (14,01, 56,0).

**J-E** : 1. C (1,90, 80,0), 2. Odin (3,60, 73,5), 3. C++ (3,80, 76,6), 4. Zig (4,77, 72,7), 5. C3 (5,74, 71,2), 6. Nim (6,67, 69,7), 7. Rust (6,68, 70,5), 8. D (7,44, 72,6), 9. Ada (8,03, 71,7), 10. Chapel (8,80, 66,1), 11. Fortran (10,25, 66,1), 12. Julia (11,24, 64,3), 13. Mojo (12,21, 62,8), 14. C# (14,03, 56,0).

**S1** : 1. C (1,91, 80,0), 2. Odin (3,61, 73,5), 3. C++ (3,84, 76,6), 4. Zig (4,85, 72,7), 5. C3 (5,80, 71,2), 6. Rust (6,78, 70,5), 7. Nim (6,80, 69,7), 8. D (7,55, 72,6), 9. Ada (8,19, 71,7), 10. Chapel (8,99, 66,1), 11. Julia (9,89, 67,4), 12. Fortran (10,51, 66,1), 13. Mojo (12,38, 62,8), 14. C# (14,05, 56,0).

**S1-K5** : 1. C (1,91, 79,9), 2. Odin (3,66, 73,4), 3. C++ (3,89, 76,5), 4. Zig (4,93, 72,6), 5. C3 (5,88, 71,2), 6. Rust (6,93, 70,4), 7. Nim (6,96, 69,6), 8. D (7,71, 72,5), 9. Ada (8,32, 71,6), 10. Julia (8,64, 69,2), 11. Chapel (9,17, 66,0), 12. Fortran (10,66, 66,1), 13. Mojo (12,44, 62,7), 14. C# (14,05, 55,9).

