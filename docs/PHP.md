# Ajout de PHP : un 25e langage, mesuré sur la machine 28 et relié aux données publiées par le C

L'auteur de l'étude m'a demandé le 7 novembre d'ajouter PHP au banc. Ce document décrit la chaîne et les choix
d'implémentation, avec les faits relevés en écrivant le code (section 2). Il fixe le plan avant toute mesure de campagne
(section 3), puis donne les résultats (section 4). Comme pour Swift, FreePascal et BQN, je n'ai consulté aucune page
web pour les faits. Ils viennent de la chaîne installée et de ses sources (archive `php-8.5.12.tar.xz` de php-src :
`README.md`, `UPGRADING`, `ext/`, `Zend/`), de la documentation officielle lue dans son dépôt (php/doc-en, extraction
partielle au commit `124e1f5` du 6 novembre), de sondes et d'essais sur la machine 28. Seuls l'archive, la liste
officielle des versions (`releases/index.php?json` de php.net), la liste des étiquettes du dépôt php-src et
l'extraction de php/doc-en ont été téléchargées.

## 1. La demande

« Ajoute le langage PHP au benchmark » : implémenter les dix noyaux de `docs/SPEC.md`, noter la grille de capacités,
mesurer et ranger PHP dans le classement publié avec la même méthode que les 24 autres langages. La contrainte
pratique est celle de FreePascal et de BQN : les données publiées viennent de plusieurs hôtes (machine 1, Cascade Lake,
pour la plupart des noyaux ; machines 3, 11 et 16, Emerald Rapids, pour K5, les latences de K8 et K9), et seule la
machine 28 est disponible (un nouvel hôte Emerald Rapids du même modèle que les machines 3, 11, 16 et 24 à 27, 4 vCPU,
2,75 à 2,89 GHz effectifs, latences de 21, 35 et 128 ns à 2, 4 et 32 Mio, 16 à 17 Go/s en mémoire ;
`results/hw/machine28`). Les clés de la machine 1 seront donc reliées d'un modèle à l'autre (3.2).

PHP est un langage dynamique à machine virtuelle, avec un JIT livré mais inactif par défaut. Trois traits pèsent sur le
reste : ses conteneurs par défaut sont des tables de hachage ordonnées (les « tableaux ») et des objets en références,
chaque valeur occupant un zval de 16 octets ; il n'a ni fils ni SIMD ; sa mémoire est gérée par comptage de
références, avec un collecteur de cycles.

## 2. Chaîne, implémentation et faits relevés (avant le plan)

### 2.1 Chaîne

* **PHP 8.5.12** du 21 octobre 2026 (version de sécurité), la dernière version stable selon la liste officielle de
  php.net (8.5.12, 8.4.27, 8.3.36 et 8.2.35, toutes du 21 octobre) et les étiquettes de php-src (la 8.6.0 n'en est
  qu'à `php-8.6.0RC5` ; je n'emploie ni la 8.6 ni la branche de développement). Archive `php-8.5.12.tar.xz`,
  SHA-256 `08bc2eba…1209`, égal à celui de la liste officielle.
* **Construction** : le README de php-src donne `./configure` pour la production (« For production »), puis `make`. Le
  banc prend cette construction avec les extensions livrées dont il a besoin, désactivées par défaut : `pcntl`
  (processus), `shmop` et `sysvshm` (mémoire partagée System V), `sysvsem` (sémaphores) et `ffi` (FFI), sans les
  interfaces CGI et phpdbg : `./configure --prefix=/opt/php85 --enable-pcntl --enable-shmop --enable-sysvsem
  --enable-sysvshm --with-ffi --disable-cgi --disable-phpdbg`. Compilateur : le `cc` du système (gcc 13.3), options
  par défaut de php-src (`-g -O2`, `-ffp-contract=off`), sans `-march` ; binaire non réentrant (NTS),
  SHA-256 `3cd23181…1677`. `php.ini-production` est installé comme `php.ini`.
* **Exécution** : le compilateur de PHP traduit le source en opcodes, qu'exécute la machine virtuelle Zend. OPcache,
  compilé d'office depuis la 8.5 (`UPGRADING` : « The Opcache extension is now always built into the PHP binary »),
  garde et optimise les opcodes ; son JIT, écrit sur le cadre IR depuis la 8.4, compile en mode « tracing » les boucles
  chaudes (après 61 tours, `opcache.jit_hot_loop`) et les fonctions chaudes (après 127 appels). **Par défaut, la CLI
  n'active ni OPcache (`opcache.enable_cli=0`) ni le JIT (`opcache.jit=disable` depuis la 8.4)** ; le manuel recommande
  le JIT tracing (« tracing/on: Use tracing JIT. Recommended for most users », `reference/opcache/ini.xml`). Le banc
  active les deux (`bench/php/run`) : c'est le mode « release » documenté de la chaîne, comme `-O` pour un compilateur.
  La CLI par défaut est une sensibilité (3.5).
* **Un seul binaire** : le C de l'interprète est compilé sans `-march`, et le JIT choisit ses instructions à
  l'exécution parmi SSE2 à SSE4.2, AVX, AVX2, BMI1 et CLDEMOTE (`ext/opcache/jit/ir/ir.h`), sans AVX-512. Cascade Lake
  a toutes ces extensions sauf CLDEMOTE, qui ne sert qu'à rétrograder dans le cache les lignes de code que le JIT vient
  d'écrire (`IR_GEN_CACHE_DEMOTE`) : le code est le même sur les deux modèles. Comme FreePascal, PHP n'a donc qu'un
  binaire, relié par le C de la construction de chaque donnée publiée (3.2).
