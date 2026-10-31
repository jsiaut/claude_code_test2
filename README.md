# Quels langages incarnent le mieux la *mechanical sympathy* ?

*Classement mesuré de 21 langages, octobre 2026.*

Un seul critère : la *mechanical sympathy* au sens large, c'est-à-dire la capacité d'un langage à faire écrire du
code en accord avec le matériel : disposition des données, SIMD, hiérarchie mémoire, concurrence, allocation,
requêtes analytiques. C'est ce qu'exigent le HPC, les moteurs OLAP et le Data-Oriented Design. Tout est mesuré
par moi sur des machines Intel, sauf le pilier « contrôle », qui est un inventaire jugé.

## Le classement

| Rang | Langage | Score | Rang plausible | Devance le suivant | Ce qui le place là |
|---|---|---|---|---|---|
| 1 | **C** | 80,1 | 1–4 | 70 % | Plafond le plus haut et meilleur code par défaut ; une partie des leviers passe par des extensions de compilateur |
| 2 | **C++** | 77,0 | 1–7 | 72 % | Le plus de contrôle (`std::simd`, `pmr`, atomiques) ; conteneurs standard à contre-courant du cache |
| 3 | **Odin** | 72,3 | 1–8 | 65 % | Le Data-Oriented Design dans le langage (`#soa`, `#simd`, allocateurs explicites) ; table et allocateur généralistes lents |
| 4 | **C3** | 71,0 | 2–9 | 54 % | C avec vecteurs natifs, 2e plafond ; ni SoA ni intrinsèques officiels |
| 5 | **Zig** | 71,5 | 2–11 | 61 % | Tous les leviers du DOD ; en 0.17, son vectoriseur de boucles est désactivé par l'équipe Zig (2e avec la version de développement) |
| 6 | **Nim** | 69,5 | 3–10 | 55 % | Les leviers de C par sa compilation vers C ; vérifications de bornes qui bloquent la vectorisation |
| 7 | **Ada** | 71,6 | 2–11 | 52 % | Disposition au bit près, 7e plafond ; vérifications coûteuses sur le code naturel |
| 8 | **Rust** | 69,4 | 4–11 | 66 % | 4e plafond, contrôle fin et sûr ; défauts coûteux (bornes, SipHash, SIMD portable encore instable) |
| 9 | **D** | 71,0 | 3–12 | 54 % | Le contrôle de C avec templates et CTFE ; ramasse-miettes par défaut |
| 10 | **Chapel** | 65,9 | 4–13 | 60 % | 3e plafond grâce au parallélisme natif ; leviers bas niveau rares ou instables |
| 11 | **Fortran** | 66,3 | 5–13 | 70 % | Natif du HPC (tableaux, `do concurrent`, OpenMP) ; ni SIMD explicite ni intrinsèques |
| 12 | **Julia** | 64,0 | 7–13 | 63 % | Le meilleur code naturel ; le plafond le plus bas des 13 premiers |
| 13 | **Mojo** | 62,7 | 9–13 | 98 % | Le SIMD au cœur du langage ; ni vectoriseur de boucles, ni threads publics dans `std` |
| 14 | **C#** | 54,8 | 13–16 | 84 % | La boîte à outils la plus riche des langages à GC ; objets en références, JIT sans vectoriseur |
| 15 | **Java** | 47,4 | 14–16 | 68 % | Meilleur allocateur de petits objets ; pas de types valeur |
| 16 | **Go** | 43,1 | 14–16 | 98 % | Structures par valeur ; ni vectoriseur, ni SIMD stable, atomiques séquentiellement cohérentes |
| 17 | **Haskell** | 35,4 | 17 | 98 % | Peut descendre bas, mais tout le code par défaut est paresseux et boxé |
| 18 | **OCaml** | 24,7 | 18 | 100 % | Bonne allocation générationnelle ; flottants boxés, aucun SIMD |
| 19 | **JavaScript** | 14,7 | 19–20 | 93 % | Tableaux typés bien compilés ; objets en références, aucun SIMD |
| 20 | **Python** | 10,0 | 19–21 | 64 % | Environ 200 fois plus lent que le meilleur ; la hiérarchie mémoire disparaît derrière l'interpréteur |
| 21 | **Lua** | 4,0 | 20–21 | — | Des tables seulement : ni types étroits, ni structures en ligne, ni threads, ni SIMD |

