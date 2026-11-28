// v7 (docs/V7.md ; olap/SPEC.md) : implémentation de référence du banc OLAP, en C. Niveau portable : aucune
// vectorisation explicite, aucune construction propre à une famille de processeurs. Le niveau spécialisé
// (-DSPECIAL) remplace des primitives par celles de olap_special.h.
//
// Usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]
//   requêtes : t1 t6 t9 t18 (TPC-H) c4 c12 c16 c20 c33 c36 (ClickBench)
//   sortie   : une ligne « RESULT;requête;niveau;fils;répétition;secondes;empreinte » par répétition ; l'empreinte est
//              le FNV-1a 64 bits du résultat canonique, que --print écrit aussi.
#define _GNU_SOURCE
#include <fcntl.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdatomic.h>
#include <stdbit.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#ifndef PBITS
#define PBITS 10           /* bits de partition */
#endif
#ifndef VEC
#define VEC 2048           /* lignes d'un vecteur */
#endif
#ifndef CHUNK
#define CHUNK 16384        /* octets utiles d'un morceau de tampon de partition */
#endif
enum {
  BLOCK = 65536,           // lignes d'un bloc : un morceau
  NPART = 1 << PBITS,      // partitions des grandes tables
  MAXT = 64,               // fils au plus
  ARENA_BLOCK = 32 << 20,  // octets d'un bloc d'arène
};
#define K1 0x9E3779B97F4A7C15ull
#define K2 0xC2B2AE3D27D4EB4Full

static void die(const char *msg) { fprintf(stderr, "olap : %s\n", msg); exit(2); }

// ------------------------------------------------------------------------------------------------ arènes
// Une arène par fil : allocation par déplacement d'un pointeur, remise à zéro du pointeur à chaque exécution ; la
// mémoire est gardée d'une répétition à l'autre.
typedef struct ArenaBlock { struct ArenaBlock *next; size_t cap, used; char pad[40]; } ArenaBlock;  // 64 octets
typedef struct { ArenaBlock *first, *cur; } Arena;

static void *arena_alloc(Arena *a, size_t n) {
  n = (n + 63) & ~(size_t)63;
  for (;;) {
    ArenaBlock *b = a->cur;
    if (b && b->used + n <= b->cap) { void *p = (char *)(b + 1) + b->used; b->used += n; return p; }
    if (b && b->next && b->next->cap >= n) { a->cur = b->next; a->cur->used = 0; continue; }
    size_t cap = n > ARENA_BLOCK ? n : ARENA_BLOCK;
    ArenaBlock *nb;
    if (posix_memalign((void **)&nb, 64, sizeof(ArenaBlock) + cap)) die("mémoire");
    nb->cap = cap; nb->used = 0;
    if (b) { nb->next = b->next; b->next = nb; } else { nb->next = NULL; a->first = nb; }
    a->cur = nb;
  }
}
static void arena_reset(Arena *a) { a->cur = a->first; if (a->cur) a->cur->used = 0; }

// ------------------------------------------------------------------------------------------------ fils persistants
typedef void (*TaskFn)(int tid);
static struct {
  int n; pthread_t th[MAXT]; pthread_mutex_t mu; pthread_cond_t work, done; TaskFn fn; uint64_t gen; int pending;
} pool = {.mu = PTHREAD_MUTEX_INITIALIZER, .work = PTHREAD_COND_INITIALIZER, .done = PTHREAD_COND_INITIALIZER};

static void *worker(void *arg) {
  int tid = (int)(intptr_t)arg;
  uint64_t seen = 0;
  for (;;) {
    pthread_mutex_lock(&pool.mu);
    while (pool.gen == seen) pthread_cond_wait(&pool.work, &pool.mu);
    seen = pool.gen;
    TaskFn fn = pool.fn;
    pthread_mutex_unlock(&pool.mu);
    fn(tid);
    pthread_mutex_lock(&pool.mu);
    if (--pool.pending == 0) pthread_cond_signal(&pool.done);
    pthread_mutex_unlock(&pool.mu);
  }
  return NULL;
}
static void pool_start(int n) {
  pool.n = n;
  for (int i = 1; i < n; i++) pthread_create(&pool.th[i], NULL, worker, (void *)(intptr_t)i);
}
// Exécute fn sur tous les fils (le fil principal est le fil 0) et attend la fin de tous.
static void run(TaskFn fn) {
  if (pool.n > 1) {
    pthread_mutex_lock(&pool.mu);
    pool.fn = fn; pool.pending = pool.n - 1; pool.gen++;
    pthread_cond_broadcast(&pool.work);
    pthread_mutex_unlock(&pool.mu);
  }
  fn(0);
  if (pool.n > 1) {
    pthread_mutex_lock(&pool.mu);
    while (pool.pending) pthread_cond_wait(&pool.done, &pool.mu);
    pthread_mutex_unlock(&pool.mu);
  }
}
// Compteur de morceaux partagé.
typedef struct { _Atomic uint64_t next; uint64_t n; } Counter;
static void counter_set(Counter *c, uint64_t n) { atomic_store(&c->next, 0); c->n = n; }
static inline int64_t take(Counter *c) {
  uint64_t i = atomic_fetch_add_explicit(&c->next, 1, memory_order_relaxed);
  return i < c->n ? (int64_t)i : -1;
}

// ------------------------------------------------------------------------------------------------ colonnes
typedef struct { int64_t min, max; uint64_t data_off, aux_off; uint32_t width, count; } Entry;
typedef struct {
  const uint8_t *base; uint64_t size; uint32_t kind, vtype; uint64_t nrows, nblocks, aux_count;
  const Entry *dir; const uint64_t *data; const uint8_t *aux;
} Col;

static const char *DATA;  // répertoire des données

static Col col_open(const char *table, const char *name) {
  char path[4096];
  snprintf(path, sizeof path, "%s/%s/%s.msc", DATA, table, name);
  int fd = open(path, O_RDONLY);
  if (fd < 0) { perror(path); exit(2); }
  struct stat st;
  fstat(fd, &st);
  Col c = {0};
  c.size = (uint64_t)st.st_size;
  c.base = mmap(NULL, c.size, PROT_READ, MAP_PRIVATE | MAP_POPULATE, fd, 0);
  if (c.base == MAP_FAILED) die("mmap");
  close(fd);
  if (memcmp(c.base, "MSC1", 4)) die("format");
  uint32_t h32[3];
  uint64_t h64[6];
  memcpy(h32, c.base + 4, 12);
  memcpy(h64, c.base + 16, 48);
  c.kind = h32[0]; c.vtype = h32[1];
  if (h32[2] != BLOCK) die("taille de bloc");
  c.nrows = h64[0]; c.nblocks = h64[1];
  c.dir = (const Entry *)(c.base + h64[2]);
  c.data = (const uint64_t *)(c.base + h64[3]);
  c.aux = c.base + h64[4];
  c.aux_count = h64[5];
  uint64_t sum = 0;  // les pages sont lues une fois : données chaudes
  for (uint64_t i = 0; i < c.size; i += 4096) sum += c.base[i];
  if (sum == UINT64_MAX) die("lecture");
  return c;
}
static inline const uint64_t *block_words(const Col *c, uint64_t b) { return c->data + c->dir[b].data_off / 8; }
// Octets des chaînes (genre 2) : la zone annexe ; ceux d'une colonne en dictionnaire suivent sa table de positions.
static inline const uint8_t *dict_entry(const Col *c, uint32_t code, uint32_t *len) {
  uint32_t pos[2];
  memcpy(pos, c->aux + 4 * (uint64_t)code, 8);
  *len = pos[1] - pos[0];
  return c->aux + 4 * (c->aux_count + 1) + pos[0];
}

// ------------------------------------------------------------------------------------------------ décodage
// Une routine par largeur : un groupe de 64 valeurs occupe « largeur » mots ; les positions sont des constantes.
#define UNPACK(W)                                                                                                  \
  static void unpack_##W(const uint64_t *restrict in, int32_t *restrict out, uint32_t n, uint32_t base) {         \
    for (uint32_t g = 0; g < n; g += 64, in += W, out += 64)                                                      \
      for (uint32_t j = 0; j < 64; j++) {                                                                         \
        const uint32_t bit = j * W, idx = bit >> 6, sh = bit & 63;                                                \
        uint64_t v = in[idx] >> sh;                                                                               \
        if (sh + W > 64) v |= in[idx + 1] << (64 - sh);                                                           \
        out[j] = (int32_t)((uint32_t)(v & ((1ull << W) - 1)) + base);                                             \
      }                                                                                                           \
  }
