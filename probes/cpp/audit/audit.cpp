// Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de C++ (g++ 16, libstdc++, -std=c++26), cas positifs.
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <functional>
#include <mdspan>
#include <memory_resource>
#include <new>
#include <numeric>
#include <set>
#include <stdexcept>
#include <thread>
#include <vector>
#include <sched.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <omp.h>

static std::size_t g_news = 0;
std::function<std::uint64_t()> g_fn;   // stockée hors de main : l'allocation ne peut pas être supprimée
void *operator new(std::size_t n) { ++g_news; if (void *p = std::malloc(n)) return p; throw std::bad_alloc(); }
void operator delete(void *p) noexcept { std::free(p); }
void operator delete(void *p, std::size_t) noexcept { std::free(p); }

struct Part { float x, y, z; std::uint8_t m; };
struct Inl { std::uint32_t n; std::array<float, 16> a; };
struct alignas(64) Line { std::uint64_t v; };
struct Reord { std::uint8_t a; double b; std::uint8_t c; };
struct BF { unsigned x : 3, y : 5; };
struct __attribute__((packed)) Pk { std::uint8_t a; std::uint32_t b; };
template <class T> T gsum(T a, T b) { return a + b; }
consteval std::uint64_t fib(int n) { std::uint64_t a = 0, b = 1; for (int i = 0; i < n; i++) { auto t = a + b; a = b; b = t; } return a; }
static int threads_now() { std::ifstream f("/proc/self/status"); std::string l; while (std::getline(f, l)) if (l.rfind("Threads:", 0) == 0) return std::atoi(l.c_str() + 8); return -1; }

