# Remarque sur OCaml : rapports appariés et scénarios

Plan : `docs/OCAML.md`. Mesures : `results/raw_ocaml/` (machine 20, 7 processus par cellule). Code :
`analysis/ocaml_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal 0.0e+00).

## Rapports appariés (même hôte) : ocaml_fix / ocaml_ref

Clés corrigées (reportées) en gras ; les autres ne changent que d'horloge (contrôle, non reportées).

| Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|
| **k1:aos:energy** | 266,53 | 45,25 | **0,170** | 0,154–0,187 |
| k1:natural:energy | 80,71 | 77,60 | 0,961 | 0,917–1,008 |
| k1:natural_shuffled:energy | 235,67 | 244,44 | 1,037 | 0,952–1,138 |
| k1:soa:energy | 7,99 | 7,88 | 0,987 | 0,858–1,102 |
| k2:tuned:16384 | 12,15 | 12,16 | 1,001 | 0,967–1,037 |
| k2:tuned:16777216 | 626,21 | 642,73 | 1,026 | 0,942–1,123 |
| k2:tuned:2097152 | 184,63 | 177,62 | 0,962 | 0,891–1,046 |
| k2:tuned:262144 | 26,54 | 27,89 | 1,051 | 1,005–1,102 |
| k2:tuned:268435456 | 968,27 | 975,31 | 1,007 | 0,979–1,037 |
| k2:tuned:33554432 | 719,85 | 731,00 | 1,015 | 0,986–1,043 |
| k2:tuned:524288 | 29,20 | 30,30 | 1,038 | 0,995–1,079 |
| k2:tuned:65536 | 26,61 | 26,74 | 1,005 | 0,988–1,023 |
| k2:tuned:67108864 | 762,38 | 760,86 | 0,998 | 0,960–1,029 |
| k2:tuned:8388608 | 270,83 | 283,30 | 1,046 | 0,979–1,125 |
| k3:rmw_packed | 542,26 | 558,41 | 1,030 | 0,977–1,083 |
| k3:rmw_padded | 305,60 | 308,09 | 1,008 | 0,954–1,067 |
| k3:sw_packed | 764,32 | 794,12 | 1,039 | 1,000–1,084 |
| k3:sw_padded | 409,79 | 414,16 | 1,011 | 0,963–1,051 |
| k4:branchless_unsorted | 21,21 | 21,64 | 1,021 | 0,949–1,089 |
| k4:natural_sorted | 19,42 | 19,42 | 1,000 | 0,859–1,193 |
| k4:natural_unsorted | 92,86 | 94,89 | 1,022 | 0,996–1,047 |
| k5:natural | 204,55 | 197,66 | 0,966 | 0,919–1,009 |
| k5:tuned | 71,61 | 69,06 | 0,964 | 0,832–1,073 |
| k6:mt:q1 | 39,48 | 32,51 | 0,824 | 0,736–0,924 |
| **k6:mt:q6** | 59,18 | 27,62 | **0,467** | 0,432–0,508 |
| k6:natural:q1 | 104,40 | 110,67 | 1,060 | 0,993–1,148 |
| k6:natural:q6 | 151,12 | 151,92 | 1,005 | 0,974–1,043 |
| k6:tuned:q1 | 98,47 | 104,79 | 1,064 | 0,972–1,214 |
| **k6:tuned:q6** | 213,62 | 87,38 | **0,409** | 0,397–0,421 |
| k7:natural | 6233,54 | 6448,25 | 1,034 | 0,975–1,089 |
| k7:tuned | 567,16 | 589,09 | 1,039 | 0,962–1,112 |
| k8:natural | 229,10 | 230,24 | 1,005 | 0,954–1,064 |
| **k8:tuned** | 205,90 | 207,59 | **1,008** | 0,974–1,041 |
| k9:mt | 24,71 | 24,91 | 1,008 | 0,954–1,071 |
| k9:natural | 57,06 | 53,46 | 0,937 | 0,858–1,002 |
| k9:tuned | 42,05 | 46,56 | 1,107 | 1,028–1,205 |

**Correction du 3 novembre au soir** (docs/OCAML.md, 4.8) : K7 tuned à deux mots par case est la convention (16 octets par case, comme en C ; Java tasse clé et compteur dans un long) ; son rapport, mesuré en sensibilité (k7_tuned_p ci-dessous), est reporté dans le classement publié. Le scénario O-E-311 garde l'O-E d'avant.

## Sensibilités (forme nouvelle / ocaml_fix, même hôte)

| Sensibilité | Clé | Base (ms) | Forme nouvelle (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|
| q6_tuned_m | k6:tuned:q6 | 87,38 | 75,07 | 0,859 | 0,815–0,926 |
| q6_mt_m | k6:mt:q6 | 27,62 | 24,02 | 0,870 | 0,751–0,991 |
| k8_tuned_val | k8:tuned | 207,59 | 159,88 | 0,770 | 0,747–0,792 |
| k7_tuned_p | k7:tuned | 589,09 | 515,44 | 0,875 | 0,795–0,951 |
| k9_tuned_fa | k9:tuned | 46,56 | 44,01 | 0,945 | 0,894–0,998 |
| k9_mt_fa | k9:mt | 24,91 | 23,39 | 0,939 | 0,901–0,981 |
| k5_tuned_8 | k5:tuned | 69,06 | 66,86 | 0,968 | 0,916–1,038 |

## Pont par le C de clang (information : scénario O-E-P ; le classement publié reporte par transfert)

| Rapport | Clé | OCaml publié | Transfert | Pont | Écart | Retenu | Facteur appliqué |
|---|---|---|---|---|---|---|---|
| pont k6:tuned:q6 | k6:tuned:q6 | 274,94 ms | 112,46 ms | 99,73 ms | 12,8 % | transfert | 0,409 |
| pont k6:mt:q6 | k6:mt:q6 | 80,01 ms | 37,34 ms | 39,16 ms | -4,7 % | transfert | 0,467 |
| pont k1:aos:energy | k1:aos:energy | 312,22 ms | 53,01 ms | 53,55 ms | -1,0 % | transfert | 0,170 |
| pont k8:tuned | k8:tuned | 263,58 ms | 265,75 ms | 218,83 ms | 21,4 % | transfert | 1,008 |
| pont k7:tuned | k7:tuned | 1433,85 ms | 1254,59 ms | 1217,61 ms | 3,0 % | transfert | 0,875 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score d'OCaml | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 24,0 | 24,7 | 18,4 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| O-code | 24,4 | 24,7 | 19,4 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 1 %; derrière JavaScript 100 % |
| O-M | 23,5 | 23,2 | 18,4 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| O-E | 23,9 | 23,2 | 19,4 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| O-E-P | 23,9 | 23,2 | 19,4 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| O-E-311 | 23,8 | 23,2 | 19,1 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| S-Q6m | 24,0 | 23,2 | 19,6 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| S-K8v | 24,2 | 23,2 | 20,1 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| S-K9fa | 24,0 | 23,2 | 19,6 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| S-K5 | 24,0 | 23,2 | 19,5 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| S-mesures | 24,4 | 23,2 | 20,5 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| S-cases | 24,2 | 23,9 | 19,4 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |
| S-tout | 24,6 | 23,9 | 20,5 | 32,1 | 18,00 | 18 | 18–18 | devant Haskell 0 %; derrière JavaScript 100 % |

**Avant** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,0), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**O-code** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,4), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**O-M** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 23,5), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**O-E** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 23,9), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**O-E-P** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 23,9), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**O-E-311** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 23,8), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**S-Q6m** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,0), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**S-K8v** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,2), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**S-K9fa** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,0), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**S-K5** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,0), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**S-mesures** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,4), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**S-cases** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,2), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

**S-tout** : 14. C# (14,13, 54,9), 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 24,6), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9).

## Rapports reportés sur la réplication (machine 3)

k1:aos:energy 0,170, k6:mt:q6 0,467, k6:tuned:q6 0,409, k7:tuned 0,875, k8:tuned 1,008.
