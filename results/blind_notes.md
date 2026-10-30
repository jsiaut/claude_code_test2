# Notes du second juge (aveugle) : cellules où j'ai hésité

Conventions adoptées :
- `rule_a` note ce que permet toute la chaîne livrée. `category` suit la lecture de la règle B (ce que fournit le standard seul), ce qui explique des cellules « standard_partiel » à rule_a = 1.
- Une bibliothèque tierce pure (rayon, crossbeam) ne figure pas dans la liste du 0,25 de la règle B : elle donne donc 0. Une FFI vers la libc donne 0,25.
- Les 60 sondes sont dans `probes/` (sources et binaires). Certaines devaient échouer pour prouver une absence.

## Incertitudes fortes

1. **odin / C4 (0,5 / 0,5).** L'attribut `@(fast_math={.Allow_Reassoc})` est documenté sur odin-lang.org (exemple `dot`). Mais le compilateur livré (dev-2026-10, commit 84bc3fc) ne pose jamais le drapeau `reassoc` : `llvm_backend_opt.cpp:63` fait `fast_math_flags & OdinFastMath_Allow_Reassoc`, avec une valeur d'énumération 0 utilisée comme masque. L'IR obtenu est `fadd nnan nsz contract`, et l'exemple `dot` de la documentation ne se vectorise pas (probes/odin/reassoc, dot). Un juge qui s'en tient à la documentation mettra 1 / 1. J'ai mis 0,5 parce que la capacité n'est pas fonctionnelle telle que livrée. Restent les réductions explicites `simd.reduce_add_pairs/bisect`.
2. **zig / C2 (0,5 / 0,25).** Zig n'a aucun module d'intrinsèques et `@cImport` a été supprimé en 0.17. Il reste l'assembleur en ligne, qui fonctionne (vaddps zmm), mais le langref déclare les chaînes de contraintes « still considered unstable ». `extern fn @"llvm.x86..."` marche aussi, sans être documenté ni utilisé par la std. Autres lectures possibles : 1 (l'asm donne accès à tout) ou 0 (pas d'intrinsèques).
3. **cpp / C1, règle B (0,5).** `std::simd` fait partie de C++26 et marche avec g++-16 en `-std=c++26`. Mais le manuel GCC 16 qualifie le support de C++26 de « highly experimental », `__cpp_lib_simd` n'est pas défini (seul `__glibcxx_simd`) et l'implémentation est conditionnée à `__SSE2__`, donc réservée à x86. J'hésitais entre 1 (c'est dans la norme), 0,5 et 0,25 (expérimental). Pour la règle A, les extensions vectorielles GCC donnent 1.
4. **cpp / C5, règle B (0,5).** Les algorithmes parallèles sont normatifs depuis C++17. Mais la libstdc++ livrée choisit le backend série faute de TBB, et `for_each(par)` tourne sur un seul thread (sonde). Une lecture « norme seule » donnerait 1. Pour la règle A, OpenMP (libgomp livrée) donne 1.
5. **Cellules « unité interne » : rust / D3, csharp / D3, nim / D3 (0,5 / 0,25).** J'ai appliqué la lettre de la règle A (« réservée à une unité interne non documentée » vaut 0,5) et de la règle B (« privé » vaut 0,25) :
   - Rust : `CachePadded` privé dans `std::sync::mpmc::utils`, l'import échoue en E0603 ;
   - .NET : `PaddingFor32`, `PaddedReference`, `CacheLineSeparated` internes à CoreLib ;
   - Nim : `const CacheLineSize = 64` non exportée dans `std/threadpool`, module déprécié.

   Un juge qui considère que l'utilisateur n'y a pas accès mettra 0 / 0. L'accès brut à CPUID (`__cpuid`, `X86Base.CpuId`, `intrinsics.x86_cpuid`) n'a pas été compté comme utilitaire de taille de ligne.

## Incertitudes moyennes

