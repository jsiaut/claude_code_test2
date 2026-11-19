# Audit de la grille : une sonde par case (v4, point 1)

*Plan : `docs/V4_PLAN.md`, section 2, poussé avant tout travail. Outils : `tools/grid_audit/` (motifs de recherche fixés
d'avance, `search.py`), `analysis/grid_audit.py` (confrontation des sondes à la matrice v1 et v2, classes de preuve).
Sorties : `results/probes/<langage>.txt`, `results/grid_audit/summary.md`, `results/grid_audit/search/` (détail de chaque
recherche d'absence). Ce document est rempli langage par langage ; les errata sont appliqués ensemble à la fin.*

## 1. Méthode

* **Classes de preuve.** [exécutée] : un programme se sert de la capacité et imprime un fait observable (taille,
  décalage, adresse modulo, valeur, fil, instruction du code produit, attribut de l'IR) ; pour ½, la limite est montrée
  aussi. [échec] : la forme canonique est tentée et le refus du compilateur (ou l'erreur à l'exécution) est imprimé, ou
  le comportement contraire est mesuré (taille d'un agrégat sur le tas, ordre d'une somme gardé). [recherche] : les
  sources livrées de la bibliothèque standard (ou la liste de ses API publiques) sont fouillées avec le motif de la
  case (`tools/grid_audit/patterns.json`) ; chaque déclaration publique trouvée est examinée, et l'examen est écrit
  dans la ligne de la sonde. C3 reste [mesurée].
* **Note.** La sonde imprime la note de la règle v2 (score central) ; quand v1 diffère, la ligne le dit.
  `analysis/grid_audit.py` compare chaque ligne à la matrice et liste les divergences.
* **Contre-épreuves.** Quand une capacité notée ½ ou 0 existe sous une forme exclue par la règle (canal instable,
  unité interne, FFI), la sonde l'exécute aussi et l'imprime en ligne NOTE : le fait est établi, la note suit la règle.
  Une case où la règle elle-même hésite est listée en section 3 avec l'effet des deux notes.
* **Écarts au plan.** (1) Après la première recherche (Rust), les fichiers `tests.rs` ont été ajoutés aux exclusions de
  Rust (modules de test, pas des API publiques) et le détail des recherches liste désormais les lignes de mention ; les
  motifs des cases n'ont pas changé.

## 2. Résultats par langage

### Rust (rustc 1.99.1 stable ; nightly 1.101.0 du 27 octobre pour les contre-épreuves)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice. Sondes : `probes/rust/probe.rs` (A5, E2) et
`probes/rust/audit/` (`audit.rs` exécuté, `codegen.rs` lu en assembleur et en IR, trois échecs sur le canal stable,
`nightly.rs` pour les contre-épreuves, sept recherches dans `std`, `core` et `alloc` de rust-src 1.99.1).
* Faits notables : `repr(Rust)` réordonne (u8, f64, u8) en 16 octets, `repr(C)` garde 24 ; `cold_path` pose des
  poids de branchement dans l'IR ; `algebraic_add` vectorise une somme (7 `vaddps` sur ymm/zmm contre 9 `vaddss` en
  chaîne) ; `get_unchecked` retire l'appel à `panic_bounds_check` ; `slice::sort` alloue un tampon pour 100 000
  éléments (tri stable, allocation documentée : B4 reste 1).
* Contre-épreuves (nightly) : `Vec::with_capacity_in` dans une arène (B2), `std::simd::f32x8` (C1), et, par le crate
  `libc` du sysroot (`#![feature(rustc_private)]`), `sched_setaffinity` (fil épinglé sur le CPU 1) et `mmap` d'un
  fichier relu comme `&[f32]` sans copie (D4, F4).

### Zig (0.17.0, compilateur du banc)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (D4 vaut 1 en v2, ½ en v1). Sondes :
`probes/zig/probe.zig` et `probe_f4.zig` (A2 à A5, D3, F4), `probes/zig/audit/` (`audit.zig` exécuté, `codegen.zig`
lu en assembleur et en IR, en ReleaseFast et en ReleaseSafe pour E6, deux échecs, quatre recherches dans `lib/std`).
* Faits notables : `std.MultiArrayList` range chaque champ dans son propre tableau (A6) ; `@setFloatMode(.optimized)`
  pose `fadd fast` sur la seule portée visée (C4), mais aucune somme n'est vectorisée en 0.17, son vectoriseur de
  boucles étant coupé ; `@branchHint(.unlikely)` pose des poids 1:2000 et sort l'appel du chemin chaud, alors que
  `@branchHint(.cold)` n'a aucun effet visible en ReleaseFast (ni poids, ni déplacement) ; `@setRuntimeSafety(false)`
  retire la panique `outOfBounds` d'une fonction compilée en ReleaseSafe (E6) ; `@fence` n'existe plus (D5 ½).
* Contre-épreuve (C2) : une fonction externe nommée `@"llvm.x86.avx512.pternlog.d.512"` appelle l'intrinsèque de
  LLVM (un `vpternlogd` dans le code produit), comme le `foreign` d'Odin ; mais ni le manuel de Zig (`langref.html`,
  qui ne parle d'intrinsèques que pour Wasm) ni sa bibliothèque ne l'emploient : C2 reste ½ (section 3).

### Odin (dev-2026-10:84bc3fc, compilateur du banc)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (C2, D4 et F4 valent 1 en v2, ½ en v1). Sondes :
`probes/odin/probe.odin` (A2, A3, A5), `probes/odin/audit/` (`main/audit.odin` exécuté, `codegen/codegen.odin` lu en
assembleur et en IR, deux échecs, cinq recherches dans `core` et `base`).
* Faits notables : `#soa[]Part` range chaque champ dans son propre tableau (A6) ; `context.allocator` remplacé par une
  arène sur un tampon de pile reçoit les `make` et les `append` (B2) ; l'assembleur en ligne est désormais fait de
  « procédures assembleur » (`asm(a: i64, b: i64) -> (r: i64) { mov r, a; add r, b; }`) ; `intrinsics.expect` sort
  l'appel du chemin chaud (E3) ; une procédure polymorphe est instanciée par type, mais `F60 :: fib(60)` est refusé
  (« not a compile-time known constant ») : pas d'exécution à la compilation (E7 ½).
* `@(fast_math = {...})` est accepté avec tous ses drapeaux, mais l'IR n'en porte aucun (le défaut relevé par la
  remarque sur Odin, corrigé après dev-2026-10) : C4 reste 0, prouvé par l'échec.
* Contre-épreuve (F2) : `linux.syscall(SYS_mbind, …)` pose une politique `MPOL_BIND` relue par `get_mempolicy` ;
  `core:sys/linux` ne livre que les numéros d'appels système, sans procédure dédiée (section 3).

### C3 (0.8.5_1, compilateur du banc, `--x86cpu=native`)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (F4 vaut 1 en v1 comme en v2). Sondes :
`probes/c3/probe.c3` (A2, A3, A5), `probes/c3/audit/` (`audit.c3` exécuté, `codegen.c3` lu en assembleur et en IR, en
-O3, en -O1 pour E6 et avec `--fp-math=relaxed` pour C4, deux contre-épreuves de C2, les sept essais d'assembleur de la
remarque sur C3, sept recherches dans `lib/std`).
* Faits notables : `mem::new` est refusé à la compilation pour un type sur-aligné (`new_aligned` l'alloue à 0 mod 64) ;
  une macro à boucle `$for` calcule fib(60) à la compilation (une constante immédiate dans l'asm) et `gsum{float}`,
  `gsum{double}` donnent deux fonctions (E7) ; `@unlikely` sort l'appel du chemin chaud ; en mode sûr, `a.ptr[i]`
  retire la comparaison à la longueur mais garde le contrôle d'alignement.
* Défauts reproduits : `@noalias` sur le 2e paramètre pose `noalias` sur le 1er (E5 ½) ; les blocs `asm` refusent
  `vfmadd231ps`, `pause`, `mfence` et un `vmovaps` depuis la mémoire, mais acceptent `vaddps` entre registres (E2 ½) ;
  `extern … @cname("llvm.…")` lie `llvm.x86.sse2.pause` mais laisse `llvm.x86.bmi.pext.32` non résolu et fait échouer
  `llvm.x86.avx512.pternlog.d.512` (« Cannot select »), les vecteurs passant par l'ABI C (C2 ½) ; la réassociation
  n'existe qu'en option globale (`--fp-math=relaxed` : 9 `fadd reassoc` vectorisés contre 9 stricts ; C4 ½).
* D3 : la bibliothèque ne livre que les clés sysctl `HW_CACHELINE` de macOS, rien sous Linux (0).

### D (LDC 1.43.0, compilateur du banc, -O3 -mcpu=native)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (C2, C4, D4 et E5 valent 1 en v2, ½ en v1). Sondes :
`probes/d/probe.d` et `probe_errata.d` (A2 à A5, F4), `probes/d/audit/` (`audit.d` exécuté, `codegen.d` lu en
assembleur et en IR, avec et sans `-boundscheck=on`, deux échecs, trois recherches dans druntime, Phobos et `ldc`).
* Faits notables : 200 allocations de 1 Mio déclenchent 100 collectes du ramasse-miettes, et `new` est refusé dans une
  fonction `@nogc` (B1 ½) ; une fermeture rendue par une fonction, un littéral de tableau rendu et une concaténation
  `~=` allouent sur le tas du GC (16, 16 et 32 octets, B4 ½), mais LDC supprime ces allocations quand rien ne
  s'échappe ; `Region` de `std.experimental.allocator` sert un tampon de pile (B2 ½, module expérimental) ;
  `std.parallelism` répartit un `foreach` sur quatre fils et réduit en parallèle (C5) ; `enum F60 = fib(60)` est
  calculé par CTFE (une constante immédiate) ; `new float[4][](5)` donne des lignes contiguës, mais la dimension
  intérieure reste fixée à la compilation (F1 ½).
* `core.builtins.expect(cond, false)` pose des poids et sort l'appel du chemin chaud, mais `core.builtins.unlikely`,
  son enveloppe `inline`, perd l'indication sous LDC -O3 (ni poids, ni déplacement) : E3 reste 1 par `expect`.
* Erreur de sonde corrigée en cours de route : des fermetures créées dans une boucle `foreach` partagent leur
  contexte (le défaut de capture que la matrice cite en B4) ; la sonde des fils passe donc par une fonction.

### Nim (2.2.12, C compilé par clang 23 comme au banc ; gcc 16 pour une contre-épreuve)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (C2 et E4 valent 1 en v2, ½ en v1). Sondes :
`probes/nim/probe.nim` (A2 à A5, F4), `probes/nim/audit/` (`audit.nim` exécuté avec `-d:nimAllocStats`,
`codegen.nim` désassemblé et son C relu, `fastsum.nim` compilé avec `-ffast-math` par `{.localPassC.}`, trois essais
OpenMP, les régions, les indications sous deux compilateurs C, cinq recherches dans `lib`).
* Faits notables : `=destroy` s'exécute à la sortie de portée sous ORC (B1) ; une fermeture, un ajout à une chaîne et
  un littéral `@[1, 2, 3]` allouent (1, 2 et 1 allocations comptées, B4 ½) ; `{.noalias.}` devient `NIM_NOALIAS`
  (`restrict`) dans le C ; `const F60 = fib(60)` est calculé par la VM du compilateur.
* B2 : sous `--mm:orc`, mode du banc et défaut de Nim 2, il n'y a qu'`alloc`/`dealloc` ; le mode `--mm:regions`, livré
  (`advopt.txt`), fournit des régions (`withRegion(MemRegion)`), que `--mm:orc` ignore : ½ (option globale seulement).
* C5 : l'itérateur `||` répartit une boucle sur quatre fils, mais seulement si les vérifications sont coupées dans le
  corps (sinon le C généré saute hors du bloc OpenMP et ne compile pas), et une réduction ne compile qu'avec une
  variable au nom C fixé (`{.exportc.}`) : ½ (sous-ensemble). Le texte de la matrice (« une réduction ne compile pas
  en -d:release ») est à préciser.
* E3 : `likely`/`unlikely` passent par une variable `NIM_BOOL` avant le test ; gcc 16, compilateur C par défaut de Nim
  (`config/nim.cfg`), en tient compte (`likely` ramène l'appel dans le chemin chaud), clang 23, celui du banc, non
  (même code avec `likely` et `unlikely`) : la note dépend du compilateur C (section 3).

### Ada (GNAT 16.2, compilateur du banc, -O3 -march=native)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (C1, C2, D2, D5, E3 et E4 valent 1 en v2, ½ en
v1). Sondes : `probes/ada/probe.adb` et `probe_errata.adb` (A2, A3, A5, B4, C1, D4, E5), `probes/ada/audit/` (`audit.adb`
exécuté, paquetage `Cg` lu en assembleur avec et sans `-ffast-math`, deux échecs, quatre recherches dans `adainclude` et
dans le manuel de GNAT, `gnat_rm.info`).
* Faits notables : un pool de stockage utilisateur attaché au type d'accès reçoit les `new` (B2) ; un tableau
  `(Positive range <>, Positive range <>)` aux bornes connues à l'exécution est contigu, par lignes, ou par colonnes
  avec `Convention => Fortran` (F1) ; une fonction d'expression `with Static` donne une constante immédiate (E7) ;
  `GNAT.Branch_Prediction.Likely`, unité livrée, ramène l'appel dans le chemin chaud (E3) ; `System.Mmap` projette un
  fichier, mais GNAT avertit lui-même qu'il s'agit d'une « internal GNAT unit » (F4 ½).
* C4 : `pragma Fast_Math` existe, mais c'est un pragma de configuration qui ne touche que la multiplication complexe ;
  la réassociation passe par l'option globale `-ffast-math` (½).
* C5 et F2 : `parallel for` ne compile pas (« missing ":" ») et le manuel note les itérateurs parallèles « Feature
  unimplemented » ; l'annexe E accepte `pragma Remote_Call_Interface`, mais « GNAT itself supports programs with only a
  single partition » : le PCS est dans PolyORB, produit séparé, sans `gnatdist` dans la chaîne (0 et 0).

### Fortran (gfortran 16.2, compilateur du banc, -O3 -march=native -fopenmp)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (A4, C4, D1, D2 et D4 valent 1 en v2 par OpenMP,
livré avec gfortran ; ½ en v1). Sondes : `probes/fortran/probe*.f90` (A3 à A5, B2, B5, C5, F2), `probes/fortran/audit/`
(`audit.f90` exécuté sous `OMP_PLACES={1}`, module `cg` lu en assembleur avec et sans `-fcheck=bounds`, témoin C pour
E5, trois échecs, dix recherches dans `gfortran.info` et `omp_lib.f90`).
* Faits notables : `!$omp atomic write release` donne un `mov`, `seq_cst` un `xchg` (D2) ; `!$omp simd reduction`
  vectorise une somme que la boucle ordinaire laisse en `vaddss` (C4) ; un tableau allouable `m(n, 4)` est contigu par
  colonnes (F1) ; une section non contiguë passée à un argument de forme explicite crée un temporaire, que
  `-fcheck=array-temps` signale à l'exécution (B4 ½) ; le type `unsigned` n'existe que sous `-funsigned` (F3 ½) ;
  `template` est refusé (E7 ½).
* E5 : la règle des arguments muets se voit dans le vectoriseur de GCC : la boucle Fortran est vectorisée sans
  version pour alias, la même boucle en C sur deux pointeurs l'est avec une.
* Motif propre à Fortran pour C2 (ajouté avant la recherche) : « intrinsic » désigne en Fortran toutes les procédures
  de la norme ; le motif cherche `_mm`, `avx`, `__builtin_ia32` et `sse` (aucun résultat). Un builtin lié par
  `bind(c)` reste un symbole externe non résolu.

### Chapel (2.10.0, compilateur du banc, --fast, CHPL_COMM=none, qthreads)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2. Sondes : `probes/chapel/probe.chpl` et
`probe_errata.chpl` (A2, A4, A5, B2, B3, C2, C4, E5 ; leurs IR, échecs et avertissements d'instabilité sont ceux de la
remarque sur Chapel, `results/chapel_check/`), `probes/chapel/audit/` (`audit.chpl` exécuté avec `--memTrack`,
procédures exportées désassemblées, une compilation `--fast --checks`, huit recherches dans `modules`).
* Faits notables : un `forall` se répartit sur quatre fils et `+ reduce` réduit en parallèle (C5) ; un tableau local
  `[0..<1000] real` alloue 8 200 octets sur le tas sans `new` (B4 ½) ; `blockDist` distribue un domaine (une seule locale
  ici, `CHPL_COMM=none` ; F2) ; `proc pfib(param n) param` est évaluée à la compilation (une constante immédiate,
  E7) ; avec `--checks`, `garr[i]` appelle `chpl_error` et `p[i]` sur un `c_ptr` non (E6).
* D4 ½ : l'exécutif qthreads place lui-même ses fils sur les cœurs (processeurs 0 à 3), réglable par variables
  d'environnement (`QT_WORKER_UNIT`), sans API pour épingler une tâche.
* F4 0 : `ioHintSet.mmap` n'est qu'une indication de lecture du module IO ; aucune projection n'est rendue au programme.

### Julia (1.13.3, julia du banc, -O3, 4 fils)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (C2, D5, E2 et E4 valent 1 en v2 par `llvmcall`,
½ en v1). Sondes : `probes/julia/probe.jl` et `probe_errata.jl` (A2, A5, B2, D3, E3, F4), `probes/julia/audit/`
(`audit.jl` exécuté avec `@code_native` et `@code_llvm`, `d4.jl` sous `JULIA_EXCLUSIVE=1`, `e3.jl`, quatre recherches
dans la liste des noms publics de Base, Core et des bibliothèques standard, obtenue par introspection :
`tools/grid_audit/listings/julia_names.jl`).
* Julia 1.13 exige pour `llvmcall` une intrinsèque la forme « module complet + point d'entrée » ; sous cette forme,
  `pternlog`, `pause`, `prefetch` et l'assembleur en ligne de l'IR passent (C2, D5, E2, E4), mais `llvm.expect` est
  perdu (aucun poids dans l'IR : E3 reste 0).
* Allocations, mesurées par appel avec résultats conservés (Julia 1.12+ supprime une allocation dont le résultat est
  jeté, ce qui fausse `@allocated`) : tuple et struct isbits 0 octet, petit tableau 80 (B3 ½) ; fermeture rendue 16
  octets, 32 avec une variable réaffectée (`Core.Box`), somme sur un `Vector{Any}` 15 504, mais une instabilité réduite
  à une petite union n'alloue plus (B4 ½ ; le texte de la matrice est à préciser).
* `@aliasscope`/`Const` retire les contrôles de recouvrement de la copie documentée (0 contre 5), pas ceux d'une mise à
  jour `y[i] += Const(x)[i]` (5) : effet partiel, module expérimental (E5 ½).
* D4 ½ : `JULIA_EXCLUSIVE=1` épingle les quatre fils sur les CPU 0 à 3 ; le seul nom public d'affinité,
  `Base.setcpuaffinity`, vise une commande lancée.

### Mojo (1.2.0, mojo build par défaut comme au banc ; bibliothèque standard de modular 26.7.0)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (C2 vaut 1 en v2 par `llvm_intrinsic`, ½ en v1).
Sondes : `probes/mojo/probe.mojo` et `probe_errata.mojo` (A4, A5, C4, D2, D5, E3, E5), `probes/mojo/audit/` (`audit.mojo`
exécuté, `codegen.mojo` et `checks.mojo` désassemblés, neuf recherches dans `std`).
* Faits notables : `reflect[Part].field_offset` donne les décalages à la compilation (A2) ; une fonction à structures,
  SIMD et fermeture capturante ne contient aucun appel, donc aucune allocation (B4) ; `l[i]` sur une `List` appelle
  `_debug_assert_fail` (assertions actives par défaut) et `unsafe_get` non (E6) ; `comptime F60 = fib(60)` est une
  constante immédiate (E7).
* D1 ½ : il n'y a pas d'API publique de fils ; `create_task` du module privé `std.runtime._asyncrt` fait tourner
  quatre tâches sur quatre fils. D4 0 : seul `_create_task(desired_worker_id)` existe, « intentionally not part of the
  public API », et vise un travailleur, pas un CPU. C5 0 : `parallelize` est dans `max.algorithm`, hors de `std`.

### C (clang 23.1.5, glibc 2.39 ; options du banc) et C++ (g++ 16.2, libstdc++)

33 cases sondées chacun (C3 mesurée), aucune divergence avec la matrice v2. Les premières sondes (`probe.c`,
`probe.cpp`) imprimaient surtout des lignes déclaratives et les notes v1 ; l'audit les remplace (`probes/c/audit/`,
`probes/cpp/audit/` : programme exécuté, code produit lu en assembleur et en IR, échecs, recherches dans les en-têtes de
la glibc, de clang et de libstdc++).
* C : `mallinfo2` ne voit aucune allocation pour `qsort`, des copies de structures, des littéraux composés et un
  `snprintf` dans un tampon de pile (B4) ; un tableau `float (*m)[cols]` aux deux dimensions connues à l'exécution est
  contigu (F1, types à dimension variable du C99) ; `constexpr` refuse un appel de fonction (E7 ½) ;
  `__attribute__((soa))` est un attribut inconnu (A6). B2 reste ½, mais la glibc livre une arène, `obstack` : le texte
  « arènes à écrire soi-même » est à corriger (section 3).
* C++ : une capture de 64 octets fait allouer `std::function`, un `throw std::runtime_error` alloue son message, rien
  pour `std::sort` ou une lambda (B4 ½) ; `std::pmr::monotonic_buffer_resource` sur un tampon de pile sert un
  `std::pmr::vector` (B2) ; `std::mdspan` aux dimensions connues à l'exécution (F1) ; `[[likely]]` ramène l'appel dans
  le chemin chaud ; `__restrict__` supprime la version pour alias du vectoriseur.
* C4 de C++ : `std::reduce(std::execution::unseq, …)` autorise la réassociation, mais g++ 16 ne vectorise pas cette
  somme, même avec `-fopenmp-simd` ; `#pragma omp simd reduction(+:s)` la vectorise. C4 reste 1 (OpenMP, livré), le
  texte de la matrice (« std::reduce… ordre libre explicite ») est à préciser.

### Swift (6.4.2, swiftc du banc : -swift-version 6 -O -target-cpu native)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (D4 vaut 1 en v2 par le module Glibc livré, ½ en
v1). L'audit (`probes/swift/audit/` : programme exécuté, code produit, deux formes refusées, recherches dans les
interfaces `.swiftinterface` livrées et dans les symboles de Foundation et de Dispatch extraits par
`swift-symbolgraph-extract`) complète la première sonde (`base.sh`).
* Faits notables : `withUnsafeTemporaryAllocation` sert un tampon sur la pile, à 944 octets d'une variable locale (B3) ;
  un `[any Shape]` met une structure de 64 octets dans une boîte sur le tas sans allocation écrite (B4 ½) ;
  `a[i]` garde deux pièges `ud2` en `-O`, `withUnsafeBufferPointer` aucun (E6) ; le module Clang non documenté
  `_Builtin_intrinsics.intel` produit un `vaddps` pour `_mm512_add_ps`, mais les fonctions intégrées sans corps (pause,
  préchargement) ne se lient pas et les macros à immédiat sont refusées (C2 ½) ; pause et préchargement ne passent que
  par l'attribut souligné `@_silgen_name("llvm.…")` (D5 ½, E4 ½).
