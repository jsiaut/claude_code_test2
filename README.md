# Quels langages incarnent le mieux la *mechanical sympathy* ?

*Classement mesuré de 21 langages, octobre 2026.*

Un seul critère : la *mechanical sympathy* au sens large, c'est-à-dire la capacité d'un langage à faire écrire du
code en accord avec le matériel : disposition des données, SIMD, hiérarchie mémoire, concurrence, allocation,
requêtes analytiques. C'est ce qu'exigent le HPC, les moteurs OLAP et le Data-Oriented Design. Tout est mesuré
par moi sur des machines Intel, sauf le pilier « contrôle », qui est un inventaire jugé.

## Le classement

| Rang | Langage | Score | Rang plausible | Devance le suivant | Ce qui le place là |
|---|---|---|---|---|---|
| 1 | **C** | 79,9 | 1–6 | 69 % | Plafond le plus haut et l'un des trois meilleurs codes par défaut ; son contrôle est celui de GNU C (extensions de clang, intrinsèques d'Intel, OpenMP, glibc) |
| 2 | **Odin** | 74,0 | 1–6 | 55 % | Le Data-Oriented Design dans le langage (`#soa`, `#simd`, intrinsèques de LLVM, allocateurs explicites) ; allocateur généraliste lent |
| 3 | **C++** | 77,1 | 1–8 | 66 % | Le plus de contrôle (`pmr`, atomiques, `std::simd` encore expérimental) ; derrière C surtout par K4, que g++ vectorise moins bien que clang |
| 4 | **Zig** | 72,3 | 1–10 | 55 % | Tous les leviers du DOD ; en 0.17, son vectoriseur de boucles est désactivé par l'équipe Zig (1er avec la version de développement) |
| 5 | **C3** | 71,6 | 2–9 | 74 % | C avec vecteurs natifs, 2e plafond ; ni SoA ni intrinsèques officiels, `asm` et `@noalias` incomplets |
| 6 | **Rust** | 69,9 | 3–10 | 53 % | 7e plafond et bon code naturel ; contrôle limité par sa bibliothèque standard (ni affinité, ni `mmap`, SIMD portable instable) |
| 7 | **Nim** | 69,3 | 3–10 | 48 % | Les leviers de C par sa compilation vers C ; vérifications et aliasing non strict qui bloquent la vectorisation du stencil |
| 8 | **D** | 72,6 | 3–12 | 62 % | Le contrôle de C avec templates et CTFE ; ramasse-miettes par défaut |
| 9 | **Ada** | 71,0 | 3–12 | 58 % | Disposition au bit près, 8e plafond ; vérifications coûteuses sur le code naturel |
| 10 | **Chapel** | 65,7 | 4–12 | 70 % | 5e plafond grâce au parallélisme natif ; leviers bas niveau rares ou instables |
| 11 | **Fortran** | 65,4 | 6–13 | 72 % | Natif du HPC (tableaux, `do concurrent`, OpenMP) ; ni SIMD explicite ni intrinsèques |
| 12 | **Julia** | 62,3 | 8–13 | 60 % | Le 2e code naturel, derrière Odin ; le plafond le plus bas des 13 premiers |
| 13 | **Mojo** | 62,3 | 10–13 | 96 % | Le SIMD au cœur du langage ; ni vectoriseur de boucles, ni threads publics dans `std` |
| 14 | **C#** | 54,9 | 13–15 | 88 % | La boîte à outils la plus riche des langages à GC ; objets en références, JIT sans vectoriseur |
| 15 | **Java** | 47,2 | 14–16 | 70 % | Meilleur allocateur de petits objets ; pas de types valeur |
| 16 | **Go** | 43,0 | 14–16 | 99 % | Structures par valeur ; ni vectoriseur, ni SIMD stable, atomiques séquentiellement cohérentes |
| 17 | **Haskell** | 34,5 | 17 | 98 % | Peut descendre bas, mais tout le code par défaut est paresseux et boxé |
| 18 | **OCaml** | 24,0 | 18 | 100 % | Bonne allocation générationnelle ; flottants boxés, aucun SIMD |
| 19 | **JavaScript** | 14,2 | 19–20 | 93 % | Tableaux typés bien compilés ; objets en références, aucun SIMD |
| 20 | **Python** | 9,9 | 19–21 | 63 % | Environ 200 fois plus lent que le meilleur ; la hiérarchie mémoire disparaît derrière l'interpréteur |
| 21 | **Lua** | 3,9 | 20–21 | — | Des tables seulement : ni types étroits, ni structures en ligne, ni threads, ni SIMD |

