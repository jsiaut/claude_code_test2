// v7 : niveau spécialisé du banc OLAP en C++ (olap/SPEC.md, 7). Inclus par olap.cpp sous -DSPECIAL, à la place des
// primitives portables de même nom. Même plan, mêmes structures, mêmes fonctions de hachage ; AVX-512 (F, BW, DQ, VL,
// VBMI) par les intrinsèques du compilateur.
//
//   0. décodage : seize valeurs à la fois, par permutation d'octets et décalages variables ;
//   1. sélection : comparaison de 16 valeurs et compression des positions retenues (vpcompressd) ;
//   2. agrégation de T1 : sommes masquées par groupe, huit lignes à la fois ;
//   3. recherche de sous-chaîne : premier et dernier octet de l'aiguille comparés à 64 positions à la fois ;
//   4. répartition : un tampon de 64 octets par partition, vidé par une écriture non temporelle ;
//   5. préchargement des cases et des octets à venir dans les agrégations et les sondes (dans olap.cpp, sous SPECIAL).
#include <immintrin.h>

static inline void prefetch(const void *p) { __builtin_prefetch(p); }
constexpr int AHEAD = 16;  // tuples d'avance pour le préchargement

// ------------------------------------------------------------------------------------------------ 0. décodage
// Seize valeurs à la fois (largeur de 25 bits au plus) : elles occupent 2 x largeur octets ; une permutation
// d'octets (vpermb) amène dans chaque voie de 32 bits les 4 octets où commence sa valeur, un décalage variable la
// cale, un masque la borne. Au-delà de 25 bits : huit valeurs à la fois dans des voies de 64 bits. Les tables de
// permutation et de décalage sont calculées à la compilation.
struct alignas(64) UnpackTab { uint8_t idx[64]; uint32_t sh32[16]; uint64_t sh64[8]; };
constexpr std::array<UnpackTab, 33> UNPACK_TAB = [] {
  std::array<UnpackTab, 33> t{};
  for (uint32_t w = 1; w <= 32; w++) {
    if (w <= 25) {
      for (uint32_t j = 0; j < 16; j++) {
        for (uint32_t k = 0; k < 4; k++) t[w].idx[4 * j + k] = static_cast<uint8_t>((j * w >> 3) + k);
        t[w].sh32[j] = j * w & 7;
      }
    } else {
      for (uint32_t j = 0; j < 8; j++) {
        for (uint32_t k = 0; k < 8; k++) t[w].idx[8 * j + k] = static_cast<uint8_t>((j * w >> 3) + k);
        t[w].sh64[j] = j * w & 7;
      }
    }
  }
  return t;
}();

static inline void unpack(const Col &c, uint64_t b, uint32_t start, uint32_t n, int32_t *out) {
  const Entry &e = c.dir[b];
  const uint32_t w = e.width;
  const __m512i base = _mm512_set1_epi32(static_cast<int32_t>(e.min));
  if (w == 0) {
    for (uint32_t i = 0; i < n; i += 16) _mm512_storeu_si512(out + i, base);
    return;
  }
  const uint8_t *p = reinterpret_cast<const uint8_t *>(c.words(b) + uint64_t{start / 64} * w);
  const UnpackTab &tab = UNPACK_TAB[w];
  const __m512i idx = _mm512_load_si512(tab.idx);
  if (w <= 25) {
    const __m512i sh = _mm512_loadu_si512(tab.sh32), mask = _mm512_set1_epi32(static_cast<int32_t>((1u << w) - 1));
    const __mmask64 need = (1ull << (2 * w + 4)) - 1;  // octets lus : pas au-delà de ce que le format garantit
    for (uint32_t i = 0; i < n; i += 16, p += 2 * w) {
      const __m512i x = _mm512_permutexvar_epi8(idx, _mm512_maskz_loadu_epi8(need, p));
      _mm512_storeu_si512(out + i, _mm512_add_epi32(_mm512_and_si512(_mm512_srlv_epi32(x, sh), mask), base));
    }
  } else {
    const __m512i sh = _mm512_loadu_si512(tab.sh64), mask = _mm512_set1_epi64(static_cast<int64_t>((1ull << w) - 1));
    const __mmask64 need = (1ull << (w + 8)) - 1;
    for (uint32_t i = 0; i < n; i += 8, p += w) {
      const __m512i x = _mm512_permutexvar_epi8(idx, _mm512_maskz_loadu_epi8(need, p));
      const __m256i v = _mm512_cvtepi64_epi32(_mm512_and_si512(_mm512_srlv_epi64(x, sh), mask));
      _mm256_storeu_si256(reinterpret_cast<__m256i *>(out + i), _mm256_add_epi32(v, _mm512_castsi512_si256(base)));
    }
  }
}

