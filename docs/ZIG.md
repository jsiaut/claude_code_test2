# Remarque sur Zig : le vectoriseur de boucles désactivé

Remarque transmise par l'utilisateur le 30 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).

## 1. Ce que dit la remarque

* (a) Zig 0.16 et 0.17 désactivent le vectoriseur de boucles de LLVM, pour contourner un bug de LLVM qui compilait mal
  le compilateur Zig lui-même (llvm-project #186922). Zig 0.18 (LLVM 23) le réactivera.
* (b) C'est la cause des boucles naturelles scalaires de K4 et K9, et pas l'aliasing (FINDINGS) ni le langage (README).
* (c) Avec le vectoriseur, Zig passerait d'environ 71,5 à 76 points, et de la 5e à la 3e place (estimation ponctuelle,
  hors analyse globale).
* (d) K5 `tuned` : le code `@Vector(16, f32)` donne le même code machine que les intrinsèques de C ; l'écart mesuré
  tient dans la dispersion entre processus.
* (e) K9 `mt` : `std.Thread.spawn` (sans libc) coûte 140 à 200 µs par thread, contre 35 µs pour un pthread ; le
  harnais en crée 16 par répétition. `std.Io.Group.concurrent` réduit ce coût, sans expliquer tout l'écart.
* (f) K8 : Zig fait jeu égal avec C compilé par clang ; ce sont les compilateurs GCC qui sont devant.
* (g) K3 sur la machine 3 : hasard de disposition du code, déjà établi par l'étude.
* (h) Le pilier « contrôle » est juste ; seule la justification de F4 a vieilli (`std.Io.File.MemoryMap` existe
  depuis 0.16).

Propositions : (1) corriger le texte sur la vectorisation ; (2) ajouter une annexe `zig_master` ; (3) créer les
threads une seule fois ou passer par `Io.Group` ; (4) compter la version de la chaîne de compilation parmi les sources
d'incertitude.

## 2. Vérifications faites avant ce plan (machine 5)

Le conteneur a redémarré le 30/10 à 13 h 22 sur un nouvel hôte (« machine 5 ») : Cascade Lake du même modèle que les
machines 1, 2 et 4 (modèle 85, révision 7, 4 vCPU, 16 Go), latence à 4 Mio de 138 à 151 ns, débit DRAM de 9,4 à
10 Go/s (`results/hw/machine5/`).

* **Sources primaires.** Les notes de version de Zig 0.16.0 (section « Loop Vectorization Disabled to Work Around
  Regression ») et de 0.17.0 (même titre) le disent : la passe est désactivée « entirely until we upgrade to a version
  of LLVM where this bug is fixed » ; le correctif n'est pas dans LLVM 22 ; 0.18.0 (LLVM 23) réactivera la passe.
  Dans les sources de 0.17.0, `src/zig_llvm.cpp`, ligne 288 :
  `pipeline_opts.LoopVectorization = false; // https://github.com/llvm/llvm-project/issues/186922`, à côté de
  `SLPVectorization` et `LoopInterleaving`, actifs hors mode debug. Dans master (0.18.0-dev.753+1420479be, du
  29/10), la même ligne est `= !options->is_debug`. Archives vérifiées (SHA-256 de l'index de ziglang.org, signatures
  minisign) : `results/zig_check/toolchains.txt`.
* **Mesures avec un pilote commun** (`tools/zig_check/`, `results/zig_check/k4_k9_versions.txt`). Les noyaux K4 et K9
  naturels, copiés tels quels de `bench/zig` et `bench/c`, liés au même pilote C ; temps minimum de 3 processus de
  61 répétitions :

  | Chaîne | LLVM | K4 (ms) | K9 naturel (ms) | Boucles vectorisées |
  |---|---|---|---|---|
  | Zig 0.15.2 | 20.1.2 | 1,8–3,2 | 25,1–26,3 | les deux |
  | Zig 0.16.0 | 21.1.0 | 6,8–7,1 | 30,3–32,8 | aucune |
  | **Zig 0.17.0 (étude)** | 22.1.8 | **6,8–9,9** | **28,9–30,3** | **aucune** |
  | Zig 0.18.0-dev.753 | 23.1.4 | 2,3–3,1 | 25,1–26,4 | les deux |
  | C, clang livré avec Zig 0.17 | 22.1.8 | 2,4–2,8 | 24,9–25,9 | les deux |
  | C, clang 23.1.5 (étude) | 23.1.5 | 2,4–3,0 | 25,0–26,2 | les deux |

  Le même LLVM 22.1.8 vectorise donc le code C équivalent ; l'IR non optimisé de Zig 0.17, passé au pipeline `-O3`
  de ce clang, est vectorisé lui aussi (K4 et K9). En master, K9 commence par un test de recouvrement des deux
  tableaux à l'exécution, puis prend la boucle vectorielle : l'aliasing possible n'empêche rien. **(a) et (b) sont
  exacts** ; l'explication de FINDINGS par l'aliasing est fausse.
