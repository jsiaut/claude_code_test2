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

*À venir.*