* **Score** (0–100) : 40 % de plafond mesuré (le meilleur code que le langage permet d'écrire pour la machine),
  25 % de code par défaut mesuré (le code qu'on écrit sans y penser) et 35 % de contrôle (les leviers qu'offrent le
  langage et sa chaîne de compilation).
* **Ordre** : le rang moyen sur 20 000 variantes de l'analyse, qui tirent au hasard les poids, les normalisations, le
  jugement porté sur chaque capacité et le bruit de mesure. Il suit le score, sauf en deux endroits. D et Ada, 4e et
  7e au score, ne sont que 8e et 9e : leur code par défaut est le plus lent (D) et l'un des plus lents (Ada) des neuf
  premiers ; Zig, C3, Rust et Nim, moins bien notés que D, ont un meilleur rang moyen (Nim de justesse : il ne
  devance D que dans 48 % des variantes), et Rust et Nim devancent Ada dans 65 et 63 % des variantes. En tête, Odin
  devance C++, pourtant mieux noté (77,1 contre 74,0 points), dans 55 % des variantes (rang moyen 3,16 contre 3,76) :
  l'avance de C++ tient au contrôle, dont la grille v1, tirée dans la moitié des variantes, lui retire 5,6 points
  depuis les errata du 1er novembre (`std::simd` expérimental ; `<immintrin.h>` et `packed`, hors norme).
* **Rang plausible** : le rang dans 90 % des variantes. **Devance le suivant** : la part des variantes où le
  langage passe devant celui de la ligne suivante.
* **Errata du 30 octobre au 1er novembre** : un second juge à l'aveugle a trouvé cinq erreurs de fait dans ma matrice
  de contrôle (aides de ligne de cache de C, de D et d'Odin, AVX-512 d'Odin, réductions parallèles de Nim), une
  remarque sur Zig une sixième (projection de fichiers), une remarque sur Ada trois autres (non-aliasing et types
  vectoriels sous-notés, allocation cachée sur-notée), une remarque sur Fortran trois encore (disposition compacte,
  alignement et allocateurs sous-notés), une remarque sur Mojo cinq autres (alignement, unions, réassociation, attente
  active et non-aliasing sous-notés), une remarque sur Julia trois encore (allocateurs, aide de ligne de cache,
  indication d'attente active sous-notés), une remarque sur Chapel trois encore (allocateurs, intrinsèques,
  non-aliasing sous-notés), une remarque sur D deux autres (indications de branchement et préchargement de druntime,
  sous-notés en règle v1), une remarque sur C3 cinq autres (réassociation globale, affinité par appel système brut et
  projection de fichiers en règle v1 sous-notées ; assembleur et non-aliasing sur-notés), une remarque sur Odin une
  autre, qui corrige ma propre correction de l'AVX-512 d'Odin : ses intrinsèques, importées de LLVM, valent 1 en
  règle v2, comme celles de Julia et de Mojo (Odin passe de 72,6 à 73,5 points et reste 3e, à égalité avec C++), une
  remarque sur C++ une autre : `std::simd`, que GCC 16 livre comme « highly experimental » (x86 seulement, absent
  de libc++), valait 1 à C++ en règle v1, quand les types vectoriels de GCC valent ½ à C et le `std::simd` nightly ½ à
  Rust ; il vaut ½ (en règle v2, les types vectoriels de GCC lui gardent 1, comme à C), une remarque sur C deux
  dernières, en règle v1 : `<immintrin.h>` (C2) et `packed` (A3), hors norme ISO, valaient 1 à C et à C++, alors que
  la règle donne ½ à ce qui est livré hors norme, comme pour `_mm_prefetch` et `_mm_pause` du même en-tête (en règle
  v2, 1), une remarque sur Java une dernière : les tableaux multidimensionnels contigus de l'API FFM
  (`sequenceLayout` imbriqués), que la grille créditait déjà de ½ en A7, valaient 0 en F1 (½ désormais). Seules celles
  de Fortran (de la 12e à la 11e place), de Chapel (de la 11e à la 10e), de C3 (Nim et Rust, à égalité, échangent les
  6e et 7e places) et de C++ (son score ne change pas, mais Odin et C++, à égalité, échangent les 2e et 3e places)
  changent un rang à elles seules. Les remarques sur Ada, Fortran, D, Rust et Java ont aussi trouvé cinq erreurs de
  mon banc, corrigées et remesurées ; celle sur Odin, une sixième, sans effet : dix de ses noyaux étaient inlinés
  dans la boucle de mesure, comme ceux de Fortran, mais leur code machine ne change pas une fois isolés, et les écarts
  remesurés sur un autre processeur, des effets de placement, ne sont pas reportés ([`docs/ODIN.md`](docs/ODIN.md)).
  Un piège de GNAT (`-fnon-call-exceptions`) laissait scalaires les noyaux optimisés d'Ada une fois inlinés : Ada
  passe de la 9e à la 7e place ([`docs/ADA.md`](docs/ADA.md)). Les noyaux de Fortran n'étaient pas isolés de la boucle
  de mesure comme ceux de C, et gfortran y laissait K4 scalaire : Fortran gagne deux places (11e depuis les errata de
  Chapel) ([`docs/FORTRAN.md`](docs/FORTRAN.md) ; 9e avec le calcul prévu par le plan, dont je me suis écarté sur une
  clé). Le Q1 optimisé de D était écrit en blocs, comme pour les langages sans types vectoriels, et non en une passe
  comme dans les autres langages à types vectoriels : réécrit avec `core.simd`, il est 2,3 fois plus rapide, et D
  passe de la 9e à la 8e place ([`docs/DLANG.md`](docs/DLANG.md)). Le K7 optimisé de Rust préchargeait en lecture,
  quand la référence C et huit autres implémentations préchargent en écriture : corrigé, sans gain (le préchargement
  en écriture y est même 1,08 fois plus lent, dans la marge des clés témoins). Le K5 optimisé de Java lisait ses
  vecteurs dans des tableaux du tas, désalignés depuis les en-têtes compacts du JDK 27, quand toutes les autres
  implémentations à SIMD explicite alignent leurs données : aligné, il va 1,7 fois plus vite sur un même hôte, et
  Java gagne 1,0 point avec son erratum, sans changer de place ([`docs/JAVA.md`](docs/JAVA.md)). La remarque sur Rust
  a aussi trouvé un défaut de mesure : les queues de latence de K8, qui comptent dans le code par défaut, suivaient
  le vol de temps de la machine virtuelle et ne reposaient que sur deux ou trois processus par langage. K8 naturel a
  été remesuré pour les 25 implémentations, sept processus chacune (Emerald Rapids) : Rust passe de la 9e à la 6e
  place, Zig de la 5e à la 4e, Ada de la 7e à la 9e, C3 et Nim reculent d'une place ([`docs/RUST.md`](docs/RUST.md)).
  La remarque sur C++ demandait de même plus de processus pour la pénalité de désordre (D2) et la hiérarchie mémoire
  (D4) : remesurées pour les 25 implémentations sur un autre Emerald Rapids, elles n'entrent pas au classement, car
  cet hôte change ce qu'elles mesurent (K2 à 8 Mio y varie d'un facteur 3 à 4 d'un processus à l'autre, et la pénalité
  de désordre des langages à références y est deux fois plus faible) ; elles confirment que les D2 et D4 de C++
  tenaient chacun à un processus aberrant ([`docs/CPP.md`](docs/CPP.md)).
* **Révision du protocole du 1er novembre au soir : un harnais commun pour K9.** La spécification n'imposait que la
  réinitialisation des grilles hors chrono ; C, Chapel et Ada les allouaient une fois, presque toutes les autres
  implémentations à chaque répétition, ce qui multiplie les défauts de page (C++ : 180 000 par processus, contre 16
  700 pour C). Sur décision de l'auteur de l'étude, toutes les allouent désormais une fois
  ([`docs/SPEC.md`](docs/SPEC.md)), et K9 a été remesuré pour toutes sur un Emerald Rapids (machine 16), faute d'hôte
  Cascade Lake disponible : comme K5, il vient donc d'un autre hôte que les autres noyaux. À hôte égal, le harnais
  commun prend 0,41 à 0,65 fois le temps des compilés qui réallouaient, à quatre fils. Le changement d'hôte seul
  aurait renforcé C (1er dans 66 % des variantes) ; avec le harnais commun, les cinq premiers ne bougent pas, C reste
  1er (49 %), et Rust et Nim, à égalité, échangent les 6e et 7e places ([`docs/K9.md`](docs/K9.md)).

![Classement final](results/charts/classement.svg)

**Ce qui est sûr, et ce qui ne l'est pas.**
* **Les grandes marches sont établies.** Les 13 premiers devancent C# dans au moins 96 % des variantes, et sur les
  deux machines. Go devance Haskell, Haskell OCaml, OCaml JavaScript, dans 98 à 100 % des variantes. Ces variantes ne
  font varier ni l'effort d'implémentation ni le choix du code naturel : avec ses meilleures formes mesurées, une
  particule en `struct` et un JIT stabilisé, C# dépasse Mojo au score (62,0 à 63,3 points contre 61,8) et fait jeu
  égal avec lui au rang, 13e ou 14e ([`docs/CSHARP.md`](docs/CSHARP.md)).