* **Bibliothèque** : les extensions livrées avec php-src (standard, SPL, FFI, pcntl, shmop, sysvsem) ; aucune
  extension PECL (ni `parallel`, ni `ds`), aucune bibliothèque tierce ; la FFI ne sert qu'aux types C (tableaux et
  `struct`), jamais à appeler une fonction C (règle du banc, comme pour BQN). `ffi.enable` vaut `preload` par défaut,
  ce qui permet la FFI dans la CLI.

### 2.2 Implémentation (`bench/php/ms.php`)

Un seul programme, lancé par `bench/php/run`. Le code naturel suit `docs/NATURAL.md` ; le code optimisé garde la forme
la plus rapide parmi celles que j'ai essayées (2.4).

| Noyau | Naturel | Optimisé |
|---|---|---|
| K1 | classe `Particle` à 16 propriétés `float` typées, promues par le constructeur ; objets dans un tableau (liste) ; `foreach` | `aos` : tableau de 2^22 `struct particle` de la FFI (16 `float`, 64 o, contigus), lu par une vue `float[]` au pas de 16 ; `soa` : 16 tableaux de PHP de `float`, quatre lus |
| K2 | — | `uint32_t[]` de la FFI (4 o par élément, contre 16 dans un tableau de PHP), `$i = $a[$i]` |
| K3 | — | 4 processus (`pcntl_fork`) créés avant la mesure ; compteurs dans un segment System V (`shmop`) : `sw`, lecture et écriture par `shmop_read`/`shmop_write` (`unpack`/`pack` sur 64 bits) ; `rmw`, la même chose entre `sem_acquire` et `sem_release` (un sémaphore par compteur : PHP n'a pas d'atomiques) ; `padded` : 128 o entre deux compteurs |
| K4 | `foreach` et `if` sur un tableau d'entiers | `branchless` : `$s += $x * ($x >> 7)` |
| K5 | boucle `for`, un accumulateur | deux accumulateurs, boucle déroulée par deux |
| K6 | boucle ligne à ligne avec conditions (Q1 : un tableau de 30 agrégats, comme Python) | Q6 : chaque intervalle en une comparaison non signée (`(x - bas) & masque < largeur`), la date d'abord ; Q1 : cinq tableaux de six agrégats ; `mt` : 4 processus créés avant la mesure, colonnes partagées en copie sur écriture, un quart des lignes chacun, résultats par paires de sockets |
| K7 | le tableau de PHP (table de hachage), un couple `[compte, somme]` par clé | table à adressage ouvert écrite en PHP : clés et couples (compte, somme) entrelacés dans deux tableaux de 2^21 cases, sondage linéaire, hachage par les bits bas (les clés sont brouillées) |
| K8 | objets d'une classe `Node` à propriétés promues (`int`, `?Node`), construits et sommés par récursion | arène : trois tableaux réutilisés, arbre construit en ordre préfixe et sommé sans récursion (piles explicites, réutilisées) |
| K9 | tableau de tableaux 2048×2048, double indice, grilles échangées par affectation de liste | grille plate ; `mt` : 4 processus créés avant la mesure, chacun garde ses lignes (et une ligne de bord de part et d'autre) dans deux grilles privées, publie ses deux lignes extrêmes dans un segment partagé à chaque itération (double tampon), lit celles de ses voisins, et écrit ses lignes dans la grille finale du segment à la fin (dans le chrono) |
| K10 | Fibers : une suspension par valeur (hors score) | Fibers : anneau borné rempli par lots (hors score) |

Harnais : `hrtime(true)` (horloge monotone, en nanosecondes) ; fichiers lus par `file_get_contents` et décodés par
`unpack` (f32 en `float`, u32 en `int`), hors chrono ; la section chronométrée appelle le noyau par son nom, sans
fermeture (2.4, point 3) ; limite de mémoire levée (`memory_limit=-1`). K3, K6 `mt`, K9 `mt` et K10 émettent `META`.
Variantes de sensibilité (`bench/php/extra_variants`) : K1 `natural_arr` et `natural_arr_shuffled`, des tableaux
associatifs à 16 clés nommées, l'autre enregistrement courant de PHP. Copie : `bench/php_def`, le même source exécuté
par la CLI telle qu'elle est configurée par défaut (ni OPcache ni JIT).

Validation par le pilote (`tools/driver.py --quick`) : toutes les cellules de `bench/php` (K1 : 6 variantes ; K2 aux
dix tailles ; K3 : 4 ; K4 : 3 ; K5 : 2 ; K6 : 6 ; K7 : 2 ; K8 : 2 ; K9 : 3 ; K10 : 2 ; l'empreinte) et les 9 cellules
naturelles de `bench/php_def`, sommes de contrôle toutes justes.

### 2.3 La grille (sonde `probes/php`, 33 cases notées, `results/probes/php.txt`)

| Cat. | Cases |
|---|---|
| A | A1 = ½ (`struct` de la FFI en tableaux, 64 o par élément ; objets et tableaux de PHP en références, comme `ctypes.Structure` en Python) ; A2 = ½ (FFI : décalages des champs) ; A3 = ½ (FFI : `packed` et champs de bits ; `pack`/`unpack`) ; A4 = ½ (FFI : `aligned(64)`) ; A5 = ½ (`pack`/`unpack`, unions de la FFI) ; A6 = 0 ; A7 = ½ (tableaux fixes dans les `struct` de la FFI) ; A8 = ½ (types étroits de la FFI pour le stockage ; valeurs de PHP en 64 bits) |
| B | B1 = 1 (comptage de références ; le collecteur de cycles se désactive par `gc_disable`, comme en Python) ; B2 = 0 ; B3 = 0 (nombres jamais boxés, mais tableaux, objets et chaînes toujours sur le tas, comme JavaScript et BQN) ; B4 = ½ (arithmétique et appels sans allocation ; la copie sur écriture copie un tableau partagé à la première écriture, comme Lua) ; B5 = ½ (pointeurs de la FFI) |
| C | C1 = 0 ; C2 = 0 ; C3 mesurée ; C4 = 0 ; C5 = 0 (aucune construction de parallélisme de données) |
| D | D1 = ½ (pas de threads : processus de `pcntl` et segments partagés de `shmop`, lus et écrits par copie) ; D2 = 0 ; D3 = 0 ; D4 = ½ (`pcntl_setcpuaffinity`, PHP 8.4, processus entier ; 1 en règle v2, comme `os.sched_setaffinity` de Python) ; D5 = 0 |
| E | E1 = ½ (JIT livré mais inactif par défaut ; listage du code machine seulement avec une construction `--with-capstone`, comme le `USE_PERF` de CBQN) ; E2 à E5 = 0 ; E6 = ½ (seulement par les pointeurs de la FFI, non vérifiés ; ses tableaux sont vérifiés) ; E7 = 0 |
| F | F1 = ½ (tableaux multidimensionnels contigus de la FFI) ; F2 = 0 ; F3 = ½ (`int` de 64 bits signé dont le dépassement passe en `float` ; masques ; types de la FFI qui enveloppent) ; F4 = 0 (pas de projection de fichier hors de la FFI vers la libc, comme `node:ffi`) |

La FFI de PHP est notée comme `ctypes` en Python et `node:ffi` en JavaScript : une extension livrée avec la chaîne
qui donne des types C, d'où ½ pour les cases qu'elle seule tient. Pilier C : 25,9 en règle v1 avec C3 = 0 (29,9 avec
C3 = 1 ; C3 est mesurée en campagne), 27,4 en règle v2 (sans C3, avec D4 à 1 : `analysis/capabilities_v2.py`), contre
29,7 pour Python, 23,2 pour OCaml, 19,7 pour BQN, 14,6 pour JavaScript et 6,8 pour Lua. `analysis/check_probes.py` :
aucune divergence entre la sonde et `analysis/capabilities.py` (les cinq divergences listées sont les anciennes, de C
et de C++).

### 2.4 Faits relevés en écrivant le code (`tools/php_check/facts.sh`, `results/php_check/facts.txt`)

Les temps cités ici viennent d'essais de développement sur la machine 28 (quelques exécutions), pas de la campagne ;
ceux du C viennent de la campagne de l'ajout de BQN sur la machine 26, du même modèle (`results/raw_bqn/c.jsonl`).

1. **Un script récent échappe au JIT** : OPcache ne met pas en cache un fichier modifié depuis moins de 2 secondes
   (`opcache.file_update_protection`, défaut 2), et le JIT ne s'y applique pas. Le même produit scalaire coûte
   13,5 ns par élément juste après l'écriture du script et 1,65 ns une fois le script vieilli (`facts.txt`). Mes
   premiers essais étaient tombés dans ce piège ; le banc met l'option à 0 (`bench/php/run`).
2. **Un bogue du JIT tracing** : deux écritures `$st[$sp++] = …` de suite dans une boucle interne, relues par
   `$st[--$sp]`, font calculer faux le JIT tracing de PHP 8.5.12. La construction itérative d'un arbre complet de 2047
   nœuds ne s'arrête plus (la reproduction, `tools/php_check/src/jit_stack_bug.php`, s'arrête par une garde), alors
   qu'elle est juste sans JIT, avec le JIT « function » et avec une pile à indices explicites. Le K8 optimisé écrit
   donc ses piles à indices explicites ; le pilote vérifie la somme de contrôle de chaque répétition.
3. **Une fermeture qui capture les données coûte cher** : K1 naturel appelé à travers une fermeture qui capture le
   tableau d'objets prend 0,89 s, contre 0,50 s par un appel direct ; le collecteur de cycles passe 36 fois pendant
   les quatre répétitions dans les deux cas, mais il y dépense 2,6 s au lieu de 1,4 s (`fermeture_gc.php`). Mon
   premier harnais passait par des fermetures ; il appelle maintenant le noyau par son nom, comme le ferait un
   programme ordinaire. Le collecteur de cycles reste actif (c'est le réglage par défaut) : chaque objet parcouru
   par `foreach` perd une référence et devient une racine possible.
4. **Les entiers ne s'enroulent pas** : un `int` qui dépasse 2^63 devient un `float` (manuel, « Integer overflow » ;
   `4294967295 * 4294967295` donne `1.8446744065119617E+19`). Un hachage multiplicatif sur 32 bits, comme celui du C
   (`k * 0x9E3779B1`), passe en flottant ; le K7 optimisé hache par les bits bas.
5. **La place des données** : une particule de K1 occupe 352 o au tas (`memory_get_usage`) : l'objet, 16 zvals de 16 o
   et son en-tête, plus le zval de la liste qui le désigne ; en tableau associatif à 16 clés, 712 o ; un tableau de PHP d'entiers ou de flottants prend
   16 o par élément, un `uint32_t[]` de la FFI 4 o.
6. **K1 naturel** : 0,48 à 0,50 s, 117 ns par particule (C : 34 ms), alors que le même code tourne à 7,5 ns par
   particule quand les objets tiennent en cache : la boucle est limitée par la mémoire (des objets de 352 o, et une
   écriture du compteur de références de chaque objet).
7. **La FFI n'aide que K2** : à 16 Kio, 6,0 ns par saut contre 6,8 dans un tableau de PHP (C : 1,8 ns) ; à 8 Mio,
   38,5 contre 43,5 ns (C : 38 ns, la latence de la mémoire masque l'interprète). Partout ailleurs, les tableaux de la
   FFI sont plus lents que ceux de PHP : K1 `soa` 26 contre 6,1 ns par particule, K5 11,8 contre 1,55 ns par élément,
   K9 0,58 contre 0,13 s. Chaque accès à la FFI passe par une conversion de la donnée C en valeur PHP.
8. **Le JIT et les boucles simples** : K5 naturel prend 0,21 s (1,55 ns par élément), à peine plus que le C naturel
   (0,19 s, une chaîne de FMA) : les deux sont limités par la latence de l'addition. Deux accumulateurs donnent 1,44 ns
   par élément ; quatre ou huit, 1,64 à 1,66 ns (les vérifications de type et de borne de chaque accès dominent).
9. **Les processus** : un `fork` coûte 3 ms (12 ms avec 1 Gio de tableaux) ; un aller-retour lecture et écriture par
   `shmop` 141 ns, une paire `sem_acquire`/`sem_release` 473 ns, `pack`/`unpack` 3,4 et 5,6 ns par `double`. K3
   (validation, une répétition) : `rmw` 22 à 25 s (les sémaphores sont des appels système), `sw` tassé 15 s contre 5 s
   espacé : le faux partage se voit au travers des copies de `shmop` (C : 12 à 13 ms). K6 `mt` : Q6 37 ms, Q1 69 ms ;
   K9 `mt` : 46 à 72 ms, contre 134 ms en un processus.
10. **Formes essayées pour le code optimisé** : Q6, 0,202 s (naturel) → 0,142 s (comparaisons non signées), la
    lecture locale de la date seule ne gagnant que 4 % ; K7, 3,7 s (naturel) → 2,1 s (deux tableaux `count`/`sum`
    indexés par la clé) → 1,2 à 1,0 s (adressage ouvert) ; K8, 4,0 s (naturel) → 1,7 s (arène récursive) → 0,62 à
    0,67 s (arène sans récursion). K9 : 0,90 à 0,96 s en tableau de tableaux, 0,13 s en grille plate, 0,147 s en lignes
    copiées localement (copie sur écriture de chaque ligne).

## 3. Plan (poussé avant les mesures)

### 3.1 Ce qui entre dans le classement publié

* **PHP, 25e langage classé** (`RANKED`, en dernier) : ses temps reliés aux données publiées par le pont du C (3.2), sa
  grille (2.3, `analysis/capabilities.py` et `capabilities_v2.py`), sa vectorisation mesurée (C3,
  `tools/c3_measure.py php` : boucles chaudes de K4 et K9 naturels) et son empreinte (`results/raw_post/php.jsonl`,
  étiquette `post_fp2`, puis `analysis/footprint.py`). L'empreinte compte les octets vivants du tas de Zend
  (`memory_get_usage` après `gc_collect_cycles`), qui suivent le RSS (352 et 345 o par particule à la validation) :
  aucune taille de structure n'est substituée.
* **Les 24 autres langages** : leurs données ne changent pas. Leur score ne bouge que par PHP lui-même : références t*
  s'il est le plus rapide sur une mesure, rangs, étages.
* **Réplication (machine 3)** : PHP y entre par le même pont, avec le C natif d'Emerald Rapids. Ce n'est pas une
  réplication indépendante pour lui ; le rapport le dit.

### 3.2 Le pont par le C

Le pont est celui de Swift, de FreePascal et de BQN (`docs/SWIFT.md` 5.3, `docs/FPC.md` 3.2, `docs/BQN.md` 3.2).
Toutes les clés de PHP sont mesurées sur la machine 28. Pour chaque clé k du score (mesures de E et de D1, K1
`natural_shuffled`, K2 tuned aux trois tailles de D4) : chaque processus de PHP est multiplié par f(k) = G(C publié, k)
/ G(C machine 28, k), où G est la moyenne géométrique des médianes de processus. Le C mesuré sur la machine 28 est la
construction qui a produit les données publiées de chaque clé :
* `bench/c/ms` (cible Cascade Lake) pour les clés de la machine 1 (K1 à K4, K6 à K8), pour K9 (machine 16) et pour les
  latences de K8 naturel (D3, machine 11 : chaque colonne [p50, p90, p99, p99,9, max] multipliée par le rapport des
  médianes du C, colonne par colonne) ;
* `bench/c_er/ms` (construction native identique au binaire de la machine 3) pour K5 (machine 3) et pour la
  réplication (toutes les clés, machine 3).

PHP n'ayant qu'un binaire (2.1), ses processus sont les mêmes pour les deux témoins, comme ceux de FreePascal. Le pont
est fait dans `analysis/analyze_v2.py` (`ADDED` : `php` dans `results/raw_php` ; `ADDED_ER` : `php` avec `c_er` pour K5
et la réplication), après toutes les corrections du jeu publié, si bien que les sorties publiées, la réplication et les
scripts d'état actuel voient PHP de la même façon.

**Le pont entre modèles.** Pour les clés de la machine 1, le facteur traverse les modèles (Emerald Rapids vers Cascade
Lake). Il absorbe ce qui sépare les hôtes tel que le C le voit, pas ce qui toucherait PHP et le C différemment. Deux
contrôles, fixés ici : P-gcc (second témoin, compilé par un autre compilateur) et P-hôte (un seul facteur pour toutes
ces clés), 3.5.

**Tirages isolés.** Les tirages du bootstrap et des latences de PHP viennent de leur propre générateur (graine
SEED + 2405 ; Swift, FreePascal et BQN gardent SEED + 2402 à 2404) : la suite des tirages des autres langages ajoutés ne
change pas. Les résidus de PHP n'entrent pas dans les réservoirs des autres ; pour ses propres tirages, il puise dans
le réservoir des langages à JIT (`JIT` de `analysis/analyze_v3.py` : JIT actif dans le banc, échauffement de 3
répétitions comme Java, C#, JavaScript et BQN). Il est le dernier de `RANKED`, donc ses bruits de jugement de la grille
sont tirés après ceux des autres. Contrôle : le calcul avec PHP retiré doit reproduire à l'identique le classement
d'avant (R-E de `results/bqn_remark.json`).

Groupe de backend (profil « langage et implémentation ») : « JIT ou VM », avec Java, C#, JavaScript, LuaJIT et BQN.

### 3.3 Copies

* `bench/php` : le banc publié (OPcache et JIT tracing), avec les variantes de sensibilité de 2.2.
* `bench/php_def` : le même source exécuté par la CLI telle qu'elle est configurée par défaut (`php.ini-production`,
  ni OPcache ni JIT ; seule la limite de mémoire est levée).
* `bench/c_gcc_cl` : le second témoin (le binaire des données publiées de `c_gcc`, `docs/FPC.md` 3.3).

### 3.4 Mesures (`tools/measure_php.py`, machine 28)

122 cellules en 7 passes (854 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20261107 + 2800) :
* `php` : les 29 cellules du score (K1 : 4 ; K2 tuned à 16 Kio, 256 Kio et 8 Mio ; K3 : 4 ; K4 : 3 ; K5 : 2 ; K6 : 6 ;
  K7 : 2 ; K8 : 2 ; K9 : 3), plus K1 `natural_arr` et `natural_arr_shuffled` ;
* `c` et `c_er` : les 29 cellules du score ;
* `c_gcc_cl` : les 24 cellules des clés de la machine 1 ;
* `php_def` : les 9 cellules naturelles du score (K1 `natural` et `natural_shuffled`, K4, K5, K6 Q6 et Q1, K7, K8, K9).

Répétitions : celles de `results/calib.json` pour les trois C. Pour PHP, la règle du pilote (3 s divisées par le temps
d'une répétition, entre 3 et 10 ; 2 au-delà de 5 s), appliquée à une répétition de calibration faite au début (avec
l'échauffement de la campagne) et écrite dans `results/calib.json` ; les cellules de `php_def` prennent les répétitions
de la cellule de `php`. Échauffement : 3 pour `php` et `php_def`, 1 pour le C ; règle de vol du pilote. Puis l'empreinte
(3 processus, `php`) et C3 (`tools/c3_measure.py php` : K4 et K9 naturels). Rien d'autre ne tourne. Sortie :
`results/raw_php/`. Durée prévue : deux heures environ, dont la moitié pour les 28 processus de K3 `rmw`.

### 3.5 Scénarios (`analysis/php_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | le classement publié à 24 langages (R-E de `results/bqn_remark.json`) ; le calcul avec PHP retiré doit le reproduire à l'identique |
| **P-E (publié)** | PHP ajouté : pont par le C (3.2), grille, empreinte mesurée, C3 mesurée |
| P-direct | information : les temps de la machine 28 sans pont pour les clés de la machine 1 (pont gardé pour K5, K9 et les latences, venus du même modèle) |
| P-hôte | P-E ; clés de la machine 1 multipliées par la médiane, sur ces clés, des facteurs f(k) du C (un facteur d'hôte au lieu d'un par clé) |
| P-gcc | P-E ; clés de la machine 1 reliées par le second témoin : G(`c_gcc` publié, k) / G(`c_gcc_cl` machine 28, k) |
| P-défaut | P-E ; les 9 cellules naturelles × r(`php_def` / `php`) : la CLI telle qu'elle est configurée par défaut, sans OPcache ni JIT |
| P-K1arr | P-E ; K1 `natural` × r(`natural_arr` / `natural`) et `natural_shuffled` × r(`natural_arr_shuffled` / `natural_shuffled`) : tableaux associatifs à clés nommées |
| P-C3 | P-E ; C3 = 0 si la mesure donne plus |
| P-cases-bas | P-E ; les cases que seule la FFI tient (A1, A2, A3, A4, A7, B5, E6, F1) = 0, comme une FFI vers le C, et D1 = 0 (des processus, pas des fils) |
| P-cases-haut | P-E ; E1 = 1 (le JIT est actif dans le mode documenté du banc ; interfaces perf et gdb sans reconstruire), C5 = ½ (processus de `pcntl`), B3 = ½ (valeurs scalaires jamais sur le tas, comme Lua) |
| P-tout-bas, P-tout-haut | P-cases-bas avec P-défaut, P-K1arr et P-C3 ; P-cases-haut seule |
| P-K7tab | information : K7 naturel relié par le facteur de K7 optimisé du C (sa table plate) au lieu de celui de sa table chaînée, comme B-K7tab de BQN (la table de PHP n'est pas chaînée par nœuds alloués un à un) |

Les rapports des copies et des variantes sont appliqués tels qu'ils sont mesurés, dans un sens ou dans l'autre (pas
de min(1, r)) : ce sont d'autres lectures de la règle, pas des améliorations. Rapports : moyenne géométrique des
médianes de processus, intervalle par bootstrap ; latences : médiane de toutes les répétitions, colonne par colonne.
Pour chaque scénario : score, piliers, rang espéré de PHP, ses voisins et les probabilités de précédence ; rangs
espérés des 24 autres et leurs écarts à « Avant ». Information : le rapport PHP / C de chaque cellule sur la machine
28 et les facteurs du pont par clé avec les deux témoins. Sorties : `results/php_check.json`, `results/report_php.md` ;
puis régénération des sorties publiées (réplication comprise) et de l'état actuel.

### 3.6 Ce qui change ailleurs

`analysis/analyze.py` (`RANKED`), `analysis/analyze_v2.py` (pont : `ADDED`, `ADDED_ER` ; groupe « JIT ou VM » ; noms),
`analysis/analyze_v3.py` (générateur de PHP, classe JIT, réplication), `analysis/capabilities.py` et
`capabilities_v2.py` (faits), `analysis/report.py` et `analysis/capabilities_md.py` (noms, ordre).
`analysis/nosimd_check.py` : PHP n'a pas de variante à vecteurs explicites ; aucune cellule ne change. Confrontation :
PHP n'est pas dans l'étude « Banc », il sort des tests qui comparent à elle, et c'est signalé. `analysis/c_check.py` et
`analysis/nosimd_check.py` prennent P-E pour témoin du classement courant. `tools/c3_measure.py` (liste, classe JIT ;
fait), graphiques. Texte : README (25 langages, tableau, paragraphe de PHP), FINDINGS, METHODOLOGY (journal),
`docs/NATURAL.md` (fait), CAPABILITIES (régénéré).

### 3.7 Ce que je ne fais pas

* Pas de mesure sur un Cascade Lake (aucun disponible) : le pont des clés de la machine 1 traverse les modèles ; P-gcc et
  P-hôte en donnent la sensibilité ; c'est écrit dans les limites.
* Pas d'autre version que la 8.5.12 (ni la 8.6 en RC, ni la branche de développement), pas d'extension PECL, pas
  d'appel de fonction C par la FFI, pas de réglage du JIT au-delà de son activation (ni `jit_hot_loop`, ni
  `jit_buffer_size`), pas de `gc_disable` dans le code naturel.
* K10 est implémenté et validé (Fibers) mais, comme pour BQN, n'est pas mesuré : il est hors score.

## 4. Résultats (après les mesures)

### 4.1 Mesures

Mesures (`tools/measure_php.py`, machine 28, calibration de 08:16:26 à 08:23:33, passes de 08:23:33 à 10:00:37) :
854 processus (122 cellules × 7 passes), aucune somme de contrôle fausse ; 13 processus refaits pour vol de temps,
aucun gardé au-dessus de 2 % (1,82 % au plus), vol médian 0,19 %. Empreinte de K1 : 352,00 o par particule au tas de
Zend dans les trois processus (RSS : 345 o), retenus tels quels (D2a = 0,18). C3 mesurée : 0, après une correction de
l'outil (4.2) : la boucle chaude de K4 naturel est du code du JIT, scalaire (vérification du type, comparaison,
addition avec contrôle de débordement, test d'interruption de la machine virtuelle) ; celle de K9 naturel n'est pas du
code du JIT mais le gestionnaire `ZEND_FETCH_DIM_R` de la machine virtuelle (`execute_ex`) : pour les lectures dans un
tableau de tableaux, le JIT rend la main à l'interprète (`results/vectorization/php_k4.txt`, `php_k9.txt`).

### 4.2 Écarts au plan

1. **C3, outil corrigé.** L'échantillonneur (`tools/sampler.c`) et `analysis/hotloop.py` ne copiaient le code des JIT
   que dans les projections anonymes et la mémoire `/memfd:` de .NET ; OPcache écrit le code de son JIT dans une
   mémoire partagée projetée depuis `/dev/zero`, que `/proc/<pid>/maps` nomme « /dev/zero (deleted) ». La mesure de la
   campagne s'est donc arrêtée sur une erreur, notée scalaire par défaut. Les deux outils reconnaissent maintenant cette
   projection (aucun autre langage n'en a : vérifié dans les 60 autres profils publiés) ; les deux profils de PHP ont été
   refaits juste après la campagne (10:02 et 10:03). Résultat : 0, la même valeur, mais mesurée.
2. **K2 à 8 Mio, pont robuste.** Sur cet hôte, le tableau de 8 Mio tient dans le L3 partagé avec les autres machines
   virtuelles, et chaque processus tourne soit vers 160 ms, soit vers 520 ms (fait déjà relevé par la remarque sur
   C++, `docs/CPP.md`). Le témoin `c` a eu deux processus lents sur sept (515 et 532 ms ; `c_er` deux, `c_gcc_cl` un, et un
   intermédiaire à 244 ms), PHP aucun (156 à 168 ms). La moyenne géométrique du pont mêle les régimes : PHP sortait 1,4 fois plus rapide
   que le C (0,72 [0,44–1,03]), le plus rapide des 25 langages à cette taille (453 ms reliés, contre 594 ms pour
   Haskell), et chacun des 24 autres perdait 0,06 à 0,42 point par D4, dont la référence est le meilleur temps. Dans un
   même régime, PHP et le C font la même chose (161 et 163 ms en médiane : une chasse de pointeurs que la latence du
   cache borne). Décidé après avoir vu les données : pour cette seule clé, le facteur du pont prend la médiane des
   médianes de processus du témoin et de PHP (`BRIDGE_MEDIAN` de `analysis/analyze_v2.py`, même règle pour le second
   témoin de P-gcc et pour la réplication) : 3,835 au lieu de 2,810, PHP à 617 ms reliés. Le calcul du plan reste un
   scénario d'information (P-E-plan : PHP 16,60 points, 22e). Pour BQN, relié depuis la machine 26 avec un processus
   lent de chaque côté, la même règle déplacerait cette clé de 8 % : elle n'est pas appliquée, le mélange y étant
   équilibré.
3. **Aucun autre.** Cellules, répétitions, scénarios et règles comme fixés en 3.4 et 3.5.

### 4.3 PHP face au C sur la machine 28, et le pont

Rapports PHP / C (moyennes géométriques des médianes de processus, `results/report_php.md`) :

| Noyau | Naturel | Optimisé et autres variantes |
|---|---|---|
| K1 | 17,2 (mélangé 38,1) | `aos` 5,1 ; `soa` 10,8 |
| K2 | — | 3,3 à 16 Kio ; 1,25 à 256 Kio ; 1,0 à 8 Mio (médianes ; 0,72 en moyenne géométrique, 4.2) |
| K3 | — | `rmw` 10,0 tassé, 97 espacé ; `sw` 1 066 tassé, 409 espacé |
| K4 | 103 (trié 36) | `branchless` 33 |
| K5 | 1,18 | 50 |
| K6 | Q6 3,8 ; Q1 6,1 | `tuned` Q6 9,5, Q1 12,0 ; `mt` Q6 8,7, Q1 12,5 |
| K7 | 12,3 | 8,0 |
| K8 | 5,9 (latences : p50 231 µs, p99,9 836 µs, max 2,8 ms) | 2,5 |
| K9 | 70 | 10,2 ; `mt` 13,5 |

PHP est au niveau du C là où le C lui-même attend la mémoire ou une chaîne de dépendances : K5 naturel (1,18 : les deux
sont bornés par la latence de l'addition flottante) et K2 à 256 Kio (1,25) et à 8 Mio (1,0). Dès que le C vectorise ou compte les cycles, l'écart
s'ouvre : 33 à 103 fois sur K4, 50 sur K5 optimisé, 70 sur K9 naturel. Ses meilleures formes restent 2,5 (K8, arène
itérative) à 13 fois le C. K3 mesure le coût des appels à `shmop` et à `sysvsem`, pas la cohérence des caches.

Facteurs du pont (C publié / C de la machine 28) : 0,74 à 3,8 sur les clés de la machine 1, sauf K3 `sw` (4,7 espacé,
11,3 tassé : le faux partage du C sur Cascade Lake, sans rapport avec PHP, dont le temps vient des appels) et K7 naturel
(15,4, la table chaînée du C ; 3,1 pour sa table plate, P-K7tab) ; 0,85 à 1,15 pour K5 et K9 ; facteur d'hôte unique
1,53 (P-hôte).

### 4.4 Le classement publié (P-E) et les scénarios

| Scénario | Score | Contrôle | Plafond | Code par défaut | Rang espéré | Place | Rang à 90 % | devant BQN | devant JavaScript |
|---|---|---|---|---|---|---|---|---|---|
| **P-E (publié)** | **16,56** | 27,4 | 4,50 | 20,7 | 22,32 | **22e** | 20–23 | 16 % | 43 % |
| P-direct (information) | 17,74 | 27,4 | 8,02 | 19,8 | 21,79 | 22e | 20–23 | 33 % | 72 % |
| P-hôte | 16,10 | 27,4 | 5,83 | 16,8 | 22,30 | 22e | 20–23 | 15 % | 46 % |
| P-gcc | 16,65 | 27,4 | 4,64 | 20,9 | 22,30 | 22e | 20–23 | 17 % | 44 % |
| P-défaut | 16,29 | 27,4 | 4,42 | 19,8 | 22,39 | 23e | 20–23 | 14 % | 39 % |
| P-K1arr | 16,40 | 27,4 | 4,50 | 20,1 | 22,35 | 23e | 20–23 | 15 % | 41 % |
| P-C3 | 16,56 | 27,4 | 4,50 | 20,7 | 22,32 | 22e | 20–23 | 16 % | 43 % |
| P-cases-bas | 11,91 | 14,1 | 4,50 | 20,7 | 22,98 | 23e | 22–24 | 2 % | 14 % |
| P-cases-haut | 18,39 | 32,6 | 4,50 | 20,7 | 22,07 | 22e | 20–23 | 26 % | 52 % |
| P-tout-bas | 11,51 | 14,1 | 4,42 | 19,2 | 23,03 | 23e | 22–24 | 1 % | 12 % |
| P-tout-haut | 18,39 | 32,6 | 4,50 | 20,7 | 22,07 | 22e | 20–23 | 26 % | 52 % |
| P-K7tab (information) | 16,61 | 27,4 | 4,50 | 20,9 | 22,31 | 22e | 20–23 | 16 % | 43 % |
| P-E-plan (information) | 16,60 | 27,4 | 4,50 | 20,9 | 22,29 | 22e | 20–23 | 17 % | 44 % |

* **Classement publié (P-E)** : PHP est **22e sur 25, à 16,56 points** [16,3–16,8] (rang plausible 20 à 23), derrière
  BQN (qui le devance dans 84 % des variantes) et à égalité de fait avec JavaScript : il passe devant lui au rang espéré
  (22,32 contre 22,34) et par le score central (16,56 contre 15,6), mais JavaScript le devance dans 57 % des variantes.
  Les deux langages ont des profils opposés : PHP a le double du contrôle de JavaScript (27,4 contre 14,6 : la FFI,
  `pack`, les processus et la mémoire partagée), JavaScript trois fois son plafond (12,2 contre 4,5 : V8 compile mieux
  que le JIT tracing de PHP les boucles sur tableaux). Selon le poids donné aux piliers, l'un ou l'autre passe devant.
  Code par défaut 20,7 (code naturel 0,015 ; empreinte 0,29 ; queues de latence 0,23 ; hiérarchie mémoire 0,61). Plafond par noyau :
  K8 0,16, K7 0,13, K1 0,09, K6 0,08, K9 0,07, K4 0,03, K5 0,02, K3 0,003.
* **Sensibilités** : PHP reste 22e ou 23e dans toutes les lectures, entre BQN et Python. La CLI par défaut (sans OPcache
  ni JIT) coûte 0,27 point : le JIT divise par 8,9 le temps de K5 naturel, par 3,2 et 4,2 celui de Q6 et Q1, mais
  par 1,2 à 1,6 seulement celui des noyaux où dominent les tables, les objets et le ramasse-miettes (K1, K7, K8, K9) ;
  les tableaux associatifs à la place des objets, 0,16 point (K1 1,9 fois plus lent, 2,5 fois dans le désordre). Les
  cases que seule la FFI tient, mises à 0 avec D1, retirent 4,6 points (contrôle 14,1, à peu près celui de JavaScript) ; PHP reste
  devant Python dans 83 % des variantes.
* **Les 24 autres langages** gardent leurs scores (écart nul). Leurs rangs espérés bougent : JavaScript, Python et Lua
  reculent d'un rang (+ 0,42, + 0,98, + 1,00), BQN de 0,21, OCaml de 0,08. Au milieu du classement, D (− 0,24), Swift
  (+ 0,16), Julia (− 0,11), Chapel (+ 0,10), C3 (− 0,09), Zig (+ 0,08), Mojo et FreePascal (+ 0,07) bougent aussi, et
  deux paires à égalité de fait échangent leurs places : C3 passe 4e devant Zig (rang espéré 5,11 contre 5,14 ; 5,20
  contre 5,06 avant PHP) et Fortran 11e devant Swift (10,85 contre 10,86 ; 10,84 contre 10,70 avant). Dans les deux
  paires, le duel direct penche toujours de l'autre côté : C3 ne devance Zig que dans 46 % des variantes (45 % avant),
  Fortran Swift dans 48 % (46 % avant) ; le rang espéré somme les duels avec tous les autres, et C3 perd moins souvent
  que Zig face à D, Rust, Chapel et Swift, Fortran moins souvent que Swift face à Julia, D et C3. Cet effet vient de
  D3 : dans la moitié des variantes de l'analyse, les latences de K8 sont lues relativement à la médiane (p99,9/p50 et
  max/p50), et PHP, dont les requêtes sont lentes mais régulières, a la plus petite queue relative (max/p50 de 11,4,
  contre 20,0 pour Zig, le suivant) : il devient la référence de D3 dans ces variantes, ce qui baisse le D3 de tous et
  rebat les paires serrées. Contrôle : avec la latence maximale de PHP doublée, seuls ses voisins bougent encore
  (JavaScript, Python, Lua, BQN et OCaml, de plus de 0,05), et C3, Zig, Fortran et Swift retrouvent exactement leurs
  rangs espérés d'avant PHP.
* **Étages** : PHP rejoint le dernier étage, qui passe de cinq à six langages ([14, 5, 6]).

### 4.5 Réplication (machine 3)

PHP entre dans la réplication par le pont du C natif (`c_er`), avec la même règle pour K2 à 8 Mio : 22e sur la machine
3 (15,76 points). Ce n'est pas une réplication indépendante pour lui. L'accord entre machines et le test nul, calculés
sur les 21 langages répliqués indépendamment, ne changent pas.

### 4.6 Bilan

PHP est **22e sur 25** (16,56 points), dans le dernier étage, entre BQN et JavaScript, avec qui il est à égalité de
fait. Sans changer aucun score, son ajout fait basculer deux paires à égalité de fait plus haut dans le classement (C3
passe devant Zig, Fortran devant Swift), parce qu'il devient la référence des queues de latence relatives (4.4). Son contrôle est celui d'un langage dynamique qui a une FFI et des processus : au niveau de Python (27,4 contre
29,7), plus haut que celui de JavaScript, de BQN et de Lua. Son plafond est bas : le JIT tracing compile bien les
boucles simples sur des tableaux d'entiers et de flottants (K5 naturel au niveau du C), mais chaque valeur est un zval
de 16 octets, chaque objet une référence de 352 octets par particule, sans SIMD, sans fils et sans tableau typé hors de
la FFI. Deux faits de la chaîne pèsent sur qui voudrait mesurer PHP : la CLI n'active pas le JIT par défaut, et le JIT
tracing de 8.5.12 calcule faux une forme courante de pile (2.4, point 2).
