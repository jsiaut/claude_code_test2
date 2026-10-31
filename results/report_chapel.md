# Remarque sur Chapel : rapports appariés et scénarios

Plan : `docs/CHAPEL.md`. Mesures : `results/raw_chapel/` (machine 8, 7 processus par cellule). Code :
`analysis/chapel_check.py`. Processus rejetés : aucun.

## Temps (moyenne géométrique des médianes par processus, ms)

| Implémentation | Clé | Temps (ms) |
|---|---|---|
| c | k1:aos:energy | 32,29 |
| c | k1:soa:energy | 5,19 |
| c | k5:tuned: | 5,24 |
| c | k6:mt:q1 | 8,57 |
| c | k6:tuned:q1 | 30,39 |
| c | k7:natural: | 519,33 |
| chapel_exp | k1:aos:energy | 23,44 |
| chapel_exp | k1:soa:energy | 5,07 |
| chapel_exp | k5:tuned: | 5,41 |
| chapel_exp | k6:mt:q1 | 9,74 |
| chapel_exp | k6:tuned:q1 | 30,92 |
| chapel_exp | k6:tuned:q6 | 16,31 |
| chapel_exp | k7:natural: | 1008,30 |
| chapel_exp | k7:tuned: | 242,43 |
| chapel_exp | k9:tuned: | 23,53 |
| chapel_ref | k1:aos:energy | 24,43 |
| chapel_ref | k1:soa:energy | 5,08 |
| chapel_ref | k5:tuned: | 5,02 |
| chapel_ref | k6:mt:q1 | 11,26 |
| chapel_ref | k6:tuned:q1 | 37,01 |
| chapel_ref | k6:tuned:q6 | 15,79 |
| chapel_ref | k7:natural: | 1784,95 |
| chapel_ref | k7:tuned: | 229,55 |
| chapel_ref | k9:tuned: | 26,04 |
| chapel_std2 | k1:aos:energy | 32,20 |
| chapel_std2 | k1:soa:energy | 5,32 |
| chapel_std2 | k5:tuned: | 8,89 |

## Rapports appariés (chapel_exp / chapel_ref)

| Clé | Rapport | IC 95 % |
|---|---|---|
| k6:tuned:q1 | 0,835 | 0,772–0,904 |
| k6:mt:q1 | 0,865 | 0,721–1,063 |
| k5:tuned: | 1,078 | 0,930–1,267 |
| k1:aos:energy | 0,960 | 0,838–1,125 |
| k1:soa:energy | 0,997 | 0,947–1,054 |
| k7:natural: | 0,565 | 0,517–0,617 |
| k9:tuned: | 0,904 | 0,818–0,995 |
| k6:tuned:q6 | 1,032 | 0,952–1,122 |
| k7:tuned: | 1,056 | 0,969–1,156 |

## Copie standard corrigée (chapel_std2 / chapel_ref)

| Clé | Rapport | IC 95 % |
|---|---|---|
| k5:tuned: | 1,772 | 1,522–2,064 |
| k1:aos:energy | 1,318 | 1,191–1,470 |
| k1:soa:energy | 1,047 | 0,941–1,193 |

## Report sur les données principales (transfert ou pont par le C de clang)

| Clé | Chapel (données principales) | Transfert | Pont | Écart | Retenu |
|---|---|---|---|---|---|
| k6:tuned:q1 | 48,55 ms | 40,56 ms | 32,68 ms | 24,1 % | transfert (0,835) |
| k6:mt:q1 | 22,76 ms | 19,69 ms | 15,27 ms | 29,0 % | pont (0,671) |
| k5:tuned: | 4,68 ms | 5,04 ms | 4,07 ms | 24,0 % | transfert (1,078) |
| k1:aos:energy | 50,70 ms | 48,65 ms | 27,91 ms | 74,3 % | pont (0,551) |
| k1:soa:energy | 7,75 ms | 7,73 ms | 7,57 ms | 2,1 % | transfert (0,997) |
| k7:natural: | 3520,92 ms | 1988,93 ms | 9914,45 ms | -79,9 % | pont (2,816) |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Chapel | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 64,1 | 56,6 | 80,2 | 48,7 | 9,94 | 11 | 5–13 | devant Fortran 44 %; derrière Julia 63 % |
| C-E | 65,9 | 61,8 | 80,2 | 48,7 | 9,03 | 10 | 4–13 | devant D 46 %; derrière Fortran 60 % |
| S-B3 | 66,6 | 63,8 | 80,2 | 48,7 | 8,60 | 10 | 4–12 | devant D 51 %; derrière Fortran 67 % |
| S1 | 65,9 | 61,8 | 80,9 | 47,4 | 9,39 | 10 | 5–13 | devant D 42 %; derrière Fortran 55 % |
| S1-B3 | 66,6 | 63,8 | 80,9 | 47,4 | 8,99 | 10 | 4–12 | devant D 47 %; derrière Fortran 61 % |
| S1-T | 66,1 | 61,8 | 80,3 | 49,5 | 8,62 | 10 | 4–13 | devant D 50 %; derrière Fortran 66 % |

