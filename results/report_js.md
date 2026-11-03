# Remarque sur JavaScript : rapports appariés et scénarios

Plan : `docs/JAVASCRIPT.md`. Mesures : `results/raw_js/` (machine 21, 7 processus par cellule). Code :
`analysis/js_check.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal 0.0e+00).

## Rapports appariés (même hôte) : js_fix / js_ref

Clé corrigée (reportée) en gras ; les deux autres ont le même code dans les deux copies (contrôle).

| Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|
| **k7:tuned** | 1417,36 | 817,99 | **0,577** | 0,541–0,618 |
| k5:tuned | 137,48 | 133,24 | 0,969 | 0,916–1,015 |
| k9:tuned | 58,94 | 57,21 | 0,971 | 0,925–1,019 |

## Sensibilités (forme nouvelle / js_ref, même hôte)

| Sensibilité | Clé | Base (ms) | Forme nouvelle (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|
| q6_tuned_m | k6:tuned:q6 | 83,52 | 49,75 | 0,596 | 0,560–0,633 |
| q6_mt_m | k6:mt:q6 | 35,90 | 23,49 | 0,654 | 0,578–0,742 |
| k9_tuned_v | k9:tuned | 58,94 | 52,07 | 0,883 | 0,828–0,935 |
| k9_mt_v | k9:mt | 29,14 | 24,12 | 0,828 | 0,684–0,987 |
| k8_natural_s | k8:natural | 1084,99 | 669,78 | 0,617 | 0,558–0,714 |
| k8_tuned_it | k8:tuned | 424,61 | 308,69 | 0,727 | 0,701–0,751 |
| k5_tuned_f64 | k5:tuned | 137,48 | 121,40 | 0,883 | 0,839–0,920 |
| k1_soa_f64 | k1:soa:energy | 14,91 | 15,60 | 1,046 | 0,981–1,132 |

## Latences de K8 naturel (médianes de toutes les répétitions, µs) : natural_s / natural

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| natural (js_ref) | 40 | 63 | 200 | 721 | 81631 |
| natural_s (js_exp) | 36 | 47 | 99 | 352 | 1104 |
| rapport [IC 95 %] | 0,890 [0,86–0,92] | 0,749 [0,68–0,87] | 0,496 [0,47–0,57] | 0,488 [0,41–0,71] | 0,014 [0,01–0,02] |

## Information : Node.js 22.22.0 / Node.js 26.12.1 (même source, même hôte)

| Clé | Node 26 (ms) | Node 22 (ms) | Rapport | IC 95 % |
|---|---|---|---|---|
| k6:tuned:q1 | 269,88 | 111,74 | 0,414 | 0,406–0,422 |
| k6:natural:q1 | 263,50 | 131,23 | 0,498 | 0,481–0,522 |

## Pont par le C de clang (information : scénario J-E-P ; le classement publié reporte par transfert)

| Rapport | Clé | JavaScript publié | Transfert | Pont | Écart | Retenu | Facteur appliqué |
|---|---|---|---|---|---|---|---|
| pont k7:tuned | k7:tuned | 2715,78 ms | 1567,34 ms | 2026,58 ms | -22,7 % | transfert | 0,577 |

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de JavaScript | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |
|---|---|---|---|---|---|---|---|---|
| Avant | 14,3 | 11,6 | 11,4 | 22,7 | 19,07 | 19 | 19–20 | devant OCaml 0 %; derrière Python 93 % |
| J-code | 14,6 | 11,6 | 12,2 | 22,7 | 19,07 | 19 | 19–20 | devant OCaml 0 %; derrière Python 93 % |
| J-M | 15,3 | 14,6 | 11,4 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 0 %; derrière Python 95 % |
| J-E | 15,6 | 14,6 | 12,2 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 0 %; derrière Python 95 % |
| J-E-P | 15,6 | 14,6 | 12,2 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 0 %; derrière Python 95 % |
| S-Q6m | 15,8 | 14,6 | 12,5 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 1 %; derrière Python 96 % |
| S-K9v | 15,7 | 14,6 | 12,4 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 1 %; derrière Python 95 % |
| S-K8s | 17,3 | 14,6 | 12,2 | 29,3 | 19,00 | 19 | 19–19 | devant OCaml 4 %; derrière Python 96 % |
| S-K8it | 15,8 | 14,6 | 12,7 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 1 %; derrière Python 96 % |
| S-K5d | 15,7 | 14,6 | 12,4 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 0 %; derrière Python 95 % |
| S-K1d | 15,6 | 14,6 | 12,2 | 22,7 | 19,04 | 19 | 19–19 | devant OCaml 0 %; derrière Python 95 % |
| S-mesures | 17,8 | 14,6 | 13,5 | 29,3 | 18,99 | 19 | 19–19 | devant OCaml 4 %; derrière Python 97 % |
| S-cases | 18,4 | 22,5 | 12,2 | 22,7 | 18,96 | 19 | 18–19 | devant OCaml 5 %; derrière Python 99 % |
| S-tout | 20,6 | 22,5 | 13,5 | 29,3 | 18,84 | 19 | 18–19 | devant OCaml 16 %; derrière Python 99 % |

**Avant** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 23,9), 19. JavaScript (19,07, 14,3), 20. Python (20,30, 9,9), 21. Lua (20,63, 3,9).

**J-code** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,00, 23,9), 19. JavaScript (19,07, 14,6), 20. Python (20,30, 9,9), 21. Lua (20,63, 3,9).

**J-M** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,3), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**J-E** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,6), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**J-E-P** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,6), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**S-Q6m** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,8), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**S-K9v** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,7), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**S-K8s** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,04, 23,9), 19. JavaScript (19,00, 17,3), 20. Python (20,33, 9,9), 21. Lua (20,62, 3,9).

**S-K8it** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,8), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**S-K5d** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,7), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**S-K1d** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,01, 23,9), 19. JavaScript (19,04, 15,6), 20. Python (20,32, 9,9), 21. Lua (20,62, 3,9).

**S-mesures** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,04, 23,9), 19. JavaScript (18,99, 17,8), 20. Python (20,34, 9,9), 21. Lua (20,62, 3,9).

**S-cases** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,06, 23,9), 19. JavaScript (18,96, 18,4), 20. Python (20,36, 9,9), 21. Lua (20,62, 3,9).

**S-tout** : 15. Java (15,41, 47,2), 16. Go (15,52, 45,4), 17. Haskell (16,82, 41,3), 18. OCaml (18,17, 23,9), 19. JavaScript (18,84, 20,6), 20. Python (20,36, 9,9), 21. Lua (20,62, 3,9).

## Rapports reportés sur la réplication (machine 3)

k7:tuned 0,577.
