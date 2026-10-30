# Remarque sur Fortran : un banc qui inlinait ses noyaux, et quatre cases de la grille

Remarque transmise par l'utilisateur le 30 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).
L'auteur de la remarque a mesuré ses propres copies sur un Emerald Rapids ; je n'ai pas son archive
(`fortran_contre_expertise.tar.gz`). Toutes les vérifications ci-dessous sont les miennes, sur gfortran 16.2 et la
machine 5 (Cascade Lake). Je n'ai ni ifx ni le temps d'installer oneAPI : ses chiffres d'ifx ne sont pas vérifiés.

## 1. Ce que dit la remarque

* (1) **K4 : le banc ne traite pas C et Fortran de la même façon.** Les 14 noyaux du banc C sont `noinline` ; aucun
  noyau de `ms.f90` ne l'est. K4 est inliné dans la boucle de mesure, où gfortran exécute sa version scalaire ; avec
  `!GCC$ ATTRIBUTES NOINLINE`, gfortran fait comme gcc sur le code C (6,6 et 4,4 ms contre 6,6 et 4,3), et 2,7 et
  2,6 ms avec `-mprefer-vector-width=512`.
* (2) **K8 : la disposition.** L'arène de Fortran tient dans trois tableaux séparés ; C et Ada utilisent un tableau
  de nœuds de 16 octets. Avec cette disposition, K8 passe de 181–195 à 122 ms, le niveau de gcc sur C.
* (3) **K5 : une forme mal compilée par gfortran** (`!$omp simd reduction` à 4 accumulateurs, finie par 64 additions
  scalaires). Des accumulateurs en petits tableaux de 16 valeurs donnent 4,59 ms contre 5,33 (95 % du C).
* (4) **Grille** : B2 (C reçoit 0,5 pour des arènes à la main, Fortran 0) ; A3 (`-fpack-derived`, option globale,
  vaut 0,5 selon la règle) ; A4 et B2 (alignement et allocateur par OpenMP, que la grille compte déjà ailleurs pour
  gfortran) ; F2 (GCC 16 livre des cotableaux en mémoire partagée, `libcaf_shmem`).
* Ce qui est justifié : ni types vectoriels ni intrinsèques, ni assembleur, ni indications de branchement, ni
  préchargement, ni constante de ligne de cache, ni projection de fichiers ; K7 et Q1 en pâtissent.
* Nuance : le classement mesure « Fortran compilé par gfortran » ; ifx et flang changent beaucoup de choses.
* Effet estimé (ponctuel) : 60,8 (12e) ; 63,9 (11e) avec K4 ; 65,2 (10e) avec K5 et K8 ; 66,5 avec B2 et A3 ;
  67,0 avec A4 ; 69,2 avec K4 en 512 bits.

## 2. Vérifications faites avant ce plan (machine 5)

Sondes et code machine : `tools/fortran_check/`, `results/fortran_check/probes.txt` et
`results/fortran_check/binaries.txt`.

* **(1) est exact.** Dans le binaire de la campagne, `run_k4` ne contient aucun appel à `k4_natural` ni à
  `k4_branchless` et aucune instruction vectorielle : K4 y est inliné, scalaire (c'est la boucle que la mesure de
  vectorisation avait échantillonnée). Les copies hors ligne des deux noyaux sont vectorisées (30 et 56 opérations
  entières empaquetées), mais jamais appelées. Avec `!GCC$ ATTRIBUTES NOINLINE`, `run_k4` les appelle. Mesure
  isolée, indicative : K4 naturel 11,6 → 6,4 ms, sans branchement 12,2 → 4,4 ms (C par gcc : 6,1 et 5,2).
  **C'est un défaut de mon banc**, pas de Fortran. La convention n'est pas écrite dans la spécification (qui ne
  demande une barrière que pour K5), mais C, C++, C3, D, Go, Julia, Nim, Rust, Zig, Mojo et OCaml isolent leurs 14
  noyaux. Ceux qui ne le font pas tous (Ada pour ses noyaux naturels, Chapel, Odin, Haskell) n'en pâtissent pas sur
  les deux boucles chaudes mesurées : K4 et K9 y sont vectorisés comme hors ligne, ou scalaires pour une autre raison
  (style du stencil d'Ada, GHC).
* **(2) : l'arène à trois tableaux est permise** par la spécification (« nœuds indexés dans des tableaux
  réutilisés »), mais C, Ada et Rust rangent leur arène en un seul tableau de nœuds. Mesure isolée, indicative : K8
  `tuned` 202 → 144 ms avec un tableau de nœuds (C par gcc : 127).
