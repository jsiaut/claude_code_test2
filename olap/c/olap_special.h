// v7 : niveau spécialisé de la référence C (olap/SPEC.md, 7). Inclus par olap.c sous -DSPECIAL, à la place des
// primitives portables de même nom. Même plan, mêmes structures, mêmes fonctions de hachage ; AVX-512 (F, BW, DQ, VL, VBMI).
//
//   0. décodage : seize valeurs à la fois, par permutation d'octets et décalages variables ;
//   1. sélection : comparaison de 16 valeurs et compression des positions retenues (vpcompressd) ;
//   2. agrégation de T1 : sommes masquées par groupe, huit lignes à la fois ;
//   3. recherche de sous-chaîne : premier et dernier octet de l'aiguille comparés à 64 positions à la fois ;
//   4. répartition : un tampon de 64 octets par partition, vidé par une écriture non temporelle ;
//   5. préchargement des cases et des octets à venir dans les agrégations et les sondes (dans olap.c, sous SPECIAL).
#include <immintrin.h>

#ifdef NO_PREFETCH
#define PREFETCH(p)
#else
#define PREFETCH(p) __builtin_prefetch(p)
#endif
enum { AHEAD = 16 };  // tuples d'avance pour le préchargement

// ------------------------------------------------------------------------------------------------ 0. décodage
// Seize valeurs à la fois (largeur de 25 bits au plus) : elles occupent 2 x largeur octets ; une permutation
// d'octets (vpermb) amène dans chaque voie de 32 bits les 4 octets où commence sa valeur, un décalage variable la
// cale, un masque la borne. Au-delà de 25 bits : huit valeurs à la fois dans des voies de 64 bits.
static struct { uint8_t idx[64]; uint32_t sh32[16]; uint64_t sh64[8]; } unpack_tab[33] __attribute__((aligned(64)));
static void unpack_tables(void) {
  for (uint32_t w = 1; w <= 32; w++) {
    if (w <= 25) {
      for (uint32_t j = 0; j < 16; j++) {
        for (uint32_t k = 0; k < 4; k++) unpack_tab[w].idx[4 * j + k] = (uint8_t)((j * w >> 3) + k);
        unpack_tab[w].sh32[j] = j * w & 7;
      }
    } else {
      for (uint32_t j = 0; j < 8; j++) {
        for (uint32_t k = 0; k < 8; k++) unpack_tab[w].idx[8 * j + k] = (uint8_t)((j * w >> 3) + k);
        unpack_tab[w].sh64[j] = j * w & 7;
      }
    }
  }
}
static inline void unpack_special(const Col *c, uint64_t b, uint32_t start, uint32_t n, int32_t *out) {
  const Entry *e = &c->dir[b];
  const uint32_t w = e->width;
  const __m512i base = _mm512_set1_epi32((int32_t)e->min);
  if (w == 0) {
    for (uint32_t i = 0; i < n; i += 16) _mm512_storeu_si512(out + i, base);
    return;
  }
  const uint8_t *p = (const uint8_t *)(block_words(c, b) + (uint64_t)(start / 64) * w);
  const __m512i idx = _mm512_load_si512(unpack_tab[w].idx);
  if (w <= 25) {
    const __m512i sh = _mm512_loadu_si512(unpack_tab[w].sh32), mask = _mm512_set1_epi32((int32_t)((1u << w) - 1));
    const __mmask64 need = (1ull << (2 * w + 4)) - 1;  // octets lus : pas au-delà de ce que le format garantit
    for (uint32_t i = 0; i < n; i += 16, p += 2 * w) {
      const __m512i x = _mm512_permutexvar_epi8(idx, _mm512_maskz_loadu_epi8(need, p));
      _mm512_storeu_si512(out + i, _mm512_add_epi32(_mm512_and_si512(_mm512_srlv_epi32(x, sh), mask), base));
    }
  } else {
    const __m512i sh = _mm512_loadu_si512(unpack_tab[w].sh64), mask = _mm512_set1_epi64((int64_t)((1ull << w) - 1));
    const __mmask64 need = (1ull << (w + 8)) - 1;
    for (uint32_t i = 0; i < n; i += 8, p += w) {
      const __m512i x = _mm512_permutexvar_epi8(idx, _mm512_maskz_loadu_epi8(need, p));
      const __m256i v = _mm512_cvtepi64_epi32(_mm512_and_si512(_mm512_srlv_epi64(x, sh), mask));
      _mm256_storeu_si256((__m256i *)(out + i), _mm256_add_epi32(v, _mm512_castsi512_si256(base)));
    }
  }
}
#define unpack unpack_special