* **En haut du tableau, l'ordre est la meilleure estimation, pas un fait établi.** Un langage y devance le suivant
  dans 48 à 74 % des variantes. C ou C++ est premier dans 61 % des variantes (C 49 %, C++ 12 %), Odin dans 17 %, Zig
  dans 10 %.
* **La 1re place de C dépend de choix de protocole.** Sous la règle « ISO seule » du « Banc de sympathie
  mécanique », qui ne compte ni les extensions de compilateur ni la glibc, C passe 5e et Odin 1er ; avec le contrôle
  noté en règle v1 partout, Odin passe aussi devant C, de peu (rang moyen 2,74 contre 2,97). Avec le K4 de clang++
  pour C++ (le même vectoriseur que C), C++ passe 1er (80,3 points contre 79,9 ; rang moyen 2,20 contre 2,54). Sur
  Emerald Rapids, C++ est 1er. À l'inverse, l'arène de K8 de C, écrite de façon à faire passer son état par la
  mémoire, lui coûte 4 points : écrite par itération, elle le remet nettement en tête (84,0 points), même face au K4
  de clang++ pour C++ (80,2). Le classement garde les implémentations et le protocole fixés d'avance
  ([`docs/C.md`](docs/C.md)).
* **L'ordre fin dépend aussi de la machine.** Sur un Emerald Rapids, le même calcul donne C++ 1er, Rust 2e, C 3e.
  L'écart vient surtout de l'écrivain unique (K3), dont le temps dépend, sur ce processeur, du placement du code par
  l'éditeur de liens (voir plus bas).
* **La version du compilateur peut déplacer un langage.** Zig 0.16 et 0.17 désactivent le vectoriseur de boucles de
  LLVM, pour contourner un bug de LLVM qui compilait mal le compilateur Zig lui-même ; la version de développement
  (0.18-dev) le réactive. Avec elle, et sans changer une ligne de code, Zig passe de 72,3 à 75,7 points et du 4e au
  1er rang espéré (1er dans 48 % des variantes, C dans 34 %). Le classement garde la règle fixée d'avance, la dernière
  version stable ([`docs/ZIG.md`](docs/ZIG.md)).
* **Le plafond de K4 compte la vectorisation automatique.** La spécification n'admet pour K4 que deux formes
  scalaires : son plafond mesure ce que le compilateur fait d'une boucle scalaire, comme le code par défaut. Sans K4
  dans le plafond, C++ passe 1er (80,0 points, rang moyen 2,46, 1er dans 37 % des variantes), devant C (79,2 ; 2,88)
  et Zig (75,5 ; 2,90), au coude à coude ; Mojo est 12e. Le classement garde la spécification fixée d'avance
  ([`docs/MOJO.md`](docs/MOJO.md)).
* **Le contrôle pèse lourd, et il est jugé.** Il explique 73 % des écarts de score entre les 13 premiers. Sur les
  seules mesures (le plafond), la tête serait C, C3, C++, Odin, Chapel, D.

## Pourquoi cet ordre, langage par langage

Les temps cités viennent de la machine de référence (Cascade Lake), sauf mention d'Emerald Rapids. « Plafond » : le
pilier mesuré du meilleur code ; « code naturel » : la variante idiomatique, écrite sans penser à la machine.

![Plafond et code naturel par langage, sur les deux machines](results/charts/v3_profiles.svg)

### En tête : le contrôle de C, et un code par défaut déjà contigu

**1. C.** Le plafond le plus haut de l'étude (85) : meilleurs temps sur la somme conditionnelle sans branchement (K4,
2,9 ms), le produit scalaire SIMD (K5) et la table de hachage plate (K7, 436 ms). L'un des trois meilleurs codes par
défaut, avec ceux de Nim et de Zig : tableau de structures contigu (64 octets par particule, aucune pénalité en ordre
permuté), tableau 2D vectorisé, allocation `malloc`/`free` régulière. Presque tous les leviers existent, mais une
partie passe par des extensions de compilateur (types vectoriels, `__builtin_prefetch`, OpenMP). Sans bibliothèque de
structures de données, la table de hachage naturelle (chaînage, un `malloc` par entrée) est 12 fois plus lente que la
table plate. Le C classé est celui de clang 23 et de la glibc, extensions de GNU C, intrinsèques d'Intel et OpenMP
compris : sous la règle « ISO seule », son contrôle passe de 91,7 à 64,0 et C tombe 5e ; en règle v1 partout, Odin
passe devant lui, de peu (rang moyen 2,74 contre 2,97). Un choix de son banc le dessert : son arène de K8 optimisée
passe le sommet de pile et le compteur par pointeur, ce qui oblige clang à les relire et à les réécrire en mémoire à
chaque nœud : écrite par itération, elle prend 0,40 fois le temps sur Emerald Rapids et vaudrait 4,1 points à C
(84,0). Ses grilles de K9 étaient allouées une fois, quand presque toutes les autres implémentations les réallouaient
à chaque répétition : depuis le 1er novembre, toutes les allouent une fois ([`docs/C.md`](docs/C.md),
[`docs/K9.md`](docs/K9.md)).

**2. Odin.** Le langage le plus proche du Data-Oriented Design : `#soa` transpose une structure en colonnes dans le
langage même, `#simd` donne les vecteurs et toute intrinsèque de LLVM s'importe par `foreign` (c'est ainsi qu'est
écrit `core:simd/x86`), l'allocateur de contexte rend chaque allocation explicite. Deux boucles naturelles
vectorisées ; SIMD explicite à 5 à 7 % du meilleur temps sur K1 et K5, mais 1,2 fois sur Q6 et 1,4 à 1,7 fois sur Q1,
qui compte ses groupes sans popcount (avec popcount, Q1 passe sous le temps de C : sensibilité, 74,3 points).
Faiblesse principale : l'allocateur généraliste (1,9 s sur K8, deux fois C), qui enveloppe `calloc` et range un nœud
de 24 octets dans un bloc de 48. Sa table `map` fait 5 fois sa table plate sur K7, comme toutes les tables standard (3
à 22 fois), mais c'est la 3e plus rapide des treize premiers ; sa lecture d'horloge fait un appel système à chaque
fois, sans coût notable. Moins bien noté que C++, il le devance pourtant dans 56 % des variantes : la grille v1
retire plus de contrôle à C++ qu'à lui.

