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

### 4.2 Écarts datés pendant le portage (21 novembre)

* **K9 à voisins glissants** (Lua 0,87, JavaScript 0,88 : section 2) : la forme manque au tableau du catalogue (3.3).
  Elle est classée propre au runtime (3.5) : son gain tient au coût de chaque lecture d'élément dans ces runtimes
  (vérifications de bornes et de type de V8, accès aux tables de Lua) ; un langage compilé garde lui-même les voisins
  dans ses registres, ou vectorise la boucle, ce que cette forme empêcherait. Elle est recopiée de la copie de la
  remarque sous le nom `rq_slide`, avec sa version à quatre fils `rq_slide_mt` (les fils de la variante `mt` du
  langage, chaque quart : `rq_slide`), plafond K9 et K9 à quatre fils.
* **Q6 en colonnes de Python** (remarque sur Python, `docs/PYTHON.md` : × 0,35, et × 0,29 à quatre fils), absente de
  la section 2 : classée propre au runtime (3.5). Son gain tient au coût de l'interpréteur par ligne, que la forme
  remplace par des boucles en C de la bibliothèque standard (`bytes.translate`, entiers longs, `bytes.find`) ; un
  langage compilé n'a pas ce coût. Recopiée sous les noms `rq_cols` et `rq_cols_mt` (la réserve de fils de Python,
  chaque quart : `rq_cols`).
* **K5 sur données f64 de JavaScript** (`rq_f64`) : la copie de la remarque convertissait les données hors chrono ; la
  conversion est faite dans le chrono, une fois par répétition (3.2, 1 : le calcul sur les données telles qu'elles
  sont stockées), pour un coût négligeable (2048 éléments, contre 65 536 produits scalaires par répétition).
* **Analyse** (`analysis/converge_v4.py`, poussée avant la campagne) : les calculs 1 à 6 de la section 8, et en
  information le calcul « Hôte, source non corrigée » (contrôle de l'erratum, 4.1, 2 : les cellules que la correction
  de la base change, mesurées sur la source du commit `ea2da12`, à la place de celles de la base). Les cellules des
  formes viennent du relevé (`results/converge/forms.json`) ; chaque nouvelle cellule est tirée par son propre
  générateur (graine fixée par la cellule et le langage), pour être tirée de la même façon dans tous les calculs.

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

## 11. Résultats (22 novembre, après la campagne)

