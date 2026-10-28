# Spécification des noyaux de mesure (contrat commun aux 21 langages)

Version 1.0 — figée le 2026-10-28, **avant** toute mesure inter-langages.

Chaque noyau illustre un ou plusieurs principes de *mechanical sympathy*. Toutes
les implémentations lisent **les mêmes fichiers binaires** (générés une fois par
`tools/gendata.c`). Elles calculent **le même résultat**, vérifié au bit près pour
les résultats entiers et avec une tolérance relative pour les résultats flottants.

## 0. Conventions communes

* Données : répertoire `$MS_DATA` (défaut `/opt/msdata`). Tableaux bruts
  little-endian, sans en-tête. `u8/u32/i32/f32` = entiers non signés/signés 8/32
  bits, flottant IEEE-754 binaire32.
* Interface : `prog <kernel> <variant> <reps> [param]`. Pour chaque répétition
  mesurée, le programme écrit une ligne :
  `RESULT;<kernel>;<variant>;<param>;<rep>;<seconds>;<checksum>`.
  `seconds` est le temps **mural** de la seule section chronométrée, mesuré avec
  l'horloge monotone de plus haute résolution du langage. Le chargement des
  données, la construction des structures et la vérification ne sont **pas**
  chronométrés (sauf mention contraire).
* Échauffement : avant les `reps` mesures, le programme exécute **une** répétition
  non mesurée. Le pilote peut demander des répétitions supplémentaires
  (`WARMUP` env, défaut 1 ; 3 pour les langages à JIT).
* Lignes informatives facultatives : `META;<clé>;<valeur>`.
* Variantes :
  * `natural` : le code qu'un développeur écrirait spontanément en suivant la
    documentation officielle du langage. Il utilise le type d'enregistrement et le
    conteneur **par défaut**, sans annotation de performance.
  * `tuned` : le meilleur code possible **dans le langage et sa bibliothèque
    standard livrée avec la chaîne officielle** : types SIMD, intrinsèques, `unsafe`,
    pragmas, attributs et options de compilation documentées sont permis.
    Interdits : FFI vers du code C/C++/asm écrit à côté, assembleur en ligne et
    bibliothèques tierces.
  * Les autres variantes sont définies noyau par noyau.
* Interdits dans toutes les variantes : déplacer le calcul hors de la zone chronométrée,
  et calculer le résultat à la compilation à partir des données. Les données ne sont
  connues qu'à l'exécution, ce qui l'empêche de fait.

## K1 — Disposition mémoire : AoS / SoA / objets (DOD)

Principes : localité spatiale, granularité ligne de cache (64 o), coût de
l'indirection (pointer chasing), sur-coût des en-têtes d'objets.

* Fichier `k1_particles.f32` : N1 = 4 194 304 particules × 16 champs `f32`, dans l'ordre
  AoS (particule 0 champs 0..15, particule 1 …). Champs dans l'ordre :
  `x y z vx vy vz ax ay az mass charge radius temp pressure energy density`
  (64 octets par particule).
* Fichier `k1_perm.u32` : permutation de 0..N1-1 (Fisher–Yates).
* Noyau `k1` (param = `energy`) : `E = Σ_i 0.5 * mass_i * (vx_i² + vy_i² + vz_i²)`.
  Le calcul se fait en f32 ou en un type plus précis, l'accumulation en f64 (ou
  plus) dans n'importe quel ordre. Résultat f64 ; tolérance relative 1e-6.
* Variantes :
  * `aos` : tableau contigu d'enregistrements **valeurs** de 16 champs, si le
    langage le permet. Sinon on prend la représentation la plus proche et on le
    signale par `META;aos_repr;...`. Code optimisé (comme `tuned`).
  * `soa` : 16 tableaux contigus (un par champ). Seuls 4 sont lus. Code
    optimisé (comme `tuned`). `aos` et `soa` reçoivent le même effort
    d'optimisation, ce qui isole l'effet de la seule disposition mémoire.
  * `natural` : le type enregistrement par défaut du langage (class, record, struct,
    table…) dans la collection séquentielle par défaut (liste, vecteur, slice…).
  * `natural_shuffled` : même structure que `natural`, mais la collection est réordonnée
    selon `k1_perm` avant la mesure (élément j ← élément perm[j]). Pour un conteneur
    de valeurs, le parcours reste séquentiel ; pour un conteneur de références, il
    devient aléatoire en mémoire.