* **Binaires de la campagne.** `bench/zig/ms`, recompilé sur la machine 5 par son script inchangé, est identique octet
  pour octet au binaire de la campagne compilé sur Cascade Lake (`e4b28d54…`, `results/hw/machine3/binaries.txt`) ;
  `bench/c/ms` aussi (`ff81685a…`). La source de Zig compile sans changement avec master.
* **Coût des threads** (`results/zig_check/threads.txt`, 4 threads lancés puis attendus, 5 processus) :
  `std.Thread.spawn` + `join` coûte en moyenne 148 à 217 µs par thread (Zig 0.17 sans libc), 125 à 171 µs lié à la
  glibc, contre 46 à 123 µs pour `pthread_create` en C et 28 à 30 µs par tâche pour `Io.Group.concurrent`. **(e)
  est exact sur le coût.** Les autres langages compilés lancent aussi leurs threads à chaque passe (C et Nim :
  pthread ; C++ : `std::thread` ; Rust : `std::thread::scope` ; Odin : `core:thread`) : c'est la règle commune des
  implémentations, et non un choix propre à Zig.
* **F4** (`probes/zig/probe_f4.zig`, `results/zig_check/f4_probe.txt`) : `std.Io.File.MemoryMap.create` projette le
  fichier (`mmap` partagé, visible dans `/proc/self/maps`) et `std.mem.bytesAsSlice` le réinterprète sans copie. En
  règle v1, F4 vaut 1 pour une projection portable de la bibliothèque standard (D `std.mmfile`, Nim `memfiles`) et
  0,5 pour une liaison POSIX seule : la note v1 de Zig (0,5, « POSIX seulement ») est une **erreur de fait**, la
  note v2 (1) est juste. La note v1 entre dans la moitié des variantes de l'analyse globale.

## 3. Plan (poussé avant les mesures)

### 3.1 Implémentations

* `zig` : Zig 0.17.0, binaire de la campagne (référence du classement).
* `zig_master` : Zig 0.18.0-dev.753+1420479be, **même source**, mêmes options (`bench/zig_master/build.sh`).
* `zig_io` (0.17) et `zig_master_io` (master) : copie où seuls les lancements de threads de K3, K6 `mt` et K9 `mt`
  passent par `Io.Group.concurrent` (pool d'`Io.Threaded`) au lieu d'un `std.Thread.spawn` par thread et par passe
  (`bench/zig_io/ms.zig`, changements marqués « Io.Group : »). Sommes de contrôle valides pour les quatre binaires.
* `c` : binaire de la campagne, témoin du même hôte sur 5 clés (K4 ×2, K5 `tuned`, K9 naturel, K9 `mt`).

### 3.2 Mesures (`tools/measure_zig.py`)

`zig` et `zig_master` sur les 27 clés qui entrent dans le score ; `zig_io` et `zig_master_io` sur les 5 clés à
threads (K3 `sw_padded` et `rmw_padded`, K6 `mt` Q6 et Q1, K9 `mt`) ; `c` sur ses 5 clés. 7 processus par cellule,
en 7 passes, ordre tiré au hasard dans chaque passe (graine 20261080 + passe), répétitions de `results/calib.json`,
échauffement de 2. Puis `tools/c3_measure.py zig_master` (vectorisation mesurée de la boucle chaude, note C3 de la
règle v1). Sortie : `results/raw_zig/`.

### 3.3 Analyse (`analysis/zig_check.py`)

Rapports appariés comme dans la confrontation : r = exp(moyenne des log des médianes de processus de la nouvelle
implémentation − moyenne de celles de `zig`), intervalle par bootstrap (2 000). Les rapports sont transférés aux
processus de Zig des données principales, puis l'analyse globale de la v3 est rejouée (mêmes 20 000 variantes, même
graine, même code que la confrontation). Tous les scénarios portent la correction de F4 (v1 = 1).

* **A'** : le classement publié avec la seule correction de F4 (base de comparaison, et nouveau classement publié).
* **S1, Zig 0.18-dev** : les 27 clés de Zig multipliées par r(`zig_master`/`zig`) ; C3 de Zig = celle de
  `zig_master`. C'est l'annexe demandée par la proposition (2).