UNPACK(1) UNPACK(2) UNPACK(3) UNPACK(4) UNPACK(5) UNPACK(6) UNPACK(7) UNPACK(8) UNPACK(9) UNPACK(10) UNPACK(11)
UNPACK(12) UNPACK(13) UNPACK(14) UNPACK(15) UNPACK(16) UNPACK(17) UNPACK(18) UNPACK(19) UNPACK(20) UNPACK(21)
UNPACK(22) UNPACK(23) UNPACK(24) UNPACK(25) UNPACK(26) UNPACK(27) UNPACK(28) UNPACK(29) UNPACK(30) UNPACK(31)
UNPACK(32)
typedef void (*UnpackFn)(const uint64_t *restrict, int32_t *restrict, uint32_t, uint32_t);
static const UnpackFn UNPACK_FN[33] = {
    NULL,      unpack_1,  unpack_2,  unpack_3,  unpack_4,  unpack_5,  unpack_6,  unpack_7,  unpack_8,
    unpack_9,  unpack_10, unpack_11, unpack_12, unpack_13, unpack_14, unpack_15, unpack_16, unpack_17,
    unpack_18, unpack_19, unpack_20, unpack_21, unpack_22, unpack_23, unpack_24, unpack_25, unpack_26,
    unpack_27, unpack_28, unpack_29, unpack_30, unpack_31, unpack_32};

// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 64.
static inline void unpack(const Col *c, uint64_t b, uint32_t start, uint32_t n, int32_t *out) {
  const Entry *e = &c->dir[b];
  if (e->width == 0) {
    for (uint32_t i = 0; i < n; i++) out[i] = (int32_t)e->min;
    return;
  }
  UNPACK_FN[e->width](block_words(c, b) + (uint64_t)(start / 64) * e->width, out, n, (uint32_t)e->min);
}
// Décode les valeurs du bloc b aux positions pos (lignes dans le bloc), dans l'ordre : out[i] est celle de pos[i].
static inline void unpack_sel(const Col *c, uint64_t b, const int32_t *pos, uint32_t n, int32_t *out) {
  const Entry *e = &c->dir[b];
  const uint64_t *in = block_words(c, b);
  const uint32_t w = e->width, base = (uint32_t)e->min;
  if (w == 0) {
    for (uint32_t i = 0; i < n; i++) out[i] = (int32_t)base;
    return;
  }
  const uint64_t mask = (1ull << w) - 1;
  for (uint32_t i = 0; i < n; i++) {
    const uint64_t bit = (uint64_t)pos[i] * w, idx = bit >> 6;
    const uint32_t sh = bit & 63;
    const uint64_t v = (in[idx] >> sh) | (in[idx + 1] << 1 << (63 - sh));
    out[i] = (int32_t)((uint32_t)(v & mask) + base);
  }
}

// ------------------------------------------------------------------------------------------------ hachage
static inline uint64_t rotl(uint64_t x, int r) { return (x << r) | (x >> (64 - r)); }
static inline uint64_t load64(const uint8_t *p) { uint64_t v; memcpy(&v, p, 8); return v; }
static inline uint64_t hash64(uint64_t k) { k *= K1; return k ^ (k >> 32); }
// Octets : deux voies de mots de 64 bits ; le dernier mot, incomplet, est masqué (8 octets lisibles après la fin).
static inline uint64_t hash_bytes(const uint8_t *p, uint32_t n) {
  uint64_t h1 = K1 ^ n, h2 = K2;
  while (n >= 16) {
    h1 = (rotl(h1, 5) ^ load64(p)) * K1;
    h2 = (rotl(h2, 5) ^ load64(p + 8)) * K2;
    p += 16; n -= 16;
  }
  if (n >= 8) { h1 = (rotl(h1, 5) ^ load64(p)) * K1; p += 8; n -= 8; }
  if (n) h2 = (rotl(h2, 5) ^ (load64(p) & ((1ull << (8 * n)) - 1))) * K2;
  uint64_t h = (h1 ^ rotl(h2, 32)) * K1;
  h ^= h >> 32;
  return h ? h : 1;  // 0 marque une case vide
}
static inline uint32_t part_of(uint64_t h) { return (uint32_t)(h >> (64 - PBITS)); }

// ------------------------------------------------------------------------------------------------ table de hachage
// Adressage ouvert, sondage linéaire, capacité en puissance de deux, clé et valeur dans la même case ; doublement
// quand la table est à moitié pleine. Clés entières positives ou nulles ; -1 marque une case vide.
typedef struct { int64_t key, val; } Cell;
typedef struct { Cell *cells; uint64_t mask, count; Arena *arena; } Map;

static void map_init(Map *m, Arena *a, uint64_t cap) {
  m->arena = a; m->mask = cap - 1; m->count = 0;
  m->cells = arena_alloc(a, cap * sizeof(Cell));
  memset(m->cells, 0xFF, cap * sizeof(Cell));
}
static uint64_t pow2_for(uint64_t n) {  // capacité pour n clés : au moins le double, 16 au moins
  uint64_t cap = 16;
  while (cap < 2 * n) cap *= 2;
  return cap;
}
// Capacité de départ d'une table d'agrégation qui recevra n tuples : celle d'un huitième de n clés ; elle double
// ensuite à la demande.
static uint64_t pow2_start(uint64_t n) { return pow2_for(n / 8); }
static inline Cell *map_find_h(const Map *m, int64_t key, uint64_t h) {  // h : hash64 de la clé
  for (uint64_t i = h & m->mask;; i = (i + 1) & m->mask) {
    Cell *c = &m->cells[i];
    if (c->key == key) return c;
    if (c->key == -1) return NULL;
  }
}
static inline Cell *map_find(const Map *m, int64_t key) { return map_find_h(m, key, hash64((uint64_t)key)); }
static void map_grow(Map *m) {
  Map old = *m;
  map_init(m, old.arena, 2 * (old.mask + 1));
  for (uint64_t j = 0; j <= old.mask; j++)
    if (old.cells[j].key != -1) {
      uint64_t i = hash64((uint64_t)old.cells[j].key) & m->mask;
      while (m->cells[i].key != -1) i = (i + 1) & m->mask;
      m->cells[i] = old.cells[j];
    }
  m->count = old.count;
}
// Rend la case de la clé, créée avec la valeur 0 si elle manquait (*fresh le dit).
static inline Cell *map_upsert(Map *m, int64_t key, int *fresh) {
  if ((m->count + 1) * 2 > m->mask + 1) map_grow(m);
  for (uint64_t i = hash64((uint64_t)key) & m->mask;; i = (i + 1) & m->mask) {
    Cell *c = &m->cells[i];
    if (c->key == key) { *fresh = 0; return c; }
    if (c->key == -1) { c->key = key; c->val = 0; m->count++; *fresh = 1; return c; }
  }
}

// Filtre de Bloom par blocs, devant les sondes de semi-jointure : 16 bits par clé, deux bits dans un même mot de
// 64 bits. Un refus est sûr ; une acceptation se confirme dans la table.
typedef struct { uint64_t *bits; uint64_t mask; } Bloom;
static void bloom_init(Bloom *f, Arena *a, uint64_t nkeys) {
  uint64_t words = 64;
  while (words * 4 < nkeys) words *= 2;
  f->bits = arena_alloc(a, words * 8);
  memset(f->bits, 0, words * 8);
  f->mask = words - 1;
}
static inline uint64_t bloom_bits(uint64_t h) { return 1ull << (h & 63) | 1ull << ((h >> 6) & 63); }
static inline void bloom_add(Bloom *f, uint64_t h) { f->bits[(h >> 12) & f->mask] |= bloom_bits(h); }
static inline int bloom_test(const Bloom *f, uint64_t h) {
  const uint64_t m = bloom_bits(h);
  return (f->bits[(h >> 12) & f->mask] & m) == m;
}

// Même table pour des clés faites d'un entier et d'une chaîne : la case garde le hachage, l'entier, la position
// et la longueur de la chaîne, et un compte. Hachage nul : case vide.
typedef struct { uint64_t hash; int64_t ikey; uint64_t ref; uint32_t len, count; } SCell;
typedef struct { SCell *cells; uint64_t mask, n; Arena *arena; const uint8_t *bytes; } SMap;

static void smap_init(SMap *m, Arena *a, uint64_t cap, const uint8_t *bytes) {
  m->arena = a; m->mask = cap - 1; m->n = 0; m->bytes = bytes;
  m->cells = arena_alloc(a, cap * sizeof(SCell));
  memset(m->cells, 0, cap * sizeof(SCell));
}
static void smap_grow(SMap *m) {
  SMap old = *m;
  smap_init(m, old.arena, 2 * (old.mask + 1), old.bytes);
  for (uint64_t j = 0; j <= old.mask; j++)
    if (old.cells[j].hash) {
      uint64_t i = old.cells[j].hash & m->mask;
      while (m->cells[i].hash) i = (i + 1) & m->mask;
      m->cells[i] = old.cells[j];
    }
  m->n = old.n;
}
static inline void smap_add(SMap *m, uint64_t hash, int64_t ikey, uint64_t ref, uint32_t len) {
  if ((m->n + 1) * 2 > m->mask + 1) smap_grow(m);
  for (uint64_t i = hash & m->mask;; i = (i + 1) & m->mask) {
    SCell *c = &m->cells[i];
    if (c->hash == hash && c->ikey == ikey && c->len == len && !memcmp(m->bytes + c->ref, m->bytes + ref, len)) {
      c->count++;
      return;
    }
    if (!c->hash) { *c = (SCell){hash, ikey, ref, len, 1}; m->n++; return; }
  }
}

