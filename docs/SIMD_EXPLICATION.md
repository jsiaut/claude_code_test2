# SIMD explicite et classement : note d'explication (1er novembre)

Pourquoi D a été corrigé et pas Nim ni Ada, ce que pèsent les formes optimisées dans le score, et ce que devient le
classement quand on n'admet que des formes scalaires. Plan, calculs et chiffres complets : [`NOSIMD.md`](NOSIMD.md)
et [`../results/report_nosimd.md`](../results/report_nosimd.md).

## Ce qui a été décidé

* **Le classement publié ne change pas.** La règle appliquée à D a été poussée le 31 octobre à 15 h 00 (UTC), avant
  les mesures de D. La changer maintenant, ce serait la changer après coup.
* **D a été corrigé** parce qu'il était le seul de sa classe à s'écarter d'une convention : les langages à types
  vectoriels portables standard (C1 = 1) écrivent Q1 avec l'algorithme de la référence C.
* **Nim et Ada ne sont pas dans cette classe.** Leurs Q1 en blocs restent dans le score ; leurs réécritures sont des
  sensibilités.
* **Sans SIMD explicite, la structure tient** : les mêmes douze langages en tête, les mêmes neuf derrière, C et C++
  dans les six premiers. Le calcul à la lettre met Chapel, Fortran et Julia devant, surtout parce que le SIMD des
  autres porte aussi la disposition SoA (K1) et la réassociation de la somme (K5). À forme égale pour tous, C, C++ et
  Odin gardent les trois premières places.

## Ce que pèse chaque pilier

Le score vaut 0,35 C + 0,40 E + 0,25 D. Les formes optimisées (*tuned*) n'entrent que dans E ; les formes naturelles
entrent dans E et dans D1.

| Pilier | Poids | Variantes prises en compte | Ce qu'il mesure |
|---|---|---|---|
| C, capacités | 35 % | aucune (matrice) | Ce que le langage permet d'exprimer, noté 0, 0,5 ou 1 par capacité ; C1 note les types vectoriels portables, C2 l'accès aux intrinsèques |
| E, plafond | 40 % | La naturelle et les optimisées, « toutes techniques », SIMD explicite compris ; K4 n'admet que deux formes scalaires | Le meilleur temps de chaque mesure, divisé par t*, le temps du meilleur langage classé |
| D, code par défaut | 25 % | D1, la moitié de D (12,5 % du score) : les seules naturelles (code idiomatique, build release par défaut, sans SIMD explicite), avec les mêmes t* | Ce que donne le code idiomatique ; le reste de D : empreinte et indirection (D2), prévisibilité des latences (D3), hiérarchie mémoire (D4) |

Précision : j'avais écrit « natural (25 %) ». C'est le poids du pilier D entier ; les variantes naturelles n'en font
que la moitié.

## Trois façons d'écrire du SIMD

La frontière retenue sépare ce que le langage sait exprimer lui-même de ce qu'il emprunte. Chaque variante optimisée
du plafond a été lue et classée (`tools/nosimd/simd_markers.py`, `results/nosimd/markers.txt`).

* **S, forme scalaire** : le source n'écrit que des opérations scalaires ; le compilateur vectorise s'il le peut.
  Accumulateurs multiples, formes sans branchement, blocs, `@simd` de Julia, `foreach` de Chapel, directives Fortran,
  préchargements.
* **V, types vectoriels du langage** : le langage nomme un vecteur et ses opérations, capacité propre et portable d'une
  largeur à l'autre. C++ `std::simd`, Zig `@Vector`, Odin `#simd`, C3 `float[<16>]`, D `core.simd`, Mojo `SIMD`,
  C# `Vector512`, Java Vector API, primitives SIMD de GHC.
* **P, intrinsèques de la plateforme** : instructions d'une architecture, fournies par la chaîne standard du langage.
  C `immintrin.h`, Rust `core::arch`, C# `Avx512F`, Go `simd/archsimd` (expérimental).
* **M, intrinsèques importées** : on passe par le C ou par le compilateur, et l'on mesure surtout l'interopérabilité.
  Nim : `importc` depuis `immintrin.h`. Ada : builtins GCC importés, sur un type `vector_type` propre à GNAT.

| Langage | C1 | K1 aos | K1 soa | K5 | Q6 | Q1 | K9 |
|---|---|---|---|---|---|---|---|
| C++ | 1 | S | V | V | V | V | S |
| Zig | 1 | S | V | V | V | V | V |
| Odin | 1 | S | V | V | V | V | V |
| C3 | 1 | S | V | V | V | V | V |
| D | 1 | S | V | V | S | V | V |
| Mojo | 1 | S | V | V | V | V | V |
| C# | 1 | S | V | V | V | V et P | V |
| C | 0,5 | S | P | P | S | P | S |
| Rust | 0,5 | S | P | P | S | P | S |
| Java | 0,5 | S | V | V | V | V | S |
| Go | 0,5 | S | P | P | P | S | S |
| Haskell | 0,5 | S | V | V | S | S | V |
| Nim | 0 | S | M | M | S | S | S |
| Ada | 0,5 | S | S | M | S | S | S |
| Julia, Chapel, Fortran, JavaScript, Python, OCaml, Lua | 0 ou 0,5 | S | S | S | S | S | S |

