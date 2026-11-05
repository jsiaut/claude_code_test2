# Ajout de Swift : un 22e langage, mesuré sur la machine 23 et relié aux données publiées par le C

L'auteur de l'étude m'a demandé le 5 novembre d'ajouter Swift au banc. Ce document décrit la chaîne et les choix
d'implémentation, avec les faits relevés en écrivant le code (section 2). Il fixe le plan avant toute mesure de
campagne (section 3), puis donne les résultats (section 4). Comme pour les remarques, je n'ai consulté aucune page web
pour les faits. Ils viennent de la chaîne installée (Swift 6.4.2, ses modules et ses en-têtes), de sondes, du code
machine produit et de mesures sur la machine 23. Seuls l'archive de la chaîne, sa signature et la liste des versions
(`releases.json`) ont été téléchargés depuis swift.org.

## 1. La demande

« Ajoute le langage Swift au benchmark » : implémenter les dix noyaux de `docs/SPEC.md`, noter la grille de capacités,
mesurer et ranger Swift dans le classement publié avec la même méthode que les 21 autres langages. Une contrainte
pratique pèse sur tout le plan : les données publiées viennent de plusieurs hôtes (machine 1 pour la plupart des
noyaux, machines 3, 11 et 16 pour K5, les latences de K8 et K9), aucun n'est disponible aujourd'hui, et seule la
machine 23 (Cascade Lake, du même modèle que la machine 1) l'est.

## 2. Chaîne, implémentation et faits relevés (avant le plan)

### 2.1 Chaîne

* **Swift 6.4.2** (`swift-6.4.2-RELEASE`, archive Ubuntu 24.04 de 1 124 819 616 octets, SHA-256 `2e9ebec0…ba8c`,
  signature vérifiée : « Swift 6.x Release Signing Key », empreinte 52BB 7E3D E28A 71BE 22EC 05FF EF80 A866 B47A 981F),
  installée dans `/opt/swift`. Le compilateur embarque son propre LLVM (clang 21.0.0 du dépôt swiftlang/llvm-project).
* **Version** : la liste des versions de swift.org date la 6.4.2 du 29 octobre et la 6.4.1 du 12 octobre. Les autres
  chaînes ont été fixées le 28 octobre ; Swift, ajouté le 5 novembre, prend la dernière version stable à cette date.
* **Mode release** : un paquet créé par `swift package init` (tools-version 6.4) se compile par `swift build -c release`
  avec `-O -whole-module-optimization -swift-version 6` (relevé dans la commande, `results/swift_check/facts.txt`).
  `-O` garde les vérifications de bornes et de débordement ; `-Ounchecked` (option documentée) les retire.
* **Banc** : `swiftc -swift-version 6 -O -wmo -target-cpu native -parse-as-library` (`bench/swift/build.sh`). Comme
  `-march=native` ou `target-cpu=native` pour les autres langages, `-target-cpu` est une option documentée de
  `swiftc --help` ; le code produit utilise les registres zmm (FMA sur 512 bits vérifiée dans le désassemblage).
* **Bibliothèques** : bibliothèque standard (dont `_Concurrency` et `Synchronization`) et bibliothèques de base livrées
  avec la chaîne (Foundation, Dispatch). Je les compte comme livrées et documentées, comme la bibliothèque `unix`
  d'OCaml ; aucun paquet (swift-numerics, swift-collections, swift-async-algorithms) : ce sont des dépendances
  tierces au sens de la règle.

### 2.2 Implémentation (`bench/swift/ms.swift`)

Un seul binaire, comme en C et en Rust : le code naturel garde les vérifications de `-O` ; le code optimisé passe par
des pointeurs non vérifiés (`UnsafePointer`, `UnsafeBufferPointer`), des opérateurs qui enveloppent (`&+`, `&*`) et
les types SIMD de la bibliothèque standard.

