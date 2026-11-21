# v4, point 4 : un code optimisé convergent — plan (21 novembre 2026)

*Plan d'ensemble : `docs/V4_PLAN.md` (point 4). Ce plan est poussé avant tout changement de code et toute mesure ; les
écarts éventuels seront datés et justifiés dans `docs/METHODOLOGY.md`.*

## 1. Question

Le plafond (pilier E, 40 % du score au centre) prend, cellule par cellule, la meilleure variante optimisée de chaque
langage. Sa valeur dépend donc aussi de l'effort mis dans chaque implémentation. Les remarques ont trouvé de
meilleures formes pour une quinzaine de langages : K8 itératif en C (× 0,40 sous clang), Q1 en une passe en Julia
(× 0,53), K8 en pile explicite en C# (× 0,51). La règle commune des remarques (`docs/FORTRAN.md`, 3.1) les a gardées
hors du classement : un erratum entre, une meilleure forme reste une sensibilité. Et personne ne les a tentées dans
les autres langages. La sixième demande de la troisième remarque générale (`docs/AUDIT3_2026-11-18.md`) est de faire
converger le code optimisé : accepter la meilleure forme, et tenter dans tous les langages toute forme admise pour
l'un. Le point 4 dresse un catalogue des formes par cellule du plafond, le porte dans tous les langages qui peuvent
l'écrire, mesure l'effet sur le classement et fixe d'avance la règle de la campagne finale de la v4.

## 2. Faits établis avant le plan

* **Cellules du plafond** (`analysis/analyze_v2.py`, `E_V2`) : K1 (meilleur de `aos` et `soa`), K3 (`sw_padded`,
  `rmw_padded`), K4 (deux formes publiées, plus `tuned` avec R3), K5, K6 Q6 et Q1 à un fil (`natural`, `tuned`) et à
  quatre fils (`mt`), K7 (`natural`, `tuned`), K8 (`natural`, `tuned`, `tuned_alloc`), K9 à un fil (`natural`,
  `tuned`) et à quatre fils (`mt`). K2 (part D4) n'a qu'une forme, fixée par la spécification ; K10 n'entre pas au
  score.
* **Écarts sur la machine 32** (base du point 3, binaires publiés, `results/equal/raw` ; sources non corrigées pour
  20 langages, voir 4.1). Rapport au plus rapide des 25 langages, pour les quatorze premiers du classement :

  | Cellule | Frontière | Langages ≥ 0,9 (sur 14) | Médiane | Le plus bas |
  |---|---|---|---|---|
  | K1 (aos, soa) | Julia, 2,37 ms | 12 | 0,97 | 0,78 (Ada) |
  | K3 | D, 16,73 ms | 2 | 0,19 | 0,18 (Julia) |
  | K4 (deux formes publiées) | Chapel, 1,17 ms | 1 | 0,75 | 0,09 (Fortran) |
  | K5 | C++, 3,36 ms | 6 | 0,81 | 0,58 (Julia) |
  | K6 Q6 un fil | Zig, 10,07 ms | 3 | 0,77 | 0,62 (C) |
  | K6 Q1 un fil | C3, 20,36 ms | 2 | 0,65 | 0,27 (Julia) |
  | K6 Q6 quatre fils | Chapel, 1,73 ms | 2 | 0,74 | 0,17 (Ada) |
  | K6 Q1 quatre fils | Zig, 5,51 ms | 3 | 0,65 | 0,23 (D) |
  | K7 | Chapel, 142,19 ms | 6 | 0,89 | 0,67 (Julia) |
  | K8 | Ada, 73,05 ms | 1 | 0,27 | 0,19 (Julia) |
  | K9 un fil | Swift, 12,58 ms | 2 | 0,65 | 0,50 (Nim) |
  | K9 quatre fils | Chapel, 3,38 ms | 1 | 0,33 | 0,26 (Zig) |

  K1 est à la bande passante pour presque tous (borne de l'hôte : 2,35 ms) ; K3 relève de R4 (point 3) ; ailleurs, le
  plus lent des quatorze premiers fait de 1,5 à 6 fois le temps de la frontière (11 fois pour K4 sans SIMD explicite).
* **Formes de la frontière** (lecture des sources) : K5, 16 voies `f32` et quatre accumulateurs (C++ `std::simd`, C
  AVX-512) ; Q6, vecteurs explicites de 16 `i32`, prédicat par comparaisons et sélection, accumulation en `i64` (Zig) ;
  Q1, l'algorithme de la référence C, 16 lignes par itération, additions masquées par groupe, accumulateurs 32 bits
  vidés toutes les 4 096 lignes (C, C3, Zig) ; K6 et K9 à quatre fils, fils gardés par le runtime (Chapel,
  `coforall` et `forall`) ou créés à chaque appel (Zig, C) ; K7, adressage ouvert, sondage linéaire, hachage de
  Fibonacci, lots de 16 clés hachées et préchargées avant insertion (Chapel ; c'est aussi la forme de la remarque sur
  Julia) ; K8, arène de nœuds indexés dont l'état passe par copie (Ada : paramètres `in out` d'un type élémentaire,
  passés par copie, RM 6.2), alors que C, avec la même arène, le fait passer par la mémoire (`int32_t *top`,
  `int64_t *counter`) et prend 3,7 fois plus de temps ; K9, vecteurs explicites de 8 `f64` sur tampons alignés sur 64
  octets (Swift).
