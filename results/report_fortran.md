# Remarque sur Fortran : rapports appariés et scénarios

Plan : `docs/FORTRAN.md`. Mesures : `results/raw_fortran/` (machine 5, 7 processus par cellule). Code :
`analysis/fortran_check.py`. Processus rejetés : aucun.

Classement publié : S1, sauf K4 sans branchement, reporté par le témoin du même hôte (écart au plan, décidé
après ce calcul : `docs/FORTRAN.md`, 4.2 ; `analysis/transfer_check.py`, `results/transfer_check.json`).

Contrôle de Fortran avec les errata (A3, A4, B2) : 65,3 en règle v2, 57,2 en règle v1. C3 (vectorisation mesurée) : 0,5 avec le banc de la campagne, 1,0 avec le banc corrigé.

## Rapports appariés (fortran_fix / fortran, machine 5)

| Clé | Fortran (ms) | Fortran corrigé (ms) | Rapport | IC 95 % | Code changé |
|---|---|---|---|---|---|
| k1:aos:energy | 33,94 | 34,25 | 1,009 | 0,950–1,069 | non (témoin) |
| k1:natural:energy | 33,54 | 33,63 | 1,003 | 0,943–1,068 | oui |
| k1:natural_shuffled:energy | 32,97 | 34,75 | 1,054 | 1,008–1,100 | oui |
| k1:soa:energy | 5,62 | 5,51 | 0,980 | 0,896–1,073 | non (témoin) |
| k2:tuned:16384 | 8,06 | 6,60 | 0,819 | 0,792–0,841 | oui |
| k2:tuned:262144 | 21,54 | 19,10 | 0,887 | 0,814–0,962 | oui |
| k2:tuned:8388608 | 611,27 | 602,42 | 0,986 | 0,909–1,058 | oui |
| k3:rmw_padded: | 275,84 | 268,62 | 0,974 | 0,932–1,014 | non (témoin) |
| k3:sw_padded: | 73,83 | 76,02 | 1,030 | 0,995–1,068 | non (témoin) |
| k4:branchless_unsorted: | 20,49 | 4,59 | 0,224 | 0,197–0,264 | oui |
| k4:natural_unsorted: | 13,80 | 6,60 | 0,478 | 0,409–0,552 | oui |
| k5:natural: | 166,49 | 168,49 | 1,012 | 1,001–1,023 | oui |
| k5:tuned: | 8,20 | 9,38 | 1,144 | 0,987–1,352 | non (témoin) |
| k6:mt:q1 | 10,58 | 12,28 | 1,161 | 1,033–1,333 | non (témoin) |
| k6:mt:q6 | 4,31 | 4,78 | 1,110 | 1,002–1,235 | non (témoin) |
| k6:natural:q1 | 50,19 | 56,13 | 1,118 | 0,996–1,265 | oui |
| k6:natural:q6 | 54,62 | 55,97 | 1,025 | 0,980–1,069 | oui |
| k6:tuned:q1 | 37,71 | 36,49 | 0,968 | 0,878–1,079 | non (témoin) |
| k6:tuned:q6 | 15,13 | 15,28 | 1,010 | 0,966–1,050 | non (témoin) |
| k7:natural: | 863,25 | 871,15 | 1,009 | 0,863–1,177 | non (témoin) |
| k7:tuned: | 521,40 | 504,39 | 0,967 | 0,933–1,003 | non (témoin) |
| k8:natural: | 801,66 | 750,86 | 0,937 | 0,801–1,094 | non (témoin) |
| k8:tuned: | 196,13 | 200,58 | 1,023 | 0,931–1,122 | non (témoin) |
| k9:mt: | 9,02 | 8,30 | 0,920 | 0,855–0,982 | non (témoin) |
| k9:natural: | 28,54 | 28,32 | 0,992 | 0,938–1,050 | oui |
| k9:tuned: | 28,21 | 28,07 | 0,995 | 0,950–1,035 | non (témoin) |

## Sensibilité : formes de la remarque (fortran_exp / fortran)

| Clé | Rapport | IC 95 % |
|---|---|---|
| k5:tuned: | 0,980 | 0,843–1,178 |
| k8:tuned: | 0,688 | 0,590–0,813 |

