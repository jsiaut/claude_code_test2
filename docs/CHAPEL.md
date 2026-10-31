# Remarque sur Chapel : trois cases sous-notées, des leviers locaux instables, et une confrontation inéquitable

Remarque transmise par l'utilisateur le 31 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).
L'auteur de la remarque a réécrit et mesuré ses propres noyaux sur un Cascade Lake à 2 vCPU, avec LLVM 18 ; je n'ai
pas son archive (`sondes_chapel_2.10.zip`). Toutes les vérifications ci-dessous sont les miennes : Chapel 2.10.0
(LLVM 22), sources dans `/opt/src/chapel`, machine 8.

## 1. Ce que dit la remarque

* **Ce qui est juste** : la place de Chapel en bas des 13 premiers se défend ; pas de types SIMD portables, ni
  `packed`, ni champs de bits, ni SoA, ni constante de ligne de cache ; ni `pause` (`_mm_pause` ne se lie pas), ni
  indication de branchement, ni `mmap` ; pas d'intent de réduction dans `foreach` ; tuples vectorisés par paires ; le
  retard sur K8 vient de LLVM face à GCC ; beaucoup de leviers existent mais sont instables.
* **(1) Quatre erreurs de la grille, toutes au détriment de Chapel** : B2 (0 → 0,5 : module standard `Allocators`,
  expérimental) ; C2 (0 → 0,5 : `require "immintrin.h"` et `extern proc`, sans macros à immédiat ni builtins) ; E5
  (0 → 0,5 : `foreach` produit `llvm.loop.parallel_accesses`, `!noalias` entre tableaux distincts) ; C4 reste à 0,5
  mais sa justification est fausse (`@llvm.metadata(("llvm.loop.vectorize.enable", true))` réassocie une seule boucle :
  K5 162 → 6,5 ms ; K1 SoA 9,9 → 5,2 ms), et avec elle les trois binaires du banc et les « options de compilation
  globales » du README. B3 (« tableaux toujours sur le tas ») est un jugement, mais `c_array`, stable, est sur la pile
  (44 contre 178 ns par appel).
* **(2) Le plafond** : sans intrinsèques, Q1 tuned s'en est privé ; avec AVX-512 importé, 46 → 23 ms (C : 20,6 ms).
* **(3) La confrontation** : le « produit scalaire 23 fois plus lent » sans `--no-ieee-float` vient du banc ; C, Ada
  et Fortran y ont été réécrits en sommes partielles, Chapel seulement recompilé ; en sommes partielles dans un
  `c_array`, K5 fait 10,5 ms au lieu de 162. K7 naturel (mineur) : `ref e = m[k]`, une recherche, 1,21 s contre 1,84.
* **Ce qui relève du cadre** : contrôle jugé à 35 % ; ce qui distingue Chapel (distribution, GPU) compte pour 2 cases
  sur 34 et n'est pas mesuré ; code naturel forcé en série.
* Effet estimé (ponctuel) : 64,1 (11e) ; 65,9 avec B2, C2, E5 ; 66,6 (10e) avec B3 à 1 ; 66,7 (10e) avec Q1 en
  intrinsèques ; 68,5 au plus.

## 2. Vérifications faites avant ce plan (machine 8)

**Machine 8.** Le conteneur a redémarré le 31 octobre à 9 h 47 sur un hôte Emerald Rapids du même modèle que la
machine 3 (modèle 207, révision 2, 4 vCPU ; latence à 4 Mio 57 ns contre 56 ; DRAM 13,9 Go/s : `results/hw/machine8/`).
Le runtime de Chapel installé n'accepte que `CHPL_TARGET_CPU=native` : je ne peux pas reproduire ici les binaires
Cascade Lake de la campagne. Le source de la campagne est donc recompilé pour l'hôte par le script du banc
(`bench/chapel_ref`), et chaque copie est comparée à lui sur le même hôte.

Sondes : `tools/chapel_check/`, `results/chapel_check/probes.txt` et `ir.txt` ; sonde des errata :
`probes/chapel/probe_errata.chpl` (aucune divergence avec la matrice corrigée, 175 lignes de sonde).

* **B2** : `Allocators` est un module standard (`modules/standard/Allocators.chpl`), marqué `@unstable("experimental")`,
  depuis la 2.2 : `bumpPtrMemPool` et `newWithAllocator` fonctionnent. Go, D et Rust reçoivent 0,5 pour un allocateur
  expérimental ou instable. **Erratum : 0,5.**
