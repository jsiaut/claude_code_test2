# Faits vérifiés pendant l'étude

Chaque fait ci-dessous a été observé et reproduit sur cette machine, ou lu dans les sources
livrées avec la chaîne de compilation. Les chemins pointent vers le code concerné. Les temps
indiqués ici viennent de la mise au point ; les chiffres de référence sont ceux de la campagne
finale (`results/`).

## Matériel (VM Firecracker, Xeon Cascade Lake, 4 vCPU) — `tools/hwprobe.c`, `results/hw/`

| Mesure | Valeur | Méthode |
|---|---|---|
| Fréquence cœur effective (scalaire) | 3,1–3,3 GHz (TSC 2,8 GHz) | chaîne de 20 additions dépendantes déroulée |
| Débit FMA AVX-512 | 1,55 FMA/cycle TSC ≈ 2 FMA/cycle à ≈ 2,2 GHz | 8 chaînes indépendantes |
| Débit FMA AVX2 / scalaire | 1,98 / 2,34 FMA/cycle TSC ≈ 2,8 / 3,3 GHz | idem |
| Latence L1 / L2 / « L3 » / DRAM | 1,2 ns (4 cycles) / 4,3 ns / 22–38 ns / 140–445 ns | chasse de pointeurs, une ligne par nœud |
| Cache de dernier niveau réellement utilisable | ≈ 2–3 Mio (et non 33 Mio annoncés) | latence de DRAM dès 4 Mio, même avec pages géantes |
| Bande passante lecture 1 thread | L1 184 Go/s, L2 ≈ 120 Go/s, ≥ 16 Mio : 7–10 Go/s | somme AVX-512 |
| STREAM triad | 8,8 Go/s (1 thread), 43 Go/s (4 threads) | 3 × 128 Mo |
| Transfert de ligne entre cœurs | 120–210 ns | ping-pong atomique |
| Pénalité d'une mauvaise prédiction | ≈ 21 cycles TSC | tableau aléatoire contre trié |
| Faux partage (incréments simples, 4 threads) | 3,9 ns contre 1,8 ns par incrément | distance 8 o contre ≥ 64 o |
| Pages géantes (THP) | accès aléatoire sur 64 Mio : 52 ns au lieu de 141 ns | `madvise(MADV_HUGEPAGE)` |

