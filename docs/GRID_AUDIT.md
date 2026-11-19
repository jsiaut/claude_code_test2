# Audit de la grille : une sonde par case (v4, point 1)

*Plan : `docs/V4_PLAN.md`, section 2, poussé avant tout travail. Outils : `tools/grid_audit/` (motifs de recherche fixés
d'avance, `search.py`), `analysis/grid_audit.py` (confrontation des sondes à la matrice v1 et v2, classes de preuve).
Sorties : `results/probes/<langage>.txt`, `results/grid_audit/summary.md`, `results/grid_audit/search/` (détail de chaque
recherche d'absence). Ce document est rempli langage par langage ; les errata sont appliqués ensemble à la fin.*

## 1. Méthode

* **Classes de preuve.** [exécutée] : un programme se sert de la capacité et imprime un fait observable (taille,
  décalage, adresse modulo, valeur, fil, instruction du code produit, attribut de l'IR) ; pour ½, la limite est montrée
  aussi. [échec] : la forme canonique est tentée et le refus du compilateur est imprimé. [recherche] : les sources livrées
  de la bibliothèque standard (ou la liste de ses API publiques) sont fouillées avec le motif de la case
  (`tools/grid_audit/patterns.json`) ; chaque déclaration publique trouvée est examinée, et l'examen est écrit dans la
  ligne de la sonde. C3 reste [mesurée].
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

## 3. Cases discutables

| Langage | Case | Note | Fait établi | Lecture de la règle | Autre note possible |
|---|---|---|---|---|---|
| Rust | D4, F4 | 0 | `sched_setaffinity` et `mmap` marchent par le crate `libc` du sysroot, sur nightly avec `#![feature(rustc_private)]` | Le crate n'est pas dans l'API publique de `std` : c'est une FFI vers la glibc, du code non intrinsèque (0) | ½ si on le lit comme une unité interne livrée, accessible sur le canal instable |
| Zig | C2 | ½ | Un `extern fn` au nom d'une intrinsèque de LLVM produit l'instruction (`vpternlogd`) | Mécanisme ni documenté ni employé par la bibliothèque livrée : la règle v2 ne compte que le « mécanisme d'import d'intrinsèques du langage » (½ par l'assembleur en ligne) | 1, comme Odin, dont la bibliothèque livrée emploie le même mécanisme |
| Odin, et tout langage dont la bibliothèque livre un appel système brut (C, C++, Go, Zig, FreePascal…) | F2 | 0 | `mbind` par appel système brut pose une politique NUMA (`MPOL_BIND` relu par `get_mempolicy`, sonde d'Odin) | F2 compte les constructions de localité et de distribution ; un numéro d'appel système n'en est pas une (C : « libnuma hors standard ») | ½ si l'appel système brut compte, comme il compte pour D4 (Go, FreePascal) |
| Nim | E3 | 1 | `likely`/`unlikely` changent la disposition avec gcc 16 (compilateur C par défaut de Nim), pas avec clang 23 (celui du banc) | La chaîne livrée compile par gcc : la capacité marche telle que livrée | 0 si l'on note la configuration du banc (clang), où l'indication est perdue |