* **C2** : `extern proc _mm512_fmadd_ps(...)` après `require "immintrin.h"` donne le bon résultat, sans C ; mais
  `_mm512_cmp_ps_mask` (macro à immédiat) est refusé (« perhaps it is missing or is a macro? ») et `_mm_pause` ne se
  lie pas. Accès partiel aux intrinsèques. **Erratum : 0,5** (règles v1 et v2 ; Nim, dont l'`importc` passe par le C
  et atteint les macros, reçoit 1 en règle v2).
* **E5** : avec `foreach`, l'IR porte `llvm.loop.parallel_accesses` ; avec ou sans `foreach`, le compilateur pose
  `!noalias` entre deux tableaux distincts. Le seul moyen de l'affirmer, `foreach`, est instable, comme
  `@aliasscope` chez Julia (0,5). **Erratum : 0,5.**
* **C4** : l'attribut de boucle `@llvm.metadata(("llvm.loop.vectorize.enable", true))` (instable) réassocie la
  réduction d'une seule boucle : produit scalaire de K5 164,7 → 6,2 ms, sans option globale. **0,5 inchangé,
  justification corrigée** ; « options de compilation globales » est faux dans le README.
* **B3** : `c_array` (CTypes, stable) est sur la pile : 5,2 ns par appel, contre 63,5 ns pour un tableau Chapel local.
  Les tuples l'étaient déjà ; c'est le cas de Julia (tuples sur la pile, tableaux sur le tas : 0,5). **0,5 inchangé,
  texte corrigé.**
* **(3) La confrontation** : la copie standard de Chapel (`bench/chapel_std`) garde K5 tuned et K1 aos/soa tels quels
  (des réductions simples qui comptent sur `--no-ieee-float`), alors que celles de Nim, d'Ada et de Fortran sont
  réécrites en sommes partielles explicites. C'est une erreur de ma part. En sommes partielles dans un `c_array`
  (32 accumulateurs), sans option ni attribut : 9,4 ms (16 : 13,9 ms ; 64 : 10,0 ms).
* **K7 naturel** : l'indexation d'une `map` ajoute la valeur par défaut quand la clé manque (`Map.chpl`) ; `ref e =
  m[k]` fait donc une seule recherche, là où mon code fait `add` puis `m[k]`.
* **Mesures isolées, indicatives** (`chapel_exp` contre `chapel_ref`) : Q1 tuned 44–45 → 30 ms ; K5 tuned 7,3 → 4,3 ms
  (attribut au lieu de `--no-ieee-float`) ; K1 SoA 6,2 → 5,1 ms ; K7 naturel 1,57 → 0,91 s ; copie standard corrigée :
  K5 tuned 9,9 ms, K1 SoA 5,5 ms.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune aux remarques

Les errata de faits et les erreurs de mon implémentation entrent dans le classement publié ; une optimisation nouvelle
(une meilleure forme) reste une analyse de sensibilité (`docs/FORTRAN.md`, 3.1). La confrontation n'est pas le
classement : l'erreur de sa copie standard est corrigée dans la confrontation.

### 3.2 Errata de la matrice (vérifiés ci-dessus)

| Case | Avant (v1 et v2) | Après (v1 et v2) | Règle du standard |
|---|---|---|---|
| B2 allocateurs | 0 | 0,5 : module `Allocators`, instable | 0,25 |
| C2 intrinsèques | 0 | 0,5 : `extern proc` depuis `immintrin.h`, sans macros à immédiat ni builtins | 0,25 |
| E5 non-aliasing | 0 | 0,5 : `foreach` (instable) ; `noalias` automatique | 0,25 |
| C4 réassociation | 0,5 | 0,5 : justification corrigée (attribut de boucle instable) | 0,25 |
| B3 pile | 0,5 | 0,5 : texte corrigé (`c_array` et tuples sur la pile) | — |

### 3.3 Hors du classement publié

* **Les formes de la remarque** (Q1 tuned en intrinsèques importées, K5 tuned et K1 aos/soa avec l'attribut de boucle
  au lieu du binaire `--no-ieee-float`, K7 naturel en une recherche) : sensibilité (S1).
* **B3 = 1** : jugement que je ne retiens pas (cohérence avec Julia) : sensibilité (S-B3).

### 3.4 Mesures (`tools/measure_chapel.py`, machine 8)