Conséquence : sur cette machine, le code AVX-512 dense tourne à une fréquence inférieure d'environ
30 % à celle du code scalaire (licences de fréquence d'Intel). Les gains SIMD mesurés en tiennent
déjà compte.

Deux erreurs de ma propre sonde, corrigées et signalées : la première version de `freq` mesurait
le coût du branchement de boucle (2,07 GHz), et la première version de `bw` laissait le compilateur
fusionner les passes répétées (355 To/s).

## Pièges de compilateurs et de bibliothèques (exactitude)

* **GCC 16 (C et C++)** : un appel à une fonction `noinline` reconnue « pure », dont le résultat
  est écrasé à l'itération suivante, est supprimé. K5 C++ mesurait 10 µs au lieu de 4,8 ms. Corrigé
  par une barrière `asm volatile` sur le résultat (`bench/cpp/ms.cpp`, `bench/c/ms.c`). Clang ne le
  faisait pas sur ce code.
* **GHC 9.14.1** : le générateur natif (NCG) produit des résultats faux en SIMD 256/512 bits. Le
  backend LLVM (`-fllvm`) est correct (`bench/haskell`).
* **GHC** : sans `-fno-full-laziness` ni `NOINLINE`, le partage paresseux fait calculer K1, K4 et
  K9 une seule fois pour toutes les répétitions (temps ≈ 0).
* **LDC 1.43** : erreur interne du compilateur sur `storeUnaligned` appliqué à une expression,
  contournée par une variable temporaire (`bench/d/ms.d`).
* **D et Julia** : les délégués (D) et les fermetures (Julia) capturent les variables de boucle
  par référence. Une variante multi-thread donnait un résultat faux.
* **Julia** : l'ordonnanceur est coopératif, et une attente active sans `yield()` bloque le
  programme (processus tué après 12 min).
* **Zig 0.17** : `@bitCast` vers une `struct` « auto » est refusé, car les champs peuvent être
  réordonnés. Il faut une `extern struct` ou une construction champ par champ.
* **LuaJIT 2.1** : (1) la FFI ignore `volatile` : le compteur de K3 reste en registre
  (0,3 ns par incrément) ; (2) un pointeur obtenu par `ffi.cast` ne garde pas l'objet d'origine
  vivant : le GC a libéré le tableau et le parcours a provoqué un SIGSEGV
  (`bench/luajit/ms.lua`, K1 aos).
* **C3 0.8.5** : `sort::quicksort` de la bibliothèque standard met environ 260 s à trier
  16 M octets ne comptant que 256 valeurs distinctes : la partition dégénère face aux doublons.
* **Chapel 2.10** : `Time.stopwatch` repose sur `gettimeofday` (résolution d'une microseconde,
  horloge non monotone) : `runtime/src/chpl-timers.c`.

## Pièges de performance (capacité contre usage)

* **Désalignement AVX-512** (Rust K5) : chargements de 64 o à cheval sur deux lignes de cache,
  2,4 fois plus lents en L1. Corrigé par un tampon aligné sur 64 o.
* **Java Vector API** : un tableau de vecteurs coûte 12 fois plus cher que des vecteurs locaux
  (Q1 : 960 ms contre 78 ms). L'analyse d'échappement ne supprime pas les objets vecteurs stockés
  en mémoire.
* **OCaml Bigarray** : sans annotation statique du *kind*, chaque accès passe par une fonction
  générique. K1 soa passe de 204 à 10,6 ms, K5 de 1,87 à 0,14 s, K9 de 304 à 61 ms une fois les
  types annotés.
* **gfortran 16** : (1) la réduction `!$omp simd reduction` termine par 64 additions scalaires
  (`vaddss`) au lieu d'un arbre vectoriel : K5 7,1 ms contre 4,7 ms en C ; (2) la vectorisation de
  boucles mêlant entiers 8 et 32 bits choisit des registres de 128 bits (Q1 « une passe par
  groupe » : 216 ms contre 60 ms pour la version naturelle) ; (3) des arguments `(:)` sans
  l'attribut `contiguous` produisent un code générique à pas variable (Q1 : 338 contre 44 ms).
* **flang 23** ignore `-mprefer-vector-width` (avertissement « argument unused »).
* **Ada (GNAT 16)** : les vérifications actives par défaut coûtent un facteur 3 sur le stencil 2D
  (K9 : 129 contre 41 ms une fois supprimées localement). Un objet `Atomic` est écrit par un
  `xchg` séquentiellement cohérent. L'Ada standard n'offre pas d'ordre relâché.
* **Chapel 2.10** : (1) `chpl` ne transmet pas `-mprefer-vector-width` au code Chapel ; il faut
  passer `-Xclang -target-feature -Xclang -prefer-256-bit` (212 contre 1 493 instructions zmm) ;
  (2) les tuples ne sont vectorisés qu'en `<2 x float>` (IR LLVM optimisée) ; (3) sans
  `--no-ieee-float`, global, aucune réduction flottante n'est vectorisée (K5 : 25 ms contre 5 ms) ;
  (4) un formel tableau générique coûte un facteur 2 par rapport à un `c_ptr` (Q1 : 103–114 contre
  49–58 ms) ; (5) `+ reduce` sur 2 048 éléments crée des tâches à chaque appel : 60 fois plus lent
  qu'une boucle sérielle ; (6) les intents de réduction sont interdits dans `foreach`.
* **Go 1.27** : `atomic.Store` est compilé en `XCHG` (séquentiellement cohérent) ; il n'existe pas
  d'ordre relâché ni acquire/release.
* **K3** : un store `relaxed` répété sur la même adresse est absorbé par le tampon d'écriture.
  C'est la raison des quatre variantes rmw/sw × packed/padded de la spécification.

## État des langages au 2026-10-28 (vérifié dans les sources ou par compilation)

* **Go 1.27** : un paquet `simd` portable et `simd/archsimd` existent derrière
  `GOEXPERIMENT=simd` (`src/simd/doc.go`) ; `arena` existe derrière `GOEXPERIMENT=arenas`.
* **Rust** : `std::hint::cold_path` est stable depuis 1.95 ; les méthodes `f32::algebraic_*`
  (réassociation autorisée opération par opération) sont stables depuis 1.98 (août 2026).
  `likely`/`unlikely` et `std::simd` restent réservés à nightly.
* **Java 27** : les en-têtes d'objets compacts sont actifs par défaut. Les classes valeur
  (JEP 401) ne sont pas dans le JDK 27 ; elles sont annoncées en préversion pour le JDK 28.
* **C++26 / GCC 16** : `std::simd` (`<simd>`, `std::simd::vec`) est disponible ;
  `std::hardware_destructive_interference_size` vaut 64.
* **Mojo 1.2** : la bibliothèque `std` n'expose ni `parallelize` ni API publique de threads CPU ;
  elle expose les atomiques à ordres mémoire, `prefetch`, `likely`/`unlikely` et l'assembleur en
  ligne (`std/sys/intrinsics.mojo`, `std/sys/_assembly.mojo`).
* **Ada 2022 / GNAT 16** : les boucles et réductions parallèles sont décrites dans la norme, mais
  GNAT les déclare « Feature unimplemented » (`gnat_rm.info`). L'aspect `CPU` des tâches et
  `Dispatching_Domains` sont disponibles.
* **Zig 0.17** : `@fence` a été retiré du langage ; `std.atomic.cache_line` et
  `std.atomic.spinLoopHint` existent.
* **Node 26 / Bun 1.4** : `Atomics.pause` est disponible.
