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
* **Julia** : une attente active sans `yield()` ne bloque pas à elle seule. Le blocage observé
  (processus tué après 12 min) venait d'une variable capturée par une fermeture et affectée hors
  d'elle (`Core.Box`) : chaque addition allouait, une collecte se déclenchait et attendait un point
  d'arrêt que le thread en attente active n'atteignait jamais (`jl_gc_wait_for_the_world` sous gdb ;
  diagnostic corrigé le 30/10, `docs/JULIA.md`).
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
  (`vaddss`) au lieu d'un arbre vectoriel : K5 7,1 ms contre 4,7 ms en C (mais quatre accumulateurs de 16
  valeurs à la place ne changent rien de mesurable sur la machine 5 : rapport 0,98, `docs/FORTRAN.md`) ; (2) la
  vectorisation de boucles mêlant entiers 8 et 32 bits choisit des registres de 128 bits (Q1 « une passe par
  groupe » : 216 ms contre 60 ms pour la version naturelle) ; (3) des arguments `(:)` sans
  l'attribut `contiguous` produisent un code générique à pas variable (Q1 : 338 contre 44 ms).
* **flang 23** ignore `-mprefer-vector-width` (avertissement « argument unused »).
* **Ada (GNAT 16)** : les vérifications actives par défaut coûtent un facteur 3 sur le stencil 2D
  écrit avec des bornes littérales sur un tableau non contraint (K9 : 129 contre 41 ms une fois
  supprimées localement) ; sur un type contraint, GNAT prouve les indices et vectorise vérifications
  actives (ajouté le 30/10, `docs/ADA.md`). Un objet `Atomic` est écrit par un `xchg`
  séquentiellement cohérent : l'Ada standard n'offre pas d'ordre relâché, GNAT si
  (`pragma Disable_Atomic_Synchronization` donne un simple `mov` ; `System.Atomic_Primitives`).
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
  ligne (`std/sys/intrinsics.mojo`, `std/sys/_assembly.mojo`). `parallelize` est passé dans le paquet
  MAX à la 1.0 ; l'API de tâches est privée depuis la 1.1, et `async def` compile avec un avertissement
  (« expérimental et instable ») (`docs/MOJO.md`).
* **Ada 2022 / GNAT 16** : les boucles et réductions parallèles sont décrites dans la norme, mais
  GNAT les déclare « Feature unimplemented » (`gnat_rm.info`). L'aspect `CPU` des tâches et
  `Dispatching_Domains` sont disponibles.
* **Zig 0.17** : `@fence` a été retiré du langage ; `std.atomic.cache_line` et
  `std.atomic.spinLoopHint` existent. Le vectoriseur de boucles de LLVM est désactivé dans le
  compilateur (0.16 et 0.17, réactivé dans master) ; `std.Io.File.MemoryMap` projette un fichier
  de façon portable (depuis 0.16). Ajouté le 30/10 (`docs/ZIG.md`).
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
* **Vectorisation du code naturel (mesurée sur la boucle chaude)** : Zig 0.17 ne vectorise ni K4
  (code sans branchement scalaire, déroulé par 8) ni K9 (scalaire déroulé par 3), parce que
  l'équipe Zig a désactivé le vectoriseur de boucles de LLVM en 0.16 et 0.17, pour contourner un
  bug de LLVM qui compilait mal le compilateur lui-même (`src/zig_llvm.cpp`, ligne 288 ; notes de
  version). Zig 0.15.2 et master (0.18-dev, LLVM 23) vectorisent les deux boucles, K9 après un test
  de recouvrement des deux tableaux à l'exécution. *Corrigé le 30/10* : j'attribuais K9 à l'aliasing
  possible des deux tableaux ; c'était faux (`docs/ZIG.md`). Rust, D, Nim et Ada ne vectorisent pas le
  stencil naturel, à cause des vérifications de bornes de leurs tableaux de tableaux (Ada : tableau
  2D non contraint et bornes littérales ; sur un type contraint, GNAT vectorise, `docs/ADA.md`) ; dans le banc
  d'origine, gfortran ne vectorisait pas K4, parce que le noyau était inliné dans la boucle de mesure
  (hors ligne, comme le banc C l'impose à ses noyaux, gfortran le vectorise : corrigé le 30/10,
  `docs/FORTRAN.md`) ; flang le vectorisait déjà dans le banc d'origine ; le JIT de
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
* **Disposition du code, expérience de la v3** (`tools/layout_v3.py`, `results/raw_v3`, plan
  `docs/ANALYSIS_V3.md`, section 6). Même source, huit dispositions tirées par lld 23 (`--randomize-section-padding`,
  sections par fonction), deux processus par disposition, K1 à K9, sur un hôte du modèle de la machine 3.
  * K3, écrivain unique : C compilé par clang fait 12 à 23 ms dans 3 dispositions sur 8 et 74 à 117 ms dans les 5
    autres ; Rust 12 à 23 ms dans 4 dispositions et 74 à 90 ms dans les 4 autres. Les deux processus d'une même
    disposition tombent toujours du même côté. Le code de GCC reste entre 11 et 24 ms dans les huit dispositions.
  * Ailleurs, la disposition ne fait pas plus que le bruit entre processus (rapport F médian de 0,8 à 1,2), sauf
    trois effets modestes : K6 Q1 en 4 threads et K2 à 256 Kio en C compilé par GCC (× 1,7 et × 1,3 entre
    dispositions extrêmes), K4 naturel en C compilé par clang (× 1,9, effet qui s'affaiblit sans les tâches
    perturbées par mes calculs).