**3. C++.** Le plus de contrôle de l'étude (92) : arènes `std::pmr` (K8 passe de 1,05 s à 181 ms), atomiques à ordres
explicites, `mdspan`, et `std::simd` (meilleur K5 sur Cascade Lake, 4,75 ms), encore expérimental dans GCC 16. Ce qui
le sépare de C tient d'abord au compilateur : K4, deux boucles scalaires que g++ vectorise moins bien que clang, lui
coûte 3,4 points ; avec le K4 de clang++ (1,06 à 1,11 fois le temps de C sur un même hôte, contre 2,6 à 3,7 fois avec
g++), C++ aurait 80,3 points et passerait 1er, devant C (79,9). Mais le classement garde un compilateur par langage,
et g++, le seul à livrer `std::simd`, lui rapporte aussi : sous clang++, l'arène de K8 prend 1,55 fois plus de temps
et K5 naturel deux fois plus. Vient ensuite la queue de latence de K8 (0,4 point) ; K9, qui lui coûtait 0,7 point
quand il réallouait ses grilles à chaque répétition, ne pèse plus depuis que toutes les implémentations les allouent
une fois (voir Limites). `std::unordered_map`, à nœuds chaînés, est 22 fois plus lent que la table plate sur K7, mais
ne lui coûte que 0,25 point face à C, dont la table naturelle est lente aussi. Premier sur Emerald Rapids
([`docs/CPP.md`](docs/CPP.md)).

### Le peloton des langages compilés à types valeur

**4. Zig.** Tous les leviers du DOD : `std.MultiArrayList` (SoA dans la bibliothèque standard), `@Vector`,
`comptime`, allocateurs passés explicitement, aucune allocation cachée, et la latence d'allocation la plus régulière
de l'étude (p99,9 égale à 3 fois la médiane sur K8, Emerald Rapids). Son plafond n'est que 11e (70), parce que Zig
0.17 ne vectorise aucune des deux boucles naturelles mesurées. Ce n'est pas le langage : l'équipe Zig a désactivé le
vectoriseur de boucles de LLVM en 0.16 et 0.17, pour contourner un bug de LLVM. La version de développement
(0.18-dev), qui le réactive, vectorise les deux boucles sans changer une ligne de code ; Zig a alors le 7e plafond
(78), le meilleur code naturel de l'étude, et passe 1er en rang espéré, devant C. Ses threads coûtent aussi trois fois
plus cher à lancer que ceux de la glibc (environ 160 µs contre 50 par thread).

