# v4, point 5 : le coût d'accès au plafond — plan (22 novembre 2026)

*Plan d'ensemble : `docs/V4_PLAN.md` (point 5). Ce plan est poussé avant tout outil et tout comptage ; les écarts
éventuels seront datés et justifiés ici et dans `docs/METHODOLOGY.md`. Le point 5 ne corrige rien de publié : le
classement de tête du README ne change pas.*

## 1. Question

La troisième remarque générale (`docs/AUDIT3_2026-11-18.md`, point 9) : « Mesurer le coût d'accès au plafond. Quand tous
les langages compilés atteignent la limite du matériel, ce qui les distingue est le prix à payer pour y arriver :
lignes ajoutées, code `unsafe`, portabilité. C'est mesurable, et cela pourrait remplacer une partie de la grille
jugée. » La réponse (`docs/AUDIT3_RESPONSE.md`, section 3) en a fait une mesure statique des sources existantes, à
définir d'avance, sans campagne. Le point 5 mesure, pour chaque langage et chaque cellule du plafond, ce que coûte en
code la forme qui l'atteint : lignes ajoutées au code naturel, lignes exécutées sans les vérifications de sûreté
mémoire du langage, constructions propres à une architecture et cibles où le code compile. Il chiffre ensuite ce que
deviendrait le classement si cette mesure remplaçait la partie de la grille qui décrit les leviers d'accès au plafond.

## 2. Faits établis avant le plan (22 novembre)

* **Formes et temps** : ceux du point 4 (`docs/V4_CONVERGE.md`, section 11), sur la machine 33. Le plafond compte 12
  cellules (`analysis/analyze_v2.py`, `E_V2`) : K1, K3, K4, K5, K6 Q6 et Q1 à un fil et à quatre fils, K7, K8, K9 à un
  fil et à quatre fils. Le point 4 a mesuré, dans une même campagne, toutes les formes admises de chaque langage
  (variantes publiées, K4 `tuned` de R3, formes du catalogue, formes propres à un runtime ; relevé
  `results/converge/forms.json`) ; sa sortie donne la forme retenue par « Convergent » pour 10 cellules
  (`results/converge/analysis.json`, `retained`), K1 et K3 n'ayant que des formes publiées.
* **Volume** : 300 cellules de langage (25 × 12) ; 424 formes à 10 % ou moins du temps de la meilleure forme de leur
  langage dans la cellule, soit 348 clés distinctes ; 585 avec les variantes naturelles de référence.
* **Code** : un fichier source par langage dans les copies du point 4 (`bench/<langage>_cv`), de 349 lignes (BQN) à
  1 961 (FreePascal), plus `tuned.f90` (Fortran) et `msvec.pas` (FreePascal). Le code d'une forme n'est pas toujours
  une fonction à part : en C, la table de K7 est écrite dans `run_k7`, avec la boucle de mesure. Les régions doivent
  donc être délimitées à la lecture.
* **Vérifications du mode publié** (`docs/V4_EQUAL.md`, section 2) : sans vérification de bornes dans leur mode publié,
  Zig (`-O fast`), C3 (`-O3`), Chapel (`--fast`), D (`-release` : bornes vérifiées dans les seules fonctions
  `@safe`), FreePascal (`{$R-}` par défaut), C, C++ et Fortran ; avec, Rust, Swift, Ada, Nim, Odin, Julia, Mojo, C#,
  Java, Go, Haskell, OCaml, JavaScript, Python, Lua, PHP et BQN.
