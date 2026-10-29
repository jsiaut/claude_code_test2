# Analyse v3 : réponse au second audit (29 octobre 2026)

*Plan fixé le 29 octobre 2026 et poussé à 15:54 (commit `ae9e1a1`) ; l'heure écrite d'abord ici, « vers 16:30 »,
était fausse. Il est poussé sur GitHub **avant** tout calcul de l'analyse v3 et
**avant** l'expérience de disposition du code de la section 6. Il n'est pas aveugle : je l'écris après avoir lu le
second audit (archivé dans `docs/AUDIT2_2026-10-29.md`) et après avoir vu les résultats v1 et v2. Les analyses v1 et
v2 restent publiées telles quelles.*

## 0. Ce que j'ai vérifié dans l'audit avant d'écrire ce plan

Détail dans `docs/AUDIT2_RESPONSE.md`.
* **Exact, recalculé sur les données** :
  * accord entre machines : 21 inversions sur 210 paires, toutes parmi les 13 premiers ; 17 sur 36 parmi les 9
    premiers, Spearman 0,22 ;
  * position des scores dans leurs intervalles : 0,78 en moyenne, 0,96 pour C ;
  * biais de la frontière dans mon propre bootstrap : sur K9, la frontière des tirages est sous la frontière
    observée dans 98 % des tirages, et Rust ne la tient que dans 14 % ;
  * sens des coupures de régime établi : 154 accélérations, 135 ralentissements ;
  * K10 réintégré : 11 des 13 premiers bougent, C++ passe premier ;
  * chronologie Git et cellules de capacités citées.
