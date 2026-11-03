# Sensibilité « sans SIMD explicite » (1er novembre) : plan et résultats

Cette page répond à une demande de méthode, pas à une erreur signalée. Le classement publié ne change pas : les
scénarios ci-dessous sont des sensibilités. Les sections 1 à 3 ont été poussées avant tout calcul de scénario ; la
section 4 vient après.

## 1. La demande

> « Le calcul en sensibilité « sans SIMD explicite » : Ce serait très instructif de voir comment le classement évolue
> en plafonnant aux seules formes scalaires/idiomatiques, surtout au vu du paradoxe où les versions tuned de Q1 en Nim
> et D se sont révélées plus lentes que leurs versions naturelles. »

Le même message garde la règle publiée : pas de changement de règle après coup ; D est corrigé parce qu'il s'écartait
de la convention de sa classe (C1 = 1) ; Nim et Ada restent hors de cette obligation dans le score principal.

Rappel des piliers : le score est 0,35 C (matrice des capacités) + 0,40 E (plafond) + 0,25 D (code par défaut). E prend,
pour chaque mesure, le meilleur temps parmi les variantes admises (naturelle et optimisées) ; D1, dans D, ne prend que
les variantes naturelles. Les deux sont normalisés par t*, le temps du meilleur langage classé sur la mesure. La
sensibilité touche E, et D1 par ses références t*.

## 2. Vérifications (faites avant le plan)

### 2.1 Classement des variantes du plafond

Quatre classes, d'après le source des variantes qui entrent dans E :

* **S, forme scalaire** : le source n'écrit que des opérations scalaires ; le compilateur peut vectoriser. Cela
  comprend les accumulateurs multiples, le déroulage, les formes sans branchement, les blocs, `restrict` et `noalias`,
  les directives de vectorisation (`@simd` de Julia, `foreach` de Chapel, directives de `bench/fortran/tuned.f90`) et
  les indications de préchargement de K7 (`_mm_prefetch` en Rust, `Sse.Prefetch0` en C#, `__builtin_prefetch`
  ailleurs) : ce sont des indications de cache, pas du SIMD.
* **V, types vectoriels du langage** : C++ `std::simd`, Zig `@Vector`, Odin `#simd`, C3 `float[<16>]`, D `core.simd`
  (avec `loadUnaligned` de `ldc.simd`), Mojo `SIMD[DType, N]`, C# `Vector512<T>`, Java Vector API (en incubation),
  Haskell primitives SIMD de GHC (`FloatX16#`, `DoubleX8#`).
