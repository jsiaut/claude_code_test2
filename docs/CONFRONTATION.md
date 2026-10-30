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