// ------------------------------------------------------------------------------------------------ partitions
// Tampons d'un fil : pour chaque partition, une liste de morceaux de CHUNK octets pris dans son arène.
typedef struct PChunk { struct PChunk *next; uint32_t used, pad; } PChunk;
typedef struct { uint8_t *cur[NPART], *end[NPART]; PChunk *head[NPART], *tail[NPART]; uint32_t tsize; Arena *arena; } Parts;

static void parts_init(Parts *p, Arena *a, uint32_t tsize) {
  memset(p, 0, sizeof *p);
  p->tsize = tsize; p->arena = a;
}
static uint8_t *parts_chunk(Parts *p, uint32_t k) {
  PChunk *c = arena_alloc(p->arena, sizeof(PChunk) + CHUNK);
  c->next = NULL; c->used = 0;
  if (p->tail[k]) { p->tail[k]->used = (uint32_t)(p->cur[k] - (uint8_t *)(p->tail[k] + 1)); p->tail[k]->next = c; }
  else p->head[k] = c;
  p->tail[k] = c;
  p->cur[k] = (uint8_t *)(c + 1);
  p->end[k] = p->cur[k] + CHUNK / p->tsize * p->tsize;
  return p->cur[k];
}
static inline void *parts_push(Parts *p, uint32_t k) {
  uint8_t *t = p->cur[k];
  if (t == p->end[k]) t = parts_chunk(p, k);
  p->cur[k] = t + p->tsize;
  return t;
}
static void parts_close(Parts *p) {
  for (uint32_t k = 0; k < NPART; k++)
    if (p->tail[k]) p->tail[k]->used = (uint32_t)(p->cur[k] - (uint8_t *)(p->tail[k] + 1));
}
static uint64_t parts_count(const Parts *p, int nt, uint32_t k) {
  uint64_t n = 0;
  for (int t = 0; t < nt; t++)
    for (const PChunk *c = p[t].head[k]; c; c = c->next) n += c->used / p[t].tsize;
  return n;
}
// Parcours des tuples (de type T) de la partition k dans les tampons de tous les fils.
#define PARTS_EACH(T, var, parts, nt, k)                                               \
  for (int t_ = 0; t_ < (nt); t_++)                                                   \
    for (const PChunk *c_ = (parts)[t_].head[k]; c_; c_ = c_->next)                   \
      for (const T *var = (const T *)(c_ + 1), *e_ = (const T *)((const uint8_t *)(c_ + 1) + c_->used); var < e_; var++)

// ------------------------------------------------------------------------------------------------ état des fils
typedef struct {
  int32_t a[VEC], b[VEC], c[VEC], d[VEC], e[VEC], f[VEC], g[VEC], sel[VEC], sel2[VEC], sel3[VEC], pos[VEC];
  int64_t x[VEC], y[VEC];
  uint64_t h[VEC];
  int32_t len[BLOCK], rows[BLOCK];
} Scratch;
static int NT;
static Arena arena[MAXT];
static Scratch *scratch[MAXT];
static Parts parts[MAXT], parts2[MAXT];
#ifdef PHASES
static void parts_stats(const char *name, const Parts *p) {  // tuples par partition : plus petite, moyenne, plus grande
  uint64_t lo = UINT64_MAX, hi = 0, sum = 0;
  for (uint32_t k = 0; k < NPART; k++) {
    const uint64_t n = parts_count(p, NT, k);
    lo = n < lo ? n : lo; hi = n > hi ? n : hi; sum += n;
  }
  fprintf(stderr, "  %-28s partitions : %llu à %llu tuples, %.0f en moyenne\n", name, (unsigned long long)lo,
          (unsigned long long)hi, (double)sum / NPART);
}
#endif

// Liste d'entiers de 64 bits dans une arène.
typedef struct { int64_t *v; uint64_t n, cap; Arena *a; } List;
static void list_init(List *l, Arena *a) { l->v = NULL; l->n = l->cap = 0; l->a = a; }
static inline void list_push(List *l, int64_t x) {
  if (l->n == l->cap) {
    uint64_t cap = l->cap ? 2 * l->cap : 1024;
    int64_t *v = arena_alloc(l->a, cap * 8);
    if (l->n) memcpy(v, l->v, l->n * 8);
    l->v = v; l->cap = cap;
  }
  l->v[l->n++] = x;
}

// ------------------------------------------------------------------------------------------------ résultat
static char *res;
static size_t res_len, res_cap;
static void out_bytes(const void *p, size_t n) {
  if (res_len + n > res_cap) { res_cap = 2 * (res_len + n) + 4096; res = realloc(res, res_cap); }
  memcpy(res + res_len, p, n);
  res_len += n;
}
static void out(const char *fmt, ...) {
  char buf[512];
  va_list ap;
  va_start(ap, fmt);
  int n = vsnprintf(buf, sizeof buf, fmt, ap);
  va_end(ap);
  out_bytes(buf, (size_t)n);
}
static uint64_t fnv1a(const char *p, size_t n) {
  uint64_t h = 0xCBF29CE484222325ull;
  for (size_t i = 0; i < n; i++) { h ^= (uint8_t)p[i]; h *= 0x100000001B3ull; }
  return h;
}

// ------------------------------------------------------------------------------------------------ diagnostic
// -DPHASES : temps de chaque phase sur la sortie d'erreur. Absent des binaires mesurés.
#ifdef PHASES
static double phase_t;
static double phase_now(void) {
  struct timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return (double)t.tv_sec + 1e-9 * (double)t.tv_nsec;
}
#define PHASE_START() (phase_t = phase_now())
#define PHASE(name) { const double t_ = phase_now(); fprintf(stderr, "  %-28s %8.1f ms\n", name, 1e3 * (t_ - phase_t)); phase_t = t_; }
#define PARTS_STATS(name, p) parts_stats(name, p)
#else
#define PHASE_START()
#define PHASE(name)
#define PARTS_STATS(name, p)
#endif

// ------------------------------------------------------------------------------------------------ dates
static int32_t days_from_civil(int y, int m, int d) {  // jours depuis le 1er janvier 1970
  y -= m <= 2;
  const int era = (y >= 0 ? y : y - 399) / 400;
  const unsigned yoe = (unsigned)(y - era * 400);
  const unsigned doy = (153u * (unsigned)(m + (m > 2 ? -3 : 9)) + 2) / 5 + (unsigned)d - 1;
  const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + (int)doe - 719468;
}
static int32_t year_start[200];  // premier jour de chaque année à partir de 1970
static inline int32_t year_of(int32_t days) {
  int y = days / 366;
  while (year_start[y + 1] <= days) y++;
  return 1970 + y;
}

// ------------------------------------------------------------------------------------------------ sous-chaînes
// Lignes d'un bloc de chaînes qui contiennent l'aiguille (2 octets au moins) : les octets du bloc sont parcourus
// d'un trait, par mots de 8 octets ; un mot est candidat si, à une même position, il porte le premier octet de
// l'aiguille et le mot décalé de sa longueur moins un porte le dernier. Une occurrence compte si elle tient dans
// une ligne, et une ligne compte une fois.
#define ONES 0x0101010101010101ull
#define HIGHS 0x8080808080808080ull
static inline uint64_t zero_bytes(uint64_t x) {  // bit de poids fort de chaque octet nul de x, exactement
  return ~(((x & ~HIGHS) + ~HIGHS) | x) & HIGHS;
}
static uint32_t search_block(const uint8_t *buf, uint64_t nbytes, const int32_t *len, const uint8_t *needle,
                             uint32_t m, int32_t *rows) {
  uint32_t r = 0, k = 0;
  uint64_t row_end = nbytes ? (uint64_t)len[0] : 0;
  const uint64_t first = ONES * needle[0], last = ONES * needle[m - 1];
  const uint64_t stop = nbytes >= m ? nbytes - m + 1 : 0;  // positions de départ possibles : [0, stop)
  for (uint64_t i = 0; i < stop;) {
    uint64_t cand;
    if (i + 8 <= stop) {  // les deux mots sont dans le bloc
      cand = zero_bytes((load64(buf + i) ^ first) | (load64(buf + i + m - 1) ^ last));
      if (!cand) { i += 8; continue; }
    } else {
      cand = 0;
      for (uint64_t j = i; j < stop; j++)
        if (buf[j] == needle[0] && buf[j + m - 1] == needle[m - 1]) cand |= 0x80ull << (8 * (j - i));
    }
    uint64_t next = i + 8;
    for (; cand; cand &= cand - 1) {
      const uint64_t at = i + ((uint64_t)stdc_trailing_zeros(cand) >> 3);
      if (memcmp(buf + at + 1, needle + 1, m - 2)) continue;
      while (row_end <= at) row_end += (uint64_t)len[++r];
      if (at + m <= row_end) { rows[k++] = (int32_t)r; next = row_end; break; }  // la suite de la ligne est sautée
    }
    i = next;
  }
  return k;
}
// Longueurs d'un bloc de chaînes (dans len) ; rend le nombre de ses octets.
static uint64_t block_lengths(const Col *c, uint64_t b, int32_t *len) {
  const uint32_t n = c->dir[b].count;
  unpack(c, b, 0, n, len);
  uint64_t total = 0;
  for (uint32_t i = 0; i < n; i++) total += (uint64_t)len[i];
  return total;
}

