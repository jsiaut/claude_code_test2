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

## 8. Règles de lecture du relevé (précisions de 3.2, fixées pendant le relevé, avant tout comptage)

Le relevé (`tools/cost/regions.py`) a été fait langage par langage, dans l'ordre du classement publié, et poussé en
sept lots le 22 novembre ; chaque lot est contrôlé par `tools/cost/count.py --check` (empreintes, bornes, fonctions
d'entrée, formes requises). Les cas que 3.2 ne tranche pas ont reçu une règle, appliquée à tous les langages :

* **Choix de la variante** : la ligne qui ne fait qu'appeler la fonction d'entrée d'une forme (avec ses arguments)
  appartient au harnais ; celle qui prépare un état propre à la forme, lance ou réveille des fils, ou combine leurs
  résultats appartient à la forme. En BQN, où le calcul tient souvent dans la ligne qui le passe au harnais
  (`{𝕤 ⋄ … } _bench @`), la ligne appartient à la forme quand elle contient le calcul.
* **Harnais** : la remise à zéro des compteurs de K3, la mesure du temps, la somme de contrôle et son formatage, les
  libérations faites après la mesure, la répétition de K5 (65 536 appels et la barrière d'optimisation) et
  l'itération de K9 (quatre pas et l'échange des grilles) n'appartiennent à aucune forme.
* **Conteneurs** : le chargement des données et le conteneur où le harnais les range, commun aux variantes,
  appartiennent au harnais ; un conteneur propre à certaines formes (tampon aligné, vue par pointeurs, colonnes
  transposées de K1, collection construite pour le seul naturel, grille à deux dimensions du naturel de K9, grille
  plate des formes optimisées, tampons partagés entre fils) appartient à ces formes, avec les fonctions qui le
  construisent.
* **Fonctions partagées** : une fonction appelée par la forme compte dans la forme ; une fonction qui sert plusieurs
  formes (travailleur commun de K6 à deux branches, réserve de fils, aide d'alignement) compte entière dans chacune,
  mais seules les fonctions appelées sur le chemin de la forme s'y ajoutent (la branche Q1 d'un travailleur commun
  n'ajoute pas Q1 tuned à la forme Q6).
* **État du harnais** : le compteur de valeurs de K8, que le harnais remet à q à chaque requête, appartient au
  harnais, qu'il soit une variable locale, un champ statique ou une classe (Python, PHP).
* **Constantes** : les constantes de taille du problème (N1, N6, ITER3, M9, `K7_LOG` et `K8_REQ` de Julia…)
  appartiennent au harnais ; les constantes propres à une forme (capacité et lot de la table de K7, déclarés pour la
  forme) lui appartiennent.
* **Déclarations** : là où les variables locales se déclarent à part (FreePascal), une ligne de déclaration compte
  dans une forme quand tous les noms qu'elle déclare ne servent qu'à elle. L'unité `msvec` de FreePascal, écrite pour
  les seules formes vectorielles (option `-Sv`), compte dans chacune : cadre, directives, types vectoriels et
  déclaration d'interface de sa fonction.
* **Directives et attributs** : les directives d'import et d'inclusion n'appartiennent à aucune forme ; les attributs
  et pragmas d'une fonction de la forme (`#[inline(never)]`, `@inline(.never)`, `{-# NOINLINE #-}`, `//go:noinline`)
  et ses gardes (profondeur des piles de K8 tuned_it) lui appartiennent ; les déclarations écrites pour une forme
  (intrinsèques importés, types vectoriels, pragmas qui coupent les vérifications) appartiennent aux formes qui les
  emploient.
* **Code exécuté ailleurs** : le code des Workers de JavaScript (même fichier : la branche de son noyau et le cadre côté
  Worker), le code des sous-interpréteurs de Python (chaînes `setup` et `K9_SUB`) et la fonction de mesure propre à
  K9 mt de PHP (dont seul le mécanisme des processus est retenu) comptent dans les formes à plusieurs fils.
* **Code généré** : l'IR de Q1 `tuned_v` de Julia a été écrit par un générateur (`tools/converge/gen_julia_ir.py`) ;
  il compte tel qu'il figure dans la source (11 donne aussi la part de lignes ajoutées avec le générateur à sa place).

## 9. Outils (poussés avant le comptage)

* `tools/cost/lex.py` : retrait des commentaires par langage (chaînes gardées ; une chaîne de documentation seule dans
  son instruction compte comme commentaire ; directives gardées comme code : `!$` de Fortran, `{-# #-}` de Haskell,
  `{$ }` de FreePascal, `#[ ]` de PHP, `//go:` de Go), lignes de code, lexèmes ;
* `tools/cost/patterns.py` : listes de 3.4 et 3.5, avec la portée de chaque construction ;
* `tools/cost/needed.py` : formes requises (forme d'accès, candidates à 10 %, références naturelles), d'après la
  campagne du point 4 ;
* `tools/cost/regions.py` : relevé des régions (25 langages) ;
* `tools/cost/count.py` : contrôle du relevé (`--check`) et comptage (`results/cost/counts.json`, `regions.md`,
  `matches.md`) ;
* `tools/cost/xcompile.sh` : compilations pour aarch64 et riscv64 (`results/cost/compile.txt`) ;
* `analysis/cost_v4.py` : calculs 1 à 5 (`results/cost/cost.json`, `results/report_cost.md`).

## 10. Écarts datés (22 novembre, avant tout comptage)

1. **Barrières de compilateur vides** (3.5) : `asm volatile("" : … : "memory")` (macros `BARRIER` et `KEEP` du harnais
   de C, fonctions `opaque` et `keep` de C++) n'émet aucune instruction et n'est propre à aucune architecture ; ces
   lignes sont écartées de la liste (elles restent dans `results/cost/matches.md`, marquées).
2. **C#, `unsafe` de classe** (3.4) : la copie déclare `static unsafe class Ms`. Ce modificateur n'est ni un bloc ni
   une méthode et n'ouvre pas de portée (sinon toutes les lignes, naturel compris, compteraient), mais il rend toutes
   les méthodes de la classe « unsafe » au sens du langage : aucune n'a besoin du mot. Lecture retenue : une méthode
   dont la signature déclare un type pointeur (paramètre ou résultat) est une méthode `unsafe` (portée : la méthode) ;
   une ligne qui déclare ou convertit un type pointeur (`float*`, `(double*)`) porte une construction de la liste.
   Limite connue : une ligne qui écrit par un pointeur déclaré plus haut, dans une méthode sans pointeur dans sa
   signature, n'est pas comptée (un cas : la préparation de K1 soa).
3. **Julia, `llvmcall`** (3.4) : ajouté à la liste ; portée : la ligne et la chaîne d'IR de LLVM qu'il reçoit, qui
   s'exécute sans aucune vérification. Sans cet ajout, les formes vectorielles de Julia (K4, K5, Q6, Q1, K9)
   n'auraient compté que leurs appels à `pointer(`.
4. **Mojo, `UntrackedOrigin`** (3.4) : ajouté (pointeurs `Pointer[T, MutUntrackedOrigin]`, dont ni la durée de vie
   ni les bornes ne sont vérifiées).
5. **Lexèmes des chaînes sur plusieurs lignes** (3.3) : une chaîne sur une ligne reste un lexème ; le texte d'une
   chaîne sur plusieurs lignes est découpé ligne par ligne comme du code. C'est du code que le programmeur écrit :
   l'IR de LLVM en Julia, le code des sous-interpréteurs en Python. Ses lignes comptaient déjà (une chaîne n'est pas
   un commentaire).
6. **Go, `//go:`** (3.3) : les directives de compilation de Go comptent comme code, comme les pragmas des autres
   langages (`{-# #-}`, `{$ }`, `!$`, `#[ ]`).

## 11. Résultats (22 novembre, après le comptage)

*Sorties : `results/cost/counts.json`, `results/cost/regions.md`, `results/cost/matches.md` (`tools/cost/count.py`),
`results/cost/compile.txt` (`tools/cost/xcompile.sh`), `results/cost/cost.json` et `results/report_cost.md`
(`analysis/cost_v4.py`). Le classement de tête du README ne change pas.*

### 11.1 Relevé et comptage

562 formes, dans 618 régions (1 115 intervalles de lignes) des 25 copies `_cv`, relevées dans l'ordre du classement
et poussées en sept lots, chacun contrôlé avant le lot suivant ; comptage le 22 novembre à 6 h 14, après les écarts
de la section 10. Le comptage lui-même prend deux secondes : tout le travail est dans la délimitation des régions.

### 11.2 Examen des occurrences

Les 2 004 occurrences trouvées dans les fichiers entiers (1 230 constructions qui contournent une vérification, dont
795 dans une région ; 774 constructions propres à une architecture, dont 751 dans une région) ont été examinées
(`results/cost/matches.md`). Elles appartiennent toutes aux familles des listes, avec deux réserves :

* **Faux positifs sans effet** : cinq `^` de FreePascal dans des chaînes de format (« 4x2^25 »), hors de toute région.
  Les motifs s'appliquent aussi aux chaînes, à dessein : les noms des intrinsèques importés par Nim (`importc`) et
  Chapel (`extern`) n'y figurent que dans des chaînes.
* **Correction de l'outil** : en Ada, un `pragma Suppress` placé dans un bloc `declare` (K7 tuned) ne s'applique qu'à ce
  bloc, et non à toute la procédure (branche naturelle comprise) ; les en-têtes `overriding procedure` n'étaient pas
  reconnus. Corrigé (`count.py`, `scope_unit`) ; effet : la forme naturelle de K7 d'Ada perd 14 lignes comptées à tort
  sans vérification, et aucune forme d'accès ne change.

Recherche complémentaire dans les langages où l'examen statique ne trouve aucune construction propre à x86 (Zig, Odin,
C3, Fortran, Julia, Mojo, Swift, FreePascal, Haskell, OCaml, Java, JavaScript, Python, Lua, PHP, BQN) : les mots x86,
AVX, SSE, amd64, pause, cpuid, popcnt et voisins n'apparaissent dans le code d'aucun d'eux, sinon dans `assert`,
`isset` et `Atomics.pause` (API portable de JavaScript).

### 11.3 Compilation pour aarch64 et riscv64

| Langage | Contrôle x86_64 | aarch64 | riscv64 | Prévision statique | Cause du refus |
|---|---|---|---|---|---|
| C | compile | refus | refus | refus | `immintrin.h` (hors x86) |
| C++ | refus | – | – | refus | contrôle : `std::simd` absent de la libc++ de LLVM ; examen statique seul |
| Zig | compile | compile | compile | compile | |
| Go | compile | refus | refus | refus | `simd/archsimd` : `archsimd.BroadcastFloat64x8` non défini pour arm64 et riscv64 |
| D | compile | refus | refus | refus | le seul builtin x86 (`__builtin_ia32_psadbw512`, K4 tuned) : sans lui, le fichier compile pour les deux cibles |
| Odin | compile | compile | compile | compile | |
| C3 | compile | compile | compile | compile | |
| Nim | compile | refus | refus | refus | `immintrin.h` (intrinsèques importés) |
| Fortran | compile | compile | compile | compile | |
| Mojo | compile | compile | compile | compile | |

Les 18 compilations interprétées (9 langages, 2 cibles ; C++ n'est pas interprété, son contrôle échouant) donnent
toutes le résultat prévu par l'examen statique du fichier entier : aucun désaccord, donc aucun écart sur la liste
de 3.5. Réglages de l'outil (`tools/cost/xcompile.sh`,
avant l'exécution retenue) : flang-23 ne livre ses modules intrinsèques (`iso_fortran_env`, `iso_c_binding`,
`omp_lib`) que pour x86_64, et suppose OpenMP 3.1 quand gfortran suppose 5.x ; les modules de l'installation x86_64 et
`-fopenmp-version=52` sont donnés pour les trois cibles. Mojo prend son processeur par défaut (l'hôte), `native`
n'étant pas un nom accepté. C++ et les langages sans chaîne croisée hors ligne sont classés par l'examen statique
seul. Cellules non portables (forme d'accès portant une construction propre à x86), tous langages : C 9, Nim 9
(intrinsèques importés de `immintrin.h`), Rust 9 (`std::arch`, `#[target_feature]`), Chapel 8 (intrinsèques
déclarés `extern`), Go 7 (`simd/archsimd`), C# 6 (`Avx512F`, `Avx512BW`, `Sse`), Ada 6 (`__builtin_ia32_…`), C++ 1
(K4 tuned, intrinsèques), D 1 (K4 tuned) ; aucune en Zig, Odin, C3, Fortran, Mojo, Swift, Julia, Java, Haskell,
FreePascal, OCaml et dans les langages interprétés.

### 11.4 Par langage (calcul 2)

| Langage | Cellules atteintes | L/N | Lignes ajoutées | Sans vérif. (abs.) | Sans vérif. (marg.) | Non portables | Indice d'accès |
|---|---|---|---|---|---|---|---|
| Mojo | 8 | 2,33 | 189 | 0,16 | 0,16 | 0 | 0,497 |
| Odin | 8 | 3,73 | 318 | 0,50 | 0,50 | 0 | 0,402 |
| C3 | 8 | 3,70 | 476 | 1,00 | 0,00 | 0 | 0,314 |
| C++ | 7 | 3,45 | 295 | 1,00 | 0,00 | 1 | 0,285 |
| Julia | 5 | 6,45 | 1 020 | 0,87 | 0,87 | 0 | 0,271 |
| Swift | 4 | 3,20 | 411 | 0,33 | 0,33 | 0 | 0,243 |
| Java | 3 | 4,81 | 313 | 0,00 | 0,00 | 0 | 0,240 |
| Nim | 8 | 6,88 | 560 | 0,39 | 0,39 | 9 | 0,239 |
| Zig | 6 | 3,71 | 391 | 1,00 | 0,01 | 0 | 0,239 |
| Rust | 8 | 5,14 | 549 | 0,39 | 0,39 | 9 | 0,218 |
| Chapel | 8 | 3,82 | 329 | 1,00 | 0,16 | 8 | 0,169 |
| C# | 3 | 3,66 | 253 | 0,27 | 0,27 | 6 | 0,168 |
| Ada | 5 | 3,62 | 568 | 0,50 | 0,50 | 6 | 0,164 |
| D | 5 | 5,39 | 375 | 1,00 | 0,06 | 1 | 0,163 |
| C | 9 | 3,52 | 318 | 1,00 | 0,00 | 9 | 0,160 |
| Fortran | 3 | 1,87 | 120 | 1,00 | 0,00 | 0 | 0,130 |
| Go | 3 | 2,61 | 262 | 0,00 | 0,00 | 7 | 0,116 |
| FreePascal | 1 | 4,16 | 722 | 1,00 | 0,03 | 0 | 0,056 |
| Haskell | 1 | 2,35 | 156 | 0,25 | 0,25 | 0 | 0,052 |
| OCaml, JavaScript, Python, Lua, BQN, PHP | 0 | 1,30 à 3,33 | 22 à 245 | 0 à 0,19 | 0 à 0,19 | 0 | 0 |

L/N : moyenne géométrique sur les 12 cellules ; parts pondérées par les lignes. Détail par cellule :
`results/report_cost.md`.

* **Atteindre le plafond coûte des lignes partout.** La forme d'accès a 3,5 fois les lignes du code naturel en
  moyenne géométrique médiane (1,3 en Lua à 6,9 en Nim) ; dans les 103 cellules atteintes, la part de lignes ajoutées
  médiane est 0,69. Sept cellules seulement ont le code naturel pour forme d'accès (K9 en Java, Fortran, Python et
  Lua ; Q1 en JavaScript et Lua ; K4 en BQN). L'indice d'accès est donc bas partout : 0,50 au plus (Mojo).
* **Le prix n'est pas le même.** Mojo atteint 8 cellules avec le moins de lignes ajoutées des sept langages qui en
  atteignent 8 ou plus (189 ; L/N 2,33), sans construction propre à une architecture (ses `SIMD[...]` compilent pour
  aarch64 et riscv64) et avec peu de code sans vérification (0,16) ; Odin et C3 atteignent aussi 8 cellules sans code
  non portable, C3 sans aucune vérification (mode publié). C atteint le plus de cellules (9), mais tout son code est
  sans vérification et 9 de ses 12 formes d'accès (dont 7 des 9 cellules atteintes) portent des intrinsèques x86 :
  indice 0,16. Rust et Nim atteignent 8 cellules, avec des intrinsèques x86 dans 9 de leurs 12 formes d'accès (dont 7
  et 6 des cellules atteintes) ; Julia paie ses formes vectorielles en IR de
  LLVM (L/N 6,45, part sans vérification 0,87). Java, Go et C# atteignent 3 cellules ; Java sans aucune ligne sans
  vérification ni propre à une architecture.
* **Là où le mode publié vérifie, le code rapide contourne souvent la vérification** : part sans vérification de
  0,87 en Julia (`@inbounds`, IR de LLVM), 0,50 en Odin et en Ada, 0,39 en Rust et en Nim, 0,33 en Swift, 0,27 en C#,
  0,25 en Haskell et 0,19 en OCaml (primitives `unsafe…`) ; 0 en Java, en Go et dans les langages interprétés. La
  part marginale des huit langages sans vérification dans leur mode publié est proche de 0 (0,16 au plus, Chapel,
  `c_ptr`) : leur code rapide n'a rien à contourner.
* **Julia, Q1** : avec le générateur de l'IR (213 lignes) à la place de l'IR (321), la part de lignes ajoutées passe de
  0,97 à 0,96.

### 11.5 Relation avec la grille (calcul 3)

| Quantité | Catégorie C | Catégorie E | Pilier contrôle | Plafond (avec R4) |
|---|---|---|---|---|
| L/N (moyenne géométrique) | 0,54 | 0,59 | 0,58 | 0,60 |
| lignes ajoutées | 0,55 | 0,66 | 0,65 | 0,58 |
| part sans vérification (absolue) | 0,64 | 0,70 | 0,76 | 0,78 |
| part sans vérification (marginale) | 0,37 | 0,51 | 0,34 | 0,24 |
| part propre à une architecture | 0,45 | 0,45 | 0,44 | 0,54 |
| cellules non portables | 0,47 | 0,47 | 0,46 | 0,52 |
| indice d'accès | 0,69 | 0,68 | 0,71 | 0,73 |

Sur les 25 langages, l'indice d'accès suit la grille et le plafond (ρ 0,68 à 0,73), mais par les six langages qui
n'atteignent aucune cellule (indice 0, et grille basse) : sur les 19 autres (information hors plan), ρ vaut 0,30
(catégorie C), 0,38 (E), 0,36 (pilier contrôle) et 0,41 (plafond). Parmi les langages qui atteignent le plafond,
l'indice mesure donc autre chose que les catégories C et E : non pas les leviers qu'un langage offre, mais ce que coûte
de s'en servir. La part absolue sans vérification suit le pilier contrôle (0,76 ; 0,53 sur 19) et le plafond (0,78 ;
0,59) : les langages que la grille et le plafond classent le plus haut sont ceux dont le code rapide s'exécute sans
vérification.