*Tableaux complets (places, rangs espérés, scores au centre, rangs plausibles, étages, forme retenue par cellule,
rapports de l'erratum) : `results/report_converge.md` ; toutes les sorties : `results/converge/analysis.json`
(`analysis/converge_v4.py`, inchangé depuis sa publication avant la campagne). Les calculs sont ceux de la section 8 et
de 4.2, sur les seules données de la campagne du point 4 (machine 33). Les temps cités sont des estimations ponctuelles
(moyenne géométrique des médianes des trois processus d'une cellule).*

### 11.1 Le portage (21 novembre)

* **Relevé** (`results/converge/inventory.md`, `results/converge/forms.json`, écrit par `tools/converge/inventory.py`) :
  25 langages × 20 formes du catalogue = 500 entrées : 230 formes écrites, 87 présentes (une variante publiée répond
  déjà à la définition), 61 non écrivibles (preuve : case de la grille et sa sonde, ou essai), 122 sans objet (forme
  de repli quand la forme principale est présente ou écrite ; réserve de fils sans forme à un fil nouvelle) ; et 17
  formes propres à un runtime (`rq_`). Les copies `bench/<langage>_cv` en tirent 247 cellules nouvelles, K4 `tuned`
  de R3 compris. Validation : chaque cellule des copies (915 en tout, publiées comprises) rend la somme de contrôle de
  la taille publiée (`results/converge/validation_cv.txt`).
* **Ce que le portage a établi en chemin** (essais du 21 novembre, notes du relevé ; rapports mesurés dans la
  campagne) :
  * FreePascal : K4 `tuned` sans assembleur (erratum du point 3, `docs/V4_EQUAL.md`, 11.8) prend la forme par
    pointeur de sa remarque ; `-Sv` refuse les tableaux d'entiers (« Operator is not overloaded ») : Q6 et Q1
    `tuned_v` ne s'écrivent pas.
  * Haskell : GHC 9.14.1 n'a, sur les vecteurs d'entiers, ni comparaison, ni masque, ni sélection : Q6 et Q1
    `tuned_v` ne s'écrivent pas (`:browse GHC.Exts`).
  * PHP : le JIT tracing de PHP 8.5.12 refuse la boucle de Q1 `tuned_s` sur les données du banc (« JIT compilation
    error », quelle que soit l'écriture essayée ; il la compile sur des données synthétiques) : elle s'exécute dans
    l'interpréteur.
  * BQN : sans fils, sans types vectoriels, sans préchargement (grille C1, C2, D1, E4 = 0) et sans entier de 64 bits,
    il n'écrit que quatre formes : Q6 `tuned_s` en primitives (2,5 fois le temps de sa variante publiée) et trois en
    boucles interprétées, Q1 `tuned_s` et K8 `tuned_val` et `tuned_it`, 35 à 107 fois plus lentes que ses variantes
    publiées en primitives.
  * Q1 `tuned_s` (30 accumulateurs locaux, une passe) est plus lente que la meilleure forme publiée dans neuf des dix
    langages qui l'ont écrite (× 1,5 en JavaScript à × 35 en BQN ; Julia × 0,42, où `tuned_v` fait mieux ; le
    mécanisme n'est pas examiné). Le plafond garde la meilleure forme : une forme lente ne pénalise pas.
  * Réserves de fils : Java (exécuteur de trois fils, le fil principal traite le quart 0 : la forme de sa remarque,
    ramenée à la définition), Python (fils liés aux sous-interpréteurs, `threading.Barrier`), OCaml (domaines,
    barrière par Mutex et Condition), FreePascal (événements de la RTL) ; présentes, celles du runtime (Chapel,
    Fortran, Julia, Mojo, Go, Haskell) et les processus ou Workers créés avant la mesure (PHP, JavaScript).

### 11.2 Campagne

* Lancée le 21 novembre à 19 h 11, constructions prêtes ; passe 0 jusqu'à 21 h 41 (2 h 29, étalonnage compris),
  passe 1 jusqu'à 23 h 36 (1 h 55), passe 2 jusqu'au 22 novembre à 1 h 29 (1 h 53), sans redémarrage.
* 3 096 processus : trois passes de 1 032, qui couvrent les mêmes cellules : 655 de la base (construction `pub`), 247
  des formes écrites (`cv`) et 129 de la source non corrigée (`old`), dont une deux fois par passe (K9 naturel de
  Fortran, que la liste du pilote comptait pour la correction de l'implémentation et pour le harnais ; l'analyse garde
  ses six processus). Tous sur le même modèle de processeur (6/207/2). Aucun échec : sommes de contrôle justes, code de
  retour nul, aucun arrêt pour la mémoire ou la durée. Aucun processus au-delà de 5 % de vol de temps (2,3 % au plus),
  donc aucun refait.
* b3, machine au repos (médianes des 16 décalages) : 84,90 et 85,40 ms au début (`results/converge/k3_ref_start.txt`),
  85,65 et 84,55 à la fin (`results/converge/k3_ref_end.txt`) ; b3 = 85,12 ms. Les décalages rapides sont ceux de la
  machine 32 (8, puis 36 à 48 ; 12 entre les deux).
* Stabilité : l'écart entre la passe la plus lente et la plus rapide d'une cellule vaut 6 % en médiane ; 170 cellules
  sur 1 031 s'écartent de plus de 20 %, dont 85 à quatre fils (K6 : 79 cellules, K9 : 38) : à quatre fils, la bande
  passante de cet hôte varie d'une mesure à l'autre (4.1). En K5, huit processus de la passe 0 (`tuned` de Julia,
  Rust, Swift, C#, Fortran et OCaml, `tuned_v` de Julia, naturel d'OCaml) ont une médiane de 1,26 à 1,59 fois celle des
  deux autres passes, avec le même minimum : une partie de leurs répétitions est lente. Les processus des autres
  langages, mesurés entre eux dans les mêmes minutes, ne le sont pas ; le mécanisme n'est pas établi. L'analyse prend
  un processus par cellule à chaque passe et tient compte de cette variation par rééchantillonnage (section 8).

### 11.3 Classements

Places ; lignes dans l'ordre de « Convergent » (rang espéré entre parenthèses). « Publié » : le classement de tête du
README ; « Sélection » : « Convergent, sélection indépendante » (calcul 5) ; « R4 » : « Convergent, avec R4 »
(calcul 6) ; « Non corrigée » : « Hôte, source non corrigée » (contrôle de l'erratum, 4.2).

| Langage | Publié | Hôte | Convergent | Remarques | Sélection | R4 | Non corrigée |
|---|---|---|---|---|---|---|---|
| C++ | 3 | 2 | 1 (1,87) | 2 | 1 | 1 | 3 |
| C | 1 | 1 | 2 (3,82) | 1 | 4 | 3 | 1 |
| C3 | 4 | 3 | 3 (3,82) | 3 | 2 | 4 | 2 |
| Zig | 5 | 6 | 4 (3,87) | 8 | 3 | 2 | 6 |
| D | 8 | 4 | 5 (5,49) | 4 | 5 | 8 | 4 |
| Odin | 2 | 5 | 6 (6,34) | 5 | 6 | 5 | 5 |
| Nim | 7 | 8 | 7 (6,42) | 7 | 7 | 6 | 7 |
| Rust | 6 | 7 | 8 (7,41) | 6 | 8 | 7 | 8 |
| Ada | 9 | 9 | 9 (9,60) | 9 | 9 | 10 | 10 |
| Mojo | 14 | 11 | 10 (10,38) | 12 | 10 | 13 | 12 |
| Chapel | 10 | 10 | 11 (10,40) | 10 | 11 | 9 | 9 |
| Fortran | 11 | 13 | 12 (11,60) | 11 | 13 | 11 | 14 |
| Julia | 13 | 14 | 13 (11,64) | 14 | 12 | 12 | 13 |
| Swift | 12 | 12 | 14 (12,77) | 13 | 14 | 14 | 11 |
| C# | 15 | 15 | 15 (14,95) | 15 | 15 | 15 | 15 |
| Java | 17 | 16 | 16 (16,46) | 16 | 16 | 16 | 17 |
| FreePascal | 16 | 17 | 17 (16,97) | 17 | 17 | 18 | 16 |
| Go | 18 | 18 | 18 (17,44) | 18 | 18 | 17 | 18 |
| Haskell | 19 | 19 | 19 (18,81) | 19 | 19 | 19 | 19 |
| OCaml | 20 | 20 | 20 (20,26) | 20 | 20 | 20 | 20 |
| BQN | 21 | 21 | 21 (21,44) | 21 | 21 | 21 | 21 |
| JavaScript | 23 | 22 | 22 (22,16) | 22 | 22 | 22 | 23 |
| PHP | 22 | 23 | 23 (22,30) | 23 | 23 | 23 | 22 |
| Python | 24 | 24 | 24 (24,08) | 24 | 24 | 24 | 24 |
| Lua | 25 | 25 | 25 (24,73) | 25 | 25 | 25 | 25 |

Étages (paires ordonnées dans au moins 95 % des variantes) : les 19 premiers | OCaml, BQN, JavaScript, PHP, Python,
Lua, dans tous les calculs sauf « Remarques », où Haskell fait un étage à lui seul entre les deux (comme dans les huit
calculs du point 3, sur la machine 32).

### 11.4 Ce que la convergence déplace

* **« Convergent » (C1) : aucun langage ne bouge de plus de deux places par rapport à « Hôte ».** C++ passe 1er (rang
  espéré 3,04 → 1,87 ; rang plausible 1 à 5, contre 1 à 8) ; Zig gagne deux places (6e → 4e ; rang plausible 1 à 7,
  contre 1 à 12) ; Mojo, Nim, Fortran et Julia en gagnent une ; Swift en perd deux (12e → 14e), C, D, Odin, Rust et
  Chapel une. Derrière C++, C, C3 et Zig sont à égalité (rangs espérés 3,82 à 3,87).
* **Les scores montent, ceux des compilés surtout** : au centre, + 5,0 points en médiane pour les 19 premiers (de
  + 2,5, Swift, à + 8,8, C++), + 0,2 pour les six derniers. Le plafond porte le gain (C++ : 70,0 → 92,7 ; Zig :
  48,9 → 69,4) ; le code par défaut perd 1,3 point au plus (C), parce que la frontière, qui sert de référence au
  code naturel (D1), avance. L'écart entre le 1er et le 14e passe de 15,4 à 21,6 points.
* **Par noyau (calcul 3) : K4 et K8 font l'essentiel.** Avec K4 seul, C++ passe 1er, Zig 4e, Mojo 9e (+ 5,8 points)
  et Fortran 11e ; Chapel recule à la 12e place. Avec K8 seul, C++ passe 1er et C3 2e, C recule à la 3e place, Swift
  monte à la 10e, Chapel à la 9e ; Ada (9e → 11e) et Mojo (11e → 13e) reculent, parce que la frontière de K8 passe
  d'Ada (73,2 ms, sa forme publiée, déjà « par valeur ») à C++ (62,5 ms, `tuned_val`). Avec K6 seul, Nim passe de la
  8e à la 6e place. Avec K5, K7 ou K9 seul, aucune place ne change. Gain médian au centre, 19 premiers : K8 2,5
  points, K4 1,6, K6 0,3, K9 0,2, K5 et K7 0.
* **Écarts au plafond** (quatorze premiers du classement publié ; frontière : le plus rapide des 25 langages ;
  « publiées → toutes » : les formes publiées seules, puis toutes les formes admises ; à comparer avec la section 2,
  mesurée sur la machine 32 et la source non corrigée) :

  | Cellule | Frontière, formes publiées | Frontière, toutes les formes | Langages ≥ 0,9 (sur 14) | Médiane | Le plus bas |
  |---|---|---|---|---|---|
  | K4 | Chapel, 1,22 ms | Zig, 0,58 ms (`tuned`) | 1 → 8 | 0,79 → 0,90 | 0,14 (Mojo) → 0,67 (Swift) |
  | K5 | C++, 3,36 ms | la même | 5 → 5 | 0,79 → 0,81 | 0,49 (Julia) → 0,61 (Fortran) |
  | K6 Q6 un fil | Zig, 12,71 ms | Rust, 12,22 ms (`tuned_v`) | 7 → 11 | 0,90 → 0,92 | 0,75 (D) → 0,87 (Fortran) |
  | K6 Q1 un fil | Zig, 21,21 ms | C3, 21,11 ms (`tuned_v`) | 3 → 8 | 0,73 → 0,92 | 0,28 (Julia) → 0,66 (Fortran) |
  | K6 Q6 quatre fils | Chapel, 1,94 ms | Chapel, 1,89 ms (`mt_pool_v`) | 3 → 9 | 0,69 → 0,91 | 0,42 (Ada) → 0,49 (Julia) |
  | K6 Q1 quatre fils | C3, 6,17 ms | Odin, 5,73 ms (`mt_pool_v`) | 3 → 7 | 0,72 → 0,91 | 0,24 (Nim) → 0,61 (Nim) |
  | K7 | C3, 142,52 ms | la même | 9 → 9 | 0,93 → 0,93 | 0,79 (Julia) → 0,84 (Julia) |
  | K8 | Ada, 73,16 ms | C++, 62,53 ms (`tuned_val`) | 1 → 1 | 0,26 → 0,69 | 0,18 (Julia) → 0,43 (Mojo) |
  | K9 un fil | D, 12,21 ms | la même | 4 → 8 | 0,86 → 0,92 | 0,52 (Julia) → 0,56 (Julia) |
  | K9 quatre fils | Chapel, 3,40 ms | Chapel, 3,27 ms (`mt_pool_v`) | 1 → 1 | 0,68 → 0,76 | 0,31 (Julia) → 0,30 (Julia) |

  Sur la base corrigée, avant toute forme nouvelle, l'écart de K9 de la section 2 se réduit (médiane 0,86 à un fil,
  contre 0,65 sur la machine 32 ; 0,68 à quatre fils, contre 0,33) : il venait surtout du harnais (4.1). Les formes
  nouvelles referment surtout K4, Q1, les cellules à quatre fils de K6 et K8. K5 et K7 bougent peu : la forme du
  catalogue y était déjà présente dans 14 langages (K5 `tuned_v`) et 18 (K7 `tuned_pf` ou `tuned_oa`).

### 11.5 Formes retenues

Forme retenue par « Convergent », cellule par cellule, et son rapport à la meilleure forme publiée :
`results/report_converge.md`. Une forme nouvelle est la plus rapide pour :

* **K4** (24 langages, BQN excepté) : `tuned` (R3) dans 20, `swar` dans 4 (Fortran, FreePascal, JavaScript, Lua).
  Seize langages font K4 en 0,58 à 0,77 ms, à la bande passante d'un cœur (borne de l'hôte : 0,60 ms) ; Swift et
  Haskell en 0,87 et 1,22 ms, FreePascal en 3,0 (`swar`), OCaml, JavaScript et PHP en 5,5 à 7,0, Python en 65, Lua en
  197 ; BQN garde 4,1 ms. `swar` bat la meilleure forme publiée dans 16 des 23 langages qui l'ont écrite (× 0,16 à
  0,83) ; `tuned` bat `swar` dans tous les langages qui ont les deux, sauf les quatre qui retiennent `swar` (Fortran :
  0,75 ms, contre 1,31 pour son `tuned`).
* **K8** (22 langages) : `tuned_it` (pile explicite) dans 17, `tuned_val` (état par valeur) dans 5 (C++, Fortran,
  Mojo, Python, Lua) ; × 0,22 (Chapel) à × 0,91 (Lua) de la meilleure forme publiée. Seize langages font K8 en 63 à
  123 ms ; avec les formes publiées, Ada seul était sous 180 ms (73 ms ; les quinze autres : 182 à 398 ms). Ada
  garde sa forme publiée (`tuned_it` y est 1,29 fois plus lent), PHP et BQN aussi.
* **Q6 et Q1 à un fil** : Q6 `tuned_v` dans 7 langages (× 0,75 à 0,93), `tuned_s` dans 3 (OCaml, JavaScript, PHP :
  × 0,64 à 0,81) ; formes propres au runtime de Python (`rq_cols`, × 0,43) et de Lua (`rq_nest`, × 0,89). Q1 `tuned_v`
  dans 8 (Julia × 0,28, Nim × 0,36, Java × 0,41, Ada × 0,50, Odin × 0,56, Mojo × 0,73, Chapel × 0,77, C3 × 0,96) :
  huit langages font Q1 en 21,1 à 23,0 ms. En Go, `tuned_v` est plus lente (× 1,52), comme la forme en une passe de sa
  remarque (section 2 : × 1,36).
* **Quatre fils** : une réserve de fils est retenue dans 18 langages pour Q6 et pour K9, dans 15 pour Q1 (× 0,26 à
  0,99) ; Lua, sans fils, y retient ses formes propres au runtime (`rq_nest_mt`, `rq_slide_mt` : quatre morceaux en
  séquence). Avec une réserve, écrite ou présente, quatorze langages compilés font Q6 à quatre fils 5,4 à 7,0 fois
  plus vite qu'à un fil (Odin et Chapel 7,0) : l'accélération au-delà de quatre de Chapel (section 2 et 4.1) ne lui
  est pas propre ; elle reste sans mécanisme établi. À K9, Chapel reste devant (3,27 ms), puis neuf langages de 3,86
  à 4,49 ms.
* **K9 à un fil** : `tuned_v` dans 7 langages (Go × 0,67 à Chapel et Julia × 0,93), plus lente en Ada (× 1,18) et
  en Java (× 1,24) ; `rq_slide` en JavaScript (× 0,86). Seize langages font K9 en 12,2 à 16,4 ms.
* **K5** : `tuned_v` en Julia (× 0,56), FreePascal (× 0,66), Go (× 0,95), Chapel (à égalité) ; formes propres au
  runtime de Fortran (`rq_acc16`, × 0,93) et de JavaScript (`rq_f64`, × 0,95). **K7** : `tuned_pf` en Julia seulement
  (× 0,95 ; Haskell × 1,03, Swift × 1,17), `tuned_oa` en Python, PHP, OCaml et Fortran (× 0,65 à 0,95) ; formes
  propres au runtime de Lua (`rq_pack`, × 0,62) et de Java (`rq_iso`, × 0,75).
* **Formes lentes** : 37 cellules écrites sont plus lentes de plus de 10 % que la meilleure forme publiée de leur
  langage, surtout Q1 `tuned_s` (11.1), `swar` là où `tuned` existe, et les formes de BQN. Le plafond prend la
  meilleure forme : elles ne changent rien.

### 11.6 Remarques et convergence (calcul 4)

« Remarques » (la base et les seules formes que la remarque de chaque langage avait trouvées) ne déplace aucun
langage de plus de deux places par rapport à « Hôte », et ses scores montent de 0,4 point en médiane pour les 19
premiers (au plus 3,4, Java), contre 5,0 pour « Convergent ». Zig, sans forme de sa remarque, y recule de la 6e à la
8e place, Rust et Nim passant devant avec les leurs (arène de K8 écrite comme en C ; Q1 `tuned_v` et arène sans
vérification de débordement). L'essentiel du gain de la convergence vient des formes portées d'un langage à l'autre :
K4 `tuned` (point 3) et `swar` (Swift), K8 `tuned_it` et `tuned_val` (C, Ada), les réserves de fils (Chapel, Java,
C#).

### 11.7 Sélection indépendante (calcul 5)

La forme choisie sur la passe 0 seule diffère de la forme retenue sur les trois passes dans 19 cas sur 250. Estimées
sur les passes 1 et 2, les cellules changent les rangs espérés de 0,41 au plus (Ada) et les scores au centre de 0,7
point au plus ; par rapport à « Convergent », aucun langage ne bouge de plus de deux places. Par rapport à « Hôte »,
la règle de la section 8 relève Zig (6e → 3e) et C (1er → 4e) : C, C3 et Zig y ont des rangs espérés de 3,70 à 3,98,
comme dans « Convergent » (3,82 à 3,87), et leur ordre change d'un calcul à l'autre sans que leur score bouge (C :
73,2 et 72,9). Le choix du minimum parmi plus de formes n'ajoute donc presque rien par hasard ; il ne départage pas
C, C3 et Zig.

### 11.8 Avec R4 (calcul 6)

Avec K3 rapporté à b3 (85,12 ms), Zig (6e → 2e) et D (4e → 8e) bougent de plus de deux places par rapport à « Hôte » :
c'est l'effet de R4 au point 3 (`docs/V4_EQUAL.md`, 11.4 et 11.5), qui se retrouve sur la base corrigée et avec la
convergence. C++ est 1er, C 3e ; les scores montent de 11,4 points en médiane pour les 19 premiers.

### 11.9 Contrôle de l'erratum (4.1, 2)

* **Cellules** (rapport des temps, source non corrigée / source corrigée, même hôte ; tableau complet dans le
  rapport) :
  * harnais commun de K9 : à quatre fils, × 1,9 à 2,7 pour C++, C3, D, Odin, Zig, Rust, Nim et Python, × 1,2 à 1,5
    pour Java, Mojo, Go, C# et OCaml ; à un fil, `tuned` × 1,5 à 1,7 pour C++, C3, D, Odin, Zig, Rust, Nim, Java et
    Go, × 1,3 pour Mojo et C# ; naturel, × 1,3 à 2,0 pour C++, C3, Odin, Zig, Java, D et JavaScript, × 1,17 pour Go
    (Fortran × 1,68 et Haskell × 2,04, avec leurs corrections propres) ; les autres cellules de K9, à 10 % près ;
  * corrections d'implémentation : K4 naturel de Haskell × 10,7, son K8 `tuned` × 3,0 ; K7 naturel de BQN × 7,3 ; K1
    `aos` d'OCaml × 5,5, son Q6 `tuned` × 2,4 et `mt` × 2,1 ; K3 de Python × 4,2, son K6 `mt` × 3,4 à 3,9 ; K4 de
    Fortran × 2,5 et 3,1 ; Q6 `mt` d'Ada × 2,9, son K9 `mt` et `tuned` × 1,24 et 1,18 ; Q1 de D × 2,6 et 2,8 ; K5
    `tuned` de Go × 2,55 et de Java × 1,52 ; K4 de Lua × 2,3 et 2,9, son K3 × 1,4 ; K7 `tuned` de JavaScript × 1,70 ;
    en sens inverse, comme la remarque sur Lua l'avait établi, son K8 naturel × 0,72 (nœuds à champs nommés). Le K2
    à 8 Mio d'Ada (× 0,75) tient à un processus de la source corrigée dans le régime lent de K2 à cette taille
    (360 ms, contre 159 aux deux autres passes ; `docs/V4_EQUAL.md`, 11.1).
* **Classement** : « Hôte, source non corrigée » et « Hôte » ne diffèrent de plus de deux places pour aucun langage
  (quatorze bougent d'une place) ; les corrections font monter les scores au centre de 1,3 point en médiane pour les
  19 premiers (Haskell 3,4). Le sens annoncé (`docs/V4_EQUAL.md`, 11.9) se vérifie pour C (rang espéré 2,16 sur la
  source non corrigée, 2,86 sur la source corrigée), Chapel (9e → 10e) et Swift (11e → 12e), dont le K9 était déjà au
  harnais commun ; Ada, dont les corrections propres pèsent davantage, gagne au contraire une place (10e → 9e).
* **Réplication** : « Hôte, source non corrigée » sur la machine 33 et « Hôte » du point 3 sur la machine 32 (même
  code, même modèle de processeur) ne diffèrent de plus de deux places pour aucun langage (Nim 5e → 7e, D 6e → 4e,
  Zig 8e → 6e).
* **Contre le classement publié** : la source corrigée (« Hôte ») déplace de plus de deux places D (8e → 4e), Odin
  (2e → 5e) et Mojo (14e → 11e) ; la source non corrigée, D, Odin et Fortran (11e → 14e). Le recul de trois places de
  Fortran aux points 2 et 3 tenait aux corrections absentes (K4 : 13e avec la source corrigée) ; celui de Zig
  (5e → 8e sur les machines 31 et 32) ne se retrouve sur la machine 33 avec aucune des deux sources (6e) : il ne
  tenait pas à l'erratum, mais à l'hôte ou au bruit de processus. La montée de D tient à K3 sur cet hôte : avec R4
  (K3 rapporté à b3), il revient à sa place publiée (8e). Odin reste 5e avec R4 : son recul n'est expliqué ni par
  l'erratum ni par K3. L'effet sur les documents des points 2 et 3 est reporté dans leurs errata (`docs/V4_SIZES.md`,
  10.7 ; `docs/V4_EQUAL.md`, 11.9).

### 11.10 Ce que cela change

* Le classement de tête du README ne change pas (section 9). C1 à C6 s'appliqueront dans la campagne finale de la v4,
  qui réunira les points 2 à 4, avec les copies `bench/<langage>_cv` et le relevé de ce point.
* La convergence ne bouleverse pas l'ordre : aucun langage ne bouge de plus de deux places, et les seuls déplacements
  plus grands de ce point viennent de R4 (Zig, D) ou d'une égalité (C, C3, Zig dans la sélection indépendante). Elle
  resserre en revanche le plafond : sur ses dix cellules, les quatorze premiers comptent 67 cases à 0,9 de la
  frontière au moins, contre 37 avec les formes publiées, et la frontière elle-même avance en K4, en K8 et dans les
  cellules à quatre fils.
* Ce qui sépare encore les compilés au plafond : K8 (médiane 0,69 de la frontière ; C++, Ada et Fortran devant), K9
  à quatre fils (Chapel devant les autres de 18 % au moins), et les langages qui ne peuvent écrire une forme (BQN,
  sans fils ni vecteurs ; Haskell, FreePascal sans comparaison vectorielle d'entiers).
* Pour la campagne finale : la règle C1 prend le meilleur de plus de formes, et la sélection indépendante montre que ce
  minimum n'ajoute presque rien par hasard ; elle sera reprise telle quelle. La variation des processus de K5 et des
  cellules à quatre fils de cet hôte (11.2) reste à examiner avant elle.
