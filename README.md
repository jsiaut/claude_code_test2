# Quels langages incarnent le mieux la *mechanical sympathy* ?

*Classement mesuré de 25 langages, octobre et novembre 2026. Tous sont mesurés sur une même machine, sept noyaux à
trois tailles de données, dans des conditions égales et avec un code optimisé convergent (campagne des 22 et
23 novembre ; analyse corrigée le 24, v4.1). Méthode : [`docs/METHOD.md`](docs/METHOD.md) ; corrections du
24 novembre : [`docs/V4_1.md`](docs/V4_1.md) ; étapes précédentes et archive : [`docs/HISTORY.md`](docs/HISTORY.md).*

Un seul critère : la *mechanical sympathy* au sens large, c'est-à-dire la capacité d'un langage à faire écrire du code
en accord avec le matériel : disposition des données, SIMD, hiérarchie mémoire, concurrence, allocation, requêtes
analytiques. C'est ce qu'exigent le HPC, les moteurs OLAP et le Data-Oriented Design. Le plafond et le code par défaut
sont mesurés sur un Xeon Emerald Rapids ; le pilier « contrôle » est un inventaire jugé.

## Le classement

| Rang | Étage | Langage | Score | Rang plausible | Devance le suivant | Sans la grille | Ce qui le place là |
|---|---|---|---|---|---|---|---|
| 1 | 1 | **C** | 81,4 | 1–3 | 75 % | 2 (1–4) | Le meilleur code naturel, le 2e code par défaut, le 3e plafond (1er sur K4 et K7) et le contrôle de GNU C (2e) ; son K8 le plus rapide, une arène écrite par itération, reste à 0,66 de la frontière |
| 2 | 1 | **C++** | 79,2 | 1–6 | 79 % | 4 (1–8) | Le plus de contrôle (`pmr`, atomiques, `std::simd` expérimental) et le 1er plafond, de peu (90,1 ; Chapel 89,9, C 89,6) : son arène de K8 par valeur fait la frontière de K8 ; code naturel 9e |
| 3 | 1 | **Odin** | 76,4 | 2–8 | 53 % | 6 (2–9) | À égalité de fait avec Rust. Le Data-Oriented Design dans le langage (`#soa`, `#simd`, intrinsèques de LLVM, allocateurs) : 5e contrôle, 5e code naturel ; plafond 9e (K4 70, K8 67) |
| 4 | 1 | **Rust** | 75,9 | 2–9 | 59 % | 1 (1–4) | Le meilleur code par défaut (2e code naturel, queues de latence de K8 courtes) et le 4e plafond ; contrôle 9e (ni affinité, ni `mmap` dans la bibliothèque standard) |
| 5 | 1 | **D** | 74,8 | 3–10 | 52 % | 7 (5–12) | À égalité de fait avec Nim. 5e plafond et 4e contrôle (le contrôle de C, templates et CTFE), mais les pauses de son ramasse-miettes font les pires queues de latence de K8 des 19 premiers (D3 : 2 sur 100) |
| 6 | 1 | **Nim** | 74,6 | 3–9 | 58 % | 3 (3–7) | Le meilleur K1 (98), 7e plafond, 3e code par défaut ; contrôle 7e (les leviers de C par sa compilation vers C) |
| 7 | 1 | **C3** | 74,2 | 3–9 | 62 % | 5 (3–7) | C avec vecteurs natifs : 6e plafond, 6e code naturel ; contrôle 8e (ni SoA ni intrinsèques officiels) ; 3e à trois tailles sans les autres règles de la v4 |
| 8 | 1 | **Zig** | 73,0 | 3–11 | 79 % | 11 (8–12) | 3e contrôle (tous les leviers du DOD) et le meilleur K6 (94), mais son code naturel compte en mode vérifié (`-O safe`, R1) : 11e code naturel, 3e place sans R1 ; plafond 8e (vectoriseur de boucles désactivé en 0.17) |
| 9 | 1 | **Ada** | 71,0 | 5–11 | 66 % | 12 (7–13) | Disposition au bit près : 6e contrôle, 10e plafond, les queues de latence de K8 les plus courtes après Fortran ; code naturel 10e (vérifications) |
| 10 | 1 | **Julia** | 69,6 | 6–13 | 67 % | 9 (6–13) | 3e code naturel et 13e plafond ; les pauses du ramasse-miettes pèsent sur K8 (D3 10) |
| 11 | 1 | **Fortran** | 68,1 | 7–14 | 66 % | 8 (5–13) | Les queues de latence de K8 les plus courtes, 4e code par défaut, 12e plafond ; ni SIMD explicite ni intrinsèques (K4 50, forme SWAR) : contrôle 14e |
| 12 | 1 | **Chapel** | 66,0 | 8–15 | 59 % | 10 (3–13) | Le 2e plafond (K9 98, K4 90, K8 80) ; code naturel 16e sous R1 (`--checks`) et contrôle 16e (leviers bas niveau rares ou instables) |
| 13 | 1 | **Swift** | 65,2 | 10–14 | 61 % | 13 (10–14) | Types SIMD et `InlineArray` : le meilleur K5 (97) ; vérifications de `-O` coûteuses sur le code naturel (14e) et le K4 le plus lent des 14 premiers (46) ; contrôle 13e |
| 14 | 1 | **Mojo** | 64,5 | 11–15 | 93 % | 14 (12–14) | Le SIMD au cœur du langage (K5 92, K7 95) ; ni vectoriseur de boucles (K4 50) ni threads publics dans `std` ; K8 46 |
| 15 | 1 | **C#** | 59,3 | 13–16 | 93 % | 16 (15–17) | La boîte à outils la plus riche des langages à GC : 15e plafond (K4 optimisé, réserves de fils) ; objets en références (K7 54, K8 50, désordre de K1) |
| 16 | 1 | **Java** | 51,2 | 15–18 | 56 % | 15 (14–17) | Les queues de latence de K8 les plus courtes des langages à ramasse-miettes (D3 59) et la Vector API (K5 84) ; pas de types valeur (K1 45, désordre de K1) ; contrôle 18e |
| 17 | 1 | **Go** | 50,6 | 16–18 | 58 % | 17 (15–18) | Structures par valeur et SIMD expérimental (K4 82) ; écritures atomiques séquentiellement cohérentes (K3 35) ; code naturel 18e |
| 18 | 1 | **FreePascal** | 49,3 | 15–19 | 88 % | 18 (16–19) | Records `packed`, assembleur, mémoire à la main : 15e contrôle ; ni vectoriseur ni intrinsèques : 19e plafond (K4 14, K5 39) et code naturel 21e |
| 19 | 1 | **Haskell** | 43,0 | 18–19 | 100 % | 19 (18–19) | Peut descendre bas (FMA vectorielle de GHC : K5 91 ; K7 90) ; code par défaut boxé, ramasse-miettes imposé : code par défaut 20e, contrôle 19e |
| 20 | 2 | **OCaml** | 26,7 | 20–21 | 92 % | 20 (20–21) | Bonne allocation générationnelle (D3 46) ; ni types valeur, ni flottant 32 bits de calcul, ni SIMD : plafond 22,7 |
| 21 | 2 | **BQN** | 19,9 | 20–23 | 47 % | 22 (20–22) | À égalité de fait avec JavaScript. Primitives vectorisées de CBQN, mais un coût fixe par appel ; ni threads, ni flottant 32 bits ; K1 hors mémoire à la grande taille |
| 22 | 2 | **JavaScript** | 19,9 | 21–24 | 70 % | 21 (21–22) | Tableaux typés compilés mais vérifiés, aucun SIMD : plafond 15,6 ; contrôle 24e |
| 23 | 2 | **PHP** | 18,0 | 21–23 | 97 % | 23 (23–23) | Chaque valeur un zval de 16 octets, chaque objet une référence : plafond 23e ; le contrôle d'un langage dynamique doté d'une FFI et de processus (21e) |
| 24 | 2 | **Python** | 10,5 | 22–25 | 76 % | 25 (25–25) | CPython seul : le plafond le plus bas (1,0), K1 naturel hors mémoire à la grande taille ; contrôle 20e (`ctypes`, sous-interpréteurs) |
| 25 | 2 | **Lua** | 7,1 | 24–25 | — | 24 (24–24) | PUC-Lua sans son API C : presque aucun levier (contrôle 6,8) ; plafond 1,4, au-dessus de CPython |