* **S1-K5** : S1 avec r = 1 pour K5 (les données principales de K5 viennent de la machine 3, un Emerald Rapids).
* **S2, Zig 0.18-dev et Io.Group** : S1, sauf les 5 clés à threads, multipliées par r(`zig_master_io`/`zig`).
* **S3, Zig 0.17 et Io.Group** : A', avec les 5 clés à threads multipliées par r(`zig_io`/`zig`).

Pour chaque scénario : score de référence, plafond E, code par défaut D, contrôle C, rang espéré sur 21, rang dans
90 % des variantes et part des variantes où Zig devance ses voisins. Témoin du même hôte : rapport Zig/C sur les 5
clés de `c`, comparé au même rapport dans les données principales (affirmations (d) et (e)).

### 3.4 Décisions fixées d'avance

1. **Le classement principal reste celui de Zig 0.17.0.** Le protocole prend les dernières versions stables au
   28/10 ; 0.18 n'est pas publiée, et changer après coup la version d'un seul langage romprait la règle commune.
   Le classement publié devient A' (correction de F4).
2. **Le README donne le résultat de S1 sur la ligne de Zig et dans son paragraphe**, et l'explication est corrigée
   partout (README, FINDINGS) : la passe a été désactivée par l'équipe Zig, ce n'est pas une propriété du langage.
3. **S2 et S3 restent des analyses de sensibilité.** Un pool pour Zig seul romprait la règle commune des
   implémentations (des threads lancés à chaque passe) ; le coût mesuré de `std.Thread.spawn` est publié comme un
   fait sur la bibliothèque standard de Zig.
4. **La version de la chaîne de compilation entre dans les limites de l'étude**, avec S1 comme mesure de son effet :
   je n'ai mesuré deux versions que pour Zig, donc elle ne devient pas un facteur de l'analyse globale.
5. (d), (f) et (g) sont vérifiés sur les données existantes et le témoin du même hôte ; ils ne changent aucune
   donnée.

## 4. Résultats

Mesures du 30/10, 13:55 à 14:10 (machine 5) : 69 cellules × 7 processus, aucune somme de contrôle fausse, rien
d'autre ne tournait. Rapports, témoin et scénarios : `results/report_zig.md` et `results/zig_check.json`.

### 4.1 Ce que change Zig master, à source identique

La boucle chaude de Zig master est vectorisée sur K4 et K9 (`tools/c3_measure.py`, registres ymm) : C3 = 1, contre 0
pour 0.17. Rapports appariés master / 0.17 (moyenne géométrique de 7 processus chacun, IC à 95 %) :

* **Les deux boucles naturelles** : K4 0,42 (`natural_unsorted`, 0,35–0,49) et 0,43 (`branchless_unsorted`) ; K9
  naturel 0,76 (0,66–0,85). Zig master fait alors jeu égal avec C sur K4 (environ 3,4 ms contre 3,5) et le devance
  sur K9 naturel (31 ms contre 32).
* **Le reste bouge peu, et pas toujours dans le bon sens** : K7 `tuned` 0,90, K6 Q1 naturel 0,87, K5 `tuned` 0,95 ;
  mais K9 `mt` 1,12 (1,05–1,19), K6 `mt` Q6 1,17, K8 `tuned_alloc` 1,12, K1 naturel 1,08. Un changement de LLVM
  (22 à 23) ne touche pas que le vectoriseur.

### 4.2 Effet sur le classement (analyse globale rejouée, 20 000 variantes)

| Scénario | Score de Zig | Plafond E | Code naturel D1 | Rang espéré | Rang dans 90 % des variantes | Part des variantes où Zig est 1er |
|---|---|---|---|---|---|---|
| **A'** : Zig 0.17, classement publié (F4 corrigée) | 71,5 | 70,8 (10e) | 22,0 | 5,39 (5e) | 2–10 | 2 % |
| **S1** : Zig 0.18-dev | 74,8 | 78,5 (4e) | 25,0 (1er) | 2,62 (2e) | 1–5 | 24 % |
| S1-K5 : S1 sans transfert pour K5 | 74,6 | 78,0 | 25,0 | 2,71 (2e) | 1–5 | — |
| S2 : 0.18-dev et `Io.Group` | 75,4 | 79,8 | 25,0 | 2,45 (2e) | 1–5 | — |
| S3 : 0.17 et `Io.Group` | 71,4 | 70,5 | 22,0 | 5,48 (5e) | 2–10 | — |

