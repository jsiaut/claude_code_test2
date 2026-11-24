# Méthode du classement (v4.1)

*État au 24 novembre 2026. Ce document décrit en un seul endroit la méthode qui produit le classement publié. Elle a
été fixée par étapes, chacune par un plan poussé avant ses mesures ou ses calculs ([`HISTORY.md`](HISTORY.md)). Le plan
de la campagne dont viennent les mesures, avec ses écarts datés et son procès-verbal, est [`V4_FINAL.md`](V4_FINAL.md) ;
celui des quatre corrections de l'analyse (A1 à A4), [`V4_1.md`](V4_1.md) ; le contrat des noyaux est
[`SPEC.md`](SPEC.md) ; le calcul est `analysis/final_v4.py`.*

## 1. Ce qui est classé

La *mechanical sympathy* au sens large : écrire du logiciel qui travaille avec le matériel (disposition des données,
lignes de cache et faux partage, écrivain unique, SIMD, hiérarchie mémoire, allocation, exécution colonnaire). Un
langage l'incarne dans la mesure où il donne le contrôle de ces aspects, où ce contrôle atteint les limites du matériel
quand on l'exerce, et où le code par défaut va déjà dans le sens du matériel, sans coût caché.

| Pilier | Poids au centre | Ce qu'il dit | D'où il vient |
|---|---|---|---|
| Contrôle (C) | 35 % | ce que le langage permet d'exprimer | grille jugée de 34 capacités, chaque case appuyée par une sonde (7) |
| Plafond (E) | 40 % | ce qu'atteint le meilleur code du langage | huit noyaux, meilleure forme admise (2 à 5) |
| Code par défaut (D) | 25 % | ce que donne le code qu'on écrit sans y penser | variantes naturelles, empreinte, latences, chaîne de pointeurs (8) |

Périmètre : 25 langages, une chaîne de référence chacun (`env/toolchains.txt`), dernière version stable au 28 octobre
2026 (Swift, FreePascal, BQN et PHP ajoutés du 5 au 7 novembre) ; bibliothèque standard seule ; compilation pour le
CPU hôte, ni PGO ni LTO ; runtimes à leurs réglages par défaut, sauf le nombre de fils, fixé à quatre.

## 2. Noyaux et validation

Neuf noyaux, un par principe. Leur contrat (données, calcul, interface, variantes) est dans [`SPEC.md`](SPEC.md).

| Noyau | Principe | Ce qui est mesuré |
|---|---|---|
| K1 | Disposition des données | énergie de particules de 64 octets : AoS, SoA, collection naturelle, dans l'ordre et permutée |
| K2 | Hiérarchie mémoire | chaîne de pointeurs, 4,2 millions de sauts dépendants |
| K3 | Faux partage, écrivain unique | 4 fils, un compteur chacun, voisins ou espacés, avec ou sans `lock` |
| K4 | Prédiction de branchement | somme conditionnelle d'octets |
| K5 | SIMD | produit scalaire |
| K6 | Requêtes OLAP colonnaires | TPC-H Q6 et Q1 simplifiées, à 1 et 4 fils |
| K7 | Agrégation par hachage | GROUP BY, 16 lignes par clé |
| K8 | Allocation, latence de queue | 16 384 requêtes qui construisent et parcourent un arbre, chronométrées une à une |
| K9 | Stencil (HPC) | Jacobi 2D, à 1 et 4 fils |

K10 (file SPSC), hors score depuis la v2, n'est plus mesuré ; son code reste dans les implémentations.