- **zig / C5, odin / C5, rust / C5 (0 / 0).** Aucune boucle ni réduction parallèle dans ces trois bibliothèques. Zig a `Io.Group` et `async` (std.Thread.Pool n'existe plus), Odin `thread.Pool`, Rust `thread::scope`. J'ai lu C5 strictement : un pool de tâches relève de D1. Une lecture « sous-ensemble » donnerait 0,5, mais alors aux trois langages à la fois.
- **nim / C5 (0,5 / 0,5).** L'itérateur `||` de system produit `#pragma omp parallel for`. En `-d:release`, la compilation échoue (« invalid branch to/from OpenMP structured block », variable `s` renommée `s_1`). Elle ne passe qu'avec `-d:danger`, une globale `exportc` et `-fopenmp` en passC/passL. La documentation prévient aussi que l'itérateur « isn't aware of the parallelism ».
- **odin / D3 (0,5 / 0,5).** `runtime.MAP_CACHE_LINE_SIZE` est public et commenté « The size of a cache-line », mais c'est un réglage des map, fixé à 64 quelle que soit la cible. J'hésitais entre 1 et 0,5.
- **csharp / D2 (0,5 / 0,5).** On a acquire (`Volatile.Read`), release (`Volatile.Write`) et des barrières complètes (`Interlocked`). Il n'y a ni relaxed explicite ni RMW relaxed, ni paramètre d'ordre. Certains mettront 1.
- **cpp / C4, règle B (1).** `std::reduce` et `std::transform_reduce` autorisent le regroupement, et libstdc++ les vectorise (vaddps/vfmadd ymm). En revanche, `execution::unseq` ne vectorise qu'avec `-fopenmp-simd`. On pourrait mettre 0,5 : la permission est donnée par l'algorithme, pas par un contrôle général du compilateur.
- **zig / C4 (1 / 1).** `@setFloatMode(.optimized)` est bien honoré : `@reduce` devient arborescent (vaddps ymm) alors qu'il reste séquentiel en `.strict`. Mais le pipeline de zig 0.17.0 n'auto-vectorise aucune boucle, même une somme d'entiers, alors que `opt-23 -O3` vectorise le même IR. Je l'ai traité comme un défaut général de l'optimiseur, pas comme une absence de contrôle.
- **d / C2, règle B (0,5).** L'assembleur en ligne normatif de D accepte SSE sous LDC (addps, mfence, prefetcht0) mais refuse `vaddps`. AVX-512 n'est accessible que par `ldc.gccbuiltins_x86`, que je classe comme intrinsèques du compilateur hors bibliothèque standard. Même raisonnement pour `ldc.attributes.fastmath` en d / C4 (0,25).
- **rust / E3 (1 / 1).** `std::hint::cold_path` et `#[cold]` sont stables en 1.99.1, mais `likely`/`unlikely` restent nightly. `cold_path` couvre l'usage ; 0,5 serait défendable.
- **rust / E4 et csharp / E4, règle B (1).** `_mm_prefetch` et `Sse.Prefetch0` sont propres à x86 mais font partie de la bibliothèque standard. Chez Rust, le prefetch portable `hint::prefetch_read` est nightly.
- **nim / C1 (0 / 0,25).** On peut obtenir un type `vector_size` en émettant du C (`{.emit.}`) et des fonctions d'appoint. J'ai compté cela comme FFI vers du code non intrinsèque : 0 en règle A, 0,25 en règle B (FFI). On pourrait aussi mettre 0 / 0.
- **nim / D5 (1 / 1).** `cpuRelax` vient de `std/sysatomics`, réexporté par system en 2.2.12 mais déprécié sous `-d:nimPreviewSlimSystem`.
- **c / D3 (1 / 0,25).** `__GCC_DESTRUCTIVE_SIZE` est défini en mode C par gcc-16 et clang-23 mais n'est pas documenté dans le manuel GCC. Le 1 de la règle A repose surtout sur `sysconf(_SC_LEVEL1_DCACHE_LINESIZE)` de la glibc.
- **csharp / D4 (1 / 1).** `Process.ProcessorAffinity` marche sous Linux mais concerne tout le processus ; l'affinité par thread est réservée à Windows. La capacité dit « un thread ou le processus », d'où 1. J'ai mis 2 en P12 pour la même raison.

## Principes

- **P5 : d = 4 et nim = 4.** Les deux diagnostiquent par défaut une partie des risques :
  - D : TLS par défaut, RMW sur `shared` rejeté, `spawn` refuse les alias mutables locaux (sondes dshared.d, dspawn.d) ;
  - Nim : effet gcsafe sur les procédures de thread (sonde ngcsafe.nim), gardes `{.guard.}`.

  La couverture reste partielle comparée à Rust, et 3 serait défendable.
- **P9 : csharp = 1.** Le langage n'offre aucune indication de branchement. J'ai crédité le PGO dynamique, actif par défaut mais réglé globalement par le runtime, comme « moyen non standard ou global ». 0 est possible.
- **P10 : csharp = 3, cpp = 2, c = 2.** J'ai pénalisé l'absence de prefetch normatif en C et C++, malgré un contrôle de disposition supérieur. Le C++ (constructive interference, pmr) pourrait monter à 3.
- **P8 : rust = 2, cpp = 2.** Pour Rust, les intrinsèques sont stables mais il manque un type portable stable. Pour C++, std::simd est expérimental dans la chaîne. Aucun langage n'a eu 4 : ni l'auto-vectorisation ni le choix d'ISA à l'exécution de .NET ne relèvent d'une règle « imposée ou diagnostiquée » du langage.
- **P4 : d = 3.** La taille de ligne n'est connue qu'à l'exécution (core.cpuid), et `align()` exige un littéral.
