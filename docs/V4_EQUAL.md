# v4, point 3 : des conditions égales — plan (21 novembre 2026)

*Plan d'ensemble : `docs/V4_PLAN.md` (point 3). Ce plan est poussé avant tout changement de code et toute mesure ; les
écarts éventuels seront datés et justifiés dans `docs/METHODOLOGY.md`.*

## 1. Question

La troisième remarque générale (`docs/AUDIT3_2026-11-18.md`, 5) relève trois conditions qui ne sont pas les mêmes
pour tous les langages : les vérifications à l'exécution du code naturel, la structure du stencil naturel, et
l'interdiction du SIMD explicite dans K4. Le point 3 change ces règles pour tous, mesure l'effet de chaque changement
sur le classement, et fixe d'avance les règles de la campagne finale de la v4. Le point 2 a trouvé deux conditions de
mesure inégales du même ordre (`docs/V4_SIZES.md`, 10.6) : le placement de la boucle de K3 et les deux régimes de K2
à 8 Mio. Elles sont traitées ici aussi (3.4 et 3.5).

## 2. Faits établis avant le plan

* **Vérifications du code naturel.** Règle actuelle (`docs/NATURAL.md`) : mode de publication documenté de la chaîne,
  « vérifications à l'exécution conservées quand ce mode les conserve ». Sans vérifications dans leur mode publié :
  Zig (`-O fast`), C3 (`-O3`, « Unsafe » selon `c3c --help`), Chapel (`--fast`, « Disable checks »), D (`-release` :
  bornes vérifiées dans les seules fonctions `@safe`), FreePascal (`{$R-}`, `{$Q-}` par défaut), et C, C++ et
  Fortran, qui n'en ont pas dans leur mode par défaut. Avec vérifications : Rust (bornes), Swift (`-O` : bornes et
  débordements), Ada (défaut de GNAT), Nim (`-d:release`), Odin (`-o:speed` : bornes), Julia, Mojo (assertions de
  `List` actives par défaut, `docs/MOJO.md`), et les langages gérés ou interprétés (C#, Java, Go, Haskell, OCaml,
  JavaScript, Python, Lua, PHP, BQN).
* **Options vérifiées dans les chaînes installées** (21 novembre, aide de chaque outil) : pour activer, `zig -O safe`,
  `c3c --safe=yes`, `chpl --checks` (« Enable all following run-time checks », après `--fast`), `ldc2
  -boundscheck=on`, `fpc -Cr -Co` ; pour retirer, `swiftc -Ounchecked`, `nim -d:danger` (`config/nim.cfg`), `odin
  -no-bounds-check`, `julia --check-bounds=no`, `go tool compile -B` (« disable bounds checking »), `ocamlopt -unsafe`,
  `mojo -D ASSERT=none` (`docs/MOJO.md`), `gnatmake -gnatp` (à sonder). Rust ne retire pas ses vérifications par une
  option ; C#, Java, Haskell, JavaScript, Python, Lua, PHP et BQN non plus.
* **Stencil naturel (K9).** Contigu en C, C#, Zig, Odin, Julia, Ada, Fortran, C3, Chapel, FreePascal, Haskell et BQN ;
  imbriqué (tableau de tableaux) en C++, Java, JavaScript, Python, D, Rust, Nim, Mojo, Go, OCaml, Lua, Swift et PHP
  (`docs/NATURAL.md`, `docs/AUDIT3_RESPONSE.md`). Le code optimisé est en grille plate partout.
* **K4.** La spécification n'admet que deux formes scalaires (`docs/SPEC.md`) ; le plafond prend la meilleure des deux
  (`natural_unsorted`, `branchless_unsorted`), le code naturel `natural_unsorted` : la vectorisation automatique compte
  deux fois. Un K4 en SIMD explicite existe déjà pour Mojo (`bench/mojo_exp`) et C# (`bench/csharp_exp`), mesuré par
  leurs remarques et non adopté, faute de règle pour tous. La grille (règle v2) crédite 18 langages d'un SIMD explicite
  (types vectoriels C1 ou intrinsèques C2 non nuls) ; 7 n'en ont pas : Fortran, JavaScript, Python, OCaml, Lua, BQN,
  PHP.
