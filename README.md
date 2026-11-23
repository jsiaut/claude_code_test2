# Quels langages incarnent le mieux la *mechanical sympathy* ?

*Classement mesuré de 25 langages, octobre et novembre 2026. Depuis le 23 novembre, le classement de la v4 : les 25
langages mesurés sur une même machine, sept noyaux à trois tailles, dans des conditions égales et avec un code optimisé
convergent ([`docs/V4_FINAL.md`](docs/V4_FINAL.md)) ; celui de la v3 est archivé
([`docs/RANKING_V3.md`](docs/RANKING_V3.md)).*

Un seul critère : la *mechanical sympathy* au sens large, c'est-à-dire la capacité d'un langage à faire écrire du
code en accord avec le matériel : disposition des données, SIMD, hiérarchie mémoire, concurrence, allocation,
requêtes analytiques. C'est ce qu'exigent le HPC, les moteurs OLAP et le Data-Oriented Design. Le classement est
mesuré par moi sur une machine Intel (Emerald Rapids), sauf le pilier « contrôle », qui est un inventaire jugé.

## Le classement

Ce classement de 1 à 25 répond à une demande de l'auteur de l'étude, et la v4 le garde en tête
([`docs/V4_PLAN.md`](docs/V4_PLAN.md)). Le plan de la v3, fixé avant ses calculs, publiait autre chose : des étages sans
ordre interne, trois quantités séparées (plafond, code naturel, contrôle) et le score composite en simple sensibilité
([`docs/ANALYSIS_V3.md`](docs/ANALYSIS_V3.md)). La colonne « Étage » donne ces étages, qui sont établis ; à l'intérieur
d'un étage, l'ordre est la meilleure estimation, pas un fait. Les trois quantités, et le classement sur les seules
mesures, suivent le tableau. Le classement de la v3, publié ici du 30 octobre au 23 novembre, est archivé avec ses
notes, ses errata et ses explications ([`docs/RANKING_V3.md`](docs/RANKING_V3.md)).

| Rang | Étage | Langage | Score | Rang plausible | Devance le suivant | Ce qui le place là |
|---|---|---|---|---|---|---|
| 1 | 1 | **C++** | 78,9 | 1–6 | 51 % | À égalité de fait avec C. Le plus de contrôle (`pmr`, atomiques, `std::simd` expérimental) et le 2e plafond : son arène de K8 par valeur fait la frontière de K8 ; code naturel 9e |
| 2 | 1 | **C** | 78,3 | 1–7 | 73 % | Le meilleur code naturel, le 3e plafond (1er sur K4 et K7) et le contrôle de GNU C (2e) ; son K8 le plus rapide, une arène écrite par itération, reste à 0,66 de la frontière |
| 3 | 1 | **Odin** | 72,7 | 1–8 | 58 % | Le Data-Oriented Design dans le langage (`#soa`, `#simd`, intrinsèques de LLVM, allocateurs) : 5e contrôle, 5e code naturel ; plafond 10e seulement (K4 70, K8 67) |
| 4 | 1 | **Rust** | 71,5 | 1–9 | 59 % | Le meilleur code par défaut (2e code naturel, queues de latence de K8 courtes) et le 6e plafond ; contrôle 9e (ni affinité, ni `mmap` dans la bibliothèque standard) |
| 5 | 1 | **C3** | 71,1 | 2–9 | 61 % | C avec vecteurs natifs : 5e plafond, 6e code naturel ; contrôle 8e (ni SoA ni intrinsèques officiels) ; 1er à trois tailles sans les autres règles de la v4 |
| 6 | 1 | **Nim** | 71,0 | 3–10 | 52 % | Le meilleur K1 (98), 7e plafond, 4e code par défaut ; contrôle 7e (les leviers de C par sa compilation vers C) |
| 7 | 1 | **D** | 73,5 | 3–12 | 58 % | 4e plafond et 4e contrôle (le contrôle de C, templates et CTFE), mais les pauses de son ramasse-miettes font les pires queues de latence de K8 des 19 premiers (D3 : 2 sur 100) |
| 8 | 1 | **Zig** | 72,2 | 2–11 | 76 % | 3e contrôle (tous les leviers du DOD), mais son code naturel compte en mode vérifié (`-O safe`, R1) : 11e code naturel, 5e place sans R1 ; plafond 11e (vectoriseur de boucles désactivé en 0.17) |
| 9 | 1 | **Ada** | 71,4 | 5–12 | 65 % | Disposition au bit près : 6e contrôle, 8e plafond, les queues de latence de K8 les plus courtes après Fortran ; code naturel 10e (vérifications) |
| 10 | 1 | **Chapel** | 67,7 | 3–14 | 54 % | Le 1er plafond (K9 98, K4 90, K6 81) ; code naturel 16e sous R1 (`--checks`) et contrôle 16e (leviers bas niveau rares ou instables) |
| 11 | 1 | **Fortran** | 67,0 | 6–14 | 49 % | À égalité de fait avec Julia. Les queues de latence de K8 les plus courtes, 3e code par défaut, 9e plafond ; ni SIMD explicite ni intrinsèques (K4 50, forme SWAR) : contrôle 14e |
| 12 | 1 | **Julia** | 66,6 | 6–14 | 78 % | 3e code naturel et 13e plafond (74,4, contre 62,3 en v3 : formes du catalogue) ; les pauses du ramasse-miettes pèsent sur K8 (D3 10) |
| 13 | 1 | **Swift** | 64,4 | 10–14 | 53 % | Types SIMD et `InlineArray` : le meilleur K5 (97) ; vérifications de `-O` coûteuses sur le code naturel (14e) et le K4 le plus lent des 14 premiers (46) ; contrôle 13e |
| 14 | 1 | **Mojo** | 64,7 | 10–15 | 91 % | Le SIMD au cœur du langage (K5 92, K7 95) ; ni vectoriseur de boucles (K4 50) ni threads publics dans `std` ; K8 46 |
| 15 | 1 | **C#** | 60,2 | 13–16 | 97 % | La boîte à outils la plus riche des langages à GC : 15e plafond (67,5, contre 53,6 en v3 : K4 optimisé, réserves de fils) ; objets en références (K7 54, K8 50, désordre de K1) |
| 16 | 1 | **Go** | 50,5 | 16–18 | 50 % | À égalité de fait avec FreePascal. Structures par valeur et SIMD expérimental (K4 82) ; écritures atomiques séquentiellement cohérentes (K3 30) ; code naturel 18e |
| 17 | 1 | **FreePascal** | 49,4 | 15–19 | 47 % | À égalité de fait avec Java. Records `packed`, assembleur, mémoire à la main : 15e contrôle, 12e code par défaut ; ni vectoriseur ni intrinsèques : 19e plafond (K4 14, K5 39) |
| 18 | 1 | **Java** | 49,4 | 16–18 | 95 % | Les queues de latence de K8 les plus courtes des langages à ramasse-miettes (D3 59) et la Vector API (K5 84) ; pas de types valeur (K1 45, désordre de K1) ; contrôle 18e |
| 19 | 1 | **Haskell** | 42,6 | 18–19 | 100 % | Peut descendre bas (FMA vectorielle de GHC : K5 91 ; K7 90) ; code par défaut boxé, ramasse-miettes imposé : code par défaut et contrôle 19e |
| 20 | 2 | **OCaml** | 24,5 | 20–22 | 89 % | Bonne allocation générationnelle (D3 46) ; ni types valeur, ni flottant 32 bits de calcul, ni SIMD : plafond 21,4 |
| 21 | 2 | **BQN** | 17,0 | 20–23 | 54 % | À égalité de fait avec JavaScript. Primitives vectorisées de CBQN, mais un coût fixe par appel ; ni threads, ni flottant 32 bits ; K1 hors mémoire à la grande taille |
| 22 | 2 | **JavaScript** | 17,6 | 21–24 | 68 % | Tableaux typés compilés mais vérifiés, aucun SIMD : plafond 14,6 ; contrôle 24e |
| 23 | 2 | **PHP** | 16,9 | 21–23 | 97 % | Chaque valeur un zval de 16 octets, chaque objet une référence : plafond 23e ; le contrôle d'un langage dynamique doté d'une FFI et de processus (21e) |
| 24 | 2 | **Python** | 12,7 | 22–25 | 76 % | CPython seul : le plafond le plus bas (1,0), K1 naturel hors mémoire à la grande taille ; contrôle 20e (`ctypes`, sous-interpréteurs) |
| 25 | 2 | **Lua** | 5,9 | 24–25 | — | PUC-Lua sans son API C : presque aucun levier (contrôle 6,8) ; plafond 1,4, au-dessus de CPython |

