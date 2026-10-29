# Analyse v2 : réponse à l'audit du 29 octobre 2026

*Plan fixé le 29 octobre 2026. Il est poussé sur GitHub **avant** la remesure de K5 et **avant** tout calcul de
l'analyse v2 ; l'heure d'envoi enregistrée par GitHub en fait foi, mieux que les horodatages de commit, que
déclare l'auteur. Ce plan n'est pas aveugle : j'ai lu les analyses de sensibilité de l'audit (sections 6.3 et
6.4) avant de l'écrire. Ses choix sont motivés par la validité des mesures, pas par leur effet sur le
classement, mais personne ne peut le vérifier. L'analyse v1, pré-enregistrée, reste publiée telle quelle.*

## 0. Ce que l'audit a établi, et ce que j'en ai vérifié

L'audit, archivé tel quel dans `docs/AUDIT_2026-10-29.md` (ses numéros de section sont cités ici), reproduit les scores publiés à l'identique. Réponse point par point : `docs/AUDIT_RESPONSE.md`. J'ai vérifié ses affirmations
sur les données et le code : elles sont exactes, à deux exceptions près.
* JEP 401 est « Integrated », release 28, d'après l'en-tête de la page lue le 29 octobre, et non « Submitted ».
* L'absence de vectoriseur automatique dans le JIT de .NET, que l'audit n'avait pas pu trancher, est confirmée
  par le désassemblage du JIT lui-même (`probes/csharp_jitvec/`).

## 1. Ce qui ne change pas

* Les noyaux, le code des implémentations et les données de la campagne d'avant le redémarrage (K1–K4,
  K6–K9), l'empreinte, la vectorisation mesurée et les sondes. Seuls les binaires sont recompilés, pour la
  machine 3 (section 2).
* **Aucune implémentation n'est réécrite après avoir vu les résultats.** Les déficits d'implémentation
  connus sont quantifiés, pas corrigés :
  * K6 Q1 `tuned` plus lent que `natural` en Nim et en D ;
  * K8 `tuned` en C ;
  * l'écart des backends GCC et LLVM sur K8.

  Les corriger pour certains langages seulement fausserait l'égalité d'effort.

## 2. Nouvelles mesures (machine 3)

**La machine a changé.** Le conteneur a redémarré le 29 octobre à 11:53 sur un autre hôte : Intel Xeon de modèle
207 (Emerald Rapids), TSC à 2,1 GHz, L2 de 2 Mio par cœur, L3 de 260 Mio partagé, 4 vCPU. La campagne (machine 1) et
les remesures du 28 octobre (machine 2, même modèle que la machine 1) ont été faites sur Cascade Lake, TSC à 2,8 GHz.
La machine 3 est caractérisée dans `results/hw/machine3/` :

