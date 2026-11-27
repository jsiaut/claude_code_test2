| Langage | Capacité | Sonde | Matrice v2 | v1 | | Preuve |
|---|---|---|---|---|---|---|
| ada | A2 | 1 | 1 | 1 |  | [exécutée] S.C'Position = 8 |
| ada | A3 | 1 | 1 | 1 |  | [exécutée] clause de représentation au bit près : BF'Size = 8 |
| ada | A5 | 1 | 1 | 1 |  | [exécutée] Unchecked_Conversion 0x 1065353216 ; Unchecked_Union UU'Size = 32 |
| ada | D4 | 1 | 1 | 1 |  | [exécutée] aspect CPU => 1 sur une tâche ; CPU disponibles = 4 |
| ada | E5 | 1 | 1 | 1 |  | [exécutée] RM 6.2(12) exploitée par GNAT sur paramètres de type contraint : Y (1) =  7.00000E+00 |
| ada | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] retour non contraint de 4 Mo par la pile secondaire (tas au-delà du morceau statique) :  5.00000000 |
| ada | C1 | 1 | 1 | 0.5 |  | [exécutée] Machine_Attribute vector_type (extension GNAT) : Add =  3.00000E+00 ; ½ en v1 (règle v2 : extension |
| ada | A1 | 1 | 1 | 1 |  | [exécutée] tableau de Part : pas de 16 o = Part'Object_Size/8 16 ; les 4 premiers octets sont le Float X en li |
| ada | A4 | 1 | 1 | 1 |  | [exécutée] aspect Alignment => 64 : Line'Alignment = 64, new Line à 0 mod 64, tableau de Line : pas 64 o, élém |
| ada | A7 | 1 | 1 | 1 |  | [exécutée] record (N : Unsigned_32; A : array (1 .. 16) of Float) : 68 o, I.A'Position = 4 (tableau en ligne) |
| ada | A8 | 1 | 1 | 1 |  | [exécutée] Unsigned_8/Integer_16/Float : 1 / 2 / 4 o ; un array (1 .. 1000) of Unsigned_8 occupe 1000 o |
| ada | B1 | 1 | 1 | 1 |  | [exécutée] aucun ramasse-miettes : mémoire rendue par Unchecked_Deallocation ou par la portée ; 1 fil (Threads |
| ada | B2 | 1 | 1 | 1 |  | [exécutée] pool de stockage utilisateur (System.Storage_Pools) attaché au type d'accès : new y alloue, bloc da |
| ada | B3 | 1 | 1 | 1 |  | [exécutée] Storage_Array (1 .. 4096) local à 848 o d'une autre variable locale, à 140735727204880 o du tas : s |
| ada | B5 | 1 | 1 | 1 |  | [exécutée] System.Address + Storage_Offset et Address_To_Access_Conversions : écriture à +12 -> Buf (4) = 42 ; |
| ada | D1 | 1 | 1 | 1 |  | [exécutée] tâches Ada : 4 tâches, 4 identifiants de fil (gettid) distincts, somme 7998000 (attendu 7998000) |
| ada | E2 | 1 | 1 | 1 |  | [exécutée] System.Machine_Code.Asm ("addl $1, %0") : 41 -> 42 |
| ada | F1 | 1 | 1 | 1 |  | [exécutée] array (Positive range <>, Positive range <>) of Float, bornes connues à l'exécution ( 3 x 4) : M (2 |
| ada | F3 | 1 | 1 | 1 |  | [exécutée] type modulaire mod 256 : 250 + 10 = 4 ; Unsigned_32'Last + 1 = 0 ; Integer'Last + 1 lève Constraint |
| ada | F4 | 0.5 | 0.5 | 0.5 |  | [exécutée] System.Mmap (unité interne de GNAT, s-mmap.ads) + réinterprétation par adresse : 1.50000E+00 4.5000 |
| ada | C2 | 1 | 1 | 0.5 |  | [exécutée] __builtin_ia32_pternlogd512_mask importé (convention Intrinsic) sur un type vectoriel (Machine_Attr |
| ada | C4 | 0.5 | 0.5 | 0.5 |  | [exécutée] option globale -ffast-math : 1 vaddps ymm/zmm (somme vectorisée) contre 15 vaddss sans l'option ; [ |
| ada | D2 | 1 | 1 | 0.5 |  | [exécutée] builtins __atomic_* à ordre explicite importés (Intrinsic), code produit : Release = 1 mov et 0 xch |
| ada | D5 | 1 | 1 | 0.5 |  | [exécutée] __atomic_thread_fence et __builtin_ia32_pause importés : 1 pause (rep nop) et 1 barrière dans spin  |
| ada | E1 | 1 | 1 | 1 |  | [exécutée] gcc-16 -S : 262 lignes d'assembleur pour le paquetage Cg |
| ada | E3 | 1 | 1 | 0.5 |  | [exécutée] GNAT.Branch_Prediction.Likely (unité livrée, __builtin_likely) : disposition [ jne call ret ret ] c |
| ada | E4 | 1 | 1 | 0.5 |  | [exécutée] __builtin_prefetch importé : 1 prefetcht0 dans pf ; ½ en v1 |
| ada | E6 | 1 | 1 | 1 |  | [exécutée] A (I) : 1 appel au contrôle d'indice (__gnat_rcheck_CE_Index_Check) ; sous pragma Suppress (Index_C |
| ada | E7 | 1 | 1 | 1 |  | [exécutée] fonction d'expression statique Sq (1234) en nombre nommé = 1522756 ; Gsum instanciée pour Float : 4 |
| ada | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans adainclude et gnat_rm.info 16.2.0 : 0 entrée, 0 mention (results/grid_audit/search/a |
| ada | C5 | 0 | 0 | 0 |  | [échec] boucle parallel for d'Ada 2022 : error: missing ":" ; le manuel de GNAT note « Feature unimplemented » |
| ada | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans adainclude et gnat_rm.info 16.2.0 : 0 entrée, 0 mention (results/grid_audit/search/a |
| ada | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans adainclude et gnat_rm.info 16.2.0 : 0 entrée, 20 mentions (results/grid_audit/search |
| c | A1 | 1 | 1 | 1 |  | [exécutée] Part v[8] : pas de 16 o = sizeof(Part) 16 ; les 4 premiers octets sont le float x en ligne : 00 00  |
| c | A2 | 1 | 1 | 1 |  | [exécutée] ordre déclaré gardé : (u8, double, u8) occupe 24 o, offsetof(b) = 8, offsetof(c) = 16 |
| c | A3 | 1 | 1 | 0.5 |  | [exécutée] champs de bits (norme) : sizeof(BF) = 4, x = 5, y = 17 ; __attribute__((packed)) : sizeof(Pk) = 5 ; |
| c | A4 | 1 | 1 | 1 |  | [exécutée] alignas(64) : alignof(Line) = 64, Line[] au pas de 64 o, aligned_alloc à 0 mod 64 |
| c | A5 | 1 | 1 | 1 |  | [exécutée] union float/uint32 : 0x3f800000 ; memcpy de réinterprétation identique |
| c | A7 | 1 | 1 | 1 |  | [exécutée] struct { uint32_t n; float a[16]; } : 68 o, offsetof(a) = 4 (tableau en ligne) |
| c | A8 | 1 | 1 | 1 |  | [exécutée] uint8_t/int16_t/_Float16/float : 1/2/2/4 o ; uint8_t[1000] occupe 1000 o |
| c | B1 | 1 | 1 | 1 |  | [exécutée] aucun ramasse-miettes : malloc/free explicites ; 1 fil (Threads: de /proc/self/status) |
| c | B3 | 1 | 1 | 1 |  | [exécutée] char local[4096] à 21783 o d'une autre variable locale, à 46599761949072 o du tas ; VLA float[4] su |
| c | B4 | 1 | 1 | 1 |  | [exécutée] mallinfo2 : tri qsort, copies de structures, littéraux composés, snprintf dans un tampon de pile -> |
| c | B5 | 1 | 1 | 1 |  | [exécutée] uint32_t * : mp[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| c | C1 | 1 | 1 | 0.5 |  | [exécutée] vector_size(32) (extension documentée de clang et gcc) : (a + a)[7] = 16 ; ½ en v1 |
| c | C5 | 1 | 1 | 0.5 |  | [exécutée] OpenMP (livré avec clang et gcc, -fopenmp) : parallel for sur 4 fils distincts (gettid), reduction( |
| c | D1 | 1 | 1 | 1 |  | [exécutée] <threads.h> (C11) : 4 fils, 4 identifiants distincts (gettid), somme 7998000 (attendu 7998000) |
| c | D3 | 1 | 1 | 0.5 |  | [exécutée] __GCC_DESTRUCTIVE_SIZE = 64 (macro prédéfinie par clang et gcc), sysconf(_SC_LEVEL1_DCACHE_LINESIZE |
| c | D4 | 1 | 1 | 0.5 |  | [exécutée] sched_setaffinity de la glibc (bibliothèque système de la plateforme) : retour 0, sched_getcpu() =  |
| c | E2 | 1 | 1 | 0.5 |  | [exécutée] __asm__ ("addq $1, %0" : "+r"(x)) : 41 -> 42 ; ½ en v1 |
| c | F1 | 1 | 1 | 1 |  | [exécutée] float (*m)[cols] = malloc(sizeof(float[rows][cols])), 3 x 4 connus à l'exécution (types à dimension |
| c | F3 | 1 | 1 | 1 |  | [exécutée] UINT32_MAX + 1 = 0, (uint8_t)(250 + 10) = 4 (non signés modulaires ; débordement signé indéfini, -f |
| c | F4 | 1 | 1 | 0.5 |  | [exécutée] mmap (POSIX, glibc) puis réinterprétation par conversion de pointeur : 1.5 2.5 3.5 4.5 ; ½ en v1 |
| c | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] obstack de la glibc (arène, <obstack.h>) : deux blocs consécutifs à 400 o d'écart, libérés d'un cou |
| c | C2 | 1 | 1 | 0.5 |  | [exécutée] _mm512_ternarylogic_epi32 (<immintrin.h> livré avec clang) : 1 vpternlogd dans tern ; ½ en v1 |
| c | C4 | 1 | 1 | 0.5 |  | [exécutée] #pragma clang fp reassociate(on), par bloc : 7 vaddps ymm/zmm dans sum_reassoc contre 9 vaddss dans |
| c | D2 | 1 | 1 | 1 |  | [exécutée] <stdatomic.h> à memory_order explicite, code produit : release = 1 mov et 0 xchg ; seq_cst = 1 xchg |
| c | D5 | 1 | 1 | 0.5 |  | [exécutée] atomic_thread_fence (C11) et _mm_pause : 1 pause et 1 barrière dans spin ; ½ en v1 |
| c | E1 | 1 | 1 | 1 |  | [exécutée] clang -S : 420 lignes d'assembleur, 6 instructions vectorielles flottantes dans axpy |
| c | E3 | 1 | 1 | 0.5 |  | [exécutée] __builtin_expect(x == 7, 0) : disposition [ je retq callq retq ] contre [ jne callq retq ] sans ind |
| c | E4 | 1 | 1 | 0.5 |  | [exécutée] __builtin_prefetch : 1 prefetcht0 dans pf ; ½ en v1 |
| c | E5 | 1 | 1 | 1 |  | [exécutée] restrict (C99) : 2 attributs noalias dans l'IR de axpy |
| c | E6 | 1 | 1 | 1 |  | [exécutée] a[i] : 0 appel de vérification (aucune vérification de bornes dans le langage) |
| c | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] constexpr int K = 12 * 12 = 144 (C23) ; _Generic choisit float puis double (sélection, pas d'instan |
| c | A6 | 0 | 0 | 0 |  | [échec] __attribute__((soa)) : error: unknown attribute 'soa' ignored [-Werror,-Wunknown-attributes] ; [recher |
| c | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans les en-têtes de la glibc et de clang (clang 23.1.5, 2.39) : 14 déclarations (results |
| c3 | A2 | 1 | 1 | 1 |  | [exécutée] $reflect(Sx.c).offset=8 |
| c3 | A3 | 1 | 1 | 1 |  | [exécutée] @packed P.sizeof=5 ; bitstruct BF.sizeof=2 |
| c3 | A5 | 1 | 1 | 1 |  | [exécutée] union 0x3f800000 bitcast 0x3f800000 |
| c3 | A1 | 1 | 1 | 1 |  | [exécutée] Part[] : pas de 16 o = Part::size 16 ; les 4 premiers octets du tampon sont le float x en ligne : 0 |
| c3 | A4 | 1 | 1 | 1 |  | [exécutée] struct @align(64) : Line::alignment = 64, mem::new_aligned(Line) à 0 mod 64 (mem::new refusé à la c |
| c3 | A7 | 1 | 1 | 1 |  | [exécutée] struct { uint n; float[16] a; } : 68 o, $reflect(Inl.a).offset = 4 (tableau en ligne) |
| c3 | A8 | 1 | 1 | 1 |  | [exécutée] char/short/float16/float : 1/2/2/4 o ; char[] de 1000 éléments : 1000 o, short[] : 2000 o |
| c3 | B1 | 1 | 1 | 1 |  | [exécutée] aucune collecte : mémoire rendue par free explicite ou par @pool ; 1 fil (Threads: de /proc/self/st |
| c3 | B2 | 1 | 1 | 1 |  | [exécutée] interface Allocator : ArenaAllocator sur un tampon de pile -> bloc dans le tampon = true, 816 o con |
| c3 | B3 | 1 | 1 | 1 |  | [exécutée] char[4096] local à 3658 o d'une autre variable locale, à 46490076182608 o du tas : sur la pile |
| c3 | B4 | 1 | 1 | 1 |  | [exécutée] allocateur traceur : tri, formatage dans un tampon de pile, tranches, macros -> 0 allocation (255.0 |
| c3 | B5 | 1 | 1 | 1 |  | [exécutée] uint* : mp[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| c3 | C1 | 1 | 1 | 1 |  | [exécutée] float[<8>] : (a + a)[7] = 16.000000, a.sum() = 36.000000, swizzle et comparaisons vectorielles dans |
| c3 | D1 | 1 | 1 | 1 |  | [exécutée] std::thread : 4 fils, 4 identifiants de fil (gettid) distincts, somme 7998000 (attendu 7998000) |
| c3 | D4 | 0.5 | 0.5 | 0.5 |  | [exécutée] @syscall(203, …) : numéro d'appel système écrit à la main (aucune constante ni enveloppe dans std)  |
| c3 | F3 | 1 | 1 | 1 |  | [exécutée] uint::max + 1 = 0, int::max + 1 = -2147483648, (char)250 + 10 = 4 (débordement défini, enveloppant) |
| c3 | F4 | 1 | 1 | 1 |  | [exécutée] std::io::file::mmap_open (portable) + réinterprétation sans copie : 1.500000 2.500000 3.500000 4.50 |
| c3 | C2 | 0.5 | 0.5 | 0.5 |  | [échec] intrinsèques de LLVM par extern @cname, mécanisme que la bibliothèque livrée n'emploie pas : llvm.x86. |
| c3 | C4 | 0.5 | 0.5 | 0.5 |  | [exécutée] option globale --fp-math=relaxed : 9 fadd reassoc (vectorisés) dans sum_plain contre 0 sans l'optio |
| c3 | D2 | 1 | 1 | 1 |  | [exécutée] Atomic{ulong} à AtomicOrdering explicite, code produit : RELEASE = 1 mov et 0 xchg ; SEQ_CONSISTENT |
| c3 | D5 | 0.5 | 0.5 | 0.5 |  | [exécutée] thread::fence(SEQ_CONSISTENT) : 1 barrière et 0 pause dans spin ; [recherche] indication d'attente  |
| c3 | E1 | 1 | 1 | 1 |  | [exécutée] --emit-asm : 135564 lignes d'assembleur, 12 instructions flottantes dans axpy |
| c3 | E2 | 0.5 | 0.5 | 0.5 |  | [exécutée] bloc asm { addl ex, 1; } : 41 -> 42 ; bloc asm avec vaddps sur zmm : accepté ; [échec] vfmadd231ps  |
| c3 | E3 | 1 | 1 | 1 |  | [exécutée] @unlikely(x == 7) : disposition [ je retq callq retq ] contre [ jne callq retq ] sans indication (a |
| c3 | E4 | 1 | 1 | 1 |  | [exécutée] @prefetch(p, VERY_NEAR) : 1 prefetcht0 dans pf |
| c3 | E5 | 0.5 | 0.5 | 0.5 |  | [exécutée] @noalias : sur le 1er paramètre (axpy), noalias posé sur %0 (1) ; [échec] sur le 2e paramètre (axpy |
| c3 | E6 | 1 | 1 | 1 |  | [exécutée] en -O1 (mode sûr), a[i] : 1 comparaison à la longueur et 1 appels à la panique (bornes, alignement) |
| c3 | E7 | 1 | 1 | 1 |  | [exécutée] macro @fib(60) déroulée par $for à la compilation = 1548008755920 ; gsum <float> = 4.000000, gsum < |
| c3 | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans lib/std 0.8.5_1 : 0 déclaration publique, 0 mention (results/grid_audit/search/c3_A6 |
| c3 | C5 | 0 | 0 | 0 |  | [recherche] motif C5 dans lib/std 0.8.5_1 : 41 déclarations publiques (results/grid_audit/search/c3_C5.txt) :  |
| c3 | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans lib/std 0.8.5_1 : 10 déclarations publiques (results/grid_audit/search/c3_D3.txt) :  |
| c3 | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] float[4][3] contigu : &m[1][0] - &m[0][3] = 4 o, sizeof = 48 o ; Slice2d de std::core::array, vue 2 |
| c3 | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans lib/std 0.8.5_1 : 1 déclaration publique (results/grid_audit/search/c3_F2.txt) : xkb |
| chapel | A2 | 1 | 1 | 1 |  | [exécutée] c_offsetof(S, "c")=8 |
| chapel | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] allocate(alignment=64) -> adresse mod 64 = 0 |
| chapel | A5 | 0.5 | 0.5 | 0.5 |  | [exécutée] (1.0: real(32)).transmute(uint(32)) = 1065353216 |
| chapel | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] Allocators (instable) : bumpPtrMemPool + newWithAllocator, v = 7 ; preuves de la remarque sur Chape |
| chapel | C2 | 0.5 | 0.5 | 0.5 |  | [exécutée] _mm512_fmadd_ps importé de immintrin.h : somme = 96.0 (macros à immédiat et builtins : refusés) ; p |
| chapel | B3 | 0.5 | 0.5 | 0.5 |  | [exécutée] c_array local (pile) : 3.0 ; tableaux Chapel sur le tas ; preuves de la remarque sur Chapel : resul |
| chapel | C4 | 0.5 | 0.5 | 0.5 |  | [exécutée] @llvm.metadata(("llvm.loop.vectorize.enable", true)) par boucle (instable) ; preuves de la remarque |
| chapel | E5 | 0.5 | 0.5 | 0.5 |  | [exécutée] foreach (instable) : llvm.loop.parallel_accesses ; noalias automatique, a[0] = 2.0 ; preuves de la  |
| chapel | A1 | 1 | 1 | 1 |  | [exécutée] tableau de records : pas de 16 o = c_sizeof(Part) 16 ; records stockés en ligne dans le tableau |
| chapel | A7 | 1 | 1 | 1 |  | [exécutée] record (n: uint(32), a: 16*real(32)) : 68 o, c_offsetof(Inl, "a") = 4 (tuple homogène en ligne) |
| chapel | A8 | 1 | 1 | 1 |  | [exécutée] int(8)/int(16)/real(32) : 1/2/4 o ; [0..<1000] int(8) occupe 1000 o |
| chapel | B1 | 1 | 1 | 1 |  | [exécutée] pas de ramasse-miettes (owned, shared, unmanaged) : deinit(b) fin-portée deinit(a) ; destruction dé |
| chapel | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] memoryUsed (MemDiagnostics) : un tableau local [0..<1000] real alloue 8200 o sur le tas, sans new n |
| chapel | B5 | 1 | 1 | 1 |  | [exécutée] c_ptr(uint(32)) : p[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| chapel | C5 | 1 | 1 | 1 |  | [exécutée] forall sur 4 fils distincts (gettid), + reduce = 499999500000 (attendu 499999500000) |
| chapel | D1 | 1 | 1 | 1 |  | [exécutée] coforall : 4 tâches sur 4 fils distincts (gettid), somme 7998000 (attendu 7998000) |
| chapel | F1 | 1 | 1 | 1 |  | [exécutée] [1..n, 1..4] real(32) avec n = 3 connu à l'exécution : &M[2,1] - &M[1,4] = 4 o (contigu, par lignes |
| chapel | F2 | 1 | 1 | 1 |  | [exécutée] blockDist.createDomain({1..100}) : tableau distribué sur 1 locale(s) (CHPL_COMM=none : une seule ic |
| chapel | F3 | 1 | 1 | 1 |  | [exécutée] max(uint(32)) + 1 = 0, uint(8) 250 + 10 = 4 (non signés enveloppants ; int(N) de largeur fixe) |
| chapel | D2 | 1 | 1 | 1 |  | [exécutée] atomic avec memoryOrder explicite, code produit : release = 1 mov et 0 xchg ; seqCst = 1 xchg ; fet |
| chapel | D4 | 0.5 | 0.5 | 0.5 |  | [exécutée] coforall de 4 tâches : processeurs 0 1 2 3 (placement décidé par l'exécutif qthreads) ; variables d |
| chapel | D5 | 0.5 | 0.5 | 0.5 |  | [exécutée] atomicFence : 1 barrière dans fence_it ; aucune indication pause (motif D5 : NOTE D5) |
| chapel | E1 | 1 | 1 | 1 |  | [exécutée] binaire natif par LLVM : objdump donne 268988 lignes ; --llvm-print-ir pour l'IR |
| chapel | E4 | 0.5 | 0.5 | 0.5 |  | [exécutée] prefetch du module package Prefetch : 1 prefetcht0 dans pf (module « package », hors des modules st |
| chapel | E6 | 1 | 1 | 1 |  | [exécutée] build --fast --checks : garr[i] = 3 appels à chpl_error (bornes) ; p[i] sur un c_ptr : 0 appel (con |
| chapel | E7 | 1 | 1 | 1 |  | [exécutée] proc pfib(param n) param, évaluée à la compilation : pfib(20) = 6765 ; gsum générique : 4.0 (real(3 |
| chapel | A3 | 0 | 0 | 0 |  | [recherche] motif A3 dans modules de Chapel 2.10.0 : 10 déclarations publiques (results/grid_audit/search/chap |
| chapel | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans modules de Chapel 2.10.0 : 0 déclaration publique, 0 mention (results/grid_audit/sea |
| chapel | C1 | 0 | 0 | 0 |  | [recherche] motif C1 dans modules de Chapel 2.10.0 : 0 déclaration publique, 0 mention (results/grid_audit/sea |
| chapel | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans modules de Chapel 2.10.0 : 14 déclarations publiques (results/grid_audit/search/chap |
| chapel | E2 | 0 | 0 | 0 |  | [recherche] motif E2 dans modules de Chapel 2.10.0 : 0 déclaration publique, 1 mention (results/grid_audit/sea |
| chapel | E3 | 0 | 0 | 0 |  | [recherche] motif E3 dans modules de Chapel 2.10.0 : 1 déclaration publique (results/grid_audit/search/chapel_ |
| chapel | F4 | 0 | 0 | 0 |  | [recherche] motif F4 dans modules de Chapel 2.10.0 : 3 déclarations publiques (results/grid_audit/search/chape |
| cpp | A1 | 1 | 1 | 1 |  | [exécutée] std::vector<Part> : pas de 16 o = sizeof(Part) 16 ; les 4 premiers octets du tampon sont le float x |
| cpp | A2 | 1 | 1 | 1 |  | [exécutée] ordre déclaré gardé : (u8, double, u8) occupe 24 o, offsetof(b) = 8, offsetof(c) = 16 |
| cpp | A3 | 1 | 1 | 0.5 |  | [exécutée] champs de bits (norme) : sizeof(BF) = 4, x = 5, y = 17 ; __attribute__((packed)) : sizeof(Pk) = 5 ; |
| cpp | A4 | 1 | 1 | 1 |  | [exécutée] alignas(64) : alignof(Line) = 64, new Line[4] (new aligné, C++17) à 0 mod 64 |
| cpp | A5 | 1 | 1 | 1 |  | [exécutée] std::bit_cast<std::uint32_t>(1.0f) = 0x3f800000 |
| cpp | A7 | 1 | 1 | 1 |  | [exécutée] struct { uint32_t n; std::array<float, 16> a; } : 68 o, offsetof(a) = 4 (tableau en ligne) |
| cpp | A8 | 1 | 1 | 1 |  | [exécutée] uint8_t/int16_t/std::float16_t/float : 1/2/2/4 o ; std::vector<uint8_t>(1000) : 1000 o |
| cpp | B1 | 1 | 1 | 1 |  | [exécutée] aucun ramasse-miettes : destructeurs et delete explicites ; 1 fil (Threads: de /proc/self/status) |
| cpp | B2 | 1 | 1 | 1 |  | [exécutée] std::pmr::monotonic_buffer_resource sur un tampon de pile, passé à std::pmr::vector : tampon dans l |
| cpp | B3 | 1 | 1 | 1 |  | [exécutée] char local[4096] à 4721 o d'une autre variable locale, à 140732016630272 o du tas : sur la pile |
| cpp | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] operator new compté : std::function à capture de 64 o -> 1 allocation ; throw std::runtime_error -> |
| cpp | B5 | 1 | 1 | 1 |  | [exécutée] uint32_t * : mp[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| cpp | C5 | 1 | 1 | 0.5 |  | [exécutée] OpenMP (livré avec g++, -fopenmp) : parallel for sur 4 fils distincts (gettid), reduction(+) = 4999 |
| cpp | D1 | 1 | 1 | 1 |  | [exécutée] std::jthread : 4 fils, 4 identifiants distincts (gettid), somme 7998000 (attendu 7998000) |
| cpp | D3 | 1 | 1 | 1 |  | [exécutée] std::hardware_destructive_interference_size = 64 |
| cpp | D4 | 1 | 1 | 0.5 |  | [exécutée] sched_setaffinity de la glibc (bibliothèque système de la plateforme) : retour 0, sched_getcpu() =  |
| cpp | E2 | 1 | 1 | 1 |  | [exécutée] déclaration asm (norme ; forme étendue de g++) : 41 -> 42 |
| cpp | F1 | 1 | 1 | 1 |  | [exécutée] std::mdspan (C++23) de 3 x 4 connus à l'exécution : &m[1, 0] - &m[0, cols-1] = 4 o (contigu, layout |
| cpp | F3 | 1 | 1 | 1 |  | [exécutée] UINT32_MAX + 1 = 0, uint8_t(250 + 10) = 4 (non signés modulaires ; débordement signé indéfini) |
| cpp | F4 | 1 | 1 | 0.5 |  | [exécutée] mmap (POSIX, glibc) + std::start_lifetime_as_array (C++23) : 1.5 2.5 3.5 4.5 ; ½ en v1 |
| cpp | C1 | 1 | 1 | 0.5 |  | [exécutée] vector_size(32) (extension documentée de g++) : 1 vaddps dans vadd ; std::simd de C++26 reste expér |
| cpp | C2 | 1 | 1 | 0.5 |  | [exécutée] _mm512_ternarylogic_epi32 (<immintrin.h> livré avec g++) : 1 vpternlogd dans tern ; ½ en v1 |
| cpp | C4 | 1 | 1 | 1 |  | [exécutée] #pragma omp simd reduction(+:s) (OpenMP SIMD, livré, -fopenmp-simd), par boucle : 1 vaddps ymm/zmm  |
| cpp | D2 | 1 | 1 | 1 |  | [exécutée] std::atomic à memory_order explicite, code produit : release = 1 mov et 0 xchg ; seq_cst = 1 xchg ; |
| cpp | D5 | 1 | 1 | 0.5 |  | [exécutée] std::atomic_thread_fence et _mm_pause : 1 pause (rep nop) et 1 barrière dans spin ; ½ en v1 |
| cpp | E1 | 1 | 1 | 1 |  | [exécutée] g++ -S : 825 lignes d'assembleur |
| cpp | E3 | 1 | 1 | 1 |  | [exécutée] [[likely]] (C++20) : disposition [ jne call ret ret ] contre [ je ret call ret ] sans indication (a |
| cpp | E4 | 1 | 1 | 0.5 |  | [exécutée] __builtin_prefetch : 1 prefetcht0 dans pf ; ½ en v1 |
| cpp | E5 | 1 | 1 | 0.5 |  | [exécutée] __restrict__ (extension documentée de g++) : axpy_r « 1 boucle vectorisée », 0 version pour alias ; |
| cpp | E6 | 1 | 1 | 1 |  | [exécutée] v[i] : 0 appel ; v.at(i) : 1 appel à __throw_out_of_range_fmt (dans idx_at.cold) : contrôle par exp |
| cpp | E7 | 1 | 1 | 1 |  | [exécutée] consteval fib(60) = 1548008755920 ; gsum<float> = 4.0, gsum<double> = 3.75 ; dans l'asm, fib60 = 1  |
| cpp | A6 | 0 | 0 | 0 |  | [échec] __attribute__((soa)) : error: 'soa' attribute directive ignored [-Werror=attributes] ; [recherche] mot |
| cpp | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans les en-têtes de libstdc++ 16.2.0 et de la glibc : 2 déclarations (results/grid_audit |
| csharp | A1 | 1 | 1 | 1 |  | [exécutée] P16[1000] (struct de 16 float) : Unsafe.SizeOf = 64 o, écart entre éléments 64 o (valeurs en ligne) |
| csharp | A2 | 1 | 1 | 1 |  | [exécutée] LayoutKind.Sequential {byte; uint; double} : décalages A=0 B=4 C=8 (ordre déclaré) ; LayoutKind.Exp |
| csharp | A3 | 0.5 | 0.5 | 0.5 |  | [exécutée] StructLayout(Pack = 1) {byte; uint} : Unsafe.SizeOf = 5 o ; [échec] champ de bits int x : 3 : error |
| csharp | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] NativeMemory.AlignedAlloc(256, 64) : adresse mod 64 = 0 (alignement par allocation, à la main) ; pa |
| csharp | A5 | 1 | 1 | 1 |  | [exécutée] FieldOffset(0) recouvrants (union brute) : float 1.0 → 0x3f800000 ; BitConverter.SingleToUInt32Bits |
| csharp | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans l'API publique de .NET 10.0.14 (paquet de référence Microsoft.NETCore.App.Ref, 38383 |
| csharp | A7 | 1 | 1 | 1 |  | [exécutée] [InlineArray(16)] de float dans une struct : sizeof(In) = 68 o, N à 64 (tableau fixe en ligne) |
| csharp | A8 | 1 | 1 | 1 |  | [exécutée] sizeof : byte 1, short 2, Half 2 (1.5), float 4 |
| csharp | B1 | 0 | 0 | 0 |  | [échec] 1 Gio de tableaux de 1 Kio sans référence : 4 collectes de génération 0 déclenchées par le runtime, sa |
| csharp | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] ArrayPool<float>.Shared : Rent, Return, Rent rend le même tableau (True) ; NativeMemory.Alloc hors  |
| csharp | B3 | 1 | 1 | 1 |  | [exécutée] stackalloc float[16] : à 1804 o d'une variable locale (pile) ; Span<float> sur ce tampon et struct  |
| csharp | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] octets alloués par opération (GC.GetAllocatedBytesForCurrentThread) : arithmétique sur des structs  |
| csharp | B5 | 1 | 1 | 1 |  | [exécutée] pointeurs unsafe : *(p + 3) = 42 → buf[3] = 42 ; écriture par décalage d'octets → buf[4] = 7 |
| csharp | C1 | 1 | 1 | 1 |  | [exécutée] Vector256.FusedMultiplyAdd(2, 3, 1) = 7 ; Vector512<float> (Vector512.IsHardwareAccelerated = True) |
| csharp | C2 | 1 | 1 | 1 |  | [exécutée] System.Runtime.Intrinsics.X86 : Avx512F.IsSupported = True, Avx512F.Add = 3 ; code machine de CgAvx |
| csharp | C4 | 0 | 0 | 0 |  | [échec] un million de doubles : boucle foreach (JIT, niveau 1) -145.65551935166778, Enumerable.Sum -145.655519 |
| csharp | C5 | 1 | 1 | 1 |  | [exécutée] Parallel.For : 64 itérations sur 5 fils (PLINQ aussi : System.Linq.ParallelEnumerable) |
| csharp | D1 | 1 | 1 | 1 |  | [exécutée] System.Threading.Thread : 4 fils, 4000 incréments |
| csharp | D2 | 1 | 1 | 1 |  | [exécutée] Interlocked.Increment → 1, Interlocked.CompareExchange → 5, Volatile.Write/Read → 9 ; code machine  |
| csharp | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans l'API publique de .NET 10.0.14 (paquet de référence Microsoft.NETCore.App.Ref, 38383 |
| csharp | D4 | 0.5 | 0.5 | 0.5 |  | [exécutée] Process.ProcessorAffinity : 0xf → 0x2, processeur courant 1 ; sur Linux, sched_setaffinity sur le P |
| csharp | D5 | 1 | 1 | 1 |  | [exécutée] X86Base.Pause, Interlocked.MemoryBarrier, Thread.SpinWait et SpinWait.SpinOnce (5 tours) ; code mac |
| csharp | E1 | 1 | 1 | 1 |  | [exécutée] DOTNET_JitDisasm : 16 méthodes Cg* listées (1281 lignes), compilées en FullOpts (variables d'enviro |
| csharp | E2 | 0 | 0 | 0 |  | [échec] asm("pause") : error CS0103: The name 'asm' does not exist in the current context ; [recherche] motif  |
| csharp | E3 | 0 | 0 | 0 |  | [recherche] motif E3 dans l'API publique de .NET 10.0.14 (paquet de référence Microsoft.NETCore.App.Ref, 38383 |
| csharp | E4 | 1 | 1 | 1 |  | [exécutée] Sse.Prefetch0(p) : 1 prefetcht0 dans le code machine (aussi Prefetch1, Prefetch2, PrefetchNonTempor |
| csharp | E5 | 0 | 0 | 0 |  | [échec] Axpy(y[1..9], y[0..8], 2) sur des tranches qui se recouvrent : y[8] = 511 (chaque écriture relue : le  |
| csharp | E6 | 1 | 1 | 1 |  | [exécutée] a[4] sur un float[4] : IndexOutOfRangeException ; Unsafe.Add(ref MemoryMarshal.GetArrayDataReferenc |
| csharp | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] CgSum<T> where T : INumber<T> : int 6, double 0.75, float 1.5 ; CgCount<T> where T : class : 2 (str |
| csharp | F1 | 1 | 1 | 1 |  | [exécutée] double[3,4] aux dimensions connues à l'exécution : écart entre lignes 32 o, g2[2,3] à 88 o = élémen |
| csharp | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans l'API publique de .NET 10.0.14 (paquet de référence Microsoft.NETCore.App.Ref, 38383 |
| csharp | F3 | 1 | 1 | 1 |  | [exécutée] byte…ulong, Int128 (16 o) : uint.MaxValue + 6 = 5 (unchecked, défaut) ; checked : OverflowException |
| csharp | F4 | 1 | 1 | 1 |  | [exécutée] MemoryMappedFile + pointeur : k5_a.f32 projeté (True, /proc/self/maps), premier float 0.4390046, de |
| d | A2 | 1 | 1 | 1 |  | [exécutée] S.c.offsetof=8 |
| d | A4 | 1 | 1 | 1 |  | [exécutée] align(64) L.alignof=64 |
| d | A5 | 1 | 1 | 1 |  | [exécutée] union 0x3f800000 |
| d | F4 | 1 | 1 | 1 |  | [exécutée] std.mmfile + cast : 0.439005 |
| d | A3 | 1 | 1 | 1 |  | [exécutée] champs de bits natifs sans -preview : NativeBF.sizeof=4 a=5 b=17 |
| d | A1 | 1 | 1 | 1 |  | [exécutée] Part[] : pas de 16 o = Part.sizeof 16 ; les 4 premiers octets du tampon sont le float x en ligne :  |
| d | A7 | 1 | 1 | 1 |  | [exécutée] struct { uint n; float[16] a; } : 68 o, Inl.a.offsetof = 4 (tableau en ligne) |
| d | A8 | 1 | 1 | 1 |  | [exécutée] ubyte/short/float : 1/2/4 o ; ubyte[] de 1000 éléments : 1000 o, short[] : 2000 o |
| d | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] std.experimental.allocator : Region sur un tampon de pile -> bloc dans le tampon = true ; module ex |
| d | B3 | 1 | 1 | 1 |  | [exécutée] float[1024] local à 476 o d'une autre variable locale, à 256700812792 o du tas : sur la pile ; stru |
| d | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] octets alloués par le GC, mesurés par GC.stats : fermeture rendue par une fonction 16 o, littéral d |
| d | B5 | 1 | 1 | 1 |  | [exécutée] uint* : mp[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| d | C1 | 1 | 1 | 1 |  | [exécutée] core.simd float8 : (a + a)[7] = 16, opérateurs vectoriels du langage |
| d | C5 | 1 | 1 | 1 |  | [exécutée] std.parallelism : foreach parallèle sur 3 fils distincts (gettid), taskPool.reduce = 499999500000 ( |
| d | D1 | 1 | 1 | 1 |  | [exécutée] core.thread : 4 fils, 4 identifiants de fil (gettid) distincts, somme 7998000 (attendu 7998000) |
| d | D3 | 1 | 1 | 1 |  | [exécutée] std.parallelism.cacheLineSize = 64, core.cpuid.dataCaches()[0].lineSize = 64 |
| d | D4 | 1 | 1 | 0.5 |  | [exécutée] core.sys.linux.sched.sched_setaffinity (liaison livrée avec druntime ; ½ en v1) : retour 0, sched_g |
| d | E2 | 1 | 1 | 1 |  | [exécutée] asm { mov EAX, 41; add EAX, 1; mov ex, EAX; } (assembleur en ligne du langage) : 42 |
| d | F3 | 1 | 1 | 1 |  | [exécutée] uint.max + 1 = 0, int.max + 1 = -2147483648, ubyte 250 + 10 = 4 (arithmétique modulaire définie) |
| d | B1 | 0.5 | 0.5 | 0.5 |  | [exécutée] new et tableaux dynamiques passent par le ramasse-miettes de druntime : 100 collectes pendant 200 a |
| d | C2 | 1 | 1 | 0.5 |  | [exécutée] ldc.gccbuiltins_x86.__builtin_ia32_pternlogd512 : 12 ^ 10 ^ 1 = 7 ; 1 vpternlogd dans tern (module  |
| d | C4 | 1 | 1 | 0.5 |  | [exécutée] @fastmath (ldc.attributes), par fonction : 9 fadd fast (vectorisés) dans sum_fast contre 0 dans sum |
| d | D2 | 1 | 1 | 1 |  | [exécutée] core.atomic à MemoryOrder explicite, code produit : rel = 1 mov et 0 xchg ; seq = 1 xchg ; atomicFe |
| d | D5 | 1 | 1 | 1 |  | [exécutée] core.atomic.pause et atomicFence : 1 pause et 1 barrière dans spin |
| d | E1 | 1 | 1 | 1 |  | [exécutée] -output-s : 928 lignes d'assembleur, 10 instructions vectorielles flottantes dans axpy |
| d | E3 | 1 | 1 | 1 |  | [exécutée] core.builtins.expect(x == 7, false) : disposition [ je retq callq retq ] contre [ jne callq retq ]  |
| d | E4 | 1 | 1 | 1 |  | [exécutée] core.simd.prefetch!(false, 3) : 1 prefetcht0 dans pf |
| d | E5 | 1 | 1 | 0.5 |  | [exécutée] @restrict (ldc.attributes) : 2 attributs noalias dans l'IR de axpy ; ½ en v1 |
| d | E6 | 1 | 1 | 1 |  | [exécutée] avec -boundscheck=on, a[i] : 1 appel à _d_arraybounds_index ; a.ptr[i] : 0 (contrôle par expression |
| d | E7 | 1 | 1 | 1 |  | [exécutée] enum F60 = fib(60) évalué par CTFE = 1548008755920 ; gsum!float = 4, gsum!double = 3.75 ; dans l'as |
| d | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans druntime, Phobos et ldc de LDC 1.43.0 : 0 ligne de code, 0 mention (results/grid_aud |
| d | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] float[4][3] contigu : &m[1][0] - &m[0][3] = 4 o, sizeof = 48 o ; new float[4][](5) : &r[1][0] - &r[ |
| d | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans druntime, Phobos et ldc de LDC 1.43.0 : 185 lignes de code (results/grid_audit/searc |
| fortran | A5 | 1 | 1 | 1 |  | [exécutée] TRANSFER(1.0) = 0x3F800000 |
| fortran | B5 | 1 | 1 | 1 |  | [exécutée] c_loc + c_f_pointer :  2.0 |
| fortran | C5 | 1 | 1 | 1 |  | [exécutée] do concurrent :   72.0 |
| fortran | A3 | 0.5 | 0.5 | 0.5 |  | [exécutée] -fpack-derived (option globale) : storage_size(t) = 6 octets |
| fortran | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] arène à la main (tableau de nœuds réutilisé), comme en C : 42 |
| fortran | A4 | 1 | 1 | 0.5 |  | [exécutée] directives OpenMP : allouable mod 128 = 0 ; locale mod 256 = 0 (directives OpenMP livrées avec gfor |
| fortran | F2 | 0.5 | 0.5 | 0.5 |  | [exécutée] cotableaux sur un nœud (libcaf_shmem) : images 4, somme 10 |
| fortran | A1 | 1 | 1 | 1 |  | [exécutée] tableau de type dérivé bind(c) : pas de 16 o = storage_size/8 16 ; les composantes sont stockées en |
| fortran | A7 | 1 | 1 | 1 |  | [exécutée] type (n : int32, a(16) : real32) : 68 o, a(1) à 4 o du début (tableau en ligne) |
| fortran | A8 | 1 | 1 | 1 |  | [exécutée] int8/int16/real32 (iso_fortran_env) : 1/2/4 o ; tableau de 1000 int8 : 1000 o |
| fortran | B1 | 1 | 1 | 1 |  | [exécutée] aucun ramasse-miettes : allouables libérés à la sortie de portée ou par deallocate ; 1 fil (Threads |
| fortran | B3 | 1 | 1 | 1 |  | [exécutée] real loc(1024) local à une procédure à 1672 o d'une autre variable locale, à 140729629390080 o d'un |
| fortran | D1 | 1 | 1 | 0.5 |  | [exécutée] !$omp parallel (OpenMP livré avec gfortran) : 4 fils, 4 identifiants de fil (gettid) distincts, som |
| fortran | F1 | 1 | 1 | 1 |  | [exécutée] real, allocatable :: m(:,:), m(3, 4) alloué à l'exécution : m(2,1) - m(1,1) = 4 o, m(1,2) - m(3,1)  |
| fortran | A2 | 0.5 | 0.5 | 0.5 |  | [exécutée] type bind(c) : disposition du C, décalage de z mesuré par c_loc = 8 o, de m = 12 o ; [recherche] mo |
| fortran | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans gfortran.info et omp_lib.f90 16.2.0 : 0 entrée, 0 mention (results/grid_audit/search |
| fortran | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] -fcheck=array-temps : An array temporary was created for argument 'x' of procedure 's' (section non |
| fortran | C1 | 0 | 0 | 0 |  | [recherche] motif C1 dans gfortran.info et omp_lib.f90 16.2.0 : 3 entrées (results/grid_audit/search/fortran_C |
| fortran | C2 | 0 | 0 | 0 |  | [recherche] motif C2 propre à Fortran (« intrinsic » y désigne les procédures de la norme) dans gfortran.info  |
| fortran | C4 | 1 | 1 | 0.5 |  | [exécutée] !$omp simd reduction(+:s) (OpenMP livré), par boucle : 1 vaddps ymm/zmm dans sum_simd contre 15 vad |
| fortran | D2 | 1 | 1 | 0.5 |  | [exécutée] !$omp atomic à clause d'ordre, code produit : write release = 1 mov et 0 xchg ; write seq_cst = 1 x |
| fortran | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans gfortran.info et omp_lib.f90 16.2.0 : 0 entrée ; 15 mentions (results/grid_audit/sea |
| fortran | D4 | 1 | 1 | 0.5 |  | [exécutée] fil OpenMP sous OMP_PLACES={1} OMP_PROC_BIND=true : sched_getcpu() = 1, omp_get_proc_bind() = true  |
| fortran | D5 | 0.5 | 0.5 | 0.5 |  | [exécutée] !$omp flush : 1 barrière dans flushit ; [recherche] indication d'attente active : motif D5, 0 entré |
| fortran | E1 | 1 | 1 | 1 |  | [exécutée] gfortran -S : 478 lignes d'assembleur pour le module cg |
| fortran | E2 | 0 | 0 | 0 |  | [recherche] motif E2 dans gfortran.info 16.2.0 : 0 entrée ; 3 mentions (results/grid_audit/search/fortran_E2.t |
| fortran | E3 | 0 | 0 | 0 |  | [recherche] motif E3 dans gfortran.info 16.2.0 : 0 entrée ; 10 mentions, toutes en prose (« likely », « expect |
| fortran | E4 | 0 | 0 | 0 |  | [recherche] motif E4 dans gfortran.info et omp_lib.f90 16.2.0 : 0 entrée, 0 mention (results/grid_audit/search |
| fortran | E5 | 1 | 1 | 1 |  | [exécutée] règle des arguments muets (pas d'alias) : axpy en Fortran : 1 boucle vectorisée, 0 version pour ali |
| fortran | E6 | 1 | 1 | 1 |  | [exécutée] a(i) sans option : 0 appel de vérification ; avec -fcheck=bounds (globale) : 2 appels au rapport d' |
| fortran | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] expression constante product([(k, k = 1, 15)]) = 1307674368000, constante immédiate dans f15c (1) ; |
| fortran | F3 | 0.5 | 0.5 | 0.5 |  | [exécutée] type unsigned, extension de gfortran 15 sous -funsigned : unsigned 4294967295u + 1u = 0 ; [échec] s |
| fortran | F4 | 0 | 0 | 0 |  | [recherche] motif F4 dans gfortran.info et omp_lib.f90 16.2.0 : 0 entrée, 0 mention (results/grid_audit/search |
| fpc | A1 | 1 | 1 | 1 |  | [exécutée] array of record : SizeOf(TParticle) = 64 o, écart entre éléments 64 o (valeurs en ligne) |
| fpc | A2 | 1 | 1 | 1 |  | [exécutée] record : décalages a=0 b=8 c=16 (ordre déclaré, alignement naturel) ; {$PACKRECORDS C} : taille 12  |
| fpc | A3 | 1 | 1 | 1 |  | [exécutée] packed record {Byte; LongWord} : 5 o ; bitpacked record {0..7; 0..31} : 1 o, champs relus 5 et 17 |
| fpc | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] GetMem + Align(p, 64) : adresse mod 64 = 0 (à la main) ; {$CODEALIGN VARMIN=64} pour les variables  |
| fpc | A5 | 1 | 1 | 1 |  | [exécutée] record à variantes sans champ d'étiquette (union brute) : Single 1.0 = $3F800000, octets 0 0 128 63 |
| fpc | A7 | 1 | 1 | 1 |  | [exécutée] record avec array[0..15] of Single : 64 o en ligne |
| fpc | A8 | 1 | 1 | 1 |  | [exécutée] Byte 1 SmallInt 2 Word 2 Single 4 ; intervalles bitpacked (A3) ; pas de flottant 16 bits |
| fpc | B1 | 1 | 1 | 1 |  | [exécutée] pas de ramasse-miettes : comptage de références des chaînes, tableaux dynamiques et interfaces (Str |
| fpc | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] SetMemoryManager (gestionnaire global remplaçable : 1 appel compté pour New) ; NewInstance/FreeInst |
| fpc | B3 | 1 | 1 | 1 |  | [exécutée] records et tableaux statiques locaux sur la pile (distance à une variable locale : 1312 o ; au tas  |
| fpc | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] allocations implicites : boucle sur un tableau 0, énumération d'un TDictionary 1 (objet énumérateur |
| fpc | C1 | 0.5 | 0.5 | 0.5 |  | [exécutée] -Sv : opérations sur array[0..3] of Single (SSE 128 bits) : 2 6 12 20 ; expérimental : 8 Single = e |
| fpc | C2 | 0.5 | 0.5 | 0.5 |  | [exécutée] assembleur en ligne jusqu'à AVX2 et FMA (E2), sans intrinsèques SSE/AVX, comme Zig : seulement des  |
| fpc | D1 | 1 | 1 | 1 |  | [exécutée] BeginThread (unité cthreads) et TThread : 4 fils, 4000 incréments |
| fpc | D2 | 0.5 | 0.5 | 0.5 |  | [exécutée] InterLockedIncrement64 / CompareExchange64 / ExchangeAdd64 (RMW séquentiellement cohérents, appels  |
| fpc | D4 | 1 | 1 | 0.5 |  | [exécutée] Do_SysCall(syscall_nr_sched_setaffinity) de l'unité Syscall livrée : retour 0, masque relu 2, proce |
| fpc | D5 | 0.5 | 0.5 | 0.5 |  | [exécutée] ReadBarrier / WriteBarrier / ReadWriteBarrier (lfence, sfence, mfence dans des procédures de la RTL |
| fpc | E2 | 1 | 1 | 1 |  | [exécutée] blocs asm (syntaxe Intel ou AT&T, procédures assembler) : 42 ; AVX2 accepté, AVX-512 inconnu de l'a |
| fpc | E4 | 0.5 | 0.5 | 0.5 |  | [exécutée] Prefetch(x) du System (intrinsèque : prefetchnta seulement, sans localité ni écriture, run.sh) ; er |
| fpc | E6 | 1 | 1 | 1 |  | [exécutée] {$R+} / {$R-} locaux : indice 5 hors bornes détecté sous {$R+} : TRUE ; sans vérification ailleurs  |
| fpc | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] génériques spécialisés à la compilation (specialize) : 7 2.5 ; expressions constantes (1219), pas d |
| fpc | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] array[0..3, 0..7] of Double : 256 o contigus (écart entre lignes 64 o), bornes fixées à la compilat |
| fpc | F3 | 1 | 1 | 1 |  | [exécutée] Byte...QWord et ShortInt...Int64, arithmétique modulaire sans {$Q+} (défaut) : 0 -2147483648 |
| fpc | F4 | 1 | 1 | 0.5 |  | [exécutée] Fpmmap (unité BaseUnix livrée, appel système propre à Unix, comme syscall.Mmap de Go ; 1 en règle v |
| fpc | C4 | 0 | 0 | 0 |  | [échec] -OoFASTMATH (aussi {$OPTIMIZATION FASTMATH}) sur une réduction : 0 FMA sans l'option, 1 avec (contract |
| fpc | B5 | 1 | 1 | 1 |  | [exécutée] pointeurs typés avec {$pointermath} : (p + 3)^ := 42 -> buf[3] = 42 ; écriture par décalage d'octet |
| fpc | E1 | 1 | 1 | 1 |  | [exécutée] fpc -al garde l'assembleur : 380 lignes pour audit.pas |
| fpc | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans l'interface des unités livrées (RTL, rtl-*, fcl-* ; ppudump) de FPC 3.2.2 : 0 symbol |
| fpc | C5 | 0 | 0 | 0 |  | [recherche] motif C5 dans l'interface des unités livrées de FPC 3.2.2 : 2 symboles (results/grid_audit/search/ |
| fpc | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans l'interface des unités livrées de FPC 3.2.2 : 2 symboles (results/grid_audit/search/ |
| fpc | E3 | 0 | 0 | 0 |  | [échec] Likely : Error: Identifier not found "Likely" (base.sh) ; [recherche] motif E3 dans l'interface des un |
| fpc | E5 | 0 | 0 | 0 |  | [échec] axpy(@x[1], @x[0], 7) sur des tampons qui se recouvrent : x[7] = 247.0 (le compilateur doit supposer l |
| fpc | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans l'interface des unités livrées de FPC 3.2.2 : 4 symboles (results/grid_audit/search/ |
| go | A1 | 1 | 1 | 1 |  | [exécutée] []Particle (struct de 16 float32) : unsafe.Sizeof = 64 o, écart entre éléments 64 o (valeurs en lig |
| go | A2 | 1 | 1 | 1 |  | [exécutée] unsafe.Offsetof : A=0 B=4 C=8 (ordre déclaré gardé par gc, alignement naturel) |
| go | A3 | 0 | 0 | 0 |  | [échec] struct {uint8; uint32} : unsafe.Sizeof = 8 o (bourrage imposé, aucun attribut packed) ; champ de bits  |
| go | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] sur-allocation + arrondi d'adresse : 9397654282624 mod 64 = 0 (à la main) ; pas d'attribut d'aligne |
| go | A5 | 0.5 | 0.5 | 0.5 |  | [exécutée] math.Float32bits(1) = 0x3f800000 ; *(*uint32)(unsafe.Pointer(&f)) = 0x3f800000 ; [échec] union : sy |
| go | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans l'API publique de Go 1.27.3 (api/go1*.txt livrés avec la chaîne) : 4 déclarations :  |
| go | A7 | 1 | 1 | 1 |  | [exécutée] struct {[16]float32; int32} : unsafe.Sizeof = 68 o, N à 64 (tableau fixe en ligne) |
| go | A8 | 1 | 1 | 1 |  | [exécutée] unsafe.Sizeof : uint8 1, int16 2, float32 4 (pas de flottant 16 bits) |
| go | B1 | 0 | 0 | 0 |  | [échec] 1 Gio de tranches de 1 Kio sans référence : 348 collectes déclenchées par le runtime, sans appel du pr |
| go | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] paquet arena avec GOEXPERIMENT=arenas : arena.New deux fois → objets à 400 o l'un de l'autre, MakeS |
| go | B3 | 0.5 | 0.5 | 0.5 |  | [exécutée] testing.AllocsPerRun : struct locale dont l'adresse ne sort pas 0 allocation, la même dont l'adress |
| go | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] testing.AllocsPerRun : arithmétique 0 ; allocations implicites : struct mise dans une interface 1,  |
| go | B5 | 1 | 1 | 1 |  | [exécutée] unsafe.Pointer + unsafe.Add : b[3] = 42 ; écriture par décalage d'octets → b[4] = 7 |
| go | C1 | 0.5 | 0.5 | 0.5 |  | [exécutée] paquet simd portable (GOEXPERIMENT=simd) : simd.VectorBitSize() = 512, LoadFloat32s(a).MulAdd(b, c) |
| go | C2 | 0.5 | 0.5 | 0.5 |  | [exécutée] simd/archsimd (GOEXPERIMENT=simd) : LoadFloat32x16(a).Add(b) = 5, 1 VADDPS sur Z dans le code machi |
| go | C4 | 0 | 0 | 0 |  | [échec] un million de float64 : boucle compilée 182.66375347116414, somme par paires écrite à la main 182.6637 |
| go | C5 | 0 | 0 | 0 |  | [recherche] motif C5 dans l'API publique de Go 1.27.3 (api/go1*.txt livrés avec la chaîne) : 3 déclarations :  |
| go | D1 | 1 | 1 | 1 |  | [exécutée] 4 goroutines sur 4 fils système (GOMAXPROCS) : 4000 incréments ; runtime.LockOSThread lie une gorou |
| go | D2 | 0.5 | 0.5 | 0.5 |  | [exécutée] sync/atomic : Store/Load → 5, Add → 1 ; aucune méthode à ordre relâché, acquire ou release ; code m |
| go | D3 | 0 | 0 | 0 |  | [échec] internal/cpu.CacheLinePad : use of internal package internal/cpu not allowed ; [recherche] motif D3 da |
| go | D4 | 1 | 1 | 0.5 |  | [exécutée] runtime.LockOSThread + syscall.RawSyscall(SYS_SCHED_SETAFFINITY) du paquet syscall livré : errno 0, |
| go | D5 | 0 | 0 | 0 |  | [échec] runtime.procyield (PAUSE, interne) : undefined: runtime.procyield ; [recherche] motif D5 dans l'API pu |
| go | E1 | 1 | 1 | 1 |  | [exécutée] go tool objdump : 9 fonctions cg* désassemblées ; aussi go build -gcflags=-S |
| go | E2 | 0.5 | 0.5 | 0.5 |  | [exécutée] assembleur de Go dans un fichier .s à part (asm/add_amd64.s, TEXT ·addOne) : addOne(41) = 42 ; [éch |
| go | E3 | 0 | 0 | 0 |  | [recherche] motif E3 dans l'API publique de Go 1.27.3 (api/go1*.txt livrés avec la chaîne) : 0 déclaration (re |
| go | E4 | 0 | 0 | 0 |  | [échec] internal/runtime/sys.Prefetch : use of internal package internal/runtime/sys not allowed ; [recherche] |
| go | E5 | 0 | 0 | 0 |  | [échec] axpy(y[1:9], y[0:8], 2) sur des tranches qui se recouvrent : y[8] = 511 (chaque écriture relue : le co |
| go | E6 | 1 | 1 | 1 |  | [exécutée] four[4] : panique « runtime error: index out of range [4] with length 4 » ; unsafe.Add sans contrôl |
| go | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] cgSum[int] = 6, cgSum[float64] = 0.75 ; cgCount[*A] = 2, cgCount[*B] = 3 ; code machine : 3 corps,  |
| go | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] [3][4]float64 : [2][3] à 88 o = élément 11 du bloc contigu (tailles constantes) ; dimensions connue |
| go | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans l'API publique de Go 1.27.3 (api/go1*.txt livrés avec la chaîne) : 113 déclarations  |
| go | F3 | 1 | 1 | 1 |  | [exécutée] uint8…uint64, int8…int64 : MaxUint32 + 6 = 5, int8(127) + 1 = -128 (enveloppement défini par la spé |
| go | F4 | 1 | 1 | 0.5 |  | [exécutée] syscall.Mmap du paquet syscall livré + unsafe.Slice : k5_a.f32 projeté (true, /proc/self/maps), pre |
| haskell | A1 | 0.5 | 0.5 | 0.5 |  | [exécutée] Storable P4 (4 float) : tableau à plat, 16 o par élément, élément 1 à 16 o (vx = 2.5) ; Data.Array  |
| haskell | A2 | 0.5 | 0.5 | 0.5 |  | [exécutée] instance Storable écrite à la main, décalages de struct s {uint8_t; uint32_t; double} calculés par  |
| haskell | A3 | 0.5 | 0.5 | 0.5 |  | [exécutée] struct __attribute__((packed)) {uint8_t; uint32_t} : taille 5, b à 1 (hsc2hs) ; instance Storable d |
| haskell | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] allocaBytesAligned 256 64 : adresse mod 64 = 0 ; tableaux épinglés alignés (newAlignedPinnedByteArr |
| haskell | A5 | 0.5 | 0.5 | 0.5 |  | [exécutée] castFloatToWord32 1.0 = 0x3f800000 ; Float relu en Word32 par castPtr = 0x3f800000 ; pas d'union |
| haskell | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules |
| haskell | A7 | 0.5 | 0.5 | 0.5 |  | [exécutée] instance Storable {16 float; int32} : 68 o, n à 64 (relu 9, f[15] = 15) ; un champ tableau d'un enr |
| haskell | A8 | 1 | 1 | 1 |  | [exécutée] sizeOf : Word8 1, Int16 2, Float 4 ; UArray Int Word8 range un octet par élément ; pas de flottant  |
| haskell | B1 | 0 | 0 | 0 |  | [échec] 1 Gio de tableaux de 1 Kio sans référence : 341 collectes déclenchées par le RTS, sans appel du progra |
| haskell | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] Foreign.Marshal.Pool : deux blocs pooledMallocBytes (distincts), libérés d'un coup à la sortie de w |
| haskell | B3 | 0.5 | 0.5 | 0.5 |  | [exécutée] n-uplet non boxé (# Int#, Int# #) rendu par une fonction NOINLINE : 0 o alloués pour 100 000 appels |
| haskell | B4 | 0 | 0 | 0 |  | [échec] allocations implicites : addG :: Num a => a -> a -> a (NOINLINE, dictionnaire) sur des Double, 120 o p |
| haskell | B5 | 1 | 1 | 1 |  | [exécutée] Foreign.Ptr : pokeByteOff p 12 → p[3] = 42 ; plusPtr 16 → p[4] = 7 |
| haskell | C1 | 0.5 | 0.5 | 0.5 |  | [exécutée] FloatX16# et fmaddFloatX16# (GHC.Exts, primops propres à GHC) : x*y + x sur 16 voies lues en mémoir |
| haskell | C2 | 0 | 0 | 0 |  | [recherche] motif C2 dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules |
| haskell | C4 | 0 | 0 | 0 |  | [échec] un million de Double : pli gauche compilé 181.8862985769915, somme par paires écrite à la main 181.886 |
| haskell | C5 | 0.5 | 0.5 | 0.5 |  | [exécutée] par et pseq (étincelles par#) sur 8 calculs : somme 840000015 : 8 étincelles, 7 converties en calcu |
| haskell | D1 | 1 | 1 | 1 |  | [exécutée] RTS multi-fil, 4 capacités : 4 fils Haskell (forkIO), 4000 incréments ; forkOS et forkOn aussi |
| haskell | D2 | 0.5 | 0.5 | 0.5 |  | [exécutée] atomicModifyIORef' ×10 → 10 ; primops fetchAddIntArray#, casIntArray#, atomicReadIntArray# → (5,8,2 |
| haskell | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules |
| haskell | D4 | 0.5 | 0.5 | 0.5 |  | [exécutée] forkOn 2 avec +RTS -N4 -qa (capacités épinglées par le RTS) : le fil tourne sur le processeur 2 ; p |
| haskell | D5 | 0 | 0 | 0 |  | [recherche] motif D5 dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules |
| haskell | E1 | 1 | 1 | 1 |  | [exécutée] ghc -S (générateur natif) : 163 lignes pour Comptime.hs ; -keep-s-files (LLVM) : 34026 lignes pour  |
| haskell | E2 | 0 | 0 | 0 |  | [échec] asm "pause" : Variable not in scope: asm :: String -> IO () ; [recherche] motif E2 dans l'API des bibl |
| haskell | E3 | 0 | 0 | 0 |  | [recherche] motif E3 dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules |
| haskell | E4 | 1 | 1 | 1 |  | [exécutée] prefetchMutableByteArray3# et prefetchMutableByteArray0# (GHC.Exts) : 1 prefetcht0 et 1 prefetchnta |
| haskell | E5 | 0 | 0 | 0 |  | [recherche] motif E5 dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules |
| haskell | E6 | 1 | 1 | 1 |  | [exécutée] four ! 4 : erreur « Ix{Int}.index: Index (4) out of range ((0,3)) » ; unsafeAt four 2 = 3 (sans con |
| haskell | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] Template Haskell : $(lift (fib 25)) = 75025, calculé pendant la compilation ; spécialisation des cl |
| haskell | F1 | 1 | 1 | 1 |  | [exécutée] UArray (Int, Int) Double de 3×4 : g ! (2, 3) = 11, élément 11 du tableau à plat (bornes connues à l |
| haskell | F2 | 0 | 0 | 0 |  | [échec] +RTS --numa : « n: --numa: This GHC build was compiled without NUMA support. » ; [recherche] motif F2  |
| haskell | F3 | 1 | 1 | 1 |  | [exécutée] Word32 : maxBound + 6 = 5 ; Int8 : 127 + 1 = -128 (enveloppement) |
| haskell | F4 | 0 | 0 | 0 |  | [recherche] motif F4 dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules |
| java | A1 | 0.5 | 0.5 | 0.5 |  | [exécutée] FFM : sequenceLayout(1000, struct de 16 float) : 64000 o, élément 1 à 64 o (en ligne, hors tas) ; u |
| java | A2 | 0.5 | 0.5 | 0.5 |  | [exécutée] FFM : structLayout {byte; padding 3; int; double} : décalages a=0 b=4 c=8 (disposition C écrite à l |
| java | A3 | 0.5 | 0.5 | 0.5 |  | [exécutée] FFM : structLayout {byte; int.withByteAlignment(1)} : 5 o (non aligné) ; [échec] champ de bits int  |
| java | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] Arena.allocate(256, 64) : adresse mod 64 = 0 (hors tas seulement) ; objets du tas alignés sur Objec |
| java | A5 | 0.5 | 0.5 | 0.5 |  | [exécutée] Float.floatToRawIntBits(1f) = 0x3f800000 ; FFM unionLayout {float; int} (4 o) : float 1.0 relu en i |
| java | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans l'API exportée d'OpenJDK 27.0.1 (paquets exportés des modules système, 48847 noms :  |
| java | A7 | 0.5 | 0.5 | 0.5 |  | [exécutée] FFM : structLayout {float[16]; int} : 68 o, n à 64 ; objets : le champ float[] f de class WithArr e |
| java | A8 | 1 | 1 | 1 |  | [exécutée] byte 1, short 2, float 4 (Byte.BYTES…) ; Float.floatToFloat16(1.5f) = 0x3e00 (demi-précision rangée |
| java | B1 | 0 | 0 | 0 |  | [échec] 1 Gio de tableaux de 1 Kio sans référence : 14 collectes déclenchées par la JVM (G1), sans appel du pr |
| java | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] SegmentAllocator.slicingAllocator (arène par tranches) : deux blocs à 400 o d'écart dans le même ta |
| java | B3 | 0 | 0 | 0 |  | [échec] record Pt(int, int) rendu par une méthode non incorporée : 16 o de tas par appel (un million d'appels  |
| java | B4 | 0 | 0 | 0 |  | [échec] ArrayList<Integer> de 100 000 entiers (génériques effacés : un Integer par élément) : 16 o de tas par  |
| java | B5 | 0.5 | 0.5 | 0.5 |  | [exécutée] MemorySegment : écriture à l'octet 12 → ia[3] = 42 ; lecture hors du segment : IndexOutOfBoundsExce |
| java | C1 | 0.5 | 0.5 | 0.5 |  | [exécutée] Vector API : FloatVector.SPECIES_512 (16 voies), fma(2, 3, 1) = 7.0 ; module jdk.incubator.vector,  |
| java | C2 | 0 | 0 | 0 |  | [recherche] motif C2 dans l'API exportée d'OpenJDK 27.0.1 (paquets exportés des modules système, 48847 noms :  |
| java | C4 | 0.5 | 0.5 | 0.5 |  | [exécutée] un million de float : boucle ordonnée (C2) 203.02669, accumulateur FloatVector + reduceLanes(ADD),  |
| java | C5 | 1 | 1 | 1 |  | [exécutée] IntStream.range(0, 64).parallel() : 64 itérations sur 4 fils (ForkJoinPool commun) |
| java | D1 | 1 | 1 | 1 |  | [exécutée] java.lang.Thread : 4 fils, 4000 incréments (fils virtuels aussi) |
| java | D2 | 1 | 1 | 1 |  | [exécutée] VarHandle : setRelease/getAcquire → 1, setOpaque/getOpaque → 2, compareAndSet(2, 5) → true, getAndA |
| java | D3 | 0.5 | 0.5 | 0.5 |  | [exécutée] @jdk.internal.vm.annotation.Contended sur deux champs long voisins (javac --add-exports java.base/j |
| java | D4 | 0 | 0 | 0 |  | [recherche] motif D4 dans l'API exportée d'OpenJDK 27.0.1 (paquets exportés des modules système, 48847 noms :  |
| java | D5 | 1 | 1 | 1 |  | [exécutée] Thread.onSpinWait, VarHandle.fullFence / acquireFence / releaseFence exécutés (code machine invisib |
| java | E1 | 0.5 | 0.5 | 0.5 |  | [exécutée] -XX:+PrintCompilation : 248 méthodes compilées listées ; [échec] -XX:+PrintAssembly : « Loading hsd |
| java | E2 | 0 | 0 | 0 |  | [échec] asm("pause") : error: cannot find symbol ; [recherche] motif E2 dans l'API exportée d'OpenJDK 27.0.1 ( |
| java | E3 | 0 | 0 | 0 |  | [recherche] motif E3 dans l'API exportée d'OpenJDK 27.0.1 (paquets exportés des modules système, 48847 noms :  |
| java | E4 | 0 | 0 | 0 |  | [recherche] motif E4 dans l'API exportée d'OpenJDK 27.0.1 (paquets exportés des modules système, 48847 noms :  |
| java | E5 | 0 | 0 | 0 |  | [échec] axpy(y, 1, y, 0, 8, 2) sur un même tableau : y[8] = 511.0 (chaque écriture relue : le compilateur doit |
| java | E6 | 0 | 0 | 0 |  | [échec] four[4] sur un int[4] : ArrayIndexOutOfBoundsException ; ni option ni construction pour couper la véri |
| java | E7 | 0 | 0 | 0 |  | [échec] génériques effacés, List<int> : error: unexpected type ; pas d'évaluation à la compilation, case N ave |
| java | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] double[3][4] : tableau de tableaux (lignes séparées, g2[1] remplacée par une ligne de 7 éléments) ; |
| java | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans l'API exportée d'OpenJDK 27.0.1 (paquets exportés des modules système, 48847 noms :  |
| java | F3 | 0.5 | 0.5 | 0.5 |  | [exécutée] entiers signés seulement : (byte) 200 = -56, Integer.MAX_VALUE + 1 = -2147483648 (enveloppe) ; Inte |
| java | F4 | 1 | 1 | 1 |  | [exécutée] FileChannel.map → MemorySegment : k5_a.f32 projeté (true, /proc/self/maps), premier float 0.4390046 |
| julia | A2 | 1 | 1 | 1 |  | [exécutée] fieldoffset(S, 3)=8 |
| julia | A5 | 1 | 1 | 1 |  | [exécutée] reinterpret(UInt32, 1f0)=0x3f800000 |
| julia | F4 | 1 | 1 | 1 |  | [exécutée] Mmap.mmap -> Vector{Float32} : 0.4390046 |
| julia | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] Libc.malloc + unsafe_wrap (publics) : arène à la main, somme = 500500 |
| julia | D3 | 0.5 | 0.5 | 0.5 |  | [exécutée] Threads.PaddedSpinLock public = true, sizeof = 120 (propre aux verrous) |
| julia | E3 | 0 | 0 | 0 |  | [échec] llvm.expect par llvmcall : poids de branchement dans l'IR optimisé = false |
| julia | A1 | 1 | 1 | 1 |  | [exécutée] Vector{Part} (isbits) : pas de 16 o = sizeof(Part) 16 ; les 4 premiers octets du tampon sont le Flo |
| julia | A7 | 1 | 1 | 1 |  | [exécutée] struct (n::UInt32, a::NTuple{16,Float32}) : 68 o, fieldoffset(Inl, 2) = 4 (tuple en ligne) |
| julia | A8 | 1 | 1 | 1 |  | [exécutée] UInt8/Int16/Float16/Float32 : 1/2/2/4 o ; Vector{UInt8}(undef, 1000) : 1000 o de données |
| julia | B1 | 0 | 0 | 0 |  | [exécutée] tout tableau et tout objet mutable passent par le ramasse-miettes : 7 collectes pendant 200 allocat |
| julia | B3 | 0.5 | 0.5 | 0.5 |  | [exécutée] octets alloués par appel (Base.gc_num, résultats conservés) : tuple 0 o, struct isbits 0 o (pile ou |
| julia | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] octets alloués par appel (Base.gc_num) : fermeture rendue 16 o, la même sur une variable réaffectée |
| julia | B5 | 1 | 1 | 1 |  | [exécutée] Ptr{UInt32} : unsafe_store!(q, 42, 4) -> buf[4] = 42 ; écriture par décalage d'octets -> buf[5] = 7 |
| julia | C1 | 0.5 | 0.5 | 0.5 |  | [exécutée] NTuple{8,VecElement{Float32}} + llvmcall : (a + a)[8] = 16.0, 1 vaddps ymm ; aucun type vectoriel a |
| julia | C2 | 1 | 1 | 0.5 |  | [exécutée] Base.llvmcall vers llvm.x86.avx512.pternlog.d.512 : 12 ^ 10 ^ 1 = 7, 1 vpternlogd ; ½ en v1 |
| julia | C4 | 1 | 1 | 1 |  | [exécutée] @fastmath et @simd, par expression ou par boucle : vaddps ymm/zmm = 3 (@fastmath), 3 (@simd), 0 san |
| julia | C5 | 1 | 1 | 1 |  | [exécutée] Threads.@threads sur 4 fils distincts (gettid, julia -t 4) |
| julia | D1 | 1 | 1 | 1 |  | [exécutée] Threads.@spawn : 4 tâches sur 4 fils (gettid), somme 7998000 (attendu 7998000) ; 55 |
| julia | D2 | 1 | 1 | 1 |  | [exécutée] @atomic à ordre explicite, code produit : :release = 1 mov et 0 xchg ; :sequentially_consistent = 1 |
| julia | D5 | 1 | 1 | 0.5 |  | [exécutée] Threads.atomic_fence et llvm.x86.sse2.pause par llvmcall : 1 pause et 1 barrière ; ½ en v1 (pause h |
| julia | E1 | 1 | 1 | 1 |  | [exécutée] @code_native : 127 lignes d'assembleur pour sum_simd ; @code_llvm pour l'IR |
| julia | E2 | 1 | 1 | 0.5 |  | [exécutée] llvmcall portant de l'assembleur en ligne (asm de l'IR de LLVM) : leaq 1(x) avec x = 41 -> 42 ; ½ e |
| julia | E4 | 1 | 1 | 0.5 |  | [exécutée] llvmcall vers llvm.prefetch : 1 prefetcht0 ; ½ en v1 |
| julia | E5 | 0.5 | 0.5 | 0.5 |  | [exécutée] Base.Experimental.@aliasscope et Const (module Experimental) : contrôles de recouvrement (vector.me |
| julia | E6 | 1 | 1 | 1 |  | [exécutée] x[i] : 1 appel à throw_boundserror ; @inbounds x[i] : 0 (local, par expression ; --check-bounds=no  |
| julia | E7 | 1 | 1 | 1 |  | [exécutée] @generated : fibg(Val(60)) = 1548008755920, calculé à la compilation (1 constante immédiate dans le |
| julia | F1 | 1 | 1 | 1 |  | [exécutée] Matrix{Float32}(3, 4) de taille connue à l'exécution : M[2,1] - M[1,1] = 4 o, M[1,2] - M[3,1] = 4 o |
| julia | F2 | 0.5 | 0.5 | 0.5 |  | [exécutée] Distributed (addprocs(2)) et SharedArray : propriétaires des éléments [2, 3] ; processus et mémoire |
| julia | F3 | 1 | 1 | 1 |  | [exécutée] typemax(UInt32) + 1 = 0, typemax(Int32) + Int32(1) = -2147483648, 0xfa + 0x0a = 4 (arithmétique ent |
| julia | A3 | 0 | 0 | 0 |  | [recherche] motif A3 dans les noms publics de Base, Core et des bibliothèques standard de Julia 1.13.3 (intros |
| julia | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] Vector{Float32}(undef, 1000) à 0 mod 64 (alignement choisi par l'allocateur de tableaux) ; [recherc |
| julia | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans les noms publics : 0 nom ; StructArrays est un paquet tiers |
| julia | D4 | 0.5 | 0.5 | 0.5 |  | [exécutée] JULIA_EXCLUSIVE=1 julia -t 4 : processeurs des fils [0, 1, 2, 3] ; Base.setcpuaffinity(`grep Cpus_a |
| mojo | A4 | 1 | 1 | 1 |  | [exécutée] @align(64) : align_of = 64 , somme des adresses mod 64 (64 sur la pile, 50 sur le tas) = 0 |
| mojo | A5 | 1 | 1 | 1 |  | [exécutée] UnsafeUnion[Float32, UInt32] : size_of = 4 , bits de 1.0f = 1065353216 |
| mojo | C4 | 0.5 | 0.5 | 0.5 |  | [exécutée] fma[FastMathFlag.REASSOC] = 7.0 (seule opération qui prend le drapeau) |
| mojo | D5 | 1 | 1 | 1 |  | [exécutée] fence() et SpinWaiter.wait() exécutés (pause dans le runtime à partir du 4e appel) |
| mojo | E5 | 1 | 1 | 1 |  | [exécutée] Pointer.unsafe_as_noalias() : 7 |
| mojo | A1 | 1 | 1 | 1 |  | [exécutée] List[Part] : pas de 16 o = size_of[Part]() 16 ; les 4 premiers octets du tampon sont le Float32 x e |
| mojo | A2 | 1 | 1 | 1 |  | [exécutée] reflect[Part].field_offset (à la compilation) : z à 8 o, m à 12 o ; ordre déclaré |
| mojo | A7 | 1 | 1 | 1 |  | [exécutée] struct (n: UInt32, a: Array[Float32, 16]) : 68 o, field_offset de a = 4 (tableau en ligne) |
| mojo | A8 | 1 | 1 | 1 |  | [exécutée] UInt8/Int16/Float16/Float32 : 1 / 2 / 2 / 4 o ; List[UInt8](capacity=1000) : capacité 1000 o |
| mojo | B1 | 1 | 1 | 1 |  | [exécutée] pas de ramasse-miettes (propriété) : del(b) fin-portée del(a) ; destruction au dernier usage (ASAP) |
| mojo | B3 | 1 | 1 | 1 |  | [exécutée] Array[Float32, 1024] local à 112 o d'une autre variable locale, à 52140098627336 o du tas : sur la  |
| mojo | B5 | 1 | 1 | 1 |  | [exécutée] UnsafePointer[UInt32] : (p + 3)[] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] =  |
| mojo | C1 | 1 | 1 | 1 |  | [exécutée] SIMD[DType.float32, 8] : (a + a)[7] = 16.0 , a.reduce_add() = 36.0 ; type vectoriel du langage |
| mojo | D1 | 0.5 | 0.5 | 0.5 |  | [exécutée] create_task de std.runtime._asyncrt (module privé, souligné ; aucune API publique de fils) : 4 tâch |
| mojo | E2 | 1 | 1 | 1 |  | [exécutée] inlined_assembly["leaq 1($1), $0"] : 41 -> 42 |
| mojo | F3 | 1 | 1 | 1 |  | [exécutée] UInt32.MAX + 1 = 0 , UInt8(250) + 10 = 4 , Int32.MAX + 1 = -2147483648 (entiers à largeur fixe enve |
| mojo | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] unsafe_alloc et free (std.memory.alloc) : allocation et libération à la main ; [recherche] interfac |
| mojo | B4 | 1 | 1 | 1 |  | [exécutée] noalloc (structures, SIMD, fermeture capturante, boucle) : 0 appel dans le code produit, donc aucun |
| mojo | C2 | 1 | 1 | 0.5 |  | [exécutée] llvm_intrinsic["llvm.x86.avx512.pternlog.d.512"] : 12 ^ 10 ^ 1 = 7, 1 vpternlogd dans tern (llvm_in |
| mojo | D2 | 1 | 1 | 1 |  | [exécutée] Atomic.store et fetch_add à Ordering explicite (std.atomic), code produit : RELEASE = 1 mov et 0 xc |
| mojo | E1 | 1 | 1 | 1 |  | [exécutée] binaire natif par LLVM : objdump donne 2460 lignes |
| mojo | E3 | 1 | 1 | 1 |  | [exécutée] unlikely (std.sys.intrinsics) : disposition [ je ret call ret ] contre [ jne call ret ] sans indica |
| mojo | E4 | 1 | 1 | 1 |  | [exécutée] prefetch[PrefetchOptions().for_read().high_locality()] : 1 prefetcht0 dans pf |
| mojo | E6 | 1 | 1 | 1 |  | [exécutée] l[i] sur une List : 1 appel à _debug_assert_fail (assertions actives par défaut) ; l.unsafe_get(i)  |
| mojo | E7 | 1 | 1 | 1 |  | [exécutée] comptime F60 = fib(60) = 1548008755920 ; gsum[DType.float32] = 4.0 , gsum[DType.float64] = 3.75 ; d |
| mojo | A3 | 0 | 0 | 0 |  | [recherche] motif A3 dans std de Mojo 1.2.0 : 0 déclaration publique ; 11 mentions (pack_bits, données « packe |
| mojo | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans std de Mojo 1.2.0 : 0 déclaration publique, 0 mention (results/grid_audit/search/moj |
| mojo | C5 | 0 | 0 | 0 |  | [recherche] motif C5 dans std de Mojo 1.2.0 : 1 déclaration publique (results/grid_audit/search/mojo_C5.txt) : |
| mojo | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans std de Mojo 1.2.0 : 0 déclaration publique ; 2 mentions (étiquettes ReadDCache de pr |
| mojo | D4 | 0 | 0 | 0 |  | [recherche] motif D4 dans std de Mojo 1.2.0 : 0 déclaration publique ; 2 mentions : _create_task(desired_worke |
| mojo | F1 | 0.5 | 0.5 | 0.5 |  | [recherche] motif F1 dans std de Mojo 1.2.0 : 0 déclaration publique (results/grid_audit/search/mojo_F1.txt) : |
| mojo | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans std de Mojo 1.2.0 : 2 déclarations publiques (results/grid_audit/search/mojo_F2.txt) |
| mojo | F4 | 0 | 0 | 0 |  | [recherche] motif F4 dans std de Mojo 1.2.0 : 0 déclaration publique, 0 mention (results/grid_audit/search/moj |
| nim | A2 | 1 | 1 | 1 |  | [exécutée] offsetOf(S, c)=8 |
| nim | A3 | 1 | 1 | 1 |  | [exécutée] packed sizeof(P)=5 ; bitsize sizeof(BF)=4 |
| nim | A4 | 1 | 1 | 1 |  | [exécutée] align(64) alignof(L)=64 |
| nim | A5 | 1 | 1 | 1 |  | [exécutée] union 0x3F800000 |
| nim | F4 | 1 | 1 | 1 |  | [exécutée] std/memfiles : 0.4390046 |
| nim | A1 | 1 | 1 | 1 |  | [exécutée] seq[Part] : pas de 16 o = sizeof(Part) 16 ; les 4 premiers octets du tampon sont le float32 x en li |
| nim | A7 | 1 | 1 | 1 |  | [exécutée] object (n: uint32, a: array[16, float32]) : 68 o, offsetOf(Inl, a) = 4 (tableau en ligne) |
| nim | A8 | 1 | 1 | 1 |  | [exécutée] uint8/int16/float32 : 1/2/4 o ; seq[uint8] de 1000 éléments : 1000 o, seq[int16] : 2000 o |
| nim | B1 | 1 | 1 | 1 |  | [exécutée] ORC/ARC, destruction déterministe : destroy(b) fin-portée destroy(a) ; 1 fil dans /proc/self/task ( |
| nim | B3 | 1 | 1 | 1 |  | [exécutée] array[4096, uint8] local à 1841 o d'une autre variable locale, à 752851953176 o du tas : sur la pil |
| nim | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] getAllocStats (-d:nimAllocStats) : fermeture qui capture (allocCount: 1, deallocCount: 0), ajout à  |
| nim | B5 | 1 | 1 | 1 |  | [exécutée] ptr UncheckedArray[uint32] : mp[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = |
| nim | D1 | 1 | 1 | 1 |  | [exécutée] std/typedthreads : 4 fils, 4 identifiants de fil (getThreadId) distincts, somme 7998000 (attendu 79 |
| nim | E2 | 1 | 1 | 1 |  | [exécutée] instruction asm (assembleur étendu de GCC, variables Nim entre accents graves) : 41 -> 42 |
| nim | F3 | 1 | 1 | 1 |  | [exécutée] high(uint32) + 1 = 0, high(int32) +% 1 = -2147483648, 250'u8 + 10 = 4 (non signés modulaires ; +% p |
| nim | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] alloc0/dealloc du tas de Nim : bloc de 400 o, q[99] = 7 ; aucune interface d'allocateur sous --mm:o |
| nim | C2 | 1 | 1 | 0.5 |  | [exécutée] importc de _mm512_ternarylogic_epi32 depuis immintrin.h, compilé par clang 23 : tern(1) = 12 ^ 10 ^ |
| nim | C4 | 0.5 | 0.5 | 0.5 |  | [exécutée] {.localPassC: "-ffast-math".} sur le module fastsum : 7 vaddps ymm/zmm dans sum_fast contre 0 dans  |
| nim | C5 | 0.5 | 0.5 | 0.5 |  | [exécutée] for i in ||(0, 3999) avec -fopenmp, vérifications coupées dans le corps : 4 fils distincts (gettid) |
| nim | D2 | 1 | 1 | 1 |  | [exécutée] std/atomics à MemoryOrder explicite, code produit : moRelease = 1 mov et 0 xchg ; moSequentiallyCon |
| nim | D4 | 1 | 1 | 1 |  | [exécutée] Thread.pinToCpu(t, 1) : sched_getcpu() dans le fil = 1 (std/typedthreads) |
| nim | D5 | 1 | 1 | 1 |  | [exécutée] cpuRelax (std/sysatomics) et fence(moSequentiallyConsistent) : 1 pause et 1 barrière dans spin |
| nim | E1 | 1 | 1 | 1 |  | [exécutée] binaire natif par le C : objdump donne 8888 lignes, 10 instructions vectorielles flottantes dans ax |
| nim | E3 | 1 | 1 | 1 |  | [exécutée] likely/unlikely (module system, __builtin_expect dans le C généré) : avec gcc 16, compilateur C par |
| nim | E4 | 1 | 1 | 0.5 |  | [exécutée] importc de __builtin_prefetch : 1 prefetcht0 dans pf ; ½ en v1 |
| nim | E5 | 1 | 1 | 1 |  | [exécutée] paramètres {.noalias.} : 2 NIM_NOALIAS (restrict) dans le prototype C de axpy |
| nim | E6 | 1 | 1 | 1 |  | [exécutée] a[i] sur une seq : 1 appel à raiseIndexError ; sous {.push boundChecks: off.} : 0 |
| nim | E7 | 1 | 1 | 1 |  | [exécutée] const F60 = fib(60) évalué par la VM du compilateur = 1548008755920 ; gsum[float32] = 4.0, gsum[flo |
| nim | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans lib de Nim 2.2.12 : 0 déclaration publique, 0 mention (results/grid_audit/search/nim |
| nim | C1 | 0 | 0 | 0 |  | [recherche] motif C1 dans lib de Nim 2.2.12 : 0 déclaration publique, 8 mentions (results/grid_audit/search/ni |
| nim | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans lib de Nim 2.2.12 : 2 déclarations publiques (results/grid_audit/search/nim_D3.txt)  |
| nim | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] array[3, array[4, float32]] contigu : &m[1][0] - &m[0][3] = 4 o, sizeof = 48 o ; [échec] array[n, a |
| nim | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans lib de Nim 2.2.12 : 14 déclarations publiques (results/grid_audit/search/nim_F2.txt) |
| ocaml | A1 | 0 | 0 | 0 |  | [échec] Array de 1000 enregistrements {4 float} : 6001 mots atteignables (6 par élément : un pointeur et un bl |
| ocaml | A2 | 0 | 0 | 0 |  | [échec] {char; int32; float} : 3 mots dans le bloc, int32 rangé à part (9 mots atteignables en tout) : un mot  |
| ocaml | A3 | 0 | 0 | 0 |  | [échec] {bool; int} : 2 mots (16 octets) : aucun compactage ni champ de bits ; [recherche] motif A3 dans les 7 |
| ocaml | A4 | 0 | 0 | 0 |  | [recherche] motif A4 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | A5 | 0.5 | 0.5 | 0.5 |  | [exécutée] Int32.bits_of_float 1.0 = 0x3f800000 ; Int64.bits_of_float 1.0 = 0x3ff0000000000000 ; octets relus  |
| ocaml | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | A7 | 0 | 0 | 0 |  | [échec] {float array; int} : 2 mots dans le bloc, le tableau de 16 float est un bloc séparé (20 mots atteignab |
| ocaml | A8 | 0.5 | 0.5 | 0.5 |  | [exécutée] Bigarray : int8 1 octet, int16 2, float32 4 (stockage) ; les valeurs lues sont des int de 63 bits o |
| ocaml | B1 | 0 | 0 | 0 |  | [échec] 1 Gio de tableaux de 1 Kio sans référence : 512 collectes mineures déclenchées par le runtime, sans ap |
| ocaml | B2 | 0 | 0 | 0 |  | [recherche] motif B2 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | B3 | 0 | 0 | 0 |  | [échec] n-uplet rendu par une fonction [@inline never] : 3 mots alloués par appel ; incorporée [@inline] : 0 ( |
| ocaml | B4 | 0 | 0 | 0 |  | [échec] allocations implicites : float rendu par une fonction non incorporée 6 mots par appel (boîte) ; somme  |
| ocaml | B5 | 0.5 | 0.5 | 0.5 |  | [exécutée] Bigarray hors tas : Array1.sub ba 3 5 (vue décalée, sans copie) puis view.{0} <- 42 → ba.{3} = 42 ; |
| ocaml | C1 | 0 | 0 | 0 |  | [échec] type float32x4 : Error: Unbound type constructor float32x4 ; [recherche] motif C1 dans les 74 interfac |
| ocaml | C2 | 0 | 0 | 0 |  | [recherche] motif C2 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | C4 | 0 | 0 | 0 |  | [échec] un million de float : boucle compilée -188.32790167414723, somme par paires écrite à la main -188.3279 |
| ocaml | C5 | 0 | 0 | 0 |  | [échec] Domainslib (bibliothèque tierce) : Error: Unbound module Domainslib ; [recherche] motif C5 dans les 74 |
| ocaml | D1 | 1 | 1 | 1 |  | [exécutée] Domain.spawn : 4 domaines (fils système), 4000 incréments (Domain.recommended_domain_count = 4) |
| ocaml | D2 | 0.5 | 0.5 | 0.5 |  | [exécutée] Atomic : compare_and_set 5 → 8 : true, fetch_and_add 3 → 8 puis 11 (séquentiellement cohérents) ; [ |
| ocaml | D3 | 1 | 1 | 1 |  | [exécutée] Atomic.make_contended : bloc de 7 mots, 64 octets avec l'en-tête (une ligne de cache) ; Atomic.make |
| ocaml | D4 | 0 | 0 | 0 |  | [recherche] motif D4 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | D5 | 0.5 | 0.5 | 0.5 |  | [exécutée] Domain.cpu_relax exécuté : 1 pause dans caml_ml_domain_cpu_relax du runtime (objdump) ; [recherche] |
| ocaml | E1 | 1 | 1 | 1 |  | [exécutée] ocamlopt -S : 10127 lignes d'assembleur pour audit.ml |
| ocaml | E2 | 0 | 0 | 0 |  | [échec] asm "pause" : Error: Unbound value asm ; [recherche] motif E2 dans les 74 interfaces livrées avec OCam |
| ocaml | E3 | 0 | 0 | 0 |  | [recherche] motif E3 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | E4 | 0 | 0 | 0 |  | [recherche] motif E4 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | E5 | 0 | 0 | 0 |  | [recherche] motif E5 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | E6 | 1 | 1 | 1 |  | [exécutée] four.(4) : Invalid_argument « index out of bounds » ; Array.unsafe_get four 2 = 3 (local) ; code ma |
| ocaml | E7 | 0 | 0 | 0 |  | [échec] pas de monomorphisation : 1 corps pour poly_sum dans l'assembleur, appelé sur des float avec allocatio |
| ocaml | F1 | 1 | 1 | 1 |  | [exécutée] Bigarray.Array2 c_layout 3×4 (dimensions à l'exécution) : g.{2,3} = 11, élément 11 du bloc à plat = |
| ocaml | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans les 74 interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, thread |
| ocaml | F3 | 0.5 | 0.5 | 0.5 |  | [exécutée] Int32.add Int32.max_int 1l = -2147483648 (enveloppe) ; Int32.unsigned_to_int (-1l) = 4294967295 ; u |
| ocaml | F4 | 1 | 1 | 1 |  | [exécutée] Unix.map_file → Bigarray float32 : k5_a.f32 projeté (true, /proc/self/maps), premier float 0.439004 |
| odin | A2 | 1 | 1 | 1 |  | [exécutée] offset_of(S, c)=8 |
| odin | A3 | 1 | 1 | 1 |  | [exécutée] #packed size_of(P)=5 ; bit_field size_of(BF)=2 |
| odin | A5 | 1 | 1 | 1 |  | [exécutée] #raw_union 0x3f800000 transmute 0x3f800000 |
| odin | A1 | 1 | 1 | 1 |  | [exécutée] []Part : pas de 16 o = size_of(Part) 16 ; les 4 premiers octets du tampon sont le f32 x en ligne :  |
| odin | A4 | 1 | 1 | 1 |  | [exécutée] struct #align(64) : align_of = 64, new(Line) à 0 mod 64, []Line : pas 64 o, éléments à 0 mod 64 |
| odin | A6 | 1 | 1 | 1 |  | [exécutée] #soa[]Part : &soa[1].x - &soa[0].x = 4 o ; soa.y commence 400 o après soa.x (un tableau par champ)  |
| odin | A7 | 1 | 1 | 1 |  | [exécutée] struct { n: u32, a: [16]f32 } : 68 o, offset_of(Inl, a) = 4 (tableau en ligne) |
| odin | A8 | 1 | 1 | 1 |  | [exécutée] u8/i16/f16/f32 : 1/2/2/4 o ; []u8 de 1000 éléments : 1000 o, []i16 : 2000 o |
| odin | B1 | 1 | 1 | 1 |  | [exécutée] aucune collecte : mémoire rendue par free/delete explicites ; 1 fil dans /proc/self/task (aucun fil |
| odin | B2 | 1 | 1 | 1 |  | [exécutée] context.allocator remplacé par mem.arena_allocator sur un tampon de pile : make et append y allouen |
| odin | B3 | 1 | 1 | 1 |  | [exécutée] [4096]u8 local à 4138 o d'une autre variable locale, à 46123243176512 o du tas : sur la pile |
| odin | B4 | 1 | 1 | 1 |  | [exécutée] allocateur traceur dans le contexte : tri, formatage dans un tampon, tranches, procédures -> 0 allo |
| odin | B5 | 1 | 1 | 1 |  | [exécutée] [^]u32 : mp[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| odin | C1 | 1 | 1 | 1 |  | [exécutée] #simd[8]f32 : (a + a)[7] = 16, simd.reduce_add_ordered(a) = 36, simd.shuffle et simd.select dans co |
| odin | D1 | 1 | 1 | 1 |  | [exécutée] core:thread : 4 fils, 4 identifiants de fil (gettid) distincts, somme 7998000 (attendu 7998000) |
| odin | D4 | 1 | 1 | 0.5 |  | [exécutée] core:sys/linux.sched_setaffinity (livré avec le compilateur ; ½ en v1, appel système brut) : retour |
| odin | E2 | 1 | 1 | 1 |  | [exécutée] procédure assembleur add64 :: asm(a: i64, b: i64) -> (r: i64) { mov r, a; add r, b; } : add64(41, 1 |
| odin | F3 | 1 | 1 | 1 |  | [exécutée] max(u32) + 1 = 0, max(i32) + 1 = -2147483648, u8 250 + 10 = 4 (débordement défini, sans piège) |
| odin | F4 | 1 | 1 | 0.5 |  | [exécutée] core:mem/virtual.map_file_from_path (portable) + slice.reinterpret : [1.5, 2.5, 3.5, 4.5] (erreur N |
| odin | C2 | 1 | 1 | 0.5 |  | [exécutée] intrinsèque de LLVM importée par foreign _ et @(link_name = "llvm.x86.avx512.pternlog.d.512"), #con |
| odin | C4 | 0 | 0 | 0 |  | [échec] @(fast_math = {.Allow_Reassoc}) et le jeu complet de drapeaux sont acceptés, mais l'IR de sum_fast por |
| odin | D2 | 1 | 1 | 1 |  | [exécutée] intrinsics.atomic_*_explicit, code produit : .Release = 1 mov et 0 xchg ; .Seq_Cst = 1 xchg ; atomi |
| odin | D3 | 0.5 | 0.5 | 0.5 |  | [exécutée] base:runtime.MAP_CACHE_LINE_SIZE = 64, constante publique de base:runtime, mais propre aux cellules |
| odin | D5 | 1 | 1 | 1 |  | [exécutée] intrinsics.cpu_relax et atomic_thread_fence(.Seq_Cst) : 1 pause et 1 barrière dans spin |
| odin | E1 | 1 | 1 | 1 |  | [exécutée] -build-mode:asm : 3021 lignes d'assembleur, 12 instructions flottantes dans axpy |
| odin | E3 | 1 | 1 | 1 |  | [exécutée] intrinsics.expect(x == 7, false) : disposition [ je retq callq retq ] contre [ jne callq retq ] san |
| odin | E4 | 1 | 1 | 1 |  | [exécutée] intrinsics.prefetch_read_data : 1 prefetcht0 dans pf |
| odin | E5 | 1 | 1 | 1 |  | [exécutée] paramètres #no_alias : 2 attributs noalias dans l'IR de axpy |
| odin | E6 | 1 | 1 | 1 |  | [exécutée] s[i] : 1 appel à runtime.bounds_check_error ; #no_bounds_check : 0 |
| odin | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] procédures polymorphes monomorphisées : gsum(f32) = 4, gsum(f64) = 3.75, 2 fonctions gsum distincte |
| odin | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] [3][4]f32 contigu : &m[1][0] - &m[0][3] = 4 o, size_of = 48 o ; matrix[4, 4]f32 : 64 o ; [échec] [n |
| odin | C5 | 0 | 0 | 0 |  | [recherche] motif C5 dans core et base dev-2026-10:84bc3fc : 4 déclarations publiques (results/grid_audit/sear |
| odin | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans core et base dev-2026-10:84bc3fc : 35 déclarations publiques (results/grid_audit/sea |
| rust | A5 | 1 | 1 | 1 |  | [exécutée] union 0x3f800000 to_bits 0x3f800000 |
| rust | E2 | 1 | 1 | 1 |  | [exécutée] asm! stable : 2 |
| rust | A1 | 1 | 1 | 1 |  | [exécutée] Vec<Part> : pas de 16 o = size_of::<Part>() 16 ; les 4 premiers octets du tampon sont le f32 x en l |
| rust | A2 | 1 | 1 | 1 |  | [exécutée] repr(Rust) réordonne (u8, f64, u8) : 16 o ; repr(C) garde l'ordre : 24 o, offset_of!(ReordC, b) = 8 |
| rust | A4 | 1 | 1 | 1 |  | [exécutée] repr(align(64)) : align_of = 64, Box à 0 mod 64, Vec<Line> : pas 64 o, éléments à 0 mod 64 |
| rust | A7 | 1 | 1 | 1 |  | [exécutée] struct Inl { n: u32, a: [f32; 16] } : 68 o, offset_of!(Inl, a) = 4 (tableau en ligne) |
| rust | A8 | 1 | 1 | 1 |  | [exécutée] u8/i16/f32 : 1/2/4 o ; Vec<u8> de 1000 éléments : 1000 o de capacité, Vec<i16> : 2000 o |
| rust | B1 | 1 | 1 | 1 |  | [exécutée] destruction déterministe sans collecteur : drop(b) fin-portée drop(a) ; 1 fil dans /proc/self/task  |
| rust | B3 | 1 | 1 | 1 |  | [exécutée] [u8; 4096] local à 1379 o d'une autre variable locale, à 46536737999112 o du tas : sur la pile |
| rust | B4 | 1 | 1 | 1 |  | [exécutée] allocateur global compteur : 0 allocation attendue pour fermetures, itérateurs, objets dyn par réfé |
| rust | B5 | 1 | 1 | 1 |  | [exécutée] *mut u32 : *p.add(3) = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| rust | C2 | 1 | 1 | 1 |  | [exécutée] std::arch::x86_64 : is_x86_feature_detected!("avx512f") = true ; _mm512_add_ps -> 56 |
| rust | D1 | 1 | 1 | 1 |  | [exécutée] std::thread::scope : 4 fils, 4 identifiants distincts, somme 7998000 (attendu 7998000) |
| rust | F3 | 1 | 1 | 1 |  | [exécutée] u32::MAX.wrapping_add(1) = 0, i32::MAX.wrapping_add(1) = -2147483648, Wrapping(250u8) + Wrapping(10 |
| rust | D2 | 1 | 1 | 1 |  | [exécutée] Ordering explicite, code produit : store(Release) = 1 mov et 0 xchg/mfence ; store(SeqCst) = 1 xchg |
| rust | D5 | 1 | 1 | 1 |  | [exécutée] std::hint::spin_loop et atomic::fence(SeqCst) : 1 pause et 1 barrière (mfence ou lock or) dans spin |
| rust | C4 | 1 | 1 | 1 |  | [exécutée] f32::algebraic_add (stable depuis 1.98), par opération : somme d'un &[f32] en 7 vaddps sur ymm/zmm  |
| rust | E1 | 1 | 1 | 1 |  | [exécutée] rustc --emit asm : 526 lignes d'assembleur lisibles, dont 10 instructions vectorielles flottantes d |
| rust | E3 | 1 | 1 | 1 |  | [exécutée] std::hint::cold_path (stable depuis 1.95) : 1 poids de branchement dans l'IR de hinted ; 2 métadonn |
| rust | E4 | 1 | 1 | 1 |  | [exécutée] _mm_prefetch::<_MM_HINT_T0> (std::arch, stable) : 1 prefetcht0 dans pf |
| rust | E5 | 1 | 1 | 1 |  | [exécutée] &mut [f32] et &[f32] : 2 attributs noalias sur les paramètres de axpy dans l'IR |
| rust | E6 | 1 | 1 | 1 |  | [exécutée] a[i] : 1 appel à panic_bounds_check ; get_unchecked : 0 |
| rust | E7 | 1 | 1 | 1 |  | [exécutée] const fn fib(60) = 1548008755920 ; gsum::<f32> = 4, gsum::<f64> = 3.75 ; dans l'asm, fib60 = 1 cons |
| rust | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] #[global_allocator] stable (allocateur compteur de la sonde) ; [échec] Vec::new_in sur stable : err |
| rust | C1 | 0.5 | 0.5 | 0.5 |  | [échec] std::simd sur stable : error[E0658]: use of unstable library feature `portable_simd` ; portable_simd r |
| rust | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] [[f32; 4]; 3] contigu : &m[1][0] - &m[0][3] = 4 o, size_of = 48 o ; [échec] tableau 2D de dimension |
| rust | A3 | 0.5 | 0.5 | 0.5 |  | [exécutée] repr(packed) : size_of::<P>() = 5 (probe.rs) ; [recherche] motif A3 dans std/core/alloc 1.99.1 : 2  |
| rust | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans std/core/alloc 1.99.1 : 0 déclaration publique, 0 mention (results/grid_audit/search |
| rust | C5 | 0 | 0 | 0 |  | [recherche] motif C5 dans std/core/alloc 1.99.1 : 2 déclarations publiques (results/grid_audit/search/rust_C5. |
| rust | D3 | 0 | 0 | 0 |  | [recherche] motif D3 dans std/core/alloc 1.99.1 : 0 déclaration publique, 1 mention en commentaire (results/gr |
| rust | D4 | 0 | 0 | 0 |  | [recherche] motif D4 dans std/core/alloc 1.99.1 : 0 déclaration publique ; 4 mentions, toutes dans la document |
| rust | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans std/core/alloc 1.99.1 : 0 déclaration publique ; 38 mentions (locale de texte, « int |
| rust | F4 | 0 | 0 | 0 |  | [recherche] motif F4 dans std/core/alloc 1.99.1 : 0 déclaration publique ; 5 mentions en commentaire (Borrowed |
| swift | A1 | 1 | 1 | 1 |  | [exécutée] [P] contigu : stride 64 o, écart entre éléments 64 o |
| swift | A2 | 1 | 1 | 1 |  | [exécutée] MemoryLayout.offset(of:) a=0 c=8 b=16 : ordre déclaré gardé (docs/ABI/TypeLayout.rst), sans attribu |
| swift | A3 | 0 | 0 | 0 |  | [échec] {UInt8, UInt32} : size 8 o (bourrage imposé) ; ni packed ni champs de bits hors struct C importée ; [r |
| swift | A4 | 0.5 | 0.5 | 0.5 |  | [exécutée] UnsafeMutableRawPointer.allocate(alignment: 64) -> adresse % 64 = 0 ; pas d'alignement de type au-d |
| swift | A5 | 0.5 | 0.5 | 0.5 |  | [exécutée] Float(bitPattern:) 0x3f800000, lecture des octets 0x3f800000, unsafeBitCast entre types de même tai |
| swift | A7 | 1 | 1 | 1 |  | [exécutée] InlineArray<16, Float> dans une struct : stride 64 o |
| swift | A8 | 1 | 1 | 1 |  | [exécutée] UInt8 1 Int16 2 Float16 2 Float 4 |
| swift | B1 | 1 | 1 | 1 |  | [exécutée] ARC : isKnownUniquelyReferenced true ; pas de GC traçant |
| swift | B3 | 1 | 1 | 1 |  | [exécutée] withUnsafeTemporaryAllocation : tampon à 944 o d'une variable locale (pile) ; structs et InlineArra |
| swift | B4 | 0.5 | 0.5 | 0.5 |  | [exécutée] [any Shape] (conteneur de 40 o, tampon en ligne de 24 o) d'une struct de 64 o : boîte 0x5585456ea6c |
| swift | C1 | 1 | 1 | 1 |  | [exécutée] SIMD16<Float>.addProduct (FMA) : 7.0 |
| swift | C5 | 1 | 1 | 1 |  | [exécutée] DispatchQueue.concurrentPerform : 64 itérations sur 4 threads |
| swift | D1 | 1 | 1 | 1 |  | [exécutée] Foundation.Thread et tâches (withTaskGroup, somme 6) |
| swift | D2 | 1 | 1 | 1 |  | [exécutée] Atomic : .relaxed/.acquiring/.releasing/.sequentiallyConsistent -> 5 |
| swift | D3 | 0.5 | 0.5 | 0.5 |  | [exécutée] sysconf(_SC_LEVEL1_DCACHE_LINESIZE) = 64 par le module Glibc livré : requête à l'exécution, ni cons |
| swift | D5 | 0.5 | 0.5 | 0.5 |  | [exécutée] atomicMemoryFence ; pause seulement par @_silgen_name, attribut souligné (_mm_pause importée : symb |
| swift | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] InlineArray<4, InlineArray<8, Double>> : 256 o contigus ; tailles fixées à la compilation seulement |
| swift | F3 | 1 | 1 | 1 |  | [exécutée] UInt8...Int64, &+ &- &* : 4 -2147483648 |
| swift | F4 | 1 | 1 | 1 |  | [exécutée] Data(contentsOf:options: .alwaysMapped) projeté (/proc/self/maps) + withUnsafeBytes/bindMemory : 67 |
| swift | C2 | 0.5 | 0.5 | 0.5 |  | [exécutée] import _Builtin_intrinsics.intel (module Clang non documenté) : 1 vaddps pour _mm512_add_ps ; fonct |
| swift | D4 | 1 | 1 | 0.5 |  | [exécutée] sched_setaffinity du module Glibc livré avec swiftc -Xcc -D_GNU_SOURCE : fil épinglé sur le CPU 1,  |
| swift | E3 | 0.5 | 0.5 | 0.5 |  | [exécutée] _slowPath/_fastPath (publics mais soulignés) : poids de branchement dans l'IR = 1 |
| swift | E4 | 0.5 | 0.5 | 0.5 |  | [exécutée] @_silgen_name("llvm.prefetch.p0"), attribut souligné : 9 prefetchw dans le code produit ; _m_prefet |
| swift | E5 | 0.5 | 0.5 | 0.5 |  | [exécutée] exclusivité des inout (règle du langage, exploitée par l'optimiseur SIL) ; IR de two(_:_:) sans noa |
| swift | B2 | 0.5 | 0.5 | 0.5 |  | [exécutée] UnsafeMutableRawPointer.allocate + arène à la main : deux blocs à 400 o d'écart dans le même tampon |
| swift | B5 | 1 | 1 | 1 |  | [exécutée] UnsafeMutablePointer<UInt32> : (p + 3).pointee = 42 -> buf[3] = 42 ; écriture par décalage d'octets |
| swift | E1 | 1 | 1 | 1 |  | [exécutée] swiftc -emit-assembly : 276 lignes pour le module cg (et -emit-ir pour l'IR, run.sh de base) |
| swift | E6 | 1 | 1 | 1 |  | [exécutée] a[i] sur un Array en -O : 2 ud2 (piège de bornes) ; withUnsafeBufferPointer { $0[i] } : 0 : contrôl |
| swift | E7 | 0.5 | 0.5 | 0.5 |  | [exécutée] gsum<T: AdditiveArithmetic> : 2 spécialisations (Float, Double) produites par l'optimiseur à côté d |
| swift | A6 | 0 | 0 | 0 |  | [recherche] motif A6 dans les interfaces livrées (version 6.4.2) et les symboles de Foundation et Dispatch : 0 |
| swift | C4 | 0 | 0 | 0 |  | [recherche] motif C4 dans les interfaces livrées (version 6.4.2) et les symboles de Foundation et Dispatch : 1 |
| swift | E2 | 0 | 0 | 0 |  | [échec] asm("addq $1, %0") : error: cannot find 'asm' in scope ; [recherche] motif E2 : 0 déclaration, 0 menti |
| swift | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans les interfaces livrées (version 6.4.2) et les symboles de Foundation et Dispatch : 6 |
| zig | A2 | 1 | 1 | 1 |  | [exécutée] @offsetOf(S, "c")=8 |
| zig | A3 | 1 | 1 | 1 |  | [exécutée] packed struct u3/u5/u8 : @bitSizeOf=16 |
| zig | A4 | 1 | 1 | 1 |  | [exécutée] align(64) : @alignOf(L)=64 |
| zig | A5 | 1 | 1 | 1 |  | [exécutée] extern union 0x3f800000 @bitCast 0x3f800000 |
| zig | D3 | 1 | 1 | 1 |  | [exécutée] std.atomic.cache_line=128 |
| zig | F4 | 1 | 1 | 1 |  | [exécutée] std.Io.File.MemoryMap + bytesAsSlice : 0.4390046, projection dans /proc/self/maps : true |
| zig | A1 | 1 | 1 | 1 |  | [exécutée] []Part : pas de 16 o = @sizeOf(Part) 16 ; les 4 premiers octets du tampon sont le f32 x en ligne :  |
| zig | A6 | 1 | 1 | 1 |  | [exécutée] std.MultiArrayList(Part) : items(.x) au pas de 4 o ; items(.y) commence 632 o après items(.x) (un t |
| zig | A7 | 1 | 1 | 1 |  | [exécutée] extern struct { n: u32, a: [16]f32 } : 68 o, @offsetOf(Inl, "a") = 4 (tableau en ligne) |
| zig | A8 | 1 | 1 | 1 |  | [exécutée] u8/i16/f16/f32 : 1/2/2/4 o ; []u8 de 1000 éléments : 1000 o, []i16 : 2000 o |
| zig | B1 | 1 | 1 | 1 |  | [exécutée] aucune collecte : mémoire rendue par free/defer explicites ; 1 fil dans /proc/self/task (aucun fil  |
| zig | B2 | 1 | 1 | 1 |  | [exécutée] std.mem.Allocator passé en argument : FixedBufferAllocator (tampon de pile) -> bloc dans le tampon  |
| zig | B3 | 1 | 1 | 1 |  | [exécutée] [4096]u8 local à 7743 o d'une autre variable locale, à 471642116432 o du tas : sur la pile |
| zig | B4 | 1 | 1 | 1 |  | [exécutée] allocateur compteur : tri, formatage dans un tampon, boucles et tranches -> 0 allocation (255.0 326 |
| zig | B5 | 1 | 1 | 1 |  | [exécutée] [*]u32 : mp[3] = 42 -> buf[3] = 42 ; écriture par décalage d'octets -> buf[4] = 7 |
| zig | C1 | 1 | 1 | 1 |  | [exécutée] @Vector(8, f32) : (a + a)[7] = 16, @reduce(.Add, a) = 36, @shuffle et @select dans le langage |
| zig | D1 | 1 | 1 | 1 |  | [exécutée] std.Thread.spawn : 4 fils, 4 identifiants de fil distincts, somme 7998000 (attendu 7998000) |
| zig | E2 | 1 | 1 | 1 |  | [exécutée] asm volatile (syntaxe AT&T, contraintes de registres) : leaq 1(x) avec x = 41 -> 42 |
| zig | D4 | 1 | 1 | 0.5 |  | [exécutée] std.os.linux.sched_setaffinity (bibliothèque standard ; ½ en v1, liaison propre à Linux) : fil épin |
| zig | F3 | 1 | 1 | 1 |  | [exécutée] maxInt(u32) +% 1 = 0, maxInt(i32) +% 1 = -2147483648, 250 +% 10 (u8) = 4, entiers de toute largeur  |
| zig | D2 | 1 | 1 | 1 |  | [exécutée] @atomicStore/@atomicRmw à ordre explicite, code produit : .release = 2 mov et 0 xchg ; .seq_cst = 1 |
| zig | D5 | 0.5 | 0.5 | 0.5 |  | [exécutée] std.atomic.spinLoopHint : 1 pause dans spin ; [échec] @fence : error: invalid builtin function: '@f |
| zig | C4 | 1 | 1 | 1 |  | [exécutée] @setFloatMode(.optimized) par portée : 9 fadd fast dans l'IR de sum_opt contre 0 dans sum_plain (9  |
| zig | E1 | 1 | 1 | 1 |  | [exécutée] -femit-asm : 5589 lignes d'assembleur, 18 instructions flottantes dans axpy |
| zig | E3 | 1 | 1 | 1 |  | [exécutée] @branchHint(.unlikely) : poids i32 1, i32 2000 dans l'IR ; disposition [ je ret call ret ] contre [ |
| zig | E4 | 1 | 1 | 1 |  | [exécutée] @prefetch : 1 prefetcht0 dans pf |
| zig | E5 | 1 | 1 | 1 |  | [exécutée] paramètres noalias : 2 attributs noalias dans l'IR de axpy |
| zig | E6 | 1 | 1 | 1 |  | [exécutée] en ReleaseSafe, s[i] : 1 appel à la panique outOfBounds ; sous @setRuntimeSafety(false) : 0 (contrô |
| zig | E7 | 1 | 1 | 1 |  | [exécutée] comptime fib(60) = 1548008755920 ; gsum(f32) = 4, gsum(f64) = 3.75 ; dans l'asm, fib60 = 1 constant |
| zig | F1 | 0.5 | 0.5 | 0.5 |  | [exécutée] [3][4]f32 contigu : &m[1][0] - &m[0][3] = 4 o, @sizeOf = 48 o ; [échec] [n][3]f32 avec n connu à l' |
| zig | C2 | 0.5 | 0.5 | 0.5 |  | [recherche] motif C2 dans lib/std 0.17.0 : 68 déclarations publiques (results/grid_audit/search/zig_C2.txt) :  |
| zig | C5 | 0 | 0 | 0 |  | [recherche] motif C5 dans lib/std 0.17.0 : 15 déclarations publiques (results/grid_audit/search/zig_C5.txt) :  |
| zig | F2 | 0 | 0 | 0 |  | [recherche] motif F2 dans lib/std 0.17.0 : 9 déclarations publiques (results/grid_audit/search/zig_F2.txt) : E |
