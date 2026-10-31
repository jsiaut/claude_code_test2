# Remarque sur D : un Q1 écrit hors de la convention, deux cases de la règle v1, et une cause fausse dans le README

Remarque transmise par l'utilisateur le 31 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).
L'auteur de la remarque n'a pas pu exécuter le banc du dépôt : il a réécrit les noyaux et mesuré avec LDC 1.36
(LLVM 17), GDC 14 et clang 17 et 23, sur un Cascade Lake à 2 vCPU. Toutes les vérifications ci-dessous sont les
miennes, sur le source de la campagne et des copies du banc, machine 10.

## 1. Ce que dit la remarque

* **Verdict** : la 9e place sous-estime D ; estimation 6e–7e en rang espéré et 3e au score (environ 72,9 au lieu de
  71,0).
* **Justifié** : le ramasse-miettes (pire pause des langages compilés sur K8 naturel, 126,9 ms contre 3,6 ms pour Java
  et Go et 1,3 ms pour C++ ; D3 = 0,034, le plus bas des 13 premiers ; `--DRT-gcopt=fork:1` la ramènerait à 10–18 ms,
  hors défaut) ; le tableau associatif de K7 (réécrit en templates depuis 2.112, mais une allocation GC par entrée) ;
  la chaîne (LDC 1.43.0, frontend 2.113.0, dernière stable) et la note de contrôle v2 (87,1).
* **(1) Q1** : la version optimisée est plus lente que la naturelle (110 contre 79 ms ; C 32 ms ; à 4 threads 43 contre
  13 ms ; K6 = 0,51). Elle fait six passes masquées par bloc, l'approche des langages sans types vectoriels ; tous les
  autres langages notés C1 = 1, et Rust, utilisent l'algorithme de la référence C, en une passe. Réécrit en
  `core.simd`, Q1 fait 22,4 ms (C 23,2). C'est, selon la règle commune, un écart à une convention que suivent les autres
  implémentations, donc une erreur ; Julia (C1 = 0,5) n'a pas de type vectoriel portable.
* **(2) Stencil naturel** : la cause écrite dans le README est fausse pour D. `-release` ne garde les vérifications de
  bornes que dans le code `@safe` ; le code est `@system` ; le désassemblage ne montre aucune vérification, mais des
  pointeurs de lignes relus après chaque écriture : LDC n'émet pas de métadonnées TBAA. Le même C++ en
  `vector<vector<double>>` est vectorisé par clang, et redevient scalaire avec `-fno-strict-aliasing`. Écrit
  autrement, le naturel vectorise (35,5 ms ; 27,2 en copiant les lignes ; 24,5 en `double[M][]` ; 25,9 en opérations
  sur tableaux).
* **(3) Règle v1** : E3 et E4 valent 0,5, justifiés par `ldc.intrinsics`, alors que druntime fournit
  `core.builtins.likely/unlikely` et `core.simd.prefetch` ; le second juge les notait 1 ; seule la v2 a été
  réconciliée. Contrôle v1 de D : 77,5 → 78,9.
* **(4) Mineur** : les noyaux laissés au vectoriseur (Q6, Q1) sont compilés sans la préférence 512 bits, contrairement
  à ceux de Fortran et de Chapel (+26 % sur sa forme de Q1) ; `build.sh` annonce LLVM 21.1.8 alors que les paquets
  officiels de LDC 1.43.0 embarquent LLVM 22.1.8 ; A3 peut citer les champs de bits natifs (sans `-preview` depuis
  2.112) ; D3 = 1 est un peu généreux, mais cohérent avec le `sysconf` crédité au C.
* **À ne pas changer** : K8 tuned (référence de GCC, même forme que le C).
* **Effet estimé** : Q1 corrigé 72,9 points, 7e (6,84) ; avec les errata, 6e (6,70) ; avec le stencil en `double[M][]`,
  73,1, 6e (6,30). D, Zig, Nim et Ada formeraient un groupe sans ordre établi.

## 2. Vérifications faites avant ce plan (machine 10)

**Machine 10.** La VM a redémarré le 31 octobre à 14 h 39 sur un hôte Emerald Rapids du même modèle que les machines 3,
8 et 9 (modèle 207, 4 vCPU ; latence à 4 Mio 52 ns, DRAM 13,4 Go/s : `results/hw/machine10/`). Preuves :
`results/d_check/` (script `tools/d_check/collect.sh`, sonde `tools/d_check/probe.d`).