* **K3.** Sur Emerald Rapids, la boucle de l'écrivain unique coûte un ou sept cycles par incrément selon son décalage
  dans sa ligne de 64 octets (`docs/FINDINGS.md`, `tools/k3_align.c`) ; l'effet existe aussi sur Granite Rapids et
  il est le premier moteur de l'effet de l'hôte du point 2 ; six implémentations y passent sous la borne de 5 cycles
  de la v3 (`docs/V4_SIZES.md`, 10.5).
* **K2 à 8 Mio** a deux régimes d'un processus à l'autre sur Emerald Rapids (0,15 à 0,28 s ou 0,44 à 0,81 s sur la
  machine 31 ; 15 constructions sur 28 ont au moins un processus lent ; `docs/CPP.md`, `docs/V4_SIZES.md` 10.2). Les
  pages géantes transparentes de l'hôte sont en mode `madvise`.
* **Hôte.** Le conteneur a redémarré le 21 novembre vers 7 h 30 sur un Xeon du même modèle que la machine 31
  (famille 6, modèle 207, stepping 2, « @ 2.10GHz », 4 vCPU) : machine 32. Les données de base de ce plan sont celles du
  calcul « Hôte » du point 2 (machine 31, taille publiée).

## 3. Règles communes, fixées ici pour la campagne finale de la v4

### 3.1 R1 : vérifications du code naturel actives pour tous

Nouvelle règle du code naturel : le mode de publication documenté de la chaîne, **avec les vérifications à
l'exécution que la chaîne offre, activées par son option documentée quand ce mode les retire**. Raisons : c'est déjà
le mode de 17 langages sur 25 ; la direction inverse est impossible pour Rust, C#, Java, Haskell, JavaScript, Python,
Lua, PHP et BQN, qui n'ont pas d'option pour les retirer, alors que celle-ci n'a qu'une exception, l'accès par
pointeur en C, que le langage ne peut pas vérifier. Les variantes optimisées (plafond) ne changent pas : elles gardent
leur mode publié, et le plafond reste le meilleur code que le langage permet d'écrire.

| Langage | Mode publié | R1 (règle) | R1' (sensibilité : sans vérifications) |
|---|---|---|---|
| C | clang `-O3` : aucune | `-fsanitize=array-bounds -fsanitize-trap=array-bounds` (tableaux de taille connue seulement) | publié |
| C++ | g++ `-O3` : aucune | `-D_GLIBCXX_ASSERTIONS` (bornes des conteneurs de libstdc++) | publié |
| Fortran | gfortran `-O3` : aucune | `-fcheck=bounds` | publié |
| Zig | `-O fast` | `-O safe` | publié |
| C3 | `-O3` | `-O3 --safe=yes` | publié |
| D | `-O3 -release` | `-boundscheck=on` en plus | `-boundscheck=off` |
| Chapel | `--fast` | `--fast --checks` | publié |
| FreePascal | `-O3` | `-Cr -Co` en plus | publié |
| Rust | bornes vérifiées | publié | aucune option : inchangé |
| Swift | `-O` | publié | `-Ounchecked` |
| Ada | défaut de GNAT | publié | `-gnatp` |
| Nim | `-d:release` | publié | `-d:danger` |
| Odin | `-o:speed` | publié | `-no-bounds-check` |
| Julia | défaut | publié | `--check-bounds=no` |
| Mojo | défaut | publié | `-D ASSERT=none` |
| Go | défaut | publié | `-gcflags=-B` |
| OCaml | défaut | publié | `-unsafe` |
| C#, Java, Haskell, JavaScript, Python, Lua, PHP, BQN | vérifiées | publié | aucune option : inchangé |

« Vérifications » désigne ce que le mode vérifié de chaque chaîne active (bornes partout ; débordements, pointeurs
nuls ou contrats selon la chaîne) : la règle égalise la politique, pas la liste, qui fait partie du langage.

### 3.2 R2 : stencil naturel en grille contiguë pour tous

