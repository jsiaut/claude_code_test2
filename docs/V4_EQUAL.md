# v4, point 3 : des conditions égales — plan et résultats (21 novembre 2026)

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
| Intrinsèques de la plateforme ou importées | C (`immintrin.h`), C++ (`immintrin.h` ou `std::experimental::simd`), Rust (`std::arch`), Nim (`importc` depuis `immintrin.h`), Ada (type vectoriel de GCC et builtins importés), Chapel (`extern proc` depuis `immintrin.h`), Go (`simd/archsimd`), FreePascal (assembleur en ligne AVX2, sa seule voie : `-Sv` n'a ni masque ni octets ; **non admis**, erratum 11.8 : la spécification interdit l'assembleur en ligne dans `tuned`) |
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
  langage, dont K2 à ses trois tailles du score et K3 `sw_padded` et `rmw_padded`), soit 655 processus par passe, et 198
  nouvelles cellules (D compris en R1') : 853 processus par passe (`tools/equal/campaign.py --dry`). Les binaires
  publiés de la campagne sont reconstruits sur la machine 32 depuis les sources suivies
  (`/dev/shm/msbuild/<langage>/pub`), comme les autres constructions.
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

## 11. Résultats (21 novembre, après la campagne)

*Tableaux complets (places, rangs espérés, scores au centre, rangs plausibles, étages, rapports de temps de chaque
règle) : `results/report_equal.md` ; toutes les sorties : `results/equal/analysis.json` (`analysis/equal_v4.py`). Les
calculs sont ceux de la section 8, sur les seules données de la machine 32 (5.1). Le contrôle de 11.6 est hors plan.*

### 11.1 Campagne

* Lancée le 21 novembre à 8 h 50, constructions prêtes ; passe 0 jusqu'à 10 h 39 (1 h 49, étalonnage compris),
  passe 1 jusqu'à 12 h 02 (1 h 23), passe 2 jusqu'à 13 h 28 (1 h 26), sans redémarrage.
* 2 559 processus : trois passes de 853, qui couvrent les mêmes cellules, sans doublon ; tous sur le même modèle de
  processeur (6/207/2). Aucun échec : sommes de contrôle justes, code de retour nul, aucun arrêt pour la mémoire ou la
  durée. Aucun processus au-delà de 5 % de vol de temps (4,0 % au plus), donc aucun refait.
* b3 à la fin de la campagne, machine au repos : 84,55 et 84,75 ms (`results/equal/k3_ref_end.txt`), contre 84,15 et
  84,85 au début ; b3 = 84,58 ms. Les décalages rapides sont les mêmes qu'au début (8, puis 36 à 48).
* K2 à 8 Mio (3.5, descriptif) : hors Lua (0,37 à 0,55 s, plus lent à toutes les tailles), 70 des 72 processus
  prennent 0,149 à 0,243 s ; deux sont plus lents, Java (0,34 s) et OCaml (0,51 s, dans la plage du régime lent de la
  machine 31). La sonde de 5.1 n'en avait trouvé aucun sur 60 processus du C : le régime lent existe aussi sur la
  machine 32, plus rare.

### 11.2 Classements

Places ; lignes dans l'ordre de « Toutes » (rang espéré entre parenthèses). « Publié » : le classement de tête du
README.

| Langage | Publié | Hôte | R1 | R1' | R2 | R3 | R4 | Toutes (rang espéré) | Toutes, R1' |
|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 (1,64) | 1 |
| C++ | 3 | 2 | 3 | 2 | 2 | 1 | 2 | 2 (2,86) | 2 |
| Odin | 2 | 4 | 4 | 4 | 5 | 5 | 4 | 3 (5,18) | 4 |
| Zig | 5 | 8 | 9 | 8 | 8 | 4 | 6 | 4 (5,39) | 3 |
| C3 | 4 | 3 | 2 | 3 | 3 | 3 | 3 | 5 (5,81) | 5 |
| Rust | 6 | 7 | 7 | 7 | 7 | 9 | 5 | 6 (6,48) | 7 |
| Nim | 7 | 5 | 5 | 5 | 4 | 6 | 8 | 7 (7,25) | 8 |
| Ada | 9 | 10 | 8 | 9 | 10 | 8 | 10 | 8 (7,26) | 6 |
| D | 8 | 6 | 6 | 6 | 6 | 7 | 9 | 9 (8,41) | 9 |
| Mojo | 14 | 12 | 12 | 12 | 12 | 11 | 13 | 10 (9,86) | 11 |
| Chapel | 10 | 9 | 10 | 10 | 9 | 10 | 7 | 11 (10,63) | 10 |
| Swift | 12 | 11 | 11 | 11 | 11 | 12 | 11 | 12 (10,65) | 12 |
| Fortran | 11 | 14 | 14 | 14 | 14 | 13 | 14 | 13 (12,07) | 13 |
| Julia | 13 | 13 | 13 | 13 | 13 | 14 | 12 | 14 (12,84) | 14 |
| C# | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 (14,05) | 15 |
| Java | 17 | 17 | 17 | 17 | 17 | 16 | 16 | 16 (16,79) | 16 |
| FreePascal | 16 | 16 | 16 | 16 | 16 | 18 | 17 | 17 (17,03) | 18 |
| Go | 18 | 18 | 18 | 18 | 18 | 17 | 18 | 18 (17,03) | 17 |
| Haskell | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 (18,79) | 19 |
| OCaml | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 (20,26) | 20 |
| BQN | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 (21,44) | 21 |
| JavaScript | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 22 (22,23) | 23 |
| PHP | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 23 (22,24) | 22 |
| Python | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 (24,13) | 24 |
| Lua | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 (24,68) | 25 |

Étages (paires ordonnées dans au moins 95 % des variantes), les mêmes dans les huit calculs : les 18 premiers |
Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua.

### 11.3 Réplication : machine 31 et machine 32

* Le calcul « Hôte » de la machine 32 et celui de la machine 31 (point 2 : même modèle de processeur, L3 effectif plus
  grand) ne diffèrent de plus de deux places pour aucun langage ; Odin (6e → 4e) et Chapel (11e → 9e) en gagnent deux.
* Par rapport au classement publié, Zig (5e → 8e) et Fortran (11e → 14e) reculent de trois places sur les deux hôtes ;
  Odin, Nim et D, qui bougeaient de trois ou quatre places sur la machine 31 (2e → 6e, 7e → 4e, 8e → 5e), en bougent
  deux sur la machine 32 (4e, 5e, 6e). L'effet de l'hôte du point 2 (`docs/V4_SIZES.md`, 10.5) se retrouve donc, dans
  le même sens, un peu plus faible.

### 11.4 Effet de chaque règle

Rapports de temps (moyennes géométriques des médianes de processus) de chaque nouvelle cellule à sa référence :
`results/report_equal.md`. Les rapports cités ici se retrouvent à chacune des trois passes. Les mécanismes des écarts
de temps ne sont pas examinés.

* **R1, vérifications actives (8 langages) : aucun langage ne bouge de plus de deux places.** Moyenne géométrique
  des 9 cellules naturelles, mode R1 / mode publié : C 1,00 (seules les rangées de taille connue de son K9 sont
  vérifiables, 5.2), D 1,05, Fortran 1,09, C++ 1,13 (K9 ×2,1 : sa grille imbriquée, 22 à 26 ms → 48 à 50), C3 1,21
  (K5 ×1,7), Zig 1,44 (K4 ×10 : 6 à 12 ms → 78 à 83), FreePascal 1,70 (K6 Q1 ×7,5, K9 ×3,4), Chapel 2,33 (K9 ×20 :
  15 à 19 ms → 323 à 332 ; K6 Q1 ×9,6, Q6 ×4,0, K5 ×2,3). Le code naturel ne compte guère que dans D1, la moitié du
  code par défaut, soit un huitième du score au centre, et il y est déjà loin de la frontière : le D1 de Chapel passe de
  0,150 à 0,065, ce qui lui retire un point de score. Le reste du mouvement vient de D3 : les latences de K8 naturel
  (p99,9 et maximum d'une itération, rapportés aux meilleurs des 25 langages) viennent des nouveaux processus, et
  leur maximum varie d'un processus à l'autre bien plus que les temps (C : 0,17 à 0,76 ms pour le binaire publié,
  0,19 à 5,2 ms en mode R1, pour un rapport des temps de 1,02). C++ perd ainsi 3,8 points de code par défaut par D3
  et 1,0 par D1 ; FreePascal en gagne 6,4 par D3 ; les meilleures latences, qui servent de référence, montent, et
  les langages hors de R1 gagnent 0,5 à 1,8 point par D3. Les échanges de places de R1 (C3 et C++, Zig et Ada) tiennent
  à ces latences (11.6).
* **R1', aucune vérification (9 langages) : aucun langage ne bouge de plus de deux places.** Mode R1' / mode publié :
  Ada 0,66 (K7 ×0,15 : 6,0 à 6,2 s → 0,7 à 1,3 ; K9 ×0,37 ; K6 Q1 ×0,50), Mojo 0,78 (K9 ×0,17, K6 Q1 ×0,33), Swift
  0,81 (K4 ×0,23 : 78 à 80 ms → 18), Odin 0,81 (K6 Q6 ×0,25), Go 0,87 (K6 Q6 ×0,43), OCaml 0,91 (K5 ×0,72), Nim
  0,93, Julia et D 0,99. Trois cellules sont plus lentes sans vérifications : K4 de Mojo (×1,50), K8 de Julia
  (×1,18), K9 d'Odin (×1,13). Ada gagne 2,9 points de code par défaut par D1 et en perd autant par D3 ; avec les
  latences de K8 des binaires publiés, il passe de la 10e à la 7e place (11.6).
* **R2, stencil contigu (13 langages) : aucun langage ne bouge de plus d'une place** (Nim et Odin échangent les 4e et
  5e). K9 contigu / imbriqué, mode publié : Swift 0,35, JavaScript 0,44, Nim 0,56, Rust 0,72, D 0,74, Mojo et OCaml
  0,77, Go 0,81 ; C++ 1,00 et Java 1,05 ; PHP 1,28, Lua 1,63, Python 1,83. Avec les vérifications de R1, la grille
  contiguë gagne davantage (C++ 0,77, D 0,63) ; sans vérifications, davantage pour Swift (0,22), Nim (0,51) et Mojo
  (0,59), moins pour Go (0,94) et D (0,82). Le code optimisé de K9 était déjà contigu : le plafond de K9 ne bouge que
  pour Nim, Java, JavaScript et Lua, où la variante naturelle est ou devient la meilleure à un fil (0,02 au plus).
* **R3, K4 `tuned` (23 langages admis ; 11.8) : Zig gagne quatre places (8e → 4e)**, seul déplacement de plus de deux
  places ; C++ passe 1er, Ada gagne deux places, Rust et FreePascal en perdent deux. Les formes `tuned` admises de 18
  langages prennent 0,58 à 1,30 ms (16 entre 0,58 et 0,79 ms ; Haskell 1,24, Fortran 1,30), à la bande passante en
  lecture d'un cœur ou près d'elle (borne
  physique de K4 sur cet hôte, 16 Mio lus à la bande passante mesurée à cette taille : 0,59 ms) ; celles d'OCaml, de
  JavaScript et de PHP 5,5 à 7,2 ms, de Python 68 ms, de Lua 212 ms. La cellule K4 du plafond monte surtout pour les
  langages dont la meilleure forme publiée était lente : C# 0,09 → 0,94, Go 0,10 → 0,89, Fortran 0,09 → 0,44, Mojo
  0,14 → 0,77, Zig 0,18 → 0,95 (6,5 → 0,61 ms), Ada 0,25 → 0,94, C++ 0,27 → 0,91. Elle baisse là où elle ne gagne
  rien, parce que la frontière passe de 1,17 ms (Chapel, forme publiée) à 0,58 ms (C3, `tuned`) : Chapel 1,00 → 0,95,
  Swift 0,76 → 0,73, BQN (sans variante `tuned`, 5.2) 0,29 → 0,14, FreePascal (forme `tuned` non admise, 11.8)
  0,07 → 0,03.
* **R4, K3 rapporté à b3 (25 langages) : Nim (5e → 8e) et D (6e → 9e) reculent de trois places** ; Rust (7e → 5e),
  Zig (8e → 6e) et Chapel (9e → 7e) en gagnent deux. Les boucles de K3 (meilleur de `sw_padded` et `rmw_padded`) se
  répartissent presque comme au point 2 (FreePascal, du côté rapide sur la machine 31, est ici entre les deux) : D,
  C3 et Nim du côté rapide (16,7 à 19,5 ms), C++, Mojo, Ada et FreePascal entre les deux (25 à 48 ms), C, Fortran,
  Zig, Chapel, Rust, Odin, Swift, Java, C# et Julia du côté lent (86 à 92 ms), autour de b3 (84,6 ms). Rapportées à
  b3, elles valent toutes 0,92 à 1, au lieu de 0,18 à 1 rapportées à la frontière (D) : K3 ne sépare plus ces
  langages, mais garde l'écart avec ceux qui ne peuvent pas écrire sans `lock` (Go 0,34, OCaml 0,25, Haskell 0,23,
  JavaScript 0,16) et avec les interprétés (0,03 au plus). La cellule K3 de C passe de 0,19 à 0,96, son plafond de
  61,7 à 75,6.