* E5 ½ : l'exclusivité des `inout` est une règle du langage, exploitée par l'optimiseur SIL, mais l'IR de
  `two(_:_:)` ne porte aucun `noalias`. D4 : comme en C, `sched_setaffinity` demande `_GNU_SOURCE` (`-Xcc
  -D_GNU_SOURCE`).
* Recherches : B2 trouve 399 déclarations publiques, 386 pour `region` (`Locale.Region`…), 13 `Deallocator` (rappel de
  libération d'octets fournis par l'appelant) et `UnitArea.squareNanometers`, aucune interface d'allocateur (B2 reste
  ½ par l'arène écrite sur `UnsafeMutableRawPointer.allocate`) ; F2 trouve 688 déclarations, toutes sur la locale de
  texte ; C4 une seule, `URL.Template.Value.associativeList`. `asm(…)` : « cannot find 'asm' in scope » (E2).

### FreePascal (3.2.2, options du banc : -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (D4 et F4 valent 1 en v2 par les unités Syscall et
BaseUnix livrées, ½ en v1). Recherches dans l'interface des unités livrées (RTL, `rtl-*`, `fcl-*`), lue par
`ppudump` (`tools/grid_audit/listings/fpc_symbols.py`).
* Faits notables : `bitpacked record` range deux intervalles dans un octet (A3) ; un record à variantes sans champ
  d'étiquette est une union brute (A5) ; `NewInstance` redéfini construit un objet dans une arène (B2 ½ : pas
  d'allocateur passé aux conteneurs) ; `-Sv` additionne des `array[0..3] of Single` en SSE, mais huit `Single`
  provoquent une erreur interne (200610072) et un opérande non aligné sur 16 octets une erreur 216 (C1 ½) ;
  l'assembleur en ligne accepte AVX2, pas AVX-512 (E2).