* **Score** (0–100) : 40 % de plafond mesuré (le meilleur code que le langage permet d'écrire pour la machine), 25 % de
  code par défaut mesuré (le code qu'on écrit sans y penser) et 35 % de contrôle (les leviers qu'offrent le langage et
  sa chaîne de compilation). Sept noyaux comptent à trois tailles : une qui tient dans le cache, la taille publiée, une
  au-delà du L3.
* **Ordre** : le rang moyen sur 20 000 variantes de l'analyse, qui tirent au hasard les poids des piliers et des
  tailles, les normalisations, le jugement porté sur chaque capacité et le bruit de mesure. Il suit le score, sauf en
  quatre endroits. D, Zig et Ada, 3e, 5e et 7e au score, ne sont que 7e, 8e et 9e : leur score tient à un contrôle élevé
  (87,1, 87,2 et 80,6 points), et leur code par défaut est le plus faible des neuf premiers (D : les pauses de son
  ramasse-miettes dans les requêtes de K8 ; Zig : son code naturel en mode vérifié ; Ada : ses vérifications) ; sur les
  seules mesures, ils sont 9e, 12e et 10e. Ailleurs, deux langages notés à moins d'un point l'un de l'autre échangent
  leur place : Swift passe devant Mojo (64,4 contre 64,7 points ; devant dans 53 % des variantes), BQN devant JavaScript
  (17,0 contre 17,6 ; 54 %), et FreePascal devant Java au rang moyen, d'un millième de rang, quand Java gagne leur duel
  (53 %).
* **Rang plausible** : le rang dans 90 % des variantes. **Devance le suivant** : la part des variantes où le langage
  passe devant celui de la ligne suivante. Sous 50 %, le rang moyen et le duel se contredisent : les deux langages sont
  à égalité de fait (Fortran et Julia, 49 % ; FreePascal et Java, 47 %) ; à peine au-dessus, C++ et C (51 %), Go et
  FreePascal (50 %) le sont aussi.
* **Étages** : les 19 premiers (de C++ à Haskell) et les six derniers (d'OCaml à Lua), chaque langage du premier
  devançant chacun du second dans au moins 99,6 % des variantes. La v3 en avait trois ([14, 5, 6]) ; ses deux autres
  marches restent hautes sans atteindre 95 % : les 14 premiers devancent C# dans au moins 91,5 % des variantes (Mojo),
  C# devance les quatre suivants dans au moins 91,1 % (FreePascal), et ces quatre devancent Haskell dans au moins 89,0 %
  (FreePascal encore).
* **Ce qui change par rapport à la v3.** Un seul langage bouge de plus de deux places : Zig, de la 5e à la 8e, par R1
  (sans R1, il serait 5e). En tête, C++ passe devant C : il est 1er dans 36,5 % des variantes, C dans 36,1 % ; C++ fait
  la frontière de K8 (son arène par valeur) et a le plus de contrôle, C garde le meilleur code naturel et les meilleurs
  K4 et K7. Rust gagne deux places (de la 6e à la 4e) avec le meilleur code par défaut ; Odin (3e), C3 (5e) et Zig en
  perdent ; Nim et D gagnent chacun une place (6e et 7e). Plus bas, Julia passe devant Swift (12e et 13e), Go devant
  FreePascal et Java (16e, 17e et 18e), JavaScript devant PHP (22e et 23e). Comparé au calcul « Convergent, avec R4 » du
  point 4 (machine 33, taille publiée seule, sans R1 ni R2), Rust passe de la 7e à la 4e place et Zig de la 2e à la 8e.
* **Cellules hors mémoire** : à la grande taille, les quatre variantes de K1 de BQN et K1 naturel de Python (dans
  l'ordre et permuté) dépassent la mémoire de la machine ; elles prennent le temps admissible le plus lent des autres
  langages (celui de Go, ou de Python pour `soa` de BQN), comme au point 2.
* **Autres chaînes, versions et modes** (C par GCC, C++ avec le K4 de clang++, Zig 0.18-dev, flang, Swift `-Ounchecked`,
  .NET 11, FreePascal 3.2.4-rc2 et branche main, LuaJIT, Bun, CPython sans GIL, PHP sans JIT) : placés sur le classement
  de la v3 ([`docs/RANKING_V3.md`](docs/RANKING_V3.md)), ils ne sont pas remesurés dans la campagne finale.

![Classement de la v4](results/charts/classement_v4.svg)

### Les mesures et la grille, séparément

Le plafond et le code naturel sont mesurés ; le contrôle est une grille jugée de 34 capacités, dont toutes les cases
reposent depuis le 19 novembre sur une sonde exécutée ou une mesure ([`docs/GRID_AUDIT.md`](docs/GRID_AUDIT.md),
[`docs/CAPABILITIES.md`](docs/CAPABILITIES.md)). Le tableau les donne séparément (plafond et code naturel sur 100,
contrôle en règle v2), avec le classement qu'on obtient sans la grille : son poids mis à 0 au centre et dans les 20 000
variantes ([`results/report_final.md`](results/report_final.md)).

| Rang | Langage | Plafond (rang) | Code naturel (rang) | Contrôle (rang) | Sur les seules mesures : place (à 90 %) |
|---|---|---|---|---|---|
| 1 | C++ | 85,0 (2) | 14,0 (9) | 92,4 (1) | 3 (1–8) |
| 2 | C | 83,1 (3) | 20,0 (1) | 91,7 (2) | 1 (1–6) |
| 3 | Odin | 77,6 (10) | 17,9 (5) | 84,0 (5) | 6 (2–10) |
| 4 | Rust | 80,5 (6) | 19,0 (2) | 73,6 (9) | 2 (1–6) |
| 5 | C3 | 80,9 (5) | 17,4 (6) | 75,7 (8) | 4 (2–8) |
| 6 | Nim | 79,0 (7) | 18,2 (4) | 76,1 (7) | 5 (3–9) |
| 7 | D | 81,1 (4) | 16,2 (7) | 87,1 (4) | 9 (5–14) |
| 8 | Zig | 76,8 (11) | 10,5 (11) | 87,2 (3) | 12 (8–13) |
| 9 | Ada | 78,4 (8) | 10,5 (10) | 80,6 (6) | 10 (6–13) |
| 10 | Chapel | 87,5 (1) | 7,5 (16) | 61,8 (16) | 7 (1–12) |
| 11 | Fortran | 78,2 (9) | 15,9 (8) | 65,3 (14) | 8 (2–11) |
| 12 | Julia | 74,4 (13) | 18,5 (3) | 73,3 (10) | 11 (7–14) |
| 13 | Swift | 75,4 (12) | 9,0 (14) | 68,1 (13) | 13 (9–14) |
| 14 | Mojo | 73,0 (14) | 9,4 (13) | 70,5 (11) | 14 (10–14) |
| 15 | C# | 67,5 (15) | 8,1 (15) | 68,8 (12) | 15 (15–18) |
| 16 | Go | 59,1 (17) | 5,5 (18) | 48,7 (17) | 17 (15–18) |
| 17 | FreePascal | 41,6 (19) | 3,9 (21) | 62,3 (15) | 18 (15–19) |
| 18 | Java | 60,0 (16) | 9,6 (12) | 42,7 (18) | 16 (15–17) |
| 19 | Haskell | 49,6 (18) | 4,6 (20) | 41,5 (19) | 19 (18–19) |
| 20 | OCaml | 21,4 (20) | 5,9 (17) | 23,2 (22) | 20 (20–21) |
| 21 | BQN | 10,5 (22) | 4,9 (19) | 19,7 (23) | 22 (20–22) |
| 22 | JavaScript | 14,6 (21) | 3,7 (22) | 14,6 (24) | 21 (21–22) |
| 23 | PHP | 6,3 (23) | 1,7 (23) | 27,4 (21) | 23 (22–23) |
| 24 | Python | 1,0 (25) | 0,4 (25) | 29,7 (20) | 25 (25–25) |
| 25 | Lua | 1,4 (24) | 0,8 (24) | 6,8 (25) | 24 (24–24) |

Sans la grille, les étages se séparent davantage : les 14 premiers (de C à Mojo), puis C#, Java, Go, FreePascal et
Haskell, puis OCaml, JavaScript et BQN, puis PHP, Lua et Python, chacun seul. C y est 1er (dans 33 % des variantes ;
Rust 24 %, C++ 20 %, Chapel 15 %). Le contrôle porte Odin (3e au lieu de 6e), D (7e au lieu de 9e) et Zig (8e au lieu de
12e), et retient Chapel (10e au lieu de 7e) et Fortran (11e au lieu de 8e) ; sur le plafond seul, la tête serait Chapel,
C++, C, D, C3, Rust.

### Ce qui est sûr, et ce qui ne l'est pas

* **Les grandes marches sont établies.** Les 19 premiers devancent les six derniers dans au moins 99,6 % des
  variantes ; dans le dernier étage, OCaml devance BQN dans 89 % des variantes et PHP
  devance Python dans 97 %. Plus haut, Mojo devance C# dans 91 % des variantes, C# devance Go dans 97 % et Java devance
  Haskell dans 95 %.
* **En haut du tableau, l'ordre est la meilleure estimation, pas un fait établi.** C++ ou C est premier dans 73 % des
  variantes (C++ 36,5 %, C 36,1 %), Odin dans 11 %, Rust dans 8 %, C3 dans 3 % ; de C++ à Zig, un langage devance le
  suivant dans 51 à 76 % des variantes.
* **La tête dépend des règles de la v4, chacune fixée avant les mesures.** Sans les formes du catalogue (C1), C est 1er
  et C++ 4e ; à trois tailles sans les autres règles (formes publiées, code naturel publié, K3 sans R4), C3 est 1er
  (dans 30 % des variantes) ; sur les seules mesures, C est 1er et Rust 2e. Les autres sensibilités ne déplacent
  personne de plus de deux places, sauf Zig (5e sans R1, 4e avec R1', le code naturel sans vérifications) et Ada (12e à
  la seule petite taille) ([`docs/V4_FINAL.md`](docs/V4_FINAL.md), 12).
* **Une machine.** Le classement de la v4 est mesuré sur un seul hôte, sans réplication : des machines du même modèle
  diffèrent (b3, la boucle de référence de K3, de 69 à 85 ms), et la vitesse de celle-ci variait d'une seconde à l'autre
  (deux exécutions de b3 jusqu'à 27 % d'écart). La v3, répliquée sur deux micro-architectures, mettait C 1er sur
  Cascade Lake et C++ 1er sur Emerald Rapids.
* **Le contrôle pèse lourd, et il est jugé.** Sans lui, C passe 1er, Rust 2e, et Zig recule de quatre places (voir « Les
  mesures et la grille, séparément »).

### La taille des données (v4, point 2 ; dans le classement de la v4)

*Dans le classement de la v4 : les sept noyaux comptent à leurs trois tailles, à poids égaux au centre ; à la seule
taille publiée, aucun langage ne bouge de plus de deux places ([`docs/V4_FINAL.md`](docs/V4_FINAL.md), 12.3). Ce qui
suit décrit le point 2, mesuré à côté du classement de la v3.*

Chaque noyau était mesuré à une seule taille, sauf K2. Le point 2 de la v4 a mesuré les sept noyaux dont le travail
dépend d'une taille de données à trois tailles (une qui tient dans le L2 d'un cœur, la taille publiée, une au-delà du
L3), pour les 25 langages, sur un même hôte (Emerald Rapids, machine 31 : 6 594 processus en trois passes), avec un
plan et une analyse fixés avant les mesures ([`docs/V4_SIZES.md`](docs/V4_SIZES.md),
[`results/report_sizes.md`](results/report_sizes.md)). Le classement ci-dessus ne change pas : il changera une seule
fois, avec les points 3 et 4, dans une campagne où les tailles compteront à poids égaux.

| Publié | Langage | Cet hôte, taille publiée | Trois tailles | Petite seule | Grande seule |
|---|---|---|---|---|---|
| 1 | C | 1 | 2 | 2 | 3 |
| 2 | Odin | 6 | 4 | 4 | 5 |
| 3 | C++ | 2 | 1 | 1 | 1 |
| 4 | C3 | 3 | 3 | 3 | 2 |
| 5 | Zig | 8 | 7 | 10 | 4 |
| 6 | Rust | 7 | 8 | 8 | 9 |
| 7 | Nim | 4 | 5 | 6 | 6 |
| 8 | D | 5 | 6 | 7 | 7 |
| 9 | Ada | 9 | 10 | 14 | 8 |
| 10 | Chapel | 11 | 9 | 5 | 10 |
| 11 | Fortran | 14 | 13 | 9 | 12 |
| 12 | Swift | 10 | 11 | 12 | 14 |
| 13 | Julia | 13 | 14 | 13 | 13 |
| 14 | Mojo | 12 | 12 | 11 | 11 |

Les onze suivants restent à une place au plus de leur rang publié dans chacun de ces calculs.

* **L'effet des tailles est faible.** Entre la taille publiée seule sur cet hôte et la moyenne des trois tailles,
  aucun langage ne bouge de plus de deux places : Odin et Chapel en gagnent deux, C++ passe devant C. C'est l'ordre du
  bruit de processus de cet hôte : refait avec les anciens binaires d'Odin, de Chapel et de Go (contrôle prévu par le
  plan), le calcul à la taille publiée déplace déjà Odin de deux places.
* **Une taille seule déplace davantage, dans les deux sens.** À la petite taille, les variantes à plusieurs fils
  paient surtout leur lancement, sauf en Chapel et en Fortran, qui gardent une réserve de fils : Chapel 5e, Fortran
  9e. À la grande, la limite de la mémoire rapproche les compilés : Zig (4e) et Ada (8e) remontent, Swift descend
  (14e).
* **L'effet de l'hôte est plus grand.** Entre le classement publié et le même calcul sur cet hôte, cinq langages
  bougent de trois ou quatre places : Nim (7e → 4e), D (8e → 5e), Odin (2e → 6e), Zig (5e → 8e), Fortran
  (11e → 14e). Le premier moteur est l'écrivain unique de K3, dont la boucle coûte un ou sept cycles par incrément
  selon sa place dans sa ligne de 64 octets (point 5 de « Ce qui sépare vraiment les langages ») : l'effet, établi sur
  Emerald Rapids, existe aussi sur Granite Rapids, mais pas sur Cascade Lake, d'où vient le K3 du classement.

*Erratum (21 novembre) : cette campagne a mesuré les sources de `bench/<langage>`, auxquelles manquent, pour 20
langages, les corrections que le classement publié applique (copies corrigées des remarques, harnais commun de K9).
L'effet des tailles, mesuré sur le même code des deux côtés, tient ; la comparaison au classement publié (« l'effet de
l'hôte », dernier point) mêle ces corrections : le K4 de Fortran, le K9 d'Odin et de Zig en dépendent
([`docs/V4_SIZES.md`](docs/V4_SIZES.md), 10.7). Les sources ont été mises en accord avec le classement publié au
point 4, qui a mesuré l'effet de l'erratum sur un même hôte : les deux sources y donnent des classements à deux places
au plus l'un de l'autre ; contre le classement publié, la source corrigée déplace de trois ou quatre places D
(8e → 4e), Odin (2e → 5e) et Mojo (14e → 11e), mais ni Fortran (13e : son recul tenait aux corrections absentes) ni
Zig (6e) ([`docs/V4_CONVERGE.md`](docs/V4_CONVERGE.md), 11.9).*

### Des conditions égales (v4, point 3 ; dans le classement de la v4)

*Dans le classement de la v4 : R1 à R5 s'appliquent ; sans R1, Zig serait 5e au lieu de 8e ; sans R2 ou sans R4, aucun
langage ne bouge de plus de deux places ([`docs/V4_FINAL.md`](docs/V4_FINAL.md), 12.3). Ce qui suit décrit le point 3,
mesuré à côté du classement de la v3.*

Trois conditions n'étaient pas les mêmes pour tous les langages : les vérifications à l'exécution du code naturel
(actives dans le mode publié de 17 langages, absentes de celui des 8 autres), la structure du stencil naturel
(contigu dans 12 langages, tableau de tableaux dans 13) et l'interdiction du SIMD explicite dans K4 ; le point 2 en a
trouvé une quatrième, la place de la boucle de K3 dans sa ligne de 64 octets. Le point 3 de la v4 a mesuré l'effet de
quatre règles communes : **R1**, vérifications actives pour tous (**R1'**, aucune vérification, en sensibilité) ;
**R2**, stencil naturel contigu pour tous ; **R3**, une variante `tuned` de K4, SIMD explicite compris ; **R4**, K3
rapporté à une boucle de référence mesurée sur l'hôte. Une seule campagne, sur un même hôte (Emerald Rapids,
machine 32 : 2 559 processus en trois passes, base comprise), avec un plan et une analyse fixés avant les mesures
([`docs/V4_EQUAL.md`](docs/V4_EQUAL.md), [`results/report_equal.md`](results/report_equal.md)). Le classement
ci-dessus ne change pas : ces règles s'appliqueront dans la campagne finale de la v4, quel que soit leur effet mesuré
ici.

| Publié | Langage | Cet hôte | R1 | R2 | R3 | R4 | Toutes | Toutes, R1' |
|---|---|---|---|---|---|---|---|---|
| 1 | C | 1 | 1 | 1 | 2 | 1 | 1 | 1 |
| 2 | Odin | 4 | 4 | 5 | 5 | 4 | 3 | 4 |
| 3 | C++ | 2 | 3 | 2 | 1 | 2 | 2 | 2 |
| 4 | C3 | 3 | 2 | 3 | 3 | 3 | 5 | 5 |
| 5 | Zig | 8 | 9 | 8 | 4 | 6 | 4 | 3 |
| 6 | Rust | 7 | 7 | 7 | 9 | 5 | 6 | 7 |
| 7 | Nim | 5 | 5 | 4 | 6 | 8 | 7 | 8 |
| 8 | D | 6 | 6 | 6 | 7 | 9 | 9 | 9 |
| 9 | Ada | 10 | 8 | 10 | 8 | 10 | 8 | 6 |
| 10 | Chapel | 9 | 10 | 9 | 10 | 7 | 11 | 10 |
| 11 | Fortran | 14 | 14 | 14 | 13 | 14 | 13 | 13 |
| 12 | Swift | 11 | 11 | 11 | 12 | 11 | 12 | 12 |
| 13 | Julia | 13 | 13 | 13 | 14 | 12 | 14 | 14 |
| 14 | Mojo | 12 | 12 | 12 | 11 | 13 | 10 | 11 |

Les onze suivants restent à une place au plus de leur rang publié dans chacun de ces calculs (R1' compris), sauf
FreePascal, 18e avec R3 et avec « Toutes, R1' ».

* **Les vérifications et le stencil bougent peu.** Ni R1, ni R1', ni R2 ne déplacent un langage de plus de deux
  places. Les vérifications coûtent pourtant cher à certains noyaux naturels : le stencil de Chapel prend 20 fois son
  temps avec `--checks`, le K4 de Zig 10 fois en `-O safe`, la requête Q1 de FreePascal 7,5 fois avec `-Cr -Co` ;
  sans vérifications (`-gnatp`), Ada fait son agrégation par hachage en 0,15 fois son temps publié. Mais le code
  naturel ne compte guère que pour un huitième du score, et il y est déjà loin de la frontière : Chapel, le plus
  touché, perd un point par son code naturel. Une part de ce qui bouge vient des latences de queue de K8, qui varient
  d'un processus à l'autre bien plus que les temps : avec celles des binaires publiés, R1' fait monter Ada de trois
  places (10e → 7e).
* **Le SIMD explicite dans K4 fait monter Zig de quatre places** (8e → 4e) : sa meilleure forme publiée prenait
  6,5 ms, sa forme en `@Vector` 0,61 ms. Les formes `tuned` de 18 langages font K4 en 0,58 à 1,30 ms, à la bande
  passante d'un cœur ou près d'elle ; K4 ne sépare plus que six langages, de 4,1 à 212 ms : BQN, OCaml, JavaScript,
  PHP, Python et Lua.
* **K3 rapporté à une boucle de référence fait reculer Nim et D de trois places** (5e → 8e, 6e → 9e). Sur cet hôte,
  la boucle de l'écrivain unique est rapide ou lente selon la forme du code émis et sa place dans sa ligne de 64
  octets : celles de D, C3 et Nim prennent 17 à 20 ms, celles de C, Rust, Odin, Zig, Chapel, Swift, Julia, Fortran, C#
  et Java 86 à 92 ms. Rapportées à la médiane des 16 places de la boucle de référence (84,6 ms), elles valent toutes
  0,92 à 1 ; l'écart reste entier avec les langages qui ne peuvent pas écrire sans `lock` (Go, OCaml, Haskell,
  JavaScript : 0,16 à 0,34).
* **Ensemble, les règles du point 3 déplacent de plus de deux places Zig (8e → 4e) et D (6e → 9e)** ; avec R1' au
  lieu de R1, aussi Ada (10e → 6e) et Nim (5e → 8e). Un contrôle hors plan, avec les latences de K8 des binaires
  publiés, montre que la montée de Zig, le recul de D et, avec R1', la montée d'Ada ne dépendent pas de ces latences ;
  les autres déplacements de Nim, de Chapel et d'Ada sont au seuil (deux ou trois places selon les latences).
* **Réplication.** Le calcul à la taille publiée sur cet hôte et celui du point 2 (machine 31, même modèle de
  processeur) ne diffèrent de plus de deux places pour aucun langage ; sur les deux, Zig (5e → 8e) et Fortran
  (11e → 14e) reculent de trois places par rapport au classement publié. Avec les règles du point 3 (« Toutes »),
  seul Mojo s'écarte de plus de deux places du classement publié (14e → 10e).

*Errata (21 novembre, le jour même). Le K4 `tuned` de FreePascal, écrit en assembleur en ligne, que la spécification
interdit dans le code optimisé, avait été compté ; écarté, FreePascal recule de deux places avec R3 (18e), Java et Go en
gagnent une ; les autres conclusions ne changent pas ([`docs/V4_EQUAL.md`](docs/V4_EQUAL.md), 11.8). Comme celle du
point 2, cette campagne a mesuré des sources sans les corrections du classement publié pour 20 langages : l'effet de
chaque règle, mesuré sur le même code des deux côtés, tient ; les comparaisons au classement publié (réplication,
dernière phrase) et la place relative de C, Chapel, Ada et Swift, dont le K9 était déjà au harnais commun, non (11.9).
Mesuré au point 4 sur un même hôte, cet erratum ne déplace aucun langage de plus de deux places, et la montée de Zig
par R3 comme le recul de D par R4 se retrouvent sur la source corrigée
([`docs/V4_CONVERGE.md`](docs/V4_CONVERGE.md), 11.9).*

### Un code optimisé convergent (v4, point 4 ; dans le classement de la v4)

*Dans le classement de la v4 : le plafond de chaque cellule prend la meilleure forme admise (C1 à C6) ; avec les seules
formes publiées, C serait 1er et C++ 4e ([`docs/V4_FINAL.md`](docs/V4_FINAL.md), 12.3). Ce qui suit décrit le point 4,
mesuré à côté du classement de la v3.*

Le plafond (40 % du score au centre) prend la meilleure variante optimisée de chaque langage : il dépend aussi de
l'effort mis dans chaque implémentation. Les remarques avaient trouvé de meilleures formes pour une quinzaine de
langages, gardées hors du classement et jamais tentées ailleurs. Le point 4 de la v4 a dressé un catalogue des formes
de la frontière et de celles que les remarques ont mesurées (20 formes, réserves de fils comprises), l'a porté dans
les 25 langages (230 formes écrites, 87 déjà présentes, 61 non écrivibles, preuve à l'appui, et 17 formes propres à un
runtime), et a mesuré l'effet de la règle qui s'appliquera dans la campagne finale : le plafond prend la meilleure
forme admise. Une seule campagne, sur un même hôte (Emerald Rapids, machine 33 : 3 096 processus en trois passes, base
comprise), avec un plan et une analyse fixés avant les mesures ([`docs/V4_CONVERGE.md`](docs/V4_CONVERGE.md),
[`results/report_converge.md`](results/report_converge.md)). Avant le portage, les sources publiées ont reçu les
corrections que le classement publié leur applique (errata des points 2 et 3, ci-dessus). Le classement ci-dessus ne
change pas.

| Publié | Langage | Cet hôte | Convergent | Choix sur une passe | Remarques seules | Convergent, R4 | Source non corrigée |
|---|---|---|---|---|---|---|---|
| 1 | C | 1 | 2 | 4 | 1 | 3 | 1 |
| 2 | Odin | 5 | 6 | 6 | 5 | 5 | 5 |
| 3 | C++ | 2 | 1 | 1 | 2 | 1 | 3 |
| 4 | C3 | 3 | 3 | 2 | 3 | 4 | 2 |
| 5 | Zig | 6 | 4 | 3 | 8 | 2 | 6 |
| 6 | Rust | 7 | 8 | 8 | 6 | 7 | 8 |
| 7 | Nim | 8 | 7 | 7 | 7 | 6 | 7 |
| 8 | D | 4 | 5 | 5 | 4 | 8 | 4 |
| 9 | Ada | 9 | 9 | 9 | 9 | 10 | 10 |
| 10 | Chapel | 10 | 11 | 11 | 10 | 9 | 9 |
| 11 | Fortran | 13 | 12 | 13 | 11 | 11 | 14 |
| 12 | Swift | 12 | 14 | 14 | 13 | 14 | 11 |
| 13 | Julia | 14 | 13 | 12 | 14 | 12 | 13 |
| 14 | Mojo | 11 | 10 | 10 | 12 | 13 | 12 |

Les onze suivants restent à une place au plus de leur rang publié dans chacun de ces calculs, sauf FreePascal, 18e
avec R4.

* **La convergence ne déplace aucun langage de plus de deux places.** C++ passe 1er, Zig gagne deux places
  (6e → 4e), Swift en perd deux (12e → 14e) ; derrière C++, C, C3 et Zig sont à égalité. Les scores des compilés
  montent de 5 points en médiane (C++ : + 8,8), par le plafond.
* **Deux noyaux font l'essentiel.** Dans K4, le SIMD explicite du point 3 et une forme par mots de 64 bits (celle de
  Swift) mettent seize langages entre 0,58 et 0,77 ms, à la bande passante d'un cœur. Dans K8, l'arbre construit et
  sommé avec une pile explicite, ou construit avec l'état passé par valeur, divise le temps de 22 langages par 1,1 à
  4,5 : seize font K8 en 63 à 123 ms, quand seul Ada était sous 180 ms avec les formes publiées, et C++ (62,5 ms) passe
  devant Ada (73,2). Les réserves de fils améliorent les cellules à quatre fils de 15 à 18 langages. K5 et K7 bougent
  peu : les formes du catalogue y étaient déjà présentes dans la plupart des langages.