* **Constructions relevées dans les copies** (recherche par motifs, fichiers entiers, avant tout découpage) :
  * contournement des vérifications : Rust (`unsafe` 49 fois, `get_unchecked` et pointeurs bruts 41), Swift
    (`Unsafe…` 57), Mojo (`unsafe_…` 73), OCaml (`unsafe_get`, `unsafe_set` 64), Ada (`pragma Suppress` 23,
    `Unchecked_…` et `'Address` 36), Julia (`@inbounds` 24), Haskell (`unsafe…` 20), Odin (`#no_bounds_check` 14),
    Nim (pragmas de vérification 11), C# (`unsafe`, `Unsafe.` 10), Go (`unsafe` 2) ;
  * propres à x86 : intrinsèques en C (`_mm…` 65), C++ (6), Rust (64, et six attributs `target_feature`), Nim (45,
    importés d'`immintrin.h`), Chapel (92, déclarés `extern`), Ada (22 `__builtin_ia32_…`), D (`ldc.gccbuiltins_x86`),
    C# (`System.Runtime.Intrinsics.X86`) ;
  * vecteurs portables ou intrinsèques génériques : Zig (`@Vector`), Odin (`#simd`, `intrinsics.…`), Mojo (`SIMD`),
    Swift (`SIMD…`), C++ (`std::simd`), Java (Vector API), C# (`Vector512<T>`), Haskell (primitives `…X16#`), Julia
    (intrinsèques LLVM génériques : `llvm.fmuladd`, `llvm.vector.reduce.…`, `llvm.ctpop`, `llvm.prefetch`) ; Go
    (`simd/archsimd`, dont la chaîne livre des fichiers pour amd64 et pour arm64 : la portabilité sera établie par la
    compilation) ;
  * aucune forme ne garde une construction propre à x86 derrière une condition avec un repli portable.
* **Compilation pour une autre architecture, hors ligne** (essais sur des programmes triviaux, 22 novembre) : objets
  aarch64 et riscv64 produits par `zig cc` (C, avec les en-têtes de libc livrés par Zig ; `immintrin.h` y est refusé
  hors x86), Zig, Go 1.27, LDC (D), Odin, C3 (`compile-only --target`), Nim (C généré pour arm64, puis `zig cc`),
  `flang-23` (Fortran, aarch64) et Mojo (`--target-triple`). `zig c++` compile aussi pour ces cibles, mais avec la
  libc++ de LLVM, alors que la construction publiée de C++ emploie GCC 16 et `std::simd` de libstdc++. Sans chaîne
  croisée installée : Rust (bibliothèque standard de la cible absente), Swift (bibliothèque standard x86_64 seule),
  FreePascal (`ppcx64` seul), GNAT, Chapel, GHC, OCaml. C# et Java compilent vers un code intermédiaire indépendant de
  l'architecture ; Julia compile à l'exécution ; JavaScript, Python, Lua, PHP et BQN sont interprétés.
* **Grille** : le contrôle pèse 35 % du score au centre ; ses catégories, A (disposition, 25 %), B (mémoire, 20 %), C
  (SIMD, 20 % : types vectoriels portables, intrinsèques de la cible, vectorisation automatique mesurée, réassociation
  flottante, parallélisme de données), D (concurrence, 15 %), E (bas niveau, 10 % : code natif inspectable, assembleur
  en ligne, indications de branchement, préchargement, non-aliasing, contrôle local des vérifications de bornes,
  calcul à la compilation et génériques monomorphisés) et F (10 %). Les catégories C et E décrivent les leviers qui
  mènent au plafond ; la mesure du point 5 observe leur emploi dans le code qui l'atteint.

## 3. Quantités, fixées ici

### 3.1 Cellules, formes, références

* **Cellules** : les 12 du plafond (section 2).
* **Référence naturelle** : K1 `natural` ; K3, la variante `packed` du même schéma (`sw_packed` pour `sw_padded`,
  `rmw_packed` pour `rmw_padded`) ; K4 `natural_unsorted` ; K5 `natural` ; Q6 et Q6 à quatre fils, Q6 `natural` ; Q1 et
  Q1 à quatre fils, Q1 `natural` ; K7, K8 `natural` ; K9 et K9 à quatre fils, K9 `natural`. Pour les cellules à quatre
  fils, la référence est le code naturel à un fil : le coût du parallélisme fait partie du prix.
* **Forme d'accès** (calcul principal) : la forme retenue par « Convergent » au point 4 (la plus rapide des formes
  admises, estimation ponctuelle) ; pour K1 et K3, la plus rapide des formes publiées, sur les mêmes données. En
  sensibilité : la plus courte (en lignes) des formes admises de la cellule dont le temps est à 10 % ou moins de la plus
  rapide, la variante naturelle comprise quand elle appartient à la cellule.

