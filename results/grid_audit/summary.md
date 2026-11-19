# Audit de la grille : état des sondes

Produit par `analysis/grid_audit.py`. Une case est « sondée » si une ligne CAP de `results/probes/<langage>.txt` la note ; la preuve est classée par ses étiquettes ([exécutée], [échec], [recherche]) ; « déclarative » : ligne sans étiquette (sonde antérieure à l'audit). Divergence : note de la sonde différente de la note de la matrice sous la règle v2 (score central).

| Langage | Sondées | Mesurées | Sans sonde | Déclaratives | Classes |
|---|---|---|---|---|---|
| c | 33 | 1 | 0 | 33 |  |
| cpp | 33 | 1 | 0 | 33 |  |
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
| mojo | 7 | 1 | 26 | 7 |  |
| csharp | 4 | 1 | 29 | 4 |  |
| java | 5 | 1 | 28 | 5 |  |
| julia | 33 | 1 | 0 | 0 | exécutée 28, exécutée+recherche 2, recherche 2, échec 1 |
| haskell | 3 | 1 | 30 | 3 |  |
| ocaml | 4 | 1 | 29 | 4 |  |
| js | 2 | 1 | 31 | 2 |  |
| python | 4 | 1 | 29 | 4 |  |
| lua | 2 | 1 | 31 | 2 |  |
| swift | 33 | 1 | 0 | 33 |  |
| fpc | 33 | 1 | 0 | 33 |  |
| bqn | 33 | 1 | 0 | 33 |  |
| php | 33 | 1 | 0 | 33 |  |

Total : 563 sondées, 25 mesurées, 262 sans sonde, 233 déclaratives.

## Divergences (sonde contre matrice v2)

| Langage | Case | Sonde | v1 | v2 | Preuve |
|---|---|---|---|---|---|
| c | C1 | 0.5 | 0.5 | 1 | types vectoriels portables par extension (vector_size) : 3 ; pas dans le standard C |
| c | C4 | 0.5 | 0.5 | 1 | réassociation : options -ffast-math/-fassociative-math, #pragma clang fp reassociate (extension) ; pas de contrôle standard |
| c | C5 | 0.5 | 0.5 | 1 | OpenMP, livré avec clang et gcc mais hors norme ISO C : parallel for simd reduction = 499500 |
| c | D3 | 0.5 | 0.5 | 1 | __GCC_DESTRUCTIVE_SIZE=64 (macro prédéfinie par clang et gcc), sysconf(_SC_LEVEL1_DCACHE_LINESIZE)=64 (glibc) ; pas de constante ISO |
| c | D4 | 0.5 | 0.5 | 1 | affinité via POSIX/Linux sched_setaffinity (pas dans le standard C) rc=0 |
| c | D5 | 0.5 | 0.5 | 1 | atomic_thread_fence standard ; pause via intrinsèque _mm_pause |
| c | E2 | 0.5 | 0.5 | 1 | assembleur en ligne par extension gcc/clang (__asm__) : 2 |
| c | E3 | 0.5 | 0.5 | 1 | __builtin_expect (extension) ; [[likely]] n'existe qu'en C++ |
| c | E4 | 0.5 | 0.5 | 1 | __builtin_prefetch (extension) ou _mm_prefetch (intrinsèque) |
| c | F4 | 0.5 | 0.5 | 1 | mmap POSIX (pas dans le standard C) puis réinterprétation par cast : 0.439005 |
| cpp | C5 | 0.5 | 0.5 | 1 | std::execution::par_unseq compile, mais libstdc++ l'exécute en série sans TBB, bibliothèque tierce (backend SERIAL) |
| cpp | D4 | 0.5 | 0.5 | 1 | pas d'affinité dans la bibliothèque standard ; sched_setaffinity de la libc, livrée avec la chaîne |
| cpp | D5 | 0.5 | 0.5 | 1 | std::atomic_thread_fence, std::barrier ; pause seulement par intrinsèque |
| cpp | E4 | 0.5 | 0.5 | 1 | __builtin_prefetch (extension) |
| cpp | E5 | 0.5 | 0.5 | 1 | __restrict__ (extension, pas dans la norme C++) |
| cpp | F4 | 0.5 | 0.5 | 1 | mmap POSIX + std::start_lifetime_as (C++23) : 0.439005 |
| go | D4 | 0.5 | 0.5 | 1 | syscall brut sched_setaffinity errno=0 |
| go | F4 | 0.5 | 0.5 | 1 | syscall.Mmap + unsafe.Slice : 0.4390046 <nil> |
| python | D4 | 0.5 | 0.5 | 1 | os.sched_setaffinity -> {0} |
| swift | D4 | 0.5 | 0.5 | 1 | sched_setaffinity du module Glibc livré avec swiftc -Xcc -D_GNU_SOURCE : fil épinglé sur le CPU 1, sched_getcpu() = 1 (sans l'option : cannot find 'sched_setaff |
| fpc | D4 | 0.5 | 0.5 | 1 | Do_SysCall(syscall_nr_sched_setaffinity) de l'unité Syscall livrée : retour 0, masque relu 2, processeur courant (/proc/self/stat) 1 ; pas d'API d'affinité (ni  |
| fpc | F4 | 0.5 | 0.5 | 1 | Fpmmap (unité BaseUnix livrée, appel système propre à Unix, comme syscall.Mmap de Go ; 1 en règle v2) + pointeur typé : premier mot 3904868352, dernier 62355461 |
| php | D4 | 0.5 | 0.5 | 1 | pcntl_setcpuaffinity (PHP 8.4, processus entier) : true → [0] (avant : [0,1,2,3]) |
