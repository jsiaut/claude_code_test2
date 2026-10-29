# Réponse à l'audit du 29 octobre 2026

*L'audit est archivé tel quel dans [`docs/AUDIT_2026-10-29.md`](AUDIT_2026-10-29.md) ; les numéros de section
cités ici sont les siens. Ce document vérifie ses affirmations une par une, sur les données brutes, le code et les
sources. Il dit ce que j'ai corrigé, ce que j'ai changé dans l'analyse et ce que je n'ai pas fait. Le plan de la
révision ([`docs/ANALYSIS_V2.md`](ANALYSIS_V2.md)) a été poussé sur GitHub avant toute nouvelle mesure, et le code de
l'analyse avant son premier calcul.*

## 1. En bref

* **L'audit est exact sur presque tout.** J'ai recalculé chacun des chiffres qu'il tire des données (section 2) : je
  les retrouve tous, à l'arrondi près.
* **Deux points où il se trompe ou s'arrête.**
  * JEP 401 n'est pas « *Submitted*, sans version cible » : la page lue le 29 octobre indique « *Integrated* »,
    release 28, mise à jour le 7 août 2026. Le reste de sa remarque (aplatissement limité à 64 bits) est exact.
  * L'absence de vectoriseur automatique dans le JIT de .NET, qu'il n'avait pas pu vérifier, est confirmée par le
    code machine que produit le JIT lui-même (section 3).
* **Un point que mes mesures nuancent** : sur K8 `tuned`, l'audit attribue l'écart entre C et Ada surtout au style de
  codage. Avec les compilateurs de l'étude (clang 23, GCC 16), sur la machine 3, le compilateur pèse plus que le style
  (section 3).
* **Six erreurs de ma part**, toutes relevées par l'audit, sont corrigées dans le README et consignées dans le journal
  (section 5).
* **Ce qui change** : une analyse v2 (section 4), une remesure complète de K5, un témoin d'environnement, un relevé
  des pages géantes, une réplication sur une autre microarchitecture. L'analyse v1 reste publiée telle quelle.

Un événement extérieur s'est ajouté : le conteneur a redémarré le 29 octobre à 11:53 sur un autre hôte, un Xeon
Emerald Rapids (machine 3), au lieu des Cascade Lake des machines 1 et 2. C'est le même type de machine que celle de
l'audit (famille 6, modèle 207, 2,1 GHz). Les nouvelles mesures y sont faites ; voir `docs/ANALYSIS_V2.md`, section 2.

## 2. Affirmations chiffrées, recalculées sur les données

Script de vérification : les mêmes fichiers bruts que l'analyse v1 (`results/raw`, `results/raw_post`).

