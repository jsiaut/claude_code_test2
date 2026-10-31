# Remarque sur Julia : un plafond plus bas que nécessaire, trois cases de la matrice, et K10 mal diagnostiqué

Remarque transmise par l'utilisateur le 30 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).
L'auteur de la remarque a mesuré ses propres réécritures des noyaux sur un Emerald Rapids à 2 vCPU ; je n'ai pas son
code. Toutes les vérifications ci-dessous sont les miennes : Julia 1.13.3 (dernière version stable, celle du banc),
machine 7.

## 1. Ce que dit la remarque

* **Ce qui est juste** : Julia a sa place dans le groupe de tête, devant C#, Java et Go ; la latence de queue de K8
  vient bien du ramasse-miettes ; plusieurs leviers manquent vraiment (structures compactes, alignement explicite,
  SoA natif, interface d'allocateur) ; son code naturel est le meilleur de l'étude ; `llvm.expect` par `llvmcall` ne
  laisse aucun poids de branchement dans l'IR (E3 = 0 est juste).
* **(1) C'est le plafond qui place Julia 12e, pas son runtime**, contrairement au README : face à Rust, l'écart de
  7,2 points vient pour 5,2 du plafond ; face à Chapel, le plafond coûte 5,4 points quand le contrôle en rapporte 4,1.
* **(2) Les versions tuned de Julia sont en retrait** : Q1 en 6 passes par bloc au lieu d'une passe masquée (65,9 →
  33,3 ms) ; K5 compilé en 256 bits (5,51 → 4,0 ms en 512 bits, par `VecElement` et intrinsèques ou par l'option
  `-C native,-prefer-256-bit`) ; K8 tuned (293 → 148 ms avec la profondeur en paramètre de compilation) ; K7 sans
  préchargement par lots (non vérifié par l'auteur).
* **(3) Trois cases sous-notées** au regard de la règle v2 appliquée aux autres : B2 (0 → 0,5 : `Libc.malloc` et
  `unsafe_wrap`, des arènes à la main comme en C, C#, Nim, Mojo), D3 (0 → 0,5 : `Threads.PaddedSpinLock`, public
  depuis la 1.13, comme Odin), D5 (0,5 → 1 : `pause` par `ccall(..., llvmcall)`, le mécanisme déjà accepté pour C2 et
  E4 chez Julia).
* **(4) Le diagnostic de K10 est faux** : le blocage ne vient pas de l'ordonnanceur coopératif, mais d'une variable
  capturée par la fermeture (`Core.Box`), qui alloue ; une allocation déclenche une collecte, qui attend un point
  d'arrêt que le producteur, en attente active, n'atteint jamais (`jl_gc_wait_for_the_world` sous gdb). Sans capture
  et avec `GC.safepoint()`, K10 tuned passe de 409 à 15 ms.
* Effet estimé (ponctuel) : 62,2 (12e) ; 64,0 avec la matrice ; 66,2 avec Q1 et K5 ; 68,8 (10e) avec K8.

## 2. Vérifications faites avant ce plan (machine 7)

**Machine 7.** Le conteneur a redémarré à 19 h 14 sur un nouvel hôte Cascade Lake du même modèle que les machines 1,
2, 4, 5 et 6 (modèle 85, révision 7, 4 vCPU, 16 Go ; latence à 4 Mio 60 ns, débit DRAM 10 Go/s :
`results/hw/machine7/`). Julia étant compilé à la volée, il n'y a pas de binaire à reconstruire.

Sondes : `probes/julia/probe_errata.jl` (aucune divergence avec la matrice corrigée, 170 lignes de sonde) et
`tools/julia_check/k10_variants.jl`.

* **B2** : `Libc.malloc`, `Libc.free` et `unsafe_wrap` sont publics ; une arène tenue à la main fonctionne. C, Nim et
  Mojo reçoivent 0,5 pour la même chose. **Erratum : 0,5.**
* **D3** : `Threads.PaddedSpinLock` est public depuis la 1.13 (120 octets, « garanti seul sur sa ligne de cache, pour
  éviter le faux partage ») ; Base n'a pas de constante de ligne de cache. Une aide propre aux verrous, comme la
  constante d'Odin, propre aux tables (0,5). **Erratum : 0,5.**
* **D5** : `ccall("llvm.x86.sse2.pause", llvmcall, Cvoid, ())` émet `pause`. C'est la voie de l'intrinsèque, notée
  comme pour C : 0,5 en règle v1 (inchangé), 1 en règle v2, comme C2 et E4 chez Julia. **Erratum : 1 en règle v2.**
* **E3** : `llvm.expect` par `llvmcall` ne laisse aucun poids de branchement dans l'IR optimisé. 0, inchangé.
* **(1) La décomposition est exacte** (`results/summary_v3.json`). Face à Rust : contrôle 1,84 point, plafond 5,18,
  défaut 0,11. Face à Chapel : contrôle −4,08, plafond +5,44, défaut +0,49. Le plafond de Julia (66,6) est le plus bas
  des 13 premiers, tiré par K8 (0,31), K6 (0,51), K5 (0,63) et K7 (0,63) ; son code par défaut (46,7), où le
  ramasse-miettes est compté, est au niveau de Rust (47,2). L'explication du README (« ce qui la place 12e, c'est son
  runtime ») est fausse.