### 11.5 Toutes les règles ensemble

* **« Toutes » (R1, R2, R3, R4 : les règles du point 3) : Zig (8e → 4e) et D (6e → 9e) bougent de plus de deux
  places.** Odin passe 3e ; C3 (3e → 5e), Nim (5e → 7e) et Chapel (9e → 11e) reculent de deux places, Ada
  (10e → 8e) et Mojo (12e → 10e) en gagnent deux. Les scores montent (C : 70,6 → 76,2), par le plafond (C : 61,7 →
  78,0), surtout par R4 et R3.
* **« Toutes, R1' » : Zig (8e → 3e), Ada (10e → 6e), Nim (5e → 8e) et D (6e → 9e).**
* Les étages ne changent pas (11.2).
* Par rapport au classement publié, dont le K3 vient surtout de Cascade Lake, où l'effet de placement n'existe pas
  (`docs/V4_SIZES.md`, 10.5), « Toutes » ne déplace de plus de deux places que Mojo (14e → 10e) ; « Hôte » en déplace
  deux (Zig et Fortran, 11.3).

### 11.6 Contrôle hors plan : latences de K8

Écrit après la première exécution de l'analyse, pour mesurer ce que D3 fait aux déplacements (11.4). Les calculs R1,
R1', « Toutes » et « Toutes, R1' » sont refaits avec les latences de K8 des binaires publiés : les temps des nouvelles
cellules sont substitués, pas les latences (`analysis/equal_v4_lat.py`, `results/equal/lat_check.txt`).

