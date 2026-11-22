# v4, point 6 : une piste ouverte (bibliothèques tierces) — plan (22 novembre 2026)

*Plan détaillé du point 6 de `docs/V4_PLAN.md` (remarque 4 de `docs/AUDIT3_2026-11-18.md` : « une piste
« bibliothèque standard seule » et une piste « ouverte », côte à côte »). Poussé avant toute recherche dans les
registres, toute installation de bibliothèque, tout code et toute mesure. Le classement de tête du README ne change
pas : la piste ouverte est publiée à côté de la piste « bibliothèque standard seule », qui reste celle du classement.*

## 1. Question

Le banc n'admet que la bibliothèque standard livrée avec la chaîne : les variantes optimisées n'ont droit à aucune
bibliothèque tierce (`docs/SPEC.md`, 0), et une capacité que seule une bibliothèque tierce fournit vaut 0 dans la
grille (`docs/CAPABILITIES.md`, légende). La règle est la même pour tous, mais elle laisse de côté l'outillage habituel
de plusieurs langages : NumPy pour Python, la crate `libc`, `rayon` et `crossbeam` pour Rust, MAX pour Mojo, `vector`,
`primitive`, `unordered-containers` et `hashtables` pour Haskell (README, Limites ; `docs/AUDIT3_RESPONSE.md`, 3).

Question : **avec une liste de bibliothèques tierces fixée d'avance par une règle commune, que deviennent la grille
(pilier contrôle) et le plafond de chaque langage ?** Le code par défaut (pilier D) ne change pas : le code naturel
suit la documentation officielle du langage (`docs/SPEC.md`, 0), qui ne comprend pas les bibliothèques tierces.

## 2. Faits établis avant le plan (22 novembre)

* **Règle actuelle.** `docs/SPEC.md`, 0 : `tuned` admet « types SIMD, intrinsèques, `unsafe`, pragmas, attributs et
  options de compilation documentées » et interdit « FFI vers du code C/C++/asm écrit à côté, assembleur en ligne et
  bibliothèques tierces ». Grille : ○ = « absente, ou seulement par une bibliothèque tierce, ou en appelant par une FFI
  du code C non intrinsèque » ; la libc compte pour C et C++ seulement (règle unique de la libc et des FFI).
* **Cases de la grille qui portent sur une API.** Sur les 34 capacités, 15 décrivent ce qu'une API fournit, et une
  bibliothèque peut donc les combler : A6 (SoA), B2 (allocateurs, arènes), B5 (mémoire brute), C1 (types vectoriels
  portables), C2 (intrinsèques), C5 (parallélisme de données), D1 (threads), D2 (atomiques à ordres explicites), D3
  (aide ligne de cache), D4 (affinité), D5 (barrières, `pause`), E4 (préchargement), F1 (tableaux multidimensionnels),
  F2 (localité, NUMA), F4 (fichiers projetés). Les 19 autres décrivent le langage ou son compilateur (disposition des
  agrégats, ramasse-miettes imposé, pile, allocations cachées, vectorisation automatique mesurée, réassociation,
  code natif, assembleur en ligne, indications de branchement, non-aliasing, vérifications de bornes, génériques,
  entiers modulaires) : aucune bibliothèque ne les change.
* **Trous de la grille.** Dans la grille v2 corrigée par le point 1, ces 15 cases valent moins de 1 pour 217 couples
  (langage, case) : de 2 (C++ : A6, F2) à 15 (JavaScript, Lua). Python : 13 ; Rust : 9 (A6, B2, C1, C5, D3, D4, F1,
  F2, F4) ; Mojo : 9 (A6, B2, C5, D1, D3, D4, F1, F2, F4).
* **Trous du plafond.** Le portage du point 4 a prouvé « non écrivibles » 61 formes du catalogue faute de levier dans
  la bibliothèque standard (`results/converge/inventory.md`) : vecteurs explicites (Fortran, FreePascal, Haskell,
  OCaml, BQN, PHP, JavaScript, Python, Lua), fils parallèles (BQN, Lua), préchargement (Java, Go, Fortran, OCaml, BQN,
  PHP, JavaScript, Python, Lua).