// ------------------------------------------------------------------------------------------------ dix premiers
typedef struct { uint32_t count, len; int64_t ikey; uint64_t ref; } Top;
typedef struct { Top t[10]; int n; } Top10;
static const uint8_t *top_bytes;
static int top_before(const Top *a, const Top *b) {  // ordre : compte décroissant, entier croissant, chaîne croissante
  if (a->count != b->count) return a->count > b->count;
  if (a->ikey != b->ikey) return a->ikey < b->ikey;
  const uint32_t n = a->len < b->len ? a->len : b->len;
  const int c = memcmp(top_bytes + a->ref, top_bytes + b->ref, n);
  return c ? c < 0 : a->len < b->len;
}
static void top_add(Top10 *t, Top x) {
  if (t->n == 10 && !top_before(&x, &t->t[9])) return;
  int i = t->n < 10 ? t->n++ : 9;
  for (; i > 0 && top_before(&x, &t->t[i - 1]); i--) t->t[i] = t->t[i - 1];
  t->t[i] = x;
}

// ================================================================================================ T1 (TPC-H Q1)
typedef struct { int64_t qty, base, disc_price, charge, disc, count, pad[2]; } Agg1;
static struct { Col ship, rf, ls, qty, ext, disc, tax; Counter ctr; int32_t cut; Agg1 agg[MAXT][6]; } t1;

static void t1_task(int tid) {
  Scratch *s = scratch[tid];
  Agg1 agg[6];
  memset(agg, 0, sizeof agg);
  for (int64_t b; (b = take(&t1.ctr)) >= 0;) {
    const Entry *e = &t1.ship.dir[b];
    if (e->min > t1.cut) continue;        // bloc exclu par sa carte de zones
    const int all = e->max <= t1.cut;     // bloc retenu en entier : le filtre n'est pas évalué
    for (uint32_t st = 0; st < e->count; st += VEC) {
      const uint32_t n = e->count - st < VEC ? e->count - st : VEC;
      unpack(&t1.rf, b, st, n, s->a);
      unpack(&t1.ls, b, st, n, s->b);
      unpack(&t1.qty, b, st, n, s->c);
      unpack(&t1.ext, b, st, n, s->d);
      unpack(&t1.disc, b, st, n, s->e);
      unpack(&t1.tax, b, st, n, s->f);
      for (uint32_t i = 0; i < n; i++) s->x[i] = (int64_t)s->d[i] * (100 - s->e[i]);
      for (uint32_t i = 0; i < n; i++) s->y[i] = s->x[i] * (100 + s->f[i]);
      for (uint32_t i = 0; i < n; i++) s->g[i] = s->a[i] * 2 + s->b[i];
#define T1_ADD(i)                                                                                    \
  { Agg1 *g = &agg[s->g[i]]; g->qty += s->c[i]; g->base += s->d[i]; g->disc_price += s->x[i];       \
    g->charge += s->y[i]; g->disc += s->e[i]; g->count++; }
      if (all) {
        for (uint32_t i = 0; i < n; i++) T1_ADD(i)
      } else {
        unpack(&t1.ship, b, st, n, s->pos);
        uint32_t k = 0;
        for (uint32_t i = 0; i < n; i++) { s->sel[k] = (int32_t)i; k += s->pos[i] <= t1.cut; }
        for (uint32_t j = 0; j < k; j++) { const uint32_t i = (uint32_t)s->sel[j]; T1_ADD(i) }
      }
    }
  }
  memcpy(t1.agg[tid], agg, sizeof agg);
}
static void t1_open(void) {
  t1.ship = col_open("lineitem", "l_shipdate"); t1.rf = col_open("lineitem", "l_returnflag");
  t1.ls = col_open("lineitem", "l_linestatus"); t1.qty = col_open("lineitem", "l_quantity");
  t1.ext = col_open("lineitem", "l_extendedprice"); t1.disc = col_open("lineitem", "l_discount");
  t1.tax = col_open("lineitem", "l_tax");
  t1.cut = days_from_civil(1998, 9, 2);
}
static void t1_run(void) {
  counter_set(&t1.ctr, t1.ship.nblocks);
  run(t1_task);
  for (int g = 0; g < 6; g++) {
    Agg1 a = {0};
    for (int t = 0; t < NT; t++) {
      const Agg1 *x = &t1.agg[t][g];
      a.qty += x->qty; a.base += x->base; a.disc_price += x->disc_price; a.charge += x->charge; a.disc += x->disc;
      a.count += x->count;
    }
    if (!a.count) continue;
    uint32_t n1, n2;
    const uint8_t *rf = dict_entry(&t1.rf, (uint32_t)g / 2, &n1), *ls = dict_entry(&t1.ls, (uint32_t)g % 2, &n2);
    out_bytes(rf, n1); out("|"); out_bytes(ls, n2);
    out("|%lld|%lld|%lld|%lld|%lld|%lld\n", (long long)a.qty, (long long)a.base, (long long)a.disc_price,
        (long long)a.charge, (long long)a.disc, (long long)a.count);
  }
}

// ================================================================================================ T6 (TPC-H Q6)
static struct { Col ship, disc, qty, ext; Counter ctr; int32_t lo, hi; int64_t sum[MAXT][8]; } t6;

static void t6_task(int tid) {
  Scratch *s = scratch[tid];
  int64_t sum = 0;
  for (int64_t b; (b = take(&t6.ctr)) >= 0;) {
    const Entry *e = &t6.ship.dir[b];
    if (e->max < t6.lo || e->min >= t6.hi) continue;
    for (uint32_t st = 0; st < e->count; st += VEC) {
      const uint32_t n = e->count - st < VEC ? e->count - st : VEC;
      unpack(&t6.ship, b, st, n, s->a);
      uint32_t k = 0;
      for (uint32_t i = 0; i < n; i++) { s->pos[k] = (int32_t)(st + i); k += (s->a[i] >= t6.lo) & (s->a[i] < t6.hi); }
      if (!k) continue;
      unpack_sel(&t6.disc, b, s->pos, k, s->b);
      uint32_t k2 = 0;
      for (uint32_t i = 0; i < k; i++) {
        s->sel[k2] = s->pos[i]; s->c[k2] = s->b[i];
        k2 += (s->b[i] >= 5) & (s->b[i] <= 7);
      }
      if (!k2) continue;
      unpack_sel(&t6.qty, b, s->sel, k2, s->d);
      uint32_t k3 = 0;
      for (uint32_t i = 0; i < k2; i++) {
        s->sel2[k3] = s->sel[i]; s->e[k3] = s->c[i];
        k3 += s->d[i] < 2400;
      }
      if (!k3) continue;
      unpack_sel(&t6.ext, b, s->sel2, k3, s->f);
      for (uint32_t i = 0; i < k3; i++) sum += (int64_t)s->f[i] * s->e[i];
    }
  }
  t6.sum[tid][0] = sum;
}
static void t6_open(void) {
  t6.ship = col_open("lineitem", "l_shipdate"); t6.disc = col_open("lineitem", "l_discount");
  t6.qty = col_open("lineitem", "l_quantity"); t6.ext = col_open("lineitem", "l_extendedprice");
  t6.lo = days_from_civil(1994, 1, 1); t6.hi = days_from_civil(1995, 1, 1);
}
static void t6_run(void) {
  counter_set(&t6.ctr, t6.ship.nblocks);
  run(t6_task);
  int64_t sum = 0;
  for (int t = 0; t < NT; t++) sum += t6.sum[t][0];
  out("%lld\n", (long long)sum);
}