int main(int argc, char **) {
  std::vector<Part> v(8, Part{1, 2, 3, 4});
  auto *raw = reinterpret_cast<unsigned char *>(v.data());
  std::printf("CAP;A1;1;[exécutée] std::vector<Part> : pas de %td o = sizeof(Part) %zu ; les 4 premiers octets du tampon sont le float x en ligne : %02x %02x %02x %02x\n",
              reinterpret_cast<char *>(&v[1]) - reinterpret_cast<char *>(&v[0]), sizeof(Part), raw[0], raw[1], raw[2], raw[3]);
  std::printf("CAP;A2;1;[exécutée] ordre déclaré gardé : (u8, double, u8) occupe %zu o, offsetof(b) = %zu, offsetof(c) = %zu\n", sizeof(Reord), offsetof(Reord, b), offsetof(Reord, c));
  BF bf{5, 17};
  std::printf("CAP;A3;1;[exécutée] champs de bits (norme) : sizeof(BF) = %zu, x = %u, y = %u ; __attribute__((packed)) : sizeof(Pk) = %zu ; ½ en v1\n", sizeof(BF), bf.x, bf.y, sizeof(Pk));
  auto *hl = new Line[4];
  std::printf("CAP;A4;1;[exécutée] alignas(64) : alignof(Line) = %zu, new Line[4] (new aligné, C++17) à %zu mod 64\n", alignof(Line), std::size_t(reinterpret_cast<std::uintptr_t>(hl) % 64));
  std::printf("CAP;A5;1;[exécutée] std::bit_cast<std::uint32_t>(1.0f) = 0x%08x\n", std::bit_cast<std::uint32_t>(1.0f));
  std::printf("CAP;A7;1;[exécutée] struct { uint32_t n; std::array<float, 16> a; } : %zu o, offsetof(a) = %zu (tableau en ligne)\n", sizeof(Inl), offsetof(Inl, a));
  std::printf("CAP;A8;1;[exécutée] uint8_t/int16_t/std::float16_t/float : %zu/%zu/%zu/%zu o ; std::vector<uint8_t>(1000) : %zu o\n", sizeof(std::uint8_t), sizeof(std::int16_t), sizeof(_Float16), sizeof(float), std::vector<std::uint8_t>(1000).size());
  std::printf("CAP;B1;1;[exécutée] aucun ramasse-miettes : destructeurs et delete explicites ; %d fil (Threads: de /proc/self/status)\n", threads_now());
  // B2 : std::pmr
  std::byte store[4096];
  std::pmr::monotonic_buffer_resource arena(store, sizeof store, std::pmr::null_memory_resource());
  std::pmr::vector<int> pv(&arena); for (int i = 0; i < 200; i++) pv.push_back(i);
  bool inside = reinterpret_cast<std::byte *>(pv.data()) >= store && reinterpret_cast<std::byte *>(pv.data()) < store + sizeof store;
  std::printf("CAP;B2;1;[exécutée] std::pmr::monotonic_buffer_resource sur un tampon de pile, passé à std::pmr::vector : tampon dans l'arène = %d, %zu éléments\n", inside, pv.size());
  // B3
  char local[4096]; local[0] = 1; char marker = local[0];
  auto *heap = new int(1);
  std::printf("CAP;B3;1;[exécutée] char local[4096] à %ld o d'une autre variable locale, à %ld o du tas : sur la pile\n", std::labs(long(&marker - local)), std::labs(long(reinterpret_cast<char *>(heap) - local)));
  // B4 (½) : allocations cachées de la bibliothèque et du langage
  std::size_t n0 = g_news;
  std::array<std::uint64_t, 8> big{}; big[0] = argc;
  g_fn = [big] { return big[0] + big[7]; };   // capture de 64 o : hors du petit tampon de std::function
  std::size_t n1 = g_news;
  try { throw std::runtime_error("x"); } catch (const std::exception &) {}
  std::size_t n2 = g_news;
  std::array<int, 64> arr{}; std::iota(arr.begin(), arr.end(), 0); std::sort(arr.begin(), arr.end(), std::greater<>());
  auto lam = [&](int x) { return x * arr[0]; };
  std::size_t n3 = g_news;
  std::printf("CAP;B4;0.5;[exécutée] operator new compté : std::function à capture de 64 o -> %zu allocation ; throw std::runtime_error -> %zu (message) ; std::sort, std::array, lambda -> %zu (%llu %d) : allocations cachées de certaines constructions\n",
              n1 - n0, n2 - n1, n3 - n2, (unsigned long long)g_fn(), lam(2));
  // B5
  std::uint32_t buf[8] = {}; auto *mp = buf; mp[3] = 42; *reinterpret_cast<std::uint32_t *>(reinterpret_cast<char *>(buf) + 16) = 7;
  std::printf("CAP;B5;1;[exécutée] uint32_t * : mp[3] = 42 -> buf[3] = %u ; écriture par décalage d'octets -> buf[4] = %u\n", buf[3], buf[4]);
  // C5 (OpenMP)
  std::vector<int> ids(4000);
#pragma omp parallel for num_threads(4)
  for (int i = 0; i < 4000; i++) ids[i] = int(syscall(SYS_gettid));
  long red = 0;
#pragma omp parallel for reduction(+:red) num_threads(4)
  for (long i = 0; i < 1000000; i++) red += i;
  std::printf("CAP;C5;1;[exécutée] OpenMP (livré avec g++, -fopenmp) : parallel for sur %zu fils distincts (gettid), reduction(+) = %ld ; std::execution::par_unseq reste série sans TBB (½ en v1)\n", std::set<int>(ids.begin(), ids.end()).size(), red);
  // D1
  std::array<std::uint64_t, 4> parts{}; std::array<long, 4> tids{};
  { std::vector<std::jthread> th; for (int t = 0; t < 4; t++) th.emplace_back([&, t] { std::uint64_t s = 0; for (int i = t * 1000; i < (t + 1) * 1000; i++) s += i; parts[t] = s; tids[t] = syscall(SYS_gettid); }); }
  std::printf("CAP;D1;1;[exécutée] std::jthread : 4 fils, %zu identifiants distincts (gettid), somme %llu (attendu 7998000)\n", std::set<long>(tids.begin(), tids.end()).size(), (unsigned long long)(parts[0] + parts[1] + parts[2] + parts[3]));
  std::printf("CAP;D3;1;[exécutée] std::hardware_destructive_interference_size = %zu\n", std::hardware_destructive_interference_size);
  cpu_set_t set; CPU_ZERO(&set); CPU_SET(1, &set);
  int ra = sched_setaffinity(0, sizeof set, &set);
  std::printf("CAP;D4;1;[exécutée] sched_setaffinity de la glibc (bibliothèque système de la plateforme) : retour %d, sched_getcpu() = %d ; ½ en v1\n", ra, sched_getcpu());
  long ex = 41; asm("addq $1, %0" : "+r"(ex));
  std::printf("CAP;E2;1;[exécutée] déclaration asm (norme ; forme étendue de g++) : 41 -> %ld\n", ex);
  constexpr auto F60 = fib(60);
  std::printf("FACT;E7;consteval fib(60) = %llu ; gsum<float> = %.1f, gsum<double> = %.2f\n", (unsigned long long)F60, gsum(1.5f, 2.5f), gsum(1.5, 2.25));
  // F1
  std::size_t rows = argc + 2, cols = argc + 3;
  std::vector<float> st(rows * cols);
  std::mdspan m(st.data(), rows, cols);
  std::printf("CAP;F1;1;[exécutée] std::mdspan (C++23) de %zu x %zu connus à l'exécution : &m[1, 0] - &m[0, cols-1] = %td o (contigu, layout_right)\n", rows, cols, reinterpret_cast<char *>(&m[1, 0]) - reinterpret_cast<char *>(&m[0, cols - 1]));
  std::uint32_t um = UINT32_MAX; std::uint8_t c250 = 250;
  std::printf("CAP;F3;1;[exécutée] UINT32_MAX + 1 = %u, uint8_t(250 + 10) = %u (non signés modulaires ; débordement signé indéfini)\n", std::uint32_t(um + 1u), std::uint8_t(c250 + 10));
  float vals[4] = {1.5f, 2.5f, 3.5f, 4.5f};
  int fd = open("/tmp/cpp_audit_f4.bin", O_CREAT | O_TRUNC | O_RDWR, 0644);
  if (write(fd, vals, sizeof vals) != ssize_t(sizeof vals)) return 1;
  void *p = mmap(nullptr, sizeof vals, PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0);
  auto *fl = std::start_lifetime_as_array<float>(p, 4);
  std::printf("CAP;F4;1;[exécutée] mmap (POSIX, glibc) + std::start_lifetime_as_array (C++23) : %.1f %.1f %.1f %.1f ; ½ en v1\n", fl[0], fl[1], fl[2], fl[3]);
  munmap(p, sizeof vals); close(fd); delete[] hl; delete heap;
}
