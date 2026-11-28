// v7 (docs/V7.md ; olap/SPEC.md) : le banc OLAP en C++. Même architecture que la référence (olap/c/olap.c), écrite
// avec les moyens du langage : gabarits pour les routines par largeur et les tuples des partitions, lambdas pour les
// tâches des fils, tables calculées à la compilation. Niveau portable : aucune vectorisation explicite, aucune
// construction propre à une famille de processeurs. Le niveau spécialisé (-DSPECIAL) remplace des primitives par
// celles de olap_special.hpp.
//
// Usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <charconv>
#include <chrono>
#include <concepts>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

constexpr uint32_t PBITS = 10;                // bits de partition
constexpr uint32_t VEC = 2048;                // lignes d'un vecteur
constexpr uint32_t CHUNK = 16384;             // octets utiles d'un morceau de tampon de partition
constexpr uint32_t BLOCK = 65536;             // lignes d'un bloc : un morceau
constexpr uint32_t NPART = 1u << PBITS;       // partitions des grandes tables
constexpr int MAXT = 64;                      // fils au plus
constexpr size_t ARENA_BLOCK = size_t{32} << 20;  // octets d'un bloc d'arène
constexpr size_t HUGE_PAGE = size_t{1} << 21;     // octets d'une page large
constexpr uint64_t K1 = 0x9E3779B97F4A7C15ull, K2 = 0xC2B2AE3D27D4EB4Full;

[[noreturn]] static void die(const char *msg) {
  std::fprintf(stderr, "olap : %s\n", msg);
  std::exit(2);
}

// ------------------------------------------------------------------------------------------------ mémoire, arènes
// Toute la mémoire du programme (colonnes chargées, arènes, vecteurs de travail) vient du système par zones alignées
// sur 2 Mio et signalées comme pages larges.
static void *huge_alloc(size_t n) {
  n = (n + HUGE_PAGE - 1) & ~(HUGE_PAGE - 1);
  void *p;
  if (posix_memalign(&p, HUGE_PAGE, n)) die("mémoire");
  madvise(p, n, MADV_HUGEPAGE);
  return p;
}

// Une arène par fil : allocation par déplacement d'un pointeur, remise à zéro à chaque exécution ; la mémoire est
// gardée d'une répétition à l'autre.
struct Arena {
  struct Block { Block *next; size_t cap, used; char pad[40]; };  // 64 octets
  Block *first = nullptr, *cur = nullptr;

  void *alloc(size_t n) {
    n = (n + 63) & ~size_t{63};
    for (;;) {
      Block *b = cur;
      if (b && b->used + n <= b->cap) { void *p = reinterpret_cast<char *>(b + 1) + b->used; b->used += n; return p; }
      if (b && b->next && b->next->cap >= n) { cur = b->next; cur->used = 0; continue; }
      const size_t cap = std::max(n, ARENA_BLOCK - sizeof(Block));
      Block *nb = static_cast<Block *>(huge_alloc(sizeof(Block) + cap));
      nb->cap = cap; nb->used = 0;
      if (b) { nb->next = b->next; b->next = nb; } else { nb->next = nullptr; first = nb; }
      cur = nb;
    }
  }
  template <class T> T *array(size_t n) { return static_cast<T *>(alloc(n * sizeof(T))); }
  void reset() { cur = first; if (cur) cur->used = 0; }
};

// ------------------------------------------------------------------------------------------------ fils persistants
// Les fils sont créés une fois et attendent, bloqués, entre deux phases. run(f) exécute f(tid) sur tous les fils (le
// fil principal est le fil 0) et attend la fin de tous.
class Pool {
  int n_ = 1;
  std::mutex mu_;
  std::condition_variable work_, done_;
  void (*fn_)(void *, int) = nullptr;
  void *ctx_ = nullptr;
  uint64_t gen_ = 0;
  int pending_ = 0;

  void worker(int tid) {
    uint64_t seen = 0;
    for (;;) {
      void (*fn)(void *, int);
      void *ctx;
      {
        std::unique_lock lk(mu_);
        work_.wait(lk, [&] { return gen_ != seen; });
        seen = gen_; fn = fn_; ctx = ctx_;
      }
      fn(ctx, tid);
      std::lock_guard lk(mu_);
      if (--pending_ == 0) done_.notify_one();
    }
  }

 public:
  void start(int n) {
    n_ = n;
    for (int i = 1; i < n; i++) std::thread(&Pool::worker, this, i).detach();
  }
  template <class F> void run(F &&f) {
    if (n_ > 1) {
      std::lock_guard lk(mu_);
      fn_ = [](void *c, int tid) { (*static_cast<std::remove_reference_t<F> *>(c))(tid); };
      ctx_ = &f; pending_ = n_ - 1; gen_++;
      work_.notify_all();
    }
    f(0);
    if (n_ > 1) {
      std::unique_lock lk(mu_);
      done_.wait(lk, [&] { return pending_ == 0; });
    }
  }
};
static Pool &pool = *new Pool;  // jamais détruite : ses fils l'attendent jusqu'à la fin du processus

// Compteur de morceaux partagé : la seule opération atomique.
struct Counter {
  std::atomic<uint64_t> next{0};
  uint64_t n = 0;
  void set(uint64_t count) { next.store(0); n = count; }
  int64_t take() {
    const uint64_t i = next.fetch_add(1, std::memory_order_relaxed);
    return i < n ? static_cast<int64_t>(i) : -1;
  }
};

// ------------------------------------------------------------------------------------------------ colonnes
struct Entry { int64_t min, max; uint64_t data_off, aux_off; uint32_t width, count; };
static inline std::string_view sv(const uint8_t *p, size_t n) { return {reinterpret_cast<const char *>(p), n}; }

struct Col {
  const uint8_t *base = nullptr;
  uint64_t size = 0;
  uint32_t kind = 0, vtype = 0;
  uint64_t nrows = 0, nblocks = 0, aux_count = 0;
  const Entry *dir = nullptr;
  const uint64_t *data = nullptr;
  const uint8_t *aux = nullptr;

  const uint64_t *words(uint64_t b) const { return data + dir[b].data_off / 8; }
  // Entrée d'un dictionnaire : ses octets suivent la table des positions.
  std::string_view dict(uint32_t code) const {
    uint32_t pos[2];
    std::memcpy(pos, aux + 4 * uint64_t{code}, 8);
    return sv(aux + 4 * (aux_count + 1) + pos[0], pos[1] - pos[0]);
  }
};

static const char *DATA;  // répertoire des données

static Col col_open(const char *table, const char *name) {
  const std::string path = std::string(DATA) + "/" + table + "/" + name + ".msc";
  const int fd = open(path.c_str(), O_RDONLY);
  if (fd < 0) { std::perror(path.c_str()); std::exit(2); }
  struct stat st;
  fstat(fd, &st);
  Col c;
  c.size = static_cast<uint64_t>(st.st_size);
  uint8_t *base = static_cast<uint8_t *>(huge_alloc(c.size));  // la colonne est lue en entier, en pages larges
  for (uint64_t off = 0; off < c.size;) {
    const ssize_t r = pread(fd, base + off, c.size - off, static_cast<off_t>(off));
    if (r <= 0) die("lecture");
    off += static_cast<uint64_t>(r);
  }
  close(fd);
  c.base = base;
  if (std::memcmp(base, "MSC1", 4)) die("format");
  uint32_t h32[3];
  uint64_t h64[6];
  std::memcpy(h32, base + 4, 12);
  std::memcpy(h64, base + 16, 48);
  c.kind = h32[0]; c.vtype = h32[1];
  if (h32[2] != BLOCK) die("taille de bloc");
  c.nrows = h64[0]; c.nblocks = h64[1];
  c.dir = reinterpret_cast<const Entry *>(base + h64[2]);
  c.data = reinterpret_cast<const uint64_t *>(base + h64[3]);
  c.aux = base + h64[4];
  c.aux_count = h64[5];
  return c;
}