### 11.6 Scénario « Accès » (calculs 4 et 5)

Contrôle : « Convergent, avec R4 », refait par `analysis/cost_v4.py`, est identique à celui du point 4 (même ordre,
écarts nuls).

| Publié | Langage | Convergent, R4 | Accès | (a) marginale | (b) sans u | (c) seuil 0,8 | (d) la plus courte | (e) grille entière | (f) lexèmes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C | 3 | 4 | 3 | 4 | 4 | 4 | 8 | 4 |
| 2 | Odin | 5 | 3 | 5 | 5 | 2 | 3 | 1 | 3 |
| 3 | C++ | 1 | 2 | 1 | 1 | 3 | 2 | 3 | 2 |
| 4 | C3 | 4 | 5 | 4 | 3 | 5 | 5 | 2 | 5 |
| 5 | Zig | 2 | 1 | 2 | 2 | 1 | 1 | 5 | 1 |
| 6 | Rust | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |
| 7 | Nim | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| 8 | D | 8 | 8 | 9 | 8 | 8 | 9 | 12 | 8 |
| 9 | Ada | 10 | 12 | 12 | 12 | 13 | 12 | 15 | 12 |
| 10 | Chapel | 9 | 9 | 8 | 9 | 9 | 8 | 10 | 9 |
| 11 | Fortran | 11 | 11 | 11 | 11 | 12 | 11 | 14 | 11 |
| 12 | Swift | 14 | 13 | 13 | 14 | 10 | 13 | 11 | 13 |
| 13 | Julia | 12 | 14 | 14 | 13 | 14 | 14 | 9 | 14 |
| 14 | Mojo | 13 | 10 | 10 | 10 | 11 | 10 | 4 | 10 |

