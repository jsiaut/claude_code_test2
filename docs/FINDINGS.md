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
  K9 une seule fois pour toutes les répétitions (temps ≈ 0). Les `NOINLINE` et la relecture des entrées dans une
  `IORef` suffisent : l'option, redondante et plus lente, est retirée depuis la remarque sur Haskell.
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
* **Taille d'une particule de 64 o selon le langage** (octets vivants par élément de la collection
  naturelle) : 64 pour les tableaux de valeurs (C, C++, Rust, Zig, Odin, C3, D, Nim, Mojo, Chapel,
  Fortran, Ada, Go, Julia) ; Java 78 (en-tête compact de 8 o + 4 o de référence + marge de capacité
  de l'`ArrayList`) ; C# 88 (en-tête de 16 o + référence de 8 o) ; Haskell 96 (constructeur à champs
  `Float` stricts empaquetés, 72 o, plus une cellule de liste de 24 o) ; OCaml 144 (un
  enregistrement de flottants est stocké à plat, derrière un en-tête de 8 o, plus le pointeur de 8 o
  qui le désigne ; chaque `float` y occupe 8 o : OCaml n'a pas de flottant 32 bits de calcul, le
  format n'existant que pour stocker, dans un `Bigarray`) ; Bun 170 (JavaScriptCore range les
  nombres dans les mots de 64 bits de l'objet) ; Node 416 (V8 sans compression de pointeurs, que les
  binaires officiels de Node n'activent pas : un objet de 24 o d'en-tête et de 16 champs de 8 o, un
  objet `HeapNumber` séparé de 16 o par propriété flottante, et la case du tableau ; 272 o avec la
  compression, celle de Chrome ; corrigé le 3/11, remarque sur JavaScript) ; LuaJIT 428 et Lua 449
  (table à 16 champs nommés) ; Python 750 (dont 608 o demandés selon `tracemalloc`, le reste en
  arrondis de pymalloc).
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
  stencil naturel (*corrigé le 1/11*, j'accusais partout les vérifications de bornes) : en D et en Rust, c'est
  l'aliasing (ni LDC ni rustc n'émettent de métadonnées TBAA ; les pointeurs de lignes sont relus après chaque
  écriture, même sans vérification, `docs/DLANG.md`, `docs/RUST.md`) ; en Nim, les vérifications et
  `-fno-strict-aliasing`, que Nim impose au compilateur C, ensemble (`docs/NIM.md`) ; en Ada, les vérifications d'un
  tableau 2D non contraint écrit avec des bornes littérales (sur un type contraint, GNAT vectorise, `docs/ADA.md`) ;
  dans le banc d'origine, gfortran ne vectorisait pas K4, parce que le noyau était inliné dans la boucle de mesure
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
* **K3 sur la machine 3 : l'alignement du code décide d'un facteur 7.** La même boucle de 16 `incq` en mémoire, celle
  que clang, rustc et Odin produisent pour l'écrivain unique, prend environ 10 ms pour 2²⁵ incréments, soit un cycle
  chacun, à certains décalages dans sa ligne de 64 octets : 8, et 36 à 48. Elle prend 56 à 77 ms, soit sept cycles, aux
  autres décalages (`tools/k3_align.c`, `results/hw/machine3/k3_align.txt`). Dans la réplication, la boucle de Rust
  (décalage 48) tourne en 13 ms, celles de C/clang (16) et d'Odin (32) en 76 et 79 ms, octet pour octet identiques. Le
  code de GCC (`mov`, `inc`, `mov`, sans déroulage) prend 11 à 19 ms aux 16 mêmes décalages (`tools/k3_align_mov.c`). Le
  mécanisme probable est un raccourci matériel de la dépendance écriture-lecture, qui ne s'applique que selon le
  placement du code ; sans compteurs matériels, je ne peux pas le confirmer. Sur Cascade Lake, tous les langages étaient
  entre 58 et 70 ms. C'est le biais de mesure de Mytkowicz et al. (ASPLOS 2009) à l'échelle d'un facteur 7.
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
  C# et Bun attendent en `sched_yield` (des centaines à des milliers par répétition) ; Python sérialisait ses 4
  threads (24 000 `futex` par répétition, rapport CPU / temps écoulé de 1,09), des fils du build par défaut, avant la
  remarque sur Python, qui les a remplacés par des sous-interpréteurs.
* **Runtimes** : des centaines à des dizaines de milliers d'appels système par répétition (Haskell 60 000 `futex` sur
  K8 naturel avec `+RTS -N4`, ramasse-miettes parallèle ; quelques dizaines avec `-N1` ; Node 26 000 `futex` et 24 000
  `malloc` sur K1 naturel). En régime établi, le code compilé n'en fait qu'un ou deux (l'écriture du résultat).
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
  ramasse-miettes, celle de C3 par son p99,9 (277 µs ; son maximum, 2,2 ms, est au niveau d'Odin et de Mojo : précisé le
  1/11, remarque sur C3) ; la pire pause des langages
  compilés, D (89 ms) ; Julia 30 fois la médiane ; Python 0,76 s. Le vol corrèle encore avec le p99,9 (corrélation de
  rang 0,49 sur les 70 processus des langages à `malloc`), mais sept processus par langage en amortissent l'effet.

## Remarque sur Nim (1er novembre, machine 12, Emerald Rapids) — `docs/NIM.md`, `results/nim_check/`

* **Nim impose `-fno-strict-aliasing` au compilateur C** (`config/nim.cfg`, 2.2.12 et 2.4.0 : « seqs_v2 violates strict
  aliasing »). Dans le stencil en `seq[seq[float]]`, la boucle ne vectorise qu'avec `-d:danger` **et**
  `-fstrict-aliasing` ; en `ref array[M, array[M, float]]`, elle vectorise en `-d:release` : × 0,29, au niveau de C.
* **Le Q1 optimisé en blocs est vectorisé** par clang (8 lignes par tour, additions masquées sur xmm et ymm), mais il
  relit chaque colonne six fois par bloc ; transcrit avec les intrinsèques importées de la référence C : × 0,30, au
  niveau de C (1,02 fois son temps).
* **`{.localPassC.}`** ajoute une option au seul fichier C du module qui la déclare.
* **Nim 2.4.0** (sorti le 28 octobre) : code machine identique à 2.2.12 pour 20 des 21 fonctions des noyaux ; la
  construction de l'arbre de K8 naturel change (92 → 89 instructions) et devient 1,10 fois plus lente.
* **Nim vers gcc 16 au lieu de clang 23** : K4 2,5 à 2,9 fois plus lent, arène de K8 23 % plus rapide, et le harnais de
  K5 naturel ne mesure plus rien (0,03 ms au lieu de 95) : gcc ne garde que le dernier des 65 536 appels, dont les
  résultats sont écrasés, la boucle ne faisant plus que la barrière volatile (`results/nim_check/gcc_k5.txt`).
* **Arène de K8 sans vérification de débordement** : × 0,91.

## Remarque sur C3 (1er novembre, machine 13, Emerald Rapids) — `docs/C3.md`, `results/c3_check/`

* **C3 0.8.5_1** (LLVM 23.1.5) : `-O3` prend le pipeline O2 de LLVM ; -O4 et -O5 donnent O3 avec des flottants
  relâchés, `--optlevel=max` donne O3 en flottants stricts (× 0,98 en moyenne sur les 27 mesures du score).
* **Réassociation** : seulement globale (`--fp-math=relaxed|fast`, qui pose `reassoc` sur tout le module) ; en mode
  strict, `.sum()` d'un vecteur flottant est une réduction ordonnée (16 `vaddss`). Remplacée par un arbre, elle ne
  change rien de mesurable sur K5 (× 1,02) : la chaîne se recouvre avec l'appel suivant.
* **`@noalias`** est posé sur le premier paramètre quel que soit le paramètre annoté (`llvm_codegen.c`, l. 1245), et
  rien n'est posé sur une tranche.
* **Blocs `asm`** : 217 mnémoniques x86, ni chargement vectoriel, ni FMA, ni `pause`, ni barrière ; `asm("…")` passe
  du texte sans opérandes.
* **Pas de TBAA** dans l'IR de C3 : la boucle de Q1 naturel relit les sept pointeurs de colonnes à chaque ligne.
* **`alloc::new`** appelle `calloc` par l'interface `Allocator`, résolue par `.dyn_search` (recherche linéaire, sans
  cache) ; **`HashMap`** est chaînée, une `Entry` allouée par insertion.
