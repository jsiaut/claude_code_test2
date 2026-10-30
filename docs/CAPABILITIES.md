# Matrice de capacités (pilier C)

● = 1 (présente, documentée, vérifiée) · ◐ = 0,5 (partielle : expérimentale, propre à un compilateur, livrée hors norme ou limitée) · ○ = 0 (absente, ou seulement par une bibliothèque tierce ou une FFI).
C3 est **mesurée** sur le code machine de la boucle chaude de K4 et de K9 en natural (`tools/c3_measure.py`). Les justifications et preuves de chaque cellule suivent le tableau.

| Capacité | C | C++ | Rust | Zig | Odin | C3 | D | Nim | Ada | Fortran | Chapel | Mojo | Go | C# | Java | Julia | Haskell | OCaml | JS | Python | Lua |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** (25 %) | | | | | | | | | | | | | | | | | | | | | |
| A1 agrégats valeurs en ligne dans les tableaux | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ◐ | ○ | ○ | ◐ | ○ |
| A2 ordre/taille des champs, disposition C, offsetof | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ● | ● | ● | ◐ | ● | ◐ | ○ | ○ | ◐ | ○ |
| A3 disposition au bit près (packed, champs de bits) | ● | ● | ◐ | ● | ● | ● | ● | ● | ● | ○ | ○ | ○ | ○ | ◐ | ◐ | ○ | ○ | ○ | ○ | ◐ | ○ |
| A4 alignement explicite >= 64 o | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ○ | ○ | ◐ | ○ |
| A5 unions et réinterprétation de bits | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ◐ | ◐ | ● | ◐ | ● | ◐ | ◐ | ◐ | ◐ | ◐ |
| A6 SoA natif | ○ | ○ | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| A7 tableaux fixes en ligne dans les agrégats | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ○ | ○ | ○ | ◐ | ○ |
| A8 types numériques étroits de stockage | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ◐ | ◐ | ○ |
| **B** (20 %) | | | | | | | | | | | | | | | | | | | | | |
| B1 pas de GC traçant imposé | ● | ● | ● | ● | ● | ● | ◐ | ● | ● | ● | ● | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| B2 allocateurs personnalisés / arènes de premier ordre | ◐ | ● | ◐ | ● | ● | ● | ◐ | ◐ | ● | ○ | ○ | ◐ | ◐ | ◐ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ |
| B3 allocation sur la pile / en ligne | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ◐ | ● | ○ | ◐ | ○ | ○ | ○ | ○ | ○ |
| B4 pas d'allocations cachées | ● | ◐ | ● | ● | ● | ● | ◐ | ◐ | ● | ◐ | ◐ | ● | ◐ | ◐ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ |
| B5 mémoire brute (pointeurs) | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ◐ | ◐ | ○ |
| **C** (20 %) | | | | | | | | | | | | | | | | | | | | | |
| C1 types vectoriels portables | ◐ | ● | ◐ | ● | ● | ● | ● | ○ | ○ | ○ | ○ | ● | ◐ | ● | ◐ | ◐ | ◐ | ○ | ○ | ○ | ○ |
| C2 intrinsèques de la cible | ● | ● | ● | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ○ | ○ | ◐ | ◐ | ● | ○ | ◐ | ○ | ○ | ○ | ○ | ○ |
| C3 auto-vectorisation (mesurée) | ● | ● | ◐ | ○ | ● | ● | ◐ | ◐ | ◐ | ◐ | ● | ○ | ○ | ○ | ◐ | ● | ○ | ○ | ○ | ○ | ○ |
| C4 contrôle de la réassociation flottante | ◐ | ● | ● | ● | ○ | ○ | ◐ | ◐ | ◐ | ◐ | ◐ | ○ | ○ | ○ | ◐ | ● | ○ | ○ | ○ | ○ | ○ |
| C5 parallélisme de données | ◐ | ◐ | ○ | ○ | ○ | ○ | ● | ◐ | ○ | ● | ● | ○ | ○ | ● | ● | ● | ◐ | ○ | ○ | ◐ | ○ |
| **D** (15 %) | | | | | | | | | | | | | | | | | | | | | |
| D1 threads parallèles en mémoire partagée | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ◐ | ● | ● | ● | ● | ● | ● | ◐ | ◐ | ○ |
| D2 atomiques à ordres mémoire explicites | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ◐ | ● | ● | ◐ | ● | ● | ● | ◐ | ◐ | ◐ | ○ | ○ |
| D3 aide ligne de cache | ◐ | ● | ○ | ● | ◐ | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | ○ | ○ | ● | ○ | ○ | ○ |
| D4 affinité CPU | ◐ | ◐ | ○ | ◐ | ◐ | ○ | ◐ | ● | ● | ◐ | ◐ | ○ | ◐ | ◐ | ○ | ◐ | ◐ | ○ | ○ | ◐ | ○ |
| D5 barrières et indication d'attente active | ◐ | ◐ | ● | ◐ | ● | ◐ | ● | ● | ◐ | ◐ | ◐ | ◐ | ○ | ● | ● | ◐ | ○ | ● | ◐ | ○ | ○ |
| **E** (10 %) | | | | | | | | | | | | | | | | | | | | | |
| E1 code natif inspectable | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ● | ● | ◐ | ○ | ○ |
| E2 assembleur en ligne | ◐ | ● | ● | ● | ● | ● | ● | ● | ● | ○ | ○ | ● | ◐ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ |
| E3 indications de branchement | ◐ | ● | ● | ● | ● | ● | ◐ | ● | ◐ | ○ | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| E4 préchargement explicite | ◐ | ◐ | ● | ● | ● | ● | ◐ | ◐ | ◐ | ○ | ◐ | ● | ○ | ● | ○ | ◐ | ● | ○ | ○ | ○ | ○ |
| E5 garanties de non-aliasing | ● | ◐ | ● | ● | ● | ● | ◐ | ● | ○ | ● | ○ | ◐ | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ |
| E6 contrôle local des vérifications de bornes | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ○ | ● | ● | ● | ○ | ◐ | ○ |
| E7 calcul à la compilation + génériques monomorphisés | ◐ | ● | ● | ● | ◐ | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ◐ | ○ | ● | ◐ | ○ | ○ | ○ | ○ |
| **F** (10 %) | | | | | | | | | | | | | | | | | | | | | |
| F1 tableaux multidimensionnels contigus | ● | ● | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ● | ● | ● | ◐ | ◐ | ● | ○ | ● | ● | ● | ○ | ◐ | ○ |
| F2 localité / distribution (PGAS, NUMA) | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | ● | ○ | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ |
| F3 entiers fixes signés et non signés modulaires | ● | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ◐ | ○ | ◐ |
| F4 fichiers projetés + réinterprétation sans copie | ◐ | ◐ | ○ | ● | ◐ | ◐ | ● | ● | ◐ | ○ | ○ | ○ | ◐ | ● | ● | ● | ○ | ● | ○ | ● | ○ |

