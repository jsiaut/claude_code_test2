# Remarque sur C# : une 14e place juste, mais une marge plus mince qu'annoncé

Remarque transmise par l'utilisateur le 31 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).
L'auteur de la remarque n'a pas pu compiler le C# du dépôt : il a réécrit les noyaux à partir de `docs/SPEC.md` et
mesuré 448 processus sur un Emerald Rapids. Je n'ai pas ses sources. Toutes les vérifications ci-dessous sont les
miennes, sur le binaire de la campagne et sur des copies du banc, machine 9.

## 1. Ce que dit la remarque

* **Verdict** : la 14e place découle honnêtement des règles ; la marge est plus mince qu'elle n'en a l'air (environ
  8 points derrière Mojo, dont 5 à 6 récupérables, C# restant 14e).
* **Exact selon elle** : .NET 10.0.14 est la dernière version stable (SDK 10.0.403), .NET 11 en est à la RC3 ; le JIT
  n'a pas de vectoriseur de boucles, .NET 11 compris (une expérience, PR 127853, a été fermée sans fusion) ; K4 naturel
  (environ 80 ms) vient du refus de l'if-conversion dans les boucles (l'expérience qui lève ce garde-fou, PR 127032,
  ne vise qu'ARM64) ; 88 octets par particule et parcours permuté 4,7 fois plus lent ; sur Cascade Lake,
  `Vector512.IsHardwareAccelerated` vaut `false` mais `Vector512` utilise l'AVX-512 ; les cases de la matrice se
  défendent, sauf E7 (0,5 comme Go, alors que Go ne monomorphise pas et que C# spécialise les types valeur et a des
  générateurs de source : +0,2 point) ; C# 14 et 15 ne changent rien (les unions de C# 15 sont des unions de types).
* **Le protocole ne pénaliserait pas le JIT** : 3 échauffements et au plus 13 appels, donc jamais le niveau 1 (30
  appels) ; les noyaux tournent en code OSR, mais l'effet est négligeable sur 16 noyaux : régime établi / protocole
  0,99 (IC 90 % 0,96–1,03) ; optimisation complète d'emblée 0,97 ; .NET 11 / .NET 10 0,99.
* **Formes moins optimisées que le C** (pas des erreurs au sens de la règle commune) : K8 tuned (arène récursive ;
  pile explicite ×0,31 en C#, ×0,32 en C par clang, ×0,50 en C par GCC) ; Q1 tuned (30 accumulateurs dans des `Span`
  de `stackalloc` ; en registres ×0,70, reformulé ×0,52) ; K4 sans branchement (déroulé par 4 ×0,68 ; .NET 11 seul
  ×0,64 à 0,71) ; K6 et K9 `mt` (`new Thread` environ 90 µs, contre 31 µs pour `pthread_create` et 4 à 8 µs pour
  `Parallel.For`).
* **Ce qui tient aux règles** : K4 n'admet que des formes scalaires (en SIMD explicite, C# fait 0,6 à 0,8 ms : 5,5
  points) ; K1 naturel en `sealed class` (en `struct`, D2 passe de 0,39 à 0,99 : +2,3 points) ; K6 naturel en champs
  statiques (en paramètres, Q6 2,4 à 2,6 fois plus rapide : +0,1 point) ; `TensorPrimitives` exclu.
* **Sensibilité estimée** : 54,8 publié ; 57,9 avec les meilleures formes ; 60,5 avec en plus K1 en `struct`, K6 en
  paramètres et E7 à 1 (Mojo : 62,7) ; 61,0 avec Q1 reformulé ; 60,3 avec K4 en SIMD admis pour C# seul. La phrase
  « les 13 premiers devancent C# dans au moins 98 % des variantes » ignore l'effort d'implémentation et le choix du
  code naturel : l'écart serait d'environ 2 points, pas 8.

## 2. Vérifications faites avant ce plan (machine 9)