**5. C3.** C avec des vecteurs natifs, des génériques par déclaration, des allocateurs et `@pool` : 2e plafond de
l'étude (83,5), deux boucles naturelles vectorisées. Il lui manque le SoA, les intrinsèques officiels et un contrôle
local de la réassociation flottante (seule une option globale, `--fp-math`, l'autorise) ; son assembleur en ligne ne
couvre qu'un sous-ensemble du jeu x86, et son `@noalias`, expérimental, marque le mauvais paramètre. Son code naturel
paie trois choix de sa bibliothèque et de son compilateur : chaque allocation passe par l'interface `Allocator`,
résolue à l'exécution, et `alloc::new` remet la mémoire à zéro (K8, 1,5 fois le temps de C) ; sans information
d'aliasing par type, les pointeurs des colonnes sont relus à chaque ligne (Q1, 1,3 fois) ; `HashMap` est chaînée, une
entrée allouée par insertion (K7, 4 fois le meilleur). Sa latence d'allocation a le p99,9 le plus long des langages
compilés sans ramasse-miettes (277 µs sur K8, Emerald Rapids) ; son maximum (2,2 ms) est au niveau de ceux d'Odin et
de Mojo. Cinq errata de sa matrice, le 1er novembre, portent son contrôle de 73 à 76 sans changer sa place ; ni une
réduction en arbre (K5), ni des fils lancés sans attente (K9), ni le pipeline O3 de LLVM ne lui en font gagner une
([`docs/C3.md`](docs/C3.md)).

**6. Rust.** 7e plafond (78) et un code naturel meilleur que celui de C, de C++ et de D : `repr(C)`, `repr(align)`,
`std::arch` avec AVX-512 stable, flottants `algebraic_*` pour réassocier opération par opération, seule file standard
sans verrou. Ce qui le retient, c'est d'abord le contrôle (74, le plus bas des neuf premiers) : sa bibliothèque
standard n'expose ni l'affinité, ni `mmap`, ni la taille de ligne de cache, que C et C++ tirent de la libc (la règle
ne compte la libc que pour eux ; étendue à Rust, elle lui vaudrait 3 points et la 4e place), et son SIMD portable
reste en *nightly*. Son stencil naturel `Vec<Vec<f64>>` n'est pas vectorisé, et pas à cause des bornes : comme LDC
pour D, rustc ne transmet pas de règle d'aliasing par type à LLVM, et les pointeurs de lignes sont relus après chaque
écriture ; en lignes de taille fixe (`Vec<[f64; M]>`), il vectorise. `HashMap` à SipHash coûte 9 fois la table plate
sur K7. Sa queue de latence sur K8, qui le plaçait 9e, venait du vol de temps de la machine virtuelle sur ses deux
processus : remesurée, elle est proche de celle de C ([`docs/RUST.md`](docs/RUST.md)). 2e sur Emerald Rapids.

**7. Nim.** Il compile vers C et en hérite la disposition et les compilateurs ; comptage de références déterministe
(ORC) ; l'un des meilleurs codes naturels de l'étude. Mais son stencil naturel n'est pas vectorisé (71 contre 36 ms) :
il faudrait lever à la fois les vérifications de bornes gardées en `-d:release` et l'interdiction d'aliasing par type
que Nim impose au compilateur C (`-fno-strict-aliasing`) ; en tableau de taille fixe, il vectorise. Sa bibliothèque
standard n'a pas de types SIMD : ses noyaux optimisés importent les intrinsèques de C, sauf Q1, écrit en blocs comme
pour les langages sans types vectoriels portables et 3 fois plus lent que celui de C ; en intrinsèques, il rejoint C et
Nim passerait 5e, en sensibilité ([`docs/NIM.md`](docs/NIM.md)).

**8. D.** Le contrôle de C avec templates, exécution à la compilation, `core.simd`, indications de branchement et de
préchargement de druntime et atomiques à ordres explicites : 4e score de l'étude (72,6). Ce qui le fait reculer au rang
espéré : son ramasse-miettes par défaut, qui donne la pire pause des langages compilés sur K8 (89 ms, Emerald Rapids),
et un code par défaut plus lent que celui de Nim ou de Zig. Son stencil naturel `double[][]` n'est pas vectorisé, non à
cause des vérifications de bornes (`-release` ne les garde que dans le code `@safe`), mais parce que LDC ne transmet pas
de règle d'aliasing à LLVM : les pointeurs de lignes sont relus après chaque écriture. En tableau rectangulaire
`double[M][]`, que la spécification recommande pour le calcul, il vectorise (temps × 0,68, une place de plus en
sensibilité). Mon Q1 optimisé était écrit en blocs, comme pour les langages sans types vectoriels : réécrit en une passe
avec `core.simd`, comme dans les autres langages à types vectoriels, il est 2,3 fois plus rapide, et D passe de la 9e à
la 8e place ([`docs/DLANG.md`](docs/DLANG.md)).

**9. Ada.** Le contrôle de disposition le plus précis de l'étude (clauses de représentation au bit près), des types
vectoriels GCC (`vector_type`), une règle de non-aliasing des paramètres que GNAT exploite, et le 8e plafond (77). Ce
qui le retient : ses vérifications, actives par défaut, coûtent sur le code naturel (Q1 naturel 194 ms contre 83 en
C ; stencil naturel scalaire, écrit avec des bornes littérales sur un tableau non contraint), et les boucles
parallèles d'Ada 2022 restent absentes de GNAT. 7e au score, il n'est que 9e en rang espéré. Un piège de GNAT laissait
aussi scalaires ses noyaux optimisés une fois inlinés : corrigé ([`docs/ADA.md`](docs/ADA.md)). Son meilleur temps
sur K8 vient d'une arène que GCC compile bien, pas de ses pools de stockage.

### Forts sur leur terrain, avec moins de contrôle ou un runtime

**10. Chapel.** 5e plafond (79) grâce au parallélisme de données natif (`forall`, `reduce`) et aux tableaux
multidimensionnels : meilleur temps de K3, stencil parallèle parmi les meilleurs. Contrôle bas niveau moyen (62) :
pas de types SIMD portables ni de champs de bits ; des leviers locaux encore instables (attribut de boucle pour
réassocier, `Allocators`, `foreach`) et des intrinsèques limitées aux fonctions inline d'`immintrin.h`
([`docs/CHAPEL.md`](docs/CHAPEL.md)). Ses threads ouvriers consomment 23 % de CPU en plus sur les noyaux à un thread.
Ce qui le distingue le plus, la distribution sur plusieurs nœuds et le GPU, n'est pas mesuré ici.

**11. Fortran.** Le langage natif du HPC : tableaux multidimensionnels contigus, syntaxe tableau, `do concurrent`,
absence d'aliasing par règle du langage, OpenMP ; stencil excellent. Mais ni types SIMD, ni intrinsèques, ni
génériques : tout dépend du vectoriseur. Sur K4, gfortran fait jeu égal avec GCC sur C (5,0 ms, contre 2,8 ms pour
clang) ; sur K5 et K8, ses versions optimisées restent 1,2 à 1,4 fois plus lentes que celles du C de GCC. Mon banc
laissait gfortran inliner ses noyaux dans la boucle de mesure, où K4 restait scalaire (13 ms) : corrigé, Fortran
gagne deux places ([`docs/FORTRAN.md`](docs/FORTRAN.md)). Le classement mesure gfortran 16.2 ; flang, en annexe,
vectorisait déjà K4 dans le banc d'origine, et ifx n'est pas mesuré.

**12. Julia.** Structures immuables stockées en ligne, fonctions spécialisées par types et JIT LLVM : les deux
boucles naturelles sont vectorisées, et son code naturel est le 2e de l'étude, derrière celui d'Odin. Ce qui la place
12e, c'est d'abord son plafond (62, le plus bas des 13 premiers) : ses versions optimisées de K8, Q1, K5 et K7
restent loin des meilleures, en partie parce qu'elles sont moins travaillées que celles des autres langages ;
réécrites comme le propose un relecteur, elles lui vaudraient 3 à 5 points, et la 11e place avec K5 en 512 bits
([`docs/JULIA.md`](docs/JULIA.md)). Son runtime pèse moins : sur K8, le ramasse-miettes porte bien la latence p99,9 à
30 fois la médiane (Emerald Rapids), mais son code par défaut reste entre ceux de C3 et d'Ada. Sur la file de K10
(hors score), le blocage que j'attribuais à l'ordonnanceur venait de mon code : une variable capturée faisait
allouer, et la collecte attendait le thread en attente active.

**13. Mojo.** Le SIMD est au cœur du langage (`SIMD[DType, N]`, paramètres de compilation), et le SIMD explicite est
efficace : écrit ainsi, K4 bat le meilleur C (2,3 contre 3,1 ms sur la même machine), mais la spécification de K4
ne l'admet pour aucun langage. Son compilateur n'a pas de vectoriseur de boucles, par choix : aucune de ses deux
boucles naturelles n'est vectorisée. Son stencil naturel (262 ms, le plus lent des langages compilés) paie d'abord
les vérifications de bornes de `List`, actives par défaut (4 fois plus rapide sans elles), puis l'absence de
vectorisation. Sa bibliothèque standard n'expose ni threads publics ni `mmap` : `parallelize` est dans le paquet MAX,
que la règle de la bibliothèque standard exclut ([`docs/MOJO.md`](docs/MOJO.md)).

### Ramasse-miettes imposé, objets en références

**14. C#.** La boîte à outils la plus riche des langages à ramasse-miettes : `struct`, `Span`, `stackalloc`,
`Vector512`, intrinsèques, `StructLayout`. En SIMD explicite, K5 est à égalité avec C une fois le JIT stabilisé (4,3
contre 3,9 ms, Emerald Rapids). Mais le code par défaut va contre la machine : 88 octets par particule, parcours
permuté 4,7 fois plus lent, et un JIT qui ne vectorise aucune boucle, même avec la PGO dynamique. Sa place tient au
code par défaut, pas à une erreur du banc : le code naturel suit les directives .NET (une classe au-delà de 16
octets ; en `struct`, une particule tiendrait 64 octets, +1,9 point), et des versions optimisées mieux travaillées
(K8 en pile explicite, K4 déroulé) vaudraient 2,5 à 3,9 points. Avec trois échauffements, ses boucles tournent en code
OSR : l'effet moyen est faible (moins d'un point), mais une méthode chargée de vecteurs peut y perdre l'optimisation.
Toutes ces sensibilités cumulées le mettent devant Mojo au score (62 à 63 points) et à égalité avec lui au rang, 13e
ou 14e ([`docs/CSHARP.md`](docs/CSHARP.md)).