* **Score** (0–100) : 40 % de plafond mesuré (le meilleur code que le langage permet d'écrire pour la machine), 25 % de
  code par défaut mesuré (le code qu'on écrit sans y penser) et 35 % de contrôle (les leviers qu'offrent le langage et
  sa chaîne de compilation). Le score affiché est sa moyenne sur 20 000 variantes de l'analyse, qui tirent au hasard
  les poids des piliers et des tailles autour de ces valeurs, les normalisations, le jugement porté sur chaque capacité
  et le bruit de mesure. **Il fixe l'ordre.**
* **Rang plausible** : le rang dans 90 % des variantes. **Devance le suivant** : la part des variantes où le langage
  passe devant celui de la ligne suivante. Autour de 50 %, les deux langages sont à égalité de fait : Odin et Rust
  (53 %), D et Nim (52 %), BQN et JavaScript (47 %).
* **Sans la grille** : la place du langage, et son rang plausible, quand le poids du contrôle est mis à 0 dans toutes
  les variantes. C'est le classement sur les seules mesures ; le contrôle, lui, est jugé.
* **Étages** : les 19 premiers (de C à Haskell) et les six derniers (d'OCaml à Lua), chaque langage du premier
  devançant chacun du second dans au moins 99,6 % des variantes. Plus haut, les marches restent sous 95 % : les 14
  premiers devancent C# dans au moins 92,2 % des variantes, C# devance les quatre suivants dans au moins 93,4 %.
* **Cellules hors mémoire** : à la grande taille, les quatre variantes de K1 de BQN et K1 naturel de Python dépassent
  la mémoire de la machine ; elles prennent le temps admissible le plus lent des autres langages, ce qui les flatte
  sans doute.

![Classement de la v4.1](results/charts/classement_v4.svg)

### Les mesures et la grille, séparément

Le plafond et le code naturel sont mesurés ; le contrôle est une grille jugée de 34 capacités, dont chaque case repose
sur une sonde exécutée ou une mesure ([`docs/CAPABILITIES.md`](docs/CAPABILITIES.md)). Le tableau les donne séparément,
sur 100, avec les poids et les choix de méthode principaux ; le code naturel est rapporté au meilleur code naturel.

| Rang | Langage | Plafond (rang) | Code naturel (rang) | Contrôle (rang) |
|---|---|---|---|---|
| 1 | C | 89,6 (3) | 69,6 (1) | 91,7 (2) |
| 2 | C++ | 90,1 (1) | 48,9 (9) | 92,4 (1) |
| 3 | Odin | 83,7 (9) | 62,3 (5) | 84,0 (5) |
| 4 | Rust | 88,3 (4) | 66,1 (2) | 73,6 (9) |
| 5 | D | 87,0 (5) | 56,6 (7) | 87,1 (4) |
| 6 | Nim | 85,9 (7) | 63,3 (4) | 76,1 (7) |
| 7 | C3 | 86,8 (6) | 60,5 (6) | 75,7 (8) |
| 8 | Zig | 84,4 (8) | 36,6 (11) | 87,2 (3) |
| 9 | Ada | 83,7 (10) | 36,7 (10) | 80,6 (6) |
| 10 | Julia | 78,4 (13) | 64,4 (3) | 73,3 (10) |
| 11 | Fortran | 79,1 (12) | 55,5 (8) | 65,3 (14) |
| 12 | Chapel | 89,9 (2) | 26,2 (16) | 61,8 (16) |
| 13 | Swift | 80,6 (11) | 31,4 (14) | 68,1 (13) |
| 14 | Mojo | 76,0 (14) | 32,6 (13) | 70,5 (11) |
| 15 | C# | 71,2 (15) | 28,2 (15) | 68,8 (12) |
| 16 | Java | 66,0 (16) | 33,5 (12) | 42,7 (18) |
| 17 | Go | 62,6 (17) | 19,2 (18) | 48,7 (17) |
| 18 | FreePascal | 43,0 (19) | 13,6 (21) | 62,3 (15) |
| 19 | Haskell | 52,3 (18) | 15,9 (20) | 41,5 (19) |
| 20 | OCaml | 22,7 (20) | 20,6 (17) | 23,2 (22) |
| 21 | BQN | 10,1 (22) | 17,1 (19) | 19,7 (23) |
| 22 | JavaScript | 15,6 (21) | 13,0 (22) | 14,6 (24) |
| 23 | PHP | 6,6 (23) | 5,8 (23) | 27,4 (21) |
| 24 | Python | 1,0 (25) | 1,3 (25) | 29,7 (20) |
| 25 | Lua | 1,4 (24) | 2,9 (24) | 6,8 (25) |

Sans la grille (colonne du premier tableau ; [`results/report_final.md`](results/report_final.md)), les étages se
séparent davantage : les 14 premiers (de Rust à Mojo), puis Java, C#, Go, FreePascal et Haskell, puis OCaml,
JavaScript et BQN, puis PHP, Lua et Python, chacun seul. Rust et C s'y disputent la tête : Rust a le meilleur score
(78,5 contre 78,3), C est premier le plus souvent (43 % des variantes ; Rust 40 %, C++ 11 %). Le contrôle porte C++
(2e au lieu de 4e), Odin (3e au lieu de 6e), D (5e au lieu de 7e), Zig (8e au lieu de 11e) et Ada (9e au lieu de 12e) ;
il retient Rust (4e au lieu de 1er), Nim (6e au lieu de 3e), C3 (7e au lieu de 5e), Fortran (11e au lieu de 8e) et
Chapel (12e au lieu de 10e). Sur le plafond seul, la tête serait C++, Chapel, C, Rust, D, C3, à moins de quatre points
les uns des autres.

### Ce qui est sûr, et ce qui ne l'est pas

* **Les grandes marches sont établies.** Les 19 premiers devancent les six derniers dans au moins 99,6 % des
  variantes. Plus haut, Mojo devance C# dans 93 % des variantes, C# devance Java dans 93 % et Java devance Haskell
  dans 97 %.
* **C est premier, sans que ce soit un fait établi.** C est premier dans 69 % des variantes, C++ dans 23 %, Rust dans
  4 %, Odin dans 2,5 % ; C devance C++ dans 75 % des variantes, et chacun des deux devance chacun des 23 autres dans au
  moins 76 %. D'Odin à Zig, un langage ne devance le suivant que dans 52 à 62 % des variantes : l'ordre de ces six-là
  est la meilleure estimation, rien de plus.
* **La tête dépend peu des règles.** C est 1er dans neuf des douze sensibilités ; C++ passe devant si K3 n'est pas
  rapporté à la boucle de référence et à la seule grande taille, Rust sur les seules mesures. Peu de langages y bougent
  de plus de deux places : C3 (3e à trois tailles sans les autres règles de la v4, 4e sans la boucle de référence de
  K3), Zig (3e si son code naturel n'est pas compilé en mode vérifié), Ada et Fortran (12e et 8e à la seule petite
  taille).
* **Une machine.** Le classement est mesuré sur un seul hôte, sans réplication. Des machines du même modèle diffèrent,
  et la vitesse de celle-ci variait d'une seconde à l'autre : deux exécutions successives de la boucle de référence de
  K3 diffèrent jusqu'à 27 %.
* **Le contrôle pèse lourd, et il est jugé.** Sans lui, Rust passe 1er, C++ 4e, et six langages bougent de trois
  places : Rust, Nim et Fortran montent, Odin, Zig et Ada reculent.

### Ce que les corrections du 24 novembre ont changé

Le classement publié le 23 novembre plaçait C++ 1er et C 2e, à égalité de fait (C++ devant dans 51 % des variantes).
Quatre éléments du calcul y créaient des écarts qui ne tenaient ni aux langages ni aux mesures. Ils ont été corrigés le
24 novembre sans mesure nouvelle, par un plan poussé avant le recalcul ([`docs/V4_1.md`](docs/V4_1.md)).

* **A1.** La grille est notée dans toutes les variantes par la règle en vigueur ; l'ancienne règle, abandonnée parce
  qu'elle pénalise les langages normalisés (C, C++, Ada, Fortran), servait encore dans une variante sur deux.
* **A2.** La boucle de référence de K3 est prise à son plus mauvais placement et non à sa médiane : une boucle sans
  `lock` tombée sur un mauvais alignement reçoit 0,92 à 1, au lieu de 0,79 à 0,88.
* **A3.** Le code naturel est rapporté au meilleur code naturel et non au meilleur code optimisé, qui l'écrasait : le
  meilleur valait 20 sur 100, et ce demi-pilier ne séparait presque plus les langages.
* **A4.** Les mesures à quatre fils ne comptent plus à la petite taille, où 10 à 15 µs de calcul ne mesurent que le
  réveil des fils.

C repasse 1er (premier dans 69 % des variantes, contre 36 %) et aucun langage ne bouge de plus de deux places : D
passe de la 7e à la 5e, C3 de la 5e à la 7e, Julia de la 12e à la 10e, Chapel de la 10e à la 12e, Java de la 18e à la
16e. A1 et A3 font l'essentiel : sans A1, C n'est premier que dans 48 % des variantes ; sans A3, dans 57 % ; sans A2,
dans 65 % ; sans A4, rien ne change en tête, mais Chapel garde le 1er plafond. Sans les quatre, le calcul redonne à
l'identique le classement du 23 novembre, gardé dans [`results/report_final.md`](results/report_final.md) (« Méthode
du 23 novembre »).

## Ce qui sépare vraiment les langages

Les constats de mécanisme, mesurés au fil de l'étude sur les hôtes de chaque étape ; chacun isole une cause. Leurs
sources sont dans l'archive ([`docs/HISTORY.md`](docs/HISTORY.md)).

1. **Les données d'abord.** Une particule de 64 octets en occupe 64 dans 15 langages, 78 en Java, 88 en C#, 128 en
   BQN, 144 en OCaml, 352 en PHP, 416 en JavaScript et 750 en Python. Parcourir une collection de références dans le
   désordre coûte 4,7 à 7,0 fois plus (C#, Java, JavaScript, OCaml) ; avec des types valeur, l'ordre ne change rien.
2. **Le SIMD explicite** divise le produit scalaire par 20 à 40 : 3,7 à 5,7 ms dans les langages compilés, en C# et en
   Java, contre 77 à 166 ms pour la boucle naturelle en ordre strict. OCaml, JavaScript, BQN et PHP n'en ont pas.
3. **La vectorisation automatique se vérifie sur le code exécuté.** Aucune des deux boucles naturelles testées n'est
   vectorisée en C#, Go, Mojo, Zig 0.17 (vectoriseur de boucles désactivé), Swift, Haskell, OCaml, JavaScript, PHP, Lua
   et Python. Sur le stencil naturel, les vérifications de bornes l'empêchent en Ada, l'aliasing en D et en Rust, les
   deux en Nim ; en Swift, `-O` garde sur K4 un test de débordement par addition.
4. **Le compilateur pèse autant que le langage.** Sur le même code C, GCC est 2,2 à 2,7 fois plus rapide que clang sur
   l'arène de K8 construite par récursion ; écrite par itération, elle va plus vite sous clang.
5. **Le placement du code aussi.** Sur Emerald Rapids, la boucle de l'écrivain unique (K3) coûte 1 ou 7 cycles par
   incrément selon son alignement : huit dispositions tirées au hasard par l'éditeur de liens donnent 12 à 23 ms ou 74
   à 117 ms pour le même source.
6. **Concurrence.** Go, Haskell et OCaml n'ont que des écritures atomiques séquentiellement cohérentes : l'écrivain
   unique y est 6 à 7 fois plus lent qu'en C. JavaScript aussi, avec en plus un appel interne de V8 par opération.
   CPython sérialise ses threads par son verrou global ; BQN et PHP n'ont pas de threads. Réveiller des fils bloqués
   coûte plus qu'un calcul court : Q6 sur 2^16 lignes prend 10 à 15 µs à un fil, mais 65 µs à quatre fils en C et en
   C++ et 105 µs en Rust, contre 7,5 µs en Fortran, dont le runtime OpenMP attend activement.
7. **Allocation.** Une arène divise K8 par 5 ou 6. Les allocateurs générationnels de Java et d'OCaml sont les
   meilleurs pour du code naturel. Les ramasse-miettes laissent des queues : pause de 89 ms en D, p99,9 à 30 fois la
   médiane en Julia, arrêt de 0,76 s en Python.
8. **Le système compte.** Odin et Lua font un appel système à chaque lecture d'horloge ; sur K7, Rust, Zig et Odin
   rendent la mémoire de leur table au système à chaque répétition, et la paient en défauts de page.

## Comment c'est mesuré

La méthode complète est dans [`docs/METHOD.md`](docs/METHOD.md) ; le contrat des noyaux dans
[`docs/SPEC.md`](docs/SPEC.md).

| Noyau | Principe | Ce qui est mesuré | Tailles : petite, publiée, grande |
|---|---|---|---|
| K1 | Disposition des données | Énergie de particules de 64 octets, en AoS, en SoA, en objets, dans l'ordre et permuté | 2^14, 2^22, 2^24 particules (1 Mio, 256 Mio, 1 Gio) |
| K2 | Hiérarchie mémoire | Chasse de pointeurs | 16 Kio, 256 Kio et 8 Mio, les trois tailles du score |
| K3 | Faux partage, écrivain unique | 4 threads, compteurs voisins ou espacés | une (sans données) |
| K4 | Prédiction de branchement | Somme conditionnelle d'octets, triés ou non, avec ou sans branchement | 1, 16, 256 Mio |
| K5 | SIMD | Produit scalaire, 2^27 produits à chaque taille | 16 Kio (L1, la publiée), 256 Kio (L2), 16 Mio (L3) |
| K6 | Requêtes OLAP colonnaires | TPC-H Q6 et Q1 simplifiées, 1 et 4 threads | 2^16, 2^24, 2^26 lignes |
| K7 | Agrégation par hachage | GROUP BY, 16 lignes par clé | 2^16, 2^24, 2^27 lignes |
| K8 | Allocation, latence de queue | 16 384 requêtes qui construisent et parcourent un arbre | profondeur 16 et 8, 20 et 10, 23 et 12 |
| K9 | Stencil (HPC) | Jacobi 2D, 1 et 4 threads | 256², 2 048², 8 192² (1 Mio, 64 Mio, 1 Gio) |

Un dixième noyau (file SPSC), hors score depuis la v2, n'est plus mesuré.

* **Des formes par noyau et par langage** : `natural`, le code idiomatique ([`docs/NATURAL.md`](docs/NATURAL.md)),
  `tuned`, la version optimisée, et les formes d'un catalogue commun, portées dans chaque langage qui le permet, avec
  la seule bibliothèque standard : le plafond prend la meilleure forme admise. Toutes rendent, à chaque taille, le
  résultat de l'implémentation C, au bit près pour les entiers.
* **Des conditions égales** : le code naturel est compilé avec les vérifications à l'exécution que sa chaîne offre ; le
  stencil naturel est en grille contiguë pour tous ; aucune forme n'est en assembleur en ligne ; K3 est rapporté à une
  boucle de référence, prise à son plus mauvais placement et mesurée sur la machine juste avant et juste après chaque
  groupe de K3.
* **Chaînes de compilation** : les dernières versions stables au 28 octobre 2026 (Swift, FreePascal, BQN et PHP
  ajoutés du 5 au 7 novembre : [`env/toolchains.txt`](env/toolchains.txt)), compilation pour le CPU hôte, ni PGO ni
  LTO ; chaque binaire est construit depuis les fichiers suivis par git, et son empreinte enregistrée.
* **Une machine** : une VM Firecracker à 4 vCPU sur un Xeon Emerald Rapids, caractérisée au repos
  ([`results/hw/machine35`](results/hw/machine35)) ; trois passes dont l'ordre est tiré au hasard, 9 738 processus, du
  22 novembre, 17 h 16, au 23 novembre, 19 h 40 (UTC). Pas de compteurs matériels.
* **Score** : contrôle (35 %), 34 capacités notées 0, ½ ou 1 ; plafond (40 %), pour chacune des douze mesures, à chaque
  taille, le meilleur temps du langage rapporté au meilleur des 25, puis la moyenne géométrique (les trois mesures à
  quatre fils ne comptent qu'aux tailles publiée et grande) ; code par défaut (25 %), la variante naturelle rapportée
  au meilleur code naturel (50 %), l'empreinte et la pénalité de désordre d'une collection naturelle (15 %), la latence
  de queue de l'allocation (15 %), la chaîne de pointeurs (20 %).
* **Incertitude** : 2 000 rééchantillonnages des processus pour le bruit de mesure ; 20 000 variantes de l'analyse.
* **Garde-fous** : chaque étape a eu son plan, poussé avant ses mesures ou ses calculs ; les écarts sont datés
  ([`docs/V4_FINAL.md`](docs/V4_FINAL.md), 11 et 12.5 ; [`docs/V4_1.md`](docs/V4_1.md), 7) ; le calcul se reproduit à
  l'octet près (`tools/check.sh`).

## Limites

* **Une machine, dont la vitesse varie.** Un seul processeur Intel, virtualisé et partagé ; ni AMD, ni ARM, ni
  compteurs matériels, ni second hôte. La médiane par processus, trois processus par cellule (sept pour K2 et les
  latences de K8), l'ordre tiré au hasard et le rééchantillonnage en tiennent compte, sans le corriger.
* **Six cellules hors mémoire** à la grande taille (BQN, Python), remplies par le temps le plus lent des autres
  langages. La grande taille est bornée par la mémoire de la machine : 1 Gio de données au plus.
* **Des corrections décidées après coup.** Les quatre corrections du 24 novembre ont été trouvées en relisant les
  résultats publiés, et leur effet estimé avant d'en écrire le plan : ce plan n'est pas aveugle, à la différence de
  ceux des mesures. Le rapport garde le calcul sans elles et l'effet de chacune.
* **Un seul auteur.** Les implémentations ont été relues après coup, langage par langage, et ces relectures ont corrigé
  des erreurs du banc et de la grille. Le catalogue commun réduit l'écart d'effort sur le plafond ; il ne touche pas le
  code naturel, dont le choix reste celui de l'auteur ([`docs/NATURAL.md`](docs/NATURAL.md)).
* **Des microbenchmarks** : ni E/S, ni décompression, ni tri ou jointure.
* **Bibliothèque standard seule.** La règle pèse sur Rust (ni affinité, ni `mmap`, ni taille de ligne de cache sans
  crate), sur Haskell (`vector` et `unordered-containers` sont des paquets), sur Mojo (`parallelize` est dans MAX) et
  sur Python (NumPy est tiers ; le classement mesure CPython dans son build par défaut).
* **Le contrôle est jugé par un seul évaluateur.** Ses 850 cases reposent toutes sur une sonde exécutée (825) ou une
  mesure (25) ; 161 ne sont prouvées que par une recherche d'absence, qui ne voit que ce que son motif décrit.
* **Les vérifications ne sont égalisées qu'en politique** : C ne vérifie que les tableaux de taille connue, C++ les
  conteneurs de libstdc++, et l'accès par pointeur reste sans vérification.
* **Une version et un compilateur par langage** : Fortran est classé avec gfortran, C avec clang, C++ avec g++ 16 (le
  seul à livrer `std::simd`). Un réglage temporaire d'une chaîne peut coûter des rangs : Zig 0.17 désactive le
  vectoriseur de boucles de LLVM, que sa version de développement réactive.
* **JIT** : trois échauffements au moins, et au moins une seconde ; les boucles chaudes tournent souvent en code OSR,
  sans atteindre le niveau d'optimisation final.
* **Réglages des runtimes par défaut**, sauf le nombre de fils, fixé à quatre (`-t 4` pour Julia, `+RTS -N4` pour
  Haskell) : leur ramasse-miettes y devient parallèle, même pour les noyaux séquentiels.

## À côté du classement

Trois résultats publiés à côté du classement, par décision de l'auteur de l'étude ; résumés et sources dans
[`docs/HISTORY.md`](docs/HISTORY.md).

* **Le coût d'accès au plafond.** La forme la plus rapide a 3,5 fois les lignes du code naturel (médiane des 25
  langages) ; Mojo et Odin atteignent le plafond au meilleur prix (huit cellules chacun, sans construction propre à
  x86).
* **Une piste ouverte aux bibliothèques tierces.** Mesurées, elles changent peu le plafond ; par la grille, Rust
  passerait 1er (huit cases comblées par des crates), 4e avec les seules bibliothèques nommées d'avance.
* **Une autre étude, un autre ordre.** Une étude voisine classe C 11e sur 18 langages communs ; la différence tient à
  sa règle du « standard », pas aux faits, sur lesquels les deux grilles s'accordent.

## Vérifier et reproduire

```bash
sh tools/check.sh --rapide
```

```bash
sh tools/check.sh
```

Le premier contrôle (30 s) vérifie la grille contre ses sondes, le relevé des formes, le plan de la campagne et le
classement sur 200 variantes ; le second (25 min) recalcule le classement complet et le compare à l'octet près. Ni l'un
ni l'autre ne demande de chaîne de compilation.

```bash
python3 analysis/final_v4.py
```

```bash
python3 analysis/charts_final.py
```

Ces deux commandes réécrivent `results/final/analysis.json`, `results/report_final.md` et le graphique. Remesurer
demande les 25 chaînes de [`env/toolchains.txt`](env/toolchains.txt), que `env/install.sh` installe en 1 h 30 environ,
et une machine du même modèle : [`docs/METHOD.md`](docs/METHOD.md), 11.

## Le dépôt

| Répertoire | Contenu |
|---|---|
| `bench/<langage>/` | l'implémentation publiée de chaque langage, son `build.sh` et son `run` |
| `bench/<langage>_cv/` | la même, avec les formes du catalogue en plus (`cv_variants`) |
| `probes/<langage>/` | les sondes de la grille de contrôle |
| `tools/` | `final/` (constructions, campagne), `sizes/` (tailles, sommes attendues), `driver.py` (essai d'une implémentation), `gendata.c` (données), `hwprobe.c` (caractérisation), `grid_audit/` (recherches d'absence), `check.sh` (garde-fou) |
| `analysis/` | `final_v4.py` (le classement), `capabilities*.py` (la grille), `check_probes.py`, `charts_final.py` |
| `results/` | `final/` (mesures brutes, étalonnage, analyse), `report_final.md`, `probes/` et `grid_audit/` (preuves de la grille), `hw/machine35/`, `converge/` (relevé des formes) |
| `docs/` | `METHOD.md` (la méthode), `SPEC.md` (les noyaux), `NATURAL.md` (le code naturel), `CAPABILITIES.md` (la grille), `V4_FINAL.md` (plan et procès-verbal de la campagne), `V4_1.md` (corrections de l'analyse), `HISTORY.md` (étapes et archive) |

Tout ce qui a précédé (v1 à v3, relectures par langage, points 2 à 6 de la v4, ancien README) est dans l'archive, le
commit `5fbe6a6` : [`docs/HISTORY.md`](docs/HISTORY.md).
