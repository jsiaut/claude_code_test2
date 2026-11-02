# Remarque sur Java : un K5 désaligné, une case de la grille, et des formes optimisées à essayer

L'auteur de l'étude m'a transmis le 2 novembre une remarque sur Java. Elle juge sa 15e place défendable, mais son score
(46,1) un peu sous-estimé : des défauts de mesure déjà corrigés ailleurs, deux erreurs dans la grille, de 1 à 7 points en
tout, sans changement de place. Ce document vérifie chaque affirmation (section 2), fixe le plan avant toute mesure
(section 3), puis donne les résultats (section 4). Je n'ai consulté aucune page web : les faits viennent du JDK de
l'étude, de sondes et des données publiées.

## 1. La remarque

1. **Le verdict** : la place de Java (15e, entre C# et Go) est défendable selon les règles de l'étude, et ce qu'elle dit
   de Java est exact pour le JDK 27 ; son score (46,1) est un peu sous-estimé. Java est l'un des sept langages qu'aucun
   connaisseur n'a relus.
2. **Les faits du JDK** : en-têtes compacts activés par défaut en Java 27 (JEP 534) ; 78 octets par particule, « 8
   (en-tête) + 64 (données) + 4 (référence) + 5,9 (marge de capacité de l'`ArrayList`) = 77,9 » ; Vector API en
   incubation pour la douzième fois (JEP 537) ; JEP 401 intégrée au JDK 28 en préversion, aplatissement limité à environ
   64 bits, comme l'annexe Valhalla le mesure.
3. **Les handicaps mesurés sont réels** : parcours permuté 4,9 fois plus lent ; K4 naturel avec branchements (79 ms
   contre 4 ms en C) ; pas de types valeur, SIMD non finalisé, ni intrinsèques, ni préchargement, ni contrôle des
   vérifications de bornes.
4. **C# devant Java** : l'écart tient au contrôle jugé (41,5 contre 68,8, soit 9,6 points pour un écart de 8,8) ; Java
   est devant sur le plafond (55,0 contre 53,6) et le code par défaut (38,5 contre 37,4). L'ordre est légitime.
5. **Six défauts de mesure** (mesurés avec l'OpenJDK 25, en-têtes compacts activés, sur un Cascade Lake de 2 vCPU) :
   (1) Q1 optimisé en blocs, une passe masquée par groupe, « exactement le défaut corrigé pour D » ; six groupes
   déroulés en variables locales : 78–92 ms → 37–46 ms ; (2) K5 : un `float[]` commence à 12 octets de l'objet, chaque
   chargement de 64 octets chevauche deux lignes de cache (C aligné 4,9 ms, C décalé de 12 octets 8,8, Java 9,8) ;
   « l'étude a corrigé ce même défaut pour Rust », son C# utilise une mémoire alignée ; `Arena.allocate(n, 64)` donne
   ×0,72 ; (3) fils créés à chaque itération (0,78 ms contre 0,15 en C pour quatre fils) ; avec une réserve, Q6 ×0,81,
   K9 ×0,72, puis ×0,63 avec la Vector API ; (4) K9 optimisé scalaire (C2 du JDK 25), plus lent que le naturel dans les
   données de l'étude (19,6 contre 15,7 ms) ; (5) K7 : 2,7 fois le temps de C sur Cascade Lake, 1,26 sur Emerald
   Rapids ; noyau isolé dans sa méthode ×0,78, lots de 16 avec lecture anticipée ×0,67 ; (6) K8 : arène itérative ×0,79,
   une sensibilité comme pour C.
6. **Deux erreurs de la grille** : A5 (« pas d'unions ») est faux, l'API FFM offre `MemoryLayout.unionLayout` et la
   réinterprétation de la mémoire, « C# et Julia obtiennent 1 pour l'équivalent » ; F1 = 0 est incomplet, des
   `sequenceLayout` imbriqués donnent des tableaux multidimensionnels contigus, ½ par la règle « hors tas » et comme C3.
   Cases discutables : B3, F2 et D4 vers le haut, D3 vers le bas.
7. **Score recalculé** (estimation ponctuelle) : 47,1 (grille), 47,3–49,2 (Q1 et K5), 49,0 (réserve de fils, K9
   vectorisé), 51,1 (K7, K8), 52,0 (et la grille), 53,2 (et les cases discutables) ; toujours 15e, mais une avance nette
   sur Go (aujourd'hui devant dans 64 % des variantes).
8. **Ce que mesure la 15e place** : le Java de la bibliothèque standard et des réglages par défaut, alors que la
   *mechanical sympathy* a été popularisée en Java par des pratiques que les règles excluent ; sur K10 (hors score), le
   Java optimisé est le plus rapide de l'étude (29 ms) ; l'étude « Banc de sympathie mécanique » le classe 12e sur 18.

## 2. Vérifications (faites avant le plan)

**Machine 17.** La VM a redémarré le 2 novembre à 7 h 24 sur un hôte Emerald Rapids du même modèle que les machines 3
et 8 à 16 (modèle 207, 4 vCPU), plus lent que la machine 16 : 2,15 à 2,44 GHz effectifs, latence à 4 Mio 57 ns,
DRAM 15 Go/s, 27 Go/s sur un fil jusqu'à 64 Mio (`results/hw/machine17/`). Chaîne de l'étude : OpenJDK 27.0.1
(`/opt/jdk27`, G1, C2). Preuves : `results/java_check/` (sondes : `tools/java_check/probes/` ; faits tirés des
données : `tools/java_check/data_facts.py`, `facts.txt`).

* **Place et piliers (1, 4)** : exacts. Contrôle 41,46 contre 68,75 ; plafond 55,02 contre 53,64 ; défaut 38,46 contre
  37,37 ; écart de score 8,72 points (8,8 en arrondissant les deux scores), dont 9,55 dus au contrôle. Java devance Go
  dans 64 % des variantes. Sept langages n'ont pas été relus : Java, Go, Haskell, OCaml, JavaScript, Python, Lua.
* **En-têtes compacts (2)** : `UseCompactObjectHeaders = true {default}` dans le JDK 27.0.1 (`offsets.txt`). **Exact.**
  Les numéros de JEP (534, 537) et le compte des incubations ne se vérifient pas sans le web ; le module
  `jdk.incubator.vector` est bien livré en incubation dans le JDK 27.0.1.
* **78 octets (2)** : empreinte publiée 78,01 o. **Exact, mais la somme de la remarque compte la référence deux fois**
  (8 + 64 + 4 + 5,9 font 81,9) : l'objet fait 8 + 64 = 72 o ; le tableau de références de l'`ArrayList` a une capacité
  de 6 153 400 pour 4 194 304 particules (croissance de 1,5 à partir de 10), soit 5,87 o par particule, dont les 4 o de
  la référence et 1,87 de capacité inutilisée ; total 77,87 o.
* **Valhalla (2)** : ce que la remarque en dit est ce que l'annexe de l'étude mesure déjà (`docs/FINDINGS.md` : un
  `value record` de 16 `float` n'est pas aplati, la limite de 64 bits citée de JEP 401, JEP 401 dans le JDK 28 en
  préversion). **Exact.**
* **Handicaps (3)** : parcours permuté 276,0 contre 56,2 ms (4,91 fois) ; K4 naturel 78,1 ms contre 4,0 en C (sans
  branchement : 6,7 ms). **Exact.**
* **(5.1) Q1 en blocs** : le code fait bien une passe masquée par groupe sur des blocs de 2 048 lignes (88,4 ms sur
  Cascade Lake, 30,7 à quatre fils ; C 32,1 et 13,4). Mais **la règle appliquée à D ne s'étend pas à Java** : elle porte
  sur la classe des langages à types vectoriels portables standard (C1 = 1 : C++, Zig, Odin, C3, Mojo, C#, D), où D
  était seul à s'écarter de l'algorithme de la référence (`docs/DLANG.md`, 3.1). Java a C1 = ½ (Vector API en
  incubation), comme Rust et Julia, et `docs/NOSIMD.md` (2.3) le range déjà parmi les cinq implémentations à SIMD
  explicite qui écrivent Q1 autrement qu'en une passe vectorielle, avec Nim, Ada, Go et Haskell. La forme en une passe
  est une meilleure forme : **sensibilité**, comme pour Nim et Julia.
* **(5.2) K5 désaligné** : **exact, et c'est une erreur de mon implémentation.** Avec les en-têtes compacts, les
  données d'un `float[]` commencent à 12 octets de l'objet (16 sans eux ; `offsets.txt`), et les objets sont alignés sur
  8 octets : chaque chargement de 64 octets chevauche deux lignes de cache. Sonde indicative sur la machine 17
  (`k5_align.txt`, médianes de processus) : C aligné 3,8 à 5,5 ms, décalé de 12 octets 7,6 à 8,2 ; Java sur le tas 7,1
  à 8,1, sur une copie hors tas alignée (`Arena.allocate(n, 64)`, `FloatVector.fromMemorySegment`) 4,8 à 4,9, sur la
  même copie décalée de 12 octets 8,2 à 10,9. Dans les données publiées (machine 3), Java fait 6,95 ms, C 3,94 et C#
  4,13. **La convention** : toutes les autres implémentations à SIMD explicite copient leurs données dans des tampons
  alignés sur 64 octets (C, C++, Rust, Zig, Odin, C3, D, Nim, Ada, Fortran, Mojo ; Haskell par un tableau épinglé
  aligné ; Go par les gros tampons alignés sur la page ; Julia par ses tableaux), y compris C#, langage à
  ramasse-miettes, qui passe par `NativeMemory.AlignedAlloc` pour K5 et K1 (soa). Java est le seul à lire ses vecteurs
  dans des tableaux du tas. C'est la seconde clause de la règle commune (un écart à une convention que les autres
  suivent). La remarque attribue la correction de Rust à l'étude : elle date de l'écriture du banc (`docs/FINDINGS.md`,
  « Pièges de performance »), pas d'une remarque.
* **(5.3) Fils créés à chaque itération** : ordre de grandeur **exact** (machine 17, `spawn.txt` : quatre fils créés,
  lancés et attendus en 0,45 à 0,54 ms en Java, 0,10 à 0,11 en C). Mais la façon de lancer les fils de `mt` relève du
  langage et de son idiome, et la révision du harnais de K9 l'a laissée telle quelle (`docs/K9.md`, 3.1) ; la réserve
  de fils de C# est restée une sensibilité (`docs/CSHARP.md`). **Sensibilité.**
* **(5.4) K9 optimisé** : **inexact pour le JDK de l'étude.** Le C2 du JDK 27 vectorise le noyau à tableau plat
  (boucle chaude en xmm et ymm : `k9_hotloop.txt`), comme le naturel ; « scalaire » vaut pour le JDK 25 de la remarque.
  Il reste plus lent que le naturel (20,1 contre 17,0 ms, machine 16, harnais commun). Le même noyau écrit en Vector
  API est une forme nouvelle : **sensibilité**.
* **(5.5) K7** : rapports à C de 2,55 sur Cascade Lake (et non 2,7) et 1,26 sur la machine 3 (exact). Le noyau est
  écrit dans `runK7`, entre les deux lectures de l'horloge, comme celui de C (`run_k7`) et de C# (`RunK7`) : pas d'écart
  à une convention. Pour un JIT, `runK7` n'est appelé qu'une fois et tourne en code compilé sur place (OSR) ; la remarque
  sur C# a gardé ce protocole et mesuré l'OSR en sensibilité. **Sensibilité** (noyau isolé ; lots de 16).
* **(5.6) K8** : l'arène itérative est une forme nouvelle, comme pour C. **Sensibilité.** Le K8 optimisé de Java est
  déjà plus rapide que celui de C (233 contre 266 ms).
* **(6) A5** : `MemoryLayout.unionLayout` existe et fonctionne sans option de préversion, et la réinterprétation passe
  par les segments, y compris ceux d'un tableau du tas (`ffm_probe.txt`). **Le texte « pas d'unions » est faux.** La note
  reste ½ : dans toute la ligne de Java, ce que seule l'API FFM permet sur des segments vaut ½ (A1, A2, A3, A4, A7, B2,
  B5), et les unions n'y existent que comme disposition de segment ; les vues de JavaScript (½) et les conversions de
  Go (½) sont de même nature. Les « équivalents » cités n'en sont pas : C# recouvre des champs dans ses types valeur
  (`FieldOffset`), Julia réinterprète ses propres agrégats (`reinterpret`). **Texte corrigé, note inchangée.**
* **(6) F1** : un `sequenceLayout` imbriqué donne un tableau 2D contigu, lu et écrit par deux indices, hors tas ou sur un
  tableau du tas (`ffm_probe.txt`). C'est le mécanisme déjà crédité de ½ en A7 (`sequenceLayout` dans un
  `structLayout`). **Erratum : F1 = ½** (règles v1 et v2).
* **(6) Cases discutables** : B3 (0) : pas d'agrégat valeur en Java, et le remplacement scalaire de C2 n'est pas
  garanti ; Go a ½ parce que ses structures sont des valeurs que l'analyse d'échappement place sur la pile. F2 (0) :
  `-XX:+UseNUMA` est une option globale du ramasse-miettes ; C, C# et Go ont aussi 0. D4 (0) : pas d'API d'affinité ;
  l'appel de la libc par FFM relève de la règle de la libc, que la sensibilité S-libc-FFI de la remarque sur Rust étend
  déjà à Java (D3, D4 et F4 à 1). D3 (½) : `@Contended` est réservé à une unité interne, ½ selon la règle v2. **Notes
  inchangées ; B3 et F2 en information** (S-cases ci-dessous).
* **(8) K10** : dans la remesure à 9 processus, le K10 optimisé de Java est bien le plus rapide (12,7 ms, devant Odin
  17,6 et Chapel 18,6) ; les « 29 ms » sont la médiane de la première campagne (2 processus), où Java était 5e et où la
  file des langages natifs était bistable (`docs/FINDINGS.md`). **Exact pour le classement, chiffre d'une autre mesure.**
  L'étude « Banc de sympathie mécanique » classe bien Java 12e sur 18. La règle de la bibliothèque standard et des
  réglages par défaut est la même pour tous les langages.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune

`docs/FORTRAN.md`, 3.1 : « Est une erreur : un code qui ne fait pas ce qu'il annonce (Ada) ou qui s'écarte d'une
convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle de mesure). Une meilleure forme
ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation nouvelle. » Le K5 désaligné relève
de la seconde clause de la première phrase : la convention (données des noyaux à SIMD explicite alignées sur 64 octets)
est suivie par toutes les autres implémentations, y compris C#, qui passe pour cela par la mémoire native. Q1 en une
passe, réserve de fils, K9 en Vector API, K7 isolé et par lots, K8 itératif sont des optimisations nouvelles.

### 3.2 Ce qui entre dans le classement publié

* **Erratum de la grille** : F1 = ½ (`analysis/capabilities.py`, règles v1 et v2) ; texte de A5 corrigé, note ½.
* **Correction de K5 tuned et de K1 soa** : rapports appariés `java_fix` / `java_ref` (machine 17), reportés sur les
  données publiées par la règle de `analysis/transfer_check.py` (pont par le C du même hôte quand le transfert et le
  pont s'écartent de plus de 25 %) ; K5 publié vient de la machine 3, du même modèle que la machine 17. La version par
  transfert seul est publiée à côté. K6 garde ses tableaux du tas, comme celui de C#.
* **Texte du README** : paragraphe de Java, langages relus, limites.

### 3.3 Copies (`tools/java_check/make_copies.py`)

* `java_ref` : copie exacte de `bench/java`, compilée le même jour que les autres.
* `java_fix` : K5 tuned et K1 soa lisent des copies hors tas alignées sur 64 octets (`Arena.global().allocate(taille,
  64)`, `FloatVector.fromMemorySegment`) ; même calcul, mêmes sommes ; rien d'autre ne change.
* `java_exp` : `bench/java_k9h` (harnais commun de K9) avec la correction de `java_fix`, et des variantes nouvelles
  à côté des variantes d'origine, inchangées : K6 `tuned_1p` et `mt_1p` (Q1 en une passe, algorithme de la référence C,
  accumulateurs des six groupes en variables locales), `mt_pool` et `mt_pool_1p` (réserve de quatre fils,
  `Executors.newFixedThreadPool(4)`, créée hors chrono) ; K9 `tuned_vec` (Vector API, 8 `double` par vecteur, même
  ordre des additions), `mt_pool`, `mt_pool_vec` ; K7 `natural_iso` et `tuned_iso` (noyau dans sa propre méthode),
  `tuned_batch` (isolé, lots de 16 : hachages et cases lus d'avance, puis insertion) ; K8 `tuned_it` (arène construite et
  sommée itérativement, comme `c_k8it`).
* Validation (`tools/java_check/validate.py`) : les 30 cellules Java de la campagne, sommes de contrôle justes.
  Différences de source : `results/java_check/copies.txt`.

### 3.4 Mesures (`tools/measure_java.py`, machine 17)

40 cellules, 7 processus chacune (280 processus), en 7 passes ; dans chaque passe, toutes les cellules dans un ordre
tiré au hasard (graine 20261402) :

* `java_ref` et `java_fix` : K5 tuned, K1 soa (clés corrigées) ; K5 naturel, K1 naturel, K6 tuned Q6 (témoins) ;
* `java_exp` : chaque forme nouvelle et la variante d'origine qu'elle remplace (20 cellules) ;
* `c` (binaire de la campagne) : témoin du même hôte pour le pont, sur les 10 clés reportées.

Répétitions de `results/calib.json` (variante d'origine) ; échauffements des données publiées (Java : 10 pour K5, 3
sinon ; C : 2 et 1) ; règle de vol du pilote. Rien d'autre ne tourne pendant les mesures. Sortie : `results/raw_java/`.

### 3.5 Scénarios (`analysis/java_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap. Les rapports des sensibilités sont
pris dans la même copie (`java_exp`, forme nouvelle / variante d'origine) et appliqués sous la forme min(1, r) : on
garde la meilleure des deux formes, comme le ferait un programmeur. Report : règle du pont ; « -T » : transfert seul.

| Scénario | Contenu |
|---|---|
| Avant | classement publié d'avant (F1 = 0, sans correction) ; doit reproduire `results/k9_check.json` (écart 0) |
| J-F1 | erratum F1 seul |
| J-K5, J-K5-T | correction de K5 et K1 soa seule |
| **J-E (publié)**, J-E-T | erratum et correction |
| S-Q1 | J-E ; K6 tuned Q1 × r(`tuned_1p`), `mt` Q1 × r(`mt_1p`) |
| S-pool | J-E ; K6 `mt` Q6 × r(`mt_pool`), `mt` Q1 × r(`mt_pool`), K9 `mt` × r(`mt_pool`) |
| S-K9v | J-E ; K9 tuned × r(`tuned_vec`), K9 `mt` × r(`mt_pool_vec`) |
| S-K7 | J-E ; K7 tuned × r(`tuned_batch`), K7 naturel × r(`natural_iso`) ; information : `tuned_iso` |
| S-K8 | J-E ; K8 tuned × r(`tuned_it`) |
| S-mesures, S-mesures-T | toutes les formes : Q1 tuned `tuned_1p`, Q1 `mt` `mt_pool_1p`, Q6 `mt` `mt_pool`, K9 `tuned_vec` et `mt_pool_vec`, K7, K8 |
| S-cases | J-E ; B3 = ½ et F2 = ½ (cases « discutables » de la remarque, information) |
| S-libc-J | J-E ; D3 = D4 = 1 (règle de la libc étendue à Java seul) |
| S-tout | S-mesures, S-cases et S-libc-J |

Pour chacun : score, piliers, rang espéré, place, rang à 90 %, voisins. Sorties : `results/java_check.json`,
`results/report_java.md` ; puis régénération des sorties publiées et de l'état actuel.

### 3.6 Ce que je ne fais pas

* Pas de mesure avec le JDK 25, ni de réglage de la JVM (ramasse-miettes, options de C2) : la règle est la même pour
  tous les langages.
* Pas de changement des variantes naturelles, ni du protocole (échauffements, compilation sur place).
* Pas de remesure sur la machine 3 (indisponible) : K5 y est corrigé par le rapport mesuré sur un hôte du même modèle.

## 4. Résultats (après les mesures)

Mesures du 2 novembre, de 7:56:48 à 8:11:02, sur la machine 17 : 280 processus (40 cellules × 7), aucune somme de
contrôle fausse ; 24 processus refaits pour vol de temps (trois deux fois), aucun gardé au-dessus de 2 % (vol médian
0,70 %, maximum 1,95 %) ; 2,65 à 2,75 GHz effectifs avant et après. Rien d'autre ne tournait. Sorties :
`results/report_java.md` et `results/java_check.json` (`analysis/java_check.py`) ; données : `results/raw_java/`. Le
scénario Avant reproduit exactement le classement publié d'avant (écart 0).

**Un écart au plan**, décidé après avoir vu les ponts et avant tout score corrigé (commit `9a1f793`) : dans J-K5 et
J-E, un rapport de correction supérieur à 1 est ramené à 1. La règle du pont donnait 1,085 à K1 soa, c'est-à-dire un
temps publié plus long pour un code qui, sur le même hôte, va 1,3 fois plus vite (4.1). J-E-règle applique la règle
telle quelle, pour information.

### 4.1 La correction (`java_fix` / `java_ref`, même hôte)

| Clé | `java_ref` | `java_fix` | Rapport (IC 95 %) | C, même hôte |
|---|---|---|---|---|
| K5 tuned | 9,23 ms | 5,54 ms | 0,600 (0,508–0,722) | 3,86 ms |
| K1 soa | 4,85 ms | 3,68 ms | 0,758 (0,615–0,936) | 3,02 ms |
| Témoins : K5 naturel, K1 naturel, K6 tuned Q6 | | | 1,013 ; 1,021 ; 1,019 | |

* **K5** : aligné, Java passe de 2,4 à 1,4 fois le temps de C sur le même hôte. Report sur les données publiées
  (machine 3) : transfert 4,17 ms, pont par le C 5,65 ms, écart 26 % ; la règle retient le pont (× 0,813) : 6,95 →
  5,65 ms (C 3,94).
* **K1 soa** : sur la machine 17, les quatre colonnes lues (4 × 16 Mio) tiennent dans le cache L3 de 260 Mio, et
  l'alignement compte (× 0,76). Sur Cascade Lake, d'où vient le K1 publié, la boucle est limitée par la mémoire (Java
  8,71 ms, C 7,76) : le transfert (6,60 ms) mettrait Java devant C sur une boucle que la bande passante borne, et le
  pont (9,45 ms) allongerait le temps d'un code corrigé. Aucun des deux reports n'est crédible ; par l'écart au plan,
  K1 soa garde son temps publié.

### 4.2 Les sensibilités (`java_exp`, forme nouvelle / variante d'origine, même copie)

| Forme | Clé | Rapport (IC 95 %) | Remarque | Retenu |
|---|---|---|---|---|
| Q1 en une passe | K6 tuned Q1 | 0,402 (0,336–0,476) : 72,8 → 29,3 ms (C 25,3) | × 0,40 à 0,58 | 0,402 |
| Q1 en une passe, quatre fils | K6 `mt` Q1 | 0,510 (0,458–0,560) : 19,9 → 10,1 ms (C 8,0) | | 0,510 |
| Réserve de quatre fils | K6 `mt` Q1 | 1,065 (0,944–1,190) | | 1 |
| Réserve de quatre fils | K6 `mt` Q6 | 1,084 (0,967–1,210) | × 0,81 | 1 |
| Réserve, Q1 en une passe | K6 `mt` Q1 | 0,509 (0,454–0,569) | | 0,509 |
| Réserve de quatre fils | K9 `mt` | 0,814 (0,708–0,944) | × 0,72 | pont 0,639 |
| Vector API | K9 tuned | 0,960 (0,786–1,196) | | 0,960 |
| Réserve et Vector API | K9 `mt` | 0,765 (0,661–0,885) | × 0,63 | pont 0,601 |
| Noyau isolé | K7 tuned | 0,716 (0,639–0,806) : 436 → 312 ms (C 184) | × 0,78 | information |
| Isolé, lots de 16 lus d'avance | K7 tuned | 0,802 (0,720–0,899) | × 0,67 | 0,802 |
| Noyau isolé | K7 naturel | 0,964 (0,791–1,200) | | 1 (pont) |
| Arène itérative | K8 tuned | 0,641 (0,561–0,726) : 246 → 158 ms (C 301) | × 0,79 | 0,641 |

* **Q1 en une passe** : confirmé ; Java fait alors 1,16 fois le temps de C sur le même hôte (2,9 fois en blocs).
* **La réserve de fils** ne gagne rien sur K6 avec quatre vCPU : créer quatre fils (0,45 ms) pèse peu face à 6 à
  20 ms de calcul, et la remise des tâches à la réserve coûte autant. Elle gagne sur K9 `mt` (× 0,81), qui crée quatre
  fils à chacune de ses quatre itérations. La remarque (deux vCPU) trouvait × 0,81 sur Q6.
* **K9 en Vector API** : × 0,96, dans le bruit, puisque le C2 du JDK 27 vectorise déjà la boucle (section 2).
* **K7** : isoler le noyau dans sa méthode suffit (× 0,72) : sinon, le code mesuré est la compilation sur place de
  `runK7`, appelé une seule fois. Les lots de 16 lus d'avance y perdent (× 0,80 au total) : sans instruction de
  préchargement, une lecture anticipée est une vraie lecture, qui attend. S-K7 retient la forme prévue au plan
  (`tuned_batch`) ; l'isolement seul vaudrait un peu plus. Le pont du K7 naturel est absurde (38,6 s : le K7 naturel de
  C, qui alloue chaque entrée, va 11 fois plus vite sur Emerald Rapids que sur Cascade Lake) ; plafonné à 1.
* **K8 itératif** : × 0,64. Sur cet hôte, le K8 optimisé de Java était déjà plus rapide que celui de C (246 contre
  301 ms).

### 4.3 Classement (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Java | Contrôle | Plafond | Rang espéré | Place | Devant Go | Devant C# |
|---|---|---|---|---|---|---|---|
| Avant | 46,1 | 41,5 | 55,0 | 15,27 | 15 | 64 % | 10 % |
| J-F1 | 46,6 | 42,7 | 55,0 | 15,23 | 15 | 68 % | 10 % |
| J-K5 ; J-K5-T | 46,7 ; 48,1 | 41,5 | 56,5 ; 60,1 | 15,22 ; 15,08 | 15 | 67 % ; 73 % | 12 % ; 19 % |
| **J-E (publié)** | **47,2** | 42,7 | 56,5 | 15,18 | 15 | 70 % | 12 % |
| J-E-T ; J-E-règle | 48,6 ; 46,9 | 42,7 | 60,1 ; 55,9 | 15,04 ; 15,20 | 15 | 75 % ; 69 % | 20 % ; 12 % |
| S-Q1 | 48,3 | 42,7 | 59,3 | 15,08 | 15 | 74 % | 18 % |
| S-pool | 47,8 | 42,7 | 58,1 | 15,13 | 15 | 72 % | 15 % |
| S-K9v | 47,9 | 42,7 | 58,3 | 15,12 | 15 | 72 % | 16 % |
| S-K7 | 47,8 | 42,7 | 58,0 | 15,13 | 15 | 73 % | 15 % |
| S-K8 | 48,4 | 42,7 | 59,7 | 15,06 | 15 | 74 % | 19 % |
| S-mesures ; S-mesures-T | 51,2 ; 52,4 | 42,7 | 66,6 ; 69,7 | 14,79 ; 14,62 | 15 | 81 % ; 83 % | 33 % ; 42 % |
| S-cases | 48,3 | 46,0 | 56,5 | 15,08 | 15 | 77 % | 15 % |
| S-libc-J | 48,7 | 47,2 | 56,5 | 15,04 | 15 | 78 % | 17 % |
| S-tout | 53,9 | 50,5 | 66,6 | 14,48 | 15 | 89 % | 50 % |

* **Classement publié** : Java gagne 1,0 point (47,2 : 0,4 par F1, 0,6 par K5) et reste 15e ; il devance Go dans 70 %
  des variantes (64 % avant) et C# dans 12 %. Les vingt autres langages gardent leurs scores et leurs places. En
  transfert seul (J-E-T), le K1 soa de Java (6,60 ms) deviendrait la frontière de K1 et retirerait 0,3 à 0,4 point à
  tous les autres : c'est ce que l'écart au plan évite.
* **Les estimations de la remarque tiennent** : 47,1 avec la grille (ici 46,6, F1 seul), 47,3 à 49,2 avec Q1 et K5
  (47,2 et 48,3), 51,1 avec K7 et K8 (S-mesures : 51,2), 53,2 avec les cases discutables (S-tout : 53,9). Dans tous les
  scénarios, Java reste 15e.
* **Avec tout** (S-tout), Java rejoint C# au rang espéré (14,48 contre 14,46 ; devant lui dans 50 % des variantes),
  mais C# a lui aussi ses formes optimisées : 63,3 points avec toutes ses sensibilités (`docs/CSHARP.md`).

### 4.4 Bilan

* **Exact** : la place et les piliers ; les faits du JDK 27 (la somme des 78 octets compte la référence deux fois) ;
  le désalignement de K5, une erreur de mon banc, corrigée ; F1 ; les gains de Q1, de K7 et de K8.
* **Inexact ou à nuancer** : le K9 optimisé « scalaire » (vrai pour le JDK 25, pas pour le 27) ; Q1, « exactement le
  défaut corrigé pour D » (Java est hors de la classe où la règle s'applique) ; A5 = 1 (les équivalents cités sont des
  unions et des réinterprétations du langage lui-même) ; les 29 ms de K10 (première campagne) ; le rapport de K7 sur
  Cascade Lake (2,55 et non 2,7) ; la réserve de fils (aucun gain sur K6 avec quatre vCPU).
* **Effet** : + 1,0 point au classement publié, toujours 15e ; 51 à 54 points avec toutes les formes optimisées et les
  cases discutables, toujours 15e, avec une avance nette sur Go (81 à 89 % des variantes).