* **Les remarques seules ne faisaient presque rien** : avec les seules formes que chaque remarque avait trouvées pour
  son langage, les scores montent de 0,4 point en médiane, contre 5 avec la convergence. Le gain vient des formes
  portées d'un langage à l'autre.
* **Choisir le minimum parmi plus de formes ajoute peu par hasard.** Choisies sur une passe et estimées sur les deux
  autres, les formes changent les rangs espérés de 0,4 au plus ; C, C3 et Zig, à égalité, y échangent leurs places
  (C 4e), ce qui fait bouger C de trois places par rapport à « Cet hôte ».
* **Avec K3 rapporté à la boucle de référence (R4), Zig passe 2e et D 8e**, comme au point 3.
* **L'erratum des points 2 et 3 compte peu.** Sur cet hôte, la source non corrigée et la source corrigée donnent des
  classements à deux places au plus l'un de l'autre, alors que des cellules changent beaucoup (harnais de K9 à quatre
  fils : × 1,9 à 2,7 pour huit langages ; K4 naturel de Haskell : × 10,7). Contre le classement publié, la source
  corrigée déplace encore D (8e → 4e), Odin (2e → 5e) et Mojo (14e → 11e) ; Fortran et Zig, qui reculaient de trois
  places aux points 2 et 3, non : le premier par les corrections, le second par l'hôte.

### Le coût d'accès au plafond (v4, point 5 ; à côté du classement)

*Dans le classement de la v4 : la grille reste en place, décision de l'auteur de l'étude (22 novembre) ; le coût d'accès
au plafond est publié à côté.*

Le plafond prend la forme la plus rapide de chaque langage, quel qu'en soit le prix ; la grille (catégories C et E)
note les leviers qu'offre le langage. Le point 5 de la v4 a mesuré, sur les sources du point 4, ce que coûte
d'atteindre le plafond : dans chacune des 12 cellules du plafond, les lignes de la forme la plus rapide contre celles
du code naturel, la part de ces lignes qui s'exécute sans vérification de sûreté mémoire, et la présence d'une
construction propre à x86, contrôlée en compilant pour aarch64 et riscv64. Un indice d'accès (0 à 1) combine ces trois
coûts dans les cellules où le langage atteint 90 % de la frontière. Relevé statique de 562 formes (618 régions), plan,
règles de lecture et écarts fixés avant tout comptage ([`docs/V4_COST.md`](docs/V4_COST.md),
[`results/report_cost.md`](results/report_cost.md)). Le classement ci-dessus ne change pas.

| Publié | Langage | Convergent, R4 | Accès | Indice d'accès | Cellules atteintes | L/N | Sans vérif. | Non portables |
|---|---|---|---|---|---|---|---|---|
| 1 | C | 3 | 4 | 0,160 | 9 | 3,52 | 1,00 | 9 |
| 2 | Odin | 5 | 3 | 0,402 | 8 | 3,73 | 0,50 | 0 |
| 3 | C++ | 1 | 2 | 0,285 | 7 | 3,45 | 1,00 | 1 |
| 4 | C3 | 4 | 5 | 0,314 | 8 | 3,70 | 1,00 | 0 |
| 5 | Zig | 2 | 1 | 0,239 | 6 | 3,71 | 1,00 | 0 |
| 6 | Rust | 7 | 7 | 0,218 | 8 | 5,14 | 0,39 | 9 |
| 7 | Nim | 6 | 6 | 0,239 | 8 | 6,88 | 0,39 | 9 |
| 8 | D | 8 | 8 | 0,163 | 5 | 5,39 | 1,00 | 1 |
| 9 | Ada | 10 | 12 | 0,164 | 5 | 3,62 | 0,50 | 6 |
| 10 | Chapel | 9 | 9 | 0,169 | 8 | 3,82 | 1,00 | 8 |
| 11 | Fortran | 11 | 11 | 0,130 | 3 | 1,87 | 1,00 | 0 |
| 12 | Swift | 14 | 13 | 0,243 | 4 | 3,20 | 0,33 | 0 |
| 13 | Julia | 12 | 14 | 0,271 | 5 | 6,45 | 0,87 | 0 |
| 14 | Mojo | 13 | 10 | 0,497 | 8 | 2,33 | 0,16 | 0 |

