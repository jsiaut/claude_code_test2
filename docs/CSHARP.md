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