**15. Java.** Excellent modèle mémoire (`VarHandle`), JIT C2 efficace, et le meilleur allocateur de petits objets
de l'étude (K8 naturel, 301 ms). Pas de types valeur dans le JDK 27 : 78 octets par particule, parcours permuté 4,9
fois plus lent ; la Vector API reste en incubation, et Valhalla (JDK 28) n'aplatit pas encore une structure de
64 octets. Relu après coup : son K5 optimisé lisait ses vecteurs dans des tableaux du tas, qui commencent à 12 octets
de l'objet avec les en-têtes compacts du JDK 27, si bien que chaque chargement de 64 octets chevauchait deux lignes de
cache ; copié hors tas sur une frontière de 64 octets par l'API FFM, comme les autres langages alignent leurs
données, il va 1,7 fois plus vite sur un même hôte (7,0 → 5,7 ms une fois reporté sur les données publiées). Avec un
erratum de la grille (tableaux multidimensionnels contigus de l'API FFM), Java gagne 1,0 point (47,2) et reste 15e,
devant Go dans 70 % des variantes. Des versions optimisées mieux travaillées (Q1 en une passe, K7 isolé de sa boucle
de mesure, K8 itératif, réserve de fils) lui vaudraient 4 points de plus, et les cases discutables de la grille avec
la règle de la libc encore 2,7 : toujours 15e ([`docs/JAVA.md`](docs/JAVA.md)).

**16. Go.** Les structures sont stockées par valeur dans les slices (64 octets, permutation sans effet). Mais ni
vectoriseur, ni SIMD stable (K5 5 fois plus lent que C avec le SIMD expérimental, Emerald Rapids), et des écritures
atomiques seulement séquentiellement cohérentes : l'écrivain unique de K3 est 6 fois plus lent qu'en C (358 contre
58 à 70 ms).

### À contre-courant par défaut

**17. Haskell.** Il peut descendre bas (`UArray`, primops non boxées, primops SIMD par LLVM), mais tout le défaut va
contre la machine : code naturel paresseux et boxé (K5 naturel en 639 ms ; K7 avec `Data.IntMap` en 88 s, le pire
de l'étude), ramasse-miettes imposé, écritures atomiques séquentiellement cohérentes. Sur K8 naturel, son runtime
fait 60 000 `futex` par répétition (Emerald Rapids).

**18. OCaml.** OCaml 5 apporte les domaines et `Atomic.make_contended`, et son allocation générationnelle est parmi
les meilleures (K8 naturel, 319 ms). Mais il n'a pas de flottant 32 bits non boxé (144 octets par particule,
parcours permuté 6,9 fois plus lent) et aucun SIMD.

### La machine disparaît derrière le moteur

**19. JavaScript.** V8 compile bien les boucles sur tableaux typés. Mais les objets sont des références (416 octets
par particule, chaque flottant dans un `HeapNumber`), il n'y a ni SIMD ni vectorisation automatique, et le runtime
travaille en fond : 26 000 `futex` par répétition de K1 naturel (Emerald Rapids).

**20. Python.** Environ 200 fois plus lent que le meilleur langage, noyau par noyau. L'interpréteur masque la
hiérarchie mémoire elle-même : un saut dépendant coûte 49 ns en L1 comme en L2, au lieu de 1,6 et 4,4 ns. Une
particule coûte 750 octets, et le verrou global sérialise les threads. Son contrôle (`array`, `memoryview`,
`mmap`, `ctypes`) le place devant Lua.

**21. Lua.** Des tables seulement : ni types numériques étroits, ni structures en ligne, ni threads, ni SIMD ; une
particule coûte 449 octets. LuaJIT, mesuré à part, montre ce qu'un JIT et une FFI changent (K1 en 45 ms par
structures C).

## Ce qui sépare vraiment les langages

Les résultats les plus solides de l'étude : chacun isole une cause, avec ses conditions.

1. **Les données d'abord.** Une particule de 64 octets en occupe 64 dans 14 langages, 78 en Java, 88 en C#, 144 en
   OCaml, 416 en JavaScript et 750 en Python. Parcourir une collection de références dans le désordre coûte 4,7 à
   6,9 fois plus (C#, Java, JavaScript, OCaml) ; avec des types valeur, l'ordre ne change rien.
2. **Le SIMD explicite** divise le produit scalaire par 20 à 40 : 3,7 à 5,7 ms dans les langages compilés, en C# et
   en Java (Vector API, sur des données alignées hors tas), contre 77 à 166 ms pour la boucle naturelle en ordre strict
   (Emerald Rapids). Go (expérimental, 19 ms) suit de loin ; OCaml et JavaScript n'en ont pas.
3. **La vectorisation automatique se vérifie sur le code exécuté.** Aucune des deux boucles naturelles testées n'est
   vectorisée en C#, Go, Mojo (dont le compilateur n'a pas de vectoriseur de boucles), Zig 0.17 (vectoriseur de boucles
   désactivé par l'équipe Zig, réactivé dans la version de développement), Haskell, OCaml, JavaScript, Lua et Python.
   Les vérifications de bornes l'empêchent sur le stencil naturel en Ada (71 ms, contre 36 ms) ; en D (56 ms, sans
   vérifications) et en Rust (73 ms, scalaire même sans elles), c'est l'aliasing : ni LDC ni rustc ne transmettent de
   règle de type à LLVM, et les pointeurs de lignes sont relus après chaque écriture ; en Nim (71 ms), ce sont les deux,
   vérifications et `-fno-strict-aliasing`, que Nim impose au compilateur C ; en Ada, sur un type contraint,
   GNAT élimine les vérifications et vectorise. En Mojo, elles coûtent plus que l'absence de vectorisation : sans elles,
   le stencil naturel passe de 169 à 41 ms (C : 28 ms) et Q1 de 137 à 67 ms, au niveau de C (même machine). Le contexte
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
6. **Concurrence.** Go et Haskell n'ont que des écritures atomiques séquentiellement cohérentes : l'écrivain unique y
   est 6 fois plus lent. Le verrou global de Python sérialise les threads : sur K3, à peine plus d'un cœur sur quatre
   travaille, pour 24 000 `futex` par répétition (Emerald Rapids).
7. **Allocation.** Une arène divise K8 par 5 ou 6. Les allocateurs générationnels de Java et d'OCaml sont les meilleurs
   pour du code naturel (300 ms). Les ramasse-miettes laissent des queues (K8 remesuré sur Emerald Rapids) : pause de 89
   ms en D, p99,9 à 30 fois la médiane en Julia, arrêt de 0,76 s en Python. Les runtimes font des centaines à des
   dizaines de milliers d'appels système par répétition, le code compilé un ou deux.
8. **Le système compte.** Odin, Lua et LuaJIT font un appel système à chaque lecture d'horloge (pour Odin, 32 768
   appels par répétition de K8, de l'ordre de 3 ms sur 1,9 s : moins de 1 %). Sur K7, Rust, Zig, Odin et flang rendent
   la mémoire de leur table au système à chaque répétition, et la paient en défauts de page (1 à 5 % du temps).

## Comment c'est mesuré

**Neuf noyaux notés**, un par principe (spécification : [`docs/SPEC.md`](docs/SPEC.md)) :

| Noyau | Principe | Ce qui est mesuré |
|---|---|---|
| K1 | Disposition des données | Énergie de 4 M particules de 64 octets, en AoS, en SoA, en objets, dans l'ordre et permuté |
| K2 | Hiérarchie mémoire | Chasse de pointeurs, de 16 Kio à 256 Mio |
| K3 | Faux partage, écrivain unique | 4 threads, compteurs voisins ou espacés |
| K4 | Prédiction de branchement | Somme conditionnelle sur 16 M octets, triés ou non, avec ou sans branchement |
| K5 | SIMD | Produit scalaire en cache L1 |
| K6 | Requêtes OLAP colonnaires | TPC-H Q6 et Q1 simplifiées, 16 M lignes, 1 et 4 threads |
| K7 | Agrégation par hachage | GROUP BY sur 16 M lignes et 1 M de clés |
| K8 | Allocation, latence de queue | 16 384 requêtes qui construisent et parcourent un arbre de 2 047 nœuds |
| K9 | Stencil (HPC) | Jacobi 2D sur 2 048 × 2 048, 1 et 4 threads |