* **Chaîne** (`versions.txt`) : ma chaîne est LDC 1.43.0 compilé depuis les sources officielles contre le LLVM 21.1.8
  du système (`/opt/src/build-ldc.sh`, `llvm-config-21`), ce que dit `build.sh`. Les paquets officiels utilisent LLVM
  22.1.8 (CHANGELOG de 1.43.0 : « The prebuilt packages use v22.1.8 » ; paquet téléchargé, `ldc2 --version`).
  **Les deux constats sont exacts** ; l'écart (même version de LDC, autre LLVM) est mesuré à titre d'information.
* **Ramasse-miettes** : dans les données principales, pause maximale de K8 naturel 126,9 ms (Java 3,6 ; Go 3,6 ; C++
  1,3) ; D3 = 0,034, le plus bas des 13 premiers. **Exact.** Indicatif, ici : avec `--DRT-gcopt=fork:1`, pause
  maximale 43 ms, mais K8 naturel passe à 2,3 s. Hors défaut : règle des runtimes par défaut.
* **K7 naturel** (`druntime.txt`) : `core.internal.newaa`, « template implementation of associative arrays », alloue
  chaque entrée par `new Entry!(K, V)` sur le tas du GC. **Exact.**
* **Q1 (1)** : dans les données principales, Q1 tuned 107,5 ms contre 88,3 naturel ; 43,4 à 4 threads (C : 32,1 et
  13,4) ; K6 = 0,515. **Exact.** Le code fait six passes masquées par bloc de 4 096 lignes, et le vectoriseur de LLVM les
  traite (33 instructions ymm : `q1_asm.txt`) : il fait ce qu'il annonce. Mais la convention existe : parmi les
  langages à types vectoriels portables standard (C1 = 1 en règle v1), C++, Zig, Odin, C3, Mojo et C# écrivent Q1 tuned
  avec l'algorithme de la référence C, en une passe de 16 lignes (leurs commentaires le disent) ; les blocs servent aux
  langages qui n'en ont pas (Nim, Fortran, Chapel, Julia ; Ada, dont les vecteurs sont propres à GNAT). D, C1 = 1, qui
  utilise `core.simd` dans K1, K5 et K9, est le seul de sa classe à s'en écarter. Copie corrigée (`bench/d_fix`) : même
  algorithme que la référence C, vecteurs `core.simd` (`vpcmpled`, `vpmovzxbd`, `vpmuldq`, 199 instructions zmm),
  sommes de contrôle justes ; indicatif ici : 72,5 → 32,0 ms (C 26,3), à 4 threads 22,5 → 12,0 ms (C 9,7). LDC 1.43
  plante sur deux écritures (une affectation `v.array[k] = …` dans une fonction `inline`, une expression vectorielle
  passée à une fonction dans un `+=`), contournées par des variables nommées.
* **Stencil (2)** (`stencil.txt`) : `-release` n'active les vérifications de bornes que dans les fonctions `@safe`
  (`ldc2 --help`, `driver/cl_options.cpp`) ; `k9Natural` est `@system`. Sa boucle n'a aucune vérification, reste
  scalaire (`vaddsd`, déroulée par 3) et relit les pointeurs de lignes après chaque écriture ; l'IR de LDC ne porte
  aucune métadonnée `!tbaa`. Contre-épreuve : clang 23 vectorise le même stencil en `vector<vector<double>>` (28
  instructions vectorielles), plus du tout avec `-fno-strict-aliasing`. **Exact : la cause écrite dans le README est
  fausse pour D.** En `double[M][]` (copie `bench/d_nat`), la boucle vectorise ; indicatif : 37,8 → 22,9 ms.