* Contre-épreuves : `-OoFASTMATH` contracte `a*b+s` en FMA mais garde la chaîne scalaire et dans l'ordre (C4 0) ;
  `axpy` sur des tampons qui se recouvrent rend le résultat de l'alias, sans règle qui permettrait de l'ignorer (E5 0) ;
  `Likely` est un identificateur inconnu (E3 0).
* F2 0 : la recherche trouve les numéros `syscall_nr_mbind`, `syscall_nr_set_mempolicy` et
  `syscall_nr_get_mempolicy` de l'unité Syscall, pour `Do_SysCall` : appel système brut (section 3).

### BQN (CBQN 0.12.0, binaire du banc)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2. La bibliothèque système se liste elle-même :
recherches dans les 90 valeurs système et leurs membres (`•listSys`, `•ns.Keys`,
`tools/grid_audit/listings/bqn_sys.bqn`).
* Faits notables : une matrice 1000×16 est un seul bloc de `f64` (A1 ½, F1) ; `•math.Sum` réassocie la somme
  (écart de 1,5e-13 avec `+´`, C4 ½) ; `•file.MapBytes` projette 64 Mio sans copie (F4).
* Contre-épreuves : `⍉` copie la matrice au lieu d'offrir une vue SoA (A6 0) ; tout tableau est sur le tas, les nombres
  ne sont jamais boxés (B3 0) ; chaque primitive alloue son résultat (B4 0) ; les indices sont toujours vérifiés,
  sans moyen de les couper (E6 0).
