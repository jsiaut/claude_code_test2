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
| go | 4 | 1 | 29 | 4 |  |
| mojo | 33 | 1 | 0 | 0 | exécutée 24, exécutée+recherche 1, recherche 8 |
| csharp | 4 | 1 | 29 | 4 |  |
| java | 5 | 1 | 28 | 5 |  |
| julia | 33 | 1 | 0 | 0 | exécutée 28, exécutée+recherche 2, recherche 2, échec 1 |
| haskell | 3 | 1 | 30 | 3 |  |
| ocaml | 4 | 1 | 29 | 4 |  |
| js | 2 | 1 | 31 | 2 |  |
| python | 4 | 1 | 29 | 4 |  |
| lua | 2 | 1 | 31 | 2 |  |
| swift | 33 | 1 | 0 | 0 | exécutée 26, exécutée+recherche 1, exécutée+échec 1, recherche 3, échec+recherche 2 |
| fpc | 33 | 1 | 0 | 0 | exécutée 26, recherche 4, échec 1, échec+recherche 2 |
| bqn | 33 | 1 | 0 | 33 |  |
| php | 33 | 1 | 0 | 33 |  |

Total : 589 sondées, 25 mesurées, 236 sans sonde, 94 déclaratives.

## Divergences (sonde contre matrice v2)

| Langage | Case | Sonde | v1 | v2 | Preuve |
|---|---|---|---|---|---|
| go | D4 | 0.5 | 0.5 | 1 | syscall brut sched_setaffinity errno=0 |
| go | F4 | 0.5 | 0.5 | 1 | syscall.Mmap + unsafe.Slice : 0.4390046 <nil> |
| python | D4 | 0.5 | 0.5 | 1 | os.sched_setaffinity -> {0} |
| php | D4 | 0.5 | 0.5 | 1 | pcntl_setcpuaffinity (PHP 8.4, processus entier) : true → [0] (avant : [0,1,2,3]) |