Le K9 naturel prend pour tous la structure du code optimisé : **une grille contiguë**, le tableau 2D contigu du
langage s'il en a un (inchangé pour les 12 langages déjà contigus), sinon un tableau 1D de son conteneur par défaut,
indexé `i*M + j`, avec la même boucle que son naturel publié. Nouvelles implémentations (13) : C++
(`std::vector<double>`), Java (`double[]`), JavaScript (`Array`), Python (`list`), D (`double[]`), Rust (`Vec<f64>`),
Nim (`seq[float]`), Mojo (`List[Float64]`), Go (`[]float64`), OCaml (`float array`), Lua (table), Swift (`[Double]`),
PHP (tableau). La structure idiomatique publiée est la sensibilité. La grille imbriquée pour tous n'est pas retenue :
elle n'est l'idiome d'aucun des langages qui ont un tableau 2D natif (C#, Fortran, Ada, Chapel, Julia, FreePascal) et
n'est la forme d'aucun code optimisé.

### 3.3 R3 : K4 admet une variante `tuned`, SIMD explicite compris

K4 suit la règle des autres noyaux : une variante **`tuned`**, de forme libre, SIMD explicite compris (types vectoriels
du langage ou intrinsèques de sa chaîne standard), même somme exacte. Le plafond de K4 prend la meilleure des trois
formes ; le code naturel (`natural_unsorted`) ne change pas. Chaque langage écrit sa variante avec la forme que la
grille lui reconnaît :

| Forme | Langages |
|---|---|
| Intrinsèques de la plateforme ou importées | C (`immintrin.h`), C++ (`immintrin.h` ou `std::experimental::simd`), Rust (`std::arch`), Nim (`importc` depuis `immintrin.h`), Ada (type vectoriel de GCC et builtins importés), Chapel (`extern proc` depuis `immintrin.h`), Go (`simd/archsimd`), FreePascal (assembleur en ligne AVX2, sa seule voie : `-Sv` n'a ni masque ni octets) |
| Types vectoriels du langage | Zig (`@Vector`), Odin (`#simd`), C3 (`char[<64>]`), D (`core.simd`), Mojo (`SIMD`, forme de `bench/mojo_exp`), Swift (`SIMD64<UInt8>`), C# (`Vector512<byte>`, forme de `bench/csharp_exp`), Java (Vector API), Julia (`VecElement` et `llvmcall`), Haskell (primitives SIMD de GHC, si elles permettent la comparaison d'octets ; sinon sa meilleure forme scalaire, avec la raison) |
| Sans SIMD explicite : la meilleure forme du langage et de sa bibliothèque standard | Fortran, JavaScript, Python, OCaml, Lua, BQN, PHP |

Les formes plus générales que la sienne (mots de 64 bits traités comme 8 octets, par exemple) relèvent du point 4
(une même forme tentée dans tous les langages).

### 3.4 R4 : K3 rapporté à une référence de placement

La cellule de K3 dans le plafond (meilleur de `sw_padded` et `rmw_padded`) devient **min(1, b3 / t)** dans toutes les
variantes de l'analyse, au lieu du rapport à la frontière (le langage le plus rapide) ou à la borne de 5 cycles par
incrément. **b3** est le temps de 2^25 incréments de la boucle de référence de l'écrivain unique (`tools/k3_align.c` :
16 `incq` en mémoire), médiane de ses 16 décalages dans une ligne de 64 octets (meilleur de trois exécutions par
décalage), mesuré sur l'hôte de la campagne, au début et à la fin, moyenne des deux. Une boucle placée sur un bon
décalage ne vaut plus mieux qu'une boucle placée au décalage le plus courant ; l'écart entre les langages qui
écrivent sans `lock` et ceux qui ne le peuvent pas (atomiques séquentiellement cohérentes de Go, Haskell, OCaml,
JavaScript) reste entier. Le code par défaut ne contient pas K3 et ne change pas.

### 3.5 R5 : K2 mesuré par sept processus

Dans la campagne finale, chaque cellule de K2 (dix tailles) est mesurée par sept processus au lieu de trois, répartis
sur les passes (3, 2, 2), pour que le régime d'un processus pèse moins. Une sonde décrit le mécanisme avant la
campagne du point 3 (descriptive, sans effet sur la règle) : K2 du C à 8 Mio, 20 processus dans chacune de trois
conditions (adresses aléatoires par défaut, adresses fixes par `setarch -R`, tampon marqué `MADV_HUGEPAGE`), avec le
temps et les pages géantes du processus (`AnonHugePages`).

