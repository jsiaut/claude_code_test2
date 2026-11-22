# v4, campagne finale : le classement de la v4 — plan (22 novembre 2026)

*Plan d'ensemble : `docs/V4_PLAN.md`. Ce plan est poussé avant tout outil, toute construction et toute mesure de la
campagne ; les écarts éventuels seront datés ici (section 11) et dans le journal (`docs/METHODOLOGY.md`).*

## 1. Question

Les points 2 à 4 de la v4 ont fixé des règles pour une campagne unique, « sur un même hôte », qui donnera le classement
de la v4 (`docs/V4_SIZES.md`, 9 ; `docs/V4_EQUAL.md`, 9 ; `docs/V4_CONVERGE.md`, 9) : trois tailles par noyau, comptées
à poids égaux ; des conditions égales (R1 à R5) ; un plafond qui prend la meilleure forme admise (C1 à C6). Le point 5
a laissé la grille de contrôle en place, le point 6 la piste ouverte à côté du classement (décisions de l'auteur de
l'étude, 22 novembre). Le classement de 1 à 25 reste en tête du README (`docs/V4_PLAN.md`, en-tête) : celui de cette
campagne y remplacera celui de la v3.

Les règles s'appliquent quel que soit leur effet, déjà mesuré règle par règle. Ce plan fixe leur mise en œuvre commune,
le sort des constats laissés « à examiner avant la campagne finale », la conduite de la campagne quand l'hôte change,
l'analyse et la publication.

## 2. Faits établis avant le plan (22 novembre)

* **Sources.** Depuis le point 4, `bench/<langage>` porte les corrections du classement publié et le harnais commun de
  K9 (`results/converge/corrections.md`), avec les tailles du point 2 (constantes redéfinies à la construction, ou
  substituées pour les six langages sans construction) et les modes du point 3 (`MS_MODE=chk` pour R1, `unc` pour R1').
  Les copies `bench/<langage>_cv` en partent : K4 `tuned` (R3 ; celui de FreePascal sans assembleur), K9 naturel contigu
  (R2, 13 langages), formes du catalogue et formes propres à un runtime (C3, C5), qui lisent les paramètres de taille
  comme les variantes publiées (C2, 5) ; leurs `build.sh` acceptent les mêmes modes. Le relevé des formes est
  `results/converge/forms.json`.
* **Validation.** La base corrigée et les copies `_cv` ont été validées à la taille publiée seulement (point 4) ; les
  tailles petite et grande l'ont été sur la base non corrigée (point 2) ; les modes R1 et R1' sur la base non corrigée
  (point 3). Les sommes de contrôle attendues à chaque taille sont dans `results/sizes/expected.json` (calculées par
  l'implémentation C, point 2).
* **Hôte.** Le conteneur a redémarré vers 12 h 03 : machine 35, un Xeon du même modèle que les machines 31 à 34
  (Emerald Rapids, famille 6, modèle 207, pas 2), 4 vCPU, 15 Gio, limite de mémoire du groupe de 13,35 Gio
  (`/dev/shm` et cache de pages compris), à caractériser. Le redémarrage a vidé `/dev/shm` ; le disque n'a plus que
  984 Mo libres.
* **Les machines d'un même modèle diffèrent.** L3 effectif (machines 31 et 32 : `docs/V4_EQUAL.md`, 5.1) ; b3, le temps
  de la boucle de référence de K3 : 85,12 ms sur la machine 33, 69,4 ms sur la machine 34 (`docs/V4_OPEN.md`, 11.1) ;
  bande passante à quatre fils (STREAM triad de 47 à 148 Go/s en quatre mesures sur la machine 33).
* **Redémarrages.** Cinq en 59 heures (20 novembre à 1 h 19 ; 21 novembre vers 7 h 30 et à 15 h 55 ; 22 novembre vers
  6 h 44 et 12 h 03), soit de 5 à 30 heures entre deux. Le modèle n'a pas changé depuis le 20 novembre.
* **Durée.** D'après les enregistrements des points 2 à 4 (temps par processus de chaque cellule, et rapport des
  tailles petite et grande à la taille publiée, langage par langage), la campagne compte environ 3 200 processus par
  passe, de 9 h 15 à 9 h 50 chacune, plus environ 3 h 30 d'étalonnage : une trentaine d'heures. Un ou plusieurs
  redémarrages pendant la campagne sont donc probables ; la section 6 fixe la conduite à tenir.

## 3. Constats à examiner avant la campagne, et ce qui en est fait

Les points 2 à 4 ont laissé quatre constats « à examiner avant la campagne finale ». Examen fait sur les
enregistrements publiés, sans mesure nouvelle :

1. **Placement de la boucle de K3** (`docs/V4_SIZES.md`, 10.6) : traité par R4. Comme b3 change d'une machine à l'autre
   du même modèle (section 2), b3 est mesuré pour chaque groupe de K3, sur sa machine (section 6), au lieu d'une fois
   au début et à la fin.
2. **K2 à 8 Mio, deux régimes d'un processus à l'autre** (`docs/V4_SIZES.md`, 10.6) : traité par R5, sept processus par
   cellule (3, 2, 2). Précision : R5 dit « chaque cellule de K2 (dix tailles) », parce que la campagne de référence
   mesurait dix tailles ; seules trois entrent dans le score (16 Kio, 256 Kio, 8 Mio : D4), et les campagnes des points
   2 à 4 n'ont mesuré qu'elles. La campagne finale mesure ces trois tailles, sept processus chacune.
3. **D3 dépend des maxima de latence de quelques processus de K8** (`docs/V4_EQUAL.md`, 11.7). Le D3 du classement
   publié repose sur sept processus par langage (K8 naturel remesuré pour les 25 implémentations après la remarque sur
   Rust, `docs/RUST.md`, 4.2 : deux ou trois processus laissaient passer les queues dues au vol de temps) ; ceux des
   points 2 à 4, sur trois. **Règle de ce plan : K8 naturel est mesuré, comme K2, par sept processus (3, 2, 2)**, dans
   chaque construction où il l'est (section 5). D3 prend la médiane, répétition par répétition, des quantiles de
   latence de tous les processus (`analysis/analyze_v2.py`, `lat_rows`) : plus de processus ne le biaisent pas, ils
   le stabilisent.
4. **Processus lents de K5 et cellules à quatre fils** (`docs/V4_CONVERGE.md`, 11.2 et 11.10). Les neuf processus lents
   de K5 du point 4 (de 1,26 à 1,74 fois la médiane des deux autres passes) ont tous tourné entre 20 h 03 et 20 h 08 le
   21 novembre, mêlés à des processus du même groupe qui ne l'étaient pas ; les processus lents (plus de 1,2 fois la
   moyenne des deux autres passes) ne se concentrent pas dans la passe 0, celle de l'étalonnage : 54, 244 et 140 dans
   les passes 0, 1 et 2 du point 2 ; 47, 18 et 36 au point 3 ; 70, 36 et 18 au point 4. Ce sont des épisodes de
   l'hôte, sans mécanisme dans le banc. La variation des cellules à quatre fils suit celle de la bande passante de
   l'hôte (section 2). **Rien ne change** : la médiane par processus, un processus par passe, le rééchantillonnage de
   la méthode v3 ; l'écart entre passes de chaque cellule est publié.

L'erratum des points 2 et 3 (`docs/V4_SIZES.md`, 10.7) est réglé : la campagne mesure la base corrigée et les copies
`_cv` qui en partent.

## 4. Règles appliquées

| Règle | Fixée par | Dans le calcul final |
|---|---|---|
| Trois tailles | `docs/V4_SIZES.md`, 3, 8 (calcul 2) et 9 | sept noyaux (K1, K4 à K9) à trois tailles, chaque cellule avec ses références à chaque taille, moyenne des trois en logarithme, à poids égaux (dans les variantes, poids tirés : Dirichlet de concentration 20 dans la moitié, uniforme dans l'autre) ; K2 et K3 à leur taille |
| R1 | `docs/V4_EQUAL.md`, 3.1 | cellules naturelles de C, C++, Fortran, Zig, C3, D, Chapel et FreePascal dans leur mode vérifié, dans le code par défaut et là où la variante naturelle entre dans le plafond |
| R2 | `docs/V4_EQUAL.md`, 3.2 | K9 naturel en grille contiguë (`natural_flat`) pour les 13 langages à grille imbriquée, dans le mode R1 pour C++ et D |
| R3 | `docs/V4_EQUAL.md`, 3.3 et 11.8 | K4 `tuned` dans l'ensemble « meilleur de » du plafond de K4 (par C1) ; aucun assembleur en ligne |
| R4 | `docs/V4_EQUAL.md`, 3.4 | K3 au plafond : min(1, b3 / t), b3 de la machine du groupe (section 6) |
| R5 | `docs/V4_EQUAL.md`, 3.5 | K2 (trois tailles du score) mesuré par sept processus |
| K8 naturel | ce plan, 3 | sept processus |
| C1 à C6 | `docs/V4_CONVERGE.md`, 3 | plafond de chaque cellule : meilleure forme admise (variantes publiées, K4 `tuned`, formes du catalogue, formes `rq_`), d'après le relevé `results/converge/forms.json` |
| Grille | point 1 (`docs/GRID_AUDIT.md`) ; point 5 (`docs/V4_COST.md`, 11.7) | inchangée : règle v2 corrigée par l'audit, règle v1 dans la moitié des variantes, bruit de jugement |
| Poids | méthode v3 | contrôle 35 %, plafond 40 %, code par défaut 25 % au centre ; tirés dans les variantes |

Hors de la campagne : K10, hors score depuis la v2, n'est pas mesuré ; la piste ouverte (point 6) n'y entre pas, ses
formes ne sont pas remesurées et ses résultats restent publiés à côté du classement, rapportés au point 4
(`docs/V4_OPEN.md`, 11).

## 5. Constructions et cellules

Constructions, dans `/dev/shm/msbuild/<langage>/<nom>`, faites depuis les fichiers suivis par git :

| Construction | Source | Mode | Langages | Cellules |
|---|---|---|---|---|
| `pub` | `bench/<langage>` | publié | 25 | les cellules du score (`analysis/analyze_v3.py`, `needed_keys`, et variantes propres de `extra_variants` qui y entrent) |
| `cv` | `bench/<langage>_cv` | publié | 25 | celles de `cv_variants` : K4 `tuned`, formes du catalogue et `rq_`, K9 `natural_flat` |
| `chk` | `bench/<langage>` | R1 | C, C++, Fortran, Zig, C3, D, Chapel, FreePascal | cellules naturelles : K1 `natural` et `natural_shuffled`, K4 `natural_unsorted`, K5, K6 Q6 et Q1, K7, K8, K9 naturels |
| `unc` | `bench/<langage>` | R1' | Swift, Ada, Nim, Odin, Julia, Mojo, Go, OCaml, D | les mêmes |
| `cv_chk` | `bench/<langage>_cv` | R1 | C++, D | K9 `natural_flat` |
| `cv_unc` | `bench/<langage>_cv` | R1' | D, Nim, Mojo, Swift, Go, OCaml | K9 `natural_flat` |

* **Tailles.** Chaque construction des 19 langages compilés est faite pour chacun des trois jeux de tailles (publié,
  petit, grand : `tools/sizes/sizes.py`, `SETS`) ; pour les six langages sans construction, la copie de chaque jeu
  substitue les constantes de taille (`tools/sizes/patches.py` : `PATCHES` pour `pub`, `chk`, `unc` ; `CV_PATCHES`
  pour `cv`), et Julia reçoit le mode R1' par l'option de son lanceur, comme au point 3.
* **Volume, par passe** : 2 978 cellules, dans 23 groupes (noyau, taille) : 1 715 de `pub`, 780 de `cv`, 216 de `chk`,
  243 de `unc`, 6 de `cv_chk`, 18 de `cv_unc`. Avec les processus supplémentaires de K2 et de K8 naturel : 3 380
  processus dans la passe 0, 3 179 dans les passes 1 et 2.
* **Empreinte.** La place des constructions dans `/dev/shm`, comptée dans la limite de mémoire du groupe, est mesurée
  avant la campagne et publiée.
* **Contrôle des constructions.** L'empreinte SHA-256 de chaque binaire (ou de chaque fichier exécuté pour les langages
  sans construction) est enregistrée (`results/final/builds.txt`). Après un redémarrage, les constructions sont
  refaites depuis les mêmes sources et comparées : sur le même modèle de processeur, elles doivent être identiques ;
  toute différence est publiée, avec les groupes mesurés de part et d'autre.
* **Aucun code nouveau.** Seule exception : une cellule qui échoue à l'étalonnage (section 7) est corrigée avant la
  passe 0, par un écart daté (cellule, cause, changement), et validée de nouveau.

## 6. Hôte et changements d'hôte

* **Modèle.** La campagne se fait sur des machines du modèle 6/207/2, vérifié avant chaque processus. Si une machine
  d'un autre modèle arrive, la règle de `docs/V4_SIZES.md` (5) s'applique : le modèle ne se choisit pas depuis la
  session, toute la campagne est refaite sur le nouveau modèle, et les mesures de l'ancien sont gardées à part.
* **Caractérisation.** Chaque machine est caractérisée à son arrivée, au repos, avant sa première mesure
  (`tools/sizes/hwchar.sh`, `results/hw/machine<N>`), et numérotée ; chaque enregistrement porte son numéro.
* **Unité : le groupe.** Un groupe (noyau, taille) d'une passe est toujours mesuré en entier sur une même machine :
  les langages qui s'y comparent le sont sur le même hôte. Si un redémarrage interrompt un groupe, les enregistrements
  de ce groupe dans cette passe sont mis à part (`results/final/discarded`) et le groupe est refait en entier, le
  premier sur la nouvelle machine ; l'ordre des groupes restants ne change pas. Un groupe terminé n'est jamais refait.
* **Reprise.** Après un redémarrage : caractérisation, constructions, contrôle des empreintes, puis reprise.
* **b3 (R4).** Mesuré à machine au repos (`tools/k3_align.c`, deux exécutions, médiane des 16 décalages de chacune)
  juste avant et juste après chaque groupe de K3, sur sa machine ; la moyenne des deux est le b3 du groupe, qui
  normalise les processus de K3 de ce groupe (section 8). b3 est aussi mesuré au début et à la fin de la campagne.
* **Bornes physiques.** Celles de la méthode (bande passante au volume des données, STREAM triad, pic de calcul,
  fréquence) sont prises, quantité par quantité, à la médiane des caractérisations des machines qui ont mesuré ; avec
  une seule machine, les siennes.
* Le rapport donne la machine de chaque groupe de chaque passe.

## 7. Étalonnage, validation et campagne

* **Étalonnage et validation, en une phase, avant la passe 0.** Chaque cellule, à chaque taille, est exécutée une fois
  (un processus, une répétition, après l'échauffement du pilote), dans l'ordre des groupes de la passe 0. Cette
  exécution fixe les répétitions (environ 3 s par processus, au moins 3 et au plus 10 000 ; une seule au-delà de
  300 s) et l'échauffement (langages à JIT : au moins 3 répétitions et au moins une seconde), comme aux points 2 à 4,
  et vérifie la somme de contrôle de la taille (`results/sizes/expected.json`, règles de tolérance de
  `docs/V4_SIZES.md`, 4.1). Une cellule fausse ou en erreur est corrigée avant la passe 0 (section 5). Une cellule
  « hors mémoire » (au-delà de 13 Gio, ou tuée par le noyau) ou au-delà de la limite de durée l'est de façon
  déterministe : elle est notée et n'est pas exécutée dans les passes ; l'analyse la remplit (section 8).
* **Passes.** Trois passes. Dans chaque passe, l'ordre des groupes est tiré au hasard (graine 20261123 + passe), puis,
  dans chaque groupe, celui des blocs (langage, construction, copie). Une cellule à sept processus (K2, K8 naturel) a
  trois copies dans la passe 0 et deux dans les passes 1 et 2, chacune dans son propre bloc, pour que ses processus
  se répartissent dans le groupe. Les données d'une seule taille d'un seul noyau sont dans `/dev/shm` à la fois
  (`tools/gendata.c`, mêmes graines et mêmes lois qu'au point 2).
* **Conditions, comme aux points 2 à 4.** Un processus par cellule et par copie ; vol de temps au-delà de 5 % : le
  processus est refait une fois ; sentinelle de mémoire (plus grand VmRSS du groupe de processus, 13 Gio) ; modèle du
  processeur vérifié avant chaque processus. Aucune autre mesure ne tourne pendant la campagne. Écritures dans
  `results/final/work`, recopiées et poussées à la fin de chaque groupe.

## 8. Analyse, fixée avant les mesures

La méthode v3 (même graine, 20 000 variantes, même rééchantillonnage, mêmes tirages des poids, des normalisations et
du jugement de la grille), sur les seules données de la campagne finale, avec les bornes physiques de la section 6.

**Calcul « Final »** (le classement de la v4) :
* **Plafond (E)** : chacune des douze cellules (K1, K3, K4, K5, Q6, Q1, Q6 et Q1 à quatre fils, K7, K8, K9, K9 à quatre
  fils) prend, à chaque taille, le meilleur temps parmi les formes admises du langage (C1 ; relevé
  `results/converge/forms.json`), la variante naturelle y entrant dans son mode R1 (huit langages) et, pour K9, sous
  sa forme contiguë (R2) ; elle est rapportée à ses références de cette taille (frontière des 25 langages à cette
  taille, ou borne physique du niveau de mémoire où tiennent les données), puis moyennée sur les trois tailles
  (section 4). K3 suit R4 : chaque temps de K3 est ramené au b3 de référence (moyenne de toutes les mesures de b3) par
  le rapport des b3 (t × b3 / b3 du groupe), puis la cellule vaut min(1, b3 / t).
* **Code par défaut (D)** : D1 (cellules naturelles, avec R1 et R2) et D2 (part de K1) à trois tailles ; D3 (latences
  de K8 naturel, sept processus) à trois tailles ; D4 (K2, sept processus) à sa taille ; empreinte de K1 inchangée.
* **Contrôle (C)** : la grille, inchangée.
* Chaque cellule nouvelle (absente de la base) est tirée par son propre générateur, à graine fixée par la cellule, le
  langage et la taille, pour être tirée de la même façon dans tous les calculs (comme aux points 3 et 4).
* **Cellule manquante** (hors mémoire ou au-delà de la limite de durée) : le temps admissible le plus lent des autres
  langages à cette taille, pour les seules variantes communes à tous les langages (`docs/V4_SIZES.md`, 6 et 8.1) ;
  chaque cas est publié.

**Sorties du calcul « Final »** : place de 1 à 25 (rang espéré), score au centre, rang plausible (90 %), étages (règle
v3 sans sa condition de réplication, comme aux points 2 à 6 : la v3 répliquait sur un second hôte, que cette campagne
n'a pas), part des variantes où chaque langage devance le suivant, les trois quantités séparées avec leurs rangs, le
classement sur les seules mesures (poids de la grille à 0, au centre et dans les variantes), le plafond par noyau et
les parts du code par défaut, et, par cellule, langage et taille, la forme retenue et son rapport à la meilleure forme
publiée.

**Sensibilités et décomposition** (information, publiées à côté) :
1. **Base, trois tailles** : formes publiées seules, code naturel publié, K3 sans R4 (le calcul 2 du point 2 sur la
   base corrigée) ;
2. « Final » sans une règle à la fois : **sans les tailles** (taille publiée seule), **sans R1**, **sans R2** (la
   structure idiomatique publiée, sensibilité prévue par R2), **sans C1** (formes publiées seules, donc sans R3),
   **sans R4** (K3 rapporté à la frontière ou à la borne de la méthode v3) ;
3. **R1' au lieu de R1** (sensibilité prévue par R1) ;
4. **Une taille à la fois** (petite, publiée, grande) ;
5. **Sélection indépendante** : la forme de chaque cellule choisie sur la passe 0 seule, la cellule estimée sur les
   passes 1 et 2 (calcul 5 du point 4) ;
6. **D3 et D4 sur trois processus** (le premier de chaque passe), pour l'effet de R5 et de la règle de K8 naturel.

Pour chaque calcul : places, rangs espérés, scores au centre, langages qui bougent de plus de deux places par rapport
à « Final ». En comparaison : le classement publié (tête du README, v3) et « Convergent, avec R4 » du point 4
(machine 33), avec les langages qui bougent de plus de deux places. Sorties : `results/final/analysis.json`,
`results/report_final.md`. L'outil (`analysis/final_v4.py`) est poussé avant la passe 0, essayé sur des données
fictives au format de la campagne.

## 9. Publication

* **Tête du README** : le classement « Final » remplace celui de la v3, dans le même tableau (rang, étage, langage,
  score, rang plausible, devance le suivant, ce qui le place là), avec les notes réécrites sur les données de cette
  campagne ; la section « Les mesures et la grille, séparément » est refaite de même ; le graphique est régénéré.
* **Le classement de la v3** (tableau, notes, errata du 30 octobre au 19 novembre, et la section « Pourquoi cet ordre,
  langage par langage » qui l'explique) passe dans `docs/RANKING_V3.md`, lié depuis la tête du README ; rien n'est
  effacé.
* **Le reste du README** est mis en accord avec le classement final : « Pourquoi cet ordre, langage par langage »
  réécrite sur ses chiffres, « Comment c'est mesuré », « Limites » et « Reproduire » pour la méthode de la v4 ; les
  sections des points 2 à 6 restent, chacune avec une ligne qui dit comment sa règle entre dans le classement final.
* Ce document (section 12, résultats), `docs/V4_PLAN.md`, le journal.

## 10. Ordre de travail

1. Ce plan, poussé.
2. Caractérisation de la machine 35 au repos, b3.
3. Outils : constructions (`tools/final/build.py`), pilote (`tools/final/campaign.py`), sauvegarde, analyse
   (`analysis/final_v4.py`) ; essayés, poussés avant la passe 0.
4. Constructions, empreinte, étalonnage et validation ; corrections éventuelles, datées.
5. Campagne : trois passes, poussées à la fin de chaque groupe.
6. Analyse, documents (README, `docs/RANKING_V3.md`, ce document, `docs/V4_PLAN.md`, journal), rapport.

## 11. Écarts datés

1. **K4 `tuned` de Java faux au-delà de 2^31 (22 novembre, 16 h 21, pendant l'étalonnage, avant toute passe).** À la
   grande taille (2^28 octets), la cellule rend -67 246 612 au lieu de 25 702 557 164 : les 16 voies `int` de la forme
   cumulaient tout le tableau, et `reduceLanesToLong` de l'API Vector réduit en `int` avant d'élargir. À la taille
   publiée, la somme (1,6·10^9) tient sous 2^31 ; la forme n'en était pas moins hors de la règle C2, 2 (« un
   accumulateur entier doit tenir par construction »), et la relecture des preuves du point 4 l'avait laissée passer.
   Correction (`bench/java_cv/Ms.java`) : chaque bloc de 128 tours est réduit en `int` (au plus 2 088 960) et ajouté à
   une somme de 64 bits ; la cellule est reconstruite et de nouveau étalonnée et validée à ses trois tailles. Comme
   la validation ne voit que les données du banc, toutes les cellules de K4 sont aussi exécutées une fois sur des
   données extrêmes (2^28 octets à 255 : chaque accumulateur reçoit son maximum), avant la passe 0
   (`tools/final/k4_extreme.py`, `results/final/k4_extreme.txt`).