// ------------------------------------------------------------------------------------------------ 1. sélection
// Masque des valeurs comprises entre lo et hi parmi les 16 (ou moins, en fin de vecteur) qui partent de v + i.
struct Between {
  __m512i lo, hi;
  Between(int32_t l, int32_t h) : lo(_mm512_set1_epi32(l)), hi(_mm512_set1_epi32(h)) {}
  static __mmask16 live(uint32_t left) { return left >= 16 ? 0xFFFF : static_cast<__mmask16>((1u << left) - 1); }
  __mmask16 operator()(const int32_t *v, __mmask16 lv) const {
    const __m512i x = _mm512_maskz_loadu_epi32(lv, v);
    return _mm512_mask_cmp_epi32_mask(lv, x, lo, _MM_CMPINT_NLT) & _mm512_cmp_epi32_mask(x, hi, _MM_CMPINT_LE);
  }
};
// Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises.
static inline uint32_t sel_between(const int32_t *v, uint32_t n, int32_t lo, int32_t hi, uint32_t base, int32_t *pos) {
  const Between between(lo, hi);
  __m512i idx = _mm512_add_epi32(_mm512_set1_epi32(static_cast<int32_t>(base)),
                                 _mm512_setr_epi32(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15));
  uint32_t k = 0;
  for (uint32_t i = 0; i < n; i += 16) {
    const __mmask16 m = between(v + i, Between::live(n - i));
    _mm512_mask_compressstoreu_epi32(pos + k, m, idx);
    k += static_cast<uint32_t>(std::popcount(m));
    idx = _mm512_add_epi32(idx, _mm512_set1_epi32(16));
  }
  return k;
}
// Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
static inline uint32_t keep_between(const int32_t *v, const int32_t *pos_in, const int32_t *pay_in, uint32_t n,
                                    int32_t lo, int32_t hi, int32_t *pos_out, int32_t *pay_out) {
  const Between between(lo, hi);
  uint32_t k = 0;
  for (uint32_t i = 0; i < n; i += 16) {
    const __mmask16 lv = Between::live(n - i), m = between(v + i, lv);
    _mm512_mask_compressstoreu_epi32(pos_out + k, m, _mm512_maskz_loadu_epi32(lv, pos_in + i));
    _mm512_mask_compressstoreu_epi32(pay_out + k, m, _mm512_maskz_loadu_epi32(lv, pay_in + i));
    k += static_cast<uint32_t>(std::popcount(m));
  }
  return k;
}

// ------------------------------------------------------------------------------------------------ 2. agrégation de T1
// Huit lignes à la fois : pour chacun des six groupes, un masque et cinq additions masquées.
static inline void t1_aggregate(Agg1 *agg, const int32_t *grp, const int32_t *qty, const int32_t *ext, const int32_t *disc,
                                const int64_t *dp, const int64_t *ch, const int32_t *ship, int32_t cut, uint32_t n,
                                int32_t *) {
  __m512i acc[6][5];
  uint64_t cnt[6] = {};
  for (auto &g : acc)
    for (auto &a : g) a = _mm512_setzero_si512();
  const __m256i vcut = _mm256_set1_epi32(cut);
  const auto load8 = [](const int32_t *p) { return _mm256_loadu_si256(reinterpret_cast<const __m256i *>(p)); };
  for (uint32_t i = 0; i < n; i += 8) {
    __mmask8 live = n - i >= 8 ? 0xFF : static_cast<__mmask8>((1u << (n - i)) - 1);
    if (ship) live &= _mm256_cmp_epi32_mask(load8(ship + i), vcut, _MM_CMPINT_LE);
    const __m256i g8 = load8(grp + i);
    const __m512i q = _mm512_cvtepi32_epi64(load8(qty + i));
    const __m512i e = _mm512_cvtepi32_epi64(load8(ext + i));
    const __m512i d = _mm512_cvtepi32_epi64(load8(disc + i));
    const __m512i x = _mm512_loadu_si512(dp + i), y = _mm512_loadu_si512(ch + i);
    for (int g = 0; g < 6; g++) {
      const __mmask8 m = _mm256_mask_cmpeq_epi32_mask(live, g8, _mm256_set1_epi32(g));
      acc[g][0] = _mm512_mask_add_epi64(acc[g][0], m, acc[g][0], q);
      acc[g][1] = _mm512_mask_add_epi64(acc[g][1], m, acc[g][1], e);
      acc[g][2] = _mm512_mask_add_epi64(acc[g][2], m, acc[g][2], x);
      acc[g][3] = _mm512_mask_add_epi64(acc[g][3], m, acc[g][3], y);
      acc[g][4] = _mm512_mask_add_epi64(acc[g][4], m, acc[g][4], d);
      cnt[g] += static_cast<uint64_t>(std::popcount(m));
    }
  }
  for (int g = 0; g < 6; g++) {
    agg[g].qty += _mm512_reduce_add_epi64(acc[g][0]);
    agg[g].base += _mm512_reduce_add_epi64(acc[g][1]);
    agg[g].disc_price += _mm512_reduce_add_epi64(acc[g][2]);
    agg[g].charge += _mm512_reduce_add_epi64(acc[g][3]);
    agg[g].disc += _mm512_reduce_add_epi64(acc[g][4]);
    agg[g].count += static_cast<int64_t>(cnt[g]);
  }
}