* **Formes trouvées par les remarques, mesurées, restées en sensibilité** (rapport au code publié, même hôte, intervalle
  à 95 % dans le document cité) : K8 par valeur, C 0,57 sous clang et 0,45 sous gcc (`docs/C.md`), OCaml 0,77 ; K8
  itératif à pile explicite, C 0,40 (clang), C# 0,51, Go 0,62, Java 0,64, JavaScript 0,73 ; Q1 en une passe, Java
  0,40 (0,51 à quatre fils), Julia 0,53, mais Go 1,36 (ses trente accumulateurs vectoriels ne tiennent pas en
  registres) et C# 4,05 sous le protocole publié, 0,84 avec FullOpts ; Q6 par masques, JavaScript 0,60, OCaml 0,86 ;
  K7 par lots préchargés,
  Julia 0,69 (Java, sans instruction de préchargement, 0,80 avec lecture anticipée, moins que le noyau isolé seul,
  0,72) ; K5 réduite en registres, Go 0,75 ; K9 en vecteurs explicites, Go 0,78 et 0,73 (Java 0,96 : C2 vectorisait
  déjà) ; K9 à voisins glissants, Lua 0,87, JavaScript 0,88 ; réserve de fils, Java 0,81 sur K9 `mt` (qui crée ses fils
  à chacune de ses quatre itérations), 1,07 sur K6 (dans le bruit), et C# (`Parallel.For`) 0,71 sur Q6 et 0,63 sur
  K9. Formes propres à un runtime : K7 à table tassée en
  Lua (0,71) et à deux mots par case en OCaml (0,875), Q6 à tests imbriqués en Lua (0,51), K5 sur données converties
  en `f64` en JavaScript (0,88), K7 isolé dans sa méthode en Java (0,72), K8 spécialisé sur la profondeur en Julia
  (0,83, avec des incréments sans conversion vérifiée), arène sans vérification de débordement en Nim. Les autres
  remarques (Nim, Rust, Odin, C3, C++, Chapel, Fortran, FreePascal, BQN) ont mesuré des formes des mêmes familles.