* **Score** (0–100) : 40 % de plafond mesuré (le meilleur code que le langage permet d'écrire pour la machine),
  25 % de code par défaut mesuré (le code qu'on écrit sans y penser) et 35 % de contrôle (les leviers qu'offrent le
  langage et sa chaîne de compilation).
* **Ordre** : le rang moyen sur 20 000 variantes de l'analyse, qui tirent au hasard les poids, les normalisations, le
  jugement porté sur chaque capacité et le bruit de mesure. Il suit le score, sauf pour C3 et Zig, que 54 % des
  variantes inversent, pour Ada, 4e au score mais que Nim, Zig et C3 devancent dans 55 à 69 % des variantes (son code
  par défaut est lent), pour D, que 66 % des variantes placent derrière Nim comme derrière Rust, et pour Chapel,
  derrière Fortran au score (65,9 contre 66,3) mais devant lui dans 60 % des variantes.
* **Rang plausible** : le rang dans 90 % des variantes. **Devance le suivant** : la part des variantes où le
  langage passe devant celui de la ligne suivante.
* **Errata des 30 et 31 octobre** : un second juge à l'aveugle a trouvé cinq erreurs de fait dans ma matrice de
  contrôle (aides de ligne de cache de C, de D et d'Odin, AVX-512 d'Odin, réductions parallèles de Nim), une remarque
  sur Zig une sixième (projection de fichiers), une remarque sur Ada trois autres (non-aliasing et types vectoriels
  sous-notés, allocation cachée sur-notée), une remarque sur Fortran trois encore (disposition compacte, alignement et
  allocateurs sous-notés), une remarque sur Mojo cinq autres (alignement, unions, réassociation, attente active et
  non-aliasing sous-notés), une remarque sur Julia trois encore (allocateurs, aide de ligne de cache, indication
  d'attente active sous-notés), une remarque sur Chapel trois encore (allocateurs, intrinsèques, non-aliasing
  sous-notés). Seules celles de Fortran (de la 12e à la 11e place) et de Chapel (de la 11e à la 10e) changent un rang
  à elles seules. Les remarques sur Ada et sur Fortran ont aussi trouvé deux erreurs de mon banc, corrigées et
  remesurées. Un piège de GNAT (`-fnon-call-exceptions`) laissait scalaires les noyaux optimisés d'Ada une fois
  inlinés : Ada passe de la 9e à la 7e place ([`docs/ADA.md`](docs/ADA.md)). Les noyaux de Fortran n'étaient pas
  isolés de la boucle de mesure comme ceux de C, et gfortran y laissait K4 scalaire : Fortran gagne deux places (11e
  depuis les errata de Chapel) ([`docs/FORTRAN.md`](docs/FORTRAN.md) ; 9e avec le calcul prévu par le plan, dont je me
  suis écarté sur une clé).

![Classement final](results/charts/classement.svg)

**Ce qui est sûr, et ce qui ne l'est pas.**
* **Les grandes marches sont établies.** Les 13 premiers devancent C# dans au moins 98 % des variantes, et sur les
  deux machines. Go devance Haskell, Haskell OCaml, OCaml JavaScript, dans 98 à 100 % des variantes. Ces variantes ne
  font varier ni l'effort d'implémentation ni le choix du code naturel : avec ses meilleures formes mesurées, une
  particule en `struct` et un JIT stabilisé, C# rejoint Mojo au score (62 points) et Mojo ne le devance plus que dans
  62 à 70 % des variantes, C# restant 14e ([`docs/CSHARP.md`](docs/CSHARP.md)).
* **En haut du tableau, l'ordre est la meilleure estimation, pas un fait établi.** Deux voisins s'y devancent dans
  52 à 72 % des variantes. C ou C++ est premier dans 86 % des variantes (C 61 %, C++ 25 %).
* **L'ordre fin dépend aussi de la machine.** Sur un Emerald Rapids, le même calcul donne C++ 1er, C 2e, Rust 3e.
  L'écart vient surtout de l'écrivain unique (K3), dont le temps dépend, sur ce processeur, du placement du code
  par l'éditeur de liens (voir plus bas).
* **La version du compilateur peut déplacer un langage.** Zig 0.16 et 0.17 désactivent le vectoriseur de boucles
  de LLVM, pour contourner un bug de LLVM qui compilait mal le compilateur Zig lui-même ; la version de développement
  (0.18-dev) le réactive. Avec elle, et sans changer une ligne de code, Zig passe de 71,5 à 74,8 points et du 5e au
  2e rang espéré (1er dans 24 % des variantes). Le classement garde la règle fixée d'avance, la dernière version
  stable ([`docs/ZIG.md`](docs/ZIG.md)).
* **Le plafond de K4 compte la vectorisation automatique.** La spécification n'admet pour K4 que deux formes
  scalaires : son plafond mesure ce que le compilateur fait d'une boucle scalaire, comme le code par défaut. Sans K4
  dans le plafond, C++ passe 1er devant C, Zig 3e et Mojo 12e. Le classement garde la spécification fixée d'avance
  ([`docs/MOJO.md`](docs/MOJO.md)).
* **Le contrôle pèse lourd, et il est jugé.** Il explique 69 % des écarts de score entre les 13 premiers. Sur les
  seules mesures (le plafond), la tête serait C, C3, Chapel, Rust, C++, Odin.

## Pourquoi cet ordre, langage par langage

Les temps cités viennent de la machine de référence (Cascade Lake), sauf mention d'Emerald Rapids. « Plafond » : le
pilier mesuré du meilleur code ; « code naturel » : la variante idiomatique, écrite sans penser à la machine.

![Plafond et code naturel par langage, sur les deux machines](results/charts/v3_profiles.svg)

### En tête : le contrôle de C, et un code par défaut déjà contigu

**1. C.** Le plafond le plus haut de l'étude (85) : meilleurs temps sur la somme conditionnelle sans branchement
(K4, 2,9 ms), le produit scalaire SIMD (K5) et la table de hachage plate (K7, 436 ms). Le meilleur code par défaut :
tableau de structures contigu (64 octets par particule, aucune pénalité en ordre permuté), tableau 2D vectorisé,
allocation `malloc`/`free` régulière. Presque tous les leviers existent, mais une partie passe par des extensions
de compilateur (types vectoriels, `__builtin_prefetch`, OpenMP). Sans bibliothèque de structures de données, la
table de hachage naturelle (chaînage, un `malloc` par entrée) est 12 fois plus lente que la table plate.

**2. C++.** Le plus de contrôle de l'étude (92) : `std::simd` (meilleur K5 sur Cascade Lake, 4,75 ms), arènes
`std::pmr` (K8 passe de 1,05 s à 181 ms), atomiques à ordres explicites, `mdspan`. Ce qui le retient : ses
conteneurs standard vont contre le cache. `std::unordered_map`, à nœuds chaînés, est 22 fois plus lent que la table
plate sur K7. Premier sur Emerald Rapids.

**3. Odin.** Le langage le plus proche du Data-Oriented Design : `#soa` transpose une structure en colonnes dans le
langage même, `#simd` et les intrinsèques donnent les vecteurs, l'allocateur de contexte rend chaque allocation
explicite. Deux boucles naturelles vectorisées, SIMD explicite au niveau du meilleur. Faiblesses : sa table `map`
(5 fois la table plate sur K7), son allocateur généraliste (1,9 s sur K8, latence p99,9 de 668 µs), et sa lecture
d'horloge, qui fait un appel système à chaque fois.

### Le peloton des langages compilés à types valeur

**4. C3.** C avec des vecteurs natifs, des génériques par modules, des allocateurs et `@pool` : 2e plafond de l'étude
(83), deux boucles naturelles vectorisées, latence d'allocation la plus régulière (p99,9 égale à 4 fois la médiane).
Il lui manque le SoA, les intrinsèques officiels et le contrôle de la réassociation flottante.

**5. Zig.** Tous les leviers du DOD : `std.MultiArrayList` (SoA dans la bibliothèque standard), `@Vector`, `comptime`,
allocateurs passés explicitement, aucune allocation cachée. Son plafond n'est que 11e (71), parce que Zig 0.17 ne
vectorise aucune des deux boucles naturelles mesurées. Ce n'est pas le langage : l'équipe Zig a désactivé le
vectoriseur de boucles de LLVM en 0.16 et 0.17, pour contourner un bug de LLVM. La version de développement
(0.18-dev), qui le réactive, vectorise les deux boucles sans changer une ligne de code ; Zig a alors le 4e plafond
(78,5), le meilleur code naturel de l'étude, et passe 2e en rang espéré, entre C et C++. Ses threads coûtent aussi
trois fois plus cher à lancer que ceux de la glibc (environ 160 µs contre 50 par thread).

**6. Nim.** Il compile vers C et en hérite la disposition et les compilateurs ; comptage de références déterministe
(ORC) ; l'un des meilleurs codes naturels de l'étude. Mais les vérifications de bornes gardées en `-d:release`
empêchent la vectorisation du stencil naturel (71 contre 36 ms), et sa bibliothèque standard n'a pas de types SIMD.

**7. Ada.** Le contrôle de disposition le plus précis de l'étude (clauses de représentation au bit près), des types
vectoriels GCC (`vector_type`), une règle de non-aliasing des paramètres que GNAT exploite, et le 7e plafond (78).
Ce qui le retient : ses vérifications, actives par défaut, coûtent sur le code naturel (Q1 naturel 194 ms contre 83
en C ; stencil naturel scalaire, écrit avec des bornes littérales sur un tableau non contraint), et les boucles
parallèles d'Ada 2022 restent absentes de GNAT. 4e au score, il n'est que 7e en rang espéré. Un piège de GNAT
laissait aussi scalaires ses noyaux optimisés une fois inlinés : corrigé ([`docs/ADA.md`](docs/ADA.md)). Son
meilleur temps sur K8 vient d'une arène que GCC compile bien, pas de ses pools de stockage.

**8. Rust.** 4e plafond (80) et un contrôle fin et sûr : `repr(C)`, `repr(align)`, `std::arch` avec AVX-512 stable,
flottants `algebraic_*` pour réassocier opération par opération, seule file standard sans verrou. Il perd sur les
défauts : vérifications de bornes qui bloquent la vectorisation du stencil naturel (73 contre 36 ms), `HashMap` à
SipHash (9 fois la table plate sur K7), SIMD portable encore réservé à *nightly*. 3e sur Emerald Rapids.

**9. D.** Le contrôle de C avec templates, exécution à la compilation, `core.simd` et atomiques à ordres explicites.
Ce qui le fait reculer : son ramasse-miettes par défaut, qui donne la pire pause des langages compilés sur K8
(127 ms), et un stencil naturel `double[][]` non vectorisé.

### Forts sur leur terrain, avec moins de contrôle ou un runtime

**10. Chapel.** 3e plafond (80) grâce au parallélisme de données natif (`forall`, `reduce`) et aux tableaux
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

**12. Julia.** Structures immuables stockées en ligne, fonctions spécialisées par types et JIT LLVM : les deux boucles
naturelles sont vectorisées, et son code naturel est le meilleur de l'étude. Ce qui la place 12e, c'est d'abord son
plafond (67, le plus bas des 13 premiers) : ses versions optimisées de K8, Q1, K5 et K7 restent loin des meilleures,
en partie parce qu'elles sont moins travaillées que celles des autres langages ; réécrites comme le propose un
relecteur, elles lui vaudraient 3 à 5 points et la 9e à la 11e place ([`docs/JULIA.md`](docs/JULIA.md)). Son runtime
pèse moins : sur K8, le ramasse-miettes porte bien la latence p99,9 à 70 fois la médiane, mais son code par défaut
reste au niveau de celui de Rust. Sur la file de K10 (hors score), le blocage que j'attribuais à l'ordonnanceur venait
de mon code : une variable capturée faisait allouer, et la collecte attendait le thread en attente active.

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
octets ; en `struct`, une particule tiendrait 64 octets, +1,9 point), et des versions optimisées mieux travaillées (K8
en pile explicite, K4 déroulé) vaudraient 2,6 à 4 points. Avec trois échauffements, ses boucles tournent en code OSR :
l'effet moyen est faible (moins d'un point), mais une méthode chargée de vecteurs peut y perdre l'optimisation. Toutes
ces sensibilités cumulées le mettent au niveau de Mojo au score, toujours 14e ([`docs/CSHARP.md`](docs/CSHARP.md)).

