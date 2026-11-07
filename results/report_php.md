# Ajout de PHP : pont par le C et scénarios

Plan : `docs/PHP.md`. Mesures : `results/raw_php/` (machine 28, Emerald Rapids, 7 processus par cellule). Code :
`analysis/php_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant (PHP retiré) reproduit le classement publié d'avant (écart maximal 0.0e+00).

## PHP / C sur la machine 28 et pont vers les données publiées

Un seul binaire de PHP, face aux deux C : `c` (cible Cascade Lake, témoin des clés de la machine 1, de K9 et des latences) et `c_er` (natif, témoin de K5 et de la réplication). Facteur gcc : second témoin (`c_gcc` publié / `c_gcc_cl` sur la machine 28).

| Cellule | PHP (ms) | C (ms) | PHP / C [IC 95 %] | PHP / C natif | C publié (ms) | facteur du pont | facteur gcc | PHP publié (ms) |
|---|---|---|---|---|---|---|---|---|
| k1:aos:energy | 123,502 | 24,322 | 5,078 [4,838–5,360] | 4,923 [4,643–5,239] | 38,442 | 1,581 | 1,503 | 195,202 |
| k1:natural:energy | 515,899 | 30,060 | 17,162 [16,500–17,855] | 18,111 [17,642–18,634] | 41,379 | 1,377 | 1,817 | 710,153 |
| k1:natural_shuffled:energy | 1196,087 | 31,394 | 38,100 [34,877–40,704] | 40,663 [39,180–42,059] | 39,342 | 1,253 | 1,464 | 1498,933 |
| k1:soa:energy | 27,452 | 2,549 | 10,769 [9,884–11,534] | 10,916 [10,302–11,547] | 7,756 | 3,043 | 2,687 | 83,532 |
| k2:tuned:16384 | 25,108 | 7,638 | 3,287 [3,158–3,425] | 3,302 [3,187–3,444] | 6,808 | 0,891 | 0,860 | 22,379 |
| k2:tuned:262144 | 30,668 | 24,582 | 1,248 [1,210–1,280] | 1,248 [1,223–1,272] | 18,280 | 0,744 | 0,769 | 22,806 |
| k2:tuned:8388608 | 161,248 | 223,020 | 0,723 [0,440–1,027] | 0,697 [0,438–0,988] | 626,639 | 3,835 | 4,038 | 618,391 |
| k3:rmw_packed | 25344,590 | 2540,795 | 9,975 [9,769–10,177] | 9,960 [9,797–10,131] | 2459,196 | 0,968 | 0,954 | 24530,637 |
| k3:rmw_padded | 22490,420 | 232,595 | 96,693 [95,277–98,693] | 94,981 [91,597–98,256] | 226,933 | 0,976 | 0,968 | 21942,907 |
| k3:sw_packed | 14733,738 | 13,823 | 1065,884 [1008,625–1121,377] | 151,509 [146,455–156,644] | 156,054 | 11,289 | 6,180 | 166335,922 |
| k3:sw_padded | 5210,428 | 12,750 | 408,661 [392,257–425,576] | 59,349 [57,686–61,082] | 59,742 | 4,686 | 3,819 | 24414,046 |
| k4:branchless_unsorted | 56,213 | 1,701 | 33,051 [29,318–36,370] | 32,337 [29,323–35,597] | 2,841 | 1,671 | 1,271 | 93,904 |
| k4:natural_sorted | 60,266 | 1,678 | 35,914 [32,621–39,098] | 35,158 [32,243–38,332] | 3,642 | 2,170 | 0,948 | 130,799 |
| k4:natural_unsorted | 166,152 | 1,618 | 102,710 [97,371–107,525] | 93,363 [85,145–101,767] | 4,039 | 2,497 | 0,917 | 414,818 |
| k5:natural | 216,131 | 183,808 | 1,176 [1,165–1,189] | 1,166 [1,150–1,183] | 158,106 | 0,853 | — | 184,387 |
| k5:tuned | 202,243 | 4,036 | 50,108 [43,817–56,930] | 54,023 [48,708–60,351] | 3,936 | 1,051 | — | 212,623 |
| k6:mt:q1 | 85,872 | 6,865 | 12,509 [10,763–14,400] | 13,651 [11,792–15,641] | 13,437 | 1,957 | 1,754 | 168,074 |
| k6:mt:q6 | 41,280 | 4,764 | 8,665 [7,889–9,554] | 9,289 [7,968–10,864] | 8,539 | 1,793 | 2,008 | 73,997 |
| k6:natural:q1 | 341,566 | 56,429 | 6,053 [5,851–6,253] | 5,864 [5,509–6,146] | 83,439 | 1,479 | 1,469 | 505,063 |
| k6:natural:q6 | 208,958 | 54,840 | 3,810 [3,731–3,884] | 3,868 [3,791–3,939] | 64,002 | 1,167 | 1,182 | 243,866 |
| k6:tuned:q1 | 274,338 | 22,925 | 11,967 [10,927–12,694] | 11,954 [11,263–12,483] | 32,109 | 1,401 | 1,468 | 384,237 |
| k6:tuned:q6 | 154,878 | 16,253 | 9,529 [9,118–9,935] | 9,544 [9,066–10,036] | 21,350 | 1,314 | 1,346 | 203,441 |
| k7:natural | 4087,957 | 331,173 | 12,344 [11,308–13,421] | 13,119 [12,209–14,034] | 5106,517 | 15,419 | 15,352 | 63034,215 |
| k7:tuned | 1165,241 | 146,453 | 7,956 [7,381–8,493] | 7,932 [7,352–8,494] | 456,848 | 3,119 | 3,482 | 3634,871 |
| k8:natural | 4076,564 | 695,312 | 5,863 [5,742–5,991] | 5,952 [5,757–6,120] | 973,350 | 1,400 | 1,788 | 5706,682 |
| k8:tuned | 706,355 | 278,964 | 2,532 [2,483–2,591] | 2,535 [2,477–2,604] | 265,629 | 0,952 | 1,088 | 672,588 |
| k9:mt | 59,616 | 4,425 | 13,473 [11,616–15,354] | 13,389 [11,755–15,021] | 4,734 | 1,070 | — | 63,780 |
| k9:natural | 954,965 | 13,558 | 70,438 [56,650–80,625] | 74,322 [68,947–79,973] | 13,856 | 1,022 | — | 975,967 |
| k9:tuned | 141,377 | 13,832 | 10,221 [8,553–11,841] | 11,223 [10,753–11,673] | 15,881 | 1,148 | — | 162,319 |

Facteur d'hôte unique de P-hôte (médiane des facteurs du C sur les clés de la machine 1) : 1,530.

K2 à 8 Mio (hôte bimodal, écart au plan : docs/PHP.md 4.2) : médiane des médianes de processus du C 163,5 ms (moyenne géométrique 223,0 ms), de PHP 161,4 ms (moyenne géométrique 161,2 ms) ; facteur du pont 3,835 (plan : 2,810).

K7 naturel (P-K7tab, information) : facteur de la table chaînée du C 15,42, de sa table plate (K7 optimisé) 3,12. Temps publiés de K7 naturel (machine 1 ; PHP relié) : Zig 1,66 s ; Nim 2,10 s ; Odin 2,42 s ; Julia 3,27 s ; Chapel 3,52 s ; Rust 3,77 s ; Mojo 4,82 s ; C 5,11 s ; Fortran 5,19 s ; C# 5,65 s ; Go 5,79 s ; D 6,03 s ; C3 7,10 s ; Java 9,15 s ; C++ 10,64 s ; Ada 11,07 s ; Lua 11,33 s ; OCaml 12,42 s ; JavaScript 14,25 s ; Swift 16,09 s ; BQN 19,01 s ; Python 28,26 s ; PHP 63,03 s ; FreePascal 78,44 s ; Haskell 88,74 s.

Latences de K8 naturel (µs, médianes de toutes les répétitions) :

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| PHP, machine 28 | 230,6 | 274,7 | 425,0 | 835,7 | 2762,9 |
| C, machine 28 | 39,3 | 48,5 | 73,1 | 155,3 | 1324,8 |
| C publié | 31,7 | 41,9 | 65,7 | 116,2 | 1018,2 |
| PHP publié | 186,0 | 237,6 | 381,9 | 625,3 | 2123,5 |

Empreinte de K1 : 352,00 octets par particule (tas de Zend, octets vivants) ; RSS 345,11 (processus : 352,00, 352,00, 352,00). C3 mesurée : 0,0.

## Sensibilités (rapports sur le même hôte, appliqués tels quels)

* la CLI par défaut, sans OPcache ni JIT (`php_def` / `php`) : k1:natural:energy 1,232 [1,181–1,286] ; k1:natural_shuffled:energy 1,611 [1,541–1,688] ; k4:natural_unsorted 1,580 [1,542–1,618] ; k5:natural 8,891 [8,762–8,998] ; k6:natural:q6 3,215 [3,153–3,275] ; k6:natural:q1 4,235 [4,073–4,444] ; k7:natural 1,572 [1,505–1,643] ; k8:natural 1,506 [1,472–1,542] ; k9:natural 1,171 [1,131–1,209].
* K1 en tableaux associatifs : `natural_arr` / `natural` 1,917 [1,854–1,980] ; `natural_arr_shuffled` / `natural_shuffled` 2,530 [2,406–2,664].

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|---|
| P-E | 16,56 | 27,4 | 4,50 | 20,7 | 22,32 | 22e | [20, 23] |
| P-direct | 17,74 | 27,4 | 8,02 | 19,8 | 21,79 | 22e | [20, 23] |
| P-hôte | 16,10 | 27,4 | 5,83 | 16,8 | 22,30 | 22e | [20, 23] |
| P-gcc | 16,65 | 27,4 | 4,64 | 20,9 | 22,30 | 22e | [20, 23] |
| P-défaut | 16,29 | 27,4 | 4,42 | 19,8 | 22,39 | 23e | [20, 23] |
| P-K1arr | 16,40 | 27,4 | 4,50 | 20,1 | 22,35 | 23e | [20, 23] |
| P-C3 | 16,56 | 27,4 | 4,50 | 20,7 | 22,32 | 22e | [20, 23] |
| P-cases-bas | 11,91 | 14,1 | 4,50 | 20,7 | 22,98 | 23e | [22, 24] |
| P-cases-haut | 18,39 | 32,6 | 4,50 | 20,7 | 22,07 | 22e | [20, 23] |
| P-tout-bas | 11,51 | 14,1 | 4,42 | 19,2 | 23,03 | 23e | [22, 24] |
| P-tout-haut | 18,39 | 32,6 | 4,50 | 20,7 | 22,07 | 22e | [20, 23] |
| P-K7tab | 16,61 | 27,4 | 4,50 | 20,9 | 22,31 | 22e | [20, 23] |
| P-E-plan | 16,60 | 27,4 | 4,50 | 20,9 | 22,29 | 22e | [20, 23] |

Voisins dans P-E : devant BQN (PHP devant dans 16 % des variantes) ; derrière JavaScript (PHP devant dans 43 % des variantes).

Notes de E de PHP par noyau dans P-E (estimation ponctuelle) : k1 0,09 ; k3 0,00 ; k4 0,03 ; k5 0,02 ; k6 0,08 ; k7 0,13 ; k8 0,16 ; k9 0,07.

## Classement : avant et avec PHP (P-E)

| Place | Avant | rang espéré | Avec PHP | rang espéré | écart du rang espéré | écart du score |
|---|---|---|---|---|---|---|
| 1 | C | 2,22 | C | 2,20 | -0,02 | 0,00 |
| 2 | Odin | 3,19 | Odin | 3,17 | -0,02 | 0,00 |
| 3 | C++ | 3,81 | C++ | 3,79 | -0,02 | 0,00 |
| 4 | Zig | 5,06 | C3 | 5,11 | -0,09 | 0,00 |
| 5 | C3 | 5,20 | Zig | 5,14 | 0,08 | 0,00 |
| 6 | Rust | 6,96 | Rust | 6,97 | 0,00 | 0,00 |
| 7 | Nim | 7,12 | Nim | 7,16 | 0,05 | 0,00 |
| 8 | D | 7,43 | D | 7,19 | -0,24 | 0,00 |
| 9 | Ada | 8,30 | Ada | 8,30 | 0,01 | 0,00 |
| 10 | Chapel | 9,19 | Chapel | 9,29 | 0,10 | 0,00 |
| 11 | Swift | 10,70 | Fortran | 10,85 | 0,02 | 0,00 |
| 12 | Fortran | 10,84 | Swift | 10,86 | 0,16 | 0,00 |
| 13 | Julia | 12,26 | Julia | 12,15 | -0,11 | 0,00 |
| 14 | Mojo | 13,01 | Mojo | 13,08 | 0,07 | 0,00 |
| 15 | C# | 15,29 | C# | 15,30 | 0,01 | 0,00 |
| 16 | FreePascal | 16,66 | FreePascal | 16,73 | 0,07 | 0,00 |
| 17 | Java | 16,95 | Java | 16,93 | -0,02 | 0,00 |
| 18 | Go | 17,15 | Go | 17,12 | -0,03 | 0,00 |
| 19 | Haskell | 18,69 | Haskell | 18,68 | -0,01 | 0,00 |
| 20 | OCaml | 20,23 | OCaml | 20,31 | 0,08 | 0,00 |
| 21 | BQN | 20,96 | BQN | 21,17 | 0,21 | 0,00 |
| 22 | JavaScript | 21,93 | PHP | 22,32 | — | — |
| 23 | Python | 23,28 | JavaScript | 22,34 | 0,42 | 0,00 |
| 24 | Lua | 23,58 | Python | 24,26 | 0,98 | 0,00 |
| 25 | — | — | Lua | 24,58 | 1,00 | 0,00 |