// ================================================================================================ T9 (TPC-H Q9)
// 1. part : noms qui contiennent « green » -> ensemble de pièces (table et filtre de Bloom) ;
// 2. partsupp : lignes de ces pièces -> (pièce, fournisseur) -> coût ; 3. supplier -> nation ;
// 4. lineitem : lignes de ces pièces, montant et nation, réparties par commande ;
// 5. orders : (commande, date) réparties de même ; 6. par partition : table des lignes de lineitem, sondée par les
//    commandes ; agrégat par nation et année.
typedef struct { int32_t okey, nation; int64_t amount; } T9Tuple;
typedef struct { int32_t okey, date; } T9Order;
static struct {
  Col p_partkey, p_name, ps_partkey, ps_suppkey, ps_cost, s_suppkey, s_nationkey, n_nationkey, n_name, l_partkey,
      l_suppkey, l_orderkey, l_qty, l_ext, l_disc, o_orderkey, o_orderdate;
  Counter ctr;
  List l1[MAXT], l2[MAXT];  // listes des fils
  Map part, ps, supp, agg[MAXT];
  Bloom fpart;
} t9;

static void t9_part_task(int tid) {
  Scratch *s = scratch[tid];
  list_init(&t9.l1[tid], &arena[tid]);
  for (int64_t b; (b = take(&t9.ctr)) >= 0;) {
    const uint64_t nbytes = block_lengths(&t9.p_name, (uint64_t)b, s->len);
    const uint32_t k = search_block(t9.p_name.aux + t9.p_name.dir[b].aux_off, nbytes, s->len,
                                    (const uint8_t *)"green", 5, s->rows);
    for (uint32_t i = 0; i < k; i += VEC) {
      const uint32_t n = k - i < VEC ? k - i : VEC;
      unpack_sel(&t9.p_partkey, (uint64_t)b, s->rows + i, n, s->a);
      for (uint32_t j = 0; j < n; j++) list_push(&t9.l1[tid], s->a[j]);
    }
  }
}
// Positions (dans le bloc) et clés des lignes d'un vecteur dont la clé est dans l'ensemble des pièces.
static inline uint32_t t9_semi(const int32_t *key, uint32_t n, uint32_t st, int32_t *pos, int32_t *out) {
  uint32_t k = 0;
  for (uint32_t i = 0; i < n; i++) {
    const uint64_t h = hash64((uint64_t)key[i]);
    if (bloom_test(&t9.fpart, h) && map_find_h(&t9.part, key[i], h)) { pos[k] = (int32_t)(st + i); out[k++] = key[i]; }
  }
  return k;
}
static void t9_ps_task(int tid) {
  Scratch *s = scratch[tid];
  list_init(&t9.l1[tid], &arena[tid]);
  list_init(&t9.l2[tid], &arena[tid]);
  for (int64_t b; (b = take(&t9.ctr)) >= 0;) {
    const uint32_t count = t9.ps_partkey.dir[b].count;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&t9.ps_partkey, (uint64_t)b, st, n, s->a);
      const uint32_t k = t9_semi(s->a, n, st, s->pos, s->b);
      if (!k) continue;
      unpack_sel(&t9.ps_suppkey, (uint64_t)b, s->pos, k, s->c);
      unpack_sel(&t9.ps_cost, (uint64_t)b, s->pos, k, s->d);
      for (uint32_t i = 0; i < k; i++) {
        list_push(&t9.l1[tid], (int64_t)s->b[i] << 32 | s->c[i]);
        list_push(&t9.l2[tid], s->d[i]);
      }
    }
  }
}
static void t9_line_task(int tid) {
  Scratch *s = scratch[tid];
  Parts *p = &parts[tid];
  parts_init(p, &arena[tid], sizeof(T9Tuple));
  for (int64_t b; (b = take(&t9.ctr)) >= 0;) {
    const uint32_t count = t9.l_partkey.dir[b].count;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&t9.l_partkey, (uint64_t)b, st, n, s->a);
      const uint32_t k = t9_semi(s->a, n, st, s->pos, s->b);
      if (!k) continue;
      unpack_sel(&t9.l_suppkey, (uint64_t)b, s->pos, k, s->c);
      unpack_sel(&t9.l_orderkey, (uint64_t)b, s->pos, k, s->d);
      unpack_sel(&t9.l_qty, (uint64_t)b, s->pos, k, s->e);
      unpack_sel(&t9.l_ext, (uint64_t)b, s->pos, k, s->f);
      unpack_sel(&t9.l_disc, (uint64_t)b, s->pos, k, s->g);
      for (uint32_t i = 0; i < k; i++) {
        const int64_t cost = map_find(&t9.ps, (int64_t)s->b[i] << 32 | s->c[i])->val;
        const int64_t nation = map_find(&t9.supp, s->c[i])->val;
        T9Tuple *t = parts_push(p, part_of(hash64((uint64_t)s->d[i])));
        t->okey = s->d[i]; t->nation = (int32_t)nation;
        t->amount = (int64_t)s->f[i] * (100 - s->g[i]) - cost * s->e[i];
      }
    }
  }
  parts_close(p);
}
static void t9_orders_task(int tid) {
  Scratch *s = scratch[tid];
  Parts *p = &parts2[tid];
  parts_init(p, &arena[tid], sizeof(T9Order));
  for (int64_t b; (b = take(&t9.ctr)) >= 0;) {
    const uint32_t count = t9.o_orderkey.dir[b].count;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&t9.o_orderkey, (uint64_t)b, st, n, s->a);
      unpack(&t9.o_orderdate, (uint64_t)b, st, n, s->b);
      for (uint32_t i = 0; i < n; i++) s->h[i] = hash64((uint64_t)s->a[i]);
      for (uint32_t i = 0; i < n; i++) {
        T9Order *t = parts_push(p, part_of(s->h[i]));
        t->okey = s->a[i]; t->date = s->b[i];
      }
    }
  }
  parts_close(p);
}
static void t9_join_task(int tid) {
  Map *agg = &t9.agg[tid];
  map_init(agg, &arena[tid], 1024);
  for (int64_t k; (k = take(&t9.ctr)) >= 0;) {
    const uint64_t n = parts_count(parts, NT, (uint32_t)k);
    if (!n) continue;
    T9Tuple *tu = arena_alloc(&arena[tid], n * sizeof(T9Tuple));
    int32_t *next = arena_alloc(&arena[tid], n * sizeof(int32_t));
    Map m;  // commande -> rang de son dernier tuple ; next chaîne les tuples d'une même commande
    map_init(&m, &arena[tid], pow2_for(n));
    uint64_t i = 0;
    PARTS_EACH(T9Tuple, t, parts, NT, k) {
      int fresh;
      Cell *c = map_upsert(&m, t->okey, &fresh);
      tu[i] = *t;
      next[i] = fresh ? -1 : (int32_t)c->val;
      c->val = (int64_t)i++;
    }
    PARTS_EACH(T9Order, o, parts2, NT, k) {
      const Cell *c = map_find(&m, o->okey);
      if (!c) continue;
      const int64_t year = year_of(o->date);
      for (int32_t j = (int32_t)c->val; j >= 0; j = next[j]) {
        int fresh;
        map_upsert(agg, (int64_t)tu[j].nation << 16 | year, &fresh)->val += tu[j].amount;
      }
    }
  }
}
static void t9_open(void) {
  t9.p_partkey = col_open("part", "p_partkey"); t9.p_name = col_open("part", "p_name");
  t9.ps_partkey = col_open("partsupp", "ps_partkey"); t9.ps_suppkey = col_open("partsupp", "ps_suppkey");
  t9.ps_cost = col_open("partsupp", "ps_supplycost"); t9.s_suppkey = col_open("supplier", "s_suppkey");
  t9.s_nationkey = col_open("supplier", "s_nationkey"); t9.n_nationkey = col_open("nation", "n_nationkey");
  t9.n_name = col_open("nation", "n_name"); t9.l_partkey = col_open("lineitem", "l_partkey");
  t9.l_suppkey = col_open("lineitem", "l_suppkey"); t9.l_orderkey = col_open("lineitem", "l_orderkey");
  t9.l_qty = col_open("lineitem", "l_quantity"); t9.l_ext = col_open("lineitem", "l_extendedprice");
  t9.l_disc = col_open("lineitem", "l_discount"); t9.o_orderkey = col_open("orders", "o_orderkey");
  t9.o_orderdate = col_open("orders", "o_orderdate");
}
typedef struct { const uint8_t *name; uint32_t len; int64_t year, sum; } T9Row;
static int t9_cmp(const void *pa, const void *pb) {
  const T9Row *a = pa, *b = pb;
  const uint32_t n = a->len < b->len ? a->len : b->len;
  const int c = memcmp(a->name, b->name, n);
  if (c) return c;
  if (a->len != b->len) return a->len < b->len ? -1 : 1;
  return a->year > b->year ? -1 : a->year < b->year;
}
static void t9_run(void) {
  Arena *a0 = &arena[0];
  Scratch *s = scratch[0];
  PHASE_START();
  counter_set(&t9.ctr, t9.p_name.nblocks);
  run(t9_part_task);
  PHASE("t9 part : recherche");
  uint64_t n = 0;
  for (int t = 0; t < NT; t++) n += t9.l1[t].n;
  map_init(&t9.part, a0, pow2_for(n));
  bloom_init(&t9.fpart, a0, n);
  for (int t = 0; t < NT; t++)
    for (uint64_t i = 0; i < t9.l1[t].n; i++) {
      int fresh;
      map_upsert(&t9.part, t9.l1[t].v[i], &fresh);
      bloom_add(&t9.fpart, hash64((uint64_t)t9.l1[t].v[i]));
    }
  PHASE("t9 part : table et filtre");
  counter_set(&t9.ctr, t9.ps_partkey.nblocks);
  run(t9_ps_task);
  PHASE("t9 partsupp : parcours");
  n = 0;
  for (int t = 0; t < NT; t++) n += t9.l1[t].n;
  map_init(&t9.ps, a0, pow2_for(n));
  for (int t = 0; t < NT; t++)
    for (uint64_t i = 0; i < t9.l1[t].n; i++) { int fresh; map_upsert(&t9.ps, t9.l1[t].v[i], &fresh)->val = t9.l2[t].v[i]; }
  map_init(&t9.supp, a0, pow2_for(t9.s_suppkey.nrows));
  for (uint64_t b = 0; b < t9.s_suppkey.nblocks; b++) {
    const uint32_t count = t9.s_suppkey.dir[b].count;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t m = count - st < VEC ? count - st : VEC;
      unpack(&t9.s_suppkey, b, st, m, s->a);
      unpack(&t9.s_nationkey, b, st, m, s->b);
      for (uint32_t i = 0; i < m; i++) { int fresh; map_upsert(&t9.supp, s->a[i], &fresh)->val = s->b[i]; }
    }
  }
  PHASE("t9 partsupp, supplier : tables");
  counter_set(&t9.ctr, t9.l_partkey.nblocks);
  run(t9_line_task);
  PHASE("t9 lineitem");
  counter_set(&t9.ctr, t9.o_orderkey.nblocks);
  run(t9_orders_task);
  PHASE("t9 orders : répartition");
  PARTS_STATS("t9 lineitem", parts);
  PARTS_STATS("t9 orders", parts2);
  counter_set(&t9.ctr, NPART);
  run(t9_join_task);
  PHASE("t9 jointure par partition");
  // fusion ; nation -> nom ; tri par nom puis année décroissante
  Map total;
  map_init(&total, a0, 1024);
  for (int t = 0; t < NT; t++)
    for (uint64_t j = 0; j <= t9.agg[t].mask; j++)
      if (t9.agg[t].cells[j].key != -1) {
        int fresh;
        map_upsert(&total, t9.agg[t].cells[j].key, &fresh)->val += t9.agg[t].cells[j].val;
      }
  Map nat;
  map_init(&nat, a0, 64);
  unpack(&t9.n_nationkey, 0, 0, (uint32_t)t9.n_nationkey.nrows, s->a);
  unpack(&t9.n_name, 0, 0, (uint32_t)t9.n_name.nrows, s->b);
  for (uint32_t i = 0; i < t9.n_nationkey.nrows; i++) { int fresh; map_upsert(&nat, s->a[i], &fresh)->val = s->b[i]; }
  T9Row *rows = arena_alloc(a0, (total.count + 1) * sizeof(T9Row));
  uint64_t nr = 0;
  for (uint64_t j = 0; j <= total.mask; j++)
    if (total.cells[j].key != -1) {
      T9Row *r = &rows[nr++];
      r->name = dict_entry(&t9.n_name, (uint32_t)map_find(&nat, total.cells[j].key >> 16)->val, &r->len);
      r->year = total.cells[j].key & 0xFFFF;
      r->sum = total.cells[j].val;
    }
  qsort(rows, nr, sizeof(T9Row), t9_cmp);
  for (uint64_t i = 0; i < nr; i++) {
    out_bytes(rows[i].name, rows[i].len);
    out("|%lld|%lld\n", (long long)rows[i].year, (long long)rows[i].sum);
  }
}