**Machine 9.** La VM a redémarré le 31 octobre à 12 h 08 sur un hôte Emerald Rapids du même modèle que les machines 3
et 8 (modèle 207, révision 2, 4 vCPU ; latence à 4 Mio 61 ns, DRAM 13,5 Go/s : `results/hw/machine9/`). Preuves :
`results/csharp_check/` (script `tools/csharp_check/collect.sh`, sondes dans `tools/csharp_check/`).

* **Score** : 54,77 dans `results/summary_v3.json` (C 68,75 ; E 56,20 ; D 32,90), Mojo 62,71 : écart de 7,9 points.
  **Exact.**
* **Binaire et données** : le binaire de la campagne correspond au source actuel (recompilé sur place avec le même
  identifiant de révision, il ne diffère que par l'horodatage, le MVID et les identifiants PDB, 71 octets) ; les 24
  fichiers de données régénérés par `tools/gendata.c` sont identiques à ceux de `/opt/msdata`
  (`results/msdata_sha256.txt`).
* **Versions** (`results/csharp_check/releases.txt`, index officiel lu le 31/10) : 10.0.14 (25/10) est la dernière
  version stable (LTS, SDK 10.0.403, celle du dépôt) ; 11.0.0-rc.3 (25/10) est une préversion. **Exact.** SDK 11.0.100-rc.3
  installé dans `/opt/dotnet11` (SHA-512 vérifié) pour les vérifications et une mesure d'information.
* **Pas de vectoriseur** (`k4_disasm.txt`) : K4 sans branchement reste scalaire en .NET 10 (OSR, niveau 1 avec PGO
  dynamique, FullOpts : la même boucle de 46 octets) et en .NET 11 RC3 (43 octets : un `movsxd` de moins). Dans les
  sources du JIT (`dotnet/runtime`, branche principale du 31/10), aucune phase de vectorisation ; les commits de la PR
  127853 (« auto vectorizer », mai 2026) n'y sont pas. **Exact** (je vérifie l'absence de fusion, pas la fermeture).
* **If-conversion** (`jit_sources.txt`) : `ifconversion.cpp` refuse de convertir un bloc situé dans une boucle
  (« Loop-carried dependencies can cause significant stalls ») ; la PR 127032 (« tune branchless heuristics more
  aggressively for ARM64 ») lève ce garde-fou sous `#ifndef TARGET_ARM64` seulement, et la branche principale le
  garde pour toutes les cibles. K4 naturel garde son branchement (`cmp`/`jl`, 73 à 83 ms ici ; 83 ms dans les données
  principales). **Exact.**
* **K1** : 88 octets par particule (`results/footprint.json`, et 88,0 remesuré ici) ; permutation 4,70 fois plus lente
  (259,2 contre 55,1 ms dans les données principales). **Exact.**
* **AVX-512 sur Cascade Lake** (`avx512.txt`) : `codeman.cpp` fixe la largeur préférée à 256 bits sur les modèles 0x55
  (Skylake serveur, Cascade Lake, Cooper Lake). Avec cette largeur imposée ici, `Vector512.IsHardwareAccelerated` vaut
  `False`, `Avx512F.IsSupported` `True`, et K1 SoA garde ses instructions zmm ; le banc ne teste jamais
  `IsHardwareAccelerated`. **Exact.**
* **E7** (`generics.txt`) : en C#, `Apply<T>` sur un `struct` est spécialisé (l'appel contraint devient un `lea`),
  sur une classe il est partagé (appel d'interface). Go 1.27 produit une copie par forme GC (`Sum[go.shape.int]`,
  `Sum[go.shape.float64]`) : « Go ne monomorphise pas » est inexact, mais l'appel de méthode y passe par le
  dictionnaire (`CALL SI`), même pour un `struct`. La spécialisation de C# est donc plus forte que celle de Go.
  Dans la matrice, 1 suppose aussi l'évaluation à la compilation dans le langage : Odin, monomorphisé sans exécution à
  la compilation, a 0,5 ; Haskell (Template Haskell, spécialisation non garantie) aussi. C# n'a que des expressions
  constantes ; les générateurs de source sont des greffons du compilateur (assemblage séparé, API Roslyn), et le SDK
  livre les siens (expressions régulières, JSON, `LibraryImport`). **Jugement** : je garde 0,5, texte précisé ; E7 = 1
  en sensibilité.