| Noyau | Naturel | Optimisé |
|---|---|---|
| K1 | `struct Particle` (16 `Float`) dans un `[Particle]`, construit champ par champ (l'ordre des champs n'est pas garanti par le langage) | `aos` : tampon aligné sur 64 o, 8 accumulateurs f64 (SIMD8) ; `soa` : 16 tableaux alignés, `SIMD16<Float>` et `addProduct` (FMA), accumulation f64, réduction en arbre |
| K2 | — | chasse sur `UnsafePointer<UInt32>` |
| K3 | — | `Synchronization.Atomic<UInt64>` dans un bloc aligné sur 128 o (pas de 8 ou 128 o) ; `wrappingAdd(.relaxed)` (`lock inc`) ou `load`/`store(.relaxed)` (`inc` en mémoire) ; 4 `Foundation.Thread` par répétition |
| K4 | `for x in v { if x >= 128 { s += UInt64(x) } }` sur `[UInt8]` | `s &+= UInt64(x) &* UInt64(x >> 7)` sur `UnsafeBufferPointer` |
| K5 | boucle indicée sur `[Float]` | 4 accumulateurs `SIMD16<Float>` (`addProduct`), réduction en arbre |
| K6 | colonnes en `[Int32]` / `[UInt8]`, Q1 dans un `[Q1Agg]` | `SIMD16<Int32>`, prédicat en masques, `replacing(with:where:)` ; Q1 en blocs de 4096 lignes (même algorithme que le C), 6 groupes déroulés ; `mt` : 4 threads |
| K7 | `[UInt32: Agg]`, `m[k, default: Agg()].add(x)` (une recherche, méthode `mutating`) | adressage ouvert, hachage de Fibonacci, sondage linéaire, sans préchargement (absent de Swift, 2.4) |
| K8 | `class Node` à champs `var` (ARC), construit en préordre, libéré dans le chrono | arène : nœuds compacts dans un tampon réutilisé, enfants par indice |
| K9 | `[[Double]]`, harnais commun (grilles allouées une fois, réinitialisées hors chrono, échangées) | tableau plat aligné, `SIMD8<Double>` ; `mt` : 4 threads par itération |
| K10 | `AsyncStream` entre deux tâches d'un groupe (seule file de la bibliothèque standard ; tampon non borné) | anneau SPSC, indices sur des lignes de 128 o, copies locales des indices distants, acquire/release, attente active sans `pause` |