* Mesure annexe d'empreinte : `prog k1 footprint 1` construit la collection
  `natural`. Le pilote compare le pic RSS au mode `prog k1 footprint0 1`
  (collection vide). Résultat : octets par particule.

## K2 — Visibilité de la hiérarchie mémoire (latence)

Principe : latence L1/L2/L3/DRAM et coût d'une dépendance de données.

* Fichiers `k2_chase_<S>.u32` pour S ∈ {16K, 64K, 256K, 512K, 2M, 8M, 16M, 32M, 64M, 256M}
  (octets). Tableau de S/4 entiers `u32`. L'élément d'indice `16k` contient
  `16·succ(k)`, où `succ` est un cycle unique aléatoire (algorithme de Sattolo) sur les
  S/64 « nœuds » d'une ligne de cache chacun. Les autres éléments valent 0.
* Noyau `k2` (param = S) : `i = 0; répéter H = 4 200 000 fois : i = a[i]`. Résultat =
  `i` final (entier). La boucle doit être une vraie chaîne de dépendances :
  interdit de paralléliser, de dérouler en plusieurs chaînes ou de précharger.
* Variante unique `tuned` : le tableau entier le plus compact disponible
  (tableau typé `u32`/`i32`).

## K3 — Faux partage (false sharing) et principe de l'écrivain unique

* T = 4 threads (vrais threads matériels parallèles). Chaque thread t incrémente
  ITER = 2^25 fois **son propre** compteur entier 64 bits `c[t]`.
* Deux mécanismes d'incrément :
  * `rmw_*` : incrément atomique lecture-modification-écriture (`fetch_add`, ordre
    le plus faible disponible). Sur x86-64, c'est toujours `lock xadd`/`lock add`,
    quel que soit le langage : on compare le langage, pas l'instruction.
  * `sw_*` (*single writer*) : chaque compteur n'a qu'un écrivain, donc aucun RMW
    n'est nécessaire. On fait `c[t] = c[t] + 1` avec la lecture/écriture la moins coûteuse
    que le langage garantit visible et non élidable : atomique `relaxed`/`opaque`,
    `volatile`, sinon le plus faible disponible (qui peut être un store
    séquentiellement cohérent, donc `xchg`). Le mécanisme est déclaré par
    `META;k3_mechanism;...`.
* Disposition : `*_packed` : 4 compteurs adjacents (même ligne de cache) ;
  `*_padded` : compteurs espacés d'au moins 128 octets.
* Variantes : `rmw_packed`, `rmw_padded`, `sw_packed`, `sw_padded`.
* Chronométré : du lancement des threads jusqu'à leur `join`. Résultat = Σ c[t] = 4·2^25.

## K4 — Prédiction de branchement

* Fichier `k4_bytes.u8` : N4 = 16 777 216 octets aléatoires.
* Noyau `k4` : `s = Σ v pour v ≥ 128` (accumulateur entier 64 bits).
* Variantes : `natural_unsorted` (if naturel sur les données telles quelles),
  `natural_sorted` (le même code sur une copie triée, triée hors chrono),
  `branchless_unsorted` (forme sans branchement au niveau source :
  `s += v * (v >> 7)` ou équivalent).

## K5 — SIMD : produit scalaire en cache L1

* Fichiers `k5_a.f32`, `k5_b.f32` : n = 2048 flottants dans [0,1).
* Noyau `k5` : répéter `INNER = 2^16` fois `d = Σ_i a[i]·b[i]`. Résultat = d de la
  dernière itération (f32 ou plus). Tolérance relative 1e-3. Le compilateur ne
  doit pas pouvoir prouver que les itérations sont identiques : le tableau `a`
  est passé via une barrière d'optimisation (fonction non inlinée, `volatile`,
  `black_box`…) ou bien `a[0]` est modifié de 0 à chaque itération par une
  écriture opaque.
* Variantes : `natural` (boucle simple, sémantique flottante stricte par défaut),
  `tuned` (types SIMD explicites, accumulateurs multiples, annotations de
  réassociation…).
* Métrique : GFLOP/s = 2·n·INNER / t.

## K6 — Requêtes OLAP colonnaires (TPC-H Q6 et Q1 simplifiées)

* N6 = 16 777 216 lignes. Colonnes :
  `k6_shipdate.i32` (jours depuis 1970, dans [8035, 10592)), `k6_quantity.u8` (1..50),
  `k6_discount.u8` (0..10, en %), `k6_tax.u8` (0..8, en %),
  `k6_returnflag.u8` (0..2), `k6_linestatus.u8` (0..1),
  `k6_extendedprice.i32` (100..50000, en centimes).