| Section | Affirmation de l'audit | Ce que je trouve | Verdict |
|---|---|---|---|
| 3.2 | Corrélations entre piliers de 0,86 à 0,91 | C–E 0,89 ; C–D 0,86 ; E–D 0,91 | exact |
| 3.3 | D1 entre 0,004 et 0,176 ; environ 14 % de l'effet de D | 0,004 à 0,176, écart-type 0,047 ; poids × écart-type : D1 0,023, D2 0,051, D3 0,047, D4 0,041, soit 14 % pour D1 | exact |
| 3.5 c | Java : meilleure queue p99,9 absolue (134 µs), D3 = 0,20 | p50 14,7 µs, p99,9 134 µs, D3 0,20 ; OCaml 191 µs (0,22) ; C 218 µs (0,91) ; Python : même rapport p99,9/p50 que C | exact |
| 4.2 | K2 à 2 Mio : 26 à 147 ns par saut pour un même binaire | Ada 28,5 / 26,3 / 146,8 ns (16:03) ; Zig 26,3 / 98,1 (14:05) / 26,0 ; Fortran 94,2 (12:57) / 27,1 / 25,9 ; Odin 131,8 / 114,7 | exact |
| 4.3 | 593 mesures notées : 279 sur 2 processus, 272 sur 3, 42 sur 9 | 279, 272, 42 | exact |
| 4.4 | K5 `tuned` bimodal ; Rust : 4 processus rapides, 5 lents, médiane 6,67 ms | C++ 4,39–4,75 ms (5) et 6,09–7,11 (4) ; C 4,65–4,93 (6) et 8,19–8,61 (3) ; Rust 4,76–5,27 (4) et 6,67–8,47 (5) | exact |
| 4.5 | C# K5 `tuned` : 10 processus sur 11 ont une seconde moitié 1,5 fois plus rapide | 10 sur 11 | exact |
| 5.2 | K10 : part des répétitions sous 20 ms, C (clang) 9 %, C (gcc) 30 %, gfortran 53 %, flang 0 % | 8,9 %, 30,0 %, 53,3 %, 0 % ; Java 63 %, Chapel 61 %, Odin 59 % | exact |
| 5.3 | Q1 `tuned` plus lent que `natural` en Nim (98 contre 95 ms) et en D (110 contre 79 ms) | Nim 98,1 contre 94,9 ms ; D 109,9 contre 79,3 ms ; C 32,1 ms | exact |
| 4.7 | Lua mesure du temps CPU, OCaml et Chapel une horloge non monotone | `os.clock()` (Lua et LuaJIT), `Unix.gettimeofday` (OCaml), `Time.stopwatch` sur `gettimeofday` (Chapel) | exact ; effet mesuré en section 5 |

## 3. Faits sur les langages et les outils

| Section | Point | Vérification | Verdict |
|---|---|---|---|
| 7 | JEP 401 « *Submitted*, sans version cible » | En-tête de la page (lue le 29 octobre) : *Status* Integrated, *Release* 28, *Updated* 2026/08/07. Phrase sur l'aplatissement : « *this limits the size of mutable fields that store flattened references to no more than 64 bits* » | **erroné** pour le statut, exact pour la limite. Mon README et `docs/FINDINGS.md` disaient déjà « intégré au JDK 28 » ; le JDK de référence de l'étude reste le 27, sans classes valeur |
| 7 | C# : « pas de vectoriseur » non vérifié | Sonde `probes/csharp_jitvec` : .NET 10.0.403, JIT en optimisation complète (`TieredCompilation=0`), désassemblage par `DOTNET_JitDisasm`. Une somme d'entiers, une addition de tableaux de `float` et une somme conditionnelle restent scalaires (`add eax, [rdi]`, `vaddss`), alors que le JIT déclare « *X64 + VEX + EVEX* ». Sortie : `results/probes/csharp_jitvec_disasm.txt` | **confirmé** par le compilateur lui-même |
| 7 | « `hardware_destructive_interference_size` vaut 64 alors que le préchargeur d'Intel impose 128 » | La sonde de faux partage ne voit pas de pénalité à 64 octets par rapport à 128 sur la machine 1 (`results/hw/fs.txt`) ; « impose » n'est pas établi | **audit fondé** : formulation corrigée (section 5) |
| 5.1 | K8 `tuned` : à algorithme égal, le style de codage fait un facteur 2,8 | J'ai repris trois codages du même algorithme (A comme `bench/c/ms.c`, B état passé par valeur, C arène globale comme Ada), deux exécutions, machine 3. clang 23 : A 242 / 239 ms, B 289 / 224, C 217 / 186. GCC 16 : A 105 / 115, B 84 / 91, C 116 / 99 | **nuancé** : avec ces compilateurs, le backend fait un facteur 2,2 à 2,7, le style 20 à 30 %. Le score K8 de C mesure surtout clang. La v2 présente les couples (langage, compilateur) et regroupe K8 et K4 par backend |
| 3.5 a | Borne de K5 trop optimiste (deux FMA par cycle, alors que les chargements limitent à une) | Exact : deux chargements de 64 octets par FMA, deux chargements par cycle | **audit fondé** : borne corrigée dans l'alternative « bornes physiques » de la v2 |
| 3.5 a | Borne de K3 lâche (un incrément par cycle) | 58 ms pour 2²⁵ incréments font environ 5,5 cycles : écriture puis relecture à chaque incrément | **audit fondé** : borne v2 à 5 cycles par incrément |

