# Quels langages incarnent le mieux la *mechanical sympathy* ?

*Classement mesuré de 20 langages, octobre et novembre 2026. Tous sont mesurés sur une même machine, sept noyaux à
trois tailles de données, dans des conditions égales et avec un code optimisé convergent (campagne des 25 et 26
novembre, analyse v6 ; elle rejoue sur un autre processeur celle des 22 et 23 novembre : même tête, mêmes étages et, à
méthode égale, quelques échanges entre langages que moins d'un point sépare). Zig est classé, par exception, avec sa
version de développement, remesurée à part : l'astérisque. Une erreur de mesure sur Go, que le tri des écarts a
retrouvée, est corrigée par une remesure à part. Cinq langages mesurés dans la même campagne ont été retirés le 27
novembre. Méthode : [`docs/METHOD.md`](docs/METHOD.md) ; campagne : [`docs/V5.md`](docs/V5.md) ; corrections de
l'analyse : [`docs/V5_1.md`](docs/V5_1.md) ; exception de Zig : [`docs/V5_2.md`](docs/V5_2.md) ; ce qui décide de
l'ordre et tri des écarts : [`docs/V5_3.md`](docs/V5_3.md) ; correction de Go : [`docs/V5_4.md`](docs/V5_4.md) ;
retrait de cinq langages : [`docs/V6.md`](docs/V6.md) ; étapes précédentes et archive :
[`docs/HISTORY.md`](docs/HISTORY.md).*

Un seul critère : la *mechanical sympathy* au sens large, c'est-à-dire la capacité d'un langage à faire écrire du code
en accord avec le matériel : disposition des données, SIMD, hiérarchie mémoire, concurrence, allocation, requêtes
analytiques. C'est ce qu'exigent le HPC, les moteurs OLAP et le Data-Oriented Design. Le plafond et le code par défaut
sont mesurés sur un Xeon Granite Rapids ; le pilier « contrôle » est un inventaire jugé.

## Le classement

| Rang | Étage | Langage | Score | Rang plausible | Devance le suivant | Sans la grille | Ce qui le place là |
|---|---|---|---|---|---|---|---|
| 1 | 1 | **C** | 83,4 | 1–4 | 68 % | 2 (1–8) | Le meilleur code par défaut et le meilleur code naturel (3e sans les vérifications), le contrôle de GNU C (2e) et le 5e plafond (1er sur K4) ; son K8 le plus rapide sous clang, une arène écrite par itération, reste à 0,68 de la frontière |
| 2 | 1 | **C++** | 81,7 | 1–7 | 72 % | 5 (1–10) | Le plus de contrôle (`pmr`, atomiques, `std::simd` expérimental) et le 1er plafond (87,5 ; Chapel 86,5, Rust 86,4) : son arène de K8 par valeur fait la frontière de K8 aux trois tailles, et il a les meilleurs K6 et K9 ; code naturel 9e |
| 3 | 1 | **Zig\*** | 79,7 | 1–9 | 66 % | 6 (1–10) | Classé avec sa version de développement, dont le vectoriseur de boucles divise par quatre le temps de la somme conditionnelle naturelle. 3e contrôle (tous les leviers du DOD), plafond 8e ; code naturel 40,5 avec les vérifications de `-O safe`, qui bloquent toujours le vectoriseur de sa somme conditionnelle, et 71,0 en mode publié. Avec la 0.17 : 5e (77,9) |
| 4 | 1 | **Odin** | 78,7 | 2–8 | 53 % | 7 (3–10) | À égalité de fait avec Rust. Le Data-Oriented Design dans le langage (`#soa`, `#simd`, intrinsèques de LLVM, allocateurs) : 5e contrôle, 4e code naturel ; plafond 9e (K4 66, K1 67) |
| 5 | 1 | **Rust** | 78,2 | 2–9 | 63 % | 1 (1–5) | Le 2e code par défaut (2e code naturel, queues de latence de K8 courtes) et le 3e plafond ; contrôle 9e (ni affinité, ni `mmap` dans la bibliothèque standard) |
| 6 | 1 | **Nim** | 77,5 | 3–9 | 61 % | 3 (1–8) | Le meilleur K1 (92), 7e plafond, 3e code par défaut, et le meilleur code naturel sans les vérifications ; contrôle 7e (les leviers de C par sa compilation vers C) |
| 7 | 1 | **C3** | 76,8 | 3–10 | 50 % | 4 (2–9) | À égalité de fait avec D. C avec vecteurs natifs : 6e plafond ; code naturel 6e avec les vérifications, 3e en mode publié ; contrôle 8e (ni SoA ni intrinsèques officiels) ; 4e à trois tailles sans les autres règles de la v4 |
| 8 | 1 | **D** | 76,6 | 3–12 | 76 % | 10 (5–14) | 4e plafond et 4e contrôle (le contrôle de C, templates et CTFE), mais les pauses de son ramasse-miettes font les pires queues de latence de K8 du classement (D3 : 2 sur 100) |
| 9 | 1 | **Ada** | 74,0 | 5–12 | 66 % | 12 (6–14) | Disposition au bit près : 6e contrôle, 10e plafond ; code naturel 12e avec les vérifications par défaut de GNAT (38,3), 10e sans (54,9) : sur K7, la protection de ses conteneurs multiplie le temps par cinq |
| 10 | 1 | **Julia** | 72,4 | 7–13 | 57 % | 11 (7–13) | 3e code naturel et 13e plafond ; les pauses du ramasse-miettes pèsent sur K8 (D3 7) |
| 11 | 1 | **Fortran** | 71,8 | 6–14 | 55 % | 9 (2–12) | À égalité de fait avec Chapel. Les queues de latence de K8 les plus courtes, 4e code par défaut, 12e plafond ; ni SIMD explicite ni intrinsèques (K4 47, forme SWAR) : contrôle 14e |
| 12 | 1 | **Chapel** | 70,9 | 7–14 | 71 % | 8 (2–12) | Le 2e plafond (K9 91, K8 88, K4 82) ; code naturel 17e avec les vérifications (`--checks`), 11e en mode publié ; contrôle 16e (leviers bas niveau rares ou instables) |
| 13 | 1 | **Mojo** | 68,3 | 10–14 | 58 % | 14 (11–14) | Le SIMD au cœur du langage (K5 86, K7 88) ; ni vectoriseur de boucles (K4 51) ni threads publics dans `std` ; K8 49 |
| 14 | 1 | **Swift** | 67,7 | 11–14 | 96 % | 13 (10–14) | Types SIMD et `InlineArray` : le meilleur K5 (97) ; vérifications de `-O` coûteuses sur le code naturel (15e) et le K4 le plus lent des 14 premiers (45) ; contrôle 13e |
| 15 | 1 | **C#** | 61,2 | 14–17 | 86 % | 16 (15–18) | La boîte à outils la plus riche des langages à GC : 15e plafond (K4 optimisé, réserves de fils) ; objets en références (K7 51, K8 51, désordre de K1) |
| 16 | 1 | **Go** | 55,3 | 15–18 | 76 % | 15 (14–17) | Structures par valeur et SIMD expérimental (K4 73) ; écritures atomiques séquentiellement cohérentes (K3 37) ; code naturel 11e depuis qu'il est mesuré hors de l'expérience `simd` de sa chaîne, qui faussait son K1 ([la correction de Go](#la-correction-de-go)). Avec le binaire de la campagne : 17e (51,7) |
| 17 | 1 | **Java** | 52,6 | 16–18 | 57 % | 17 (15–17) | Les queues de latence de K8 les plus courtes des langages à ramasse-miettes (D3 43) et la Vector API (K5 81) ; pas de types valeur (K1 44, désordre de K1) ; contrôle 18e |
| 18 | 1 | **FreePascal** | 51,6 | 15–19 | 83 % | 19 (16–19) | Records `packed`, assembleur, mémoire à la main : 15e contrôle ; ni vectoriseur ni intrinsèques : 19e plafond (K4 11, K5 38) et le dernier code naturel avec les vérifications |
| 19 | 1 | **Haskell** | 45,7 | 18–19 | 100 % | 18 (18–19) | Peut descendre bas (FMA vectorielle de GHC : K5 86 ; le meilleur K7, 95) ; code par défaut boxé, ramasse-miettes imposé : code par défaut 19e, contrôle 19e |
| 20 | 2 | **OCaml** | 27,9 | 20–20 | — | 20 (20–20) | Bonne allocation générationnelle (D3 36) ; ni types valeur, ni flottant 32 bits de calcul, ni SIMD : le plafond le plus bas (23,2) |

* **\* Zig** est classé, par exception, avec sa version de développement (0.18.0-dev.1298, du 25 novembre) et non avec
  sa dernière version stable comme les 19 autres : la 0.17 désactive le vectoriseur de boucles de LLVM. Avec la 0.17,
  il serait 5e (77,9). Mesure et limites : [l'exception de Zig](#lexception-de-zig).
* **Score** (0–100) : 40 % de plafond mesuré (le meilleur code que le langage permet d'écrire pour la machine), 25 % de
  code par défaut mesuré (le code qu'on écrit sans y penser) et 35 % de contrôle (les leviers qu'offrent le langage et
  sa chaîne de compilation). Le score affiché est sa moyenne sur 20 000 variantes de l'analyse, qui tirent au hasard
  les poids des piliers et des tailles autour de ces valeurs, les normalisations, le mode de compilation du code
  naturel (trois politiques de vérifications), le jugement porté sur chaque capacité et le bruit de mesure. **Il fixe
  l'ordre.**
* **Rang plausible** : le rang dans 90 % des variantes. **Devance le suivant** : la part des variantes où le langage
  passe devant celui de la ligne suivante. Autour de 50 %, les deux langages sont à égalité de fait : Odin et Rust
  (53 %), C3 et D (50 %), Fortran et Chapel (55 %).
* **Sans la grille** : la place du langage, et son rang plausible, quand le poids du contrôle est mis à 0 dans toutes
  les variantes. C'est le classement sur les seules mesures ; le contrôle, lui, est jugé.
* **Étages** : les 19 premiers (de C à Haskell), puis OCaml, seul. Une marche sépare deux étages quand chaque langage
  au-dessus devance chaque langage au-dessous dans au moins 95 % des variantes : 99,8 % après Haskell. Plus haut, les
  marches restent sous ce seuil : les 14 premiers devancent C# dans au moins 94,9 % des variantes, C# devance les
  quatre suivants dans au moins 86,1 %.

![Classement de la v6](results/charts/classement_v4.svg)

### Les mesures et la grille, séparément

Le plafond et le code naturel sont mesurés ; le contrôle est une grille jugée de 34 capacités, dont chaque case repose
sur une sonde exécutée ou une mesure ([`docs/CAPABILITIES.md`](docs/CAPABILITIES.md)). Le tableau les donne séparément,
sur 100, avec les poids et les choix de méthode principaux. Le code naturel, rapporté au meilleur code naturel, est
donné dans ses trois modes : compilé avec toutes les vérifications à l'exécution que la chaîne offre, dans le mode de
publication de la chaîne, ou sans les vérifications qu'une option de la chaîne retire ; un tiers des variantes prend
chacun.

| Rang | Langage | Plafond (rang) | Code naturel, avec les vérifications (rang) | Code naturel, mode publié (rang) | Code naturel, sans les vérifications (rang) | Contrôle (rang) |
|---|---|---|---|---|---|---|
| 1 | C | 84,4 (5) | 71,5 (1) | 72,9 (1) | 66,5 (3) | 91,7 (2) |
| 2 | C++ | 87,5 (1) | 49,3 (9) | 58,5 (10) | 53,3 (11) | 92,4 (1) |
| 3 | Zig\* | 83,1 (8) | 40,5 (10) | 71,0 (2) | 64,8 (5) | 87,2 (3) |
| 4 | Odin | 81,6 (9) | 65,5 (4) | 66,4 (6) | 66,8 (2) | 84,0 (5) |
| 5 | Rust | 86,4 (3) | 67,3 (2) | 68,2 (4) | 62,2 (7) | 73,6 (9) |
| 6 | Nim | 83,3 (7) | 65,1 (5) | 66,1 (8) | 67,1 (1) | 76,1 (7) |
| 7 | C3 | 84,0 (6) | 62,8 (6) | 70,0 (3) | 63,9 (6) | 75,7 (8) |
| 8 | D | 85,4 (4) | 59,0 (7) | 61,4 (9) | 56,7 (9) | 87,1 (4) |
| 9 | Ada | 81,4 (10) | 38,3 (12) | 38,8 (13) | 54,9 (10) | 80,6 (6) |
| 10 | Julia | 77,8 (13) | 66,7 (3) | 67,6 (5) | 65,0 (4) | 73,3 (10) |
| 11 | Fortran | 78,3 (12) | 57,3 (8) | 66,4 (7) | 60,5 (8) | 65,3 (14) |
| 12 | Chapel | 86,5 (2) | 26,3 (17) | 58,2 (11) | 53,1 (12) | 61,8 (16) |
| 13 | Mojo | 75,7 (14) | 34,4 (14) | 34,9 (15) | 43,7 (13) | 70,5 (11) |
| 14 | Swift | 79,5 (11) | 33,0 (15) | 33,5 (16) | 41,9 (14) | 68,1 (13) |
| 15 | C# | 69,8 (15) | 29,4 (16) | 29,8 (17) | 27,2 (17) | 68,8 (12) |
| 16 | Go | 62,4 (17) | 39,9 (11) | 40,5 (12) | 41,9 (15) | 48,7 (17) |
| 17 | Java | 65,2 (16) | 34,9 (13) | 35,4 (14) | 32,2 (16) | 42,7 (18) |
| 18 | FreePascal | 42,2 (19) | 14,0 (20) | 20,9 (19) | 19,0 (19) | 62,3 (15) |
| 19 | Haskell | 54,1 (18) | 17,2 (19) | 17,5 (20) | 15,9 (20) | 41,5 (19) |
| 20 | OCaml | 23,2 (20) | 21,1 (18) | 21,4 (18) | 21,8 (18) | 23,2 (20) |

Sans la grille (colonne du premier tableau ; [`results/report_final.md`](results/report_final.md)), les étages se
séparent davantage : les 14 premiers (de Rust à Mojo), puis Go, C#, Java, Haskell et FreePascal, puis OCaml, seul. Rust
y prend la tête : il a le meilleur score (82,0 contre 81,4 pour C) et il est premier le plus souvent (39 % des
variantes ; C 30 %, C++ 10 %). Le contrôle porte C++ (2e au lieu de 5e), Zig (3e au lieu de 6e), Odin (4e au lieu de
7e), D (8e au lieu de 10e) et Ada (9e au lieu de 12e) ; il retient Rust (5e au lieu de 1er), Nim (6e au lieu de 3e), C3
(7e au lieu de 4e), Fortran (11e au lieu de 9e) et Chapel (12e au lieu de 8e). Sur le plafond seul, la tête serait C++,
Chapel, Rust, D, C, C3, à moins de quatre points les uns des autres.

### Ce qui est sûr, et ce qui ne l'est pas

* **Les grandes marches sont établies.** Les 19 premiers devancent OCaml dans au moins 99,8 % des variantes. Plus haut,
  Swift devance C# dans 96 % des variantes, C# devance Go dans 86 %, et Go, Java et FreePascal devancent Haskell dans
  au moins 83 %.
* **C est premier, sans que ce soit un fait établi.** C est premier dans 57 % des variantes, C++ dans 27 %, Zig dans
  8 %, Rust dans 4 % ; C devance C++ dans 68 % des variantes, et chacun des deux devance chacun des 18 autres dans au
  moins 71,7 %. Zig devance Odin dans 66 % des variantes ; d'Odin à D, un langage ne devance le suivant que dans 50 à
  63 % : l'ordre de ces cinq-là est la meilleure estimation, rien de plus.
* **Le classement se répète.** Rejouée sur une autre machine et un autre modèle de processeur, la campagne redonne la
  même tête et les mêmes étages ; à méthode et à configurations égales, seuls s'échangent des langages que moins d'un
  point sépare (section suivante).
* **La tête dépend des règles.** C est 1er dans huit des douze sensibilités ; C++ passe devant à la seule taille
  publiée, à la seule grande taille et si K3 n'est pas rapporté à la boucle de référence, Rust sur les seules mesures.
  Peu de langages y bougent de plus de deux places : à trois tailles sans les autres règles de la v4, C3 est 4e, Odin
  7e, Nim 9e et Julia 13e ; sans la boucle de référence de K3, C3 est 4e, D 5e, Zig 6e et Odin 7e ; à la seule petite
  taille, Chapel est 9e et Ada 12e.
* **Le contrôle pèse lourd, et il est jugé.** Sans lui, Rust passe 1er, C++ 5e, et huit langages bougent de trois
  places ou plus : Rust, Nim, C3 et Chapel montent, C++, Zig, Odin et Ada reculent. Il pèse d'autant plus qu'on monte
  dans le classement : pour un poids de 35 %, il porte 39 % de la variance du score entre les 20 langages, 41 % dans le
  premier étage, 54 % entre les 14 langages qui peuvent se classer dans la première moitié et 67 % entre les 8 qui
  peuvent atteindre le podium. Le plafond, de poids 40 %, en porte 42, 38, 17 et 12 % : entre langages compilés par les
  mêmes optimiseurs, les plafonds se valent, et c'est la grille qui départage
  ([`results/report_final.md`](results/report_final.md), « Ce qui décide de l'ordre », calculé sur le score au centre).

### D'une campagne à l'autre

Jusqu'au 26 novembre, le classement publié venait de la campagne des 22 et 23 novembre, mesurée sur un Xeon Emerald
Rapids (machine 35). Celle des 25 et 26 novembre la rejoue en entier sur un Xeon Granite Rapids (machine 38), avec les
chaînes réinstallées par `env/install.sh` et une seule source par langage ; les cellules de C y sont aussi mesurées
avec gcc. Plan, écarts et résultats : [`docs/V5.md`](docs/V5.md). Les deux campagnes sont comparées à configurations
égales : Zig y est pris en 0.17 et Go dans le binaire de la campagne, comme chacune les a mesurés (calcul « Campagne
telle que mesurée » du rapport).

* **La même tête et les mêmes étages.** Contre le classement publié de la machine 35, deux paires s'échangent : Zig et
  D (5e et 8e), Mojo et Swift (13e et 14e) ; les 16 autres langages gardent leur place. C était premier dans 69 % des
  variantes ; il l'est dans 60 %.
* **À méthode égale**, l'ancienne campagne recalculée avec les corrections ci-dessous, les six premiers et les étages
  sont les mêmes. Deux paires que moins d'un point sépare dans chaque campagne s'échangent : C3 et D (7e et 8e), Mojo
  et Swift (13e et 14e). Les scores des deux campagnes diffèrent de 0,5 point en moyenne, de 1,64 au plus (Haskell).
* **Les temps changent, leurs rapports beaucoup moins.** Une cellule prend 15 % de temps en moins, en médiane, sur la
  nouvelle machine, et deux cellules sur trois sont à moins de 10 % de ce rapport (2 485 cellules communes). Les
  plafonds bougent plus que l'ordre : celui de C perd 5 points (son K7 passe de 97 à 81), celui de Haskell en gagne 2.
* **C compilé par gcc reste premier.** Score 83,1 au lieu de 83,4 avec clang ; premier dans 56 % des variantes au
  lieu de 57 % ; devant C++ dans 74 % au lieu de 68 %. gcc donne à C un meilleur plafond (87,9 contre 84,4 :
  l'arène de K8 passée par valeur y va deux fois plus vite) et, avec les vérifications, un moins bon code naturel (62,4
  contre 71,5 : la somme conditionnelle de K4 y est 2,3 à 4,1 fois plus lente). L'écart de score entre C et C++ passe
  de 1,7 point à 1,5 : le compilateur en fait un septième.
* **Deux corrections de l'analyse, A5 et A6**, fixées le 25 novembre avant toute analyse des nouvelles mesures. L'écart
  de vitesse commun à tout un groupe de mesures d'une passe ne compte plus comme un bruit propre à chaque cellule ; le
  débit mémoire à quatre fils, borne physique dans une variante sur deux, était relevé plusieurs fois trop haut par une
  sonde qui chronométrait mal (153 Go/s au lieu de 43 sur la machine 38). Aucune des deux ne déplace un langage dans la
  nouvelle campagne ; A6 relève de 1,7 à 2 points les scores des quinze premiers. Les quatre corrections du 24 novembre
  restent en place ([`docs/V4_1.md`](docs/V4_1.md)) : sans aucune des huit corrections, C serait encore 1er ici,
  premier dans 42 % des variantes, quand la campagne précédente plaçait C++ devant lui de justesse.

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
  au lieu de 6e, C3 8e au lieu de 7e et D 7e au lieu de 8e, et les étages ne changeraient pas. Un premier tirage, entre
  les deux premières politiques seulement (« Sans A8 »), comptait dans toutes les variantes les vérifications d'Ada, de
  Swift et de Mojo, et dans une sur deux celles de Zig : il donne les mêmes places, avec 1,1 point de moins pour Ada,
  aucun autre score ne bougeant de plus de 0,6 point. Plan et résultats : [`docs/V5_1.md`](docs/V5_1.md).

### L'exception de Zig

Zig est classé avec sa version de développement, 0.18.0-dev.1298 du 25 novembre 2026, et non avec sa dernière version
stable comme les 19 autres : décision de l'auteur de l'étude, que l'astérisque signale. La 0.17 livre LLVM avec son
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
* **Ce que ça donne.** Zig passe de la 5e à la 3e place, de 77,9 à 79,7 ; il devance Odin dans 66 % des variantes. Le
  gain vient du code naturel dans les deux modes sans `-O safe` (71,0 sur 100 en mode publié au lieu de 56,6). Avec le
  rapport appliqué à K4 et à K9 seulement, les deux noyaux dont le code machine change, Zig est 3e avec 79,6 : sa place
  ne tient pas au bruit des autres cellules.
* **Ce que ça ne règle pas.** Un seul langage profite d'une version de développement ; aucune autre chaîne n'a été
  essayée dans la sienne. Zig n'est pas mesuré dans les groupes des 19 autres, et une archive de développement ne se
  retrouve pas toujours : la remesure peut ne plus être reproductible à l'identique. La 0.18 n'est pas plus rapide
  partout : les formes qui créent leurs fils à chaque appel y sont jusqu'à 1,4 fois plus lentes aux petites tailles. La
  grille de contrôle reste celle de la 0.17, que les sondes rejouées sous la 0.18 confirment.

### Le tri des écarts

Chaque cellule du code naturel est comparée à ses pairs : son temps est rapporté à la médiane de quinze langages dont
la chaîne produit son code machine par LLVM ou par GCC, aux trois tailles et dans les trois modes de vérifications. Un
facteur deux, dans un sens ou dans l'autre, doit avoir une cause, et `tools/check.sh` échoue s'il en manque une. Règle
et registre des causes : [`docs/V5_3.md`](docs/V5_3.md) ; tableaux :
[`results/report_final.md`](results/report_final.md).

44 couples (langage, mesure) sont signalés. Pour 29, un contrôle nommé établit la cause ; pour 15, elle est attribuée
sans contrôle propre ; aucun ne reste sans cause.

* **Une erreur de mesure, trouvée par ce tri : K1 de Go.** Dans la campagne, son K1 naturel prenait 1 489 ms à la
  taille publiée, contre 29 ms pour C et 30 ms pour FreePascal. La cause était dans la construction de Go, pas dans le
  langage ; elle est corrigée ([section suivante](#la-correction-de-go)), et K1 de Go n'est plus signalé. Son niveau
  de référence ayant baissé, sa requête Q6 l'est à son tour, et son stencil dans les trois modes au lieu d'un : deux
  causes connues, ses vérifications de bornes et l'absence de vectoriseur automatique.
* **Un réglage par défaut de clang coûte à C un facteur deux sur K5.** clang fusionne la multiplication et l'addition
  du produit scalaire naturel en une seule instruction, ce qui allonge la chaîne de dépendance de la somme : le même
  source compilé par gcc va 2 à 2,2 fois plus vite aux trois tailles. C'est le mode publié de la chaîne : rien à
  corriger, et « C par gcc » le compte déjà.
* **GCC vectorise moins bien la somme conditionnelle de K4.** En mode publié, C++, Ada et Fortran y sont 2,5 à 4 fois
  derrière la médiane des pairs ; le source de C compilé par gcc y prend 2,5 à 3,9 fois son temps sous clang.
* **Deux cellules sont avantagées : K7 naturel de C et de Fortran**, environ trois fois plus rapides que la médiane
  des pairs à leur meilleure taille. Aucun des deux n'a de table de hachage en bibliothèque standard ; leur code
  naturel est la table à chaînage des manuels, écrite pour le noyau et dimensionnée d'avance, quand les tables de
  bibliothèque des autres grandissent et hachent plus fort. La règle du code naturel l'accepte
  ([`docs/NATURAL.md`](docs/NATURAL.md)) ; le code naturel étant rapporté au meilleur, cette table sert de référence à
  tous sur K7 aux tailles petite et publiée.
* **Le reste confirme ce qui était connu** : vérifications à l'exécution qui bloquent la vectorisation (Zig, Swift,
  Ada, Chapel, Mojo, selon le mode), chaînes sans vectoriseur de boucles, ramasse-miettes, types par défaut en
  références.

### La correction de Go

Le tri des écarts a retrouvé une erreur de mesure. Tout le banc de Go était compilé avec `GOEXPERIMENT=simd`, que
seules demandent ses dix variantes à SIMD explicite. Sous cette expérience, sur un processeur AVX-512, la préemption
asynchrone de Go 1.27 restaure les registres vectoriels sans les nettoyer, et une boucle scalaire qui mêle deux
encodages d'instructions le paie à chaque itération. Un programme Go qui n'utilise pas `simd/archsimd` n'est pas
compilé ainsi : l'erreur était celle de la mesure, pas du langage, et elle était dans tous les classements publiés du
23 au 27 novembre. Plan, mesures et résultats : [`docs/V5_4.md`](docs/V5_4.md).

* **Ce qui était faussé.** Quinze cellules de Go : K1 naturel et K1 naturel permuté, dans ses deux modes, et la forme
  AoS de K1, aux trois tailles. À la taille publiée, son K1 naturel prenait 1 489 ms dans la campagne ; sur la machine
  de la remesure, le même binaire prend 1 723 ms et le binaire standard 28 ms, 62 fois moins. Le contrôle de la
  remesure a trouvé deux autres cellules touchées, plus faiblement : K7 naturel à la grande taille, dans ses deux
  modes. L'erreur débordait sur les autres langages compilés : ses écarts d'un processus à l'autre gonflaient le bruit
  attribué à leur K1 (à la petite taille, un écart type de 0,42 au lieu de 0,09).
* **Comment c'est corrigé.** `bench/go` construit désormais deux binaires de la même source, et seules les dix
  variantes à SIMD explicite vont à celui de l'expérience. Go est remesuré à part, sur la machine 40 : 1 164
  processus, chaque groupe mesurant la nouvelle configuration à côté du binaire de la campagne, pris pour témoin, et,
  pour K1, à côté de C. Une cellule faussée abandonne son temps de la campagne, où l'artefact est intermittent : elle
  prend le temps de la même boucle de C dans la campagne, multiplié par le rapport de Go à C mesuré côte à côte dans
  six passes (0,87 à 1,17 selon la cellule). Ce rapport est rééchantillonné avec les mesures. Les 113 autres cellules
  de Go gardent leur temps de la campagne : mesurées dans les deux binaires, elles donnent un rapport de 0,99 en
  médiane, et 88 % sont à moins de 10 % de 1.
* **Ce que ça donne.** Go passe de la 17e à la 16e place, de 51,7 à 55,3 ; il devance Java dans 76 % des variantes.
  Avec les vérifications, son code naturel passe de 22,6 à 39,9 sur 100 (du 17e au 11e rang), son coût de structure
  (D2) de 72 à 97. Java recule d'une place. Aucun autre score ne bouge de plus de 0,1 point. Les étages ne changent
  pas. Avec toutes ses cellules ramenées par le témoin (« Go, toutes les cellules » du rapport), Go est 16e avec
  55,6.
* **Ce que ça ne règle pas.** La remesure s'est faite sur un autre modèle de processeur que la campagne : la
  correction suppose que le rapport de Go à C, mesuré avec les mêmes binaires, s'y transporte, et ce rapport varie
  d'une passe à l'autre (écart type de 8 à 15 % à la taille publiée). K7 naturel à la grande taille subit le même
  artefact par à-coups (une à trois fois le temps du binaire standard selon la répétition) ; le plan ne lui donnait
  pas de pont, et il garde sa mesure de la campagne : le code naturel de Go reste un peu sous-estimé. Les dix
  variantes à SIMD explicite restent compilées avec l'expérience, seule façon d'appeler `archsimd` : si l'artefact les
  touche, c'est le prix de ce paquet dans Go 1.27. Le tri ne regarde que le code naturel : une erreur de même nature
  dans une forme optimisée ne serait pas vue.

## Ce qui sépare vraiment les langages

Les constats de mécanisme, mesurés au fil de l'étude sur les hôtes de chaque étape ; chacun isole une cause. Leurs
sources sont dans l'archive ([`docs/HISTORY.md`](docs/HISTORY.md)).

1. **Les données d'abord.** Une particule de 64 octets en occupe 64 dans 16 langages, 78 en Java, 88 en C#, 96 en
   Haskell et 144 en OCaml. Parcourir une collection de références dans le désordre coûte 2,7 à 3,8 fois plus aux
   tailles publiée et grande (C#, Java et OCaml, dans la campagne publiée) ; avec des types valeur, l'ordre ne change
   rien.
2. **Le SIMD explicite** divise le produit scalaire par 20 à 40 : 3,7 à 5,7 ms dans les langages compilés, en C# et en
   Java, contre 77 à 166 ms pour la boucle naturelle en ordre strict. OCaml n'en a pas.
3. **La vectorisation automatique se vérifie sur le code exécuté.** Aucune des deux boucles naturelles testées n'est
   vectorisée en C#, Go, Mojo, Zig 0.17 (vectoriseur de boucles désactivé ; elles le sont sous sa version de
   développement), Swift, Haskell et OCaml. Sur le stencil naturel, les vérifications de bornes l'empêchent en Ada,
   l'aliasing en D et en Rust, les deux en Nim ; en Swift, `-O` garde sur K4 un test de débordement par addition.
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
   unique y est 6 à 7 fois plus lent qu'en C. Réveiller des fils bloqués coûte plus qu'un calcul court : Q6 sur 2^16
   lignes prend 10 à 15 µs à un fil, mais 65 µs à quatre fils en C et en C++ et 105 µs en Rust, contre 7,5 µs en
   Fortran, dont le runtime OpenMP attend activement.
7. **Allocation.** Une arène divise K8 par 5 ou 6. Les allocateurs générationnels de Java et d'OCaml sont les meilleurs
   pour du code naturel. Les ramasse-miettes laissent des queues : pause de 89 ms en D, p99,9 à 30 fois la médiane en
   Julia.
8. **Le système compte.** Odin fait un appel système à chaque lecture d'horloge ; sur K7, Rust, Zig et Odin rendent la
   mémoire de leur table au système à chaque répétition, et la paient en défauts de page.

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
* **Chaînes de compilation** : les dernières versions stables au 28 octobre 2026 (Swift et FreePascal ajoutés les 5 et
  6 novembre : [`env/toolchains.txt`](env/toolchains.txt)), installées par `env/install.sh` ; Zig seul est classé
  avec sa version de développement (plus haut). Compilation pour le CPU hôte, ni PGO ni LTO ; chaque binaire est
  construit depuis les fichiers suivis par git, et son empreinte enregistrée.
* **Une machine** : une VM Firecracker à 4 vCPU sur un Xeon Granite Rapids, caractérisée au repos
  ([`results/hw/machine38`](results/hw/machine38)) ; trois passes dont l'ordre est tiré au hasard, du 25 novembre,
  6 h 12, au 26 novembre, 10 h 30 (UTC), sans redémarrage ni processus en échec : 8 559 processus pour les 20
  langages (dont 420 pour C par gcc), mesurés dans les mêmes groupes que les cinq langages retirés depuis. Pas de
  compteurs matériels. Zig sous sa version de développement est remesuré à part le 26 novembre, sur une machine du même
  modèle ([`results/zig_dev`](results/zig_dev)) : six passes, 1 554 processus, avec son témoin. Go hors de
  l'expérience `simd` l'est le 27 novembre, sur une machine d'un autre modèle ([`results/go_std`](results/go_std)) :
  1 164 processus, avec son témoin et C.
* **Score** : contrôle (35 %), 34 capacités notées 0, ½ ou 1 ; plafond (40 %), pour chacune des douze mesures, à
  chaque taille, le meilleur temps du langage rapporté au meilleur des 20, puis la moyenne géométrique (les trois
  mesures à quatre fils ne comptent qu'aux tailles publiée et grande) ; code par défaut (25 %), la variante naturelle
  rapportée au meilleur code naturel (50 %), l'empreinte et la pénalité de désordre d'une collection naturelle
  (15 %), la latence de queue de l'allocation (15 %), la chaîne de pointeurs (20 %).
* **Incertitude** : 2 000 rééchantillonnages des processus pour le bruit de mesure ; 20 000 variantes de l'analyse.
* **Garde-fous** : chaque étape a eu son plan, poussé avant ses mesures ou ses calculs ; les écarts sont datés
  ([`docs/V4_FINAL.md`](docs/V4_FINAL.md), 11 et 12.5 ; [`docs/V4_1.md`](docs/V4_1.md), 7 ;
  [`docs/V5.md`](docs/V5.md), 8 ; [`docs/V5_1.md`](docs/V5_1.md), 7 et 10 ; [`docs/V5_2.md`](docs/V5_2.md), 8 ;
  [`docs/V5_4.md`](docs/V5_4.md), 8) ; le calcul se reproduit à l'octet près (`tools/check.sh`).

## Limites

* **Des machines partagées, dont la vitesse varie.** Deux Xeon d'Intel, virtualisés et partagés ; ni AMD, ni ARM, ni
  compteurs matériels. Sur la machine publiée, le temps d'une cellule varie de 13 % en médiane entre sa passe la plus
  lente et sa plus rapide (8 % sur la précédente), et de 28 à 41 % pour K1, K4, K7 et K9 à la taille publiée, dont
  les données débordent des caches privés d'un cœur. La médiane par processus, trois processus par cellule (sept pour
  K2 et les latences de K8), l'ordre tiré au hasard et le rééchantillonnage en tiennent compte, sans le corriger.
* **Une campagne inachevée, non publiée.** La campagne a d'abord été relancée sur le modèle de processeur d'origine ;
  un premier redémarrage de la machine l'a fait changer d'hôte, un second l'a arrêtée à 61 %, la machine revenant sur
  un autre modèle. Elle n'entre dans aucun calcul ([`docs/V5.md`](docs/V5.md), 8 et 9).
* **La grande taille est bornée par la mémoire de la machine** : 1 Gio de données au plus.
* **Des corrections décidées après coup.** Les quatre corrections du 24 novembre ont été trouvées en relisant les
  résultats publiés, et leur effet estimé avant d'en écrire le plan : ce plan n'est pas aveugle, à la différence de
  ceux des mesures. Les deux du 25 novembre ont été fixées avant toute analyse des nouvelles mesures, mais en
  connaissant celles de la campagne précédente. Les deux du 26 novembre répondent à une place qui surprenait dans le
  classement publié, puis à ce que la première laissait d'inégal ; leur effet était estimé avant d'en écrire le plan.
  Celle du 27 novembre répare une erreur de mesure que le tri des écarts avait retrouvée ; son effet était estimé
  avant le plan, lui aussi. Le rapport garde le calcul sans elles et l'effet de chacune.
* **Un périmètre réduit après coup.** La campagne a mesuré 25 langages ; les cinq derniers du classement en ont été
  retirés le 27 novembre, par décision de l'auteur de l'étude. Trois références du code par défaut venaient d'eux :
  sans eux, le score des 20 autres monte de 0,3 point au plus, et aucun ne change de place dans le classement publié.
  Le plafond et la grille ne changent pas. L'état à 25 langages reste dans l'historique de git, au commit `de69749`
  ([`docs/V6.md`](docs/V6.md)).
* **Un seul auteur.** Les implémentations ont été relues après coup, langage par langage, et ces relectures ont corrigé
  des erreurs du banc et de la grille. Le catalogue commun réduit l'écart d'effort sur le plafond ; il ne touche pas le
  code naturel, dont le choix reste celui de l'auteur ([`docs/NATURAL.md`](docs/NATURAL.md)).
* **Une erreur de mesure corrigée après coup.** Le K1 naturel de Go était faussé d'un facteur 50 dans tous les
  classements publiés du 23 au 27 novembre. Il est corrigé par une remesure faite à part, sur un autre modèle de
  processeur, et par un pont par le C ([la correction de Go](#la-correction-de-go)) : sa valeur corrigée vaut sous ces
  réserves. Le tri des écarts passe le code naturel au crible, pas le plafond.
* **Des microbenchmarks** : ni E/S, ni décompression, ni tri ou jointure.
* **Bibliothèque standard seule.** La règle pèse sur Rust (ni affinité, ni `mmap`, ni taille de ligne de cache sans
  crate), sur Haskell (`vector` et `unordered-containers` sont des paquets) et sur Mojo (`parallelize` est dans MAX).
* **Le contrôle est jugé par un seul évaluateur.** Ses 680 cases reposent toutes sur une sonde exécutée (660) ou une
  mesure (20) ; 86 ne sont prouvées que par une recherche d'absence, qui ne voit que ce que son motif décrit.
* **Les vérifications ne sont égalisées qu'en politique** : C ne vérifie que les tableaux de taille connue, C++ les
  conteneurs de libstdc++, et l'accès par pointeur reste sans vérification ; Zig teste le débordement des entiers, Rust
  non, bien que son compilateur en ait l'option. Le tirage au sort du mode du code naturel répartit le poids de ces
  différences sans les supprimer : les vérifications qu'une option ajoute (Zig, Chapel) comptent dans une variante sur
  trois, celles que le mode publié garde et qu'une option retire (Ada, Swift, Mojo) dans deux sur trois.
* **Une version et un compilateur par langage** : Fortran est classé avec gfortran, C avec clang (avec gcc, il reste
  1er : plus haut), C++ avec g++ 16 (le seul à livrer `std::simd`). Un réglage temporaire d'une chaîne peut coûter des
  rangs : le vectoriseur de boucles coupé de Zig 0.17 lui coûtait deux places.
* **Une exception pour un langage.** Zig est classé avec une version de développement, les 19 autres avec leur dernière
  version stable, et aucune autre version de développement n'a été essayée. Ses temps ne viennent pas de la campagne :
  ils y sont ramenés par un témoin, à partir d'une remesure faite à part. Sa place vaut sous ces réserves ; avec la
  0.17, il est 5e.
* **JIT** : trois échauffements au moins, et au moins une seconde ; les boucles chaudes tournent souvent en code OSR,
  sans atteindre le niveau d'optimisation final.
* **Réglages des runtimes par défaut**, sauf le nombre de fils, fixé à quatre (`-t 4` pour Julia, `+RTS -N4` pour
  Haskell) : leur ramasse-miettes y devient parallèle, même pour les noyaux séquentiels.

## À côté du classement

Trois résultats publiés à côté du classement, par décision de l'auteur de l'étude, quand il comptait 25 langages ;
résumés et sources dans [`docs/HISTORY.md`](docs/HISTORY.md).

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

Le premier contrôle (une minute environ) vérifie la grille contre ses sondes, le relevé des formes, le plan de la
campagne, le classement sur 200 variantes et que chaque écart du tri a une cause ; le second (une demi-heure environ)
recalcule le classement complet et le compare à l'octet près. Ni l'un ni l'autre ne demande de chaîne de compilation.

```bash
python3 analysis/final_v4.py
```

```bash
python3 analysis/charts_final.py
```

Ces deux commandes réécrivent `results/final/analysis.json`, `results/report_final.md` et le graphique. Remesurer
demande les 20 chaînes de [`env/toolchains.txt`](env/toolchains.txt), que `env/install.sh` installe en moins de
1 h 30, et une machine à 4 cœurs et 15 Gio pendant moins d'un jour (la campagne publiée a pris 28 heures, dont une
dizaine pour les processus des cinq langages retirés depuis) ; une campagne s'écrit dans son propre répertoire et se
mesure sur un seul modèle de processeur : [`docs/METHOD.md`](docs/METHOD.md), 11.

## Le dépôt

| Répertoire | Contenu |
|---|---|
| `bench/<langage>/` | l'implémentation de chaque langage : variantes publiées et formes du catalogue (`cv_variants`), son `build.sh` et son `run` |
| `probes/<langage>/` | les sondes de la grille de contrôle |
| `tools/` | `final/` (constructions, campagne), `sizes/` (tailles, sommes attendues), `driver.py` (essai d'une implémentation), `gendata.c` (données), `hwprobe.c` (caractérisation), `grid_audit/` (recherches d'absence), `check.sh` (garde-fou) |
| `analysis/` | `final_v4.py` (le classement), `capabilities*.py` (la grille), `check_probes.py`, `charts_final.py` |
| `results/` | `final/` (mesures brutes, étalonnage, analyse), `zig_dev/` (remesure de Zig par sa version de développement, avec son témoin et la caractérisation de sa machine), `go_std/` (remesure de Go hors de l'expérience `simd`, avec son témoin et C), `report_final.md`, `probes/` et `grid_audit/` (preuves de la grille), `hw/` (caractérisation de la machine 38 et de la machine 35, celle de la campagne précédente), `converge/` (relevé des formes) |
| `docs/` | `METHOD.md` (la méthode), `SPEC.md` (les noyaux), `NATURAL.md` (le code naturel), `CAPABILITIES.md` (la grille), `V5.md` (plan, écarts et résultats de la campagne publiée), `V5_1.md` (corrections A7 et A8 de l'analyse), `V5_2.md` (exception de Zig : plan, mesures et résultats), `V5_3.md` (ce qui décide de l'ordre, tri des écarts), `V5_4.md` (correction de la mesure de Go : plan, mesures et résultats), `V6.md` (retrait de cinq langages : plan et résultats), `V4_FINAL.md` (plan et procès-verbal de la campagne précédente), `V4_1.md` (corrections A1 à A4 de l'analyse), `HISTORY.md` (étapes et archive) |
| `env/` | `install.sh` (installe les 20 chaînes et la version de développement de Zig), `toolchains.txt` (leurs versions), `msdata.sha256` (empreintes des données) |

Tout ce qui a précédé (v1 à v3, relectures par langage, points 2 à 6 de la v4, ancien README) est dans l'archive, le
commit `5fbe6a6` ; les mesures de la campagne précédente et de la campagne inachevée, dans le commit `76d07af` ;
l'état à 25 langages, dans le commit `de69749` : [`docs/HISTORY.md`](docs/HISTORY.md).
