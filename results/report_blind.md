# Notation à l'aveugle : comparaison du second juge

Plan : `docs/CONFRONTATION.md`, addendum. Données du juge : `results/blind_notation.json`, notes `results/blind_notes.md`.

| Comparaison | Cellules | Accord exact | Kappa pondéré | Spearman | À un niveau près |
|---|---|---|---|---|---|
| (1) juge règle A / ma matrice v2 | 88 | 89 % | 0,75 | 0,84 | — |
| (2) juge règle B / ma table du test 1 | 88 | 82 % | 0,80 | 0,89 | — |
| (3) juge principes / leur grille | 48 | 56 % | 0,46 | 0,65 | 94 % |

Repère : sur les mêmes principes et les mêmes 8 langages, Spearman entre leur grille et ma table du test 1 : 0,65.

**Verdict selon le critère fixé avant le lancement : l'écart tient aux règles en partie (kappa entre 0,4 et 0,6).**

| Langage | Accord règle A | Accord règle B | Principes à un niveau près |
|---|---|---|---|
| C | 91 % | 91 % | 100 % |
| C++ | 100 % | 91 % | 100 % |
| Rust | 91 % | 82 % | 100 % |
| Zig | 100 % | 91 % | 100 % |
| Odin | 82 % | 73 % | 100 % |
| D | 91 % | 82 % | 83 % |
| Nim | 82 % | 73 % | 83 % |
| C# | 73 % | 73 % | 83 % |

Ordre des 8 langages selon le juge : règle A C, C++, D, Zig, Odin, Nim, Rust, C# ; règle B D, Zig, Odin, Rust, C#, C++, Nim, C ; principes D, Zig, Odin, Rust, C++, Nim, C#, C.

## Désaccords (1), règle A