### 3.2 Régions

* La **région** d'une forme est l'ensemble des lignes de la copie `bench/<langage>_cv` que la forme ajoute au harnais :
  les fonctions appelées dans la zone chronométrée et celles qu'elles appellent dans le fichier, les types et constantes
  propres à la forme, et sa préparation propre (réserve de fils, tampons, conversion des données). En sont exclues les
  lignes communes à toutes les variantes : mesure du temps, chargement des données, somme de contrôle, choix de la
  variante. Une fonction partagée par plusieurs formes compte dans chacune ; le code de la bibliothèque standard ne
  compte pas.
* Le **relevé des régions** (`tools/cost/regions.py`) donne, pour chaque langage, les intervalles de lignes de chaque
  région, les régions de chaque forme et le nom de sa fonction d'entrée, et l'empreinte (`git hash-object`) de chaque
  fichier source : l'outil refuse de compter si un fichier a changé. Il vérifie que chaque forme contient sa fonction
  d'entrée et que ses intervalles ne se chevauchent pas, et publie la liste des régions de chaque forme
  (`results/cost/regions.md`). Les régions sont délimitées langage par langage, dans l'ordre du classement publié,
  avant tout comptage.

### 3.3 Taille

* **Lignes de code** : lignes non vides qui gardent un caractère de code une fois les commentaires retirés (syntaxe des
  commentaires de chaque langage dans l'outil ; une chaîne de documentation seule dans son instruction compte comme
  commentaire). En sensibilité : **lexèmes** (identifiants, nombres, chaînes, opérateurs et ponctuation), comptés de la
  même façon.
* Par cellule : lignes de la forme d'accès L, de la référence naturelle N, rapport L/N, lignes ajoutées L − N, et part
  des lignes ajoutées s = max(0 ; 1 − N/L).

### 3.4 Code sans vérification

* **Part absolue** (calcul principal) : part des lignes de la forme d'accès qui s'exécutent sans les vérifications de
  sûreté mémoire du langage dans son mode publié. Elle vaut 1 dans les huit langages dont le mode publié n'en a pas
  (section 2) ; ailleurs, c'est la part des lignes qui portent une construction de la liste ci-dessous, ou qui sont
  dans la portée d'une construction de bloc de la liste.