* **P, intrinsèques de la plateforme fournies par la chaîne standard** : C `immintrin.h`, Rust `core::arch`, C#
  `System.Runtime.Intrinsics.X86` (`Avx512F`, dans Q1, avec `Vector512`), Go `simd/archsimd` (expérimental, types
  propres à l'architecture).
* **M, intrinsèques importées** : Nim (`importc` depuis `immintrin.h`) ; Ada (`pragma Import (Intrinsic)` de builtins
  GCC, sur un type marqué `vector_type`, extension de GNAT).

| Langage | K1 aos | K1 soa | K5 tuned | Q6 tuned | Q1 tuned | K9 tuned |
|---|---|---|---|---|---|---|
| C | S | P | P | S | P | S |
| C++ | S | V | V | V | V | S |
| Zig | S | V | V | V | V | V |
| Odin | S | V | V | V | V | V |
| C3 | S | V | V | V | V | V |
| Rust | S | P | P | S | P | S |
| D (publié) | S | V | V | S | V (1) | V |
| Mojo | S (2) | V | V | V | V | V |
| C# | S | V | V | V | V et P | V |
| Java | S | V | V | V | V | S |
| Go | S | P | P | P | S | S |
| Haskell | S | V | V | S | S | V |
| Nim | S | M | M | S | S | S |
| Ada | S | S | M | S | S | S |
| Julia, Chapel, Fortran, JavaScript, Python, OCaml, Lua | S | S | S | S | S | S |

(1) Une passe en `core.simd`, corrigée le 31/10 (`bench/d_fix`, transfert de `results/transfers.json`) ; avant, des
blocs scalaires (`bench/d`).
(2) Cas limite : Mojo range les huit accumulateurs de K1 aos dans un `SIMD[DType.float64, 8]` qu'il remplit voie par
voie (`acc[k] += …`), comme les `double acc[8]` de C ; seule la réduction finale est vectorielle. Rangé en S, avec une
sous-vérification qui le compte SIMD (scénario 4).

* **Variantes mt** : dans toutes les implémentations qui écrivent du SIMD, K6 mt et K9 mt appellent les fonctions tuned
  dans quatre fils (vérifié dans les sources) ; elles suivent donc la classe de leur variante tuned.
* **Variantes naturelles** : toutes scalaires. Les quatre marqueurs trouvés dans des fonctions naturelles sont des faux
  positifs (alias `ss::vec` de C++ et `SIMD` de Mojo déclarés après la fonction, types `uint8` de Nim et `int8` de
  Fortran).
* **K3, K4, K7 et K8** : aucune variante n'écrit de SIMD.
* **Implémentations annexes** (`c_gcc`, `fortran_flang`, `luajit`, `js_bun`, `python_ft`) : même source, même classe
  que leur langage.
* **Preuves** : `tools/nosimd/simd_markers.py` → `results/nosimd/markers.txt` (fonctions qui contiennent des marqueurs
  de SIMD, puis les lignes lues à la main : faux positifs, `pause` des files de K10, préchargements de K7).

### 2.2 Le paradoxe de Q1

Temps de Q1 dans les données principales (moyenne géométrique des médianes de processus) :

| | naturel | optimisé |
|---|---|---|
| Nim (blocs) | 95,4 ms | 98,5 ms |
| D, blocs (avant correction) | 88,3 ms | 107,5 ms |
| D, une passe `core.simd` (publié) | 88,3 ms | 35,7 ms |
| Fortran, Chapel, Ada (blocs) | 97,5 ; 116,3 ; 194,0 ms | 47,5 ; 48,5 ; 57,5 ms |
| Julia (blocs) | 132,4 ms | 98,8 ms |

Les blocs ne sont pas lents en soi : ceux de Fortran, de Chapel et d'Ada sont parmi les plus rapides des formes
scalaires. Comme E prend le minimum des variantes de chaque mesure, un optimisé plus lent que le naturel ne coûte rien :
pour Q1, E retenait déjà le naturel de Nim, et celui de D avant la correction.

### 2.3 Correction : le « 9 contre 2 »

`docs/NIM.md` (section 2) et mes deux réponses (sur Nim, puis sur la règle de D) comptaient, parmi les
implémentations qui écrivent d'autres noyaux optimisés en SIMD explicite, neuf Q1 en une passe contre deux en blocs
(Nim et Ada). **Le décompte oubliait trois langages** qui ont eux aussi du SIMD explicite ailleurs : Java (Vector API),
Go (`simd/archsimd`) et Haskell (primitives de GHC). Sur ces quatorze implémentations :

* une passe vectorielle, algorithme de la référence C : C, C++, Zig, Odin, C3, Mojo, C#, D (corrigé), Rust (9) ;
* des blocs en SIMD explicite (blocs de 2 048 lignes, une passe masquée par groupe, en Vector API) : Java (1) ;
* des blocs scalaires, vectorisés par le compilateur : Nim, Ada (2) ;
* une passe scalaire sans branchement : Go, Haskell (2).

C'est donc **9 contre 5**, et ce critère, s'il était retenu, demanderait de réécrire le Q1 de cinq langages (Nim, Ada,
Java, Go, Haskell), pas de deux. La règle appliquée à D ne change pas : elle porte sur la classe C1 = 1 (C++, Zig, Odin,
C3, Mojo, C#, D), où D était seul à s'écarter, et cette liste est exacte. La conclusion sur Nim tient aussi : hors de
cette classe, la pratique est partagée, plus encore qu'écrit. Les sept autres langages n'écrivent de SIMD explicite
nulle part : Chapel, Julia et Fortran font des blocs scalaires ; JavaScript et OCaml, une passe scalaire sans
branchement ; Lua, une passe avec des accumulateurs locaux ; Python, la même boucle que le naturel.

## 3. Plan (poussé avant les calculs)

### 3.1 Ce qui ne change pas

Le classement publié, ses règles et ses données. Aucune sortie publiée ne change (`results/transfers.json`, résumés,
tableau du README). Tous les scénarios partent de l'état publié : `v2.dataset_main(transfers=True)` (corrections
transférées, latences de D3 remesurées), même graine, mêmes 20 000 variantes de l'analyse d'incertitude, mêmes
tirages.

### 3.2 Scénarios

1. **Publié** : le témoin. Il doit reproduire les chiffres publiés (contrôle d'égalité avec le scénario « Avant » de
   `results/nim_check.json`).
2. **Contrôle sans mt** : les trois mesures multithread (K6 mt Q6, K6 mt Q1, K9 mt) sortent de E pour tous ; les
   données ne changent pas. Ce scénario sépare l'effet du retrait des mesures mt de celui du retrait du SIMD.
3. **S-scalaire** (le calcul demandé) : les variantes V, P et M de chaque langage (table 2.1) sont retirées. Chaque
   mesure prend le meilleur temps des variantes qui restent (règle publiée du minimum). Les mesures mt sortent pour
   tous, comme au scénario 2 : il n'existe pas de forme mt scalaire mesurée pour les langages qui écrivent leurs noyaux
   en SIMD. Pour D, le Q1 en blocs d'avant la correction (données principales sans le transfert) redevient sa forme
   optimisée scalaire. **Biais connu** : les quatorze langages qui écrivent des noyaux optimisés en SIMD n'ont pas de
   forme optimisée scalaire mesurée pour ces noyaux et retombent sur leur code naturel, alors que les sept autres
   gardent leurs formes optimisées scalaires. Ce scénario est donc une borne basse pour les premiers.
4. **S-scalaire, K1 aos de Mojo compté SIMD** : sous-vérification du cas limite (2) ; K1 de Mojo prend alors sa
   variante naturelle.
5. **S-symétrique** : la même forme pour tous sur chaque mesure vectorisable. K1 n'a plus que aos (soa sort pour tous) ;
   K5, Q6, Q1 et K9 n'ont plus que le naturel ; les mesures mt sortent ; K3, K4, K7 et K8 ne changent pas. Personne ne
   profite d'avoir écrit des formes optimisées scalaires, mais le plafond ne récompense plus aucune optimisation
   manuelle de ces noyaux, et leurs formes naturelles comptent deux fois (dans E et dans D1).
6. **S-noyaux-scalaires** : E réduit aux noyaux où personne n'écrit de SIMD (K3, K4, K7, K8), par le mécanisme
   `e_drop` déjà utilisé dans `docs/MOJO.md` ; C et D ne changent pas. Il n'y a pas de repli, donc pas de biais de
   forme, mais le plafond perd les noyaux vectorisables.
7. **S-importées** : seules les variantes M sont retirées (K1 soa et K5 tuned de Nim, K5 tuned d'Ada) ; les mesures mt
   restent. C'est le test miroir de la distinction retenue : si les intrinsèques importées mesurent surtout
   l'interopérabilité, que doivent Nim et Ada à ces deux noyaux ?

### 3.3 Calcul

* `analysis/nosimd_check.py`. `cf.scenario` reçoit deux paramètres optionnels, sans effet quand ils manquent :
  `e_meas` (les mesures de E) et `patch` (une fonction appliquée aux temps simulés). Les cellules sont chargées et
  tirées comme dans le calcul publié. Ensuite, les temps simulés des variantes retirées passent à NaN, que le minimum
  ignore ; les mesures retirées sortent de `e_meas` ; et le Q1 en blocs de D est rétabli en divisant ses temps simulés
  par le rapport transféré (0,3322). Les tirages sont donc les mêmes d'un scénario à l'autre ; seules les variantes
  admises changent.
* Les références t*, qui servent aussi à D1, sont recalculées sur les variantes restantes, comme le veut la règle
  publiée.
* Sorties : `results/nosimd_check.json` et `results/report_nosimd.md`.
* Rapporté pour chaque scénario : score ponctuel, piliers C, E et D, rang espéré sur 21 et ordre, intervalle de rang à
  90 %, part des premières places, facteurs de E par noyau, langage qui fixe t* sur chaque mesure, déplacements par
  rapport au publié, corrélation de rang (Spearman) avec le publié.

### 3.4 Lecture prévue

* S-scalaire répond à la lettre de la demande ; S-symétrique et S-noyaux-scalaires disent ce qui tient sans le biais de
  forme. Une conclusion n'est retenue que si elle tient dans les trois.
* Quel que soit le résultat, le classement publié ne change pas : ce serait changer la règle après coup.

## 4. Résultats

Sorties : `results/report_nosimd.md` et `results/nosimd_check.json` (`analysis/nosimd_check.py`, environ 40 s par
scénario). Le témoin reproduit exactement le scénario « Avant » de `results/nim_check.json` (écart 0). Aucun écart au
plan.

### 4.1 Classement par scénario

Position par rang espéré (convention publiée) ; entre parenthèses, le score ponctuel.

| Langage | Publié | Sans mt | S-scalaire | S-symétrique | S-noyaux-scalaires | S-importées |
|---|---|---|---|---|---|---|
| C | 1 (80,0) | 1 (80,5) | 5 (63,8) | 3 (80,7) | 1 (77,6) | 1 (80,0) |
| C++ | 2 (76,6) | 2 (77,9) | 6 (62,4) | 1 (80,9) | 3 (73,0) | 2 (76,6) |
| Odin | 3 (72,6) | 3 (74,0) | 7 (58,5) | 2 (77,5) | 2 (70,9) | 3 (72,6) |
| Zig | 4 (72,7) | 4 (74,2) | 9 (60,0) | 4 (77,4) | 7 (68,3) | 4 (72,7) |
| C3 | 5 (70,3) | 5 (71,5) | 12 (54,9) | 6 (73,8) | 6 (68,1) | 5 (70,3) |
| Rust | 6 (70,5) | 6 (71,6) | 10 (57,1) | 8 (71,7) | 8 (68,1) | 6 (70,5) |
| Nim | 7 (69,7) | 7 (70,6) | 8 (58,8) | 5 (73,7) | 5 (68,5) | 13 (57,2) |
| D | 8 (72,6) | 8 (74,1) | 11 (58,6) | 7 (74,8) | 9 (70,4) | 7 (72,6) |
| Ada | 9 (71,7) | 9 (73,8) | 4 (65,1) | 9 (72,2) | 4 (72,9) | 11 (62,3) |
| Chapel | 10 (66,1) | 10 (65,9) | 1 (67,8) | 12 (66,1) | 10 (63,9) | 8 (66,1) |
| Fortran | 11 (66,1) | 11 (66,4) | 2 (68,2) | 10 (70,2) | 11 (63,2) | 9 (66,1) |
| Julia | 12 (64,3) | 12 (64,9) | 3 (66,5) | 11 (69,2) | 12 (63,2) | 10 (64,3) |
| Mojo | 13 (62,8) | 13 (63,3) | 13 (46,0) | 13 (57,0) | 13 (57,8) | 12 (62,8) |
| C# | 14 (56,0) | 14 (57,2) | 14 (43,7) | 14 (54,5) | 14 (50,3) | 14 (56,0) |
| Java | 15 (47,2) | 15 (47,9) | 15 (36,9) | 15 (50,4) | 15 (44,8) | 15 (47,2) |
| Go | 16 (43,0) | 16 (42,4) | 16 (36,8) | 16 (46,7) | 16 (40,1) | 16 (43,0) |
| Haskell | 17 (35,5) | 17 (35,8) | 17 (26,8) | 17 (32,7) | 17 (30,0) | 17 (35,5) |
| OCaml | 18 (24,7) | 18 (25,1) | 18 (25,6) | 18 (26,9) | 18 (24,9) | 18 (24,7) |
| JavaScript | 19 (14,7) | 19 (14,8) | 19 (15,1) | 19 (19,1) | 19 (14,4) | 19 (14,7) |
| Python | 20 (10,0) | 20 (10,0) | 20 (10,0) | 20 (10,3) | 20 (10,0) | 20 (10,0) |
| Lua | 21 (4,0) | 21 (4,1) | 21 (4,1) | 21 (4,8) | 21 (4,1) | 21 (4,0) |
| *Spearman / publié* | 1,000 | 1,000 | 0,730 | 0,986 | 0,970 | 0,965 |
| *1re place (part)* | C 57 % | C 47 % | Chapel 43 % | C++ 29 % | C 50 % | C 58 % |

La sous-vérification de Mojo (scénario 4) ne change rien : Mojo reste 13e (45,9 points au lieu de 46,0), les autres
positions sont celles de S-scalaire.

### 4.2 Pourquoi S-scalaire bouleverse la tête

Le plafond des langages qui écrivent du SIMD s'effondre dans S-scalaire (C : 86,6 → 44,4 entre le contrôle sans mt et
S-scalaire), et presque tout vient de deux noyaux où leur variante SIMD porte aussi un gain qui n'a rien de vectoriel :

| Données principales | K1 aos | K1 soa | K5 naturel | K5 optimisé |
|---|---|---|---|---|
| C (intrinsèques) | 38,4 ms | 7,8 ms | 158,1 ms | 3,94 ms |
| C++ (`std::simd`) | 40,2 ms | 7,6 ms | 77,1 ms | 4,02 ms |
| Ada (K1 soa scalaire) | 38,5 ms | 7,2 ms | 86,1 ms | 4,95 ms |
| Chapel (scalaire, `foreach`) | 50,7 ms | 7,7 ms | 156,9 ms | 4,68 ms |
| Fortran (scalaire) | 41,5 ms | 7,5 ms | 85,7 ms | 5,50 ms |
| Julia (scalaire, `@simd`) | 62,2 ms | 8,0 ms | 81,4 ms | 6,29 ms |

* **K1 : la disposition, pas le SIMD.** Les variantes SoA des quatorze langages qui écrivent du SIMD et de Chapel,
  Fortran et Julia tiennent entre 7,2 et 9,4 ms, vectorielles ou non ; c'est Ada, en scalaire, qui fixe t* (7,2 ms). Le
  gain (× 5 sur AoS) vient de ne lire que 16 octets par particule au lieu de 64. Mais treize des quatorze langages qui
  écrivent du SIMD (tous sauf Ada) l'écrivent dans la même variante que la disposition SoA : S-scalaire leur retire les
  deux, et leur facteur K1 tombe de 0,9-1,0 à 0,15-0,19.
* **K5 : la réassociation, pas le SIMD.** Le meilleur SIMD (C, 3,94 ms) ne bat la meilleure forme scalaire (Chapel,
  4,68 ms) que de 1,2 fois. Le code naturel, une somme séquentielle que le compilateur n'a pas le droit de réordonner,
  prend 77 à 350 ms. Chez les quatorze, la permission de réordonner est dans la variante SIMD (plusieurs accumulateurs
  vectoriels) ; sans elle, leur facteur K5 tombe à 0,01-0,06.
* **Ensemble, K1 et K5 expliquent 82 à 96 % de la baisse du plafond** de C, C++, Zig, Odin, C3, Rust, D, Java et Go
  (en logarithme, du contrôle sans mt à S-scalaire) ; toute celle de Nim et d'Ada ; 62 à 72 % pour Mojo, C# et
  Haskell, dont les K6 et K9 naturels sont lents aussi. Chapel, Fortran et Julia ne gagnent presque rien en valeur
  absolue (+ 5,5 % de plafond, parce que t* monte sur K5, Q6 et Q1) : ils passent devant parce que les autres tombent.
* **Le paradoxe de Q1** : dans S-scalaire, la référence de Q1 est une forme scalaire en blocs (Fortran, 47,5 ms ;
  Chapel 48,5, Ada 57,5). Nim et D gardent leur naturel (95,4 et 88,3 ms), comme E le faisait déjà pour Nim.

S-scalaire mesure donc surtout qui a écrit la disposition SoA et la réassociation de K5 en forme scalaire, plus que la
capacité à se passer du SIMD.

### 4.3 Ce qui tient dans les trois scénarios (règle de lecture 3.4)

* **Les positions 13 à 21 ne bougent pas** : Mojo, C#, Java, Go, Haskell, OCaml, JavaScript, Python, Lua.
* **Les douze premières places reviennent aux mêmes douze langages** : C, C++, Odin, Zig, C3, Rust, Nim, D, Ada,
  Chapel, Fortran, Julia.
* **C et C++ restent dans les six premiers** : C 5e, 3e, 1er ; C++ 6e, 1er, 3e.
* **Rust et C3 perdent des places** dans les trois : Rust 10e, 8e, 8e au lieu de 6e ; C3 12e, 6e, 6e au lieu de 5e.

**Ce qui ne tient pas** : la tête de Chapel, Fortran et Julia (1er, 2e, 3e dans S-scalaire ; 10e à 12e dans les deux
autres), qui vient du biais de forme décrit en 4.2. Dans S-symétrique et S-noyaux-scalaires, les neuf premiers sont
les neuf du classement publié, dans un autre ordre (Spearman 0,986 et 0,970) ; la première place se partage dans
S-symétrique (C++ 29 %, C 23 %, Odin 22 %, Zig 19 %) et reste à C dans S-noyaux-scalaires (50 %).

### 4.4 Contrôle sans mt et S-importées

* **Sans les mesures mt**, aucune position ne change (Spearman 1,000) ; la part des premières places de C passe de
  57 % à 47 %.
* **S-importées** : Nim passe de la 7e à la 13e place (69,7 → 57,2 points), Ada de la 9e à la 11e (71,7 → 62,3).
  Plafond de Nim 72,9 → 41,6 (K1 0,98 → 0,19 ; K5 0,82 → 0,05), d'Ada 78,1 → 54,6 (K5 0,79 → 0,05). Le biais de
  4.2 joue ici aussi : la variante SoA de Nim porte la disposition avec les intrinsèques, et les deux langages portent
  la réassociation de K5 dans leur variante importée. C'est donc une borne haute de ce que les intrinsèques importées
  leur apportent ; Ada garde son K1 SoA, scalaire.

### 4.5 Verdicts

* **Le classement publié ne change pas.**
* **Sans SIMD explicite, la structure tient** : les mêmes douze langages en tête, les mêmes neuf derrière, C et C++
  dans les six premiers. L'ordre à l'intérieur des douze dépend du traitement des formes scalaires qui manquent. Le
  calcul à la lettre (S-scalaire) met Chapel, Fortran et Julia devant, mais il mesure surtout un biais de forme ; à
  forme égale pour tous (S-symétrique) comme sans les noyaux vectorisables (S-noyaux-scalaires), C, C++ et Odin
  occupent les trois premières places (Zig 4e et 7e, Ada 9e et 4e).
* **Le paradoxe de Q1 ne coûte rien** : E prend le minimum des variantes ; sans SIMD, la meilleure forme scalaire de
  Q1 est en blocs (Fortran, Chapel, Ada), et Nim et D gardent leur naturel.
* **Limite du banc mise au jour** : dans K1 et K5, le SIMD explicite emporte des gains qui ne sont pas vectoriels (la
  disposition SoA, la réassociation). Les séparer demanderait des variantes optimisées scalaires (K1 en SoA, K5 à
  accumulateurs multiples) dans les quatorze langages, donc de nouvelles mesures ; ce n'est pas fait ici.

### 4.6 Recalcul après les errata de C3 (1er novembre, midi)

Les sorties ci-dessus datent du matin. Recalculé dans l'état actuel (`results/report_nosimd_current.md`, témoin égal au
scénario Errata de `results/c3_check.json`) : les conclusions de 4.3 tiennent (mêmes douze langages en tête, positions
13 à 21 inchangées, C et C++ dans les six premiers, C, C++ et Odin aux trois premières places à forme égale comme sans
les noyaux vectorisables), sauf une : C3, 5e au publié, garde sa 5e place dans S-symétrique et S-noyaux-scalaires (11e
dans S-scalaire) ; seul Rust perd des places dans les trois (10e, 8e, 8e au lieu de 7e).