* **`Thread.create`** attend sous Linux que le fils ait démarré (sémaphore) ; lancer les fils par
  `posix::pthread_create` ne gagne que 6 % sur K9 mt (non significatif).
* **Sur Emerald Rapids**, le K9 de C3 met 1,58 fois le temps de celui de C en un fil et 2,18 fois à quatre (0,93 et 1,40
  sur Cascade Lake) ; aligner ses accès ne change rien.

## Remarque sur Odin (1er novembre, machine 14, Emerald Rapids) — `docs/ODIN.md`, `results/odin_check/`

* **Odin dev-2026-10** (commit `84bc3fc`) : `-o:speed` prend le pipeline O2 de LLVM, `-o:aggressive` le pipeline O3
  (et une génération de code agressive) : × 1,006 en moyenne sur les 27 mesures du score, de 0,83 (Q1 `mt`) à 1,24
  (Q1 naturel).
* **Intrinsèques de LLVM** : `foreign _` et `@(link_name="llvm.…")` importent n'importe quelle intrinsèque, `#const`
  pour les opérandes immédiats ; `core:simd/x86` est écrit ainsi (246 liaisons ; 554 dans `core` et `base`, dont 77
  dans `core:sys/llvm`). Sonde : `vpconflictd` et `vpternlogd`, absentes de `core:simd/x86`, sont émises.
* **`@(optimization_mode="favor_size")` n'empêche pas l'inlining** ; `#force_no_inline` l'empêche. Sans annotation, LLVM
  inlinait dix des quatorze noyaux du banc dans leur boucle de mesure. **Leurs boucles chaudes n'en changent pas** :
  mêmes instructions, registres renommés près, isolés ou inlinés, pour Emerald Rapids comme pour Cascade Lake
  (`results/odin_check/codegen.txt`) ; seuls K5 naturel (isolé, la vérification de bornes reste dans la boucle) et les
  boucles externes de K9 diffèrent.
* **Placement du code** : K4 naturel et K4 sans branchement d'Odin compilent en la même boucle ; dans un même binaire,
  elles diffèrent de 8 % sur Cascade Lake (3,02 et 3,25 ms) et de 30 % sur Emerald Rapids (2,01 et 2,60 ms).
* **Le pont par le C ne tient pas pour un code inchangé** : quand la boucle ne change pas, l'écart entre transfert et
  pont vaut exactement la variation du rapport du langage au C d'un hôte à l'autre. Pour Odin, ce rapport passe de
  0,99 à 0,75 sur K2 à 8 Mio, de 1,01 à 0,81 sur Q6 optimisé, de 0,95 à 0,71 sur Q6 `mt` et de 0,94 à 1,49 sur K9
  naturel entre Cascade Lake et Emerald Rapids.
* **Allocateur par défaut** : `heap_allocator_proc` demande alignement − 1 + 8 + taille octets, soit 39 pour un nœud
  de 24 : glibc rend un bloc de 48 au lieu de 32 ; mémoire remise à zéro par `calloc` ; un appel indirect par
  allocation (`mem_alloc_bytes`).
* **Horloge** : `time.tick_now` passe par `syscall(SYS_clock_gettime)`, sans vDSO : 32 768 appels par répétition de
  K8, de l'ordre de 3 ms sur 1,9 s.
