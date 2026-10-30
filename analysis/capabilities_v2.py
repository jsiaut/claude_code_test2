"""Pilier C, règle v2 (réponse à l'audit du 29 octobre 2026, section 3.6 ; plan : docs/ANALYSIS_V2.md).

Règle v1 (pré-enregistrée) : 0,5 pour une capacité « non standard mais livrée avec la chaîne officielle, ou
seulement via une extension du compilateur ». L'audit montre qu'elle pénalise les langages normalisés (C, C++,
Ada, Fortran) : pour un langage à implémentation unique, tout ce que livre la chaîne est « standard ».

Règle v2, la même pour tous les langages :
  1   la capacité s'exprime avec la chaîne de référence telle qu'elle est livrée (langage, bibliothèque
      standard et ses liaisons au système, extensions, attributs, pragmas et intrinsèques documentés du
      compilateur, y compris les builtins importés par le mécanisme d'import d'intrinsèques du langage, et la
      bibliothèque système de la plateforme pour C et C++), sous une forme stable, et complète pour l'usage
      décrit ;
  0,5 elle est expérimentale ou instable (nightly, GOEXPERIMENT, incubation, module « experimental »), réservée
      à une unité interne non documentée, ou partielle (option globale seulement, sous-ensemble) ;
  0   elle est absente, ou seulement accessible par une bibliothèque tierce ou une FFI vers du code non
      intrinsèque.
La portabilité entre implémentations (norme ISO ou non) n'entre plus dans la note.

Les cellules ci-dessous sont celles que la règle v2 reclasse. Toutes les autres gardent leur note v1. La liste a
été établie le 29 octobre, avant la remesure de K5 et avant le calcul de l'analyse v2, en relisant les 166
cellules notées 0,5 en v1 (le choix reste un jugement de l'auteur).
En plus, la capacité C3 (vectorisation automatique mesurée) sort du pilier C en v2 : elle est déjà mesurée par
E (K4) et par D1 (K4 et K9 naturels), un double compte relevé par l'audit (section 3.4).
"""

