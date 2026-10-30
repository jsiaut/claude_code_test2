# Remarque sur Ada : rapports appariés et scénarios

Plan : `docs/ADA.md`. Mesures : `results/raw_ada/` (machine 5, 7 processus par cellule). Code :
`analysis/ada_check.py`. Processus rejetés : aucun.

Contrôle d'Ada avec les errata (E5, C1, B4) : 80,6 en règle v2, 71,7 en règle v1.

## Rapports appariés (ada_fix / ada, machine 5)

| Clé | Ada (ms) | Ada corrigé (ms) | Rapport | IC 95 % | Code changé |
|---|---|---|---|---|---|
| k1:aos:energy | 33,49 | 31,77 | 0,949 | 0,893–1,006 | oui |
| k1:natural:energy | 33,36 | 33,90 | 1,016 | 0,979–1,056 | non (témoin) |
| k1:natural_shuffled:energy | 32,24 | 33,73 | 1,046 | 0,967–1,133 | non (témoin) |
| k1:soa:energy | 5,59 | 5,26 | 0,942 | 0,851–1,030 | oui |
| k2:tuned:16384 | 9,92 | 8,23 | 0,829 | 0,748–0,901 | oui |
| k2:tuned:262144 | 23,58 | 20,89 | 0,886 | 0,810–0,968 | oui |
| k2:tuned:8388608 | 617,97 | 622,96 | 1,008 | 0,965–1,056 | oui |
| k3:rmw_padded: | 280,35 | 280,40 | 1,000 | 0,951–1,050 | non (témoin) |
| k3:sw_padded: | 84,89 | 82,48 | 0,972 | 0,906–1,025 | non (témoin) |
| k4:branchless_unsorted: | 4,38 | 4,62 | 1,054 | 0,953–1,216 | non (témoin) |
| k4:natural_unsorted: | 6,09 | 6,22 | 1,021 | 0,975–1,087 | non (témoin) |
| k5:natural: | 170,49 | 172,50 | 1,012 | 0,971–1,079 | non (témoin) |
| k5:tuned: | 6,81 | 7,45 | 1,094 | 0,932–1,279 | oui |
| k6:mt:q1 | 21,81 | 21,97 | 1,007 | 0,897–1,141 | oui |
| k6:mt:q6 | 17,23 | 8,75 | 0,508 | 0,467–0,552 | oui |
| k6:natural:q1 | 112,34 | 113,34 | 1,009 | 0,848–1,187 | non (témoin) |
| k6:natural:q6 | 63,97 | 61,26 | 0,958 | 0,874–1,049 | non (témoin) |
| k6:tuned:q1 | 47,39 | 47,75 | 1,008 | 0,840–1,255 | oui |
| k6:tuned:q6 | 16,21 | 16,58 | 1,022 | 0,966–1,085 | oui |
| k7:natural: | 7798,86 | 8049,29 | 1,032 | 0,972–1,091 | non (témoin) |
| k7:tuned: | 381,23 | 396,03 | 1,039 | 0,946–1,144 | non (témoin) |
| k8:natural: | 922,06 | 758,73 | 0,823 | 0,733–0,934 | non (témoin) |
| k8:tuned: | 117,03 | 92,19 | 0,788 | 0,629–1,000 | non (témoin) |
| k8:tuned_alloc: | 185,72 | 203,20 | 1,094 | 0,969–1,222 | non (témoin) |
| k9:mt: | 20,44 | 17,30 | 0,846 | 0,788–0,911 | oui |
| k9:natural: | 54,70 | 68,18 | 1,246 | 1,076–1,488 | non (témoin) |
| k9:tuned: | 36,12 | 27,26 | 0,755 | 0,666–0,844 | oui |

## Témoin du même hôte : C compilé par GCC

| Clé | Ada (ms) | Ada corrigé (ms) | C par GCC (ms) | Ada corrigé / GCC | Ada / GCC données principales |
|---|---|---|---|---|---|
| k6:tuned:q6 | 16,21 | 16,58 | 16,78 | 0,99 | 0,97 |
| k6:tuned:q1 | 47,39 | 47,75 | 26,78 | 1,78 | 1,68 |
| k6:mt:q6 | 17,23 | 8,75 | 5,86 | 1,49 | 2,38 |
| k6:mt:q1 | 21,81 | 21,97 | 9,46 | 2,32 | 2,31 |
| k9:tuned: | 36,12 | 27,26 | 27,14 | 1,00 | 1,37 |
| k9:mt: | 20,44 | 17,30 | 9,77 | 1,77 | 2,22 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score d'Ada | Plafond E | D1 | Contrôle C | Rang espéré | Place | Rang 90 % | Devance le suivant |
|---|---|---|---|---|---|---|---|---|
| A-E | 69,5 | 73,9 | 14,1 | 80,6 | 7,97 | 9 | 3–11 | Chapel 63 % |
| S1 | 71,6 | 78,1 | 14,0 | 80,6 | 6,78 | 7 | 2–11 | Rust 52 % |
| S1-K5 | 71,2 | 77,2 | 14,0 | 80,6 | 6,96 | 7 | 2–11 | Rust 49 % |
| S1-27 | 70,9 | 76,6 | 13,4 | 80,6 | 6,65 | 7 | 2–11 | Rust 53 % |

**A-E** : 1. C (1,64, 80,1), 2. C++ (2,63, 77,1), 3. Odin (3,88, 72,3), 4. C3 (4,86, 71,1), 5. Zig (5,44, 71,5), 6. Nim (6,26, 69,6), 7. Rust (6,90, 69,4), 8. D (7,85, 71,1), 9. Ada (7,97, 69,5), 10. Chapel (9,17, 64,1), 11. Julia (10,97, 62,3), 12. Fortran (11,57, 60,9).

**S1** : 1. C (1,66, 80,1), 2. C++ (2,67, 77,0), 3. Odin (3,98, 72,3), 4. C3 (4,98, 71,0), 5. Zig (5,58, 71,5), 6. Nim (6,41, 69,5), 7. Ada (6,78, 71,6), 8. Rust (7,07, 69,4), 9. D (8,02, 71,0), 10. Chapel (9,30, 64,1), 11. Julia (11,05, 62,2), 12. Fortran (11,62, 60,8).

**S1-K5** : 1. C (1,66, 80,1), 2. C++ (2,66, 77,0), 3. Odin (3,96, 72,3), 4. C3 (4,96, 71,0), 5. Zig (5,56, 71,5), 6. Nim (6,38, 69,5), 7. Ada (6,96, 71,2), 8. Rust (7,04, 69,4), 9. D (7,99, 71,0), 10. Chapel (9,28, 64,1), 11. Julia (11,04, 62,2), 12. Fortran (11,61, 60,8).

**S1-27** : 1. C (1,68, 79,0), 2. C++ (2,69, 76,0), 3. Odin (4,00, 71,2), 4. C3 (5,02, 70,0), 5. Zig (5,58, 70,6), 6. Nim (6,41, 68,6), 7. Ada (6,65, 70,9), 8. Rust (7,09, 68,4), 9. D (8,02, 70,1), 10. Chapel (9,32, 63,1), 11. Julia (11,04, 61,4), 12. Fortran (11,62, 59,9).