// ------------------------------------------------------------------------------------------------ 1. sélection
// Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises.
static inline uint32_t sel_between(const int32_t *v, uint32_t n, int32_t lo, int32_t hi, uint32_t base, int32_t *pos) {
  const __m512i vlo = _mm512_set1_epi32(lo), vhi = _mm512_set1_epi32(hi);
  __m512i idx = _mm512_add_epi32(_mm512_set1_epi32((int32_t)base), _mm512_setr_epi32(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15));
  uint32_t k = 0;
  for (uint32_t i = 0; i < n; i += 16) {
    const __mmask16 live = n - i >= 16 ? 0xFFFF : (__mmask16)((1u << (n - i)) - 1);
    const __m512i x = _mm512_maskz_loadu_epi32(live, v + i);
    const __mmask16 m = _mm512_mask_cmp_epi32_mask(live, x, vlo, _MM_CMPINT_NLT) & _mm512_cmp_epi32_mask(x, vhi, _MM_CMPINT_LE);
    _mm512_mask_compressstoreu_epi32(pos + k, m, idx);
    k += (uint32_t)__builtin_popcount(m);
    idx = _mm512_add_epi32(idx, _mm512_set1_epi32(16));
  }
  return k;
}
// Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
static inline uint32_t keep_between(const int32_t *v, const int32_t *pos_in, const int32_t *pay_in, uint32_t n,
                                    int32_t lo, int32_t hi, int32_t *pos_out, int32_t *pay_out) {
  const __m512i vlo = _mm512_set1_epi32(lo), vhi = _mm512_set1_epi32(hi);
  uint32_t k = 0;
  for (uint32_t i = 0; i < n; i += 16) {
    const __mmask16 live = n - i >= 16 ? 0xFFFF : (__mmask16)((1u << (n - i)) - 1);
    const __m512i x = _mm512_maskz_loadu_epi32(live, v + i);
    const __mmask16 m = _mm512_mask_cmp_epi32_mask(live, x, vlo, _MM_CMPINT_NLT) & _mm512_cmp_epi32_mask(x, vhi, _MM_CMPINT_LE);
    _mm512_mask_compressstoreu_epi32(pos_out + k, m, _mm512_maskz_loadu_epi32(live, pos_in + i));
    _mm512_mask_compressstoreu_epi32(pay_out + k, m, _mm512_maskz_loadu_epi32(live, pay_in + i));
    k += (uint32_t)__builtin_popcount(m);
  }
  return k;
}

// ------------------------------------------------------------------------------------------------ 2. agrégation de T1
// Huit lignes à la fois : pour chacun des six groupes, un masque et cinq additions masquées.
static inline void t1_aggregate(Agg1 *agg, const int32_t *grp, const int32_t *qty, const int32_t *ext, const int32_t *disc,
                                const int64_t *dp, const int64_t *ch, const int32_t *ship, int32_t cut, uint32_t n,
                                int32_t *sel) {
  (void)sel;
  __m512i acc[6][5];
  uint64_t cnt[6] = {0};
  for (int g = 0; g < 6; g++)
    for (int j = 0; j < 5; j++) acc[g][j] = _mm512_setzero_si512();
  const __m256i vcut = _mm256_set1_epi32(cut);
  for (uint32_t i = 0; i < n; i += 8) {
    __mmask8 live = n - i >= 8 ? 0xFF : (__mmask8)((1u << (n - i)) - 1);
    if (ship) live &= _mm256_cmp_epi32_mask(_mm256_loadu_si256((const __m256i *)(ship + i)), vcut, _MM_CMPINT_LE);
    const __m256i g8 = _mm256_loadu_si256((const __m256i *)(grp + i));
    const __m512i q = _mm512_cvtepi32_epi64(_mm256_loadu_si256((const __m256i *)(qty + i)));
    const __m512i e = _mm512_cvtepi32_epi64(_mm256_loadu_si256((const __m256i *)(ext + i)));
    const __m512i d = _mm512_cvtepi32_epi64(_mm256_loadu_si256((const __m256i *)(disc + i)));
    const __m512i x = _mm512_loadu_si512(dp + i), y = _mm512_loadu_si512(ch + i);
    for (int g = 0; g < 6; g++) {
      const __mmask8 m = _mm256_mask_cmpeq_epi32_mask(live, g8, _mm256_set1_epi32(g));
      acc[g][0] = _mm512_mask_add_epi64(acc[g][0], m, acc[g][0], q);
      acc[g][1] = _mm512_mask_add_epi64(acc[g][1], m, acc[g][1], e);
      acc[g][2] = _mm512_mask_add_epi64(acc[g][2], m, acc[g][2], x);
      acc[g][3] = _mm512_mask_add_epi64(acc[g][3], m, acc[g][3], y);
      acc[g][4] = _mm512_mask_add_epi64(acc[g][4], m, acc[g][4], d);
      cnt[g] += (uint64_t)__builtin_popcount(m);
    }
  }
  for (int g = 0; g < 6; g++) {
    agg[g].qty += _mm512_reduce_add_epi64(acc[g][0]);
    agg[g].base += _mm512_reduce_add_epi64(acc[g][1]);
    agg[g].disc_price += _mm512_reduce_add_epi64(acc[g][2]);
    agg[g].charge += _mm512_reduce_add_epi64(acc[g][3]);
    agg[g].disc += _mm512_reduce_add_epi64(acc[g][4]);
    agg[g].count += (int64_t)cnt[g];
  }
}

