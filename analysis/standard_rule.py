"""Test 1 de la confrontation (docs/CONFRONTATION.md, section 3) : ma matrice de capacités sous la règle du standard
du « Banc de sympathie mécanique ».

Base : notes de la règle v2 (C3 retiré). Seules les cellules ci-dessous changent ; chacune porte sa raison. Classes :
1 = standard et complet ; 0,5 = standard mais partiel ; 0,25 = seulement par un moyen non standard (extension,
builtin ou intrinsèque du compilateur hors de la bibliothèque standard, POSIX ou glibc pour C et C++, option globale,
module expérimental, nightly, en incubation, privé ou « package », FFI) ; 0 = absent.
« Standard » suit leurs règles d'interprétation : norme plus bibliothèque livrée avec la chaîne de référence ; pour C
et C++, la norme ISO seule ; une liaison au système livrée dans la bibliothèque standard du langage compte, un appel
système brut ou une extension de la glibc non. Une fonction publique de la bibliothèque standard compte même quand
elle donne accès au générateur de code (Base.llvmcall de Julia, llvm_intrinsic de Mojo) ; l'import de code C (Nim
importc) est une FFI. Table établie le 30 octobre 2026 avant tout calcul du test 1 ; c'est un jugement de l'auteur.
"""

R_OVERRIDES = {
    # C : ISO C23 et sa bibliothèque seulement
    ("c", "A3"): (0.5, "champs de bits standard (disposition propre à l'implémentation) ; packed seulement par attribut"),
    ("c", "C1"): (0.25, "vector_size : extension de gcc et clang"),
    ("c", "C2"): (0.25, "immintrin.h : intrinsèques du compilateur, hors norme"),
    ("c", "C4"): (0.25, "#pragma clang fp reassociate, -ffast-math : extensions"),
    ("c", "C5"): (0.25, "OpenMP : spécification externe et option -fopenmp"),
    ("c", "D3"): (0.25, "__GCC_DESTRUCTIVE_SIZE et sysconf : extension et glibc, hors norme (erratum du 30/10)"),
    ("c", "D4"): (0.25, "sched_setaffinity : glibc, hors ISO C"),
    ("c", "D5"): (0.5, "atomic_thread_fence (C11) ; pause seulement par intrinsèque"),
    ("c", "E2"): (0.25, "__asm__ : extension (annexe J, hors norme)"),
    ("c", "E3"): (0.25, "__builtin_expect : builtin ; C23 n'a pas d'attribut de probabilité"),
    ("c", "E4"): (0.25, "__builtin_prefetch : builtin"),
    ("c", "F4"): (0.25, "mmap : POSIX, hors ISO C"),
    # C++ : ISO C++26 et sa bibliothèque seulement
    ("cpp", "A3"): (0.5, "champs de bits ; packed seulement par attribut"),
    ("cpp", "C2"): (0.25, "immintrin.h : hors norme"),
    ("cpp", "C5"): (0.5, "std::execution::par_unseq (norme) exécuté en série par libstdc++ sans TBB ; OpenMP hors norme"),
    ("cpp", "D4"): (0.25, "sched_setaffinity : glibc"),
    ("cpp", "D5"): (0.5, "atomic_thread_fence ; pause seulement par intrinsèque"),
    ("cpp", "E4"): (0.25, "__builtin_prefetch : builtin"),
    ("cpp", "E5"): (0.25, "__restrict__ : extension"),
    ("cpp", "F4"): (0.25, "mmap : POSIX"),
    # Rust stable (std::arch est standard)
    ("rust", "C1"): (0.25, "std::simd : nightly seulement"),
    # D : druntime et Phobos ; ldc.* est propre au compilateur
    ("d", "B2"): (0.25, "std.experimental.allocator : expérimental"),
    ("d", "C2"): (0.25, "ldc.gccbuiltins_x86 : propre à LDC"),
    ("d", "C4"): (0.25, "@fastmath (ldc.attributes) : propre à LDC"),
    ("d", "E3"): (1, "core.builtins.likely, unlikely et expect (druntime)"),
    ("d", "E4"): (1, "core.simd.prefetch (druntime)"),
    ("d", "E5"): (0.25, "@restrict (ldc.attributes) : propre à LDC"),
    # C3
    ("c3", "C2"): (0.25, "builtins $$ réservés à la bibliothèque standard (avertissement du compilateur)"),
    # Nim
    ("nim", "C2"): (0.25, "importc d'intrinsèques C : FFI"),
    ("nim", "C4"): (0.25, "--passC:-ffast-math : option globale"),
    ("nim", "C5"): (0.25, "itérateur || : demande OpenMP au compilateur C (option globale)"),
    ("nim", "E4"): (0.25, "importc de __builtin_prefetch : FFI"),
    # Ada 2022 et ses annexes ; unités GNAT.*, pragmas et builtins GCC hors norme
    ("ada", "C1"): (0.25, "Machine_Attribute vector_type : propre à GNAT (erratum du 30/10, remarque sur Ada)"),
    ("ada", "C2"): (0.25, "builtins GCC importés (Intrinsic) et type vectoriel GCC : propres à GNAT/GCC"),
    ("ada", "C4"): (0.25, "option globale seulement"),
    ("ada", "D2"): (0.5, "System.Atomic_Operations (Ada 2022) sans ordre explicite ; builtins __atomic_* hors norme"),
    ("ada", "D5"): (0.25, "barrière et pause seulement par builtins importés"),
    ("ada", "E3"): (0.25, "__builtin_expect importé"),
    ("ada", "E4"): (0.25, "__builtin_prefetch importé"),
    ("ada", "F4"): (0.25, "System.Mmap : unité interne de GNAT"),
    # Fortran 2023 ; OpenMP hors norme
    ("fortran", "C4"): (0.25, "!$omp simd reduction : OpenMP"),
    ("fortran", "C5"): (0.5, "do concurrent (norme) ; exécution parallèle seulement par option du compilateur ou OpenMP"),
    ("fortran", "D1"): (0.25, "threads seulement par OpenMP ; les cotableaux sont des images (bibliothèque externe)"),
    ("fortran", "D2"): (0.5, "sous-programmes atomiques (Fortran 2008) sans ordre mémoire ; ordres seulement par OpenMP"),
    ("fortran", "D4"): (0.25, "proc_bind, OMP_PLACES : OpenMP"),
    ("fortran", "D5"): (0.25, "!$omp flush : OpenMP"),
    # Chapel : modules standard ; modules « package » et options globales hors norme
    ("chapel", "C4"): (0.25, "--no-ieee-float : option globale"),
    ("chapel", "D4"): (0.25, "variables d'environnement de l'exécutif"),
    ("chapel", "E4"): (0.25, "module « package » Prefetch"),
    # Julia
    ("julia", "D4"): (0.25, "JULIA_EXCLUSIVE : variable d'environnement globale"),
    ("julia", "E5"): (0.25, "Base.Experimental.@aliasscope : expérimental"),
    # Mojo : modules publics de la bibliothèque standard
    ("mojo", "D1"): (0.25, "std.runtime._asyncrt : module privé"),
    # Go sans GOEXPERIMENT
    ("go", "B2"): (0.25, "arena derrière GOEXPERIMENT=arenas"),
    ("go", "C1"): (0.25, "paquet simd derrière GOEXPERIMENT=simd"),
    ("go", "C2"): (0.25, "simd/archsimd : expérimental"),
    ("go", "D4"): (0.25, "appel système brut (syscall.RawSyscall) : niveau 1 dans leur règle"),
    # Java : modules java.* et jdk.* hors incubation et hors unités internes
    ("java", "C1"): (0.25, "Vector API : en incubation"),
    ("java", "C4"): (0.25, "réduction sans ordre de la Vector API : en incubation"),
    ("java", "D3"): (0.25, "@Contended : unité interne (jdk.internal) et option -XX"),
}


def c_cells_r(c3):
    """Cellules sous leur règle : notes v2 (sans C3), remplacées par R_OVERRIDES."""
    from analyze_v2 import c_cells
    cells = c_cells("v2", c3)
    for (l, cap), (v, _why) in R_OVERRIDES.items():
        if l in cells and cap in cells[l]:
            cells[l][cap] = v
    return cells
