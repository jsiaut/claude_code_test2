# Remarque sur Mojo : diagnostics et scénarios

Plan : `docs/MOJO.md`. Mesures : `results/raw_mojo/` (machine 6, 7 processus par cellule). Code :
`analysis/mojo_check.py`. Processus rejetés : aucun.

## Temps (moyenne géométrique des médianes par processus, ms)

| Implémentation | Clé | Temps (ms) |
|---|---|---|
| c | k4:branchless_unsorted: | 3,03 |
| c | k4:natural_unsorted: | 3,89 |
| c | k6:natural:q1 | 65,80 |
| c | k9:natural: | 27,67 |
| mojo | k4:branchless_unsorted: | 12,47 |
| mojo | k4:natural_sorted: | 11,34 |
| mojo | k4:natural_unsorted: | 14,40 |
| mojo | k6:natural:q1 | 136,21 |
| mojo | k6:natural:q6 | 53,17 |
| mojo | k9:natural: | 167,14 |
| mojo_exp | k4:branchless_unsorted: | 15,11 |
| mojo_exp | k4:simd_cold: | 2,44 |
| mojo_exp | k4:simd_unsorted: | 2,22 |
| mojo_noassert | k4:branchless_unsorted: | 12,20 |
| mojo_noassert | k4:natural_unsorted: | 13,33 |
| mojo_noassert | k6:natural:q1 | 65,47 |
| mojo_noassert | k6:natural:q6 | 50,81 |
| mojo_noassert | k9:natural: | 41,03 |

## Rapports (même hôte, IC 95 % par rééchantillonnage des processus)

| Rapport | Valeur | IC 95 % |
|---|---|---|
| noassert/défaut k4:natural_unsorted: | 0,926 | 0,678–1,290 |
| noassert/défaut k4:branchless_unsorted: | 0,979 | 0,815–1,191 |
| noassert/défaut k9:natural: | 0,245 | 0,229–0,266 |
| noassert/défaut k6:natural:q1 | 0,481 | 0,438–0,527 |
| noassert/défaut k6:natural:q6 | 0,956 | 0,892–1,006 |
| simd chaud / sans branchement (mojo_exp) | 0,147 | 0,118–0,183 |
| simd chaud / clang sans branchement | 0,733 | 0,634–0,826 |
| simd caches vidés / simd chaud | 1,096 | 0,981–1,245 |
| naturel trié / non trié (mojo) | 0,788 | 0,615–1,015 |
| noassert K9 naturel / clang K9 naturel | 1,483 | 1,395–1,583 |
| noassert Q1 naturel / clang Q1 naturel | 0,995 | 0,883–1,106 |
| témoin : sans branchement mojo_exp / mojo | 1,212 | 0,945–1,523 |

## Données principales (ms)

| Langage | k4:natural_unsorted: | k4:branchless_unsorted: | k9:natural: | k6:natural:q1 | k6:natural:q6 |
|---|---|---|---|---|---|
| mojo | 12,34 | 12,83 | 202,30 | 227,26 | 56,94 |
| c | 4,04 | 2,84 | 13,86 | 83,44 | 64,00 |
| c_gcc | 6,06 | 5,22 | 14,44 | 84,74 | 64,33 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Mojo | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 59,5 | 62,7 | 67,0 | 43,3 | 13,73 | 14 | 12–15 | devant Julia 23 %; derrière C# 88 % |
| M-E | 62,3 | 70,5 | 67,0 | 43,3 | 13,08 | 14 | 10–14 | devant Julia 37 %; derrière C# 96 % |
| S-B4 | 61,6 | 68,5 | 67,0 | 43,3 | 13,28 | 14 | 11–14 | devant Julia 33 %; derrière C# 95 % |
| S-K4 | 66,7 | 70,5 | 78,1 | 43,3 | 11,59 | 13 | 8–14 | devant Swift 51 %; derrière Julia 71 % |
| S-K4-B4 | 66,0 | 68,5 | 78,1 | 43,3 | 11,95 | 13 | 9–14 | devant Swift 43 %; derrière Julia 68 % |

**Avant** : 1. C (2,19, 80,0), 2. Odin (3,17, 74,0), 3. C++ (3,79, 77,1), 4. C3 (5,11, 71,6), 5. Zig (5,13, 72,3), 6. Rust (6,96, 70,0), 7. Nim (7,15, 69,3), 8. D (7,18, 72,7), 9. Ada (8,29, 71,1), 10. Chapel (9,21, 65,7), 11. Fortran (10,73, 65,4), 12. Swift (10,73, 66,5), 13. Julia (12,01, 62,4), 14. Mojo (13,73, 59,5).

**M-E** : 1. C (2,20, 80,0), 2. Odin (3,17, 74,0), 3. C++ (3,79, 77,1), 4. C3 (5,11, 71,6), 5. Zig (5,14, 72,3), 6. Rust (6,97, 70,0), 7. Nim (7,16, 69,3), 8. D (7,19, 72,7), 9. Ada (8,30, 71,1), 10. Chapel (9,29, 65,7), 11. Fortran (10,85, 65,4), 12. Swift (10,86, 66,5), 13. Julia (12,15, 62,4), 14. Mojo (13,08, 62,3).

**S-B4** : 1. C (2,19, 80,0), 2. Odin (3,17, 74,0), 3. C++ (3,79, 77,1), 4. C3 (5,11, 71,6), 5. Zig (5,14, 72,3), 6. Rust (6,96, 70,0), 7. Nim (7,16, 69,3), 8. D (7,18, 72,7), 9. Ada (8,30, 71,1), 10. Chapel (9,26, 65,7), 11. Fortran (10,81, 65,4), 12. Swift (10,82, 66,5), 13. Julia (12,10, 62,4), 14. Mojo (13,28, 61,6).

**S-K4** : 1. C++ (2,44, 80,0), 2. C (2,87, 79,2), 3. Zig (2,96, 75,6), 4. Odin (4,20, 73,3), 5. C3 (5,73, 71,5), 6. Ada (7,16, 72,8), 7. Rust (7,66, 69,5), 8. Nim (7,75, 69,0), 9. D (8,01, 72,0), 10. Chapel (10,12, 65,3), 11. Fortran (10,58, 66,5), 12. Swift (11,43, 66,2), 13. Mojo (11,59, 66,7), 14. Julia (12,96, 60,9).

**S-K4-B4** : 1. C++ (2,44, 80,0), 2. C (2,87, 79,2), 3. Zig (2,96, 75,6), 4. Odin (4,19, 73,3), 5. C3 (5,73, 71,5), 6. Ada (7,14, 72,8), 7. Rust (7,64, 69,5), 8. Nim (7,72, 69,0), 9. D (7,98, 72,0), 10. Chapel (10,06, 65,3), 11. Fortran (10,52, 66,5), 12. Swift (11,34, 66,2), 13. Mojo (11,95, 66,0), 14. Julia (12,93, 60,9).