* **Q1 optimisé** : chaque groupe est compté par `simd.reduce_add_pairs(m & 1)` (39 permutations, aucun `popcnt`) ;
  `card(simd.extract_msbs(m))` donne un `popcnt` du masque et divise le temps par 1,8 (41,96 → 23,10 ms ; 0,88 fois C
  sur l'hôte) ; à quatre threads, × 0,54.
* **Table `map`** : 4,9 fois la table plate sur K7 naturel, mais 3e des treize premiers langages (2,42 s ; Zig 1,66,
  Nim 2,10 ; Rust 3,77, C 5,11, C++ 10,64) : toutes les tables standard sont 3,4 à 22 fois plus lentes que la leur.

## Remarque sur C++ (1er novembre, machine 15, Emerald Rapids) — `docs/CPP.md`, `results/cpp_check/`

* **`std::simd` dans GCC 16.2** : le manuel qualifie `-std=c++26` de « highly experimental » ; libstdc++ ne définit
  pas `__cpp_lib_simd` et ne déclare `std::simd` qu'en C++26 hébergé, avec les liaisons structurées et les
  instructions d'expansion de C++26, et `__SSE2__` (x86 seulement) ; `__cpp_lib_mdspan` est défini dès C++23. libc++
  23 n'a pas d'en-tête `<simd>`, seulement `<experimental/simd>` (TS Parallelism v2) : le C++ du banc ne compile pas
  avec clang++ 23.
* **Réflexion** : g++ 16 la compile et l'exécute avec `-std=c++26 -freflection` (« experimental »), la refuse sans
  `-freflection` ; clang++ 23 ignore `-freflection` (« argument unused ») et refuse l'opérateur `^^`.
* **C++20 par défaut** : g++ 16 sans `-std` définit `__cplusplus` à 202002L ; clang++ 23, à 201703L.
* **P2795** : sous `-std=c++26`, g++ 16 met à zéro les variables locales non initialisées (sonde : deux rangements à
  zéro sur la pile), pas sous `-std=c++23`, ni avec `-ftrivial-auto-var-init=uninitialized`, ni clang++ 23. Dans le
  binaire du banc, aucune des 17 fonctions de noyaux n'en change ; seules des fonctions du harnais, hors chrono.
* **K4 et le compilateur** : sous GCC, C et C++ donnent la même boucle pour chaque forme (61 et 44 instructions) ;
  clang++ 23 vectorise comme clang (`vpminsb`, `vpmovzxbq`, `vpaddq`), en boucle plus courte que celle de C (19
  instructions, contre 35 sur Cascade Lake et 67 sur Emerald Rapids). Sous clang++, les boucles de K1 aos et SoA, K2,
  K5, Q6 et K9 sont celles de C à l'instruction près (`results/cpp_check/clang_loops.txt`).
* **Harnais de K9** : d'après les sources, les grilles du chemin tuned et `mt` sont allouées une fois en C, Chapel, Ada
  et Fortran, à chaque répétition en C++, Zig, Odin, C3, Rust, Nim, D, Julia, C#, Mojo, Go et Java ; la spécification
  n'impose que la réinitialisation hors chrono (`results/cpp_check/k9_harness.txt`).
* **Mesures appariées (machine 15, sept processus)** : clang++ 23 divise le temps de g++ 16 par 2,4 à 3,5 sur K4 (0,285
  et 0,423) et fait 1,06 et 1,11 fois le temps de C ; sur les 26 mesures communes, C++ compilé par clang++ fait 0,995
  fois le temps de C (moyenne géométrique). Mais clang++ prend 1,55 fois plus de temps sur l'arène de K8 et 1,94 fois
  sur K5 naturel (GCC met moitié moins de temps que clang sur ce noyau, en C comme en C++), et vectorise Q6 naturel dans
  la forme de C++ (0,31 fois g++ et 0,31 fois C). L'arène de K8 par pointeur brut gagne 23 % sous g++. La forme en
  intrinsèques de C n'accélère pas Q1 sous g++ (1,04) ; le Q1 `std::simd` de C++ fait 1,03 fois celui de C sur cet
  hôte (1,15 sur Cascade Lake).
* **Allocation des grilles de K9** : réallouer à chaque répétition coûte à C 1,70, 1,93 et 2,01 fois son temps
  (naturel, tuned, `mt`) sur la machine 15 ; allouées une fois, les grilles de C++ lui donnent le temps de C (0,98 en
  `mt`). Sur Cascade Lake, les implémentations qui réallouent font le temps de C en un fil et 1,1 à 1,9 fois à quatre
  fils : la pénalité dépend de l'hôte.
* **Machine 15, artefacts d'hôte** : K2 à 8 Mio y est bimodal (pour 21 implémentations sur 25, facteur 3,2 à 4,0
  entre processus d'une même cellule, au même nombre de défauts de page, en pages de 4 Kio) ; la pénalité de désordre
  des langages à références y est deux fois plus faible que sur Cascade Lake (C# 2,68 contre 4,70, OCaml 2,22 contre
  6,99) ; K3 en écrivain unique y dépend du placement du code (C++ par clang++ 0,33 fois le temps de g++, 0,19 fois
  celui de C). Go met 1,8 à 2,3 s sur K1 naturel sur les Emerald Rapids (médianes de processus, machines 3 et 15), 56 ms
  sur Cascade Lake, en temps utilisateur (cause non cherchée).

## Remarque sur C (1er novembre, machine 16, Emerald Rapids) — `docs/C.md`, `results/c_check/`

* **C23 strict** : pas d'attribut `likely` (clang 23 l'ignore, gcc 16 le refuse en `-pedantic-errors`), ni type
  vectoriel, ni préchargement, ni constante de ligne de cache ; `__GCC_DESTRUCTIVE_SIZE` (64) est une macro prédéfinie
  par clang 23 et gcc 16 en mode C. `<immintrin.h>` (AVX-512, `_mm_prefetch`, `_mm_pause`) compile en C23 strict, hors
  norme. `#pragma clang fp reassociate(on)` agit localement (somme vectorisée sous le pragma, scalaire sans).
* **K9, harnais sur Cascade Lake** : `k9_rows` de C par gcc et de C++ par g++ compilent pour Cascade Lake en les mêmes
  boucles. Dans les données principales, à code égal, réallouer les grilles et lancer les fils par `std::jthread`
  coûte × 0,99 en un fil et × 1,58 à quatre fils.