Les variantes multithread appellent les fonctions optimisées dans quatre fils et suivent leur classe. Les variantes
naturelles sont toutes scalaires, comme K3, K4, K7 et K8 partout. Mojo range ses huit accumulateurs de K1 aos dans un
vecteur rempli voie par voie, comme le `double acc[8]` de C : compté scalaire, avec une vérification qui le compte
SIMD (rien ne change).

## La règle appliquée à D

> « Est une erreur : un code qui ne fait pas ce qu'il annonce […] ou qui s'écarte d'une convention que les autres
> implémentations suivent […]. Une meilleure forme ou une meilleure disposition, même plus proche de ce que fait C, est
> une optimisation nouvelle. »
>
> Règle commune, [`FORTRAN.md`](FORTRAN.md), section 3.1

> « parmi les langages à types vectoriels portables standard (C1 = 1 en règle v1), C++, Zig, Odin, C3, Mojo et C#
> écrivent Q1 tuned avec l'algorithme de la référence C, en une passe de 16 lignes […] ; les blocs servent aux langages
> qui n'en ont pas (Nim, Fortran, Chapel, Julia ; Ada, dont les vecteurs sont propres à GNAT). D, C1 = 1, qui utilise
> `core.simd` dans K1, K5 et K9, est le seul de sa classe à s'en écarter. »
>
> [`DLANG.md`](DLANG.md), section 2, poussé le 31/10 à 15 h 00 (UTC), avant les mesures de D

Le Q1 de D en blocs faisait ce qu'il annonçait (vectorisé par LLVM) ; il s'écartait de la convention de sa classe,
d'où la correction : une passe en `core.simd`, 107,5 → 35,7 ms dans les données principales. Nim (C1 = 0) et Ada
(C1 = 0,5) sont hors de la classe, et le texte les nomme parmi les langages à blocs : leur Q1 n'est pas une erreur, sa
réécriture est une optimisation nouvelle.

## Le décompte de Q1 : 9 contre 5, pas 9 contre 2

J'avais écrit que, parmi les implémentations qui écrivent d'autres noyaux optimisés en SIMD explicite, neuf font Q1
en une passe et deux en blocs. **Le décompte oubliait Java, Go et Haskell**, qui ont eux aussi du SIMD explicite
ailleurs. Sur ces quatorze implémentations, c'est 9 contre 5.

| Forme du Q1 optimisé | Nombre | Langages |
|---|---|---|
| Une passe vectorielle, algorithme de la référence C | 9 | C, C++, Zig, Odin, C3, Mojo, C#, D (corrigé le 31/10), Rust |
| Blocs en SIMD explicite | 1 | Java : blocs de 2 048 lignes, une passe masquée par groupe, en Vector API |
| Blocs scalaires, vectorisés par le compilateur | 2 | Nim, Ada |
| Une passe scalaire sans branchement | 2 | Go, Haskell |
| *Pas de SIMD explicite nulle part* | 7 | Chapel, Julia, Fortran (blocs scalaires) ; JavaScript, OCaml (une passe sans branchement) ; Lua (accumulateurs locaux) ; Python (la boucle du naturel) |

La règle de D n'en dépend pas : elle porte sur la classe C1 = 1 (C++, Zig, Odin, C3, Mojo, C#, D), où D était seul à
s'écarter, et cette liste est exacte. Le critère « SIMD explicite ailleurs », lui, demanderait de réécrire le Q1 de
cinq langages (Nim, Ada, Java, Go, Haskell), pas de deux.

## Le paradoxe de Q1

Les Q1 en blocs de Nim et de D (avant correction) sont plus lents que leur code naturel. Ce n'est pas propre aux
blocs : ceux de Fortran, de Chapel et d'Ada sont parmi les plus rapides des formes scalaires.

| Q1, données principales | Naturel | Optimisé |
|---|---|---|
| Nim, blocs | 95,4 ms | 98,5 ms |
| D, blocs (avant correction) | 88,3 ms | 107,5 ms |
| D, une passe `core.simd` (publié) | 88,3 ms | 35,7 ms |
| Fortran, blocs | 97,5 ms | 47,5 ms |
| Chapel, blocs | 116,3 ms | 48,5 ms |
| Ada, blocs | 194,0 ms | 57,5 ms |
| C, une passe (référence) | 83,4 ms | 32,1 ms |

Comme E prend le minimum des variantes, un optimisé plus lent que le naturel ne coûte rien : pour Q1, E retenait déjà
le naturel de Nim, et celui de D avant la correction.

## Le classement sans SIMD explicite

Les scénarios ont été définis et poussés avant tout calcul ([`NOSIMD.md`](NOSIMD.md), sections 2 et 3). Tous
repartent de l'état publié, avec les mêmes tirages ; seules les variantes admises changent.