// ------------------------------------------------------------------------------------------------ 3. sous-chaînes
// Candidates parmi les 64 positions qui partent de p : premier octet de l'aiguille en p + i, dernier en p + i + m - 1.
constexpr uint64_t SEARCH_STEP = 64;
static inline uint64_t search_candidates(const uint8_t *p, uint32_t m, uint8_t c0, uint8_t c1) {
  const __m512i a = _mm512_loadu_si512(p), b = _mm512_loadu_si512(p + m - 1);
  return _mm512_cmpeq_epi8_mask(a, _mm512_set1_epi8(static_cast<char>(c0))) &
         _mm512_cmpeq_epi8_mask(b, _mm512_set1_epi8(static_cast<char>(c1)));
}

// ------------------------------------------------------------------------------------------------ 4. répartition
// Chaque partition a un tampon de 64 octets ; plein, il part d'un trait dans le morceau, sans passer par le cache.
// La taille d'un tuple divise 64.
struct Parts {
  uint8_t *dst[NPART], *end[NPART];
  PChunk *head[NPART], *tail[NPART];
  uint8_t fill[NPART];
  uint32_t tsize;
  Arena *arena;
  uint8_t (*wc)[64];

  void init(Arena &a, uint32_t ts) {
    uint8_t (*keep)[64] = wc;
    if (!keep) keep = static_cast<uint8_t (*)[64]>(huge_alloc(size_t{NPART} * 64));
    std::memset(static_cast<void *>(this), 0, sizeof *this);
    tsize = ts; arena = &a; wc = keep;
  }
  void chunk(uint32_t k) {
    PChunk *c = static_cast<PChunk *>(arena->alloc(sizeof(PChunk) + CHUNK));
    c->next = nullptr; c->used = 0;
    if (tail[k]) { tail[k]->used = static_cast<uint32_t>(dst[k] - reinterpret_cast<uint8_t *>(tail[k] + 1)); tail[k]->next = c; }
    else head[k] = c;
    tail[k] = c;
    dst[k] = reinterpret_cast<uint8_t *>(c + 1);
    end[k] = dst[k] + CHUNK;
  }
  template <class T> T *push(uint32_t k) {
    uint32_t f = fill[k];
    if (f == 64) {  // tampon plein : il est vidé avant de resservir
      if (dst[k] == end[k]) chunk(k);
      _mm512_stream_si512(reinterpret_cast<__m512i *>(dst[k]), _mm512_load_si512(wc[k]));
      dst[k] += 64;
      f = 0;
    }
    fill[k] = static_cast<uint8_t>(f + sizeof(T));
    return reinterpret_cast<T *>(wc[k] + f);
  }
  void close() {
    for (uint32_t k = 0; k < NPART; k++) {
      if (fill[k]) {
        if (dst[k] == end[k]) chunk(k);
        std::memcpy(dst[k], wc[k], fill[k]);
        dst[k] += fill[k];
        fill[k] = 0;
      }
      if (tail[k]) tail[k]->used = static_cast<uint32_t>(dst[k] - reinterpret_cast<uint8_t *>(tail[k] + 1));
    }
    _mm_sfence();
  }
};
