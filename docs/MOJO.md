# Remarque sur Mojo : cinq cases de la matrice, un plafond de K4 qui mesure le vectoriseur, et un diagnostic à corriger

Remarque transmise par l'utilisateur le 30 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).
L'auteur de la remarque a mesuré ses propres reproductions des noyaux sur un Cascade Lake ; je n'ai pas son code.
Toutes les vérifications ci-dessous sont les miennes : Mojo 1.2.0 (2016d0cd), ses sources au tag `mojo/v1.2.0`
(`/opt/src/modular`), et la machine 6.

## 1. Ce que dit la remarque

* **Ce qui est juste** : pas de threads publics ni de `parallelize` dans `std` (passé dans le paquet MAX à la 1.0) ;
  ni `mmap`, ni affinité CPU, ni constante de ligne de cache ; aucune boucle naturelle vectorisée, et c'est voulu (le
  vectoriseur de boucles de LLVM n'est pas dans la chaîne de passes de Mojo) ; `Optional[OwnedPointer[Node]]` est
  refusé (le contournement de K8 est légitime) ; le SIMD explicite de K5 donne le même code que clang.
* **(1) Quatre erreurs de fait dans la matrice** : A4 (0,5 → 1, `@align(N)`), A5 (0,5 → 1, `UnsafeUnion`), C4 (0 →
  0,5, `FastMathFlag` sur `fma` seulement), E5 (0,5 → 1, `unsafe_as_noalias`). Deux cases de jugement qui s'annulent
  presque : D5 → 1 (`fence`, `pause` par `llvm_intrinsic`, `SpinWaiter`) et B4 → 0,5 (une erreur levée porte une
  chaîne et une trace de pile ; les coroutines allouent sur le tas).
* **(2) Un biais de méthode : K4 dans le plafond.** La spécification n'admet pour K4 que deux formes scalaires : son
  plafond mesure donc le vectoriseur automatique, déjà compté dans le code par défaut. En SIMD explicite, Mojo ferait
  K4 en 1,1 ms à chaud (2,2 ms caches vidés), contre 2,8 ms pour le meilleur C ; la borne physique de K4 (1,68 ms)
  rejetterait le premier temps, alors que les 16 Mo de K4 tiennent dans les 33 Mo du L3.
* **(3) Un diagnostic du README à corriger** : les 262 ms du stencil naturel viennent des vérifications de bornes de
  `List`, actives par défaut (227 → 38,7 ms avec `-D ASSERT=none` ; Q1 naturel 186 → 59 ms), pas de l'absence de
  vectorisation ; Mojo écrit la position dans le source sur la pile avant chaque comparaison de la boucle chaude.
* **(4) Point mineur** : sur Emerald Rapids, K5 optimisé est 35 % plus lent en Mojo qu'en C, à code identique ;
  l'auteur n'a pas pu le vérifier.
* **(5) La règle « bibliothèque standard seule »** pénalise Mojo depuis la réorganisation de juillet 2026, qui a
  déplacé `parallelize` vers MAX : le README devrait le dire.
* Effet estimé (score ponctuel) : 60,0 (13e) ; 62,2 avec la matrice ; 64,5 (11e) sans K4 dans le plafond ; 66,7
  (11e) avec les deux ; 67,7 (10e) avec K4 en SIMD explicite admis pour tous.

## 2. Vérifications faites avant ce plan (machine 6)

**Machine 6.** Le conteneur a redémarré à 17 h 39 sur un nouvel hôte Cascade Lake du même modèle que les machines 1,
2, 4 et 5 (modèle 85, révision 7, 4 vCPU, 16 Go ; latence à 4 Mio 43 ns, débit DRAM 10 Go/s :
`results/hw/machine6/`). Le binaire de Mojo du banc (`bench/mojo/ms`) était encore celui compilé pour la machine 3 ;
recompilé par son script inchangé, il est identique octet pour octet au binaire de la campagne compilé sur la
machine 2 (empreinte `aae62075…`, `results/hw/machine3/binaries.txt`).

Sondes et code machine : `tools/mojo_check/`, `results/mojo_check/probes.txt` et `results/mojo_check/binaries.txt` ;
sonde des errata : `probes/mojo/probe_errata.mojo` (aucune divergence avec la matrice corrigée, 166 lignes de sonde).

* **Ce que la remarque tient pour juste est exact.** `LLVMPassesPipeline.cpp` (tag `mojo/v1.2.0`) ajoute le
  vectoriseur SLP et `VectorCombine`, jamais `LoopVectorizePass`. Les notes de version disent que `parallelize()` est
  passé dans MAX à la 1.0 (bêta 1), et qu'à la 1.1 l'API de tâches de `std.runtime.asyncrt` est devenue privée
  (`_asyncrt`) parce que « le support async de Mojo est inachevé » ; `async def` compile avec un avertissement du
  compilateur (« expérimental et instable […] ne pas utiliser en production »).
