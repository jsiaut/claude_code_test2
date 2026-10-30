# Confrontation avec le « Banc de sympathie mécanique »

**Plan pré-enregistré**, écrit le 30 octobre 2026 vers 10 h 15 (UTC), avant toute nouvelle mesure. Il est poussé sur
GitHub avant les réécritures et les mesures ; le code d'analyse le sera avant son premier calcul sur les nouvelles
données. Tout écart sera consigné dans `docs/METHODOLOGY.md` (date, raison, effet attendu).

## 1. Objet

L'étude « Banc de sympathie mécanique » (pré-enregistrée le 22/09/2026, fournie par l'utilisateur) note les langages
sur 14 principes, en niveaux de 0 à 4 : son score S juge ce que le langage rend exprimable, direct, puis garanti par
défaut, et la vitesse n'en fait pas partie. Sur les 18 langages communs, son ordre et mon classement final ont une
corrélation de rang de 0,77. Cinq langages font 83 % de la somme des carrés des écarts de rang : C (44 %), C# (16 %),
D (9 %), Zig (7 %), Nim (7 %).

Hypothèses à départager :

* **H1, construit** : leur S mesure des capacités, mon score surtout des temps.
* **H2, frontière du « standard »** : chez eux, une extension du compilateur, un intrinsèque hors de la bibliothèque
  standard, POSIX pour C, une option globale ou un module expérimental ne valent que le niveau 1 sur 4 ; chez moi, une
  capacité livrée avec la chaîne de référence compte en entier (règle v2).
* **H4, principes et poids** : 14 % de leur poids porte sur des principes que je ne mesure pas.
* **H8, notation** : une seule personne a noté chaque grille.