// ------------------------------------------------------------------------------------------------ décodage
// Une routine par largeur, instanciée par un gabarit : un groupe de 64 valeurs occupe W mots ; les positions sont des
// constantes. Deux formes : quand W divise 64, chaque valeur tient dans un mot ; sinon, deux mots voisins sont
// toujours combinés, sans test, et la boucle des 64 valeurs est déroulée.
template <unsigned W>
static void unpack_w(const uint64_t *__restrict in, int32_t *__restrict out, uint32_t n, uint32_t base) {
  if constexpr (64 % W == 0) {
    for (uint32_t g = 0; g < n; g += 64, in += W, out += 64)
      for (uint32_t j = 0; j < 64; j++) {
        const uint32_t bit = j * W;
        out[j] = static_cast<int32_t>(static_cast<uint32_t>((in[bit >> 6] >> (bit & 63)) & ((1ull << W) - 1)) + base);
      }
  } else {
    for (uint32_t g = 0; g < n; g += 64, in += W, out += 64) {
#pragma GCC unroll 64
      for (uint32_t j = 0; j < 64; j++) {
        const uint32_t bit = j * W, idx = bit >> 6, sh = bit & 63;
        const uint64_t v = (in[idx] >> sh) | (in[idx + 1] << 1 << (63 - sh));
        out[j] = static_cast<int32_t>(static_cast<uint32_t>(v & ((1ull << W) - 1)) + base);
      }
    }
  }
}
using UnpackFn = void (*)(const uint64_t *__restrict, int32_t *__restrict, uint32_t, uint32_t);
template <size_t... I> constexpr std::array<UnpackFn, 33> unpack_table(std::index_sequence<I...>) {
  return {nullptr, &unpack_w<I + 1>...};
}
constexpr std::array<UnpackFn, 33> UNPACK_FN = unpack_table(std::make_index_sequence<32>{});

// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 64.
[[maybe_unused]] static inline void unpack_portable(const Col &c, uint64_t b, uint32_t start, uint32_t n, int32_t *out) {
  const Entry &e = c.dir[b];
  if (e.width == 0) {
    std::fill_n(out, n, static_cast<int32_t>(e.min));
    return;
  }
  UNPACK_FN[e.width](c.words(b) + uint64_t{start / 64} * e.width, out, n, static_cast<uint32_t>(e.min));
}
// Décode les valeurs du bloc b aux positions pos (lignes dans le bloc), dans l'ordre : out[i] est celle de pos[i].
static inline void unpack_sel(const Col &c, uint64_t b, const int32_t *pos, uint32_t n, int32_t *out) {
  const Entry &e = c.dir[b];
  const uint64_t *in = c.words(b);
  const uint32_t w = e.width, base = static_cast<uint32_t>(e.min);
  if (w == 0) {
    std::fill_n(out, n, static_cast<int32_t>(base));
    return;
  }
  const uint64_t mask = (1ull << w) - 1;
  for (uint32_t i = 0; i < n; i++) {
    const uint64_t bit = static_cast<uint64_t>(pos[i]) * w, idx = bit >> 6;
    const uint32_t sh = bit & 63;
    const uint64_t v = (in[idx] >> sh) | (in[idx + 1] << 1 << (63 - sh));
    out[i] = static_cast<int32_t>(static_cast<uint32_t>(v & mask) + base);
  }
}

// ------------------------------------------------------------------------------------------------ hachage
static inline uint64_t load64(const uint8_t *p) { uint64_t v; std::memcpy(&v, p, 8); return v; }
static inline uint64_t hash64(uint64_t k) { k *= K1; return k ^ (k >> 32); }
// Octets : deux voies de mots de 64 bits ; le dernier mot, incomplet, est masqué (8 octets lisibles après la fin).
static inline uint64_t hash_bytes(const uint8_t *p, uint32_t n) {
  uint64_t h1 = K1 ^ n, h2 = K2;
  while (n >= 16) {
    h1 = (std::rotl(h1, 5) ^ load64(p)) * K1;
    h2 = (std::rotl(h2, 5) ^ load64(p + 8)) * K2;
    p += 16; n -= 16;
  }
  if (n >= 8) { h1 = (std::rotl(h1, 5) ^ load64(p)) * K1; p += 8; n -= 8; }
  if (n) h2 = (std::rotl(h2, 5) ^ (load64(p) & ((1ull << (8 * n)) - 1))) * K2;
  uint64_t h = (h1 ^ std::rotl(h2, 32)) * K1;
  h ^= h >> 32;
  return h ? h : 1;  // 0 marque une case vide
}
static inline uint32_t part_of(uint64_t h) { return static_cast<uint32_t>(h >> (64 - PBITS)); }

// ------------------------------------------------------------------------------------------------ table de hachage
// Adressage ouvert, sondage linéaire, capacité en puissance de deux, clé et valeur dans la même case ; doublement
// quand la table est à moitié pleine. Clés entières positives ou nulles ; -1 marque une case vide.
static constexpr uint64_t pow2_for(uint64_t n) {  // capacité pour n clés : au moins le double, 16 au moins
  uint64_t cap = 16;
  while (cap < 2 * n) cap *= 2;
  return cap;
}
// Capacité de départ d'une table d'agrégation qui recevra n tuples ; elle double ensuite à la demande.
static constexpr uint64_t pow2_start(uint64_t n) { return pow2_for(n / 8); }

struct Cell { int64_t key, val; };
struct Map {
  Cell *cells;
  uint64_t mask, count;
  Arena *arena;

  void init(Arena &a, uint64_t cap) {
    arena = &a; mask = cap - 1; count = 0;
    cells = a.array<Cell>(cap);
    std::memset(cells, 0xFF, cap * sizeof(Cell));
  }
  Cell *find(int64_t key, uint64_t h) const {  // h : hash64 de la clé
    for (uint64_t i = h & mask;; i = (i + 1) & mask) {
      Cell *c = &cells[i];
      if (c->key == key) return c;
      if (c->key == -1) return nullptr;
    }
  }
  Cell *find(int64_t key) const { return find(key, hash64(static_cast<uint64_t>(key))); }
  void grow() {
    const Map old = *this;
    init(*old.arena, 2 * (old.mask + 1));
    for (uint64_t j = 0; j <= old.mask; j++)
      if (old.cells[j].key != -1) {
        uint64_t i = hash64(static_cast<uint64_t>(old.cells[j].key)) & mask;
        while (cells[i].key != -1) i = (i + 1) & mask;
        cells[i] = old.cells[j];
      }
    count = old.count;
  }
  // Rend la case de la clé, créée avec la valeur 0 si elle manquait (fresh le dit).
  Cell &upsert(int64_t key, bool &fresh) {
    if ((count + 1) * 2 > mask + 1) grow();
    for (uint64_t i = hash64(static_cast<uint64_t>(key)) & mask;; i = (i + 1) & mask) {
      Cell &c = cells[i];
      if (c.key == key) { fresh = false; return c; }
      if (c.key == -1) { c.key = key; c.val = 0; count++; fresh = true; return c; }
    }
  }
  Cell &upsert(int64_t key) { bool fresh; return upsert(key, fresh); }
  template <class F> void each(F &&f) const {
    for (uint64_t j = 0; j <= mask; j++)
      if (cells[j].key != -1) f(cells[j]);
  }
};

// Filtre de Bloom par blocs, devant les sondes de semi-jointure : 16 bits par clé, deux bits dans un même mot de
// 64 bits. Un refus est sûr ; une acceptation se confirme dans la table.
struct Bloom {
  uint64_t *bits;
  uint64_t mask;
  void init(Arena &a, uint64_t nkeys) {
    uint64_t words = 64;
    while (words * 4 < nkeys) words *= 2;
    bits = a.array<uint64_t>(words);
    std::memset(bits, 0, words * 8);
    mask = words - 1;
  }
  static uint64_t two(uint64_t h) { return 1ull << (h & 63) | 1ull << ((h >> 6) & 63); }
  void add(uint64_t h) { bits[(h >> 12) & mask] |= two(h); }
  bool test(uint64_t h) const { const uint64_t m = two(h); return (bits[(h >> 12) & mask] & m) == m; }
};

// Même table pour des clés faites d'un entier et d'une chaîne : la case garde le hachage, l'entier, la position
// et la longueur de la chaîne, et un compte. Hachage nul : case vide.
struct SCell { uint64_t hash; int64_t ikey; uint64_t ref; uint32_t len, count; };
struct SMap {
  SCell *cells;
  uint64_t mask, n;
  Arena *arena;
  const uint8_t *bytes;

