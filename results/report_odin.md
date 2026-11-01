# Remarque sur Odin : rapports appariés et scénarios

Plan : `docs/ODIN.md`. Mesures : `results/raw_odin/` (machine 14, 7 processus par cellule). Code :
`analysis/odin_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit le publié d'avant la remarque (écart maximal 0.0e+00).

## Rapports appariés (même hôte)

| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|
| odin_fix / odin_ref (corrigée) | k1:natural:energy | 38,14 | 37,22 | 0,976 | 0,914–1,041 |
| odin_fix / odin_ref (corrigée) | k1:natural_shuffled:energy | 36,52 | 38,01 | 1,041 | 0,962–1,125 |
| odin_fix / odin_ref (corrigée) | k1:aos:energy | 31,69 | 32,01 | 1,010 | 0,945–1,095 |
| odin_fix / odin_ref (corrigée) | k1:soa:energy | 3,49 | 3,14 | 0,900 | 0,667–1,230 |
| odin_fix / odin_ref (corrigée) | k2:tuned:16384 | 8,92 | 8,41 | 0,943 | 0,667–1,225 |
| odin_fix / odin_ref (corrigée) | k2:tuned:262144 | 24,87 | 25,10 | 1,009 | 0,974–1,044 |
| odin_fix / odin_ref (corrigée) | k2:tuned:8388608 | 213,56 | 192,50 | 0,901 | 0,632–1,319 |
| odin_fix / odin_ref (témoin) | k3:sw_padded | 92,32 | 88,97 | 0,964 | 0,921–1,014 |
| odin_fix / odin_ref (témoin) | k3:rmw_padded | 280,71 | 294,67 | 1,050 | 0,947–1,158 |
| odin_fix / odin_ref (corrigée) | k4:natural_unsorted | 2,01 | 1,71 | 0,853 | 0,722–1,022 |
| odin_fix / odin_ref (corrigée) | k4:branchless_unsorted | 2,60 | 1,99 | 0,764 | 0,577–0,983 |
| odin_fix / odin_ref (corrigée) | k5:natural | 98,83 | 101,59 | 1,028 | 0,964–1,095 |
| odin_fix / odin_ref (corrigée) | k5:tuned | 4,29 | 4,31 | 1,005 | 0,847–1,208 |
| odin_fix / odin_ref (témoin) | k6:natural:q6 | 70,03 | 68,91 | 0,984 | 0,932–1,041 |
| odin_fix / odin_ref (corrigée) | k6:tuned:q6 | 14,63 | 14,72 | 1,006 | 0,929–1,081 |
| odin_fix / odin_ref (corrigée) | k6:mt:q6 | 4,32 | 4,48 | 1,037 | 0,865–1,226 |
| odin_fix / odin_ref (témoin) | k6:natural:q1 | 85,61 | 81,29 | 0,950 | 0,786–1,144 |
| odin_fix / odin_ref (témoin) | k6:tuned:q1 | 41,68 | 41,96 | 1,007 | 0,921–1,083 |
| odin_fix / odin_ref (témoin) | k6:mt:q1 | 13,43 | 14,32 | 1,066 | 0,911–1,254 |
| odin_fix / odin_ref (témoin) | k7:natural | 1039,40 | 1012,43 | 0,974 | 0,880–1,078 |
| odin_fix / odin_ref (témoin) | k7:tuned | 211,38 | 213,01 | 1,008 | 0,966–1,048 |
| odin_fix / odin_ref (témoin) | k8:natural | 1537,09 | 1560,02 | 1,015 | 0,919–1,118 |
| odin_fix / odin_ref (témoin) | k8:tuned | 303,31 | 297,01 | 0,979 | 0,955–1,007 |
| odin_fix / odin_ref (témoin) | k8:tuned_alloc | 1056,37 | 1018,80 | 0,964 | 0,906–1,029 |
| odin_fix / odin_ref (corrigée) | k9:natural | 21,42 | 24,25 | 1,132 | 0,939–1,368 |
| odin_fix / odin_ref (témoin) | k9:tuned | 22,42 | 22,50 | 1,003 | 0,808–1,214 |
| odin_fix / odin_ref (témoin) | k9:mt | 11,00 | 10,52 | 0,956 | 0,807–1,128 |
| odin_q1 / odin_fix | k6:tuned:q1 | 41,96 | 23,10 | 0,551 | 0,513–0,590 |
| odin_q1 / odin_fix | k6:mt:q1 | 14,32 | 7,66 | 0,535 | 0,462–0,616 |
| odin_agg / odin_fix | k1:natural:energy | 37,22 | 37,02 | 0,995 | 0,922–1,073 |
| odin_agg / odin_fix | k1:natural_shuffled:energy | 38,01 | 35,88 | 0,944 | 0,909–0,984 |
| odin_agg / odin_fix | k1:aos:energy | 32,01 | 32,21 | 1,006 | 0,939–1,059 |
| odin_agg / odin_fix | k1:soa:energy | 3,14 | 2,88 | 0,918 | 0,716–1,070 |
| odin_agg / odin_fix | k2:tuned:16384 | 8,41 | 7,64 | 0,908 | 0,771–0,998 |
| odin_agg / odin_fix | k2:tuned:262144 | 25,10 | 25,42 | 1,013 | 0,982–1,045 |
| odin_agg / odin_fix | k2:tuned:8388608 | 192,50 | 200,55 | 1,042 | 0,682–1,534 |
| odin_agg / odin_fix | k3:sw_padded | 88,97 | 92,32 | 1,038 | 0,989–1,080 |
| odin_agg / odin_fix | k3:rmw_padded | 294,67 | 296,23 | 1,005 | 0,876–1,177 |
| odin_agg / odin_fix | k4:natural_unsorted | 1,71 | 1,75 | 1,025 | 0,901–1,159 |
| odin_agg / odin_fix | k4:branchless_unsorted | 1,99 | 2,18 | 1,098 | 0,884–1,337 |
| odin_agg / odin_fix | k5:natural | 101,59 | 122,24 | 1,203 | 1,077–1,363 |
| odin_agg / odin_fix | k5:tuned | 4,31 | 4,05 | 0,940 | 0,800–1,118 |
| odin_agg / odin_fix | k6:natural:q6 | 68,91 | 68,27 | 0,991 | 0,922–1,070 |
| odin_agg / odin_fix | k6:tuned:q6 | 14,72 | 14,76 | 1,003 | 0,933–1,075 |
| odin_agg / odin_fix | k6:mt:q6 | 4,48 | 4,31 | 0,962 | 0,832–1,092 |
| odin_agg / odin_fix | k6:natural:q1 | 81,29 | 100,68 | 1,238 | 0,976–1,510 |
| odin_agg / odin_fix | k6:tuned:q1 | 41,96 | 42,65 | 1,016 | 0,942–1,094 |
| odin_agg / odin_fix | k6:mt:q1 | 14,32 | 11,91 | 0,832 | 0,725–0,942 |
| odin_agg / odin_fix | k7:natural | 1012,43 | 1041,66 | 1,029 | 0,955–1,105 |
| odin_agg / odin_fix | k7:tuned | 213,01 | 218,38 | 1,025 | 0,954–1,103 |
| odin_agg / odin_fix | k8:natural | 1560,02 | 1546,36 | 0,991 | 0,909–1,083 |
| odin_agg / odin_fix | k8:tuned | 297,01 | 305,66 | 1,029 | 1,015–1,043 |
| odin_agg / odin_fix | k8:tuned_alloc | 1018,80 | 1021,96 | 1,003 | 0,948–1,059 |
| odin_agg / odin_fix | k9:natural | 24,25 | 20,61 | 0,850 | 0,661–1,112 |
| odin_agg / odin_fix | k9:tuned | 22,50 | 24,39 | 1,084 | 0,840–1,374 |
| odin_agg / odin_fix | k9:mt | 10,52 | 11,11 | 1,057 | 0,904–1,248 |

Témoins (13 clés non corrigées), odin_fix / odin_ref en moyenne géométrique : 0,993.
`-o:aggressive` / `-o:speed`, moyenne géométrique des 27 clés : 1,006.

## Odin et C sur les clés témoins du pont (information)

| Clé | C, hôte (ms) | Odin, hôte (ms) | Odin / C, hôte [IC 95 %] | Odin / C, données principales |
|---|---|---|---|---|
| k1:natural:energy | 37,43 | 38,14 | 1,02 [0,96–1,08] | 1,03 |
| k1:natural_shuffled:energy | 36,73 | 36,52 | 0,99 [0,91–1,08] | 1,07 |
| k1:aos:energy | 29,56 | 31,69 | 1,07 [0,99–1,15] | 1,05 |
| k1:soa:energy | 2,85 | 3,49 | 1,22 [0,98–1,57] | 0,97 |
| k2:tuned:16384 | 7,73 | 8,92 | 1,16 [0,97–1,61] | 0,97 |
| k2:tuned:262144 | 25,59 | 24,87 | 0,97 [0,93–1,01] | 1,12 |
| k2:tuned:8388608 | 284,32 | 213,56 | 0,75 [0,46–1,23] | 0,99 |
| k4:natural_unsorted | 2,16 | 2,01 | 0,93 [0,71–1,21] | 0,75 |
| k4:branchless_unsorted | 1,84 | 2,60 | 1,41 [1,12–1,78] | 1,14 |
| k5:natural | 194,98 | 98,83 | 0,51 [0,48–0,53] | 0,49 |
| k5:tuned | 4,50 | 4,29 | 0,95 [0,77–1,18] | 1,07 |
| k6:tuned:q6 | 18,10 | 14,63 | 0,81 [0,77–0,85] | 1,01 |
| k6:mt:q6 | 6,06 | 4,32 | 0,71 [0,59–0,85] | 0,95 |
| k9:natural | 14,37 | 21,42 | 1,49 [1,32–1,68] | 0,94 |
| k6:tuned:q1 | 26,33 | 41,68 | 1,58 [1,43–1,78] | 1,44 |
| k6:mt:q1 | 8,03 | 13,43 | 1,67 [1,48–1,94] | 1,53 |

## Report sur les données principales (transfert ou pont par le C de la campagne)

Lignes « Fix » : information seulement, la correction du banc n'est pas reportée (écart au plan, `docs/ODIN.md`
4.2) ; la colonne « Règle du plan » donne ce que la règle du pont aurait retenu (scénario « Fix-pont (plan) »).
Lignes S-Q1 : règle du plan (sensibilité).

| Clé | Odin (données principales) | Transfert | Pont | Écart | Règle du plan |
|---|---|---|---|---|---|
| Fix k1:natural:energy | 42,76 ms | 41,73 ms | 41,15 ms | 1,4 % | transfert (0,976) |
| Fix k1:natural_shuffled:energy | 42,08 ms | 43,79 ms | 40,71 ms | 7,6 % | transfert (1,041) |
| Fix k1:aos:energy | 40,29 ms | 40,69 ms | 41,63 ms | -2,2 % | transfert seul (fixé d'avance) (1,010) |
| Fix k1:soa:energy | 7,53 ms | 6,78 ms | 8,53 ms | -20,5 % | transfert (0,900) |
| Fix k2:tuned:16384 | 6,62 ms | 6,24 ms | 7,41 ms | -15,8 % | transfert (0,943) |
| Fix k2:tuned:262144 | 20,45 ms | 20,63 ms | 17,93 ms | 15,1 % | transfert (1,009) |
| Fix k2:tuned:8388608 | 617,85 ms | 556,93 ms | 424,27 ms | 31,3 % | pont (0,687) |
| Fix k4:natural_unsorted | 3,02 ms | 2,58 ms | 3,19 ms | -19,2 % | transfert (0,853) |
| Fix k4:branchless_unsorted | 3,25 ms | 2,48 ms | 3,07 ms | -19,1 % | transfert (0,764) |
| Fix k5:natural | 77,71 ms | 79,88 ms | 82,38 ms | -3,0 % | transfert (1,028) |
| Fix k5:tuned | 4,23 ms | 4,25 ms | 3,77 ms | 12,5 % | transfert (1,005) |
| Fix k6:tuned:q6 | 21,59 ms | 21,72 ms | 17,36 ms | 25,2 % | pont (0,804) |
| Fix k6:mt:q6 | 8,10 ms | 8,39 ms | 6,31 ms | 33,0 % | pont (0,780) |
| Fix k9:natural | 36,27 ms | 41,06 ms | 64,78 ms | -36,6 % | transfert seul (fixé d'avance) (1,132) |
| S-Q1 k6:tuned:q1 | 46,08 ms | 25,37 ms | 28,17 ms | -9,9 % | transfert (0,551) |
| S-Q1 k6:mt:q1 | 20,55 ms | 10,99 ms | 12,82 ms | -14,3 % | transfert (0,535) |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score d'Odin | C | E | D | Rang espéré (C++) | Place | Rang 90 % | Devant C++ | Devant Zig | C 1er |
|---|---|---|---|---|---|---|---|---|---|---|
| Avant | 72,6 | 81,5 | 78,6 | 50,6 | 3,88 (3,58) | 3 | 1–8 | 44 % | 55 % | 57 % |
| Publié | 73,5 | 84,0 | 78,6 | 50,6 | 3,63 (3,61) | 3 | 1–7 | 47 % | 59 % | 56 % |
| Fix-T | 73,7 | 84,0 | 79,4 | 50,3 | 3,09 (3,69) | 2 | 1–6 | 56 % | 66 % | 51 % |
| Fix-T sans K4 | 73,5 | 84,0 | 78,8 | 50,2 | 3,56 (3,62) | 2 | 1–7 | 48 % | 60 % | 56 % |
| Fix-pont (plan) | 74,2 | 84,0 | 80,6 | 50,3 | 2,74 (3,75) | 2 | 1–6 | 62 % | 72 % | 47 % |
| S-Q1 | 74,3 | 84,0 | 80,7 | 50,4 | 2,99 (3,72) | 2 | 1–6 | 58 % | 69 % | 51 % |
| S-agg | 73,3 | 84,0 | 78,7 | 49,7 | 3,50 (3,62) | 2 | 1–7 | 49 % | 61 % | 55 % |
| S-Q1+agg | 74,0 | 84,0 | 80,5 | 49,5 | 2,90 (3,73) | 2 | 1–6 | 60 % | 70 % | 50 % |
| H-fm | 75,2 | 89,0 | 78,6 | 50,6 | 2,88 (3,75) | 2 | 1–6 | 61 % | 73 % | 52 % |
| H-tout | 75,7 | 89,0 | 80,5 | 49,5 | 2,29 (3,87) | 2 | 1–5 | 74 % | 82 % | 43 % |

**Avant** : 1. C (1,93, 80,0), 2. C++ (3,58, 76,6), 3. Odin (3,88, 72,6), 4. Zig (4,75, 72,7), 5. C3 (5,74, 71,2), 6. Nim (6,66, 69,7), 7. Rust (6,67, 70,5), 8. D (7,42, 72,6), 9. Ada (8,01, 71,7), 10. Chapel (8,80, 66,1), 11. Fortran (10,25, 66,1), 12. Julia (11,24, 64,3), 13. Mojo (12,21, 62,8), 14. C# (14,03, 56,0).

**Publié** : 1. C (1,94, 80,0), 2. C++ (3,61, 76,6), 3. Odin (3,63, 73,5), 4. Zig (4,80, 72,7), 5. C3 (5,77, 71,2), 6. Nim (6,68, 69,7), 7. Rust (6,70, 70,5), 8. D (7,45, 72,6), 9. Ada (8,03, 71,7), 10. Chapel (8,81, 66,1), 11. Fortran (10,25, 66,1), 12. Julia (11,24, 64,3), 13. Mojo (12,21, 62,8), 14. C# (14,03, 56,0).

**Fix-T** : 1. C (2,03, 78,9), 2. Odin (3,09, 73,7), 3. C++ (3,69, 75,6), 4. Zig (4,86, 71,8), 5. C3 (5,87, 70,2), 6. Nim (6,72, 68,8), 7. Rust (6,76, 69,5), 8. D (7,51, 71,6), 9. Ada (8,05, 70,7), 10. Chapel (8,84, 65,1), 11. Fortran (10,27, 65,2), 12. Julia (11,25, 63,4), 13. Mojo (12,20, 61,9), 14. C# (14,03, 55,3).

**Fix-T sans K4** : 1. C (1,95, 79,6), 2. Odin (3,56, 73,5), 3. C++ (3,62, 76,2), 4. Zig (4,80, 72,3), 5. C3 (5,79, 70,8), 6. Nim (6,67, 69,3), 7. Rust (6,71, 70,1), 8. D (7,47, 72,2), 9. Ada (8,04, 71,2), 10. Chapel (8,81, 65,6), 11. Fortran (10,26, 65,7), 12. Julia (11,24, 63,9), 13. Mojo (12,21, 62,4), 14. C# (14,03, 55,6).

**Fix-pont (plan)** : 1. C (2,10, 78,5), 2. Odin (2,74, 74,2), 3. C++ (3,75, 75,2), 4. Zig (4,92, 71,3), 5. C3 (5,91, 69,8), 6. Nim (6,73, 68,3), 7. Rust (6,78, 69,1), 8. D (7,55, 71,2), 9. Ada (8,07, 70,3), 10. Chapel (8,85, 64,6), 11. Fortran (10,27, 64,7), 12. Julia (11,25, 62,9), 13. Mojo (12,20, 61,5), 14. C# (14,03, 54,9).

**S-Q1** : 1. C (2,03, 79,6), 2. Odin (2,99, 74,3), 3. C++ (3,72, 76,2), 4. Zig (4,89, 72,3), 5. C3 (5,88, 70,8), 6. Nim (6,72, 69,4), 7. Rust (6,76, 70,1), 8. D (7,51, 72,2), 9. Ada (8,06, 71,3), 10. Chapel (8,84, 65,7), 11. Fortran (10,27, 65,8), 12. Julia (11,25, 63,9), 13. Mojo (12,21, 62,4), 14. C# (14,03, 55,7).

**S-agg** : 1. C (1,95, 79,3), 2. Odin (3,50, 73,3), 3. C++ (3,62, 75,9), 4. Zig (4,82, 72,1), 5. C3 (5,80, 70,5), 6. Nim (6,69, 69,1), 7. Rust (6,71, 69,8), 8. D (7,47, 71,9), 9. Ada (8,03, 71,0), 10. Chapel (8,82, 65,4), 11. Fortran (10,26, 65,5), 12. Julia (11,25, 63,6), 13. Mojo (12,21, 62,2), 14. C# (14,03, 55,5).

**S-Q1+agg** : 1. C (2,05, 78,7), 2. Odin (2,90, 74,0), 3. C++ (3,73, 75,4), 4. Zig (4,90, 71,6), 5. C3 (5,91, 70,0), 6. Nim (6,71, 68,5), 7. Rust (6,77, 69,3), 8. D (7,52, 71,4), 9. Ada (8,06, 70,5), 10. Chapel (8,85, 64,8), 11. Fortran (10,27, 65,0), 12. Julia (11,25, 63,2), 13. Mojo (12,20, 61,7), 14. C# (14,03, 55,1).

**H-fm** : 1. C (2,04, 80,0), 2. Odin (2,88, 75,2), 3. C++ (3,75, 76,6), 4. Zig (4,94, 72,7), 5. C3 (5,86, 71,2), 6. Nim (6,73, 69,7), 7. Rust (6,75, 70,5), 8. D (7,53, 72,6), 9. Ada (8,08, 71,7), 10. Chapel (8,82, 66,1), 11. Fortran (10,26, 66,1), 12. Julia (11,25, 64,3), 13. Mojo (12,21, 62,8), 14. C# (14,03, 56,0).

**H-tout** : 1. C (2,18, 78,7), 2. Odin (2,29, 75,7), 3. C++ (3,87, 75,4), 4. Zig (5,02, 71,6), 5. C3 (5,96, 70,0), 6. Nim (6,75, 68,5), 7. Rust (6,79, 69,3), 8. D (7,58, 71,4), 9. Ada (8,09, 70,5), 10. Chapel (8,86, 64,8), 11. Fortran (10,28, 65,0), 12. Julia (11,26, 63,2), 13. Mojo (12,20, 61,7), 14. C# (14,03, 55,1).

