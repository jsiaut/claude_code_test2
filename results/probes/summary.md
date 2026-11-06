| Langage | Capacité | Sonde | Matrice | | Preuve exécutée |
|---|---|---|---|---|---|
| ada | A2 | 1 | 1 |  | S.C'Position = 8 |
| ada | A3 | 1 | 1 |  | clause de représentation au bit près : BF'Size = 8 |
| ada | A5 | 1 | 1 |  | Unchecked_Conversion 0x 1065353216 ; Unchecked_Union UU'Size = 32 |
| ada | D4 | 1 | 1 |  | aspect CPU => 1 sur une tâche ; CPU disponibles = 4 |
| ada | C1 | 0.5 | 0.5 |  | Machine_Attribute vector_type (extension GNAT) : Add =  3.00000E+00 |
| ada | E5 | 1 | 1 |  | RM 6.2(12) exploitée par GNAT sur paramètres de type contraint : Y (1) =  7.00000E+00 |
| ada | B4 | 0.5 | 0.5 |  | retour non contraint de 4 Mo par la pile secondaire (tas au-delà du morceau statique) :  5.00000000000000E+05 |
| bqn | A1 | 0.5 | 0.5 |  | matrice 1000×16 : f64arr d'un seul tenant (rangées homogènes en ligne) ; liste d'espaces de noms : harr (référ |
| bqn | A2 | 0 | 0 |  | ni ordre ni taille de champs : un espace de noms n'a pas de disposition (les types de structure de •FFI ne ser |
| bqn | A3 | 0.5 | 0.5 |  | booléens rangés à 1 bit (bitarr) ; ⟨1,'u'⟩‿⟨8,'i'⟩ •bit._cast 8 bits → ⟨ -115 ⟩ ; pas de champs de bits dans u |
| bqn | A4 | 0 | 0 |  | aucun contrôle de l'alignement |
| bqn | A5 | 0.5 | 0.5 |  | •bit._cast : 1.0 en f64 → deux i32 ⟨ 0 1072693248 ⟩ (tableaux seulement ; ni union ni f32) |
| bqn | A6 | 0.5 | 0.5 |  | ⍉ fait passer la matrice 1000×16 (une particule par rangée) en 16×1000 (un champ par rangée, f64arr) : AoS et  |
| bqn | A7 | 0.5 | 0.5 |  | tableau de rang 3 (2×16×4, f64arr) : sous-tableaux fixes en ligne, homogènes seulement |
| bqn | A8 | 0.5 | 0.5 |  | stockage étroit choisi par l'implémentation : 1‿2‿3 i8arr, 300‿1 i16arr, 70000‿1 i32arr, 0.5‿1 f64arr ; •bit._ |
| bqn | B1 | 0.5 | 0.5 |  | comptage de références (•internal.Refc ↕1000 : 1) ; ramasse-miettes traçant automatique, désactivable seulemen |
| bqn | B2 | 0 | 0 |  | aucun allocateur à choisir ni arène |
| bqn | B3 | 0 | 0 |  | nombres jamais boxés (100 000 additions scalaires : tas vivant 128 octets de plus) ; tout tableau est sur le t |
| bqn | B4 | 0 | 0 |  | chaque primitive alloue son résultat (sauf mise à jour en place d'un tableau non partagé) |
| bqn | B5 | 0.5 | 0.5 |  | pointeurs par •FFI seulement : malloc, Write 123456, Read 123456 (objets pointeurs Read/Write/Add/Cast) |
| bqn | C1 | 0 | 0 |  | aucun type vectoriel : les primitives travaillent sur des tableaux entiers |
| bqn | C2 | 0 | 0 |  | aucune intrinsèque |
| bqn | C4 | 0.5 | 0.5 |  | +´ ordonnée 14.392726722865772 ; •math.Sum (somme vectorielle réassociée) 14.392726722865621 ; écart 1.5099033 |
| bqn | C5 | 0 | 0 |  | ni threads ni boucle parallèle |
| bqn | D1 | 0 | 0 |  | pas de threads (la bibliothèque système n'en a pas ; CBQN n'est pas réentrant) |
| bqn | D2 | 0 | 0 |  | aucun atomique |
| bqn | D3 | 0 | 0 |  | aucune aide de ligne de cache |
| bqn | D4 | 0 | 0 |  | pas d'affinité (sched_setaffinity seulement par •FFI vers la libc) |
| bqn | D5 | 0 | 0 |  | ni barrière ni pause |
| bqn | E1 | 0.5 | 0.5 |  | interprète de bytecode avec un JIT x86-64 actif par défaut (src/vm/vm.h : JIT_START 2, une fonction compilée a |
| bqn | E2 | 0 | 0 |  | aucun |
| bqn | E3 | 0 | 0 |  | aucun |
| bqn | E4 | 0 | 0 |  | aucun |
| bqn | E5 | 0 | 0 |  | aucune annotation (valeurs immuables) |
| bqn | E6 | 0 | 0 |  | indices toujours vérifiés (5 ⊑ ↕3 : « 𝕨⊑𝕩: indexing out-of-bounds (𝕨≡5, 3≡≠𝕩) ») ; aucun moyen de les désactiv |
| bqn | E7 | 0 | 0 |  | ni calcul à la compilation ni génériques |
| bqn | F1 | 1 | 1 |  | tableaux multidimensionnels natifs, contigus en ordre des rangées (3×4×5 : i8arr, (⟨1,2,3⟩⊑r) = 33) |
| bqn | F2 | 0 | 0 |  | aucun |
| bqn | F3 | 0.5 | 0.5 |  | entiers exacts jusqu'à 2⋆53 (f64) ; enveloppement par modulo : (2⋆32)|¯1 = 4294967295, par •bit._cast 300 → i8 |
| bqn | F4 | 1 | 1 |  | •file.MapBytes projette 64 Mio (c8slice, tas vivant + 128 o) ; •bit._cast en i32 sans copie (i32slice, tas + 6 |
| c | A1 | 1 | 1 |  | tableau de struct contigu sizeof(arr)=64 (4x16) |
| c | A2 | 1 | 1 |  | offsetof(S,b)=4 offsetof(S,c)=8 |
| c | A3 | 1 | 0.5 | DIVERGENCE | bitfields sizeof(BF)=4 ; packed (extension) sizeof(P)=5 |
| c | A4 | 1 | 1 |  | alignas(64) alignof(L)=64, aligned_alloc % 64=0 |
| c | A5 | 1 | 1 |  | union f32->u32 = 0x3f800000 |
| c | A6 | 0 | 0 |  | pas de SoA dans le langage ni la bibliothèque standard |
| c | A7 | 1 | 1 |  | sizeof(In)=68 (float[16] en ligne) |
| c | A8 | 1 | 1 |  | uint8_t/int16_t/float stockés à leur taille : 1 2 4 |
| c | B1 | 1 | 1 |  | pas de ramasse-miettes |
| c | B2 | 0.5 | 0.5 |  | malloc/free seulement ; arènes à écrire soi-même (pas d'interface d'allocateur standard) |
| c | B3 | 1 | 1 |  | tableau sur la pile (1024 o) et VLA |
| c | B4 | 1 | 1 |  | aucune allocation implicite du langage |
| c | B5 | 1 | 1 |  | pointeurs bruts, mmap anonyme 0x7f3a61090000 |
| c | C1 | 0.5 | 0.5 |  | types vectoriels portables par extension (vector_size) : 3 ; pas dans le standard C |
| c | C2 | 1 | 0.5 | DIVERGENCE | intrinsèques AVX-512 <immintrin.h> : 32 |
| c | C3 | 1 | mesuré |  | auto-vectorisation clang/gcc -O3 (vérifiée sur K4/K9 natural) |
| c | C4 | 0.5 | 0.5 |  | réassociation : options -ffast-math/-fassociative-math, #pragma clang fp reassociate (extension) ; pas de cont |
| c | C5 | 0.5 | 0.5 |  | OpenMP, livré avec clang et gcc mais hors norme ISO C : parallel for simd reduction = 499500 |
| c | D1 | 1 | 1 |  | threads <threads.h>/pthreads |
| c | D2 | 1 | 1 |  | <stdatomic.h> memory_order_relaxed/acquire/release/seq_cst : 1 |
| c | D3 | 0.5 | 0.5 |  | __GCC_DESTRUCTIVE_SIZE=64 (macro prédéfinie par clang et gcc), sysconf(_SC_LEVEL1_DCACHE_LINESIZE)=64 (glibc)  |
| c | D4 | 0.5 | 0.5 |  | affinité via POSIX/Linux sched_setaffinity (pas dans le standard C) rc=0 |
| c | D5 | 0.5 | 0.5 |  | atomic_thread_fence standard ; pause via intrinsèque _mm_pause |
| c | E1 | 1 | 1 |  | compilation native, objdump/-S |
| c | E2 | 0.5 | 0.5 |  | assembleur en ligne par extension gcc/clang (__asm__) : 2 |
| c | E3 | 0.5 | 0.5 |  | __builtin_expect (extension) ; [[likely]] n'existe qu'en C++ |
| c | E4 | 0.5 | 0.5 |  | __builtin_prefetch (extension) ou _mm_prefetch (intrinsèque) |
| c | E5 | 1 | 1 |  | restrict (C99) |
| c | E6 | 1 | 1 |  | pas de vérification de bornes (rien à désactiver) |
| c | E7 | 0.5 | 0.5 |  | constexpr C23 et _Generic, mais ni génériques monomorphisés ni calcul arbitraire à la compilation : 64 |
| c | F1 | 1 | 1 |  | tableaux 2D C99 contigus en ligne (VLA/pointeur vers tableau) : 3 |
| c | F2 | 0 | 0 |  | pas de construction de localité/distribution (libnuma hors standard) |
| c | F3 | 1 | 1 |  | uint32_t modulaire (w=0) ; débordement signé indéfini |
| c | F4 | 0.5 | 0.5 |  | mmap POSIX (pas dans le standard C) puis réinterprétation par cast : 0.439005 |
| c3 | A2 | 1 | 1 |  | $reflect(Sx.c).offset=8 |
| c3 | A3 | 1 | 1 |  | @packed P.sizeof=5 ; bitstruct BF.sizeof=2 |
| c3 | A5 | 1 | 1 |  | union 0x3f800000 bitcast 0x3f800000 |
| c3 | E3 | 1 | 1 |  | @likely : 2 |
| chapel | A2 | 1 | 1 |  | c_offsetof(S, "c")=8 |
| chapel | A4 | 0.5 | 0.5 |  | allocate(alignment=64) -> adresse mod 64 = 0 |
| chapel | A5 | 0.5 | 0.5 |  | (1.0: real(32)).transmute(uint(32)) = 1065353216 |
| chapel | D5 | 0.5 | 0.5 |  | atomicFence |
| chapel | B2 | 0.5 | 0.5 |  | Allocators (instable) : bumpPtrMemPool + newWithAllocator, v = 7 |
| chapel | C2 | 0.5 | 0.5 |  | _mm512_fmadd_ps importé de immintrin.h : somme = 96.0 (macros à immédiat et builtins : refusés) |
| chapel | B3 | 0.5 | 0.5 |  | c_array local (pile) : 3.0 ; tableaux Chapel sur le tas |
| chapel | C4 | 0.5 | 0.5 |  | @llvm.metadata(("llvm.loop.vectorize.enable", true)) par boucle (instable) |
| chapel | E5 | 0.5 | 0.5 |  | foreach (instable) : llvm.loop.parallel_accesses ; noalias automatique, a[0] = 2.0 |
| cpp | A1 | 1 | 1 |  | std::vector<S> de valeurs contiguës : &v[1]-&v[0]=16 o |
| cpp | A2 | 1 | 1 |  | offsetof(S,c)=8 (types à disposition standard) |
| cpp | A3 | 1 | 0.5 | DIVERGENCE | champs de bits sizeof(BF)=4 ; packed par attribut gnu sizeof(P)=5 |
| cpp | A4 | 1 | 1 |  | alignas(64) + new aligné C++17 : 0 |
| cpp | A5 | 1 | 1 |  | std::bit_cast<uint32_t>(1.0f)=0x3f800000 ; unions |
| cpp | A6 | 0 | 0 |  | pas de SoA standard (la réflexion C++26 permettrait de l'écrire) |
| cpp | A7 | 1 | 1 |  | std::array en ligne sizeof(In)=68 |
| cpp | A8 | 1 | 1 |  | types étroits |
| cpp | B1 | 1 | 1 |  | pas de GC |
| cpp | B2 | 1 | 1 |  | std::pmr (monotonic_buffer_resource, pools) + concept Allocator |
| cpp | B3 | 1 | 1 |  | objets et std::array sur la pile |
| cpp | B4 | 0.5 | 0.5 |  | pas d'allocation cachée par le langage, mais std::function, exceptions et coroutines peuvent allouer |
| cpp | B5 | 1 | 1 |  | pointeurs bruts |
| cpp | C1 | 1 | 0.5 | DIVERGENCE | std::simd (C++26) : reduce=32 |
| cpp | C2 | 1 | 0.5 | DIVERGENCE | intrinsèques <immintrin.h> : 16 |
| cpp | C3 | 1 | mesuré |  | auto-vectorisation -O3 |
| cpp | C4 | 1 | 1 |  | réassociation permise dans la norme : std::reduce/transform_reduce (ordre non spécifié) et std::simd::reduce |
| cpp | C5 | 0.5 | 0.5 |  | std::execution::par_unseq compile, mais libstdc++ l'exécute en série sans TBB, bibliothèque tierce (backend SE |
| cpp | D1 | 1 | 1 |  | std::thread/jthread |
| cpp | D2 | 1 | 1 |  | std::memory_order relaxed/acquire/release/seq_cst |
| cpp | D3 | 1 | 1 |  | std::hardware_destructive_interference_size=64 |
| cpp | D4 | 0.5 | 0.5 |  | pas d'affinité dans la bibliothèque standard ; sched_setaffinity de la libc, livrée avec la chaîne |
| cpp | D5 | 0.5 | 0.5 |  | std::atomic_thread_fence, std::barrier ; pause seulement par intrinsèque |
| cpp | E1 | 1 | 1 |  | natif |
| cpp | E2 | 1 | 1 |  | déclaration asm, dans la norme C++ ([dcl.asm], sens défini par l'implémentation) : 2 |
| cpp | E3 | 1 | 1 |  | [[likely]]/[[unlikely]] (C++20) |
| cpp | E4 | 0.5 | 0.5 |  | __builtin_prefetch (extension) |
| cpp | E5 | 0.5 | 0.5 |  | __restrict__ (extension, pas dans la norme C++) |
| cpp | E6 | 1 | 1 |  | pas de vérification de bornes par défaut ; .at() les ajoute |
| cpp | E7 | 1 | 1 |  | templates monomorphisés + consteval : 49 42 |
| cpp | F1 | 1 | 1 |  | std::mdspan (C++23), dispositions layout_right/left/stride : 3 |
| cpp | F2 | 0 | 0 |  | pas de localité/distribution |
| cpp | F3 | 1 | 1 |  | entiers non signés modulaires (w=0) |
| cpp | F4 | 0.5 | 0.5 |  | mmap POSIX + std::start_lifetime_as (C++23) : 0.439005 |
| csharp | A2 | 1 | 1 |  | Marshal.OffsetOf(S, C)=8 |
| csharp | A5 | 1 | 1 |  | FieldOffset recouvrants 0x3f800000 |
| csharp | A7 | 1 | 1 |  | [InlineArray(16)] sizeof(In)=68 |
| csharp | F4 | 1 | 1 |  | MemoryMappedFile + pointeur : 0.4390046 |
| d | A2 | 1 | 1 |  | S.c.offsetof=8 |
| d | A3 | 1 | 1 |  | align(1) P.sizeof=5 ; bitfields BF.sizeof=1 |
| d | A4 | 1 | 1 |  | align(64) L.alignof=64 |
| d | A5 | 1 | 1 |  | union 0x3f800000 |
| d | F4 | 1 | 1 |  | std.mmfile + cast : 0.439005 |
| d | D5 | 1 | 1 |  | core.atomic.pause + atomicFence |
| d | E3 | 1 | 1 |  | core.builtins.likely/unlikely (druntime) : somme 499500 |
| d | E4 | 1 | 1 |  | core.simd.prefetch!(false, 3) (druntime) : prefetcht0, somme 499500 |
| d | A3 | 1 | 1 |  | champs de bits natifs sans -preview : NativeBF.sizeof=4 a=5 b=17 |
| fortran | A5 | 1 | 1 |  | TRANSFER(1.0) = 0x3F800000 |
| fortran | B5 | 1 | 1 |  | c_loc + c_f_pointer :  2.0 |
| fortran | C5 | 1 | 1 |  | do concurrent :   72.0 |
| fortran | A3 | 0.5 | 0.5 |  | -fpack-derived (option globale) : storage_size(t) = 6 octets |
| fortran | A4 | 0.5 | 0.5 |  | directives OpenMP : allouable mod 128 = 0 ; locale mod 256 = 0 |
| fortran | B2 | 0.5 | 0.5 |  | arène à la main (tableau de nœuds réutilisé), comme en C : 42 |
| fortran | F2 | 0.5 | 0.5 |  | cotableaux sur un nœud (libcaf_shmem) : images 4, somme 10 |
| fpc | A1 | 1 | 1 |  | array of record : SizeOf(TParticle) = 64 o, écart entre éléments 64 o (valeurs en ligne) |
| fpc | A2 | 1 | 1 |  | record : décalages a=0 b=8 c=16 (ordre déclaré, alignement naturel) ; {$PACKRECORDS C} : taille 12 o, b à 4 (d |
| fpc | A3 | 1 | 1 |  | packed record {Byte; LongWord} : 5 o ; bitpacked record {0..7; 0..31} : 1 o, champs relus 5 et 17 |
| fpc | A4 | 0.5 | 0.5 |  | GetMem + Align(p, 64) : adresse mod 64 = 0 (à la main) ; {$CODEALIGN VARMIN=64} pour les variables globales ;  |
| fpc | A5 | 1 | 1 |  | record à variantes sans champ d'étiquette (union brute) : Single 1.0 = $3F800000, octets 0 0 128 63 ; absolute |
| fpc | A6 | 0 | 0 |  | aucun type SoA |
| fpc | A7 | 1 | 1 |  | record avec array[0..15] of Single : 64 o en ligne |
| fpc | A8 | 1 | 1 |  | Byte 1 SmallInt 2 Word 2 Single 4 ; intervalles bitpacked (A3) ; pas de flottant 16 bits |
| fpc | B1 | 1 | 1 |  | pas de ramasse-miettes : comptage de références des chaînes, tableaux dynamiques et interfaces (StringRefCount |
| fpc | B2 | 0.5 | 0.5 |  | SetMemoryManager (gestionnaire global remplaçable : 1 appel compté pour New) ; NewInstance/FreeInstance redéfi |
| fpc | B3 | 1 | 1 |  | records et tableaux statiques locaux sur la pile (distance à une variable locale : 1312 o ; au tas : TRUE) |
| fpc | B4 | 0.5 | 0.5 |  | allocations implicites : boucle sur un tableau 0, énumération d'un TDictionary 1 (objet énumérateur), concatén |
| fpc | B5 | 1 | 1 |  | Pointer, pointeurs typés, arithmétique ({$pointermath}), GetMem/FreeMem (bench) |
| fpc | C1 | 0.5 | 0.5 |  | -Sv : opérations sur array[0..3] of Single (SSE 128 bits) : 2 6 12 20 ; expérimental : 8 Single = erreur inter |
| fpc | C2 | 0.5 | 0.5 |  | assembleur en ligne jusqu'à AVX2 et FMA (E2), sans intrinsèques SSE/AVX, comme Zig : seulement des intrinsèque |
| fpc | C5 | 0 | 0 |  | aucune boucle parallèle ni réserve de tâches dans la RTL et les paquets livrés (mtprocs est un paquet de Lazar |
| fpc | D1 | 1 | 1 |  | BeginThread (unité cthreads) et TThread : 4 fils, 4000 incréments |
| fpc | D2 | 0.5 | 0.5 |  | InterLockedIncrement64 / CompareExchange64 / ExchangeAdd64 (RMW séquentiellement cohérents, appels de la RTL)  |
| fpc | D3 | 0 | 0 |  | aucune constante, requête ni type de bourrage de ligne de cache dans la RTL (l'unité cpu ne détecte que des je |
| fpc | D4 | 0.5 | 0.5 |  | Do_SysCall(syscall_nr_sched_setaffinity) de l'unité Syscall livrée : retour 0, masque relu 2, processeur coura |
| fpc | D5 | 0.5 | 0.5 |  | ReadBarrier / WriteBarrier / ReadWriteBarrier (lfence, sfence, mfence dans des procédures de la RTL) ; ThreadS |
| fpc | E1 | 1 | 1 |  | code natif, -al garde l'assembleur produit |
| fpc | E2 | 1 | 1 |  | blocs asm (syntaxe Intel ou AT&T, procédures assembler) : 42 ; AVX2 accepté, AVX-512 inconnu de l'assembleur d |
| fpc | E3 | 0 | 0 |  | pas d'indication de branchement (Likely/Unlikely inconnus, run.sh) |
| fpc | E4 | 0.5 | 0.5 |  | Prefetch(x) du System (intrinsèque : prefetchnta seulement, sans localité ni écriture, run.sh) ; erratum du 6/ |
| fpc | E5 | 0 | 0 |  | ni restrict ni garantie de non-aliasing |
| fpc | E6 | 1 | 1 |  | {$R+} / {$R-} locaux : indice 5 hors bornes détecté sous {$R+} : TRUE ; sans vérification ailleurs (défaut) :  |
| fpc | E7 | 0.5 | 0.5 |  | génériques spécialisés à la compilation (specialize) : 7 2.5 ; expressions constantes (1219), pas d'évaluation |
| fpc | F1 | 0.5 | 0.5 |  | array[0..3, 0..7] of Double : 256 o contigus (écart entre lignes 64 o), bornes fixées à la compilation ; array |
| fpc | F2 | 0 | 0 |  | aucun |
| fpc | F3 | 1 | 1 |  | Byte...QWord et ShortInt...Int64, arithmétique modulaire sans {$Q+} (défaut) : 0 -2147483648 |
| fpc | F4 | 0.5 | 0.5 |  | Fpmmap (unité BaseUnix livrée, appel système propre à Unix, comme syscall.Mmap de Go ; 1 en règle v2) + pointe |
| fpc | C4 | 0 | 0 |  | -OoFASTMATH (aussi {$OPTIMIZATION FASTMATH}) sur une réduction : 0 FMA sans l'option, 1 avec (contraction a*b+ |
| go | A2 | 1 | 1 |  | unsafe.Offsetof(S.C)=8 |
| go | A5 | 0.5 | 0.5 |  | math.Float32bits(1)=0x3f800000 |
| go | F4 | 0.5 | 0.5 |  | syscall.Mmap + unsafe.Slice : 0.4390046 <nil> |
| go | D4 | 0.5 | 0.5 |  | syscall brut sched_setaffinity errno=0 |
| haskell | A5 | 0.5 | 0.5 |  | castFloatToWord32 1.0 = 0x3f800000 |
| haskell | A4 | 0.5 | 0.5 |  | allocaBytesAligned 64 -> adresse mod 64 = 0 |
| haskell | E4 | 1 | 1 |  | prefetchAddr3# (GHC.Exts) |
| java | D2 | 1 | 1 |  | VarHandle setRelease/getAcquire/setOpaque : 1 ; D5 fullFence + onSpinWait |
| java | F4 | 1 | 1 |  | FileChannel.map -> MemorySegment : 0.4390046 |
| java | A1 | 0.5 | 0.5 |  | FFM sequenceLayout(1024, structLayout(...)) : 65536 octets ; A7 sequenceLayout dans structLayout |
| java | A3 | 0.5 | 0.5 |  | FFM disposition non alignée : 5 octets |
| java | A4 | 0.5 | 0.5 |  | Arena.allocate(256, 64) adresse mod 64 = 0 |
| js | D5 | 0.5 | 0.5 |  | Atomics.pause existe (function) ; pas de barrière explicite |
| js | A5 | 0.5 | 0.5 |  | vues typées sur un même ArrayBuffer : 0x3f800000 |
| julia | A2 | 1 | 1 |  | fieldoffset(S, 3)=8 |
| julia | A5 | 1 | 1 |  | reinterpret(UInt32, 1f0)=0x3f800000 |
| julia | F4 | 1 | 1 |  | Mmap.mmap -> Vector{Float32} : 0.4390046 |
| julia | D5 | 0.5 | 0.5 |  | Threads.atomic_fence ; pas de pause publique |
| julia | B2 | 0.5 | 0.5 |  | Libc.malloc + unsafe_wrap (publics) : arène à la main, somme = 500500 |
| julia | D3 | 0.5 | 0.5 |  | Threads.PaddedSpinLock public = true, sizeof = 120 (propre aux verrous) |
| julia | D5 | 0.5 | 0.5 |  | Threads.atomic_fence ; pause par ccall llvmcall : true (règle v2 : 1) |
| julia | E3 | 0 | 0 |  | llvm.expect par llvmcall : poids de branchement dans l'IR optimisé = false |
| lua | A5 | 0.5 | 0.5 |  | string.pack/unpack : 0x3f800000 |
| lua | F3 | 0.5 | 0.5 |  | entiers 64 bits enveloppants : true ; math.ult true |
| mojo | D2 | 1 | 1 |  | Atomic.fetch_add[ordering=RELAXED] |
| mojo | A5 | 1 | 1 |  | bitcast[DType.uint32] = 1065353216 ; unions : probe_errata.mojo |
| mojo | E3 | 1 | 1 |  | likely |
| mojo | A4 | 1 | 1 |  | @align(64) : align_of = 64 , somme des adresses mod 64 (64 sur la pile, 50 sur le tas) = 0 |
| mojo | A5 | 1 | 1 |  | UnsafeUnion[Float32, UInt32] : size_of = 4 , bits de 1.0f = 1065353216 |
| mojo | C4 | 0.5 | 0.5 |  | fma[FastMathFlag.REASSOC] = 7.0 (seule opération qui prend le drapeau) |
| mojo | D5 | 1 | 1 |  | fence() et SpinWaiter.wait() exécutés (pause dans le runtime à partir du 4e appel) |
| mojo | E5 | 1 | 1 |  | Pointer.unsafe_as_noalias() : 7 |
| nim | A2 | 1 | 1 |  | offsetOf(S, c)=8 |
| nim | A3 | 1 | 1 |  | packed sizeof(P)=5 ; bitsize sizeof(BF)=4 |
| nim | A4 | 1 | 1 |  | align(64) alignof(L)=64 |
| nim | A5 | 1 | 1 |  | union 0x3F800000 |
| nim | F4 | 1 | 1 |  | std/memfiles : 0.4390046 |
| nim | D5 | 1 | 1 |  | cpuRelax + fence |
| nim | E3 | 1 | 1 |  | likely/unlikely |
| ocaml | D3 | 1 | 1 |  | Atomic.make_contended ; D5 Domain.cpu_relax : 1 |
| ocaml | A5 | 0.5 | 0.5 |  | Int32.bits_of_float 1.0 = 0x3f800000 |
| ocaml | F1 | 1 | 1 |  | Bigarray.Array2 c_layout : 3 |
| ocaml | F4 | 1 | 1 |  | Unix.map_file -> Bigarray float32 : 0.439005 |
| odin | A2 | 1 | 1 |  | offset_of(S, c)=8 |
| odin | A3 | 1 | 1 |  | #packed size_of(P)=5 ; bit_field size_of(BF)=2 |
| odin | A5 | 1 | 1 |  | #raw_union 0x3f800000 transmute 0x3f800000 |
| odin | E3 | 1 | 1 |  | intrinsics.expect : 2 |
| odin | E4 | 1 | 1 |  | prefetch_read_data ; D5 cpu_relax |
| python | A2 | 0.5 | 0.5 |  | ctypes S.c.offset=8 |
| python | A3 | 0.5 | 0.5 |  | ctypes _pack_=1 et champ de 3 bits : sizeof(P)=9 |
| python | F4 | 1 | 1 |  | mmap + memoryview.cast('f') sans copie : 0.4390046000480652 |
| python | D4 | 0.5 | 0.5 |  | os.sched_setaffinity -> {0} |
| rust | A2 | 1 | 1 |  | offset_of!(S, c)=8 (repr(C)) |
| rust | A3 | 0.5 | 0.5 |  | repr(packed) size_of::<P>()=5 |
| rust | A4 | 1 | 1 |  | repr(align(64)) align_of::<L>()=64 |
| rust | A5 | 1 | 1 |  | union 0x3f800000 to_bits 0x3f800000 |
| rust | C4 | 1 | 1 |  | f32::algebraic_add stable : 64 |
| rust | E2 | 1 | 1 |  | asm! stable : 2 |
| rust | E3 | 1 | 1 |  | std::hint::cold_path stable |
| rust | E4 | 1 | 1 |  | _mm_prefetch (std::arch) |
| swift | A1 | 1 | 1 |  | [P] contigu : stride 64 o, écart entre éléments 64 o |
| swift | A2 | 1 | 1 |  | MemoryLayout.offset(of:) a=0 c=8 b=16 : ordre déclaré gardé (docs/ABI/TypeLayout.rst), sans attribut de dispos |
| swift | A3 | 0 | 0 |  | {UInt8, UInt32} : size 8 o (bourrage imposé) ; ni packed ni champs de bits hors struct C importée |
| swift | A4 | 0.5 | 0.5 |  | UnsafeMutableRawPointer.allocate(alignment: 64) -> adresse % 64 = 0 ; pas d'alignement de type au-delà de 16 |
| swift | A5 | 0.5 | 0.5 |  | Float(bitPattern:) 0x3f800000, lecture des octets 0x3f800000, unsafeBitCast entre types de même taille ; enum  |
| swift | A6 | 0 | 0 |  | aucun type SoA en bibliothèque standard |
| swift | A7 | 1 | 1 |  | InlineArray<16, Float> dans une struct : stride 64 o |
| swift | A8 | 1 | 1 |  | UInt8 1 Int16 2 Float16 2 Float 4 |
| swift | B1 | 1 | 1 |  | ARC : isKnownUniquelyReferenced true ; pas de GC traçant |
| swift | B2 | 0.5 | 0.5 |  | allocate/deallocate de pointeurs bruts ; pas d'interface d'allocateur (arènes à la main, bench K8 tuned) |
| swift | B3 | 1 | 1 |  | withUnsafeTemporaryAllocation : tampon à 944 o d'une variable locale (pile) ; structs et InlineArray en ligne |
| swift | B4 | 0.5 | 0.5 |  | [any Shape] (conteneur de 40 o, tampon en ligne de 24 o) d'une struct de 64 o : boîte 0x55ef1d3156c0 sur le ta |
| swift | B5 | 1 | 1 |  | UnsafeMutableRawPointer, UnsafePointer (bench) |
| swift | C1 | 1 | 1 |  | SIMD16<Float>.addProduct (FMA) : 7.0 |
| swift | C4 | 0 | 0 |  | aucun contrôle de la réassociation (ni fast-math ni API relâchée en bibliothèque standard ; Relaxed est dans s |
| swift | C5 | 1 | 1 |  | DispatchQueue.concurrentPerform : 64 itérations sur 3 threads |
| swift | D1 | 1 | 1 |  | Foundation.Thread et tâches (withTaskGroup, somme 6) |
| swift | D2 | 1 | 1 |  | Atomic : .relaxed/.acquiring/.releasing/.sequentiallyConsistent -> 5 |
| swift | D3 | 0.5 | 0.5 |  | sysconf(_SC_LEVEL1_DCACHE_LINESIZE) = 64 par le module Glibc livré : requête à l'exécution, ni constante ni ty |
| swift | D5 | 0.5 | 0.5 |  | atomicMemoryFence ; pause seulement par @_silgen_name, attribut souligné (_mm_pause importée : symbole introuv |
| swift | E1 | 1 | 1 |  | natif, -emit-assembly / -emit-ir |
| swift | E2 | 0 | 0 |  | pas d'assembleur en ligne |
| swift | E6 | 1 | 1 |  | UnsafeBufferPointer sans vérification en -O (bench), -Ounchecked global |
| swift | E7 | 0.5 | 0.5 |  | génériques spécialisés par l'optimiseur (non garanti, 9) ; pas d'évaluation à la compilation (macros : paquet  |
| swift | F1 | 0.5 | 0.5 |  | InlineArray<4, InlineArray<8, Double>> : 256 o contigus ; tailles fixées à la compilation seulement ; [[Double |
| swift | F2 | 0 | 0 |  | aucun |
| swift | F3 | 1 | 1 |  | UInt8...Int64, &+ &- &* : 4 -2147483648 |
| swift | F4 | 1 | 1 |  | Data(contentsOf:options: .alwaysMapped) projeté (/proc/self/maps) + withUnsafeBytes/bindMemory : 67108864 o, p |
| swift | C2 | 0.5 | 0.5 |  | import _Builtin_intrinsics.intel (module Clang non documenté) : 1 vaddps pour _mm512_add_ps ; fonctions intégr |
| swift | D4 | 0.5 | 0.5 |  | sched_setaffinity du module Glibc livré avec swiftc -Xcc -D_GNU_SOURCE : fil épinglé sur le CPU 1, sched_getcp |
| swift | E3 | 0.5 | 0.5 |  | _slowPath/_fastPath (publics mais soulignés) : poids de branchement dans l'IR = 1 |
| swift | E4 | 0.5 | 0.5 |  | @_silgen_name("llvm.prefetch.p0"), attribut souligné : 9 prefetchw dans le code produit ; _m_prefetchw importé |
| swift | E5 | 0.5 | 0.5 |  | exclusivité des inout (règle du langage, exploitée par l'optimiseur SIL) ; IR de two(_:_:) sans noalias : 0 ;  |
| zig | A2 | 1 | 1 |  | @offsetOf(S, "c")=8 |
| zig | A3 | 1 | 1 |  | packed struct u3/u5/u8 : @bitSizeOf=16 |
| zig | A4 | 1 | 1 |  | align(64) : @alignOf(L)=64 |
| zig | A5 | 1 | 1 |  | extern union 0x3f800000 @bitCast 0x3f800000 |
| zig | C4 | 1 | 1 |  | @setFloatMode(.optimized) par portée : 2016 |
| zig | E3 | 1 | 1 |  | @branchHint(.likely) : 2 |
| zig | E4 | 1 | 1 |  | @prefetch |
| zig | D3 | 1 | 1 |  | std.atomic.cache_line=128 |
| zig | D5 | 0.5 | 0.5 |  | spinLoopHint ; pas de @fence |
| zig | F4 | 1 | 1 |  | std.Io.File.MemoryMap + bytesAsSlice : 0.4390046, projection dans /proc/self/maps : true |