* **Sans mt** : les trois mesures multithread sortent pour tous. C'est le témoin du retrait suivant, car les formes mt
  scalaires n'existent pas chez les langages qui écrivent du SIMD.
* **S-scalaire**, le calcul demandé : les variantes V, P et M sont retirées ; chaque mesure prend la meilleure
  variante qui reste, souvent le naturel ; les mesures mt sortent.
* **S-symétrique** : la même forme pour tous, K1 en AoS, K5, Q6, Q1 et K9 en naturel.
* **S-noyaux-scalaires** : le plafond ne garde que K3, K4, K7 et K8, où personne n'écrit de SIMD.
* **S-importées** : seules les intrinsèques importées de Nim et d'Ada sont retirées.

Position par rang espéré sur les 20 000 variantes de l'analyse d'incertitude ; entre parenthèses, le score ponctuel.
État du 1er novembre au matin, avant les errata de C3 ; recalcul dans l'état actuel :
[`../results/report_nosimd_current.md`](../results/report_nosimd_current.md).

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

Compter K1 aos de Mojo comme SIMD ne change rien : Mojo reste 13e (45,9 points au lieu de 46,0).

### Pourquoi le calcul à la lettre bouleverse la tête

Dans K1 et K5, la variante SIMD des langages qui en écrivent porte aussi un gain qui n'a rien de vectoriel. La retirer
leur enlève les deux.

| Données principales | K1 aos | K1 soa | K5 naturel | K5 optimisé |
|---|---|---|---|---|
| C (P) | 38,4 ms | 7,8 ms | 158,1 ms | 3,94 ms |
| C++ (V) | 40,2 ms | 7,6 ms | 77,1 ms | 4,02 ms |
| Ada (K1 soa scalaire) | 38,5 ms | 7,2 ms | 86,1 ms | 4,95 ms |
| Chapel (S) | 50,7 ms | 7,7 ms | 156,9 ms | 4,68 ms |
| Fortran (S) | 41,5 ms | 7,5 ms | 85,7 ms | 5,50 ms |
| Julia (S) | 62,2 ms | 8,0 ms | 81,4 ms | 6,29 ms |

* **K1 : la disposition, pas le SIMD.** Les variantes SoA des quatorze langages à SIMD et de Chapel, Fortran et Julia
  tiennent entre 7,2 et 9,4 ms, vectorielles ou non ; Ada, en scalaire, fixe la référence. Le gain (× 5 sur AoS) vient
  de ne lire que 16 octets par particule au lieu de 64.
* **K5 : la réassociation, pas le SIMD.** Le meilleur SIMD (3,94 ms) ne bat la meilleure forme scalaire (4,68 ms) que
  de 1,2 fois. Le naturel, une somme que le compilateur n'a pas le droit de réordonner, prend 77 à 350 ms.
* Ensemble, K1 et K5 expliquent 82 à 96 % de la baisse du plafond de C, C++, Zig, Odin, C3, Rust, D, Java et Go.
  Chapel, Fortran et Julia ne gagnent presque rien : ils passent devant parce que les autres tombent.

### Ce qui tient dans les trois calculs sans SIMD

* Les positions 13 à 21 ne bougent pas : Mojo, C#, Java, Go, Haskell, OCaml, JavaScript, Python, Lua.
* Les douze premières places reviennent aux mêmes douze langages.
* C et C++ restent dans les six premiers ; C, C++ et Odin prennent les trois premières places à forme égale pour tous
  comme sans les noyaux vectorisables.
* Rust perd des places dans les trois. C3 en perdait aussi dans l'état du matin, plus depuis les errata de sa matrice
  (5e à forme égale comme sans les noyaux vectorisables ; `results/report_nosimd_current.md`).
* Ne tient pas : la tête de Chapel, Fortran et Julia, 1er à 3e à la lettre, 10e à 12e dans les deux autres.

### Nim et Ada sans leurs intrinsèques importées

C'est le test miroir de la distinction retenue. Nim passe de la 7e à la 13e place, Ada de la 9e à la 11e. C'est une
borne haute : la variante SoA de Nim porte aussi la disposition, et les deux langages portent la réassociation de K5
dans leur variante importée. Le classement publié les garde tels quels : leurs intrinsèques importées restent des
formes optimisées admises, comme pour tous les langages.

## Sources

* [`NOSIMD.md`](NOSIMD.md) : classement des variantes, plan poussé avant les calculs, résultats.
* [`../results/report_nosimd.md`](../results/report_nosimd.md) et `results/nosimd_check.json` : sorties de
  `analysis/nosimd_check.py`.
* [`DLANG.md`](DLANG.md) (règle de D), [`NIM.md`](NIM.md) (Q1 de Nim, correction du décompte),
  [`FORTRAN.md`](FORTRAN.md) (règle commune, 3.1), [`METHODOLOGY.md`](METHODOLOGY.md) (piliers).
* `results/nosimd/markers.txt` : marqueurs de SIMD trouvés dans chaque source.