V2_OVERRIDES = {
    # C (clang 23 + glibc)
    ("c", "C1"): (1, "vector_size : extension documentée de clang et gcc, stable"),
    ("c", "C4"): (1, "#pragma clang fp reassociate(on) : contrôle local, documenté"),
    ("c", "C5"): (1, "OpenMP livré avec clang et gcc (-fopenmp), exécuté par la sonde"),
    ("c", "D4"): (1, "sched_setaffinity de la glibc (bibliothèque système de la plateforme)"),
    ("c", "D5"): (1, "atomic_thread_fence (C11) et _mm_pause (<immintrin.h> livré)"),
    ("c", "E2"): (1, "__asm__ : extension documentée de clang et gcc"),
    ("c", "E3"): (1, "__builtin_expect : builtin documenté"),
    ("c", "E4"): (1, "__builtin_prefetch, _mm_prefetch"),
    ("c", "F4"): (1, "mmap (POSIX, glibc)"),
    # C++ (g++ 16 + libstdc++ + glibc)
    ("cpp", "C5"): (1, "OpenMP livré avec g++ (-fopenmp) ; par_unseq reste série sans TBB"),
    ("cpp", "D4"): (1, "sched_setaffinity de la glibc"),
    ("cpp", "D5"): (1, "atomic_thread_fence et _mm_pause (<immintrin.h> livré)"),
    ("cpp", "E4"): (1, "__builtin_prefetch : builtin documenté"),
    ("cpp", "E5"): (1, "__restrict__ : extension documentée de g++"),
    ("cpp", "F4"): (1, "mmap (POSIX, glibc) + std::start_lifetime_as"),
    # Zig
    ("zig", "D4"): (1, "std.os.linux.sched_setaffinity dans la bibliothèque standard"),
    ("zig", "F4"): (1, "std.Io.File.MemoryMap (portable) et std.posix.mmap dans la bibliothèque standard"),
    # Odin
    ("odin", "D4"): (1, "core:sys/linux livré avec le compilateur"),
    ("odin", "F4"): (1, "core:sys/linux et core:mem/virtual livrés"),
    # C3
    ("c3", "F4"): (1, "liaison std::os::posix livrée"),
    # D (LDC, compilateur de référence de l'étude)
    ("d", "C2"): (1, "ldc.gccbuiltins_x86 livré avec LDC"),
    ("d", "C4"): (1, "@fastmath (ldc.attributes), par fonction"),
    ("d", "D4"): (1, "core.sys.linux.sched_setaffinity livré"),
    ("d", "E3"): (1, "llvm_expect (ldc.intrinsics)"),
    ("d", "E4"): (1, "llvm_prefetch (ldc.intrinsics)"),
    ("d", "E5"): (1, "@restrict (ldc.attributes)"),
    # Nim (backend clang)
    ("nim", "C2"): (1, "importc des intrinsèques de <immintrin.h> du compilateur C de la chaîne"),
    ("nim", "C5"): (0.5, "itérateur || du module system (OpenMP) : une réduction ne compile pas en -d:release ; erratum du 30/10, juge à l'aveugle"),
    ("nim", "E4"): (1, "importc de __builtin_prefetch"),
    # Ada (GNAT 16)
    ("ada", "C1"): (1, "Machine_Attribute vector_type : types vectoriels GCC, extension documentée de GNAT (corrigé le 30/10)"),
    ("ada", "C2"): (1, "builtins GCC importés par Convention Intrinsic + Machine_Attribute vector_type (documentés par GNAT)"),
    ("ada", "D2"): (1, "builtins __atomic_* à ordre explicite importables comme intrinsèques"),
    ("ada", "D5"): (1, "__atomic_thread_fence et pause importés comme intrinsèques"),
    ("ada", "E3"): (1, "__builtin_expect importé comme intrinsèque"),
    ("ada", "E4"): (1, "__builtin_prefetch importé comme intrinsèque"),
    # Fortran (gfortran 16, OpenMP livré)
    ("fortran", "C4"): (1, "!$omp simd reduction : réassociation locale, OpenMP livré avec gfortran"),
    ("fortran", "A4"): (1, "!$omp allocate align / !$omp allocators : alignement par OpenMP livré avec gfortran (sonde a4 ; corrigé le 30/10)"),
    ("fortran", "D1"): (1, "threads OpenMP livrés avec gfortran"),
    ("fortran", "D2"): (1, "!$omp atomic avec clauses d'ordre mémoire"),
    ("fortran", "D4"): (1, "proc_bind / OMP_PLACES (OpenMP)"),
    # Go
    ("go", "D4"): (1, "syscall.RawSyscall(SYS_SCHED_SETAFFINITY) + runtime.LockOSThread (paquets livrés)"),
    ("go", "F4"): (1, "syscall.Mmap + unsafe.Slice (paquets livrés)"),
    # Julia
    ("julia", "C2"): (1, "Base.llvmcall vers les intrinsèques LLVM (documenté)"),
    ("julia", "E2"): (1, "Base.llvmcall avec asm en ligne dans l'IR"),
    ("julia", "E4"): (1, "Base.llvmcall de llvm.prefetch"),
    # Mojo
    ("mojo", "C2"): (1, "llvm_intrinsic de la bibliothèque standard"),
    # Python
    ("python", "D4"): (1, "os.sched_setaffinity de la bibliothèque standard"),
    # erratum du 30 octobre (notation à l'aveugle) : fait omis
    ("c", "D3"): (1, "sysconf(_SC_LEVEL1_DCACHE_LINESIZE) de la glibc ; __GCC_DESTRUCTIVE_SIZE prédéfini par clang et gcc"),
}

# C3 (vectorisation automatique mesurée) sort du pilier C en v2 : double compte avec E et D1.
V2_DROP = {"C3"}


def cell_v1(matrix, lang, cap, c3, M):
    """Note v1 d'une cellule (la capacité C3 lue dans les mesures)."""
    v = matrix[lang][cap]
    return c3.get(lang, 0) if v == M else v[0]


def cell_v2(matrix, lang, cap, c3, M):
    if (lang, cap) in V2_OVERRIDES:
        return V2_OVERRIDES[(lang, cap)][0]
    return cell_v1(matrix, lang, cap, c3, M)
