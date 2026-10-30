| Langage | Capacité | Sonde | Matrice | | Preuve exécutée |
|---|---|---|---|---|---|
| ada | A2 | 1 | 1 |  | S.C'Position = 8 |
| ada | A3 | 1 | 1 |  | clause de représentation au bit près : BF'Size = 8 |
| ada | A5 | 1 | 1 |  | Unchecked_Conversion 0x 1065353216 ; Unchecked_Union UU'Size = 32 |
| ada | D4 | 1 | 1 |  | aspect CPU => 1 sur une tâche ; CPU disponibles = 4 |
| ada | C1 | 0.5 | 0.5 |  | Machine_Attribute vector_type (extension GNAT) : Add =  3.00000E+00 |
| ada | E5 | 1 | 1 |  | RM 6.2(12) exploitée par GNAT sur paramètres de type contraint : Y (1) =  7.00000E+00 |
| ada | B4 | 0.5 | 0.5 |  | retour non contraint de 4 Mo par la pile secondaire (tas au-delà du morceau statique) :  5.00000000000000E+05 |
| c | A1 | 1 | 1 |  | tableau de struct contigu sizeof(arr)=64 (4x16) |
| c | A2 | 1 | 1 |  | offsetof(S,b)=4 offsetof(S,c)=8 |
| c | A3 | 1 | 1 |  | bitfields sizeof(BF)=4 ; packed (extension) sizeof(P)=5 |
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
| c | C2 | 1 | 1 |  | intrinsèques AVX-512 <immintrin.h> : 32 |
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
| cpp | A1 | 1 | 1 |  | std::vector<S> de valeurs contiguës : &v[1]-&v[0]=16 o |
| cpp | A2 | 1 | 1 |  | offsetof(S,c)=8 (types à disposition standard) |
| cpp | A3 | 1 | 1 |  | champs de bits sizeof(BF)=4 ; packed par attribut gnu sizeof(P)=5 |
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
| cpp | C1 | 1 | 1 |  | std::simd (C++26) : reduce=32 |
| cpp | C2 | 1 | 1 |  | intrinsèques <immintrin.h> : 16 |
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
| fortran | A5 | 1 | 1 |  | TRANSFER(1.0) = 0x3F800000 |
| fortran | B5 | 1 | 1 |  | c_loc + c_f_pointer :  2.0 |
| fortran | C5 | 1 | 1 |  | do concurrent :   72.0 |
| fortran | A3 | 0.5 | 0.5 |  | -fpack-derived (option globale) : storage_size(t) = 6 octets |
| fortran | A4 | 0.5 | 0.5 |  | directives OpenMP : allouable mod 128 = 0 ; locale mod 256 = 0 |
| fortran | B2 | 0.5 | 0.5 |  | arène à la main (tableau de nœuds réutilisé), comme en C : 42 |
| fortran | F2 | 0.5 | 0.5 |  | cotableaux sur un nœud (libcaf_shmem) : images 4, somme 10 |
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