* **Écarts sans explication dans les sources** : K9 à un fil, C, Swift et Chapel (12,2 à 16,9 ms) contre Rust, Zig,
  C++, Odin, D, Nim, Julia, Go et Java (17 à 33 ms), aux trois passes ; K9 à quatre fils, Chapel, C, Swift et Fortran
  (3,3 à 5,5 ms) contre les autres (8,6 à 14,3 ms) ; Chapel fait Q6 à quatre fils 8 fois plus vite qu'à un fil, avec
  la même routine. Hypothèses, non vérifiées : alignement des tampons, distance entre les deux grilles modulo 4 Kio
  (repliement de 4 Kio), largeur des vecteurs (les formes rapides ont des vecteurs explicites de 512 bits ou un
  compilateur qui les choisit peut-être), pages géantes (mode `madvise` sur l'hôte), fils inoccupés du runtime de
  Chapel.
* **Règles en vigueur** : `docs/SPEC.md` (0 : le code optimisé emploie le langage et la bibliothèque standard livrée,
  options documentées comprises ; interdits : FFI vers du code écrit à côté, assembleur en ligne, bibliothèques
  tierces ; rien ne sort de la zone chronométrée) ; règle commune des remarques (ci-dessus) ; R3 (point 3, avec
  l'erratum `docs/V4_EQUAL.md`, 11.8 : l'assembleur en ligne n'est pas admis).

## 3. Règles communes, fixées ici pour la campagne finale de la v4

### 3.1 C1 : le plafond prend la meilleure forme admise

Le plafond de chaque cellule prend le meilleur temps parmi les formes admises que le langage a écrites : variantes
publiées, K4 `tuned` de R3, formes du catalogue (3.3) et formes propres à son runtime trouvées par sa remarque (3.5).
La règle commune des remarques ne vaut plus pour le code optimisé : une meilleure forme, une fois admise, compte.
Elle vaut toujours pour le code naturel (point 3, R1 et R2).

### 3.2 C2 : admission d'une forme

Une forme est admise si :

1. elle fait le calcul de la spécification du noyau (`docs/SPEC.md`) sur les données telles qu'elles sont stockées,
   dans la zone chronométrée prévue (la table de K7, allocation comprise ; chaque requête de K8), sans rien en sortir ;
2. elle est exacte pour toutes les données admises par la spécification, pas seulement pour les fichiers du banc : un
   accumulateur entier doit tenir par construction (taille de bloc et bornes des colonnes, justifiées en commentaire) ;
3. pour K8, chaque nœud est écrit avec sa valeur et ses deux liens, et la somme suit les liens (récursion ou pile) ;
   l'arbre peut être construit en tirant parti de sa forme complète (indices des enfants calculés) ;
4. elle respecte la règle du code optimisé de `docs/SPEC.md` (0), sans assembleur en ligne, et se construit avec les
   options de la construction publiée du langage (aucune option propre à une variante) ;
5. elle lit les paramètres de taille comme les variantes publiées (macros `MS_*`, constantes substituées : point 2),
   pour pouvoir entrer telle quelle dans la campagne finale.

### 3.3 C3 : le catalogue

Une forme entre au catalogue si elle est la forme de la frontière d'une cellule sur la machine 32 (section 2) ou si
une remarque l'a mesurée avec un gain d'au moins 10 % (rapport ≤ 0,90, intervalle à 95 % sous 1) dans au moins un
langage, et si ce gain ne tient pas à un coût propre à un runtime (3.5). Une forme de repli ne sert qu'aux langages
qui ne peuvent pas écrire la forme principale de la même cellule.

| Cellule | Forme (nom de la variante) | Définition | Origine |
|---|---|---|---|
| K4 | `tuned` (R3) | SIMD explicite (types vectoriels du langage ou intrinsèques de sa chaîne), point 3, 3.3 | point 3 |
| K4 | `swar` | octets traités par mots de 64 bits (ou du plus large entier natif) : octets ≥ 128 gardés par un masque tiré de leur bit de poids fort, sommés par voies de 16 bits, voies vidées au plus toutes les 128 mots, sans branchement sur les données | Swift (point 3, 3.3 : « relève du point 4 ») |
| K5 | `tuned_v` | vecteurs explicites de 16 `f32` (la plus grande largeur de la chaîne sur cet hôte), quatre accumulateurs indépendants, 64 éléments par tour, multiplication-addition contractée permise, réduction horizontale une fois par appel | frontière (C++, C) ; Go 0,75 |
| K6 Q6 | `tuned_v` | blocs de 16 lignes en vecteurs explicites : colonnes élargies en `i32`, prédicat par comparaisons, produit prix × remise en `i32` (≤ 500 000), sélection, accumulation en `i64` | frontière (Zig) |
| K6 Q6 | `tuned_s` (repli) | sans branchement : prédicat en 0/1 par soustractions non signées et comparaisons, `s += prix × remise × m` en 64 bits, sommes par blocs | JavaScript 0,60, OCaml 0,86 |
| K6 Q1 | `tuned_v` | algorithme de la référence C : 16 lignes par tour, masque de passage, groupe `2 × rf + ls`, par groupe un masque, compte par population du masque, additions masquées de la quantité, du prix et de `prix × (100 − remise)` en voies de 32 bits vidées toutes les 4 096 lignes, charge en 64 bits | frontière (C3, Zig, C) |
| K6 Q1 | `tuned_s` (repli) | une passe ; les 30 accumulateurs en variables locales ; par ligne, sélection des six groupes par masques, sans branchement ; accumulateurs de 64 bits, ou de 32 bits vidés avec la même preuve | Java 0,40, Julia 0,53 |
| K6 Q6, Q1, K9 à quatre fils | `mt_pool`, `mt_pool_v`, `mt_pool_s` (K9 : `mt_pool_a`) | réserve de fils : quatre fils de travail en tout (le fil principal compris), créés une fois par processus avant l'échauffement ; à chaque appel, quatre quarts contigus, réveil des fils, attente de leur fin ; entre deux appels, attente bloquante ; chaque quart exécute la forme à un fil désignée par le suffixe (aucun : la forme publiée) | frontière (Chapel) ; Java 0,81, C# 0,71 et 0,63 |
| K7 | `tuned_pf` | capacité `2^(LOG2+1)`, cases de 16 octets (clé `u32`, compte `u32`, somme `u64`) contiguës, allouées et remises à zéro dans la zone chronométrée, hachage `(clé × 0x9E3779B1 mod 2^32) >> (32 − LOG)`, sondage linéaire, clés par lots de 16 : les 16 hachages calculés et leurs cases préchargées en écriture (instruction de préchargement de la chaîne), puis les 16 insertions | frontière (Chapel) ; Julia 0,69 |
| K7 | `tuned_oa` (repli) | la même table, sans préchargement, si le K7 optimisé publié du langage en diffère | Chapel, C |
| K8 | `tuned_val` | arène de nœuds (valeur `i64`, enfants `i32`) réutilisée ; construction récursive en ordre préfixe où l'état (prochain indice libre ; valeur du nœud = numéro de requête + son indice préfixe) passe par valeur, en arguments et en retour, sans pointeur vers un état ; somme récursive par les liens | frontière (Ada) ; C 0,57 et 0,45, OCaml 0,77 |
| K8 | `tuned_it` | la même arène, construction et somme itératives avec une pile explicite (tableau) de nœuds en attente | C 0,40, C# 0,51, Go 0,62, Java 0,64, JavaScript 0,73 |
| K9 | `tuned_v` | grilles plates alignées sur 64 octets ; par ligne, vecteurs explicites de 8 `f64` : haut, bas, gauche et droite chargés en vecteurs (désalignés pour gauche et droite), même ordre des additions, résultat écrit en vecteur, reste scalaire | frontière (Swift) ; Go 0,78 |
| K9 | `tuned_a` (repli ; retiré, 4.1) | grilles plates alignées sur 64 octets, boucle vectorisée par le compilateur | C (0,91) |

Le diagnostic de la section 4 peut ajouter des formes à ce tableau, par un écart daté, avant le portage.

### 3.4 C4 : portage

* Chaque langage écrit chaque forme du catalogue qu'il peut exprimer, sauf une forme de repli quand il écrit la forme
  principale de la même cellule. Pour K6 et K9 à quatre fils, il écrit `mt_pool` et la variante `mt_pool_*` de chaque
  forme à un fil nouvelle qu'il a écrite.
* Une forme est **présente** si une variante existante du langage répond déjà à sa définition (lecture du source,
  notée) ; elle n'est pas réécrite. Exemples attendus : `mt_pool` pour Chapel (`coforall`, `forall`), Fortran (équipe
  OpenMP), Julia (`Threads.@spawn`), Go (goroutines) ; `tuned_pf` pour Chapel ; `tuned_val` pour Ada.
* Une forme est **non écrivible** si la capacité qu'elle demande manque au langage, preuve à l'appui : case de la
  grille et sa sonde (`results/probes`) pour le SIMD explicite (C1, C2), les fils (D1), le préchargement (E4) ; ou
  tentative échouée (refus du compilateur, résultat faux). La raison est notée.
* Chaque forme est écrite dans l'idiome du langage, avec le même soin que ses variantes publiées : la définition fixe
  l'algorithme, la disposition et le parallélisme, pas la syntaxe.
* Le relevé, langage par langage et forme par forme (présente, écrite sous tel nom, non écrivible et pourquoi), est
  publié dans `results/converge/inventory.md` et lu par l'analyse (`results/converge/forms.json`).

### 3.5 C5 : formes propres à un runtime

Une forme trouvée par une remarque dont le gain tient à un coût propre au runtime de son langage (représentation des
tables de Lua, champs de deux mots d'OCaml, conversion des tableaux typés de JavaScript, unité de compilation du JIT de
Java, vérification de débordement de Nim, spécialisation de Julia) entre dans le plafond de son langage (C1), sans
être portée ailleurs. Elle est recopiée de la copie de la remarque (`bench/<langage>_exp`, `_k8`, `_q1`…) dans la
copie du point 4, sous un nom en `rq_`, et mesurée dans la même campagne. La liste, avec la raison de chaque
classement, est dans le relevé (3.4).

### 3.6 C6 : composition des formes à quatre fils

La variante `mt` publiée (fils créés à chaque appel, forme publiée) reste mesurée. Les variantes à réserve de fils
reprennent chacune une forme à un fil (3.3). Le croisement « fils créés à chaque appel, forme nouvelle » n'est pas
écrit : à cette taille, créer quatre fils coûte de 0,1 à 0,5 ms par appel, ce qu'une réserve ne paie pas (Java :
réserve × 1,07 sur K6, dans le bruit, × 0,81 sur K9 ; C# : × 0,71 sur Q6, × 0,63 sur K9).

## 4. Diagnostic des écarts sans explication (avant le portage)

Pour les trois écarts de la section 2 (K9 à un fil, K9 à quatre fils, Q6 de Chapel), une expérience en C sur la
machine du point 4, à machine au repos, mesure séparément : alignement des grilles (64 octets contre 16), distance
entre les deux grilles modulo 4 Kio, largeur des vecteurs (boucle vectorisée en 256 bits, en 512 bits explicites),
pages géantes (`madvise`), et, pour Chapel, le nombre de fils de son runtime (`CHPL_RT_NUM_THREADS_PER_LOCALE`), avec,
si l'hôte les expose, les compteurs matériels de `perf_event_open` (`docs/INSTRUMENTS_V3.md`). Les mesures sont publiées
(`results/converge/diag/`). Un mécanisme établi qui s'exprime dans le source (alignement, décalage des tampons,
largeur) devient une forme du catalogue par un écart daté, avant le portage ; un mécanisme qui tient à la
configuration d'un runtime est décrit et n'entre pas au catalogue (règle 3.2, 4).