Un dixième noyau (file SPSC façon Disruptor) est mesuré mais hors score : son temps dépendait d'un régime plus que
du langage.

* **Deux variantes par noyau et par langage** : `natural`, le code idiomatique
  ([`docs/NATURAL.md`](docs/NATURAL.md)), et `tuned`, le meilleur que je sache écrire pour la machine avec la seule
  bibliothèque standard. Toutes doivent rendre le même résultat, au bit près pour les entiers. Un temps sous la
  borne physique de la machine est rejeté.
* **Chaînes de compilation** : les dernières versions stables au 28 octobre 2026
  ([`env/toolchains.txt`](env/toolchains.txt)), compilation pour le CPU hôte, ni PGO ni LTO.
* **Machines** : des VM Firecracker à 4 vCPU, un Xeon Cascade Lake (mesures de référence) et un Xeon Emerald Rapids
  (réplication complète) ; K5 et K9 viennent de deux Emerald Rapids (machines 3 et 16). Pas de compteurs matériels ;
  les compteurs du noyau (appels système, défauts de page, uprobes) servent aux faits de mécanisme
  ([`docs/INSTRUMENTS_V3.md`](docs/INSTRUMENTS_V3.md)).
* **Score** :
  * **Contrôle (35 %)** : 34 capacités (disposition, SIMD, mémoire, concurrence, abstractions sans coût,
    prévisibilité…), notées 0, ½ ou 1 selon ce que livre la chaîne de référence
    ([`docs/CAPABILITIES.md`](docs/CAPABILITIES.md)) ;
  * **Plafond (40 %)** : pour chaque mesure, le meilleur temps du langage rapporté au meilleur langage, puis la
    moyenne géométrique sur les 8 noyaux qui le mesurent (K2, la hiérarchie mémoire, compte dans le code par défaut) ;
  * **Code par défaut (25 %)** : la variante naturelle rapportée au même meilleur temps (50 %), l'empreinte et la
    pénalité de désordre d'une collection naturelle (15 %), la latence de queue de l'allocation (15 %), la
    visibilité de la hiérarchie mémoire (20 %).
* **Incertitude** : bootstrap de 2 000 tirages pour le bruit de mesure ; 20 000 variantes de l'analyse ; réplication
  sur une seconde micro-architecture ; expérience de disposition aléatoire du code.