* **E3 et E4 (3)** (`druntime.txt`, sonde) : `core.builtins` définit `expect`, `likely` et `unlikely` (selon le
  compilateur, `__builtin_expect` ou `llvm_expect` ; `llvm.expect` présent dans l'IR) ; `core.simd.prefetch` émet
  `llvm.prefetch`, puis `prefetcht0`. Le juge à l'aveugle les notait 1 sous les deux règles, et ma règle R les crédite
  déjà (`analysis/standard_rule.py` : « druntime ») ; seule la matrice v1 garde 0,5 et une justification par
  `ldc.intrinsics`. **Erratum : E3 = 1, E4 = 1 en règle v1** (textes v2 précisés).
* **512 bits (4)** : Fortran (`tuned.f90`, `-mprefer-vector-width=512`) et Chapel (`ms_tuned`) compilent leurs noyaux
  optimisés sans la préférence 256 bits ; D, Nim, Julia et les autres non. Pas de convention ; pour Julia, la même
  option est restée une sensibilité. **Exact, sensibilité.**
* **A3** (sonde) : `struct BF { uint a : 3; uint b : 5; }` compile sans `-preview` (4 octets). **Texte précisé**, note
  inchangée (1). **D3** : gardé à 1, comme le `sysconf` du C, ce que la remarque admet.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune aux remarques

`docs/FORTRAN.md`, 3.1 : « Est une erreur : un code qui ne fait pas ce qu'il annonce (Ada) ou qui s'écarte d'une
convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle de mesure). Une meilleure forme
ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation nouvelle. » Le Q1 de D relève de
la première phrase : la convention est celle de mes propres implémentations pour sa classe de langages (types
vectoriels portables standard), et la forme corrigée n'est pas nouvelle, c'est l'algorithme de référence du banc, tel
que je l'ai transcrit pour C++, Zig, Odin, C3, Mojo et C#. Les formes en une passe proposées pour Julia (C1 = 0,5) et
la forme en registres de C# (déjà dans la convention) restent des optimisations nouvelles.

### 3.2 Ce qui entre dans le classement publié