* **(2) Les formes décrites sont exactes.** Q1 tuned refait 6 passes par bloc de 4 096 lignes, une par groupe, quand
  C charge chaque ligne une fois et accumule les 6 groupes sous masque. K5 tuned (`@simd`) n'émet que des FMA de
  256 bits (4 sur `ymm`) ; avec `-C native,-prefer-256-bit`, 4 FMA sur `zmm`. Ma version `VecElement` + `llvmcall`
  donne le bon résultat, mais Julia 1.13 met en boîte les vecteurs de 512 bits rendus par `llvmcall` (environ 10 Ko
  alloués par appel, 60 fois plus lent) : je ne la retiens pas, l'option `-C` sert à la sensibilité. K7 tuned n'a
  aucun préchargement (C précharge par lots de 16). K8 tuned passe ses compteurs par `Ref`, et `top[] += 1` convertit
  un `Int64` en `Int32` avec vérification.
* **(4) Le mécanisme de K10 est exact.** Dans le K10 tuned du banc, `s` est affectée dans la fermeture du consommateur
  et dans la fonction (`s = fetch(cons)`) : Julia la met dans une `Core.Box`. Cinq variantes, une par processus, en
  deux séries (`tools/julia_check/k10_variants.jl`, `tools/julia_check/run_k10.sh`,
  `results/julia_check/k10_variants.txt`) :
  * V0 (code de la campagne, `yield()` tous les 1 024 tours) : 245 à 469 ms, 6 à 8 Mo alloués par répétition ;
  * V1 (capture, attente active sans `yield()`) : bloquée dans les deux séries (aucune répétition en 35 et 40 s, tuée
    par SIGKILL) ; sous gdb, un thread attend dans `jl_gc_wait_for_the_world`, appelé par `ijl_gc_collect`
    (`results/julia_check/k10_gdb.txt`) ;
  * V2 (sans capture, sans `yield()`, sans point d'arrêt) : 22 à 215 ms, rien d'alloué après la première répétition,
    jamais bloquée ;
  * V3 (sans capture, avec `GC.safepoint()`) : 26 à 158 ms ; V4 (capture et `GC.safepoint()`) : 326 à 868 ms.

  L'attente active sans `yield()` ne bloque donc pas à elle seule : c'est la collecte déclenchée par la boîte qui
  attend le thread en attente active. Le README et FINDINGS disent le contraire.
* **Mesures isolées, indicatives** (`julia_exp`, formes de la remarque) : Q1 tuned 73–92 → 31–54 ms ; K8 tuned 271–278
  → 231–246 ms ; K7 tuned 434–547 → 414–627 ms ; K10 tuned 7–45 ms ; K5 tuned avec l'option `-C` 5,2–7,0 ms contre
  5,7–7,4 ms.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune aux remarques

Les errata de faits et les erreurs de mon implémentation entrent dans le classement publié ; une optimisation nouvelle
(une meilleure forme, même plus proche de ce que fait C) reste une analyse de sensibilité (`docs/FORTRAN.md`, 3.1).

### 3.2 Errata de la matrice (vérifiés ci-dessus)

| Case | Avant (v1 / v2) | Après (v1 / v2) |
|---|---|---|
| B2 allocateurs | 0 / 0 | 0,5 / 0,5 : `Libc.malloc` et `unsafe_wrap`, arènes à la main |
| D3 aide ligne de cache | 0 / 0 | 0,5 / 0,5 : `Threads.PaddedSpinLock`, propre aux verrous |
| D5 barrières, attente active | 0,5 / 0,5 | 0,5 / 1 : `pause` par `llvmcall`, comme les intrinsèques de C |

### 3.3 Ce qui reste hors du classement publié

* **Les formes tuned de la remarque** (Q1 en une passe masquée, K5 en 512 bits, K8 spécialisé sur la profondeur, K7
  préchargé par lots) sont de meilleures formes, pas des corrections : sensibilité (S1). Mes noyaux font ce qu'ils
  annoncent ; ils sont moins travaillés.
* **K10** : la capture de `s` est une erreur de mon implémentation, mais K10 est hors score ; je corrige le diagnostic
  du README et de FINDINGS, et je mesure la forme corrigée.

### 3.4 Mesures (`tools/measure_julia.py`, machine 7)

`julia` (source de la campagne) et `julia_exp` (formes de la remarque, `bench/julia_exp`) sur Q1 tuned et mt, K7
tuned, K8 tuned et K10 tuned, plus quatre témoins dont le code ne change pas (K5 tuned, K9 tuned, Q6 tuned, K1 soa) ;
`julia_c512` (source de la campagne, option `-C native,-prefer-256-bit`) sur K5 tuned ; C par clang (témoin du même
hôte) sur K5 tuned, Q1 tuned et mt, K7 tuned, K8 tuned ; C par GCC sur K8 tuned. 25 cellules, 7 processus par
cellule en 7 passes, ordre tiré au hasard (graine 20261120 + passe), échauffement de 2.

### 3.5 Analyse (`analysis/julia_check.py`) et décisions fixées d'avance

* **J-E, classement publié** : les errata de 3.2 ; aucune donnée ne change. L'analyse v3 recalculée doit redonner
  exactement ce scénario. **Avant** : le calcul publié avant la remarque, refait par le même code.
* **S1 (sensibilité)** : J-E, plus les rapports `julia_exp`/`julia` de Q1 tuned et mt, K7 tuned et K8 tuned ; K5 à 1
  (les données principales de K5 viennent de la machine 3). Chaque rapport est reporté sur les données principales
  par transfert, ou par le pont du C de clang quand le transfert s'en écarte de plus de 25 % (règle de
  `analysis/transfer_check.py`). **S1-K5** : S1 plus le rapport `julia_c512`/`julia` de K5 tuned.
