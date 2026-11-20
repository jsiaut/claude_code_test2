# v4, point 2 : trois tailles par noyau — plan (19 novembre 2026)

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

### 7.2 Changement d'hôte (20 novembre, 1 h 45, avant toute mesure sur le nouvel hôte et toute analyse)

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