* **Part marginale** (sensibilité) : la part des lignes qui portent une construction de la liste ou sont dans sa
  portée, pour tous les langages (nulle dans les langages qui n'en ont pas) ; elle mesure ce que le programmeur écrit
  pour contourner une vérification, pas ce que le langage ne vérifie jamais.
* **Liste** (fixée ici ; chaque occurrence trouvée est examinée ; un ajout ou un retrait est un écart daté) :
  * Rust : blocs et fonctions `unsafe` (portée : le bloc, la fonction), `get_unchecked…`, `from_raw_parts…`,
    `transmute`, déréférencement de pointeurs bruts (`*const`, `*mut`, `.add(`, `.offset(`) ;
  * Swift : `withUnsafe…` (portée : la fermeture), `Unsafe…Pointer`, `unsafeBitCast`, `assumingMemoryBound`,
    opérateurs sans contrôle de débordement (`&+`, `&-`, `&*`) ;
  * Nim : `{.push checks: off.}` et ses variantes (portée : jusqu'au `{.pop.}`), `{.boundChecks: off.}`,
    `{.overflowChecks: off.}`, `ptr UncheckedArray`, `cast[`, `addr`, `unsafeAddr`, `copyMem` ;
  * Ada : `pragma Suppress` (portée : l'unité qui le contient), `Unchecked_Conversion`, `Unchecked_Access`,
    `'Address`, `Address_To_Access_Conversions` ;
  * Odin : `#no_bounds_check` (portée : le bloc ou la procédure), `rawptr`, `transmute`, pointeurs multiples `[^]`,
    `mem.ptr_offset` ;
  * Julia : `@inbounds` (portée : l'expression ou le bloc), `unsafe_…`, `pointer(` ;
  * Mojo : `UnsafePointer`, `unsafe_…`, `bitcast` ;
  * C# : blocs et méthodes `unsafe` (portée : le bloc, la méthode), `fixed`, `stackalloc`, `Unsafe.`,
    `MemoryMarshal.` ;
  * Java : `sun.misc.Unsafe`, `jdk.internal.misc.Unsafe` ;
  * Go : `unsafe.` ;
  * Haskell : fonctions `unsafe…`, `Ptr`, `peek`, `poke`, `plusPtr`, primitives sur la mémoire brute
    (`index…OffAddr#`, `read…OffAddr#`, `write…OffAddr#`, `…Array#` non vérifiées) ;
  * OCaml : `unsafe_get`, `unsafe_set`, `Array.unsafe_…`, `Bytes.unsafe_…`, `Obj.magic` ;
  * Zig, C3, Chapel, D, FreePascal, C, C++, Fortran : les mêmes familles (`@ptrCast`, `@ptrFromInt`,
    `@setRuntimeSafety(false)` ; `c_ptr`, `c_ptrTo` ; `.ptr`, `cast(` vers un pointeur ; `Move(`, pointeurs `^`), pour
    la seule part marginale ;
  * JavaScript, Python, Lua, PHP, BQN : aucune construction.

### 3.5 Architecture et portabilité

* **Lignes propres à une architecture** : lignes de la forme d'accès qui portent une construction de la liste
  ci-dessous. Liste (fixée ici, mêmes règles d'examen et d'écart) : intrinsèques x86 (`_mm…`, `__m128…`, `__m256…`,
  `__m512…`, `__builtin_ia32_…`, en-têtes `immintrin.h`, `x86intrin.h`), `std::arch::x86_64` et `core::arch`,
  `#[target_feature]`, `is_x86_feature_detected`, `ldc.gccbuiltins_x86`, `System.Runtime.Intrinsics.X86` et ses
  classes (`Avx…`, `Sse…`, `Bmi…`, `Popcnt`, `Lzcnt`, `X86Base`), `llvm.x86.…`, assembleur en ligne (`asm`, `asm!`,
  `System.Machine_Code`), déclarations `extern` ou `importc` de ces intrinsèques (Chapel, Nim), `simd/archsimd` de Go
  (classement confirmé ou corrigé par la compilation, ci-dessous). Ne comptent pas : les types vectoriels portables et
  les intrinsèques génériques (section 2), `__builtin_prefetch`, `__builtin_popcount…` et leurs équivalents portables.
* **Forme portable** : aucune ligne propre à une architecture dans sa région, ou chacune gardée par une condition avec
  un repli portable dans la forme (aucun cas relevé à la section 2). Par cellule : p = 0 si la forme d'accès est
  portable, 1 sinon.
* **Compilation** : pour les langages qui ont une chaîne croisée hors ligne (section 2 : C, Zig, Go, D, Odin, C3, Nim,
  Fortran, Mojo ; C++ si la compilation de contrôle passe), la copie `_cv` entière est compilée pour aarch64 et pour
  riscv64 (Linux), après une compilation de contrôle pour x86_64 avec le même outil et les options les plus proches de
  la construction publiée. Résultat par fichier : compile, ou refus (première erreur). Si le contrôle échoue, la
  compilation croisée n'est pas interprétée (cas attendu : C++, `std::simd` absent de la libc++). Prévision : un fichier
  compile si et seulement si l'examen statique ne trouve aucune ligne propre à une architecture dans le fichier entier ;
  un désaccord est examiné, et corrige la liste par un écart daté. Les autres langages sont classés par le seul examen
  statique, noté comme tel.

## 4. Indice d'accès

Pour le scénario de la section 5 (calcul 4) : pour un langage et une cellule, la cellule est **atteinte** si le temps
du plafond du langage y est à 0,9 ou plus de celui de la frontière (rapport frontière / langage, estimation
ponctuelle, calcul « Convergent, avec R4 » du point 4, K3 rapporté à b3) ; son **coût** vaut (s + u + p) / 3 (part des
lignes ajoutées, part absolue sans vérification, non-portabilité). L'**indice d'accès** du langage est la moyenne, sur
les 12 cellules, de 1 − coût pour les cellules atteintes et de 0 pour les autres : il vaut 1 pour un langage qui atteint
la limite de l'hôte partout avec son code naturel, sûr et portable, et 0 pour un langage qui ne l'atteint nulle part.
Le seuil de 0,9 est celui des tableaux d'écarts du point 4 (11.4).

## 5. Analyse, fixée avant le comptage

1. **Descriptif** (par langage et par cellule) : forme d'accès, L, N, L/N, lignes ajoutées, parts sans vérification
   (absolue, marginale), lignes propres à une architecture, portabilité ; résultats de compilation par fichier.
2. **Par langage** : moyenne géométrique de L/N sur les 12 cellules, total des lignes ajoutées, parts sans
   vérification et part propre à une architecture pondérées par les lignes, nombre de cellules non portables, indice
   d'accès.
3. **Relation avec la grille** : corrélation de rang (Spearman) sur les 25 langages entre chaque quantité de 2 et les
   scores des catégories C et E de la grille (règle v2), le pilier contrôle entier, et le plafond (calcul « Convergent,
   avec R4 » du point 4).
4. **Scénario « Accès »** (sensibilité, à côté du classement) : le calcul « Convergent, avec R4 » du point 4, où chaque
   capacité des catégories C et E de la grille prend la valeur de l'indice d'accès du langage (valeur mesurée, sans
   bruit de jugement), au centre et dans chaque variante ; même graine, mêmes tirages, mêmes poids des catégories.
   Sorties : places, rangs espérés, rangs plausibles (90 %), étages indicatifs, langages qui bougent de plus de deux
   places par rapport à « Convergent, avec R4 ».
5. **Sensibilités du scénario** : (a) part marginale au lieu de la part absolue ; (b) sans la part sans vérification
   (coût = (s + p) / 2) ; (c) seuil d'atteinte 0,8 ; (d) forme d'accès la plus courte à 10 % ou moins (3.1) ; (e) la
   grille entière remplacée par l'indice d'accès (pilier contrôle = 100 × indice).

Sorties : `results/cost/cost.json`, `results/report_cost.md` (`analysis/cost_v4.py`), `results/cost/regions.md`,
`results/cost/compile.txt`.

## 6. Publication

Le classement de tête du README ne change pas : le point 5 ne corrige rien de publié (`docs/V4_PLAN.md`). La mesure
et le scénario sont publiés à côté du classement (README, ce document). Remplacer une partie de la grille dans la
campagne finale serait un changement de règle : c'est une décision de l'auteur de l'étude, qui lui sera soumise avec
les résultats.

## 7. Ordre de travail

1. Ce plan, poussé.
2. Outils (retrait des commentaires, comptage des lignes et des lexèmes, recherche des constructions, contrôle du
   relevé), poussés avant tout comptage.
3. Relevé des régions, langage par langage dans l'ordre du classement publié, poussé par lots ; puis comptage.
4. Compilations pour aarch64 et riscv64.
5. Analyse (calculs 1 à 5), résultats (section 11 de ce document), README, `docs/V4_PLAN.md`, journal.