### 4.7 Recalcul après la remarque sur Odin (1er novembre, après-midi)

Recalculé de nouveau (`results/report_nosimd_current.md`, témoin égal au scénario Publié de `results/odin_check.json`,
où Odin passe de 72,6 à 73,5 points par l'erratum C2) : les conclusions de 4.3 et 4.6 tiennent. Seul changement de
place en tête : à forme égale (S-symétrique), Odin passe 1er devant C++ et C (78,4 points ; C++ 1er auparavant) ; sans
les noyaux vectorisables, l'ordre reste C, Odin, C++.

### 4.8 Recalcul après la remarque sur C++ (1er novembre, soir)

Recalculé de nouveau (`results/report_nosimd_current.md`, témoin égal au scénario Publié de `results/cpp_check.json`,
où C++ perd 2 points de contrôle en règle v1 par l'erratum C1 et passe 3e derrière Odin) : les conclusions tiennent,
sauf une. À la lettre (S-scalaire), C++ passe 7e derrière Odin (6e), C restant 5e : C, Odin et C++ restent dans les
sept premiers, et non plus C et C++ dans les six. À forme égale (S-symétrique), l'ordre reste Odin, C++, C ; sans les
noyaux vectorisables, C, Odin, C++.

### 4.9 Recalcul après la remarque sur C (1er novembre, soir)

Recalculé de nouveau (`results/report_nosimd_current.md`, témoin égal au scénario Publié de `results/c_check.json`,
où C et C++ perdent chacun 3,6 points de contrôle en règle v1 par les errata A3 et C2 ; scores inchangés) : les
positions 13 à 21, les douze premiers et l'ordre sans les noyaux vectorisables (C, Odin, C++) ne changent pas. Deux
places changent, de justesse. À la lettre (S-scalaire), C++ passe 9e (rang moyen 6,96), derrière Nim (6,74) et Zig
(6,87), C et Odin restant 5e et 6e : C et Odin restent dans les six premiers dans les trois scénarios, C++ seulement
dans deux. À forme égale (S-symétrique), Zig passe 3e devant C (3,54 contre 3,65 ; Odin 1er, 2,69 ; C++ 2e, 3,48),
chacun des quatre étant 1er dans 20 à 28 % des variantes. Sans les mesures mt, C est 1er dans 43 % des variantes
(52 % au publié).

### 4.10 Recalcul après le harnais commun de K9 (1er novembre, soir)

Recalculé de nouveau (`results/report_nosimd_current.md`, témoin égal au scénario Publié de `results/k9_check.json` :
K9 de toutes les implémentations remesuré sur la machine 16, grilles allouées une fois) : les douze premiers restent
les mêmes et les neuf derniers aussi, mais à la lettre (S-scalaire) Go et Java échangent les 15e et 16e places (rang
moyen 15,11 contre 15,16). À la lettre, C est 5e, Odin 6e et C++ 7e (il était 9e) : C et Odin restent dans les six
premiers dans les trois scénarios, C++ dans les sept. À forme égale (S-symétrique), C, Odin et C++ retrouvent les
trois premières places : Odin 1er (2,64), C 2e (3,32), C++ 3e (3,33), Zig 4e (4,25) ; sans les noyaux vectorisables,
C, Odin, C++, comme avant. Sans les mesures mt, C est 1er dans 48 % des variantes (49 % au publié).

### 4.11 Recalcul après la remarque sur Java (2 novembre)

Recalculé de nouveau (`results/report_nosimd_current.md`, témoin égal au scénario J-E de `results/java_check.json` :
K5 de Java corrigé, F1 de Java à ½). Seules deux places bougent : à la lettre (S-scalaire), Java repasse devant Go
(15e et 16e, rang moyen 15,09 contre 15,14) ; Java est donc 15e dans tous les scénarios. Le reste ne change pas : à
forme égale, Odin, C et C++ en tête ; sans les mesures mt, C est 1er dans 48 % des variantes (49 % au publié).

### 4.12 Recalcul après la remarque sur Go (2 novembre)

Recalculé de nouveau (témoin égal au scénario G-E de `results/go_check.json` : K5 de Go corrigé, artefact de la
préemption retiré des clés publiées depuis Emerald Rapids). Aucune place ne change : Java reste 15e et Go 16e dans
tous les scénarios, de peu à la lettre (rang moyen 15,10 contre 15,12) ; en tête, rien ne bouge.

### 4.13 Recalcul après la remarque sur Haskell (3 novembre)

Recalculé de nouveau (témoin égal au scénario H-E de `results/haskell_check.json` : options, K1, K5 et K8 de Haskell
corrigés, B2, B3 et A7 de Haskell à ½). Haskell reste 17e dans tous les scénarios (41,3 points publiés, 31,1 à la
lettre). À la lettre (S-scalaire), Go passe devant Java (rang moyen 15,13 contre 15,17) : le K3 `rmw_padded` corrigé
de Haskell devient le meilleur temps de sa clé, et ce déplacement des références suffit à départager ces deux
langages si proches ; à forme égale (S-symétrique) et sans les noyaux vectorisables, Java reste devant (14,90 contre
15,35 ; 14,99 contre 15,90). En tête, rien ne bouge.