« Convergent, R4 » : le calcul du point 4 avec K3 rapporté à la boucle de référence ; « Accès » : le même, avec
l'indice à la place de chaque capacité des catégories C et E. L/N : lignes de la forme la plus rapide sur lignes du
code naturel, moyenne géométrique des 12 cellules ; « Sans vérif. » : part de ces lignes sans vérification de sûreté
mémoire (1 dans les huit langages dont le mode publié ne vérifie pas les bornes) ; « Non portables » : cellules dont la
forme la plus rapide porte une construction propre à x86. Les onze suivants restent à deux places au plus de leur rang
« Convergent, R4 » ; Java atteint 3 cellules (indice 0,240), C# 3 (0,168), Go 3 (0,116), FreePascal et Haskell 1, les
langages interprétés et OCaml aucune.

* **Atteindre le plafond coûte des lignes partout.** La forme la plus rapide a 3,5 fois les lignes du code naturel
  (médiane des 25 langages ; de 1,3 en Lua à 6,9 en Nim), et seules sept cellules sur 300 ont le code naturel pour forme
  la plus rapide. L'indice est donc bas partout : 0,50 au plus.
* **Mojo et Odin atteignent le plafond au meilleur prix** : 8 cellules chacun, sans construction propre à x86 (leurs
  formes vectorielles compilent pour aarch64 et riscv64), Mojo avec le moins de lignes ajoutées des langages qui
  atteignent 8 cellules ou plus, et peu de code sans vérification ; C3 aussi, mais sans aucune vérification. C atteint
  le plus de cellules (9), mais sans aucune vérification, et 9 de ses 12 formes les plus rapides portent des
  intrinsèques x86, comme 9 de celles de Rust et de Nim (8 cellules chacun). Julia paie ses formes vectorielles en IR
  de LLVM (L/N 6,45, 87 % des lignes sans vérification). Java atteint 3 cellules sans une ligne sans vérification ni
  propre à une architecture.
* **Remplacer les catégories C et E par l'indice ne déplace qu'un langage de plus de deux places** : Mojo, 13e → 10e.
  Zig passe 1er devant C++, Odin 3e, C 4e. La part marginale, la part sans vérification retirée, la forme la plus
  courte et les lexèmes donnent le même résultat ; le seuil de 0,8 déplace Odin (2e), Swift (10e) et Ada (13e).
  Remplacer la grille entière bouleverse le haut : Odin 1er, C3 2e, C++ 3e, Mojo 4e, Zig 5e, C 8e.
* **L'indice mesure autre chose que la grille.** Sur les 25 langages, il suit les catégories C et E (ρ de Spearman
  0,69 et 0,68), mais par les six langages qui n'atteignent aucune cellule ; sur les 19 autres, ρ tombe à 0,30 et 0,38.
  La grille note les leviers qu'un langage offre ; l'indice, ce que coûte de s'en servir.
* **La compilation croisée confirme l'examen statique** : les 18 compilations interprétées (9 langages, aarch64 et
  riscv64) acceptent ou refusent la source exactement comme prévu ; D ne refuse que pour un seul builtin x86 (K4).
* **La grille est gardée** (décision de l'auteur de l'étude, 22 novembre) : l'indice d'accès est publié à côté, et
  non à sa place. Son effet sur l'ordre est faible, il compterait une seconde fois une part du plafond (les cellules
  atteintes) et ferait de l'absence de vérification de huit langages un coût de chaque forme
  ([`docs/V4_COST.md`](docs/V4_COST.md), 11.7).

### Une piste ouverte : les bibliothèques tierces (v4, point 6 ; à côté du classement)

*Dans le classement de la v4 : la piste ouverte reste à côté, décision de l'auteur de l'étude (22 novembre) ; ses formes
ne sont pas remesurées dans la campagne finale.*

Le classement n'admet que la bibliothèque standard et note « absente » une capacité qu'offre seulement une
bibliothèque tierce. Le point 6 de la v4 pose l'autre question, celle de l'écosystème, sur une liste fixée par une
règle commune avant toute mesure : pour chaque case de la grille que la bibliothèque standard laisse vide, la première
bibliothèque admise parmi les dix plus employées du registre du langage, plus celles que nomme le dossier (NumPy, la
crate `libc`, MAX…). 47 bibliothèques dans 17 langages comblent 47 cases ; une sonde par case donne sa note (41 montent)
et 40 formes nouvelles du plafond s'en servent dans 12 langages, mesurées sur un même hôte à côté de la forme la plus
rapide du point 4 et reportées sur sa campagne. Plan, relevé et écarts : [`docs/V4_OPEN.md`](docs/V4_OPEN.md) ;
résultats : [`results/report_open.md`](results/report_open.md). Le classement ci-dessus ne change pas.

| Publié | Langage | Convergent, R4 | Ouverte | Plafond ouvert seul | Grille ouverte seule | Nommées seules | Cases à ½ |
|---|---|---|---|---|---|---|---|
| 1 | C | 3 | 3 | 3 | 3 | 2 | 2 |
| 2 | Odin | 5 | 7 | 5 | 7 | 6 | 7 |
| 3 | C++ | 1 | 2 | 1 | 2 | 1 | 1 |
| 4 | C3 | 4 | 6 | 4 | 6 | 5 | 6 |
| 5 | Zig | 2 | 4 | 2 | 4 | 3 | 3 |
| 6 | Rust | 7 | **1** | 7 | **1** | **4** | **4** |
| 7 | Nim | 6 | 5 | 6 | 5 | 7 | 5 |
| 8 | D | 8 | 8 | 8 | 8 | 8 | 8 |
| 9 | Ada | 10 | 10 | 10 | 10 | 12 | 10 |
| 10 | Chapel | 9 | 9 | 9 | 9 | 9 | 9 |
| 11 | Fortran | 11 | 13 | 12 | 13 | 11 | 11 |
| 12 | Swift | 14 | 14 | 14 | 14 | 14 | 14 |
| 13 | Julia | 12 | 11 | 11 | 11 | 13 | 12 |
| 14 | Mojo | 13 | 12 | 13 | 12 | **10** | 13 |

