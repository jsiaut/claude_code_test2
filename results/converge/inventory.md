# Relevé des formes du point 4 (v4)

Écrit par `tools/converge/inventory.py` (données dans le script) ; plan : `docs/V4_CONVERGE.md`, 3.3 à 3.5.
États : **présente** (variante existante conforme à la définition), **écrite** (variante nouvelle de la copie `bench/<langage>_cv`), **non écrivible** (preuve dans la note), **sans objet** (repli d'une forme principale présente ou écrite ; réserve de fils sans forme à un fil nouvelle). « R » : forme trouvée par la remarque du langage (calcul 4).

Langages relevés : 11 sur 25 (C, Odin, C++, C3, Zig, Rust, Nim, D, Ada, Chapel, Fortran).

## Règles de lecture appliquées au relevé (fixées au fil du portage, 21 novembre)

1. **Q1 `tuned_v`, « compte par population du masque ».** Sont lus comme conformes : le compte des bits d'un masque en bits à chaque tour (popcount ; C, Zig, C++, Rust) et l'accumulation des voies du masque dans un vecteur réduit une fois par bloc de 4 096 lignes (D). Une variante qui réduit horizontalement les voies du masque à chaque tour (Odin, C3) n'est pas la forme : `tuned_v` est écrite avec un popcount quand le langage peut tirer un masque en bits (la remarque sur Odin a mesuré × 0,55 pour ce seul changement).
2. **K9 `tuned_v`.** La forme de la frontière (Swift) part de j = 1 : haut et bas sont lus à 8 octets d'une frontière de 64 octets, droite à 16, gauche alignée, et l'écriture se fait à 8. Les variantes écrites reprennent cette boucle avec des chargements et écritures non alignés ; l'alignement ne change rien de mesurable (4.1).
3. **Formes propres à un langage (3.5).** S'ajoutent à la liste du plan les formes trouvées par une remarque dont le gain tient à un idiome du langage plutôt qu'à l'algorithme : arène passée par pointeur brut en C++ (`std::vector` et état par référence) et arène écrite comme en C en Rust (`Vec::push` et vérifications de bornes). Elles entrent dans le plafond de leur langage, sans portage.
4. **Options de construction.** Une forme dont le gain venait d'une option de construction (D, `-mattr=-prefer-256-bit`) n'est pas admise (3.2, 4). Une correction déjà reportée en base (4.1) n'est pas une forme nouvelle.
5. **Réserve de fils (3.6).** `mt_pool` exécute dans chaque quart la forme de la variante `mt` publiée ; `mt_pool_v` (ou `_s`) n'est écrite que si la forme à un fil correspondante est nouvelle dans le langage. Sans barrière dans la bibliothèque standard, elle est faite du mutex et de la variable de condition du langage (numéro de génération).

## C

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : intrinsèques AVX-512BW, vpsadbw |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits ; clang vectorise la boucle (registres ymm) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | AVX-512 : 16 f32, quatre accumulateurs, 64 éléments par tour, FMA |
| `q6 tuned_v` | Q6 | écrite | `k6 tuned_v q6` | AVX-512 ; la variante tuned publiée est scalaire sans branchement |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` | Q1 | présente | `k6 tuned q1` | la référence de la forme |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | barrières POSIX ; chaque quart : q6_tuned publiée |
| `q6 mt_pool_v` | Q6 mt | écrite | `k6 mt_pool_v q6` | chaque quart : tuned_v |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1_tuned publiée (déjà tuned_v) |
| `q1 mt_pool_v` | Q1 mt | sans objet | — | tuned_v de Q1 présente : mt_pool l'exécute |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | capacité 2^(LOG2+1), cases de 16 octets, Fibonacci, lots de 16, __builtin_prefetch en écriture |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` (R) | K8 | écrite | `k8 tuned_val` | copie bench/c_k8val (remarque sur C) |
| `k8 tuned_it` (R) | K8 | écrite | `k8 tuned_it` | copie bench/c_k8it (remarque sur C) |
| `k9 tuned_v` | K9 | écrite | `k9 tuned_v` | AVX-512, 8 f64 ; boucle de Swift (j depuis 1, accès non alignés) |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9_rows publiée |
| `k9 mt_pool_v` | K9 mt | écrite | `k9 mt_pool_v` | chaque quart : tuned_v |

## Odin

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : #simd[64]u8, core:simd |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (intrinsics.unaligned_load) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | #simd[16]f32, quatre accumulateurs, simd.fma |
| `q6 tuned_v` | Q6 | présente | `k6 tuned q6` | #simd[16]i32, simd.select, accumulation en #simd[16]i64 |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` (R) | Q1 | écrite | `k6 tuned_v q1` | forme de bench/odin_q1 (remarque sur Odin, × 0,55) : compte par card(simd.extract_msbs) ; la variante tuned publiée compte par somme des voies du masque |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | barrières de core:sync ; chaque quart : q6_tuned publiée (tuned_v) |
| `q6 mt_pool_v` | Q6 mt | sans objet | — | tuned_v de Q6 présente : mt_pool l'exécute |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1_tuned publiée |
| `q1 mt_pool_v` | Q1 mt | écrite | `k6 mt_pool_v q1` | chaque quart : tuned_v (le Q1 mt de la remarque, fils créés à chaque appel, n'est pas écrit : 3.6) |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, intrinsics.prefetch_write_data |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | procédure récursive, état en paramètres et en retour |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes ([64]) |
| `k9 tuned_v` | K9 | présente | `k9 tuned` | #simd[8]f64, chargements et écriture non alignés, j depuis 1 |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9_rows publiée (tuned_v) |
| `k9 mt_pool_v` | K9 mt | sans objet | — | tuned_v de K9 présente : mt_pool l'exécute |

## C++

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : intrinsèques AVX-512BW, comme C |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (std::memcpy) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | std::simd vec<float, 16>, quatre accumulateurs, chargements alignés |
| `q6 tuned_v` | Q6 | écrite | `k6 tuned_v q6` | std::simd, accumulation en vec<int64_t, 16> ; la variante tuned publiée accumule en i32, vidé tous les 256 pas |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` | Q1 | présente | `k6 tuned q1` | std::simd : compte par reduce_count, charge en vec<int64_t, 16> |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | std::barrier et std::jthread ; chaque quart : q6_tuned publiée |
| `q6 mt_pool_v` | Q6 mt | écrite | `k6 mt_pool_v q6` | chaque quart : tuned_v |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1_tuned publiée (tuned_v) |
| `q1 mt_pool_v` | Q1 mt | sans objet | — | tuned_v de Q1 présente : mt_pool l'exécute |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, __builtin_prefetch en écriture |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | arène passée par pointeur |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en std::array<.., 64> |
| `k9 tuned_v` | K9 | écrite | `k9 tuned_v` | std::simd vec<double, 8>, j depuis 1 ; la variante tuned publiée est une boucle scalaire vectorisée par g++ |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9_rows publiée |
| `k9 mt_pool_v` | K9 mt | écrite | `k9 mt_pool_v` | chaque quart : tuned_v |
| `k8 rq_ptr` (R) | K8 | écrite | `k8 rq_ptr` | forme de bench/cpp_k8 (remarque sur C++, × 0,77) : la variante tuned, l'arène passée par pointeur brut ; son gain tient au std::vector passé par référence avec un état lui aussi par référence (rechargements imposés par l'aliasing), un coût de l'idiome de C++ ; les formes du catalogue reçoivent l'arène par pointeur |

## C3

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : char[<64>], comp_ge, math::select |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (mem::load non aligné) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | float[<16>], quatre accumulateurs, math::fma |
| `q6 tuned_v` | Q6 | présente | `k6 tuned q6` | int[<16>], math::select, accumulation en long[<16>] |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` | Q1 | écrite | `k6 tuned_v q1` | compte par mask_to_int puis popcount ; la variante tuned publiée compte par somme des voies d'une sélection |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | barrière faite du Mutex et de la ConditionVariable de std::thread ; chaque quart : q6_tuned publiée (tuned_v) |
| `q6 mt_pool_v` | Q6 mt | sans objet | — | tuned_v de Q6 présente : mt_pool l'exécute |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1_tuned publiée |
| `q1 mt_pool_v` | Q1 mt | écrite | `k6 mt_pool_v q1` | chaque quart : tuned_v |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, @prefetch(…, VERY_NEAR, true) (écriture) |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | fonction récursive, état en paramètres et en retour |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes ([64]) |
| `k9 tuned_v` | K9 | présente | `k9 tuned` | double[<8>], mem::load et mem::store non alignés, j depuis 1 |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9_rows publiée (tuned_v) |
| `k9 mt_pool_v` | K9 mt | sans objet | — | tuned_v de K9 présente : mt_pool l'exécute |

## Zig

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : @Vector(64, u8), @select |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (std.mem.readInt) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | @Vector(16, f32), quatre accumulateurs, @mulAdd |
| `q6 tuned_v` | Q6 | présente | `k6 tuned q6` | la forme de la frontière : @Vector(16, i32), @select, accumulation en @Vector(16, i64) |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` | Q1 | présente | `k6 tuned q1` | compte par @popCount(@bitCast(masque)), charge en @Vector(16, i64) |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | barrière faite de std.Io.Mutex et std.Io.Condition ; chaque quart : q6Tuned publiée (tuned_v) |
| `q6 mt_pool_v` | Q6 mt | sans objet | — | tuned_v de Q6 présente : mt_pool l'exécute |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1Tuned publiée (tuned_v) |
| `q1 mt_pool_v` | Q1 mt | sans objet | — | tuned_v de Q1 présente : mt_pool l'exécute |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, @prefetch(.write) |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | fonction récursive, état en paramètres et en retour |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes ([64]) |
| `k9 tuned_v` | K9 | présente | `k9 tuned` | @Vector(8, f64), tranches non alignées, j depuis 1 |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9Rows publiée (tuned_v) |
| `k9 mt_pool_v` | K9 mt | sans objet | — | tuned_v de K9 présente : mt_pool l'exécute |

## Rust

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : std::arch AVX-512BW, vpsadbw |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (chunks_exact, u64::from_le_bytes) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | std::arch AVX-512 : 16 f32, quatre accumulateurs, FMA |
| `q6 tuned_v` | Q6 | écrite | `k6 tuned_v q6` | std::arch AVX-512 ; la variante tuned publiée est scalaire sans branchement (std::simd n'est pas stable) |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` | Q1 | présente | `k6 tuned q1` | std::arch, la référence ; count_ones compilé en popcnt sous target-cpu=native : la forme de la remarque (_popcnt32, bench/rust_clpop, × 0,83 sur le code de Cascade Lake) n'en diffère pas sur cet hôte |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | std::sync::Barrier, fils de std::thread::scope ; chaque quart : q6_tuned publiée |
| `q6 mt_pool_v` | Q6 mt | écrite | `k6 mt_pool_v q6` | chaque quart : tuned_v |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1_tuned publiée (tuned_v) |
| `q1 mt_pool_v` | Q1 mt | sans objet | — | tuned_v de Q1 présente : mt_pool l'exécute |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, _mm_prefetch::<_MM_HINT_ET0> (écriture) |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | arène préallouée, get_unchecked (sûreté : indices < longueur par construction) |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes ([_; 64]) |
| `k9 tuned_v` | K9 | écrite | `k9 tuned_v` | std::arch AVX-512, grilles ABuf alignées sur 64 octets, j depuis 1 ; la variante tuned publiée est une boucle scalaire vectorisée par rustc |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9_rows publiée (grilles ABuf) |
| `k9 mt_pool_v` | K9 mt | écrite | `k9 mt_pool_v` | chaque quart : tuned_v |
| `k8 rq_arena` (R) | K8 | écrite | `k8 rq_arena` | forme de bench/rust_k8 (remarque sur Rust, × 0,74) : l'arène écrite comme en C (tranche préallouée, indice libre et compteur par référence, get_unchecked) ; son gain tient à Vec::push (test de capacité, longueur mise à jour) et aux vérifications de bornes de la variante tuned publiée, des coûts de l'idiome de Rust |

## Nim

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : intrinsèques AVX-512BW importées de immintrin.h |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (copyMem) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | intrinsèques AVX-512 importées : quatre accumulateurs, FMA |
| `q6 tuned_v` | Q6 | écrite | `k6 tuned_v q6` | intrinsèques AVX-512 importées ; la variante tuned publiée est scalaire sans branchement |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` (R) | Q1 | écrite | `k6 tuned_v q1` | forme de bench/nim_q1 (remarque sur Nim, × 0,30), recopiée : la référence C en intrinsèques importées ; la variante tuned publiée agrège par blocs et par groupe en scalaire |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | barrière faite du Lock et du Cond de std/locks ; chaque quart : q6Tuned publiée |
| `q6 mt_pool_v` | Q6 mt | écrite | `k6 mt_pool_v q6` | chaque quart : tuned_v |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1Tuned publiée |
| `q1 mt_pool_v` | Q1 mt | écrite | `k6 mt_pool_v q1` | chaque quart : tuned_v (le Q1 mt de la remarque, fils créés à chaque appel, n'est pas écrit : 3.6) |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, __builtin_prefetch(p, 1, 3) importé (écriture) |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | sous boundChecks et overflowChecks désactivés, comme les autres noyaux optimisés |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes (array[64, …]) |
| `k9 tuned_v` | K9 | écrite | `k9 tuned_v` | intrinsèques AVX-512 importées, j depuis 1 ; la variante tuned publiée est une boucle scalaire que clang vectorise |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9Rows publiée |
| `k9 mt_pool_v` | K9 mt | écrite | `k9 mt_pool_v` | chaque quart : tuned_v |
| `k8 rq_noovf` (R) | K8 | écrite | `k8 rq_noovf` | forme de bench/nim_k8 (remarque sur Nim, × 0,91) : la variante tuned sans vérification de débordement ; son gain tient aux vérifications de débordement de Nim (classée propre au runtime par le plan, 2) |

## D

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : vecteurs de core.simd, masque de ldc.simd, psadbw de ldc.gccbuiltins_x86 |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (memcpy) |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | float16 de core.simd, quatre accumulateurs, contraction permise (@llvmFastMathFlag("contract")) |
| `q6 tuned_v` | Q6 | écrite | `k6 tuned_v q6` | int16 de core.simd, accumulation en long8 (voies paires et impaires) ; la variante tuned publiée est scalaire sans branchement. La préférence 512 bits de la remarque (bench/d_512, -mattr=-prefer-256-bit) n'est pas admise : option de construction propre à une variante (3.2, 4) |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` | Q1 | présente | `k6 tuned q1` | core.simd (la correction de la remarque, reportée en base) : compte par accumulation des voies du masque, réduite toutes les 4 096 lignes (la population du masque sans réduction à chaque tour ; LDC n'expose pas de comparaison vers un masque en bits), charge en 64 bits par voies paires et impaires |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | core.sync.barrier, fils de core.thread ; chaque quart : q6Tuned publiée |
| `q6 mt_pool_v` | Q6 mt | écrite | `k6 mt_pool_v q6` | chaque quart : tuned_v |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : q1Tuned publiée (tuned_v) |
| `q1 mt_pool_v` | Q1 mt | sans objet | — | tuned_v de Q1 présente : mt_pool l'exécute |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, llvm_prefetch(p, 1, 3, 1) (écriture) |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | fonction récursive, état en paramètres et en retour |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes ([64]) |
| `k9 tuned_v` | K9 | présente | `k9 tuned` | double8 de core.simd, loadUnaligned et storeUnaligned, j depuis 1 |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : k9Rows publiée (tuned_v) |
| `k9 mt_pool_v` | K9 mt | sans objet | — | tuned_v de K9 présente : mt_pool l'exécute |

## Ada

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : type vectoriel GCC et builtins importés (vpmovb2m, vmovdqu8 masqué, vpsadbw) |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits lus par superposition d'adresse |
| `k5 tuned_v` | K5 | présente | `k5 tuned` | type vectoriel GCC de 16 Float, builtin FMA, quatre accumulateurs |
| `q6 tuned_v` | Q6 | écrite | `k6 tuned_v q6` | type vectoriel GCC et builtins AVX-512 importés (pmovzxbd, comparaisons vers masque, pmulld masqué) ; la variante tuned publiée est scalaire, vectorisée par GCC |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` | Q1 | écrite | `k6 tuned_v q1` | la référence C en builtins importés (popcount, pext, pmuldq) ; boucle des six groupes déroulée (pragma Loop_Optimize (Unroll) : 70 → 22 ms) ; la variante tuned publiée agrège par blocs et par groupe en scalaire |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | écrite | `k6 mt_pool q6` | trois tâches Ada créées une fois, rendez-vous Go et Done ; chaque quart : Q6_Tuned publiée |
| `q6 mt_pool_v` | Q6 mt | écrite | `k6 mt_pool_v q6` | chaque quart : tuned_v |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | écrite | `k6 mt_pool q1` | chaque quart : Q1_Tuned publiée |
| `q1 mt_pool_v` | Q1 mt | écrite | `k6 mt_pool_v q1` | chaque quart : tuned_v |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | lots de 16, __builtin_prefetch(p, 1, 0) importé (écriture) |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | présente | `k8 tuned` | la forme de la frontière : paramètres in out de types élémentaires, passés par copie (RM 6.2) |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes (0 .. 63) |
| `k9 tuned_v` | K9 | écrite | `k9 tuned_v` | type vectoriel GCC de 8 Long_Float, builtins loadupd, addpd, mulpd, storeupd, j depuis 1 ; la variante tuned publiée est une boucle scalaire vectorisée par GCC |
| `k9 mt_pool` | K9 mt | écrite | `k9 mt_pool` | chaque quart : K9_Rows publiée |
| `k9 mt_pool_v` | K9 mt | écrite | `k9 mt_pool_v` | chaque quart : tuned_v |

## Chapel

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : intrinsèques AVX-512BW importées par extern proc |
| `k4 swar` | K4 | écrite | `k4 swar` | mots de 64 bits (OS.POSIX.memcpy) |
| `k5 tuned_v` | K5 | écrite | `k5 tuned_v` | intrinsèques AVX-512 importées (FMA, quatre accumulateurs), binaire ms_tuned ; la variante tuned publiée est une boucle simple vectorisée par LLVM sous --no-ieee-float |
| `q6 tuned_v` | Q6 | écrite | `k6 tuned_v q6` | intrinsèques importées ; comparaisons par le bit de signe d'une différence (les comparaisons à immédiat sont des macros, non importables) ; la variante tuned publiée est scalaire, vectorisée par LLVM |
| `q6 tuned_s` | Q6 | sans objet | — | forme principale présente ou écrite |
| `q1 tuned_v` (R) | Q1 | écrite | `k6 tuned_v q1` | forme de bench/chapel_exp (remarque sur Chapel, × 0,84), recopiée : la référence C en intrinsèques importées ; la variante tuned publiée agrège par blocs et par groupe |
| `q1 tuned_s` | Q1 | sans objet | — | forme principale présente ou écrite |
| `q6 mt_pool` | Q6 mt | présente | `k6 mt q6` | coforall : tâches sur les fils gardés par le runtime (créés une fois) |
| `q6 mt_pool_v` | Q6 mt | écrite | `k6 mt_pool_v q6` | coforall, chaque quart : tuned_v |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | pas de forme scalaire nouvelle |
| `q1 mt_pool` | Q1 mt | présente | `k6 mt q1` | coforall (fils du runtime) |
| `q1 mt_pool_v` | Q1 mt | écrite | `k6 mt_pool_v q1` | coforall, chaque quart : tuned_v |
| `q1 mt_pool_s` | Q1 mt | sans objet | — | pas de forme scalaire nouvelle |
| `k7 tuned_pf` | K7 | présente | `k7 tuned` | la forme de la frontière ; le module Prefetch n'expose que __builtin_prefetch(addr), un préchargement en lecture |
| `k7 tuned_oa` | K7 | sans objet | — | forme principale présente ou écrite |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | procédure récursive, état en paramètres et en retour |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tuples (64 * int(32)) : aucune allocation |
| `k9 tuned_v` | K9 | écrite | `k9 tuned_v` | intrinsèques importées sur les tableaux 2D de Chapel lus par pointeur, j depuis 1 ; la variante tuned publiée est une boucle foreach vectorisée par LLVM |
| `k9 mt_pool` | K9 mt | présente | `k9 mt` | forall (fils du runtime), quatre blocs de lignes |
| `k9 mt_pool_v` | K9 mt | écrite | `k9 mt_pool_v` | coforall, quatre quarts : tuned_v |

## Fortran

| Forme | Cellule | État | Variante | Note |
|---|---|---|---|---|
| `k4 tuned` | K4 | écrite | `k4 tuned` | point 3 (R3) : sans SIMD explicite, la meilleure boucle scalaire (vectorisée par gfortran) |
| `k4 swar` | K4 | écrite | `k4 swar` | tableau d'octets vu en entiers de 64 bits (c_f_pointer) ; masque par ishft(m, 8) - m (entiers signés) ; gfortran vectorise la boucle |
| `k5 tuned_v` | K5 | non écrivible | — | pas de vecteurs explicites : grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt ; la forme de la remarque (rq_acc16) en tient lieu |
| `q6 tuned_v` | Q6 | non écrivible | — | grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt |
| `q6 tuned_s` | Q6 | présente | `k6 tuned q6` | prédicat en 0/1 par merge (pas d'entiers non signés), s += prix × remise × m en 64 bits, !$omp simd |
| `q1 tuned_v` | Q1 | non écrivible | — | grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt |
| `q1 tuned_s` | Q1 | écrite | `k6 tuned_s q1` | une passe, 30 accumulateurs locaux de 64 bits, masques par merge ; la variante tuned publiée agrège par blocs et par groupe |
| `q6 mt_pool` | Q6 mt | présente | `k6 mt q6` | équipe OpenMP (fils gardés par le runtime) |
| `q6 mt_pool_v` | Q6 mt | sans objet | — | tuned_v de Q6 non écrivible |
| `q6 mt_pool_s` | Q6 mt | sans objet | — | tuned_s de Q6 présente : mt_pool l'exécute |
| `q1 mt_pool` | Q1 mt | présente | `k6 mt q1` | équipe OpenMP |
| `q1 mt_pool_v` | Q1 mt | sans objet | — | tuned_v de Q1 non écrivible |
| `q1 mt_pool_s` | Q1 mt | écrite | `k6 mt_pool_s q1` | équipe OpenMP, chaque quart : tuned_s |
| `k7 tuned_pf` | K7 | non écrivible | — | pas d'instruction de préchargement : grille E4 = 0 ; la variante tuned publiée lit par lots les cases (chargements anticipés) avec un autre hachage |
| `k7 tuned_oa` | K7 | écrite | `k7 tuned_oa` | la table de tuned_pf sans préchargement ni lots ; produit de Fibonacci modulo 2^32 par moitiés de 16 bits (entiers signés de 64 bits) |
| `k8 tuned_val` | K8 | écrite | `k8 tuned_val` | arguments value, arène de nœuds de 16 octets |
| `k8 tuned_it` | K8 | écrite | `k8 tuned_it` | piles en tableaux fixes (64) |
| `k9 tuned_v` | K9 | non écrivible | — | grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt |
| `k9 mt_pool` | K9 mt | présente | `k9 mt` | équipe OpenMP, quatre blocs de colonnes |
| `k9 mt_pool_v` | K9 mt | sans objet | — | tuned_v de K9 non écrivible |
| `k5 rq_acc16` (R) | K5 | écrite | `k5 rq_acc16` | forme de bench/fortran_exp (remarque sur Fortran) : quatre accumulateurs écrits comme des tableaux de 16 valeurs, une réduction finale ; propre à Fortran, qui n'a pas de type vectoriel (K5 tuned_v non écrivible) |
| `k8 rq_aos` (R) | K8 | écrite | `k8 rq_aos` | forme de bench/fortran_exp (remarque sur Fortran) : la variante tuned (état par référence) sur une arène de nœuds de 16 octets au lieu de trois tableaux |