* **K8, arène de C** : `a8_build` relit et réécrit à chaque nœud ses deux compteurs passés par pointeur (`*top`,
  `*counter`, du même type que des champs de l'arène), alors que `v = q + indice`. Sur la machine 16 : forme du banc
  290 ms sous clang 23, 155 ms sous gcc 16 ; récursion par valeur 166 et 70 ms ; itérative 116 et 135 ms (processus de
  94 à 151 ms sous clang). Avec la meilleure forme, le K8 tuned de C (106 ms reporté sur Cascade Lake) rejoint la
  frontière (Ada, 107,7 ms).

## Harnais commun de K9 (1er novembre, machine 16, Emerald Rapids) — `docs/K9.md`, `results/raw_k9h/`

* **Inventaire des harnais** (sources de `bench/`) : C, C par gcc, Chapel et Ada allouaient leurs grilles une fois ;
  Fortran et JavaScript aussi, sauf pour leur naturel ; toutes les autres implémentations les réallouaient à chaque
  répétition. Les fils de `mt` sont créés à chaque itération (C, C++, Zig, Odin, C3, Nim, D, C#, Java, Ada, OCaml,
  Python), pris dans une réserve (Chapel, Fortran par OpenMP, JavaScript par des workers créés une fois) ou lancés comme
  tâches ou goroutines (Julia, Mojo, Go, Haskell).
* **Défauts de page par processus**, ancien harnais puis harnais commun : C++ et Zig, environ 180 000 puis 16 700 (C :
  16 600) ; C# (tuned) 216 000 puis 19 000 ; Rust (tuned) 189 000 puis 25 000 ; Go (tuned) 51 000 puis 17 000. Java en
  a peu dès l'ancien harnais en tuned et `mt` (28 700 et 32 800) : la JVM réutilise son tas.
* **À hôte égal**, le harnais commun prend 0,41 à 0,65 fois le temps à quatre fils pour les compilés qui réallouaient,
  0,73 à 0,99 pour les langages à ramasse-miettes (Java tuned et `mt` : aucun gain), environ 1 pour les interprètes et
  Haskell.
* **L'hôte** : la machine 16 lit 25 à 27 Go/s sur un fil jusqu'à 64 Mio (Cascade Lake : 7 à 10 Go/s) ; les
  implémentations natives qui allouaient une fois y vont 1,9 à 2,8 fois plus vite qu'à Cascade Lake, celles qui
  réallouaient 1,2 à 2 fois.
* **Au harnais commun**, K9 `mt` prend de 3,8 ms (Chapel) à 6,5 ms (Mojo) pour douze implémentations compilées ; le
  naturel le plus rapide est celui de C3 (13,1 ms), le tuned celui de D (12,8 ms).

## Remarque sur Java (2 novembre, machine 17, Emerald Rapids) — `docs/JAVA.md`, `results/java_check/`

* **En-têtes compacts du JDK 27** (activés par défaut) : les données d'un `byte[]`, `int[]`, `float[]` ou `Object[]`
  commencent à 12 octets de l'objet (16 pour `long[]` et `double[]`, 16 pour tous sans en-têtes compacts) ; les
  objets sont alignés sur 8 octets. Un `float[]` n'est donc jamais aligné sur 16, 32 ou 64 octets, et chaque
  chargement de 64 octets de la Vector API chevauche deux lignes de cache.
* **K5 tuned** : sur la machine 17, C aligné 3,8 à 5,5 ms, décalé de 12 octets 7,6 à 8,2 ; Java sur le tas 7,1 à 8,1,
  sur une copie hors tas alignée (`Arena.allocate(n, 64)`, `FloatVector.fromMemorySegment`) 4,8 à 4,9, sur la même
  copie décalée de 12 octets 8,2 à 10,9 : le désalignement fait l'essentiel de l'écart à C. Campagne : × 0,60
  (9,23 → 5,54 ms ; C 3,86). Toutes les autres implémentations à SIMD explicite alignaient leurs données, C# par
  `NativeMemory.AlignedAlloc`.
* **K1 soa** : × 0,76 sur la machine 17, où les colonnes tiennent dans le cache L3 ; sur Cascade Lake, limité par la
  mémoire (Java 8,71 ms, C 7,76), l'effet ne se reporte pas.
* **Créer, lancer et attendre quatre fils** : 0,45 à 0,54 ms en Java, 0,10 à 0,11 ms en C. Une réserve de quatre
  fils (`Executors.newFixedThreadPool(4)`) gagne sur K9 `mt` (× 0,81), pas sur K6 `mt` (× 1,07 et 1,08).
* **Le C2 du JDK 27 vectorise le K9 à tableau plat** (xmm et ymm) ; écrit en Vector API, × 0,96 seulement.
* **Q1 en une passe**, accumulateurs des six groupes en variables locales et masques convertis par `toLong` et
  `fromLong` : × 0,40 (72,8 → 29,3 ms ; C 25,3) ; à quatre fils × 0,51.
* **K7 tuned** : le noyau isolé dans sa propre méthode va 1,4 fois plus vite (× 0,72) : sinon, le code mesuré est la
  compilation sur place (OSR) de `runK7`, appelé une seule fois. Des lots de 16 lus d'avance y perdent (× 0,80 au total
  avec l'isolement) : sans instruction de préchargement, la lecture anticipée attend la donnée.
* **K8 tuned** : arène construite et sommée itérativement, × 0,64 (246 → 158 ms) ; la forme du banc était déjà plus
  rapide que celle de C sur cet hôte (301 ms).
* **API FFM** (finale depuis le JDK 22) : `MemoryLayout.unionLayout` et les vues de segments, y compris d'un tableau
  du tas, réinterprètent la mémoire sans option de préversion ; des `sequenceLayout` imbriqués donnent un tableau
  multidimensionnel contigu, lu et écrit par plusieurs indices.

## Remarque sur Go (2 novembre, machine 18, Emerald Rapids) — `docs/GO.md`, `results/go_check/`

* **Le K1 naturel de Go à 2 s sur Emerald Rapids** (machines 3 et 15, « cause non cherchée ») : avec
  `GOEXPERIMENT=simd`, sur un processeur AVX-512, la préemption asynchrone de go1.27.3 (`runtime/preempt_amd64.s`)
  sauvegarde et restaure les registres Z0 à Z31, puis revient sans `VZEROUPPER`. Le code scalaire qui mêle SSE hérité
  (`MOVSS`, `CVTSS2SD`, `MULSD`) et VEX (les FMA de `GOAMD64=v4`) paie ensuite chaque passage d'un encodage à l'autre :
  K1 naturel 2 241 ms avec l'expérience, 38 ms sans, 37 ms avec `GODEBUG=asyncpreemptoff=1`. K9, tout en SSE, et les
  autres noyaux ne sont presque pas touchés (0,87 à 1,11). Toutes les variantes de Go étaient compilées avec
  l'expérience ; celles qui n'utilisent pas archsimd sont désormais prises d'une copie compilée sans elle.
* **K5 tuned de Go** : après la boucle AVX-512, la réduction s'exécute en SSE hérité (`XORPS`, `ADDSS`) sans
  `VZEROUPPER` ; les autres compilateurs l'émettent d'eux-mêmes, archsimd demande `ClearAVXUpperBits()`. Une ligne :
  22,6 → 8,7 ms sur la machine 18 (C 4,3).
* **Le compilateur Go déplace `ClearAVXUpperBits`** : dans une réduction horizontale suivie de l'appel, il a sorti les
  accumulateurs, exécuté `VZEROUPPER`, puis refait la réduction en AVX-512 avant un `MOVD` SSE. Passer le résultat par
  la mémoire (`StoreArray`) avant l'appel impose l'ordre.
* **K9 en archsimd** (`Float64x8`, même ordre des additions, résultat identique au bit près) : × 0,78 en un fil, × 0,73
  à quatre goroutines. **Q1 en une passe** en archsimd (six groupes, trente accumulateurs) : × 1,36, plus lent que la
  forme scalaire. **K8 tuned itératif** : × 0,62 (277 → 172 ms ; C 295 sur cet hôte).

## Remarque sur Haskell (3 novembre, machine 19, Emerald Rapids) — `docs/HASKELL.md`, `results/haskell_check/`

* **`-fno-omit-yields` ralentit les boucles serrées** : l'option met un test de préemption (`HpLim`) en tête de chaque
  boucle qui n'alloue pas ; l'en-tête devient un bloc à part, et chaque itération range son état sur la pile Haskell
  puis y revient par un appel terminal. LLVM ne garde plus la boucle dans les registres et ne change plus un
  branchement en déplacement conditionnel (IR : `results/haskell_check/llvm_k4_*.txt`). Sans elle (sept processus) :
  K4 naturel non trié 73,4 → 11,2 ms, K5 naturel 346 → 187 ms (C : 168), K3 `rmw_padded` 343 → 235 ms. L'option
  était appliquée à tout le banc, sans justification écrite ; K10 et K3 tournent sans elle.
* **`-fno-full-laziness` n'était pas nécessaire au harnais** (entrées relues dans une `IORef` à chaque répétition,
  noyaux naturels `NOINLINE`) ; sans elle, aucun temps ne s'effondre, et K9 naturel passe de 208 à 126 ms (avec
  `-fno-omit-yields` retirée aussi).
* **La FMA vectorielle de GHC 9.14.1 est dans `GHC.Prim`, pas dans `GHC.Exts`** : `fmaddFloatX16#`,
  `fmsubFloatX16#`, `fnmaddFloatX16#` ; le générateur natif refuse la FMA large (« sorry! … Please use -fllvm for
  wide vector FMA support »). K5 tuned avec elle : 5,97 → 4,60 ms, 1,04 fois C sur le même hôte.
* **Allocation cachée dans une arène** : une `IORef Int` boxe l'entier à chaque écriture (1,35 Go par répétition de
  K8 tuned, 33,5 millions de nœuds) ; un compteur rendu dans un n-uplet par une fonction récursive en `IO` reste
  boxé à chaque feuille (`I# (+# ww5 1#)` dans le Core), 281 Mo de plus. Les deux compteurs en mémoire brute, comme
  les pointeurs du C : 12,8 Mo par répétition (les latences du harnais), 719 → 214 ms (C de clang : 252 ms).
* **L'arbre longue durée de K8 gardé vivant (`touch#`)** : deux fois moins de collections majeures, mais plus longues
  (pause maximale 32 contre 9 ms, un processus) ; K8 naturel × 1,031, maximum des latences × 1,11 (intervalle large).
* **`+RTS -N4` rend le ramasse-miettes parallèle**, à quatre fils par défaut (`-qg0`, `-qn` = `-N` dans GHC 9.14.1),
  même pour un noyau séquentiel : sur K8 naturel, 87 414 `futex` sous `strace` contre 25 avec `-N1`, et `-N1`
  ramène le temps à 0,69 fois et le p99,9 à 0,29 fois. Julia, lancé avec `-t 4`, marque aussi à quatre fils.
* **K7 naturel (`Data.IntMap`)** : 51 à 54 s sur la machine 19 (89 s publiés, Cascade Lake) ; ni les options ni
  `-N1` ne le changent.