* E1 ½ : les symboles du compilateur à la volée sont dans le binaire (`nm`), mais aucune option n'affiche le code
  produit : il faut reconstruire CBQN.

### PHP (8.5.12, réglages du banc : OPcache, JIT tracing)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (D4 vaut 1 en v2 par l'extension pcntl livrée, ½
en v1). L'API publique de la construction du banc se liste par introspection (`tools/grid_audit/listings/php_api.php` :
7 090 noms, fonctions, classes et méthodes, constantes, directives ini et extensions) ; `probes/php/audit/` ajoute un
programme exécuté et trois formes refusées.
* Contre-épreuves : un petit agrégat de trois flottants coûte 216 octets de tas en tableau et 106 en objet à propriétés
  typées (B3 0) ; la boucle compilée par le JIT et `array_sum` donnent la même somme au bit près, qu'une somme par
  paires écrite à la main change de 6,3e-12 : l'ordre est gardé, rien ne permet de le relâcher (C4 0) ;
  `asm("pause")` est un appel de fonction inconnue (E2 0) ; un générique est une erreur de syntaxe et un appel de
  fonction dans une expression constante est refusé (E7 0).
* Les dix noms trouvés par les recherches sont des faux positifs : `DNS_SOA` (A6) ; `PHP_RELEASE_VERSION`,
  `sem_acquire` et `sem_release`, des sémaphores System V (D2) ; `realpath_cache_size`, fonction et directive (D3) ;
  `PDO::ATTR_PREFETCH` et `Pdo\Sqlite::ATTR_PREFETCH` (E4) ; `POSIX_PC_CHOWN_RESTRICTED` et `opcache.restrict_api`
  (E5).