* **Errata de la règle v1** : E3 = 1 (`core.builtins`), E4 = 1 (`core.simd.prefetch`).
* **Correction de Q1** : rapports appariés `d_fix` / `d_ref` de K6 tuned Q1 et K6 `mt` Q1, reportés sur les données
  principales par la règle de `analysis/transfer_check.py` (pont par le C du même hôte au-delà de 25 % d'écart) ; la
  version par transfert seul est publiée à côté.
* **Texte du README** : la cause du stencil naturel de D (aliasing, pas vérifications de bornes), et Q1 dans le
  paragraphe de D.

### 3.3 Hors du classement

La préférence 512 bits (S-512) ; le stencil naturel en `double[M][]` (S-nat : le code naturel ne change pas, règle
commune, `docs/ADA.md` décision 3) ; le paquet officiel à LLVM 22.1.8 (S-L22, information) ; le ramasse-miettes en
marquage concurrent (information sur la latence de K8).

### 3.4 Mesures (`tools/measure_d.py`, machine 10)

77 cellules × 7 processus (539), en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard
(graine 20261331). Répétitions de `results/calib.json` (clé de D, ou de C pour le témoin) ; échauffements des données
principales (1 ; 2 pour K5). Sortie : `results/raw_d/`.

* `d_ref` : source de la campagne recompilé sur l'hôte (référence des paires), 26 clés du score.
* `d_l22` : même source, paquet officiel (LLVM 22.1.8), 26 clés.
* `d_fix` : K6 tuned et `mt` Q1 ; témoins K6 naturel Q1, K6 tuned Q6, K9 tuned, K5 tuned ; et K6 `mt` Q6, K4 sans
  branchement, K1 aos (paires de S-512).
* `d_512` : copie corrigée avec `-mattr=-prefer-256-bit` : K6 tuned et `mt` Q6 et Q1, K4 sans branchement, K1 aos.
* `d_nat` : K9 naturel en `double[M][]`, témoin K9 tuned. `d_gc` : K8 naturel avec `--DRT-gcopt=fork:1`.
* `c` (clang, binaire de la campagne) : témoin du pont sur les 7 clés reportées.

### 3.5 Analyse (`analysis/d_check.py`) et décisions fixées d'avance

Analyse globale de la v3 rejouée (mêmes tirages), données principales avec les corrections transférées :

| Scénario | Ce qui change |
|---|---|
| Avant | rien (doit redonner 71,0 points et la 9e place) |
| D-E | errata E3 et E4 en règle v1 |
| D-Q1, D-Q1-T | Q1 corrigé (pont / transfert seul) |
| **D-EQ (publié)**, D-EQ-T | errata et Q1 corrigé |
| S-512 | D-EQ, et K6 tuned et `mt` Q6, K4 sans branchement, K1 aos × min(1, r(d_512 / d_fix)) ; Q1 × min(1, r(d_512 / d_fix)) |
| S-nat | D-EQ, et K9 naturel × r(d_nat / d_ref) (règle du pont) |
| S-L22 (information) | D-EQ, et les 26 clés × r(d_l22 / d_ref), transfert seul (Q1 tuned et `mt` gardent la correction) |
| S-tout | D-EQ + S-512 + S-nat |

Décisions :
1. **D-EQ devient le classement publié** ; tous les chiffres publiés (tableau, figures, README) sont recalculés.
2. **Le README est corrigé** : cause du stencil de D, Q1 dans son paragraphe, et sa place.
3. **Le code naturel ne change pas** ; S-nat est publié comme sensibilité, avec la recommandation des tableaux
   rectangulaires par la spécification de D.
4. **La version de LLVM entre dans les limites** si S-L22 déplace D ; la chaîne du classement reste celle fixée le 28
   octobre.

## 4. Résultats

539 processus (77 cellules × 7 passes), le 31 octobre de 15 h 00 à 15 h 12 sur la machine 10 ; aucune somme de contrôle
fausse ; 21 processus refaits pour vol de temps au-dessus de 2 %, un seul gardé au-dessus du seuil (`d_ref`, K4 naturel,
6,2 %). **Incident** : j'ai compilé et lancé une sonde (`probes/d`, une dizaine de secondes) pendant la première passe,
de 15:02:36 à 15:02:46 environ. Avant de regarder les résultats, j'ai fixé la règle d'écarter les processus dont la
durée recoupe cette fenêtre (à une seconde près) : 8 processus de la première passe sont écartés
(`analysis/d_check.py`). Rapports et scénarios : `results/report_d.md`, `results/d_check.json` ; données :
`results/raw_d/`.

### 4.1 Mesures appariées (machine 10, même hôte)

| Clé | Forme | Rapport (IC 95 %) | Remarque |
|---|---|---|---|
| Q1 tuned | une passe en `core.simd` (`d_fix` / `d_ref`) | 0,438 (0,420–0,467) : 72,6 → 31,8 ms | 84 → 22 ms |
| Q1 `mt` | idem | 0,458 (0,389–0,526) : 23,7 → 10,9 ms | 42 → 12 ms |
| 7 témoins (Q1 naturel, Q6, K9, K5, K1 aos…) | code inchangé | 0,96 à 1,05 | |
| Q6 tuned / `mt`, K4 sans branchement | préférence 512 bits (`d_512` / `d_fix`) | 0,84 / 0,80 / 0,62 | |
| Q1 tuned, K1 aos | préférence 512 bits | 1,03 / 1,03 (déjà en vecteurs explicites) | +26 % sur sa forme |
| K9 naturel | `double[M][]` (`d_nat` / `d_ref`) | 0,676 (0,643–0,715) : 36,4 → 24,6 ms | 35,5 → 24,5 ms |
| 26 clés | LLVM 22.1.8 / 21.1.8 (`d_l22` / `d_ref`) | 1,01 en moyenne ; de 0,77 (K1 naturel) à 1,31 (K1 permuté) | |
| K8 naturel | `--DRT-gcopt=fork:1` | pause max 82 → 33 ms ; p99,9 0,90 → 1,79 ms ; temps × 1,15 | 10–18 ms |

### 4.2 Report sur les données principales et classement

Q1 tuned : transfert 47,1 ms, pont par le C du même hôte 35,7 ms, écart 32 % : la règle retient le pont (×0,332), comme
le prévoit le plan ; Q1 `mt` : transfert (×0,458, écart 16 %). Le pont est plausible ici : la forme corrigée reprend
l'algorithme du C témoin (1,11 fois son temps sur l'hôte), alors que l'ancienne forme, par blocs, ralentit bien plus que
le C entre l'hôte et les données principales (× 1,48 contre × 1,12) ; je n'en ai pas cherché la cause. Pour K9
naturel (S-nat), le pont se trompe, comme pour Chapel : le C de ce stencil va 2,6 fois plus vite sur cet Emerald Rapids
que sur le Cascade Lake des données principales, et le pont prédit un stencil rectangulaire plus lent que l'original
(×1,15) quand la mesure appariée donne ×0,68. J'ajoute donc, **après avoir vu ces chiffres** (écart au plan), S-nat-T
et S-tout-T, par transfert seul.

