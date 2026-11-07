# Remarque sur PHP : rapports appariés et scénarios

Plan : `docs/PHP.md`, section 5. Mesures : `results/raw_php_rq/` (machine 29, Emerald Rapids, 7 processus par cellule). Code : `analysis/php_remark.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit P-E de `results/php_check.json` (écart maximal 0.0e+00).

## Rapports appariés (machine 29)

Moyennes géométriques des médianes de processus ; intervalles à 95 % par bootstrap. Chaque cellule est rapportée à la cellule du banc publié (`php`, PHP 8.5.12) : `natural` pour `natural_idx` et `natural_gcoff`, `natural_shuffled` pour leurs versions dans le désordre.

| Cellule | publié (ms) | cellule (ms) | rapport [IC à 95 %] |
|---|---|---|---|
| php_rq:k1:natural:energy | 507,9 | 510,5 | 1,005 [0,981–1,028] |
| php_rq:k1:natural_idx:energy | 507,9 | 147,5 | 0,290 [0,282–0,301] |
| php_rq:k1:natural_idx_shuffled:energy | 1196,3 | 387,4 | 0,324 [0,309–0,341] |
| php_rq:k1:natural_gcoff:energy | 507,9 | 128,1 | 0,252 [0,245–0,260] |
| php_rq:k1:natural_gcoff_shuffled:energy | 1196,3 | 277,9 | 0,232 [0,219–0,249] |
| php83:k9:natural | 912,5 | 266,8 | 0,292 [0,281–0,306] |
| php83:k9:tuned | 135,5 | 151,3 | 1,116 [1,089–1,147] |
| php84:k9:natural | 912,5 | 904,0 | 0,991 [0,959–1,023] |
| php84:k9:tuned | 135,5 | 133,9 | 0,988 [0,961–1,019] |
| php8513rc1:k9:natural | 912,5 | 882,5 | 0,967 [0,935–0,998] |
| php8513rc1:k9:tuned | 135,5 | 134,5 | 0,993 [0,962–1,028] |
| php86rc5:k9:natural | 912,5 | 908,0 | 0,995 [0,964–1,028] |
| php86rc5:k9:tuned | 135,5 | 131,8 | 0,973 [0,946–1,002] |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % | devant BQN | devant JavaScript | écart à BQN | plus grand écart de rang espéré des autres |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Avant | 16,56 | 27,4 | 4,50 | 20,7 | 22,32 | 22e | [20, 23] | 16 % | 43 % | 1,16 | — |
| R-K1idx | 16,54 | 27,4 | 4,50 | 20,6 | 22,32 | 22e | [20, 23] | 16 % | 43 % | 1,18 | JavaScript 0,00 |
| R-K1gc | 16,65 | 27,4 | 4,50 | 21,1 | 22,30 | 22e | [20, 23] | 17 % | 44 % | 1,07 | JavaScript 0,01 |
| R-K9-83 | 16,60 | 27,4 | 4,50 | 20,9 | 22,31 | 22e | [20, 23] | 17 % | 43 % | 1,12 | JavaScript 0,01 |
| R-tout | 16,69 | 27,4 | 4,50 | 21,3 | 22,28 | 22e | [20, 23] | 18 % | 45 % | 1,03 | JavaScript 0,02 |
| R-tout-idx | 16,58 | 27,4 | 4,50 | 20,8 | 22,30 | 22e | [20, 23] | 17 % | 44 % | 1,14 | JavaScript 0,01 |

Code par défaut de PHP par partie (D1 code naturel, D2 empreinte et désordre, D3 queues, D4 hiérarchie) : Avant D1 0,015, D2 0,293, D3 0,225, D4 0,610 ; R-K1idx D1 0,018, D2 0,278, D3 0,225, D4 0,610 ; R-K1gc D1 0,018, D2 0,306, D3 0,225, D4 0,610 ; R-K9-83 D1 0,018, D2 0,293, D3 0,225, D4 0,610 ; R-tout D1 0,022, D2 0,306, D3 0,225, D4 0,610 ; R-tout-idx D1 0,022, D2 0,278, D3 0,225, D4 0,610.