## Témoin du même hôte : C compilé par GCC

| Clé | Fortran (ms) | Fortran corrigé (ms) | Sensibilité (ms) | C par GCC (ms) | Corrigé / GCC | Fortran / GCC données principales |
|---|---|---|---|---|---|---|
| k4:branchless_unsorted: | 20,49 | 4,59 | — | 4,78 | 0,96 | 2,50 |
| k4:natural_unsorted: | 13,80 | 6,60 | — | 6,12 | 1,08 | 1,92 |
| k5:tuned: | 8,20 | 9,38 | 8,03 | 6,50 | 1,44 | 1,40 |
| k8:tuned: | 196,13 | 200,58 | 134,95 | 146,24 | 1,37 | 1,20 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Fortran | Plafond E | D1 | Contrôle C | Rang espéré | Place | Rang 90 % | Devance le suivant |
|---|---|---|---|---|---|---|---|---|
| F-E | 62,6 | 67,2 | 18,0 | 65,3 | 11,13 | 11 | 8–13 | Julia 47 % |
| S1 | 68,4 | 79,9 | 19,8 | 65,3 | 8,24 | 9 | 3–12 | D 50 % |
| S1-K5 | 68,4 | 79,9 | 19,8 | 65,3 | 8,24 | 9 | 3–12 | D 49 % |
| S1-26 | 67,8 | 78,4 | 20,0 | 65,3 | 8,54 | 10 | 4–12 | Chapel 70 % |
| S2 | 70,0 | 84,0 | 19,8 | 65,3 | 7,28 | 8 | 2–11 | Rust 50 % |

**F-E** : 1. C (1,66, 80,1), 2. C++ (2,67, 77,0), 3. Odin (3,99, 72,3), 4. C3 (4,99, 71,0), 5. Zig (5,59, 71,5), 6. Nim (6,42, 69,5), 7. Ada (6,79, 71,6), 8. Rust (7,09, 69,4), 9. D (8,05, 71,0), 10. Chapel (9,40, 64,1), 11. Fortran (11,13, 62,6), 12. Julia (11,16, 62,2).

**S1** : 1. C (1,67, 80,1), 2. C++ (2,76, 77,0), 3. Odin (4,10, 72,3), 4. C3 (5,13, 71,0), 5. Zig (5,84, 71,5), 6. Nim (6,69, 69,5), 7. Ada (7,09, 71,6), 8. Rust (7,39, 69,4), 9. Fortran (8,24, 68,4), 10. D (8,38, 71,0), 11. Chapel (9,88, 64,1), 12. Julia (11,55, 62,2).

**S1-K5** : 1. C (1,67, 80,1), 2. C++ (2,76, 77,0), 3. Odin (4,10, 72,3), 4. C3 (5,13, 71,0), 5. Zig (5,84, 71,5), 6. Nim (6,68, 69,5), 7. Ada (7,09, 71,6), 8. Rust (7,38, 69,4), 9. Fortran (8,24, 68,4), 10. D (8,37, 71,0), 11. Chapel (9,88, 64,1), 12. Julia (11,55, 62,2).

**S1-26** : 1. C (1,67, 80,1), 2. C++ (2,75, 77,0), 3. Odin (4,08, 72,2), 4. C3 (5,11, 71,0), 5. Zig (5,82, 71,5), 6. Nim (6,64, 69,5), 7. Ada (7,05, 71,6), 8. Rust (7,35, 69,4), 9. D (8,34, 71,0), 10. Fortran (8,54, 67,8), 11. Chapel (9,84, 64,1), 12. Julia (11,54, 62,2).

**S2** : 1. C (1,70, 80,1), 2. C++ (2,81, 77,0), 3. Odin (4,19, 72,3), 4. C3 (5,24, 71,0), 5. Zig (5,93, 71,5), 6. Nim (6,81, 69,5), 7. Ada (7,20, 71,6), 8. Fortran (7,28, 70,0), 9. Rust (7,51, 69,4), 10. D (8,47, 71,0), 11. Chapel (9,97, 64,1), 12. Julia (11,58, 62,2).
