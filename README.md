# Quels langages incarnent le mieux la *mechanical sympathy* ?

*Classement mesuré de 25 langages, octobre et novembre 2026. Tous sont mesurés sur une même machine, sept noyaux à
trois tailles de données, dans des conditions égales et avec un code optimisé convergent (campagne des 25 et 26
novembre, analyse v5.2 ; elle rejoue sur un autre processeur celle des 22 et 23 novembre : même tête, mêmes étages et,
à méthode égale, quelques échanges entre langages que moins d'un point sépare). Zig est classé, par exception, avec sa
version de développement, remesurée à part : l'astérisque. Méthode : [`docs/METHOD.md`](docs/METHOD.md) ; campagne :
[`docs/V5.md`](docs/V5.md) ; corrections de l'analyse : [`docs/V5_1.md`](docs/V5_1.md) ; exception de Zig :
[`docs/V5_2.md`](docs/V5_2.md) ; étapes précédentes et archive : [`docs/HISTORY.md`](docs/HISTORY.md).*

Un seul critère : la *mechanical sympathy* au sens large, c'est-à-dire la capacité d'un langage à faire écrire du code
en accord avec le matériel : disposition des données, SIMD, hiérarchie mémoire, concurrence, allocation, requêtes
analytiques. C'est ce qu'exigent le HPC, les moteurs OLAP et le Data-Oriented Design. Le plafond et le code par défaut
sont mesurés sur un Xeon Granite Rapids ; le pilier « contrôle » est un inventaire jugé.

## Le classement

| Rang | Étage | Langage | Score | Rang plausible | Devance le suivant | Sans la grille | Ce qui le place là |
|---|---|---|---|---|---|---|---|
| 1 | 1 | **C** | 83,2 | 1–4 | 68 % | 2 (1–8) | Le meilleur code par défaut et le meilleur code naturel (3e sans les vérifications), le contrôle de GNU C (2e) et le 5e plafond (1er sur K4) ; son K8 le plus rapide sous clang, une arène écrite par itération, reste à 0,68 de la frontière |
| 2 | 1 | **C++** | 81,5 | 1–7 | 71 % | 5 (1–10) | Le plus de contrôle (`pmr`, atomiques, `std::simd` expérimental) et le 1er plafond (87,5 ; Chapel 86,5, Rust 86,4) : son arène de K8 par valeur fait la frontière de K8 aux trois tailles, et il a les meilleurs K6 et K9 ; code naturel 9e |
| 3 | 1 | **Zig\*** | 79,6 | 1–9 | 67 % | 6 (1–10) | Classé avec sa version de développement, dont le vectoriseur de boucles divise par quatre le temps de la somme conditionnelle naturelle. 3e contrôle (tous les leviers du DOD), plafond 8e ; code naturel 39,5 avec les vérifications de `-O safe`, qui bloquent toujours le vectoriseur de sa somme conditionnelle, et 69,3 en mode publié. Avec la 0.17 : 5e (77,7) |
| 4 | 1 | **Odin** | 78,5 | 2–9 | 53 % | 7 (3–10) | À égalité de fait avec Rust. Le Data-Oriented Design dans le langage (`#soa`, `#simd`, intrinsèques de LLVM, allocateurs) : 5e contrôle, 4e code naturel ; plafond 9e (K4 66, K1 67) |
| 5 | 1 | **Rust** | 78,0 | 2–9 | 62 % | 1 (1–5) | Le 2e code par défaut (2e code naturel, queues de latence de K8 courtes) et le 3e plafond ; contrôle 9e (ni affinité, ni `mmap` dans la bibliothèque standard) |
| 6 | 1 | **Nim** | 77,3 | 3–9 | 61 % | 3 (1–8) | Le meilleur K1 (92), 7e plafond, 3e code par défaut, et le meilleur code naturel sans les vérifications ; contrôle 7e (les leviers de C par sa compilation vers C) |
| 7 | 1 | **C3** | 76,6 | 3–10 | 50 % | 4 (2–9) | À égalité de fait avec D. C avec vecteurs natifs : 6e plafond ; code naturel 6e avec les vérifications, 3e en mode publié ; contrôle 8e (ni SoA ni intrinsèques officiels) ; 4e à trois tailles sans les autres règles de la v4 |
| 8 | 1 | **D** | 76,4 | 3–12 | 76 % | 11 (5–14) | 4e plafond et 4e contrôle (le contrôle de C, templates et CTFE), mais les pauses de son ramasse-miettes font les pires queues de latence de K8 des 19 premiers (D3 : 2 sur 100) |
| 9 | 1 | **Ada** | 73,8 | 5–12 | 65 % | 12 (6–14) | Disposition au bit près : 6e contrôle, 10e plafond ; code naturel 11e avec les vérifications par défaut de GNAT (37,4), 10e sans (54,9) : sur K7, la protection de ses conteneurs multiplie le temps par cinq |
| 10 | 1 | **Julia** | 72,3 | 7–13 | 58 % | 10 (7–13) | 3e code naturel et 13e plafond ; les pauses du ramasse-miettes pèsent sur K8 (D3 7) |
| 11 | 1 | **Fortran** | 71,7 | 6–14 | 55 % | 9 (2–12) | Les queues de latence de K8 les plus courtes, 4e code par défaut, 12e plafond ; ni SIMD explicite ni intrinsèques (K4 47, forme SWAR) : contrôle 14e |
| 12 | 1 | **Chapel** | 70,8 | 6–14 | 71 % | 8 (2–12) | Le 2e plafond (K9 91, K8 88, K4 82) ; code naturel 16e avec les vérifications (`--checks`), 11e en mode publié ; contrôle 16e (leviers bas niveau rares ou instables) |
| 13 | 1 | **Mojo** | 68,2 | 10–14 | 58 % | 14 (11–14) | Le SIMD au cœur du langage (K5 86, K7 88) ; ni vectoriseur de boucles (K4 51) ni threads publics dans `std` ; K8 49 |
| 14 | 1 | **Swift** | 67,6 | 11–14 | 95 % | 13 (10–14) | Types SIMD et `InlineArray` : le meilleur K5 (97) ; vérifications de `-O` coûteuses sur le code naturel (14e) et le K4 le plus lent des 14 premiers (45) ; contrôle 13e |
| 15 | 1 | **C#** | 61,2 | 14–16 | 96 % | 15 (15–17) | La boîte à outils la plus riche des langages à GC : 15e plafond (K4 optimisé, réserves de fils) ; objets en références (K7 51, K8 51, désordre de K1) |
| 16 | 1 | **Java** | 52,6 | 16–18 | 61 % | 16 (15–17) | Les queues de latence de K8 les plus courtes des langages à ramasse-miettes (D3 43) et la Vector API (K5 81) ; pas de types valeur (K1 44, désordre de K1) ; contrôle 18e |
| 17 | 1 | **Go** | 51,6 | 16–18 | 49 % | 17 (16–18) | À égalité de fait avec FreePascal. Structures par valeur et SIMD expérimental (K4 73) ; écritures atomiques séquentiellement cohérentes (K3 37) ; code naturel 17e |
| 18 | 1 | **FreePascal** | 51,5 | 15–19 | 83 % | 19 (15–19) | Records `packed`, assembleur, mémoire à la main : 15e contrôle ; ni vectoriseur ni intrinsèques : 19e plafond (K4 11, K5 38) et code naturel 21e |
| 19 | 1 | **Haskell** | 45,7 | 18–19 | 100 % | 18 (18–19) | Peut descendre bas (FMA vectorielle de GHC : K5 86 ; le meilleur K7, 95) ; code par défaut boxé, ramasse-miettes imposé : code par défaut 19e, contrôle 19e |
| 20 | 2 | **OCaml** | 27,9 | 20–21 | 94 % | 20 (20–21) | Bonne allocation générationnelle (D3 36) ; ni types valeur, ni flottant 32 bits de calcul, ni SIMD : plafond 23,2 |
| 21 | 2 | **BQN** | 20,3 | 21–23 | 53 % | 22 (20–22) | À égalité de fait avec JavaScript. Primitives vectorisées de CBQN, mais un coût fixe par appel ; ni threads, ni flottant 32 bits ; K1 hors mémoire à la grande taille |
| 22 | 2 | **JavaScript** | 19,7 | 21–24 | 62 % | 21 (21–23) | Tableaux typés compilés mais vérifiés, aucun SIMD : plafond 15,8 ; contrôle 24e |
| 23 | 2 | **PHP** | 18,8 | 21–23 | 97 % | 23 (22–23) | Chaque valeur un zval de 16 octets, chaque objet une référence : plafond 23e ; le contrôle d'un langage dynamique doté d'une FFI et de processus (21e) |
| 24 | 2 | **Python** | 10,7 | 22–25 | 73 % | 25 (25–25) | CPython seul : le plafond le plus bas (1,1), K1 naturel hors mémoire à la grande taille ; contrôle 20e (`ctypes`, sous-interpréteurs) |
| 25 | 2 | **Lua** | 7,6 | 24–25 | — | 24 (24–24) | PUC-Lua sans son API C : presque aucun levier (contrôle 6,8) ; plafond 1,5, au-dessus de CPython |

* **\* Zig** est classé, par exception, avec sa version de développement (0.18.0-dev.1298, du 25 novembre) et non avec
  sa dernière version stable comme les 24 autres : la 0.17 désactive le vectoriseur de boucles de LLVM. Avec la 0.17,
  il serait 5e (77,7). Mesure et limites : [l'exception de Zig](#lexception-de-zig).
* **Score** (0–100) : 40 % de plafond mesuré (le meilleur code que le langage permet d'écrire pour la machine), 25 % de
  code par défaut mesuré (le code qu'on écrit sans y penser) et 35 % de contrôle (les leviers qu'offrent le langage et
  sa chaîne de compilation). Le score affiché est sa moyenne sur 20 000 variantes de l'analyse, qui tirent au hasard
  les poids des piliers et des tailles autour de ces valeurs, les normalisations, le mode de compilation du code
  naturel (trois politiques de vérifications), le jugement porté sur chaque capacité et le bruit de mesure. **Il fixe
  l'ordre.**
* **Rang plausible** : le rang dans 90 % des variantes. **Devance le suivant** : la part des variantes où le langage
  passe devant celui de la ligne suivante. Autour de 50 %, les deux langages sont à égalité de fait : Odin et Rust
  (53 %), C3 et D (50 %), Go et FreePascal (49 %), BQN et JavaScript (53 %).
* **Sans la grille** : la place du langage, et son rang plausible, quand le poids du contrôle est mis à 0 dans toutes
  les variantes. C'est le classement sur les seules mesures ; le contrôle, lui, est jugé.
* **Étages** : les 19 premiers (de C à Haskell) et les six derniers (d'OCaml à Lua). Une marche sépare deux étages
  quand chaque langage au-dessus devance chaque langage au-dessous dans au moins 95 % des variantes : 99,7 % après
  Haskell. Plus haut, les marches restent sous ce seuil : les 14 premiers devancent C# dans au moins 94,6 % des
  variantes, C# devance les quatre suivants dans au moins 92,1 %.
* **Cellules hors mémoire** : à la grande taille, les quatre variantes de K1 de BQN et K1 naturel de Python dépassent
  la mémoire de la machine ; elles prennent le temps admissible le plus lent des autres langages, ce qui les flatte
  sans doute.

![Classement de la v5.2](results/charts/classement_v4.svg)

### Les mesures et la grille, séparément

Le plafond et le code naturel sont mesurés ; le contrôle est une grille jugée de 34 capacités, dont chaque case repose
sur une sonde exécutée ou une mesure ([`docs/CAPABILITIES.md`](docs/CAPABILITIES.md)). Le tableau les donne séparément,
sur 100, avec les poids et les choix de méthode principaux. Le code naturel, rapporté au meilleur code naturel, est
donné dans ses trois modes : compilé avec toutes les vérifications à l'exécution que la chaîne offre, dans le mode de
publication de la chaîne, ou sans les vérifications qu'une option de la chaîne retire ; un tiers des variantes prend
chacun.

| Rang | Langage | Plafond (rang) | Code naturel, avec les vérifications (rang) | Code naturel, mode publié (rang) | Code naturel, sans les vérifications (rang) | Contrôle (rang) |
|---|---|---|---|---|---|---|
| 1 | C | 84,4 (5) | 69,8 (1) | 71,2 (1) | 66,5 (3) | 91,7 (2) |
| 2 | C++ | 87,5 (1) | 48,1 (9) | 57,1 (10) | 53,3 (11) | 92,4 (1) |
| 3 | Zig\* | 83,1 (8) | 39,5 (10) | 69,3 (2) | 64,8 (5) | 87,2 (3) |
| 4 | Odin | 81,6 (9) | 64,0 (4) | 64,8 (6) | 66,8 (2) | 84,0 (5) |
| 5 | Rust | 86,4 (3) | 65,7 (2) | 66,6 (4) | 62,2 (7) | 73,6 (9) |
| 6 | Nim | 83,3 (7) | 63,6 (5) | 64,5 (8) | 67,1 (1) | 76,1 (7) |
| 7 | C3 | 84,0 (6) | 61,3 (6) | 68,4 (3) | 63,9 (6) | 75,7 (8) |
| 8 | D | 85,4 (4) | 57,6 (7) | 59,9 (9) | 56,7 (9) | 87,1 (4) |
| 9 | Ada | 81,4 (10) | 37,4 (11) | 37,9 (12) | 54,9 (10) | 80,6 (6) |
| 10 | Julia | 77,8 (13) | 65,1 (3) | 66,0 (5) | 65,0 (4) | 73,3 (10) |
| 11 | Fortran | 78,3 (12) | 56,0 (8) | 64,8 (7) | 60,5 (8) | 65,3 (14) |
| 12 | Chapel | 86,5 (2) | 25,7 (16) | 56,8 (11) | 53,1 (12) | 61,8 (16) |
| 13 | Mojo | 75,7 (14) | 33,6 (13) | 34,0 (14) | 43,7 (13) | 70,5 (11) |
| 14 | Swift | 79,5 (11) | 32,2 (14) | 32,7 (15) | 41,9 (14) | 68,1 (13) |
| 15 | C# | 69,8 (15) | 28,7 (15) | 29,1 (16) | 27,2 (16) | 68,8 (12) |
| 16 | Java | 65,2 (16) | 34,0 (12) | 34,5 (13) | 32,2 (15) | 42,7 (18) |
| 17 | Go | 62,4 (17) | 22,1 (17) | 22,3 (17) | 23,3 (17) | 48,7 (17) |
| 18 | FreePascal | 42,2 (19) | 13,7 (21) | 20,4 (19) | 19,0 (19) | 62,3 (15) |
| 19 | Haskell | 54,1 (18) | 16,8 (19) | 17,0 (20) | 15,9 (20) | 41,5 (19) |
| 20 | OCaml | 23,2 (20) | 20,6 (18) | 20,9 (18) | 21,8 (18) | 23,2 (22) |
| 21 | BQN | 9,9 (22) | 16,5 (20) | 16,7 (21) | 15,6 (21) | 19,7 (23) |
| 22 | JavaScript | 15,8 (21) | 12,9 (22) | 13,1 (22) | 12,2 (22) | 14,6 (24) |
| 23 | PHP | 6,8 (23) | 6,0 (23) | 6,1 (23) | 5,7 (23) | 27,4 (21) |
| 24 | Python | 1,1 (25) | 1,3 (25) | 1,3 (25) | 1,3 (25) | 29,7 (20) |
| 25 | Lua | 1,5 (24) | 3,0 (24) | 3,0 (24) | 2,8 (24) | 6,8 (25) |

Sans la grille (colonne du premier tableau ; [`results/report_final.md`](results/report_final.md)), les étages se
séparent davantage : les 14 premiers (de Rust à Mojo), puis C#, Java, Go, Haskell et FreePascal, puis OCaml,
JavaScript, BQN et PHP, puis Lua et Python, chacun seul. Rust y prend la tête : il a le meilleur score (81,7 contre
81,1 pour C) et il est premier le plus souvent (38 % des variantes ; C 29 %, C++ 10 %). Le contrôle porte C++ (2e au
lieu de 5e), Zig (3e au lieu de 6e), Odin (4e au lieu de 7e), D (8e au lieu de 11e) et Ada (9e au lieu de 12e) ; il
retient Rust (5e au lieu de 1er), Nim (6e au lieu de 3e), C3 (7e au lieu de 4e), Fortran (11e au lieu de 9e) et Chapel
(12e au lieu de 8e). Sur le plafond seul, la tête serait C++, Chapel, Rust, D, C, C3, à moins de quatre points les uns
des autres.

### Ce qui est sûr, et ce qui ne l'est pas

* **Les grandes marches sont établies.** Les 19 premiers devancent les six derniers dans au moins 99,7 % des variantes.
  Plus haut, Swift devance C# dans 95 % des variantes, C# devance Java dans 96 % et Java devance Haskell dans 95 %.
* **C est premier, sans que ce soit un fait établi.** C est premier dans 56 % des variantes, C++ dans 27 %, Zig dans
  8 %, Rust dans 4 % ; C devance C++ dans 68 % des variantes, et chacun des deux devance chacun des 23 autres dans au
  moins 70,9 %. Zig devance Odin dans 67 % des variantes ; d'Odin à D, un langage ne devance le suivant que dans 50 à
  62 % : l'ordre de ces cinq-là est la meilleure estimation, rien de plus.
* **Le classement se répète.** Rejouée sur une autre machine et un autre modèle de processeur, la campagne redonne la
  même tête et les mêmes étages ; à méthode et à compilateurs égaux, seuls s'échangent des langages que moins d'un
  point sépare (section suivante).
* **La tête dépend des règles.** C est 1er dans huit des douze sensibilités ; C++ passe devant à la seule taille
  publiée, à la seule grande taille et si K3 n'est pas rapporté à la boucle de référence, Rust sur les seules mesures.
  Peu de langages y bougent de plus de deux places : à trois tailles sans les autres règles de la v4, C3 est 4e, Odin
  7e, Nim 9e et Julia 13e ; sans la boucle de référence de K3, C3 est 4e, D 5e, Zig 6e et Odin 7e ; à la seule petite
  taille, Chapel est 9e et Ada 12e.
* **Le contrôle pèse lourd, et il est jugé.** Sans lui, Rust passe 1er, C++ 5e, et neuf langages bougent de trois
  places ou plus : Rust, Nim, C3 et Chapel montent, C++, Zig, Odin, D et Ada reculent.

### D'une campagne à l'autre

Jusqu'au 26 novembre, le classement publié venait de la campagne des 22 et 23 novembre, mesurée sur un Xeon Emerald
Rapids (machine 35). Celle des 25 et 26 novembre la rejoue en entier sur un Xeon Granite Rapids (machine 38), avec les
25 chaînes réinstallées par `env/install.sh` et une seule source par langage ; les cellules de C y sont aussi mesurées
avec gcc. Plan, écarts et résultats : [`docs/V5.md`](docs/V5.md). Les deux campagnes sont comparées à compilateurs
égaux : Zig y est pris en 0.17, comme il a été mesuré dans chacune (calcul « Zig 0.17 » du rapport).

* **La même tête et les mêmes étages.** Contre le classement publié de la machine 35, deux paires s'échangent : Zig et
  D (5e et 8e), Mojo et Swift (13e et 14e) ; les 21 autres langages gardent leur place. C était premier dans 69 % des
  variantes ; il l'est dans 59 %.
* **À méthode égale**, l'ancienne campagne recalculée avec les corrections ci-dessous, les cinq premiers et les étages
  sont les mêmes. De la 6e à la 8e place, trois langages que moins d'un point sépare dans chaque campagne changent
  d'ordre (D, Nim, C3 sur l'ancienne ; Nim, C3, D sur la nouvelle), comme Mojo et Swift, BQN et JavaScript. Les scores
  des deux campagnes diffèrent de 0,6 point en moyenne, de 1,65 au plus (Haskell).
* **Les temps changent, leurs rapports beaucoup moins.** Une cellule prend 15 % de temps en moins, en médiane, sur la
  nouvelle machine, et deux cellules sur trois sont à moins de 10 % de ce rapport (2 972 cellules communes). Les
  plafonds bougent plus que l'ordre : celui de C perd 5 points (son K7 passe de 97 à 81), celui de Haskell en gagne 2.
* **C compilé par gcc reste premier.** Score 82,9 au lieu de 83,2 avec clang ; premier dans 55 % des variantes au lieu
  de 56 % ; devant C++ dans 73 % au lieu de 68 %. gcc donne à C un meilleur plafond (87,9 contre 84,4 : l'arène de K8
  passée par valeur y va deux fois plus vite) et, avec les vérifications, un moins bon code naturel (60,8 contre 69,8 :
  la somme conditionnelle de K4 y est 2,3 à 4,1 fois plus lente). L'écart de score entre C et C++ passe de 1,7 point à
  1,5 : le compilateur en fait un huitième.
* **Deux corrections de l'analyse, A5 et A6**, fixées le 25 novembre avant toute analyse des nouvelles mesures. L'écart
  de vitesse commun à tout un groupe de mesures d'une passe ne compte plus comme un bruit propre à chaque cellule ; le
  débit mémoire à quatre fils, borne physique dans une variante sur deux, était relevé plusieurs fois trop haut par une
  sonde qui chronométrait mal (153 Go/s au lieu de 43 sur la machine 38). A5 ne déplace aucun langage dans la nouvelle
  campagne ; sans A6, seuls Go et FreePascal, à égalité de fait, s'échangent, et A6 relève de 1,7 à 2 points les scores
  des quinze premiers. Les quatre corrections du 24 novembre restent en place ([`docs/V4_1.md`](docs/V4_1.md)) : sans
  aucune des huit corrections, C serait encore 1er ici, premier dans 40 % des variantes, quand la campagne précédente
  plaçait C++ devant lui de justesse.

### Le code naturel, avec ou sans vérifications

Le code naturel peut être compilé selon trois politiques défendables : avec toutes les vérifications à l'exécution que
la chaîne offre (la règle R1 de la v4), dans le mode de publication de chaque chaîne, ou sans les vérifications qu'une
option retire. Les mesures ne tranchent pas, et ce choix déplace Zig de trois places : 6e si tout est vérifié, 3e en
mode publié, 3e si rien ne l'est.

* **Trois vérifications font les plus grands écarts.**
  * **Zig, K4.** En `-O safe`, la somme conditionnelle est 42 fois plus lente qu'en `-O fast` (11 fois en 0.17, avant
    le retour du vectoriseur) ; ses autres mesures naturelles changent de 0,7 à 1,4 fois. Le test de débordement de
    chaque addition garde un branchement, mal prédit une fois sur deux, et empêche de vectoriser la boucle.
  * **Ada, K7.** L'agrégation par `Hashed_Maps` prend 383 ns par ligne avec les vérifications par défaut de GNAT et 71
    sans (`-gnatp`), au niveau de C++ et de Rust. Presque tout vient de la protection des conteneurs contre leur
    modification pendant un parcours : la retirer seule ramène le temps de 405 à 78 ns (essai hors campagne).
  * **Chapel, K9.** Le stencil est 13,5 fois plus lent avec `--checks` qu'en `--fast`, surtout par ses vérifications de
    bornes (essai hors campagne : 10,6 ms sans, 133 ms avec elles seules, 199 ms avec toutes) ; les deux requêtes de K6
    le sont 6,8 et 4,2 fois.
* **Aucune politique ne traite tous les langages de la même façon.** rustc a le même test que Zig (`-C
  overflow-checks=on`), que son mode de publication retire et que R1 n'active pas : essayé hors campagne, il rend la
  même somme 31 à 46 fois plus lente en Rust, avec le même code machine que Zig 0.17. Le mode publié, lui, garde les
  vérifications d'Ada, de Swift ou de Mojo quand il retire celles de Zig, de C3 ou de Chapel.
* **Le mode est donc tiré au sort** (corrections A7 et A8, 26 novembre) : chaque variante prend le code naturel dans
  l'une des trois politiques, une fois sur trois, comme pour les autres choix de méthode discutables. Si tout était
  vérifié (« Sans A7 » du rapport), Zig serait 6e au lieu de 3e, Odin 3e au lieu de 4e, Rust 4e au lieu de 5e, Nim 5e
  au lieu de 6e, C3 8e au lieu de 7e et D 7e au lieu de 8e, et les étages seraient trois. Un premier tirage, entre les
  deux premières politiques seulement (« Sans A8 »), comptait dans toutes les variantes les vérifications d'Ada, de
  Swift et de Mojo, et dans une sur deux celles de Zig : il donne les mêmes places, avec 1,1 point de moins pour Ada,
  aucun autre score ne bougeant de plus de 0,6 point. Plan et résultats : [`docs/V5_1.md`](docs/V5_1.md).

### L'exception de Zig

Zig est classé avec sa version de développement, 0.18.0-dev.1298 du 25 novembre 2026, et non avec sa dernière version
stable comme les 24 autres : décision de l'auteur de l'étude, que l'astérisque signale. La 0.17 livre LLVM avec son
vectoriseur de boucles coupé, réglage passager que la version de développement a retiré et que la 0.17.1 du 2 novembre
garde encore. Plan, mesures et résultats : [`docs/V5_2.md`](docs/V5_2.md).

* **Ce que le vectoriseur change.** La même source, sans retouche, rend les mêmes résultats avec les deux versions. En
  `-O fast`, la somme conditionnelle naturelle de K4 prend 0,24 à 0,35 fois son temps de la 0.17 selon la taille, le
  stencil naturel de K9 0,48 à 0,84 fois. En `-O safe`, K4 ne change pas : le test de débordement bloque toujours la
  vectorisation. Le plafond bouge peu, la meilleure forme de K4 étant déjà à SIMD explicite.
* **Comment c'est mesuré.** Zig n'est pas remesuré dans la campagne mais à part, sur la machine 39 : six passes, 1 554
  processus, chaque groupe mesurant ses cellules par les deux versions. La 0.17 y sert de témoin : chaque temps de Zig
  de la campagne est multiplié par le rapport, mesuré côte à côte, de la 0.18 à la 0.17. Ce rapport est rééchantillonné
  avec les mesures. Les latences de queue de Zig restent celles de la campagne : leurs rapports ne se distinguent pas
  du bruit, ce qui a été constaté après les mesures et s'écarte du plan ([`docs/V5_2.md`](docs/V5_2.md), 8).
* **Ce que ça donne.** Zig passe de la 5e à la 3e place, de 77,7 à 79,6 ; il devance Odin dans 67 % des variantes. Le
  gain vient du code naturel dans les deux modes sans `-O safe` (69,3 sur 100 en mode publié au lieu de 55,2). Avec le
  rapport appliqué à K4 et à K9 seulement, les deux noyaux dont le code machine change, Zig est 3e avec 79,5 : sa place
  ne tient pas au bruit des autres cellules.
* **Ce que ça ne règle pas.** Un seul langage profite d'une version de développement ; aucune autre chaîne n'a été
  essayée dans la sienne. Zig n'est pas mesuré dans les groupes des 24 autres, et une archive de développement ne se
  retrouve pas toujours : la remesure peut ne plus être reproductible à l'identique. La 0.18 n'est pas plus rapide
  partout : les formes qui créent leurs fils à chaque appel y sont jusqu'à 1,4 fois plus lentes aux petites tailles. La
  grille de contrôle reste celle de la 0.17, que les sondes rejouées sous la 0.18 confirment.

## Ce qui sépare vraiment les langages

Les constats de mécanisme, mesurés au fil de l'étude sur les hôtes de chaque étape ; chacun isole une cause. Leurs
sources sont dans l'archive ([`docs/HISTORY.md`](docs/HISTORY.md)).

1. **Les données d'abord.** Une particule de 64 octets en occupe 64 dans 15 langages, 78 en Java, 88 en C#, 128 en
   BQN, 144 en OCaml, 352 en PHP, 416 en JavaScript et 750 en Python. Parcourir une collection de références dans le
   désordre coûte 4,7 à 7,0 fois plus (C#, Java, JavaScript, OCaml) ; avec des types valeur, l'ordre ne change rien.
2. **Le SIMD explicite** divise le produit scalaire par 20 à 40 : 3,7 à 5,7 ms dans les langages compilés, en C# et en
   Java, contre 77 à 166 ms pour la boucle naturelle en ordre strict. OCaml, JavaScript, BQN et PHP n'en ont pas.
3. **La vectorisation automatique se vérifie sur le code exécuté.** Aucune des deux boucles naturelles testées n'est
   vectorisée en C#, Go, Mojo, Zig 0.17 (vectoriseur de boucles désactivé ; elles le sont sous sa version de
   développement), Swift, Haskell, OCaml, JavaScript, PHP, Lua et Python. Sur le stencil naturel, les vérifications de
   bornes l'empêchent en Ada, l'aliasing en D et en Rust, les deux en Nim ; en Swift, `-O` garde sur K4 un test de
   débordement par addition.
4. **Le compilateur pèse autant que le langage.** Sur le même code C, dans la campagne publiée : gcc est 1,9 à 2,9 fois
   plus rapide que clang sur l'arène de K8 construite par récursion, clang 1,1 à 1,3 fois plus rapide quand elle est
   écrite par itération ; la somme conditionnelle naturelle de K4 va 2,3 à 4,1 fois plus vite sous clang ; le produit
   scalaire naturel de K5 va deux fois plus vite sous gcc, parce que clang fond chaque produit et son addition en une
   FMA (quatre cycles par élément) quand gcc multiplie par vecteurs puis additionne dans l'ordre (deux cycles).
5. **Le placement du code aussi.** Sur Emerald Rapids, la boucle de l'écrivain unique (K3) coûte 1 ou 7 cycles par
   incrément selon son alignement : huit dispositions tirées au hasard par l'éditeur de liens donnent 12 à 23 ms ou 74
   à 117 ms pour le même source. Sur Granite Rapids, dans la campagne publiée, la boucle de C prend 65 ms compilée par
   clang et 10 ms par gcc.
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
* **Des conditions égales** : le code naturel est compilé selon une politique de vérifications tirée dans chaque
  variante parmi trois (toutes celles que la chaîne offre, le mode publié de la chaîne, aucune de celles qu'une option
  retire) ; le stencil naturel est en grille contiguë pour tous ; aucune forme n'est en assembleur en ligne ; K3 est
  rapporté à une boucle de référence, prise à son plus mauvais placement et mesurée sur la machine juste avant et
  juste après chaque groupe de K3.
* **Chaînes de compilation** : les dernières versions stables au 28 octobre 2026 (Swift, FreePascal, BQN et PHP
  ajoutés du 5 au 7 novembre : [`env/toolchains.txt`](env/toolchains.txt)), installées par `env/install.sh` ; Zig
  seul est classé avec sa version de développement (plus haut). Compilation pour le CPU hôte, ni PGO ni LTO ; chaque
  binaire est construit depuis les fichiers suivis par git, et son empreinte enregistrée.
* **Une machine** : une VM Firecracker à 4 vCPU sur un Xeon Granite Rapids, caractérisée au repos
  ([`results/hw/machine38`](results/hw/machine38)) ; trois passes dont l'ordre est tiré au hasard, 10 158 processus
  (dont 420 pour C par gcc), du 25 novembre, 6 h 12, au 26 novembre, 10 h 30 (UTC), sans redémarrage ni processus en
  échec. Pas de compteurs matériels. Zig sous sa version de développement est remesuré à part le 26 novembre, sur une
  machine du même modèle ([`results/zig_dev`](results/zig_dev)) : six passes, 1 554 processus, avec son témoin.
* **Score** : contrôle (35 %), 34 capacités notées 0, ½ ou 1 ; plafond (40 %), pour chacune des douze mesures, à chaque
  taille, le meilleur temps du langage rapporté au meilleur des 25, puis la moyenne géométrique (les trois mesures à
  quatre fils ne comptent qu'aux tailles publiée et grande) ; code par défaut (25 %), la variante naturelle rapportée
  au meilleur code naturel (50 %), l'empreinte et la pénalité de désordre d'une collection naturelle (15 %), la latence
  de queue de l'allocation (15 %), la chaîne de pointeurs (20 %).
* **Incertitude** : 2 000 rééchantillonnages des processus pour le bruit de mesure ; 20 000 variantes de l'analyse.
* **Garde-fous** : chaque étape a eu son plan, poussé avant ses mesures ou ses calculs ; les écarts sont datés
  ([`docs/V4_FINAL.md`](docs/V4_FINAL.md), 11 et 12.5 ; [`docs/V4_1.md`](docs/V4_1.md), 7 ;
  [`docs/V5.md`](docs/V5.md), 8 ; [`docs/V5_1.md`](docs/V5_1.md), 7 et 10 ; [`docs/V5_2.md`](docs/V5_2.md), 8) ; le
  calcul se reproduit à l'octet près (`tools/check.sh`).

## Limites

* **Des machines partagées, dont la vitesse varie.** Deux Xeon d'Intel, virtualisés et partagés ; ni AMD, ni ARM, ni
  compteurs matériels. Sur la machine publiée, le temps d'une cellule varie de 13 % en médiane entre sa passe la plus
  lente et sa plus rapide (8 % sur la précédente), et de 28 à 35 % pour K1, K4, K7 et K9 à la taille publiée, dont
  les données débordent des caches privés d'un cœur. La médiane par processus, trois processus par cellule (sept pour
  K2 et les latences de K8), l'ordre tiré au hasard et le rééchantillonnage en tiennent compte, sans le corriger.
* **Une campagne inachevée, non publiée.** La campagne a d'abord été relancée sur le modèle de processeur d'origine ;
  un premier redémarrage de la machine l'a fait changer d'hôte, un second l'a arrêtée à 61 %, la machine revenant sur
  un autre modèle. Elle n'entre dans aucun calcul ([`docs/V5.md`](docs/V5.md), 8 et 9).
* **Six cellules hors mémoire** à la grande taille (BQN, Python), remplies par le temps le plus lent des autres
  langages. La grande taille est bornée par la mémoire de la machine : 1 Gio de données au plus.
* **Des corrections décidées après coup.** Les quatre corrections du 24 novembre ont été trouvées en relisant les
  résultats publiés, et leur effet estimé avant d'en écrire le plan : ce plan n'est pas aveugle, à la différence de
  ceux des mesures. Les deux du 25 novembre ont été fixées avant toute analyse des nouvelles mesures, mais en
  connaissant celles de la campagne précédente. Les deux du 26 novembre répondent à une place qui surprenait dans le
  classement publié, puis à ce que la première laissait d'inégal ; leur effet était estimé avant d'en écrire le plan.
  Le rapport garde le calcul sans elles et l'effet de chacune.
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
  conteneurs de libstdc++, et l'accès par pointeur reste sans vérification ; Zig teste le débordement des entiers, Rust
  non, bien que son compilateur en ait l'option. Le tirage au sort du mode du code naturel répartit le poids de ces
  différences sans les supprimer : les vérifications qu'une option ajoute (Zig, Chapel) comptent dans une variante sur
  trois, celles que le mode publié garde et qu'une option retire (Ada, Swift, Mojo) dans deux sur trois.
* **Une version et un compilateur par langage** : Fortran est classé avec gfortran, C avec clang (avec gcc, il reste
  1er : plus haut), C++ avec g++ 16 (le seul à livrer `std::simd`). Un réglage temporaire d'une chaîne peut coûter des
  rangs : le vectoriseur de boucles coupé de Zig 0.17 lui coûtait deux places.
* **Une exception pour un langage.** Zig est classé avec une version de développement, les 24 autres avec leur
  dernière version stable, et aucune autre version de développement n'a été essayée. Ses temps ne viennent pas de la
  campagne : ils y sont ramenés par un témoin, à partir d'une remesure faite à part. Sa place vaut sous ces
  réserves ; avec la 0.17, il est 5e.
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

Le premier contrôle (45 s) vérifie la grille contre ses sondes, le relevé des formes, le plan de la campagne et le
classement sur 200 variantes ; le second (25 minutes environ) recalcule le classement complet et le compare à l'octet
près. Ni l'un ni l'autre ne demande de chaîne de compilation.

```bash
python3 analysis/final_v4.py
```

```bash
python3 analysis/charts_final.py
```

Ces deux commandes réécrivent `results/final/analysis.json`, `results/report_final.md` et le graphique. Remesurer
demande les 25 chaînes de [`env/toolchains.txt`](env/toolchains.txt), que `env/install.sh` installe en 1 h 30 environ,
et une machine à 4 cœurs et 15 Gio pendant un peu plus d'un jour (28 heures pour la campagne publiée) ; une campagne
s'écrit dans son propre répertoire et se mesure sur un seul modèle de processeur :
[`docs/METHOD.md`](docs/METHOD.md), 11.

## Le dépôt

| Répertoire | Contenu |
|---|---|
| `bench/<langage>/` | l'implémentation de chaque langage : variantes publiées et formes du catalogue (`cv_variants`), son `build.sh` et son `run` |
| `probes/<langage>/` | les sondes de la grille de contrôle |
| `tools/` | `final/` (constructions, campagne), `sizes/` (tailles, sommes attendues), `driver.py` (essai d'une implémentation), `gendata.c` (données), `hwprobe.c` (caractérisation), `grid_audit/` (recherches d'absence), `check.sh` (garde-fou) |
| `analysis/` | `final_v4.py` (le classement), `capabilities*.py` (la grille), `check_probes.py`, `charts_final.py` |
| `results/` | `final/` (mesures brutes, étalonnage, analyse), `zig_dev/` (remesure de Zig par sa version de développement, avec son témoin et la caractérisation de sa machine), `report_final.md`, `probes/` et `grid_audit/` (preuves de la grille), `hw/` (caractérisation de la machine 38 et de la machine 35, celle de la campagne précédente), `converge/` (relevé des formes) |
| `docs/` | `METHOD.md` (la méthode), `SPEC.md` (les noyaux), `NATURAL.md` (le code naturel), `CAPABILITIES.md` (la grille), `V5.md` (plan, écarts et résultats de la campagne publiée), `V5_1.md` (corrections A7 et A8 de l'analyse), `V5_2.md` (exception de Zig : plan, mesures et résultats), `V4_FINAL.md` (plan et procès-verbal de la campagne précédente), `V4_1.md` (corrections A1 à A4 de l'analyse), `HISTORY.md` (étapes et archive) |
| `env/` | `install.sh` (installe les 25 chaînes et la version de développement de Zig), `toolchains.txt` (leurs versions), `msdata.sha256` (empreintes des données) |

Tout ce qui a précédé (v1 à v3, relectures par langage, points 2 à 6 de la v4, ancien README) est dans l'archive, le
commit `5fbe6a6` ; les mesures de la campagne précédente et de la campagne inachevée, dans le commit `76d07af` :
[`docs/HISTORY.md`](docs/HISTORY.md).
