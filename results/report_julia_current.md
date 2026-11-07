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
| Avant | 60,6 | 68,3 | 62,3 | 47,2 | 12,66 | 13 | 9–14 | devant Swift 28 %; derrière Mojo 54 % |
| J-E | 62,4 | 73,3 | 62,3 | 47,2 | 12,15 | 13 | 8–14 | devant Swift 36 %; derrière Mojo 63 % |
| S1 | 65,3 | 73,3 | 69,6 | 47,2 | 10,88 | 11 | 7–14 | devant Chapel 36 %; derrière Swift 54 % |
| S1-K5 | 67,0 | 73,3 | 73,8 | 47,1 | 9,73 | 11 | 5–14 | devant Chapel 52 %; derrière Swift 68 % |

**Avant** : 1. C (2,19, 80,0), 2. Odin (3,17, 74,0), 3. C++ (3,79, 77,1), 4. C3 (5,09, 71,6), 5. Zig (5,13, 72,3), 6. Rust (6,94, 70,0), 7. Nim (7,15, 69,3), 8. D (7,18, 72,7), 9. Ada (8,25, 71,1), 10. Chapel (9,22, 65,7), 11. Fortran (10,76, 65,4), 12. Swift (10,79, 66,5), 13. Julia (12,66, 60,6), 14. Mojo (12,99, 62,3).

**J-E** : 1. C (2,20, 80,0), 2. Odin (3,17, 74,0), 3. C++ (3,79, 77,1), 4. C3 (5,11, 71,6), 5. Zig (5,14, 72,3), 6. Rust (6,97, 70,0), 7. Nim (7,16, 69,3), 8. D (7,19, 72,7), 9. Ada (8,30, 71,1), 10. Chapel (9,29, 65,7), 11. Fortran (10,85, 65,4), 12. Swift (10,86, 66,5), 13. Julia (12,15, 62,4), 14. Mojo (13,08, 62,3).

**S1** : 1. C (2,20, 80,0), 2. Odin (3,18, 74,0), 3. C++ (3,82, 77,1), 4. C3 (5,14, 71,6), 5. Zig (5,19, 72,3), 6. Rust (7,03, 70,0), 7. D (7,26, 72,7), 8. Nim (7,26, 69,3), 9. Ada (8,44, 71,1), 10. Chapel (9,46, 65,7), 11. Julia (10,88, 65,3), 12. Swift (11,04, 66,5), 13. Fortran (11,09, 65,4), 14. Mojo (13,26, 62,3).

**S1-K5** : 1. C (2,20, 79,9), 2. Odin (3,19, 73,9), 3. C++ (3,85, 77,0), 4. C3 (5,18, 71,6), 5. Zig (5,27, 72,2), 6. Rust (7,13, 69,9), 7. D (7,36, 72,6), 8. Nim (7,39, 69,2), 9. Ada (8,56, 71,0), 10. Chapel (9,62, 65,6), 11. Julia (9,73, 67,0), 12. Swift (11,18, 66,4), 13. Fortran (11,25, 65,4), 14. Mojo (13,33, 62,2).

