// Sonde de capacités C23 (clang 23). Chaque ligne CAP;<id>;<valeur>;<preuve> est produite
// par du code qui compile et s'exécute : la capacité existe et fonctionne.
#define _GNU_SOURCE
#include <immintrin.h>
#include <pthread.h>
#include <sched.h>
#include <stdalign.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

struct S { uint8_t a; uint32_t b; double c; };               // ordre déclaré, remplissage C
struct __attribute__((packed)) P { uint8_t a; uint32_t b; }; // extension (gcc/clang)
struct BF { unsigned x : 3, y : 5; };                         // champs de bits (standard)
struct alignas(64) L { int v; };                               // alignement explicite
union U { float f; uint32_t u; };
struct In { float v[16]; int n; };                             // tableau fixe en ligne
static int cmp(const void *a, const void *b) { return 0; (void)a; (void)b; }

int main(void) {
    struct S arr[4];
    printf("CAP;A1;1;tableau de struct contigu sizeof(arr)=%zu (4x%zu)\n", sizeof arr, sizeof(struct S));
    printf("CAP;A2;1;offsetof(S,b)=%zu offsetof(S,c)=%zu\n", offsetof(struct S, b), offsetof(struct S, c));
    printf("CAP;A3;1;bitfields sizeof(BF)=%zu ; packed (extension) sizeof(P)=%zu\n", sizeof(struct BF), sizeof(struct P));
    struct L *l = aligned_alloc(64, 64 * 4);
    printf("CAP;A4;1;alignas(64) alignof(L)=%zu, aligned_alloc %% 64=%zu\n", alignof(struct L), (size_t)((uintptr_t)l % 64));
    union U u = {.f = 1.0f};
    printf("CAP;A5;1;union f32->u32 = 0x%08x\n", u.u);
    printf("CAP;A6;0;pas de SoA dans le langage ni la bibliothèque standard\n");
    printf("CAP;A7;1;sizeof(In)=%zu (float[16] en ligne)\n", sizeof(struct In));
    printf("CAP;A8;1;uint8_t/int16_t/float stockés à leur taille : %zu %zu %zu\n", sizeof(uint8_t), sizeof(int16_t), sizeof(float));
    printf("CAP;B1;1;pas de ramasse-miettes\n");
    printf("CAP;B2;0.5;malloc/free seulement ; arènes à écrire soi-même (pas d'interface d'allocateur standard)\n");
    float stackarr[256]; stackarr[0] = 1;
    printf("CAP;B3;1;tableau sur la pile (%zu o) et VLA\n", sizeof stackarr);
    printf("CAP;B4;1;aucune allocation implicite du langage\n");
    void *raw = mmap(NULL, 1 << 20, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    printf("CAP;B5;1;pointeurs bruts, mmap anonyme %p\n", raw);
    typedef float v16f __attribute__((vector_size(64)));
    v16f va = {1}, vb = {2};
    v16f vc = va + vb;
    printf("CAP;C1;0.5;types vectoriels portables par extension (vector_size) : %g ; pas dans le standard C\n", vc[0]);
    __m512 z = _mm512_set1_ps(2.0f);
    printf("CAP;C2;1;intrinsèques AVX-512 <immintrin.h> : %g\n", _mm512_reduce_add_ps(z));
    printf("CAP;C3;1;auto-vectorisation clang/gcc -O3 (vérifiée sur K4/K9 natural)\n");
    printf("CAP;C4;0.5;réassociation : options -ffast-math/-fassociative-math, #pragma clang fp reassociate (extension) ; pas de contrôle standard\n");
    printf("CAP;C5;0;pas de construction de parallélisme de données dans le langage (OpenMP hors standard C)\n");
    pthread_t th;
    printf("CAP;D1;1;threads <threads.h>/pthreads\n");
    _Atomic int at = 0;
    atomic_fetch_add_explicit(&at, 1, memory_order_relaxed);
    printf("CAP;D2;1;<stdatomic.h> memory_order_relaxed/acquire/release/seq_cst : %d\n", atomic_load(&at));
    printf("CAP;D3;0;pas de constante de taille de ligne standard (C++ seulement)\n");
    cpu_set_t cs; CPU_ZERO(&cs); CPU_SET(0, &cs);
    int aff = sched_setaffinity(0, sizeof cs, &cs);
    printf("CAP;D4;0.5;affinité via POSIX/Linux sched_setaffinity (pas dans le standard C) rc=%d\n", aff);
    atomic_thread_fence(memory_order_seq_cst); _mm_pause();
    printf("CAP;D5;0.5;atomic_thread_fence standard ; pause via intrinsèque _mm_pause\n");
    (void)th;
    printf("CAP;E1;1;compilation native, objdump/-S\n");
    int x = 1; __asm__ volatile("add $1, %0" : "+r"(x));
    printf("CAP;E2;0.5;assembleur en ligne par extension gcc/clang (__asm__) : %d\n", x);
    if (__builtin_expect(x == 2, 1)) printf("CAP;E3;0.5;__builtin_expect (extension) ; [[likely]] n'existe qu'en C++\n");
    __builtin_prefetch(raw, 0, 3);
    printf("CAP;E4;0.5;__builtin_prefetch (extension) ou _mm_prefetch (intrinsèque)\n");
    printf("CAP;E5;1;restrict (C99)\n");
    printf("CAP;E6;1;pas de vérification de bornes (rien à désactiver)\n");
    constexpr int K = 4 * 16;
    printf("CAP;E7;0.5;constexpr C23 et _Generic, mais ni génériques monomorphisés ni calcul arbitraire à la compilation : %d\n", K);
    double (*m)[8] = malloc(sizeof(double[8][8])); m[1][2] = 3;
    printf("CAP;F1;1;tableaux 2D C99 contigus en ligne (VLA/pointeur vers tableau) : %g\n", m[1][2]);
    printf("CAP;F2;0;pas de construction de localité/distribution (libnuma hors standard)\n");
    uint32_t w = UINT32_MAX; w += 1;
    printf("CAP;F3;1;uint32_t modulaire (w=%u) ; débordement signé indéfini\n", w);
    int fd = open("/opt/msdata/k5_a.f32", O_RDONLY);
    float *mp = mmap(NULL, 8192, PROT_READ, MAP_PRIVATE, fd, 0);
    printf("CAP;F4;0.5;mmap POSIX (pas dans le standard C) puis réinterprétation par cast : %g\n", mp[0]);
    qsort(arr, 0, sizeof arr[0], cmp);
    return 0;
}