| Grandeur | Machine 3 |
|---|---|
| Fréquence effective (scalaire) | 3,1 à 3,5 GHz |
| Débit FMA AVX-512 f32 (3 mesures) | 164, 182 et 232 Gflop/s : l'état de l'hôte varie d'une minute à l'autre |
| Latence de chargement | L1 1,2–1,6 ns ; L2 (jusqu'à 1 Mio) 5–5,6 ns ; L3 (4–16 Mio) 56–71 ns ; au-delà de 24 Mio, 100 à 275 ns |
| Bande passante en lecture, 1 thread | 24,7 Go/s sur 64 Mio (en partie dans le L3) ; 11,9 Go/s sur 1 Gio |

Deux défauts d'outil, découverts en préparant cette caractérisation et corrigés avant toute mesure de K5 :
* sur ce cœur (génération Golden Cove), le renommage replie les chaînes d'additions d'un immédiat (`add $1`) :
  la sonde de fréquence `freq` donnait 14 à 18 GHz. Elle utilise désormais des additions registre-registre ; elle
  était valide sur Cascade Lake, qui ne fait pas ce repliement ;
* la première version du témoin construisait mal sa chasse de pointeurs (plusieurs cycles courts au lieu d'un seul).

Conséquences pour le plan :
* **K5 est remesuré entièrement sur la machine 3**, `natural` et `tuned`, pour toutes les implémentations. Chaque
  noyau reste mesuré sur une seule machine ; E mêle deux machines d'un noyau à l'autre (K5 sur la machine 3, les
  autres sur la machine 1, plus le pont de K3 pour Haskell, déjà publié), jamais à l'intérieur d'un noyau.
* **Recompilation.** Les implémentations compilées à l'avance sont recompilées sur la machine 3 par leurs scripts
  inchangés (`-march=native` ou équivalent), sources inchangées : le protocole compile pour la machine de mesure, et
  les JIT s'adaptent d'eux-mêmes à la machine. Empreintes des binaires avant et après :
  `results/hw/machine3/binaries.txt`. clang 23 y voit un `emeraldrapids`, GCC 16 un `sapphirerapids` ; les deux
  préfèrent des vecteurs de 256 bits pour la vectorisation automatique, comme sur la machine 1.
* Les expériences du 29 octobre (désassemblage du JIT de .NET, styles de K8) ont été faites sur la machine 3.

Mesures, toutes par `tools/measure_v2.py`, sortie `results/raw_v2/<implémentation>.jsonl` (l'analyse v1 ne lit pas
ce répertoire). Chaque processus est précédé d'un **témoin d'environnement** (`hwprobe witness`, 0,4 s) : médiane de
5 essais du débit FMA AVX-512 et de la fréquence effective, latence d'un saut dépendant sur 2 et 32 Mio, bande
passante en lecture sur 64 Mio.

1. **K5, `natural` et `tuned`, toutes les implémentations** (étiquette `v2_k5`).
   * 9 processus en 9 passes, ordre tiré au hasard (graine fixe).
   * Échauffement : 10 répétitions pour les JIT, 2 pour les autres.
   * Répétitions mesurées : 20, ou le nombre figé par la calibration si une répétition dépasse 1 s.
   * Ces données remplacent toutes les données de K5 dans l'analyse v2 : K5 ne mêle plus deux machines (section
     4.6 de l'audit).
2. **Pages géantes** (étiquette `v2_thp`). La politique est `madvise` sur les trois machines (relevée le 29
   octobre). Mesure descriptive : K1 `natural`, un processus par implémentation, avec relevé toutes les 100 ms de
   `AnonHugePages` (`/proc/<pid>/smaps_rollup`). On saura quels runtimes marquent eux-mêmes leur tas.
3. **Réplication sur une autre microarchitecture** (étiquette `v2_m3`, descriptive). Une passe de K1 à K4 et de K6
   à K9, un processus par mesure, toutes les implémentations, mêmes répétitions que la campagne
   (`results/calib.json`), ordre des blocs tiré au hasard. K10 n'est pas repris (hors score en v2).

**Usage du témoin, fixé d'avance.** Sa variabilité propre, mesurée avant la remesure, est du même ordre que les
épisodes qu'il devrait signaler (12 lancements consécutifs : 112 à 226 Gflop/s, latence à 2 Mio de 36 à 64 ns).
* Aucune mesure n'est rejetée sur sa foi.
* Publié : pour chaque implémentation de K5, la corrélation de rang (Spearman) entre le débit FMA du témoin et le
  temps médian du processus, et la même corrélation sur l'ensemble des processus, après division du temps par la
  médiane de l'implémentation.
* Analyse de sensibilité : scores de K5 recalculés sans les processus dont le témoin est dans le décile le plus
  lent (débit FMA) de la remesure ; on publie les rangs qui changent.

**Usage de la réplication, fixé d'avance.** Avec un seul processus par mesure, elle ne donne pas d'intervalles.
* Par mesure (noyau, variante, paramètre) : corrélation de rang de Spearman entre les temps de la machine 1
  (médiane de la campagne) et ceux de la machine 3.
* Classement de la configuration principale v2 recalculé avec les seules données de la machine 3 (K1 à K4 et K6 à
  K9 de `v2_m3`, K5 de `v2_k5` ; empreinte D2 et pilier C inchangés, car indépendants de la machine), comparé au
  classement v2 : corrélation de Spearman, plus grand déplacement, langages qui changent de groupe.
* Les tailles des noyaux ont été choisies pour la machine 1. Sur la machine 3, dont le L3 fait 260 Mio, les
  données de 64 à 256 Mio (K1, K6, K9) tiennent en partie dans le L3 : la réplication teste donc la stabilité du
  classement quand le goulot d'étranglement change, pas seulement quand la machine est plus rapide.

## 3. Analyse v2 : configuration principale

| # | Choix | v1 (pré-enregistré) | v2 | Motif (audit) |
|---|---|---|---|---|
| 1 | Répétitions d'un processus | toutes | **régime établi** : dernier segment après une rupture détectée | JIT de C# mesuré pendant sa recompilation (4.5) |
| 2 | Estimateur | médiane des médianes de processus | idem (le minimum est une alternative de l'analyse d'incertitude) | distributions bimodales (4.4) |
| 3 | K10 | dans E et D1 | **hors score**, publié comme statistique descriptive | régime bistable qui dépend du compilateur et de la machine (5.2) |
| 4 | D3 | queue rapportée à la médiane du langage | **latences absolues** : moyenne géométrique de (meilleur p99,9 / p99,9) et (meilleur max / max) | Java pénalisé pour sa bonne médiane (3.5 c) |
| 5 | Référence de D4 | C | **meilleur langage** | asymétrie (3.5 b) |
| 6 | Règle du pilier C | norme contre extension | **chaîne livrée** (`analysis/capabilities_v2.py`, 45 cellules reclassées) | pénalité des langages normalisés (3.6) |
| 7 | C3 dans le pilier C | oui | **non** (déjà mesurée par E et D1) | double compte (3.4) |
| 8 | Normalisation de E | frontière (meilleur langage) | frontière (bornes physiques : alternative) | (3.5 a) |
| 9 | Agrégation | arithmétique 0,35 C + 0,40 E + 0,25 D | idem (géométrique : alternative) | (3.1) |
| 10 | Bootstrap | 1 000 tirages ; D3 et D4 fixes | 2 000 tirages ; latences de D3 rééchantillonnées par répétition, référence de D4 recalculée à chaque tirage | (6.1) |

**Détection du régime établi (choix 1).**
* On cherche une rupture de niveau unique dans le logarithme des temps d'un processus. Pour chaque coupure
  possible, avec au moins 3 répétitions de chaque côté, on calcule la réduction de la somme des carrés. La
  rupture est retenue si elle passe le critère BIC, (n − 2)·ln(RSS₀/RSS₁) > 3·ln n, et si les médianes des
  deux segments diffèrent de plus de 20 %.
* On garde alors le dernier segment.
* Les processus de moins de 6 répétitions sont gardés entiers.

**Bornes physiques (choix 8, alternative).** E_bornes = moyenne géométrique de min(1, borne / t) :

| Mesure | Borne |
|---|---|
| K1 | 4 colonnes × 16 Mio à 10 Go/s (6,7 ms) |
| K3 | 2²⁵ incréments à 5 cycles (latence du transfert écriture-lecture) à 3,2 GHz (52 ms) |
| K4 | 16 Mio à 10 Go/s (1,7 ms) |
| K5 | une FMA AVX-512 par cycle, limitée par deux chargements de 512 bits par cycle : la moitié du débit FMA crête mesuré sur la machine 3 (médiane de 3 mesures, 182 Gflop/s), soit 2 × 2 × 2 048 × 65 536 / 182·10⁹ = 2,95 ms |
| K6 Q6 / Q1, 1 thread | 10 et 13 o par ligne à 10 Go/s |
| K6 Q6 / Q1, 4 threads | à 61 Go/s (lecture seule) |
| K9, 1 thread | 4 × 64 Mio à 8,84 Go/s (triade) |
| K9, 4 threads | 4 × 64 Mio à 43,3 Go/s (triade) |
| K7, K8 | pas de borne : frontière |

Ce choix ne change pas l'ordre selon E : il multiplie tous les scores d'un noyau par la même constante. Il change
l'échelle de E, donc son poids effectif dans le score composite.

## 4. Analyse d'incertitude globale (étape 7 du manuel OCDE/JRC)

20 000 tirages. Chacun combine un tirage bootstrap des mesures et un tirage des choix suivants, tous
équiprobables :

| Choix | Options |
|---|---|
| Estimateur | médiane des médianes de processus ; minimum des médianes de processus |
| Normalisation de E | frontière ; bornes physiques |
| D3 | absolu ; relatif à p50 |
| Référence de D4 | meilleur langage ; C |
| Référence de D1 | t\* de la mesure ; meilleur code naturel |
| Agrégation | arithmétique ; géométrique |
| Règle du pilier C | v2 sans C3 ; v1 avec C3 |
| Bruit de jugement | chaque cellule de la matrice glisse d'un cran (0 ↔ 0,5 ↔ 1) avec une probabilité de 10 % |
| Poids des piliers | Dirichlet centrée sur (0,35 ; 0,40 ; 0,25), concentration 20, dans la moitié des tirages ; Dirichlet(1,1,1) dans l'autre |
| Poids internes | catégories de C, composantes de D, noyaux de E : Dirichlet centrée sur les poids publiés, concentration 20 |

K10 reste hors score dans tous les tirages : ce n'est plus un choix, c'est une décision de validité.

Sorties :
* rang médian, intervalle [5 %, 95 %], P(1er), P(3 premiers), P(10 premiers) ;
* les mêmes grandeurs en ne faisant varier que les mesures (configuration principale).

## 5. Ensembles de confiance simultanés pour les rangs

Méthode de Mogstad, Romano, Shaikh et Wilhelm (2024), par projection, dans la configuration principale :
* bootstrap des différences de score Δ_jk pour toutes les paires ;
* valeur critique c = quantile à 95 % de max_jk |Δ\*_jk − Δ̂_jk| / σ_jk ;
* j précède k de façon significative si Δ̂_jk − c·σ_jk > 0 ;
* rang de j dans [1 + #{k significativement devant j}, n − #{k significativement derrière j}].

Ces ensembles couvrent tout le classement à la fois, à 95 %, pour l'incertitude de mesure.

## 6. Forme de la réponse

* **Plus de « 1er » imprimé quand l'ordre n'est pas établi.** Deux langages sont déclarés à égalité si
  leurs ensembles simultanés se recouvrent, ou si aucun ne précède l'autre dans 90 % des tirages de l'analyse
  globale. Les groupes publiés en découlent.
* **Profils par principe**, sur les données de la configuration principale :
  * disposition (K1, D2) ;
  * SIMD et vectorisation (K5, K4, C3) ;
  * hiérarchie mémoire (K2, K9) ;
  * concurrence et modèle mémoire (K3, K6 et K9 en 4 threads) ;
  * allocation et prévisibilité (K8, D3) ;
  * analytique (K6, K7) ;
  * capacités par catégorie (A à F).
* **Carte à deux axes** (plafond E, code par défaut D1) et **front de Pareto** sur (C, E, D).
* **Langage et implémentation séparés** : les couples (C, clang), (C, gcc), (Fortran, gfortran) et (Fortran,
  flang) sont présentés côte à côte ; pour K8 et K4, regroupement par backend (GCC, LLVM, autres).

## 7. Ce que cette révision ne fait pas, et pourquoi

| Recommandation de l'audit | Pourquoi elle n'est pas faite ici |
|---|---|
| Machine nue et compteurs matériels | Impossible dans cet environnement : VM sans PMU |
| Plusieurs architectures | Une deuxième microarchitecture est arrivée par accident (machine 3). La réplication de la section 2 n'y fait qu'un processus par mesure : une réplication complète demanderait une campagne entière (environ 15 h pour 9 processus) |
| Relecture par des experts de chaque langage | Hors de portée d'un auteur unique |
| Nouveaux noyaux (E/S, pages géantes, NUMA, énergie, démarrage, code irrégulier) | 21 nouvelles implémentations chacun ; NUMA et énergie (RAPL) inaccessibles dans la VM |
| K10 refait (régimes contrôlés, boucle ouverte) et D3 en boucle ouverte | Réécriture du harnais dans 21 langages ; reporté |
| Campagne complète à 10 processus ou plus | Possible (une dizaine d'heures). Proposé comme étape suivante : elle réduirait l'incertitude de mesure, mais l'audit montre que les égalités du haut viennent surtout des choix de méthode |
| Pré-enregistrement chez un tiers et analyse en aveugle | Impossible a posteriori pour v1 ; ce plan est poussé avant ses données |

Ces limites figurent aussi dans le README, section 7.

## 8. Précisions d'implémentation (fixées avant le premier calcul sur les données v2)

Le code (`analysis/analyze_v2.py`, `analysis/charts_v2.py`) est poussé avant d'être exécuté sur les données de la
machine 3. Je l'ai mis au point sur des données brouillées : K5 de v1 à la place de la remesure, réplication
simulée, étiquettes des langages permutées au hasard. Les résultats de ces essais n'ont aucun sens et ne sont pas
conservés. Les précisions suivantes complètent le plan sans le modifier.

1. **Régime établi** : appliqué à tous les processus de toutes les mesures (machines 1 et 3). Pour K8 `natural`, les
   latences d'un processus sont coupées au même endroit que ses temps.
2. **Bootstrap hiérarchique** : processus tirés avec remise ; pour chaque processus tiré, médiane d'un tirage avec
   remise de ses répétitions (prise dans une réserve de B tirages indépendants du même processus : même loi). D3 :
   processus, puis répétitions, puis médianes sur toutes les répétitions retenues (l'estimation ponctuelle prend,
   comme v1, les médianes sur toutes les répétitions).
3. **Analyse globale** : chaque tirage prend au hasard l'un des 2 000 tirages bootstrap. Le bruit de jugement touche
   toutes les cellules sauf C3 mesurée ; une cellule à 0,5 passe à 0 ou à 1 avec la même probabilité. Les
   implémentations annexes reçoivent le pilier C de leur langage (comme v1) et ne sont pas classées.
4. **Groupes.** L'égalité de la section 6 n'est pas transitive. Une frontière de groupe sépare les positions i et
   i + 1 de l'ordre principal seulement si aucun langage au-dessus n'est à égalité avec un langage au-dessous. Je
   publie aussi les groupes obtenus avec les seuls ensembles simultanés (incertitude de mesure seule) : on voit
   ainsi ce qui vient de la mesure et ce qui vient des choix de méthode.
5. **Contrôle de vraisemblance** des données de la machine 3, même règle que v1 (temps < 0,9 × borne : calcul
   sauté, mesure exclue).
   * K5 : débit FMA le plus haut mesuré sur la machine 3 (232 Gflop/s).
   * Réplication : bornes généreuses (50 Go/s sur 1 thread, 200 Go/s sur 4, 3,9 GHz pour K3), qui ne signalent
     qu'un travail sauté, pas un cache plus grand.
6. **Profils** (0–100) : moyenne arithmétique de composantes comprises entre 0 et 1.
   * disposition : K1 (score E du noyau), D2 ;
   * SIMD : K5, K4, C3 mesurée ;
   * hiérarchie mémoire : D4, K9 sur 1 thread ;
   * concurrence : K3, K6 sur 4 threads (Q6 et Q1), K9 sur 4 threads ;
   * allocation et prévisibilité : K8, D3 ;
   * analytique : K6 sur 1 thread (Q6 et Q1), K7 ;
   * capacités : moyenne de chaque catégorie A à F (règle v2).

   Pour K6 et K9, le rapport t\*/t de chaque mesure ; pour les autres noyaux, leur score E.
7. **Poids effectifs** : R² de chaque pilier avec MS sur les 21 langages, et sa part dans la somme des trois.
8. **Bimodalité** : signalée quand la plus grande médiane de processus d'une mesure dépasse la plus petite de 25 %,
   après le régime établi.
9. **Décomposition** : la configuration principale, puis chaque choix ramené à sa version v1, un à la fois (dont le
   K5 d'avant et K10 réintégré).
10. **Corrélations de rang** : Spearman, avec rangs moyens pour les ex aequo.
11. **Réplication** : un langage change de groupe si son rang sur la machine 3 sort des rangs qu'occupe son groupe
    v2.

## 9. Erratum (29 octobre, après les mesures)

* Section 2, point 2 : « la politique est `madvise` sur les trois machines » est inexact. Je l'ai relevée sur la
  machine 1, le 28 octobre à 08:02 et à 11:14, juste avant la campagne, mais seulement dans ma session de travail,
  pas dans le dépôt. Je l'ai relevée aussi sur la machine 3. Elle ne l'a pas été sur la machine 2.