* **(3) : la réduction finale coûteuse était connue** (commentaire de `tuned.f90`). Mesure isolée trop bruitée pour
  trancher (K5 `tuned` varie de 30 à 60 % d'un processus à l'autre, `FINDINGS`).
* **(4)** : `-fpack-derived` fait passer un type (entier 8 bits, 32 bits, 8 bits) de 12 à 6 octets (**A3**). Les
  directives OpenMP de gfortran 16.2 alignent les allouables (`!$omp allocators allocate(align(128): a)`, 50
  allocations sur 50 alignées, contre 0 sans directive) et les variables locales (`!$omp allocate ... align(256)`)
  (**A4**). Un allocateur OpenMP à traits se branche sur `ALLOCATE`, mais la limite de réserve n'a pas été respectée
  dans ma sonde (**B2** : ce n'est pas un allocateur programmable comme les pools d'Ada ou `std::pmr`). GCC 16.2,
  compilé ici depuis les sources, livre `libcaf_shmem` : 4 images, `co_sum` juste (**F2**).

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune aux trois remarques

Les errata de faits (la grille) et les erreurs de mon implémentation entrent dans le classement publié ; une
optimisation nouvelle reste une analyse de sensibilité. Est une erreur : un code qui ne fait pas ce qu'il annonce
(Ada) ou qui s'écarte d'une convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle
de mesure). Une meilleure forme ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation
nouvelle ; de même pour les options réservées aux noyaux `tuned` appliquées au code naturel.

### 3.2 Errata de la grille (vérifiés ci-dessus)

| Case | Avant (v1 / v2) | Après (v1 / v2) | Règle R |
|---|---|---|---|
| A3 disposition compacte | 0 / 0 | 0,5 / 0,5 : `-fpack-derived`, option globale | 0,25 |
| A4 alignement | 0,5 / 0,5 | 0,5 / 1 : directives `allocate` et `allocators` d'OpenMP livrées avec gfortran | 0,5 |
| B2 allocateurs | 0 / 0 | 0,5 / 0,5 : arènes à la main (comme C) ; allocateurs OpenMP à traits | 0,5 |
| F2 localité, PGAS | 0,5 / 0,5 | inchangé ; justification : cotableaux sur un nœud par `libcaf_shmem` livrée, plusieurs nœuds par OpenCoarrays | 0,5 |

### 3.3 Correction du banc et sensibilités

* `fortran` : binaire de la campagne. `fortran_fix` (`bench/fortran_fix/ms.f90`) : les six noyaux de `ms.f90`
  (`k1_natural`, `k2_chase`, `k4_natural`, `k4_branchless`, `q6_natural`, `q1_natural`) marqués `!GCC$ ATTRIBUTES
  NOINLINE`, K5 et K9 naturels déplacés dans des fonctions `NOINLINE` au corps inchangé (`dot_product`, instruction
  tableau). Les noyaux `tuned` sont dans `tuned.f90`, compilé à part : déjà hors ligne.
* `fortran_exp` (sensibilité) : `fortran_fix`, plus K5 `tuned` en quatre accumulateurs de 16 valeurs et l'arène de
  K8 en tableau de nœuds de 16 octets.
* Mesures (`tools/measure_fortran.py`) : `fortran` et `fortran_fix` sur les 26 clés du score qu'a Fortran,
  `fortran_exp` sur K5 `tuned` et K8 `tuned`, C par GCC (`bench/c_gcc`) sur K4 ×2, K5 `tuned` et K8 `tuned`. 7
  processus par cellule, 7 passes, ordre tiré au hasard (graine 20261100 + passe), échauffement de 2. Puis
  `tools/c3_measure.py fortran_fix` (C3, vectorisation mesurée des boucles chaudes).

### 3.4 Analyse (`analysis/fortran_check.py`) et décisions fixées d'avance

* **F-E** : le classement publié, avec les errata de la grille de Fortran.
* **S1, classement publié** : F-E, plus les rapports `fortran_fix`/`fortran` sur les 11 clés dont le code change (K1
  naturel et désordonné, K2 ×3, K4 ×2, K5 naturel, K6 naturel ×2, K9 naturel), **K5 forcé à 1** (données de la
  machine 3), et la C3 de Fortran mesurée sur `fortran_fix`. Les rapports s'ajoutent à ceux d'Ada dans
  `results/transfers.json`.
* S1-K5 (avec K5), S1-26 (les 26 rapports, témoin).
* **S2, sensibilité** : S1, plus les rapports `fortran_exp`/`fortran` de K5 `tuned` et K8 `tuned` (formes de la
  remarque) ; pas dans le classement publié (règle 3.1).