* **README** : (a) l'explication de la place de Julia suit la décomposition (le plafond d'abord) ; (b) le diagnostic
  de K10 est corrigé, comme dans FINDINGS ; (c) S1 est cité comme sensibilité, avec la règle qui la tient hors du
  classement.

## 4. Résultats

175 processus (25 cellules, 7 passes, échauffement de 2), le 30 octobre de 19 h 34 à 19 h 50 sur la machine 7 ;
aucune somme de contrôle fausse, aucun processus refait. Temps, rapports et scénarios : `results/report_julia.md` et
`results/julia_check.json` ; données : `results/raw_julia/`.

### 4.1 Rapports appariés (machine 7, même hôte)

| Clé | Julia | Formes de la remarque | Rapport (IC 95 %) | C par clang |
|---|---|---|---|---|
| Q1 tuned | 81,3 ms | 42,7 ms | 0,525 (0,453–0,596) | 29,1 ms |
| Q1 mt (4 threads) | 29,0 ms | 14,7 ms | 0,506 (0,445–0,580) | 9,2 ms |
| K7 tuned (préchargement par lots) | 571 ms | 394 ms | 0,690 (0,594–0,821) | 346 ms |
| K8 tuned (profondeur en `Val`) | 304 ms | 251 ms | 0,827 (0,710–0,929) | 247 ms (GCC : 138 ms) |
| K10 tuned, hors score (sans capture) | 440 ms | 17,9 ms | 0,041 (0,028–0,063) | — |
| K5 tuned, `-C native,-prefer-256-bit` | 6,51 ms | 6,33 ms | 0,972 (0,797–1,176) | 6,44 ms |
| 4 témoins (code inchangé : K5, K9, Q6 tuned, K1 soa) | | | de 0,97 à 1,06 | |

* **Q1** : confirmé (la remarque : 65,9 → 33,3 ms). Julia reste 1,5 fois plus lente que C en une passe masquée.
* **K7** : le préchargement par lots, que la remarque n'avait pas pu mesurer, gagne 31 %.
* **K8** : la spécialisation sur la profondeur gagne 17 %, pas 49 % : Julia rejoint le C de clang (251 contre 247 ms),
  loin de GCC (138 ms).
