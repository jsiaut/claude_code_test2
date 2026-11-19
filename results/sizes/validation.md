# v4, point 2 : validation des sommes de contrôle aux trois tailles (avant la campagne)

*`tools/sizes/validate.py`, un processus par cellule, une répétition, contre `results/sizes/expected.json` (implémentation C) ; variantes propres comprises. Dernière validation de chaque cellule (Ada : `tuned_alloc` revalidée après la correction de `P_Build` ; Mojo : revalidé après le répertoire de données fixé à la compilation) ; journal complet : `results/sizes/validation.log`.*

| Langage | Cellules | OK | Hors mémoire | Autres échecs |
|---|---|---|---|---|
| ada | 69 | 69 | 0 | 0 |
| bqn | 78 | 72 | 6 | 0 |
| c | 66 | 66 | 0 | 0 |
| c3 | 69 | 69 | 0 | 0 |
| chapel | 66 | 66 | 0 | 0 |
| cpp | 69 | 69 | 0 | 0 |
| csharp | 66 | 66 | 0 | 0 |
| d | 66 | 66 | 0 | 0 |
| fortran | 66 | 66 | 0 | 0 |
| fpc | 66 | 66 | 0 | 0 |
| go | 66 | 66 | 0 | 0 |
| haskell | 66 | 66 | 0 | 0 |
| java | 66 | 66 | 0 | 0 |
| js | 66 | 66 | 0 | 0 |
| julia | 66 | 66 | 0 | 0 |
| lua | 66 | 66 | 0 | 0 |
| mojo | 66 | 66 | 0 | 0 |
| nim | 66 | 66 | 0 | 0 |
| ocaml | 66 | 66 | 0 | 0 |
| odin | 69 | 69 | 0 | 0 |
| php | 72 | 69 | 3 | 0 |
| python | 66 | 64 | 2 | 0 |
| rust | 66 | 66 | 0 | 0 |
| swift | 66 | 66 | 0 | 0 |
| zig | 69 | 69 | 0 | 0 |
| **total** | 1683 | 1672 | 11 | 0 |

## Cellules hors mémoire (limite du groupe de processus, 13,35 Gio ; section 6 du plan)

* bqn : k1:large natural
* bqn : k1:large aos
* bqn : k1:large soa
* bqn : k1:large natural_shuffled
* bqn : k1:large natural_ns
* bqn : k1:large natural_ns_shuffled
* php : k1:large natural_arr
* php : k1:large natural_arr_shuffled
* php : k4:large natural_sorted
* python : k1:large natural
* python : k1:large natural_shuffled

## Sommes de contrôle au-delà de 2^53 acceptées à l'arrondi d'un double près (`docs/V4_SIZES.md`, 4.1)

* bqn : k6:large:q1 natural
* bqn : k6:large:q1 mt
* js : k6:large:q1 natural
* js : k6:large:q1 tuned