## 4. Code

* **Copies** `bench/<langage>_eq` : source publié, plus la variante `k4 tuned` (25 langages) et la variante
  `k9 natural_flat` (les 13 langages imbriqués), déclarées dans `extra_variants`. Les binaires publiés ne changent
  pas.
* **Constructions** : `bench/<langage>` (publié) et `bench/<langage>_eq` sont construits dans le mode publié ; le source
  publié l'est aussi dans le mode R1 (8 langages) et dans le mode R1' (8 langages), et la copie dans ces modes pour les
  langages imbriqués qui en ont un (C++ et D en R1 ; Nim, Mojo, Swift, Go et OCaml en R1'), pour les calculs combinés.
  Les constructions des modes R1 et R1' partent du source publié pour que seul le mode change.
* **Sondes de mode** (`results/equal/probes`) : pour chaque mode R1 et R1', un programme qui sort des bornes dans le
  même genre d'accès que le code naturel (tableau alloué, tableau 2D) ; chaque mode R1 doit s'arrêter, chaque mode R1'
  et publié sans vérification ne doit pas. Un mode dont la sonde ne se comporte pas comme prévu est corrigé avant toute
  mesure, et l'écart est daté.
* **Validation** : sommes de contrôle de chaque nouvelle cellule (variante ou mode) à la taille publiée, un processus
  par cellule, avant la campagne, égales à celles du C.
* Le pilote et l'analyse sont de nouveaux outils (`tools/equal/`, `analysis/equal_v4.py`), poussés avant la campagne.

## 5. Hôte

La campagne se fait sur un hôte du modèle de la machine 31 (6/207/2), pour que ses rapports s'appliquent aux données de
base du point 2. Avant les mesures, à machine au repos : caractérisation (`tools/sizes/hwchar.sh`,
`results/hw/machine32`), mesure de b3, sonde de K2. Si le modèle change, la règle de `docs/V4_SIZES.md` (5) s'applique,
et les cellules de la taille publiée du point 2 entrent dans la campagne pour refaire la base sur le nouveau modèle.

### 5.1 Écart au plan (21 novembre, 8 h, après la caractérisation, avant toute mesure de la campagne)

* **Faits.** La machine 32 est du modèle de la machine 31, mais ne se comporte pas comme elle (`results/hw/machine32`
  contre `results/hw/machine31`) : la latence passe à celle de la mémoire entre 8 et 16 Mio (102 ns à 16 Mio, contre
  40 ns sur la machine 31, dont le L3 effectif allait jusqu'à 16 à 24 Mio) ; STREAM triad sur 4 fils donne 176 Go/s
  (226) ; le pic FMA AVX-512 165 Gflop/s (179). La part du L3 partagé qu'obtient la machine virtuelle diffère donc d'un
  hôte à l'autre du même modèle.
* **Conséquence.** Les rapports mesurés sur la machine 32 ne valent pas pour les données de la machine 31 : les 16 Mio
  de K4, par exemple, tiennent dans le L3 effectif de l'une et pas de l'autre, et le gain d'un K4 en SIMD dépend de la
  bande passante du niveau où sont les données. **La base est donc refaite sur la machine 32, dans la campagne du
  point 3** : toutes les cellules du calcul « Hôte » à la taille publiée (K1 à K9, binaires publiés ; K10, hors score,
  n'est pas mesuré), qui servent aussi de références aux nouvelles cellules. L'analyse (section 8) porte sur les seules
  données de la machine 32, avec ses bornes physiques, et chaque calcul remplace directement les cellules qu'une règle
  change par celles qui sont mesurées dans le nouveau mode ou la nouvelle forme, sans report de rapport. Le calcul
  « Hôte » de la machine 31 (point 2) et celui de la machine 32 sont comparés, en réplication descriptive.
* **b3 (3.4), début de la campagne** : 84,15 et 84,85 ms (médianes des 16 décalages, deux exécutions ;
  `results/equal/k3_ref_start.txt`). La boucle est rapide à 5 décalages sur 16 (8, puis 36 à 48 : 12 à 16 ms), lente
  aux 11 autres (63 à 88 ms), comme sur les Emerald Rapids précédents.
* **Sonde de K2 (3.5)** : sur la machine 32, aucun des 60 processus n'a le régime lent de la machine 31 (0,145 à
  0,169 s avec adresses aléatoires ou fixes ; 0,131 à 0,151 s avec 8 Mio de pages géantes ; `results/equal/k2_probe.txt`).
  Les deux régimes de la machine 31 ne tiennent donc ni aux adresses virtuelles ni au TLB ; le régime lent (0,44 à
  0,81 s, environ 105 à 190 ns par saut) a la latence de la mémoire, comme si les 8 Mio sortaient par moments du L3
  effectif (hypothèse, non vérifiée). R5 ne change pas.

### 5.2 Écarts au plan (21 novembre, après les copies, les constructions et les sondes, avant toute mesure de la campagne)

* **BQN n'a pas de variante `tuned` de K4** (3.3 : 25 langages, donc 24). Trois formes essayées, toutes justes : le
  filtre `+´ (128 ≤ d) / d` (sa forme naturelle publiée, 7,0 ms), le masque `+´ d × 128 ≤ d` (sa forme sans branche
  publiée, 7,1 ms) et l'histogramme `/⁼` (7,6 ms). Aucune ne bat les deux formes publiées, qui s'exécutent déjà dans
  les primitives vectorisées de CBQN ; son plafond de K4 reste le meilleur des deux formes publiées.
* **D est aussi mesuré dans le mode R1'** (`-boundscheck=off`), comme le prévoit le tableau de 3.1 ; les sections 4, 6
  et 8 l'oubliaient (« 8 » langages, copie en R1' pour Nim, Mojo, Swift, Go et OCaml seulement). Le mode publié
  (`-release`) ne retire les vérifications de bornes que du code `@system` : celles du code `@safe`, dont les modèles
  de Phobos instanciés dans le programme, restent. Le binaire publié contient 893 appels aux gestionnaires de
  dépassement, 177 avec `-boundscheck=off` (ceux de la bibliothèque précompilée) et 965 avec `-boundscheck=on` ; les
  noyaux naturels nommés (`k1Natural`, `k4Natural`, `k5Natural`, `k9Natural`) n'en ont aucun dans le binaire publié
  (`results/equal/builds.txt` ; `objdump`). R1' compte donc 9 langages, et la copie de D est aussi construite dans ce
  mode (`eq_unc`), pour le calcul 8.
* **Les variantes des copies sont listées dans `eq_variants`**, et non `extra_variants` (section 4) : ce fichier, copié
  du source publié, garde les variantes propres déjà publiées (K8 `tuned_alloc`).
* **Base** : les cellules du score à la taille publiée (`analysis/analyze_v3.py`, `needed_keys` : 27 cellules par
  langage, dont K2 à ses trois tailles du score et K3 `sw_padded` et `rmw_padded`), soit 655 processus par passe, et
  188 nouvelles cellules : 843 processus par passe (`tools/equal/campaign.py --dry`). Les binaires publiés de la
  campagne sont reconstruits sur la machine 32 depuis les sources suivies (`/dev/shm/msbuild/<langage>/pub`), comme
  les autres constructions.
* **Faits établis avant la campagne.** Les modes ajoutés aux `build.sh` ne changent pas les binaires publiés : sans
  `MS_MODE`, les commandes du compilateur sont les mêmes et les binaires identiques octet pour octet (14 langages) ;
  ceux de Swift ne diffèrent que par l'identifiant de construction et l'empreinte du module, qui diffèrent aussi entre
  deux constructions avec l'ancien script (`results/equal/hookcheck.txt`). Chaque mode change le binaire
  (`results/equal/builds.txt`). Les sondes de mode se comportent comme prévu (`results/equal/probes/probes.txt`) : les
  8 modes R1 s'arrêtent sur la lecture hors des bornes (le C sur les rangées de taille connue de son K9 seulement :
  l'accès par pointeur n'est pas vérifiable, 3.1), les 9 modes R1' et les modes publiés sans vérification ne
  s'arrêtent pas, les modes publiés vérifiés s'arrêtent.