* **K5** : sur ce Cascade Lake, le 512 bits n'apporte rien (Julia en 256 bits fait déjà jeu égal avec C, 6,5 ms).
* **K10** : le correctif de la remarque divise le temps par 24 (440 → 18 ms).

### 4.2 Report sur les données principales et classement

Les quatre rapports de S1 restent sous le seuil de 25 % face au pont par le C de clang (écarts de −18,6 à +10,3 %) :
ils sont transférés tels quels. Pour K5, le transfert (0,97) s'écarte du pont de 58 % : les données principales de K5
viennent de la machine 3 (Emerald Rapids), où le C en 512 bits fait 3,94 ms et Julia en 256 bits 6,29 ms ; le pont
reporte Julia en 512 bits à 3,87 ms, au niveau de C, ce qui rejoint la mesure de la remarque sur Emerald Rapids (5,51
→ 4,0 ms). S1-K5 retient donc le pont.

| Scénario | Score | Contrôle C | Plafond E | Rang espéré | Place | Rang 90 % |
|---|---|---|---|---|---|---|
| Avant (publié avant la remarque, refait par le même code) | 62,2 | 68,3 | 66,6 | 11,63 | 12 | 8–13 |
| **J-E, publié** : errata B2, D3, D5 (v2) | **64,0** | **73,3** | 66,6 | **11,12** | **12** | 7–13 |
| S1 (sensibilité) : formes de la remarque pour Q1, K7, K8 | 67,1 | 73,3 | 74,5 | 9,62 | 10 | 5–13 |
| S1-K5 : S1 et K5 en 512 bits (pont) | 68,9 | 73,3 | 79,0 | 8,35 | 9 | 4–12 |

Depuis les errata de Chapel (`docs/CHAPEL.md`), la correction de D (`docs/DLANG.md`) et la remesure des queues de
latence de K8 (`docs/RUST.md`), le classement publié donne à Julia 64,3 points et un rang espéré de 11,20, sans changer
sa place (12e) ni son rang plausible (7–13). Rejouées dans ce même état le 31 octobre (même code, sorties
`results/julia_check_current.json` et `results/report_julia_current.md`), les sensibilités donnent S1 67,4 points et la
11e place (rang espéré 9,82), Chapel la devançant désormais, et S1-K5 69,2 points et la 10e place (8,54), entre Ada et
Chapel : une ou deux places au lieu de deux ou trois.

* **Publié** : les errata rapportent 1,8 point (le contrôle passe de 68,3 à 73,3). Julia reste 12e, à 0,1 point de
  Chapel, qui la devance dans 63 % des variantes ; elle devance Mojo dans 63 %.
* **Sensibilité** : avec les formes de la remarque, Julia gagne 3,1 points et passe 10e, devant Fortran (S1) ; avec
  K5 en 512 bits sur Emerald Rapids, 68,9 points et la 9e place, entre Rust et D (S1-K5). La règle commune (3.1) les
  tient hors du classement publié : ce sont de meilleures formes, pas des corrections.
* **La remarque estimait** 64,0 points avec la matrice (exactement mon calcul), 66,2 avec Q1 et K5, 68,8 avec K8 en
  plus ; mes calculs donnent 67,1 avec Q1, K7 et K8, et 68,9 avec K5 en plus.

### 4.3 Verdicts

* **(1) La décomposition** : exacte. Le README attribuait la 12e place au runtime ; c'est d'abord le plafond. Corrigé.
* **(2) Les versions tuned** : Q1 confirmé (0,53) ; K7 confirmé (0,69), alors que la remarque ne l'avait pas mesuré ;
  K8 moitié moins qu'annoncé (0,83) ; K5 sans effet sur Cascade Lake, mais cohérent, par le pont, avec la mesure de
  la remarque sur Emerald Rapids. Ce sont des optimisations nouvelles : sensibilité, pas classement publié.
* **(3) La matrice** : B2 et D3 exacts (0,5), D5 accepté en règle v2 (1), comme pour C.
* **(4) K10** : diagnostic exact, et le mien était faux ; le README et FINDINGS sont corrigés. K10 étant hors score,
  le classement ne bouge pas.
* **L'effort d'implémentation** : la remarque a raison de dire que mes versions tuned de Julia étaient moins
  travaillées que d'autres ; S1-K5 en donne l'ordre de grandeur (4,9 points, trois places). Je n'ai pas mesuré ce
  qu'une relecture experte rapporterait aux autres langages ; Ada et Fortran y ont gagné deux places chacun.