// ================================================================================================ T18 (TPC-H Q18)
typedef struct { int32_t key, qty; } KQ;
typedef struct { int64_t okey, cust, date, price, sum; const uint8_t *name; uint32_t len; } T18Row;
static struct {
  Col l_orderkey, l_qty, o_orderkey, o_custkey, o_orderdate, o_totalprice, c_custkey, c_name;
  Counter ctr;
  List l1[MAXT], l2[MAXT], l3[MAXT], l4[MAXT];
  Map big, cust, sums[MAXT];
  Bloom fbig, fcust;
} t18;

static void t18_scatter_task(int tid) {  // lineitem réparti par commande
  Scratch *s = scratch[tid];
  Parts *p = &parts[tid];
  parts_init(p, &arena[tid], sizeof(KQ));
  for (int64_t b; (b = take(&t18.ctr)) >= 0;) {
    const uint32_t count = t18.l_orderkey.dir[b].count;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&t18.l_orderkey, (uint64_t)b, st, n, s->a);
      unpack(&t18.l_qty, (uint64_t)b, st, n, s->b);
      for (uint32_t i = 0; i < n; i++) s->h[i] = hash64((uint64_t)s->a[i]);
      for (uint32_t i = 0; i < n; i++) {
        KQ *t = parts_push(p, part_of(s->h[i]));
        t->key = s->a[i]; t->qty = s->b[i];
      }
    }
  }
  parts_close(p);
}
static void t18_agg_task(int tid) {  // une partition : somme par commande ; garde celles de plus de 300 unités
  list_init(&t18.l1[tid], &arena[tid]);
  for (int64_t k; (k = take(&t18.ctr)) >= 0;) {
    Map m;
    map_init(&m, &arena[tid], pow2_start(parts_count(parts, NT, (uint32_t)k)));
    PARTS_EACH(KQ, t, parts, NT, k) {
      int fresh;
      map_upsert(&m, t->key, &fresh)->val += t->qty;
    }
    for (uint64_t j = 0; j <= m.mask; j++)
      if (m.cells[j].key != -1 && m.cells[j].val > 30000) list_push(&t18.l1[tid], m.cells[j].key);
  }
}
static void t18_orders_task(int tid) {  // commandes retenues : client, date, prix
  Scratch *s = scratch[tid];
  list_init(&t18.l1[tid], &arena[tid]); list_init(&t18.l2[tid], &arena[tid]);
  list_init(&t18.l3[tid], &arena[tid]); list_init(&t18.l4[tid], &arena[tid]);
  for (int64_t b; (b = take(&t18.ctr)) >= 0;) {
    const uint32_t count = t18.o_orderkey.dir[b].count;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&t18.o_orderkey, (uint64_t)b, st, n, s->a);
      uint32_t k = 0;
      for (uint32_t i = 0; i < n; i++) {
        const uint64_t h = hash64((uint64_t)s->a[i]);
        if (bloom_test(&t18.fbig, h) && map_find_h(&t18.big, s->a[i], h)) { s->pos[k] = (int32_t)(st + i); s->b[k++] = s->a[i]; }
      }
      if (!k) continue;
      unpack_sel(&t18.o_custkey, (uint64_t)b, s->pos, k, s->c);
      unpack_sel(&t18.o_orderdate, (uint64_t)b, s->pos, k, s->d);
      unpack_sel(&t18.o_totalprice, (uint64_t)b, s->pos, k, s->e);
      for (uint32_t i = 0; i < k; i++) {
        list_push(&t18.l1[tid], s->b[i]); list_push(&t18.l2[tid], s->c[i]);
        list_push(&t18.l3[tid], s->d[i]); list_push(&t18.l4[tid], s->e[i]);
      }
    }
  }
}
static void t18_cust_task(int tid) {  // clients de ces commandes : position et longueur de leur nom
  Scratch *s = scratch[tid];
  list_init(&t18.l1[tid], &arena[tid]); list_init(&t18.l2[tid], &arena[tid]); list_init(&t18.l3[tid], &arena[tid]);
  for (int64_t b; (b = take(&t18.ctr)) >= 0;) {
    const uint32_t count = t18.c_custkey.dir[b].count;
    uint64_t pos = t18.c_name.dir[b].aux_off;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&t18.c_custkey, (uint64_t)b, st, n, s->a);
      unpack(&t18.c_name, (uint64_t)b, st, n, s->b);
      for (uint32_t i = 0; i < n; i++) {
        const uint64_t h = hash64((uint64_t)s->a[i]);
        if (bloom_test(&t18.fcust, h) && map_find_h(&t18.cust, s->a[i], h)) {
          list_push(&t18.l1[tid], s->a[i]); list_push(&t18.l2[tid], (int64_t)pos); list_push(&t18.l3[tid], s->b[i]);
        }
        pos += (uint64_t)s->b[i];
      }
    }
  }
}
static void t18_sum_task(int tid) {  // lineitem des commandes retenues : somme des quantités
  Scratch *s = scratch[tid];
  Map *m = &t18.sums[tid];
  map_init(m, &arena[tid], 1024);
  for (int64_t b; (b = take(&t18.ctr)) >= 0;) {
    const uint32_t count = t18.l_orderkey.dir[b].count;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&t18.l_orderkey, (uint64_t)b, st, n, s->a);
      uint32_t k = 0;
      for (uint32_t i = 0; i < n; i++) {
        const uint64_t h = hash64((uint64_t)s->a[i]);
        if (bloom_test(&t18.fbig, h) && map_find_h(&t18.big, s->a[i], h)) { s->pos[k] = (int32_t)(st + i); s->b[k++] = s->a[i]; }
      }
      if (!k) continue;
      unpack_sel(&t18.l_qty, (uint64_t)b, s->pos, k, s->c);
      for (uint32_t i = 0; i < k; i++) { int fresh; map_upsert(m, s->b[i], &fresh)->val += s->c[i]; }
    }
  }
}
static void t18_open(void) {
  t18.l_orderkey = col_open("lineitem", "l_orderkey"); t18.l_qty = col_open("lineitem", "l_quantity");
  t18.o_orderkey = col_open("orders", "o_orderkey"); t18.o_custkey = col_open("orders", "o_custkey");
  t18.o_orderdate = col_open("orders", "o_orderdate"); t18.o_totalprice = col_open("orders", "o_totalprice");
  t18.c_custkey = col_open("customer", "c_custkey"); t18.c_name = col_open("customer", "c_name");
}
static int t18_cmp(const void *pa, const void *pb) {  // prix décroissant, date, commande
  const T18Row *a = pa, *b = pb;
  if (a->price != b->price) return a->price > b->price ? -1 : 1;
  if (a->date != b->date) return a->date < b->date ? -1 : 1;
  return a->okey < b->okey ? -1 : a->okey > b->okey;
}
static void t18_run(void) {
  Arena *a0 = &arena[0];
  // 1. et 2. agrégation de lineitem par commande ; 3. commandes de plus de 300 unités
  PHASE_START();
  counter_set(&t18.ctr, t18.l_orderkey.nblocks);
  run(t18_scatter_task);
  PHASE("t18 lineitem : répartition");
  PARTS_STATS("t18", parts);
  counter_set(&t18.ctr, NPART);
  run(t18_agg_task);
  PHASE("t18 agrégation");
  uint64_t n = 0;
  for (int t = 0; t < NT; t++) n += t18.l1[t].n;
  map_init(&t18.big, a0, pow2_for(n));
  bloom_init(&t18.fbig, a0, n);
  for (int t = 0; t < NT; t++)
    for (uint64_t i = 0; i < t18.l1[t].n; i++) {
      int fresh;
      map_upsert(&t18.big, t18.l1[t].v[i], &fresh);
      bloom_add(&t18.fbig, hash64((uint64_t)t18.l1[t].v[i]));
    }
  // 4. leurs lignes dans orders
  counter_set(&t18.ctr, t18.o_orderkey.nblocks);
  run(t18_orders_task);
  PHASE("t18 orders");
  T18Row *rows = arena_alloc(a0, (n + 1) * sizeof(T18Row));
  uint64_t nr = 0;
  map_init(&t18.cust, a0, pow2_for(n));
  bloom_init(&t18.fcust, a0, n);
  for (int t = 0; t < NT; t++)
    for (uint64_t i = 0; i < t18.l1[t].n; i++) {
      rows[nr++] = (T18Row){t18.l1[t].v[i], t18.l2[t].v[i], t18.l3[t].v[i], t18.l4[t].v[i], 0, NULL, 0};
      int fresh;
      map_upsert(&t18.cust, t18.l2[t].v[i], &fresh);
      bloom_add(&t18.fcust, hash64((uint64_t)t18.l2[t].v[i]));
    }
  // 5. leurs clients ; 6. leurs lignes dans lineitem
  counter_set(&t18.ctr, t18.c_custkey.nblocks);
  run(t18_cust_task);
  PHASE("t18 customer");
  Map name;  // client -> rang dans les listes des fils
  map_init(&name, a0, pow2_for(n));
  List pos, len;
  list_init(&pos, a0); list_init(&len, a0);
  for (int t = 0; t < NT; t++)
    for (uint64_t i = 0; i < t18.l1[t].n; i++) {
      int fresh;
      map_upsert(&name, t18.l1[t].v[i], &fresh)->val = (int64_t)pos.n;
      list_push(&pos, t18.l2[t].v[i]); list_push(&len, t18.l3[t].v[i]);
    }
  counter_set(&t18.ctr, t18.l_orderkey.nblocks);
  run(t18_sum_task);
  PHASE("t18 lineitem : second parcours");
  for (uint64_t i = 0; i < nr; i++) {
    for (int t = 0; t < NT; t++) {
      const Cell *c = map_find(&t18.sums[t], rows[i].okey);
      if (c) rows[i].sum += c->val;
    }
    const int64_t j = map_find(&name, rows[i].cust)->val;
    rows[i].name = t18.c_name.aux + pos.v[j];
    rows[i].len = (uint32_t)len.v[j];
  }
  qsort(rows, nr, sizeof(T18Row), t18_cmp);
  for (uint64_t i = 0; i < nr && i < 100; i++) {
    out_bytes(rows[i].name, rows[i].len);
    out("|%lld|%lld|%lld|%lld|%lld\n", (long long)rows[i].cust, (long long)rows[i].okey, (long long)rows[i].date,
        (long long)rows[i].price, (long long)rows[i].sum);
  }
}