  void init(Arena &a, uint64_t cap, const uint8_t *b) {
    arena = &a; mask = cap - 1; n = 0; bytes = b;
    cells = a.array<SCell>(cap);
    std::memset(cells, 0, cap * sizeof(SCell));
  }
  void grow() {
    const SMap old = *this;
    init(*old.arena, 2 * (old.mask + 1), old.bytes);
    for (uint64_t j = 0; j <= old.mask; j++)
      if (old.cells[j].hash) {
        uint64_t i = old.cells[j].hash & mask;
        while (cells[i].hash) i = (i + 1) & mask;
        cells[i] = old.cells[j];
      }
    n = old.n;
  }
  void add(uint64_t hash, int64_t ikey, uint64_t ref, uint32_t len) {
    if ((n + 1) * 2 > mask + 1) grow();
    for (uint64_t i = hash & mask;; i = (i + 1) & mask) {
      SCell &c = cells[i];
      if (c.hash == hash && c.ikey == ikey && c.len == len && !std::memcmp(bytes + c.ref, bytes + ref, len)) {
        c.count++;
        return;
      }
      if (!c.hash) { c = {hash, ikey, ref, len, 1}; n++; return; }
    }
  }
};

// ------------------------------------------------------------------------------------------------ deux niveaux
// Les primitives qui suivent ont une forme portable, ici, et une forme spécialisée, dans olap_special.hpp.
struct Agg1 { int64_t qty, base, disc_price, charge, disc, count, pad[2]; };  // un groupe de T1
struct PChunk { PChunk *next; uint32_t used, pad; char fill[48]; };           // 64 octets, puis CHUNK octets de tuples

#ifdef SPECIAL
#include "olap_special.hpp"
#else
static inline void unpack(const Col &c, uint64_t b, uint32_t start, uint32_t n, int32_t *out) {
  unpack_portable(c, b, start, n, out);
}

// Sélection. Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises ; sans branchement.
static inline uint32_t sel_between(const int32_t *v, uint32_t n, int32_t lo, int32_t hi, uint32_t base, int32_t *pos) {
  uint32_t k = 0;
  for (uint32_t i = 0; i < n; i++) {
    pos[k] = static_cast<int32_t>(base + i);
    k += (v[i] >= lo) & (v[i] <= hi);
  }
  return k;
}
// Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
static inline uint32_t keep_between(const int32_t *v, const int32_t *pos_in, const int32_t *pay_in, uint32_t n,
                                    int32_t lo, int32_t hi, int32_t *pos_out, int32_t *pay_out) {
  uint32_t k = 0;
  for (uint32_t i = 0; i < n; i++) {
    pos_out[k] = pos_in[i]; pay_out[k] = pay_in[i];
    k += (v[i] >= lo) & (v[i] <= hi);
  }
  return k;
}

// Agrégation de T1 : un vecteur de n lignes dans le tableau des six groupes ; ship non nul : seules comptent les
// lignes dont la date ne dépasse pas cut (vecteur de sélection dans sel).
static inline void t1_aggregate(Agg1 *agg, const int32_t *grp, const int32_t *qty, const int32_t *ext, const int32_t *disc,
                                const int64_t *dp, const int64_t *ch, const int32_t *ship, int32_t cut, uint32_t n,
                                int32_t *sel) {
  const auto add = [&](uint32_t i) {
    Agg1 &g = agg[grp[i]];
    g.qty += qty[i]; g.base += ext[i]; g.disc_price += dp[i]; g.charge += ch[i]; g.disc += disc[i]; g.count++;
  };
  if (!ship) {
    for (uint32_t i = 0; i < n; i++) add(i);
  } else {
    const uint32_t k = sel_between(ship, n, INT32_MIN, cut, 0, sel);
    for (uint32_t j = 0; j < k; j++) add(static_cast<uint32_t>(sel[j]));
  }
}

// Partitions. Tampons d'un fil : pour chaque partition, une liste de morceaux de CHUNK octets pris dans son arène.
struct Parts {
  uint8_t *cur[NPART], *end[NPART];
  PChunk *head[NPART], *tail[NPART];
  uint32_t tsize;
  Arena *arena;

  void init(Arena &a, uint32_t ts) {
    std::memset(static_cast<void *>(this), 0, sizeof *this);
    tsize = ts; arena = &a;
  }
  uint8_t *chunk(uint32_t k) {
    PChunk *c = static_cast<PChunk *>(arena->alloc(sizeof(PChunk) + CHUNK));
    c->next = nullptr; c->used = 0;
    if (tail[k]) { tail[k]->used = static_cast<uint32_t>(cur[k] - reinterpret_cast<uint8_t *>(tail[k] + 1)); tail[k]->next = c; }
    else head[k] = c;
    tail[k] = c;
    cur[k] = reinterpret_cast<uint8_t *>(c + 1);
    end[k] = cur[k] + CHUNK / tsize * tsize;
    return cur[k];
  }
  // Place du prochain tuple (de type T, de taille tsize) de la partition k.
  template <class T> T *push(uint32_t k) {
    uint8_t *t = cur[k];
    if (t == end[k]) t = chunk(k);
    cur[k] = t + sizeof(T);
    return reinterpret_cast<T *>(t);
  }
  void close() {
    for (uint32_t k = 0; k < NPART; k++)
      if (tail[k]) tail[k]->used = static_cast<uint32_t>(cur[k] - reinterpret_cast<uint8_t *>(tail[k] + 1));
  }
};
#endif

static uint64_t parts_count(const Parts *p, int nt, uint32_t k) {
  uint64_t n = 0;
  for (int t = 0; t < nt; t++)
    for (const PChunk *c = p[t].head[k]; c; c = c->next) n += c->used / p[t].tsize;
  return n;
}
// Parcours des tuples (de type T) de la partition k dans les tampons de tous les fils : f(tuple, fin du morceau en
// cours) ; le niveau spécialisé lit la fin pour précharger les tuples à venir.
template <class T, class F> static inline void parts_each(const Parts *p, int nt, uint32_t k, F &&f) {
  for (int t = 0; t < nt; t++)
    for (const PChunk *c = p[t].head[k]; c; c = c->next) {
      const T *it = reinterpret_cast<const T *>(c + 1);
      const T *const end = reinterpret_cast<const T *>(reinterpret_cast<const uint8_t *>(c + 1) + c->used);
      for (; it < end; it++) f(it, end);
    }
}

// ------------------------------------------------------------------------------------------------ état des fils
struct Scratch {
  int32_t a[VEC], b[VEC], c[VEC], d[VEC], e[VEC], f[VEC], g[VEC], sel[VEC], sel2[VEC], pos[VEC];
  int64_t x[VEC], y[VEC];
  uint64_t h[VEC];
  int32_t len[BLOCK], rows[BLOCK];
};
static int NT;
static Arena arena[MAXT];
static Scratch *scratch[MAXT];
static Parts parts[MAXT], parts2[MAXT];

// Liste d'entiers de 64 bits dans une arène.
struct List {
  int64_t *v;
  uint64_t n, cap;
  Arena *a;
  void init(Arena &ar) { v = nullptr; n = cap = 0; a = &ar; }
  void push(int64_t x) {
    if (n == cap) {
      const uint64_t c = cap ? 2 * cap : 1024;
      int64_t *nv = a->array<int64_t>(c);
      if (n) std::memcpy(nv, v, n * 8);
      v = nv; cap = c;
    }
    v[n++] = x;
  }
};
// Blocs d'une colonne vecteur par vecteur : f(début dans le bloc, lignes du vecteur).
template <class F> static inline void each_vector(uint32_t count, F &&f) {
  for (uint32_t st = 0; st < count; st += VEC) f(st, std::min(count - st, VEC));
}

// ------------------------------------------------------------------------------------------------ résultat
static std::string res;
static void emit(std::string_view s) { res.append(s); }
template <std::integral T> static void emit(T v) {
  char buf[24];
  res.append(buf, std::to_chars(buf, buf + sizeof buf, v).ptr);
}
template <class A, class B, class... R> static void emit(const A &a, const B &b, const R &...r) {
  emit(a); emit(b); (emit(r), ...);
}
static uint64_t fnv1a(std::string_view s) {
  uint64_t h = 0xCBF29CE484222325ull;
  for (const char c : s) { h ^= static_cast<uint8_t>(c); h *= 0x100000001B3ull; }
  return h;
}