* `q6` : `Σ price·discount` pour les lignes vérifiant
  `8766 ≤ shipdate < 9131 ∧ 5 ≤ discount ≤ 7 ∧ quantity < 24` (entier exact).
* `q1` : sur les lignes avec `shipdate ≤ 10471`, groupement par
  `g = returnflag·2 + linestatus` (6 groupes). Agrégats par groupe : `count`,
  `Σqty`, `Σprice`, `Σprice·(100−disc)`, `Σprice·(100−disc)·(100+tax)`.
  Checksum = somme des 30 agrégats (< 2^53, donc exacte même en flottant double).
* Variantes : `natural` (boucle ligne à ligne avec conditions), `tuned`
  (mono-thread, toutes techniques), `mt` (tuned, 4 threads, partition en morceaux).
* Métrique : lignes/s et Go/s des colonnes touchées (q6 : 10 o/ligne ; q1 : 13 o/ligne).

## K7 — Agrégation par hachage à forte cardinalité (GROUP BY)

* Fichiers `k7_keys.u32`, `k7_vals.u32` : N7 = 16 777 216 lignes, 2^20 clés distinctes
  (clés brouillées, non denses), valeurs dans 0..999.
* Noyau : pour chaque clé, `count` et `Σ val`. Après la mesure, on calcule le
  checksum `"<nb_clés>:<Σ_k sum_k·((k & 1023)+1)>"`.
* Variantes : `natural` (table de hachage de la bibliothèque standard),
  `tuned` (table maison à adressage ouvert).
* Chronométré : construction de la table seule (y compris son allocation).

## K8 — Allocation, ramasse-miettes et latence de queue

* Structure longue durée : un arbre binaire complet de profondeur 20 (2^21−1 nœuds)
  construit avant la mesure. Il reste vivant jusqu'à la fin.
* Q = 16 384 « requêtes ». La requête r construit un arbre binaire complet de
  profondeur 10 (2047 nœuds). Chaque nœud contient une valeur entière, égale à
  `r + numéro du nœud dans l'ordre préfixe`. La requête parcourt ensuite l'arbre
  pour en sommer les valeurs, puis l'abandonne ou le libère.
* Chaque requête est chronométrée individuellement. Sorties :
  `RESULT` (temps total des Q requêtes) et `LAT;<variant>;p50;p90;p99;p999;max` (ns).
  Checksum = Σ des sommes des requêtes + somme de l'arbre long.
* Variantes : `natural` (nœuds alloués individuellement de la manière par défaut du langage),
  `tuned` (arène, pool ou nœuds indexés dans des tableaux réutilisés : aucune
  allocation en régime permanent).

## K9 — Stencil 2D (HPC)

* Grille M×M, M = 2048, `f64`. Initialisation : `g[i][j] = ((i·31 + j·17) mod 1024) / 1024`.
* Itération Jacobi sur l'intérieur :
  `out[i][j] = 0.25 · (((in[i−1][j] + in[i+1][j]) + in[i][j−1]) + in[i][j+1])`
  (ordre d'évaluation imposé, sans contraction FMA, résultats identiques au bit
  près). Le bord est recopié. On échange `in` et `out`. IT = 4 itérations par
  répétition, toujours repartant de la grille initiale (réinitialisation hors chrono).
* Checksum = Σ de la grille finale (f64), tolérance relative 1e-12.
* Variantes : `natural` (le tableau 2D idiomatique du langage), `tuned` (tableau plat
  contigu, toutes techniques, mono-thread), `mt` (tuned, 4 threads). Chaque
  itération fait une passe complète de la grille. Le blocage temporel (fusion
  d'itérations), qui changerait l'algorithme et pas seulement la façon de
  l'exprimer, est interdit.

## K10 — File SPSC entre deux threads (style Disruptor)

* Un producteur envoie les entiers 1..M (M = 2^22) à un consommateur qui les somme.
  Checksum = M(M+1)/2.
* Variantes : `natural` (canal ou file concurrente standard du langage), `tuned`
  (anneau SPSC sans verrou, capacité 2^14, indices sur des lignes de cache
  séparées, copies locales des indices distants, ordres mémoire les plus faibles
  corrects disponibles, attente active).
* Chronométré : du démarrage des deux threads au `join` des deux.