// ------------------------------------------------------------------------------------------------ 3. sous-chaînes
// Candidates parmi les 64 positions qui partent de p : premier octet de l'aiguille en p + i, dernier en p + i + m - 1.
#define SEARCH_STEP 64
static inline uint64_t search_candidates(const uint8_t *p, uint32_t m, uint8_t c0, uint8_t c1) {
  const __m512i a = _mm512_loadu_si512(p), b = _mm512_loadu_si512(p + m - 1);
  return _mm512_cmpeq_epi8_mask(a, _mm512_set1_epi8((char)c0)) & _mm512_cmpeq_epi8_mask(b, _mm512_set1_epi8((char)c1));
}

// ------------------------------------------------------------------------------------------------ 4. répartition
#ifndef NO_SWWC
// Chaque partition a un tampon de 64 octets ; plein, il part d'un trait dans le morceau, sans passer par le cache.
typedef struct PChunk { struct PChunk *next; uint32_t used, pad; char fill[48]; } PChunk;  // 64 octets
typedef struct {
  uint8_t *dst[NPART], *end[NPART];
  PChunk *head[NPART], *tail[NPART];
  uint8_t fill[NPART];
  uint32_t tsize;
  Arena *arena;
  uint8_t (*wc)[64];
} Parts;

static void parts_init(Parts *p, Arena *a, uint32_t tsize) {
  uint8_t (*wc)[64] = p->wc;
  if (!wc) wc = huge_alloc((size_t)NPART * 64);
  memset(p, 0, sizeof *p);
  p->tsize = tsize; p->arena = a; p->wc = wc;
}
static void parts_chunk(Parts *p, uint32_t k) {
  PChunk *c = arena_alloc(p->arena, sizeof(PChunk) + CHUNK);
  c->next = NULL; c->used = 0;
  if (p->tail[k]) { p->tail[k]->used = (uint32_t)(p->dst[k] - (uint8_t *)(p->tail[k] + 1)); p->tail[k]->next = c; }
  else p->head[k] = c;
  p->tail[k] = c;
  p->dst[k] = (uint8_t *)(c + 1);
  p->end[k] = p->dst[k] + CHUNK;
}
static inline void *parts_push(Parts *p, uint32_t k) {
  uint32_t f = p->fill[k];
  if (f == 64) {  // tampon plein : il est vidé avant de resservir
    if (p->dst[k] == p->end[k]) parts_chunk(p, k);
    _mm512_stream_si512((void *)p->dst[k], _mm512_load_si512(p->wc[k]));
    p->dst[k] += 64;
    f = 0;
  }
  p->fill[k] = (uint8_t)(f + p->tsize);
  return p->wc[k] + f;
}
static void parts_close(Parts *p) {
  for (uint32_t k = 0; k < NPART; k++) {
    if (p->fill[k]) {
      if (p->dst[k] == p->end[k]) parts_chunk(p, k);
      memcpy(p->dst[k], p->wc[k], p->fill[k]);
      p->dst[k] += p->fill[k];
      p->fill[k] = 0;
    }
    if (p->tail[k]) p->tail[k]->used = (uint32_t)(p->dst[k] - (uint8_t *)(p->tail[k] + 1));
  }
  _mm_sfence();
}
#endif