// ================================================================================================ C4
static struct { Col uid; Counter ctr; uint64_t count[MAXT][8]; int minus1[MAXT][16]; } c4;

static void c4_scatter_task(int tid) {
  Scratch *s = scratch[tid];
  Parts *p = &parts[tid];
  parts_init(p, &arena[tid], 8);
  for (int64_t b; (b = take(&c4.ctr)) >= 0;) {
    const uint32_t count = c4.uid.dir[b].count;
    const int64_t *v = (const int64_t *)block_words(&c4.uid, (uint64_t)b);  // 64 bits : valeurs telles quelles
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      for (uint32_t i = 0; i < n; i++) s->h[i] = hash64((uint64_t)v[st + i]);
      for (uint32_t i = 0; i < n; i++) *(int64_t *)parts_push(p, part_of(s->h[i])) = v[st + i];
    }
  }
  parts_close(p);
}
static void c4_count_task(int tid) {
  uint64_t count = 0;
  int minus1 = 0;
  for (int64_t k; (k = take(&c4.ctr)) >= 0;) {
    Map m;
    map_init(&m, &arena[tid], pow2_start(parts_count(parts, NT, (uint32_t)k)));
    PARTS_EACH(int64_t, t, parts, NT, k) {
      int fresh;
      if (*t == -1) minus1 = 1;  // la valeur qui marque les cases vides est comptée à part
      else map_upsert(&m, *t, &fresh);
    }
    count += m.count;
  }
  c4.count[tid][0] = count;
  c4.minus1[tid][0] = minus1;
}
static void c4_open(void) { c4.uid = col_open("hits", "UserID"); }
static void c4_run(void) {
  PHASE_START();
  counter_set(&c4.ctr, c4.uid.nblocks);
  run(c4_scatter_task);
  PHASE("c4 répartition");
  PARTS_STATS("c4", parts);
  counter_set(&c4.ctr, NPART);
  run(c4_count_task);
  PHASE("c4 comptes");
  uint64_t count = 0;
  int minus1 = 0;
  for (int t = 0; t < NT; t++) { count += c4.count[t][0]; minus1 |= c4.minus1[t][0]; }
  out("%llu\n", (unsigned long long)(count + (uint64_t)minus1));
}

// ================================================================================================ agrégations par chaîne
// C12, C16, C33, C36 : les lignes retenues sont hachées, réparties, puis agrégées partition par partition ; chaque
// fil garde ses dix premiers groupes.
typedef struct { uint64_t hash; int64_t ikey; uint64_t ref; uint32_t len, pad; } STuple;
static struct {
  Col str, uid, counter, date, dch, refresh;
  Counter ctr;
  int mode;  // 12, 16, 33, 36
  int32_t lo, hi;
  Top10 top[MAXT];
} cs;