* **Sans K3, le plafond se réplique entre les deux micro-architectures** (diagnostic hors plan,
  `results/report_v3.md`). Pour les 13 premiers langages, la corrélation de rang du plafond E entre Cascade Lake et
  Emerald Rapids passe de 0,61 à 0,97 quand on retire K3, et les paires inversées de 22 à 5 sur 78. Dans la
  réplication, la boucle de K3 était tombée sur une bonne disposition pour Rust, Nim, Ada, C3, Mojo, D et C++ (13 à
  19 ms), sur une mauvaise pour C, C#, Chapel, Odin, Fortran, Zig, Java et Julia (76 à 82 ms) ; sur Cascade Lake,
  tous étaient entre 58 et 70 ms.
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

## Compteurs du noyau, sans PMU (29 octobre au soir) — `docs/INSTRUMENTS_V3.md`, `results/report_instruments_v3.md`

* **Ce qui existe sans PMU, vérifié** : compteurs logiciels (temps CPU, changements de contexte, migrations,
  défauts de page), tracepoints d'appels système, uprobes, points d'arrêt matériels, PSI. Le binaire `perf` est
  absent : `tools/pecount.c` ouvre ces compteurs par `perf_event_open`, hérités par tous les threads. Une uprobe
  ouverte par la PMU `uprobe` fait échouer les `fork` du processus compté ; l'outil la définit donc dans
  `uprobe_events`.
* **Coût d'une trappe dans cette microVM** : environ 30 µs par passage dans une uprobe ou un point d'arrêt matériel
  (une paire `malloc` + `free` passe de 10 ns à 59 µs ; une écriture de 0,2 ns à 30 µs), pour des comptes exacts
  (`probes/trap_cost`). Appel système minimal : environ 100 ns ; défaut de page mineur : 1,4 à 1,7 µs, et 19 µs au
  premier contact de la VM avec une mémoire (défaut côté hôte) (`results/hw/machine3/syspf.txt`).
* **Horloges** : Odin (`time.tick_now`, `clock_gettime` sans vDSO), Lua et LuaJIT (`os.clock`, temps CPU) font un
  appel système à chaque lecture d'horloge ; 32 770 par répétition de K8, deux par requête chronométrée.
* **Mémoire rendue puis retouchée** : sur K7 naturel, Rust, Zig, Odin et Fortran (flang) rendent la mémoire de leur
  table au système à chaque répétition, puis subissent 10 000 à 29 000 défauts de page en la reprenant (1 à 5 % du
  temps) ; C, C++, C3, Nim et gfortran la réutilisent.
* **Threads** : sur K3, la plupart des implémentations créent leurs 4 threads à chaque répétition ; flang (OpenMP),
  C# et Bun attendent en `sched_yield` (des centaines à des milliers par répétition) ; Python sérialise ses 4
  threads (24 000 `futex` par répétition, rapport CPU / temps écoulé de 1,09).
* **Runtimes** : des centaines à des dizaines de milliers d'appels système par répétition (Haskell 60 000 `futex`
  sur K8 naturel ; Node 26 000 `futex` et 24 000 `malloc` sur K1 naturel). En régime établi, le code compilé n'en
  fait qu'un ou deux (l'écriture du résultat).