`chapel_ref` et `chapel_exp` sur Q1 tuned et mt, K5 tuned, K1 aos et soa, K7 naturel, plus trois témoins dont le code
ne change pas (K9 tuned, Q6 tuned, K7 tuned) ; `chapel_std2` (copie standard corrigée) sur K5 tuned et K1 aos/soa ;
C par clang (témoin du même hôte) sur les six clés changées. 27 cellules, 7 processus par cellule en 7 passes, ordre
tiré au hasard (graine 20261130 + passe), échauffement de 2.

### 3.5 Analyse (`analysis/chapel_check.py`) et décisions fixées d'avance

* **C-E, classement publié** : les errata de 3.2 ; aucune donnée ne change. L'analyse v3 recalculée doit redonner
  exactement ce scénario. **Avant** : le calcul publié avant la remarque, refait par le même code.
* **S1** : C-E, plus les rapports `chapel_exp`/`chapel_ref`, reportés par transfert ou par le pont du C de clang
  quand le transfert s'en écarte de plus de 25 % (règle de `analysis/transfer_check.py`). Le rapport de K5 est
  transféré comme les autres : les données principales de K5 viennent de la machine 3, un Emerald Rapids comme
  l'hôte. **S-B3** et **S1-B3** : avec B3 = 1.
* **Confrontation** : scénario C (règle du standard sur les données) recalculé deux fois dans l'état actuel du
  classement, avec les rapports d'origine de la copie standard, puis avec ceux de la copie corrigée pour K5 tuned et
  K1 aos/soa (`chapel_std2`/`chapel_ref`). `docs/CONFRONTATION.md` et le README citent l'écart.
* **README** : le paragraphe de Chapel ne parle plus d'« options de compilation globales » ; il dit des leviers
  locaux instables (attribut de boucle, `Allocators`, `foreach`) et des intrinsèques limitées aux fonctions inline
  d'`immintrin.h`.

## 4. Résultats

189 processus (27 cellules, 7 passes, échauffement de 2), le 31 octobre de 10 h 10 à 10 h 15 sur la machine 8 ;
aucune somme de contrôle fausse ; 8 processus refaits pour vol de temps au-dessus de 2 % (aucun gardé au-dessus du
seuil). Temps, rapports et scénarios : `results/report_chapel.md` et `results/chapel_check.json` ; données :
`results/raw_chapel/`.

### 4.1 Mesures appariées (machine 8, même hôte)

| Clé | Chapel (campagne) | Formes de la remarque | Rapport (IC 95 %) | C par clang |
|---|---|---|---|---|
| Q1 tuned (intrinsèques importées) | 37,3 ms | 31,1 ms | 0,835 (0,772–0,904) | 30,5 ms |
| Q1 mt | 11,3 ms | 9,8 ms | 0,865 (0,721–1,063) | 8,7 ms |
| K5 tuned (attribut au lieu de `--no-ieee-float`) | 5,05 ms | 5,56 ms | 1,078 (0,930–1,267) | 5,26 ms |
| K1 aos (attribut) | 25,0 ms | 23,5 ms | 0,960 (0,838–1,125) | 32,4 ms |
| K1 soa (attribut) | 5,11 ms | 5,10 ms | 0,997 (0,947–1,054) | 5,22 ms |
| K7 naturel (`ref e = m[k]`) | 1 785 ms | 1 008 ms | 0,565 (0,517–0,617) | 556 ms |
| 3 témoins (K9 tuned, Q6 tuned, K7 tuned) | | | de 0,90 à 1,06 | |

Copie standard corrigée de la confrontation (`chapel_std2`/`chapel_ref`, sommes partielles sans option ni attribut) :
K5 tuned 1,772 (1,522–2,064), K1 aos 1,318 (1,191–1,470), K1 soa 1,047 (0,941–1,193).

* **L'attribut de boucle vaut l'option globale** (K5 1,08, K1 0,96 et 1,00) : un seul binaire aurait suffi, et les
  « options de compilation globales » du README étaient une erreur de fait.
* **Q1 en intrinsèques importées** : −16 % sur cet hôte, au niveau du C (31,1 contre 30,5 ms) ; la remarque mesurait
  −50 % sur Cascade Lake (46 → 23 ms).
* **K7 naturel en une recherche** : −43 %.

### 4.2 Report sur les données principales et classement