* **Registres.** Joignables depuis le conteneur : PyPI, crates.io, npm, Hackage, opam, NuGet, Maven Central, le proxy
  des modules Go, dub, LuaRocks, Packagist, le registre General de Julia, les paquets de Modular (MAX) ; les clones
  Git depuis GitHub passent (registres nimble, Alire, Mason), mais ni l'API ni les archives de GitHub. Statistiques
  d'usage joignables : téléchargements de crates.io, de npm, de PyPI (pypistats), de Hackage, de NuGet, de Packagist,
  de dub et de LuaRocks ; requêtes de paquets de Julia ; « imported by » de pkg.go.dev ; dépendants de deps.dev
  (Maven) ; dépendants inverses d'opam (ocaml.org) ; installations (popcon d'Ubuntu).
* **Versions.** NumPy 2.5.5 (15 novembre) livre des roues pour CPython 3.15, la version classée (3.15.2). MAX 26.7.0
  est sorti le même jour que Mojo 1.2.0, la version classée, et le paquet `modular` 26.7.0 lie les deux.
* **Hôte.** Le conteneur a redémarré vers 6 h 44 sur un Xeon du même modèle (6/207) : machine 34, à caractériser.

## 3. La liste, fixée d'avance

### 3.1 Registre de chaque langage

| Langage | Registre | Statistique d'usage |
|---|---|---|
| C, C++ | archive de la distribution de l'hôte (Ubuntu) | installations (popcon d'Ubuntu) |
| Rust | crates.io | téléchargements des 90 derniers jours |
| D | dub | téléchargements du dernier mois |
| Nim | nimble (liste `nim-lang/packages`) | aucune (3.3, b) |
| Ada | Alire (index) | dépendants dans l'index (3.3, b) |
| Chapel | Mason (registre) | dépendants dans le registre (3.3, b) |
| Mojo | paquets de Modular (PyPI, `max`) et canal `modular-community` | aucune (3.3, b) |
| Swift | Swift Package Index | aucune (3.3, b) |
| C3 | dépôt `vendor` de c3lang (`c3c vendor-fetch`) | aucune (3.3, b) |
| FreePascal | fppkg | aucune (3.3, b) |
| Fortran | index des paquets de fortran-lang.org | aucune (3.3, b) |
| Go | modules (pkg.go.dev) | « imported by » |
| C# | NuGet | téléchargements |
| Java | Maven Central | dépendants (deps.dev) |
| Julia | General | requêtes du dernier mois (julialang-logs) |
| Haskell | Hackage | téléchargements des 30 derniers jours |
| OCaml | opam | dépendants inverses |
| JavaScript | npm | téléchargements du dernier mois |
| Python | PyPI | téléchargements du dernier mois (pypistats) |
| Lua | LuaRocks | téléchargements |
| PHP | Packagist | téléchargements du dernier mois |
| Zig, Odin, BQN | aucun registre (paquets par URL, collection `vendor` livrée, aucun gestionnaire) | — |

### 3.2 Recherche

Pour chaque couple (langage, case) de la section 2 où la case vaut moins de 1, le registre est interrogé avec les mots
de la case (table ci-dessous, en anglais ; un mot par requête, résultats réunis) ; les résultats sont classés par la
statistique d'usage du registre, et les dix premiers sont examinés dans cet ordre.

| Case | Mots |
|---|---|
| A6 | soa ; struct of arrays ; structure of arrays |
| B2 | arena ; bump allocator ; memory pool |
| B5 | raw memory ; pointer ; unsafe memory |
| C1 | simd ; vector types |
| C2 | intrinsics ; avx |
| C5 | parallel ; parallel for ; data parallel |
| D1 | threads ; multithreading |
| D2 | atomic ; atomics |
| D3 | cache line ; cache padded ; false sharing |
| D4 | affinity ; cpu affinity ; thread pinning |
| D5 | spin ; spin wait ; barrier |
| E4 | prefetch |
| F1 | ndarray ; multidimensional array ; matrix |
| F2 | numa ; hwloc |
| F4 | mmap ; memory map |

### 3.3 Choix