// ------------------------------------------------------------------------------------------------ dates
static constexpr int32_t days_from_civil(int y, int m, int d) {  // jours depuis le 1er janvier 1970
  y -= m <= 2;
  const int era = (y >= 0 ? y : y - 399) / 400;
  const unsigned yoe = static_cast<unsigned>(y - era * 400);
  const unsigned doy = (153u * static_cast<unsigned>(m + (m > 2 ? -3 : 9)) + 2) / 5 + static_cast<unsigned>(d) - 1;
  const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + static_cast<int>(doe) - 719468;
}
// Premier jour de chaque année à partir de 1970 : table calculée à la compilation.
constexpr std::array<int32_t, 200> YEAR_START = [] {
  std::array<int32_t, 200> t{};
  for (int y = 0; y < 200; y++) t[y] = days_from_civil(1970 + y, 1, 1);
  return t;
}();
static inline int32_t year_of(int32_t days) {
  int y = days / 366;
  while (YEAR_START[y + 1] <= days) y++;
  return 1970 + y;
}

// ------------------------------------------------------------------------------------------------ sous-chaînes
// Lignes d'un bloc de chaînes qui contiennent l'aiguille (2 octets au moins) : les octets du bloc sont parcourus
// d'un trait, par mots de 8 octets ; un mot est candidat si, à une même position, il porte le premier octet de
// l'aiguille et le mot décalé de sa longueur moins un porte le dernier. Une occurrence compte si elle tient dans
// une ligne, et une ligne compte une fois.
constexpr uint64_t ONES = 0x0101010101010101ull, HIGHS = 0x8080808080808080ull;
static inline uint64_t zero_bytes(uint64_t x) {  // bit de poids fort de chaque octet nul de x, exactement
  return ~(((x & ~HIGHS) + ~HIGHS) | x) & HIGHS;
}
static uint32_t search_block(const uint8_t *buf, uint64_t nbytes, const int32_t *len, std::string_view needle_sv,
                             int32_t *rows) {
  const uint8_t *needle = reinterpret_cast<const uint8_t *>(needle_sv.data());
  const uint32_t m = static_cast<uint32_t>(needle_sv.size());
  uint32_t r = 0, k = 0;
  uint64_t row_end = nbytes ? static_cast<uint64_t>(len[0]) : 0;
  const uint64_t first = ONES * needle[0], last = ONES * needle[m - 1];
  const uint64_t stop = nbytes >= m ? nbytes - m + 1 : 0;  // positions de départ possibles : [0, stop)
  for (uint64_t i = 0; i < stop;) {
    uint64_t cand, next;
    int shift = 3;  // un bit candidat par octet du mot : rang du bit / 8
#ifdef SPECIAL
    if (i + SEARCH_STEP + m - 1 <= nbytes) {  // 64 positions d'un coup, un bit candidat par position
      cand = search_candidates(buf + i, m, needle[0], needle[m - 1]);
      if (!cand) { i += SEARCH_STEP; continue; }
      next = i + SEARCH_STEP; shift = 0;
    } else
#endif
    if (i + 8 <= stop) {  // les deux mots sont dans le bloc
      cand = zero_bytes((load64(buf + i) ^ first) | (load64(buf + i + m - 1) ^ last));
      if (!cand) { i += 8; continue; }
      next = i + 8;
    } else {
      cand = 0;
      for (uint64_t j = i; j < stop; j++)
        if (buf[j] == needle[0] && buf[j + m - 1] == needle[m - 1]) cand |= 0x80ull << (8 * (j - i));
      next = i + 8;
    }
    for (; cand; cand &= cand - 1) {
      const uint64_t at = i + (static_cast<uint64_t>(std::countr_zero(cand)) >> shift);
      if (std::memcmp(buf + at + 1, needle + 1, m - 2)) continue;
      while (row_end <= at) row_end += static_cast<uint64_t>(len[++r]);
      if (at + m <= row_end) { rows[k++] = static_cast<int32_t>(r); next = row_end; break; }  // la suite de la ligne est sautée
    }
    i = next;
  }
  return k;
}
// Longueurs d'un bloc de chaînes (dans len) ; rend le nombre de ses octets.
static uint64_t block_lengths(const Col &c, uint64_t b, int32_t *len) {
  const uint32_t n = c.dir[b].count;
  unpack(c, b, 0, n, len);
  uint64_t total = 0;
  for (uint32_t i = 0; i < n; i++) total += static_cast<uint64_t>(len[i]);
  return total;
}

// ------------------------------------------------------------------------------------------------ dix premiers
struct Top { uint32_t count, len; int64_t ikey; uint64_t ref; };
struct Top10 {
  Top t[10];
  int n = 0;
  // Ordre : compte décroissant, entier croissant, chaîne croissante.
  static bool before(const Top &a, const Top &b, const uint8_t *bytes) {
    if (a.count != b.count) return a.count > b.count;
    if (a.ikey != b.ikey) return a.ikey < b.ikey;
    return sv(bytes + a.ref, a.len) < sv(bytes + b.ref, b.len);
  }
  void add(const Top &x, const uint8_t *bytes) {
    if (n == 10 && !before(x, t[9], bytes)) return;
    int i = n < 10 ? n++ : 9;
    for (; i > 0 && before(x, t[i - 1], bytes); i--) t[i] = t[i - 1];
    t[i] = x;
  }
};

// ================================================================================================ T1 (TPC-H Q1)
struct T1 {
  Col ship, rf, ls, qty, ext, disc, tax;
  Counter ctr;
  int32_t cut;
  Agg1 agg[MAXT][6];

  void open() {
    ship = col_open("lineitem", "l_shipdate"); rf = col_open("lineitem", "l_returnflag");
    ls = col_open("lineitem", "l_linestatus"); qty = col_open("lineitem", "l_quantity");
    ext = col_open("lineitem", "l_extendedprice"); disc = col_open("lineitem", "l_discount");
    tax = col_open("lineitem", "l_tax");
    cut = days_from_civil(1998, 9, 2);
  }
  void task(int tid) {
    Scratch &s = *scratch[tid];
    Agg1 local[6] = {};
    for (int64_t b; (b = ctr.take()) >= 0;) {
      const Entry &e = ship.dir[b];
      if (e.min > cut) continue;      // bloc exclu par sa carte de zones
      const bool all = e.max <= cut;  // bloc retenu en entier : le filtre n'est pas évalué
      each_vector(e.count, [&](uint32_t st, uint32_t n) {
        unpack(rf, b, st, n, s.a);
        unpack(ls, b, st, n, s.b);
        unpack(qty, b, st, n, s.c);
        unpack(ext, b, st, n, s.d);
        unpack(disc, b, st, n, s.e);
        unpack(tax, b, st, n, s.f);
        for (uint32_t i = 0; i < n; i++) s.x[i] = static_cast<int64_t>(s.d[i]) * (100 - s.e[i]);
        for (uint32_t i = 0; i < n; i++) s.y[i] = s.x[i] * (100 + s.f[i]);
        for (uint32_t i = 0; i < n; i++) s.g[i] = s.a[i] * 2 + s.b[i];
        const int32_t *dates = nullptr;
        if (!all) { unpack(ship, b, st, n, s.pos); dates = s.pos; }
        t1_aggregate(local, s.g, s.c, s.d, s.e, s.x, s.y, dates, cut, n, s.sel);
      });
    }
    std::copy_n(local, 6, agg[tid]);
  }
  void run() {
    ctr.set(ship.nblocks);
    pool.run([this](int tid) { task(tid); });
    for (uint32_t g = 0; g < 6; g++) {
      Agg1 a{};
      for (int t = 0; t < NT; t++) {
        const Agg1 &x = agg[t][g];
        a.qty += x.qty; a.base += x.base; a.disc_price += x.disc_price; a.charge += x.charge; a.disc += x.disc;
        a.count += x.count;
      }
      if (!a.count) continue;
      emit(rf.dict(g / 2), "|", ls.dict(g % 2), "|", a.qty, "|", a.base, "|", a.disc_price, "|", a.charge, "|", a.disc,
           "|", a.count, "\n");
    }
  }
};

