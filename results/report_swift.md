# Ajout de Swift : pont par le C et scénarios

Plan : `docs/SWIFT.md`. Mesures : `results/raw_swift/` (machine 23, Cascade Lake, 7 processus par cellule). Code :
`analysis/swift_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant (Swift retiré) reproduit le classement publié d'avant (écart maximal 0.0e+00).

## Swift / C sur la machine 23 et pont vers les données publiées

| Cellule | Swift (ms) | C (ms) | Swift / C [IC 95 %] | C publié (ms) | facteur du pont | Swift publié (ms) |
|---|---|---|---|---|---|---|
| k1:aos:energy | 30,523 | 27,347 | 1,116 [1,057–1,177] | 38,442 | 1,406 | 42,908 |
| k1:natural:energy | 29,229 | 31,082 | 0,940 [0,866–1,016] | 41,379 | 1,331 | 38,913 |
| k1:natural_shuffled:energy | 31,252 | 28,555 | 1,094 [1,006–1,199] | 39,342 | 1,378 | 43,059 |
| k1:soa:energy | 5,236 | 5,531 | 0,947 [0,910–0,991] | 7,756 | 1,402 | 7,343 |
| k10:natural | 14151,360 | 888,384 | 15,929 [14,990–17,174] | — | — | — |
| k10:tuned | 29,689 | 34,104 | 0,871 [0,558–1,303] | — | — | — |
| k2:tuned:16384 | 6,775 | 6,630 | 1,022 [1,003–1,041] | 6,808 | 1,027 | 6,956 |
| k2:tuned:262144 | 20,402 | 19,413 | 1,051 [0,945–1,164] | 18,280 | 0,942 | 19,212 |
| k2:tuned:8388608 | 601,804 | 539,772 | 1,115 [1,016–1,224] | 626,639 | 1,161 | 698,654 |
| k3:rmw_packed | 2744,972 | 2666,585 | 1,029 [0,969–1,093] | 2459,196 | 0,922 | 2531,487 |
| k3:rmw_padded | 235,771 | 239,349 | 0,985 [0,934–1,027] | 226,933 | 0,948 | 223,540 |
| k3:sw_packed | 89,437 | 88,868 | 1,006 [0,982–1,035] | 156,054 | 1,756 | 157,054 |
| k3:sw_padded | 80,123 | 79,483 | 1,008 [0,996–1,021] | 59,742 | 0,752 | 60,222 |
| k4:branchless_unsorted | 2,779 | 2,376 | 1,170 [0,963–1,415] | 2,841 | 1,196 | 3,323 |
| k4:natural_sorted | 7,800 | 2,609 | 2,990 [2,528–3,637] | 3,642 | 1,396 | 10,888 |
| k4:natural_unsorted | 76,598 | 2,616 | 29,278 [24,190–35,624] | 4,039 | 1,544 | 118,248 |
| k5:natural | 165,094 | 164,614 | 1,003 [0,987–1,019] | 158,106 | 0,960 | 158,567 |
| k5:tuned | 6,688 | 6,266 | 1,067 [0,946–1,207] | 3,936 | 0,628 | 4,201 |
| k6:mt:q1 | 11,016 | 8,267 | 1,332 [1,205–1,492] | 13,437 | 1,625 | 17,904 |
| k6:mt:q6 | 4,439 | 5,092 | 0,872 [0,724–1,008] | 8,539 | 1,677 | 7,444 |
| k6:natural:q1 | 92,136 | 63,201 | 1,458 [1,262–1,688] | 83,439 | 1,320 | 121,642 |
| k6:natural:q6 | 55,887 | 51,391 | 1,087 [1,044–1,133] | 64,002 | 1,245 | 69,601 |
| k6:tuned:q1 | 36,020 | 24,565 | 1,466 [1,278–1,634] | 32,109 | 1,307 | 47,081 |
| k6:tuned:q6 | 13,594 | 14,551 | 0,934 [0,872–1,002] | 21,350 | 1,467 | 19,946 |
| k7:natural | 2114,525 | 671,196 | 3,150 [2,819–3,522] | 5106,517 | 7,608 | 16087,484 |
| k7:tuned | 306,204 | 268,271 | 1,141 [1,021–1,268] | 456,848 | 1,703 | 521,445 |
| k8:natural | 1869,737 | 771,760 | 2,423 [2,212–2,641] | 973,350 | 1,261 | 2358,128 |
| k8:tuned | 222,447 | 219,065 | 1,015 [0,942–1,081] | 265,629 | 1,213 | 269,730 |
| k9:mt | 9,697 | 8,694 | 1,115 [0,980–1,257] | 4,734 | 0,545 | 5,280 |
| k9:natural | 75,635 | 25,405 | 2,977 [2,784–3,197] | 13,856 | 0,545 | 41,251 |
| k9:tuned | 24,785 | 24,715 | 1,003 [0,959–1,055] | 15,881 | 0,643 | 15,925 |

Latences de K8 naturel (µs, médianes de toutes les répétitions) :

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| Swift, machine 23 | 101,3 | 164,2 | 242,4 | 371,6 | 1777,5 |
| C, machine 23 | 38,4 | 66,0 | 97,8 | 189,1 | 1560,8 |
| C publié | 31,7 | 41,9 | 65,7 | 116,2 | 1018,2 |
| Swift publié | 83,8 | 104,3 | 162,8 | 228,3 | 1159,6 |

Empreinte de K1 : 64,02 octets par particule ; C3 mesurée : 0,0.

## Sensibilités (même hôte)

* K8 naturel, `natural_fl` / `natural` (swift_exp) : 0,673 [0,614–0,744] ; latences p50 0,69, p90 0,70, p99 0,75, p99,9 0,86, max 0,82.
* `-Ounchecked` / `-O` (cellules naturelles) : k1:natural:energy 1,042 [0,956–1,136] ; k1:natural_shuffled:energy 1,007 [0,915–1,105] ; k4:natural_unsorted 0,172 [0,163–0,182] ; k5:natural 1,002 [0,988–1,018] ; k6:natural:q6 0,926 [0,882–0,976] ; k6:natural:q1 0,732 [0,614–0,874] ; k7:natural 0,980 [0,880–1,098] ; k8:natural 1,076 [1,023–1,143] ; k9:natural 0,832 [0,787–0,878].

## Hors plan : facteurs d'hôte (publié / machine 23) des langages mesurés avec leur code publié

Médianes par machine source (S-hôte) : machine 1 1,282 ; machine 16 1,126. Par clé : lua k1:soa:energy 1,36 (C 1,40) ; lua k2:tuned:16384 1,14 (C 1,03) ; lua k2:tuned:262144 1,15 (C 0,94) ; lua k2:tuned:8388608 1,19 (C 1,16) ; lua k3:rmw_packed 1,23 (C 0,92) ; lua k3:rmw_padded 1,40 (C 0,95) ; lua k3:sw_packed 1,24 (C 1,76) ; lua k3:sw_padded 1,48 (C 0,75) ; lua k4:branchless_unsorted 1,38 (C 1,20) ; lua k4:natural_sorted 1,27 (C 1,40) ; lua k4:natural_unsorted 1,27 (C 1,54) ; lua k6:mt:q6 1,32 (C 1,68) ; lua k6:natural:q6 1,26 (C 1,25) ; lua k6:tuned:q6 1,35 (C 1,47) ; lua k7:tuned 1,78 (C 1,70) ; lua k8:natural 1,28 (C 1,26) ; lua k8:tuned 1,10 (C 1,21) ; lua k9:mt 1,17 (C 0,54) ; lua k9:tuned 1,08 (C 0,64) ; luajit k8:natural 1,49 (C 1,26) ; python k8:natural 1,37 (C 1,26).

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|---|
| S-E | 65,24 | 64,4 | 79,38 | 43,8 | 11,01 | 12e | [6, 14] |
| S-direct | 67,63 | 64,4 | 83,84 | 46,2 | 6,94 | 6e | [1, 13] |
| S-K8fl | 65,65 | 64,4 | 79,38 | 45,5 | 11,02 | 12e | [6, 14] |
| S-Ou | 65,57 | 64,4 | 79,38 | 45,1 | 10,55 | 11e | [5, 14] |
| S-cases-bas | 62,85 | 57,6 | 79,38 | 43,8 | 12,04 | 13e | [7, 15] |
| S-cases-haut | 66,61 | 68,3 | 79,38 | 43,8 | 10,32 | 11e | [5, 14] |
| S-tout-bas | 62,85 | 57,6 | 79,38 | 43,8 | 12,04 | 13e | [7, 15] |
| S-tout-haut | 67,38 | 68,3 | 79,38 | 46,9 | 9,77 | 11e | [5, 13] |
| S-hôte | 60,77 | 64,4 | 69,85 | 41,2 | 12,25 | 13e | [8, 15] |

Voisins dans S-E : devant Fortran (Swift devant dans 48 % des variantes) ; derrière Julia (Swift devant dans 61 % des variantes).

## Classement : avant et avec Swift (S-E)

| Place | Avant | rang espéré | Avec Swift | rang espéré | écart du rang espéré |
|---|---|---|---|---|---|
| 1 | C | 2,21 | C | 2,20 | -0,00 |
| 2 | Odin | 3,16 | Odin | 3,18 | 0,02 |
| 3 | C++ | 3,76 | C++ | 3,80 | 0,04 |
| 4 | Zig | 4,93 | Zig | 5,12 | 0,19 |
| 5 | C3 | 5,14 | C3 | 5,12 | -0,02 |
| 6 | Rust | 6,82 | Rust | 6,95 | 0,13 |
| 7 | Nim | 6,92 | Nim | 7,14 | 0,22 |
| 8 | D | 7,24 | D | 7,22 | -0,02 |
| 9 | Ada | 8,06 | Ada | 8,29 | 0,23 |
| 10 | Chapel | 8,85 | Chapel | 9,22 | 0,37 |
| 11 | Fortran | 10,29 | Fortran | 10,80 | 0,50 |
| 12 | Julia | 11,57 | Swift | 11,01 | — |
| 13 | Mojo | 12,19 | Julia | 12,11 | 0,55 |
| 14 | C# | 14,13 | Mojo | 13,02 | 0,83 |
| 15 | Java | 15,41 | C# | 15,11 | 0,98 |
| 16 | Go | 15,52 | Java | 16,40 | 0,99 |
| 17 | Haskell | 16,82 | Go | 16,50 | 0,99 |
| 18 | OCaml | 18,02 | Haskell | 17,82 | 1,00 |
| 19 | JavaScript | 19,08 | OCaml | 19,02 | 1,00 |
| 20 | Python | 20,31 | JavaScript | 20,08 | 1,00 |
| 21 | Lua | 20,58 | Python | 21,31 | 1,00 |
| 22 | — | — | Lua | 21,58 | 1,00 |