* **A4** : `@align(64)` (depuis la 26.2) donne `align_of` = 64 ; 128 objets sur la pile, 50 allocations et une
  `List` sur le tas, tous alignés sur 64 octets. **Erratum : 1.**
* **A5** : `UnsafeUnion[Float32, UInt32]` (`std.ffi`) fait 4 octets et rend les bits de 1.0f. **Erratum : 1.**
* **C4** : `FastMathFlag.REASSOC` existe, mais seule `SIMD.fma` prend le drapeau (IR : `call reassoc float
  @llvm.fma.f32`) ; l'option globale `--fp-mode` ne règle que la contraction. C'est un contrôle local partiel, comme
  la réduction sans ordre de la Vector API de Java (0,5). **Erratum : 0,5** (la note 0 disait « aucun contrôle local
  trouvé »).
* **D5** : `fence()` donne `lock or` ; `SpinWaiter` (`std.utils.lock`, d'où le banc importe déjà `BlockingSpinLock`)
  appelle le runtime, qui exécute `pause` du 4e au 63e appel puis cède la main : c'est l'attente active de la
  bibliothèque standard, comme `SpinWait` de C# (1). `pause` s'obtient aussi par `llvm_intrinsic`. **Erratum : 1**
  (la note disait « pas d'indication pause »).
* **E5** : `Pointer.unsafe_as_noalias()` (`std.memory`) existe et l'optimiseur s'en sert : après `a[0] = 1 ;
  b[0] = 2`, la lecture de `a[0]` devient la constante 1. Mais dans une boucle `a[i] += b[0]`, `b[0]` est relu à
  chaque tour avec ou sans la conversion. C'est un équivalent déclaré de `restrict`, exploité en partie.
  **Erratum : 1**, avec cette réserve.
* **B4 (jugement)** : une erreur levée n'alloue pas : 1 000 levées, message littéral ou formaté, donnent 6
  allocations en tout, au premier passage ; la trace de pile n'est capturée que si `MODULAR_DEBUG=stack-trace-on-error`
  est défini. Les tâches async allouent (1,5 à 1,8 allocation par tâche), mais l'async est expérimental selon le
  compilateur et privé dans `std`. Les fermetures déclarent leurs captures et les portent dans une valeur.
  **B4 reste à 1** ; la note de la remarque (0,5) devient un scénario de sensibilité.
* **(3) K9 naturel** : dans le binaire de la campagne, chaque vérification de bornes de la boucle chaude est précédée
  de six écritures sur la pile (dont les constantes `$0x6` et `$0x27`) : 6 comparaisons et 36 écritures par point.
  Mesure isolée, indicative : 168 à 180 ms par défaut, 37 à 47 ms avec `-D ASSERT=none` ; Q1 naturel 136–197 →
  57–63 ms.
* **(2) K4 en SIMD explicite** (`bench/mojo_exp` : 64 octets par tour, `vpminsb` puis élargissements) : 2,0 à 2,3 ms
  à chaud, 2,1 à 2,3 ms caches vidés (mesure isolée), pas 1,1 ms. Sur la machine 6, une boucle de type K4 écrite en
  C traite 16 Mio à 6,7–7,6 Go/s et 4 Mio à 20 Go/s : ces 16 Mio ne restent pas dans le L3 d'une passe à l'autre.
* **Borne physique de K4** : 16 Mio à 10 Go/s, soit 1,68 ms. Sur la machine des données principales, le débit mesuré
  à 16 Mio était celui de la DRAM (9,86 Go/s, `results/hw/bw.txt`) : la borne y était cohérente, et aucune mesure de
  K4 n'en approchait (la meilleure : 2,85 ms). Sur les machines 4 à 6, le test de débit voit 23 à 29 Go/s à 16 Mio :
  là, la borne pourrait rejeter un temps valide. Elle dépend de l'hôte ; je la garde pour les données principales,
  et je le dis.
* **(2) K4 et le double compte : exact sur le principe.** La spécification ne donne à K4 que deux formes scalaires
  (`docs/SPEC.md`) ; son plafond mesure ce que le compilateur fait d'une boucle scalaire, comme le code par défaut (K4
  naturel, dans D1). C'est un choix de méthode de la spécification, pas une erreur d'implémentation ; il pèse sur
  tous les langages sans vectoriseur automatique pour cette boucle (Mojo, Zig 0.17, Go, C#, Java, Haskell, OCaml,
  JavaScript, Lua, Python).
* **(4) K5 sur Emerald Rapids** : mes données le confirment (5,20 ms contre 3,94 ms pour C, +32 %) ; sur Cascade Lake,
  Mojo n'était pas plus rapide (5,99 contre 5,78 ms, mesure v1). Sans la machine 3, je ne peux pas aller plus loin.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune aux remarques

Les errata de faits et les erreurs de mon implémentation entrent dans le classement publié ; une optimisation nouvelle
ou un changement de méthode reste une analyse de sensibilité (`docs/FORTRAN.md`, 3.1).

### 3.2 Errata de la matrice (vérifiés ci-dessus)

| Case | Avant (v1 et v2) | Après (v1 et v2) |
|---|---|---|
| A4 alignement | 0,5 | 1 : `@align(64)`, respecté sur la pile et le tas |
| A5 unions | 0,5 | 1 : `UnsafeUnion` |
| C4 réassociation | 0 | 0,5 : `FastMathFlag.REASSOC`, sur `fma` seulement |
| D5 barrières, attente active | 0,5 | 1 : `fence`, `SpinWaiter` (`pause`) |
| E5 non-aliasing | 0,5 | 1 : `unsafe_as_noalias` |
| B4 allocations cachées | 1 | inchangé (0,5 en sensibilité) |

La règle du standard (confrontation) n'a pas de cas particulier pour ces cases : elles y prennent les mêmes valeurs.

### 3.3 Mesures (diagnostics, hors classement)

`tools/measure_mojo.py`, machine 6 : `mojo` (binaire de la campagne) sur K4 naturel, trié et sans branchement, K9
naturel, Q1 et Q6 naturels ; `mojo_noassert` (même source, `-D ASSERT=none`) sur les mêmes clés sauf K4 trié ;
`mojo_exp` sur K4 `simd_unsorted`, `simd_cold` (caches vidés par 64 Mio écrits avant chaque répétition, hors chrono)
et K4 sans branchement ; C par clang (témoin) sur K4 naturel et sans branchement, K9 naturel et Q1 naturel. 18
cellules, 7 processus par cellule en 7 passes, ordre tiré au hasard (graine 20261110 + passe), échauffement de 2.

### 3.4 Analyse (`analysis/mojo_check.py`) et décisions fixées d'avance

* **M-E, classement publié** : les errata de 3.2 ; aucune donnée ne change. L'analyse v3 recalculée doit redonner
  exactement ce scénario.
* **Avant** (le calcul publié avant la remarque, refait par le même code), et trois sensibilités : **S-B4** (B4 =
  0,5), **S-K4** (K4 retiré du plafond E pour tous les langages ; K4 naturel reste dans D1), **S-K4-B4**.
* **Non adoptés** : K4 en SIMD explicite dans le score (la spécification ne l'admet pour aucun langage ; l'admettre
  pour Mojo seul serait inéquitable, et le mesurer dans les 21 langages sort de cette vérification) ; le paquet MAX
  (règle de la bibliothèque standard).
* **README** : (a) si K9 naturel sans vérifications fait au plus 1,2 fois le K9 naturel de C sur le même hôte,
  l'explication du stencil naturel de Mojo devient « les vérifications de bornes de `List`, actives par défaut » ;
  même règle pour Q1 ; (b) la règle de la bibliothèque standard et le départ de `parallelize` vers MAX sont dits ;
  (c) K4 dans le plafond entre dans les limites de l'étude.

## 4. Résultats

126 processus (18 cellules, 7 passes, échauffement de 2), le 30 octobre de 18 h 05 à 18 h 07 sur la machine 6 ;
aucune somme de contrôle fausse ; 2 processus refaits pour vol de temps au-dessus de 2 % (aucun gardé au-dessus du
seuil). Temps, rapports et scénarios : `results/report_mojo.md` et `results/mojo_check.json` ; données :
`results/raw_mojo/`.

### 4.1 Diagnostics (machine 6, même hôte)

| Noyau naturel | Mojo par défaut | Mojo, `-D ASSERT=none` | Rapport (IC 95 %) | C par clang |
|---|---|---|---|---|
| K9 (stencil) | 168,8 ms | 41,2 ms | 0,245 (0,229–0,266) | 27,8 ms |
| Q1 (requête OLAP) | 137,0 ms | 66,7 ms | 0,481 (0,438–0,527) | 66,3 ms |
| Q6 | 53,5 ms | 51,0 ms | 0,956 (0,892–1,006) | — |
| K4 | 14,8 ms | 13,7 ms | 0,93 (0,68–1,29) | 3,9 ms |

* **(3) Le stencil naturel paie d'abord les vérifications de bornes** : sans elles, il est 4,1 fois plus rapide. Mais
  il reste 1,48 fois (1,40–1,58) plus lent que le C naturel de clang, qui est vectorisé : la règle fixée d'avance (au
  plus 1,2) n'est pas remplie pour K9. Elle l'est pour Q1 (0,995 ; 0,88–1,11), dont la lenteur vient toute des
  vérifications. Le README dit donc les deux causes pour le stencil, et la seule pour Q1.