### C# (.NET 10.0.14, SDK 10.0.403 ; réglages du banc : JIT à niveaux, PGO dynamique)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2. La première sonde n'imprimait que quatre cas ;
`probes/csharp/audit/` les reprend tous : programme exécuté (`Audit.cs`) dont le code machine des méthodes `Cg*` est
lu par `DOTNET_JitDisasm`, trois formes refusées par `csc`, et recherches dans l'API publique du paquet de référence
`Microsoft.NETCore.App.Ref` (38 383 noms, lus dans les métadonnées par `tools/grid_audit/listings/dotnet_api`).
* Code machine : `Vector256.FusedMultiplyAdd` donne un `vfmadd213ps` sur ymm, `Avx512F.Add` un `vaddps` sur zmm,
  `Interlocked.Increment` un `lock xadd`, `Volatile.Write` un `mov` simple, `X86Base.Pause` un `pause`,
  `Sse.Prefetch0` un `prefetcht0` ; `a[i]` appelle `CORINFO_HELP_RNGCHKFAIL`, `Unsafe.Add` non (E6) ; un générique
  a un corps par type valeur (int, double, float) et un corps partagé pour les références (E7 ½).
* Contre-épreuves et limites : `a*b + a` sur `Vector512` reste `vmulps` + `vaddps` (pas de contraction, C4 0) ;
  `Process.ProcessorAffinity` n'épingle sur Linux que le fil principal (`sched_setaffinity` sur le PID ; douze autres
  fils du runtime restent libres) et `ProcessThread.ProcessorAffinity` lève `PlatformNotSupportedException` (D4 ½) ;
  `GC.TryStartNoGCRegion` suspend le ramasse-miettes pour un budget borné, après quoi la région se termine (B1,
  section 3).