**15. Java.** Excellent modèle mémoire (`VarHandle`), JIT C2 efficace, et le meilleur allocateur de petits objets
de l'étude (K8 naturel, 301 ms). Pas de types valeur dans le JDK 27 : 78 octets par particule, parcours permuté 4,9
fois plus lent ; la Vector API reste en incubation, et Valhalla (JDK 28) n'aplatit pas encore une structure de
64 octets.

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
2. **Le SIMD explicite** divise le produit scalaire par 20 à 40 : 3,7 à 5,7 ms dans les langages compilés et en C#,
   contre 77 à 166 ms pour la boucle naturelle en ordre strict (Emerald Rapids). Java (Vector API, 6,9 ms) et Go
   (expérimental, 19 ms) suivent de loin ; OCaml et JavaScript n'en ont pas.
3. **La vectorisation automatique se vérifie sur le code exécuté.** Aucune des deux boucles naturelles testées n'est
   vectorisée en C#, Go, Mojo (dont le compilateur n'a pas de vectoriseur de boucles), Zig 0.17 (vectoriseur de
   boucles désactivé par l'équipe Zig, réactivé dans la version de développement), Haskell, OCaml, JavaScript, Lua et
   Python. Les vérifications de bornes l'empêchent sur le stencil naturel en Rust, Nim, D et Ada (55 à 80 ms, contre
   36 ms) ; en Ada, sur un type contraint, GNAT élimine les vérifications et vectorise. En Mojo, elles coûtent plus
   que l'absence de vectorisation : sans elles, le stencil naturel passe de 169 à 41 ms (C : 28 ms) et Q1 de 137 à
   67 ms, au niveau de C (même machine). Le contexte d'appel compte aussi : inlinés dans la boucle
   de mesure, les deux noyaux de K4 de Fortran restaient scalaires, alors que leurs copies hors ligne, vectorisées,
   n'étaient jamais appelées (corrigé).