### 4.1 Résultats du diagnostic et écarts au plan (21 novembre, avant le portage)

* **Hôte.** Le conteneur a redémarré vers 15 h 55 sur un Xeon du même modèle (6/207/2) : machine 33, caractérisée à
  machine au repos (`results/hw/machine33`). Latences, bande passante d'un fil (28 Go/s) et pic de calcul sont ceux de
  la machine 32 ; à quatre fils, la bande passante varie beaucoup d'une mesure à l'autre (STREAM triad de 47 à 148 Go/s
  en quatre mesures ; sur la machine 32, de 43 à 176 Go/s selon le noyau de STREAM).
* **K9 : ni l'alignement ni la largeur.** Sur la boucle de K9 du C (`tools/converge/k9_diag.c`,
  `tools/converge/diag.sh`, `results/converge/diag/k9.txt`), le décalage des grilles dans leur page (0 à 64 octets),
  leur distance modulo 4 Kio, les pages géantes et la forme (boucle du C, vecteurs explicites de 256 ou 512 bits)
  restent dans la variation d'une exécution à l'autre : 11,5 à 16,0 ms à un fil (boucle non vectorisée : 13,4 à
  20,4), 3,7 à 6,5 ms à quatre.
* **K9 : le harnais.** Les écarts de la section 2 viennent du harnais : les sources publiées de 18 implémentations
  réallouent encore les grilles à chaque répétition, alors que le classement publié a mesuré K9 au harnais commun
  (`docs/K9.md`). Sur la machine 33, le K9 de Rust passe de 20,3 à 12,7 ms à un fil et de 11,3 à 5,1 ms à quatre fils
  avec sa copie au harnais commun (médianes de sept répétitions ; défauts de page par processus : 139 600 contre
  24 800 ; `results/converge/diag/harnais.txt`).