« Ouverte » : grille et plafond ouverts ; « Nommées seules » : les seules bibliothèques nommées par le dossier ;
« Cases à ½ » : chaque case comblée par une bibliothèque vaut ½. En gras : plus de deux places d'écart avec
« Convergent, R4 ». Les onze suivants (C# à Lua) gardent leur place dans tous les calculs, Python (24e) et Lua (25e)
compris.

* **Mesurées, les bibliothèques changent peu le plafond.** Elles ne battent la forme la plus rapide de la bibliothèque
  standard que dans 13 cellules sur 35, et de beaucoup seulement en Python (NumPy : de 5 à 70 fois plus rapide dans
  huit cellules) et en Lua (vmsl sur K5, 18 fois) ; ces deux langages restent de 5 à 48 fois plus lents que la
  frontière, où l'échelle du plafond ne leur donne presque rien. Ailleurs, la bibliothèque est au mieux à 3 % de la
  forme standard (Bumper en Julia, MAX en Mojo), souvent plus lente (gonum × 12 sur K9, amphp × 24 sur K9 mt, l'appel C
  par élément d'`ocaml_intrinsics_kernel` × 7 sur K4). Le plafond ouvert seul ne déplace personne de plus de deux
  places.
* **La grille fait tout le déplacement : Rust passe 1er.** L'écosystème de Rust comble huit cases de sa grille (bumpalo,
  fearless_simd, rayon, cache-padded, core_affinity, ndarray, hwlocality-sys, libc) ; aucun autre langage ne bouge de
  plus de deux places. Avec les seules bibliothèques nommées, ou avec des cases comblées à ½, Rust est 4e, et Mojo monte
  de 13e à 10e avec MAX seul.
* **Moins de lignes, pas plus de vitesse** : 25 des 40 formes ont moins de lignes que la forme standard la plus rapide
  (NumPy : une à treize lignes dans les cellules à un fil), mais le gain de lignes va rarement avec un gain de temps.
* **La piste ouverte reste à côté** (décision de l'auteur de l'étude, 22 novembre) : elle n'est pas une seconde colonne
  du classement. Son seul effet tient à des notes de grille d'un langage, et la partie mesurée ne déplace personne
  ([`docs/V4_OPEN.md`](docs/V4_OPEN.md), 11.5).

## Pourquoi cet ordre, langage par langage

*Chiffres du calcul « Final », au centre ([`results/report_final.md`](results/report_final.md)) : plafond par noyau sur
100 (K6 réunit Q6 et Q1, à un et quatre fils ; K9 le stencil à un et quatre fils), parts du code par défaut sur 100
(D1 : code naturel ; D2 : empreinte et désordre de K1 ; D3 : queues de latence de K8 ; D4 : hiérarchie mémoire),
contrôle en règle v2. Les mécanismes, mesurés pendant la v3 et les points de la v4, sont détaillés dans l'explication du
classement de la v3 ([`docs/RANKING_V3.md`](docs/RANKING_V3.md)) et dans le document de chaque langage.*

### En tête : C++ et C, à égalité de fait

**C++** (78,9 points) et **C** (78,3) se départagent dans la moitié des variantes chacun (C++ devant dans 51 %). Ils ont
les deux contrôles les plus riches (92,4 et 91,7) et deux des trois meilleurs plafonds (85,0 et 83,1, derrière Chapel),
mais pas sur les mêmes noyaux : l'arène de K8 de C++, récursive, son état passé par valeur (`tuned_val`), fait la
frontière de K8 (C : 66, avec son arène écrite par itération, la plus rapide sous clang ; g++ compile bien mieux la
récursion de l'arène : « Ce qui sépare vraiment les langages », 4), et C++ atteint b3 sur K3 (C : 87) ; C a les
meilleurs K4 et K7 (98 et 97, contre 79 et 80), et le meilleur code naturel (D1 20, C++ 14, 9e). La forme optimisée de
K4 admise par R3 réduit l'écart que le vectoriseur de g++ laissait à C++ sur ce noyau, sans le combler. Sans les formes
du catalogue (C1), C est 1er et C++ 4e ; sur les seules mesures, C est 1er, C++ 3e.

### Le peloton des langages compilés à types valeur

**Odin** (3e) doit sa place à son contrôle (84,0, 5e : `#soa`, `#simd`, intrinsèques de LLVM, allocateurs explicites) et
à son code naturel (5e) ; son plafond n'est que 10e (77,6 : K4 70, K8 67, K3 82), et sur les seules mesures il est 6e.
**Rust** (4e, deux places de mieux qu'en v3) a le meilleur code par défaut (54,1 : D1 19, 2e ; D3 68, parmi les queues
de latence de K8 les plus courtes) et le 6e plafond (80,5) ; son contrôle (73,6, 9e) reste limité par sa bibliothèque
standard (ni affinité, ni `mmap`) ; sans la grille, il est 2e. **C3** (5e) a le 5e plafond (80,9 ; K3 au niveau de b3,
K7 96) et le 6e code naturel ; son contrôle (75,7, 8e) n'a ni SoA ni intrinsèques officiels. À trois tailles sans les
autres règles de la v4, il serait 1er. **Nim** (6e) a le meilleur K1 (98), le 7e plafond et le 4e code par défaut. **D**
(7e) a le 4e plafond (81,1) et le 4e contrôle (87,1), mais les pires queues de latence de K8 des 19 premiers (D3 : 2 sur
100, les pauses de son ramasse-miettes) : 3e au score, il n'est que 7e au rang, et 9e sur les seules mesures. **Zig**
(8e) a le 3e contrôle (87,2), mais son code naturel, compilé en `-O safe` sous R1, n'est que 11e (D1 11), et son plafond
11e (76,8 ; vectoriseur de boucles désactivé en 0.17) : sans R1 il serait 5e, et 12e sur les seules mesures. **Ada**
(9e) : disposition au bit près, 6e contrôle, 8e plafond et les queues de latence de K8 les plus courtes après Fortran
(D3 70), mais un code naturel 10e, ses vérifications à l'exécution actives.

### Forts sur leur terrain, avec moins de contrôle ou un runtime

**Chapel** (10e) a le 1er plafond (87,5 : K9 98, K4 90, K6 81), mais un code naturel 16e (D1 8, sous `--checks`) et un
contrôle 16e (61,8 : leviers bas niveau rares ou instables) ; sans la grille, il est 7e. **Fortran** (11e, à égalité de
fait avec Julia) a les queues de latence de K8 les plus courtes (D3 73) et le 3e code par défaut, un plafond 9e, mais ni
SIMD explicite ni intrinsèques (K4 50, par une forme SWAR) : contrôle 14e. **Julia** (12e, une place de mieux qu'en v3)
a le 3e code naturel et un plafond relevé par les formes du catalogue (74,4, contre 62,3 en v3), mais les pauses de son
ramasse-miettes pèsent sur les latences de K8 (D3 10). **Swift** (13e) a le meilleur K5 (97 : types SIMD de la
bibliothèque standard), mais le K4 le plus lent des 14 premiers (46) et des vérifications de `-O` qui coûtent au code
naturel (14e) ; son plafond passe de 80,3 (3e en v3) à 75,4 (12e). **Mojo** (14e) : le SIMD au cœur du langage (K5 92,
K7 95, K3 au niveau de b3), mais ni vectoriseur de boucles (K4 50) ni threads publics dans `std`, et K8 46.

### Ramasse-miettes imposé, objets en références, et FreePascal

**C#** (15e) a la boîte à outils la plus riche des langages à GC : son plafond passe de 53,6 en v3 à 67,5 avec la forme
optimisée de K4 (20 fois plus rapide que ses formes publiées), les réserves de fils et l'arène itérative de K8 du
catalogue ; ses objets en références coûtent sur K7 (54), K8 (50) et le désordre de K1 (D2 58). **Go** (16e, deux places
de mieux qu'en v3) : structures par valeur et SIMD expérimental (K4 82), mais des écritures atomiques séquentiellement
cohérentes (K3 30) et un code naturel 18e. **FreePascal** (17e) a un contrôle de langage système (62,3, 15e : records
`packed`, assembleur, mémoire à la main) et le 12e code par défaut, mais le 19e plafond (41,6) : ni vectoriseur ni
intrinsèques (K4 14, K5 39). **Java** (18e) a les queues de latence de K8 les plus courtes des langages à
ramasse-miettes (D3 59) et la Vector API (K5 84), mais pas de types valeur (K1 45, D2 58) et le 18e contrôle. Go,
FreePascal et Java se suivent à 1,1 point, à égalité de fait. **Haskell** (19e) peut descendre bas (FMA vectorielle de
GHC : K5 91 ; K7 90), mais son code par défaut est boxé et son ramasse-miettes imposé (19e code par défaut et 19e
contrôle).

### Le dernier étage : la machine disparaît derrière le langage

**OCaml** (20e) garde une bonne allocation générationnelle (D3 46), mais n'a ni types valeur, ni flottant 32 bits de
calcul, ni SIMD (plafond 21,4). **BQN** (21e) : les primitives vectorisées de CBQN, mais un coût fixe par appel, ni
threads, ni flottant 32 bits (plafond 10,5) ; à égalité de fait avec **JavaScript** (22e, une place de mieux qu'en v3),
dont les tableaux typés sont compilés mais vérifiés, sans SIMD (plafond 14,6, contrôle 24e). **PHP** (23e) : chaque
valeur est un zval de 16 octets, chaque objet une référence (plafond 6,3) ; son contrôle, celui d'un langage dynamique
doté d'une FFI et de processus (27,4), est un peu plus faible que celui de Python, mais son plafond et son code par
défaut le tiennent devant lui. **Python** (24e) : CPython seul, le plafond le plus bas (1,0), un contrôle de 29,7.
**Lua** (25e) : PUC-Lua sans son API C, presque aucun levier (contrôle 6,8), mais un plafond (1,4) au-dessus de celui de
CPython.

## Ce qui sépare vraiment les langages

Les résultats les plus solides de l'étude : chacun isole une cause, avec ses conditions.

1. **Les données d'abord.** Une particule de 64 octets en occupe 64 dans 15 langages, 78 en Java, 88 en C#, 128 en
   BQN (sans flottant 32 bits), 144 en OCaml, 352 en PHP, 416 en JavaScript et 750 en Python. Parcourir une
   collection de références dans le désordre coûte 4,7 à 7,0 fois plus (C#, Java, JavaScript, OCaml) ; avec des types
   valeur, l'ordre ne change rien.
2. **Le SIMD explicite** divise le produit scalaire par 20 à 40 : 3,7 à 5,7 ms dans les langages compilés, en C# et
   en Java (Vector API, sur des données alignées hors tas), contre 77 à 166 ms pour la boucle naturelle en ordre strict
   (Emerald Rapids). Go (expérimental, 7,2 ms) suit ; OCaml, JavaScript, BQN et PHP n'en ont pas (la somme
   vectorielle de la bibliothèque de BQN, `•math.Sum`, prend 33 ms).
3. **La vectorisation automatique se vérifie sur le code exécuté.** Aucune des deux boucles naturelles testées n'est
   vectorisée en C#, Go, Mojo (dont le compilateur n'a pas de vectoriseur de boucles), Zig 0.17 (vectoriseur de boucles
   désactivé par l'équipe Zig, réactivé dans la version de développement), Swift, Haskell, OCaml, JavaScript, PHP
   (dont le JIT, depuis 8.4, échoue à compiler la boucle du stencil et la laisse à l'interprète), Lua et Python. En BQN, les boucles chaudes sont celles
   des primitives, écrites à la main en Singeli : celle du stencil est vectorisée, celle de K4 (le filtre, une
   compression par `vpshufb`) compte comme scalaire, la règle ne retenant que l'arithmétique empaquetée.
   Les vérifications de bornes l'empêchent sur le stencil naturel en Ada (71 ms, contre 36 ms) ; en D (56 ms, sans
   vérifications) et en Rust (73 ms, scalaire même sans elles), c'est l'aliasing : ni LDC ni rustc ne transmettent de
   règle de type à LLVM, et les pointeurs de lignes sont relus après chaque écriture ; en Nim (71 ms), ce sont les deux,
   vérifications et `-fno-strict-aliasing`, que Nim impose au compilateur C ; en Ada, sur un type contraint,
   GNAT élimine les vérifications et vectorise. En Mojo, elles coûtent plus que l'absence de vectorisation : sans elles,
   le stencil naturel passe de 169 à 41 ms (C : 28 ms) et Q1 de 137 à 67 ms, au niveau de C (même machine). En Swift,
   `-O` garde sur K4 un branchement par octet et un test de débordement par addition, et sur le stencil `[[Double]]`
   un test de bornes par lecture et un test d'unicité de la ligne (copie sur écriture) par écriture ; `-Ounchecked`,
   qui retire les vérifications de bornes et de débordement, divise K4 naturel par 5,8, le stencil par 1,2 seulement ;
   écrite avec `&+=`, la boucle de K4 est vectorisée et va au rythme du C. Le contexte
   d'appel compte aussi : inlinés dans la boucle de mesure, les deux noyaux de K4 de Fortran restaient scalaires, alors
   que leurs copies hors ligne, vectorisées, n'étaient jamais appelées (corrigé).
4. **Le compilateur pèse autant que le langage.** Sur le même code C, GCC est 2,2 à 2,7 fois plus rapide que clang sur
   l'arène de K8, construite par récursion ; écrite par itération, elle va plus vite sous clang que sous GCC (116
   contre 135 ms sur Emerald Rapids, [`docs/C.md`](docs/C.md)). Sur Emerald Rapids, clang, flang, Chapel et Mojo
   fusionnent la réduction naturelle de K5 en FMA scalaire, deux fois plus lente qu'une addition sur ce cœur ; GCC
   l'évite. Sur Cascade Lake, l'écart disparaît.
5. **Le placement du code aussi.** Sur Emerald Rapids, la boucle de l'écrivain unique (K3) coûte 1 ou 7 cycles par
   incrément selon son alignement. Huit dispositions tirées au hasard par l'éditeur de liens donnent 12 à 23 ms ou 74
   à 117 ms pour le même source en C (clang) ou en Rust ; le code de GCC reste rapide dans les huit.
6. **Concurrence.** Go, Haskell et OCaml n'ont que des écritures atomiques séquentiellement cohérentes : l'écrivain
   unique y est 6 à 7 fois plus lent qu'en C. JavaScript non plus n'en a pas d'autres, et V8 appelle en plus une
   fonction interne à chaque opération atomique : 26 fois C sous Node, 8 fois sous Bun. Dans le build par défaut de
   CPython, le verrou global sérialise les threads (sur K3, à peine plus d'un cœur sur quatre travaillait, pour 24 000
   `futex` par répétition, Emerald Rapids) ; des sous-interpréteurs, un verrou chacun, travaillent en parallèle et
   font apparaître le faux partage que le verrou masquait (3,0 fois en écriture unique). BQN n'a ni threads ni
   atomiques : K3 s'y exécute en séquence (211 fois C en écriture unique, compteurs espacés). PHP non plus : ses noyaux
   parallèles passent par des processus, et K3 par des sémaphores System V et des copies de mémoire partagée, des
   appels système (409 fois C en écriture unique, compteurs espacés).
7. **Allocation.** Une arène divise K8 par 5 ou 6. Les allocateurs générationnels de Java et d'OCaml sont les
   meilleurs pour du code naturel (302 et 334 ms). Les ramasse-miettes laissent des queues (K8 remesuré sur Emerald
   Rapids) : pause de 89 ms en D, p99,9 à 30 fois la médiane en Julia, arrêt de 0,76 s en Python. En PHP, le collecteur
   de cycles prend les trois quarts d'un simple parcours d'objets (K1 naturel), sans rien libérer. Les runtimes font
   des centaines à des dizaines de milliers d'appels système par répétition, le code compilé un ou deux.
8. **Le système compte.** Odin, Lua et LuaJIT font un appel système à chaque lecture d'horloge (pour Odin, 32 768
   appels par répétition de K8, de l'ordre de 3 ms sur 1,9 s : moins de 1 %). Sur K7, Rust, Zig, Odin et flang rendent
   la mémoire de leur table au système à chaque répétition, et la paient en défauts de page (1 à 5 % du temps).

## Comment c'est mesuré

*Méthode du classement de la v4 ([`docs/V4_FINAL.md`](docs/V4_FINAL.md)) ; celle de la v3, mesurée sur plusieurs
hôtes, est décrite avec son classement ([`docs/RANKING_V3.md`](docs/RANKING_V3.md)).*

**Neuf noyaux notés**, un par principe (spécification : [`docs/SPEC.md`](docs/SPEC.md)), sept d'entre eux à trois
tailles depuis la v4 ([`docs/V4_SIZES.md`](docs/V4_SIZES.md)) :

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

Un dixième noyau (file SPSC façon Disruptor), hors score depuis la v2, n'est plus mesuré.

* **Des formes par noyau et par langage** : `natural`, le code idiomatique ([`docs/NATURAL.md`](docs/NATURAL.md)),
  `tuned`, la version optimisée publiée, et, depuis la v4, les formes d'un catalogue commun, portées dans chaque
  langage qui le permet, avec la seule bibliothèque standard : le plafond prend la meilleure forme admise (règles C1 à
  C6, [`docs/V4_CONVERGE.md`](docs/V4_CONVERGE.md)). Toutes doivent rendre, à chaque taille, le résultat de
  l'implémentation C, au bit près pour les entiers. Un temps sous la borne physique de la machine est rejeté.
* **Des conditions égales** ([`docs/V4_EQUAL.md`](docs/V4_EQUAL.md)) : le code naturel est compilé dans le mode de
  publication de chaque chaîne, avec les vérifications à l'exécution qu'elle offre (R1 : C, C++, Fortran, Zig, C3, D,
  Chapel et FreePascal les reçoivent par leur option documentée) ; le stencil naturel est en grille contiguë pour tous
  (R2) ; K4 admet une forme optimisée, aucune forme n'est en assembleur en ligne (R3) ; K3 est rapporté à b3, le
  temps d'une boucle de référence mesurée sur la machine juste avant et juste après chaque groupe de K3 (R4) ; K2 (R5)
  et les latences de K8 reposent sur sept processus par cellule.
* **Chaînes de compilation** : les dernières versions stables au 28 octobre 2026, Swift 6.4.2, ajouté le
  5 novembre, Free Pascal 3.2.2 et CBQN 0.12.0 (BQN), ajoutés le 6, PHP 8.5.12, ajouté le 7
  ([`env/toolchains.txt`](env/toolchains.txt)), compilation pour le CPU hôte, ni PGO ni LTO ; chaque binaire est
  construit depuis les fichiers suivis par git, et son empreinte enregistrée.
* **Une machine** : toutes les cellules des 25 langages, à toutes les tailles, sont mesurées sur la même machine
  (machine 35 : une VM Firecracker à 4 vCPU sur un Xeon Emerald Rapids, caractérisée au repos,
  [`results/hw/machine35`](results/hw/machine35)), en trois passes dont l'ordre des groupes et des blocs est tiré au
  hasard : 9 738 processus, du 22 novembre, 17 h 16, au 23 novembre, 19 h 40 (UTC). Pas de compteurs matériels ; les
  compteurs du noyau (appels système, défauts de page, uprobes) servent aux faits de mécanisme
  ([`docs/INSTRUMENTS_V3.md`](docs/INSTRUMENTS_V3.md)).
* **Score** :
  * **Contrôle (35 %)** : 34 capacités (disposition, SIMD, mémoire, concurrence, abstractions sans coût,
    prévisibilité…), notées 0, ½ ou 1 selon ce que livre la chaîne de référence, chaque case appuyée sur une sonde ou
    une mesure ([`docs/CAPABILITIES.md`](docs/CAPABILITIES.md), [`docs/GRID_AUDIT.md`](docs/GRID_AUDIT.md)) ;
  * **Plafond (40 %)** : pour chacune des douze mesures, à chaque taille, le meilleur temps du langage rapporté à la
    référence de cette taille (le meilleur des 25 langages, ou la borne physique du niveau de mémoire où tiennent les
    données), moyenné sur les trois tailles, puis la moyenne géométrique des douze ;
  * **Code par défaut (25 %)** : la variante naturelle rapportée à la même référence (50 %), l'empreinte et la
    pénalité de désordre d'une collection naturelle (15 %), la latence de queue de l'allocation (15 %), la
    visibilité de la hiérarchie mémoire (20 %).
* **Incertitude** : bootstrap de 2 000 tirages sur les processus pour le bruit de mesure ; 20 000 variantes de
  l'analyse, qui tirent les poids des piliers, ceux des trois tailles, les normalisations et le jugement porté sur
  chaque capacité. La v4 n'a pas de réplication sur un second hôte : la v3 en avait une.
* **Garde-fous** : plans d'analyse poussés sur GitHub avant les mesures et les calculs, deux audits externes et des
  relectures langage par langage vérifiés point par point, écarts datés et journal de tous les écarts au protocole
  ([`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)).

## Limites

*Limites du classement de la v4 ; celles de la v3 (ponts entre hôtes, corrections reportées par rapports, une taille par
noyau) sont gardées avec son classement ([`docs/RANKING_V3.md`](docs/RANKING_V3.md)).*

* **Une machine.** Un seul processeur Intel (Emerald Rapids), virtualisé et partagé ; ni AMD, ni ARM, ni compteurs
  matériels. La v3 répliquait son classement sur une seconde micro-architecture ; la campagne finale n'a pas de second
  hôte, et ses étages suivent la règle de la v3 sans sa condition de réplication. Des machines du même modèle diffèrent
  (b3 de 69,4 à 85,1 ms, bande passante à quatre fils, L3 effectif : [`docs/V4_FINAL.md`](docs/V4_FINAL.md), 2) : le
  classement est celui d'une machine, mesurée en une fois.
* **Une machine dont la vitesse varie.** Deux exécutions successives de la boucle de référence de K3 diffèrent jusqu'à
  27 % sur la machine 35, et l'écart touche tous ses décalages à la fois. La médiane par processus, trois processus par
  cellule (sept pour K2 et les latences de K8), l'ordre tiré au hasard et le rééchantillonnage en tiennent compte ; R4
  retire de K3 la part commune à un groupe, pas celle d'un processus.
* **Six cellules hors mémoire.** À la grande taille, les quatre variantes de K1 de BQN et K1 naturel (dans l'ordre et
  permuté) de Python dépassent la limite de mémoire de la machine (13,35 Gio pour le groupe de processus, données
  comprises) ; l'analyse leur donne le temps admissible le plus lent des autres langages (règle du point 2), ce qui les
  flatte sans doute. La grande taille est bornée par cette mémoire : 1 Gio de données au plus.
* Des implémentations écrites par un seul auteur, sans relecture experte au départ ; les 25 langages ont été relus après
  coup par des connaisseurs, et ces relectures ont corrigé des erreurs de mon banc et de ma grille (le détail est dans
  [`docs/RANKING_V3.md`](docs/RANKING_V3.md), « Limites (v3) »). Le catalogue commun du point 4, porté dans les 25
  langages, réduit l'écart d'effort sur le plafond ; il ne touche pas le code naturel, dont le choix reste le mien
  ([`docs/NATURAL.md`](docs/NATURAL.md)).
* Des microbenchmarks : ni E/S, ni décompression, ni tri ou jointure.
* Des règles de construit : bibliothèque standard seule, compilation pour le CPU hôte, ni PGO ni LTO, réglages des
  runtimes par défaut, sauf le nombre de fils, fixé aux quatre cœurs pour tous les noyaux (`-t 4` pour Julia, `+RTS -N4`
  pour Haskell ; Go et Java les prennent d'eux-mêmes) : le ramasse-miettes de Julia et de Haskell y devient parallèle,
  même pour les noyaux séquentiels ([`docs/HASKELL.md`](docs/HASKELL.md)).
* Une seule règle pour la libc et les FFI : compte ce que la chaîne livre, y compris les intrinsèques et builtins du
  compilateur qu'un langage importe par sa FFI (Nim, Chapel, C3, Odin) ; les types C qu'une FFI livrée définit
  (`ctypes`, FFM, FFI de PHP) valent ½ ; appeler du code C ordinaire par une FFI ne compte pas, sauf pour C et C++, dont
  la libc est la bibliothèque système. L'affinité, `mmap` et la taille de ligne de cache valent donc 0 à Rust, qui doit
  les appeler par sa FFI. La piste ouverte du point 6, où la libc et des bibliothèques tierces nommées d'avance comptent
  pour tous, est publiée à côté du classement (voir plus haut).
* La règle de la bibliothèque standard pèse sur Haskell (`vector`, `primitive`, `unordered-containers`, `hashtables`
  sont des paquets de Hackage ; d'où `Data.IntMap` pour K7), sur Mojo (`parallelize`, le GPU et les tenseurs sont dans
  le paquet MAX ; ses noyaux à threads passent par un module privé de `std`) et sur Python (NumPy, Numba, Polars ou
  DuckDB sont tiers ; le classement mesure CPython dans son build par défaut). PyPy n'est pas mesuré.
* Le pilier « contrôle » est jugé par un seul évaluateur. Depuis l'audit de la grille (v4, point 1), ses 850 cases
  reposent toutes sur une sonde exécutée (825) ou une mesure (25), contre 330 avant ; 161 ne sont prouvées que par une
  recherche d'absence dans les sources ou l'API livrées, qui ne voit que ce que son motif décrit
  ([`docs/GRID_AUDIT.md`](docs/GRID_AUDIT.md), [`docs/CAPABILITIES.md`](docs/CAPABILITIES.md), état de preuve).
* R1 égalise la politique des vérifications (le mode vérifié de chaque chaîne), pas leur liste, qui fait partie du
  langage : C ne vérifie que les tableaux de taille connue, C++ les conteneurs de libstdc++, et l'accès par pointeur
  reste sans vérification ([`docs/V4_EQUAL.md`](docs/V4_EQUAL.md), 3.1).
* Une seule version de compilateur par langage, la dernière stable au 28 octobre (Swift au 5 novembre, FreePascal et BQN
  au 6, PHP au 7), et un seul compilateur : Fortran est classé avec gfortran, C++ avec g++ 16 (le seul à livrer
  `std::simd`). Un réglage temporaire d'une chaîne peut coûter des rangs : Zig 0.17 désactive le vectoriseur de boucles
  de LLVM, que sa version de développement réactive ([`docs/ZIG.md`](docs/ZIG.md)).
* Le code naturel de K4 compte la vectorisation automatique : une boucle naturelle laissée scalaire y coûte, quelle
  qu'en soit la cause (pas de vectoriseur de boucles, vérifications, branchement gardé). Le plafond de K4 admet depuis
  R3 une forme optimisée, SIMD explicite compris, sans assembleur en ligne.
* La sensibilité « sans SIMD explicite » ([`docs/NOSIMD.md`](docs/NOSIMD.md)) a été calculée sur les données de la v3 ;
  elle n'est pas refaite sur celles de la v4.
* Trois échauffements au moins pour les langages à JIT (et au moins une seconde) : les boucles chaudes tournent souvent
  en code OSR, sans atteindre le niveau d'optimisation final (C# : 0 à 2,5 % en moyenne,
  [`docs/CSHARP.md`](docs/CSHARP.md) ; Java : le K7 optimisé isolé de sa boucle de mesure va 1,4 fois plus vite,
  [`docs/JAVA.md`](docs/JAVA.md)).

## Une autre étude, un autre ordre : pourquoi

Le « Banc de sympathie mécanique », une étude voisine faite sur le même processeur que ma machine 3, classe C 11e sur 18
langages communs, là où le classement de la v4 le place 2e, à égalité de fait avec C++ (la v3 le plaçait 1er).
Corrélation de rang entre les deux ordres : 0,74 (0,78 avec celui de la v3, 0,77 le 30 octobre). Je l'ai confrontée à la
mienne par quatre tests pré-enregistrés, faits sur le classement de la v3
([`docs/CONFRONTATION.md`](docs/CONFRONTATION.md)) :

* **Leur règle du « standard »** (une extension du compilateur, POSIX pour C, une option globale ou un module
  expérimental ne valent que le niveau 1 sur 4) appliquée à mon pilier contrôle classe C 12e, à un rang du leur
  (11e) ; C était 11e le 30 octobre, et les errata de Mojo ont depuis placé Mojo devant lui.
* **La même règle appliquée au code mesuré change peu la performance de C** : réécrit en C standard (sommes
  partielles au lieu des intrinsèques, `threads.h`, sans préchargement), il garde 94 % de son plafond. Elle coûte
  beaucoup à Java (sans la Vector API en incubation), à Go (sans le SIMD expérimental), et à Fortran et Mojo, qui
  n'ont pas de threads standard. À Chapel, 8 points de plafond, une fois ses réductions réécrites en sommes
  partielles comme celles des autres ; j'avais d'abord compté un produit scalaire 23 fois plus lent, faute de cette
  réécriture ([`docs/CHAPEL.md`](docs/CHAPEL.md)).
* **Les deux règles à la fois** : C passe 6e, la corrélation monte à 0,90. Le reste de l'écart tient à la question
  posée : leur score ne compte pas la vitesse. Mêler à peu près moitié de leur score au mien reproduit leur ordre.
* **Sur les faits, les deux grilles, notées indépendamment, s'accordent** (0,74 à 0,81 ; 0,83 à 0,88 le 30 octobre :
  les errata de ma grille, surtout ceux de Mojo et de Julia, l'en ont éloignée). Leurs désaccords portent presque tous
  sur ce que recouvre chaque principe.
* **Un second juge, à l'aveugle** (un sous-agent sans accès aux deux grilles ni à mes conclusions), retrouve ma grille
  du 30 octobre sous ma règle (kappa pondéré 0,75) comme sous la leur (0,80 ; 0,87 et 0,86 sur ma grille corrigée
  depuis), et la leur à un niveau près dans 94 % des cas. Sur les mêmes faits, il classe C premier de ses 8 langages
  sous ma règle, dernier sous la leur : la règle suffit au renversement. Il n'accorde presque jamais leur niveau 4
  (« imposé ou par défaut »), celui qui met Zig en tête.

## Pour aller plus loin

* [`docs/FINDINGS.md`](docs/FINDINGS.md) : tous les faits vérifiés (machines, compilateurs, runtimes).
* [`results/report_final.md`](results/report_final.md) : l'analyse du classement de la v4 (tous les calculs, plafond
  par noyau, parts du code par défaut, forme retenue cellule par cellule, cellules remplies) ;
  [`results/report_v3.md`](results/report_v3.md) : celle de la v3 (intervalles, variantes, réplication,
  décomposition de la variance, disposition du code).
* [`results/report_instruments_v3.md`](results/report_instruments_v3.md) : appels système, défauts de page,
  allocations et pilote de contrôle du bruit.
* Les audits et mes réponses : [`docs/AUDIT_2026-10-29.md`](docs/AUDIT_2026-10-29.md) et
  [`docs/AUDIT_RESPONSE.md`](docs/AUDIT_RESPONSE.md), [`docs/AUDIT2_2026-10-29.md`](docs/AUDIT2_2026-10-29.md) et
  [`docs/AUDIT2_RESPONSE.md`](docs/AUDIT2_RESPONSE.md).
* La confrontation avec le « Banc de sympathie mécanique » : [`docs/CONFRONTATION.md`](docs/CONFRONTATION.md)
  et [`results/report_confrontation.md`](results/report_confrontation.md) ; rejouée dans l'état actuel :
  [`results/report_confrontation_current.md`](results/report_confrontation_current.md).
* L'ajout de Swift (chaîne et faits relevés en écrivant le code, grille, plan, pont par le C, sensibilités, pont mis à
  l'épreuve par le facteur d'hôte des autres langages) : [`docs/SWIFT.md`](docs/SWIFT.md) et
  [`results/report_swift.md`](results/report_swift.md) ; la remarque sur Swift (errata D4 et E4, pont mesuré sur un
  Emerald Rapids, Q1 et K5 selon le processeur, `UniqueBox` et `&+=` en sensibilité) : [`docs/SWIFT.md`](docs/SWIFT.md),
  section 5, et [`results/report_swift_remark.md`](results/report_swift_remark.md).
* L'ajout de FreePascal (chaîne, faits relevés, grille, plan, pont par le C entre modèles, sensibilités) :
  [`docs/FPC.md`](docs/FPC.md) et [`results/report_fpc.md`](results/report_fpc.md) ; la remarque sur FreePascal
  (errata C2, E4 et F4, `Length`, formes mieux écrites, 3.2.4-rc2 et branche main) : [`docs/FPC.md`](docs/FPC.md),
  section 5, et [`results/report_fpc_remark.md`](results/report_fpc_remark.md).
* L'ajout de BQN (CBQN construit pour la cible de chaque donnée publiée, choix du code naturel d'un langage de
  tableaux, faits relevés, grille, plan, pont par le C, sensibilités) : [`docs/BQN.md`](docs/BQN.md) et
  [`results/report_bqn.md`](results/report_bqn.md) ; la remarque sur BQN (K7 naturel et somme de contrôle de K9
  corrigés, errata A3 et A6, formes en blocs en sensibilité) : [`docs/BQN.md`](docs/BQN.md), section 5, et
  [`results/report_bqn_remark.md`](results/report_bqn_remark.md).
* L'ajout de PHP (OPcache et JIT tracing activés comme le recommande le manuel, choix du code naturel, faits relevés
  dont un bogue du JIT tracing, processus et mémoire partagée pour les variantes parallèles, grille, plan, pont par le
  C, sensibilités) : [`docs/PHP.md`](docs/PHP.md) et [`results/report_php.md`](results/report_php.md) ; la remarque
  sur PHP (le collecteur de cycles dans K1 naturel, l'échec de compilation du stencil et le bogue de pile datés de 8.4,
  reproductions pour php-src) : [`docs/PHP.md`](docs/PHP.md), section 5, et
  [`results/report_php_remark.md`](results/report_php_remark.md).
* La remarque sur Ada (piège de GNAT, errata, implémentation corrigée et remesurée) : [`docs/ADA.md`](docs/ADA.md)
  et [`results/report_ada.md`](results/report_ada.md).
* La remarque sur D (Q1 corrigé, deux errata de la règle v1, cause du stencil naturel) :
  [`docs/DLANG.md`](docs/DLANG.md) et [`results/report_d.md`](results/report_d.md).
* La remarque sur Nim (Q1 en blocs conforme à la pratique de sa classe, cause du stencil naturel, sensibilités) :
  [`docs/NIM.md`](docs/NIM.md) et [`results/report_nim.md`](results/report_nim.md).
* La remarque sur C3 (cinq errata de la matrice, `noalias` posé sur le mauvais paramètre, réduction de K5, démarrage des
  fils, `--optlevel=max`) : [`docs/C3.md`](docs/C3.md) et [`results/report_c3.md`](results/report_c3.md).
* La remarque sur Odin (intrinsèques importées de LLVM, erratum en règle v2 ; noyaux inlinés dans la boucle de mesure,
  sans effet sur leur code machine ; Q1 par popcount et `-o:aggressive` en sensibilité) : [`docs/ODIN.md`](docs/ODIN.md)
  et [`results/report_odin.md`](results/report_odin.md).
* La remarque sur C++ (erratum de `std::simd` en règle v1 ; K4 et le compilateur ; pratique d'allocation de K9 ;
  remesure de D2 et D4 non publiée ; P2795 sans effet sur les noyaux) : [`docs/CPP.md`](docs/CPP.md) et
  [`results/report_cpp.md`](results/report_cpp.md).
* La remarque sur C (deux errata de la règle v1, `<immintrin.h>` et `packed`, partagés avec C++ ; arène de K8 par
  valeur et par itération ; pénalité du harnais de K9 sur Cascade Lake ; rangs en règle v1 et « ISO seule ») :
  [`docs/C.md`](docs/C.md) et [`results/report_c.md`](results/report_c.md).
* Le harnais commun de K9 (inventaire des harnais, règle, copies, campagne de la machine 16, effet du harnais à hôte
  égal et de l'hôte, scénarios) : [`docs/K9.md`](docs/K9.md) et [`results/report_k9.md`](results/report_k9.md).
* La remarque sur JavaScript (K7 en cases de 32 octets, errata E1, A4 et E6 ; les 416 octets de V8 sans compression de
  pointeurs ; K3 et les appels de V8, le code de K5, le pretenuring de K8, Q1 sous Node 26 ; Q6, K9, K8 naturel et
  itératif, K5 et K1 en f64, cases discutables en sensibilité ; K7 d'OCaml reclassé) :
  [`docs/JAVASCRIPT.md`](docs/JAVASCRIPT.md) et [`results/report_js.md`](results/report_js.md).
* La remarque sur Python (noyaux parallèles sur des fils que le GIL sérialise, corrigés par des sous-interpréteurs ;
  errata B1 et F3 ; le build sans GIL, Q6 en colonnes, `gc.freeze()` pour K8 et les cases B2 et D1 en sensibilité ; ce
  que mesure le classement) : [`docs/PYTHON.md`](docs/PYTHON.md) et
  [`results/report_python.md`](results/report_python.md).
* La remarque sur Lua (K3 dans la partie hachée, K4 décodé dans la boucle, masque de Q6 qui branche, K8 naturel
  positionnel et, par la même règle, `__slots__` du K8 de Python ; errata B3 et B4 ; formes plus poussées, A8 et
  LuaJIT en sensibilité) : [`docs/LUA.md`](docs/LUA.md) et [`results/report_lua.md`](results/report_lua.md).
* La remarque sur OCaml (Q6 optimisé qui branchait encore, `pow` dans K1, arène de K8 qui allouait, horloge hors
  contrat, K7 à trois mots par case, reclassé le 3/11 au soir, erratum de D5 ; seules les clés dont le code change
  sont reportées ; masque de signe, arène par valeur, `floatarray` et K5 à huit accumulateurs en sensibilité) :
  [`docs/OCAML.md`](docs/OCAML.md) et [`results/report_ocaml.md`](results/report_ocaml.md).
* La remarque sur Haskell (options de compilation hors du mode release annoncé, FMA vectorielle de K5 et de K1,
  arène et arbre longue durée de K8, trois errata de la matrice ; report par transfert, latences de K8 reportées ;
  `-N1` et cases discutables en sensibilité) : [`docs/HASKELL.md`](docs/HASKELL.md) et
  [`results/report_haskell.md`](results/report_haskell.md).
* La remarque sur Go (transition d'AVX à SSE de K5 corrigée ; artefact de la préemption sous `GOEXPERIMENT=simd`,
  corrigé dans le classement publié et dans la réplication ; K9 et Q1 en archsimd, K8 itératif en sensibilité) :
  [`docs/GO.md`](docs/GO.md) et [`results/report_go.md`](results/report_go.md).
* La remarque sur Java (désalignement de K5 corrigé, erratum de F1 et texte de A5 ; Q1 en une passe, réserve de fils,
  K9 en Vector API, K7 isolé, K8 itératif et cases discutables en sensibilité ; écart au plan sur K1 soa) :
  [`docs/JAVA.md`](docs/JAVA.md) et [`results/report_java.md`](results/report_java.md).
* La troisième remarque générale (le tableau final mêle le langage, la taille des données, la chaîne et le règlement ;
  étages et trois quantités du plan v3, grille et état de ses preuves, variantes, plan d'une v4) :
  [`docs/AUDIT3_RESPONSE.md`](docs/AUDIT3_RESPONSE.md) et [`results/report_audit3.md`](results/report_audit3.md).
* La v4, point par point, dans l'ordre de pertinence ([`docs/V4_PLAN.md`](docs/V4_PLAN.md)). Point 1, une sonde par
  case de la grille : méthode, preuves langage par langage, cases discutables et leur effet, erratum
  ([`docs/GRID_AUDIT.md`](docs/GRID_AUDIT.md), [`results/grid_audit/summary.md`](results/grid_audit/summary.md),
  [`results/grid_audit/report_errata.md`](results/grid_audit/report_errata.md)). Point 2, trois tailles par noyau :
  plan, écarts, campagne, contrôle et résultats ([`docs/V4_SIZES.md`](docs/V4_SIZES.md),
  [`results/report_sizes.md`](results/report_sizes.md)). Point 3, des conditions égales (vérifications, stencil, SIMD
  explicite dans K4, placement de K3) : plan, écarts, campagne, contrôle et résultats
  ([`docs/V4_EQUAL.md`](docs/V4_EQUAL.md), [`results/report_equal.md`](results/report_equal.md)). Point 4, un code
  optimisé convergent (catalogue des formes du plafond porté dans les 25 langages, base corrigée, effet de l'erratum
  des points 2 et 3) : plan, diagnostic, écarts, relevé des formes, campagne et résultats
  ([`docs/V4_CONVERGE.md`](docs/V4_CONVERGE.md), [`results/converge/inventory.md`](results/converge/inventory.md),
  [`results/report_converge.md`](results/report_converge.md)). Point 5, le coût d'accès au plafond (lignes ajoutées,
  code sans vérification, portabilité, compilation pour aarch64 et riscv64, indice d'accès) : plan, règles de lecture,
  écarts, relevé des régions, occurrences et résultats ([`docs/V4_COST.md`](docs/V4_COST.md),
  [`results/cost/regions.md`](results/cost/regions.md), [`results/cost/matches.md`](results/cost/matches.md),
  [`results/report_cost.md`](results/report_cost.md)). Point 6, une piste ouverte (bibliothèques tierces nommées
  d'avance, libc pour tous) : plan, liste, sondes de la grille ouverte, formes, campagne et résultats, publiés à côté
  du classement ([`docs/V4_OPEN.md`](docs/V4_OPEN.md), [`results/report_open.md`](results/report_open.md)). La
  campagne finale, qui réunit les règles des points 2 à 4 sur une machine et donne le classement de la v4 : plan,
  écarts, campagne, analyse, sensibilités et formes retenues ([`docs/V4_FINAL.md`](docs/V4_FINAL.md),
  [`results/report_final.md`](results/report_final.md)).
* Le classement de la v3, publié en tête de ce README du 30 octobre au 23 novembre, avec ses notes, ses errata, ses
  explications langage par langage, sa méthode et ses limites : [`docs/RANKING_V3.md`](docs/RANKING_V3.md) ; son
  analyse statistique complète : [`results/report_v3.md`](results/report_v3.md).
* La sensibilité « sans SIMD explicite », le classement des variantes (types vectoriels du langage, intrinsèques de la
  plateforme, intrinsèques importées) et le décompte corrigé des formes de Q1 (9 contre 5) :
  [`docs/NOSIMD.md`](docs/NOSIMD.md) et [`results/report_nosimd.md`](results/report_nosimd.md) ; note d'explication
  (règle de D, vecteurs du langage et intrinsèques importées, poids des piliers) :
  [`docs/SIMD_EXPLICATION.md`](docs/SIMD_EXPLICATION.md).
* La remarque sur Rust (queues de latence de K8 remesurées pour tous les langages, préchargement de K7 corrigé, cause du
  stencil naturel, règle de la libc en sensibilité) : [`docs/RUST.md`](docs/RUST.md) et
  [`results/report_rust.md`](results/report_rust.md).
* La remarque sur C# (faits vérifiés, protocole du JIT, formes optimisées et code naturel en sensibilité) :
  [`docs/CSHARP.md`](docs/CSHARP.md) et [`results/report_csharp.md`](results/report_csharp.md).
* La remarque sur Chapel (trois errata, leviers locaux instables, confrontation corrigée) :
  [`docs/CHAPEL.md`](docs/CHAPEL.md) et [`results/report_chapel.md`](results/report_chapel.md).
* La remarque sur Julia (plafond, versions optimisées, trois errata, diagnostic de K10) :
  [`docs/JULIA.md`](docs/JULIA.md) et [`results/report_julia.md`](results/report_julia.md).
* La remarque sur Mojo (cinq errata de la matrice, K4 dans le plafond, vérifications de bornes) :
  [`docs/MOJO.md`](docs/MOJO.md) et [`results/report_mojo.md`](results/report_mojo.md).
* La remarque sur Fortran (noyaux inlinés, errata, banc corrigé et remesuré, écart au plan) :
  [`docs/FORTRAN.md`](docs/FORTRAN.md) et [`results/report_fortran.md`](results/report_fortran.md).
* La remarque sur Zig (vectoriseur désactivé, quatre versions comparées, rang avec la version de développement) :
  [`docs/ZIG.md`](docs/ZIG.md) et [`results/report_zig.md`](results/report_zig.md).
* Les données brutes de chaque processus : `results/raw*`.

## Reproduire

Le classement de la v4 (campagne finale, [`docs/V4_FINAL.md`](docs/V4_FINAL.md)), sur une machine du modèle 6/207/2 :

```bash
sh tools/final/machine.sh 35               # caractérisation au repos, b3 d'arrivée, constructions et empreintes
```

```bash
python3 tools/final/campaign.py calibrate  # étalonnage et validation : chaque cellule à chaque taille
```

```bash
python3 tools/final/k4_extreme.py          # K4 sur des données extrêmes -> results/final/k4_extreme.txt
```

```bash
python3 tools/final/campaign.py run        # trois passes -> results/final/work, recopiées et poussées par groupe
```

```bash
python3 tools/final/campaign.py b3 "fin de la campagne"  # b3 hors groupe, machine au repos
```

```bash
python3 analysis/final_v4.py               # classement « Final », sensibilités -> results/report_final.md
```

```bash
python3 analysis/charts_final.py           # graphique -> results/charts/classement_v4.svg
```

Les points 2 à 6 de la v4 ont chacun leurs outils, décrits dans leur document ([`docs/V4_PLAN.md`](docs/V4_PLAN.md)).
Le classement de la v3, ses remarques et ses ajouts ([`docs/RANKING_V3.md`](docs/RANKING_V3.md)) :

```bash
python3 tools/driver.py c --quick          # valide une implémentation (1 processus, 1 répétition)
```

```bash
python3 tools/campaign.py                  # campagne de référence -> results/raw
```

```bash
python3 tools/measure_v2.py k5 thp m3      # K5 remesuré et réplication -> results/raw_v2
```

```bash
python3 tools/layout_v3.py build           # huit dispositions du code (lld 23)
```

```bash
python3 tools/layout_v3.py run             # expérience de disposition -> results/raw_v3
```

```bash
python3 tools/measure_ada.py               # remarque sur Ada : mesures appariées -> results/raw_ada
```

```bash
python3 tools/measure_fortran.py           # remarque sur Fortran : mesures appariées -> results/raw_fortran
```

```bash
python3 analysis/ada_check.py              # rapports d'Ada -> results/transfers.json (réécrit)
```

```bash
python3 analysis/fortran_check.py          # rapports de Fortran, ajoutés -> results/transfers.json
```

```bash
python3 analysis/transfer_check.py         # pont par le témoin du même hôte -> results/transfers.json
```

```bash
python3 tools/measure_rust.py              # remarque sur Rust : paires et K8 remesuré -> results/raw_rust, raw_d3
```

```bash
python3 analysis/rust_check.py             # rapport de K7 -> results/transfers.json ; scénarios -> report_rust.md
```

```bash
python3 tools/measure_c3.py                # remarque sur C3 : paires et --optlevel=max -> results/raw_c3
```

```bash
python3 analysis/c3_check.py               # errata de C3 (déjà dans la matrice) et scénarios -> report_c3.md
```

```bash
python3 tools/measure_odin.py              # remarque sur Odin : noyaux isolés, Q1, -o:aggressive -> results/raw_odin
```

```bash
python3 tools/odin_check/codegen.py        # boucles des noyaux d'Odin, isolés ou inlinés -> results/odin_check
```

```bash
python3 analysis/odin_check.py             # erratum C2 (déjà dans la matrice) et scénarios -> report_odin.md
```

```bash
python3 tools/cpp_check/make_copies.py     # remarque sur C++ : copies clang++, formes de C, K9, K8 -> bench/cpp_*, c_*
```

```bash
python3 tools/cpp_check/collect.py         # sondes : std::simd, réflexion, P2795, K4, harnais de K9 -> results/cpp_check
```

```bash
python3 tools/cpp_check/data_facts.py      # faits tirés des données et décomposition -> results/cpp_check
```

```bash
python3 tools/measure_cpp.py               # copies appariées et remesure de D2 et D4 -> results/raw_cpp, raw_d24
```

```bash
python3 analysis/cpp_check.py              # erratum C1 (déjà dans la matrice), remesure, scénarios -> report_cpp.md
```

```bash
python3 tools/c_check/make_copies.py       # remarque sur C : arène de K8 par valeur et itérative -> bench/c_k8*, c_gcc_*
```

```bash
python3 tools/c_check/collect.py           # sondes C23, réassociation, code de K9 et de K8 -> results/c_check
```

```bash
python3 tools/c_check/data_facts.py        # rangs, contrôle selon la règle, K9 de Cascade Lake -> results/c_check
```

```bash
python3 tools/measure_c.py                 # copies appariées de K8, clang et gcc -> results/raw_c
```

```bash
python3 analysis/c_check.py                # errata A3 et C2 (déjà dans la matrice), scénarios -> report_c.md
```

```bash
python3 tools/k9h/make_copies.py           # harnais commun de K9 : copies bench/*_k9h, compilées
```

```bash
python3 tools/k9h/validate.py              # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/measure_k9h.py               # K9 : ancien et nouveau harnais, machine 16 -> results/raw_k9h
```

```bash
python3 analysis/k9_check.py               # effet du harnais et de l'hôte, scénarios -> report_k9.md
```

```bash
python3 tools/java_check/make_copies.py    # remarque sur Java : copies java_ref, java_fix, java_exp -> bench/java_*
```

```bash
python3 tools/java_check/validate.py       # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/java_check/data_facts.py     # piliers, K7, K10, empreinte de K1 -> results/java_check/facts.txt
```

```bash
python3 tools/measure_java.py              # copies appariées et témoin C, machine 17 -> results/raw_java
```

```bash
python3 analysis/java_check.py             # erratum F1 (dans la matrice), K5 corrigé, scénarios -> report_java.md
```

```bash
python3 tools/go_check/make_copies.py      # remarque sur Go : copies go_ref, go_fix, go_noexp, go_exp, go_nopre
```

```bash
python3 tools/go_check/validate.py         # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/measure_go.py                # copies appariées et témoin C, machine 18 -> results/raw_go
```

```bash
python3 analysis/go_check.py               # corrections de K5 et de l'artefact, scénarios -> report_go.md
```

```bash
python3 tools/haskell_check/make_copies.py # remarque sur Haskell : haskell_ref, _rel, _fix, _n1 (puis leurs build.sh)
```

```bash
python3 tools/haskell_check/validate.py    # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/measure_haskell.py           # copies appariées et témoin C, machine 19 -> results/raw_haskell
```

```bash
python3 analysis/haskell_check.py          # options, K1, K5, K8, errata B2, B3, A7 ; scénarios -> report_haskell.md
```

```bash
python3 tools/ocaml_check/make_copies.py   # remarque sur OCaml : ocaml_ref, ocaml_fix, ocaml_exp (puis leurs build.sh)
```

```bash
python3 tools/ocaml_check/validate.py      # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/measure_ocaml.py             # copies appariées et témoin C, machine 20 -> results/raw_ocaml
```

```bash
python3 analysis/ocaml_check.py            # Q6, K1 aos, K7, K8, horloge, erratum D5 ; scénarios -> report_ocaml.md
```

```bash
python3 tools/js_check/make_copies.py      # remarque sur JavaScript : js_ref, js_fix, js_exp, js_n22
```

```bash
python3 tools/js_check/validate.py         # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/measure_js.py                # copies appariées, Node 22 et témoin C, machine 21 -> results/raw_js
```

```bash
python3 analysis/js_check.py               # K7, errata E1, A4, E6 ; sensibilités ; scénarios -> report_js.md
```

```bash
python3 tools/python_check/make_copies.py  # remarque sur Python : python_ref, python_fix, python_exp, python_ftfix
```

```bash
python3 tools/python_check/validate.py     # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/measure_python.py            # copies appariées, build sans GIL et témoin C, machine 22 -> results/raw_python
```

```bash
python3 analysis/python_check.py           # noyaux parallèles, errata B1, F3 ; sensibilités ; scénarios -> report_python.md
```

```bash
python3 tools/lua_check/make_copies.py     # remarque sur Lua : lua_ref, lua_fix, lua_exp, luajit_ref, luajit_fix, python_k8n
```

```bash
python3 tools/lua_check/validate.py        # sommes de contrôle des copies (un processus par cellule)
```

```bash
python3 tools/measure_lua.py               # copies appariées, LuaJIT, Python et témoin C, machine 23 -> results/raw_lua
```

```bash
python3 analysis/lua_check.py              # K3, K4, Q6, K8, errata B3, B4 ; sensibilités, LuaJIT ; -> report_lua.md
```

```bash
bench/swift/build.sh                       # Swift 6.4.2 : -O, module entier, mode Swift 6, cible native
```

```bash
python3 tools/measure_swift.py             # ajout de Swift : Swift, témoin C, sensibilités, machine 23 -> results/raw_swift
```

```bash
python3 tools/c3_measure.py swift          # vectorisation mesurée de Swift (C3) -> results/vectorization.json
```

```bash
python3 analysis/swift_check.py            # pont par le C, classement avec Swift, sensibilités -> report_swift.md
```

```bash
tools/swift_rq/facts.sh                    # remarque sur Swift : faits vérifiés -> results/swift_check/facts2.txt
```

```bash
python3 tools/measure_swift_er.py          # remarque sur Swift : Swift et C sur Emerald Rapids -> results/raw_swift_er
```

```bash
python3 analysis/swift_remark.py           # errata, pont par Emerald Rapids, scénarios -> report_swift_remark.md
```

```bash
bench/fpc/build.sh                         # FreePascal 3.2.2 : -O3, cible COREAVX2, -Sv (K1 soa et K5)
```

```bash
probes/fpc/run.sh > results/probes/fpc.txt # sonde de la grille de FreePascal
```

```bash
tools/fpc_check/facts.sh                   # ajout de FreePascal : faits vérifiés -> results/fpc_check/facts.txt
```

```bash
python3 tools/measure_fpc.py               # FreePascal, trois témoins C, copies, machine 25 -> results/raw_fpc ; C3
```

```bash
python3 analysis/fpc_check.py              # pont par le C, classement avec FreePascal, sensibilités -> report_fpc.md
```

```bash
tools/fpc_remark/facts.sh                  # remarque sur FreePascal : faits (3.2.2, 3.2.4-rc2, main) -> results/fpc_remark
```

```bash
python3 tools/measure_fpc_rq.py            # remarque sur FreePascal : copies et témoins C, machine 26 -> results/raw_fpc_rq
```

```bash
python3 analysis/fpc_remark.py             # errata, formes de la remarque, rc2, branche main -> report_fpc_remark.md
```

```bash
bench/bqn/build.sh                         # BQN : CBQN 0.12.0, cible Cascade Lake (/opt/cbqn-cl) ; bqn_er, bqn_o3 de même
```

```bash
probes/bqn/run.sh > results/probes/bqn.txt # sonde de la grille de BQN
```

```bash
tools/bqn_check/facts.sh                   # ajout de BQN : faits vérifiés -> results/bqn_check/facts.txt
```

```bash
python3 tools/measure_bqn.py               # BQN (trois constructions), trois témoins C, machine 26 -> results/raw_bqn ; C3
```

```bash
python3 analysis/bqn_check.py              # pont par le C, classement avec BQN, sensibilités -> report_bqn.md
```

```bash
python3 tools/measure_bqn_rq.py            # remarque sur BQN : copie bqn_rq (blocs, K9, K7), machine 27 -> results/raw_bqn_rq
```

```bash
python3 analysis/bqn_remark.py             # errata, formes en blocs, C5 ; transfers.json (ratios_added) -> report_bqn_remark.md
```

```bash
bench/php/build.sh                         # PHP : 8.5.12 (/opt/php85), vérification syntaxique ; php_def de même
```

```bash
probes/php/run.sh > results/probes/php.txt # sonde de la grille de PHP
```

```bash
tools/php_check/facts.sh > results/php_check/facts.txt  # ajout de PHP : faits vérifiés et reproductions
```

```bash
python3 tools/measure_php.py               # PHP, CLI par défaut, trois témoins C, machine 28 -> results/raw_php ; C3
```

```bash
python3 analysis/php_check.py              # pont par le C, classement avec PHP, sensibilités -> report_php.md
```

```bash
tools/php_remark/build.sh                  # remarque sur PHP : 8.3.36, 8.4.27, 8.5.13RC1, 8.6.0RC5 (options du banc)
```

```bash
tools/php_remark/facts.sh > results/php_remark/facts.txt  # remarque sur PHP : sources et reproductions (K9, K1, pile)
```

```bash
python3 tools/measure_php_rq.py            # remarque sur PHP : copie php_rq et autres versions, machine 29 -> raw_php_rq
```

```bash
python3 analysis/php_remark.py             # remarque sur PHP : rapports et scénarios -> report_php_remark.md
```

```bash
python3 analysis/audit3.py                 # troisième remarque : mesures seules, substitutions, preuves -> report_audit3.md
```

```bash
sh probes/rust/run.sh > results/probes/rust.txt  # audit de la grille : sonde d'un langage (de même pour les 24 autres)
```

```bash
python3 analysis/grid_audit.py             # sondes confrontées à la matrice v1 et v2 -> results/grid_audit/summary.md
```

```bash
python3 analysis/grid_audit_errata.py --published  # erratum et cases discutables -> results/grid_audit/report_errata.md
```

```bash
python3 analysis/c_check.py --current      # sensibilités de la remarque sur C, état actuel -> report_c_current.md
```

```bash
python3 analysis/analyze_v3.py             # analyse -> results/summary_v3.json, results/report_v3.md
```

```bash
python3 analysis/confrontation_current.py  # confrontation et juge à l'aveugle, état actuel -> results/*_current*
```

```bash
python3 analysis/nosimd_check.py           # sensibilité sans SIMD explicite -> results/report_nosimd.md
```

```bash
python3 analysis/charts_v3.py              # graphiques -> results/charts
```

```bash
python3 tools/instruments_v3.py count      # compteurs du noyau (puis alloc, noise) -> results/raw_v3
```

Arborescence : `bench/<langage>/` (implémentation, `build.sh`, `run`), `tools/` (pilote, campagne, sondes
matérielles, compteurs), `probes/` (sondes de capacités et de mécanismes), `analysis/` (capacités, analyses,
graphiques), `results/` (données brutes et synthèses), `docs/` (spécification, méthode, faits, audits).