* **Analyse** (`analysis/equal_v4.py`, essayée sur des données fictives avant la campagne) : la cellule de K3 de R4
  est obtenue en relevant les temps de K3 à b3 au moins et en prenant b3 pour référence dans les deux normalisations,
  ce qui donne min(1, b3 / t) partout ; la cellule K4 `tuned` de R3 est tirée comme les autres cellules de K4 (mêmes
  réservoirs de résidus), par un générateur à part pour que les autres tirages ne changent pas ; chaque mesure de b3
  (début, fin) est la moyenne des médianes de deux exécutions de `tools/k3_align.c`.

## 6. Cellules (taille publiée)

Chaque nouvelle cellule est mesurée avec sa cellule de référence, du même langage, dans la même campagne (et, depuis
l'écart 5.1, avec toute la base à la taille publiée) :

| Règle | Nouvelle cellule | Référence | Langages |
|---|---|---|---|
| R1, R1' | les cellules naturelles (K1 `natural` et `natural_shuffled`, K4 `natural_unsorted`, K5, K6 Q1 et Q6, K7, K8 avec ses latences, K9), dans le mode R1 ou R1' | la même cellule, binaire publié | 8 et 8 |
| R2 | K9 `natural_flat` (mode publié ; R1 pour C++ et D ; R1' pour Nim, Mojo, Swift, Go, OCaml) | K9 `natural`, binaire publié | 13 |
| R3 | K4 `tuned` | K4 `branchless_unsorted`, binaire publié | 25 |

Environ 190 nouvelles cellules ; avec la base (5.1), environ 520 cellules par passe.

## 7. Campagne

Le pilote du point 2 (`tools/sizes/campaign.py`), adapté : groupes par noyau, ordre aléatoire des groupes puis des
blocs à graine fixe différente à chaque passe, trois passes, répétitions fixées par la première passe (environ 3 s par
processus, au moins trois), échauffement des JIT, vol de temps au-delà de 5 % refait une fois, sentinelle de mémoire
(plus grand VmRSS), écritures dans `results/equal/work`, recopiées et poussées à chaque fin de groupe. Aucune autre
mesure ne tourne pendant la campagne.

## 8. Analyse, fixée avant les mesures

La méthode v3 du point 2 (même graine, 20 000 variantes, mêmes poids, grille v2 corrigée par le point 1), appliquée à
la base « Hôte » refaite sur la machine 32, avec ses bornes physiques (écart 5.1 : la base et les nouvelles cellules
viennent de la même campagne, et chaque calcul substitue directement les cellules mesurées ; le report de rapports
prévu ici d'abord n'a plus d'objet). Calculs :

1. **Hôte** : la base, refaite.
2. **R1** : cellules naturelles des 8 langages en mode vérifié (dans le code par défaut et, là où la variante
   naturelle entre dans le plafond, dans le plafond).
3. **R1'** (sensibilité) : cellules naturelles des 8 autres en mode sans vérifications.
4. **R2** : K9 naturel contigu pour les 13 langages imbriqués.
5. **R3** : plafond de K4 au meilleur des trois formes.
6. **R4** : K3 rapporté à b3.
7. **Toutes** : R1, R2, R3 et R4 ensemble, les règles du point 3 (K9 contigu dans le mode R1 pour C++ et D).
8. **Toutes, R1' au lieu de R1** (sensibilité).

Pour chaque calcul : scores, rangs espérés, rang plausible (90 %), étages indicatifs (règle v3 sans sa condition de
réplication), langages dont le rang change de plus de deux places par rapport à « Hôte ». Sorties :
`results/equal/analysis.json`, `results/report_equal.md`.

## 9. Publication

Le classement de tête du README ne change pas au point 3 : comme les tailles du point 2, les règles R1 à R5 entreront
dans la campagne finale qui réunira les points 2 à 4 (`docs/V4_SIZES.md`, 9). Elles s'y appliqueront quel que soit
l'effet mesuré ici : il est publié à côté du classement (README, ce document), règle par règle.

## 10. Ordre de travail

1. Ce plan, poussé.
2. Caractérisation de la machine 32, b3, sonde de K2.
3. Copies et constructions, sondes de mode, validation ; outils poussés avant la campagne.
4. Campagne.
5. Analyse, documents, journal.