* **Q6 de Chapel.** Avec un seul fil de runtime, son Q6 à un fil ne change pas (14,1 ms, comme avec quatre) : les fils
  inoccupés n'y sont pour rien. À quatre fils, 1,7 ms (médiane) : plus de quatre fois plus vite qu'à un fil, sur la
  machine 33 comme sur la machine 32 ; non expliqué, et sans forme à porter (`results/converge/diag/chapel_q6.txt`).
* **Erratum des points 2 et 3.** Plus largement, les sources publiées de 20 langages n'ont ni les corrections que le
  classement publié applique (copies `_fix`, `bqn_rq`), ni le harnais commun de K9 (copies `_k9h`), alors que les
  campagnes des points 2 et 3 les ont mesurées comme « le source publié » (`docs/V4_SIZES.md`, 10.7 ;
  `docs/V4_EQUAL.md`, 11.9). Les écarts de la section 2 sont mesurés sur ces sources.
* **Écarts au plan qui en découlent :**
  1. **Base corrigée.** Avant le portage, chaque source publiée `bench/<langage>` reçoit les corrections que le
     classement publié lui applique (différence entre la copie corrigée et sa copie de référence de la remarque,
     reportée sur la source actuelle, qui garde les tailles du point 2 et les modes du point 3) et le harnais commun
     de K9, sans autre changement ; chaque source corrigée est validée (sommes de contrôle) et le relevé des
     corrections reportées est publié (`results/converge/corrections.md`). La base du point 4 et les copies `_cv`
     partent de ces sources (au lieu de `bench/<langage>_eq`), avec les variantes du point 3 recopiées (K4 `tuned`,
     sauf celui de FreePascal ; K9 `natural_flat`, au harnais commun).
  2. **Contrôle de l'erratum.** La campagne mesure aussi chaque cellule que la correction change sur la source non
     corrigée (le code des points 2 et 3) ; ces paires, au même hôte, donnent l'effet de l'erratum.
  3. **Catalogue.** `tuned_a` (K9) est retiré : l'alignement ne change rien de mesurable. Les autres formes restent ;
     les écarts de la section 2 seront remesurés sur la base corrigée.