## Remarque sur OCaml (3 novembre, machine 20, Emerald Rapids) — `docs/OCAML.md`, `results/ocaml_check/`

* **`Bool.to_int (a && b)` branche** : `ocamlopt -O3` (OCaml 5.5.2, flambda) compile les `&&` en court-circuit en
  branchements conditionnels (`jl`), même sous `Bool.to_int` ; des comparaisons séparées, chacune par `Bool.to_int` et
  combinées par `land`, donnent des `setcc` et plus aucun branchement de données. Q6 tuned 213,6 → 87,4 ms (× 0,409,
  sept processus), `mt` × 0,467 ; le masque des bits de signe gagne encore × 0,86.
* **`x ** 2.` appelle `pow`** : flambda ne le remplace pas par une multiplication, et la fonction d'énergie de K1 aos,
  non inlinée, appelle `pow@plt` trois fois par particule ; `x *. x` : 266,5 → 45,3 ms (× 0,170).
* **Ni `cmov`, ni `popcnt`, ni préchargement** dans le code x86-64 d'`ocamlopt` (sondes : un `max` garde `cmp` et
  `jle`) ; `Int.popcount` est écrit en OCaml (`int.ml`). `Atomic.get` est une lecture de champ ; `Atomic.set` (par
  `exchange`) et `fetch_and_add` appellent des fonctions C du runtime (`caml_atomic_exchange_field`,
  `caml_atomic_fetch_add_field`) : l'écrivain unique de K3 est 7,2 fois plus lent qu'en C (Go 6,2, Haskell 6,5).
* **Horloge monotone** : `Runtime_events.Timestamp.get_current` (OCaml 5.4 et suivants, nanosecondes) coûte autant que
  `Unix.gettimeofday` (31 à 36 ns la lecture) et n'alloue pas ; deux lectures successives sont à 29 ns d'écart, contre
  0 avec `gettimeofday` (microseconde).
* **Références dans une arène** : deux `ref` par requête dans K8 tuned font 65 536 mots alloués par répétition dans le
  tas mineur, sans effet mesurable (× 1,008) ; passer sommet et compteur par valeur gagne × 0,770 (sensibilité, comme
  `c_k8val` pour C).
* **Formes plus poussées, même hôte** : K7 à deux mots par case (clé et compteur tassés dans un entier) × 0,875 ; K9
  en `floatarray` × 0,945 (`mt` × 0,939), les accès `Bigarray` du banc, à *kind* annoté, étant déjà des lectures en
  ligne (désassemblage) ; K5 à huit accumulateurs × 0,968. Les facteurs de la remarque (× 1,22, × 1,45 à 1,56)
  venaient d'OCaml 4.14.1 sans flambda et de réécritures de son auteur, que je n'ai pas pu reproduire.
* **Placement** : sur les 32 clés dont seule l'horloge change, les rapports vont de 0,82 (Q1 `mt`) à 1,11 (K9 tuned),
  moyenne géométrique 1,008 ; à code identique, des effets du binaire, non reportés.

## Remarque sur JavaScript (3 novembre, machine 21, Emerald Rapids) — `docs/JAVASCRIPT.md`, `results/js_check/`

* **Node.js n'active pas la compression de pointeurs de V8** (`process.config.variables.v8_enable_pointer_compression`
  = 0 dans le binaire officiel de Node 26.12.1) : un objet à 16 propriétés flottantes coûte 24 o d'en-tête, 16 champs
  de 8 o et un `HeapNumber` de 16 o par flottant, d'où 416 o par particule (272 o avec la compression, celle de
  Chrome).
* **TurboFan garde les vérifications sur les tableaux typés** : dans la boucle de `k5Tuned` (Node 26), pour 8
  éléments, 16 vérifications de bornes, 8 de débordement (7 indices et l'incrément), une adresse recalculée (`leaq`)
  avant chaque chargement, et les accumulateurs relus depuis la pile. K5 naturel (machine 3) : 152 ms contre 79 pour
  le C scalaire de GCC.
* **Une opération atomique est un appel** : sous Node 26 comme sous Node 22, `Atomics.add`, `Atomics.load` et
  `Atomics.store` deviennent des appels aux fonctions internes `AtomicsAdd`, `AtomicsLoad`, `AtomicsStore`. K3
  `rmw_padded` : 4,1 fois C sous Node, 1,3 fois sous Bun (JavaScriptCore) ; `sw_padded` : 26 et 8 fois.
* **Pretenuring de V8 sur K8 naturel** : l'arbre longue durée, construit par la même fonction que les arbres des
  requêtes, fait marquer le site d'allocation comme durable, et V8 alloue ensuite les nœuds jetables dans la vieille
  génération. Avec un site distinct (même hôte, sept processus) : temps × 0,617 [0,558–0,714], p99 × 0,496, p99,9
  × 0,488, pire pause 81,6 → 1,1 ms ; `--no-allocation-site-pretenuring` fait de même (sonde).
* **Q1 deux fois plus lent sous Node 26 que sous Node 22** (même source, même hôte) : tuned 269,9 contre 111,7 ms,
  naturel 263,5 contre 131,2. Turbolev est désactivé par défaut dans Node 26 (`--turbolev`), et l'activer accélère Q1
  (178 ms, sonde) : la lenteur vient du chemin par défaut de V8 14.6.
* **Cases de 16 o en JavaScript** : clé et compteur en `Uint32Array`, somme en `Float64Array`, deux vues sur le même
  `ArrayBuffer` ; K7 tuned × 0,577 [0,541–0,618] par rapport aux quatre f64 par case.
* **Formes plus poussées, même hôte** : Q6 par masque de négation et sommes entières par blocs de 4 096 × 0,596 (`mt`
  × 0,654) ; K9 par vues de lignes et voisins dans des variables × 0,883 (`mt` × 0,828) ; arène de K8 itérative
  × 0,727 ; K5 avec les données copiées en f64 × 0,883 ; K1 soa en colonnes f64 sans gain (× 1,046).
* **Outils** : `--print-opt-code` affiche le code machine de TurboFan avec les binaires officiels de Node 26 et 22 ;
  le module `node:ffi` de Node 26.12.1, actif par défaut (avertissement expérimental), donne l'adresse d'un
  `ArrayBuffer` (`getRawPointer`), la lecture et l'écriture par pointeur sans vérification (`getFloat64`…) et la
  conversion d'un pointeur en `ArrayBuffer` (`toArrayBuffer`). `Atomics.pause`, `Float16Array` et `Math.f16round` sont
  livrés ; pas d'objet `SIMD`.

## Remarque sur Python (5 novembre, machine 22, Cascade Lake) — `docs/PYTHON.md`, `results/python_check/`

* **Des sous-interpréteurs, un GIL chacun** : CPython 3.15.2 livre `concurrent.interpreters` dans sa bibliothèque
  standard ; une `memoryview` d'un `array` se partage entre eux sans copie. Par rapport aux fils du build par défaut
  (même hôte, sept processus) : K3 espacé × 0,323 et 0,308, tassé × 0,699 et 0,902 ; K6 `mt` × 0,371 (Q6) et 0,343
  (Q1) ; K9 `mt` × 0,515. Le faux partage, invisible sous le GIL (tassé contre espacé : 0,98 et 1,03), apparaît : 2,1
  fois en `rmw`, 3,0 fois en `sw`.
* **Le build sans GIL** : un `array` partagé y sérialise les fils par son verrou d'objet (sonde, quatre fils de 2^22
  incréments : 6,7 et 9,4 s, contre 0,71 et 1,75 s par une `memoryview` propre à chaque fil). Même avec K3 ainsi
  corrigé, il ne bat les sous-interpréteurs sur aucune clé parallèle (K9 `mt` × 1,155 par rapport aux fils du build
  par défaut). À source égale, sur les noyaux séquentiels de cet hôte : Q6 × 1,23 à 1,32, K9 × 1,36 à 1,59, K5 tuned
  × 0,85 (un processus) ; K10, deux fils qui échangent par une `queue.Queue`, 5,2 fois plus lent.