* **C# 14 et 15** (`union15.txt`) : une union de C# 15 entre deux `struct` de 4 et 8 octets est un `struct` de 8
  octets qui contient un seul champ `object` : les cas sont mis en boîte, sans recouvrement mémoire (A5 vaut déjà 1
  par `FieldOffset`). **Exact.**
* **Protocole** (`tiers.txt`) : 3 échauffements et 3 à 10 répétitions, soit au plus 13 appels. **Exact.** Avec ce
  protocole, les méthodes chaudes de K1, K2, K3, K4, K6 et K9 tournent en code OSR, K5 tuned en niveau 0 instrumenté
  (d'où les 20,6 ms de la campagne, remplacées dans les données principales par la remesure v2 à 10 échauffements,
  4,3 ms), et Q1 tuned (qui contient un `stackalloc`) passe directement en FullOpts. Avec 120 échauffements, toutes
  atteignent le niveau 1 sauf parfois K1 SoA ; la boucle de K7 est dans `RunK7`, appelée une fois, donc toujours en OSR.
* **Formes de la remarque, mesures isolées et indicatives** :
  * **Q1 en variables locales** (`q1_tiers.txt`) : avec le protocole du dépôt, la compilation OSR de cette forme se
    replie en MinOpts (« compiling with minopt ») : 131 ms contre 42 ms ; en FullOpts, 31,9 contre 31,1 ms, sans gain.
    Sur cet hôte, Q1 tuned varie de 32 à 47 ms d'un processus à l'autre.
  * **K8 en pile explicite** : C# 240 → 123 ms (×0,51) ; C par clang 217 → 227 ms ; C par GCC 133 → 94 ms (×0,71).
  * **K4 sans branchement déroulé par 4** : 15 → 12 ms (OSR, vérification de bornes conservée) ; **K4 en SIMD
    explicite** : 0,86 ms.
  * **K6 naturel, colonnes en paramètres** : Q6 119 → 54 ms, Q1 82 → 74 ms ; **K1 naturel en `struct`** : 35 → 31 ms,
    permuté 128 → 30 ms, 64,0 octets par particule.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune aux remarques

Les errata de faits et les erreurs de mon implémentation entrent dans le classement publié ; une optimisation nouvelle
(une meilleure forme), un autre choix de code naturel ou un autre protocole restent des analyses de sensibilité
(`docs/FORTRAN.md`, 3.1 ; `docs/ADA.md`, décision 3 pour le code naturel ; `docs/ZIG.md`, décision 3 pour les threads
lancés à chaque passe et la version de la chaîne).

### 3.2 Ce qui entre dans le classement publié

* **Rien, en l'état de la section 2** : aucun fait de la remarque n'est faux dans le dépôt ; E7 est un jugement
  (gardé à 0,5, texte précisé) ; aucune erreur d'implémentation : chaque noyau fait ce qu'il annonce, ce que la
  remarque dit aussi. Si les mesures révélaient un noyau qui ne fait pas ce qu'il annonce, sa correction entrerait dans
  le classement publié, et je le signalerais comme un écart au plan.