* **(2) K4 en SIMD explicite** : 2,25 ms à chaud (le plus rapide des processus : 1,66 ms), 2,45 ms caches vidés ;
  0,73 fois (0,63–0,83) K4 sans branchement de clang sur le même hôte (3,05 ms). En SIMD explicite, Mojo bat donc le
  meilleur C vectorisé automatiquement, mais pas dans la proportion annoncée (1,1 contre 2,8 ms) : sur cet hôte, la
  passe reste limitée par la mémoire (caches vidés : 1,10 fois le temps à chaud ; 0,98–1,25). Le processus le plus
  rapide (1,66 ms) passe de peu la borne de K4, qui rejette sous 1,51 ms.
* **Pas de pénalité de branchement sur K4 naturel**, comme le dit la remarque : le code est sans saut (`sar`, `and`),
  et le plus rapide des processus fait 10,5 ms avec ou sans tri ; l'écart des moyennes (0,79 ; 0,62–1,02) vient de
  quelques processus lents.
* Témoin de disposition : K4 sans branchement, même source dans `mojo_exp` et dans `mojo` : 1,21 (0,95–1,52).

### 4.2 Classement

| Scénario | Score | Contrôle C | Plafond E | Rang espéré | Place | Rang 90 % |
|---|---|---|---|---|---|---|
| Avant (publié avant la remarque, refait par le même code) | 60,0 | 62,7 | 67,9 | 12,49 | 13 | 10–14 |
| **M-E, publié** : errata A4, A5, C4, D5, E5 | **62,7** | **70,5** | 67,9 | **11,87** | **13** | 9–13 |
| S-B4 : B4 = 0,5 (la note de la remarque) | 62,0 | 68,5 | 67,9 | 12,06 | 13 | 10–13 |
| S-K4 : K4 hors du plafond, pour tous les langages | 67,2 | 70,5 | 79,2 | 10,38 | 11 | 7–13 |
| S-K4-B4 | 66,5 | 68,5 | 79,2 | 10,70 | 12 | 7–13 |