// ================================================================================================ T6 (TPC-H Q6)
struct T6 {
  Col ship, disc, qty, ext;
  Counter ctr;
  int32_t lo, hi;
  int64_t sum[MAXT][8];

  void open() {
    ship = col_open("lineitem", "l_shipdate"); disc = col_open("lineitem", "l_discount");
    qty = col_open("lineitem", "l_quantity"); ext = col_open("lineitem", "l_extendedprice");
    lo = days_from_civil(1994, 1, 1); hi = days_from_civil(1995, 1, 1);
  }
  void task(int tid) {
    Scratch &s = *scratch[tid];
    int64_t total = 0;
    for (int64_t b; (b = ctr.take()) >= 0;) {
      const Entry &e = ship.dir[b];
      if (e.max < lo || e.min >= hi) continue;
      each_vector(e.count, [&](uint32_t st, uint32_t n) {
        unpack(ship, b, st, n, s.a);
        const uint32_t k = sel_between(s.a, n, lo, hi - 1, st, s.pos);
        if (!k) return;
        unpack_sel(disc, b, s.pos, k, s.b);
        const uint32_t k2 = keep_between(s.b, s.pos, s.b, k, 5, 7, s.sel, s.c);
        if (!k2) return;
        unpack_sel(qty, b, s.sel, k2, s.d);
        const uint32_t k3 = keep_between(s.d, s.sel, s.c, k2, INT32_MIN, 2399, s.sel2, s.e);
        if (!k3) return;
        unpack_sel(ext, b, s.sel2, k3, s.f);
        for (uint32_t i = 0; i < k3; i++) total += static_cast<int64_t>(s.f[i]) * s.e[i];
      });
    }
    sum[tid][0] = total;
  }
  void run() {
    ctr.set(ship.nblocks);
    pool.run([this](int tid) { task(tid); });
    int64_t total = 0;
    for (int t = 0; t < NT; t++) total += sum[t][0];
    emit(total, "\n");
  }
};

// ================================================================================================ T9 (TPC-H Q9)
// 1. part : noms qui contiennent « green » -> ensemble de pièces (table et filtre de Bloom) ;
// 2. partsupp : lignes de ces pièces -> (pièce, fournisseur) -> coût ; 3. supplier -> nation ;
// 4. lineitem : lignes de ces pièces, montant et nation, réparties par commande ;
// 5. orders : (commande, date) réparties de même ; 6. par partition : table des lignes de lineitem, sondée par les
//    commandes ; agrégat par nation et année.
struct T9 {
  struct Tuple { int32_t okey, nation; int64_t amount; };
  struct Order { int32_t okey, date; };
  Col p_partkey, p_name, ps_partkey, ps_suppkey, ps_cost, s_suppkey, s_nationkey, n_nationkey, n_name, l_partkey,
      l_suppkey, l_orderkey, l_qty, l_ext, l_disc, o_orderkey, o_orderdate;
  Counter ctr;
  List l1[MAXT], l2[MAXT];  // listes des fils
  Map part, ps, supp, agg[MAXT];
  Bloom fpart;

  void open() {
    p_partkey = col_open("part", "p_partkey"); p_name = col_open("part", "p_name");
    ps_partkey = col_open("partsupp", "ps_partkey"); ps_suppkey = col_open("partsupp", "ps_suppkey");
    ps_cost = col_open("partsupp", "ps_supplycost"); s_suppkey = col_open("supplier", "s_suppkey");
    s_nationkey = col_open("supplier", "s_nationkey"); n_nationkey = col_open("nation", "n_nationkey");
    n_name = col_open("nation", "n_name"); l_partkey = col_open("lineitem", "l_partkey");
    l_suppkey = col_open("lineitem", "l_suppkey"); l_orderkey = col_open("lineitem", "l_orderkey");
    l_qty = col_open("lineitem", "l_quantity"); l_ext = col_open("lineitem", "l_extendedprice");
    l_disc = col_open("lineitem", "l_discount"); o_orderkey = col_open("orders", "o_orderkey");
    o_orderdate = col_open("orders", "o_orderdate");
  }
  void part_task(int tid) {
    Scratch &s = *scratch[tid];
    l1[tid].init(arena[tid]);
    for (int64_t b; (b = ctr.take()) >= 0;) {
      const uint64_t nbytes = block_lengths(p_name, b, s.len);
      const uint32_t k = search_block(p_name.aux + p_name.dir[b].aux_off, nbytes, s.len, "green", s.rows);
      for (uint32_t i = 0; i < k; i += VEC) {
        const uint32_t n = std::min(k - i, VEC);
        unpack_sel(p_partkey, b, s.rows + i, n, s.a);
        for (uint32_t j = 0; j < n; j++) l1[tid].push(s.a[j]);
      }
    }
  }
  // Positions (dans le bloc) et clés des lignes d'un vecteur dont la clé est dans l'ensemble des pièces.
  uint32_t semi(const int32_t *key, uint32_t n, uint32_t st, int32_t *pos, int32_t *out) const {
    uint32_t k = 0;
    for (uint32_t i = 0; i < n; i++) {
      const uint64_t h = hash64(static_cast<uint64_t>(key[i]));
      if (fpart.test(h) && part.find(key[i], h)) { pos[k] = static_cast<int32_t>(st + i); out[k++] = key[i]; }
    }
    return k;
  }
  void ps_task(int tid) {
    Scratch &s = *scratch[tid];
    l1[tid].init(arena[tid]);
    l2[tid].init(arena[tid]);
    for (int64_t b; (b = ctr.take()) >= 0;)
      each_vector(ps_partkey.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(ps_partkey, b, st, n, s.a);
        const uint32_t k = semi(s.a, n, st, s.pos, s.b);
        if (!k) return;
        unpack_sel(ps_suppkey, b, s.pos, k, s.c);
        unpack_sel(ps_cost, b, s.pos, k, s.d);
        for (uint32_t i = 0; i < k; i++) {
          l1[tid].push(static_cast<int64_t>(s.b[i]) << 32 | s.c[i]);
          l2[tid].push(s.d[i]);
        }
      });
  }
  void line_task(int tid) {
    Scratch &s = *scratch[tid];
    Parts &p = parts[tid];
    p.init(arena[tid], sizeof(Tuple));
    for (int64_t b; (b = ctr.take()) >= 0;)
      each_vector(l_partkey.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(l_partkey, b, st, n, s.a);
        const uint32_t k = semi(s.a, n, st, s.pos, s.b);
        if (!k) return;
        unpack_sel(l_suppkey, b, s.pos, k, s.c);
        unpack_sel(l_orderkey, b, s.pos, k, s.d);
        unpack_sel(l_qty, b, s.pos, k, s.e);
        unpack_sel(l_ext, b, s.pos, k, s.f);
        unpack_sel(l_disc, b, s.pos, k, s.g);
#ifdef SPECIAL
        for (uint32_t i = 0; i < k; i++) {  // les cases des deux tables sont préchargées pour tout le vecteur
          prefetch(&ps.cells[hash64(static_cast<uint64_t>(static_cast<int64_t>(s.b[i]) << 32 | s.c[i])) & ps.mask]);
          prefetch(&supp.cells[hash64(static_cast<uint64_t>(s.c[i])) & supp.mask]);
        }
#endif
        for (uint32_t i = 0; i < k; i++) {
          const int64_t cost = ps.find(static_cast<int64_t>(s.b[i]) << 32 | s.c[i])->val;
          const int64_t nation = supp.find(s.c[i])->val;
          Tuple *t = p.push<Tuple>(part_of(hash64(static_cast<uint64_t>(s.d[i]))));
          t->okey = s.d[i]; t->nation = static_cast<int32_t>(nation);
          t->amount = static_cast<int64_t>(s.f[i]) * (100 - s.g[i]) - cost * s.e[i];
        }
      });
    p.close();
  }
  void orders_task(int tid) {
    Scratch &s = *scratch[tid];
    Parts &p = parts2[tid];
    p.init(arena[tid], sizeof(Order));
    for (int64_t b; (b = ctr.take()) >= 0;)
      each_vector(o_orderkey.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(o_orderkey, b, st, n, s.a);
        unpack(o_orderdate, b, st, n, s.b);
        for (uint32_t i = 0; i < n; i++) s.h[i] = hash64(static_cast<uint64_t>(s.a[i]));
        for (uint32_t i = 0; i < n; i++) {
          Order *t = p.push<Order>(part_of(s.h[i]));
          t->okey = s.a[i]; t->date = s.b[i];
        }
      });
    p.close();
  }
  void join_task(int tid) {
    Map &total = agg[tid];
    total.init(arena[tid], 1024);
    for (int64_t k; (k = ctr.take()) >= 0;) {
      const uint64_t n = parts_count(parts, NT, static_cast<uint32_t>(k));
      if (!n) continue;
      Tuple *tu = arena[tid].array<Tuple>(n);
      int32_t *next = arena[tid].array<int32_t>(n);
      Map m;  // commande -> rang de son dernier tuple ; next chaîne les tuples d'une même commande
      m.init(arena[tid], pow2_for(n));
      uint64_t i = 0;
      parts_each<Tuple>(parts, NT, static_cast<uint32_t>(k), [&](const Tuple *t, const Tuple *) {
        bool fresh;
        Cell &c = m.upsert(t->okey, fresh);
        tu[i] = *t;
        next[i] = fresh ? -1 : static_cast<int32_t>(c.val);
        c.val = static_cast<int64_t>(i++);
      });
      parts_each<Order>(parts2, NT, static_cast<uint32_t>(k), [&](const Order *o, [[maybe_unused]] const Order *end) {
#ifdef SPECIAL
        if (o + AHEAD < end) prefetch(&m.cells[hash64(static_cast<uint64_t>(o[AHEAD].okey)) & m.mask]);
#endif
        const Cell *c = m.find(o->okey);
        if (!c) return;
        const int64_t year = year_of(o->date);
        for (int32_t j = static_cast<int32_t>(c->val); j >= 0; j = next[j])
          total.upsert(static_cast<int64_t>(tu[j].nation) << 16 | year).val += tu[j].amount;
      });
    }
  }
  void run() {
    Arena &a0 = arena[0];
    Scratch &s = *scratch[0];
    ctr.set(p_name.nblocks);
    pool.run([this](int tid) { part_task(tid); });
    uint64_t n = 0;
    for (int t = 0; t < NT; t++) n += l1[t].n;
    part.init(a0, pow2_for(n));
    fpart.init(a0, n);
    for (int t = 0; t < NT; t++)
      for (uint64_t i = 0; i < l1[t].n; i++) {
        part.upsert(l1[t].v[i]);
        fpart.add(hash64(static_cast<uint64_t>(l1[t].v[i])));
      }
    ctr.set(ps_partkey.nblocks);
    pool.run([this](int tid) { ps_task(tid); });
    n = 0;
    for (int t = 0; t < NT; t++) n += l1[t].n;
    ps.init(a0, pow2_for(n));
    for (int t = 0; t < NT; t++)
      for (uint64_t i = 0; i < l1[t].n; i++) ps.upsert(l1[t].v[i]).val = l2[t].v[i];
    supp.init(a0, pow2_for(s_suppkey.nrows));
    for (uint64_t b = 0; b < s_suppkey.nblocks; b++)
      each_vector(s_suppkey.dir[b].count, [&](uint32_t st, uint32_t m) {
        unpack(s_suppkey, b, st, m, s.a);
        unpack(s_nationkey, b, st, m, s.b);
        for (uint32_t i = 0; i < m; i++) supp.upsert(s.a[i]).val = s.b[i];
      });
    ctr.set(l_partkey.nblocks);
    pool.run([this](int tid) { line_task(tid); });
    ctr.set(o_orderkey.nblocks);
    pool.run([this](int tid) { orders_task(tid); });
    ctr.set(NPART);
    pool.run([this](int tid) { join_task(tid); });
    // fusion ; nation -> nom ; tri par nom puis année décroissante
    Map total;
    total.init(a0, 1024);
    for (int t = 0; t < NT; t++) agg[t].each([&](const Cell &c) { total.upsert(c.key).val += c.val; });
    Map nat;
    nat.init(a0, 64);
    unpack(n_nationkey, 0, 0, static_cast<uint32_t>(n_nationkey.nrows), s.a);
    unpack(n_name, 0, 0, static_cast<uint32_t>(n_name.nrows), s.b);
    for (uint32_t i = 0; i < n_nationkey.nrows; i++) nat.upsert(s.a[i]).val = s.b[i];
    struct Row { std::string_view name; int64_t year, sum; };
    Row *rows = a0.array<Row>(total.count + 1);
    uint64_t nr = 0;
    total.each([&](const Cell &c) {
      rows[nr++] = {n_name.dict(static_cast<uint32_t>(nat.find(c.key >> 16)->val)), c.key & 0xFFFF, c.val};
    });
    std::sort(rows, rows + nr, [](const Row &a, const Row &b) { return a.name != b.name ? a.name < b.name : a.year > b.year; });
    for (uint64_t i = 0; i < nr; i++) emit(rows[i].name, "|", rows[i].year, "|", rows[i].sum, "\n");
  }
};

