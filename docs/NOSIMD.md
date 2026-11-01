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
