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
| Avant | 60,0 | 62,7 | 67,9 | 43,8 | 12,74 | 13 | 11–14 | devant Julia 20 %; derrière C# 88 % |
| M-E | 62,8 | 70,5 | 67,9 | 43,8 | 12,20 | 13 | 10–13 | devant Julia 34 %; derrière C# 96 % |
| S-B4 | 62,1 | 68,5 | 67,9 | 43,8 | 12,38 | 13 | 10–13 | devant Julia 30 %; derrière C# 95 % |
| S-K4 | 67,3 | 70,5 | 79,2 | 43,8 | 10,90 | 12 | 7–13 | devant Fortran 40 %; derrière Julia 68 % |
| S-K4-B4 | 66,6 | 68,5 | 79,2 | 43,8 | 11,21 | 12 | 8–13 | devant Fortran 34 %; derrière Julia 64 % |

**Avant** : 1. C (1,89, 80,0), 2. C++ (3,53, 76,6), 3. Odin (3,80, 72,6), 4. Zig (4,69, 72,7), 5. C3 (6,45, 70,3), 6. Rust (6,54, 70,5), 7. Nim (6,55, 69,7), 8. D (7,31, 72,6), 9. Ada (7,92, 71,7), 10. Chapel (8,65, 66,1), 11. Fortran (10,09, 66,1), 12. Julia (11,07, 64,3), 13. Mojo (12,74, 60,0), 14. C# (13,94, 56,0).

**M-E** : 1. C (1,90, 80,0), 2. C++ (3,53, 76,6), 3. Odin (3,80, 72,6), 4. Zig (4,69, 72,7), 5. C3 (6,47, 70,3), 6. Rust (6,55, 70,5), 7. Nim (6,57, 69,7), 8. D (7,34, 72,6), 9. Ada (7,94, 71,7), 10. Chapel (8,74, 66,1), 11. Fortran (10,21, 66,1), 12. Julia (11,20, 64,3), 13. Mojo (12,20, 62,8), 14. C# (14,03, 56,0).

**S-B4** : 1. C (1,90, 80,0), 2. C++ (3,53, 76,6), 3. Odin (3,80, 72,6), 4. Zig (4,69, 72,7), 5. C3 (6,47, 70,3), 6. Rust (6,55, 70,5), 7. Nim (6,56, 69,7), 8. D (7,33, 72,6), 9. Ada (7,93, 71,7), 10. Chapel (8,71, 66,1), 11. Fortran (10,17, 66,1), 12. Julia (11,16, 64,3), 13. Mojo (12,38, 62,1), 14. C# (14,02, 56,0).

**S-K4** : 1. C++ (2,40, 79,4), 2. C (2,47, 79,2), 3. Zig (2,74, 76,0), 4. Odin (4,89, 71,8), 5. Ada (6,87, 73,5), 6. C3 (7,04, 70,1), 7. Nim (7,18, 69,4), 8. Rust (7,22, 70,1), 9. D (8,15, 72,0), 10. Chapel (9,51, 65,6), 11. Fortran (9,88, 67,3), 12. Mojo (10,90, 67,3), 13. Julia (12,02, 62,9), 14. C# (13,80, 60,1).

**S-K4-B4** : 1. C++ (2,40, 79,4), 2. C (2,47, 79,2), 3. Zig (2,74, 76,0), 4. Odin (4,88, 71,8), 5. Ada (6,85, 73,5), 6. C3 (7,02, 70,1), 7. Nim (7,15, 69,4), 8. Rust (7,19, 70,1), 9. D (8,12, 72,0), 10. Chapel (9,46, 65,6), 11. Fortran (9,82, 67,3), 12. Mojo (11,21, 66,6), 13. Julia (11,99, 62,9), 14. C# (13,79, 60,1).

