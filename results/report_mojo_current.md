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
| Avant | 59,6 | 62,7 | 67,0 | 43,3 | 12,71 | 13 | 11–14 | devant Julia 25 %; derrière C# 88 % |
| M-E | 62,3 | 70,5 | 67,0 | 43,3 | 12,19 | 13 | 10–13 | devant Julia 39 %; derrière C# 96 % |
| S-B4 | 61,6 | 68,5 | 67,0 | 43,3 | 12,35 | 13 | 10–13 | devant Julia 35 %; derrière C# 95 % |
| S-K4 | 66,7 | 70,5 | 78,1 | 43,3 | 10,98 | 12 | 8–13 | devant Fortran 42 %; derrière Julia 73 % |
| S-K4-B4 | 66,0 | 68,5 | 78,1 | 43,3 | 11,26 | 12 | 8–13 | devant Fortran 36 %; derrière Julia 69 % |

**Avant** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,13, 71,6), 6. Rust (6,81, 70,0), 7. Nim (6,90, 69,3), 8. D (7,22, 72,7), 9. Ada (8,05, 71,1), 10. Chapel (8,76, 65,7), 11. Fortran (10,16, 65,4), 12. Julia (11,43, 62,4), 13. Mojo (12,71, 59,6), 14. C# (14,05, 54,9).

**M-E** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 70,0), 7. Nim (6,92, 69,3), 8. D (7,24, 72,7), 9. Ada (8,07, 71,1), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,4), 13. Mojo (12,19, 62,3), 14. C# (14,13, 54,9).

**S-B4** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 70,0), 7. Nim (6,91, 69,3), 8. D (7,23, 72,7), 9. Ada (8,06, 71,1), 10. Chapel (8,82, 65,7), 11. Fortran (10,25, 65,4), 12. Julia (11,53, 62,4), 13. Mojo (12,35, 61,6), 14. C# (14,12, 54,9).

**S-K4** : 1. C++ (2,46, 80,1), 2. C (2,88, 79,2), 3. Zig (2,91, 75,6), 4. Odin (4,16, 73,3), 5. C3 (5,75, 71,5), 6. Ada (7,05, 72,8), 7. Rust (7,50, 69,5), 8. Nim (7,51, 69,0), 9. D (8,03, 72,0), 10. Chapel (9,64, 65,3), 11. Fortran (10,12, 66,5), 12. Mojo (10,98, 66,7), 13. Julia (12,30, 60,9), 14. C# (13,85, 58,6).

**S-K4-B4** : 1. C++ (2,46, 80,1), 2. C (2,88, 79,2), 3. Zig (2,91, 75,6), 4. Odin (4,16, 73,3), 5. C3 (5,74, 71,5), 6. Ada (7,03, 72,8), 7. Rust (7,48, 69,5), 8. Nim (7,48, 69,0), 9. D (8,01, 72,0), 10. Chapel (9,58, 65,3), 11. Fortran (10,06, 66,5), 12. Mojo (11,26, 66,0), 13. Julia (12,27, 60,9), 14. C# (13,83, 58,6).

