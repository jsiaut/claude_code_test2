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
* **Java 27** : les en-têtes d'objets compacts sont actifs par défaut (`UseCompactObjectHeaders =
  true`, vérifié par `-XX:+PrintFlagsFinal`). Les classes valeur (JEP 401) ne sont pas dans le
  JDK 27 ; la page de JEP 401 les indique « Integrated », en préversion, pour le JDK 28.
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

## Faits établis après le redémarrage de la VM (mesures indépendantes de la vitesse, et outils)

* **Empreinte par pic RSS : un piège de mesure.** La plupart des chargements lisent le fichier
  dans un tampon, puis le copient dans un tampon aligné : le pic RSS (512 Mio) est atteint pendant
  le chargement, et la collection construite ensuite (256 Mio) ne le dépasse pas. Huit langages
  « mesuraient » 0 octet par particule. Corrigé par une mesure en deux points dans le processus
  (`tools/patch_footprint_mem.py`).
* **`/proc/self/statm` annonce une taille nulle** : la lecture « fichier entier » de Zig
  (`readFileAlloc`), Nim (`readFile`) et D (`readText`) rend une chaîne vide. Il faut lire en flux.
* **Les allocateurs gardent la mémoire libérée.** Nim (allocateur TLSF) réutilise le tampon de
  chargement libéré, et arrondit une demande de 256 Mio à sa classe de taille (264 Mio) ; le runtime
  de Mojo (zones réservées de 1 Gio, libération par `madvise`) réutilise environ 24 Mo du tampon
  libéré (vu avec `strace`) ; les tas de Java et de C# réutilisent eux aussi la mémoire libérée (RSS
  de 37 et 26 o par particule pour 78 et 88 o vivants). Seule la comptabilité du runtime, après un
  GC complet, donne la taille réelle d'une collection dans ces langages.
* **Taille d'une particule de 64 o selon le langage** (octets vivants par élément de la
  collection naturelle) : 64 pour les tableaux de valeurs (C, C++, Rust, Zig, Odin, C3, D, Nim,
  Mojo, Chapel, Fortran, Ada, Go, Julia) ; Java 78 (en-tête compact de 8 o + 4 o de référence +
  marge de capacité de l'`ArrayList`) ; C# 88 (en-tête de 16 o + référence de 8 o) ; Haskell 96
  (constructeur à champs `Float` stricts empaquetés, 72 o, plus une cellule de liste de 24 o) ;
  OCaml 144 (un enregistrement de flottants est stocké à plat, mais chaque `float` y occupe 8 o :
  pas de flottant 32 bits non boxé) ; Bun 170 (JavaScriptCore range les nombres dans les mots de
  64 bits de l'objet) ; Node 416 (V8, avec la compression de pointeurs, range chaque propriété
  flottante dans un objet `HeapNumber` séparé) ; LuaJIT 428 et Lua 449 (table à 16 champs nommés) ;
  Python 750 (dont 608 o demandés selon `tracemalloc`, le reste en arrondis de pymalloc).
* **Valhalla (JEP 401, build EA `27-jep401ea3`)** : un tableau de `value record` de 16 `float` n'est
  pas aplati (85,8 o par élément ; parcours permuté 4,1 fois plus lent, comme pour des objets
  ordinaires). La JVM n'aplatit un tableau que si la valeur et son marqueur de nullité tiennent
  dans un accès atomique de 64 bits : un `value record` d'un `float` est aplati
  (`NULLABLE_ATOMIC_FLAT`, 8 o par élément, `-XX:+PrintFlatArrayLayout`), un de deux `float` ne
  l'est plus (36 o). Le texte de JEP 401 l'annonce (« this limits the size of mutable fields that
  store flattened references to no more than 64 bits »). JEP 401 est intégré au JDK 28, en
  préversion (`bench/java_valhalla/`).
* **Bun applique `BUN_OPTIONS`** (vérifié par `process.execArgv`). L'outil qui lance les commandes
  exporte `BUN_OPTIONS=--smol` ; effet mesuré sur l'annexe Bun : K1 natural 97 contre 98 ms, K8
  natural 837 contre 811 ms, pic RSS de l'empreinte −1 %. Négligeable.
* **K10 `tuned` est bistable** pour toutes les implémentations natives : file pleine (le
  consommateur lit par rafales, 6 à 10 ms pour 4 M messages) ou file presque vide (une ligne de
  cache échangée par message, jusqu'à 200 ms). Le régime change d'une répétition à l'autre dans le
  même processus.
* **K5 `tuned` : états de performance par processus.** Deux processus du même binaire diffèrent de
  30 à 60 % (Zig : 5,6 ms dans l'un, 8,2 ms dans l'autre), mais chaque processus est stable : un
  état de l'environnement de la VM (hôte partagé), pas du code.
* **objdump affiche comme données le code de GHC** : les tables d'info sont des symboles de type
  objet placés dans `.text`. Il faut désassembler les octets bruts.
* **Vectorisation du code naturel (mesurée sur la boucle chaude)** : Zig ne vectorise ni K4
  (code sans branchement scalaire, déroulé par 8) ni K9 (scalaire déroulé par 3 ; les deux
  tableaux, passés par pointeur, peuvent s'aliaser) ; Rust, D, Nim et Ada ne vectorisent pas le
  stencil naturel, à cause des vérifications de bornes de leurs tableaux de tableaux ; gfortran ne
  vectorise pas K4 (somme d'octets dans un accumulateur 64 bits) alors que flang le fait ; le JIT de
  .NET n'a pas de vectoriseur automatique ; C2 (Java) vectorise K9 en 128 bits mais pas K4.

## Machine 3 (Xeon Emerald Rapids, depuis le 29 octobre) — `results/hw/machine3/`

* **Caractérisation.** TSC à 2,1 GHz ; fréquence effective scalaire de 3,1 à 3,5 GHz ; débit FMA
  AVX-512 f32 de 164, 182 et 232 Gflop/s sur trois mesures à quelques minutes d'écart. Latences :
  L1 1,2 à 1,6 ns ; L2 5 à 5,6 ns jusqu'à 1 Mio, 40 ns à 2 Mio ; L3 56 à 71 ns de 4 à 16 Mio ; puis
  100 à 275 ns. Lecture sur un thread : 138 à 143 Go/s dans le L2, 22 à 28 Go/s de 4 à 64 Mio,
  11,9 Go/s sur 1 Gio. Transfert d'une ligne entre deux vCPU : 99 à 200 ns selon la paire. Le L3
  (260 Mio, partagé) loge une partie des tableaux de 64 à 256 Mio que la machine 1 servait depuis
  la DRAM.
* **Le cœur replie les additions d'immédiats au renommage.** Une chaîne dépendante de
  `add $1, reg` s'exécute à 11 à 22 additions par ns : la sonde de fréquence de la machine 1, qui
  reposait sur elle, affichait 14 à 18 GHz. Une chaîne `add reg, reg` ou `imul` donne 3,1 à
  3,9 GHz. Un micro-benchmark écrit pour une génération de cœur ne mesure plus la même chose sur
  la suivante.
* **Latences de la machine 3 : addition flottante 2 cycles, FMA 4.** Chaîne dépendante de `vaddss` contre
  `vfmadd231ss`, fréquence mesurée par une chaîne d'`imul` : 2,0 cycles contre 3,9 à 4,0 en médiane
  (`tools/addfma.c`, `results/hw/machine3/addfma.txt`). Sur Cascade Lake, les deux valent 4 cycles. C'est ce qui
  sépare les deux familles du K5 naturel (fait suivant).
* **K3 sur la machine 3 : l'alignement du code décide d'un facteur 7.** La même boucle de 16 `incq` en mémoire,
  celle que clang, rustc et Odin produisent pour l'écrivain unique, prend environ 10 ms pour 2²⁵ incréments, soit
  un cycle chacun, à certains décalages dans sa ligne de 64 octets : 8, et 36 à 48. Elle prend 56 à 77 ms, soit
  sept cycles, aux autres décalages (`tools/k3_align.c`, `results/hw/machine3/k3_align.txt`). Dans la réplication,
  la boucle de Rust (décalage 48) tourne en 13 ms, celles de C/clang (16) et d'Odin (32) en 76 et 79 ms, octet
  pour octet identiques. Le code de GCC (`mov`, `inc`, `mov`, sans déroulage) prend 11 à 19 ms aux 16 mêmes décalages (`tools/k3_align_mov.c`). Le
  mécanisme probable est un raccourci matériel de la dépendance écriture-lecture, qui ne s'applique que selon le
  placement du code ; sans compteurs matériels, je ne peux pas le confirmer. Sur Cascade Lake, tous les langages
  étaient entre 58 et 70 ms. C'est le biais de mesure de Mytkowicz et al. (ASPLOS 2009) à l'échelle d'un facteur 7.
* **Le témoin d'environnement varie autant que les épisodes qu'il devrait signaler.** Douze
  lancements consécutifs, avant toute mesure : débit FMA de 112 à 226 Gflop/s, latence à 2 Mio de
  36 à 64 ns. Il reste descriptif (règle fixée dans `docs/ANALYSIS_V2.md`).
* **Le JIT de .NET ne vectorise pas les boucles.** En optimisation complète
  (`DOTNET_TieredCompilation=0`), son propre désassemblage (`DOTNET_JitDisasm`) montre une somme
  d'entiers, une addition de tableaux de `float` et une somme conditionnelle scalaires (`add eax,
  [rdi]`, `vaddss`), alors qu'il déclare cibler « *X64 + VEX + EVEX* » (`probes/csharp_jitvec`).
  Avec les réglages par défaut, compilation par niveaux et PGO dynamique actives, le code de niveau 1
  (« *optimized using Dynamic PGO* ») reste lui aussi scalaire (`probes/csharp_jitvec_tiered`, sonde ajoutée
  après le second audit).
* **K8 `tuned` : le compilateur pèse plus que le style.** Trois codages C du même algorithme (A :
  compteurs passés par pointeur, comme `bench/c/ms.c` ; B : état passé par valeur ; C : arène
  globale, comme Ada), médiane de deux exécutions : clang 23 de 186 à 289 ms, GCC 16 de 84 à
  116 ms. Facteur 2,2 à 2,7 entre compilateurs, 20 à 30 % entre styles.
* **Pages géantes : presque aucun runtime ne marque son tas.** La politique est `madvise` sur les machines 1
  et 3 : le noyau n'en donne qu'aux régions que le programme marque. K1 `natural`, un processus par
  implémentation, relevé de `AnonHugePages` toutes les 100 ms : CPython en obtient 34 Mio (sur 3,3 Gio), Go
  2 Mio (sur 517 Mio), toutes les autres implémentations 0. JVM, .NET, V8, Bun et Julia compris. Les écarts de
  K1 entre langages ne viennent donc pas des pages géantes ; les demander reste un levier que le programme doit
  actionner lui-même (`madvise`, capacité absente de la matrice).
* **K5 sur la machine 3 : la FMA rallonge la réduction stricte.**
  * clang (C), flang, Chapel et Mojo fusionnent `s += a[i] * b[i]` en une FMA scalaire : `vfmadd231ss` dans la
    boucle, vérifié au désassemblage. Leur produit scalaire naturel prend 160 à 166 ms.
  * GCC vectorise la réduction en ordre strict : multiplications en vecteur (`vmulps`), puis une chaîne
    d'additions scalaires (`vaddss`) dans l'ordre des indices. Même boucle en C (`-std=c23` ou `-std=gnu23`), en
    C++ et en Fortran, et avec `--param avoid-fma-max-bits=0` : ni le mode ISO ni le réglage anti-chaînes de FMA
    n'y sont pour rien (`probes/k5_reduction`, `results/probes/k5_reduction.txt`). *Correction du 29 octobre :
    j'avais attribué ce code au mode ISO, et le second audit au réglage `avoid_fma256_chains` ; les deux
    explications sont fausses.*
  * clang laisse la boucle scalaire et la contracte en FMA (158,6 ms). Avec `-ffp-contract=off`, 82,2 ms ; avec
    `-mllvm -force-ordered-reductions`, qui vectorise la réduction ordonnée comme GCC, 80,3 ms.
  * Les autres langages compilés restent entre 77 et 87 ms, ce qui exclut une chaîne de FMA dans leur boucle.
  * Sur Cascade Lake (machine 1), la plupart des langages compilés étaient entre 164 et 184 ms, avec ou sans FMA.
* **Le témoin d'environnement ne prédit pas le temps des processus.** Sur les 450 processus de K5, corrélation
  de rang entre le témoin et le temps (rapporté à la médiane de sa mesure) : de −0,11 à 0,08 selon la grandeur.
  Sans le décile le plus lent du témoin (45 processus), aucun rang ne change. Le témoin a pourtant beaucoup
  varié : débit FMA de 82 à 250 Gflop/s, fréquence effective de 1,2 à 4,1 GHz, latence à 32 Mio de 91 à
  618 ns. Un instantané de 0,4 s avant le processus ne dit rien de l'état de l'hôte pendant celui-ci.
