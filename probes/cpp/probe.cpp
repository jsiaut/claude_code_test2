// Sonde de capacités C++26 (g++ 16).
#include <atomic>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <immintrin.h>
#include <mdspan>
#include <memory_resource>
#include <new>
#include <simd>
#include <thread>
#include <vector>
#include <array>
#include <sys/mman.h>
#include <fcntl.h>
#include <sched.h>

struct S { std::uint8_t a; std::uint32_t b; double c; };
struct [[gnu::packed]] P { std::uint8_t a; std::uint32_t b; };
struct BF { unsigned x : 3, y : 5; };
struct alignas(64) L { int v; };
struct In { std::array<float, 16> v; int n; };
template <int N> consteval int sq() { return N * N; }
template <class T> T twice(T x) { return x + x; }

int main() {
    std::vector<S> v(4);
    std::printf("CAP;A1;1;std::vector<S> de valeurs contiguës : &v[1]-&v[0]=%td o\n", (char *)&v[1] - (char *)&v[0]);
    std::printf("CAP;A2;1;offsetof(S,c)=%zu (types à disposition standard)\n", offsetof(S, c));
    std::printf("CAP;A3;1;champs de bits sizeof(BF)=%zu ; packed par attribut gnu sizeof(P)=%zu\n", sizeof(BF), sizeof(P));
    auto *l = new L[4];
    std::printf("CAP;A4;1;alignas(64) + new aligné C++17 : %zu\n", (std::size_t)((std::uintptr_t)l % 64));
    float f = 1.0f;
    std::printf("CAP;A5;1;std::bit_cast<uint32_t>(1.0f)=0x%08x ; unions\n", std::bit_cast<std::uint32_t>(f));
    std::printf("CAP;A6;0;pas de SoA standard (la réflexion C++26 permettrait de l'écrire)\n");
    std::printf("CAP;A7;1;std::array en ligne sizeof(In)=%zu\n", sizeof(In));
    std::printf("CAP;A8;1;types étroits\n");
    std::printf("CAP;B1;1;pas de GC\n");
    std::byte buf[4096];
    std::pmr::monotonic_buffer_resource mono(buf, sizeof buf);
    std::pmr::vector<int> pv(&mono); pv.push_back(1);
    std::printf("CAP;B2;1;std::pmr (monotonic_buffer_resource, pools) + concept Allocator\n");
    std::printf("CAP;B3;1;objets et std::array sur la pile\n");
    std::printf("CAP;B4;0.5;pas d'allocation cachée par le langage, mais std::function, exceptions et coroutines peuvent allouer\n");
    std::printf("CAP;B5;1;pointeurs bruts\n");
    namespace ss = std::simd;
    ss::vec<float, 16> a = 2.0f;
    std::printf("CAP;C1;1;std::simd (C++26) : reduce=%g\n", ss::reduce(a));
    __m512 z = _mm512_set1_ps(1.0f);
    std::printf("CAP;C2;1;intrinsèques <immintrin.h> : %g\n", _mm512_reduce_add_ps(z));
    std::printf("CAP;C3;1;auto-vectorisation -O3\n");
    std::printf("CAP;C4;0.5;réassociation : std::simd::reduce / transform_reduce l'autorisent ; sinon options -ffast-math\n");
    std::printf("CAP;C5;1;algorithmes parallèles std::execution::par_unseq (C++17)\n");
    std::jthread t([] {});
    std::printf("CAP;D1;1;std::thread/jthread\n");
    std::atomic<int> at{0}; at.fetch_add(1, std::memory_order_relaxed);
    std::printf("CAP;D2;1;std::memory_order relaxed/acquire/release/seq_cst\n");
    std::printf("CAP;D3;1;std::hardware_destructive_interference_size=%zu\n", std::hardware_destructive_interference_size);
    std::printf("CAP;D4;0;pas d'affinité dans la bibliothèque standard (sched_setaffinity POSIX)\n");
    std::atomic_thread_fence(std::memory_order_seq_cst);
    std::printf("CAP;D5;0.5;std::atomic_thread_fence, std::barrier ; pause seulement par intrinsèque\n");
    std::printf("CAP;E1;1;natif\n");
    int x = 1; asm volatile("add $1, %0" : "+r"(x));
    std::printf("CAP;E2;0.5;asm (conditionnellement supporté par la norme, implémenté par gcc/clang) : %d\n", x);
    if (x == 2) [[likely]] std::printf("CAP;E3;1;[[likely]]/[[unlikely]] (C++20)\n");
    __builtin_prefetch(&x);
    std::printf("CAP;E4;0.5;__builtin_prefetch (extension)\n");
    std::printf("CAP;E5;0.5;__restrict__ (extension, pas dans la norme C++)\n");
    std::printf("CAP;E6;1;pas de vérification de bornes par défaut ; .at() les ajoute\n");
    std::printf("CAP;E7;1;templates monomorphisés + consteval : %d %d\n", sq<7>(), twice(21));
    std::vector<double> d(64);
    std::mdspan m(d.data(), 8, 8); m[1, 2] = 3;
    std::printf("CAP;F1;1;std::mdspan (C++23), dispositions layout_right/left/stride : %g\n", d[10]);
    std::printf("CAP;F2;0;pas de localité/distribution\n");
    std::uint32_t w = UINT32_MAX; w += 1;
    std::printf("CAP;F3;1;entiers non signés modulaires (w=%u)\n", w);
    int fd = open("/opt/msdata/k5_a.f32", O_RDONLY);
    auto *mp = (float *)mmap(nullptr, 8192, PROT_READ, MAP_PRIVATE, fd, 0);
    std::printf("CAP;F4;0.5;mmap POSIX + std::start_lifetime_as (C++23) : %g\n", mp[0]);
}