* Les noms trouvés par les recherches sont des faux positifs : `Regex.CacheSize` (D3), l'en-tête HTTP `Expect` (E3),
  50 `Restriction`… (E5), `XmlEnumAttribute` et `DataTable.Locale` (F2).

### Java (OpenJDK 27.0.1 ; réglages du banc : C2, G1, `--add-modules jdk.incubator.vector`)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2. `probes/java/audit/` : programme exécuté
(`Audit.java`), contre-épreuves lancées dans des JVM à part (Epsilon, `@Contended`, `PrintAssembly`, `UseNUMA`),
cinq formes refusées par `javac`, et recherches dans l'API exportée des modules système (48 847 noms,
`tools/grid_audit/listings/JavaApi.java`). Sans hsdis, le code machine ne se lit pas (E1 ½) : les preuves sont des
valeurs et des mesures.
* Cas contraires mesurés : HotSpot place `class P {byte a; long b; int c;}` à a=20 b=8 c=16 (A2) ; un tableau
  d'objets ne tient que des références de 4 o (A1) ; un `record` rendu par une méthode non incorporée coûte 16 o de
  tas par appel, 0 une fois incorporé par l'analyse d'échappement (B3) ; un `ArrayList<Integer>` coûte 16 o de plus
  par élément (B4) ; une boucle compilée par C2 garde l'ordre de la somme, la réduction de la Vector API non (C4 ½).
* `@Contended` (annotation interne) écarte deux champs de 136 o avec `-XX:-RestrictContended` et l'export du paquet
  interne, de 8 o sans (D3 ½) ; `sched_setaffinity` marche par l'API FFM vers la glibc, non comptée (D4 0).
* Cases discutables (section 3) : B1 (collecteur Epsilon, expérimental), E6 (`sun.misc.Unsafe` lit hors d'un tableau
  sans contrôle), F2 (`-XX:+UseNUMA`, coupée par l'ergonomie sur cet hôte).

### Go (1.27.3 ; réglages du banc : GOAMD64=v4, GOEXPERIMENT=simd)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (D4 et F4 valent 1 en v2 par le paquet syscall
livré, ½ en v1). `probes/go/audit/` : programme exécuté dont le code machine est lu par `go tool objdump`, paquets
expérimentaux `arena` et `simd` construits avec et sans `GOEXPERIMENT`, une fonction dans l'assembleur de Go, huit
formes refusées, et recherches dans la liste de l'API publique livrée avec la chaîne (`api/go1*.txt`).
* Code machine : `atomic.Int32.Store` est un `XCHGL` (séquentiellement cohérent, D2 ½), la somme de `float64` une
  suite d'`ADDSD` scalaires (C4 0), `s[i]` un `CMPQ` et un appel à `runtime.panicBounds` que `unsafe.Add` et
  `-gcflags=-B` retirent (E6) ; un générique a un corps par forme GC, `*A` et `*B` partageant le même (E7 ½) ; le
  paquet `simd` portable produit une version par largeur (simd128, simd256, simd512).