* **Hors du classement** : .NET 11 (préversion à la date de la campagne, même règle que Zig 0.18) ; les formes de la
  remarque ; les threads du pool ; K1 en `struct` et K6 en paramètres ; un autre protocole ; K4 en SIMD explicite (la
  spécification ne l'admet pour aucun langage).

### 3.3 Mesures (`tools/measure_csharp.py`, machine 9)

144 cellules × 7 processus (1 008), en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard
(graine 20261231). Répétitions de `results/calib.json` ; échauffements des données principales (C# : 3, et 10 pour
K5 comme la remesure v2 ; C : 1, et 2 pour K5). Sortie : `results/raw_csharp/`.

* `csharp` (binaire de la campagne, protocole P0) : les 26 clés du score (E, D1, D2 et D4).
* `csharp_full` : même binaire, compilation à niveaux désactivée (P1 : FullOpts dès le premier appel), 26 clés.
* `csharp_steady` : même binaire, 120 échauffements (P2 : niveau 1 avec PGO dynamique), 16 clés (celles dont la méthode
  chaude atteint le niveau 1 : section 2).
* `csharp_net11` : même binaire, runtime .NET 11 RC3, P0, 26 clés.
* `csharp_exp` (P0) et `csharp_exp_full` (P1) : formes de la remarque (K4 sans branchement déroulé par 4, Q1 en
  variables locales, K8 en pile explicite ; P0 : 12 cellules dont `k4 simd_unsorted`, `mt_pool` pour Q6, Q1 et K9, et
  deux témoins ; P1 : les 4 clés changées).
* `csharp_nat2` (P0) : K1 naturel en `struct` dans `List<T>` (naturel et permuté), K6 naturel en paramètres (Q6, Q1),
  K1 aos en témoin ; puis empreinte de K1 (3 processus, méthode de `analysis/footprint.py`), comme pour `csharp`.
* `c` (clang, binaire de la campagne) : témoin du même hôte sur les 26 clés ; `c_exp` (clang), `c_gcc` et `c_gcc_exp`
  (GCC) : K8 tuned récursif et en pile explicite.

### 3.4 Analyse (`analysis/csharp_check.py`) et décisions fixées d'avance

Rapports appariés r = moyenne géométrique des médianes par processus, nouveau / ancien, même hôte (IC 95 % par
bootstrap). Report sur les données principales : pour les scénarios qui changent le code (S1, S-pool, S-nat), règle de
`analysis/transfer_check.py` (pont par le C du même hôte si transfert et pont s'écartent de plus de 25 %), et, publiée
à côté, la version par transfert seul (suffixe -T), puisque le pont peut se tromper entre Cascade Lake et Emerald Rapids
(`docs/CHAPEL.md`, 4.2) ; pour les scénarios de protocole et de version (même code), transfert seul. Un développeur
garde la meilleure de deux formes : pour chaque clé changée, le rapport retenu est min(1, r). Latences de K8 (D3) et
pilier C inchangés, sauf mention.

| Scénario | Ce qui change pour C# |
|---|---|
| Publié | rien (doit redonner 54,77 et la 14e place) |
| S-E7 | E7 = 1 |
| S-P1 | 26 clés × r(csharp_full / csharp) |
| S-P2 | 16 clés × r(csharp_steady / csharp) |
| S-N11 (information) | 26 clés × r(csharp_net11 / csharp) |
| S1, S1-T | K4 sans branchement, Q1 tuned, Q1 mt, K8 tuned × min(1, r(csharp_exp / csharp)) |
| S1-R | S1-T, et le K8 tuned des autres langages classés × r(c_gcc_exp / c_gcc) si < 1 (la meilleure référence de K8 vient d'Ada, compilé par GCC) |
| S1-P1 | clés de S1 × min(1, r_full, r_exp, r_exp_full) ; 22 autres clés × r_full |
| S-pool, S-pool-T | K6 mt (Q6, Q1) et K9 mt × min(1, r(mt_pool / mt)), rapports pris dans `csharp_exp` |
| S-nat, S-nat-T | K1 naturel et permuté × r(csharp_nat2 / csharp), empreinte mesurée de `csharp_nat2` ; K6 naturel Q6 et Q1 × r |
| S-K1, S-K6 (T) | les deux moitiés de S-nat, séparément |
| S-max, S-max-T | S1-P1 + S-pool + S-nat + E7 = 1 : le plus favorable à C# |
| S-K4 | K4 retiré du plafond E pour tous les langages (comme pour Mojo) |
| S-K4simd (unilatéral) | K4 sans branchement de C# remplacé par son SIMD explicite, les autres langages inchangés |

Décisions :
1. **Classement publié inchangé** sauf erreur établie (3.2).
2. **Le README est précisé** : la phrase sur les 98 % des variantes dira que les variantes de l'analyse ne font varier
   ni l'effort d'implémentation ni le choix du code naturel, avec l'écart de S-max ; le paragraphe de C# et
   `docs/FINDINGS.md` reçoivent ce qui est établi (protocole, formes, K1 en `struct`).
3. **Le protocole reste commun aux langages à JIT** (Java, JavaScript, Julia, LuaJIT) : un effet mesuré sur C# est
   publié comme limite de l'étude, pas corrigé pour C# seul.
4. **.NET 11** est une information (préversion), comme Zig 0.18.

## 4. Résultats

1 008 processus (144 cellules × 7 passes) et 6 mesures d'empreinte, le 31 octobre de 12 h 47 à 13 h 24 sur la machine
9 ; aucune somme de contrôle fausse ; 22 processus refaits pour vol de temps au-dessus de 2 %, un seul gardé au-dessus
du seuil (K4 en SIMD explicite, 3,5 %, hors classement). Témoins de disposition : 0,985, 0,975 et 1,001. Temps,
rapports et scénarios : `results/report_csharp.md` et `results/csharp_check.json` ; données : `results/raw_csharp/`.

### 4.1 Protocole et version (même binaire, même hôte)

| Comparaison | Clés | Moyenne géométrique des rapports | IC 90 % | Remarque |
|---|---|---|---|---|
| FullOpts dès le premier appel / protocole (P1/P0) | 26 | 0,998 | 0,976–1,018 | 0,97 |
| 120 échauffements, niveau 1 avec PGO / protocole (P2/P0) | 16 | 0,975 | 0,948–0,999 | 0,99 (0,96–1,03) |
| .NET 11 RC3 / .NET 10, protocole P0 | 26 | 0,990 | 0,966–1,014 | 0,99 |

* **En moyenne, le protocole ne pénalise presque pas C#** : 0 à 2,5 %, soit 0,7 à 0,9 point de score (S-P1, S-P2).
  Clé par clé, l'effet va de 0,85 (K1 SoA en FullOpts, K6 `mt` Q6 en régime établi ; K5 tuned 0,86) à 1,16 (K7
  naturel en FullOpts, c'est-à-dire sans PGO dynamique) ; K4 sans branchement gagne 6 à 10 % hors du code OSR, qui
  garde une vérification de bornes dans la boucle.
* **.NET 11 RC3** : 0,99 en moyenne ; K4 sans branchement 0,81 (IC 0,76–0,85 ; la remarque disait 0,64 à 0,71), dont la
  boucle compte un `movsxd` de moins. Information seulement (préversion).

### 4.2 Formes de la remarque, threads du pool, autres choix de code naturel

| Clé | Forme | Rapport mesuré (IC 95 %) | Remarque |
|---|---|---|---|
| K4 sans branchement | déroulée par 4, protocole P0 | 0,82 (0,77–0,88) | 0,68 |
| | déroulée par 4, FullOpts | 0,72 (0,68–0,76) | |
| Q1 tuned | accumulateurs en variables locales, protocole P0 | 4,05 (3,07–6,02) | 0,70 |
| | la même forme, FullOpts | 0,84 (0,79–0,89) | |
| Q1 `mt` | la même forme, P0 / FullOpts | 2,66 / 0,85 | |
| K8 tuned | pile explicite (C#) | 0,51 (0,47–0,54) | 0,31 |
| | pile explicite, C par clang / par GCC | 0,93 / 0,65 | 0,32 / 0,50 |
| K6 `mt` Q6 / K9 `mt` | threads du pool (`Parallel.For`) | 0,71 / 0,63 | |
| K1 naturel / permuté | `struct` dans `List<T>` (64,0 octets par particule) | 0,83 / 0,23 | |
| K6 naturel Q6 / Q1 | colonnes en paramètres | 0,47 / 0,86 | 0,38 à 0,42 (Q6) |
| K4 | SIMD explicite (`vpsadbw`) : 0,83 ms | 0,053 | 0,6 à 0,8 ms |

* **Le piège de l'OSR** : avec le protocole commun, la forme « en registres » de Q1 est quatre fois plus lente, car sa
  compilation OSR se replie en MinOpts (section 2) ; elle n'est meilleure (0,84) qu'en optimisation complète, ce que
  l'attribut documenté `[MethodImpl(MethodImplOptions.AggressiveOptimization)]` obtient méthode par méthode.
* **K8** : la pile explicite aide C# (0,51) et le C de GCC (0,65), presque pas le C de clang (0,93) : le gain n'est pas
  propre à C#. Mesurée ici, la version itérative de C# (124 ms) égale la version récursive du C de GCC (124 ms).
* **K6 naturel** (désassemblage, FullOpts) : avec les colonnes en champs statiques, le JIT recharge le champ à chaque
  accès et garde deux comparaisons par test de plage ; en paramètres, il fusionne chaque test en une comparaison non
  signée (`sub`, `cmp`, `jbe`). Les vérifications de bornes restent dans les deux formes : la remarque a raison sur la
  fusion, pas sur l'élimination des vérifications.
* **Threads du pool** : pour Q1 `mt`, le gain est noyé par le noyau piégé de la copie (1,10) ; il est retenu à 1.

### 4.3 Report sur les données principales et scénarios

Le pont par le C de clang s'écarte du transfert de plus de 25 % pour K8 tuned (34 %), Q1 tuned, K1 naturel et permuté,
K6 naturel Q1, et Q1 et K9 `mt` du pool (`results/report_csharp.md`) : les deux versions sont publiées, comme prévu. Entre les deux
architectures, le rapport hôte de C# et celui du C diffèrent, ce que `docs/CHAPEL.md` (4.2) avait déjà montré.

| Scénario | Score de C# | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % | Écart avec Mojo | Min. des 13 premiers devant C# |
|---|---|---|---|---|---|---|---|---|
| Publié (refait par le même code) | 54,8 | 56,2 | 32,9 | 14,19 | 14 | 13–16 | 7,9 | 98 % |
| S-E7 : E7 = 1 | 55,0 | 56,2 | 32,9 | 14,17 | 14 | 13–16 | 7,7 | 97 % |
| S-P1 : FullOpts | 55,7 | 58,9 | 32,2 | 14,12 | 14 | 13–16 | 6,6 | 97 % |
| S-P2 : régime établi | 55,4 | 58,0 | 32,7 | 14,12 | 14 | 13–16 | 6,9 | 97 % |
| S-N11 : .NET 11 RC3 (information) | 55,5 | 58,1 | 32,7 | 14,15 | 14 | 13–16 | 7,2 | 97 % |
| S1 / S1-T : formes de la remarque (P0) | 58,3 / 57,4 | 65,0 / 62,7 | 32,9 | 13,89 / 14,00 | 14 | 12–15 / 13–15 | 4,4 / 5,4 | 93 / 95 % |
| S1-R : K8 itératif aussi pour les autres | 56,0 | 59,4 | 32,6 | 14,10 | 14 | 13–15 | 6,7 | 97 % |
| S1-P1 : formes et FullOpts | 58,8 | 66,7 | 32,2 | 13,84 | 14 | 12–15 | 3,5 | 90 % |
| S-pool / S-pool-T | 55,0 / 55,7 | 56,8 / 58,5 | 32,9 | 14,17 / 14,13 | 14 | 13–16 | 7,7 / 7,0 | 97 % |
| S-nat / S-nat-T : K1 en `struct`, K6 en paramètres | 57,1 / 56,7 | 56,2 | 42,2 / 40,7 | 13,88 / 13,93 | 14 | 13–15 | 5,6 / 6,0 | 94 / 95 % |
| S-K1 / S-K6 (transfert) | 56,6 / 54,9 | 56,2 | 40,4 / 33,2 | 13,95 / 14,16 | 14 | 13–15 / 13–16 | 6,1 / 7,9 | 96 / 98 % |
| **S-max / S-max-T** : tout à la fois, E7 = 1 | **62,6 / 62,0** | 70,0 / 69,4 | 41,2 / 39,8 | **12,88 / 13,16** | **14** | 10–14 / 11–14 | **−0,3 / 0,2** | **62 / 70 %** |
| S-K4 : K4 hors du plafond, pour tous | 58,9 | 66,4 | 32,9 | 13,98 | 14 | 13–15 | (Julia, 13e : 3,8) | 92 % |
| S-K4simd (unilatéral) | 60,1 | 69,9 | 32,1 | 12,85 | 14 | 8–15 | −1,3 | 67 % |

* **C# reste 14e dans les 19 scénarios.** Quand C# devient la référence d'un noyau (K1 SoA en FullOpts, K6 naturel en
  paramètres, K4 en SIMD), les autres langages perdent un peu : Mojo passe de 62,7 à 62,3 points dans S-max ; dans
  S-K4simd, tous perdent 4 à 5 points, ce qui rend ce scénario unilatéral.
* **Les gains se décomposent ainsi** : formes de la remarque +2,6 à +3,5 points (+4,0 avec FullOpts, +1,2 seulement si
  les autres langages reçoivent aussi K8 itératif) ; K1 en `struct` +1,9 ; protocole +0,7 à +0,9 ; threads du pool +0,2
  à +0,9 ; E7 +0,25 ; K6 en paramètres +0,1.
* **La remarque estimait** 57,9 avec les meilleures formes (ici 56,0 à 58,8 selon K8 et le protocole), 60,5 à 61,0 avec
  K1 en `struct`, K6 en paramètres et E7 à 1 (ici, avec le protocole et le pool en plus : 62,0 à 62,6), 60,3 avec K4 en
  SIMD pour C# seul (ici 60,1), +2,3 points pour K1 en `struct` (ici +1,9) et +0,1 pour K6 (ici +0,1).

### 4.4 Verdicts

* **Les faits** : tous exacts, sauf un détail : Go monomorphise par forme GC (une copie pour `int`, une pour
  `float64`), mais appelle les méthodes par dictionnaire. Pour les PR de `dotnet/runtime`, je vérifie l'absence de
  fusion, pas la fermeture.
* **E7** : jugement, gardé à 0,5 (texte précisé) ; à 1, +0,25 point.
* **Le protocole** : confirmé, l'effet moyen est faible (0 à 2,5 %, +0,7 à +0,9 point). Mais il a un piège que la
  remarque ne voit pas : une méthode qui garde beaucoup de vecteurs vivants peut perdre l'optimisation en OSR. Le
  protocole reste commun aux langages à JIT (décision 3) ; l'effet est publié comme limite.
* **Les formes** : confirmées en direction, plus faibles qu'annoncé (K4 0,72 à 0,82 ; K8 0,51 ; Q1 0,84 en FullOpts
  seulement) ; ce ne sont pas des erreurs de mon implémentation (le code fait ce qu'il annonce), elles restent des
  sensibilités.
* **La marge** : la remarque a raison sur le fond. Avec tout ce qui est favorable à C# à la fois (S-max), C# rejoint
  Mojo au score (62,0 à 62,6 contre 62,3) et Mojo ne le devance plus que dans 62 à 70 % des variantes, au lieu de 98 % ;
  C# reste 14e en rang espéré. Les autres langages ont aussi leur marge (Julia : `docs/JULIA.md`).
* **Effet sur le classement publié** : aucun, conformément au plan (3.2) ; le README est précisé (décision 2).

Depuis la remesure des queues de latence de K8 pour tous les langages (31 octobre, `docs/RUST.md`), C# a 56,0 points et
reste 14e ; sa queue sur K8 était l'une des plus pénalisées par le vol de temps (p99,9 777 → 180 µs). Rejoués dans cet
état (`analysis/csharp_check.py _current`, sorties `results/csharp_check_current.json` et
`results/report_csharp_current.md`), S-max lui donne 63,8 points et la 13e place, devant Mojo (62,3), qu'il devance
dans 54 % des variantes ; S-max-T 63,2 points et la 14e place, Mojo le devançant dans 54 %.