## 5. Code

* **Copies** `bench/<langage>_cv`, faites depuis `bench/<langage>_eq` (source publié, K4 `tuned` de R3, K9 naturel
  contigu), avec les formes nouvelles déclarées dans `cv_variants`. Les binaires publiés et les copies du point 3 ne
  changent pas.
* **Ordre** : les langages dans l'ordre du classement publié, le premier étage d'abord ; chaque langage est poussé dès
  que ses formes sont écrites et validées.
* **FreePascal** reçoit un K4 `tuned` sans assembleur (erratum du point 3), à côté de `swar`.
* **Validation** : chaque nouvelle cellule, exécutée une fois à la taille publiée, doit rendre la somme de contrôle de
  la taille publiée (`tools/driver.py`) ; les preuves d'exactitude (3.2, 2) sont relues.
* Pilote et analyse : nouveaux outils (`tools/converge/`, `analysis/converge_v4.py`), poussés avant la campagne.

## 6. Hôte

Comme au point 3 (`docs/V4_EQUAL.md`, 5) : la campagne mesure aussi la base (binaires publiés, cellules du score à la
taille publiée) sur le même hôte ; le modèle de processeur est vérifié à chaque passe ; si l'hôte a changé depuis le
point 3, il est caractérisé avant les mesures (`tools/sizes/hwchar.sh`) ; b3 (`tools/equal/k3_ref.sh`) est mesuré au
début et à la fin, pour le calcul 6 (section 8).