* Non adoptés, et non mesurés : K4 compilé en 512 bits (option des noyaux `tuned`, que le C de K4 n'a pas non plus),
  ifx.
* README : l'explication de K4 est corrigée, et la dépendance au compilateur dite (gfortran ; annexe flang).

## 4. Résultats

406 processus (58 cellules, 7 passes, échauffement de 2), le 30 octobre de 16 h 36 à 16 h 47 sur la machine 5 ;
aucune somme de contrôle fausse ; 16 processus refaits pour vol de temps au-dessus de 2 % (aucun gardé
au-dessus du seuil). Rapports, témoins et scénarios : `results/report_fortran.md` et
`results/fortran_check.json` ; données : `results/raw_fortran/`.

### 4.1 Ce que change l'isolement des noyaux (`fortran_fix` / `fortran`, même hôte)

| Clé | Fortran | Fortran corrigé | Rapport (IC 95 %) | C par GCC, même hôte |
|---|---|---|---|---|
| K4 sans branchement | 20,5 ms | 4,6 ms | 0,224 (0,197–0,264) | 4,8 ms |
| K4 naturel | 13,8 ms | 6,6 ms | 0,478 (0,409–0,552) | 6,1 ms |
| K2 chasse de pointeurs, 16 Kio | 8,1 ms | 6,6 ms | 0,819 (0,792–0,841) | — |
| K2, 256 Kio | 21,5 ms | 19,1 ms | 0,887 (0,814–0,962) | — |
| K2, en mémoire | 611 ms | 602 ms | 0,986 (0,909–1,058) | — |
| K1 ×2, K5, K6 ×2 et K9 naturels | | | de 0,99 à 1,12 | |
| 15 témoins, dont le code ne change pas | | | de 0,92 à 1,16 | |

* **(1) est confirmé.** Isolé, K4 est vectorisé et fait jeu égal avec C compilé par GCC sur le même hôte (0,96 et
  1,08 fois son temps ; la remarque : 4,4 et 6,6 ms contre 4,3 et 6,6). Inliné dans la boucle de mesure, il prenait
  le chemin scalaire.
* **K2 en cache gagnait aussi à être isolé** : 0,82 et 0,89, presque exactement ce qu'avait donné la même correction
  pour Ada (0,83 et 0,89, `docs/ADA.md`) ; rien en mémoire, où la latence domine.
* **Les autres clés changées restent dans l'enveloppe des témoins.** Entre les deux binaires, des noyaux dont le
  source ne change pas bougent de 0,92 (K9 `mt`) à 1,16 (K6 `mt` Q1) : K6 naturel Q1 (1,12) et K1 désordonné
  (1,05) ne se distinguent pas d'un effet de disposition. Le plan les transfère quand même, tels quels.

### 4.2 Écart au plan : K4 sans branchement passe par le témoin

Le plan transfère aux données principales le rapport mesuré sur la machine 5. Pour K4 sans branchement, cela donne
13,1 × 0,224 = 2,9 ms, soit 0,56 fois le C de GCC dans les mêmes données (5,2 ms), presque le temps de clang
(2,8 ms). Or, sur la machine 5, Fortran corrigé fait jeu égal avec GCC (0,96). Le transfert suppose que l'hôte agit
de la même façon sur les deux versions du noyau ; ce n'est pas le cas ici : la boucle scalaire inlinée varie beaucoup
d'un hôte et d'un processus à l'autre (médianes par processus de 14,0 à 26,6 ms sur la machine 5, de 12,0 à 15,0 ms
dans les données principales), alors que la boucle vectorisée suit celle de GCC, qui sort du même moteur.

J'ai donc ajouté une règle **après avoir vu ces chiffres** (c'est un écart au plan) : pour chaque clé transférée qui a
un témoin mesuré sur le même hôte (6 clés d'Ada, 2 de Fortran), je calcule aussi le pont par le témoin : temps du C de
GCC dans les données principales × (corrigé / C de GCC, machine 5). Quand le transfert s'en écarte de plus de 25 %,
plus que l'effet de disposition le plus fort mesuré sur une clé témoin (K9 naturel d'Ada, 1,25, `docs/ADA.md`), le
pont remplace le transfert (`analysis/transfer_check.py`, `results/transfer_check.json`).

| Clé | Transfert (plan) | Pont par le témoin | Écart | Retenu |
|---|---|---|---|---|
| Fortran, K4 sans branchement | 2,93 ms | 5,01 ms | −41,6 % | pont (rapport 0,384) |
| Fortran, K4 naturel | 5,56 ms | 6,54 ms | −14,9 % | transfert |
| Ada, 6 clés (K6 `tuned` et `mt`, K9 `tuned` et `mt`) | | | de −19,1 à +6,0 % | transfert |

