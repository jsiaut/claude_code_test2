# Remarque sur Swift : pont par la machine 24 (Emerald Rapids), errata et scénarios

Plan : `docs/SWIFT.md`, section 5. Mesures : `results/raw_swift_er/` (machine 24, Emerald Rapids, 7 processus par cellule). Code : `analysis/swift_remark.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant (grille et pont d'avant la remarque) reproduit S-E de `results/swift_check.json` (écart maximal 0.0e+00).

## Swift / C : machine 24 (constructions natives) et machine 23 (Cascade Lake)

| Cellule | Swift ER (ms) | C ER (ms) | Swift / C, machine 24 [IC 95 %] | Swift / C, machine 23 [IC 95 %] |
|---|---|---|---|---|
| k1:aos:energy | 33,092 | 31,237 | 1,059 [1,016–1,115] | 1,116 [1,051–1,179] |
| k1:natural:energy | 27,705 | 31,093 | 0,891 [0,804–0,999] | 0,940 [0,871–1,015] |
| k1:natural_shuffled:energy | 33,613 | 26,242 | 1,281 [1,179–1,390] | 1,094 [1,003–1,204] |
| k1:soa:energy | 2,702 | 2,679 | 1,009 [0,957–1,063] | 0,947 [0,908–0,990] |
| k2:tuned:16384 | 6,453 | 6,309 | 1,023 [0,935–1,113] | 1,022 [1,003–1,041] |
| k2:tuned:262144 | 20,735 | 20,950 | 0,990 [0,972–1,006] | 1,051 [0,949–1,167] |
| k2:tuned:8388608 | 253,099 | 254,188 | 0,996 [0,939–1,058] | 1,115 [1,012–1,218] |
| k3:rmw_packed | 4197,293 | 4303,893 | 0,975 [0,919–1,036] | 1,029 [0,969–1,089] |
| k3:rmw_padded | 197,255 | 198,031 | 0,996 [0,966–1,025] | 0,985 [0,935–1,025] |
| k3:sw_packed | 93,064 | 84,506 | 1,101 [1,073–1,138] | 1,006 [0,982–1,037] |
| k3:sw_padded | 79,065 | 71,879 | 1,100 [1,089–1,111] | 1,008 [0,996–1,022] |
| k4:branchless_unsorted | 1,737 | 2,094 | 0,830 [0,784–0,886] | 1,170 [0,956–1,409] |
| k4:natural_sorted | 7,901 | 1,999 | 3,952 [3,564–4,422] | 2,990 [2,507–3,634] |
| k4:natural_unsorted | 63,271 | 2,127 | 29,751 [26,608–33,002] | 29,278 [23,907–35,416] |
| k5:natural | 79,853 | 159,535 | 0,501 [0,486–0,514] | 1,003 [0,988–1,019] |
| k5:tuned | 3,827 | 3,740 | 1,023 [0,840–1,223] | 1,067 [0,945–1,215] |
| k6:mt:q1 | 9,655 | 9,071 | 1,064 [0,924–1,218] | 1,332 [1,202–1,504] |
| k6:mt:q6 | 3,915 | 4,683 | 0,836 [0,731–0,974] | 0,872 [0,733–1,008] |
| k6:natural:q1 | 61,387 | 50,217 | 1,222 [1,148–1,288] | 1,458 [1,266–1,688] |
| k6:natural:q6 | 51,124 | 49,991 | 1,023 [0,962–1,072] | 1,087 [1,042–1,132] |
| k6:tuned:q1 | 30,616 | 29,637 | 1,033 [0,946–1,096] | 1,466 [1,280–1,639] |
| k6:tuned:q6 | 14,551 | 17,096 | 0,851 [0,820–0,882] | 0,934 [0,872–1,000] |
| k7:natural | 1306,345 | 410,264 | 3,184 [3,012–3,362] | 3,150 [2,780–3,519] |
| k7:tuned | 186,726 | 172,657 | 1,081 [1,031–1,140] | 1,141 [1,023–1,261] |
| k8:natural | 1393,522 | 523,079 | 2,664 [2,498–2,861] | 2,423 [2,218–2,644] |
| k8:tuned | 236,278 | 230,692 | 1,024 [0,986–1,061] | 1,015 [0,942–1,084] |
| k9:mt | 5,196 | 4,950 | 1,050 [0,884–1,258] | 1,115 [0,989–1,246] |
| k9:natural | 62,491 | 12,409 | 5,036 [4,674–5,438] | 2,977 [2,767–3,202] |
| k9:tuned | 12,072 | 11,624 | 1,039 [0,955–1,121] | 1,003 [0,957–1,055] |

Binaires publiés (Cascade Lake) exécutés sur la machine 24 (pont de K9 et des latences de K8 ; Q1 pour information) :

| Cellule | Swift (ms) | C (ms) | Swift / C [IC 95 %] |
|---|---|---|---|
| k6:tuned:q1 | 31,267 | 27,744 | 1,127 [1,067–1,186] |
| k8:natural | 1378,194 | 534,243 | 2,580 [2,414–2,774] |
| k9:mt | 4,582 | 4,594 | 0,997 [0,929–1,061] |
| k9:natural | 61,283 | 12,748 | 4,807 [4,389–5,224] |
| k9:tuned | 12,101 | 12,027 | 1,006 [0,935–1,084] |

Latences de K8 naturel (µs, médianes de toutes les répétitions) :

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| Swift, machine 24 (binaire publié) | 82,6 | 97,0 | 134,7 | 257,1 | 1421,6 |
| C, machine 24 (binaire publié) | 31,4 | 39,8 | 62,0 | 112,2 | 797,3 |
| Swift / C, machine 24 | 2,63 | 2,43 | 2,17 | 2,29 | 1,78 |
| Swift / C, machine 23 | 2,64 | 2,49 | 2,48 | 1,97 | 1,14 |

## Le pont, avant et après (valeurs publiées de Swift)

| Clé | C publié (ms) | Swift, pont de la machine 23 (ms) | Swift, pont de la machine 24 (ms) |
|---|---|---|---|
| k5:natural | 158,106 | 158,567 | 79,138 |
| k5:tuned | 3,936 | 4,201 | 4,028 |
| k9:mt | 4,734 | 5,280 | 4,721 |
| k9:natural | 13,856 | 41,251 | 66,609 |
| k9:tuned | 15,881 | 15,925 | 15,979 |

| Latences de K8 (µs) | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| C publié | 31,7 | 41,9 | 65,7 | 116,2 | 1018,2 |
| Swift, pont de la machine 23 | 83,8 | 104,3 | 162,8 | 228,3 | 1159,6 |
| Swift, pont de la machine 24 | 83,4 | 102,0 | 142,7 | 266,3 | 1815,4 |

## Information

* K4 naturel avec `&+=` (`swift_ub`, cible cascadelake) / avec `+=` : 0,026 [0,024–0,030] (1,78 contre 67,23 ms) ; / C natif : 0,837.
* K8 naturel en `UniqueBox` / classe : 0,453 [0,428–0,477] ; / C (binaire publié) : 1,195 ; latences p50 0,45, p90 0,45, p99 0,49, p99,9 0,46, max 0,59.
* Facteurs du pont de K7 (C publié / C machine 23) : naturel 7,608, optimisé 1,703 ; R-K7 multiplie K7 naturel de Swift par 0,224.

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|---|
| Avant | 65,24 | 64,4 | 79,38 | 43,8 | 11,01 | 12e | [6, 14] |
| R-D4 | 66,29 | 67,4 | 79,38 | 43,8 | 10,60 | 11e | [5, 14] |
| R-E4 | 65,49 | 65,1 | 79,38 | 43,8 | 10,89 | 12e | [5, 14] |
| R-grille | 66,54 | 68,1 | 79,38 | 43,8 | 10,47 | 11e | [5, 14] |
| R-pont | 65,16 | 64,4 | 80,35 | 42,0 | 11,22 | 12e | [6, 14] |
| R-E | 66,46 | 68,1 | 80,35 | 42,0 | 10,69 | 11e | [6, 14] |
| R-E4-0 | 66,21 | 67,4 | 80,35 | 42,0 | 10,81 | 12e | [6, 14] |
| R-D4-½ | 65,93 | 66,6 | 80,35 | 42,0 | 10,83 | 12e | [6, 14] |
| R-K7 | 66,69 | 68,1 | 80,35 | 42,9 | 10,36 | 11e | [5, 14] |
| R-UB | 67,84 | 68,1 | 80,35 | 47,5 | 10,23 | 11e | [5, 14] |
| R-hôte | 64,44 | 68,1 | 76,63 | 39,8 | 11,10 | 12e | [6, 14] |
| R-Ou | 66,80 | 68,1 | 80,35 | 43,3 | 10,18 | 11e | [5, 14] |
| R-cases-bas | 64,08 | 61,3 | 80,35 | 42,0 | 11,80 | 12e | [7, 15] |
| R-cases-haut | 67,83 | 72,0 | 80,35 | 42,0 | 9,97 | 11e | [5, 14] |

Voisins dans R-E : devant Chapel (Swift devant dans 33 % des variantes) ; derrière Fortran (Swift devant dans 54 % des variantes).

## Classement : avant la remarque et publié (R-E)

| Place | Avant | rang espéré | R-E | rang espéré | score R-E |
|---|---|---|---|---|---|
| 1 | C | 2,20 | C | 2,22 | 80,0 |
| 2 | Odin | 3,18 | Odin | 3,18 | 74,0 |
| 3 | C++ | 3,80 | C++ | 3,81 | 77,1 |
| 4 | Zig | 5,12 | Zig | 5,06 | 72,3 |
| 5 | C3 | 5,12 | C3 | 5,20 | 71,6 |
| 6 | Rust | 6,95 | Rust | 6,96 | 70,0 |
| 7 | Nim | 7,14 | Nim | 7,12 | 69,3 |
| 8 | D | 7,22 | D | 7,41 | 72,7 |
| 9 | Ada | 8,29 | Ada | 8,30 | 71,1 |
| 10 | Chapel | 9,22 | Chapel | 9,18 | 65,7 |
| 11 | Fortran | 10,80 | Swift | 10,69 | 66,5 |
| 12 | Swift | 11,01 | Fortran | 10,83 | 65,4 |
| 13 | Julia | 12,11 | Julia | 12,24 | 62,4 |
| 14 | Mojo | 13,02 | Mojo | 12,99 | 62,3 |
| 15 | C# | 15,11 | C# | 15,10 | 54,9 |
| 16 | Java | 16,40 | Java | 16,40 | 47,2 |
| 17 | Go | 16,50 | Go | 16,51 | 45,4 |
| 18 | Haskell | 17,82 | Haskell | 17,82 | 41,3 |
| 19 | OCaml | 19,02 | OCaml | 19,02 | 23,9 |
| 20 | JavaScript | 20,08 | JavaScript | 20,08 | 15,6 |
| 21 | Python | 21,31 | Python | 21,31 | 11,8 |
| 22 | Lua | 21,58 | Lua | 21,58 | 5,4 |