// ================================================================================================ T18 (TPC-H Q18)
struct T18 {
  struct KQ { int32_t key, qty; };
  struct Row { int64_t okey, cust, date, price, sum; std::string_view name; };
  Col l_orderkey, l_qty, o_orderkey, o_custkey, o_orderdate, o_totalprice, c_custkey, c_name;
  Counter ctr;
  List l1[MAXT], l2[MAXT], l3[MAXT], l4[MAXT];
  Map big, cust, sums[MAXT];
  Bloom fbig, fcust;

  void open() {
    l_orderkey = col_open("lineitem", "l_orderkey"); l_qty = col_open("lineitem", "l_quantity");
    o_orderkey = col_open("orders", "o_orderkey"); o_custkey = col_open("orders", "o_custkey");
    o_orderdate = col_open("orders", "o_orderdate"); o_totalprice = col_open("orders", "o_totalprice");
    c_custkey = col_open("customer", "c_custkey"); c_name = col_open("customer", "c_name");
  }
  void scatter_task(int tid) {  // lineitem réparti par commande
    Scratch &s = *scratch[tid];
    Parts &p = parts[tid];
    p.init(arena[tid], sizeof(KQ));
    for (int64_t b; (b = ctr.take()) >= 0;)
      each_vector(l_orderkey.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(l_orderkey, b, st, n, s.a);
        unpack(l_qty, b, st, n, s.b);
        for (uint32_t i = 0; i < n; i++) s.h[i] = hash64(static_cast<uint64_t>(s.a[i]));
        for (uint32_t i = 0; i < n; i++) {
          KQ *t = p.push<KQ>(part_of(s.h[i]));
          t->key = s.a[i]; t->qty = s.b[i];
        }
      });
    p.close();
  }
  void agg_task(int tid) {  // une partition : somme par commande ; garde celles de plus de 300 unités
    l1[tid].init(arena[tid]);
    for (int64_t k; (k = ctr.take()) >= 0;) {
      Map m;
      m.init(arena[tid], pow2_start(parts_count(parts, NT, static_cast<uint32_t>(k))));
      parts_each<KQ>(parts, NT, static_cast<uint32_t>(k), [&](const KQ *t, [[maybe_unused]] const KQ *end) {
#ifdef SPECIAL
        if (t + AHEAD < end) prefetch(&m.cells[hash64(static_cast<uint64_t>(t[AHEAD].key)) & m.mask]);
#endif
        m.upsert(t->key).val += t->qty;
      });
      m.each([&](const Cell &c) { if (c.val > 30000) l1[tid].push(c.key); });
    }
  }
  // Positions et clés des lignes d'un vecteur dont la commande est retenue.
  uint32_t semi(const int32_t *key, uint32_t n, uint32_t st, int32_t *pos, int32_t *out) const {
    uint32_t k = 0;
    for (uint32_t i = 0; i < n; i++) {
      const uint64_t h = hash64(static_cast<uint64_t>(key[i]));
      if (fbig.test(h) && big.find(key[i], h)) { pos[k] = static_cast<int32_t>(st + i); out[k++] = key[i]; }
    }
    return k;
  }
  void orders_task(int tid) {  // commandes retenues : client, date, prix
    Scratch &s = *scratch[tid];
    l1[tid].init(arena[tid]); l2[tid].init(arena[tid]); l3[tid].init(arena[tid]); l4[tid].init(arena[tid]);
    for (int64_t b; (b = ctr.take()) >= 0;)
      each_vector(o_orderkey.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(o_orderkey, b, st, n, s.a);
        const uint32_t k = semi(s.a, n, st, s.pos, s.b);
        if (!k) return;
        unpack_sel(o_custkey, b, s.pos, k, s.c);
        unpack_sel(o_orderdate, b, s.pos, k, s.d);
        unpack_sel(o_totalprice, b, s.pos, k, s.e);
        for (uint32_t i = 0; i < k; i++) {
          l1[tid].push(s.b[i]); l2[tid].push(s.c[i]); l3[tid].push(s.d[i]); l4[tid].push(s.e[i]);
        }
      });
  }
  void cust_task(int tid) {  // clients de ces commandes : position et longueur de leur nom
    Scratch &s = *scratch[tid];
    l1[tid].init(arena[tid]); l2[tid].init(arena[tid]); l3[tid].init(arena[tid]);
    for (int64_t b; (b = ctr.take()) >= 0;) {
      uint64_t pos = c_name.dir[b].aux_off;
      each_vector(c_custkey.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(c_custkey, b, st, n, s.a);
        unpack(c_name, b, st, n, s.b);
        for (uint32_t i = 0; i < n; i++) {
          const uint64_t h = hash64(static_cast<uint64_t>(s.a[i]));
          if (fcust.test(h) && cust.find(s.a[i], h)) {
            l1[tid].push(s.a[i]); l2[tid].push(static_cast<int64_t>(pos)); l3[tid].push(s.b[i]);
          }
          pos += static_cast<uint64_t>(s.b[i]);
        }
      });
    }
  }
  void sum_task(int tid) {  // lineitem des commandes retenues : somme des quantités
    Scratch &s = *scratch[tid];
    Map &m = sums[tid];
    m.init(arena[tid], 1024);
    for (int64_t b; (b = ctr.take()) >= 0;)
      each_vector(l_orderkey.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(l_orderkey, b, st, n, s.a);
        const uint32_t k = semi(s.a, n, st, s.pos, s.b);
        if (!k) return;
        unpack_sel(l_qty, b, s.pos, k, s.c);
        for (uint32_t i = 0; i < k; i++) m.upsert(s.b[i]).val += s.c[i];
      });
  }
  void run() {
    Arena &a0 = arena[0];
    // 1. et 2. agrégation de lineitem par commande ; 3. commandes de plus de 300 unités
    ctr.set(l_orderkey.nblocks);
    pool.run([this](int tid) { scatter_task(tid); });
    ctr.set(NPART);
    pool.run([this](int tid) { agg_task(tid); });
    uint64_t n = 0;
    for (int t = 0; t < NT; t++) n += l1[t].n;
    big.init(a0, pow2_for(n));
    fbig.init(a0, n);
    for (int t = 0; t < NT; t++)
      for (uint64_t i = 0; i < l1[t].n; i++) {
        big.upsert(l1[t].v[i]);
        fbig.add(hash64(static_cast<uint64_t>(l1[t].v[i])));
      }
    // 4. leurs lignes dans orders
    ctr.set(o_orderkey.nblocks);
    pool.run([this](int tid) { orders_task(tid); });
    Row *rows = a0.array<Row>(n + 1);
    uint64_t nr = 0;
    cust.init(a0, pow2_for(n));
    fcust.init(a0, n);
    for (int t = 0; t < NT; t++)
      for (uint64_t i = 0; i < l1[t].n; i++) {
        rows[nr++] = {l1[t].v[i], l2[t].v[i], l3[t].v[i], l4[t].v[i], 0, {}};
        cust.upsert(l2[t].v[i]);
        fcust.add(hash64(static_cast<uint64_t>(l2[t].v[i])));
      }
    // 5. leurs clients ; 6. leurs lignes dans lineitem
    ctr.set(c_custkey.nblocks);
    pool.run([this](int tid) { cust_task(tid); });
    Map name;  // client -> rang dans les listes
    name.init(a0, pow2_for(n));
    List pos, len;
    pos.init(a0); len.init(a0);
    for (int t = 0; t < NT; t++)
      for (uint64_t i = 0; i < l1[t].n; i++) {
        name.upsert(l1[t].v[i]).val = static_cast<int64_t>(pos.n);
        pos.push(l2[t].v[i]); len.push(l3[t].v[i]);
      }
    ctr.set(l_orderkey.nblocks);
    pool.run([this](int tid) { sum_task(tid); });
    for (uint64_t i = 0; i < nr; i++) {
      for (int t = 0; t < NT; t++)
        if (const Cell *c = sums[t].find(rows[i].okey)) rows[i].sum += c->val;
      const int64_t j = name.find(rows[i].cust)->val;
      rows[i].name = sv(c_name.aux + pos.v[j], static_cast<size_t>(len.v[j]));
    }
    std::sort(rows, rows + nr, [](const Row &a, const Row &b) {  // prix décroissant, date, commande
      if (a.price != b.price) return a.price > b.price;
      if (a.date != b.date) return a.date < b.date;
      return a.okey < b.okey;
    });
    for (uint64_t i = 0; i < nr && i < 100; i++)
      emit(rows[i].name, "|", rows[i].cust, "|", rows[i].okey, "|", rows[i].date, "|", rows[i].price, "|", rows[i].sum, "\n");
  }
};