* **Inexact** : le réglage `avoid_fma256_chains` de GCC n'explique pas le K5 naturel. `--param
  avoid-fma-max-bits=0` ne change rien. Le mécanisme est autre : GCC, quel que soit le front-end, vectorise la
  réduction en ordre strict (multiplications en vecteur, puis chaîne d'additions scalaires), alors que clang la
  laisse scalaire et la fusionne en FMA (`probes/k5_reduction`). Mon explication précédente (« GCC en mode ISO »)
  était fausse elle aussi : avec `-std=gnu23`, où la contraction est permise, GCC produit la même boucle.
* **Objection juste, conclusion inchangée** : ma sonde du JIT de .NET désactivait la compilation par niveaux. Avec les
  réglages par défaut (niveau 1 et PGO dynamique), les trois boucles restent scalaires
  (`probes/csharp_jitvec_tiered`).

## 1. Forme de la réponse

L'audit montre que l'ordre interne du premier groupe ne se réplique pas d'une machine à l'autre, et que le pilier le
plus subjectif le décide. La v3 change donc ce qu'elle publie comme réponse.
1. **Des étages** (règle de la section 3), sans ordre à l'intérieur d'un étage.
2. **Trois quantités publiées séparément**, par langage (chaîne de référence nommée) et par machine :
   * **plafond** : score E de la configuration v2, avec référence fixe (section 2), noyau par noyau, et part de la
     borne physique là où elle existe ;
   * **code naturel**, sous deux formes : rapport à la même référence (D1), et écart du langage à son propre meilleur
     code (moyenne géométrique de t_meilleur / t_naturel sur les mesures de D1) ;
   * **contrôle** : le pilier C sous les règles v1 et v2, présenté comme un inventaire jugé, pas comme une mesure.
3. **Des énoncés de mécanisme**, chacun avec ses conditions (langage, chaîne, machine).
4. **Le score composite** MS n'est plus qu'une analyse de sensibilité.

## 2. Inférence

* **Estimateur par cellule** (langage × mesure) : moyenne des logarithmes des médianes de processus, sans coupure de
  régime établi. La médiane des médianes de processus reste en sensibilité. Les processus sont classés (plat,
  accélération, ralentissement) avec le critère de rupture de la v2, à titre descriptif seulement.
* **Références fixes.** Pour chaque mesure, la référence de E et de D1 (meilleur langage classé), celles de D3
  (meilleur p99,9, meilleur maximum) et celle de D4 (meilleur temps par taille) sont calculées une fois, sur les
  estimations ponctuelles, puis tenues fixes dans tous les tirages. Le bootstrap ne recalcule plus de minimum.
* **Bootstrap à résidus regroupés.** Avec 2 ou 3 processus, une cellule ne peut pas estimer seule la variance entre
  processus. On la tire donc de toutes les cellules comparables.
  * Pour chaque cellule à P ≥ 2 processus, les résidus r = (y_p − ȳ) × √(P / (P − 1)) sont rangés dans un réservoir
    par noyau et par classe d'implémentation : compilée à l'avance, JIT ou VM, interprète. Un réservoir de moins de
    20 résidus est fusionné avec celui du noyau.
  * Pour chaque tirage, chaque cellule reçoit ȳ* = ȳ + la moyenne de P résidus tirés avec remise dans son réservoir.
  * 2 000 tirages.
  * Les latences de D3 gardent le rééchantillonnage hiérarchique de la v2, avec références fixes ; l'empreinte reste
    fixe.
* **Diagnostic** : position de chaque estimation dans son intervalle, qui doit être proche de 0,5.
* **Analyse globale** : les mêmes options et les mêmes poids que la v2 (20 000 tirages), avec cette inférence.
* **Ensembles de rangs simultanés** (Mogstad et al.) : recalculés sur ce bootstrap et publiés en second rang. Leur
  validité dépend de l'hypothèse que les résidus sont échangeables à l'intérieur d'un réservoir.

## 3. Étages (règle fixée d'avance)

On part de l'ordre de la configuration principale v3. Une frontière entre les positions i et i + 1 est retenue si :
1. aucune paire de langages de part et d'autre n'est inversée dans la réplication sur la machine 3 ;
2. et chaque paire de part et d'autre est ordonnée dans le même sens dans au moins 95 % des tirages de l'analyse
   globale v3.

Les étages sont les suites de langages entre deux frontières retenues. Dans un étage, les langages sont présentés par
ordre alphabétique.

## 4. Réplication : bruit ou interaction langage × machine ?

L'audit le note : la machine 3 n'a qu'un processus par mesure, et ne peut pas trancher. Test, fixé d'avance :
* **Hypothèse nulle** : pas d'interaction ; chaque cellule a la même valeur sur les deux machines, à un décalage près
  par mesure.
* **Vérité simulée** : les estimations v3 de la machine 1, avec K5 commun aux deux classements comme dans la v2.
* **Décalage par mesure** : la médiane, sur les langages, de la différence observée entre machines.
* **Simulation** : un jeu de la machine 1 (P processus par cellule) et un jeu de la machine 3 (un processus par
  cellule), bruités par les résidus regroupés. Pour chaque jeu, scores de la configuration principale v3 et rangs.
* **Statistiques** : Spearman sur les 21, sur les 13 premiers et sur les 9 premiers ; paires inversées parmi les 13
  premiers. 2 000 simulations.
* **Valeur p unilatérale** : part des simulations où l'accord est au plus celui observé.
* **Lecture** : p < 0,05 établit une interaction au-delà du bruit. Sinon, la réplication ne distingue pas
  l'interaction du bruit.

Limite connue : prendre les estimations pour la vérité exagère un peu les écarts entre langages, ce qui rend le test
un peu trop prompt à conclure à l'interaction.

## 5. Décomposition de la variance (descriptive)

Pour chaque mesure présente sur les deux machines, la variance du logarithme du temps est décomposée en :
* part des langages ;
* part de l'interaction langage × machine ;
* part du processus, estimée par la variance des résidus regroupés de la machine 1.

## 6. Expérience de disposition du code (machine actuelle, Emerald Rapids)

* **Implémentations** : C (clang), C (gcc) et Rust, les mêmes sources.
* **Huit dispositions par implémentation** : `-ffunction-sections` (C) et l'éditeur de liens lld avec
  `--randomize-section-padding=<graine>`, graines 1 à 8. Pour Rust, les mêmes options passent par `-C link-arg`.
  Vérification déjà faite sur C (clang) : selon la graine, la boucle de K3 tombe à un décalage 0, 16 ou 48 dans sa
  ligne de 64 octets, et K3 `sw_padded` passe de 79–98 ms à 11–19 ms.
* **Mesure** : toutes les mesures de K1 à K9, deux processus par disposition, dans un ordre tiré au hasard (graine
  fixe), avec les répétitions de la campagne. K10 est exclu.
* **Sorties, descriptives** :
  * par mesure, le rapport de la variance entre dispositions à la variance entre processus d'une même disposition ;
  * l'étendue des moyennes par disposition.

  Elles n'entrent pas dans les scores.

## 7. Ce qui n'est pas fait, et pourquoi

| Recommandation de l'audit | Raison |
|---|---|
| Nouvelle notation du pilier C à l'aveugle par plusieurs évaluateurs | Un seul évaluateur possible. Le pilier C est présenté à part, sous deux règles, et son poids sur l'ordre est publié |
| Campagne entrelacée de 10 à 30 processus, sur trois micro-architectures avec compteurs | Pas d'autre machine ni de PMU ici. Une campagne sur cette machine seule ne dirait pas si l'ordre fin est une propriété des langages |
| Régimes « base » (x86-64-v3) et « peak » (PGO, LTO, BOLT, options du runtime) | Les variantes optimisées en AVX-512 explicite ne compilent pas en x86-64-v3 sans réécriture ; reporté |
| Relecture experte, deux implémentations par noyau, entrées réservées | Hors de portée d'un auteur seul, et les tailles sont fixées dans 21 implémentations |
| Nouveaux noyaux : parallélisme mémoire, décompression, JSON, tri et jointure, E/S groupées, thread par cœur, démarrage | 21 implémentations par noyau ; reportés |