## Confrontation, scénario C (règle du standard sur les données), état actuel du classement

| Copie standard de Chapel | Rapports K5 tuned / K1 aos / K1 soa | Plafond E | Score | Place sur 18 |
|---|---|---|---|---|
| origine | 23,04 / 0,98 / 1,69 | 49,3 | 53,5 | 11 |
| corrigé | 1,77 / 0,98 / 1,05 | 72,1 | 62,7 | 10 |

**Avant** : 1. C (1,67, 80,1), 2. C++ (2,71, 77,0), 3. Odin (4,05, 72,3), 4. C3 (5,09, 71,0), 5. Zig (5,75, 71,5), 6. Nim (6,58, 69,5), 7. Ada (7,01, 71,6), 8. Rust (7,31, 69,4), 9. D (8,32, 71,0), 10. Fortran (9,62, 66,3), 11. Chapel (9,94, 64,1), 12. Julia (11,12, 64,0), 13. Mojo (11,97, 62,7), 14. C# (14,16, 54,8).

**C-E** : 1. C (1,67, 80,1), 2. C++ (2,72, 77,0), 3. Odin (4,07, 72,3), 4. C3 (5,13, 71,0), 5. Zig (5,80, 71,5), 6. Nim (6,66, 69,5), 7. Ada (7,09, 71,6), 8. Rust (7,41, 69,4), 9. D (8,43, 71,0), 10. Chapel (9,03, 65,9), 11. Fortran (9,78, 66,3), 12. Julia (11,25, 64,0), 13. Mojo (12,07, 62,7), 14. C# (14,19, 54,8).

**S-B3** : 1. C (1,67, 80,1), 2. C++ (2,73, 77,0), 3. Odin (4,08, 72,3), 4. C3 (5,15, 71,0), 5. Zig (5,83, 71,5), 6. Nim (6,71, 69,5), 7. Ada (7,14, 71,6), 8. Rust (7,46, 69,4), 9. D (8,48, 71,0), 10. Chapel (8,60, 66,6), 11. Fortran (9,84, 66,3), 12. Julia (11,29, 64,0), 13. Mojo (12,11, 62,7), 14. C# (14,19, 54,8).

**S1** : 1. C (1,67, 80,1), 2. C++ (2,71, 77,0), 3. Odin (4,06, 72,3), 4. C3 (5,10, 71,0), 5. Zig (5,78, 71,5), 6. Nim (6,64, 69,5), 7. Ada (7,05, 71,6), 8. Rust (7,36, 69,4), 9. D (8,38, 71,0), 10. Chapel (9,39, 65,9), 11. Fortran (9,72, 66,3), 12. Julia (11,19, 64,0), 13. Mojo (12,06, 62,7), 14. C# (14,18, 54,8).

**S1-B3** : 1. C (1,67, 80,1), 2. C++ (2,71, 77,0), 3. Odin (4,07, 72,3), 4. C3 (5,12, 71,0), 5. Zig (5,80, 71,5), 6. Nim (6,68, 69,5), 7. Ada (7,09, 71,6), 8. Rust (7,41, 69,4), 9. D (8,43, 71,0), 10. Chapel (8,99, 66,6), 11. Fortran (9,78, 66,3), 12. Julia (11,24, 64,0), 13. Mojo (12,10, 62,7), 14. C# (14,19, 54,8).

**S1-T** : 1. C (1,67, 80,1), 2. C++ (2,74, 77,0), 3. Odin (4,09, 72,3), 4. C3 (5,17, 71,0), 5. Zig (5,83, 71,5), 6. Nim (6,70, 69,5), 7. Ada (7,13, 71,6), 8. Rust (7,46, 69,4), 9. D (8,46, 71,0), 10. Chapel (8,62, 66,1), 11. Fortran (9,84, 66,3), 12. Julia (11,28, 64,0), 13. Mojo (12,09, 62,7), 14. C# (14,19, 54,8).