* C D3 : juge 1,00, moi 0,00 — sysconf(_SC_LEVEL1_DCACHE_LINESIZE) (glibc) ; macro __GCC_DESTRUCTIVE_SIZE prédéfinie en mode C par gcc-16 et clang-23 ; alignas normatif mais sans taille (extension)
* Rust D3 : juge 0,50, moi 0,00 — aucun utilitaire public ; CachePadded privé (std::sync::mpmc::utils) ; #[repr(align(N))] sans constante ; crossbeam (tiers) (experimental)
* Odin C4 : juge 0,50, moi 0,00 — @(fast_math={.Allow_Reassoc}) documenté, mais le compilateur livré n'applique jamais reassoc (llvm_backend_opt.cpp:63 teste l'indice 0 comme masque) ; reste simd.reduce_add_pairs/bisect sur vecteurs explicites (standard_partiel)
* Odin D3 : juge 0,50, moi 0,00 — base:runtime.MAP_CACHE_LINE_SIZE (64, public mais propre à l'implémentation des map) ; pas de constante générale (standard_partiel)
* D D3 : juge 1,00, moi 0,00 — core.cpuid.dataCaches()[i].lineSize (documenté) ; std.parallelism.cacheLineSize (standard)
* Nim C5 : juge 0,50, moi 1,00 — itérateur `||` de system (#pragma omp parallel for) : exige -fopenmp en passC/passL, des contrôles désactivés et une globale exportc pour reduction ; instruction parallel expérimentale ; std/threadpool déprécié (standard_partiel)
* Nim D3 : juge 0,50, moi 0,00 — aucune constante publique ; const CacheLineSize = 64 privée dans std/threadpool (déprécié) ; {.align(N).} sans taille (experimental)
* C# D2 : juge 0,50, moi 1,00 — Volatile.Read (acquire) / Volatile.Write (release), Interlocked.* (barrière complète) ; ni relaxed explicite ni paramètre d'ordre (standard_partiel)
* C# D3 : juge 0,50, moi 0,00 — aucune constante publique ; PaddingFor32, PaddedReference, CacheLineSeparated internes à System.Private.CoreLib (experimental)
* C# D4 : juge 1,00, moi 0,50 — Process.ProcessorAffinity (Linux et Windows) ; ProcessThread.ProcessorAffinity Windows seulement (standard)

## Désaccords (2), règle B

* C D3 : juge 0,25, moi 0,00 — sysconf(_SC_LEVEL1_DCACHE_LINESIZE) (glibc) ; macro __GCC_DESTRUCTIVE_SIZE prédéfinie en mode C par gcc-16 et clang-23 ; alignas normatif mais sans taille (extension)
* C++ C1 : juge 0,50, moi 1,00 — std::simd (<simd>, C++26) avec -std=c++26 ; extensions vectorielles GCC (vector_size) stables et portables (standard_partiel)
* Rust D3 : juge 0,25, moi 0,00 — aucun utilitaire public ; CachePadded privé (std::sync::mpmc::utils) ; #[repr(align(N))] sans constante ; crossbeam (tiers) (experimental)
* Rust D4 : juge 0,25, moi 0,00 — aucune API std ; sched_setaffinity par FFI (extern "C" ou crate libc) (externe)
* Zig C2 : juge 0,25, moi 0,50 — pas de module d'intrinsèques ; assembleur en ligne (le langref déclare les contraintes « still considered unstable ») ; extern fn @"llvm.x86.*" accepté mais non documenté ; @cImport supprimé (experimental)
* Odin C2 : juge 0,50, moi 1,00 — core:simd/x86 (SSE à AVX assez complets, mais AVX2 12 procédures, AVX-512F 8, AVX-512BW 6) ; intrinsèques LLVM importées par foreign + @(link_name="llvm.x86...") (mécanisme de core:sys/llvm) (standard_partiel)
* Odin C4 : juge 0,50, moi 0,00 — @(fast_math={.Allow_Reassoc}) documenté, mais le compilateur livré n'applique jamais reassoc (llvm_backend_opt.cpp:63 teste l'indice 0 comme masque) ; reste simd.reduce_add_pairs/bisect sur vecteurs explicites (standard_partiel)
* Odin D3 : juge 0,50, moi 0,00 — base:runtime.MAP_CACHE_LINE_SIZE (64, public mais propre à l'implémentation des map) ; pas de constante générale (standard_partiel)
* D C2 : juge 0,50, moi 0,25 — ldc.gccbuiltins_x86 (437 intrinsèques avx512 via pragma(LDC_intrinsic)) et asm de style GCC ; l'assembleur en ligne normatif de D accepte SSE mais pas les opcodes VEX/AVX sous LDC (standard_partiel)
* D D3 : juge 1,00, moi 0,00 — core.cpuid.dataCaches()[i].lineSize (documenté) ; std.parallelism.cacheLineSize (standard)
* Nim C1 : juge 0,25, moi 0,00 — rien dans la std ; seulement par {.emit.} d'un typedef vector_size GCC et de fonctions C d'appoint importées (externe)
* Nim C5 : juge 0,50, moi 0,25 — itérateur `||` de system (#pragma omp parallel for) : exige -fopenmp en passC/passL, des contrôles désactivés et une globale exportc pour reduction ; instruction parallel expérimentale ; std/threadpool déprécié (standard_partiel)
* Nim D3 : juge 0,25, moi 0,00 — aucune constante publique ; const CacheLineSize = 64 privée dans std/threadpool (déprécié) ; {.align(N).} sans taille (experimental)
* C# D2 : juge 0,50, moi 1,00 — Volatile.Read (acquire) / Volatile.Write (release), Interlocked.* (barrière complète) ; ni relaxed explicite ni paramètre d'ordre (standard_partiel)
* C# D3 : juge 0,25, moi 0,00 — aucune constante publique ; PaddingFor32, PaddedReference, CacheLineSeparated internes à System.Private.CoreLib (experimental)
* C# D4 : juge 1,00, moi 0,50 — Process.ProcessorAffinity (Linux et Windows) ; ProcessThread.ProcessorAffinity Windows seulement (standard)

## Désaccords (3), leurs principes

* C P10 : juge 2, eux 1 — Disposition des structures et alignas sont normatifs, mais prefetch et taille de ligne restent hors norme (__builtin_prefetch, sysconf).
* C++ P4 : juge 3, eux 4 — std::hardware_destructive_interference_size et alignas sont normatifs et stables depuis C++17.
* C++ P8 : juge 2, eux 3 — std::simd est dans C++26 mais GCC 16 déclare C++26 « highly experimental » (pas de __cpp_lib_simd, x86 seulement) ; std::reduce autorise la réassociation ; les intrinsèques sont hors norme.
* C++ P10 : juge 2, eux 1 — Disposition, alignas, hardware_constructive_interference_size et allocateurs pmr sont normatifs, mais aucun prefetch standard.
* C++ P12 : juge 2, eux 3 — std::thread et hardware_concurrency sont normatifs ; l'affinité ne passe que par native_handle et la glibc.
* Zig P4 : juge 3, eux 4 — std.atomic.cache_line, documenté contre le faux partage, et align() sont de premier ordre.
* Zig P5 : juge 3, eux 2 — std.Thread, atomiques avec AtomicOrder et Io.Mutex sont standard ; @fence a disparu et aucune course n'est diagnostiquée.
* Zig P10 : juge 3, eux 4 — @prefetch, align, structs extern/packed, std.MultiArrayList (SoA) et allocateurs explicites sont standard.
* Zig P12 : juge 3, eux 4 — std.Thread, Thread.getCpuCount et std.os.linux.sched_setaffinity sont dans la std.
* Odin P12 : juge 3, eux 4 — core:thread, os.get_processor_core_count et core:sys/linux.sched_setaffinity sont dans la bibliothèque livrée.
* D P4 : juge 3, eux 2 — align(N) et la taille de ligne via core.cpuid.dataCaches().lineSize ou std.parallelism.cacheLineSize sont standard (valeur connue à l'exécution).
* D P5 : juge 4, eux 2 — TLS par défaut et qualificatif shared diagnostiqué (RMW sur shared rejeté, spawn refuse les alias mutables locaux), plus core.atomic à ordres explicites.
* D P9 : juge 3, eux 2 — core.builtins.likely/unlikely/expect sont standard et honorés par LDC.
* D P12 : juge 3, eux 4 — core.thread, core.cpuid (cœurs et threads), std.parallelism.totalCPUs et core.sys.linux.sched sont standard.
* Nim P5 : juge 4, eux 3 — Threads et std/atomics à ordres explicites ; l'effet gcsafe rejette par défaut les procédures de thread qui touchent des globales gérées par le GC, et {.guard.} vérifie les verrous.
* Nim P9 : juge 3, eux 2 — likely/unlikely sont fournis par system.
* Nim P10 : juge 2, eux 0 — Objets valeur, seq contiguës et {.align.} sont standard, mais pas de prefetch hors importc de __builtin_prefetch.
* C# P4 : juge 2, eux 0 — StructLayout(Explicit, Size)/FieldOffset permettent le padding, mais aucune constante publique (les aides de padding de CoreLib sont internes).
* C# P8 : juge 3, eux 2 — Vector<T>, Vector128/256/512 et intrinsèques X86 (Avx512F, Avx10v2) sont dans la BCL ; aucune réassociation automatique.
* C# P9 : juge 1, eux 2 — Aucune indication de branchement dans le langage ; seul le PGO dynamique du runtime, réglage global actif par défaut, agit sur la disposition des branches.
* C# P12 : juge 2, eux 3 — Environment.ProcessorCount et Process.ProcessorAffinity (processus entier) ; l'affinité par thread est réservée à Windows et il n'y a pas d'API de topologie.