Quatre tests ont été proposés. Le quatrième (une notation à l'aveugle par une autre personne) n'est pas faisable tel
quel : l'utilisateur m'interdit les sous-agents et je ne peux pas recruter une personne. Je le remplace par ce qui en
tient lieu : leur grille est une notation indépendante, faite par quelqu'un d'autre, de principes qui recoupent ma
matrice (section 7).

## 2. Données de l'autre étude

Les niveaux des 18 langages communs sur les 14 principes, les poids et le score S sont transcrits dans
`analysis/banc_data.py`. Contrôle : S recalculé depuis la grille = S publié, au dixième près, pour les 18 langages.
Leur ordre de référence est celui de S (C++ et D ex aequo, rang 3,5 sur 18).

## 3. Test 1 : mon pilier C sous leur règle du standard

Chaque cellule de ma matrice (règle v2, sans C3, 18 langages) est relue. Le moyen qui justifie sa note est classé :

| Classe | Définition | Valeur |
|---|---|---|
| S | dans la norme du langage ou sa bibliothèque standard, stable, complet pour l'usage | inchangée (1) |
| S½ | standard mais partiel | 0,5 |
| N | seulement par un moyen non standard : extension, attribut, builtin ou intrinsèque du compilateur hors de la bibliothèque standard ; POSIX ou glibc pour C et C++ ; option globale du compilateur ; module expérimental, « nightly », en incubation, privé ou « package » | 0,25 (leur niveau 1 sur 4) |
| 0 | absent | 0 |

« Standard » suit leurs règles d'interprétation : norme plus bibliothèque livrée avec la chaîne de référence ; pour C
et C++, la norme ISO seule ; une liaison au système livrée dans la bibliothèque standard du langage compte (Zig
`std.os.linux`, D `core.sys.linux`, Nim `pinToCpu`, Python `os.sched_setaffinity`), une extension de la glibc non.
`System.Runtime.Intrinsics` (C#) et `std::arch` (Rust stable) sont standard. La table des cellules reclassées, avec
une raison par cellule, est publiée dans `analysis/standard_rule.py` ; toute autre cellule garde sa note v2. Ce
classement est un jugement de l'auteur, publié pour être contesté.

Résultat : pilier C_R, score MS avec C_R (autres piliers inchangés), classement.

## 4. Test 2 : mon plafond (E) sous leur restriction de code

### 4.1 Code admissible

Même notion de standard qu'au test 1. Options permises : niveau d'optimisation, choix de la cible et de la largeur
des vecteurs, mode « release » documenté du langage, nombre de threads, taille du tas. Options et moyens exclus :
relâchement de la virgule flottante (`-ffast-math`, `--no-ieee-float`, attribut `@llvmFastMathFlag`), OpenMP,
`GOEXPERIMENT`, modules en incubation, fonctions « nightly », modules privés (Mojo `std.runtime._asyncrt`), modules
« package » (Chapel `Prefetch`), pragmas et builtins propres à GNAT ou GCC, modules propres à LDC (`ldc.*`), code C
injecté ou importé (Nim `importc` d'intrinsèques). Exemptés, parce qu'ils jouent le même rôle dans tous les langages
et ne sont pas la technique mesurée : chronométrage, chargement des données d'entrée, barrières contre l'optimisation,
attributs `noinline`, lecture de la RSS.

### 4.2 Audit, fait avant toute mesure

Pour chaque langage et chaque mesure de E, la variante qui fixe le plafond dans les données principales a été relue.
Celles qui ne sont pas admissibles :

| Langage | Mesures touchées | Moyen non standard | Réécriture standard |
|---|---|---|---|
| C | K1 soa, K5 tuned | intrinsèques `immintrin.h` | sommes partielles explicites en C |
| C | K6 tuned Q1 | intrinsèques, `_pext_u32`, `__builtin_popcount` | agrégation masquée par blocs en C, `stdc_count_ones` |
| C | K3, K6 mt Q6 et Q1, K9 mt | threads POSIX | `threads.h` (C11) ; K6 mt Q1 avec le Q1 standard |
| C | K7 tuned | `__builtin_prefetch` | sans préchargement |
| C++ | K7 tuned | `__builtin_prefetch` | sans préchargement |
| C++ | K9 tuned et mt | `__restrict` | sans |
| Nim | K1 soa, K5 tuned | intrinsèques importés de `immintrin.h` | sommes partielles explicites en Nim |
| Nim | K7 tuned | `__builtin_prefetch` importé | sans préchargement |
| Nim | K1 soa, K7 tuned, K9 tuned et mt | `aligned_alloc` importé de la libc | allocation alignée en Nim standard |
| D | K1 soa, K5 tuned | `@llvmFastMathFlag` (ldc) | sans l'attribut (`core.simd` seul) |
| D | K7 tuned | `ldc.intrinsics.llvm_prefetch` | `core.simd.prefetch` |
| D | K9 tuned et mt | `ldc.simd.loadUnaligned`, `storeUnaligned` | `core.simd` |
| Ada | K5 tuned | types vectoriels et builtins GCC | sommes partielles explicites en Ada |
| Ada | K6 tuned et mt Q6 et Q1, K9 tuned et mt | `pragma Loop_Optimize` (GNAT) | sans le pragma |
| Ada | K7 tuned | builtin de préchargement GCC | sans préchargement |
| Fortran | K1 soa, K5 tuned | `!$omp simd` et `-fopenmp` | sommes partielles explicites ; binaire sans `-fopenmp` |
| Fortran | K3, K6 mt, K9 mt | OpenMP | aucun thread standard avec gfortran seul (les cotableaux demandent une bibliothèque externe) : section 4.4 |
| Chapel | K1 aos et soa, K5 tuned | binaire compilé avec `--no-ieee-float` | binaire sans cette option |
| Chapel | K7 tuned | module « package » `Prefetch` | sans préchargement |
| Go | K1 soa, K5 tuned, K6 tuned et mt Q6 | `simd/archsimd` (`GOEXPERIMENT=simd`) | boucles Go ; binaire sans `GOEXPERIMENT` |
| Java | K1 soa, K5 tuned, K6 tuned et mt Q6 et Q1 | `jdk.incubator.vector` | boucles Java |
| Mojo | K3, K6 mt, K9 mt | `std.runtime._asyncrt` (privé) ; pas d'API publique de threads CPU | section 4.4 |

Inchangés : Rust, Zig, Odin, C3, Julia, C#, JavaScript, Python. Les variantes naturelles sont admissibles partout
(exemptions de harnais comprises).

### 4.3 Principe des réécritures

Chaque réécriture garde la technique de la variante (disposition, découpage, threads, accumulateurs) et remplace
seulement le moyen non admissible par le plus proche moyen standard, ou le retire s'il n'en existe pas. Elle doit
donner les mêmes sommes de contrôle (contrôle du pilote). Les sources vont dans `bench/<langage>_std/`, copies des
sources d'origine où chaque changement est marqué « standard : », compilées par le même compilateur avec les seules
options admissibles.

### 4.4 Mesures sans implémentation admissible

* Mesures multi-threads (K6 mt Q6 et Q1, K9 mt) : le même travail sur un seul thread, c'est-à-dire le meilleur temps
  admissible à un thread de la même requête (K6 natural ou tuned, K9 natural ou tuned).
* K3 n'a pas d'équivalent séquentiel (le faux partage suppose des écrivains concurrents). Analyse principale : le
  langage reçoit le temps admissible le plus lent des 18 langages pour cette mesure. Analyse de sensibilité : K3 est
  retiré du plafond de ce langage.

### 4.5 Protocole de mesure

* Machine : l'hôte actuel, Cascade Lake du même modèle que la machine 1 (modèle 85, révision 7, 4 vCPU). Il est
  caractérisé avant les mesures (`hwprobe` : fréquence, latences, bandes passantes), pour savoir s'il ressemble à la
  machine 1 ou à la machine 2.
* Binaires d'origine : recompilés par leurs scripts inchangés ; leurs empreintes sont comparées à celles de la
  compilation sur Cascade Lake du 28 octobre (`results/hw/machine3/binaries.txt`, section « avant »).
* Plan apparié : pour chaque langage et chaque clé touchée, la variante d'origine et sa réécriture, 7 processus
  chacune, en 7 passes ; dans chaque passe, toutes les tâches dans un ordre tiré au hasard (graine fixe). Répétitions
  figées par `results/calib.json` (clé d'origine), échauffement de 10 répétitions pour les JIT et de 2 sinon. Rien
  d'autre ne tourne pendant les passes (pas de compilation).
* Fortran et Go changent d'options de compilation : si le code machine de leurs fonctions naturelles change (objdump
  avant et après), leurs variantes naturelles sont mesurées aussi, de la même façon.
* Validité : toutes les sommes de contrôle justes ; vol de temps de l'hyperviseur sous 2 % (le pilote refait la
  mesure sinon).
* Transfert : rapport apparié r = exp(moyenne des log des médianes de processus de la réécriture − même chose pour
  l'origine), par langage et par clé ; les processus des données principales sont multipliés par r. Les données
  principales de K5 viennent de la machine 3 (Emerald Rapids) : le rapport mesuré sur Cascade Lake y est transféré, et
  les boucles chaudes de K5 d'origine et réécrites sont comparées au désassemblage (rapporté).
* Contrôle de l'hôte : rapport « origine maintenant / données principales » par clé, publié (pas de règle
  d'acceptation : le transfert est apparié).

## 5. Scénarios comparés

* **A** : classement publié (pilier C v2, plafond principal).
* **B** : C_R seul (test 1).
* **C** : plafond E_R seul (test 2).
* **D** : C_R et E_R : mon étude sous leur règle.

Pour chacun : score de la configuration de référence, rang espéré sur l'analyse globale d'incertitude de la v3
(mêmes tirages ; dans B et D, C_R remplace le tirage entre les règles v1 et v2, avec le même bruit de jugement),
classement restreint aux 18 langages communs, corrélations de Spearman et de Kendall avec leur ordre, somme des
carrés des écarts de rang et part de chaque langage.

## 6. Test 3 : leur S comme quatrième pilier

MS_w = (1 − w) MS + w S sur les 18 langages (deux échelles de 0 à 100), pour w de 0 à 1 par pas de 0,05.
Incertitude : 2 000 tirages par valeur de w, combinant un tirage bootstrap de mon MS (configuration de référence) et
un tirage de leur S : poids de Dirichlet de concentration 20 centrée sur leurs poids, et chaque cellule de leur grille
décalée de ±1 (bornée à 0–4) avec une probabilité de 0,10. Résultats : la plus petite valeur de w pour laquelle
P(C premier) < 0,5 ; celle pour laquelle l'ordre combiné est plus proche du leur que du mien (Spearman) ; celle pour
laquelle sa corrélation avec leur ordre atteint 0,95.

## 7. Test 4 : accord de deux notations indépendantes

Correspondance fixée maintenant entre leurs principes et mes capacités (P6 batching/E-S, P13 hétérogène et P14 files
bornées n'ont pas d'équivalent) :

| Leur principe | Mes capacités |
|---|---|
| P1 accès prévisible | A1, F1 |
| P2 layout | A2, A3, A4, A5, A7, A8 |
| P3 SoA | A6 |
| P4 faux partage | D3 |
| P5 concurrence | D2, D5 |
| P7 allocation | B1, B2, B3, B4 |
| P8 SIMD/ILP | C1, C2, C4 |
| P9 branchements | E3 |
| P10 hiérarchie mémoire | E4 |
| P11 transparence | E1, E2, E5, E6 |
| P12 threads/topologie | C5, D1, D4, F2 |

Mesures : pour chaque principe, corrélation de Spearman sur les 18 langages entre leur niveau et la moyenne de mes
cellules correspondantes, (i) avec mes notes v2, (ii) avec mes notes sous leur règle (test 1) ; plus une corrélation
d'ensemble entre leur S restreint aux 11 principes communs et mon C restreint aux capacités correspondantes, pondéré
par leurs poids. Désaccords : les cellules où |leur niveau / 4 − ma moyenne sous leur règle| ≥ 0,5 sont listées ;
pour les correspondances à une seule capacité (P3, P4, P9, P10), le fait en cause est vérifié dans la documentation ou
par une sonde quand c'est possible, et le verdict publié.

## 8. Critères de décision, fixés maintenant

* H2 explique l'écart sur C si, dans le scénario D, C est au rang 8 ou plus loin parmi les 18 (au plus 3 places de
  leur rang 11) ; en partie s'il est entre les rangs 4 et 7 ; non s'il reste dans les 3 premiers.
* H2 explique l'écart d'ensemble si la corrélation de Spearman entre D et leur ordre atteint 0,90 ; en partie entre
  0,80 et 0,90 ; non sous 0,80 (0,77 aujourd'hui).
* La restriction touche la performance mesurée d'un langage si E_R / E < 0,95.
* Test 4 : les faits concordent si, pour les correspondances à une seule capacité et sous leur règle, au moins 80 %
  des cellules diffèrent de moins de 0,5 ; la notation, et non les faits, explique l'écart du pilier C si la
  corrélation d'ensemble augmente de (i) à (ii).
* Test 3 n'a pas de seuil : les valeurs de w sont publiées telles quelles.

## Résultats (30 octobre 2026, après les mesures)

Calcul : `analysis/confrontation.py`, poussé avant son premier calcul ; tableaux complets dans
`results/report_confrontation.md`, données dans `results/confrontation.json` et `results/raw_conf/`. Contrôle : le
scénario A rejoue exactement l'analyse publiée (mêmes rangs espérés, à 10⁻¹⁴ près). Mesures : 96 cellules × 7
processus, aucune somme de contrôle fausse. Les écarts au plan sont consignés dans `docs/METHODOLOGY.md` (30 octobre).

### Verdicts selon les critères de la section 8

| Critère | Résultat | Verdict |
|---|---|---|
| Rang de C dans le scénario D (leur rang : 11e) | 5e sur 18 | H2 explique l'écart sur C **en partie** |
| Spearman entre le scénario D et leur ordre (0,77 au départ) | 0,87 | H2 explique l'écart d'ensemble **en partie** |
| Langages dont E_R / E < 0,95 | Fortran 0,44, Mojo 0,44, Chapel 0,61, Java 0,66, Go 0,74, C 0,944 | la restriction touche leur performance mesurée |
| Accord d'ensemble des deux grilles, (i) puis (ii) | 0,83 puis 0,88 | la notation, plus que les faits, explique une part de l'écart du pilier C |
| Cellules des correspondances à une capacité à moins de 0,5 | 58 % (seuil : 80 %) | critère **non rempli** ; les désaccords sont examinés plus bas |
| Test 3 | C perd la tête dès w = 0,15 ; Spearman ≥ 0,95 dès w = 0,45 | sans seuil |

| Langage | Leur rang | A (publié) | B (C_R) | C (E_R) | D (C_R et E_R) |
|---|---|---|---|---|---|
| C | 11 | 1 | 5 | 1 | 5 |
| C++ | 3–4 | 2 | 2 | 2 | 2 |
| Odin | 2 | 3 | 1 | 3 | 1 |
| C3 | 5 | 4 | 4 | 4 | 4 |
| Zig | 1 | 5 | 3 | 5 | 3 |
| Nim | 10 | 6 | 7 | 6 | 7 |
| Rust | 6 | 7 | 6 | 7 | 6 |
| D | 3–4 | 8 | 8 | 8 | 8 |
| Ada | 7 | 9 | 9 | 9 | 9 |
| Chapel | 9 | 10 | 10 | 11 | 11 |
| Julia | 13 | 11 | 11 | 10 | 10 |
| Fortran | 14 | 12 | 13 | 13 | 14 |
| Mojo | 15 | 13 | 12 | 14 | 13 |
| C# | 8 | 14 | 14 | 12 | 12 |
| Java | 12 | 15 | 15 | 15 | 15 |
| Go | 17 | 16 | 16 | 16 | 16 |
| JavaScript | 18 | 17 | 17 | 17 | 17 |
| Python | 16 | 18 | 18 | 18 | 18 |

Spearman avec leur ordre : A 0,77, B 0,85, C 0,79, D 0,87. Part de C dans la somme des carrés des écarts : 44 %,
25 %, 48 %, 29 %.

### Test 1 : leur règle dans mon pilier C

Les 59 cellules reclassées coûtent surtout aux langages normalisés et à ceux qui passent par le compilateur C : C
88,7 → 63,3, C++ 92,4 → 76,8, Ada 76,2 → 64,7, Nim 78,6 → 68,8, D 84,1 → 74,6, Fortran 60,1 → 47,1. Zig, Odin et C#
ne bougent pas : tout ce que livre leur chaîne compte comme standard. **Sous leur règle, mon pilier C classe C 11e
sur 18, exactement son rang chez eux** (2e avec ma règle). Dans le scénario B, C passe de 1er à 5e et Odin prend la
tête.

### Test 2 : mon plafond sous leur restriction de code

Rapport apparié = temps de la réécriture standard / temps de l'original, mêmes conditions, 7 processus de chaque côté.

| Langage | Ce qui change dans les mesures qui fixent le plafond | E publié → E_R |
|---|---|---|
| C | K1 SoA et K5 en sommes partielles : 0,97 et 1,05 ; `threads.h` au lieu des threads POSIX : 0,89 à 1,01 ; Q1 sans intrinsèques : 1,89 (1,71 en multi-thread) ; K7 sans préchargement : 1,22 | 85,4 → 80,7 |
| C++ | K7 sans préchargement : 1,10 ; K9 sans `__restrict` : 1,01 à 1,03 | 78,8 → 77,7 |
| Nim | K5 sans intrinsèques : 1,37 (le C généré n'a plus de FMA) ; K7 : 1,21 | 73,0 → 70,3 |
| D | K5 sans `@llvmFastMathFlag` : 1,20 (plus de FMA) ; préchargement par `core.simd` : 0,95 | 74,8 → 73,5 |
| Ada | K5 : 1,17 ; K7 sans préchargement : 1,31 ; Q1 sans `Loop_Optimize` : 0,77, plus rapide | 73,9 → 71,1 |
| Fortran | sommes partielles au lieu de `!$omp simd` : 0,98 et 0,99 ; Q6 et Q1 : 1,09 et 1,15 ; pas de threads standard : replis et pénalité de K3 | 67,3 → 29,3 |
| Chapel | sans `--no-ieee-float` : K5 ×23, K1 SoA ×1,69 ; K7 sans `Prefetch` : 1,27 | 80,3 → 49,3 |
| Java | sans la Vector API : K5 ×4,9, Q6 et Q1 ×7,8 et ×8,7 | 57,7 → 37,9 |
| Go | sans `GOEXPERIMENT` : K5 ×9, Q6 ×2,5, K1 SoA ×1,5 | 38,6 → 28,6 |
| Mojo | pas d'API publique de threads : replis et pénalité de K3 | 68,0 → 29,9 |
| C3 | macros publiques au lieu des builtins : même code machine | inchangé |

Rust, Zig, Odin, Julia, C#, JavaScript et Python n'ont rien de non standard dans les variantes qui fixent leur
plafond. Le C standard garde 94,5 % de son plafond et reste 1er dans le scénario C. La frontière bouge sur quatre
mesures : K5 passe à C++ (`std::simd`), Q1 à C3, K7 à D (préchargement standard de `core.simd`), K1 à Nim.

Robustesse : K3 retiré du plafond de Mojo et de Fortran (sensibilité prévue) : D donne 0,86 et C 6e. Rapports de K5
forcés à 1 (contrôle hors plan, `analysis/confrontation_posthoc.py`, parce que les données de K5 viennent d'Emerald
Rapids et que le transfert du rapport n'est sûr que pour C et Fortran, dont la boucle chaude ne change pas) : 0,87 et
C 5e.

### Test 3 : leur S comme quatrième pilier

| w | 0 | 0,15 | 0,30 | 0,45 | 0,60 | 0,80 | 1 |
|---|---|---|---|---|---|---|---|
| Spearman avec leur ordre | 0,78 | 0,82 | 0,87 | 0,95 | 0,96 | 0,99 | 1 |
| P(C premier) | 0,87 | 0,36 | 0,03 | 0 | 0 | 0 | 0 |
| Rang de C | 1 | 2 | 4 | 7 | 8 | 11 | 11 |

Avec 15 % de leur score, C n'est plus premier ; avec à peu près moitié, l'ordre est le leur (0,95). C n'atteint
leur rang qu'à partir de w = 0,80.

### Test 4 : deux notations indépendantes

Accord d'ensemble sur les 11 principes communs : 0,83 avec mes notes, 0,88 sous leur règle. Par principe, l'accord
monte surtout pour les threads (0,30 → 0,76), la hiérarchie mémoire (0,57 → 0,82), le SIMD (0,60 → 0,71) et le
layout (0,66 → 0,77) ; il baisse pour la transparence (0,54 → 0,39).

Le critère par cellule n'est pas rempli (58 % au lieu de 80 %). Examen des 30 désaccords des correspondances à une
capacité :

* 27 sont des différences de portée, sur le même fait. P3 (16 cellules) : les deux grilles ne voient une SoA native
  que chez Zig et Odin (accord de rang 1,00) ; leur niveau 2 récompense une SoA écrite à la main, ma capacité A6 ne
  compte que la construction native. P4 (7) : même absence de constante de ligne de cache ; leur niveau 2 compte
  l'alignement, que ma matrice note en A4. P9 pour C#, Julia et Fortran : leur principe inclut la sélection sans
  branchement (`ifelse`, `MERGE`). P10 pour Python : leur principe inclut `mmap` et `madvise`.
* 1 tient à l'interprétation de la règle : le préchargement de Julia par `Base.llvmcall`, que je compte comme
  standard (fonction publique de Base).
* 2 portent sur un fait, vérifié de mon côté : D (`core.builtins.likely`, druntime) et Nim (`likely` et `unlikely`
  exportés par `system`) ont des indications de branchement standard ; leur niveau 2 vient peut-être d'un critère
  plus large.

Les désaccords des principes à plusieurs capacités sont de même nature : P2 pour Julia et Go (leur layout est un
contrôle explicite), P12 pour Zig, Odin, C3 et Python (ils comptent les API de threads, je compte aussi les boucles
parallèles et la localité NUMA), P5 pour D (ils pénalisent l'absence de chapitre « modèle mémoire » dans la
spécification, je note l'API).

### Ce qui explique l'écart

1. **La frontière du « standard » explique une grande part de l'écart, presque entièrement par le pilier
   capacités.** Sous leur règle, mon pilier classe C 11e, comme eux, alors que le C standard garde 94,5 % de sa
   performance mesurée.
2. **Le reste tient au construit.** Ils ne comptent pas la vitesse ; je la compte pour 65 %. Mêler à peu près
   moitié de leur score au mien reproduit leur ordre.
3. **Sur les faits, les deux notations indépendantes s'accordent** (0,83 à 0,88). Leurs désaccords portent presque
   tous sur ce que recouvre chaque principe.
4. **Ce que la restriction change à la performance mesurée** : quelques pour cent au plus pour C, C++, D, Ada et
   Nim ; rien pour Rust, Zig, Odin et C3 ; beaucoup pour Chapel, Java et Go, dont la vitesse tient à une option ou à
   un module expérimental, et pour Fortran et Mojo, faute de threads standard.

## Addendum : notation à l'aveugle (autorisée par l'utilisateur le 30 octobre, plan écrit avant le lancement)

L'utilisateur autorise, pour cette fois, un sous-agent comme second juge. Limite à garder en tête : c'est une autre
instance du même modèle, pas une personne indépendante ; elle part des mêmes connaissances générales, mais sans mes
notes, sans les leurs et sans mes conclusions.

**Aveugle.** Le sous-agent travaille dans un répertoire vide qui lui est réservé. Il lui est interdit de lire le dépôt,
l'étude fournie par l'utilisateur et mes fichiers de travail. Il peut lire la documentation et les sources livrées
avec les chaînes installées (`/opt/...`), et compiler de petites sondes pour vérifier un fait.

**Cellules.** 8 langages : C, C++, Rust, Zig, Odin, D, Nim, C# (les cinq langages qui font 83 % du désaccord, plus
trois repères). Deux grilles :

* 11 de mes capacités (C1, C2, C4, C5, D1, D2, D3, D4, D5, E3, E4), notées deux fois : avec ma règle v2 (1, 0,5, 0)
  et avec leur règle du standard telle que je l'ai rendue au test 1 (1, 0,5, 0,25, 0). Pour chaque cellule, le juge
  donne aussi le moyen, sa catégorie (norme ou bibliothèque standard, extension de la chaîne, expérimental, externe,
  absent) et sa preuve.
* 6 de leurs principes (P4 faux partage, P5 concurrence, P8 SIMD/ILP, P9 branchements, P10 hiérarchie mémoire,
  P12 threads/topologie), notés de 0 à 4 avec leur échelle et leur définition du standard, telles qu'ils les
  publient. Leurs listes d'indicateurs par principe ne sont pas publiées : le juge ne les a pas.

**Comparaisons.** (1) juge, règle v2, contre ma matrice v2 ; (2) juge, leur règle, contre ma table du test 1 ;
(3) juge, leurs principes, contre leur grille. Mesures : accord exact, kappa de Cohen pondéré (poids linéaires sur
les classes ordonnées), et pour (3) accord à un niveau près.

**Critères, fixés avant le lancement.**

* L'écart tient aux règles, pas aux juges, si le kappa pondéré atteint 0,6 dans (1) ou (2) **et** dans (3) : un
  juge indépendant retrouve chaque grille sous sa propre règle.
* Il tient aussi aux juges (H8) si l'une des comparaisons a un kappa pondéré sous 0,4 : la grille correspondante
  contient des jugements qu'un autre juge ne reproduit pas. Entre 0,4 et 0,6 : en partie.
* Chaque cellule où le juge contredit un fait de ma matrice (et non une classe) est vérifiée, et le verdict publié.

### Résultats de la notation à l'aveugle

Le second juge (`results/blind_notation.json`, notes `results/blind_notes.md`) a noté les 88 cellules et les
48 principes. Il a compilé 60 sondes, dont 13 écrites pour échouer et prouver une absence (`results/blind_probes/`).
Comparaison calculée par `analysis/blind_compare.py`, poussé avant la lecture de ses notes, sur ma matrice d'avant
correction (`results/report_blind.md`).

| Comparaison | Accord exact | Kappa pondéré | À un niveau près |
|---|---|---|---|
| (1) juge, règle v2 / ma matrice | 89 % | 0,75 | — |
| (2) juge, leur règle / ma table du test 1 | 82 % | 0,80 | — |
| (3) juge, leurs principes / leur grille | 56 % | 0,46 | 94 % |

**Verdict selon les critères fixés avant le lancement : l'écart tient aux règles en partie.** Les deux premiers
kappas dépassent 0,6 ; le troisième est entre 0,4 et 0,6.

* **Ma grille se reproduit** sous ma règle comme sous la leur.
* **La leur se reproduit à un niveau près** (94 %), mais moins exactement. Leurs listes d'indicateurs par principe ne
  sont pas publiées, et le juge ne les avait pas. Surtout, il n'accorde presque jamais le niveau 4 (« imposé ou par
  défaut ») : sur les 7 niveaux 4 de leur grille parmi ces cellules, il n'en retrouve qu'un (Rust, concurrence). Les
  trois niveaux 4 de Zig présents ici (faux partage, hiérarchie mémoire, threads) deviennent des 3. C'est la partie la
  plus subjective de leur échelle, et c'est elle qui place Zig loin devant.
* **Le juge reproduit à lui seul le renversement sur C.** En moyenne de ses notes, il classe C premier des 8 langages
  sous ma règle (C, C++, D, Zig, Odin, Nim, Rust, C#) et dernier sous leur règle (D, Zig, Odin, Rust, C#, C++, Nim,
  C), comme avec leurs principes. Sur les mêmes faits, la règle suffit à faire passer C de la tête à la queue.

**Erreurs de fait de ma matrice trouvées par le juge, vérifiées à la main :**

| Cellule | Ma note | Fait vérifié | Note corrigée (v2 ; leur règle) |
|---|---|---|---|
| C, D3 aide ligne de cache | 0 | `sysconf(_SC_LEVEL1_DCACHE_LINESIZE)` (glibc) ; `__GCC_DESTRUCTIVE_SIZE` = 64 prédéfini en C par clang 23 et gcc 16 | 1 ; 0,25 |
| D, D3 | 0 | `std.parallelism.cacheLineSize` (Phobos), `core.cpuid.dataCaches` (druntime) | 1 ; 1 |
| Odin, D3 | 0 | `base:runtime.MAP_CACHE_LINE_SIZE`, public mais réglage des tables | 0,5 ; 0,5 |
| Odin, C2 intrinsèques | 1 | `core:simd/x86` ne couvre l'AVX-512 que par 8 procédures AVX-512F et 6 AVX-512BW | 0,5 ; 0,5 |
| Nim, C5 parallélisme de données | 1 | une réduction avec l'itérateur `||` ne compile pas en `-d:release` (C généré invalide) | 0,5 ; 0,25 |

Autres faits relevés par le juge, sans changer ma note :

* L'attribut `@(fast_math={.Allow_Reassoc})` d'Odin est documenté, mais le compilateur livré ne pose jamais le
  drapeau. Son énumération donne des indices de bit, que le code teste comme des masques (vérifié dans
  `llvm_backend_opt.cpp`). Je garde 0 : la capacité est sans effet ; le juge met 0,5.

Le reste des écarts tient à la notation, pas aux faits :

* types privés de la bibliothèque standard (`CachePadded` de Rust, constantes internes de .NET et de Nim) : le juge
  les compte comme « unité interne » (0,5), moi comme absents, puisqu'on ne peut pas les importer ;
* atomiques de C# sans ordre relâché explicite ;
* affinité de C# au niveau du processus ;
* `std::simd` de GCC, dont le manuel déclare le C++26 « highly experimental ».