| Calcul | Plus de deux places contre « Hôte », plan | Contrôle |
|---|---|---|
| R1 | aucun | aucun (Ada et Chapel échangent les 9e et 10e places) |
| R1' | aucun | Ada 10e → 7e |
| Toutes | Zig 8e → 4e, D 6e → 9e | Zig 8e → 3e, Ada 10e → 7e, Nim 5e → 8e, D 6e → 9e, Chapel 9e → 12e |
| Toutes, R1' | Zig 8e → 3e, Ada 10e → 6e, Nim 5e → 8e, D 6e → 9e | Zig 8e → 3e, Ada 10e → 6e, D 6e → 9e |

Ne dépendent pas des latences de K8 : la montée de Zig (quatre ou cinq places) et le recul de D (trois places) dans
les deux calculs combinés, la montée d'Ada dans « Toutes, R1' » (quatre places). Sont au seuil, à deux ou trois places
selon les latences : les reculs de Nim et de Chapel et la montée d'Ada dans « Toutes », le recul de Nim dans
« Toutes, R1' ».

### 11.7 Ce que cela change

* Le classement de tête du README ne change pas (section 9). R1 à R5 s'appliqueront dans la campagne finale de la v4,
  qui réunira les points 2 à 4.
* Les règles qui touchent au plafond (R3, R4) déplacent le plus ; celles qui touchent au code naturel (R1, R2) peu,
  parce que le code naturel ne pèse qu'un huitième du score au centre et qu'il est déjà loin de la frontière, même
  quand une vérification multiplie un temps par 10 ou 20.
