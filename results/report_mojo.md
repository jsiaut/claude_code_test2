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
| mojo | 12,34 | 12,83 | 265,49 | 227,26 | 56,94 |
| c | 4,04 | 2,84 | 38,39 | 83,44 | 64,00 |
| c_gcc | 6,06 | 5,22 | 36,61 | 84,74 | 64,33 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Mojo | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 60,0 | 62,7 | 67,9 | 43,6 | 12,49 | 13 | 10–14 | devant Julia 31 %; derrière C# 91 % |
| M-E | 62,7 | 70,5 | 67,9 | 43,6 | 11,87 | 13 | 9–13 | devant Julia 46 %; derrière C# 98 % |
| S-B4 | 62,0 | 68,5 | 67,9 | 43,6 | 12,06 | 13 | 10–13 | devant Julia 42 %; derrière C# 97 % |
| S-K4 | 67,2 | 70,5 | 79,2 | 43,6 | 10,38 | 11 | 7–13 | devant D 37 %; derrière Chapel 54 % |
| S-K4-B4 | 66,5 | 68,5 | 79,2 | 43,6 | 10,70 | 12 | 7–13 | devant Chapel 49 %; derrière Julia 75 % |

**Avant** : 1. C (1,67, 80,1), 2. C++ (2,71, 77,0), 3. Odin (4,04, 72,3), 4. C3 (5,05, 71,0), 5. Zig (5,73, 71,5), 6. Nim (6,53, 69,5), 7. Ada (6,95, 71,6), 8. Rust (7,24, 69,4), 9. D (8,24, 71,0), 10. Fortran (9,40, 66,3), 11. Chapel (9,70, 64,1), 12. Julia (11,47, 62,2), 13. Mojo (12,49, 60,0), 14. C# (14,08, 54,8).

**M-E** : 1. C (1,67, 80,1), 2. C++ (2,71, 77,0), 3. Odin (4,04, 72,3), 4. C3 (5,06, 71,0), 5. Zig (5,73, 71,5), 6. Nim (6,56, 69,5), 7. Ada (6,96, 71,6), 8. Rust (7,27, 69,4), 9. D (8,29, 71,0), 10. Fortran (9,52, 66,3), 11. Chapel (9,84, 64,1), 12. Julia (11,63, 62,2), 13. Mojo (11,87, 62,7), 14. C# (14,14, 54,8).

**S-B4** : 1. C (1,67, 80,1), 2. C++ (2,71, 77,0), 3. Odin (4,04, 72,3), 4. C3 (5,06, 71,0), 5. Zig (5,73, 71,5), 6. Nim (6,55, 69,5), 7. Ada (6,96, 71,6), 8. Rust (7,26, 69,4), 9. D (8,27, 71,0), 10. Fortran (9,48, 66,3), 11. Chapel (9,80, 64,1), 12. Julia (11,58, 62,2), 13. Mojo (12,06, 62,0), 14. C# (14,14, 54,8).

**S-K4** : 1. C++ (1,86, 79,8), 2. C (2,12, 79,3), 3. Zig (3,75, 74,8), 4. Odin (5,10, 71,5), 5. C3 (5,66, 70,8), 6. Ada (6,04, 73,4), 7. Nim (7,20, 69,2), 8. Rust (7,91, 69,0), 9. Fortran (9,19, 67,5), 10. D (9,19, 70,2), 11. Mojo (10,38, 67,2), 12. Chapel (10,57, 63,7), 13. Julia (12,32, 60,9), 14. C# (13,88, 58,9).

**S-K4-B4** : 1. C++ (1,86, 79,8), 2. C (2,12, 79,3), 3. Zig (3,75, 74,8), 4. Odin (5,09, 71,5), 5. C3 (5,65, 70,8), 6. Ada (6,03, 73,4), 7. Nim (7,16, 69,2), 8. Rust (7,87, 69,0), 9. Fortran (9,13, 67,5), 10. D (9,14, 70,2), 11. Chapel (10,51, 63,7), 12. Mojo (10,70, 66,5), 13. Julia (12,29, 60,9), 14. C# (13,87, 58,9).