4. **Le compilateur pèse autant que le langage.** Sur le même code C, GCC est 2,2 à 2,7 fois plus rapide que clang
   sur l'arène de K8. Sur Emerald Rapids, clang, flang, Chapel et Mojo fusionnent la réduction naturelle de K5 en FMA
   scalaire, deux fois plus lente qu'une addition sur ce cœur ; GCC l'évite. Sur Cascade Lake, l'écart disparaît.
5. **Le placement du code aussi.** Sur Emerald Rapids, la boucle de l'écrivain unique (K3) coûte 1 ou 7 cycles par
   incrément selon son alignement. Huit dispositions tirées au hasard par l'éditeur de liens donnent 12 à 23 ms ou 74
   à 117 ms pour le même source en C (clang) ou en Rust ; le code de GCC reste rapide dans les huit.
6. **Concurrence.** Go et Haskell n'ont que des écritures atomiques séquentiellement cohérentes : l'écrivain unique y
   est 6 fois plus lent. Le verrou global de Python sérialise les threads : sur K3, à peine plus d'un cœur sur quatre
   travaille, pour 24 000 `futex` par répétition (Emerald Rapids).
7. **Allocation.** Une arène divise K8 par 5 ou 6. Les allocateurs générationnels de Java et d'OCaml sont les
   meilleurs pour du code naturel (300 ms). Les ramasse-miettes laissent des queues : pause de 127 ms en D, p99,9 à
   70 fois la médiane en Julia, arrêt de 1,08 s en Python. Les runtimes font des centaines à des dizaines de milliers
   d'appels système par répétition, le code compilé un ou deux.