// ================================================================================================ C4
struct C4 {
  Col uid;
  Counter ctr;
  uint64_t count[MAXT][8];
  int minus1[MAXT][16];

  void open() { uid = col_open("hits", "UserID"); }
  void scatter_task(int tid) {
    Scratch &s = *scratch[tid];
    Parts &p = parts[tid];
    p.init(arena[tid], sizeof(int64_t));
    for (int64_t b; (b = ctr.take()) >= 0;) {
      const int64_t *v = reinterpret_cast<const int64_t *>(uid.words(b));  // 64 bits : valeurs telles quelles
      each_vector(uid.dir[b].count, [&](uint32_t st, uint32_t n) {
        for (uint32_t i = 0; i < n; i++) s.h[i] = hash64(static_cast<uint64_t>(v[st + i]));
        for (uint32_t i = 0; i < n; i++) *p.push<int64_t>(part_of(s.h[i])) = v[st + i];
      });
    }
    p.close();
  }
  void count_task(int tid) {
    uint64_t total = 0;
    int seen_minus1 = 0;
    for (int64_t k; (k = ctr.take()) >= 0;) {
      Map m;
      m.init(arena[tid], pow2_start(parts_count(parts, NT, static_cast<uint32_t>(k))));
      parts_each<int64_t>(parts, NT, static_cast<uint32_t>(k), [&](const int64_t *t, [[maybe_unused]] const int64_t *end) {
#ifdef SPECIAL
        if (t + AHEAD < end) prefetch(&m.cells[hash64(static_cast<uint64_t>(t[AHEAD])) & m.mask]);
#endif
        if (*t == -1) seen_minus1 = 1;  // la valeur qui marque les cases vides est comptée à part
        else m.upsert(*t);
      });
      total += m.count;
    }
    count[tid][0] = total;
    minus1[tid][0] = seen_minus1;
  }
  void run() {
    ctr.set(uid.nblocks);
    pool.run([this](int tid) { scatter_task(tid); });
    ctr.set(NPART);
    pool.run([this](int tid) { count_task(tid); });
    uint64_t total = 0;
    int seen_minus1 = 0;
    for (int t = 0; t < NT; t++) { total += count[t][0]; seen_minus1 |= minus1[t][0]; }
    emit(total + static_cast<uint64_t>(seen_minus1), "\n");
  }
};

// ================================================================================================ agrégations par chaîne
// C12, C16, C33, C36 : les lignes retenues sont hachées, réparties, puis agrégées partition par partition ; chaque
// fil garde ses dix premiers groupes.
struct CS {
  struct Tuple { uint64_t hash; int64_t ikey; uint64_t ref; uint32_t len, pad; };
  Col str, uid, counter, date, dch, refresh;
  Counter ctr;
  int mode;  // 12, 16, 33, 36
  int32_t lo, hi;
  Top10 top[MAXT];