static void cs_scatter_task(int tid) {
  Scratch *s = scratch[tid];
  Parts *p = &parts[tid];
  parts_init(p, &arena[tid], sizeof(STuple));
  const uint8_t *bytes = cs.str.aux;
  for (int64_t b; (b = take(&cs.ctr)) >= 0;) {
    const uint32_t count = cs.str.dir[b].count;
    if (cs.mode == 36) {  // cartes de zones : compteur et date
      const Entry *ec = &cs.counter.dir[b], *ed = &cs.date.dir[b];
      if (ec->min > 62 || ec->max < 62 || ed->max < cs.lo || ed->min > cs.hi) continue;
    }
    const int64_t *uid = cs.mode == 16 ? (const int64_t *)block_words(&cs.uid, (uint64_t)b) : NULL;
    uint64_t pos = cs.str.dir[b].aux_off;
    for (uint32_t st = 0; st < count; st += VEC) {
      const uint32_t n = count - st < VEC ? count - st : VEC;
      unpack(&cs.str, (uint64_t)b, st, n, s->a);  // longueurs
      for (uint32_t i = 0; i < n; i++) { s->x[i] = (int64_t)pos; pos += (uint64_t)s->a[i]; }
      uint32_t k = 0;
      if (cs.mode == 36) {
        unpack(&cs.counter, (uint64_t)b, st, n, s->b);
        for (uint32_t i = 0; i < n; i++) { s->pos[k] = (int32_t)(st + i); k += s->b[i] == 62; }
        if (!k) continue;
        unpack_sel(&cs.date, (uint64_t)b, s->pos, k, s->c);
        unpack_sel(&cs.dch, (uint64_t)b, s->pos, k, s->d);
        unpack_sel(&cs.refresh, (uint64_t)b, s->pos, k, s->e);
        uint32_t k2 = 0;
        for (uint32_t i = 0; i < k; i++) {
          const uint32_t j = (uint32_t)s->pos[i] - st;
          s->sel[k2] = (int32_t)j;
          k2 += (s->c[i] >= cs.lo) & (s->c[i] <= cs.hi) & (s->d[i] == 0) & (s->e[i] == 0) & (s->a[j] > 0);
        }
        k = k2;
      } else if (cs.mode == 12) {
        for (uint32_t i = 0; i < n; i++) { s->sel[k] = (int32_t)i; k += s->a[i] > 0; }
      } else {
        for (uint32_t i = 0; i < n; i++) s->sel[i] = (int32_t)i;
        k = n;
      }
      for (uint32_t j = 0; j < k; j++) {
        const uint32_t i = (uint32_t)s->sel[j];
        s->h[j] = hash_bytes(bytes + s->x[i], (uint32_t)s->a[i]);
      }
      if (uid)
        for (uint32_t j = 0; j < k; j++) {
          const uint64_t h = hash64(s->h[j] ^ ((uint64_t)uid[st + (uint32_t)s->sel[j]] * K2));
          s->h[j] = h ? h : 1;
        }
      for (uint32_t j = 0; j < k; j++) {
        const uint32_t i = (uint32_t)s->sel[j];
        STuple *t = parts_push(p, part_of(s->h[j]));
        t->hash = s->h[j]; t->ikey = uid ? uid[st + i] : 0; t->ref = (uint64_t)s->x[i]; t->len = (uint32_t)s->a[i];
      }
    }
  }
  parts_close(p);
}
static void cs_agg_task(int tid) {
  Top10 *top = &cs.top[tid];
  top->n = 0;
  for (int64_t k; (k = take(&cs.ctr)) >= 0;) {
    SMap m;
    smap_init(&m, &arena[tid], pow2_start(parts_count(parts, NT, (uint32_t)k)), cs.str.aux);
    PARTS_EACH(STuple, t, parts, NT, k) smap_add(&m, t->hash, t->ikey, t->ref, t->len);
    for (uint64_t j = 0; j <= m.mask; j++)
      if (m.cells[j].hash) top_add(top, (Top){m.cells[j].count, m.cells[j].len, m.cells[j].ikey, m.cells[j].ref});
  }
}
static void cs_open(int mode) {
  cs.mode = mode;
  cs.str = col_open("hits", mode == 12 || mode == 16 ? "SearchPhrase" : "URL");
  if (mode == 16) cs.uid = col_open("hits", "UserID");
  if (mode == 36) {
    cs.counter = col_open("hits", "CounterID"); cs.date = col_open("hits", "EventDate");
    cs.dch = col_open("hits", "DontCountHits"); cs.refresh = col_open("hits", "IsRefresh");
    cs.lo = days_from_civil(2013, 7, 1); cs.hi = days_from_civil(2013, 7, 31);
  }
}
static void cs_run(void) {
  PHASE_START();
  counter_set(&cs.ctr, cs.str.nblocks);
  run(cs_scatter_task);
  PHASE("chaînes : hachage, répartition");
  PARTS_STATS("chaînes", parts);
  top_bytes = cs.str.aux;
  counter_set(&cs.ctr, NPART);
  run(cs_agg_task);
  PHASE("chaînes : agrégation");
  Top10 all = {.n = 0};
  for (int t = 0; t < NT; t++)
    for (int i = 0; i < cs.top[t].n; i++) top_add(&all, cs.top[t].t[i]);
  for (int i = 0; i < all.n; i++) {
    if (cs.mode == 16) out("%lld|", (long long)all.t[i].ikey);
    out_bytes(cs.str.aux + all.t[i].ref, all.t[i].len);
    out("|%u\n", all.t[i].count);
  }
}

// ================================================================================================ C20
static struct { Col url; Counter ctr; uint64_t count[MAXT][8]; } c20;

static void c20_task(int tid) {
  Scratch *s = scratch[tid];
  uint64_t count = 0;
  for (int64_t b; (b = take(&c20.ctr)) >= 0;) {
    const uint64_t nbytes = block_lengths(&c20.url, (uint64_t)b, s->len);
    count += search_block(c20.url.aux + c20.url.dir[b].aux_off, nbytes, s->len, (const uint8_t *)"google", 6, s->rows);
  }
  c20.count[tid][0] = count;
}
static void c20_open(void) { c20.url = col_open("hits", "URL"); }
static void c20_run(void) {
  counter_set(&c20.ctr, c20.url.nblocks);
  run(c20_task);
  uint64_t count = 0;
  for (int t = 0; t < NT; t++) count += c20.count[t][0];
  out("%llu\n", (unsigned long long)count);
}

// ================================================================================================ principal
static double now(void) {
  struct timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return (double)t.tv_sec + 1e-9 * (double)t.tv_nsec;
}
int main(int argc, char **argv) {
  if (argc < 5) die("usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]");
  const char *q = argv[1];
  NT = atoi(argv[2]);
  const int reps = atoi(argv[3]);
  DATA = argv[4];
  const int print = argc > 5 && !strcmp(argv[5], "--print");
  if (NT < 1 || NT > MAXT) die("nombre de fils");
  for (int y = 0; y < 200; y++) year_start[y] = days_from_civil(1970 + y, 1, 1);
  for (int t = 0; t < NT; t++)
    if (posix_memalign((void **)&scratch[t], 64, sizeof(Scratch))) die("mémoire");
  void (*runq)(void) = NULL;
  if (!strcmp(q, "t1")) { t1_open(); runq = t1_run; }
  else if (!strcmp(q, "t6")) { t6_open(); runq = t6_run; }
  else if (!strcmp(q, "t9")) { t9_open(); runq = t9_run; }
  else if (!strcmp(q, "t18")) { t18_open(); runq = t18_run; }
  else if (!strcmp(q, "c4")) { c4_open(); runq = c4_run; }
  else if (!strcmp(q, "c12")) { cs_open(12); runq = cs_run; }
  else if (!strcmp(q, "c16")) { cs_open(16); runq = cs_run; }
  else if (!strcmp(q, "c33")) { cs_open(33); runq = cs_run; }
  else if (!strcmp(q, "c36")) { cs_open(36); runq = cs_run; }
  else if (!strcmp(q, "c20")) { c20_open(); runq = c20_run; }
  else die("requête inconnue");
  pool_start(NT);
#ifdef SPECIAL
  const char *level = "s";
#else
  const char *level = "p";
#endif
  for (int r = 0; r < reps; r++) {
    for (int t = 0; t < NT; t++) arena_reset(&arena[t]);
    res_len = 0;
    const double t0 = now();
    runq();
    const double dt = now() - t0;
    printf("RESULT;%s;%s;%d;%d;%.6f;%016llx\n", q, level, NT, r, dt, (unsigned long long)fnv1a(res, res_len));
    if (print && r == reps - 1) fwrite(res, 1, res_len, stdout);
    fflush(stdout);
  }
  return 0;
}
