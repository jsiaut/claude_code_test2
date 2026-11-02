# Remarque sur Go : rapports appariés et scénarios

Plan : `docs/GO.md`. Mesures : `results/raw_go/` (machine 18, 7 processus par cellule). Code :
`analysis/go_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal 0.0e+00).

## Rapports appariés (même hôte)

| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|
| go_fix / go_ref | k5:tuned | 22,57 | 8,66 | 0,384 | 0,318–0,482 |
| go_fix / go_ref | k1:soa:energy | 2,56 | 2,77 | 1,081 | 1,029–1,141 |
| go_fix / go_ref | k6:tuned:q6 | 17,15 | 17,67 | 1,031 | 0,955–1,123 |
| go_fix / go_ref | k6:mt:q6 | 4,92 | 4,51 | 0,917 | 0,812–1,021 |
| go_noexp / go_ref | k1:aos:energy | 1463,72 | 34,21 | 0,023 | 0,022–0,025 |
| go_noexp / go_ref | k1:natural:energy | 2241,29 | 38,15 | 0,017 | 0,016–0,018 |
| go_noexp / go_ref | k1:natural_shuffled:energy | 2298,00 | 36,99 | 0,016 | 0,015–0,017 |
| go_noexp / go_ref | k2:tuned:16384 | 7,94 | 7,64 | 0,961 | 0,904–1,002 |
| go_noexp / go_ref | k2:tuned:16777216 | 582,40 | 574,64 | 0,987 | 0,945–1,029 |
| go_noexp / go_ref | k2:tuned:2097152 | 122,16 | 119,39 | 0,977 | 0,828–1,153 |
| go_noexp / go_ref | k2:tuned:262144 | 25,75 | 25,75 | 1,000 | 0,958–1,040 |
| go_noexp / go_ref | k2:tuned:268435456 | 743,17 | 719,63 | 0,968 | 0,914–1,024 |
| go_noexp / go_ref | k2:tuned:33554432 | 609,75 | 615,92 | 1,010 | 0,955–1,083 |
| go_noexp / go_ref | k2:tuned:524288 | 28,71 | 28,43 | 0,990 | 0,947–1,035 |
| go_noexp / go_ref | k2:tuned:65536 | 23,95 | 24,55 | 1,025 | 1,001–1,050 |
| go_noexp / go_ref | k2:tuned:67108864 | 638,99 | 635,40 | 0,994 | 0,946–1,050 |
| go_noexp / go_ref | k2:tuned:8388608 | 202,50 | 196,15 | 0,969 | 0,608–1,584 |
| go_noexp / go_ref | k3:rmw_packed | 2867,58 | 2880,01 | 1,004 | 0,983–1,026 |
| go_noexp / go_ref | k3:rmw_padded | 304,96 | 289,19 | 0,948 | 0,847–1,036 |
| go_noexp / go_ref | k3:sw_packed | 4117,44 | 4187,60 | 1,017 | 0,987–1,048 |
| go_noexp / go_ref | k3:sw_padded | 441,83 | 434,92 | 0,984 | 0,953–1,014 |
| go_noexp / go_ref | k4:branchless_unsorted | 15,27 | 15,44 | 1,011 | 0,835–1,266 |
| go_noexp / go_ref | k4:natural_sorted | 14,05 | 13,54 | 0,963 | 0,893–1,051 |
| go_noexp / go_ref | k4:natural_unsorted | 13,45 | 13,38 | 0,994 | 0,907–1,085 |
| go_noexp / go_ref | k5:natural | 99,73 | 102,06 | 1,023 | 0,980–1,077 |
| go_noexp / go_ref | k6:mt:q1 | 25,86 | 27,44 | 1,061 | 0,968–1,183 |
| go_noexp / go_ref | k6:natural:q1 | 91,47 | 89,59 | 0,979 | 0,872–1,096 |
| go_noexp / go_ref | k6:natural:q6 | 151,81 | 148,81 | 0,980 | 0,906–1,066 |
| go_noexp / go_ref | k6:tuned:q1 | 68,17 | 75,85 | 1,113 | 0,901–1,402 |
| go_noexp / go_ref | k7:natural | 2132,13 | 1851,35 | 0,868 | 0,657–1,082 |
| go_noexp / go_ref | k7:tuned | 238,15 | 248,87 | 1,045 | 0,985–1,108 |
| go_noexp / go_ref | k8:natural | 1124,95 | 1090,72 | 0,970 | 0,930–1,011 |
| go_noexp / go_ref | k8:tuned | 263,18 | 277,02 | 1,053 | 0,981–1,131 |
| go_noexp / go_ref | k9:mt | 8,64 | 7,90 | 0,914 | 0,816–1,013 |
| go_noexp / go_ref | k9:natural | 45,52 | 45,04 | 0,989 | 0,812–1,196 |
| go_noexp / go_ref | k9:tuned | 19,31 | 20,00 | 1,036 | 0,901–1,179 |
| go_nopre / go_ref (information) | k7:natural | 2132,13 | 1963,74 | 0,921 | 0,680–1,157 |
| go_nopre / go_ref (information) | k1:natural:energy | 2241,29 | 37,08 | 0,017 | 0,016–0,017 |
| go_nopre / go_ref (information) | k8:natural | 1124,95 | 1114,85 | 0,991 | 0,952–1,039 |
| go_nopre / go_ref (information) | k5:natural | 99,73 | 98,01 | 0,983 | 0,958–1,006 |
| go_nopre / go_ref (information) | k9:tuned | 19,31 | 26,64 | 1,380 | 1,138–1,647 |
| go_nopre / go_ref (information) | k9:natural | 45,52 | 45,21 | 0,993 | 0,817–1,207 |
| go_exp tuned_r / go_exp tuned | k5:tuned | 10,60 | 7,98 | 0,753 | 0,616–0,929 |
| go_exp tuned_vec / go_noexp tuned | k9:tuned | 20,00 | 15,52 | 0,776 | 0,674–0,879 |
| go_exp mt_vec / go_noexp mt | k9:mt | 7,90 | 5,77 | 0,730 | 0,657–0,817 |
| go_exp tuned_1p / go_noexp tuned | k6:tuned:q1 | 75,85 | 103,21 | 1,361 | 1,088–1,644 |
| go_exp mt_1p / go_noexp mt | k6:mt:q1 | 27,44 | 25,79 | 0,940 | 0,898–0,988 |
| go_noexp tuned_it / go_noexp tuned | k8:tuned | 277,02 | 171,98 | 0,621 | 0,556–0,691 |

## Report sur les données publiées (transfert ou pont par le C de clang)

| Rapport | Clé | Go publié | Base (G-E) | Transfert | Pont | Écart | Retenu | Facteur appliqué |
|---|---|---|---|---|---|---|---|---|
| correction k5:tuned | k5:tuned | 18,86 ms | 1,000 | 7,24 ms | 7,88 ms | -8,2 % | transfert | 0,384 |
| correction k1:soa:energy | k1:soa:energy | 7,55 ms | 1,000 | 8,17 ms | 7,76 ms | 5,2 % | transfert | 1,000 |
| correction k6:tuned:q6 | k6:tuned:q6 | 20,07 ms | 1,000 | 20,69 ms | 21,25 ms | -2,6 % | transfert | 1,000 |
| correction k6:mt:q6 | k6:mt:q6 | 7,77 ms | 1,000 | 7,13 ms | 7,96 ms | -10,5 % | transfert | 0,917 |
| artefact k5:natural | k5:natural | 84,86 ms | 1,000 | 86,85 ms | 83,68 ms | 3,8 % | transfert | 1,023 |
| artefact k9:natural | k9:natural | 42,90 ms | 1,000 | 42,45 ms | 42,16 ms | 0,7 % | transfert | 0,989 |
| artefact k9:tuned | k9:tuned | 26,68 ms | 1,000 | 27,64 ms | 21,88 ms | 26,3 % | pont | 0,820 |
| artefact k9:mt | k9:mt | 8,32 ms | 1,000 | 7,61 ms | 7,80 ms | -2,5 % | transfert | 0,914 |
| k5_tuned_r | k5:tuned | 18,86 ms | 0,384 | 5,45 ms | 7,27 ms | -24,9 % | transfert | 0,289 |
| k9_tuned_vec | k9:tuned | 26,68 ms | 0,820 | 16,98 ms | 16,98 ms | 0,0 % | transfert | 0,636 |
| k9_mt_vec | k9:mt | 8,32 ms | 0,914 | 5,55 ms | 5,69 ms | -2,5 % | transfert | 0,667 |
| q1_tuned_1p | k6:tuned:q1 | 86,35 ms | 1,000 | 117,49 ms | 135,52 ms | -13,3 % | transfert | 1,000 |
| q1_mt_1p | k6:mt:q1 | 37,95 ms | 1,000 | 35,67 ms | 45,08 ms | -20,9 % | transfert | 0,940 |
| k8_tuned_it | k8:tuned | 410,36 ms | 1,000 | 254,77 ms | 154,93 ms | 64,4 % | pont | 0,378 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Go | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 43,0 | 48,7 | 38,7 | 42,1 | 15,62 | 16 | 14–16 | devant Java 30 %; derrière Haskell 99 % |
| G-K5 | 45,0 | 48,7 | 43,7 | 42,1 | 15,47 | 16 | 14–16 | devant Java 42 %; derrière Haskell 100 % |
| G-K5-T | 45,0 | 48,7 | 43,7 | 42,1 | 15,47 | 16 | 14–16 | devant Java 42 %; derrière Haskell 100 % |
| G-pre | 43,3 | 48,7 | 39,4 | 42,1 | 15,61 | 16 | 14–16 | devant Java 31 %; derrière Haskell 99 % |
| G-pre-T | 43,1 | 48,7 | 38,8 | 42,1 | 15,62 | 16 | 14–16 | devant Java 31 %; derrière Haskell 99 % |
| G-E | 45,3 | 48,7 | 44,5 | 42,1 | 15,45 | 16 | 14–16 | devant Java 43 %; derrière Haskell 100 % |
| G-E-T | 45,1 | 48,7 | 43,9 | 42,1 | 15,47 | 16 | 14–16 | devant Java 42 %; derrière Haskell 100 % |
| S-K5r | 46,0 | 48,7 | 46,1 | 42,1 | 15,39 | 16 | 14–16 | devant Java 48 %; derrière Haskell 100 % |
| S-K9v | 46,0 | 48,7 | 46,1 | 42,1 | 15,41 | 16 | 14–16 | devant Java 47 %; derrière Haskell 100 % |
| S-Q1 | 45,4 | 48,7 | 44,6 | 42,1 | 15,45 | 16 | 14–16 | devant Java 44 %; derrière Haskell 100 % |
| S-K8 | 47,7 | 48,7 | 50,3 | 42,1 | 15,17 | 15 | 14–16 | devant C# 20 %; derrière Java 62 % |
| S-mesures | 49,2 | 48,7 | 54,1 | 42,1 | 15,01 | 15 | 14–16 | devant C# 26 %; derrière Java 71 % |
| S-mesures-T | 47,6 | 48,7 | 50,1 | 42,1 | 15,21 | 15 | 14–16 | devant C# 18 %; derrière Java 60 % |

**Avant** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,18, 62,3), 14. C# (14,09, 54,9), 15. Java (15,18, 47,2), 16. Go (15,62, 43,0), 17. Haskell (17,00, 34,5).

**G-K5** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,11, 54,9), 15. Java (15,30, 47,2), 16. Go (15,47, 45,0), 17. Haskell (17,01, 34,5).

**G-K5-T** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,11, 54,9), 15. Java (15,30, 47,2), 16. Go (15,47, 45,0), 17. Haskell (17,01, 34,5).

**G-pre** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,18, 62,3), 14. C# (14,09, 54,9), 15. Java (15,19, 47,2), 16. Go (15,61, 43,3), 17. Haskell (17,00, 34,5).

**G-pre-T** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,18, 62,3), 14. C# (14,09, 54,9), 15. Java (15,18, 47,2), 16. Go (15,62, 43,1), 17. Haskell (17,00, 34,5).

**G-E** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,12, 54,9), 15. Java (15,31, 47,2), 16. Go (15,45, 45,3), 17. Haskell (17,01, 34,5).

**G-E-T** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,11, 54,9), 15. Java (15,30, 47,2), 16. Go (15,47, 45,1), 17. Haskell (17,01, 34,5).

**S-K5r** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,13, 54,9), 15. Java (15,36, 47,2), 16. Go (15,39, 46,0), 17. Haskell (17,01, 34,5).

**S-K9v** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,13, 54,9), 15. Java (15,35, 47,2), 16. Go (15,41, 46,0), 17. Haskell (17,01, 34,5).

**S-Q1** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,12, 54,9), 15. Java (15,32, 47,2), 16. Go (15,45, 45,4), 17. Haskell (17,01, 34,5).

**S-K8** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,21, 54,9), 15. Go (15,17, 47,7), 16. Java (15,50, 47,2), 17. Haskell (17,01, 34,5).

**S-mesures** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,27, 54,9), 15. Go (15,01, 49,2), 16. Java (15,59, 47,2), 17. Haskell (17,01, 34,5).

**S-mesures-T** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,19, 54,9), 15. Go (15,21, 47,6), 16. Java (15,48, 47,2), 17. Haskell (17,01, 34,5).

## Rapports reportés sur la réplication (machine 3)

k1:aos:energy 0,023, k1:natural_shuffled:energy 0,016, k1:natural:energy 0,017, k1:soa:energy 1,000, k2:tuned:16384 0,961, k2:tuned:16777216 0,987, k2:tuned:2097152 0,977, k2:tuned:262144 1,000, k2:tuned:268435456 0,968, k2:tuned:33554432 1,010, k2:tuned:524288 0,990, k2:tuned:65536 1,025, k2:tuned:67108864 0,994, k2:tuned:8388608 0,969, k3:rmw_packed 1,004, k3:rmw_padded 0,948, k3:sw_packed 1,017, k3:sw_padded 0,984, k4:branchless_unsorted 1,011, k4:natural_sorted 0,963, k4:natural_unsorted 0,994, k5:natural 1,023, k5:tuned 0,384, k6:mt:q1 1,061, k6:mt:q6 0,917, k6:natural:q1 0,979, k6:natural:q6 0,980, k6:tuned:q1 1,113, k6:tuned:q6 1,000, k7:natural 0,868, k7:tuned 1,045, k8:natural 0,970, k8:tuned 1,053, k9:mt 0,914, k9:natural 0,989, k9:tuned 1,036.