* **A'** : la correction de F4 ne change aucun rang ni aucun score de référence (la règle v2 donnait déjà 1) ;
  elle ne joue que dans les variantes en règle v1. Ordre : C, C++, Odin, C3, Zig, Nim, Rust, D, Ada, Chapel…
* **S1** : C (rang espéré 1,89 ; 79,4 points), **Zig (2,62 ; 74,8)**, C++ (3,04 ; 76,4), Odin, C3, Nim, Rust, D,
  Ada, Chapel. Zig reste 3e au score de référence, derrière C++, mais passe devant lui dans 53 % des variantes, devant
  Odin dans 85 %, devant C3 dans 87 %. Les scores des autres baissent un peu (C 80,1 à 79,4) : Zig master devient la
  référence de plusieurs mesures (K1, K7 `tuned`, K9 naturel), ce qui relève le meilleur temps auquel tous sont
  comparés.
* **Ce qui fait la différence** : sur K4, Zig passe de 33 à 79 % du meilleur temps ; sur K5, de 82 à 86 % ; sur K7,
  à 100 %. Le code naturel D1 devient le meilleur de l'étude (25,0, devant Julia).

### 4.3 Verdicts sur la remarque

* **(a), (b) : exacts.** Le vectoriseur est désactivé par l'équipe Zig (sources et notes de version) ; à source
  identique, master vectorise K4 et K9, et K9 n'est pas bloqué par l'aliasing (test de recouvrement à l'exécution).
  Mon explication de K9 par l'aliasing était fausse ; celle du README (« sans le faire à votre place ») aussi : ce
  n'est pas le langage. Le second juge à l'aveugle l'avait déjà vu (`results/blind_notes.md`, Zig C4 : « le
  pipeline de zig 0.17.0 n'auto-vectorise aucune boucle […] alors que `opt-23 -O3` vectorise le même IR ») ; je ne
  l'avais pas suivi, parce que sa note portait sur une capacité et pas sur les mesures.
* **(c) : confirmé, et un peu au-delà.** L'estimation ponctuelle de la remarque (76 points, 3e) est proche du score
  mesuré par S1 (74,8, 3e au score) ; sur les 20 000 variantes, Zig 0.18-dev est 2e en rang espéré.
* **(d) : exact pour le code, pas tranché pour le temps.** La boucle chaude de K5 `tuned` est la même en Zig et en C
  (quatre accumulateurs zmm, huit FMA 512 bits par tour ; `results/zig_check/k5_tuned_asm.txt`). Sur la machine 5,
  Zig/C = 1,06, contre 1,22 dans les données principales (machine 3). L'écart des données principales tient sans doute
  aux états de performance par processus déjà documentés ; il reste dans les données, comme pour tous les langages,
  et l'analyse globale le traite par son bootstrap des processus.
* **(e) : exact sur le coût, mais `Io.Group` ne paie pas partout.** `std.Thread.spawn` coûte 3 à 4 fois un
  `pthread_create`. Avec `Io.Group`, K9 `mt` gagne 10 % (0,90 ; 0,86–0,94), K6 `mt` Q1 4 %, mais K6 `mt` Q6 perd
  30 % (1,30 ; 1,20–1,41), et K3 ne bouge pas. Sur K9 `mt`, Zig reste 1,34 fois plus lent que C avec `Io.Group` : les
  threads n'expliquent qu'une partie de l'écart, comme le disait la remarque. S3 ne change rien au classement.
* **(f) : exact.** Sur K8, les meilleurs temps viennent des langages compilés par GCC (Ada 108 ms, C par gcc 160,
  C++ par g++ 181, Fortran 193) ; Zig (255 ms) devance C compilé par clang (266) et Rust (270).
* **(g) : exact**, déjà établi par l'étude (K3 sur la machine 3, `docs/FINDINGS.md`).
* **(h) : exact, avec une conséquence que la remarque n'avait pas vue.** La note v1 de F4 était fausse (0,5 au lieu
  de 1) ; elle entre dans la moitié des variantes. Corrigée, elle ne change aucun rang.

### 4.4 Ce qui change dans l'étude

* Le classement principal reste celui de Zig 0.17.0 (décision 1), avec la correction de F4 (A').
* README et FINDINGS : l'explication de la vectorisation de Zig est corrigée, et le résultat de S1 est donné sur la
  ligne de Zig, dans son paragraphe et dans les limites (décisions 2 et 4).
* Le coût de création des threads de Zig est publié comme un fait ; les implémentations `mt` ne changent pas
  (décision 3).
