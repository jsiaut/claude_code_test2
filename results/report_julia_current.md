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
| Avant | 60,6 | 68,3 | 62,3 | 47,1 | 11,98 | 12 | 9–13 | devant Fortran 18 %; derrière Mojo 51 % |
| J-E | 62,3 | 73,3 | 62,3 | 47,1 | 11,57 | 12 | 8–13 | devant Fortran 28 %; derrière Mojo 60 % |
| S1 | 65,3 | 73,3 | 69,6 | 47,1 | 10,53 | 12 | 7–13 | devant Fortran 51 %; derrière Mojo 79 % |
| S1-K5 | 67,0 | 73,3 | 73,8 | 47,1 | 9,56 | 11 | 5–13 | devant Chapel 49 %; derrière Fortran 66 % |

**Avant** : 1. C (2,21, 79,9), 2. Odin (3,15, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,13, 71,6), 6. Rust (6,80, 69,9), 7. Nim (6,90, 69,3), 8. D (7,22, 72,6), 9. Ada (8,02, 71,0), 10. Chapel (8,79, 65,7), 11. Fortran (10,20, 65,4), 12. Julia (11,98, 60,6), 13. Mojo (12,09, 62,3), 14. C# (14,03, 54,9).

**J-E** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,18, 62,3), 14. C# (14,06, 54,9).

**S1** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,78, 77,1), 4. Zig (4,98, 72,3), 5. C3 (5,17, 71,6), 6. Rust (6,88, 69,9), 7. Nim (7,00, 69,3), 8. D (7,30, 72,6), 9. Ada (8,19, 71,0), 10. Chapel (9,01, 65,7), 11. Fortran (10,52, 65,4), 12. Julia (10,53, 65,3), 13. Mojo (12,37, 62,3), 14. C# (14,07, 54,9).

**S1-K5** : 1. C (2,22, 79,9), 2. Odin (3,18, 73,9), 3. C++ (3,81, 77,0), 4. Zig (5,05, 72,2), 5. C3 (5,21, 71,5), 6. Rust (6,98, 69,9), 7. Nim (7,12, 69,2), 8. D (7,40, 72,6), 9. Ada (8,32, 71,0), 10. Chapel (9,16, 65,6), 11. Julia (9,56, 67,0), 12. Fortran (10,68, 65,3), 13. Mojo (12,44, 62,2), 14. C# (14,08, 54,8).