* **Le contrôle du bruit dans l'invité ne réduit pas le bruit** : épingler sur un CPU, passer en `SCHED_FIFO` et
  déplacer les interruptions laisse l'écart-type entre processus inchangé (rapport 1,00 [0,64–1,33] sur cinq
  mesures natives), et ni la PSI, ni le temps volé, ni les changements de contexte, ni les migrations ne prédisent
  la lenteur d'un processus (|ρ| ≤ 0,23).

## Code standard seul (30 octobre, machine 4, Cascade Lake) — `docs/CONFRONTATION.md`

Rapports appariés réécriture standard / original, 7 processus de chaque côté, mêmes conditions.

* **C standard vaut presque C avec extensions.** Des sommes partielles explicites donnent la même boucle chaude que
  les intrinsèques AVX-512 (FMA 512 bits, quatre accumulateurs ; avec `-mprefer-vector-width=512`) : K5 1,05, K1 SoA
  0,97. `threads.h` vaut les threads POSIX (0,89 à 1,01). Ce qui coûte : Q1 sans intrinsèques (1,89) et K7 sans
  `__builtin_prefetch` (1,22).
* **Nim et D perdent la FMA sans moyen non standard.** Le C généré par Nim sépare la multiplication et l'addition,
  et seule une option globale (`--passC:-ffast-math`) les refusionne ; D sans `@llvmFastMathFlag` (ldc) fait de même.
  K5 : 1,37 et 1,20.
* **Chapel tient sa vitesse de `--no-ieee-float`, une option globale** : sans elle, la réduction de K5 n'est plus
  réassociable et devient une chaîne scalaire de FMA, 23 fois plus lente ; K1 SoA 1,69.
* **Go sans `GOEXPERIMENT=simd` ne vectorise rien** (K5 ×9, Q6 ×2,5) ; **Java sans la Vector API en incubation**
  non plus sur les réductions (K5 ×4,9, Q6 et Q1 ×7,8 et ×8,7).
* **`pragma Loop_Optimize (Vector)` de GNAT ralentit Q1** : sans lui, 0,77 (un et quatre threads).
* **C3** : les builtins `$$veccomp*`, que le compilateur réserve à la bibliothèque standard (avertissement à la
  compilation), ont des équivalents publics (`comp_*` de `std::math::vector`) qui donnent le même code machine.
* **Les binaires recompilés à l'identique** : recompilés sur ce nouvel hôte par leurs scripts inchangés, les
  binaires de C, C++, Nim, D, Ada, Fortran, Go, C3 et Chapel sont identiques octet pour octet à ceux de la campagne
  (compilés sur Cascade Lake le 28 octobre).

## Faits relevés par le second juge à l'aveugle (30 octobre), vérifiés — `docs/CONFRONTATION.md`, addendum

* **C a une aide de taille de ligne** : `sysconf(_SC_LEVEL1_DCACHE_LINESIZE)` (glibc, 64 ici) et la macro
  `__GCC_DESTRUCTIVE_SIZE` (64), prédéfinie en mode C par clang 23 comme par gcc 16. Ma matrice l'avait omise.
* **D a `std.parallelism.cacheLineSize`** (Phobos) et `core.cpuid.dataCaches` (druntime). Omis aussi.
* **Odin** : `base:runtime.MAP_CACHE_LINE_SIZE` est public, mais c'est un réglage des tables ; `core:simd/x86` ne
  couvre l'AVX-512 que par 8 procédures AVX-512F et 6 AVX-512BW.
* **L'attribut `@(fast_math={.Allow_Reassoc})` d'Odin est sans effet** dans le compilateur livré : l'énumération
  donne des indices de bit, que `llvm_backend_opt.cpp` teste comme des masques. Le drapeau `reassoc` n'est donc
  jamais posé.
* **Nim** : une réduction écrite avec l'itérateur `||` (OpenMP) ne compile pas en `-d:release` : le C généré
  renomme la variable que la clause `reduction` nomme.
* **D et Nim ont des indications de branchement standard** : `core.builtins.likely` et `unlikely` (druntime),
  `likely` et `unlikely` exportés par `system`.

## Remarque sur Zig (30 octobre, machine 5, Cascade Lake) — `docs/ZIG.md`, `results/zig_check/`