Les onze suivants restent à deux places au plus de leur rang de « Convergent, avec R4 » dans chacun de ces calculs,
sauf Java (16e → 13e) quand la grille entière est remplacée.

* **Remplacer les catégories C et E par l'indice ne déplace qu'un langage de plus de deux places** : Mojo, 13e → 10e.
  Zig passe 1er (rang espéré 2,83) devant C++ (2,97), Odin 3e (3,60, contre 5,39), C 4e (3,98, contre 2,88). Les
  scores au centre baissent de 0 (Lua) à 8,8 points (D ; C − 8,6, C++ − 7,5), médiane − 3,2 : l'indice (0,50 au plus)
  est plus bas que les notes des catégories C et E qu'il remplace, sauf la note E de Java (7,1 sur 100 ; indice 0,24) ;
  en Lua, les trois valent 0.
* **Sensibilités** : avec la part marginale, sans la part sans vérification, avec la forme la plus courte à 10 % ou
  avec les lexèmes, Mojo (13e → 10e) reste le seul langage à bouger de plus de deux places, et aucun n'est à plus de
  deux places de sa place dans « Accès ». Le seuil de 0,8 déplace Odin (5e → 2e), Swift (14e → 10e) et Ada (10e → 13e) ;
  Mojo y gagne deux places (11e). Remplacer la grille entière par l'indice bouleverse le haut : Odin 1er, C3 2e, C++ 3e,
  Mojo 4e, Zig 5e, C 8e, D 12e, Ada 15e.

### 11.7 Ce que cela change

* **Le classement publié ne change pas** (section 6).
* **La décision de remplacer une partie de la grille revient à l'auteur de l'étude.** Les faits utiles : remplacer les
  catégories C et E par l'indice déplace un seul langage de plus de deux places ; l'indice ne compte que les cellules
  atteintes, donc une part du plafond (40 % du score), déjà compté, entre une seconde fois dans le pilier contrôle ;
  la part sans vérification vaut 1 par construction dans huit langages, ce qui fait d'une propriété du mode publié un
  coût de chaque forme ; parmi les 19 langages qui atteignent le plafond, l'indice ne suit les catégories C et E que de
  loin (ρ 0,30 et 0,38) : il ne les remplace pas, il mesure autre chose. Le point 5 recommande de publier l'indice à
  côté de la grille plutôt qu'à sa place.
* **Décision de l'auteur de l'étude (22 novembre) : la grille est gardée** dans la campagne finale ; l'indice d'accès
  est publié à côté (README, section du point 5).