| Scénario | Score de D | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % |
|---|---|---|---|---|---|---|---|
| Avant (publié avant la remarque, refait par le même code) | 71,0 | 87,1 | 74,7 | 42,5 | 8,43 | 9 | 3–12 |
| D-E : errata E3, E4 (v1) | 71,0 | 87,1 | 74,7 | 42,5 | 8,28 | 9 | 3–12 |
| D-Q1 / D-Q1-T : Q1 corrigé | 72,6 / 72,4 | 87,1 | 78,8 / 78,1 | 42,5 | 7,45 / 7,62 | 8 / 9 | 3–12 |
| **D-EQ, publié** (D-EQ-T) | **72,6** (72,4) | 87,1 | **78,8** (78,1) | 42,5 | **7,29** (7,46) | **8** (8) | 3–12 |
| S-512 : préférence 512 bits | 73,3 | 87,1 | 80,7 | 42,2 | 6,22 | 6 | 2–12 |
| S-nat (pont) / S-nat-T (transfert) : K9 naturel en `double[M][]` | 72,6 / 72,8 | 87,1 | 78,8 | 42,3 / 43,0 | 7,37 / 7,01 | 8 / 7 | 3–12 |
| S-tout / S-tout-T | 73,3 / 73,4 | 87,1 | 80,7 | 42,0 / 42,7 | 6,31 / 5,95 | 6 / 5 | 2–12 |
| S-L22 (information) : LLVM 22.1.8 | 71,3 | 87,1 | 77,2 | 39,5 | 8,24 | 9 | 3–13 |

* **Publié** : D passe de 71,0 à 72,6 points (3e score du classement, derrière C et C++) et de la 9e à la 8e place
  (rang espéré 7,29). Il devance Ada dans 53 % des variantes, Rust dans 51 %, Nim dans 50 %, et reste derrière Zig dans
  64 % : D, Ada, Nim et Rust forment un groupe sans ordre établi. Le plafond de K6 passe de 0,515 à 0,784. Les errata
  E3 et E4 ne changent pas le score ponctuel (règle v2), mais gagnent 0,15 de rang espéré.
* **S-512** : avec la préférence 512 bits, K4 sans branchement passe sous le meilleur temps de K4 des autres langages
  (rapport 0,62) : D devient la référence de K4, et les autres langages y perdent ; d'où la 6e place.
* **S-L22** : le paquet officiel (LLVM 22.1.8) ne fait pas mieux (1,01 en moyenne) ; il ralentit surtout K1 permuté
  (×1,31), ce qui coûte 1,4 point. La chaîne du classement reste celle du 28 octobre.
* **La remarque estimait** 72,9 points et la 7e place (6,84) avec Q1 corrigé, la 6e (6,70) avec les errata, et 73,1
  avec le stencil en `double[M][]` ; mes calculs donnent 72,6 et la 8e place (7,29), et 72,8 et la 7e place (7,01)
  avec le stencil.

### 4.3 Verdicts

* **(1) Q1** : exact, et c'était une erreur de mon implémentation au sens de la règle commune (écart à la convention de
  sa classe de langages) : corrigée dans le classement publié. Gain mesuré proche de celui de la remarque (×0,44).
* **(2) Stencil** : exact. La cause écrite dans le README était fausse pour D (aliasing sans métadonnées TBAA, pas
  vérifications de bornes) : corrigée. Le code naturel ne change pas ; en `double[M][]`, forme que la spécification
  de D recommande pour le calcul (`results/d_check/spec_arrays.txt`), D gagnerait une place (S-nat-T, par
  transfert).
* **(3) E3 et E4** : exacts, errata en règle v1 ; ils n'étaient faux que dans la v1.
* **(4) Mineurs** : 512 bits exact (sensibilité, +0,7 point et deux places, en partie parce que D devient la référence
  de K4) ; LLVM : `build.sh` est juste pour ma chaîne, compilée depuis les sources contre LLVM 21.1.8, et les paquets
  officiels embarquent bien LLVM 22.1.8 (sans gain mesuré) ; A3 : texte précisé ; D3 : inchangé.
* **Ce qui est justifié** (GC, K7) : exact. Avec `fork:1`, la pause maximale de K8 tombe à 33 ms ici (la remarque disait
  10–18 ms), au prix de 15 % de temps ; hors défaut.
* **Effet** : D passe de la 9e à la 8e place (72,6 points). La remarque estimait 6e–7e ; l'écart vient des errata,
  qui ne changent pas le score ponctuel (la règle v2 les comptait déjà), et de Q1 : la forme corrigée reste à 1,11 fois
  le C sur l'hôte, quand la remarque la mesurait plus rapide que lui (22,4 contre 23,2 ms). Le transfert seul donne
  aussi la 8e place.