* Contre-épreuves : `debug.SetGCPercent(-1)` arrête le ramasse-miettes (aucune collecte pour 256 Mio), mais rien n'est
  rendu (B1, section 3) ; `internal/cpu.CacheLinePad`, `internal/runtime/sys.Prefetch` et `runtime.procyield` existent
  mais ne s'importent pas (D3, E4, D5 : 0).
* F2 : la recherche trouve les numéros `SYS_MBIND`, `SYS_SET_MEMPOLICY`… du paquet syscall (appel système brut,
  section 3) ; `testing.B.RunParallel` (C5) parallélise des bancs d'essai, pas des données.

### Haskell (GHC 9.14.1 ; réglages du banc : -O2 -fllvm -mavx512f -mfma -threaded)

33 cases sondées (C3 mesurée), **une divergence** avec la matrice : A3 (section 4). `probes/haskell/audit/` : programme
exécuté avec `+RTS -N4 -qa -T -s`, décalages de structures C calculés par `hsc2hs` (livré avec GHC), Template Haskell
dans un module à part, code machine lu dans l'assembleur gardé (`-keep-s-files`), et recherches dans 219 229 lignes de
« :browse » sur les 833 modules exposés des bibliothèques livrées (`tools/grid_audit/listings/haskell_api.sh`).
* Faits notables : `fmaddFloatX16#` donne des `vfmadd…ps` sur zmm (C1 ½, primops propres à GHC) ; sept étincelles
  sur huit converties en calculs parallèles, `Control.Parallel.Strategies` absent de la chaîne (C5 ½) ; `forkOn 2`
  avec `-qa` fait tourner le fil sur le processeur 2 (D4 ½) ; un n-uplet non boxé rendu par une fonction NOINLINE
  n'alloue rien, le n-uplet boxé 72 o par appel (B3 ½) ; `prefetchMutableByteArray3#` donne `prefetcht0` (E4).
* Contre-épreuves : `+RTS --numa` répond « This GHC build was compiled without NUMA support » (F2 0, malgré les champs
  `numa` de `GHC.RTS.Flags`) ; `mmap` marche par la FFI vers la glibc, non comptée (F4 0).
* A3 : une instance `Storable` de 5 o range `{Word8; Word32}` à plat, le `Word32` non aligné, sur les décalages
  d'une structure C `packed` que donne `hsc2hs` : c'est le mécanisme que la matrice compte pour A2 (½, « Storable
  manuel »), il donne aussi la disposition compactée (sans champ de bits) ; la note devrait être ½, comme Rust et C#.

### OCaml (5.5.2 + flambda ; réglages du banc : ocamlopt -O3, unix et bigarray)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2. `probes/ocaml/audit/` : programme exécuté (mots
atteignables par `Obj.reachable_words`, mots alloués par `Gc.minor_words`), code machine lu dans l'assembleur (`-S`) et
dans le runtime (`objdump`), trois formes refusées, recherches dans les 74 interfaces `.mli` livrées (bibliothèque
standard, unix, str, threads, runtime_events ; sans compiler-libs).
* Cas contraires mesurés (cases à 0) : un tableau de 1000 enregistrements de quatre flottants occupe 6 mots par élément
  (pointeur et bloc séparé), un `Float.Array` 1 (A1) ; `{char; int32; float}` prend un mot par champ et range l'int32
  à part (A2) ; un n-uplet rendu par une fonction non incorporée coûte 3 mots, 0 une fois incorporé par flambda (B3) ;
  une somme polymorphe alloue 4 mots par élément, la boucle monomorphe 0, et l'assembleur ne contient qu'un corps de
  `poly_sum` (B4, E7).
* Positifs : `Atomic.make_contended` occupe une ligne de cache (7 mots et l'en-tête : 64 o, D3) ; `Domain.cpu_relax`
  exécute un `pause` du runtime (D5 ½) ; `-unsafe` retire la comparaison et l'appel à `caml_ml_array_bound_error`
  (E6) ; `Unix.map_file` projette le fichier (F4).

### JavaScript (Node 26.12.1, V8 ; réglages du banc : --expose-gc)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2. `probes/js/audit/` : programme exécuté (octets
alloués lus dans `v8.getHeapStatistics().total_allocated_bytes`, collectes par `PerformanceObserver`), code machine de
TurboFan (`--print-opt-code`), une forme refusée, recherches dans 12 301 noms de l'objet global et des modules
intégrés (`tools/grid_audit/listings/node_api.js` ; accesseurs nommés sans être appelés, variables d'environnement
exclues).
* Cas contraires mesurés : 128 o de tas par objet `{x, y, z, w}` (A1), 40 o par objet qui s'échappe et 0,1 o par
  objet resté local, l'analyse d'échappement le supprimant (B3), 96 o par fermeture, 16 o par flottant rangé dans un
  tableau générique (B4) ; un objet passé à un `Worker` est copié (D1 ½).
* `node:ffi`, expérimental et actif par défaut, donne les ½ de A4, B5 et E6 (pointeur brut, lecture hors tampon sans
  contrôle) ; `sched_setaffinity` et `mmap` de la glibc par `node:ffi` marchent, non comptés (D4, F4 : 0).

### Python (3.15.2, CPython avec GIL)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2 (D4 vaut 1 en v2, ½ en v1). `probes/python/audit/`
: programme exécuté, une forme refusée, recherches dans les sources `.py` livrées (sans les tests) et dans les noms
publics des modules écrits en C (`tools/grid_audit/listings/python_cmods.py`, modules de test de CPython exclus).
* `ctypes` donne les ½ de la catégorie A (dispositions C, `_pack_` et champ de bits, union, tableau fixe) ;
  `_align_ = 64` règle l'alignement déclaré mais pas celui du tampon alloué (adresse à 48 mod 64), d'où la
  sur-allocation (A4 ½).
