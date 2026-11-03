# Remarque sur Haskell : rapports appariés et scénarios

Plan : `docs/HASKELL.md`. Mesures : `results/raw_haskell/` (machine 19, 7 processus par cellule, 4 pour K7
naturel). Code : `analysis/haskell_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal 0.0e+00).

## Rapports appariés (même hôte)

| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|
| fix / ref | k1:aos:energy | 28,01 | 27,32 | 0,976 | 0,928–1,023 |
| fix / ref | k1:natural:energy | 88,13 | 90,79 | 1,030 | 0,968–1,089 |
| fix / ref | k1:natural_shuffled:energy | 155,55 | 154,09 | 0,991 | 0,922–1,047 |
| fix / ref | k1:soa:energy | 4,43 | 4,35 | 0,981 | 0,778–1,239 |
| fix / ref | k2:tuned:16384 | 7,95 | 8,36 | 1,051 | 1,014–1,117 |
| fix / ref | k2:tuned:16777216 | 603,03 | 586,98 | 0,973 | 0,847–1,128 |
| fix / ref | k2:tuned:2097152 | 179,13 | 180,45 | 1,007 | 0,930–1,103 |
| fix / ref | k2:tuned:262144 | 24,00 | 23,78 | 0,991 | 0,892–1,065 |
| fix / ref | k2:tuned:268435456 | 965,29 | 949,63 | 0,984 | 0,943–1,026 |
| fix / ref | k2:tuned:33554432 | 732,97 | 736,15 | 1,004 | 0,973–1,036 |
| fix / ref | k2:tuned:524288 | 26,07 | 26,50 | 1,017 | 0,961–1,075 |
| fix / ref | k2:tuned:65536 | 22,79 | 22,58 | 0,991 | 0,974–1,007 |
| fix / ref | k2:tuned:67108864 | 782,48 | 767,48 | 0,981 | 0,946–1,014 |
| fix / ref | k2:tuned:8388608 | 283,12 | 287,77 | 1,016 | 0,952–1,095 |
| fix / ref | k3:rmw_packed | 4118,11 | 4601,19 | 1,117 | 1,056–1,173 |
| fix / ref | k3:rmw_padded | 342,89 | 234,67 | 0,684 | 0,624–0,776 |
| fix / ref | k3:sw_packed | 7374,00 | 6092,05 | 0,826 | 0,784–0,874 |
| fix / ref | k3:sw_padded | 358,79 | 419,84 | 1,170 | 1,003–1,429 |
| fix / ref | k4:branchless_unsorted | 11,31 | 11,01 | 0,974 | 0,869–1,097 |
| fix / ref | k4:natural_sorted | 10,28 | 11,58 | 1,126 | 1,028–1,229 |
| fix / ref | k4:natural_unsorted | 73,38 | 11,24 | 0,153 | 0,148–0,159 |
| fix / ref | k5:natural | 346,50 | 187,47 | 0,541 | 0,515–0,574 |
| fix / ref | k5:tuned | 6,17 | 4,60 | 0,745 | 0,674–0,823 |
| fix / ref | k6:mt:q1 | 19,04 | 17,97 | 0,944 | 0,836–1,077 |
| fix / ref | k6:mt:q6 | 14,99 | 12,59 | 0,840 | 0,737–0,943 |
| fix / ref | k6:natural:q1 | 60,01 | 60,44 | 1,007 | 0,955–1,047 |
| fix / ref | k6:natural:q6 | 48,63 | 51,14 | 1,052 | 1,019–1,091 |
| fix / ref | k6:tuned:q1 | 58,74 | 56,43 | 0,961 | 0,920–1,006 |
| fix / ref | k6:tuned:q6 | 36,54 | 31,20 | 0,854 | 0,813–0,897 |
| fix / ref | k7:natural | 53551,14 | 54187,75 | 1,012 | 0,974–1,048 |
| fix / ref | k7:tuned | 251,39 | 195,58 | 0,778 | 0,729–0,834 |
| fix / ref | k8:natural | 1645,40 | 1690,14 | 1,027 | 1,002–1,055 |
| fix / ref | k8:tuned | 724,33 | 213,65 | 0,295 | 0,286–0,304 |
| fix / ref | k9:mt | 13,47 | 13,48 | 1,000 | 0,934–1,072 |
| fix / ref | k9:natural | 207,80 | 125,52 | 0,604 | 0,569–0,651 |
| fix / ref | k9:tuned | 25,86 | 25,18 | 0,974 | 0,890–1,070 |
| rel / ref (options seules) | k1:soa:energy | 4,43 | 4,74 | 1,071 | 0,852–1,352 |
| rel / ref (options seules) | k5:tuned | 6,17 | 5,97 | 0,967 | 0,851–1,126 |
| rel / ref (options seules) | k8:natural | 1645,40 | 1638,55 | 0,996 | 0,971–1,020 |
| rel / ref (options seules) | k8:tuned | 724,33 | 718,89 | 0,992 | 0,953–1,034 |
| n1 / fix (sensibilité) | k1:natural:energy | 90,79 | 86,93 | 0,957 | 0,892–1,028 |
| n1 / fix (sensibilité) | k1:natural_shuffled:energy | 154,09 | 153,27 | 0,995 | 0,949–1,043 |
| n1 / fix (sensibilité) | k4:natural_unsorted | 11,24 | 11,49 | 1,022 | 0,953–1,099 |
| n1 / fix (sensibilité) | k5:natural | 187,47 | 196,03 | 1,046 | 0,959–1,158 |
| n1 / fix (sensibilité) | k8:natural | 1690,14 | 1170,35 | 0,692 | 0,675–0,707 |
| n1 / fix (sensibilité) | k9:natural | 125,52 | 114,89 | 0,915 | 0,848–0,976 |

## Latences de K8 naturel (médianes de toutes les répétitions, µs)

| Rapport | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| fix / ref : ancien | 57 | 253 | 505 | 1729 | 6002 |
| fix / ref : nouveau | 61 | 256 | 484 | 1383 | 6684 |
| fix / ref : rapport [IC 95 %] | 1,061 [1,05–1,11] | 1,010 [0,95–1,07] | 0,960 [0,89–1,05] | 0,800 [0,60–1,08] | 1,114 [0,70–1,38] |
| rel / ref : ancien | 57 | 253 | 505 | 1729 | 6002 |
| rel / ref : nouveau | 59 | 251 | 485 | 1427 | 5930 |
| rel / ref : rapport [IC 95 %] | 1,024 [1,01–1,03] | 0,992 [0,93–1,01] | 0,961 [0,88–0,99] | 0,825 [0,68–0,95] | 0,988 [0,71–1,24] |
| n1 / fix : ancien | 61 | 256 | 484 | 1383 | 6684 |
| n1 / fix : nouveau | 60 | 97 | 147 | 404 | 3550 |
| n1 / fix : rapport [IC 95 %] | 0,981 [0,93–0,99] | 0,378 [0,36–0,38] | 0,303 [0,28–0,31] | 0,292 [0,19–0,41] | 0,531 [0,30–1,16] |

## Pont par le C de clang (information : scénario H-E-P ; le classement publié reporte par transfert)

| Rapport | Clé | Haskell publié | Base | Transfert | Pont | Écart | Retenu | Facteur appliqué |
|---|---|---|---|---|---|---|---|---|
| pont k1:aos:energy | k1:aos:energy | 39,22 ms | 1,000 | 38,27 ms | 31,25 ms | 22,5 % | transfert | 0,976 |
| pont k1:natural:energy | k1:natural:energy | 71,06 ms | 1,000 | 73,21 ms | 97,14 ms | -24,6 % | transfert | 1,030 |
| pont k1:natural_shuffled:energy | k1:natural_shuffled:energy | 65,93 ms | 1,000 | 65,31 ms | 216,89 ms | -69,9 % | pont | 1,000 |
| pont k1:soa:energy | k1:soa:energy | 9,38 ms | 1,000 | 9,21 ms | 11,01 ms | -16,3 % | transfert | 0,981 |
| pont k2:tuned:16384 | k2:tuned:16384 | 7,91 ms | 1,000 | 8,31 ms | 8,38 ms | -0,8 % | transfert | 1,051 |
| pont k2:tuned:16777216 | k2:tuned:16777216 | 659,62 ms | 1,000 | 642,06 ms | 795,11 ms | -19,2 % | transfert | 0,973 |
| pont k2:tuned:2097152 | k2:tuned:2097152 | 114,99 ms | 1,000 | 115,83 ms | 123,51 ms | -6,2 % | transfert | 1,007 |
| pont k2:tuned:262144 | k2:tuned:262144 | 20,00 ms | 1,000 | 19,82 ms | 19,62 ms | 1,0 % | transfert | 0,991 |
| pont k2:tuned:268435456 | k2:tuned:268435456 | 1540,10 ms | 1,000 | 1515,11 ms | 1390,87 ms | 8,9 % | transfert | 0,984 |
| pont k2:tuned:33554432 | k2:tuned:33554432 | 821,25 ms | 1,000 | 824,81 ms | 753,16 ms | 9,5 % | transfert | 1,004 |
| pont k2:tuned:524288 | k2:tuned:524288 | 28,85 ms | 1,000 | 29,33 ms | 29,29 ms | 0,1 % | transfert | 1,017 |
| pont k2:tuned:65536 | k2:tuned:65536 | 19,40 ms | 1,000 | 19,22 ms | 19,23 ms | -0,0 % | transfert | 0,991 |
| pont k2:tuned:67108864 | k2:tuned:67108864 | 971,92 ms | 1,000 | 953,30 ms | 974,54 ms | -2,2 % | transfert | 0,981 |
| pont k2:tuned:8388608 | k2:tuned:8388608 | 584,24 ms | 1,000 | 593,84 ms | 646,56 ms | -8,2 % | transfert | 1,016 |
| pont k3:rmw_packed | k3:rmw_packed | 2452,45 ms | 1,000 | 2740,14 ms | 2615,07 ms | 4,8 % | transfert | 1,117 |
| pont k3:rmw_padded | k3:rmw_padded | 281,44 ms | 1,000 | 192,62 ms | 243,85 ms | -21,0 % | transfert | 0,684 |
| pont k3:sw_packed | k3:sw_packed | 4108,94 ms | 1,000 | 3394,62 ms | 76296,71 ms | -95,6 % | pont | 1,000 |
| pont k3:sw_padded | k3:sw_padded | 331,32 ms | 1,000 | 387,70 ms | 2026,98 ms | -80,9 % | pont | 6,118 |
| pont k4:branchless_unsorted | k4:branchless_unsorted | 11,46 ms | 1,000 | 11,16 ms | 17,43 ms | -36,0 % | pont | 1,000 |
| pont k4:natural_sorted | k4:natural_sorted | 8,90 ms | 1,000 | 10,03 ms | 24,38 ms | -58,9 % | pont | 2,737 |
| pont k4:natural_unsorted | k4:natural_unsorted | 73,35 ms | 1,000 | 11,24 ms | 23,07 ms | -51,3 % | pont | 0,315 |
| pont k5:natural | k5:natural | 349,74 ms | 1,000 | 189,22 ms | 176,09 ms | 7,5 % | transfert | 0,541 |
| pont k5:tuned | k5:tuned | 6,35 ms | 1,000 | 4,73 ms | 4,08 ms | 15,9 % | transfert | 0,745 |
| pont k6:mt:q1 | k6:mt:q1 | 31,98 ms | 1,000 | 30,18 ms | 29,89 ms | 1,0 % | transfert | 0,944 |
| pont k6:mt:q6 | k6:mt:q6 | 17,27 ms | 1,000 | 14,51 ms | 18,63 ms | -22,1 % | transfert | 0,840 |
| pont k6:natural:q1 | k6:natural:q1 | 103,08 ms | 1,000 | 103,82 ms | 91,53 ms | 13,4 % | transfert | 1,007 |
| pont k6:natural:q6 | k6:natural:q6 | 75,76 ms | 1,000 | 79,67 ms | 64,00 ms | 24,5 % | transfert | 1,052 |
| pont k6:tuned:q1 | k6:tuned:q1 | 70,20 ms | 1,000 | 67,44 ms | 63,69 ms | 5,9 % | transfert | 0,961 |
| pont k6:tuned:q6 | k6:tuned:q6 | 70,53 ms | 1,000 | 60,24 ms | 36,56 ms | 64,8 % | pont | 0,518 |
| pont k7:natural | k7:natural | 87693,25 ms | 1,000 | 88735,75 ms | 638956,07 ms | -86,1 % | pont | 7,286 |
| pont k7:tuned | k7:tuned | 725,05 ms | 1,000 | 564,09 ms | 449,39 ms | 25,5 % | pont | 0,620 |
| pont k8:natural | k8:natural | 2428,25 ms | 1,000 | 2494,27 ms | 2807,06 ms | -11,1 % | transfert | 1,027 |
| pont k8:tuned | k8:tuned | 1189,30 ms | 1,000 | 350,80 ms | 225,55 ms | 55,5 % | pont | 0,190 |
| pont k9:mt | k9:mt | 12,26 ms | 1,000 | 12,27 ms | 11,17 ms | 9,8 % | transfert | 1,000 |
| pont k9:natural | k9:natural | 270,53 ms | 1,000 | 163,41 ms | 123,48 ms | 32,3 % | pont | 0,456 |
| pont k9:tuned | k9:tuned | 23,58 ms | 1,000 | 22,95 ms | 27,06 ms | -15,2 % | transfert | 0,974 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Haskell | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 34,5 | 34,4 | 34,6 | 34,4 | 17,01 | 17 | 17–17 | devant Go 0 %; derrière OCaml 98 % |
| H-opt | 36,1 | 34,4 | 38,0 | 35,4 | 16,98 | 17 | 17–17 | devant Go 0 %; derrière OCaml 99 % |
| H-code | 39,3 | 34,4 | 46,2 | 35,2 | 16,92 | 17 | 16–17 | devant Go 3 %; derrière OCaml 99 % |
| H-M | 36,4 | 39,9 | 34,6 | 34,4 | 16,98 | 17 | 17–17 | devant Go 0 %; derrière OCaml 99 % |
| H-E | 41,3 | 39,9 | 46,2 | 35,2 | 16,82 | 17 | 16–17 | devant Go 7 %; derrière OCaml 100 % |
| H-E-P | 42,9 | 39,9 | 50,8 | 34,4 | 16,64 | 17 | 15–17 | devant Go 17 %; derrière OCaml 99 % |
| S-N1 | 42,1 | 39,9 | 46,2 | 38,6 | 16,62 | 17 | 15–17 | devant Go 15 %; derrière OCaml 100 % |
| S-cases | 42,8 | 44,4 | 46,2 | 35,2 | 16,66 | 17 | 15–17 | devant Go 15 %; derrière OCaml 100 % |
| S-tout | 43,7 | 44,4 | 46,2 | 38,6 | 16,41 | 17 | 15–17 | devant Go 27 %; derrière OCaml 100 % |

**Avant** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,12, 54,9), 15. Java (15,31, 47,2), 16. Go (15,45, 45,3), 17. Haskell (17,01, 34,5), 18. OCaml (17,98, 24,0).

**H-opt** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 70,0), 7. Nim (6,92, 69,3), 8. D (7,23, 72,7), 9. Ada (8,07, 71,1), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,4), 13. Mojo (12,19, 62,3), 14. C# (14,12, 54,9), 15. Java (15,32, 47,2), 16. Go (15,45, 45,4), 17. Haskell (16,98, 36,1), 18. OCaml (17,99, 24,0).

**H-code** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 70,0), 7. Nim (6,92, 69,3), 8. D (7,23, 72,7), 9. Ada (8,07, 71,1), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,4), 13. Mojo (12,19, 62,3), 14. C# (14,13, 54,9), 15. Java (15,35, 47,2), 16. Go (15,48, 45,4), 17. Haskell (16,92, 39,3), 18. OCaml (18,00, 24,0).

**H-M** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,83, 69,9), 7. Nim (6,91, 69,3), 8. D (7,24, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,3), 14. C# (14,12, 54,9), 15. Java (15,33, 47,2), 16. Go (15,45, 45,3), 17. Haskell (16,98, 36,4), 18. OCaml (17,99, 24,0).

**H-E** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 70,0), 7. Nim (6,92, 69,3), 8. D (7,23, 72,7), 9. Ada (8,07, 71,1), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,4), 13. Mojo (12,19, 62,3), 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,0).

**H-E-P** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,2), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,2), 8. D (7,23, 72,6), 9. Ada (8,07, 71,0), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,3), 13. Mojo (12,19, 62,2), 14. C# (14,14, 54,8), 15. Java (15,46, 47,1), 16. Go (15,63, 45,3), 17. Haskell (16,64, 42,9), 18. OCaml (18,00, 24,0).

**S-N1** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 70,0), 7. Nim (6,92, 69,3), 8. D (7,24, 72,7), 9. Ada (8,07, 71,1), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,4), 13. Mojo (12,19, 62,3), 14. C# (14,16, 54,9), 15. Java (15,49, 47,2), 16. Go (15,60, 45,4), 17. Haskell (16,62, 42,1), 18. OCaml (18,01, 24,0).

**S-cases** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,83, 70,0), 7. Nim (6,92, 69,3), 8. D (7,23, 72,7), 9. Ada (8,06, 71,1), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,4), 13. Mojo (12,19, 62,3), 14. C# (14,13, 54,9), 15. Java (15,47, 47,2), 16. Go (15,60, 45,4), 17. Haskell (16,66, 42,8), 18. OCaml (18,00, 24,0).

**S-tout** : 1. C (2,21, 80,0), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,83, 70,0), 7. Nim (6,92, 69,3), 8. D (7,24, 72,7), 9. Ada (8,06, 71,1), 10. Chapel (8,85, 65,7), 11. Fortran (10,29, 65,4), 12. Julia (11,57, 62,4), 13. Mojo (12,19, 62,3), 14. C# (14,16, 54,9), 15. Java (15,57, 47,2), 16. Go (15,72, 45,4), 17. Haskell (16,41, 43,7), 18. OCaml (18,01, 24,0).

## Rapports reportés sur la réplication (machine 3)

k1:aos:energy 0,976, k1:natural_shuffled:energy 0,991, k1:natural:energy 1,030, k1:soa:energy 0,981, k2:tuned:16384 1,051, k2:tuned:16777216 0,973, k2:tuned:2097152 1,007, k2:tuned:262144 0,991, k2:tuned:268435456 0,984, k2:tuned:33554432 1,004, k2:tuned:524288 1,017, k2:tuned:65536 0,991, k2:tuned:67108864 0,981, k2:tuned:8388608 1,016, k3:rmw_packed 1,117, k3:rmw_padded 0,684, k3:sw_packed 0,826, k3:sw_padded 1,170, k4:branchless_unsorted 0,974, k4:natural_sorted 1,126, k4:natural_unsorted 0,153, k5:natural 0,541, k5:tuned 0,745, k6:mt:q1 0,944, k6:mt:q6 0,840, k6:natural:q1 1,007, k6:natural:q6 1,052, k6:tuned:q1 0,961, k6:tuned:q6 0,854, k7:natural 1,012, k7:tuned 0,778, k8:natural 1,027, k8:tuned 0,295, k9:mt 1,000, k9:natural 0,604, k9:tuned 0,974.

Latences de K8 naturel : p50 1,061, p90 1,010, p99 0,960, p99,9 0,800, max 1,114.