* Un constat sera examiné avant la campagne finale, comme ceux du point 2 (`docs/V4_SIZES.md`, 10.6) : la part D3 du
  code par défaut dépend des maxima de latence de quelques processus de K8, qui varient d'un processus à l'autre bien
  plus que les temps ; ici, elle déplace des langages autant que les vérifications elles-mêmes.

### 11.8 Erratum (21 novembre, après la publication de cette section, en préparant le point 4)

* **Faute.** Le K4 `tuned` de FreePascal (`bench/fpc_eq`, `K4TunedAsm`) est écrit en assembleur en ligne. La
  spécification l'interdit dans `tuned` (`docs/SPEC.md`, 0 : « Interdits : FFI vers du code C/C++/asm écrit à côté,
  assembleur en ligne et bibliothèques tierces »), le texte de R3 ne l'admet pas (« types vectoriels du langage ou
  intrinsèques de sa chaîne standard », 3.3) et les autres variantes optimisées de FreePascal s'en passent
  (`docs/FPC.md`). Le tableau de 3.3 l'admettait à tort, et la cellule (0,61 ms) était comptée dans R3, « Toutes » et
  « Toutes, R1' ».
* **Correction.** La cellule est écartée des calculs (`analysis/equal_v4.py`, `NOT_ADMITTED`) : FreePascal garde le
  meilleur de ses deux formes publiées de K4 (18 ms). Les sorties sont régénérées (`results/equal/analysis.json`,
  `results/report_equal.md`, `results/equal/lat_check.txt`) et les sections 11.2 et 11.4 corrigées.