Seule une clé change. Le classement publié retient le pont, parce que le transfert y contredit une mesure faite sur le
même hôte ; le scénario du plan reste publié à côté. Le pont suppose à son tour que Fortran corrigé et le C de GCC
réagissent de la même façon au changement d'hôte : vraisemblable (même moteur, même boucle vectorisée), mais pas
démontré. K4 naturel garde le transfert, plus favorable à Fortran que le pont, parce que l'écart reste sous le seuil.

### 4.3 Classement

| Scénario | Score | Plafond E | Rang espéré | Place | Rang 90 % |
|---|---|---|---|---|---|
| Publié avant la remarque | 60,8 | 67,2 | 11,62 | 12 | 9–14 |
| F-E : errata de la grille (A3, A4, B2) | 62,6 | 67,2 | 11,13 | 11 | 8–13 |
| S1 du plan : F-E, 11 rapports transférés (K5 forcé à 1), C3 de `fortran_fix` | 68,4 | 79,9 | 8,24 | 9 | 3–12 |
| **S1 retenu, publié** : S1 avec le pont pour K4 sans branchement | **66,3** | 74,7 | 9,40 | **10** | 5–12 |
| S1-K5 (plan, avec K5) | 68,4 | 79,9 | 8,24 | 9 | 3–12 |
| S1-26 (plan, les 26 rapports) | 67,8 | 78,4 | 8,54 | 10 | 4–12 |
| S2 du plan (sensibilité : formes de la remarque pour K5 et K8 `tuned`) | 70,0 | 84,0 | 7,28 | 8 | 2–11 |
| S2 sur S1 retenu (sensibilité) | 67,8 | 78,5 | 8,54 | 10 | 3–12 |

Depuis les errata de Mojo et de Julia (`docs/MOJO.md`, `docs/JULIA.md`), le classement publié donne à Fortran un rang
espéré de 9,62 et un rang plausible de 5–13, sans changer son score, sa place (10e) ni ses voisins (D le devance dans
64 % des variantes, il devance Chapel dans 56 %).

* **Publié** : Fortran passe de la 12e à la 10e place, derrière D (qui le devance dans 64 % des variantes) et devant
  Chapel (56 %). Les errata de la grille comptent pour 1,8 point, la correction du banc pour 3,7 (5,8 avec le
  transfert du plan). C3 (vectorisation mesurée des boucles chaudes) passe de 0,5 à 1 ; elle ne compte que dans les
  variantes en règle v1, la règle v2 la retire du contrôle.
* **Les formes de la remarque pour K5 et K8** (S2, hors classement publié) ajouteraient 1,5 point (67,8), sans changer
  la place : D garde 54 % des variantes devant Fortran.
* **La remarque estimait** 63,9 points avec K4 seul, 66,5 avec K5, K8, B2 et A3, 67,0 avec A4 et 69,2 avec K4 en 512
  bits. Mes calculs donnent 66,3 points sans K5, K8 ni 512 bits (publié), 67,8 avec K5 et K8.

### 4.4 Verdicts

* **(1) K4** : exact ; erreur de mon banc, corrigée dans le classement publié. Le 512 bits n'est pas adopté (3.4).
* **(2) K8** : la disposition en tableau de nœuds gagne 31 % (0,688 ; 0,590–0,813), à 135 ms contre 146 pour le C de
  GCC sur le même hôte (la remarque : 122 ms, au niveau de GCC). L'effet est réel, mais c'est une disposition
  nouvelle : sensibilité seulement (règle 3.1).
* **(3) K5** : non confirmé sur la machine 5 : 0,98 (0,84–1,18), 8,0 contre 8,2 ms (C de GCC : 6,5 ms). Les 64
  additions scalaires finales existent, mais leur coût ne sort pas du bruit de K5 `tuned` sur cet hôte.
* **(4) Grille** : A3, A4 et B2 corrigés, F2 inchangé avec une justification à jour (2 et 3.2). B2 reçoit 0,5 et non
  1 : un allocateur à traits d'OpenMP n'est pas un allocateur programmable, et sa limite de réserve n'a pas été
  respectée dans ma sonde.
* **Ce que la remarque tient pour justifié** (ni types vectoriels, ni intrinsèques, ni assembleur, ni indications de
  branchement, ni préchargement, ni constante de ligne de cache, ni projection de fichiers) : inchangé.
* **Compilateur** : le classement mesure Fortran compilé par gfortran 16.2. flang, en annexe, vectorisait déjà K4 dans
  le banc d'origine ; ifx n'est pas mesuré.