* **Zig 0.16 et 0.17 désactivent le vectoriseur de boucles de LLVM** : `pipeline_opts.LoopVectorization = false`
  (`src/zig_llvm.cpp`, ligne 288 des sources de 0.17.0), pour contourner un bug de LLVM qui compilait mal le
  compilateur Zig lui-même (notes de version de 0.16.0 et de 0.17.0). Master (0.18.0-dev.753, LLVM 23) le
  réactive. Le vectoriseur SLP et l'entrelacement restent actifs, d'où des boucles scalaires déroulées.
* **Mêmes noyaux, même pilote, quatre versions de Zig** (K4 et K9 naturels, temps minimum de 3 processus) :
  0.15.2 vectorise les deux boucles (K4 1,8 à 3,2 ms, K9 25 à 26 ms) ; 0.16.0 et 0.17.0 aucune (6,8 à 9,9 ms ;
  29 à 33 ms) ; master les deux (2,3 à 3,1 ms ; 25 à 26 ms), comme C compilé par le clang de Zig 0.17 (même
  LLVM 22.1.8) ou par clang 23. L'IR non optimisé de Zig 0.17, passé au pipeline `-O3` de ce clang, est vectorisé.
* **Lancer un thread coûte trois à quatre fois plus en Zig qu'en C** : `std.Thread.spawn` puis `join`, 148 à
  217 µs en moyenne par thread (Zig 0.17 sans libc), 125 à 171 µs lié à la glibc, contre 46 à 123 µs pour
  `pthread_create` en C ; `Io.Group.concurrent` (pool d'`Io.Threaded`) coûte 28 à 30 µs par tâche.
* **`std.Io.File.MemoryMap`** (depuis 0.16) projette un fichier de façon portable (`mmap` partagé sous Linux,
  visible dans `/proc/self/maps`) ; `std.mem.bytesAsSlice` le réinterprète sans copie. F4 de Zig vaut donc 1 en
  règle v1, et non 0,5.

## Remarque sur Ada (30 octobre, machine 5, Cascade Lake) — `docs/ADA.md`, `results/ada_check/`

* **Sans `-gnatp`, GNAT compile avec `-fnon-call-exceptions`** (`gcc-interface/misc.cc`, GCC 16.2). Inliné dans
  un appelant qui a des régions d'exceptions (programme principal, corps de tâche), un noyau ne se vectorise plus,
  même sous `pragma Suppress (All_Checks)` et `pragma Loop_Optimize (Vector)` : c'était le cas du stencil `tuned`
  et `mt` et de Q6 à 4 threads dans le binaire de la campagne. Hors ligne (`with No_Inline`), même source, mêmes
  options : K9 `tuned` 0,75 (au niveau de C compilé par GCC), K6 `mt` Q6 0,51, K9 `mt` 0,85.
* **Un changement d'inlining déplace aussi des noyaux qu'il ne touche pas** : dans le même binaire corrigé, K8
  naturel 0,82, K8 `tuned` 0,79 et K9 naturel 1,25, à source identique.
* **GNAT exploite RM 6.2(12)** (accès croisé entre paramètres = erreur bornée) : à -O3, une boucle qui n'écrit
  que dans des paramètres d'un type tableau contraint est marquée `ivdep` et vectorisée sans test de recouvrement
  (`trans.cc`) ; pas pour un tableau non contraint (pointeur « gras ») ni pour des valeurs d'accès.
* **`pragma Machine_Attribute (T, "vector_type")`** fait d'un tableau Ada un type vectoriel GCC : à -O3, une
  boucle d'addition sur ce type donne un seul `vaddps`, une multiplication-addition un seul `vfmadd132ps`.
* **`pragma Disable_Atomic_Synchronization`** remplace le `xchg` d'une écriture `Atomic` par un `mov`.
* **La pile secondaire alloue sur le tas** : une fonction qui rend un tableau non contraint de 4 Mo, sans `new`,
  appelle `__gnat_malloc` depuis `System.Secondary_Stack.Allocate_Dynamic`.
* **K2** : la boucle de chasse soustrait la borne inférieure dynamique à chaque saut (inlinée, elle ajoutait un
  `movsxd`) ; la borne fixe (extension `-gnatX` de GNAT) supprimerait la soustraction.
* **K8** : le meilleur temps d'Ada (108 ms) est l'arène de nœuds indexés, que GCC compile bien ; le pool de stockage
  prend 187 ms.

## Remarque sur Fortran (30 octobre, machine 5, Cascade Lake) — `docs/FORTRAN.md`, `results/fortran_check/`

* **Inliné dans la boucle de mesure, K4 restait scalaire** : dans le binaire de la campagne, `run_k4` ne contient ni
  appel ni instruction vectorielle, alors que les copies hors ligne de `k4_natural` et `k4_branchless`, vectorisées,
  ne sont jamais appelées. Avec `!GCC$ ATTRIBUTES NOINLINE` : K4 sans branchement 20,5 → 4,6 ms (C par GCC sur le
  même hôte : 4,8), K4 naturel 13,8 → 6,6 ms (6,1) ; K2 en cache 0,82 et 0,89, comme Ada avec la même correction.
* **Un rapport transféré d'un hôte à l'autre peut tromper** quand l'une des deux versions dépend de l'hôte : la
  boucle scalaire inlinée de K4 fait de 12,0 à 15,0 ms par processus dans les données principales, de 14,0 à 26,6 ms
  sur la machine 5. Transféré, le rapport mettait Fortran à 0,56 fois le C de GCC, alors que le même hôte les donne à
  égalité ; le témoin du même hôte sert de pont (`docs/FORTRAN.md`, 4.2).
* **`-fpack-derived`** fait passer un type dérivé (entier 8 bits, 32 bits, 8 bits) de 12 à 6 octets.
* **OpenMP dans gfortran 16.2** : `!$omp allocators allocate(align(128): a)` aligne les allouables (50 allocations
  sur 50, contre 0 sans directive), `!$omp allocate ... align(256)` les variables locales ; un allocateur à traits
  se branche sur `ALLOCATE`, mais la limite de réserve n'a pas été respectée dans ma sonde.
* **GCC 16.2 livre `libcaf_shmem`** : cotableaux en mémoire partagée sur un nœud, sans OpenCoarrays (4 images,
  `co_sum` juste).
* **K8** : une arène en un tableau de nœuds de 16 octets, au lieu de trois tableaux, donne 0,69 (135 ms, contre 146
  pour le C de GCC sur le même hôte).

## Remarque sur Mojo (30 octobre, machine 6, Cascade Lake) — `docs/MOJO.md`, `results/mojo_check/`

* **Pas de vectoriseur de boucles, par construction** : la chaîne de passes de Mojo 1.2.0
  (`LLVMPassesPipeline.cpp`, tag `mojo/v1.2.0`) ajoute le vectoriseur SLP et `VectorCombine`, jamais
  `LoopVectorizePass`.
* **Leviers de Mojo 1.2 vérifiés par sonde** : `@align(64)` respecté sur la pile et le tas ; `UnsafeUnion` (union
  non étiquetée) ; `FastMathFlag.REASSOC`, accepté par `SIMD.fma` seulement (`--fp-mode` ne règle que la
  contraction, `fast` par défaut) ; `fence()` donne `lock or` ; `SpinWaiter.wait()` ne fait rien aux trois premiers
  appels, exécute `pause` du 4e au 63e, puis cède la main ; `Pointer.unsafe_as_noalias()` est exploité en ligne
  droite, mais ne sort pas une lecture invariante d'une boucle dans ma sonde.
* **Allocations** : une erreur levée n'alloue pas (message littéral ou formaté) ; la trace de pile n'est capturée
  qu'avec `MODULAR_DEBUG=stack-trace-on-error`. Une tâche async coûte 1,5 à 1,8 allocation ; `async def` compile
  avec un avertissement (« expérimental et instable »).
* **Vérifications de bornes de `List`** (mode `ASSERT=safe`, par défaut) : dans la boucle chaude du stencil naturel,
  chaque comparaison est précédée de six écritures sur la pile (la position dans le source). Avec `-D ASSERT=none` :
  K9 naturel 169 → 41 ms (C par clang : 28 ms), Q1 naturel 137 → 67 ms (C : 66 ms).
* **K4 en SIMD explicite** (hors spécification) : 2,25 ms à chaud, 2,45 ms caches vidés, contre 3,05 ms pour K4 sans
  branchement de clang sur le même hôte.
* **Le L3 ne garde pas toujours 16 Mio** : sur la machine 6, une boucle de type K4 en C traite 16 Mio à 6,7–7,6 Go/s
  même répétée, mais 4 Mio à 20 Go/s ; le test de débit (`hwprobe bw`) voit pourtant 23 à 29 Go/s à 16 Mio sur les
  machines 4 à 6, et 9,9 Go/s sur la machine des données principales.
* **Le binaire de Mojo du banc était celui de la machine 3** ; recompilé sur Cascade Lake par son script inchangé, il
  redonne octet pour octet le binaire de la campagne (compilation reproductible).

## Remarque sur Julia (30 octobre, machine 7, Cascade Lake) — `docs/JULIA.md`, `results/julia_check/`

* **Julia 1.13.3** : `Threads.PaddedSpinLock` (public depuis la 1.13) occupe seul sa ligne de cache (120 octets) ;
  `Libc.malloc`, `Libc.free` et `unsafe_wrap` sont publics ; `ccall("llvm.x86.sse2.pause", llvmcall, ...)` émet
  `pause` ; `llvm.expect` par `llvmcall` ne laisse aucun poids de branchement dans l'IR optimisé.
* **K5 tuned (`@simd`)** n'émet que des FMA de 256 bits sur Cascade Lake (préférence de LLVM) ;
  `-C native,-prefer-256-bit` donne des FMA de 512 bits, sans gain mesurable sur la machine 7 (0,97). Des vecteurs
  `NTuple{16,VecElement{Float32}}` rendus par `llvmcall` sont mis en boîte (environ 10 Ko alloués par appel de K5).
* **Une variable capturée peut bloquer une attente active** : affectée dans une fermeture et dans la fonction
  englobante, elle est mise dans une `Core.Box`, et chaque mise à jour alloue ; la collecte ainsi déclenchée attend
  que tous les threads atteignent un point d'arrêt, ce qu'un thread en attente active sans `yield()` ni
  `GC.safepoint()` ne fait jamais (`jl_gc_wait_for_the_world`). Sans capture, K10 tuned passe de 440 à 18 ms.
* **Formes optimisées** (machine 7) : Q1 en une passe masquée 0,53 ; K7 préchargé par lots 0,69 ; K8 avec la
  profondeur en paramètre de compilation 0,83.

## Remarque sur Chapel (31 octobre, machine 8, Emerald Rapids) — `docs/CHAPEL.md`, `results/chapel_check/`

* **Chapel 2.10** : le module standard `Allocators` (instable) fournit `bumpPtrMemPool` et `newWithAllocator` ;
  `extern proc` importe les fonctions inline d'`immintrin.h` (`_mm512_fmadd_ps`), mais ni les macros à immédiat
  (`_mm512_cmp_ps_mask` : « perhaps it is missing or is a macro? ») ni `_mm_pause` (non lié) ; `c_array`, stable, vit
  sur la pile (5 ns par appel, contre 64 à 96 ns pour un tableau Chapel local).
* **L'attribut de boucle `@llvm.metadata(("llvm.loop.vectorize.enable", true))`** (instable) réassocie la réduction
  d'une seule boucle : produit scalaire de K5 165 → 6 ms ; il vaut l'option globale `--no-ieee-float` (K5 1,08, K1 aos
  0,96, K1 soa 1,00).
* **IR** : `foreach` pose `llvm.loop.parallel_accesses` ; avec ou sans `foreach`, le compilateur pose `!noalias` entre
  deux tableaux distincts.
* **Formes optimisées** (machine 8) : Q1 en intrinsèques importées 0,84 (au niveau du C) ; K7 naturel en une
  recherche (`ref e = m[k]`) 0,57 ; sommes partielles dans un `c_array`, sans option : K5 en 9 à 10 ms
  (32 accumulateurs), contre 165 ms en ordre strict.
* **Un pont par un témoin peut tromper entre deux architectures** : le C naturel de K7 (table chaînée) va dix fois plus
  vite sur cet Emerald Rapids que sur le Cascade Lake des données principales, Chapel non ; ponter K7 naturel par le C
  donnait un rapport de 2,8, quand la nouvelle forme divise le temps par 1,8.

## Remarque sur C# (31 octobre, machine 9, Emerald Rapids) — `docs/CSHARP.md`, `results/csharp_check/`

* **Compilation à niveaux de .NET 10** : avec 3 échauffements (au plus 13 appels), la boucle chaude d'un noyau appelé
  une fois par répétition tourne en code OSR (« Tier1-OSR »), compilé pour une entrée au milieu de la boucle : celui de
  K4 garde une vérification de bornes que le code de niveau 1 n'a pas. Une méthode qui contient un `stackalloc` passe
  directement en FullOpts. Le niveau 1 avec PGO dynamique demande ici plus de 70 appels (deux phases instrumentées).
* **Repli en MinOpts** : la compilation OSR d'une méthode qui garde une trentaine de vecteurs de 512 bits vivants (Q1
  en variables locales) se replie en MinOpts (« compiling with minopt ») : quatre fois plus lente que la forme
  d'origine, alors qu'en FullOpts elle gagne 16 %.