## 4. Critiques de méthode : ce que la v2 change

Le détail est dans `docs/ANALYSIS_V2.md`. Rien n'y a été choisi pour son effet sur le classement, mais le plan a été
écrit après lecture des analyses de sensibilité de l'audit : il n'est pas aveugle.

| Section | Critique | Réponse |
|---|---|---|
| Verdict 1, 7 | « Odin 1er » imprimé en gras alors que l'ordre n'est pas établi | Plus de rang imprimé à l'intérieur d'un groupe. Groupes déclarés à partir d'ensembles de confiance simultanés et de l'analyse globale |
| 5.2 | K10 mesure la probabilité d'un régime, pas une propriété de langage | K10 sort du score ; part du régime rapide publiée comme statistique descriptive |
| 3.5 c | D3 rapporte la queue à la médiane du langage | D3 sur latences absolues (meilleur p99,9 / p99,9 et meilleur max / max) ; l'ancienne forme reste une option de l'analyse globale |
| 3.5 b | D4 rapporté à C, qui ne peut rien perdre | D4 rapporté au meilleur langage, recalculé à chaque tirage |
| 3.6 | La règle « norme contre extension » pénalise C, C++, Ada et Fortran | Règle unique « chaîne livrée » : 45 cellules reclassées, après relecture des 166 cellules notées 0,5 (`analysis/capabilities_v2.py`) ; l'ancienne règle reste une option de l'analyse globale |
| 3.4 | C3 compté deux fois (pilier C, puis E et D1) | C3 sort du pilier C |
| 3.7 | Une seule cellule suffit à inverser des voisins | Bruit de jugement dans l'analyse globale : chaque cellule glisse d'un cran avec une probabilité de 10 %, pas seulement celles notées 0,5 |
| 4.4 | Médiane d'une distribution bimodale | Minimum des médianes de processus comme option de l'analyse globale ; bimodalité signalée mesure par mesure |
| 4.5 | C# mesuré pendant sa recompilation | Détection du régime établi (rupture de niveau, critère BIC) appliquée à tous les processus ; échauffement de 10 répétitions pour les JIT dans la remesure de K5 |
| 4.6 | K5 et K10 mêlent deux machines dans un même score | K5 remesuré entièrement sur une seule machine ; K10 hors score |
| 4.3 | Trop peu de processus | K5 : 9 processus par mesure. Le reste n'est pas remesuré : une campagne complète à 9 processus demanderait environ 15 h (proposée) |
| 4.2 | État de la machine non surveillé ; pages géantes non relevées | Témoin d'environnement avant chaque processus (débit FMA, fréquence, latences à 2 et 32 Mio, bande passante) ; politique `madvise` relevée ; relevé de `AnonHugePages` par implémentation |
| 6.1 | Bootstrap : D3 et D4 fixes, peu de tirages | 2 000 tirages ; latences de D3 rééchantillonnées (processus puis répétitions) ; référence de D4 recalculée |
| 6.2, 6.3 | Intervalles de rang marginaux ; seuls les poids des piliers varient | Ensembles de rangs simultanés (Mogstad, Romano, Shaikh et Wilhelm, 2024) ; analyse d'incertitude globale de 20 000 tirages sur l'estimateur, les normalisations, les références, l'agrégation, la règle du pilier C, le bruit de jugement et tous les poids |
| 3.2, 3.3 | Piliers corrélés ; poids effectifs loin des poids nominaux | Poids effectifs publiés à côté des poids nominaux |
| 2.3, 8 (P0) | Répondre par profils, carte à deux axes, front de Pareto | Profils par principe, carte plafond / code par défaut, front de Pareto sur (C, E, D) |
| 2.2, 8 (P1) | Le score mesure un assemblage (langage, compilateur, auteur, machine) | Couples (C, clang) / (C, gcc) et (Fortran, gfortran) / (Fortran, flang) côte à côte ; K4 et K8 par backend ; réplication sur une autre microarchitecture |
| 5.3 | Effort inégal des variantes `tuned` | Quantifié, pas corrigé : réécrire seulement certains langages après avoir vu les résultats fausserait l'égalité d'effort |
| 4.8 | Pré-enregistrement partiel ; une phrase du texte « pré-enregistré » affirmait d'avance un résultat | Plan v2 poussé avant les données, code d'analyse poussé avant son premier calcul, mis au point sur des données brouillées. La phrase reste dans `METHODOLOGY.md` (texte d'origine), avec une note dans le journal |

## 5. Erreurs de ma part, corrigées

1. **K10 et le *batching*.** J'avais écrit que le régime rapide de K10 était « l'effet de *natural batching* décrit
   par Thompson ». C'est faux : le *smart batching* de Thompson est une conception délibérée, qui envoie dès que des
   données sont disponibles et amortit une opération coûteuse. Ici, c'est un régime émergent et non contrôlé, que la
   médiane échantillonne. Le README est corrigé.
2. **« Aucune mesure n'est tirée de deux machines. »** Vrai variante par variante, faux pour le score : la mesure de E
   de K5 et de K10 prenait le minimum de `natural` (machine 1) et de `tuned` (machine 2), et la frontière t\* mêlait
   donc deux hôtes. Corrigé dans le README ; la v2 remesure K5 sur une seule machine et sort K10 du score.
3. **64 ou 128 octets.** « Le préchargeur d'Intel impose 128 » et « 128, la bonne valeur sur Intel » (Zig) étaient trop
   forts : ma propre sonde ne voit aucune pénalité à 64 octets par rapport à 128 sur la machine 1. Le README dit
   maintenant que la question reste ouverte et que l'étude ne la tranche pas.
4. **Horloges.** Le README annonçait des répétitions « sur l'horloge monotone ». Trois implémentations s'en écartent :
   Lua et LuaJIT mesurent du temps CPU (`os.clock()`), OCaml et Chapel une horloge murale non monotone
   (`gettimeofday`). Effet mesuré : pour les processus à un thread, le temps CPU vaut 98,8 % du temps mural en médiane
   pour Lua (96,5 % au pire), comme pour C (98,6 %). L'écart est de l'ordre du pour cent, sans effet sur les rangs
   (Lua est dernier, à un facteur 200 de la frontière). Une horloge non monotone n'a d'effet que si l'heure système
   est réglée pendant la mesure, ce que rien n'indique. Écart consigné dans le journal.
5. **Une phrase écrite avant les données.** `METHODOLOGY.md` (section 2) affirmait qu'une analyse de sensibilité
   « montre » que le classement ne dépend pas des poids. Elle a été écrite avant toute mesure, et elle est démentie :
   l'ordre change dans les deux premiers groupes. Je laisse le texte d'origine et l'annote dans le journal.
6. **« Latence la plus régulière » et « 1er ».** Le rapport p99,9/p50 désignait C3, C++ et C comme les plus
   prévisibles, alors que Java et OCaml ont les meilleures queues absolues. Et le tableau d'ouverture classait Odin
   premier, en gras, alors que l'ordre des trois premiers n'était pas établi. Les deux sont corrigés dans le README.

## 6. Ce que je ne fais pas, et pourquoi

| Recommandation | Raison |
|---|---|
| Machine nue, compteurs matériels, fréquence fixée | Impossible ici : VM sans PMU, sans contrôle de la fréquence |
| Plusieurs architectures (Intel, AMD, ARM) | Une deuxième microarchitecture Intel est arrivée par accident ; la réplication n'y fait qu'un processus par mesure |
| Relecture par des experts de chaque langage, deux implémentations indépendantes par noyau | Hors de portée d'un auteur unique ; c'est la limite la plus importante qui reste (section 2.2 de l'audit) |
| Nouveaux noyaux : E/S et *smart batching*, pages géantes, NUMA, énergie, démarrage, code irrégulier | 21 implémentations chacun ; NUMA et RAPL inaccessibles dans la VM. Le construit reste plus étroit que la *mechanical sympathy* étendue (section 2.1 de l'audit) |
| K10 refait en régimes contrôlés, D3 en boucle ouverte sans omission coordonnée | Réécriture du harnais dans 21 langages ; reportée. K10 sort du score en attendant |
| Campagne complète à 10 processus ou plus, dimensionnée selon Kalibera et Jones | Possible (environ 15 h) ; proposée comme étape suivante |
| Évaluateurs indépendants du pilier C (κ de Cohen) | Un seul évaluateur ; le bruit de jugement de l'analyse globale en tient lieu, faute de mieux |
| Contrôle de K3 par un résultat dépendant des données | Non fait : la borne physique et l'inspection du code machine restent les seuls garde-fous (section 5.5 de l'audit) |
| Pré-enregistrement chez un tiers, analyse en aveugle | Impossible a posteriori pour v1. Pour v2, l'heure d'envoi sur GitHub fait foi, et le code a été mis au point sur des données brouillées |

## 7. Résultats de la v2

Détail : `results/report_v2.md` ; synthèse en tête du README.

* **Le haut du classement s'ordonne en partie.** L'audit concluait à « un trio de tête probable mais non
  ordonné ». Avec ses recommandations appliquées, C et C++ sont les deux seuls langages qui peuvent être premiers.
  * Ensembles de confiance simultanés à 95 % : C 1–2, C++ 1–3.
  * L'un des deux est premier dans 87 % des 20 000 tirages de l'analyse globale (C 57 %, C++ 30 %).
  * Ils devancent Odin dans 84 % et 72 % des tirages ; C ne devance C++ que dans 64 %.
  * Odin est troisième (ensemble 2–9, premier dans 7 % des tirages).
* **La règle de groupement fixée d'avance fait un seul groupe des 13 premiers.** Leurs ensembles simultanés se
  chevauchent de proche en proche, de C (1–2) à Mojo (11–13). Les rangs 14 à 21 sont déterminés exactement par la
  mesure : C#, Java, Go, Haskell, OCaml, JavaScript, Python, Lua.
* **Ce que l'audit prévoyait se vérifie en partie.**
  * Chapel recule (6e → 10e) ; Rust remonte d'un rang (9e → 8e), moins que prévu.
  * Ada gagne un rang (10e → 9e) : la nouvelle règle des capacités le remonte, la queue de latence absolue le
    retient.
  * Aucun choix pris isolément ne déplace un langage de plus de trois rangs : c'est la combinaison des choix de la
    v1 qui mettait Odin en tête.
* **C# en régime établi** : 4,3 ms sur K5 optimisé, contre 3,9 ms pour C ; la v1 le mesurait à 17 ms, pendant la
  recompilation du JIT.
* **Poids effectifs.** Sur les 21 langages, les trois piliers expliquent chacun l'essentiel de MS (R² de 0,93,
  0,97 et 0,86), tant ils sont corrélés. Parmi les 13 premiers, où se joue l'ordre fin, c'est le **pilier C**
  (jugements sur les capacités) qui fait l'essentiel des écarts.
  * R² : 0,78 pour C, 0,52 pour E, 0,27 pour D.
  * Poids × écart-type : 3,8 points pour C, 2,5 pour E, 0,9 pour D.

  La remarque de l'audit sur D (section 3.3) reste donc vraie en v2, et l'ordre à l'intérieur du premier groupe
  dépend surtout du pilier le plus subjectif. Le bruit de jugement de l'analyse globale en tient compte.
* **Témoin et pages géantes.**
  * Le témoin d'environnement ne prédit pas le temps des processus : corrélation de rang de −0,11 à 0,08 sur 450
    processus. Sans le décile le plus lent, aucun rang ne change.
  * Sous la politique `madvise`, seuls CPython (34 Mio) et Go (2 Mio) obtiennent des pages géantes : elles
    n'expliquent pas les écarts entre langages.
<!-- M3_AUDIT -->