Depuis les errata de Julia et de Chapel (`docs/JULIA.md`, `docs/CHAPEL.md`), le classement publié donne à Mojo un rang
espéré de 12,07, sans changer son score, sa place (13e) ni son rang plausible (9–13) ; Julia (64,0 points) repasse
devant lui au score.

* **Publié** : l'analyse v3 recalculée redonne exactement M-E (scores et rangs plausibles des 21 langages). Mojo gagne
  2,7 points et dépasse Julia au score (62,7 contre 62,2), mais reste 13e en rang espéré : il ne passe devant elle que
  dans 46 % des variantes (31 % avant), parce que son code naturel est le plus lent des langages compilés à l'avance.
  Les scores des autres langages ne bougent pas.
* **Sans K4 dans le plafond**, Mojo passerait 11e (67,2 points), mais il n'est pas seul à bouger : C++ passerait 1er
  devant C (79,8 contre 79,3 points), Zig 3e, Ada 6e. Le choix de la spécification (deux formes scalaires pour K4)
  pèse donc sur le haut du classement ; le README le dit. Je ne change pas la méthode après coup (3.1).
* **La remarque estimait** 62,2 points avec ses quatre errata (j'en retiens cinq : 62,7), 64,5 points (11e) sans K4
  dans le plafond, et 66,7 (11e) avec les deux ; mes calculs donnent 67,2 (11e) avec les errata et sans K4, et 66,5
  (12e) avec en plus sa note de B4.

### 4.3 Verdicts

* **(1) Matrice** : A4, A5, C4 et E5 exacts (E5 avec une réserve : la conversion n'aide pas dans ma boucle) ; D5
  accepté (`SpinWaiter`, comme `SpinWait` de C#) ; B4 non retenu : une erreur levée n'alloue pas, la trace de pile est
  désactivée par défaut, et seule l'async expérimentale alloue.
* **(2) K4 dans le plafond** : exact sur le principe. C'est un choix de la spécification, que je garde ; la
  sensibilité est publiée. En SIMD explicite, K4 est bien plus rapide que le meilleur C (0,73 fois), sans atteindre
  1,1 ms sur cet hôte. La borne physique de K4 était cohérente avec la machine des données principales (9,86 Go/s à
  16 Mio), mais fragile ailleurs.
* **(3) Diagnostic du README** : exact pour l'essentiel (vérifications : ×4,1 sur le stencil, ×2,1 sur Q1), mais il
  reste sur le stencil un facteur 1,5 face au C vectorisé. Corrigé dans le README.
* **(4) K5 sur Emerald Rapids** : écart confirmé dans mes données (+32 %), cause non vérifiée.
* **(5) La bibliothèque standard et MAX** : dit dans les limites du README.