* **Effet moyen du protocole sur C#** : FullOpts d'emblée 0,998 (26 clés), régime établi 0,975 (16 clés), .NET 11 RC3
  0,99 ; de 0,85 à 1,16 selon la clé.
* **Sur Cascade Lake, .NET ramène la largeur préférée des vecteurs à 256 bits** (`codeman.cpp`, modèles 0x55) :
  `Vector512.IsHardwareAccelerated` vaut `false`, mais `Vector512` reste compilé en AVX-512.
* **Ni vectoriseur de boucles, ni if-conversion dans les boucles** dans le JIT (.NET 10, .NET 11 RC3, branche
  principale du 31/10) ; la PR 127032 lève ce garde-fou pour ARM64 seulement, la PR 127853 proposait un vectoriseur ;
  ni l'une ni l'autre n'est fusionnée.
* **Génériques** : C# spécialise une méthode générique pour chaque `struct` (l'appel contraint est inliné) et partage
  le code des classes ; Go 1.27 fait une copie par forme GC et appelle les méthodes par dictionnaire, même pour un
  `struct`.
* **Unions de C# 15** : un `struct` qui contient un champ `object` ; les cas valeur sont mis en boîte.
* **Formes optimisées** (machine 9) : K8 en pile explicite 0,51 (C par clang 0,93, par GCC 0,65) ; K4 sans branchement
  déroulé par 4, 0,72 à 0,82 ; threads du pool au lieu d'un `new Thread` par passe : K6 `mt` Q6 0,71, K9 `mt` 0,63 ;
  K4 en SIMD explicite : 0,83 ms.