* **Pauses de K8 naturel** : elles viennent des collectes de la plus vieille génération, qui parcourent l'arbre longue
  durée (2^21 − 1 nœuds). Avec `gc.freeze()` après sa construction : temps × 0,800 [0,729–0,881], pire pause 752 →
  9,0 ms, p50 à p99,9 à 10 % près.
* **Q6 en colonnes** : masques 0/1 par `bytes.translate` (l'entier de date lu par ses octets), combinés en entiers
  longs, lignes retenues (1,79 %) trouvées par `bytes.find` : × 0,354 en tuned, × 0,286 en `mt` ; le masque seul
  coûte 0,70 s pour 16,8 millions de lignes.
* **Faits de CPython 3.15.2** (sondes, deux builds) : JIT non compilé (`sys._jit.is_available()` = `False`) ;
  ramasse-miettes générationnel (seuils 2000, 10, 10 ; trois générations) ; `gc.disable()` et `gc.freeze()` ; types
  `ctypes` de largeur fixe qui enveloppent (`c_uint32(2**32 + 5)` = 5, `c_int32(2**31)` = −2 147 483 648, tableaux
  compris), `array('I')` qui refuse les valeurs hors bornes ; NumPy, Numba, Polars, DuckDB et cffi absents.
  Empreinte de K1 selon `tracemalloc` : 608 o par particule pour une classe ordinaire, 552 avec `__slots__`, 64,7 en
  `array('f')`.

## Remarque sur Lua (5 novembre, machine 23, Cascade Lake) — `docs/LUA.md`, `results/lua_check/`

* **Partie tableau et partie hachée** : une table Lua n'étend sa partie tableau que si plus de la moitié de ses cases
  sont prises ; avec `c = {}`, les compteurs aux indices 17, 33 et 49 de K3 « espacé » allaient dans la partie
  hachée, 1,42 fois plus lente : le « faux partage × 0,63 » publié pour Lua, qui n'a pas de fils, venait de là.
  Préremplie, la table rend espacé et serré égaux (1,05 et 0,99).
* **Un appel C par octet** : `string.byte` coûtait 62 ns par octet dans K4 ; sur une table d'octets décodée hors
  chrono, K4 va 2,8 à 3,6 fois plus vite, et la prédiction de branchement apparaît (trié 1,5 fois plus rapide que non
  trié, contre 1,2).
* **`cond and 1 or 0` branche** : dans le bytecode de la 5.5.1, chaque prédicat du masque de Q6 donne une comparaison
  et deux sauts (`LT`, `JMP`, `LOADI`, `TEST`, `JMP`) ; le bit de signe d'une différence, décalé de 63 bits, donne le
  même masque sans saut (× 0,74), et des tests imbriqués font mieux encore dans l'interpréteur (× 0,51 de plus).
* **Champs nommés contre table positionnelle** : un nœud de K8 à trois champs nommés coûte 1,44 fois un nœud
  `{v, false, false}` (latences 1,27 à 1,58 fois ; LuaJIT, 1,37 fois) ; en Python, un nœud de classe ordinaire coûte
  1,06 fois un nœud à `__slots__` (pire pause 1,29 fois).
* **Allocations de PUC-Lua 5.5.1** (sonde) : aucun octet pour un million d'opérations flottantes et entières ni pour un
  million d'appels à trois retours ; 80 octets par fermeture, 82 par concaténation, 12 par élément d'une table
  construite élément par élément. **Empreinte** : 48 octets par table vide, 24 par champ nommé, 9 par case de
  tableau ; une particule à 16 champs coûte 449 octets (48 + 8 + 16 × 24 + 9).
* **LuaJIT** : son code compilé ignore `volatile` (sa documentation ; sonde : 0,32 à 0,64 ns par incrément de K3, le
  compteur en registre) ; la boucle interprétée (`jit.off`) sur une table, conforme, coûte 0,74 à 0,78 fois celle de
  PUC-Lua ; `-jdump=m` affiche le code machine des traces ; la version 2.1.1792588164 est l'horodatage de son commit
  du 21 octobre 2026.
* **Formes plus poussées, même hôte** : Q6 par tests imbriqués × 0,51 (`mt` × 0,49) ; K7 dans une seule table, compte
  et somme tassés dans un entier, × 0,71 ; K9 aux voisins glissants × 0,87 (`mt` × 0,96) ; K1 `soa` au 0,5 sorti de
  la boucle × 0,83 ; K2 aux indices décalés × 0,77, 0,82 et 0,97 ; arène itérative de K8 × 1,06, plus lente.
* **Machine 23** : latence 25 ns jusqu'à 2 Mio, 137 ns dès 4 Mio ; sur la machine 22, du même modèle, 25 ns encore à
  4 Mio : l'hôte ne laisse à la VM qu'une part de son L3.

## Ajout de Swift (5 novembre, machine 23, Cascade Lake) — `docs/SWIFT.md`, `results/swift_check/`

* **Chaîne et mode** : Swift 6.4.2 (29 octobre), LLVM de la chaîne (clang 21). `swift build -c release` compile en `-O`
  sur le module entier et en mode Swift 6 (relevé sur un paquet de `swift package init`) ; `-O` garde les
  vérifications de bornes et de débordement, `-Ounchecked` les retire.
* **Conversions SIMD de la bibliothèque** : `SIMD16<Int32>(truncatingIfNeeded:)` depuis des octets ou vers des entiers
  de 64 bits n'est pas inliné (un appel par conversion, `vzeroupper` et écritures sur la pile) ; écrite voie par voie,
  la même conversion donne `vpmovzxbd` / `vpmovsxdq`.
* **Comparaisons vecteur contre scalaire** : `v .== 3` est compilé voie par voie, avec trois branchements (44
  instructions, contre 14 sans branchement pour `v .== SIMD16(repeating: 3)`) ; dans Q1 optimisé, 1,79 s au lieu de
  39 ms. Une boucle sur un `InlineArray` de six accumulateurs SIMD n'est pas déroulée (accumulateurs en mémoire, 82 ms).
  `sum()` additionne dans l'ordre des voies (15 `vaddss`), sans réassociation.
* **Masques** : ni compte des bits d'un `SIMDMask`, ni conversion d'un masque entre largeurs de voies. Q1 optimisé
  compte donc ses lignes dans un accumulateur vectoriel de plus par groupe et refait des comparaisons 64 bits pour la
  colonne des charges : 36 vecteurs vivants pour 32 registres zmm, 74 accès à la pile par tour de 16 lignes, 1,47 fois
  le temps du C sur le même hôte (le C compte par `popcnt` du masque).
* **Intrinsèques** : `import _Builtin_intrinsics.intel` (module Clang non documenté) donne les intrinsèques à corps ;
  `_mm_pause` est appelée comme une fonction externe (`undefined reference`), `_m_prefetchw` disparaît du code sans
  message, `_mm_prefetch` est une macro refusée : ni préchargement ni `pause` en Swift.
* **Module Glibc** : sans les extensions GNU (`sched_setaffinity`, `sched_getcpu`, `gettid`, `mallinfo2` introuvables) ;
  aucune affinité possible avec la chaîne livrée. `@_alignment` (non documenté) plafonne à 16 octets ; les paramètres
  `inout` n'ont pas `noalias` dans l'IR.
* **Allocations cachées** (sonde) : une struct de 64 octets rangée dans un `[any Shape]` (conteneur existentiel de 40
  octets, tampon en ligne de 24) est mise en boîte sur le tas sans allocation écrite ; de même les fermetures
  échappantes et la copie sur écriture.
* **Ce que `-O` garde, sur le code exécuté** : K4 naturel (`if x >= 128 { s += UInt64(x) }` sur un `[UInt8]`) reste
  scalaire, un branchement par octet et un test de débordement par addition : 29 fois le temps du C sur le même hôte
  (76,6 contre 2,6 ms), 5,8 fois moins en `-Ounchecked`. Dans le stencil `[[Double]]`, la boucle chaude (48 % des
  échantillons) teste les bornes de chaque lecture et appelle `swift_isUniquelyReferenced_nonNull_native` à chaque
  écriture (copie sur écriture de la ligne de destination) : 3,0 fois le C, 2,5 fois en `-Ounchecked`.
* **ARC sur K8** : l'arbre de `class Node` à champs `var` coûte 2,4 fois le `malloc`/`free` du C ; une classe finale à
  champs `let`, construite de bas en haut, prend 0,67 fois ce temps (moins de comptages de références). Latences :
  p50 101 µs, p99,9 372 µs (C : 38 et 189 µs), sans pause : chaque arbre est libéré dans le chrono.
* **`AsyncStream`** (K10 naturel, hors score) : chaque élément suspend et reprend la tâche consommatrice ; 14 à 19 s
  pour 2^22 éléments, 5,8 s de temps système, 388 000 changements de contexte volontaires.
* **Empreinte** : 64,02 octets par particule (structs en ligne dans un `Array`).
* **Facteur d'hôte** : la machine 1 était plus lente que la machine 23 pour tous les codes mesurés sur les deux (21
  couples de Lua, LuaJIT et Python : 1,10 à 1,78, médiane 1,28). Le facteur du C suit celui des autres à ±20 % près
  sur les clés à un fil de la machine 1, mais pas sur K3 (0,75 à 1,76 contre 1,23 à 1,48), Q6 `mt` (1,68 contre 1,32)
  ni K9, venu de la machine 16 (0,55 et 0,64 contre 1,17 et 1,08 pour Lua).

