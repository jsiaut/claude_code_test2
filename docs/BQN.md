# Ajout de BQN (CBQN) : un 24e langage, mesuré sur la machine 26 et relié aux données publiées par le C

L'auteur de l'étude m'a demandé le 6 novembre d'ajouter BQN au banc, dans son implémentation CBQN. Ce document décrit
la chaîne et les choix d'implémentation, avec les faits relevés en écrivant le code (section 2). Il fixe le plan avant
toute mesure de campagne (section 3), puis donne les résultats (section 4). Comme pour Swift et FreePascal, je n'ai
consulté aucune page web pour les faits. Ils viennent de la chaîne installée et de ses sources (dépôt de CBQN à
l'étiquette v0.12.0 : `README.md`, `docs/`, `src/`), de sondes, du code machine des binaires et d'essais sur la
machine 26. Seuls le dépôt de CBQN (avec ses sous-modules) et la liste de ses versions publiées (les étiquettes du
dépôt) ont été téléchargés.

## 1. La demande

« Ajoute le langage BQN via CBQN au benchmark » : implémenter les dix noyaux de `docs/SPEC.md`, noter la grille de
capacités, mesurer et ranger BQN dans le classement publié avec la même méthode que les 23 autres langages. La
contrainte pratique est celle de FreePascal : les données publiées viennent de plusieurs hôtes (machine 1, Cascade
Lake, pour la plupart des noyaux ; machines 3, 11 et 16, Emerald Rapids, pour K5, les latences de K8 et K9), et seule
la machine 26 (Emerald Rapids, du même modèle que les machines 3, 11, 16, 24 et 25 ; `results/hw/machine26`) est
disponible. Les clés de la machine 1 seront donc reliées d'un modèle à l'autre (3.2).

BQN est le premier langage de tableaux du banc. Deux traits pèsent sur tout le reste : le code s'écrit en primitives
appliquées à des tableaux entiers (une boucle élément par élément y est l'exception), et le langage n'a ni threads ni
coroutines : K3 et les variantes `mt` s'exécutent en séquence, comme en Lua, et il n'y a pas de K10 (hors score).

## 2. Chaîne, implémentation et faits relevés (avant le plan)

### 2.1 Chaîne

* **CBQN 0.12.0**, « A BQN implementation in C » (titre de son README) : étiquette `v0.12.0` du dépôt dzaima/CBQN,
  commit `b4db324a` du 28 juin 2026, la dernière version publiée (les étiquettes du dépôt n'en listent pas de plus
  récente ; je n'utilise pas la branche de développement). Sous-modules : bytecode précompilé du compilateur BQN
  `156b47c`, Singeli `5187ed3` ; replxx (édition de ligne du REPL) n'est pas construit. Les autres chaînes ont été
  fixées le 28 octobre ; BQN, ajouté le 6 novembre, prend la dernière version publiée à cette date, comme Swift et
  FreePascal.
* **Exécution** : le compilateur de CBQN traduit le source en bytecode, qu'exécute une machine virtuelle ; un JIT
  x86-64, actif par défaut, compile une fonction en code machine après deux appels (`src/vm/vm.h` : `JIT_START 2`).
  Les primitives sont écrites en C et, pour les plus chaudes, en Singeli, un langage de génération de code SIMD : un
  programme BQN passe l'essentiel de son temps dans ce code compilé à l'avance. Mémoire : comptage de références et
  ramasse-miettes traçant automatique (`ENABLE_GC 1`) ; seule la commande `)gc disable` du REPL l'arrête
  (`docs/commands.md`). Allocateur par blocs compagnons (`src/core/h.h` : `MM 1` ; `src/opt/mm_buddy.h` :
  `mm_round` arrondit chaque demande à la puissance de deux supérieure).
* **Construction** : le README recommande `make o3n` pour une construction locale sur x86-64 (« TL;DR: use `make
  o3n` for local builds on x86-64 ») : `-O3 -march=native`, et Singeli vise les extensions de l'hôte ; la cible par
  défaut `make o3` ne vise que le jeu d'instructions de base. CBQN choisit son code à la construction, pas à
  l'exécution : la construction native de la machine 26 emploie des extensions qu'un Cascade Lake n'a pas (compression
  `vpcompressb`/`vpcompressw` d'AVX-512 VBMI2 pour le filtre `/`, GFNI pour certains balayages ; 2.4, point 7). Comme
  le C publié et Swift, BQN a donc deux binaires, construits avec clang 23.1.5, sans replxx, `version=0.12.0` :
  * `bench/bqn` (`/opt/cbqn-cl`, SHA-256 `21c51ab6…2453`) : l'équivalent de `make o3n` pour la cible de la machine 1
    (Cascade Lake), pour les clés qui en viennent, K9 et les latences de K8 (témoin `c`, cible Cascade Lake) : `make o3 target_from_cc=1
    f=-march=cascadelake`, où Singeli prend les extensions que le compilateur annonce pour cette cible (AVX2, BMI2,
    AVX-512 F, BW, CD, DQ, VL et VNNI ; `results/bqn_check/singeli_args_cl.txt`), mécanisme documenté par le README
    pour les constructions croisées ;
  * `bench/bqn_er` (`/opt/cbqn`, `9faa903c…f600`) : `make o3n` sur la machine 26, pour K5 et la réplication (témoin
    `c_er`, construction native d'Emerald Rapids).

  La cible par défaut est une copie de sensibilité (`bench/bqn_o3`, `/opt/cbqn-o3`, `c120eb7d…0ac7`, 3.3).
* **Bibliothèque** : les fonctions système de CBQN (`docs/system.md`) : `•file` (dont `MapBytes`), `•bit._cast`,
  `•math.Sum`, `•HashMap`, `•MonoTime`, `•FFI`, `•internal`. Aucune bibliothèque tierce ; le code optimisé n'appelle
  pas de code C par `•FFI` (règle du banc).

### 2.2 Implémentation (`bench/bqn/ms.bqn`)

Un seul programme, lancé par `bench/bqn/run` : les variables du pilote (`MS_DATA`, `WARMUP`) lui passent en
arguments, la bibliothèque système n'ayant pas de lecture de l'environnement. Le code naturel suit la règle de
`docs/NATURAL.md` lue pour un langage de tableaux : les structures et les primitives par défaut, sans recherche de
vitesse ; le code optimisé garde la forme la plus rapide parmi celles que j'ai essayées.

| Noyau | Naturel | Optimisé |
|---|---|---|
| K1 | matrice n×16 de f64, une particule par rangée ; colonnes 3, 4, 5 et 9 extraites (`3‿4‿5‿9⊸⊏˘`, `⍉`, `<˘`), énergie en primitives, somme `+´` | `aos` : même matrice et même extraction, somme `•math.Sum` ; `soa` : 16 listes de f64, `•math.Sum` |
| K2 | — | `⊑⟜a⍟4200000 0` sur une liste d'entiers 32 bits (forme tacite, 2.4 point 3) |
| K3 | — | ni threads ni atomiques : quatre « threads » en séquence sur un cœur, `1⊸+⌾(i⊸⊑)` (mise à jour en place d'un tableau non partagé) ; `padded` : 128 o entre deux compteurs |
| K4 | `+´ (128 ≤ d) / d` (filtre) | `branchless` : `+´ d × 128 ≤ d` |
| K5 | `+´ a × b` (pli ordonné) | `•math.Sum a × b` (somme vectorielle réassociée) |
| K6 | Q6 : masque, filtre `/`, `+´` ; Q1 : filtre, numéro de groupe, regroupement `⊔` et histogramme `/⁼` (l'idiome du GROUP BY) | Q6 : masque, deux filtrages ; Q1 : un masque par groupe et des sommes filtrées ; `mt` : quatre morceaux en séquence |
| K7 | `•HashMap` de la bibliothèque système : `Get` puis `Set` d'un couple ⟨compte, somme⟩ par ligne | clés lues en motifs de 32 bits, classement `⊐` (table de hachage interne de CBQN), histogramme `/⁼`, sommes par tri stable `⍋` et sommes préfixes |
| K8 | listes imbriquées ⟨valeur, gauche, droite⟩ construites par récursion, sommées par récursion | nœuds indexés : trois listes (valeurs, fils gauches, fils droits) construites niveau par niveau en primitives, sommées par un parcours en largeur |
| K9 | matrice 2048×2048 de f64 ; voisins par `»`, `«`, `»˘`, `«˘` ; bord recollé par `∾` et `∾˘` | grille plate ; voisins par tranches décalées (`↓`), sans copie ; bord recopié par `⌾` sur les seuls indices des colonnes de bord ; `mt` : même code, un cœur |
| K10 | absent (ni threads ni coroutines) | absent |

Écarts au harnais commun, tous imposés par le langage : les valeurs de BQN sont immuables, si bien que chaque
itération de K9 produit une nouvelle matrice (comme le K9 naturel de Haskell, la grille initiale est construite une
fois) ; le K8 optimisé alloue ses trois listes à chaque requête, aucune primitive n'écrivant dans un tableau existant
hors des mises à jour en place ; les fichiers f32 sont décodés en f64 hors chrono (2.4, point 1). Harnais :
`•MonoTime` (horloge monotone, en secondes) ; fichiers lus par `•file.Bytes` puis réinterprétés par `•bit._cast` ;
sommes de contrôle flottantes écrites par `•Repr` (17 chiffres significatifs). K3, K6 `mt` et K9 `mt` émettent
`META;k3_mechanism`, `META;k6_mt`, `META;k9_mt`.

Variantes de sensibilité (dans le même programme, `bench/bqn/extra_variants`) : K1 `natural_ns` et
`natural_ns_shuffled` (un espace de noms à 16 champs nommés par particule, dans une liste, mélangée ou non : la lecture
littérale de « type enregistrement par défaut ») ; K7 `natural_arr` (l'idiome tableau : `⊐`, `/⁼`, `⊔`) ; K8
`natural_ns` (nœuds en espaces de noms à champs `v`, `l`, `r`).

Validation par le pilote (`tools/driver.py --quick`) : les 43 cellules de chacun des deux binaires `bqn` et
`bqn_er` (les neuf noyaux, toutes les tailles de K2, les variantes de sensibilité et l'empreinte) et les 36 cellules
de la copie `bqn_o3`, sommes de contrôle toutes justes.

### 2.3 La grille (sonde `probes/bqn`, 33 cases notées, `results/probes/bqn.txt`)

| Cat. | Cases |
|---|---|
| A | A1 = ½ (matrice de f64 d'un seul tenant : rangées homogènes en ligne ; ni enregistrement hétérogène ni champs nommés en ligne) ; A2 = 0 ; A3 = ½ (booléens rangés à 1 bit, `•bit._cast` en u1 ; pas de champs de bits) ; A4 = 0 ; A5 = ½ (`•bit._cast` entre i8, i16, i32, f64 et caractères, sur des tableaux seulement ; ni union ni f32) ; A6 = ½ (`⍉` fait passer la même matrice d'une particule par rangée à un champ par rangée, sans champs nommés) ; A7 = ½ (tableaux de rang 3 et plus, homogènes) ; A8 = ½ (stockage étroit i8/i16/i32/bits choisi par l'implémentation, forçable par `•bit._cast` ; flottants f64 seulement) |
| B | B1 = ½ (comptage de références et ramasse-miettes traçant automatique, que seul le REPL arrête) ; B2 = 0 ; B3 = 0 (nombres jamais boxés, mais tout tableau sur le tas, comme JavaScript) ; B4 = 0 (chaque primitive alloue son résultat) ; B5 = ½ (objets pointeurs de `•FFI`) |
| C | C1 = 0 ; C2 = 0 ; C3 mesurée ; C4 = ½ (`+´` ordonnée ou `•math.Sum` réassociée, pour la somme seulement) ; C5 = 0 |
| D | D1 à D5 = 0 (ni threads, ni atomiques, ni aide de ligne de cache ; l'affinité ne passerait que par `•FFI` vers la libc) |
| E | E1 = ½ (bytecode et JIT actif par défaut ; le code machine n'est visible qu'avec une option de construction, `USE_PERF`) ; E2 à E7 = 0 (E6 : les indices sont toujours vérifiés, sans moyen de l'éviter) |
| F | F1 = 1 (tableaux multidimensionnels natifs et contigus) ; F2 = 0 ; F3 = ½ (entiers exacts jusqu'à 2⋆53 en f64, enveloppement par modulo, comme les masques de Python et de JavaScript) ; F4 = 1 (`•file.MapBytes` et `•bit._cast` sans copie : `i32slice` sur le fichier projeté) |

Aucune case ne change en règle v2. Pilier C : 22,3 en règle v1 avec C3 = 0 (26,3 avec C3 = 1 ; C3 est mesurée en
campagne), 22,8 en règle v2 (sans C3), contre 29,7 pour Python, 14,6 pour JavaScript et 6,8 pour Lua.
`analysis/check_probes.py` : aucune divergence entre la sonde et `analysis/capabilities.py`.

### 2.4 Faits relevés en écrivant le code (`tools/bqn_check/facts.sh`, `results/bqn_check/facts.txt`)

Les temps cités ici viennent d'essais de développement sur la machine 26 (quelques exécutions), pas de la campagne ;
ceux du C viennent de la campagne de la remarque sur FreePascal sur la même machine (`results/raw_fpc_rq`).

1. **Pas de f32 ni de u32** : `•bit._cast` refuse la largeur 32 pour les flottants et pour les entiers non signés
   (« Unsupported width 32 », `src/builtins/bit.c`). Les fichiers f32 sont décodés hors chrono par arithmétique exacte
   (signe, exposant, mantisse, dénormaux compris) ; les clés u32 de K7 sont relevées en positif dans le naturel et
   lues en i32 (mêmes égalités, deux fois moins d'octets que des f64) dans le code optimisé. La matrice de K1 occupe
   donc 128 o par particule, le double de l'enregistrement de 64 o des autres langages.
2. **K5** : `+´` est un pli ordonné, sans réassociation ; sa chaîne d'additions coûte 0,62 ns par élément (moins de
   deux cycles à 2,8 GHz : la latence de l'addition flottante), le produit `a × b` est calculé à part, en vecteurs
   (0,029 s pour les 65 536 itérations). K5 naturel : 0,11 s, plus rapide que le C naturel sur la même machine
   (0,186 s : clang contracte la boucle en une chaîne de FMA, de latence 4 cycles). `•math.Sum` (Singeli,
   `si_sum_f64` de `src/builtins/fold.c`) : 0,030 s, 8 fois le C optimisé (3,8 ms, AVX-512).
3. **K2** : la forme tacite `⊑⟜a⍟n` coûte 8 ns par saut à 16 Kio, le bloc `{𝕩⊑a}⍟n` 25 ns ; le banc prend la forme
   tacite. La latence de L1 de la machine 26 est de 1,8 ns (`results/hw/machine26/lat.txt`) : à petite taille, BQN
   mesure le coût d'une primitive interprétée.
4. **K9** : recopier le bord par une mise à jour structurelle du centre (`(Inner s)˙⌾Inner g`) coûte 1,7 à 1,8 s par
   itération selon l'essai, contre 0,024 à 0,026 s pour recoller les rangées (`∾`, `∾˘`), mêmes valeurs : 70 à 80
   fois. Le naturel recolle ; l'optimisé travaille sur la grille plate et ne remplace par `⌾` que les 4094 cases des
   colonnes de bord.
   K9 naturel : 0,23 s, optimisé 0,084 s (C : 13,2 et 13,3 ms).
5. **K1, place en mémoire** : une matrice de 4 194 304 × 16 f64 construite sans intermédiaires fait monter le RSS de
   128,0 o par particule et le tas vivant compté par CBQN de 256,0 o : la demande de 512 Mio plus l'en-tête reçoit un
   bloc de 1 Gio (`mm_round`), dont la moitié n'est jamais touchée. Dans le banc, le décodage des f32 laisse en plus
   ses intermédiaires libérés dans le tas de CBQN, que le RSS compte encore.
6. **K7** : `•HashMap` coûte 300 à 480 ns par ligne selon l'essai (une recherche, une insertion et un couple neuf par
   ligne), contre 60 à 65 ns pour `⊐`, `/⁼` et `⊔`. K7 naturel : 8,2 s ; `natural_arr` : 1,1 s ; optimisé : 0,75 s
   (C : naturel 0,29 s).
7. **Construction** : Singeli a des chemins AVX-512 (`src/singeli/src/avx512.singeli`, `slash.singeli` :
   « AVX-512 compress », `scan.singeli` : GFNI et VPCLMULQDQ), pris quand la cible les a. Le binaire natif de la
   machine 26 contient 91 compressions `vpcompressb` et `vpcompressw` et 14 instructions GFNI ; celui de la cible
   Cascade Lake aucune, mais des opérations AVX-512 masquées ; celui de `make o3` n'emploie que les registres xmm (comptes de
   `objdump` dans `results/bqn_check/facts.txt`). Essais de validation (une répétition) : la construction par défaut
   est jusqu'à 1,7 fois plus lente que la native sur les noyaux de tableaux (K4 naturel 1,7 ; K1 naturel 1,4 ; K5
   optimisé 1,55 ; K6 1,15 à 1,5 ; K9 1,1 à 1,25 ; K1 `soa` inchangé), aussi rapide sur ceux que dominent les appels
   de primitives sur des scalaires (K2, K3, K7 et K8 naturels).
8. **K8** : les listes imbriquées coûtent 6,4 s pour les 16 384 arbres de 2047 nœuds (190 ns par nœud, construction
   et parcours ; C : 0,70 s), les espaces de noms 7,7 s, les nœuds indexés 0,17 s (C : arène, 0,28 s).
9. **Sans threads** : K3 fait ses quatre fois 2^25 mises à jour à la suite, 2,7 s par répétition, sans écart entre les
   dispositions (aucun partage) ; le compteur passe d'un tableau de bits à des entiers de 16 puis de 32 bits à mesure
   qu'il grandit, d'où l'écart de 32 éléments (128 o) de `padded`. K6 `mt` et K9 `mt` ne font que découper le travail :
   Q1 en quatre morceaux prend 0,14 s contre 0,25 s d'un bloc (des intermédiaires quatre fois plus petits).

## 3. Plan (poussé avant les mesures)

### 3.1 Ce qui entre dans le classement publié

* **BQN, 24e langage classé** (`RANKED`, en dernier) : ses temps reliés aux données publiées par le pont du C (3.2),
  sa grille (2.3, `analysis/capabilities.py`), sa vectorisation mesurée (C3, `tools/c3_measure.py bqn`, comme pour les
  autres langages : boucle chaude de K4 et de K9 naturels) et son empreinte (`results/raw_post/bqn.jsonl`, étiquette
  `post_fp2`, puis `analysis/footprint.py`).
* **Empreinte** : la mesure de CBQN compte le tas vivant (`•internal.HeapStats` après `•internal.GC`), donc le bloc
  compagnon de 1 Gio (256 o par particule). Comme pour Nim, dont l'allocateur arrondit aussi la demande à sa classe de
  taille, la valeur retenue est la mémoire physique de la structure : 128 o par particule (16 f64, 2.4 point 5),
  écrite dans `STRUCTURAL` ; la mesure brute reste dans `results/footprint_detail.json`, et B-fp en donne la
  sensibilité (3.5).
* **Les 23 autres langages** : leurs données ne changent pas. Leur score ne bouge que par BQN lui-même : références t*
  s'il est le plus rapide sur une mesure, rangs, étages.
* **Réplication (machine 3)** : BQN y entre par le même pont, avec le C natif d'Emerald Rapids. Ce n'est pas une
  réplication indépendante pour lui ; le rapport le dit.

### 3.2 Le pont par le C

Le pont est celui de Swift et de FreePascal (`docs/SWIFT.md` 5.3, `docs/FPC.md` 3.2). Toutes les clés de BQN sont
mesurées sur la machine 26. Pour chaque clé k du score (mesures de E et de D1, K1 `natural_shuffled`, K2 tuned aux
trois tailles de D4) : chaque processus de BQN est multiplié par f(k) = G(C publié, k) / G(C machine 26, k), où G est
la moyenne géométrique des médianes de processus. Le C mesuré sur la machine 26 est la construction qui a produit les
données publiées de chaque clé, et BQN est pris dans la construction de la même cible :
* `bench/c/ms` (`ff81685a…`, cible Cascade Lake), avec `bench/bqn` (cible Cascade Lake), pour les clés de la machine 1
  (K1 à K4, K6 à K8), pour K9 (machine 16) et pour les latences de K8 naturel (D3, machine 11 : chaque colonne [p50,
  p90, p99, p99,9, max] multipliée par le rapport des médianes du C, colonne par colonne) ;
* `bench/c_er/ms` (`ca4eeb97…`, construction native identique au binaire de la machine 3), avec `bench/bqn_er`
  (construction native de la machine 26), pour K5 (machine 3) et pour la réplication (toutes les clés, machine 3).

Les processus de BQN gardent leur propre dispersion. Le pont est fait dans `analysis/analyze_v2.py` (`ADDED` : `bqn`
dans `results/raw_bqn` ; `ADDED_ER` : `bqn_er` pour K5 et la réplication), après toutes les corrections du jeu publié,
si bien que les sorties publiées, la réplication et les scripts d'état actuel voient BQN de la même façon.

**Le pont entre modèles.** Pour les clés de la machine 1, le facteur traverse les modèles (Emerald Rapids vers
Cascade Lake). Il absorbe ce qui sépare les hôtes tel que le C le voit, pas ce qui toucherait BQN et le C
différemment ; la construction pour la cible Cascade Lake retire la principale différence connue, les extensions
qu'Emerald Rapids a en plus (2.4, point 7). Deux contrôles, fixés ici : B-gcc (second témoin, compilé par un autre
compilateur) et B-hôte (un seul facteur pour toutes ces clés), 3.5 ; B-natif dit ce que vaudraient ces clés avec la
construction native de la machine 26.

**Tirages isolés.** Les tirages du bootstrap et des latences de BQN viennent de leur propre générateur (graine
SEED + 2404 ; Swift garde SEED + 2402 et FreePascal SEED + 2403) : la suite des tirages des deux autres langages
ajoutés ne change pas. Les résidus de BQN n'entrent pas dans les réservoirs des autres ; pour ses propres tirages, il
puise dans le réservoir des langages à JIT (`JIT` de `analysis/analyze_v3.py` : machine virtuelle et JIT actif par
défaut, échauffement de 3 répétitions comme Java, C# et JavaScript). Il est le dernier de `RANKED`, donc ses bruits de
jugement de la grille sont tirés après ceux des autres. Contrôle : le calcul avec BQN retiré doit reproduire à
l'identique le classement d'avant (R-E de `results/fpc_remark.json`).

Groupe de backend (profil « langage et implémentation ») : « JIT ou VM », avec Java, C#, JavaScript et LuaJIT.

### 3.3 Copies

* `bench/bqn` : le banc publié pour les clés de la machine 1, K9 et les latences (cible Cascade Lake), avec les
  variantes de sensibilité de 2.2.
* `bench/bqn_er` : le même source, construction native de la machine 26 (K5, réplication).
* `bench/bqn_o3` : le même source exécuté par la construction par défaut (`make o3`).
* `bench/c_gcc_cl` : le second témoin (le binaire des données publiées de `c_gcc`, `docs/FPC.md` 3.3).

### 3.4 Mesures (`tools/measure_bqn.py`, machine 26)

153 cellules en 7 passes (1071 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard
(graine 20261106 + 2600) :
* `bqn` : les 29 cellules du score (K1 : 4 ; K2 tuned à 16 Kio, 256 Kio et 8 Mio ; K3 : 4 ; K4 : 3 ; K5 : 2 ; K6 :
  6 ; K7 : 2 ; K8 : 2 ; K9 : 3), plus K1 `natural_ns` et `natural_ns_shuffled`, K7 `natural_arr`, K8 `natural_ns` ;
* `bqn_er`, `c` et `c_er` : les 29 cellules du score ;
* `c_gcc_cl` : les 24 cellules des clés de la machine 1 ;
* `bqn_o3` : les 9 cellules naturelles du score (K1 `natural` et `natural_shuffled`, K4, K5, K6 Q6 et Q1, K7, K8,
  K9).

Répétitions : celles de `results/calib.json` pour les trois C. Pour BQN, la règle du pilote (3 s divisées par le temps
d'une répétition, entre 3 et 10 ; 2 au-delà de 5 s), appliquée à une répétition de calibration faite au début (avec
l'échauffement de la campagne) et écrite dans `results/calib.json` ; les variantes de sensibilité ont leur propre
calibration, les cellules de `bqn_er` et de `bqn_o3` prennent les répétitions de la cellule de `bqn`. Échauffement :
3 pour les trois exécutions de BQN (JIT), 1 pour le C ; règle de vol du pilote. Puis l'empreinte (3 processus, `bqn`)
et C3 (`tools/c3_measure.py bqn` : K4 et K9 naturels, deux clés du binaire `bqn`). Rien d'autre ne tourne. Sortie :
`results/raw_bqn/`.

### 3.5 Scénarios (`analysis/bqn_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | le classement publié à 23 langages (R-E de `results/fpc_remark.json`) ; le calcul avec BQN retiré doit le reproduire à l'identique |
| **B-E (publié)** | BQN ajouté : pont par le C (3.2), grille, empreinte de 128 o, C3 mesurée |
| B-direct | information : les temps de la machine 26 sans pont pour les clés de la machine 1 (pont gardé pour K5, K9 et les latences, venus du même modèle) |
| B-hôte | B-E ; clés de la machine 1 multipliées par la médiane, sur ces clés, des facteurs f(k) du C (un facteur d'hôte au lieu d'un par clé) |
| B-gcc | B-E ; clés de la machine 1 reliées par le second témoin : G(`c_gcc` publié, k) / G(`c_gcc_cl` machine 26, k) |
| B-natif | information : clés de la machine 1, K9 et latences prises au binaire natif de la machine 26 (`bqn_er`), même pont |
| B-o3 | B-E ; les 9 cellules naturelles × r(`bqn_o3` / binaire de la clé dans B-E, `bqn` ou `bqn_er`) : la construction par défaut de CBQN |
| B-K1ns | B-E ; K1 `natural` × r(`natural_ns` / `natural`) et `natural_shuffled` × r(`natural_ns_shuffled` / `natural_shuffled`) : espaces de noms à champs nommés |
| B-K7arr | B-E ; K7 naturel × r(`natural_arr` / `natural`) : l'idiome tableau |
| B-K8ns | B-E ; K8 naturel (temps et latences) × r(`natural_ns` / `natural`) : nœuds en espaces de noms |
| B-fp | B-E ; empreinte mesurée par le tas (256 o par particule) |
| B-C3 | B-E ; C3 = 0 si la mesure donne plus : la vectorisation vue dans les boucles chaudes serait celle des primitives écrites en Singeli, pas celle d'un compilateur sur la boucle du programmeur |
| B-cases-bas | B-E ; A1, A6, A7, B1 et E1 = 0 (matrice homogène sans enregistrement ; transposition par copie ; rang 3 homogène ; ramasse-miettes qu'un programme ne peut pas arrêter ; code machine invisible sans reconstruire) |
| B-cases-haut | B-E ; A8, B1, C4 et E1 = 1 (stockage étroit automatique ; libération immédiate par comptage de références ; réassociation demandée par `•math.Sum` ; JIT par défaut) |
| B-tout-bas, B-tout-haut | B-cases-bas avec B-o3, B-K1ns, B-K8ns, B-fp et B-C3 ; B-cases-haut avec B-K7arr |

**Ajouté pendant la campagne, avant tout résultat de BQN (hors plan, information)** : B-K7tab, K7 naturel relié par
le facteur de K7 optimisé du C (sa table plate) au lieu de celui de sa table chaînée. `•HashMap` est une table à
adressage ouvert (`src/builtins/search.c`, `hashmap_set` : charge gardée sous 7/8), comme le `TDictionary` de
FreePascal, dont le K7 naturel s'était révélé sans doute trop pénalisé par le facteur de la table chaînée du C
(F-K7tab, `docs/FPC.md` 4.4). B-E garde le pont du plan.

Les rapports des copies et des variantes sont appliqués tels qu'ils sont mesurés, dans un sens ou dans l'autre (pas
de min(1, r)) : ce sont d'autres lectures de la règle, pas des améliorations. Rapports : moyenne géométrique des
médianes de processus, intervalle par bootstrap ; latences : médiane de toutes les répétitions, colonne par colonne.
Pour chaque scénario : score, piliers, rang espéré de BQN, ses voisins et les probabilités de précédence ; rangs
espérés des 23 autres et leurs écarts à « Avant ». Information : le rapport BQN / C de chaque cellule sur la machine
26 et les facteurs du pont par clé avec les deux témoins. Sorties : `results/bqn_check.json`, `results/report_bqn.md` ;
puis régénération des sorties publiées (réplication comprise) et de l'état actuel.

### 3.6 Ce qui change ailleurs

`analysis/analyze.py` (`RANKED`), `analysis/analyze_v2.py` (pont : `ADDED`, `ADDED_ER` ; groupe « JIT ou VM » ; noms),
`analysis/analyze_v3.py` (générateur de BQN, classe JIT, réplication), `analysis/capabilities.py` (fait),
`analysis/footprint.py` (`STRUCTURAL`), `analysis/report.py` et `analysis/capabilities_md.py` (noms, ordre).
`analysis/nosimd_check.py` : BQN n'a pas de variante à vecteurs explicites (ses primitives sont vectorisées par
l'implémentation, comme une bibliothèque) ; aucune cellule ne change. Confrontation : BQN n'est pas dans l'étude
« Banc », il sort des tests qui comparent à elle, et c'est signalé. `analysis/c_check.py` et
`analysis/nosimd_check.py` prennent B-E pour témoin du classement courant. `tools/c3_measure.py` (liste, classe JIT),
graphiques. Texte : README (24 langages, tableau, paragraphe de BQN), FINDINGS, METHODOLOGY (journal),
`docs/NATURAL.md` (fait), CAPABILITIES (régénéré).

### 3.7 Ce que je ne fais pas

* Pas de mesure sur un Cascade Lake (aucun disponible) : le pont des clés de la machine 1 traverse les modèles ; B-gcc
  et B-hôte en donnent la sensibilité ; c'est écrit dans les limites.
* Pas d'autre implémentation de BQN que CBQN (la demande la nomme), pas de branche de développement, pas d'autre
  construction que `make o3n` (pour la cible de l'hôte des données de chaque clé, 2.1) et la cible par défaut
  `make o3` : ni `has=…`, ni réglage du JIT, ni options du compilateur C.
* Pas d'appel à du code C par `•FFI` dans le code optimisé (règle), pas de `)gc disable` (commande du REPL, hors
  d'atteinte d'un programme).
* K10 n'existe pas en BQN (ni threads ni coroutines) : rien n'est mesuré, comme pour les cellules absentes des autres
  langages.

## 4. Résultats (après les mesures)

Mesures (`tools/measure_bqn.py`, machine 26, calibration à 13:47:26, passes de 13:50:44 à 15:11:12) : 1071
processus (153 cellules × 7 passes), aucune somme de contrôle fausse ; 18 processus refaits pour vol de temps, aucun
gardé au-dessus de 2 % (1,96 % au plus), vol médian 0,16 %. Empreinte de K1 : 256 o par particule au tas de CBQN dans
les trois processus, 128 o retenus (taille de structure, plan 3.1) ; le RSS monte de 866 o par particule, les
intermédiaires du décodage des f32 restant dans le tas. C3 mesurée : ½. La boucle chaude de K9 naturel est vectorisée
(registres ymm, 28 % des échantillons) ; celle de K4 naturel (52 %) est le filtre `/`, une compression Singeli par
`vpshufb` sur une table de 256 motifs, 128 bits, que la règle de `analysis/hotloop.py` compte scalaire parce qu'elle
ne retient que l'arithmétique empaquetée (une seule instruction, `vpaddb`) ; la comparaison `128 ≤ d` (25 %) est
vectorisée, la somme `+´` des entiers de 16 bits (13 %, `sum_i16`) est scalaire.
Contrôle : le scénario Avant (BQN retiré) reproduit à l'identique le classement d'avant (R-E de
`results/fpc_remark.json`, écart 0). Sorties : `results/bqn_check.json`, `results/report_bqn.md`.

### 4.1 BQN face au C, sur le même hôte (machine 26)

Rapports BQN / C (moyennes géométriques des médianes de processus ; binaire de la cible Cascade Lake face au C
publié, natif face au C natif pour K5) :

| Groupe | Cellules (rapport) |
|---|---|
| Plus rapide que le C | K5 naturel 0,60 (le produit vectoriel puis la chaîne d'additions, contre la chaîne de FMA du C) ; Q6 naturel 0,86 (masques sur des colonnes entières, contre la boucle à conditions du C) ; K8 optimisé 0,66 (l'arbre indexé construit niveau par niveau, contre l'arène du C) |
| Même ordre que le C | K3 `rmw_packed` 1,05 (le C y paie le partage de la ligne entre quatre fils) ; K2 à 8 Mio 1,24 ; Q6 optimisé 1,34 |
| Coût d'une primitive interprétée | K2 à 16 Kio 4,47 et à 256 Kio 2,03 (8 ns par saut) |
| Primitives contre boucle compilée | K1 naturel 3,87, `aos` 4,93, `soa` 12,4 (f64 contre f32, réduction AVX-512 du C) ; K4 naturel 3,01, trié 2,31, sans branchement 4,61 ; K5 optimisé 7,53 ; Q1 naturel 5,78 et optimisé 9,90 ; K7 optimisé 5,09 ; K9 naturel 19,4 (une matrice neuve par décalage), optimisé 6,60 |
| Pas de threads | K3 `rmw_padded` 11,5, `sw_padded` 211 et `sw_packed` 190 (quatre fois 2^25 mises à jour interprétées à la suite, contre quatre fils) ; Q6 `mt` 4,50, Q1 `mt` 20,6 ; K9 `mt` 21,3 |
| Structures naturelles | K7 naturel 28,0 (`•HashMap`) ; K8 naturel 9,43 (listes imbriquées ; latences p50 9,6, p99 9,9, p99,9 8,7, max 6,4) |

Le binaire natif de la machine 26 ne change presque rien (natif / Cascade Lake : 0,85 à 1,10, le plus bas sur K2 à
8 Mio, d'intervalle 0,61 à 1,00 ; K6 `tuned` et `mt`, où le binaire natif filtre par `vpcompress`, gagnent 6 à 9 % ;
K3 perd 4 à 10 %).

### 4.2 Le pont et le classement publié (B-E)

Facteurs du pont (C publié / C machine 26) sur les clés de la machine 1 : 0,75 à 3,6, sauf K3 `sw_padded` (4,8),
`sw_packed` (11,4) et K7 naturel (16,3), comme pour FreePascal. Sur les clés venues du même modèle, proches de 1 :
K5 0,85 et 1,02, K9 0,99 à 1,14 ; latences de K8 naturel, colonne par colonne, 0,80 à 1,48. Le second témoin donne
des facteurs voisins, sauf sur K4 (0,94 à 1,30 contre 1,79 à 2,47), K1 naturel (1,65 contre 1,23) et K8 naturel (1,78
contre 1,42).

**Classement publié (B-E)** : BQN **21e** sur 24, **18,65 points** [18,5–18,8], rang espéré 20,89, rang plausible 20
à 22, 3e étage. Contrôle 22,8 (22e ; 24,3 en règle v1, avec C3 = ½), plafond 12,45 [12,1–12,8] (21e : devant
JavaScript, 12,2, Lua et Python), code par défaut 22,7 (21e ; D1 0,038, empreinte D2 0,71, queues de latence D3 0,10,
hiérarchie mémoire D4 0,43). Plafond par noyau : K1 0,08, K3 0,02, K4 0,23, K5 0,12, K6 0,15, K7 0,20, K8 0,61, K9
0,07. OCaml (20e, 23,9 points) le devance dans 75 % des variantes ; BQN devance JavaScript (22e, 15,6) dans 87 %,
Python dans 98 %, Lua dans toutes.

Les 23 autres gardent leurs scores ; JavaScript, Python et Lua reculent d'un rang (rangs espérés + 0,87, + 0,98 et
+ 1,00), OCaml de 0,25 ; les autres bougent de 0,01 au plus. **Les étages changent** : BQN, placé entre OCaml et
JavaScript et proche des deux, relie les deux derniers étages ; ils sont désormais trois, [14, 5, 5] au lieu de
[14, 5, 1, 3], le dernier réunissant OCaml, BQN, JavaScript, Python et Lua.

### 4.3 Sensibilités (plan 3.5)

| Scénario | Score | Contrôle | Plafond | Code par défaut | Rang espéré | Place | Rang à 90 % |
|---|---|---|---|---|---|---|---|
| **B-E (publié)** | 18,65 | 22,8 | 12,45 | 22,7 | 20,89 | 21e | 20–22 |
| B-direct (information) | 21,72 | 22,8 | 19,33 | 24,0 | 20,40 | 20e | 20–21 |
| B-hôte | 19,01 | 22,8 | 14,32 | 21,2 | 20,76 | 21e | 20–22 |
| B-gcc | 19,18 | 22,8 | 13,80 | 22,7 | 20,80 | 21e | 20–22 |
| B-natif (information) | 18,90 | 22,8 | 12,55 | 23,5 | 20,84 | 21e | 20–22 |
| B-o3 | 18,52 | 22,8 | 12,34 | 22,3 | 20,92 | 21e | 20–22 |
| B-K1ns | 17,31 | 22,8 | 12,45 | 17,4 | 21,07 | 21e | 20–22 |
| B-K7arr | 18,81 | 22,8 | 12,45 | 23,3 | 20,84 | 21e | 20–22 |
| B-K8ns | 18,65 | 22,8 | 12,45 | 22,7 | 20,87 | 21e | 20–22 |
| B-fp | 17,87 | 22,8 | 12,45 | 19,6 | 20,98 | 21e | 20–22 |
| B-C3 | 18,65 | 22,8 | 12,45 | 22,7 | 20,93 | 21e | 20–22 |
| B-cases-bas | 16,06 | 15,4 | 12,45 | 22,7 | 21,21 | 21e | 20–22 |
| B-cases-haut | 21,02 | 29,6 | 12,45 | 22,7 | 20,67 | 21e | 20–22 |
| B-tout-bas | 14,19 | 15,4 | 12,34 | 15,4 | 21,55 | 21e | 20–23 |
| B-tout-haut | 21,18 | 29,6 | 12,45 | 23,3 | 20,63 | 21e | 20–22 |

* **Le pont entre modèles tient** : avec le second témoin (B-gcc), BQN a 19,18 points (+ 0,53) ; avec un seul facteur
  d'hôte (1,492, B-hôte), 19,01. B-direct (20e, devant OCaml dans 59 % des variantes) est biaisé, comme pour
  FreePascal : la machine 26 est plus rapide que la machine 1 pour presque tous les codes. Le binaire natif (B-natif)
  ajouterait 0,25 point.
* **Rapports sur le même hôte** : la construction par défaut ralentit le code naturel de 1,12 à 1,83 sur les noyaux de
  tableaux (K1 1,54 et 1,56, K4 1,83, K5 1,12, Q6 1,28, Q1 1,25), pas K7, K8 ni K9 (0,98 à 1,02) ; les espaces de noms
  coûtent 3,49 sur K1 naturel et 13,3 sur K1 mélangé (des références : le parcours devient aléatoire), 1,19 sur K8
  (latences × 1,12 à 1,20, maximum × 0,83) ; l'idiome tableau divise K7 naturel par 7,5 (0,134).
* Les cases (B-cases-bas, B-cases-haut) déplacent le score de 2,6 points vers le bas et de 2,4 vers le haut ; le
  pilier C de BQN tient à peu de cases (22,8), et chacune pèse. BQN reste **21e dans tous les scénarios du plan** ; dans
  la lecture la plus défavorable (B-tout-bas, 14,19 points), il ne devance plus JavaScript que dans 47 % des variantes
  (rang espéré 21,55).

### 4.4 Hors plan : K7 naturel et la table du C (B-K7tab, information)

Relié par le facteur de la table chaînée du C (16,3), K7 naturel de BQN vaut 142,9 s dans les données publiées, le
temps le plus long de l'étude (Haskell 88,7 s, FreePascal 78,4 s, Python 28,3 s) ; sur la machine 26, il prend 8,76 s,
28 fois le C. Relié par le facteur de la table plate du C (K7 optimisé, 3,15), il vaut 27,6 s : 18,77 points
(+ 0,12), rang espéré 20,85, 21e. Ce scénario a été déclaré pendant la campagne, avant tout résultat de BQN (3.5) ; le
classement garde la règle du plan. De même, K3 `sw_packed` est relié par un facteur de 11,4 (29,7 s publiés), qui
traduit le faux partage du C sur la machine 1 et non un trait de BQN ; il n'entre pas dans le score (E ne retient que
les dispositions espacées).

### 4.5 Réplication (machine 3)

BQN entre dans la réplication par le pont du C natif (`c_er`, binaire natif de BQN) : 21e sur la machine 3 (17,30
points). Ce n'est pas une réplication indépendante pour lui. L'accord entre machines et le test nul, calculés sur les 21
langages répliqués indépendamment, ne changent pas.

### 4.6 Écarts au plan

* B-K7tab, ajouté pendant la campagne, avant tout résultat de BQN (3.5, poussé à 13:52, deux minutes après le début
  des passes) : information, hors du classement.
* Aucun processus gardé au-dessus de 2 % de vol de temps ; aucun rejeté.
* Pendant la campagne, seule l'intégration à l'analyse a été écrite (pont, générateur, `analysis/bqn_check.py`, témoins
  des états actuels) ; rien n'a été exécuté hors de vérifications de syntaxe.

### 4.7 Bilan

BQN se classe **21e sur 24**, entre OCaml et JavaScript, dans le dernier étage. Son plafond (12,45) est celui d'un
langage dont chaque primitive est rapide mais dont chaque appel coûte : là où un noyau tient en quelques primitives sur
de grands tableaux, il approche le C ou le dépasse (K5 naturel, Q6 naturel, K8 optimisé, K4 à 2 à 3 fois) ; là où il
faut une boucle (K2 à petite taille, K3, la table de hachage de K7, l'arbre de K8 naturel), l'interprète domine, et
sans threads les variantes parallèles restent séquentielles. Son code par défaut (22,7) est pénalisé par les flottants
64 bits (128 o par particule), les queues de latence du comptage de références et du ramasse-miettes (D3 0,10) et un
coût fixe par primitive qui masque la hiérarchie mémoire aux petites tailles (D4 0,43). Son contrôle (22,8) est celui
d'un langage de tableaux : tableaux multidimensionnels natifs, stockage étroit automatique, projection de fichiers sans
copie, mais ni disposition des enregistrements, ni SIMD explicite, ni threads, ni atomiques. Le rang résiste aux deux
contrôles du pont entre modèles et à toutes les sensibilités du plan.
