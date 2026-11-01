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
| Avant | 62,5 | 68,3 | 66,6 | 47,8 | 11,72 | 12 | 8–13 | devant Fortran 23 %; derrière Mojo 57 % |
| J-E | 64,3 | 73,3 | 66,6 | 47,8 | 11,23 | 12 | 7–13 | devant Fortran 34 %; derrière Mojo 66 % |
| S1 | 67,4 | 73,3 | 74,5 | 47,8 | 9,87 | 11 | 6–13 | devant Chapel 42 %; derrière Fortran 60 % |
| S1-K5 | 69,2 | 73,3 | 79,0 | 47,8 | 8,60 | 10 | 4–12 | devant Ada 47 %; derrière Chapel 60 % |

**Avant** : 1. C (2,19, 80,0), 2. Odin (3,47, 73,5), 3. C++ (4,16, 76,6), 4. Zig (4,65, 72,7), 5. C3 (5,58, 71,2), 6. Rust (6,57, 70,5), 7. Nim (6,58, 69,7), 8. D (7,35, 72,6), 9. Ada (7,94, 71,7), 10. Chapel (8,69, 66,1), 11. Fortran (10,13, 66,1), 12. Julia (11,72, 62,5), 13. Mojo (12,12, 62,8), 14. C# (14,01, 56,0).

**J-E** : 1. C (2,20, 80,0), 2. Odin (3,47, 73,5), 3. C++ (4,16, 76,6), 4. Zig (4,66, 72,7), 5. C3 (5,61, 71,2), 6. Nim (6,60, 69,7), 7. Rust (6,61, 70,5), 8. D (7,37, 72,6), 9. Ada (7,99, 71,7), 10. Chapel (8,77, 66,1), 11. Fortran (10,24, 66,1), 12. Julia (11,23, 64,3), 13. Mojo (12,21, 62,8), 14. C# (14,03, 56,0).

**S1** : 1. C (2,20, 80,0), 2. Odin (3,49, 73,5), 3. C++ (4,21, 76,6), 4. Zig (4,74, 72,7), 5. C3 (5,67, 71,2), 6. Rust (6,70, 70,5), 7. Nim (6,73, 69,7), 8. D (7,49, 72,6), 9. Ada (8,15, 71,7), 10. Chapel (8,97, 66,1), 11. Julia (9,87, 67,4), 12. Fortran (10,51, 66,1), 13. Mojo (12,38, 62,8), 14. C# (14,04, 56,0).

**S1-K5** : 1. C (2,21, 79,9), 2. Odin (3,53, 73,4), 3. C++ (4,27, 76,5), 4. Zig (4,83, 72,6), 5. C3 (5,76, 71,2), 6. Rust (6,85, 70,4), 7. Nim (6,89, 69,6), 8. D (7,64, 72,5), 9. Ada (8,29, 71,6), 10. Julia (8,60, 69,2), 11. Chapel (9,15, 66,0), 12. Fortran (10,65, 66,1), 13. Mojo (12,44, 62,7), 14. C# (14,05, 55,9).