a. **La première bibliothèque admise dans cet ordre entre dans la liste pour cette case.** Admise : (1) son API
   documentée fournit le levier de la case, tel que la légende de la grille le définit ; (2) elle s'installe et
   s'exécute avec la chaîne classée, sur cet hôte ; (3) ce n'est ni une autre mise en œuvre ou un autre compilateur du
   langage (Numba, Cython, mypyc, PyPy, LuaJIT, GraalJS : ils relèvent d'« une ligne par compilateur », remarque 3),
   ni un moteur de requêtes qui exécute un calcul déclaré (DuckDB, Polars, Spark : une autre question), ni une liaison
   écrite pour l'étude. Si aucune des dix ne l'est, le trou reste, avec sa raison.
b. **Registre sans statistique** : toutes les bibliothèques trouvées sont examinées ; la première admise par le nombre
   de dépendants dans le registre quand il se calcule (Alire, Mason), sinon par ancienneté de la première version
   parmi celles qui ont publié une version depuis le 22 novembre 2024.
c. **Bibliothèques nommées par le dossier** (section 1) : elles entrent dans la liste pour les cases qu'elles
   comblent, même si la règle en choisit une autre, sauf si elles tombent sous a (3) : Numba et Polars, nommés par
   `docs/AUDIT3_RESPONSE.md`, en sont exclus.
d. Une bibliothèque peut combler plusieurs cases ; une case n'a qu'une bibliothèque de la règle (plus, le cas échéant,
   une bibliothèque nommée).
e. Les versions sont les dernières stables au 22 novembre 2026 qui s'installent avec la chaîne classée ; elles sont
   relevées et figées (fichiers de verrouillage).

### 3.4 Relevé

Les requêtes et leurs réponses (`results/open/registry/<langage>.json`), l'examen de chaque candidate et la liste
(`results/open/list.md` : langage, case, bibliothèque, version, statistique, raison des refus) sont poussés avant toute
sonde et toute forme. La même liste fixe, pour chaque bibliothèque, les cellules du plafond où son API documentée fait
le calcul chaud de la cellule ou remplace son conteneur (5.1) : aucune forme n'est écrite hors de ce relevé.

## 4. Grille ouverte

* **Sondes.** Chaque case comblée par une bibliothèque de la liste reçoit une sonde exécutée, selon la norme du point 1
  (`docs/GRID_AUDIT.md`, 2.1) : un programme qui se sert de l'API pour le levier de la case et en montre l'effet
  (affinité relue, page projetée lue, parallélisme constaté, préchargement présent dans le code machine quand le
  langage l'expose…), sortie gardée dans `results/open/probes/<langage>.txt`.
* **Note.** La case reçoit la note que la légende donnerait si l'API était dans la bibliothèque standard (1, ou ½ si
  la bibliothèque est expérimentale ou limitée) ; une sonde qui échoue laisse la note publiée.
* La grille ouverte est la grille v2 du score central, ces cases changées ; les autres cases ne changent pas.

## 5. Plafond ouvert

### 5.1 Formes

* Les 12 cellules du plafond des points 4 et 5 (K1, K3, K4, K5, Q6, Q1, Q6 mt, Q1 mt, K7, K8, K9, K9 mt).
* Pour chaque bibliothèque de la liste et chaque cellule que le relevé (3.4) lui attribue : une forme, l'idiome que la
  documentation de la bibliothèque donne pour ce calcul (expression sur tableaux entiers de NumPy, `par_chunks` de
  `rayon`, `parallelize` de MAX…), écrite à partir de la forme d'accès du langage (point 5 : la forme la plus rapide du
  point 4) en remplaçant la partie que la bibliothèque fournit ; deux au plus par couple, nommées dans le relevé. Une
  forme peut combiner des bibliothèques de la liste du même langage.
* Admission : les règles C2 du point 4 (`docs/V4_CONVERGE.md`, 3.2), la bibliothèque en plus ; K9 garde son ordre
  d'évaluation imposé et ses résultats au bit près ; K8 garde des nœuds à valeur et deux liens, sommés en suivant les
  liens.

### 5.2 Code et constructions

