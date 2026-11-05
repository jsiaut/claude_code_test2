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
   par accès et un test d'unicité par ligne (71 ms ; 58 ms en `-Ounchecked`).
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