8. **Le système compte.** Odin, Lua et LuaJIT font un appel système à chaque lecture d'horloge. Sur K7, Rust, Zig,
   Odin et flang rendent la mémoire de leur table au système à chaque répétition, et la paient en défauts de page
   (1 à 5 % du temps).

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
  (réplication complète). Pas de compteurs matériels ; les compteurs du noyau (appels système, défauts de page,
  uprobes) servent aux faits de mécanisme ([`docs/INSTRUMENTS_V3.md`](docs/INSTRUMENTS_V3.md)).
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
  l'autre. Sept langages ont été relus après coup par des connaisseurs. Ada et Fortran y ont gagné deux places chacun,
  par la correction de mon banc (un piège de GNAT ; des noyaux que gfortran inlinait dans la boucle de mesure) ;
  Chapel une place par trois errata de la matrice ; Mojo 2,7 points et Julia 1,8 point, mais aucune place, par des
  errata de la matrice ; Zig trois places, mais par une version de compilateur que la règle exclut ; C# rien, sa
  remarque ne relevant ni erratum ni erreur du banc. Des versions optimisées mieux travaillées vaudraient une à trois
  places de plus à Julia et, cumulées avec un autre choix de code naturel et un JIT stabilisé, 7 à 8 points à C#,
  assez pour rejoindre Mojo au score : la règle les garde hors du classement, mais l'effort d'implémentation compte.