Chaque programme chronomètre lui-même sa section de calcul et rend une somme de contrôle. Toute cellule doit rendre, à
chaque taille, la somme de l'implémentation C (`results/expected.json` pour la taille publiée,
`results/sizes/expected.json` pour les autres) : égalité exacte pour les entiers, tolérance relative de 1e-6 (K1),
1e-3 (K5) et 1e-9 (K9) pour les flottants ; une somme entière au-delà de 2^53 se compare à l'arrondi d'un double près
(BQN n'a que des doubles). Une cellule fausse à l'étalonnage est corrigée avant les passes ; un processus dont une
somme est fausse est écarté de l'analyse (aucun dans la campagne).

## 3. Tailles

Sept noyaux comptent à trois tailles ; K2 et K3 à la leur.

| Noyau | Paramètre | Petite | Publiée | Grande |
|---|---|---|---|---|
| K1 | particules de 64 octets | 2^14 (1 Mio) | 2^22 (256 Mio) | 2^24 (1 Gio) |
| K4 | octets | 2^20 (1 Mio) | 2^24 (16 Mio) | 2^28 (256 Mio) |
| K5 | n × répétitions (2^27 produits à chaque taille) | 2^11 × 2^16 (16 Kio, L1 : la publiée) | 2^15 × 2^12 (256 Kio, L2) | 2^21 × 2^6 (16 Mio, L3) |
| K6 | lignes de 13 octets | 2^16 | 2^24 | 2^26 |
| K7 | lignes / clés distinctes | 2^16 / 2^12 | 2^24 / 2^20 | 2^27 / 2^23 |
| K8 | profondeur de l'arbre long / d'une requête | 16 / 8 | 20 / 10 | 23 / 12 |
| K9 | côté M des deux grilles de `f64` | 2^8 (1 Mio) | 2^11 (64 Mio) | 2^13 (1 Gio) |
| K2 | tableau | 16 Kio, 256 Kio et 8 Mio : les trois tailles du score | | |
| K3 | sans données | 4 × 2^25 incréments | | |

* **Données.** `tools/gendata.c`, déterministe (mêmes graines et mêmes lois à chaque taille). Les fichiers de la taille
  publiée sont dans `/opt/msdata` (empreintes : `env/msdata.sha256`) ; ceux des autres tailles sont produits à la
  demande dans `/dev/shm`, un noyau et une taille à la fois (`tools/sizes/sizes.py`).
* **Code.** Seule la taille change. Les 19 langages compilés reçoivent les tailles à la construction (variables
  `MS_*` lues par leur `build.sh`) ; pour les six langages sans construction (Python, Lua, PHP, BQN, JavaScript,
  Julia), une copie du source reçoit les constantes de la taille (`tools/sizes/patches.py`, occurrences vérifiées).
* **Dans le score.** Chaque cellule est calculée à chaque taille avec ses propres références, puis moyennée en
  logarithme sur les trois tailles, à poids égaux au centre (8).
* **Cellule manquante.** Une cellule qui dépasse 13 Gio de mémoire ou que le système tue est « hors mémoire » ; elle
  prend le temps admissible le plus lent des autres langages à cette taille (variantes communes à tous les langages
  seulement). Six cas, tous à la grande taille : les quatre variantes de K1 de BQN, K1 naturel de Python dans l'ordre
  et permuté.

## 4. Formes du plafond (règles C1 à C6)

* **C1.** Le plafond de chaque cellule prend le meilleur temps parmi les formes admises que le langage a écrites :
  variantes publiées (`tuned`, `mt`…, définies par `SPEC.md`), K4 `tuned` (R3), formes du catalogue, formes propres à
  son runtime.
* **C2, admission.** Une forme fait le calcul de la spécification sur les données telles qu'elles sont stockées, dans la
  zone chronométrée prévue ; elle est exacte pour toute donnée admise, pas seulement pour les fichiers du banc (un
  accumulateur entier tient par construction, ce qu'un commentaire justifie) ; pour K8, chaque nœud est écrit avec sa
  valeur et ses liens et la somme suit les liens ; langage et bibliothèque standard seuls, sans assembleur en ligne ni
  option propre à une variante ; elle lit les tailles comme les variantes publiées.
* **C3, le catalogue**, porté dans tout langage qui peut l'écrire :

  | Cellule | Forme | Définition courte |
  |---|---|---|
  | K4 | `tuned` | SIMD explicite (types vectoriels du langage ou intrinsèques de sa chaîne) |
  | K4 | `swar` | octets traités par mots de 64 bits, voies de 16 bits vidées toutes les 128 mots |
  | K5 | `tuned_v` | vecteurs de 16 `f32`, quatre accumulateurs, 64 éléments par tour |
  | Q6 | `tuned_v`, `tuned_s` (repli) | blocs de 16 lignes en vecteurs explicites ; sans branchement, prédicat en 0/1 |
  | Q1 | `tuned_v`, `tuned_s` (repli) | 16 lignes par tour, additions masquées par groupe ; une passe à 30 accumulateurs |
  | Q6, Q1, K9 à 4 fils | `mt_pool`, `mt_pool_v`, `mt_pool_s` | réserve de quatre fils créés une fois par processus, attente bloquante entre deux appels |
  | K7 | `tuned_pf`, `tuned_oa` (repli) | adressage ouvert, cases de 16 octets, hachage de Fibonacci, lots de 16 clés préchargées |
  | K8 | `tuned_val`, `tuned_it` | arène de nœuds indexés : état passé par valeur ; ou pile explicite |
  | K9 | `tuned_v` | vecteurs explicites de 8 `f64` sur grilles plates alignées |

* **C4, portage.** Pour chaque langage et chaque forme, un état : *présente* (une variante existante répond à la
  définition), *écrite*, *non écrivible* (capacité absente, preuve à l'appui) ou *sans objet* (repli inutile). Le
  relevé est dans `tools/converge/inventory.py`, qui écrit `results/converge/inventory.md` (à lire) et
  `results/converge/forms.json` (lu par le pilote et par l'analyse).
* **C5.** Une forme dont le gain tient à un coût propre au runtime d'un langage (tables de Lua, conversion des
  tableaux typés de JavaScript…) entre dans le plafond de ce langage sous un nom en `rq_`, sans être portée ailleurs.
* **C6.** La variante `mt` publiée (fils créés à chaque appel) reste mesurée à côté des réserves de fils.

Les formes ajoutées sont dans `bench/<langage>_cv`, copie de `bench/<langage>` qui en est un sur-ensemble ; ses
variantes nouvelles sont déclarées dans `cv_variants`. Le rapport donne, cellule par cellule et taille par taille, la
forme retenue. Le biais de choisir le minimum parmi plusieurs formes est contrôlé par la sensibilité « sélection
indépendante » (10).

## 5. Conditions égales (règles R1 à R5) et code naturel

Le code naturel est le code qu'un développeur écrit en suivant la documentation du langage : type d'enregistrement et
conteneur par défaut, aucune annotation de performance ([`NATURAL.md`](NATURAL.md)).

* **R1, vérifications actives pour tous.** Le code naturel est compilé dans le mode de publication de la chaîne, avec
  les vérifications à l'exécution qu'elle offre, activées par son option documentée quand ce mode les retire. Huit
  langages les reçoivent ainsi (construction `chk`) :

  | Langage | Mode publié | Option de R1 |
  |---|---|---|
  | C | clang `-O3` | `-fsanitize=array-bounds -fsanitize-trap=array-bounds` (tableaux de taille connue seulement) |
  | C++ | g++ `-O3` | `-D_GLIBCXX_ASSERTIONS` (conteneurs de libstdc++) |
  | Fortran | gfortran `-O3` | `-fcheck=bounds` |
  | Zig | `-O fast` | `-O safe` |
  | C3 | `-O3` | `--safe=yes` |
  | D | `-O3 -release` | `-boundscheck=on` |
  | Chapel | `--fast` | `--checks` |
  | FreePascal | `-O3` | `-Cr -Co` |

  Les 17 autres gardent déjà leurs vérifications. La règle égalise la politique, pas la liste des vérifications, qui
  fait partie du langage : l'accès par pointeur de C et de C++ reste sans vérification. Les formes du plafond gardent
  le mode publié. **R1'**, en sensibilité : aucune vérification là où une option les retire (construction `unc` :
  Swift, Ada, Nim, Odin, Julia, Mojo, Go, OCaml, D).
* **R2, stencil naturel contigu.** K9 naturel est une grille contiguë pour tous ; les 13 langages dont l'idiome est un
  tableau de tableaux reçoivent la variante `natural_flat` (tableau 1D de leur conteneur par défaut, indexé `i*M + j`).
* **R3.** K4 admet une forme `tuned`, SIMD explicite compris ; aucune forme n'est en assembleur en ligne.
* **R4, K3 rapporté à une boucle de référence.** Sur ce processeur, la boucle de l'écrivain unique coûte de un à sept
  cycles par incrément selon la place du code dans sa ligne de 64 octets. La cellule de K3 vaut donc min(1, b3 / t) :
  b3 est le temps de la même boucle écrite en assembleur (`tools/k3_align.c`), au plus lent de ses 16 décalages (A2 ;
  leur médiane jusqu'au 23 novembre), moyenne de deux exécutions, mesuré juste avant et juste après chaque groupe de
  K3 ; les temps de K3 d'un groupe sont ramenés au b3 de référence (moyenne de toutes les mesures) par le rapport des
  b3. Une boucle sans `lock` ne vaut ainsi pas moins que la boucle de référence à son plus mauvais placement.
* **R5.** K2 (dont vient D4) est mesuré par sept processus par cellule au lieu de trois ; la campagne finale applique
  la même règle à K8 naturel (dont vient D3).

## 6. Campagne

Outils : `tools/final/` ([`V4_FINAL.md`](V4_FINAL.md), 5 à 7, pour le détail et le procès-verbal).

* **Machine.** Un seul modèle de processeur (famille 6, modèle 207, pas 2 : Emerald Rapids), vérifié avant chaque
  processus. Chaque machine est caractérisée au repos avant de mesurer (`tools/sizes/hwchar.sh`, `tools/hwprobe.c` :
  bande passante selon le volume, STREAM, débit crête, fréquence) dans `results/hw/machine<N>` ; ces relevés donnent
  les bornes physiques (8). Un groupe (noyau, taille) d'une passe est toujours mesuré en entier sur une même machine.
* **Constructions** (`tools/final/build.py`), depuis les fichiers suivis par git, dans `/dev/shm` : `pub`
  (`bench/<langage>`), `cv` (`bench/<langage>_cv`), `chk` et `unc` (modes R1 et R1'), `cv_chk` et `cv_unc`, chacune
  aux trois jeux de tailles ; l'empreinte de chaque fichier exécuté est enregistrée (`results/final/builds.jsonl`).
* **Étalonnage et validation** (`campaign.py calibrate`). Chaque cellule, à chaque taille, est exécutée une fois : la
  somme de contrôle est vérifiée, et la durée fixe le nombre de répétitions (environ 3 s par processus, de 3 à 10 000 ;
  une seule au-delà de 300 s) et l'échauffement (une répétition ; au moins trois et au moins une seconde pour Java, C#,
  JavaScript et Julia).
* **Passes** (`campaign.py run`). Trois passes ; dans chacune, l'ordre des groupes puis celui des blocs (langage,
  construction) sont tirés au hasard, à graine fixe. Un processus par cellule et par passe ; trois, deux et deux pour K2
  et K8 naturel. Un processus dont le vol de temps de l'hyperviseur dépasse 5 % est refait une fois. Rien d'autre ne
  tourne pendant la campagne.
* **Volume.** 2 978 cellules, 9 738 processus, du 22 novembre, 17 h 16, au 23 novembre, 19 h 40 (UTC), sur la
  machine 35, sans redémarrage ; aucun processus en échec.

## 7. Grille de contrôle (pilier C)

34 capacités en six catégories, équipondérées dans chaque catégorie : disposition des données (A, 8 capacités, 25 %),
gestion de la mémoire (B, 5, 20 %), SIMD et vectorisation (C, 5, 20 %), concurrence (D, 5, 15 %), contrôle de la
génération de code (E, 7, 10 %), HPC et OLAP (F, 4, 10 %). La liste, les notes et leurs justifications sont dans
`analysis/capabilities.py` et, mises en page, dans [`CAPABILITIES.md`](CAPABILITIES.md).

* **Notes.** 1, ½ ou 0. **Règle v2** (score central, `analysis/capabilities_v2.py`) : 1 si la capacité s'exprime avec
  la chaîne de référence telle qu'elle est livrée, sous une forme stable et complète ; ½ si elle est expérimentale,
  réservée à une unité interne ou partielle ; 0 si elle est absente ou seulement accessible par une bibliothèque tierce
  ou par une FFI vers du code non intrinsèque. La vectorisation automatique mesurée (C3) n'y compte pas : le plafond et
  le code naturel la mesurent déjà. **Règle v1**, d'origine : ½ aussi pour ce qui est livré hors norme ou propre à un
  compilateur, et C3 comptée (`results/vectorization.json`) ; elle pénalise les langages normalisés et ne sert plus,
  depuis A1, que dans la sensibilité « Sans A1 ».
* **Une seule règle pour la libc et les FFI.** Compte ce que la chaîne livre, y compris les intrinsèques que le
  langage importe par sa FFI ; appeler du code C ordinaire par une FFI ne compte pas, sauf pour C et C++, dont la libc
  est la bibliothèque système ; les types C qu'une FFI livrée définit valent ½.
* **Preuves.** Chaque case a une ligne `CAP;<case>;<note>;<preuve>` produite par une exécution
  (`probes/<langage>/run.sh`, sortie dans `results/probes/<langage>.txt`). La preuve porte sa classe : **[exécutée]**,
  un programme se sert de la capacité et imprime un fait observable ; **[échec]**, la forme canonique est refusée ou le
  comportement contraire est mesuré ; **[recherche]**, pour une API absente, fouille des sources livrées avec des
  motifs fixés d'avance (`tools/grid_audit/`, relevés dans `results/grid_audit/search/`), qui ne voit que ce que son
  motif décrit. `analysis/check_probes.py` confronte les 825 lignes à la grille : aucune divergence.

## 8. Score

Pour une cellule, le temps t d'un langage est la moyenne géométrique des médianes de ses processus, pour sa forme la
plus rapide parmi les formes admises.

* **Plafond.** E = 100 × moyenne géométrique des scores de huit noyaux (K1, K3 à K9). Le score d'un noyau est la moyenne
  géométrique de ses mesures (quatre pour K6 : Q6 et Q1 à 1 et 4 fils ; deux pour K9 ; une ailleurs) ; une mesure vaut
  référence / t, moyennée en logarithme sur les trois tailles ; les trois mesures à quatre fils ne comptent qu'aux
  tailles publiée et grande (A4 : à la petite taille, elles mesurent le réveil des fils). La référence est la frontière,
  le meilleur temps des 25 langages à cette taille ; dans une variante sur deux, c'est la borne physique de la machine
  (octets à déplacer sur la bande passante du niveau de mémoire où ils tiennent, opérations sur le débit crête), le
  rapport étant alors plafonné à 1. K3 suit R4.
* **Code par défaut.** D = 100 × (0,5 D1 + 0,15 D2 + 0,15 D3 + 0,2 D4).
  * D1, code naturel : comme le plafond, avec la seule variante naturelle (K1, K4, K5, Q6, Q1, K7, K8, K9), rapportée
    au meilleur code naturel des 25 langages à chaque taille (A3 ; à la frontière du plafond jusqu'au 23 novembre).
  * D2, coût de structure : moyenne géométrique de min(1, 64 / octets par particule) (`results/footprint.json`) et de
    min(1, t naturel / t naturel permuté) sur K1, ce second terme aux trois tailles.
  * D3, prévisibilité : sur les latences des requêtes de K8 naturel, moyenne géométrique de (meilleur p99,9 / p99,9)
    et de (meilleur maximum / maximum), aux trois tailles, chaque quantile étant la médiane, sur les répétitions, du
    quantile de la répétition ; dans une variante sur deux, les mêmes rapports relatifs à la médiane p50.
  * D4, hiérarchie mémoire : moyenne géométrique, sur les trois tailles de K2, de min(1, meilleur temps / t) (dans une
    variante sur deux, le temps du C sert de référence).
* **Contrôle.** C = 100 × somme, sur les catégories, du poids de la catégorie fois la moyenne de ses cases.
* **Score.** 0,35 C + 0,40 E + 0,25 D (dans une variante sur deux, la moyenne géométrique pondérée).

## 9. Incertitude et ordre publié

* **Bruit de mesure.** 2 000 rééchantillonnages. Avec trois processus, une cellule ne peut pas estimer seule sa
  variance : les résidus des cellules sont regroupés par noyau et par classe d'implémentation (compilée à l'avance,
  JIT, interprète ; moins de 20 résidus : tout le noyau), et chaque tirage ajoute à l'estimation de la cellule la
  moyenne de résidus tirés dans son réservoir. Les références restent celles des estimations ponctuelles. Les latences
  sont rééchantillonnées par processus puis par répétition.
* **20 000 variantes de l'analyse.** Chacune tire : un rééchantillonnage ; cinq choix de méthode à deux options
  (estimateur : moyenne géométrique ou minimum des processus ; référence du plafond ; formes de D3 et de D4 ;
  agrégation) ; les poids des piliers et ceux des trois tailles (autour de leurs valeurs du centre dans une variante sur
  deux, uniformes sur le simplexe dans l'autre), ceux des noyaux, des parts de D et des catégories de la grille (autour
  de leurs valeurs du centre) ; un bruit de jugement, chaque case jugée changeant de note avec une probabilité de 10 %.
* **Ce qui est publié.** L'ordre est le **rang moyen** sur les variantes. Le **rang plausible** est l'intervalle des
  rangs dans 90 % des variantes. « Devance le suivant » est la part des variantes où un langage passe devant celui de
  la ligne suivante. Le **score** affiché est celui du centre (poids et choix principaux, estimation ponctuelle) : il
  ne suit pas toujours l'ordre. Les **étages** : une frontière sépare deux langages voisins si chaque langage au-dessus
  devance chaque langage au-dessous dans au moins 95 % des variantes.
* **Reproductibilité.** Les graines sont fixes : le calcul redonne ses sorties à l'octet près (`tools/check.sh`).

## 10. Sensibilités publiées

`results/report_final.md` donne, à côté du classement, la place de chaque langage dans dix-sept autres calculs faits
avec les mêmes tirages : formes publiées seules et code naturel publié à trois tailles (« Base ») ; « Final » sans une
règle à la fois (sans les tailles, sans R1, sans R2, sans C1, sans R4) ; R1' au lieu de R1 ; une taille seule (petite,
grande) ; sélection indépendante (la forme de chaque cellule choisie sur la passe 0, estimée sur les passes 1 et 2) ; D3
et D4 sur trois processus ; sur les seules mesures (poids de la grille à 0) ; « Final » sans une correction de la v4.1 à
la fois (« Sans A1 » à « Sans A4 ») ; sans aucune (« Méthode du 23 novembre », qui redonne le classement publié ce
jour-là).

## 11. Vérifier, recalculer, remesurer

```bash
sh tools/check.sh --rapide
```

```bash
sh tools/check.sh
```

```bash
python3 analysis/final_v4.py
```

```bash
python3 analysis/charts_final.py
```

Le premier contrôle prend environ 30 s, le second 15 min (classement complet comparé à l'octet près) ; aucun ne
demande de chaîne de compilation. Les deux commandes suivantes réécrivent `results/final/analysis.json`,
`results/report_final.md` et le graphique.

Remesurer demande les 25 chaînes de `env/toolchains.txt`, installées aux chemins que lisent les `build.sh`, et les
données de `/opt/msdata` (`tools/gendata.c`) ; le dépôt n'a pas de script d'installation. Sur une machine du modèle
6/207/2 :

```bash
sh tools/final/machine.sh 36
```

```bash
python3 tools/final/campaign.py calibrate
```

```bash
python3 tools/final/k4_extreme.py
```

```bash
python3 tools/final/campaign.py run
```

`machine.sh` caractérise la machine, mesure b3 et fait les constructions ; `calibrate` étalonne et valide chaque
cellule ; `k4_extreme.py` contrôle les formes de K4 sur des données extrêmes ; `run` fait les trois passes et
enregistre chaque groupe (`tools/final/save_progress.sh`, qui committe et pousse sur la branche courante). Pour essayer
une seule implémentation, construite sur place :

```bash
python3 tools/driver.py c
```