## Justifications

### C

* **A** : A1 = 1 (tableaux de struct (sonde)) ; A2 = 1 (offsetof (sonde)) ; A3 = 1 (champs de bits standard ; packed par attribut (sonde)) ; A4 = 1 (alignas, aligned_alloc (sonde)) ; A5 = 1 (union, memcpy (sonde)) ; A6 = 0 (aucun) ; A7 = 1 (float v[16] dans struct (sonde)) ; A8 = 1 (stdint.h)
* **B** : B1 = 1 (pas de GC) ; B2 = 0.5 (malloc seulement ; arènes à la main (bench K8 tuned)) ; B3 = 1 (tableaux sur la pile, VLA) ; B4 = 1 (aucune allocation implicite) ; B5 = 1 (pointeurs)
* **C** : C1 = 0.5 (vector_size : extension gcc/clang (sonde)) ; C2 = 1 (immintrin.h (bench K5/K1/K6)) ; C3 = 1.0 (mesuré) ; C4 = 0.5 (-ffast-math, #pragma clang fp reassociate (extensions)) ; C5 = 0.5 (OpenMP (livré avec gcc/clang, hors norme C))
* **D** : D1 = 1 (threads.h / pthreads) ; D2 = 1 (stdatomic.h memory_order_*) ; D3 = 0.5 (__GCC_DESTRUCTIVE_SIZE prédéfini par clang et gcc ; sysconf (glibc) ; corrigé le 30/10, juge à l'aveugle) ; D4 = 0.5 (sched_setaffinity (glibc, hors ISO C) (sonde)) ; D5 = 0.5 (atomic_thread_fence ; pause seulement par intrinsèque)
* **E** : E1 = 1 (natif) ; E2 = 0.5 (__asm__ extension gcc/clang (sonde)) ; E3 = 0.5 (__builtin_expect (extension)) ; E4 = 0.5 (__builtin_prefetch / _mm_prefetch) ; E5 = 1 (restrict (C99)) ; E6 = 1 (aucune vérification de bornes) ; E7 = 0.5 (constexpr C23 limité, _Generic, pas de génériques)
* **F** : F1 = 1 (tableaux 2D C99 (bench K9 natural)) ; F2 = 0 (aucun) ; F3 = 1 (uintN_t modulaires) ; F4 = 0.5 (mmap POSIX (hors ISO C) (sonde))

### C++

* **A** : A1 = 1 (std::vector<struct> (bench)) ; A2 = 1 (offsetof, disposition standard (sonde)) ; A3 = 1 (champs de bits ; packed par attribut (sonde)) ; A4 = 1 (alignas + new aligné C++17 (sonde)) ; A5 = 1 (std::bit_cast, unions (sonde)) ; A6 = 0 (aucun en bibliothèque standard) ; A7 = 1 (std::array en ligne) ; A8 = 1 (cstdint)
* **B** : B1 = 1 (pas de GC) ; B2 = 1 (std::pmr, concept Allocator (bench K8 tuned_alloc)) ; B3 = 1 (objets sur la pile) ; B4 = 0.5 (std::function, exceptions, coroutines peuvent allouer) ; B5 = 1 (pointeurs)
* **C** : C1 = 1 (std::simd C++26 (bench K1/K5/K6)) ; C2 = 1 (immintrin.h) ; C3 = 1.0 (mesuré) ; C4 = 1 (std::reduce/transform_reduce et std::simd::reduce : ordre libre explicite) ; C5 = 0.5 (std::execution::par_unseq : série sans TBB tiers (libstdc++ : backend SERIAL, src c++config.h))
* **D** : D1 = 1 (std::jthread) ; D2 = 1 (std::memory_order) ; D3 = 1 (std::hardware_destructive_interference_size (sonde : 64)) ; D4 = 0.5 (pas en bibliothèque standard ; sched_setaffinity de la libc) ; D5 = 0.5 (atomic_thread_fence, std::barrier ; pause seulement par intrinsèque)
* **E** : E1 = 1 (natif) ; E2 = 1 (déclaration asm (norme, sens défini par l'implémentation) (sonde)) ; E3 = 1 ([[likely]]/[[unlikely]] C++20 (sonde)) ; E4 = 0.5 (__builtin_prefetch (extension)) ; E5 = 0.5 (__restrict__ (extension)) ; E6 = 1 (pas de vérification par défaut) ; E7 = 1 (templates + consteval (sonde))
* **F** : F1 = 1 (std::mdspan C++23 (sonde)) ; F2 = 0 (aucun) ; F3 = 1 (non signés modulaires) ; F4 = 0.5 (mmap POSIX + start_lifetime_as (sonde))

### Rust

* **A** : A1 = 1 (Vec<struct> (bench)) ; A2 = 1 (#[repr(C)] + offset_of! (sonde)) ; A3 = 0.5 (#[repr(packed)] ; pas de champs de bits (crates tierces)) ; A4 = 1 (#[repr(align(64))], Layout (bench ABuf)) ; A5 = 1 (union, to_bits, transmute (sonde)) ; A6 = 0 (aucun en std) ; A7 = 1 ([f32; 16]) ; A8 = 1 (u8/i16/f32)
* **B** : B1 = 1 (pas de GC) ; B2 = 0.5 (#[global_allocator] stable ; allocator_api (Vec::new_in) instable) ; B3 = 1 (valeurs sur la pile) ; B4 = 1 (allocations explicites (Box, Vec...)) ; B5 = 1 (*const/*mut, unsafe)
* **C** : C1 = 0.5 (std::simd : nightly uniquement) ; C2 = 1 (std::arch AVX-512 (bench)) ; C3 = 0.5 (mesuré) ; C4 = 1 (f32::algebraic_add/mul... stables depuis 1.98 (sonde)) ; C5 = 0 (rayon est tiers)
* **D** : D1 = 1 (std::thread) ; D2 = 1 (Ordering::Relaxed/Acquire/Release/SeqCst) ; D3 = 0 (pas de type de bourrage en std (crossbeam tiers)) ; D4 = 0 (pas d'affinité en std) ; D5 = 1 (std::hint::spin_loop + atomic::fence)
* **E** : E1 = 1 (natif) ; E2 = 1 (asm! stable (sonde)) ; E3 = 1 (std::hint::cold_path stable depuis 1.95 (sonde)) ; E4 = 1 (_mm_prefetch dans std::arch (sonde)) ; E5 = 1 (&mut exclusif -> noalias) ; E6 = 1 (get_unchecked, itérateurs) ; E7 = 1 (génériques monomorphisés + const fn)
* **F** : F1 = 0.5 (tableaux de tableaux de taille fixe seulement) ; F2 = 0 (aucun) ; F3 = 1 (wrapping_*, Wrapping<T>) ; F4 = 0 (pas de mmap en std (crate memmap2))

### Zig

* **A** : A1 = 1 (ArrayList(struct) (bench)) ; A2 = 1 (extern struct + @offsetOf (sonde)) ; A3 = 1 (packed struct, entiers u3... (sonde)) ; A4 = 1 (align(64) (sonde)) ; A5 = 1 (extern/packed union, @bitCast (sonde)) ; A6 = 1 (std.MultiArrayList (bench K1 soa)) ; A7 = 1 ([16]f32) ; A8 = 1 (u8/i16/f32)
* **B** : B1 = 1 (pas de GC) ; B2 = 1 (std.mem.Allocator passé explicitement, ArenaAllocator (bench K8)) ; B3 = 1 (valeurs sur la pile) ; B4 = 1 (pas d'allocation cachée (principe du langage)) ; B5 = 1 (pointeurs, [*]T)
* **C** : C1 = 1 (@Vector (bench)) ; C2 = 0.5 (pas d'intrinsèques x86 ; asm en ligne) ; C3 = 0.0 (mesuré) ; C4 = 1 (@setFloatMode(.optimized) par portée (sonde)) ; C5 = 0 (aucun)
* **D** : D1 = 1 (std.Thread) ; D2 = 1 (@atomicLoad/.monotonic/.acquire...) ; D3 = 1 (std.atomic.cache_line (src)) ; D4 = 0.5 (std.os.linux.sched_setaffinity (src, Linux)) ; D5 = 0.5 (std.atomic.spinLoopHint ; @fence retiré du langage (src))
* **E** : E1 = 1 (natif) ; E2 = 1 (asm volatile) ; E3 = 1 (@branchHint (sonde)) ; E4 = 1 (@prefetch (sonde)) ; E5 = 1 (noalias) ; E6 = 1 (@setRuntimeSafety par portée) ; E7 = 1 (comptime)
* **F** : F1 = 0.5 ([M][N]T de taille connue à la compilation seulement) ; F2 = 0 (aucun) ; F3 = 1 (+%, *% et types non signés) ; F4 = 1 (std.Io.File.MemoryMap (portable, depuis 0.16) + bytesAsSlice (sonde probe_f4) ; corrigé le 30/10, remarque sur Zig)

### Odin

* **A** : A1 = 1 ([dynamic]Particle (bench)) ; A2 = 1 (#raw_union/#packed, offset_of (sonde)) ; A3 = 1 (#packed + bit_field (sonde)) ; A4 = 1 (#align(64) (bench K3/K10)) ; A5 = 1 (#raw_union + transmute (sonde)) ; A6 = 1 (#soa intégré (bench K1)) ; A7 = 1 ([16]f32) ; A8 = 1 (u8/i16/f32)
* **B** : B1 = 1 (pas de GC) ; B2 = 1 (context.allocator, arènes core:mem (bench K8)) ; B3 = 1 (valeurs sur la pile) ; B4 = 1 (allocations explicites via l'allocateur du contexte) ; B5 = 1 (rawptr, [^]T)
* **C** : C1 = 1 (#simd[16]f32 (bench)) ; C2 = 0.5 (core:simd/x86 : AVX-512 très partiel (8 procédures AVX-512F, 6 AVX-512BW) ; corrigé le 30/10, juge à l'aveugle) ; C3 = 1.0 (mesuré) ; C4 = 0 (pas de contrôle local de la réassociation) ; C5 = 0 (core:thread.Pool seulement)
* **D** : D1 = 1 (core:thread) ; D2 = 1 (intrinsics.atomic_*_explicit avec ordre) ; D3 = 0.5 (base:runtime.MAP_CACHE_LINE_SIZE, public mais propre aux tables ; corrigé le 30/10, juge à l'aveugle) ; D4 = 0.5 (seulement par appel système brut core:sys/linux) ; D5 = 1 (intrinsics.cpu_relax + atomic_thread_fence (src))
* **E** : E1 = 1 (natif) ; E2 = 1 (asm (procédures assembleur)) ; E3 = 1 (intrinsics.expect) ; E4 = 1 (intrinsics.prefetch_read_data (src)) ; E5 = 1 (#no_alias (src)) ; E6 = 1 (#no_bounds_check (bench)) ; E7 = 0.5 (polymorphisme paramétrique monomorphisé ; pas d'exécution à la compilation)
* **F** : F1 = 0.5 (tableaux fixes et matrix[R,C] petits seulement) ; F2 = 0 (aucun) ; F3 = 1 (non signés, débordement défini) ; F4 = 0.5 (mmap par core:sys/linux ou core:mem/virtual (src))

### C3

* **A** : A1 = 1 (Particle[] (bench)) ; A2 = 1 (ordre déclaré, .offsetof (sonde)) ; A3 = 1 (@packed + bitstruct (sonde)) ; A4 = 1 (@align(128) (bench K10)) ; A5 = 1 (union + bitcast (sonde)) ; A6 = 0 (aucun) ; A7 = 1 (float[16]) ; A8 = 1 (char/short/float)
* **B** : B1 = 1 (pas de GC) ; B2 = 1 (interface Allocator, @pool temporaire (bench K8)) ; B3 = 1 (valeurs sur la pile) ; B4 = 1 (allocations explicites) ; B5 = 1 (pointeurs)
* **C** : C1 = 1 (vecteurs float[<16>] (bench)) ; C2 = 0.5 (builtins $$ (avertissement : réservés à la bibliothèque standard)) ; C3 = 1.0 (mesuré) ; C4 = 0 (pas de contrôle local) ; C5 = 0 (aucun)
* **D** : D1 = 1 (std::thread) ; D2 = 1 (std::atomic avec AtomicOrdering (src)) ; D3 = 0 (aucune) ; D4 = 0 (aucune) ; D5 = 0.5 (thread::fence ; pas d'indication pause (src))
* **E** : E1 = 1 (natif) ; E2 = 1 (asm) ; E3 = 1 (@likely/@unlikely (src)) ; E4 = 1 (prefetch dans std::core::builtin (src)) ; E5 = 1 (attribut @noalias (src du compilateur)) ; E6 = 1 (pas de vérification en -O3 ; @unchecked) ; E7 = 1 (modules génériques + macros à la compilation ($foreach...))
* **F** : F1 = 0.5 (tableaux fixes de tableaux fixes) ; F2 = 0 (aucun) ; F3 = 1 (débordement défini (enveloppant)) ; F4 = 0.5 (mmap par la liaison libc std::os::posix (src))

### D

* **A** : A1 = 1 (Particle[] (bench)) ; A2 = 1 (ordre déclaré, .offsetof (sonde)) ; A3 = 1 (align(1) + std.bitmanip.bitfields (sonde)) ; A4 = 1 (align(64) (sonde)) ; A5 = 1 (union, cast de pointeurs) ; A6 = 0 (aucun en Phobos) ; A7 = 1 (float[16]) ; A8 = 1 (ubyte/short/float)
* **B** : B1 = 0.5 (GC par défaut (new, tableaux, fermetures) ; @nogc et -betterC l'évitent) ; B2 = 0.5 (std.experimental.allocator (expérimental)) ; B3 = 1 (struct et tableaux statiques sur la pile) ; B4 = 0.5 (fermetures, ~, littéraux de tableaux allouent sur le tas GC (bench : bug de capture)) ; B5 = 1 (pointeurs)
* **C** : C1 = 1 (core.simd) ; C2 = 0.5 (ldc.gccbuiltins_x86 (propre à LDC)) ; C3 = 0.5 (mesuré) ; C4 = 0.5 (@fastmath de ldc.attributes (propre à LDC)) ; C5 = 1 (std.parallelism (parallel foreach, reduce))
* **D** : D1 = 1 (core.thread) ; D2 = 1 (core.atomic MemoryOrder raw/acq/rel/seq) ; D3 = 1 (std.parallelism.cacheLineSize, core.cpuid.dataCaches ; corrigé le 30/10, juge à l'aveugle) ; D4 = 0.5 (core.sys.linux.sched_setaffinity (liaison livrée)) ; D5 = 1 (core.atomic.pause + atomicFence (src))
* **E** : E1 = 1 (natif) ; E2 = 1 (asm (iasm DMD, ldc.llvmasm)) ; E3 = 0.5 (llvm_expect de ldc.intrinsics) ; E4 = 0.5 (llvm_prefetch de ldc.intrinsics) ; E5 = 0.5 (@restrict de ldc.attributes) ; E6 = 1 (arr.ptr[i] ; -boundscheck) ; E7 = 1 (templates + CTFE)
* **F** : F1 = 0.5 (tableaux statiques de tableaux statiques) ; F2 = 0 (aucun) ; F3 = 1 (débordement défini) ; F4 = 1 (std.mmfile (sonde))

### Nim

* **A** : A1 = 1 (seq[Particle] (bench)) ; A2 = 1 (ordre déclaré, offsetOf (sonde)) ; A3 = 1 ({.packed.} + {.bitsize.} (sonde)) ; A4 = 1 ({.align(64).} (sonde)) ; A5 = 1 ({.union.} + cast (sonde)) ; A6 = 0 (aucun) ; A7 = 1 (array[16, float32]) ; A8 = 1 (uint8/int16/float32)
* **B** : B1 = 1 (ARC/ORC : comptage de références déterministe) ; B2 = 0.5 (alloc/dealloc manuels ; pas d'interface d'allocateur) ; B3 = 1 (objets valeur sur la pile) ; B4 = 0.5 (fermetures, chaînes et seq allouent implicitement) ; B5 = 1 (ptr, cast)
* **C** : C1 = 0 (aucun type vectoriel en std) ; C2 = 0.5 (importc depuis immintrin.h (passage par le C)) ; C3 = 0.5 (mesuré) ; C4 = 0.5 (seulement --passC:-ffast-math global) ; C5 = 0.5 (itérateur || (OpenMP) ; threadpool obsolète)
* **D** : D1 = 1 (threads) ; D2 = 1 (std/atomics moRelaxed/moAcquire...) ; D3 = 0 (aucune) ; D4 = 1 (Thread.pinToCpu (src std/typedthreads)) ; D5 = 1 (cpuRelax (std/sysatomics) + fence (sonde))
* **E** : E1 = 1 (natif via C) ; E2 = 1 (instruction asm) ; E3 = 1 (likely/unlikely (system)) ; E4 = 0.5 (pas de prefetch en std ; importc __builtin_prefetch) ; E5 = 1 ({.noalias.}) ; E6 = 1 ({.boundChecks: off.} local, UncheckedArray) ; E7 = 1 (génériques + static/macros)
* **F** : F1 = 0.5 (array[M, array[N, T]] fixe) ; F2 = 0 (aucun) ; F3 = 1 (non signés modulaires, +%) ; F4 = 1 (std/memfiles (sonde))

### Ada

* **A** : A1 = 1 (tableaux d'enregistrements (bench)) ; A2 = 1 (clauses de représentation, 'Position (sonde)) ; A3 = 1 (clauses au bit près, pragma Pack (sonde)) ; A4 = 1 (aspect Alignment => 64/128 (bench K3/K10)) ; A5 = 1 (Unchecked_Union, Unchecked_Conversion (sonde)) ; A6 = 0 (aucun) ; A7 = 1 (tableaux contraints en ligne) ; A8 = 1 (Interfaces.Unsigned_8, Float)
* **B** : B1 = 1 (pas de GC) ; B2 = 1 (pools de stockage utilisateur, sous-pools (bench K8 tuned_alloc)) ; B3 = 1 (tout sur la pile par défaut) ; B4 = 1 (pas d'allocation de tas implicite (pile secondaire pour les retours non contraints)) ; B5 = 1 (System.Address, 'Address, Address_To_Access_Conversions)
* **C** : C1 = 0 (aucun type vectoriel standard) ; C2 = 0.5 (builtins GCC importés + Machine_Attribute vector_type (propre à GNAT) (bench K5)) ; C3 = 0.5 (mesuré) ; C4 = 0.5 (seulement par option globale) ; C5 = 0 (boucles parallèles d'Ada 2022 non implémentées par GNAT (src : gnat_rm))
* **D** : D1 = 1 (tâches) ; D2 = 0.5 (Ada standard : seq_cst seulement ; ordres via System.Atomic_Primitives (unité interne GNAT)) ; D3 = 0 (aucune) ; D4 = 1 (aspect CPU des tâches, Dispatching_Domains (src s-mudido)) ; D5 = 0.5 (barrières par atomiques ; pause par builtin importé)
* **E** : E1 = 1 (natif) ; E2 = 1 (System.Machine_Code.Asm) ; E3 = 0.5 (__builtin_expect importé) ; E4 = 0.5 (__builtin_prefetch importé (bench K7)) ; E5 = 0 (pas de garantie de non-aliasing des paramètres) ; E6 = 1 (pragma Suppress local (bench)) ; E7 = 1 (génériques instanciés + expressions statiques)
* **F** : F1 = 1 (tableaux multidimensionnels, Convention Fortran possible) ; F2 = 0 (annexe E (systèmes répartis) non livrée) ; F3 = 1 (types modulaires + entiers signés) ; F4 = 0.5 (System.Mmap (unité interne GNAT) (src))

### Fortran

* **A** : A1 = 1 (tableau de type dérivé (bench)) ; A2 = 0.5 (bind(c)/sequence ; pas d'offsetof) ; A3 = 0 (ni packed ni champs de bits) ; A4 = 0.5 (pas d'attribut standard ; sur-allocation + c_loc (bench)) ; A5 = 1 (TRANSFER (réinterprétation arbitraire)) ; A6 = 0 (aucun) ; A7 = 1 (composantes tableaux fixes) ; A8 = 1 (int8/int16/real32)
* **B** : B1 = 1 (pas de GC) ; B2 = 0 (aucun allocateur personnalisé) ; B3 = 1 (tableaux locaux fixes sur la pile) ; B4 = 0.5 (temporaires de tableaux implicites (copie à l'appel, expressions)) ; B5 = 1 (iso_c_binding : c_ptr, c_f_pointer)
* **C** : C1 = 0 (aucun type vectoriel) ; C2 = 0 (aucun) ; C3 = 0.5 (mesuré) ; C4 = 0.5 (!$omp simd reduction (OpenMP, livré avec gfortran/flang)) ; C5 = 1 (do concurrent, syntaxe tableau (standard) + OpenMP)
* **D** : D1 = 0.5 (pas de threads dans la norme (coarrays = images) ; OpenMP) ; D2 = 0.5 (OpenMP atomic avec clauses d'ordre ; atomic_define/atomic_ref sur coarrays) ; D3 = 0 (aucune) ; D4 = 0.5 (OMP_PROC_BIND/OMP_PLACES (OpenMP)) ; D5 = 0.5 (!$omp flush ; pas d'indication pause)
* **E** : E1 = 1 (natif) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 0 (aucun) ; E5 = 1 (les arguments muets ne s'aliasent pas (règle du langage)) ; E6 = 1 (pas de vérification par défaut) ; E7 = 0.5 (pas de génériques (prévus après 2023) ; expressions constantes)
* **F** : F1 = 1 (tableaux multidimensionnels natifs, ordre colonne) ; F2 = 0.5 (coarrays (multi-images via OpenCoarrays externe)) ; F3 = 0.5 (entiers signés seulement (unsigned = extension gfortran 15)) ; F4 = 0 (pas de mmap)

### Chapel

* **A** : A1 = 1 (tableau de records (bench)) ; A2 = 1 (c_offsetof (src CTypes)) ; A3 = 0 (aucun) ; A4 = 0.5 (allocate(..., alignment=) ; pas d'attribut de type (src)) ; A5 = 0.5 (transmute pour les réels ; unions sûres (src)) ; A6 = 0 (aucun) ; A7 = 1 (tuples homogènes en ligne) ; A8 = 1 (int(8), real(32))
* **B** : B1 = 1 (pas de GC (owned/shared/unmanaged)) ; B2 = 0 (aucun) ; B3 = 0.5 (records sur la pile ; tableaux toujours sur le tas) ; B4 = 0.5 (tableaux locaux et tâches allouent implicitement) ; B5 = 1 (c_ptr, c_ptrTo (bench K6))
* **C** : C1 = 0 (aucun ; les tuples ne sont vectorisés que par paires (bench, IR)) ; C2 = 0 (aucun hors blocs extern C) ; C3 = 1.0 (mesuré) ; C4 = 0.5 (--no-ieee-float global seulement (bench)) ; C5 = 1 (forall, reduce, promotion)
* **D** : D1 = 1 (tâches sur threads) ; D2 = 1 (memoryOrder.relaxed/acquire/release/seqCst (bench)) ; D3 = 0 (aucune) ; D4 = 0.5 (variables d'environnement de l'exécutif (qthreads)) ; D5 = 0.5 (atomicFence ; pas d'indication pause)
* **E** : E1 = 1 (natif (LLVM)) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 0.5 (module package Prefetch (bench K7)) ; E5 = 0 (aucun) ; E6 = 1 (accès c_ptr sans vérification ; --no-checks) ; E7 = 1 (génériques instanciés + param)
* **F** : F1 = 1 (tableaux multidimensionnels, domaines) ; F2 = 1 (locales, distributions Block/Cyclic/Stencil (src)) ; F3 = 1 (uint(32) enveloppant) ; F4 = 0 (pas de projection utilisateur (indication useMmap pour la lecture))

### Mojo

* **A** : A1 = 1 (List[Particle] (bench)) ; A2 = 1 (reflection field_offset (src)) ; A3 = 0 (aucun) ; A4 = 0.5 (alloc(alignment=) (bench K8) ; pas d'attribut de type) ; A5 = 0.5 (bitcast de scalaires/SIMD ; pas d'unions) ; A6 = 0 (aucun) ; A7 = 1 (InlineArray/Array[T, N]) ; A8 = 1 (UInt8/Float32)
* **B** : B1 = 1 (pas de GC (propriété)) ; B2 = 0.5 (alloc/free manuels ; pas d'interface d'allocateur) ; B3 = 1 (structs sur la pile) ; B4 = 1 (allocations explicites) ; B5 = 1 (UnsafePointer)
* **C** : C1 = 1 (SIMD[DType, N] (bench)) ; C2 = 0.5 (llvm_intrinsic (src)) ; C3 = 0.0 (mesuré) ; C4 = 0 (aucun contrôle local trouvé) ; C5 = 0 (parallelize absent de std (MAX) (src))
* **D** : D1 = 0.5 (seulement runtime._asyncrt, privé (bench)) ; D2 = 1 (Atomic avec Ordering RELAXED/ACQUIRE/RELEASE (src)) ; D3 = 0 (aucune) ; D4 = 0 (aucune) ; D5 = 0.5 (fence ; pas d'indication pause)
* **E** : E1 = 1 (natif (LLVM)) ; E2 = 1 (inlined_assembly (src)) ; E3 = 1 (likely/unlikely/expect (src)) ; E4 = 1 (prefetch (src)) ; E5 = 0.5 (exclusivité des références mut) ; E6 = 1 (unsafe_get, pointeurs) ; E7 = 1 (paramètres à la compilation, monomorphisation)
* **F** : F1 = 0.5 (pas de tableau multidimensionnel en std (LayoutTensor dans MAX)) ; F2 = 0 (aucun) ; F3 = 1 (UInt32 enveloppant) ; F4 = 0 (pas de mmap en std (src))

### Go

* **A** : A1 = 1 ([]Particle (bench)) ; A2 = 1 (ordre déclaré (gc), unsafe.Offsetof (sonde)) ; A3 = 0 (aucun) ; A4 = 0.5 (pas d'attribut ; sur-allocation + unsafe) ; A5 = 0.5 (math.Float32bits, unsafe ; pas d'unions) ; A6 = 0 (aucun) ; A7 = 1 ([16]float32) ; A8 = 1 (uint8/int16/float32)
* **B** : B1 = 0 (GC imposé) ; B2 = 0.5 (arena derrière GOEXPERIMENT=arenas (src)) ; B3 = 0.5 (décidé par l'analyse d'échappement) ; B4 = 0.5 (échappement, interfaces, fermetures allouent implicitement) ; B5 = 1 (unsafe.Pointer, unsafe.Add)
* **C** : C1 = 0.5 (paquet simd portable derrière GOEXPERIMENT=simd (src)) ; C2 = 0.5 (simd/archsimd expérimental (bench)) ; C3 = 0.0 (mesuré) ; C4 = 0 (la spécification interdit la réassociation) ; C5 = 0 (aucun)
* **D** : D1 = 1 (goroutines sur threads) ; D2 = 0.5 (sync/atomic séquentiellement cohérent seulement (store = XCHG mesuré)) ; D3 = 0 (CacheLinePad seulement dans internal/cpu et x/sys (src)) ; D4 = 0.5 (syscall brut SYS_SCHED_SETAFFINITY) ; D5 = 0 (ni pause ni barrière explicite)
* **E** : E1 = 1 (natif) ; E2 = 0.5 (assembleur Go dans des fichiers .s séparés) ; E3 = 0 (aucun (PGO seulement)) ; E4 = 0 (aucun exporté) ; E5 = 0 (aucun) ; E6 = 1 (accès non vérifiés locaux par unsafe.Add / unsafe.Slice) ; E7 = 0.5 (génériques par formes GC (dictionnaires), pas de CTFE)
* **F** : F1 = 0.5 ([M][N]T fixe seulement) ; F2 = 0 (aucun) ; F3 = 1 (débordement enveloppant défini) ; F4 = 0.5 (syscall.Mmap + unsafe.Slice)

### C#

* **A** : A1 = 1 (struct dans T[] (bench aos)) ; A2 = 1 (StructLayout Sequential/Explicit + FieldOffset (sonde)) ; A3 = 0.5 (Pack=1 ; pas de champs de bits) ; A4 = 0.5 (NativeMemory.AlignedAlloc ; pas d'attribut d'alignement de type) ; A5 = 1 (FieldOffset recouvrants, Unsafe.As, BitConverter (sonde)) ; A6 = 0 (aucun) ; A7 = 1 ([InlineArray(16)] (C# 12) (sonde)) ; A8 = 1 (byte/short/float)
* **B** : B1 = 0 (GC imposé) ; B2 = 0.5 (ArrayPool, NativeMemory ; pas d'allocateur d'objets) ; B3 = 1 (struct, stackalloc, Span) ; B4 = 0.5 (boxing, fermetures, LINQ allouent) ; B5 = 1 (pointeurs unsafe)
* **C** : C1 = 1 (Vector128/256/512<T> (bench)) ; C2 = 1 (System.Runtime.Intrinsics.X86 (bench)) ; C3 = 0.0 (mesuré) ; C4 = 0 (aucun) ; C5 = 1 (Parallel.For, PLINQ)
* **D** : D1 = 1 (threads) ; D2 = 1 (Volatile.Read/Write (acquire/release), Interlocked, accès simples) ; D3 = 0 (aucune) ; D4 = 0.5 (Process.ProcessorAffinity (processus)) ; D5 = 1 (Thread.SpinWait/SpinWait + Interlocked.MemoryBarrier)
* **E** : E1 = 1 (JIT/AOT, DOTNET_JitDisasm) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 1 (Sse.Prefetch0) ; E5 = 0 (aucun) ; E6 = 1 (Unsafe.Add, MemoryMarshal, pointeurs) ; E7 = 0.5 (génériques spécialisés pour les struct ; pas de CTFE)
* **F** : F1 = 1 (tableaux rectangulaires T[,] (bench K9)) ; F2 = 0 (aucun) ; F3 = 1 (uint/ulong, unchecked) ; F4 = 1 (MemoryMappedFile + pointeur (sonde))

### Java

* **A** : A1 = 0.5 (objets référencés (JEP 401 absente du JDK 27) ; tableaux de structures hors tas par l'API FFM (sonde)) ; A2 = 0.5 (aucun contrôle des objets ; MemoryLayout (FFM) pour la mémoire hors tas) ; A3 = 0.5 (FFM : dispositions non alignées (withByteAlignment(1)) ; pas de champs de bits (sonde)) ; A4 = 0.5 (Arena.allocate(taille, alignement) hors tas seulement) ; A5 = 0.5 (Float.floatToRawIntBits ; pas d'unions) ; A6 = 0 (aucun) ; A7 = 0.5 (objets : non ; FFM : sequenceLayout dans structLayout (sonde)) ; A8 = 1 (byte/short/float)
* **B** : B1 = 0 (GC imposé) ; B2 = 0.5 (Arena (FFM) pour les segments hors tas) ; B3 = 0 (pas d'agrégat sur la pile (scalar replacement non garanti)) ; B4 = 0 (boxing, varargs, lambdas) ; B5 = 0.5 (MemorySegment (accès vérifié, pas de pointeurs))
* **C** : C1 = 0.5 (Vector API, toujours en incubation (bench)) ; C2 = 0 (aucun) ; C3 = 0.5 (mesuré) ; C4 = 0.5 (réduction ADD de la Vector API sans ordre (incubation)) ; C5 = 1 (flux parallèles)
* **D** : D1 = 1 (threads) ; D2 = 1 (VarHandle plain/opaque/acquire/release/volatile) ; D3 = 0.5 (@Contended interne (jdk.internal, -XX:-RestrictContended)) ; D4 = 0 (aucune) ; D5 = 1 (Thread.onSpinWait + VarHandle.fullFence)
* **E** : E1 = 0.5 (JIT C2 ; désassemblage seulement avec hsdis (non livré)) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 0 (aucun) ; E5 = 0 (aucun) ; E6 = 0 (vérification toujours active) ; E7 = 0 (génériques effacés, pas de CTFE)
* **F** : F1 = 0 (tableaux de tableaux) ; F2 = 0 (aucun) ; F3 = 0.5 (entiers signés seulement + méthodes unsigned) ; F4 = 1 (FileChannel.map -> MemorySegment)

### Julia

* **A** : A1 = 1 (Vector{Particle} isbits en ligne (bench)) ; A2 = 1 (ordre déclaré, fieldoffset (src)) ; A3 = 0 (aucun) ; A4 = 0.5 (tableaux alignés par l'implémentation ; pas d'attribut) ; A5 = 1 (reinterpret pour tout type isbits) ; A6 = 0 (StructArrays est tiers) ; A7 = 1 (NTuple{16,Float32}) ; A8 = 1 (UInt8/Float32)
* **B** : B1 = 0 (GC imposé) ; B2 = 0 (aucun) ; B3 = 0.5 (structs isbits et tuples sur la pile ; tableaux sur le tas) ; B4 = 0.5 (instabilité de type et fermetures (Core.Box) allouent (bench : capture)) ; B5 = 1 (Ptr, unsafe_load, Libc.malloc)
* **C** : C1 = 0.5 (VecElement + llvmcall seulement (SIMD.jl tiers)) ; C2 = 0.5 (llvmcall vers intrinsèques LLVM) ; C3 = 1.0 (mesuré) ; C4 = 1 (@simd, @fastmath) ; C5 = 1 (Threads.@threads, @spawn)
* **D** : D1 = 1 (threads) ; D2 = 1 (@atomic :monotonic/:acquire/:release (src)) ; D3 = 0 (aucune) ; D4 = 0.5 (JULIA_EXCLUSIVE=1 (épinglage global)) ; D5 = 0.5 (Threads.atomic_fence ; pause interne seulement)
* **E** : E1 = 1 (@code_native) ; E2 = 0.5 (llvmcall (IR LLVM pouvant contenir asm)) ; E3 = 0 (aucun) ; E4 = 0.5 (llvmcall) ; E5 = 0.5 (Base.Experimental.@aliasscope / Const (expérimental) (src)) ; E6 = 1 (@inbounds) ; E7 = 1 (spécialisation par méthode + @generated)
* **F** : F1 = 1 (Array{T,N} colonne-majeur) ; F2 = 0.5 (Distributed, SharedArrays (processus)) ; F3 = 1 (UInt32 enveloppant) ; F4 = 1 (Mmap.mmap (sonde))

### Haskell

* **A** : A1 = 0.5 (pas de tableau d'enregistrements non boxés dans le langage ; tableaux Storable (base, Foreign.Marshal.Array)) ; A2 = 0.5 (Storable manuel (base)) ; A3 = 0 (aucun) ; A4 = 0.5 (allocaBytesAligned, tableaux épinglés alignés) ; A5 = 0.5 (castWord32ToFloat, unsafeCoerce#) ; A6 = 0 (aucun) ; A7 = 0 (aucun) ; A8 = 1 (Word8/Int16/Float (UArray))
* **B** : B1 = 0 (GC imposé) ; B2 = 0 (aucun (régions compactes : données immuables durables)) ; B3 = 0 (aucun) ; B4 = 0 (paresse, thunks, boxing omniprésents (bench : partage)) ; B5 = 1 (Foreign.Ptr, mallocBytes, peek/poke)
* **C** : C1 = 0.5 (primops SIMD (GHC.Exts) ; NCG faux en 9.14.1, LLVM requis (bench)) ; C2 = 0 (aucun) ; C3 = 0.0 (mesuré) ; C4 = 0 (aucun) ; C5 = 0.5 (par# (ghc-prim) ; parallel/strategies non livrés)
* **D** : D1 = 1 (RTS threadé, forkOn) ; D2 = 0.5 (IORef/MVar/STM, primops atomiques séquentiellement cohérents) ; D3 = 0 (aucune) ; D4 = 0.5 (forkOn + RTS -qa) ; D5 = 0 (aucun)
* **E** : E1 = 1 (natif) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 1 (primops prefetch*# (GHC.Exts)) ; E5 = 0 (aucun) ; E6 = 1 (unsafeRead/unsafeAt) ; E7 = 0.5 (Template Haskell ; spécialisation non garantie)
* **F** : F1 = 1 (UArray à indices tuples) ; F2 = 0 (aucun) ; F3 = 1 (Word32/Int32 enveloppants) ; F4 = 0 (pas de mmap dans base)

### OCaml

* **A** : A1 = 0 (enregistrements boxés (sauf flottants)) ; A2 = 0 (aucun contrôle) ; A3 = 0 (aucun) ; A4 = 0 (aucun) ; A5 = 0.5 (Int32.bits_of_float...) ; A6 = 0 (aucun) ; A7 = 0 (aucun) ; A8 = 0.5 (Bigarray int8/int16/float32 pour le stockage ; scalaires larges)
* **B** : B1 = 0 (GC imposé) ; B2 = 0 (aucun) ; B3 = 0 (flambda déboxe localement, sans garantie) ; B4 = 0 (boxing des flottants, fermetures, tuples) ; B5 = 0.5 (Bigarray hors tas, Obj)
* **C** : C1 = 0 (aucun en OCaml 5.5) ; C2 = 0 (aucun) ; C3 = 0.0 (mesuré) ; C4 = 0 (aucun) ; C5 = 0 (Domainslib est tiers)
* **D** : D1 = 1 (Domain (OCaml 5)) ; D2 = 0.5 (Atomic séquentiellement cohérent) ; D3 = 1 (Atomic.make_contended) ; D4 = 0 (aucune) ; D5 = 1 (Domain.cpu_relax + Atomic)
* **E** : E1 = 1 (natif) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 0 (aucun) ; E5 = 0 (aucun) ; E6 = 1 (unsafe_get, -unsafe) ; E7 = 0 (pas de monomorphisation (représentation uniforme))
* **F** : F1 = 1 (Bigarray.Array2 c_layout/fortran_layout) ; F2 = 0 (aucun) ; F3 = 0.5 (Int32/Int64 signés boxés ; pas de non signés) ; F4 = 1 (Unix.map_file (bench))

### JS

* **A** : A1 = 0 (objets référencés) ; A2 = 0 (aucun) ; A3 = 0 (aucun) ; A4 = 0 (aucun) ; A5 = 0.5 (vues typées sur le même ArrayBuffer, DataView) ; A6 = 0 (aucun) ; A7 = 0 (aucun) ; A8 = 0.5 (tableaux typés pour le stockage ; nombres f64)
* **B** : B1 = 0 (GC imposé) ; B2 = 0 (aucun) ; B3 = 0 (aucun) ; B4 = 0 (allocations implicites omniprésentes) ; B5 = 0.5 (ArrayBuffer, pas de pointeurs)
* **C** : C1 = 0 (SIMD.js retiré) ; C2 = 0 (aucun) ; C3 = 0.0 (mesuré) ; C4 = 0 (aucun) ; C5 = 0 (aucun)
* **D** : D1 = 0.5 (Workers isolés + SharedArrayBuffer) ; D2 = 0.5 (Atomics séquentiellement cohérents seulement) ; D3 = 0 (aucune) ; D4 = 0 (aucune) ; D5 = 0.5 (Atomics.pause (sonde) ; pas de barrière explicite)
* **E** : E1 = 0.5 (JIT (V8) ; --print-opt-code selon la compilation de node) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 0 (aucun) ; E5 = 0 (aucun) ; E6 = 0 (aucun) ; E7 = 0 (aucun)
* **F** : F1 = 0 (aucun) ; F2 = 0 (aucun) ; F3 = 0.5 (|0 et >>>0 sur 32 bits, BigInt.asUintN) ; F4 = 0 (pas de mmap dans node)

### Python

* **A** : A1 = 0.5 (ctypes.Structure en tableaux (stdlib) ; les objets Python sont référencés) ; A2 = 0.5 (ctypes (_fields_, offset)) ; A3 = 0.5 (ctypes _pack_ et champs de bits) ; A4 = 0.5 (sur-allocation + ctypes.addressof) ; A5 = 0.5 (struct.pack/unpack, ctypes.Union) ; A6 = 0 (numpy est tiers) ; A7 = 0.5 (tableaux ctypes dans Structure) ; A8 = 0.5 (array, memoryview.cast pour le stockage ; entiers arbitraires)
* **B** : B1 = 0 (comptage de références + GC de cycles) ; B2 = 0 (aucun) ; B3 = 0 (aucun) ; B4 = 0 (allocations omniprésentes) ; B5 = 0.5 (ctypes, mmap)
* **C** : C1 = 0 (aucun) ; C2 = 0 (aucun) ; C3 = 0.0 (mesuré) ; C4 = 0 (aucun) ; C5 = 0.5 (multiprocessing.Pool.map, concurrent.futures)
* **D** : D1 = 0.5 (threads avec GIL (version par défaut) ; sans GIL dans la version free-threaded) ; D2 = 0 (aucun atomique) ; D3 = 0 (aucune) ; D4 = 0.5 (os.sched_setaffinity (Unix)) ; D5 = 0 (aucun)
* **E** : E1 = 0 (interpréteur (JIT expérimental désactivé par défaut)) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 0 (aucun) ; E5 = 0 (aucun) ; E6 = 0.5 (seulement par pointeurs ctypes, non vérifiés) ; E7 = 0 (aucun)
* **F** : F1 = 0.5 (memoryview.cast(shape=...)) ; F2 = 0 (aucun) ; F3 = 0 (entiers à précision arbitraire) ; F4 = 1 (mmap + memoryview.cast sans copie (sonde))

### Lua

* **A** : A1 = 0 (tables) ; A2 = 0 (aucun) ; A3 = 0 (aucun) ; A4 = 0 (aucun) ; A5 = 0.5 (string.pack/unpack) ; A6 = 0 (aucun) ; A7 = 0 (aucun) ; A8 = 0 (nombres 64 bits seulement ; chaînes comme octets)
* **B** : B1 = 0 (GC imposé) ; B2 = 0 (aucun (lua_Alloc côté C)) ; B3 = 0 (aucun) ; B4 = 0 (allocations omniprésentes) ; B5 = 0 (aucun)
* **C** : C1 = 0 (aucun) ; C2 = 0 (aucun) ; C3 = 0.0 (mesuré) ; C4 = 0 (aucun) ; C5 = 0 (aucun)
* **D** : D1 = 0 (pas de threads (coroutines)) ; D2 = 0 (aucun) ; D3 = 0 (aucune) ; D4 = 0 (aucune) ; D5 = 0 (aucun)
* **E** : E1 = 0 (interpréteur) ; E2 = 0 (aucun) ; E3 = 0 (aucun) ; E4 = 0 (aucun) ; E5 = 0 (aucun) ; E6 = 0 (aucun) ; E7 = 0 (aucun)
* **F** : F1 = 0 (aucun) ; F2 = 0 (aucun) ; F3 = 0.5 (entiers 64 bits enveloppants ; pas de non signés (math.ult)) ; F4 = 0 (aucun)

