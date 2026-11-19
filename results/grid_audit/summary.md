# Audit de la grille : état des sondes

Produit par `analysis/grid_audit.py`. Une case est « sondée » si une ligne CAP de `results/probes/<langage>.txt` la note ; la preuve est classée par ses étiquettes ([exécutée], [échec], [recherche]) ; « déclarative » : ligne sans étiquette (sonde antérieure à l'audit). Divergence : note de la sonde différente de la note de la matrice sous la règle v2 (score central).

| Langage | Sondées | Mesurées | Sans sonde | Déclaratives | Classes |
|---|---|---|---|---|---|
| c | 33 | 1 | 0 | 0 | exécutée 30, exécutée+échec 1, recherche 1, échec+recherche 1 |
| cpp | 33 | 1 | 0 | 0 | exécutée 31, recherche 1, échec+recherche 1 |
| rust | 33 | 1 | 0 | 0 | exécutée 23, exécutée+recherche 1, exécutée+échec 2, recherche 6, échec 1 |
| zig | 33 | 1 | 0 | 0 | exécutée 28, exécutée+recherche 1, exécutée+échec 2, recherche 2 |
| odin | 33 | 1 | 0 | 0 | exécutée 28, exécutée+échec 2, recherche 2, échec 1 |
| c3 | 33 | 1 | 0 | 0 | exécutée 23, exécutée+recherche 2, exécutée+échec 2, exécutée+échec+recherche 1, recherche 4, échec 1 |
| d | 33 | 1 | 0 | 0 | exécutée 29, exécutée+échec 1, exécutée+échec+recherche 1, recherche 2 |
| nim | 33 | 1 | 0 | 0 | exécutée 27, exécutée+échec 1, exécutée+échec+recherche 1, recherche 4 |
| ada | 33 | 1 | 0 | 0 | exécutée 28, exécutée+recherche 1, recherche 3, échec 1 |
| fortran | 33 | 1 | 0 | 0 | exécutée 21, exécutée+recherche 2, exécutée+échec 2, recherche 7, échec+recherche 1 |
| chapel | 33 | 1 | 0 | 0 | exécutée 26, recherche 7 |
| go | 33 | 1 | 0 | 0 | exécutée 18, exécutée+échec 3, exécutée+échec+recherche 1, recherche 4, échec 1, échec+recherche 6 |
| mojo | 33 | 1 | 0 | 0 | exécutée 24, exécutée+recherche 1, recherche 8 |
| csharp | 33 | 1 | 0 | 0 | exécutée 22, exécutée+recherche 1, exécutée+échec 2, recherche 4, échec 1, échec+recherche 3 |
| java | 33 | 1 | 0 | 0 | exécutée 14, exécutée+recherche 3, exécutée+échec 3, recherche 6, échec 3, échec+recherche 4 |
| julia | 33 | 1 | 0 | 0 | exécutée 28, exécutée+recherche 2, recherche 2, échec 1 |
| haskell | 33 | 1 | 0 | 0 | exécutée 19, exécutée+recherche 1, exécutée+échec 1, recherche 7, échec 2, échec+recherche 3 |
| ocaml | 33 | 1 | 0 | 0 | exécutée 10, exécutée+recherche 2, recherche 9, échec 3, échec+recherche 9 |
| js | 33 | 1 | 0 | 0 | exécutée 9, exécutée+recherche 1, recherche 14, échec 4, échec+recherche 5 |
| python | 33 | 1 | 0 | 0 | exécutée 16, recherche 12, échec 2, échec+recherche 3 |
| lua | 33 | 1 | 0 | 0 | exécutée 4, recherche 19, échec 3, échec+recherche 7 |
| swift | 33 | 1 | 0 | 0 | exécutée 26, exécutée+recherche 1, exécutée+échec 1, recherche 3, échec+recherche 2 |
| fpc | 33 | 1 | 0 | 0 | exécutée 26, recherche 4, échec 1, échec+recherche 2 |
| bqn | 33 | 1 | 0 | 0 | exécutée 10, recherche 17, échec 2, échec+recherche 4 |
| php | 33 | 1 | 0 | 0 | exécutée 16, recherche 13, échec+recherche 4 |

Total : 825 sondées, 25 mesurées, 0 sans sonde, 0 déclaratives.

## Divergences (sonde contre matrice v2)

| Langage | Case | Sonde | v1 | v2 | Preuve |
|---|---|---|---|---|---|
| haskell | A3 | 0.5 | 0 | 0 | [exécutée] struct __attribute__((packed)) {uint8_t; uint32_t} : taille 5, b à 1 (hsc2hs) ; instance Storable de 5 o : tableau de 1000 éléments à plat, élément 1 |
