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
| Avant | 59,5 | 62,7 | 67,0 | 43,2 | 12,70 | 13 | 11–14 | devant Julia 25 %; derrière C# 88 % |
| M-E | 62,3 | 70,5 | 67,0 | 43,2 | 12,18 | 13 | 10–13 | devant Julia 40 %; derrière C# 96 % |
| S-B4 | 61,6 | 68,5 | 67,0 | 43,2 | 12,34 | 13 | 10–13 | devant Julia 35 %; derrière C# 95 % |
| S-K4 | 66,7 | 70,5 | 78,1 | 43,2 | 10,98 | 12 | 8–13 | devant Fortran 42 %; derrière Julia 73 % |
| S-K4-B4 | 66,0 | 68,5 | 78,1 | 43,2 | 11,26 | 12 | 8–13 | devant Fortran 36 %; derrière Julia 69 % |

**Avant** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,81, 69,9), 7. Nim (6,89, 69,3), 8. D (7,21, 72,6), 9. Ada (8,05, 71,0), 10. Chapel (8,77, 65,7), 11. Fortran (10,17, 65,4), 12. Julia (11,42, 62,3), 13. Mojo (12,70, 59,5), 14. C# (13,98, 54,9).

**M-E** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,18, 62,3), 14. C# (14,06, 54,9).

**S-B4** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,90, 69,3), 8. D (7,22, 72,6), 9. Ada (8,06, 71,0), 10. Chapel (8,82, 65,7), 11. Fortran (10,25, 65,4), 12. Julia (11,52, 62,3), 13. Mojo (12,34, 61,6), 14. C# (14,05, 54,9).

**S-K4** : 1. C++ (2,46, 80,0), 2. C (2,88, 79,2), 3. Zig (2,90, 75,5), 4. Odin (4,17, 73,3), 5. C3 (5,75, 71,4), 6. Ada (7,06, 72,8), 7. Rust (7,50, 69,4), 8. Nim (7,50, 69,0), 9. D (8,03, 72,0), 10. Chapel (9,64, 65,2), 11. Fortran (10,12, 66,5), 12. Mojo (10,98, 66,7), 13. Julia (12,30, 60,9), 14. C# (13,81, 58,6).

**S-K4-B4** : 1. C++ (2,46, 80,0), 2. C (2,88, 79,2), 3. Zig (2,90, 75,5), 4. Odin (4,16, 73,3), 5. C3 (5,74, 71,4), 6. Ada (7,04, 72,8), 7. Nim (7,47, 69,0), 8. Rust (7,47, 69,4), 9. D (8,01, 72,0), 10. Chapel (9,58, 65,2), 11. Fortran (10,07, 66,5), 12. Mojo (11,26, 66,0), 13. Julia (12,26, 60,9), 14. C# (13,80, 58,6).

