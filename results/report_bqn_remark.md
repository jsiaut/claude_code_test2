# Remarque sur BQN : errata, formes en blocs et scénarios

Plan : `docs/BQN.md`, section 5. Mesures : `results/raw_bqn_rq/` (machine 27, Emerald Rapids, 7 processus par cellule). Code : `analysis/bqn_remark.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant (grille et données d'avant la remarque) reproduit B-E de `results/bqn_check.json` (écart maximal 0.0e+00).

## Rapports appariés (machine 27)

Moyennes géométriques des médianes de processus ; intervalles à 95 % par bootstrap. Cible Cascade Lake : `bqn_rq` / `bqn` (classement) ; native : `bqn_er_rq` / `bqn_er` (réplication). `tuned_flat` et `mt_flat` (somme de contrôle hors chrono, sans blocs) sont rapportés à `tuned` et `mt` publiés.

| Cellule | publié (ms) | copie (ms) | rapport, cible Cascade Lake | rapport, natif |
|---|---|---|---|---|
| k1:aos:energy | 127,279 | 65,576 | 0,515 [0,492–0,540] | 0,496 [0,475–0,514] |
| k1:natural:energy | 128,508 | 130,466 | 1,015 [0,990–1,042] | 0,982 [0,948–1,019] |
| k1:soa:energy | 35,155 | 16,179 | 0,460 [0,377–0,541] | 0,481 [0,426–0,534] |
| k4:branchless_unsorted | 7,726 | 2,868 | 0,371 [0,308–0,448] | 0,388 [0,353–0,422] |
| k5:tuned | 32,410 | 32,007 | 0,988 [0,960–1,016] | 0,986 [0,969–1,006] |
| k6:mt:q1 | 162,539 | 83,133 | 0,511 [0,465–0,553] | 0,498 [0,467–0,526] |
| k6:mt:q6 | 21,002 | 17,979 | 0,856 [0,820–0,894] | 0,820 [0,783–0,859] |
| k6:tuned:q1 | 238,380 | 83,419 | 0,350 [0,335–0,364] | 0,344 [0,335–0,352] |
| k6:tuned:q6 | 22,595 | 17,826 | 0,789 [0,732–0,849] | 0,833 [0,743–0,938] |
| k7:natural | 8683,366 | 1155,620 | 0,133 [0,127–0,140] | 0,132 [0,122–0,147] |
| k9:mt | 88,352 | 52,429 | 0,593 [0,547–0,644] | 0,611 [0,563–0,688] |
| k9:mt_flat | 88,352 | 86,954 | 0,984 [0,919–1,037] | 1,017 [0,973–1,067] |
| k9:natural | 268,210 | 252,225 | 0,940 [0,846–1,036] | 1,001 [0,940–1,078] |
| k9:tuned | 87,142 | 56,646 | 0,650 [0,613–0,692] | 0,590 [0,558–0,626] |
| k9:tuned_flat | 87,142 | 87,406 | 1,003 [0,946–1,077] | 0,964 [0,907–1,031] |

Témoins inchangés (rapport attendu 1) : k1:natural:energy 1,015 [0,990–1,042] ; k5:tuned 0,988 [0,960–1,016].

Rapports des errata (classement) : k9:natural 0,940 ; k9:tuned 1,003 ; k9:mt 0,984 ; k7:natural 0,133. Rapports de R-blocs : k9:natural 0,940 ; k9:tuned 0,650 ; k9:mt 0,593 ; k7:natural 0,133 ; k1:aos:energy 0,515 ; k1:soa:energy 0,460 ; k4:branchless_unsorted 0,371 ; k6:tuned:q6 0,789 ; k6:tuned:q1 0,350 ; k6:mt:q6 0,856 ; k6:mt:q1 0,511.

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % | devant OCaml | devant JavaScript |
|---|---|---|---|---|---|---|---|---|---|
| Avant | 18,65 | 22,8 | 12,45 | 22,7 | 20,89 | 21e | [20, 22] | 25 % | 87 % |
| R-grille | 17,55 | 19,7 | 12,45 | 22,7 | 21,01 | 21e | [20, 22] | 19 % | 82 % |
| R-K9 | 18,66 | 22,8 | 12,46 | 22,7 | 20,88 | 21e | [20, 22] | 25 % | 87 % |
| R-K7 | 18,81 | 22,8 | 12,45 | 23,3 | 20,84 | 21e | [20, 22] | 27 % | 89 % |
| R-E | 17,72 | 19,7 | 12,46 | 23,3 | 20,96 | 21e | [20, 22] | 21 % | 84 % |
| R-blocs | 19,72 | 19,7 | 17,45 | 23,3 | 20,69 | 21e | [20, 22] | 38 % | 94 % |
| R-C5 | 18,60 | 22,2 | 12,46 | 23,3 | 20,88 | 21e | [20, 22] | 26 % | 88 % |
| R-blocs-C5 | 20,59 | 22,2 | 17,45 | 23,3 | 20,61 | 21e | [20, 22] | 43 % | 96 % |
| R-K7map | 17,56 | 19,7 | 12,46 | 22,7 | 21,01 | 21e | [20, 22] | 19 % | 82 % |
| R-K7tab | 17,89 | 19,7 | 12,46 | 24,0 | 20,92 | 21e | [20, 22] | 23 % | 86 % |

Plafond de BQN par noyau (estimation ponctuelle) : R-E k1 0,08 ; k3 0,02 ; k4 0,23 ; k5 0,12 ; k6 0,15 ; k7 0,20 ; k8 0,61 ; k9 0,07 ; R-blocs k1 0,16 ; k3 0,02 ; k4 0,58 ; k5 0,12 ; k6 0,25 ; k7 0,20 ; k8 0,61 ; k9 0,11.

## Classement : avant et après la remarque (R-E)

| Place | Avant | rang espéré | R-E | rang espéré | écart du rang espéré | écart du score |
|---|---|---|---|---|---|---|
| 1 | C | 2,22 | C | 2,22 | 0,00 | 0,00 |
| 2 | Odin | 3,19 | Odin | 3,19 | 0,00 | 0,00 |
| 3 | C++ | 3,81 | C++ | 3,81 | 0,00 | 0,00 |
| 4 | Zig | 5,06 | Zig | 5,06 | 0,00 | 0,00 |
| 5 | C3 | 5,20 | C3 | 5,20 | 0,00 | 0,00 |
| 6 | Rust | 6,96 | Rust | 6,96 | 0,00 | 0,00 |
| 7 | Nim | 7,12 | Nim | 7,12 | 0,00 | 0,00 |
| 8 | D | 7,43 | D | 7,43 | -0,00 | 0,00 |
| 9 | Ada | 8,30 | Ada | 8,30 | 0,00 | 0,00 |
| 10 | Chapel | 9,19 | Chapel | 9,19 | 0,00 | 0,00 |
| 11 | Swift | 10,70 | Swift | 10,70 | 0,00 | 0,00 |
| 12 | Fortran | 10,84 | Fortran | 10,84 | 0,00 | 0,00 |
| 13 | Julia | 12,26 | Julia | 12,26 | 0,00 | 0,00 |
| 14 | Mojo | 13,01 | Mojo | 13,01 | 0,00 | 0,00 |
| 15 | C# | 15,29 | C# | 15,29 | 0,00 | 0,00 |
| 16 | FreePascal | 16,66 | FreePascal | 16,66 | 0,00 | 0,00 |
| 17 | Java | 16,95 | Java | 16,95 | 0,00 | 0,00 |
| 18 | Go | 17,15 | Go | 17,15 | 0,00 | 0,00 |
| 19 | Haskell | 18,69 | Haskell | 18,69 | 0,00 | 0,00 |
| 20 | OCaml | 20,27 | OCaml | 20,23 | -0,04 | 0,00 |
| 21 | BQN | 20,89 | BQN | 20,96 | — | — |
| 22 | JavaScript | 21,95 | JavaScript | 21,93 | -0,03 | 0,00 |
| 23 | Python | 23,29 | Python | 23,28 | -0,01 | 0,00 |
| 24 | Lua | 23,58 | Lua | 23,58 | 0,00 | 0,00 |