* **Effet.** FreePascal passe de la 16e à la 18e place avec R3 et « Toutes, R1' », à la 17e avec « Toutes » ; Java et
  Go gagnent une place (Java 16e dans R3 et les deux calculs combinés, Go 17e dans R3 et « Toutes, R1' »). Les
  déplacements de plus de deux places et le contrôle hors plan (11.6) ne changent pas ; dans les quatorze premiers,
  aucune place ne change, et les rangs espérés de 0,04 au plus (Julia dans « Toutes »). Les calculs sans R3 sont
  identiques.
* **Pour la campagne finale.** FreePascal recevra un K4 `tuned` sans assembleur, dans le catalogue du point 4.

### 11.9 Erratum : la base n'est pas le code du classement publié (21 novembre, en préparant le point 4)

* La campagne a mesuré, comme celle du point 2, les sources de `bench/<langage>`, auxquelles manquent pour 20 langages
  les corrections que le classement publié applique (copies `_fix`, harnais commun de K9 des copies `_k9h`, `bqn_rq`) :
  la liste et les ordres de grandeur sont dans `docs/V4_SIZES.md`, 10.7. Les copies `bench/<langage>_eq` en partent
  aussi.
* **Ce qui tient** : les comparaisons entre calculs (« Hôte » contre R1, R1', R2, R3, R4 et « Toutes », 11.4 à 11.6)
  portent sur le même code des deux côtés ; elles décrivent l'effet des règles sur le code non corrigé.
* **Ce qui ne tient pas** : les comparaisons au classement publié. En 11.3, « Zig et Fortran reculent de trois places
  par rapport au classement publié » mêle les corrections absentes (harnais de K9 pour Zig, K4 de Fortran) ; en 11.5,
  la phrase sur l'écart de « Toutes » au classement publié aussi. La place du premier étage dans « Hôte » est faussée
  dans le même sens : C, Chapel, Ada et Swift, dont le K9 était déjà au harnais commun, y sont avantagés.
* **Suite** : comme pour le point 2 (`docs/V4_SIZES.md`, 10.7) ; la campagne du point 4 mesure les cellules touchées
  avec les deux sources, et l'effet de l'erratum sur les calculs de ce point sera publié ici.