## Remarque sur Swift (5 novembre au soir, machine 24, Emerald Rapids) — `docs/SWIFT.md` (5), `results/swift_check/facts2.txt`

* **Affinité** : `sched_setaffinity`, `pthread_setaffinity_np`, `sched_getcpu` et `gettid` sont dans le module Glibc
  livré, derrière `_GNU_SOURCE`, comme en C ; avec `swiftc -Xcc -D_GNU_SOURCE`, un fil s'épingle (`sched_getcpu`
  rend le CPU demandé). Sans l'option, « cannot find 'sched_setaffinity' in scope ».
* **Préchargement et `pause`** : `prfchwintrin.h` (Clang 21 de la chaîne) déclare `_m_prefetch` et `_m_prefetchw` sans
  corps ; Swift les importe `[readnone]` (SIL) et l'optimiseur supprime l'appel. `@_silgen_name("llvm.prefetch.p0")`
  donne `prefetchw`, `@_silgen_name("llvm.x86.sse2.pause")` donne `pause` : un attribut souligné, que l'interface
  publique de la bibliothèque standard emploie 59 fois, jamais vers une intrinsèque de LLVM.
* **`noalias`** : seuls les `inout` de type pointeur le portent dans l'IR ; ni `inout Int`, ni `inout [Float]`, ni
  l'`inout` d'une struct, ni les pointeurs passés par valeur.
* **Spécialisation** : `@specialized(where T == Int)` et `@inline(always)` compilent sans option dans la 6.4.2 ;
  `@const` exige `-enable-experimental-feature CompileTimeValues`.
* **Types de la 6.4** : `UniqueBox`, `UniqueArray`, `Ref`, `MutableRef`, `Iterable` sont publics. Un arbre de nœuds
  `~Copyable` reliés par `UniqueBox` épuise la mémoire du compilateur (« LLVM ERROR: out of memory » après 201 à 210 s,
  plafond de 6 Go, passe `EarlyPerfInliner`) sauf avec un `deinit {}` vide (1,1 s). En K8, il prend 0,45 fois le temps
  de la classe et 1,20 fois celui du C (Emerald Rapids).
* **K4 naturel avec `&+=`** : vectorisé (12 `vpaddq`), 1,78 ms contre 67,2 ms avec `+=`, 0,84 fois le C natif ; en
  `-Ounchecked`, la boucle avec `+=` reste scalaire, sans branchement (18 `cmov`).
* **Swift / C sur Emerald Rapids** (constructions natives, 7 processus) : K5 naturel 0,50 (le C y fusionne la somme en
  FMA scalaire, Swift non), K9 naturel 5,0 (3,0 sur Cascade Lake), Q1 optimisé 1,03 (1,47 sur Cascade Lake ; 1,13 avec
  le code de Cascade Lake exécuté sur Emerald Rapids), K4 sans branchement 0,83 ; queues de latence de K8 plus longues
  qu'à Cascade Lake (p99,9 2,29 fois le C contre 1,97, maximum 1,78 contre 1,14).
* **Provenance** : recompilé sur la machine 24 par les options de `bench/c/build.sh`, le C est identique octet pour
  octet au binaire de la machine 3 ; compilé pour `cascadelake`, au binaire publié.

## Ajout de FreePascal (6 novembre, machine 25, Emerald Rapids) — `docs/FPC.md`, `results/fpc_check/`

* **Chaîne et mode** : Free Pascal 3.2.2 (mai 2021), la dernière version publiée ; générateur de code propre à FPC.
  Le `fpc.cfg` livré définit un mode « release » (`-dRELEASE` : `-O2 -Xs`) ; le banc prend `-O3`, le plus haut niveau
  que `fpc -h` ne dit pas risqué (`-O4` réordonne les champs des classes et contracte les réductions en FMA). Bornes et
  débordements ne sont pas vérifiés par défaut. La cible la plus haute est `COREAVX2` : pas d'AVX-512, pas même dans
  l'assembleur en ligne (registres zmm inconnus ; seulement en octets bruts).
* **SIMD** : aucun vectoriseur (C3 mesurée : 0). Le seul SIMD sans assembleur est le traitement vectoriel de `-Sv`,
  des opérateurs sur des tableaux de 4 `Single` ou de 2 `Double` traduits en SSE de 128 bits : erreur interne
  200610072 pour 8 `Single`, opérandes en encodage SSE classique (alignement de 16 octets exigé, erreur d'exécution 216
  sinon), vecteurs gardés en mémoire entre deux opérations, ni masque, ni FMA, ni conversion. Il divise K5 optimisé par
  1,72 et K1 `soa` par 1,43, mais ralentit le stencil ; sans expression vectorielle, il ne change pas un octet du
  binaire.