* **Code naturel** : K1 en `struct` dans `List<T>` : 64 octets par particule, et le parcours permuté ne coûte plus rien
  (0,23 fois le temps de la classe) ; K6 avec les colonnes en paramètres au lieu de champs statiques : Q6 0,47, par la
  fusion des tests de plage (les vérifications de bornes restent).

## Remarque sur D (31 octobre, machine 10, Emerald Rapids) — `docs/DLANG.md`, `results/d_check/`

* **LDC 1.43.0** : ma chaîne est compilée depuis les sources contre LLVM 21.1.8 ; les paquets officiels embarquent LLVM
  22.1.8. Sur 26 clés, le paquet officiel donne 1,01 en moyenne, de 0,77 (K1 naturel) à 1,31 (K1 permuté).
* **`-release`** ne garde les vérifications de bornes que dans les fonctions `@safe` ; le code `@system` n'en a aucune.
* **Pas de métadonnées TBAA dans l'IR de LDC** : dans le stencil sur un tableau de tranches (`double[][]`), les
  pointeurs de lignes sont relus après chaque écriture et la boucle reste scalaire ; clang 23 vectorise le même stencil
  en `vector<vector<double>>`, et plus du tout avec `-fno-strict-aliasing`. En `double[M][]` (lignes de taille fixe),
  la boucle vectorise : K9 naturel 0,68 (36,4 → 24,6 ms).