  void open(int m) {
    mode = m;
    str = col_open("hits", mode == 12 || mode == 16 ? "SearchPhrase" : "URL");
    if (mode == 16) uid = col_open("hits", "UserID");
    if (mode == 36) {
      counter = col_open("hits", "CounterID"); date = col_open("hits", "EventDate");
      dch = col_open("hits", "DontCountHits"); refresh = col_open("hits", "IsRefresh");
      lo = days_from_civil(2013, 7, 1); hi = days_from_civil(2013, 7, 31);
    }
  }
  void scatter_task(int tid) {
    Scratch &s = *scratch[tid];
    Parts &p = parts[tid];
    p.init(arena[tid], sizeof(Tuple));
    const uint8_t *bytes = str.aux;
    for (int64_t b; (b = ctr.take()) >= 0;) {
      if (mode == 36) {  // cartes de zones : compteur et date
        const Entry &ec = counter.dir[b], &ed = date.dir[b];
        if (ec.min > 62 || ec.max < 62 || ed.max < lo || ed.min > hi) continue;
      }
      const int64_t *u = mode == 16 ? reinterpret_cast<const int64_t *>(uid.words(b)) : nullptr;
      uint64_t pos = str.dir[b].aux_off;
      each_vector(str.dir[b].count, [&](uint32_t st, uint32_t n) {
        unpack(str, b, st, n, s.a);  // longueurs
        for (uint32_t i = 0; i < n; i++) { s.x[i] = static_cast<int64_t>(pos); pos += static_cast<uint64_t>(s.a[i]); }
        uint32_t k = 0;
        if (mode == 36) {
          unpack(counter, b, st, n, s.b);
          k = sel_between(s.b, n, 62, 62, st, s.pos);
          if (!k) return;
          unpack_sel(date, b, s.pos, k, s.c);
          unpack_sel(dch, b, s.pos, k, s.d);
          unpack_sel(refresh, b, s.pos, k, s.e);
          uint32_t k2 = 0;
          for (uint32_t i = 0; i < k; i++) {
            const uint32_t j = static_cast<uint32_t>(s.pos[i]) - st;
            s.sel[k2] = static_cast<int32_t>(j);
            k2 += (s.c[i] >= lo) & (s.c[i] <= hi) & (s.d[i] == 0) & (s.e[i] == 0) & (s.a[j] > 0);
          }
          k = k2;
        } else if (mode == 12) {
          k = sel_between(s.a, n, 1, INT32_MAX, 0, s.sel);
        } else {
          for (uint32_t i = 0; i < n; i++) s.sel[i] = static_cast<int32_t>(i);
          k = n;
        }
        for (uint32_t j = 0; j < k; j++) {
          const uint32_t i = static_cast<uint32_t>(s.sel[j]);
          s.h[j] = hash_bytes(bytes + s.x[i], static_cast<uint32_t>(s.a[i]));
        }
        if (u)
          for (uint32_t j = 0; j < k; j++) {
            const uint64_t h = hash64(s.h[j] ^ (static_cast<uint64_t>(u[st + static_cast<uint32_t>(s.sel[j])]) * K2));
            s.h[j] = h ? h : 1;
          }
        for (uint32_t j = 0; j < k; j++) {
          const uint32_t i = static_cast<uint32_t>(s.sel[j]);
          Tuple *t = p.push<Tuple>(part_of(s.h[j]));
          t->hash = s.h[j]; t->ikey = u ? u[st + i] : 0; t->ref = static_cast<uint64_t>(s.x[i]);
          t->len = static_cast<uint32_t>(s.a[i]);
        }
      });
    }
    p.close();
  }
  void agg_task(int tid) {
    Top10 &best = top[tid];
    best.n = 0;
    for (int64_t k; (k = ctr.take()) >= 0;) {
      SMap m;
      m.init(arena[tid], pow2_start(parts_count(parts, NT, static_cast<uint32_t>(k))), str.aux);
      parts_each<Tuple>(parts, NT, static_cast<uint32_t>(k), [&](const Tuple *t, [[maybe_unused]] const Tuple *end) {
#ifdef SPECIAL
        if (t + AHEAD < end) {  // à AHEAD tuples : la case et les octets du tuple ; à mi-distance : les octets de la case
          prefetch(&m.cells[t[AHEAD].hash & m.mask]);
          prefetch(m.bytes + t[AHEAD].ref);
          const SCell &c = m.cells[t[AHEAD / 2].hash & m.mask];
          if (c.hash == t[AHEAD / 2].hash) prefetch(m.bytes + c.ref);
        }
#endif
        m.add(t->hash, t->ikey, t->ref, t->len);
      });
      for (uint64_t j = 0; j <= m.mask; j++)
        if (m.cells[j].hash) best.add({m.cells[j].count, m.cells[j].len, m.cells[j].ikey, m.cells[j].ref}, str.aux);
    }
  }
  void run() {
    ctr.set(str.nblocks);
    pool.run([this](int tid) { scatter_task(tid); });
    ctr.set(NPART);
    pool.run([this](int tid) { agg_task(tid); });
    Top10 all;
    for (int t = 0; t < NT; t++)
      for (int i = 0; i < top[t].n; i++) all.add(top[t].t[i], str.aux);
    for (int i = 0; i < all.n; i++) {
      if (mode == 16) emit(all.t[i].ikey, "|");
      emit(sv(str.aux + all.t[i].ref, all.t[i].len), "|", all.t[i].count, "\n");
    }
  }
};

// ================================================================================================ C20
struct C20 {
  Col url;
  Counter ctr;
  uint64_t count[MAXT][8];

  void open() { url = col_open("hits", "URL"); }
  void run() {
    ctr.set(url.nblocks);
    pool.run([this](int tid) {
      Scratch &s = *scratch[tid];
      uint64_t total = 0;
      for (int64_t b; (b = ctr.take()) >= 0;) {
        const uint64_t nbytes = block_lengths(url, b, s.len);
        total += search_block(url.aux + url.dir[b].aux_off, nbytes, s.len, "google", s.rows);
      }
      count[tid][0] = total;
    });
    uint64_t total = 0;
    for (int t = 0; t < NT; t++) total += count[t][0];
    emit(total, "\n");
  }
};

// ================================================================================================ principal
static T1 t1;
static T6 t6;
static T9 t9;
static T18 t18;
static C4 c4;
static CS cs;
static C20 c20;

int main(int argc, char **argv) {
  if (argc < 5) die("usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]");
  const std::string_view q = argv[1];
  NT = std::atoi(argv[2]);
  const int reps = std::atoi(argv[3]);
  DATA = argv[4];
  const bool print = argc > 5 && std::string_view(argv[5]) == "--print";
  if (NT < 1 || NT > MAXT) die("nombre de fils");
  for (int t = 0; t < NT; t++) scratch[t] = static_cast<Scratch *>(huge_alloc(sizeof(Scratch)));
  void (*runq)() = nullptr;
  if (q == "t1") { t1.open(); runq = [] { t1.run(); }; }
  else if (q == "t6") { t6.open(); runq = [] { t6.run(); }; }
  else if (q == "t9") { t9.open(); runq = [] { t9.run(); }; }
  else if (q == "t18") { t18.open(); runq = [] { t18.run(); }; }
  else if (q == "c4") { c4.open(); runq = [] { c4.run(); }; }
  else if (q == "c12" || q == "c16" || q == "c33" || q == "c36") { cs.open(std::atoi(argv[1] + 1)); runq = [] { cs.run(); }; }
  else if (q == "c20") { c20.open(); runq = [] { c20.run(); }; }
  else die("requête inconnue");
  pool.start(NT);
#ifdef SPECIAL
  const char *level = "s";
#else
  const char *level = "p";
#endif
  for (int r = 0; r < reps; r++) {
    for (int t = 0; t < NT; t++) arena[t].reset();
    res.clear();
    const auto t0 = std::chrono::steady_clock::now();
    runq();
    const double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::printf("RESULT;%s;%s;%d;%d;%.6f;%016llx\n", argv[1], level, NT, r, dt, static_cast<unsigned long long>(fnv1a(res)));
    if (print && r == reps - 1) std::fwrite(res.data(), 1, res.size(), stdout);
    std::fflush(stdout);
  }
  return 0;
}
