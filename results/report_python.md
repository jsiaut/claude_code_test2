# Remarque sur Python : rapports appariés et scénarios

Plan : `docs/PYTHON.md`. Mesures : `results/raw_python/` (machine 22, Cascade Lake, 7 processus par cellule). Code :
`analysis/python_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal 0.0e+00).

## Rapports appariés (même hôte) : python_fix / python_ref

Clés corrigées (reportées) en gras : sous-interpréteurs au lieu de fils sérialisés par le GIL ; Q6 naturel, au code identique dans les deux copies, sert de contrôle.

| Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|
| **k3:rmw_packed** | 26036,9 | 18200,6 | **0,699** | 0,669–0,731 |
| **k3:rmw_padded** | 26658,1 | 8609,8 | **0,323** | 0,286–0,366 |
| **k3:sw_packed** | 14034,6 | 12654,3 | **0,902** | 0,847–0,954 |
| **k3:sw_padded** | 13584,6 | 4181,6 | **0,308** | 0,286–0,332 |
| **k6:mt:q6** | 1798,3 | 667,6 | **0,371** | 0,339–0,409 |
| **k6:mt:q1** | 6671,6 | 2285,4 | **0,343** | 0,323–0,363 |
| **k9:mt** | 1987,4 | 1023,1 | **0,515** | 0,472–0,558 |
| k6:natural:q6 | 1340,3 | 1361,7 | 1,016 | 0,958–1,072 |

## Build sans GIL, K3 corrigé (python_ftfix / python_ref, même hôte : sensibilité S-FT)

| Clé | Build par défaut, code publié (ms) | Sans GIL (ms) | Rapport | IC 95 % |
|---|---|---|---|---|
| k3:rmw_packed | 26036,9 | 20085,6 | 0,771 | 0,744–0,802 |
| k3:rmw_padded | 26658,1 | 9231,5 | 0,346 | 0,324–0,367 |
| k3:sw_packed | 14034,6 | 17411,0 | 1,241 | 1,174–1,322 |
| k3:sw_padded | 13584,6 | 5219,3 | 0,384 | 0,349–0,427 |
| k6:mt:q6 | 1798,3 | 786,1 | 0,437 | 0,409–0,470 |
| k6:mt:q1 | 6671,6 | 3294,5 | 0,494 | 0,466–0,524 |
| k9:mt | 1987,4 | 2295,5 | 1,155 | 1,071–1,250 |

## Sensibilités (forme nouvelle / base, même hôte)

| Sensibilité | Clé | Base | Base (ms) | Forme nouvelle (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|---|
| q6_tuned_c | k6:tuned:q6 | python_ref | 1590,2 | 563,0 | 0,354 | 0,324–0,391 |
| q6_mt_c | k6:mt:q6 | python_fix | 667,6 | 190,7 | 0,286 | 0,255–0,319 |
| k8_natural_f | k8:natural | python_ref | 19472,7 | 15573,4 | 0,800 | 0,729–0,881 |

## Latences de K8 naturel (médianes de toutes les répétitions, µs) : natural_f / natural

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| natural (python_ref) | 791 | 1525 | 1737 | 3564 | 752210 |
| natural_f (python_exp) | 793 | 1433 | 1714 | 3204 | 8985 |
| rapport [IC 95 %] | 1,003 [0,96–1,05] | 0,940 [0,84–1,21] | 0,987 [0,93–1,09] | 0,899 [0,81–1,07] | 0,012 [0,01–0,01] |

## Pont par le C de clang (information : scénario P-E-P ; le classement publié reporte par transfert)

| Rapport | Clé | Python publié | Transfert | Pont | Écart | Retenu | Facteur appliqué |
|---|---|---|---|---|---|---|---|
| pont k3:rmw_padded | k3:rmw_padded | 33100,3 ms | 10690,5 ms | 5701,8 ms | 87,5 % | pont | 0,172 |
| pont k3:sw_padded | k3:sw_padded | 17536,4 ms | 5398,0 ms | 2034,4 ms | 165,3 % | pont | 0,116 |
| pont k6:mt:q6 | k6:mt:q6 | 2358,8 ms | 875,7 ms | 714,3 ms | 22,6 % | transfert | 0,371 |
| pont k6:mt:q1 | k6:mt:q1 | 9031,5 ms | 3093,8 ms | 2346,5 ms | 31,8 % | pont | 0,260 |
| pont k9:mt | k9:mt | 1889,0 ms | 972,4 ms | 344,4 ms | 182,4 % | pont | 0,182 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Python | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 9,9 | 24,4 | 0,46 | 4,9 | 20,32 | 20 | 20–21 | devant JavaScript 5 %; derrière Lua 62 % |
| P-code | 10,0 | 24,4 | 0,59 | 4,9 | 20,27 | 20 | 20–21 | devant JavaScript 5 %; derrière Lua 68 % |
| P-M | 11,8 | 29,7 | 0,46 | 4,9 | 20,23 | 20 | 19–21 | devant JavaScript 9 %; derrière Lua 67 % |
| P-E | 11,8 | 29,7 | 0,59 | 4,9 | 20,17 | 20 | 19–21 | devant JavaScript 9 %; derrière Lua 72 % |
| P-E-P | 11,9 | 29,7 | 0,72 | 4,9 | 20,12 | 20 | 19–21 | devant JavaScript 9 %; derrière Lua 77 % |
| S-Q6c | 11,9 | 29,7 | 0,63 | 4,9 | 20,15 | 20 | 19–21 | devant JavaScript 9 %; derrière Lua 74 % |
| S-K8f | 12,0 | 29,7 | 0,59 | 5,6 | 19,99 | 20 | 19–21 | devant JavaScript 14 %; derrière Lua 83 % |
| S-FT | 11,8 | 29,7 | 0,59 | 4,9 | 20,17 | 20 | 19–21 | devant JavaScript 9 %; derrière Lua 72 % |
| S-mesures | 12,0 | 29,7 | 0,63 | 5,6 | 19,98 | 20 | 19–21 | devant JavaScript 15 %; derrière Lua 85 % |
| S-cases | 13,1 | 33,2 | 0,59 | 4,9 | 20,10 | 20 | 19–21 | devant JavaScript 12 %; derrière Lua 75 % |
| S-tout | 13,3 | 33,2 | 0,63 | 5,6 | 19,91 | 20 | 19–21 | devant JavaScript 19 %; derrière Lua 86 % |

**Avant** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,6), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**P-code** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,6), 20. Python (20,27, 10,0), 21. Lua (20,68, 3,9).

**P-M** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,23, 11,8), 21. Lua (20,67, 3,9).

**P-E** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,17, 11,8), 21. Lua (20,72, 3,9).

**P-E-P** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,09, 15,6), 20. Python (20,12, 11,9), 21. Lua (20,77, 3,9).

**S-Q6c** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,15, 11,9), 21. Lua (20,74, 3,9).

**S-K8f** : 16. Go (15,51, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,03, 23,9), 19. JavaScript (19,14, 15,6), 20. Python (19,99, 12,0), 21. Lua (20,83, 3,9).

**S-FT** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,17, 11,8), 21. Lua (20,72, 3,9).

**S-mesures** : 16. Go (15,51, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,03, 23,9), 19. JavaScript (19,14, 15,6), 20. Python (19,98, 12,0), 21. Lua (20,85, 3,9).

**S-cases** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,03, 23,9), 19. JavaScript (19,12, 15,6), 20. Python (20,10, 13,1), 21. Lua (20,75, 3,9).

**S-tout** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,05, 23,9), 19. JavaScript (19,18, 15,6), 20. Python (19,91, 13,3), 21. Lua (20,86, 3,9).

## Rapports reportés sur la réplication (machine 3)

k3:rmw_packed 0,699, k3:rmw_padded 0,323, k3:sw_packed 0,902, k3:sw_padded 0,308, k6:mt:q1 0,343, k6:mt:q6 0,371, k9:mt 0,515.