Harnais : horloge `CLOCK_MONOTONIC` comme le C, fichiers lus dans des tampons alignés sur 64 o, `Foundation.Thread`
(qui n'a pas de `join` : un `DispatchSemaphore` en tient lieu). Barrière de K5 : `atomicMemoryFence(ordering:
.acquiring)` (barrière du compilateur, aucune instruction sur x86, comme `BARRIER(a)` en C) et rangement du résultat
dans un atomique en mode relâché (comme `KEEP(d)`) ; K5 naturel prend le temps du C sur la même machine (0,162 s contre
0,171 s), donc l'appel n'est pas sorti de la boucle.

Validation par le pilote (`tools/driver.py --quick`) : 51 cellules (`swift` : 41, toutes les tailles de K2 et
l'empreinte comprises ; `swift_exp` : 1 ; `swift_ou` : 9), sommes de contrôle toutes justes. Empreinte de K1 :
64,02 octets par particule.

### 2.3 La grille (sonde `probes/swift`, 36 lignes, `results/probes/swift.txt`)

| Cat. | Cases |
|---|---|
| A | A1 = 1 (`[struct]` en ligne, stride 64) ; A2 = 1 (ordre déclaré gardé par l'ABI, `MemoryLayout.offset(of:)`, comme Go) ; A3 = 0 ; A4 = ½ (`allocate(alignment: 64)` ; `@_alignment`, non documenté, plafonne à 16) ; A5 = ½ (`bitPattern`, `unsafeBitCast` ; pas d'union brute, comme Go) ; A6 = 0 ; A7 = 1 (`InlineArray`, Swift 6.2) ; A8 = 1 |
| B | B1 = 1 (ARC) ; B2 = ½ (pointeurs bruts, pas d'interface d'allocateur) ; B3 = 1 (`withUnsafeTemporaryAllocation`) ; B4 = ½ (existentiel de plus de 24 o mis en boîte sur le tas, fermetures, copie sur écriture) ; B5 = 1 |
| C | C1 = 1 (`SIMD16`, `addProduct`) ; C2 = ½ (module Clang `_Builtin_intrinsics.intel`, non documenté : intrinsèques à corps seulement) ; C3 mesurée ; C4 = 0 ; C5 = 1 (`DispatchQueue.concurrentPerform`) |
| D | D1 = 1 ; D2 = 1 (`Atomic`, cinq ordres) ; D3 = ½ (`sysconf(_SC_LEVEL1_DCACHE_LINESIZE)` par le module Glibc : requête à l'exécution, ni constante ni type de bourrage) ; D4 = 0 ; D5 = ½ (`atomicMemoryFence`, pas de `pause`) |
| E | E1 = 1 ; E2 = 0 ; E3 = ½ (`_slowPath`, public mais souligné) ; E4 = 0 ; E5 = ½ (exclusivité des `inout`, sans `noalias` dans l'IR) ; E6 = 1 ; E7 = ½ (spécialisation non garantie, pas d'évaluation à la compilation) |
| F | F1 = ½ (`InlineArray` imbriqués de taille fixe) ; F2 = 0 ; F3 = 1 ; F4 = 1 (`Data(contentsOf:options: .alwaysMapped)`, projeté, vu sans copie) |

Règle v2 : aucune case ne change. C2 et E3 passent par un module ou des fonctions non documentés ; les autres
demi-points sont partiels. Pilier C (règle v2, sans C3) : 64,4. Les cases à 0 ou ½ tiennent à des faits exécutés
(2.4).

### 2.4 Faits relevés en écrivant le code (`tools/swift_check/facts.sh`, `results/swift_check/facts.txt`)

1. **Conversions SIMD** : `SIMD16<Int32>(truncatingIfNeeded:)` depuis des octets, ou vers `SIMD16<Int64>`, n'est pas
   inliné. Chaque conversion est un appel de fonction, avec `vzeroupper` et des écritures sur la pile. Écrite voie par
   voie, la même conversion donne `vpmovzxbd` / `vpmovsxdq`.
2. **Comparaisons vecteur contre scalaire** : `v .== 3` est compilé voie par voie, avec des branchements (44
   instructions et 3 branchements, contre 14 sans branchement pour `v .== SIMD16(repeating: 3)`). Q1 optimisé passait
   de 39 ms à 1,79 s.
3. **`InlineArray` de 6 accumulateurs SIMD** : la boucle sur les groupes n'est pas déroulée et les accumulateurs restent
   en mémoire. Q1 optimisé : 82 ms ; déroulé à la main, 39 ms (C : 42 ms sur la même machine).
4. **`sum()` d'un vecteur** : somme dans l'ordre des voies (15 `vaddss`). Le code optimisé réduit en arbre par moitiés
   (4 `vaddps`), comme `_mm512_reduce_add_ps`.
5. **Intrinsèques** : `import _Builtin_intrinsics.intel` donne les intrinsèques qui ont un corps (`_mm512_add_ps`,
   `_pext_u32`, `_lzcnt_u32`). Celles qui n'en ont pas sont inutilisables : `_mm_pause` est appelée comme une fonction
   externe (`undefined reference`), `_m_prefetchw` disparaît du code produit sans message. `_mm_prefetch` est une
   macro, refusée. Swift n'a donc ni préchargement (K7 optimisé n'en a pas) ni `pause` (K10 optimisé attend sans).
6. **Module Glibc** : il n'expose pas les extensions GNU (`sched_setaffinity`, `sched_getcpu`, `gettid`,
   `mallinfo2`). Aucune affinité n'est donc possible avec la chaîne livrée.
7. **`inout`** : pas de `noalias` dans l'IR. L'exclusivité reste une règle du langage, exploitée par l'optimiseur SIL,
   pas par LLVM.
8. **Vérifications de `-O`** : K4 naturel reste scalaire, avec un branchement par octet et le piège de débordement
   (72 à 80 ms contre 3,5 ms pour le C, qui vectorise ; 15 ms en `-Ounchecked`). K9 naturel garde un test de bornes
   par accès et un test d'unicité par ligne (71 ms ; 58 ms en `-Ounchecked`). [Corrigé après les mesures (4.6) : le
   test d'unicité est fait à chaque écriture, pas à chaque ligne.]
9. **K8 naturel** : une classe finale à champs `let`, construite de bas en haut, est 25 à 35 % plus rapide que la
   classe à champs `var` (moins de comptages de références).
10. **`AsyncStream`** : chaque élément suspend puis reprend la tâche consommatrice (réveil d'un thread du pool de
    libdispatch). Pour 2^22 éléments : 14 à 19 s, contre 0,99 s pour la file `pthread` du C ; 9,6 s de temps
    utilisateur, 5,8 s de temps système, 388 000 changements de contexte volontaires. K10 est hors score depuis la v2.

## 3. Plan (poussé avant les mesures)

### 3.1 Ce qui entre dans le classement publié

* **Swift, 22e langage classé** (`RANKED`, en dernier) : ses temps reliés aux données publiées par le pont du C (3.2),
  sa grille (2.3, `analysis/capabilities.py`), sa vectorisation mesurée (C3, `tools/c3_measure.py swift`) et son
  empreinte (`results/raw_post/swift.jsonl`, étiquette `post_fp2`, puis `analysis/footprint.py`).
* **Les 21 autres langages** : leurs données ne changent pas. Leur score ne bouge que par Swift lui-même : références
  t* quand Swift est le plus rapide sur une mesure, rangs, étages.
* **Réplication (machine 3)** : Swift y entre par le même pont, avec le C de la machine 3. Ce n'est pas une
  réplication indépendante pour Swift ; le rapport le dit.

### 3.2 Le pont par le C

Pour chaque clé k du score (mesures de E et de D1, K1 `natural_shuffled`, K2 tuned aux trois tailles de D4) : chaque
processus de Swift sur la machine 23 est multiplié par f(k) = G(C publié, k) / G(C machine 23, k), où G est la moyenne
géométrique des médianes de processus. « C publié » désigne la clé du C telle que le calcul publié l'utilise. Les
sources sont donc la machine 1 pour K1 à K4 et K6 à K8 (même modèle que la 23), la machine 3 pour K5, la machine 16
pour K9 (Emerald Rapids). Latences de K8 naturel (D3, machine 11, Emerald Rapids) : chaque colonne [p50, p90, p99,
p99,9, max] est multipliée par le rapport des médianes du C, colonne par colonne. Les processus de Swift gardent leur
propre dispersion. Le binaire C mesuré sur la machine 23 est `bench/c/ms`, identique octet pour octet à une
recompilation sur cet hôte. C'est la construction Cascade Lake des données de la machine 1, et la source du K9 publié
du C (harnais inchangé).

Le pont est fait dans `analysis/analyze_v2.py` (après toutes les corrections du jeu publié), si bien que les sorties
publiées, la réplication et les scripts d'état actuel voient Swift de la même façon.

**Tirages isolés.** Les tirages du bootstrap et des latences de Swift viennent de leur propre générateur (graine SEED
+ 2402). Ses résidus n'entrent pas dans les réservoirs des autres. Il est le dernier de `RANKED`, donc ses bruits de
jugement de la grille sont tirés après ceux des autres. C'est la règle de la remesure de D2 et D4 (`docs/CPP.md`) :
les tirages des 21 autres langages ne changent pas. Contrôle : le calcul avec Swift retiré doit reproduire à
l'identique le classement d'avant (L-E de `results/lua_check.json`).

### 3.3 Copies

* `bench/swift` : le banc publié.
* `bench/swift_exp` : le même code, plus la variante K8 `natural_fl` (classe finale à champs `let`, construite de bas
  en haut) ; même binaire pour la base de la sensibilité.
* `bench/swift_ou` : le source de `bench/swift` compilé en `-Ounchecked`.

### 3.4 Mesures (`tools/measure_swift.py`, machine 23)

73 cellules en 7 passes (511 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20263105) :
* `swift` et `c` (témoin du pont) : les 31 cellules du classement et de K10 (K1 : 4 ; K2 tuned à 16 Kio, 256 Kio et
  8 Mio ; K3 : 4 ; K4 : 3 ; K5 : 2 ; K6 : 6 ; K7 : 2 ; K8 : 2 ; K9 : 3 ; K10 : 2) ;
* `swift_exp` : K8 `natural` et `natural_fl` ;
* `swift_ou` : les 9 cellules naturelles du score (K1 `natural` et `natural_shuffled`, K4, K5, K6 Q6 et Q1, K7, K8,
  K9).

Répétitions : celles de `results/calib.json` pour le C. Pour Swift, la règle du pilote (3 s divisées par le temps
d'une répétition, entre 3 et 10 ; 2 au-delà de 5 s), appliquée à une répétition de calibration faite au début et
écrite dans `results/calib.json`. Les copies prennent les répétitions de la cellule d'origine. Échauffement : 1 (code
compilé à l'avance) ; règle de vol du pilote. Puis l'empreinte (3 processus) et C3 (`tools/c3_measure.py swift`).
Rien d'autre ne tourne. Sortie : `results/raw_swift/`.

### 3.5 Scénarios (`analysis/swift_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | le classement publié à 21 langages (L-E de `results/lua_check.json`) ; le calcul avec Swift retiré doit le reproduire à l'identique |
| **S-E (publié)** | Swift ajouté : pont par le C (3.2), grille, empreinte, C3 mesurée |
| S-direct | information : les temps de Swift de la machine 23 sans pont pour les clés de la machine 1 (même modèle) ; pont gardé pour K5, K9 et les latences (autre modèle) |
| S-K8fl | S-E ; K8 naturel (temps et latences) × r(`natural_fl` / `natural`, tous deux de `swift_exp`) |
| S-Ou | S-E ; les 9 cellules naturelles × r(`swift_ou` / `swift`) |
| S-cases-bas | S-E ; A2 = ½ (ordre des champs sans garantie du langage), C5 = ½ et F4 = ½ (Dispatch et Foundation hors bibliothèque standard), D3 = 0 (une requête n'est ni constante ni type de bourrage) |
| S-cases-haut | S-E ; C2 = 1, E3 = 1, E5 = 1 |
| S-tout-bas, S-tout-haut | S-cases-bas ; S-K8fl, S-Ou et S-cases-haut |

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap ; latences : médiane de toutes les
répétitions, colonne par colonne ; sensibilités en min(1, r). Pour chaque scénario : score, piliers, rang espéré de
Swift, ses voisins et les probabilités de précédence ; rangs espérés des 21 autres et leurs écarts à « Avant ».
Information : le rapport Swift / C de chaque cellule sur la machine 23, et K10. Sorties : `results/swift_check.json`,
`results/report_swift.md` ; puis régénération des sorties publiées (réplication comprise) et de l'état actuel.

### 3.6 Ce qui change ailleurs

`analysis/analyze.py` (`RANKED`), `analysis/analyze_v2.py` (pont, groupe de backend LLVM, noms), `analysis/analyze_v3.py`
(tirages isolés, réplication), `analysis/capabilities.py` (fait), `analysis/report.py` et `analysis/capabilities_md.py`
(noms, ordre). `analysis/nosimd_check.py` : variantes SIMD de Swift classées V (K1 `aos` et `soa`, K5, Q6 et Q1 tuned,
K9 tuned). Confrontation : Swift n'est pas dans l'étude « Banc », il sort des tests qui comparent à elle, et c'est
signalé. `tools/c3_measure.py` (liste), graphiques. Texte : README (22 langages, tableau, paragraphe de Swift),
FINDINGS, METHODOLOGY (journal), `docs/NATURAL.md` (fait), CAPABILITIES (régénéré).

### 3.7 Ce que je ne fais pas

* Pas de mesure sur un Emerald Rapids (aucun disponible) : le pont de K5, de K9 et des latences de K8 traverse les
  modèles. La remarque sur C3 a montré qu'il peut s'y tromper (K9) ; c'est écrit dans les limites.
* Pas de paquet (swift-numerics, swift-collections, swift-async-algorithms), pas d'Embedded Swift, pas de
  `-Ounchecked` dans le classement publié (sensibilité S-Ou seulement), pas de Swift sur macOS.
* K10 est mesuré (information) et reste hors score ; pas de sensibilité sur sa file.

## 4. Résultats (après les mesures)

Mesures du 5 novembre, de 16:05:35 à 16:27:22, sur la machine 23 : 511 processus (73 cellules, 7 chacune), aucune
somme de contrôle fausse ; neuf processus refaits pour vol de temps, aucun gardé au-dessus de 2 % (vol médian 0,31 %).
Empreinte de K1 : 64,02 octets par particule (3 processus). C3 mesurée : 0 (boucles chaudes de K4 et de K9 naturels
scalaires, `results/vectorization/swift_*.txt`). Analyse : `analysis/swift_check.py` (`results/report_swift.md`), puis
les sorties publiées régénérées. Contrôle : le scénario Avant (Swift retiré) reproduit le classement publié d'avant
(L-E de `results/lua_check.json`) à l'identique (écart 0,0), et les états actuels de la sensibilité sans SIMD et de la
remarque sur C reproduisent S-E à l'identique : les tirages des 21 autres langages ne changent pas.

### 4.1 Swift face au C, sur le même hôte

Moyenne géométrique des médianes de 7 processus ; intervalle à 95 % par bootstrap.

| Cellule | Swift (ms) | C (ms) | Swift / C |
|---|---|---|---|
| K1 natural | 29,2 | 31,1 | 0,94 [0,87–1,02] |
| K1 natural_shuffled | 31,3 | 28,6 | 1,09 [1,00–1,19] |
| K1 aos | 30,5 | 27,3 | 1,12 [1,05–1,18] |
| K1 soa | 5,24 | 5,53 | 0,95 [0,91–0,99] |
| K2 tuned 16 Kio / 256 Kio / 8 Mio | 6,77 / 20,4 / 602 | 6,63 / 19,4 / 540 | 1,02 / 1,05 / 1,11 |
| K3 rmw_packed / rmw_padded | 2 745 / 236 | 2 667 / 239 | 1,03 / 0,99 |
| K3 sw_packed / sw_padded | 89,4 / 80,1 | 88,9 / 79,5 | 1,01 / 1,01 |
| K4 natural_unsorted | 76,6 | 2,62 | **29,3 [24,1–35,3]** |
| K4 natural_sorted | 7,80 | 2,61 | 2,99 [2,51–3,63] |
| K4 branchless_unsorted | 2,78 | 2,38 | 1,17 [0,97–1,41] |
| K5 natural / tuned | 165 / 6,69 | 165 / 6,27 | 1,00 / 1,07 [0,94–1,22] |
| Q6 natural / tuned / mt | 55,9 / 13,6 / 4,44 | 51,4 / 14,6 / 5,09 | 1,09 / 0,93 / 0,87 |
| Q1 natural / tuned / mt | 92,1 / 36,0 / 11,0 | 63,2 / 24,6 / 8,27 | **1,46 / 1,47 / 1,33** |
| K7 natural / tuned | 2 115 / 306 | 671 / 268 | **3,15 [2,82–3,52]** / 1,14 [1,03–1,27] |
| K8 natural / tuned | 1 870 / 222 | 772 / 219 | **2,42 [2,21–2,65]** / 1,02 |
| K9 natural / tuned / mt | 75,6 / 24,8 / 9,70 | 25,4 / 24,7 / 8,69 | **2,98 [2,78–3,19]** / 1,00 / 1,12 |
| K10 natural / tuned (hors score) | 14 151 / 29,7 | 888 / 34,1 | 15,9 / 0,87 [0,55–1,31] |

* **Code optimisé** : 0,87 à 1,17 fois le temps du C, sauf Q1 (1,47, et 1,33 en `mt`) ; K7 (1,14) n'a pas de
  préchargement (2.4, point 5). Q1 : sans accès aux masques de bits (ni compte des bits d'un `SIMDMask`, ni conversion
  entre largeurs de voies), le compte des lignes demande un accumulateur vectoriel de plus par groupe et la colonne
  des charges des comparaisons 64 bits élargies : 36 vecteurs vivants pour 32 registres zmm, 74 accès à la pile par
  tour de 16 lignes (le C tient ses comptes dans des registres généraux par `popcnt` du masque).
* **Code naturel** : au niveau du C pour K1, K5 et Q6 ; derrière lui partout où les vérifications de `-O`, ARC ou la
  table de la bibliothèque pèsent : K4 (29 fois : branchement par octet et piège de débordement ; 5,8 fois plus vite
  en `-Ounchecked`), Q1 (1,46 : vérifications de bornes et de débordement dans la boucle ; 0,73 en `-Ounchecked`), K7
  (`Dictionary` à SipHash, 3,2 fois la table chaînée du C), K8 (classe à champs `var` : 2,4 fois `malloc`/`free`), K9
  (`[[Double]]` vérifié à chaque accès, 3,0 fois le tableau 2D du C ; 0,83 en `-Ounchecked`).
* **Latences de K8 naturel** : p50 101 µs, p99,9 372 µs, max 1,78 ms (C : 38, 189 et 1 561 µs) ; ARC libère chaque
  arbre dans le chrono, sans pause de ramasse-miettes.

### 4.2 Le pont et le classement publié (S-E)

Les facteurs du pont (C publié / C machine 23) valent 0,92 à 1,76 sur les clés de la machine 1, 7,6 sur K7 naturel
(la table chaînée du C prenait 5,1 s sur la machine 1 contre 0,67 s ici ; tous les K7 naturels de la machine 1 sont
lents, de 1,6 s pour Zig à 10,5 s pour C++), 0,63 sur K5 tuned (machine 3) et 0,55 à 0,64 sur K9 (machine 16).

**Classement publié (S-E)** : Swift **12e** sur 22, **65,24 points** [63,97–66,40], rang espéré 11,01, rang plausible
6 à 14. Contrôle 64,4 (14e), plafond 79,4 [77,2–81,5] (6e, dans le paquet de Chapel, Odin, C++ et D, 79,2 à 80,1),
code par défaut 43,8 (12e ; D1 0,073, 17e ; D2 0,95 ; D3 0,50 ; D4 0,92). Fortran (11e, 65,4) le devance dans 52 % des
variantes ; Swift devance Julia (13e) dans 61 % et Mojo dans 77 %, Chapel dans 28 %, Ada dans 21 %. Plafond par noyau :
K1 0,98 (3e), K3 0,97, K4 0,86, K5 0,94, K6 0,78, K7 0,88, K8 0,40 (comme le C, 0,41), K9 0,76.

**Ce que Swift change pour les autres** : aucun score publié (dans la configuration principale, Swift n'est le plus
rapide sur aucune mesure : les références t* ne bougent pas) et aucun ordre : les 21 gardent le leur. Ceux qu'il
devance presque toujours reculent d'un rang (C# 15e, Java, Go, Haskell, OCaml, JavaScript, Python, Lua 22e) ; les
rangs espérés de Mojo (+0,83), Julia (+0,55), Fortran (+0,50), Chapel (+0,37), Ada, Nim, Zig et Rust (+0,13 à +0,23)
montent un peu. Swift a le 2e K1 naturel (38,9 ms, derrière C++ à 37,5) : dans les tirages où il passe devant, il
devient la référence du code naturel de K1, ce qui déplace les précédences entre les autres de 2,4 points au plus (D
devant Chapel dans 68,4 % des variantes au lieu de 66,0), sans changer d'ordre. Ses autres codes naturels sont loin :
K4 20e, K5 17e, Q6 11e, Q1 14e, K7 20e, K8 18e, K9 12e.

### 4.3 Sensibilités (plan 3.5)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|---|
| **S-E (publié)** | 65,24 | 64,4 | 79,38 | 43,8 | 11,01 | 12e | 6–14 |
| S-direct (information) | 67,63 | 64,4 | 83,84 | 46,2 | 6,94 | 6e | 1–13 |
| S-K8fl | 65,65 | 64,4 | 79,38 | 45,5 | 11,02 | 12e | 6–14 |
| S-Ou | 65,57 | 64,4 | 79,38 | 45,1 | 10,55 | 11e | 5–14 |
| S-cases-bas (= S-tout-bas) | 62,85 | 57,6 | 79,38 | 43,8 | 12,04 | 13e | 7–15 |
| S-cases-haut | 66,61 | 68,3 | 79,38 | 43,8 | 10,32 | 11e | 5–14 |
| S-tout-haut | 67,38 | 68,3 | 79,38 | 46,9 | 9,77 | 11e | 5–13 |

* **S-K8fl** : la classe finale à champs `let` va 0,67 fois plus vite [0,61–0,74] (latences × 0,69 à 0,86) ; +0,4 point.
* **S-Ou** : `-Ounchecked` ramène K4 naturel à 0,17, Q1 naturel à 0,73, K9 naturel à 0,83 ; +0,3 point, 11e.
* **Cases** : de 62,9 (13e) à 66,6 (11e) selon que Foundation et Dispatch comptent comme livrés ou non, et selon la
  note des intrinsèques importées, des indications de branchement et du non-aliasing.
* **S-direct** n'est pas une estimation : la machine 1 était plus lente que la machine 23 pour tous les codes (4.4),
  et prendre les temps de la machine 23 tels quels avantage Swift de 4,5 points de plafond.
* **Sans SIMD explicite** (`docs/NOSIMD.md`, 4.18) : toutes les variantes optimisées de Swift sont écrites avec ses
  types SIMD ; sans elles, il retombe sur son code naturel (plafond 33,7, 13e), comme Mojo ; en lecture symétrique
  (K1 `aos` et naturels), 60,2 points, 13e.

### 4.4 Le pont à l'épreuve (hors plan, information)

Ajouté après avoir vu les facteurs du pont. La remarque sur Lua a mesuré sur la machine 23 le code publié de Lua, de
LuaJIT et de Python. Ces 21 couples (langage, clé) donnent chacun un facteur d'hôte (publié / machine 23), comparable
à celui du C :

* **La machine 1 était plus lente que la machine 23 pour tous les codes**, interprétés compris : facteur médian 1,28
  (1,10 à 1,78). Prendre les temps de Swift tels quels (S-direct) l'avantage donc à tort.
* **Clés mono-thread de la machine 1** : le facteur du C suit celui des autres à ±20 % près (K1 `soa` 1,40 contre
  1,36 ; Q6 naturel 1,25 contre 1,26 ; K7 tuned 1,70 contre 1,78 ; K8 naturel 1,26 contre 1,28 à 1,49 ; K4 1,20 à
  1,54 contre 1,27 à 1,38).
* **Il s'en écarte sur K3** (0,75 à 1,76 contre 1,23 à 1,48 : placement des threads), **Q6 `mt`** (1,68 contre 1,32)
  et surtout **K9**, venu d'Emerald Rapids (0,55 et 0,64 contre 1,17 et 1,08 pour Lua) : le rapport au C d'un code
  limité par la mémoire ne se transporte pas tel quel d'un modèle à l'autre (déjà vu pour C3).

**S-hôte** remplace le facteur du C par le facteur médian des autres langages, par machine source (1,282 pour la
machine 1, 1,126 pour la machine 16 ; K5 et latences de K8 : pont du C, faute d'autre donnée) : **60,77 points, 13e**
(rang espéré 12,25, rang plausible 8 à 15 ; plafond 69,9). Swift y gagne K1 et K7 (il devient la référence de ces deux
noyaux, 1,0) et perd K3 (0,57) et K9 (0,40). Les deux lectures défendables du pont placent donc Swift 12e ou 13e ;
S-direct (6e) n'en est pas une.

### 4.5 Réplication (machine 3)

Swift y entre par le même pont, avec le C de la machine 3 (plan 3.1) : ce n'est pas une réplication de Swift, seulement
le report sur Emerald Rapids de ses rapports au C mesurés sur Cascade Lake. Il y est **12e** (54,7 points), comme sur la
machine 1. Son plafond y tombe à 53,9 (11e), parce que le pont lui transmet ce qui est propre au C sur cet hôte :
l'écrivain unique de K3, que le placement du code y rend lent pour le C (plafond de K3 : 0,17 pour l'un comme pour
l'autre), et K9 (0,49, contre 0,52 pour le C). Il garde ses huit noyaux de plafond.

* **Accord entre machines** (sur les 21 langages répliqués indépendamment, 4.6) : inchangé, Spearman 0,93 / 0,72 /
  0,30 et 19 inversions parmi les 13 premiers ; le test nul aussi.
* **Étages de la v3** : [14, 4, 1, 3] au lieu de [13, 4, 1, 3] ; Swift rejoint le premier (de C à Mojo), les trois
  autres ne changent pas.
* **Hors plan de la v3** : « Cascade Lake seul » (K5 des machines 1 et 2, K9 au harnais d'origine), Swift 12e (plafond
  79,0) ; estimateur de la v2, 12e ; rangs compatibles avec les paires établies, 4 à 14 au score et 1 à 11 au plafond,
  et 17e, seul rang possible, pour son code naturel D1 (7,3, le plus lent des 14 premiers).

### 4.6 Écarts au plan et corrections

* **Accord entre machines et test nul sur 21 langages** (écrit pendant la campagne, poussé avant les données, commit
  3db2ef6) : le plan disait que la réplication de Swift n'est pas indépendante (3.1), sans dire comment l'accord la
  traite. L'y compter aurait mêlé à l'accord des mesures une concordance construite par le pont ; l'accord, le test nul
  et ses seuils portent donc sur les 21 langages répliqués indépendamment. Les rangs publiés de la machine 3 comprennent
  Swift.
* **« Cascade Lake seul »** (calcul hors plan de la v3 ; écrit avec l'intégration, avant les données) : Swift y prend K5
  et K9 par le même pont, relié au C de ces données (K5 des machines 1 et 2, K9 de Cascade Lake), ses latences restant
  celles du calcul principal.
* **Bornes physiques du pont** (corrigé après le premier calcul avec les données) : les clés de Swift reliées à la
  machine 3 étaient contrôlées avec les bornes de la machine 1. Son K1 `soa` relié (2,8 ms) passait sous la borne de
  la machine 1 et était écarté : plafond 39,1 sur la machine 3 et étages [18, 1, 3]. Les clés reliées sont désormais
  contrôlées avec les bornes de l'hôte des données cibles (machine 3 pour la réplication, machine 1 pour « Cascade
  Lake seul »), comme celles des autres langages ; aucune n'est plus écartée, ni dans le calcul publié ni dans la
  réplication (29 clés sur chaque hôte).
* **S-hôte** (4.4) : hors plan, ajouté après avoir vu les facteurs du pont ; information, sans effet sur le classement
  publié.
* **Q1 optimisé du C** : avant le plan (2.4, point 3), je comparais Q1 de Swift (39 ms) à un seul processus du C
  (42 ms). La campagne donne au C 24,6 ms (7 processus) : Swift y est à 1,47 fois le C, pas au même niveau.
* **Point 8 de 2.4** : le test d'unicité du stencil naturel est fait à chaque écriture, pas à chaque ligne. Le profil
  du binaire mesuré (`results/vectorization/swift_k9.txt`, 48 % des échantillons) montre l'appel à
  `swift_isUniquelyReferenced_nonNull_native` dans la boucle interne, entre les tests de bornes de chaque accès.
* **Chiffres du README sur « les 13 premiers »** : ils portaient sur les langages classés devant C#, au nombre de 13
  avant Swift ; `analysis/readme_figures.py` les calcule désormais sur les langages classés devant C#, 14 avec Swift
  (part des écarts de score expliquée par le contrôle : 74 % ; voisins : 46 à 75 % ; tous devant C# dans au moins
  96 % des variantes).

### 4.7 Bilan

Swift entre **12e sur 22 (65,2 points)**, entre Fortran et Julia, dans le premier étage. Son profil est singulier : le
6e plafond, avec des types SIMD dans la bibliothèque standard qui mettent la plupart de ses noyaux optimisés au niveau
de ceux du C (0,87 à 1,17 fois leur temps, sauf Q1) ; mais le contrôle d'un langage applicatif (14e : ni préchargement,
ni `pause`, ni affinité, ni assembleur) et un code par défaut que les vérifications de `-O` et ARC ralentissent (12e ;
son code naturel est le plus lent des 14 premiers). Sa place dépend d'abord du pont : par le facteur du C, 12e ; par
le facteur d'hôte des autres langages, 13e ; sans pont, 6e, mais cette lecture l'avantage à tort. Les sensibilités du
plan le placent de la 11e à la 13e place. Les 21 autres langages gardent leur ordre et leurs scores. Comme le pont
traverse les modèles de processeur pour K5, K9 et les latences de K8, une mesure de Swift sur un Emerald Rapids et une
relecture par un connaisseur restent à faire.