## 7. Campagne

Le pilote du point 3, adapté : constructions `pub` et `cv`, groupes par noyau, ordre aléatoire des groupes puis des
blocs à graine fixe différente à chaque passe, trois passes, répétitions fixées par la première passe (environ 3 s
par processus, au moins trois), échauffement des JIT, vol de temps au-delà de 5 % refait une fois, sentinelle de
mémoire, écritures dans `results/converge/work`, recopiées et poussées à chaque fin de groupe. Aucune autre mesure ne
tourne pendant la campagne.

## 8. Analyse, fixée avant les mesures

La méthode v3 du point 3 (même graine, 20 000 variantes, mêmes poids, grille v2 corrigée par le point 1), sur les
seules données de la campagne du point 4, avec les bornes physiques de son hôte. Chaque nouvelle cellule s'ajoute à
l'ensemble « meilleur de » de sa cellule du plafond ; ses tirages suivent ceux des autres cellules du même noyau
(mêmes réservoirs de résidus), par un générateur à part, pour que les autres tirages ne changent pas (comme la cellule
K4 `tuned` de R3). Calculs :

1. **Hôte** : la base.
2. **Convergent** : toutes les formes admises (C1).
3. **Par noyau** (information) : « Convergent » sur K4, K5, K6, K7, K8 ou K9 seul, pour attribuer les déplacements.
4. **Remarques** (information) : la base et les seules formes que les remarques avaient trouvées pour leur propre
   langage, pour comparer l'effort d'une relecture à la convergence.
5. **Convergent, sélection indépendante** (sensibilité) : la meilleure forme de chaque langage et de chaque cellule est
   choisie sur la passe 0 seule, et sa cellule estimée sur les passes 1 et 2 seules, pour mesurer ce que le choix du
   minimum parmi plus de formes ajoute par hasard.
6. **Convergent, avec R4** (information, vers la campagne finale ; R3 est déjà dans C1) : K3 rapporté à b3 de cette
   campagne.

Pour chaque calcul : scores, rangs espérés, rang plausible (90 %), étages indicatifs (règle v3 sans sa condition de
réplication), langages dont le rang change de plus de deux places par rapport à « Hôte » ; en descriptif, pour chaque
cellule et chaque langage, la forme retenue et son rapport à la meilleure forme publiée. Sorties :
`results/converge/analysis.json`, `results/report_converge.md`.

## 9. Publication

Le classement de tête du README ne change pas au point 4 : C1 à C6 entreront dans la campagne finale, qui réunira les
points 2 à 4, quel que soit l'effet mesuré ici. Il est publié à côté du classement (README, ce document), noyau par
noyau.

## 10. Ordre de travail

1. Ce plan, poussé.
2. Diagnostic (section 4) ; écarts datés s'il ajoute des formes.
3. Copies et formes, langage par langage, poussées au fur et à mesure ; relevé (3.4).
4. Validation, pilote et analyse, poussés avant la campagne.
5. Campagne.
6. Analyse, documents, journal.
