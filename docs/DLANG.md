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