* Ces corrections ont été mesurées après coup sur une autre machine Cascade Lake, puis reportées sur les données
  principales par des rapports appariés ; pour une clé de Fortran, par un témoin mesuré sur le même hôte, au prix
  d'un écart au plan ([`docs/FORTRAN.md`](docs/FORTRAN.md), 4.2).
* Des microbenchmarks : ni E/S, ni décompression, ni tri ou jointure ; une seule taille d'entrée par noyau, sauf K2.
* Des règles de construit : bibliothèque standard seule, compilation pour le CPU hôte, ni PGO ni LTO, réglages des
  runtimes par défaut.
* Le pilier « contrôle » est jugé par un seul évaluateur ; c'est lui qui départage le plus le haut du tableau.
* Une seule version de compilateur par langage, la dernière stable au 28 octobre. Un réglage temporaire d'une chaîne
  peut coûter des rangs : Zig 0.17, dont le vectoriseur de boucles est désactivé, perd trois places en rang espéré par
  rapport à sa version de développement. Je n'ai mesuré deux versions que pour Zig et pour C# (.NET 11, en
  préversion : 0,99 fois les temps de .NET 10 en moyenne, aucune place gagnée). Et un seul compilateur par langage :
  Fortran est classé avec gfortran ; flang n'est mesuré qu'en annexe, ifx pas du tout.
* La règle de la bibliothèque standard pèse plus sur Mojo que sur les autres : depuis juillet 2026, `parallelize`,
  le GPU et les tenseurs sont dans le paquet MAX. Le classement mesure Mojo et sa `std` sur CPU ; ses noyaux à
  threads passent par un module privé de `std`.
* Le plafond de K4 n'admet que des formes scalaires et compte donc la vectorisation automatique (voir plus haut).
* Trois échauffements pour les langages à JIT : les boucles chaudes tournent souvent en code OSR (compilé pour
  reprendre une boucle en cours), sans atteindre le niveau d'optimisation final. Mesuré pour C# : 0 à 2,5 % en moyenne
  (moins d'un point), de −15 % à +16 % selon le noyau ([`docs/CSHARP.md`](docs/CSHARP.md)) ; non mesuré pour Java,
  JavaScript et Julia.

## Une autre étude, un autre ordre : pourquoi

Le « Banc de sympathie mécanique », une étude voisine faite sur le même processeur que ma machine 3, classe C 11e sur
18 langages communs, là où je le classe 1er. Corrélation de rang entre les deux ordres : 0,76 (0,77 le 30 octobre,
avant les errata de ma grille). Je l'ai confrontée à la mienne par quatre tests pré-enregistrés
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
* **Les deux règles à la fois** : C passe 5e, la corrélation monte à 0,87. Le reste de l'écart tient à la question
  posée : leur score ne compte pas la vitesse. Mêler à peu près moitié de leur score au mien reproduit leur ordre.
* **Sur les faits, les deux grilles, notées indépendamment, s'accordent** (0,74 à 0,81 ; 0,83 à 0,88 le 30 octobre :
  les errata de ma grille, surtout ceux de Mojo et de Julia, l'en ont éloignée). Leurs désaccords portent presque tous
  sur ce que recouvre chaque principe.
* **Un second juge, à l'aveugle** (un sous-agent sans accès aux deux grilles ni à mes conclusions), retrouve ma grille
  du 30 octobre sous ma règle (kappa pondéré 0,75) comme sous la leur (0,80 ; 0,85 et 0,86 sur ma grille corrigée
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
python3 analysis/analyze_v3.py             # analyse -> results/summary_v3.json, results/report_v3.md
```

```bash
python3 analysis/confrontation_current.py  # confrontation et juge à l'aveugle, état actuel -> results/*_current*
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