* **druntime** : `core.builtins.likely`, `unlikely` et `expect` (`llvm.expect` sous LDC) ; `core.simd.prefetch`
  (`prefetcht0`) ; champs de bits natifs (`uint a : 3`) sans `-preview` ; les tableaux associatifs
  (`core.internal.newaa`) allouent chaque entrée par `new Entry!(K, V)` sur le tas du GC.
* **Deux plantages de LDC 1.43** (erreur interne dans `DtoLVal`) : une affectation `v.array[k] = …` dans une fonction
  `pragma(inline, true)` ; une expression vectorielle passée à une fonction inline dans un `+=`
  (`acc[g][4] += sum8(ace[g] + aco[g])`). Des variables nommées les contournent.
* **Q1 en une passe de `core.simd`** (l'algorithme de la référence C, 16 lignes à la fois ; 199 instructions zmm) :
  0,44 (72,6 → 31,8 ms) contre six passes masquées par bloc de 4 096 lignes ; à 4 threads, 0,46.
* **Préférence 512 bits** (`-mattr=-prefer-256-bit`) : Q6 tuned 0,84, Q6 `mt` 0,80, K4 sans branchement 0,62 ; sans
  effet sur les formes déjà écrites en vecteurs explicites (Q1, K1 aos : 1,03).
* **Marquage concurrent du GC** (`--DRT-gcopt=fork:1`) : pause maximale de K8 naturel 82 → 33 ms, mais p99,9
  0,90 → 1,79 ms et temps × 1,15.
* **Le pont par le C se trompe encore entre architectures** (comme pour Chapel) : le C naturel de K9 va 2,6 fois plus
  vite sur cet Emerald Rapids que sur le Cascade Lake ; ponter K9 naturel par le C donnait × 1,15, quand la mesure
  appariée donne × 0,68.

## Remarque sur Rust (31 octobre, machine 11, Emerald Rapids) — `docs/RUST.md`, `results/rust_check/`

* **Pas de métadonnées TBAA dans l'IR de rustc** (comme LDC) : dans le stencil naturel en `Vec<Vec<f64>>` indexé deux
  fois, les pointeurs de lignes sont relus après chaque écriture et la boucle reste scalaire, **même sans vérification
  de bornes** (`get_unchecked`). Les lignes liées une fois en `&[f64]`, `Vec<[f64; M]>` et `Vec<f64>` plat
  vectorisent, vérifications actives.
* **Préchargement en écriture en Rust stable** : `_mm_prefetch::<_MM_HINT_ET0>` émet `prefetchw` (cibles native et
  cascadelake), sans attribut de fonctionnalité ; le K7 optimisé du banc utilisait `_MM_HINT_T0` (`prefetcht0`), alors
  que la référence C et huit autres implémentations préchargent en écriture.
* **`u16::count_ones` dans une boucle AVX-512** : pour Cascade Lake (sans `vpopcnt`), le vectoriseur SLP de LLVM 23
  regroupe 4 des 6 popcounts de Q1 dans une émulation par `vpshufb` : 209 instructions et 15 vidages sur la pile dans la
  boucle de 16 lignes, contre 174 et 12 avec `_popcnt32(m as i32)`, et 169 et 11 pour le C de clang 23. Sur Emerald
  Rapids, qui a `vpopcnt`, c'est l'inverse (159 contre 183).
* **Queues de K8 et vol de temps** (campagne principale) : sur les 24 processus des implémentations qui passent par
  `malloc`, la corrélation de rang entre le vol de l'hyperviseur et le p99,9 vaut 0,81 ; pour un même binaire (Rust), le
  p99,9 passe de 327 à 692 µs quand le vol passe de 0,43 à 0,84 % de la capacité des 4 vCPU.
* **Préchargement en écriture sur K7** (machine 11) : `prefetchw` au lieu de `prefetcht0` rend la table 1,08 fois plus
  lente (IC 0,99–1,17), dans la marge des clés témoins au code inchangé (0,93 à 1,03 d'un binaire à l'autre).
* **Formes de Rust** (machine 11, rapports appariés) : K9 naturel en `Vec<[f64; M]>` 0,553 ; K8 tuned en arène écrite
  comme en C (index de sommet, `get_unchecked`) 0,742 ; Q1 avec `_popcnt32`, code de Cascade Lake exécuté sur Emerald
  Rapids, 0,825 (tuned) et 0,879 (`mt`). À algorithme égal, Rust et C font jeu égal sur Q1, Q6, K7 et K8 tuned (1,00 à
  1,05), pas sur K9 tuned (1,45).
* **Queues de latence de K8 remesurées** (machine 11, 25 implémentations × 7 processus) : la plus régulière est celle de
  Zig (p99,9 = 3,0 fois la médiane), puis Nim (3,1) et Mojo (3,2) ; la plus longue des langages compilés sans
  ramasse-miettes, celle de C3 (p99,9 277 µs, maximum 2,2 ms, comme sur Cascade Lake) ; la pire pause des langages
  compilés, D (89 ms) ; Julia 30 fois la médiane ; Python 0,76 s. Le vol corrèle encore avec le p99,9 (corrélation de
  rang 0,49 sur les 70 processus des langages à `malloc`), mais sept processus par langage en amortissent l'effet.

