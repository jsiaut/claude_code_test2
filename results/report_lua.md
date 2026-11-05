# Remarque sur Lua : rapports appariés et scénarios

Plan : `docs/LUA.md`. Mesures : `results/raw_lua/` (machine 23, Cascade Lake, 7 processus par cellule). Code :
`analysis/lua_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal 0.0e+00).

## Rapports appariés (même hôte) : lua_fix / lua_ref

Clés corrigées (reportées) en gras ; Q6 naturel, au code identique dans les deux copies, sert de contrôle.

| Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|
| **k3:rmw_packed** | 2073,7 | 2000,6 | **0,965** | 0,913–1,019 |
| **k3:rmw_padded** | 2938,8 | 2104,9 | **0,716** | 0,679–0,754 |
| **k3:sw_packed** | 2065,8 | 2187,0 | **1,059** | 0,975–1,146 |
| **k3:sw_padded** | 2931,6 | 2154,6 | **0,735** | 0,689–0,790 |
| **k4:natural_unsorted** | 821,5 | 290,8 | **0,354** | 0,331–0,380 |
| **k4:natural_sorted** | 689,1 | 189,2 | **0,275** | 0,242–0,312 |
| **k4:branchless_unsorted** | 715,2 | 225,7 | **0,316** | 0,288–0,345 |
| **k6:tuned:q6** | 1212,5 | 900,2 | **0,742** | 0,691–0,811 |
| **k6:mt:q6** | 1209,6 | 933,5 | **0,772** | 0,702–0,853 |
| **k8:natural** | 8538,3 | 12259,4 | **1,436** | 1,381–1,500 |
| k6:natural:q6 | 496,6 | 531,0 | 1,069 | 1,013–1,124 |

## Latences de K8 naturel (médianes de toutes les répétitions, µs) : lua_fix / lua_ref

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| positionnel (lua_ref) | 370 | 546 | 746 | 27608 | 39277 |
| champs nommés (lua_fix) | 536 | 860 | 1064 | 36638 | 49810 |
| rapport [IC 95 %] | 1,449 [1,41–1,51] | 1,577 [1,36–1,77] | 1,427 [1,40–1,48] | 1,327 [1,24–1,43] | 1,268 [1,15–1,33] |

## Sensibilités (forme nouvelle / base, même hôte)

| Sensibilité | Clé | Base | Base (ms) | Forme nouvelle (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|---|
| q6_tuned_n | k6:tuned:q6 | lua_fix | 900,2 | 460,1 | 0,511 | 0,465–0,552 |
| q6_mt_n | k6:mt:q6 | lua_fix | 933,5 | 452,7 | 0,485 | 0,436–0,534 |
| k9_tuned_s | k9:tuned | lua_ref | 918,5 | 801,8 | 0,873 | 0,810–0,944 |
| k9_mt_s | k9:mt | lua_ref | 851,1 | 814,8 | 0,957 | 0,888–1,040 |
| k7_tuned_p | k7:tuned | lua_ref | 5672,9 | 4013,5 | 0,707 | 0,684–0,730 |
| k8_tuned_it | k8:tuned | lua_ref | 4545,5 | 4838,1 | 1,064 | 0,995–1,131 |
| k1_soa_h | k1:soa:energy | lua_ref | 216,3 | 179,8 | 0,831 | 0,737–0,937 |
| k2_tuned_s_16384 | k2:tuned:16384 | lua_ref | 33,5 | 25,8 | 0,770 | 0,687–0,876 |
| k2_tuned_s_262144 | k2:tuned:262144 | lua_ref | 45,6 | 37,5 | 0,821 | 0,763–0,885 |
| k2_tuned_s_8388608 | k2:tuned:8388608 | lua_ref | 646,7 | 630,1 | 0,974 | 0,886–1,055 |

## LuaJIT (S-LuaJIT, information)

| Rapport | Clé | Base (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|
| K3 conforme : luajit_fix / lua_fix | k3:rmw_packed | 2000,6 | 1552,5 | 0,776 | 0,735–0,817 |
| K3 conforme : luajit_fix / lua_fix | k3:rmw_padded | 2104,9 | 1550,2 | 0,736 | 0,698–0,779 |
| K3 conforme : luajit_fix / lua_fix | k3:sw_packed | 2187,0 | 1694,6 | 0,775 | 0,705–0,848 |
| K3 conforme : luajit_fix / lua_fix | k3:sw_padded | 2154,6 | 1594,8 | 0,740 | 0,694–0,787 |
| champs nommés : luajit_fix / luajit_ref | k8:natural | 4048,5 | 5546,4 | 1,370 | 1,286–1,457 |

## Python, K8 naturel sans `__slots__` (python_k8n / python_ref ; appliqué par analysis/python_check.py)

18796,6 → 19939,7 ms, rapport 1,061 [1,026–1,099].

## Pont par le C de clang (information : scénario L-E-P ; le classement publié reporte par transfert)

| Rapport | Clé | Lua publié | Transfert | Pont | Écart | Retenu | Facteur appliqué |
|---|---|---|---|---|---|---|---|
| pont k3:sw_padded | k3:sw_padded | 4343,0 ms | 3191,9 ms | 1048,8 ms | 204,3 % | pont | 0,241 |
| pont k3:rmw_padded | k3:rmw_padded | 4115,2 ms | 2947,4 ms | 1404,2 ms | 109,9 % | pont | 0,341 |
| pont k4:natural_unsorted | k4:natural_unsorted | 1040,3 ms | 368,2 ms | 440,3 ms | -16,4 % | transfert | 0,354 |
| pont k4:branchless_unsorted | k4:branchless_unsorted | 985,2 ms | 310,9 ms | 252,4 ms | 23,2 % | transfert | 0,316 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Lua | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 3,9 | 2,8 | 1,08 | 10,0 | 20,72 | 21 | 20–21 | devant Python 28 % |
| L-code | 4,0 | 2,8 | 1,31 | 10,0 | 20,67 | 21 | 20–21 | devant Python 33 % |
| L-M | 5,3 | 6,8 | 1,08 | 10,0 | 20,62 | 21 | 20–21 | devant Python 37 % |
| L-E | 5,4 | 6,8 | 1,31 | 10,0 | 20,58 | 21 | 20–21 | devant Python 42 % |
| L-E-P | 5,5 | 6,8 | 1,49 | 10,0 | 20,56 | 21 | 20–21 | devant Python 44 % |
| S-Q6n | 5,4 | 6,8 | 1,34 | 10,0 | 20,58 | 21 | 20–21 | devant Python 42 % |
| S-K9s | 5,4 | 6,8 | 1,31 | 10,0 | 20,58 | 21 | 20–21 | devant Python 42 % |
| S-K7p | 5,4 | 6,8 | 1,37 | 10,0 | 20,57 | 21 | 20–21 | devant Python 42 % |
| S-K8it | 5,4 | 6,8 | 1,31 | 10,0 | 20,58 | 21 | 20–21 | devant Python 42 % |
| S-K1h | 5,4 | 6,8 | 1,34 | 10,0 | 20,58 | 21 | 20–21 | devant Python 42 % |
| S-K2s | 5,7 | 6,8 | 1,31 | 11,3 | 20,56 | 21 | 20–21 | devant Python 44 % |
| S-mesures | 5,8 | 6,8 | 1,43 | 11,3 | 20,54 | 21 | 20–21 | devant Python 46 % |
| S-cases | 6,0 | 8,4 | 1,31 | 10,0 | 20,55 | 21 | 20–21 | devant Python 45 % |
| S-tout | 6,3 | 8,4 | 1,43 | 11,3 | 20,51 | 21 | 20–21 | devant Python 49 % |
| S-LuaJIT | 11,1 | 6,8 | 11,61 | 16,4 | 20,13 | 20 | 19–21 | devant JavaScript 8 %; derrière Python 79 % |
| S-LuaJIT-FFI | 15,9 | 20,3 | 11,61 | 16,4 | 19,49 | 19 | 19–20 | devant OCaml 4 %; derrière JavaScript 53 % |

Dans S-LuaJIT et S-LuaJIT-FFI, la ligne « Lua » porte LuaJIT.

**Avant** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,17, 11,8), 21. Lua (20,72, 3,9).

**L-code** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,22, 11,8), 21. Lua (20,67, 4,0).

**L-M** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,27, 11,8), 21. Lua (20,62, 5,3).

**L-E** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,31, 11,8), 21. Lua (20,58, 5,4).

**L-E-P** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,33, 11,8), 21. Lua (20,56, 5,5).

**S-Q6n** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,32, 11,8), 21. Lua (20,58, 5,4).

**S-K9s** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,31, 11,8), 21. Lua (20,58, 5,4).

**S-K7p** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,32, 11,8), 21. Lua (20,57, 5,4).

**S-K8it** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,31, 11,8), 21. Lua (20,58, 5,4).

**S-K1h** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,32, 11,8), 21. Lua (20,58, 5,4).

**S-K2s** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,34, 11,8), 21. Lua (20,56, 5,7).

**S-mesures** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,35, 11,8), 21. Lua (20,54, 5,8).

**S-cases** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,35, 11,8), 21. Lua (20,55, 6,0).

**S-tout** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,08, 15,6), 20. Python (20,39, 11,8), 21. Lua (20,51, 6,3).

**S-LuaJIT** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,02, 23,9), 19. JavaScript (19,16, 15,6), 20. Lua (20,13, 11,1), 21. Python (20,69, 11,8).

**S-LuaJIT-FFI** : 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,06, 23,9), 19. Lua (19,49, 15,9), 20. JavaScript (19,61, 15,6), 21. Python (20,84, 11,8).

## Rapports reportés sur la réplication (machine 3)

k3:rmw_packed 0,965, k3:rmw_padded 0,716, k3:sw_packed 1,059, k3:sw_padded 0,735, k4:branchless_unsorted 0,316, k4:natural_sorted 0,275, k4:natural_unsorted 0,354, k6:mt:q6 0,772, k6:tuned:q6 0,742, k8:natural 1,436 ; latences de K8 naturel : 1,449, 1,577, 1,427, 1,327, 1,268.
