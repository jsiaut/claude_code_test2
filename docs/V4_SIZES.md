# v4, point 2 : trois tailles par noyau — plan (19 novembre 2026) et résultats (20 novembre)

*Plan d'ensemble : `docs/V4_PLAN.md` (point 2). Ce plan est poussé avant tout changement de code et toute mesure ; les
écarts éventuels seront datés et justifiés dans `docs/METHODOLOGY.md`.*

## 1. Question

Chaque noyau est mesuré à une seule taille, sauf K2 (dix tailles), où le rapport de Python au C passe de 30 à 1,2 selon
que les données tiennent dans le L1 ou vont en mémoire. Le classement publié dépend-il de la taille choisie pour les
autres noyaux ? Le point 2 mesure les sept noyaux dont le travail dépend d'une taille de données à trois tailles, sur un
même hôte, pour les 25 langages, et fixe d'avance la façon dont les tailles entreront dans le classement.

## 2. Faits établis avant le plan

* **Les tailles sont figées dans le code.** Les 25 implémentations déclarent leurs tailles en constantes (C :
  `enum { N1 = 1 << 22 }`, Python : `N1 = 1 << 22`, de même ailleurs), comme le générateur de données
  `tools/gendata.c`. Contrairement à ce que supposait la remarque (« aucun code nouveau »), changer de taille demande de
  modifier chaque implémentation pour qu'elle lise ses tailles à l'exécution.
* **L'hôte** (machine 30, depuis le 19 novembre à 7 h 27) : Xeon Granite Rapids, modèle 173, 4 vCPU, 15 Gio de mémoire ;
  L1d de 48 Kio et L2 de 2 Mio par cœur, L3 annoncé de 504 Mio, partagé avec les autres machines virtuelles de l'hôte
  (la part effective est inconnue). Les tailles publiées de K1 (256 Mio), K6 (208 Mio) et K7 (128 Mio) tiennent dans ce
  L3 annoncé ; elles dépassaient le L3 des hôtes Cascade Lake de la campagne de référence.
* **Le disque** n'a plus que 630 Mo libres : les données des nouvelles tailles iront dans `/dev/shm` (16 Gio, en
  mémoire), générées et effacées noyau par noyau.

## 3. Noyaux et tailles

K2 (déjà dix tailles), K3 et K10 (synchronisation : un nombre fixe d'opérations, sans données) gardent leur taille ;
ils sont remesurés à cette taille pour que le classement puisse être calculé sur ce seul hôte. Les sept autres sont
mesurés à la taille publiée et à deux autres : une qui tient dans le L2 d'un cœur (au plus 2 Mio de données), une qui
dépasse le L3 annoncé (au moins 1 Gio), sauf K4, borné par la prédiction de branchement et non par la mémoire, et K5,
dont la taille publiée tient déjà dans le L1.

| Noyau | Paramètre | Petite | Publiée | Grande |
|---|---|---|---|---|
| K1 | particules (64 o) | 2^14 (1 Mio) | 2^22 (256 Mio) | 2^24 (1 Gio) |
| K4 | octets | 2^20 (1 Mio) | 2^24 (16 Mio) | 2^28 (256 Mio) |
| K5 | n × INNER (travail constant, 2^27 produits) | 2^11 × 2^16 (16 Kio, L1 ; publiée) | 2^15 × 2^12 (256 Kio, L2) | 2^21 × 2^6 (16 Mio, L3) |
| K6 | lignes (13 o) | 2^16 (832 Kio) | 2^24 (208 Mio) | 2^26 (832 Mio) |
| K7 | lignes / clés distinctes | 2^16 / 2^12 | 2^24 / 2^20 | 2^27 / 2^23 |
| K8 | profondeur de l'arbre long / d'une requête (Q = 16 384) | 16 / 8 | 20 / 10 | 23 / 12 |
| K9 | M (deux grilles M × M de f64) | 2^8 (1 Mio) | 2^11 (64 Mio) | 2^13 (1 Gio) |

Pour K5, les trois colonnes ne suivent pas l'ordre « petite, publiée, grande » : la publiée est la plus petite. Les
données, la valeur des clés et leur répartition gardent la même loi à chaque taille (K7 : 16 lignes par clé).

## 4. Code

* Chaque implémentation lit ses tailles dans des variables d'environnement (`MS_N1`, `MS_N4`, `MS_N5`, `MS_INNER5`,
  `MS_N6`, `MS_N7`, `MS_K8_LONG`, `MS_K8_REQ`, `MS_M9`), aux valeurs publiées par défaut : sans elles, le programme fait
  le calcul publié. Seule la taille change ; le code des variantes reste celui de la publication. Une structure
  dimensionnée à la compilation (tableau de Fortran ou d'Ada, domaine de Chapel, constante d'un type) devient
  dimensionnée à l'exécution ; chaque cas est noté par langage.
* Contrôle du changement de code : à la taille publiée, les anciens binaires sont mesurés avec les nouveaux pendant la
  campagne (section 7). Un écart de plus de 5 % sur une cellule est publié, et le calcul de la section 8 est refait avec
  les anciens binaires à la taille publiée.
* `tools/gendata.c` prend les tailles en arguments, avec le même générateur pseudo-aléatoire et les mêmes graines : les
  fichiers de la taille publiée doivent être identiques au bit près à ceux de `/opt/msdata` (empreintes SHA-256).
