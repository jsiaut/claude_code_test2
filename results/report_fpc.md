# Ajout de FreePascal : pont par le C et scénarios

Plan : `docs/FPC.md`. Mesures : `results/raw_fpc/` (machine 25, Emerald Rapids, 7 processus par cellule). Code :
`analysis/fpc_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant (FreePascal retiré) reproduit le classement publié d'avant (écart maximal 0.0e+00).

## FreePascal / C sur la machine 25 et pont vers les données publiées

Témoin de chaque clé : le C de la construction des données publiées (`c`, Cascade Lake ; `c_er` pour K5). Facteur gcc : second témoin (`c_gcc` publié / `c_gcc_cl` sur la machine 25).

| Cellule | FreePascal (ms) | C (ms) | FreePascal / C [IC 95 %] | C publié (ms) | facteur du pont | facteur gcc | FreePascal publié (ms) |
|---|---|---|---|---|---|---|---|
| k1:aos:energy | 30,540 | 25,670 | 1,190 [1,148–1,232] | 38,442 | 1,498 | 1,408 | 45,735 |
| k1:natural:energy | 36,697 | 33,713 | 1,089 [1,043–1,134] | 41,379 | 1,227 | 1,670 | 45,041 |
| k1:natural_shuffled:energy | 36,024 | 33,419 | 1,078 [1,044–1,112] | 39,342 | 1,177 | 1,362 | 42,409 |
| k1:soa:energy | 3,684 | 2,530 | 1,456 [1,393–1,512] | 7,756 | 3,066 | 2,998 | 11,294 |
| k10:natural | 1872,591 | 845,842 | 2,214 [2,143–2,287] | — | — | — | — |
| k10:tuned | 65,745 | 102,606 | 0,641 [0,583–0,704] | — | — | — | — |
| k2:tuned:16384 | 7,570 | 7,566 | 1,001 [0,988–1,016] | 6,808 | 0,900 | 0,871 | 6,812 |
| k2:tuned:262144 | 24,090 | 24,204 | 0,995 [0,975–1,012] | 18,280 | 0,755 | 0,772 | 18,194 |
| k2:tuned:8388608 | 156,072 | 159,731 | 0,977 [0,939–1,009] | 626,639 | 3,923 | 4,023 | 612,281 |
| k3:rmw_packed | 2918,210 | 2533,906 | 1,152 [1,129–1,174] | 2459,196 | 0,971 | 0,969 | 2832,169 |
| k3:rmw_padded | 338,350 | 222,497 | 1,521 [1,502–1,535] | 226,933 | 1,020 | 1,006 | 345,096 |
| k3:sw_packed | 16,259 | 13,641 | 1,192 [1,062–1,413] | 156,054 | 11,440 | 8,788 | 186,006 |
| k3:sw_padded | 15,942 | 12,967 | 1,229 [1,138–1,327] | 59,742 | 4,607 | 4,627 | 73,448 |
| k4:branchless_unsorted | 17,623 | 1,579 | 11,161 [10,797–11,541] | 2,841 | 1,799 | 1,293 | 31,711 |
| k4:natural_sorted | 19,082 | 1,574 | 12,126 [11,799–12,397] | 3,642 | 2,314 | 0,968 | 44,165 |
| k4:natural_unsorted | 94,164 | 1,731 | 54,395 [48,326–60,322] | 4,039 | 2,333 | 0,945 | 219,687 |
| k5:natural | 383,001 | 185,077 | 2,069 [2,054–2,086] | 158,106 | 0,854 | — | 327,188 |
| k5:tuned | 28,832 | 3,866 | 7,457 [6,646–7,984] | 3,936 | 1,018 | — | 29,351 |
| k6:mt:q1 | 18,784 | 6,783 | 2,769 [2,306–3,298] | 13,437 | 1,981 | 2,102 | 37,210 |
| k6:mt:q6 | 8,517 | 4,237 | 2,010 [1,725–2,330] | 8,539 | 2,015 | 2,134 | 17,164 |
| k6:natural:q1 | 73,355 | 56,012 | 1,310 [1,279–1,332] | 83,439 | 1,490 | 1,477 | 109,275 |
| k6:natural:q6 | 138,391 | 54,594 | 2,535 [2,509–2,561] | 64,002 | 1,172 | 1,142 | 162,238 |
| k6:tuned:q1 | 58,076 | 22,396 | 2,593 [2,479–2,717] | 32,109 | 1,434 | 1,462 | 83,263 |
| k6:tuned:q6 | 29,777 | 17,216 | 1,730 [1,626–1,807] | 21,350 | 1,240 | 1,289 | 36,927 |
| k7:natural | 4453,283 | 289,914 | 15,361 [14,397–16,540] | 5106,517 | 17,614 | 17,397 | 78439,806 |
| k7:tuned | 174,702 | 149,758 | 1,167 [1,091–1,245] | 456,848 | 3,051 | 3,462 | 532,942 |
| k8:natural | 1005,542 | 691,065 | 1,455 [1,431–1,483] | 973,350 | 1,408 | 1,820 | 1416,284 |
| k8:tuned | 328,677 | 280,497 | 1,172 [1,155–1,190] | 265,629 | 0,947 | 1,095 | 311,255 |
| k9:mt | 9,287 | 4,562 | 2,036 [1,764–2,273] | 4,734 | 1,038 | — | 9,637 |
| k9:natural | 32,816 | 13,620 | 2,409 [2,223–2,592] | 13,856 | 1,017 | — | 33,384 |
| k9:tuned | 24,843 | 14,438 | 1,721 [1,524–1,921] | 15,881 | 1,100 | — | 27,326 |

Facteur d'hôte unique de F-hôte (médiane des facteurs du C sur les clés de la machine 1) : 1,494.

K7 naturel (hors plan, F-K7tab) : facteur de la table chaînée du C 17,61, de sa table plate (K7 optimisé) 3,05. Temps publiés de K7 naturel (machine 1 ; FreePascal relié) : Zig 1,66 s ; Nim 2,10 s ; Odin 2,42 s ; Julia 3,27 s ; Chapel 3,52 s ; Rust 3,77 s ; Mojo 4,82 s ; C 5,11 s ; Fortran 5,19 s ; C# 5,65 s ; Go 5,79 s ; D 6,03 s ; C3 7,10 s ; Java 9,15 s ; C++ 10,64 s ; Ada 11,07 s ; Lua 11,33 s ; OCaml 12,42 s ; JavaScript 14,25 s ; Swift 16,09 s ; Python 28,26 s ; FreePascal 78,44 s ; Haskell 88,74 s.

Latences de K8 naturel (µs, médianes de toutes les répétitions) :

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| FreePascal, machine 25 | 58,4 | 71,2 | 91,6 | 132,0 | 732,0 |
| C, machine 25 | 39,8 | 45,5 | 67,4 | 108,9 | 673,6 |
| C publié | 31,7 | 41,9 | 65,7 | 116,2 | 1018,2 |
| FreePascal publié | 46,6 | 65,6 | 89,2 | 140,8 | 1106,5 |

Empreinte de K1 : 64,00 octets par particule ; C3 mesurée : 0,0.

## Sensibilités (rapports sur le même hôte, appliqués tels quels)

* sans `-Sv` (`fpc_scal` / `fpc`) : k1:soa:energy 1,428 [1,389–1,467] ; k5:tuned 1,723 [1,694–1,766].
* mode `RELEASE` du `fpc.cfg` (`fpc_o2` / `fpc`) : k1:natural:energy 0,974 [0,941–1,006] ; k1:natural_shuffled:energy 1,002 [0,980–1,027] ; k4:natural_unsorted 0,977 [0,952–1,006] ; k5:natural 1,003 [0,992–1,019] ; k6:natural:q6 0,981 [0,971–0,992] ; k6:natural:q1 1,005 [0,995–1,016] ; k7:natural 0,953 [0,872–1,030] ; k8:natural 1,023 [1,004–1,038] ; k9:natural 1,006 [0,948–1,065].
* K7 naturel, valeurs de classe (`natural_cls` / `natural`, fpc_exp) : 0,365 [0,341–0,391].
* K8 naturel, nœuds de classe : 2,157 [2,002–2,289] ; latences p50 2,30, p90 2,09, p99 1,98, p99,9 1,79, max 1,77.
* K9 naturel, `array of array of Double` : 0,917 [0,880–0,959].

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|---|
| F-E | 47,44 | 60,5 | 36,33 | 46,9 | 16,71 | 16e | [15, 19] |
| F-direct | 51,02 | 60,5 | 45,83 | 46,1 | 13,65 | 15e | [6, 16] |
| F-hôte | 47,29 | 60,5 | 39,43 | 41,4 | 15,92 | 16e | [14, 18] |
| F-gcc | 47,51 | 60,5 | 36,48 | 47,0 | 16,69 | 16e | [15, 19] |
| F-scal | 45,89 | 60,5 | 32,46 | 46,9 | 17,05 | 18e | [15, 19] |
| F-O2 | 47,45 | 60,5 | 36,33 | 47,0 | 16,71 | 16e | [15, 19] |
| F-K7cls | 47,54 | 60,5 | 36,33 | 47,3 | 16,65 | 16e | [15, 19] |
| F-K8cls | 46,30 | 60,5 | 36,33 | 42,4 | 16,83 | 16e | [15, 19] |
| F-K9dyn | 47,45 | 60,5 | 36,33 | 47,0 | 16,71 | 16e | [15, 19] |
| F-cases-bas | 45,96 | 56,3 | 36,33 | 46,9 | 16,98 | 17e | [15, 19] |
| F-cases-haut | 49,81 | 67,3 | 36,33 | 46,9 | 16,30 | 16e | [14, 19] |
| F-tout-bas | 43,28 | 56,3 | 32,46 | 42,4 | 17,41 | 18e | [15, 19] |
| F-tout-haut | 49,91 | 67,3 | 36,33 | 47,3 | 16,24 | 16e | [14, 19] |
| F-K7tab | 47,62 | 60,5 | 36,33 | 47,6 | 16,60 | 16e | [15, 19] |

Voisins dans F-E : devant C# (FreePascal devant dans 18 % des variantes) ; derrière Java (FreePascal devant dans 53 % des variantes).

## Classement : avant et avec FreePascal (F-E)

| Place | Avant | rang espéré | Avec FreePascal | rang espéré | écart du rang espéré |
|---|---|---|---|---|---|
| 1 | C | 2,22 | C | 2,22 | -0,00 |
| 2 | Odin | 3,18 | Odin | 3,19 | 0,00 |
| 3 | C++ | 3,81 | C++ | 3,81 | 0,00 |
| 4 | Zig | 5,06 | Zig | 5,06 | 0,00 |
| 5 | C3 | 5,20 | C3 | 5,20 | 0,00 |
| 6 | Rust | 6,96 | Rust | 6,96 | 0,00 |
| 7 | Nim | 7,12 | Nim | 7,12 | 0,00 |
| 8 | D | 7,41 | D | 7,43 | 0,01 |
| 9 | Ada | 8,30 | Ada | 8,30 | 0,00 |
| 10 | Chapel | 9,18 | Chapel | 9,19 | 0,01 |
| 11 | Swift | 10,69 | Swift | 10,70 | 0,02 |
| 12 | Fortran | 10,83 | Fortran | 10,84 | 0,01 |
| 13 | Julia | 12,24 | Julia | 12,26 | 0,02 |
| 14 | Mojo | 12,99 | Mojo | 13,01 | 0,02 |
| 15 | C# | 15,10 | C# | 15,28 | 0,18 |
| 16 | Java | 16,40 | FreePascal | 16,71 | — |
| 17 | Go | 16,51 | Java | 16,93 | 0,53 |
| 18 | Haskell | 17,82 | Go | 17,13 | 0,62 |
| 19 | OCaml | 19,02 | Haskell | 18,68 | 0,86 |
| 20 | JavaScript | 20,08 | OCaml | 20,02 | 1,00 |
| 21 | Python | 21,31 | JavaScript | 21,08 | 1,00 |
| 22 | Lua | 21,58 | Python | 22,31 | 1,00 |
| 23 | — | — | Lua | 22,58 | 1,00 |