* Copies `bench/<langage>_op`, faites depuis `bench/<langage>_cv` ; formes nouvelles nommées `op_<bibliothèque>`.
* Bibliothèques installées hors du dépôt (`/opt/open/<langage>`), versions et fichiers de verrouillage dans
  `results/open/versions.txt` ; compilées avec les options de la construction publiée du langage (processeur hôte,
  niveau d'optimisation, ni PGO ni LTO) quand on les compile ; NumPy et MAX tels que distribués (roues binaires).
* Validation : chaque forme, exécutée une fois à la taille publiée, rend la somme de contrôle publiée
  (`tools/driver.py`) ; preuves d'exactitude relues (C2, 2).
* **Témoin de construction** : la forme d'accès de chaque cellule touchée est mesurée dans la construction `_op`
  (bibliothèques liées) et dans la construction `_cv`, pour vérifier que lier les bibliothèques ne change pas le code
  standard.

## 6. Hôte et campagne

* Machine 34 caractérisée au repos avant toute mesure (`tools/sizes/hwchar.sh`).
* Processus : pour chaque (langage, cellule) touché, chaque forme `op_*`, la forme d'accès dans `_op` et dans `_cv`,
  et la forme de C de la cellule (témoin d'hôte) ; pour K3, b3 au début et à la fin (`tools/equal/k3_ref.sh`).
* Pilote du point 4 (`tools/converge/campaign.py`), adapté : trois passes, ordre aléatoire à graine fixe par passe,
  répétitions fixées par la première passe (environ 3 s par processus, au moins trois), échauffement des JIT, vol de
  temps au-delà de 5 % refait une fois, sorties dans `results/open/work`, poussées à chaque fin de groupe. Aucune autre
  mesure pendant la campagne.

## 7. Analyse, fixée avant les mesures

* **Report** : une forme `op_*` mesurée sur la machine 34 entre dans l'ensemble « meilleur de » de sa cellule dans les
  données du point 4 (machine 33), avec le temps de la forme d'accès du point 4 multiplié par r, la médiane sur les
  trois passes du rapport (médiane de la forme `op_*`) / (médiane de la forme d'accès dans `_op`) ; ses tirages sont
  ceux de la forme d'accès, multipliés par r. La frontière de la cellule est recalculée.
* **Contrôle** : « Convergent, avec R4 » du point 4, refait par l'outil, à l'identique (comme au point 5).
* **Calculs** (méthode v3 du point 4 : même graine, 20 000 variantes, mêmes poids) :
  1. **Ouverte** : plafond ouvert et grille ouverte ;
  2. **Plafond ouvert seul** (grille publiée) ;
  3. **Grille ouverte seule** (plafond du point 4) ;
  4. **Bibliothèques nommées** : la piste ouverte réduite aux bibliothèques nommées par le dossier (3.3, c) ;
  5. **Cases comblées à ½** (sensibilité) : chaque case comblée par une bibliothèque vaut ½ ;
  6. **Report par le témoin C** (sensibilité) : r rapporté au rapport des formes de C de la cellule sur les deux
     hôtes, au lieu de la forme d'accès du langage ;
  7. **Coût d'accès** (information) : lignes des formes `op_*` (outil et règles de lecture du point 5,
     `docs/V4_COST.md`, 3.3 et 8) rapportées à celles du code naturel, à côté de la forme d'accès standard.
* Pour chaque calcul : scores, rangs espérés, rang plausible (90 %), étages indicatifs, langages qui bougent de plus de
  deux places par rapport à « Convergent, avec R4 » ; par cellule, la forme retenue et son rapport à la forme d'accès
  standard ; par langage, les cases changées. Sorties : `results/open/analysis.json`, `results/report_open.md`.

## 8. Publication

Le classement de tête du README ne change pas : la piste « bibliothèque standard seule » reste celle du classement.
La piste ouverte est publiée à côté (README, ce document). En faire une seconde colonne du classement final serait une
décision de l'auteur de l'étude, qui lui sera soumise avec les résultats.

## 9. Ordre de travail

1. Ce plan, poussé.
2. Machine 34 caractérisée.
3. Relevé de la liste (3.2 à 3.4), poussé avant toute sonde et toute forme ; écarts datés s'il le faut.
4. Sondes de la grille ouverte, langage par langage, poussées.
5. Formes du plafond, d'abord pour les bibliothèques nommées par le dossier (Python, Rust, Mojo, Haskell), puis dans
   l'ordre du classement ; validation, poussées au fur et à mesure ; outils de campagne et d'analyse poussés avant la
   campagne.
6. Campagne.
7. Analyse, résultats (section 11 de ce document), README, `docs/V4_PLAN.md`, journal.

## 10. Écarts datés

1. **Recherche (3.2), 22 novembre, 7 h 08, avant toute recherche retenue.** La recherche du site de PyPI est protégée
   par un défi JavaScript, et celle de Hackage refuse les requêtes automatisées (protection CSRF) : ni l'une ni
   l'autre n'est contournée. Le registre General de Julia, opam, le Swift Package Index et l'archive d'Ubuntu n'ont pas
   d'API de recherche. Pour ces registres, la requête devient la recherche des mots de la case (mot entier, sans
   distinction de casse) dans le nom, la description et les mots-clés des paquets de l'index du registre tel que le
   publie ecosyste.ms (service ouvert de métadonnées de paquets) : l'index entier (Hackage, opam, General, Swift
   Package Index, Ubuntu 24.04), ou ses 20 000 paquets les plus téléchargés (PyPI, près d'un million de paquets).
   Nimble, Alire, Mason, l'index de fortran-lang.org et le dépôt `vendor` de C3 sont lus de même dans leur propre
   index (fichier ou clone Git). Les statistiques d'usage restent celles de 3.1. Les registres qui ont une API de
   recherche publique (crates.io, npm, NuGet, Packagist, dub, Maven Central, pkg.go.dev, LuaRocks) sont interrogés
   par elle, comme prévu.
2. **Popcon (3.1), 22 novembre, 7 h 15, avant tout choix.** Le concours de popularité d'Ubuntu n'est plus publié
   (`popcon.ubuntu.com` ne sert plus de données) : pour C et C++, la statistique d'usage est celle de Debian
   (`popcon.debian.org`, installations), dont l'archive d'Ubuntu dérive ; l'index reste celui d'Ubuntu 24.04.
3. **Attribution des cellules du plafond (3.4), 22 novembre, 7 h 23, avant toute sonde et toute forme.** Le plan
   attribuait à chaque bibliothèque toutes les cellules où son API fait le calcul chaud : une bibliothèque de tableaux
   ou de vecteurs l'aurait été à huit cellules dans chaque langage, même là où la forme d'accès du langage (point 5)
   use déjà du même levier par sa bibliothèque standard. Une bibliothèque ne peut alors changer le plafond que par la
   qualité de sa mise en œuvre, et le portage du point 4 a déjà donné à chaque langage les meilleures formes connues
   de ce levier. L'attribution se limite donc aux cellules où la bibliothèque apporte un levier que la bibliothèque
   standard n'offre pas en entier, selon la grille du score central :
   * vecteurs explicites (C1, C2) ou opérations compilées sur tableaux entiers (F1) : K1, K4, K5, Q6, Q1, K9 et leurs
     formes à quatre fils, si C1 et C2 valent toutes deux moins de 1 ;
   * fils parallèles ou parallélisme de données (D1, C5) : Q6 mt, Q1 mt, K9 mt et K3, si D1 vaut moins de 1 ;
   * préchargement (E4) : K7, si E4 vaut moins de 1 ;
   * aide ligne de cache (D3) : K3, si D3 vaut moins de 1 ;
   * arènes et allocateurs (B2) : K8, si B2 vaut moins de 1 ;
   * SoA (A6) : K1, si A6 vaut moins de 1.
   Une bibliothèque qui comble une case n'est attribuée à une cellule de la table que si son API fait le calcul de
   cette cellule (une bibliothèque de tableaux sans opérations de calcul n'est attribuée à aucune). La grille ouverte
   (section 4) n'est pas touchée : toutes les cases comblées y comptent.