Le pont par le C (règle de `analysis/transfer_check.py`) est retenu pour Q1 mt (écart de 29 %), K1 aos (74 %) et K7
naturel (−80 %). Pour K7 naturel, il donne un non-sens : un rapport de 2,8, quand la nouvelle forme divise le temps par
1,8 sur l'hôte même. Les données principales de ces clés viennent de Cascade Lake, et l'hôte est un Emerald Rapids au
L3 immense : la table chaînée du C de K7 naturel y va dix fois plus vite que dans les données principales, Chapel non.
Le pont suppose que le facteur d'hôte est le même pour les deux, ce qui est faux ici. J'ajoute donc, **après avoir vu
ces chiffres** (écart au plan), le scénario S1-T, où les rapports sont transférés sans pont ; S1 reste publié tel que le
plan le prévoyait.

| Scénario | Score | Contrôle C | Plafond E | Rang espéré | Place | Rang 90 % |
|---|---|---|---|---|---|---|
| Avant (publié avant la remarque, refait par le même code) | 64,1 | 56,6 | 80,2 | 9,94 | 11 | 5–13 |
| **C-E, publié** : errata B2, C2, E5 | **65,9** | **61,8** | 80,2 | **9,03** | **10** | 4–13 |
| S-B3 : B3 = 1 | 66,6 | 63,8 | 80,2 | 8,60 | 10 | 4–12 |
| S1 (plan) : formes de la remarque, ponts compris | 65,9 | 61,8 | 80,9 | 9,39 | 10 | 5–13 |
| S1-B3 | 66,6 | 63,8 | 80,9 | 8,99 | 10 | 4–12 |
| S1-T (écart au plan) : formes de la remarque, transferts seuls | 66,1 | 61,8 | 80,3 | 8,62 | 10 | 4–13 |

* **Publié** : les errata rapportent 1,8 point (le contrôle passe de 56,6 à 61,8). Chapel passe 10e : il reste derrière
  Fortran au score (65,9 contre 66,3), mais le devance dans 60 % des variantes ; D le devance dans 54 %.
* **Sensibilité** : les formes de la remarque et B3 = 1 n'y ajoutent qu'entre 0 et 0,7 point ; Chapel reste 10e dans
  tous les scénarios.
* **La remarque estimait** 65,9 points avec B2, C2 et E5 (exactement mon calcul), 11e au score : en rang espéré, c'est
  la 10e place. Elle estimait 66,6 avec B3 à 1 (identique) et 66,7 avec Q1 en intrinsèques.

### 4.3 Confrontation corrigée

Scénario C de la confrontation (règle du standard appliquée aux données), recalculé dans l'état actuel du classement :

| Copie standard de Chapel | K5 tuned / K1 aos / K1 soa | Plafond E | Score | Place sur 18 |
|---|---|---|---|---|
| D'origine (recompilée sans `--no-ieee-float`) | ×23,0 / ×0,98 / ×1,69 | 49,3 | 53,5 | 11 |
| Corrigée (meilleure forme standard par clé) | ×1,77 / ×0,98 / ×1,05 | 72,1 | 62,7 | 10 |

Une variante standard est le meilleur code que la règle admet : pour K1 aos, la boucle d'origine sans option (×0,98)
bat ma réécriture en sommes partielles (×1,32), et je la garde ; pour K5 et K1 soa, les sommes partielles l'emportent.
J'ai précisé ce choix clé par clé après avoir vu K1 aos (le plan prévoyait les trois rapports de la copie corrigée) ;
il ne change pas le résultat, parce que le plafond de K1 se joue sur soa. La règle du standard coûte donc 8 points de
plafond à Chapel (80,2 → 72,1), pas 31. `docs/CONFRONTATION.md` et le README sont corrigés.

### 4.4 Verdicts

* **(1) La grille** : B2, C2 et E5 exacts (0,5 chacun) ; la justification de C4 était fausse (corrigée, note
  inchangée) ; B3 : texte corrigé, note gardée (cohérence avec Julia ; 1 en sensibilité).
* **(2) Q1 en intrinsèques** : confirmé, moins fort sur cet hôte (−16 %) ; sensibilité, comme l'attribut de boucle et
  K7 naturel en une recherche (−43 %).
* **(3) La confrontation** : exact, et c'était mon erreur ; corrigée.
* **Ce qui relève du cadre** (contrôle jugé à 35 %, distribution et GPU non mesurés, code naturel en série) : juste ;
  le README le dit désormais pour Chapel.
* **Effet** : Chapel passe de la 11e à la 10e place, comme la remarque l'estimait.