* Le GIL de la construction par défaut : quatre calculs prennent 0,32 s en série comme sur quatre fils, 0,12 s sur
  quatre sous-interpréteurs (`InterpreterPoolExecutor`, D1 ½) ; le JIT expérimental est absent de cette construction
  (`sys._jit.is_available()` faux, E1 0) ; `sum()` compense l'erreur et `math.fsum` est exacte, aucune option
  n'autorise la réassociation (C4 0).

### Lua (5.5.1, interpréteur de référence)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice v2. `probes/lua/audit/` : programme exécuté (mémoire
lue par `collectgarbage("count")`), bytecode listé par `luac -l`, une forme refusée, recherches dans les 160 noms de la
bibliothèque standard (`tools/grid_audit/listings/lua_api.lua`), sans aucun résultat.
* Un million d'appels qui rendent deux valeurs n'allouent rien (B3 ½) ; une fermeture coûte 80 o, une table `{i}` 61 o
  (B4 ½) ; quatre coroutines alternent sur un seul fil (D1 0).
* `string.pack('<BI4')` range un enregistrement compacté de 5 o, dans une chaîne immuable : même lecture que A8 (0) ;
  `collectgarbage("stop")` arrête le ramasse-miettes, et rien n'est rendu (B1, section 3).

## 3. Cases discutables

| Langage | Case | Note | Fait établi | Lecture de la règle | Autre note possible |
|---|---|---|---|---|---|
| Rust | D4, F4 | 0 | `sched_setaffinity` et `mmap` marchent par le crate `libc` du sysroot, sur nightly avec `#![feature(rustc_private)]` | Le crate n'est pas dans l'API publique de `std` : c'est une FFI vers la glibc, du code non intrinsèque (0) | ½ si on le lit comme une unité interne livrée, accessible sur le canal instable |
| Zig | C2 | ½ | Un `extern fn` au nom d'une intrinsèque de LLVM produit l'instruction (`vpternlogd`) | Mécanisme ni documenté ni employé par la bibliothèque livrée : la règle v2 ne compte que le « mécanisme d'import d'intrinsèques du langage » (½ par l'assembleur en ligne) | 1, comme Odin, dont la bibliothèque livrée emploie le même mécanisme |
| Odin, et tout langage dont la bibliothèque livre un appel système brut (C, C++, Go, Zig, FreePascal…) | F2 | 0 | `mbind` par appel système brut pose une politique NUMA (`MPOL_BIND` relu par `get_mempolicy`, sonde d'Odin) | F2 compte les constructions de localité et de distribution ; un numéro d'appel système n'en est pas une (C : « libnuma hors standard ») | ½ si l'appel système brut compte, comme il compte pour D4 (Go, FreePascal) |
| Nim | E3 | 1 | `likely`/`unlikely` changent la disposition avec gcc 16 (compilateur C par défaut de Nim), pas avec clang 23 (celui du banc) | La chaîne livrée compile par gcc : la capacité marche telle que livrée | 0 si l'on note la configuration du banc (clang), où l'indication est perdue |
| C | B2 | ½ | La glibc livre une arène (`obstack`, `<obstack.h>`) : deux blocs consécutifs, libérés d'un coup | Pas d'interface d'allocateur que la bibliothèque accepterait : ½ | 1 si une arène de la bibliothèque système suffit |
| C, C++, Fortran | F2 | 0, 0, ½ | Le trait d'allocateur OpenMP `omp_atk_partition` (interleaved, nearest, blocked) est accepté par libomp et libgomp ; sur cet hôte à un seul nœud NUMA, aucune politique n'est posée | Effet invérifiable ici ; libgomp passe par libnuma, tierce | ½ si le trait d'OpenMP compte comme construction de localité |
| C#, Java, Go, Lua | B1 | 0 | Le ramasse-miettes s'arrête : `GC.TryStartNoGCRegion` (C#, budget borné), collecteur Epsilon (Java, expérimental), `debug.SetGCPercent(-1)` (Go, stable), `collectgarbage("stop")` (Lua, stable) ; aucune collecte, mais rien n'est rendu | B1 compte la mémoire rendue sans ramasse-miettes traçant (comptage de références, propriété) : ici seule la collecte la rend | ½ si un ramasse-miettes qu'on peut arrêter n'est plus « imposé » |
| Java | E6 | 0 | `sun.misc.Unsafe.getInt(tableau, décalage)` lit hors du tableau sans contrôle | Méthode de `jdk.unsupported`, dépréciée pour suppression, avertissement à la première utilisation : pas une construction du langage | ½ si une API non prise en charge mais livrée compte, comme une unité interne |
| Java | F2 | 0 | `-XX:+UseNUMA` (allocation NUMA du collecteur) est acceptée, puis coupée par l'ergonomie sur cet hôte à un seul nœud ; HotSpot passe par libnuma | Option globale de la JVM, effet invérifiable ici, bibliothèque tierce | ½ si une option globale d'allocation NUMA compte |

## 4. Divergences

Une sonde contredit la note de la matrice ; l'erratum est appliqué avec les autres une fois toutes les sondes faites
(docs/V4_PLAN.md 2.3).

| Langage | Case | Matrice (v1, v2) | Sonde | Fait établi |
|---|---|---|---|---|
| Haskell | A3 | 0, 0 | ½ | Instance `Storable` compactée de 5 o (décalages de `hsc2hs`), tableau à plat, `Word32` non aligné relu ; même mécanisme que A2 (½) |