* **Optimiseur** : l'accumulateur de K5 naturel reste sur la pile (la procédure appelle `fpc_dynarray_high` pour
  `High(a)`) : 2,1 fois le C ; deux `vmovaps` par FMA scalaire ; les champs d'un record passé en paramètre sont relus et
  les adresses recalculées à chaque accès (Q1 optimisé : 88 ms avec quatre tables et une procédure imbriquée `inline`,
  plus lent que le naturel, 54 ms avec deux tables et des pointeurs ; K7 optimisé : 0,32 s dans une procédure à
  variables gérées, 0,17 s dans une fonction à pointeurs) ; le stencil naturel recalcule l'adresse des trois lignes à
  chaque point.
* **Bibliothèque** : `TDictionary` coûte 30 ns par recherche même en cache, 200 à 225 ns sur 1 M de clés ; K7 naturel
  (deux recherches par ligne, pas d'accès en place) : 15,4 fois le C ; en valeurs de classe, une recherche : 0,37 fois.
  `New` / `Dispose` : 1,46 fois `malloc` ; nœuds de classe : 2,16 fois `New`. La RTL n'a ni file bloquante ni variable
  de condition : la file naturelle de K10 (`TQueue`, section critique, événements) prend 2,2 fois celle du C.
* **Concurrence** : `InterLocked*` sont des procédures de la RTL (`lock xadd` après un appel ; sans contention, K3
  `rmw_padded` 1,52 fois le C) ; `ReadBarrier`, `WriteBarrier`, `ReadWriteBarrier` émettent `lfence`, `sfence`,
  `mfence` ; ni `volatile`, ni atomique à ordre explicite, ni `pause` : K10 optimisé repose sur l'ordre TSO de x86-64
  (0,64 fois le C, qui attend avec `pause`).
* **Grille** (`probes/fpc`) : contrôle 60,5 en règle v2 (58,5 en v1) : disposition complète (records en ligne,
  `{$PACKRECORDS C}`, `packed`, `bitpacked`, records à variantes), pointeurs, assembleur en ligne, `Prefetch`,
  `{$R+}`/`{$R-}` locaux, génériques spécialisés ; ni intrinsèques, ni ordres mémoire, ni aide de ligne de cache, ni
  indication de branchement, ni non-aliasing ; affinité par un appel système brut (½ en v1, 1 en v2).
* **Classement** : 16e sur 23 (47,44 points ; rang espéré 16,71 ; 2e étage). Contrôle 16e, plafond 19e (36,3), code
  par défaut 12e (46,9 : empreinte 1,0, queues de latence 0,66, hiérarchie mémoire 0,98, comme C sur le même code, mais
  code naturel 0,050). C# le devance dans 82 % des variantes ; il devance Java dans 53 %.
* **Pont entre modèles** : toutes ses clés viennent de la machine 25 ; les facteurs du C vont de 0,76 à 4,6 sur les clés
  de la machine 1, 11,4 sur K3 `sw_packed` et 17,6 sur K7 naturel, et restent proches de 1 sur les clés venues du même
  modèle (K5, K9). Le second témoin (gcc, 47,51 points), un facteur d'hôte unique (47,29) et, hors plan, K7 naturel au
  facteur de la table plate du C (47,62) le laissent 16e ; la réplication aussi (machine 3, par le même pont).
* **Sensibilités** : 16e dans neuf scénarios sur treize, 15e sans pont pour les clés de la machine 1 (information,
  biaisé), 17e avec des cases plus basses, 18e sans `-Sv` (45,89) et avec toutes les lectures défavorables (43,28).

## Remarque sur FreePascal (6 novembre, machine 26, Emerald Rapids) — `docs/FPC.md`, section 5

* **Errata de la grille** : C2 ½ (assembleur en ligne jusqu'à AVX2, sans intrinsèques : comme Zig ; FreePascal était le
  seul langage noté avec un assembleur en ligne et C2 à 0), E4 ½ (`Prefetch` n'émet que `prefetchnta`, sans localité
  ni écriture), F4 ½ en v1 et 1 en v2 (`Fpmmap`, appel système d'Unix, comme `syscall.Mmap` de Go). Contrôle 62,3 en
  v2 (15e, devant Chapel), 58,5 en v1. FreePascal reste **16e, 48,06 points** [47,1–48,8] (+ 0,62) ; les scores des
  22 autres ne changent pas.
* **Faits de la remarque** (`results/fpc_remark/facts.txt`) : exacts pour l'essentiel. Branche main (instantané
  3.3.1-21612 du 4 novembre) : AVX-512 dans l'assembleur et les cibles, `TParallel.For` (dont le premier appel passe
  parfois sur le seul fil appelant), `pause` dans `TThread.SpinWait` et une procédure `fpc_x86_pause`, 502 intrinsèques
  SSE déclarées sans procédure ; `-Sv` refusé sur les tableaux simples, `__m128` faux en `-CfSSE64`, vecteurs de 256
  bits refusés à l'assemblage, x87 en `-CfX86-64-V4`. Trois réserves : `end align 64` n'est respecté ni sur la pile
  ni par `New` ; `AtomicIncrement` reste un appel à la RTL sans ordre mémoire ; la 3.2.4-rc2 (qui se nomme 3.2.4-rc1)
  n'a pas « les mêmes temps » : `TDictionary` y est 2,5 fois plus rapide sur K7 naturel.
* **Code naturel et FMA** : `High(a)` est un appel en 3.2.2, ce qui garde l'accumulateur de K5 naturel sur la pile ;
  avec `Length(a) - 1` (ou `High` développé en ligne par main), la boucle va 4 fois plus vite et passe à 0,51 fois le
  C : clang fusionne `s += a[i] * b[i]` en une chaîne de `vfmadd` (4 cycles par élément) quand FreePascal garde une
  addition séparée (2 cycles sur Emerald Rapids). Effet sur le score : + 0,15.
* **Noyaux optimisés mieux écrits** : K4 par masque × 0,75 (le gain exige de lire la valeur dans une variable locale ;
  écrit sur `v[i]`, × 1,03), par pointeur × 0,71 ; K5 en `-Sv` par pointeurs × 0,68 ; K8 en arène itérative × 0,38.
  Ensemble + 3,3 points par le plafond (36,3 → 44,6) ; 16e, C# devant dans 63 % des variantes.
* **Versions** : 3.2.4-rc2 47,37 points (16e) ; main, même code 47,62 (16e), avec sa grille (C5 et D5 à 1 ; contrôle
  68,8) 49,89, avec ses meilleures formes 52,64 et les deux 54,92 (**15e**, au score de C#, devant lui dans 62 % des
  variantes). Les queues de latence de K8 naturel (p99,9, max) sortent plus hautes avec la rc2 et main (× 1,6 à 1,9,
  très dispersées) ; sans elles (hors plan), 48,31, 48,37 et 55,66 points.
* **Assembleur** (hors des règles du banc) : K5 optimisé en AVX2 avec la 3.2.2, 1,39 fois le C natif ; en AVX-512 sous
  main, 1,03 fois ; en `-Sv`, 7,7 fois : la règle « pas d'assembleur » coûte plus à FreePascal qu'aux langages dotés
  d'intrinsèques.