* **Garde-fous** : plans d'analyse poussés sur GitHub avant les calculs, deux audits externes vérifiés point par
  point, journal de tous les écarts au protocole ([`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)).

## Limites

* Deux processeurs Intel, virtualisés et partagés ; ni AMD, ni ARM, ni compteurs matériels.
* Des implémentations écrites par un seul auteur, sans relecture experte ; l'effort peut varier d'un langage à
  l'autre. Quinze langages ont été relus après coup par des connaisseurs, Java en dernier, alors que la référence de C
  est la seule implémentation mise au point, mesures à l'appui, avant le plan. Ada et Fortran y ont gagné deux places
  chacun, par la correction de mon banc (un piège de GNAT ; des noyaux que gfortran inlinait dans la boucle de
  mesure) ; D une place, par la correction de son Q1 optimisé et deux errata de la règle v1 ; Rust deux places
  (trois avant les errata de C3), surtout par la remesure des queues de latence de K8, qui a aussi déplacé Zig, C3,
  Nim et Ada ; Chapel une place par trois errata de la matrice ; Mojo 2,7 points, Julia 1,8 point, C3 et Odin 0,9
  point, mais aucune place, par des errata de la matrice (ceux de C3 font passer Nim devant Rust, à égalité ; celui
  d'Odin le met à égalité avec C++) ; Zig trois places, mais par une version de compilateur que la règle exclut ;
  C++ a perdu la 2e place au profit d'Odin par un erratum de la règle v1, et C et C++ chacun 3,6 points de contrôle en
  règle v1 par deux autres, relevés par la remarque sur C, sans changer de place (C reste 1er, mais ne l'est plus que
  dans 52 % des variantes, contre 57 %) ; Java 1,0 point, sans changer de place, par la correction de son K5
  désaligné et un erratum de la matrice ; C# et Nim rien, leurs remarques ne relevant ni erratum ni erreur du banc.
  Des versions optimisées mieux travaillées vaudraient deux places à Nim (Q1 en intrinsèques), 0,8 point à Odin, déjà
  2e (Q1 par popcount), une place à Julia (avec K5 en 512 bits), aucune à Rust ni à C3 une par une et, cumulées avec
  un autre choix de code naturel et un JIT stabilisé, 7 à 8 points à C#, assez pour dépasser Mojo au score ; 4 points
  à Java (Q1 en une passe, K7 isolé de sa boucle de mesure, K8 itératif), sans changer de place ; à C++, le K4 de
  clang++ donnerait la 1re place (80,3 points contre 79,9), et à C une arène de K8 écrite par itération 4,1 points
  (84,0) : la règle les garde hors du classement, mais l'effort d'implémentation compte.
* Ces corrections ont été mesurées après coup sur une autre machine (Cascade Lake pour Ada et Fortran, Emerald Rapids
  pour D et Rust), puis reportées sur les données principales par des rapports appariés ; pour une clé de Fortran et
  une de D, par un témoin mesuré sur le même hôte, au prix d'un écart au plan pour Fortran
  ([`docs/FORTRAN.md`](docs/FORTRAN.md), 4.2), comme le prévoyait le plan pour D ([`docs/DLANG.md`](docs/DLANG.md),
  4.2). Pour Odin, dont le code des noyaux ne change pas une fois isolés, rien n'est reporté : à code identique, un
  rapport mesuré sur un autre processeur ne porte qu'un effet de placement (écart au plan,
  [`docs/ODIN.md`](docs/ODIN.md), 4.2). Les queues de latence de K8 de tous les langages viennent d'une remesure sur
  Emerald Rapids (sept processus), K5 de la machine 3 depuis la v2, et K9 de la machine 16 depuis le 1er novembre ;
  tous les autres temps sont ceux de Cascade Lake, y compris D2 et D4, dont la remesure sur un autre Emerald Rapids
  n'est pas publiée (voir les errata).
* Des microbenchmarks : ni E/S, ni décompression, ni tri ou jointure ; une seule taille d'entrée par noyau, sauf K2.
* Des règles de construit : bibliothèque standard seule, compilation pour le CPU hôte, ni PGO ni LTO, réglages des
  runtimes par défaut.
* La libc ne compte que pour C et C++ : l'affinité, `mmap` et la taille de ligne de cache qu'elle leur donne valent 0
  à Rust et aux autres langages qui doivent passer par une FFI pour les appeler. Étendue à Rust, la règle lui vaudrait
  3 points et la 4e place ; étendue à tous les langages dotés d'une FFI sans C, la 5e
  ([`docs/RUST.md`](docs/RUST.md)).
* Le pilier « contrôle » est jugé par un seul évaluateur ; c'est lui qui départage le plus le haut du tableau.
* Une seule version de compilateur par langage, la dernière stable au 28 octobre, à l'installation : Nim 2.4.0 est
  sorti le même jour, après les premières mesures, et son code machine est identique pour 20 des 21 fonctions des
  noyaux. Un réglage temporaire d'une chaîne peut coûter des rangs : Zig 0.17, dont le vectoriseur de boucles est
  désactivé, perd trois places en rang espéré par rapport à sa version de développement. Je n'ai mesuré deux versions
  que pour Zig et pour C# (.NET 11, en préversion : 0,99 fois les temps de .NET 10 en moyenne, aucune place gagnée).
  D est compilé par LDC 1.43.0 construit depuis ses sources contre LLVM 21.1.8 ; le paquet officiel embarque LLVM
  22.1.8, sans gain mesuré (D y perdrait une place). Et un seul compilateur par langage : Fortran est classé avec
  gfortran ; flang n'est mesuré qu'en annexe, ifx pas du tout. C++ est classé avec g++ 16, le seul à livrer
  `std::simd` : il y perd K4, que clang++ vectorise comme C (avec le K4 de clang++, C++ aurait 80,3 points et la 1re
  place), mais y gagne l'arène de K8 et K5 naturel, que clang++ fait 1,55 et 2 fois plus lentement
  ([`docs/CPP.md`](docs/CPP.md)).
* K9 vient d'un Emerald Rapids (machine 16), remesuré pour toutes les implémentations avec le harnais commun du 1er
  novembre (grilles allouées une fois) : sur cet hôte, la lecture sur un fil atteint 25 à 27 Go/s pour les 64 Mio des
  deux grilles, contre 7 à 10 Go/s sur Cascade Lake, et les écarts de code y pèsent davantage. Reportée sur les temps
  de Cascade Lake par les rapports de la machine 16 (information), la correction du harnais ferait passer Odin 1er,
  devant C et C++, à égalité : la pénalité de réallocation de cet hôte dépasse celle de Cascade Lake (1,58 fois à
  quatre fils, rien en un fil), et ce report surcorrige ([`docs/K9.md`](docs/K9.md)).
* La règle de la bibliothèque standard pèse plus sur Mojo que sur les autres : depuis juillet 2026, `parallelize`,
  le GPU et les tenseurs sont dans le paquet MAX. Le classement mesure Mojo et sa `std` sur CPU ; ses noyaux à
  threads passent par un module privé de `std`.
* Le plafond de K4 n'admet que des formes scalaires et compte donc la vectorisation automatique (voir plus haut).
* Ailleurs, le plafond admet le SIMD explicite (« toutes techniques »). Sans lui
  ([`docs/NOSIMD.md`](docs/NOSIMD.md)), les mêmes douze langages restent en tête et les neuf mêmes derrière (Go et
  Java, au coude à coude, échangent leurs places à la lettre) ; C et Odin restent dans les six premiers, C++ dans les
  sept. L'ordre des douze dépend du traitement des formes scalaires qui manquent : à la lettre, Chapel, Fortran et
  Julia passent devant, parce que dans K1 et K5 le SIMD des autres porte aussi la disposition SoA et la réassociation
  de la somme ; à forme égale pour tous, comme sans les noyaux vectorisables, C, Odin et C++ gardent les trois
  premières places (Odin 1er à forme égale, C 1er sans les noyaux vectorisables).
* Trois échauffements pour les langages à JIT : les boucles chaudes tournent souvent en code OSR (compilé pour
  reprendre une boucle en cours), sans atteindre le niveau d'optimisation final. Mesuré pour C# : 0 à 2,5 % en moyenne
  (moins d'un point), de −15 % à +16 % selon le noyau ([`docs/CSHARP.md`](docs/CSHARP.md)) ; pour Java, le K7
  optimisé isolé de sa boucle de mesure va 1,4 fois plus vite ([`docs/JAVA.md`](docs/JAVA.md)) ; non mesuré pour
  JavaScript et Julia.

## Une autre étude, un autre ordre : pourquoi

Le « Banc de sympathie mécanique », une étude voisine faite sur le même processeur que ma machine 3, classe C 11e sur 18
langages communs, là où je le classe 1er. Corrélation de rang entre les deux ordres : 0,78 (0,77 le 30 octobre). Je l'ai
confrontée à la mienne par quatre tests pré-enregistrés ([`docs/CONFRONTATION.md`](docs/CONFRONTATION.md)) :

* **Leur règle du « standard »** (une extension du compilateur, POSIX pour C, une option globale ou un module
  expérimental ne valent que le niveau 1 sur 4) appliquée à mon pilier contrôle classe C 12e, à un rang du leur
  (11e) ; C était 11e le 30 octobre, et les errata de Mojo ont depuis placé Mojo devant lui.
* **La même règle appliquée au code mesuré change peu la performance de C** : réécrit en C standard (sommes
  partielles au lieu des intrinsèques, `threads.h`, sans préchargement), il garde 94 % de son plafond. Elle coûte
  beaucoup à Java (sans la Vector API en incubation), à Go (sans le SIMD expérimental), et à Fortran et Mojo, qui
  n'ont pas de threads standard. À Chapel, 8 points de plafond, une fois ses réductions réécrites en sommes
  partielles comme celles des autres ; j'avais d'abord compté un produit scalaire 23 fois plus lent, faute de cette
  réécriture ([`docs/CHAPEL.md`](docs/CHAPEL.md)).
* **Les deux règles à la fois** : C passe 6e, la corrélation monte à 0,89. Le reste de l'écart tient à la question
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
* [`results/report_v3.md`](results/report_v3.md) : l'analyse statistique complète (intervalles, variantes,
  réplication, décomposition de la variance, disposition du code).
* [`results/report_instruments_v3.md`](results/report_instruments_v3.md) : appels système, défauts de page,
  allocations et pilote de contrôle du bruit.
* Les audits et mes réponses : [`docs/AUDIT_2026-10-29.md`](docs/AUDIT_2026-10-29.md) et
  [`docs/AUDIT_RESPONSE.md`](docs/AUDIT_RESPONSE.md), [`docs/AUDIT2_2026-10-29.md`](docs/AUDIT2_2026-10-29.md) et
  [`docs/AUDIT2_RESPONSE.md`](docs/AUDIT2_RESPONSE.md).
* La confrontation avec le « Banc de sympathie mécanique » : [`docs/CONFRONTATION.md`](docs/CONFRONTATION.md)
  et [`results/report_confrontation.md`](results/report_confrontation.md) ; rejouée dans l'état actuel :
  [`results/report_confrontation_current.md`](results/report_confrontation_current.md).
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
* La remarque sur Java (désalignement de K5 corrigé, erratum de F1 et texte de A5 ; Q1 en une passe, réserve de fils,
  K9 en Vector API, K7 isolé, K8 itératif et cases discutables en sensibilité ; écart au plan sur K1 soa) :
  [`docs/JAVA.md`](docs/JAVA.md) et [`results/report_java.md`](results/report_java.md).
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