* Validation : les sommes de contrôle de chaque taille sont calculées par l'implémentation C ; chaque implémentation
  doit les reproduire (tolérances de la spécification) à chaque taille, un processus par cellule, avant la campagne.

### 4.1 Écart au plan (19 novembre, 11 h 15, avant toute mesure)

Lire les tailles dans l'environnement, comme prévu ci-dessus, change le code mesuré, même à la taille publiée : une
borne de boucle, une taille de tableau ou de pile connue à la compilation devient une valeur lue à l'exécution, que le
compilateur ne replie plus (en PHP, une constante `define()` n'est plus substituée par OPcache). Le contrôle par les
anciens binaires aurait mesuré cet effet sans l'éviter. Le code a donc été changé autrement :

* **Langages compilés (19)** : les tailles restent des constantes de compilation, redéfinissables à la construction et
  aux valeurs publiées par défaut ; une construction par jeu de tailles (petit, grand : `tools/sizes/sizes.py`), dans
  `/dev/shm/msbuild`. Mécanisme par langage : macros (`-D`) en C et C++ ; `option_env!` lu par une fonction constante
  en Rust ; fichier de constantes écrit par `build.sh` en Zig, C3, Swift, Go, C#, Java et Fortran (module) ; import de
  chaîne (`-J`) en D ; `#config` en Odin ; `intdefine` en Nim ; préprocesseur intégré de GNAT (`-gnateD`) en Ada ;
  `config param` (`-s`) en Chapel ; `get_defined_int` (`-D`) en Mojo ; macros d'un fichier inclus en FreePascal ;
  préprocesseur C de GHC en Haskell ; préprocesseur `-pp` en OCaml. Les ajouts sont placés de façon à ne décaler
  aucune ligne (les numéros de ligne entrent dans plusieurs binaires).
* **Langages interprétés ou à JIT sans construction (6)** : Python, Lua, PHP, BQN, JavaScript et Julia gardent leur
  source publié intact ; la copie d'un jeu de tailles remplace les seules constantes de taille par celles du jeu
  (`tools/sizes/patches.py`, chaque motif vérifié par son nombre d'occurrences).
* **Contrôle, fait avant les mesures** : chaque binaire publié reconstruit sur la machine 30 à partir du nouveau
  source est comparé à celui que donne le source d'origine. Identiques octet pour octet : C, C++, Rust, D, Fortran,
  Mojo, FreePascal, OCaml. Segments chargés identiques, seules diffèrent les tables de symboles, l'identifiant de
  construction ou une somme de contrôle du source : Zig, Nim, Haskell, Ada, Swift (dont l'empreinte de module change à
  chaque construction), C3 (code et données identiques, ordre des symboles dynamiques changé). Code intermédiaire
  identique une fois les références résolues : C# (IL des 77 méthodes) et Java (bytecode ; le pool de constantes
  gagne deux entrées). Instructions identiques mais disposées autrement : Odin (une fonction de K10 placée ailleurs),
  Chapel (deux entrées de tables de méthodes virtuelles échangées), Go (descripteurs de types décalés de 16 octets).
  Le contrôle de la section 4 (anciens binaires mesurés à la taille publiée, au plus 5 % d'écart par cellule) est
  gardé pour ces trois langages, sur les dix noyaux ; ailleurs, le code mesuré à la taille publiée est le code
  publié, et le contrôle n'aurait rien à mesurer.
* **Paramètres** : `MS_K7_LOG2` (logarithme du nombre de clés, d'où la taille de la table de la variante tuned) et
  `MS_K7_NB` (plus grand nombre premier inférieur au nombre de clés, seaux de la table du naturel en C) remplacent
  `MS_K7_KEYS` ; `MS_N5` n'est employé que là où le code fixe n = 2048 (C, C++, Haskell), ailleurs n suit le fichier
  de données. Les étiquettes de taille imprimées (« 16M », « 2048x65536 ») font partie du binaire publié et ne changent
  pas ; le pilote enregistre la taille.
* **Sommes de contrôle au-delà de 2^53** : à la grande taille, celle de Q1 (K6) vaut 1,6·10^16. BQN et JavaScript,
  dont les nombres sont des doubles, la rendent à l'arrondi près (…010, …012, …016 au lieu de …014), alors que chaque
  agrégat, sous 2^53, est exact. Règle, pour tous les langages : une somme de contrôle entière supérieure à 2^53 se
  compare à 10^-15 près en valeur relative (quelques unités du dernier rang d'un double) ; en dessous, l'égalité reste
  exacte. Les tolérances de la spécification (K1, K5, K9) ne changent pas.
* **Mémoire** : la limite du groupe de processus de la machine (13,35 Gio, page cache et `/dev/shm` compris) est
  atteinte avant le plafond de 13 Gio de la section 6 ; le processus mesuré est désigné premier tué, et la cellule
  devient « hors mémoire » (« que le noyau tue »). La validation en trouve à la grande taille : Python (K1 naturel et
  naturel mélangé), BQN (K1, toutes variantes), PHP (K1 `natural_arr` et `natural_arr_shuffled`, K4 `natural_sorted`).
* **Mojo** fixe le répertoire des données à la compilation (`/opt/msdata/`) : ses constructions de taille reçoivent un
  répertoire de liens propre au jeu (`/dev/shm/ms_view_<jeu>`), le binaire publié restant identique.
* **Campagne (section 7)** : pour que les données d'une seule taille d'un seul noyau occupent `/dev/shm` à la fois
  (jusqu'à 1 Gio), l'ordre aléatoire porte sur les groupes (noyau, taille), puis sur les langages dans chaque groupe,
  avec une graine fixée et différente à chaque passe. Les comparaisons du calcul 2 de la section 8 se font entre
  langages à une même taille d'un même noyau, donc à l'intérieur d'un groupe. Les blocs de contrôle d'Odin, de Chapel et
  de Go sont dans les groupes de la taille publiée, à côté des nouveaux binaires.

## 5. Hôte

Caractérisation de la machine 30 avant la campagne (`tools/hwprobe.c`, `results/hw/machine30`) : latences, bandes
passantes par niveau, pic de calcul, et une chaîne de pointeurs de K2 jusqu'à 2 Gio, qui situe le L3 effectif. Si la
machine virtuelle change de modèle d'hôte pendant la campagne, les passes touchées sont refaites sur un hôte du même
modèle ; si c'est impossible, toute la campagne est refaite sur le nouveau modèle, caractérisé de même.

## 6. Cellules

Toutes les variantes publiées des sept noyaux, aux trois tailles, et K2, K3, K10 à leur taille, pour les 25 langages
classés (le C est le témoin de l'hôte) ; les implémentations en annexe (C par GCC, flang, LuaJIT, Bun, CPython sans GIL)
ne sont pas mesurées. Limites :
* mémoire : un processus qui dépasse 13 Gio ou que le noyau du système tue rend la cellule « hors mémoire » ;
* durée : une répétition de plus de 300 s ramène la cellule à une seule répétition mesurée par processus ;
* une cellule manquante prend le temps admissible le plus lent des autres langages à cette taille, la règle qu'ont déjà
  les langages sans threads en K3 ; chaque cas est publié.

## 7. Campagne

Comme la campagne de référence (`tools/campaign.py`) : trois passes, chaque bloc (langage, noyau, taille) exécute un
processus par variante, ordre des blocs tiré au hasard avec une graine fixée et différente à chaque passe ; répétitions
fixées par la première passe, comme dans `tools/driver.py` (environ 3 s par processus, au moins trois répétitions), mais
sans le plafond de dix répétitions à la petite taille, où une répétition peut ne durer que quelques microsecondes
(jusqu'à 10 000) ; échauffement d'au moins une seconde pour les langages à JIT (au moins trois répétitions), pour que
la compilation à la volée soit faite avant les répétitions mesurées. La statistique d'une cellule reste la médiane
par processus, puis la combinaison des processus de la méthode v3. Les anciens binaires à la taille publiée
(section 4) sont des blocs de plus, mélangés aux autres. Le vol de temps de la machine virtuelle est noté pour chaque
processus ; un processus qui en a plus de 5 % est refait une fois.

### 7.1 Constats de la passe 0 (19 novembre, 20 h 45, pendant la passe 1, avant toute analyse)

* **Sentinelle de mémoire.** La première version de la sentinelle du pilote (`tools/sizes/campaign.py`) comparait à
  13 Gio la somme des VmRSS du groupe de processus mesuré. Cette somme compte autant de fois qu'il y a de processus
  les pages partagées en copie sur écriture : les variantes `mt` de PHP créent quatre processus par `pcntl_fork`, qui
  partagent les colonnes de K6. À la grande taille, K6 `mt` de PHP (Q1 et Q6), passé à la validation (sans sentinelle,
  sous la limite du groupe), a ainsi été arrêté dès l'étalonnage de la passe 0. La règle de la section 6 porte sur un
  processus : la sentinelle compare désormais le plus grand VmRSS du groupe (la somme reste enregistrée). Le pilote en
  cours garde l'ancienne sentinelle ; ces deux cellules seront remesurées après la passe 2, aux trois passes, avec la
  nouvelle (`tools/sizes/requeue.py`, puis `campaign.py --langs php --groups k6:large`), donc hors de l'ordre
  aléatoire ; les enregistrements écartés sont gardés (`results/sizes/discarded`). Aucune autre cellule n'a été arrêtée
  par la sentinelle : les autres cellules « hors mémoire » de la passe 0 (Python, BQN et PHP, K1 et K4 à la grande
  taille, les mêmes que la validation) sont des processus tués par le noyau à la limite du groupe (code -9).
* **K10 de BQN** : absent par conception (ni threads ni coroutines, `docs/BQN.md`), il apparaît comme un échec
  d'étalonnage (code 1). K10 étant hors score depuis la v2, l'analyse ne le remplit pas et le classe à part
  (`analysis/sizes_v4.py`) ; seules les cellules du score reçoivent le temps le plus lent des autres langages.
* **Incident** : à 18 h 34, une exécution à blanc du pilote (`--dry`, pour compter les blocs restants) a écrit une
  ligne d'en-tête « passe 0 » dans le journal de campagne ; elle n'a lancé aucune mesure et a duré moins d'une seconde,
  pendant un processus de PHP (K7 naturel, grande taille, passe 0). La ligne a été retirée du journal ; le mode à blanc
  n'écrit plus dans le journal.

### 7.2 Changement d'hôte (20 novembre, 1 h 25, avant toute mesure sur le nouvel hôte et toute analyse)

* **Faits.** Le conteneur a redémarré le 20 novembre vers 1 h 19, pendant le dernier groupe de la passe 1 (K7, grande
  taille), sur une autre machine (machine 31) d'un autre modèle : Xeon Emerald Rapids (famille 6, modèle 207,
  stepping 2, « @ 2.10GHz »), 4 vCPU, 15 Gio, L1d de 48 Kio et L2 de 2 Mio par cœur, L3 annoncé de 260 Mio, même
  limite de mémoire du groupe (13,35 Gio). La machine 30 était un Granite Rapids (6/173/1, « @ 2.30GHz », L3 annoncé
  de 504 Mio). La passe 0 était complète, la passe 1 à 23 groupes sur 24 : 4 382 processus enregistrés, tous lisibles ;
  le processus en cours est perdu. Le redémarrage a vidé `/dev/shm` (constructions des tailles, données) ; le disque
  est conservé.
* **Règle appliquée (section 5).** Les passes touchées devraient être refaites sur un hôte du même modèle ; le modèle de
  l'hôte ne se choisit pas depuis la session : toute la campagne est donc refaite sur la machine 31, caractérisée de
  même (`tools/sizes/hwchar.sh`, `results/hw/machine31`). Dans les sections 6 à 8, « machine 30 » se lit
  « machine 31 » : l'analyse porte sur les seules données de la machine 31, avec ses bornes physiques. Les tailles de
  la section 3 gardent leur rôle : la petite tient dans le L2 d'un cœur (2 Mio), la grande dépasse le L3 annoncé.
  Si l'hôte change encore de modèle, la même règle s'applique ; après un redémarrage sur le même modèle, la campagne
  reprend où elle s'est arrêtée (un processus enregistré n'est pas refait).
* **Données de la machine 30** : gardées telles quelles dans `results/sizes/machine30/` (mesures brutes, étalonnage,
  journaux) ; elles n'entrent dans aucun calcul du point 2.
* **Constructions.** Les binaires publiés (`bench/<langage>`) avaient été construits sur la machine 30 avec des options
  qui visent le processeur hôte (`-march=native` et équivalents). Ils sont reconstruits sur la machine 31 à partir de
  sources propres (caches et objets de construction effacés), et le contrôle de la section 4 est refait : binaire du
  nouveau source contre binaire du source d'origine, construits sur la machine 31. Le pilote refait, avant la première
  mesure, les constructions des tailles et les anciens binaires d'Odin, de Chapel et de Go. La validation (4.1,
  `results/sizes/validation.md`, machine 30) n'est pas refaite : le code n'a pas changé, la limite de mémoire est la
  même, et chaque processus de la campagne vérifie ses sommes de contrôle.
  Fait à 1 h 35, avant toute mesure : les 19 langages compilés reconstruits sans erreur. Par rapport aux binaires de
  la machine 30, le code change pour les trois langages compilés par GCC 16 (C++, Ada, Fortran : `-march=native` y vaut
  `sapphirerapids`) ; il est identique pour les autres (mêmes fichiers, ou mêmes sections de code et de données pour
  Zig et Swift ; clang 23 vise ici `emeraldrapids`). Contrôle
  refait, binaire du nouveau source contre binaire du source d'origine (`f0168b7`), tous deux construits sur la
  machine 31 : identiques octet pour octet pour C, C++, Rust, D, Fortran, FreePascal et OCaml ; sections de code
  (`.text`) et de données (`.data`, et `.rodata` sauf exceptions) identiques pour Zig, Haskell, Swift et C3 ; Mojo ne
  diffère que par le chemin du source inscrit dans le binaire (construits à des chemins de même longueur : code
  identique, un octet du chemin et l'identifiant de construction diffèrent) ; Nim, 3 octets de `.rodata` qui changent
  avec l'emplacement de la construction (le même source construit à deux endroits diffère de même) ; Ada, 4 octets de
  `.rodata` qui suivent le texte du source (somme de contrôle de l'unité). L'IL de C# et le bytecode de Java ne
  dépendent pas de la machine : le contrôle de la machine 30 vaut tel quel. Odin, Chapel et Go gardent le contrôle par
  la mesure des anciens binaires.
* **Sentinelle** : la nouvelle campagne a dès le départ la sentinelle corrigée (7.1) ; K6 `mt` de PHP à la grande
  taille est mesuré dans l'ordre aléatoire, comme les autres cellules, et la remise en file prévue en 7.1 n'a plus
  d'objet.
* **Ordre et durée** : mêmes graines, donc même ordre des groupes et des blocs que sur la machine 30 ; environ
  20 heures (sur la machine 30 : 8 h pour la passe 0, étalonnage compris, environ 5 h 40 pour chacune des autres).

## 8. Analyse, fixée avant les mesures

La méthode v3 (même graine, 20 000 variantes, mêmes poids, grille v2 corrigée par le point 1), appliquée aux seules
données de la machine 30 :
1. **Hôte** : la taille publiée seule. Comparé au classement publié, il donne l'effet de l'hôte et du nouveau code.
2. **Trois tailles** (résultat central du point 2) : pour chacun des sept noyaux, chaque cellule du plafond et du code
   par défaut est calculée à chaque taille, avec ses propres références (frontière des langages à cette taille ; bornes
   physiques du niveau de mémoire où tiennent les données, mesurées sur l'hôte), puis moyennée sur les trois tailles à
   poids égaux. Dans les variantes, les poids des tailles sont tirés comme les autres poids (loi de Dirichlet autour de
   l'égalité, concentration 20, dans la moitié des variantes ; uniforme dans l'autre). Comparé à « Hôte », il donne
   l'effet des tailles.
3. **Une taille à la fois** (petite, publiée, grande), en sensibilité.

Pour chaque calcul : scores, rangs espérés, rang plausible, étages indicatifs (règle v3 sans sa condition de
réplication, comme `analysis/audit3.py`), et les langages dont le rang change de plus de deux places entre « Hôte » et
« Trois tailles ». Sorties : `results/sizes/`, `results/report_sizes.md`.

### 8.1 Mise en œuvre (19 novembre, avant les mesures)

`analysis/sizes_v4.py`, poussé avant la campagne et éprouvé sur des données synthétiques seulement. Choix de mise en
œuvre de la section 8 :
* une seule campagne : aucun langage n'y est relié par un pont, tous ont les mêmes réservoirs de résidus et le même
  générateur (l'ajout de Swift, FreePascal, BQN et PHP par un pont du C ne s'applique pas) ;
* bornes physiques de la machine 30 dans les quatre calculs (Hôte compris), mêmes volumes que celles du classement
  publié : bande passante sur 1 thread du plus petit volume mesuré qui contient les données (`hwprobe bw`) ; sur
  4 threads, 4 fois celle d'un quart du volume tant qu'il tient dans le L2 d'un cœur, STREAM sur 4 threads au-delà ;
  pic FMA mesuré pour K5 (calcul seul dans le L1, comme le classement publié ; au-delà, la plus grande des bornes de
  calcul et de bande passante) ; fréquence mesurée pour K3 ; STREAM : la triad (sa figure de mérite ; la copie sur
  4 threads donne 466 Go/s, valeur aberrante) ; `tools/hwprobe.c` compilé en `-O3` (en `-O2`, GCC 13.3 garde les
  accumulateurs du test de pic en mémoire : 53 Gflop/s au lieu de 224) ;
* calcul 2 : moyenne en logarithme sur les tailles de chaque cellule de E et de D1, de la part de K1 dans D2 et de D3
  (latences de K8) ; K3 et D4 (une seule taille) pris à la taille publiée ; les tirages des variantes sont ceux de
  « Hôte », les poids des tailles viennent d'un générateur à part ;
* calcul 3 : colonnes du tableau de la section 3 (pour K5 : 2^11, 2^15, 2^21) ; « Hôte » prend K5 à sa taille
  publiée (2^11) ;
* cellule manquante (section 6) : seulement pour les variantes communes à tous les langages ; une variante propre à
  un langage (`extra_variants`) n'est pas donnée aux autres.

## 9. Publication

Le classement de tête du README ne change pas au point 2 : les points 3 (conditions égales) et 4 (code optimisé
convergent) modifient aussi les implémentations et demanderont une campagne. Le classement final de la v4 viendra
d'une seule campagne qui réunira les points 2 à 4, sur un même hôte, avec les tailles comptées comme au calcul 2 de la
section 8 (moyenne des trois tailles à poids égaux) : cette règle est fixée ici. D'ici là, les résultats du point 2
sont publiés à côté du classement (README, `docs/V4_SIZES.md`), avec les deux effets séparés.

## 10. Résultats (20 novembre, après la campagne)

*Tableaux complets (rangs espérés, scores au centre, étages, contrôle) : `results/report_sizes.md` ; toutes les sorties :
`results/sizes/analysis.json` (`analysis/sizes_v4.py`). Les calculs sont ceux de la section 8, sur les seules données
de la machine 31 (7.2).*

### 10.1 Campagne

* Lancée le 20 novembre à 1 h 38 ; constructions des tailles et anciens binaires prêts à 1 h 44 ; passe 0 jusqu'à
  10 h 23 (8 h 39, étalonnage compris), passe 1 jusqu'à 16 h 53 (6 h 31), passe 2 jusqu'à 23 h 06 (6 h 13), sans
  redémarrage.
* 6 594 processus : trois passes de 2 198, qui couvrent les mêmes cellules, sans doublon ; tous sur le même modèle de
  processeur (6/207/2) ; aucun au-delà de 5 % de vol de temps, donc aucun refait.
* Échecs : à chaque passe, les 13 cellules attendues et elles seules. Onze sont « hors mémoire » à la grande taille,
  tuées par le noyau à la limite du groupe, les mêmes qu'à la validation : Python (K1 naturel et naturel mélangé), BQN
  (K1, six variantes), PHP (K1 `natural_arr` et `natural_arr_shuffled`, K4 `natural_sorted`). Les deux autres sont K10
  de BQN, absent par conception. Les deux cellules de PHP arrêtées à tort sur la machine 30 (K6 `mt`, Q1 et Q6, grande
  taille) passent avec la sentinelle corrigée.
* Cellules manquantes remplies (section 6), à la grande taille seulement : K1 de BQN (`aos`, `natural`,
  `natural_shuffled`, `soa`) et de Python (`natural`, `natural_shuffled`), au temps de Go, le plus lent des autres
  langages, sauf `soa` de BQN, au temps de Python. Les autres cellules hors mémoire sont des variantes propres à un
  langage, ou n'entrent pas dans le score.

### 10.2 Contrôle des anciens binaires (Odin, Chapel, Go)

* 115 cellules ; 41 s'écartent de plus de 5 % (rapports de 0,29 à 1,55). Presque toujours, un processus sur les trois
  d'une construction s'écarte des deux autres, dans un sens ou dans l'autre. Seules 3 cellules ont tous les processus
  d'une construction plus lents que tous ceux de l'autre, alors que le hasard seul en donnerait environ une sur dix
  (11 sur 115) avec trois processus de chaque côté : rien n'indique un effet du code (descriptif, hors plan).
* L'écart le plus grand, K2 de Go à 8 Mio (0,29), vient de l'hôte. Sur la machine 31, K2 à 8 Mio a deux régimes d'un
  processus à l'autre, pour tous les langages : 0,15 à 0,28 s, ou 0,44 à 0,81 s. 15 constructions sur 28 ont au moins
  un processus lent, et les trois processus de l'ancien binaire de Go sont tombés dans le régime lent. La remarque
  sur C++ avait déjà trouvé K2 à 8 Mio bimodal sur un autre Emerald Rapids (`docs/CPP.md`) ; sur la machine 30, à
  cette taille, aucune construction ne variait de plus d'un facteur 1,75.
* Règle de la section 4 : les calculs de la section 8 sont refaits avec les anciens binaires à la taille publiée.
  « Hôte » : Odin passe de la 6e à la 4e place (rang espéré 6,83 → 5,69), Chapel de la 11e à la 10e ; Nim, D et Swift
  reculent d'une place. « Trois tailles » : aucune place ne change (Odin 5,69 → 5,21). Aucun rang ne bouge de plus de
  deux places entre « Hôte » et « Trois tailles », avec les anciens binaires comme avec les nouveaux. Le bruit de
  processus de cet hôte déplace donc à lui seul un langage de deux places : c'est l'ordre de grandeur de l'effet des
  tailles (10.4).
* Correction, après le premier calcul et avant toute rédaction : le calcul refait avec les anciens binaires ne leur
  donnait K2, K3 et K10 qu'à la position publiée. Or ces noyaux n'ont que leur taille publiée, qui entre dans les trois
  positions. Après correction (`b0df134`), seuls « Taille petite » et « Taille grande » avec les anciens binaires
  changent. Les calculs avec les nouveaux binaires sont identiques d'une exécution à l'autre (graines fixes).

### 10.3 Classements

Places (rang espéré de « Trois tailles » entre parenthèses) ; lignes dans l'ordre de « Trois tailles ».

| Langage | Publié | Hôte | Trois tailles (rang espéré) | Petite | Publiée | Grande |
|---|---|---|---|---|---|---|
| C++ | 3 | 2 | 1 (2,37) | 1 | 3 | 1 |
| C | 1 | 1 | 2 (2,84) | 2 | 1 | 3 |
| C3 | 4 | 3 | 3 (3,51) | 3 | 2 | 2 |
| Odin | 2 | 6 | 4 (5,69) | 4 | 6 | 5 |
| Nim | 7 | 4 | 5 (6,09) | 6 | 4 | 6 |
| D | 8 | 5 | 6 (6,43) | 7 | 5 | 7 |
| Zig | 5 | 8 | 7 (7,70) | 10 | 8 | 4 |
| Rust | 6 | 7 | 8 (7,76) | 8 | 7 | 9 |
| Chapel | 10 | 11 | 9 (8,47) | 5 | 10 | 10 |
| Ada | 9 | 9 | 10 (10,32) | 14 | 9 | 8 |
| Swift | 12 | 10 | 11 (10,65) | 12 | 11 | 14 |
| Mojo | 14 | 12 | 12 (10,98) | 11 | 12 | 11 |
| Fortran | 11 | 14 | 13 (11,05) | 9 | 14 | 12 |
| Julia | 13 | 13 | 14 (11,44) | 13 | 13 | 13 |
| C# | 15 | 15 | 15 (15,30) | 15 | 15 | 16 |
| FreePascal | 16 | 17 | 16 (16,22) | 16 | 17 | 15 |
| Java | 17 | 16 | 17 (16,69) | 17 | 16 | 17 |
| Go | 18 | 18 | 18 (17,56) | 18 | 18 | 18 |
| Haskell | 19 | 19 | 19 (18,98) | 19 | 19 | 19 |
| OCaml | 20 | 20 | 20 (20,32) | 20 | 20 | 20 |
| BQN | 21 | 21 | 21 (21,29) | 21 | 21 | 21 |
| PHP | 22 | 22 | 22 (22,26) | 23 | 22 | 23 |
| JavaScript | 23 | 23 | 23 (22,33) | 22 | 23 | 22 |
| Python | 24 | 24 | 24 (24,17) | 24 | 24 | 24 |
| Lua | 25 | 25 | 25 (24,60) | 25 | 25 | 25 |

« Publié » : le classement de tête du README. Colonnes « Petite », « Publiée », « Grande » : calcul 3 (pour K5,
colonnes 2^11, soit la taille publiée, 2^15 et 2^21).

### 10.4 Effet des tailles : « Hôte » contre « Trois tailles »

* **Aucun langage ne bouge de plus de deux places** (seuil de la section 8), avec les nouveaux binaires comme avec les
  anciens. Deux bougent de deux places : Odin (6e → 4e) et Chapel (11e → 9e) ; C++ passe devant C (rangs espérés
  2,37 et 2,84), les autres bougent d'une place au plus. Ces déplacements sont de l'ordre du bruit de processus de
  l'hôte (10.2).
* Étages de « Trois tailles » (paires ordonnées dans au moins 95 % des variantes) : les 14 premiers | C#, FreePascal,
  Java, Go | Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua. Avec la taille publiée seule (« Hôte »), la frontière
  entre le 14e et le 15e n'est pas établie sur cet hôte : le premier étage compte 18 langages.
* Une taille à la fois (sensibilité), les déplacements sont plus grands, dans les deux sens :
  * **petite taille** : Chapel 5e et Fortran 9e (11e et 14e dans « Hôte »), Zig 10e, Ada 14e. Les variantes à plusieurs
    fils y paient surtout leur lancement : celles de C, C++, Zig, Ada, Rust et Odin, qui créent leurs fils à chaque
    appel, sont plus lentes que leurs variantes à un fil (K9 : 0,43 à 1,8 ms, contre 0,08 à 0,24 ms), celles de Chapel
    et de Fortran, qui gardent une réserve de fils (tâches de Chapel, équipe OpenMP de Fortran), plus rapides
    (0,06 ms). Le plafond de K9 va de 11 à 99 parmi les 14 premiers, celui de K6 de 13 à 79 ;
  * **grande taille** : Zig 4e, Ada 8e, FreePascal 15e (devant C#), Swift 14e. Les noyaux limités par la mémoire
    rapprochent les compilés : parmi les 14 premiers, le plafond de K1 va de 84 à 100 (63 à 100 à la taille publiée),
    celui de K9 de 68 à 99 (35 à 97). Zig et Ada, en retrait sur ces deux noyaux à la taille publiée, en profitent le
    plus (K1 : 69 → 98 et 63 → 91).
* La moyenne des trois tailles efface donc ces déplacements opposés : la petite taille favorise les runtimes à réserve
  de fils, la grande les langages que la limite de la mémoire rapproche des meilleurs.

### 10.5 Effet de l'hôte et du nouveau code : « Publié » contre « Hôte »

* Cinq langages bougent de plus de deux places : **Nim (7e → 4e), D (8e → 5e), Odin (2e → 6e), Zig (5e → 8e),
  Fortran (11e → 14e)**. Les scores baissent pour tous (C : 80,0 → 68,6), surtout par le plafond (C : 85,2 → 62,9).
  Le changement de code du point 2 n'y est pour rien hors d'Odin, de Chapel et de Go : à la taille publiée, le code
  machine est celui du source publié (4.1, 7.2) ; pour ces trois, voir 10.2.
* **K3 en est le premier moteur, par un effet de placement du code déjà établi** (`docs/FINDINGS.md`, « K3 sur la
  machine 3 », et l'expérience de disposition de la v3) : sur Emerald Rapids, la boucle de 16 `incq` en mémoire que
  clang, rustc et Odin produisent pour l'écrivain unique coûte un ou sept cycles par incrément selon son décalage dans
  sa ligne de 64 octets (un cycle à 8 et de 36 à 48), alors que le code de GCC (`mov`, `inc`, `mov`) reste rapide à
  tous les décalages ; sur Cascade Lake, l'effet n'existe pas. La campagne le retrouve. Sur la machine 31, K3
  `sw_padded` (un compteur par fil, sur sa propre ligne, lu et écrit sans `lock`) prend 0,017 à 0,020 s en D, C3, Nim
  et FreePascal (1,5 à 1,7 cycle par incrément), 0,027 à 0,080 s en C++, Mojo et Ada, et 0,087 à 0,092 s, cinq fois
  plus, en C, Fortran, Zig, C#, Rust, Odin, Chapel, Swift, Julia et Java ; les boucles du C et de Rust sont aux
  décalages 16 et 32, du côté lent. Fait nouveau, l'effet existe aussi sur Granite Rapids : sur la machine 30, les
  sept premiers sont ensemble (0,009 à 0,011 s), les dix autres à 0,059 à 0,066 s. Dans les données publiées, les 15
  de ces 17 implémentations mesurées sur Cascade Lake (toutes sauf Swift et FreePascal, reliés par un pont) étaient
  entre 84 et 100 % de la frontière. Le groupe d'un binaire tient donc à la forme du code émis et à la place de sa
  boucle, que le source ne fixe pas. D, C3, Nim, FreePascal, C++ et Mojo passent sous la borne de la section 8
  (5 cycles par incrément, 0,057 s). K3 compte pour un huitième du plafond : sur ce noyau, Odin et Zig perdent 77 et
  79 points de plafond, Fortran 66 ; D en gagne 11, Nim en perd 9.
* Autres noyaux : Odin et Zig perdent aussi sur K1 (96 → 67 et 98 → 69) et K9 (86 → 45 et 66 → 35), Fortran sur K4
  (57 → 10) ; Nim gagne sur K5 (82 → 95).
* L'effet de l'hôte, cinq langages à plus de deux places, est donc plus grand que celui des tailles, aucun.

### 10.6 Ce que cela change

* Le classement de tête du README ne change pas (section 9). La règle fixée pour la v4 s'applique : les tailles y
  compteront comme au calcul 2 (moyenne des trois à poids égaux), dans une seule campagne réunissant les points 2 à 4.
* Deux constats de cette campagne seront examinés avant cette campagne commune : l'effet de placement de K3, établi
  sur Emerald Rapids et retrouvé sur Granite Rapids, premier moteur de l'effet de l'hôte, qui fait passer six
  implémentations sous la borne physique du plan ; sur la machine 31, comme sur l'Emerald Rapids de la remarque sur
  C++, K2 à 8 Mio a deux régimes d'un processus à l'autre, ce qui touche la part D4 du code par défaut.

### 10.7 Erratum (21 novembre, trouvé en préparant le point 4 : `docs/V4_CONVERGE.md`, 4.1)

* **Faute.** La campagne a mesuré les sources de `bench/<langage>`, présentées comme « le source publié » (4.1,
  7.2, 10.5). Pour 20 langages sur 25, ce n'est pas le code du classement publié. Les errata des remarques ont été
  corrigés dans des copies (`bench/<langage>_fix`, `bench/<implémentation>_k9h`, `bench/bqn_rq`), mesurées par paires ;
  le classement publié applique leurs rapports aux données d'origine (`results/transfers.json`, `results/raw_k9h`,
  `analysis/analyze_v2.py`, `dataset_main`), et les sources publiées sont restées d'origine. Manquent aux sources :
  * les corrections d'implémentation : Ada (K1 `aos` et `soa`, K2, Q6 et Q1 `tuned` et `mt`, K9 `tuned` et `mt`),
    Fortran (K1 naturel et mélangé, K2, K4 naturel et sans branchement, K6 naturel, K9 naturel), D (Q1 `tuned` et
    `mt`), Rust (K7 `tuned`), Java (K5 `tuned`, K1 `soa`), Go (K5, K1 `soa`, Q6 `tuned` et `mt`, K9), Haskell (une
    trentaine de clés, K9, latences de K8), OCaml (Q6 `tuned` et `mt`, K1 `aos`, K7 et K8 `tuned`), JavaScript (K7
    `tuned`), Python (K3, K6 `mt`, K8 naturel, K9 `mt`, latences de K8), Lua (K3, K4, Q6 `tuned` et `mt`, K8 naturel et
    ses latences), BQN (K9, K7 naturel) ;
  * le harnais commun de K9 (révision du 1er novembre, `docs/K9.md`) : les grilles sont encore réallouées à chaque
    répétition dans les sources de C++, Zig, Odin, C3, Nim, D, C#, Java, Rust, Go, Julia, Mojo, Haskell, OCaml, Python
    et Lua (les trois variantes), de Fortran et de JavaScript (naturel).
* **Ordre de grandeur.** Certaines corrections sont grandes : K5 `tuned` de Go × 0,38, K1 `aos` d'OCaml × 0,17, K4
  naturel de Haskell × 0,15, Q1 de D × 0,33, K4 sans branchement de Fortran × 0,38 (le noyau inliné dans la boucle de
  mesure n'était pas vectorisé) ; le harnais de K9, × 0,41 à 0,65 à quatre fils sur la machine 16, et sur la machine
  33, pour Rust, 20,3 → 12,7 ms à un fil et 11,3 → 5,1 ms à quatre fils (`results/converge/diag/harnais.txt`).
* **Ce qui tient.** Les comparaisons internes de la campagne (« Hôte » contre « Trois tailles » et contre les tailles
  seules, 10.3 et 10.4) portent sur le même code des deux côtés : elles décrivent l'effet des tailles sur le code non
  corrigé. Le contrôle des anciens binaires (10.2) n'est pas touché.
* **Ce qui ne tient pas.** La comparaison au classement publié (10.5, « effet de l'hôte et du nouveau code ») mêle
  l'hôte et les corrections absentes : la baisse de Fortran sur K4 (57 → 10) tient d'abord à la correction
  `NOINLINE`, une partie des baisses d'Odin et de Zig sur K9 (86 → 45, 66 → 35) au harnais ; le nombre de langages
  déplacés par « l'hôte » (cinq) n'est donc pas établi.
* **Suite.** Les sources publiées sont mises en accord avec le classement publié avant le point 4
  (`docs/V4_CONVERGE.md`, 4.1). La campagne du point 4 mesure, sur un même hôte, chaque cellule touchée avec les deux
  sources ; l'effet de l'erratum sera publié ici. La campagne finale de la v4 mesure le code corrigé.
* **Effet mesuré (22 novembre, campagne du point 4, machine 33 : `docs/V4_CONVERGE.md`, 11.9).** Les rapports de
  temps sont de l'ordre annoncé : harnais de K9 à quatre fils × 1,9 à 2,7 pour C++, C3, D, Odin, Zig, Rust, Nim et
  Python, `tuned` × 1,5 à 1,7 pour neuf langages ; K4 naturel de Haskell × 10,7, K1 `aos` d'OCaml × 5,5, K4 de
  Fortran × 2,5 et 3,1, Q1 de D × 2,6 et 2,8, K5 `tuned` de Go × 2,55. Mais le calcul « Hôte » sur l'une et l'autre
  source ne diffère de plus de deux places pour aucun langage. Contre le classement publié, la source corrigée
  déplace de plus de deux places D (8e → 4e), Odin (2e → 5e) et Mojo (14e → 11e). Pour 10.5 : la baisse de Fortran de
  trois places tenait aux corrections absentes (13e avec la source corrigée) ; celle de Zig ne se retrouve sur la
  machine 33 avec aucune des deux sources (6e), ni la montée de Nim (7e ou 8e) ; celle d'Odin et la montée de D, si.
  Sur le code corrigé et sur cet hôte, l'effet de l'hôte déplace trois langages de trois ou quatre places (D, Odin,
  Mojo), au lieu de cinq ; avec K3 rapporté à la boucle de référence (R4, point 3), D revient à sa place publiée.

