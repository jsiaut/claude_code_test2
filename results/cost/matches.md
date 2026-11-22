# Constructions trouvées (v4, point 5)

*Écrit par `tools/cost/count.py`. U : contourne une vérification (3.4) ; X : propre à une architecture (3.5). Chaque occurrence est à examiner ; « hors région » : dans le fichier, dans aucune région relevée.*

## c

* X ms.c:4 `immintrin.h` (hors région) : `#include <immintrin.h>`
* X ms.c:127 `__asm__` (hors région ; barrière à gabarit vide : pas propre à une architecture) : `#define BARRIER(p) __asm__ volatile("" : : "r"(p) : "memory")`
* X ms.c:129 `__asm__` (hors région ; barrière à gabarit vide : pas propre à une architecture) : `#define KEEP(x) __asm__ volatile("" : : "g"(x) : "memory")`
* X ms.c:159 `_mm512_setzero_pd` (région) : `__m512d a0 = _mm512_setzero_pd(), a1 = a0, a2 = a0, a3 = a0;`
* X ms.c:159 `__m512d` (région) : `__m512d a0 = _mm512_setzero_pd(), a1 = a0, a2 = a0, a3 = a0;`
* X ms.c:160 `_mm512_set1_ps` (région) : `const __m512 h = _mm512_set1_ps(0.5f);`
* X ms.c:160 `__m512` (région) : `const __m512 h = _mm512_set1_ps(0.5f);`
* X ms.c:164 `_mm512_load_ps` (région) : `__m512 x = _mm512_load_ps(vx + j), y = _mm512_load_ps(vy + j), z = _mm512_load_ps(vz + j), w = _mm512_load_ps(`
* X ms.c:164 `_mm512_load_ps` (région) : `__m512 x = _mm512_load_ps(vx + j), y = _mm512_load_ps(vy + j), z = _mm512_load_ps(vz + j), w = _mm512_load_ps(`
* X ms.c:164 `_mm512_load_ps` (région) : `__m512 x = _mm512_load_ps(vx + j), y = _mm512_load_ps(vy + j), z = _mm512_load_ps(vz + j), w = _mm512_load_ps(`
* X ms.c:164 `_mm512_load_ps` (région) : `__m512 x = _mm512_load_ps(vx + j), y = _mm512_load_ps(vy + j), z = _mm512_load_ps(vz + j), w = _mm512_load_ps(`
* X ms.c:164 `__m512` (région) : `__m512 x = _mm512_load_ps(vx + j), y = _mm512_load_ps(vy + j), z = _mm512_load_ps(vz + j), w = _mm512_load_ps(`
* X ms.c:165 `_mm512_fmadd_ps` (région) : `__m512 v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));`
* X ms.c:165 `_mm512_fmadd_ps` (région) : `__m512 v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));`
* X ms.c:165 `_mm512_mul_ps` (région) : `__m512 v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));`
* X ms.c:165 `__m512` (région) : `__m512 v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));`
* X ms.c:166 `_mm512_mul_ps` (région) : `__m512 e = _mm512_mul_ps(_mm512_mul_ps(h, w), v2);`
* X ms.c:166 `_mm512_mul_ps` (région) : `__m512 e = _mm512_mul_ps(_mm512_mul_ps(h, w), v2);`
* X ms.c:166 `__m512` (région) : `__m512 e = _mm512_mul_ps(_mm512_mul_ps(h, w), v2);`
* X ms.c:167 `_mm512_cvtps_pd` (région) : `__m512d lo = _mm512_cvtps_pd(_mm512_castps512_ps256(e));`
* X ms.c:167 `_mm512_castps512_ps256` (région) : `__m512d lo = _mm512_cvtps_pd(_mm512_castps512_ps256(e));`
* X ms.c:167 `__m512d` (région) : `__m512d lo = _mm512_cvtps_pd(_mm512_castps512_ps256(e));`
* X ms.c:168 `_mm512_cvtps_pd` (région) : `__m512d hi = _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1)));`
* X ms.c:168 `_mm256_castpd_ps` (région) : `__m512d hi = _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1)));`
* X ms.c:168 `_mm512_extractf64x4_pd` (région) : `__m512d hi = _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1)));`
* X ms.c:168 `_mm512_castps_pd` (région) : `__m512d hi = _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1)));`
* X ms.c:168 `__m512d` (région) : `__m512d hi = _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1)));`
* X ms.c:169 `_mm512_add_pd` (région) : `if (u == 0) { a0 = _mm512_add_pd(a0, lo); a1 = _mm512_add_pd(a1, hi); }`
* X ms.c:169 `_mm512_add_pd` (région) : `if (u == 0) { a0 = _mm512_add_pd(a0, lo); a1 = _mm512_add_pd(a1, hi); }`
* X ms.c:170 `_mm512_add_pd` (région) : `else { a2 = _mm512_add_pd(a2, lo); a3 = _mm512_add_pd(a3, hi); }`
* X ms.c:170 `_mm512_add_pd` (région) : `else { a2 = _mm512_add_pd(a2, lo); a3 = _mm512_add_pd(a3, hi); }`
* X ms.c:173 `_mm512_reduce_add_pd` (région) : `return _mm512_reduce_add_pd(_mm512_add_pd(_mm512_add_pd(a0, a1), _mm512_add_pd(a2, a3)));`
* X ms.c:173 `_mm512_add_pd` (région) : `return _mm512_reduce_add_pd(_mm512_add_pd(_mm512_add_pd(a0, a1), _mm512_add_pd(a2, a3)));`
* X ms.c:173 `_mm512_add_pd` (région) : `return _mm512_reduce_add_pd(_mm512_add_pd(_mm512_add_pd(a0, a1), _mm512_add_pd(a2, a3)));`
* X ms.c:173 `_mm512_add_pd` (région) : `return _mm512_reduce_add_pd(_mm512_add_pd(_mm512_add_pd(a0, a1), _mm512_add_pd(a2, a3)));`
* X ms.c:305 `_mm512_setzero_si512` (région) : `__m512i acc = _mm512_setzero_si512();`
* X ms.c:305 `__m512i` (région) : `__m512i acc = _mm512_setzero_si512();`
* X ms.c:306 `_mm512_setzero_si512` (région) : `const __m512i zero = _mm512_setzero_si512();`
* X ms.c:306 `__m512i` (région) : `const __m512i zero = _mm512_setzero_si512();`
* X ms.c:309 `_mm512_loadu_si512` (région) : `__m512i x = _mm512_loadu_si512((const void *)(v + i));`
* X ms.c:309 `__m512i` (région) : `__m512i x = _mm512_loadu_si512((const void *)(v + i));`
* X ms.c:310 `_mm512_maskz_mov_epi8` (région) : `__m512i y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.c:310 `_mm512_movepi8_mask` (région) : `__m512i y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.c:310 `__m512i` (région) : `__m512i y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.c:311 `_mm512_add_epi64` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(y, zero));`
* X ms.c:311 `_mm512_sad_epu8` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(y, zero));`
* X ms.c:313 `_mm512_reduce_add_epi64` (région) : `uint64_t s = (uint64_t)_mm512_reduce_add_epi64(acc);`
* X ms.c:369 `_mm512_setzero_ps` (région) : `__m512 s0 = _mm512_setzero_ps(), s1 = s0, s2 = s0, s3 = s0;`
* X ms.c:369 `__m512` (région) : `__m512 s0 = _mm512_setzero_ps(), s1 = s0, s2 = s0, s3 = s0;`
* X ms.c:371 `_mm512_fmadd_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(a + i), _mm512_load_ps(b + i), s0);`
* X ms.c:371 `_mm512_load_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(a + i), _mm512_load_ps(b + i), s0);`
* X ms.c:371 `_mm512_load_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(a + i), _mm512_load_ps(b + i), s0);`
* X ms.c:372 `_mm512_fmadd_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 16), _mm512_load_ps(b + i + 16), s1);`
* X ms.c:372 `_mm512_load_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 16), _mm512_load_ps(b + i + 16), s1);`
* X ms.c:372 `_mm512_load_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 16), _mm512_load_ps(b + i + 16), s1);`
* X ms.c:373 `_mm512_fmadd_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 32), _mm512_load_ps(b + i + 32), s2);`
* X ms.c:373 `_mm512_load_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 32), _mm512_load_ps(b + i + 32), s2);`
* X ms.c:373 `_mm512_load_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 32), _mm512_load_ps(b + i + 32), s2);`
* X ms.c:374 `_mm512_fmadd_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 48), _mm512_load_ps(b + i + 48), s3);`
* X ms.c:374 `_mm512_load_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 48), _mm512_load_ps(b + i + 48), s3);`
* X ms.c:374 `_mm512_load_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 48), _mm512_load_ps(b + i + 48), s3);`
* X ms.c:376 `_mm512_reduce_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* X ms.c:376 `_mm512_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* X ms.c:376 `_mm512_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* X ms.c:376 `_mm512_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* X ms.c:435 `_mm512_set1_epi32` (région) : `const __m512i lim = _mm512_set1_epi32(10471), c100 = _mm512_set1_epi32(100);`
* X ms.c:435 `_mm512_set1_epi32` (région) : `const __m512i lim = _mm512_set1_epi32(10471), c100 = _mm512_set1_epi32(100);`
* X ms.c:435 `__m512i` (région) : `const __m512i lim = _mm512_set1_epi32(10471), c100 = _mm512_set1_epi32(100);`
* X ms.c:438 `__m512i` (région) : `__m512i aq[6], ap[6], adp[6], ace[6], aco[6];`
* X ms.c:440 `_mm512_setzero_si512` (région) : `for (int g = 0; g < 6; g++) aq[g] = ap[g] = adp[g] = ace[g] = aco[g] = _mm512_setzero_si512();`
* X ms.c:443 `_mm512_cmple_epi32_mask` (région) : `__mmask16 pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(c->sd + i), lim);`
* X ms.c:443 `_mm512_loadu_si512` (région) : `__mmask16 pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(c->sd + i), lim);`
* X ms.c:444 `_mm512_add_epi32` (région) : `__m512i vg = _mm512_add_epi32(_mm512_slli_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->rf +`
* X ms.c:444 `_mm512_slli_epi32` (région) : `__m512i vg = _mm512_add_epi32(_mm512_slli_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->rf +`
* X ms.c:444 `_mm512_cvtepu8_epi32` (région) : `__m512i vg = _mm512_add_epi32(_mm512_slli_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->rf +`
* X ms.c:444 `_mm_loadu_si128` (région) : `__m512i vg = _mm512_add_epi32(_mm512_slli_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->rf +`
* X ms.c:444 `__m512i` (région) : `__m512i vg = _mm512_add_epi32(_mm512_slli_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->rf +`
* X ms.c:444 `__m128i` (région) : `__m512i vg = _mm512_add_epi32(_mm512_slli_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->rf +`
* X ms.c:445 `_mm512_cvtepu8_epi32` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->ls + i))));`
* X ms.c:445 `_mm_loadu_si128` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->ls + i))));`
* X ms.c:445 `__m128i` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->ls + i))));`
* X ms.c:446 `_mm512_cvtepu8_epi32` (région) : `__m512i vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:446 `_mm_loadu_si128` (région) : `__m512i vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:446 `__m512i` (région) : `__m512i vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:446 `__m128i` (région) : `__m512i vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:447 `_mm512_cvtepu8_epi32` (région) : `__m512i vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:447 `_mm_loadu_si128` (région) : `__m512i vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:447 `__m512i` (région) : `__m512i vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:447 `__m128i` (région) : `__m512i vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:448 `_mm512_add_epi32` (région) : `__m512i vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->t + i))), c100);`
* X ms.c:448 `_mm512_cvtepu8_epi32` (région) : `__m512i vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->t + i))), c100);`
* X ms.c:448 `_mm_loadu_si128` (région) : `__m512i vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->t + i))), c100);`
* X ms.c:448 `__m512i` (région) : `__m512i vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->t + i))), c100);`
* X ms.c:448 `__m128i` (région) : `__m512i vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->t + i))), c100);`
* X ms.c:449 `_mm512_loadu_si512` (région) : `__m512i vp = _mm512_loadu_si512(c->pr + i);`
* X ms.c:449 `__m512i` (région) : `__m512i vp = _mm512_loadu_si512(c->pr + i);`
* X ms.c:450 `_mm512_mullo_epi32` (région) : `__m512i vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));`
* X ms.c:450 `_mm512_sub_epi32` (région) : `__m512i vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));`
* X ms.c:450 `__m512i` (région) : `__m512i vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));`
* X ms.c:451 `_mm512_mul_epi32` (région) : `__m512i che = _mm512_mul_epi32(vdp, vt);                                              // lignes paires`
* X ms.c:451 `__m512i` (région) : `__m512i che = _mm512_mul_epi32(vdp, vt);                                              // lignes paires`
* X ms.c:452 `_mm512_mul_epi32` (région) : `__m512i cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));  // lignes impaires`
* X ms.c:452 `_mm512_srli_epi64` (région) : `__m512i cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));  // lignes impaires`
* X ms.c:452 `_mm512_srli_epi64` (région) : `__m512i cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));  // lignes impaires`
* X ms.c:452 `__m512i` (région) : `__m512i cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));  // lignes impaires`
* X ms.c:454 `_mm512_mask_cmpeq_epi32_mask` (région) : `__mmask16 m = _mm512_mask_cmpeq_epi32_mask(pass, vg, _mm512_set1_epi32(g));`
* X ms.c:454 `_mm512_set1_epi32` (région) : `__mmask16 m = _mm512_mask_cmpeq_epi32_mask(pass, vg, _mm512_set1_epi32(g));`
* X ms.c:456 `_mm512_mask_add_epi32` (région) : `aq[g] = _mm512_mask_add_epi32(aq[g], m, aq[g], vq);`
* X ms.c:457 `_mm512_mask_add_epi32` (région) : `ap[g] = _mm512_mask_add_epi32(ap[g], m, ap[g], vp);`
* X ms.c:458 `_mm512_mask_add_epi32` (région) : `adp[g] = _mm512_mask_add_epi32(adp[g], m, adp[g], vdp);`
* X ms.c:459 `_mm512_mask_add_epi64` (région) : `ace[g] = _mm512_mask_add_epi64(ace[g], (__mmask8)_pext_u32(m, 0x5555), ace[g], che);`
* X ms.c:460 `_mm512_mask_add_epi64` (région) : `aco[g] = _mm512_mask_add_epi64(aco[g], (__mmask8)_pext_u32(m, 0xAAAA), aco[g], cho);`
* X ms.c:465 `_mm512_reduce_add_epi32` (région) : `acc->a[g][1] += _mm512_reduce_add_epi32(aq[g]);`
* X ms.c:466 `_mm512_reduce_add_epi32` (région) : `acc->a[g][2] += _mm512_reduce_add_epi32(ap[g]);`
* X ms.c:467 `_mm512_reduce_add_epi64` (région) : `acc->a[g][3] += (int64_t)_mm512_reduce_add_epi64(_mm512_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256`
* X ms.c:467 `_mm512_add_epi64` (région) : `acc->a[g][3] += (int64_t)_mm512_reduce_add_epi64(_mm512_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256`
* X ms.c:467 `_mm512_cvtepi32_epi64` (région) : `acc->a[g][3] += (int64_t)_mm512_reduce_add_epi64(_mm512_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256`
* X ms.c:467 `_mm512_castsi512_si256` (région) : `acc->a[g][3] += (int64_t)_mm512_reduce_add_epi64(_mm512_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256`
* X ms.c:468 `_mm512_cvtepi32_epi64` (région) : `_mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(adp[g], 1))));`
* X ms.c:468 `_mm512_extracti64x4_epi64` (région) : `_mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(adp[g], 1))));`
* X ms.c:469 `_mm512_reduce_add_epi64` (région) : `acc->a[g][4] += _mm512_reduce_add_epi64(_mm512_add_epi64(ace[g], aco[g]));`
* X ms.c:469 `_mm512_add_epi64` (région) : `acc->a[g][4] += _mm512_reduce_add_epi64(_mm512_add_epi64(ace[g], aco[g]));`
* X ms.c:479 `_mm512_set1_epi32` (région) : `const __m512i d0 = _mm512_set1_epi32(8766), d1 = _mm512_set1_epi32(9131), r0 = _mm512_set1_epi32(5),`
* X ms.c:479 `_mm512_set1_epi32` (région) : `const __m512i d0 = _mm512_set1_epi32(8766), d1 = _mm512_set1_epi32(9131), r0 = _mm512_set1_epi32(5),`
* X ms.c:479 `_mm512_set1_epi32` (région) : `const __m512i d0 = _mm512_set1_epi32(8766), d1 = _mm512_set1_epi32(9131), r0 = _mm512_set1_epi32(5),`
* X ms.c:479 `__m512i` (région) : `const __m512i d0 = _mm512_set1_epi32(8766), d1 = _mm512_set1_epi32(9131), r0 = _mm512_set1_epi32(5),`
* X ms.c:480 `_mm512_set1_epi32` (région) : `r1 = _mm512_set1_epi32(7), q0 = _mm512_set1_epi32(24);`
* X ms.c:480 `_mm512_set1_epi32` (région) : `r1 = _mm512_set1_epi32(7), q0 = _mm512_set1_epi32(24);`
* X ms.c:481 `_mm512_setzero_si512` (région) : `__m512i a0 = _mm512_setzero_si512(), a1 = _mm512_setzero_si512();`
* X ms.c:481 `_mm512_setzero_si512` (région) : `__m512i a0 = _mm512_setzero_si512(), a1 = _mm512_setzero_si512();`
* X ms.c:481 `__m512i` (région) : `__m512i a0 = _mm512_setzero_si512(), a1 = _mm512_setzero_si512();`
* X ms.c:484 `_mm512_loadu_si512` (région) : `__m512i sd = _mm512_loadu_si512(c->sd + i), pr = _mm512_loadu_si512(c->pr + i);`
* X ms.c:484 `_mm512_loadu_si512` (région) : `__m512i sd = _mm512_loadu_si512(c->sd + i), pr = _mm512_loadu_si512(c->pr + i);`
* X ms.c:484 `__m512i` (région) : `__m512i sd = _mm512_loadu_si512(c->sd + i), pr = _mm512_loadu_si512(c->pr + i);`
* X ms.c:485 `_mm512_cvtepu8_epi32` (région) : `__m512i d = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:485 `_mm_loadu_si128` (région) : `__m512i d = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:485 `__m512i` (région) : `__m512i d = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:485 `__m128i` (région) : `__m512i d = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->d + i)));`
* X ms.c:486 `_mm512_cvtepu8_epi32` (région) : `__m512i q = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:486 `_mm_loadu_si128` (région) : `__m512i q = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:486 `__m512i` (région) : `__m512i q = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:486 `__m128i` (région) : `__m512i q = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(c->q + i)));`
* X ms.c:487 `_mm512_cmpge_epi32_mask` (région) : `__mmask16 m = _mm512_cmpge_epi32_mask(sd, d0) & _mm512_cmplt_epi32_mask(sd, d1) &`
* X ms.c:487 `_mm512_cmplt_epi32_mask` (région) : `__mmask16 m = _mm512_cmpge_epi32_mask(sd, d0) & _mm512_cmplt_epi32_mask(sd, d1) &`
* X ms.c:488 `_mm512_cmpge_epi32_mask` (région) : `_mm512_cmpge_epi32_mask(d, r0) & _mm512_cmple_epi32_mask(d, r1) & _mm512_cmplt_epi32_mask(q, q0);`
* X ms.c:488 `_mm512_cmple_epi32_mask` (région) : `_mm512_cmpge_epi32_mask(d, r0) & _mm512_cmple_epi32_mask(d, r1) & _mm512_cmplt_epi32_mask(q, q0);`
* X ms.c:488 `_mm512_cmplt_epi32_mask` (région) : `_mm512_cmpge_epi32_mask(d, r0) & _mm512_cmple_epi32_mask(d, r1) & _mm512_cmplt_epi32_mask(q, q0);`
* X ms.c:489 `_mm512_maskz_mov_epi32` (région) : `__m512i p = _mm512_maskz_mov_epi32(m, _mm512_mullo_epi32(pr, d));`
* X ms.c:489 `_mm512_mullo_epi32` (région) : `__m512i p = _mm512_maskz_mov_epi32(m, _mm512_mullo_epi32(pr, d));`
* X ms.c:489 `__m512i` (région) : `__m512i p = _mm512_maskz_mov_epi32(m, _mm512_mullo_epi32(pr, d));`
* X ms.c:490 `_mm512_add_epi64` (région) : `a0 = _mm512_add_epi64(a0, _mm512_cvtepi32_epi64(_mm512_castsi512_si256(p)));`
* X ms.c:490 `_mm512_cvtepi32_epi64` (région) : `a0 = _mm512_add_epi64(a0, _mm512_cvtepi32_epi64(_mm512_castsi512_si256(p)));`
* X ms.c:490 `_mm512_castsi512_si256` (région) : `a0 = _mm512_add_epi64(a0, _mm512_cvtepi32_epi64(_mm512_castsi512_si256(p)));`
* X ms.c:491 `_mm512_add_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(p, 1)));`
* X ms.c:491 `_mm512_cvtepi32_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(p, 1)));`
* X ms.c:491 `_mm512_extracti64x4_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(p, 1)));`
* X ms.c:493 `_mm512_reduce_add_epi64` (région) : `return _mm512_reduce_add_epi64(_mm512_add_epi64(a0, a1)) + q6_natural(c, i, hi);  // reste (< 16 lignes)`
* X ms.c:493 `_mm512_add_epi64` (région) : `return _mm512_reduce_add_epi64(_mm512_add_epi64(a0, a1)) + q6_natural(c, i, hi);  // reste (< 16 lignes)`
* X ms.c:758 `_mm512_set1_pd` (région) : `const __m512d q = _mm512_set1_pd(0.25);`
* X ms.c:758 `__m512d` (région) : `const __m512d q = _mm512_set1_pd(0.25);`
* X ms.c:764 `_mm512_add_pd` (région) : `__m512d s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up + j), _mm512_loadu_pd(dn + j)),`
* X ms.c:764 `_mm512_add_pd` (région) : `__m512d s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up + j), _mm512_loadu_pd(dn + j)),`
* X ms.c:764 `_mm512_add_pd` (région) : `__m512d s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up + j), _mm512_loadu_pd(dn + j)),`
* X ms.c:764 `_mm512_loadu_pd` (région) : `__m512d s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up + j), _mm512_loadu_pd(dn + j)),`
* X ms.c:764 `_mm512_loadu_pd` (région) : `__m512d s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up + j), _mm512_loadu_pd(dn + j)),`
* X ms.c:764 `__m512d` (région) : `__m512d s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up + j), _mm512_loadu_pd(dn + j)),`
* X ms.c:765 `_mm512_loadu_pd` (région) : `_mm512_loadu_pd(mid + j - 1)),`
* X ms.c:766 `_mm512_loadu_pd` (région) : `_mm512_loadu_pd(mid + j + 1));`
* X ms.c:767 `_mm512_storeu_pd` (région) : `_mm512_storeu_pd(o + j, _mm512_mul_pd(q, s));`
* X ms.c:767 `_mm512_mul_pd` (région) : `_mm512_storeu_pd(o + j, _mm512_mul_pd(q, s));`
* X ms.c:868 `_mm_pause` (hors région) : `if (w - sq->read_idx_cache == CAP10) _mm_pause();`
* X ms.c:882 `_mm_pause` (hors région) : `if (rd == sq->write_idx_cache) _mm_pause();`

## odin

* U ms.odin:48 `#no_bounds_check` (hors région ; portée brace : lignes 48 à 59) : `k1_aos :: proc(ps: []Particle) -> f64 #no_bounds_check {`
* U ms.odin:61 `#no_bounds_check` (région ; portée brace : lignes 61 à 80) : `k1_soa :: proc(ps: #soa[]Particle) -> f64 #no_bounds_check {`
* U ms.odin:138 `#no_bounds_check` (hors région ; portée brace : lignes 138 à 142) : `k2_chase :: proc(a: []u32, h: int) -> u32 #no_bounds_check {`
* U ms.odin:198 `rawptr` (région ; portée line : lignes 198 à 198) : `job:         proc(data: rawptr, t: int),`
* U ms.odin:199 `rawptr` (région ; portée line : lignes 199 à 199) : `data:        rawptr,`
* U ms.odin:217 `rawptr` (région ; portée line : lignes 217 à 217) : `pool_run :: proc(job: proc(data: rawptr, t: int), data: rawptr) {`
* U ms.odin:217 `rawptr` (région ; portée line : lignes 217 à 217) : `pool_run :: proc(job: proc(data: rawptr, t: int), data: rawptr) {`
* U ms.odin:268 `#no_bounds_check` (hors région ; portée brace : lignes 268 à 287) : `k4_swar :: proc(v: []u8) -> u64 #no_bounds_check {`
* U ms.odin:309 `#no_bounds_check` (région ; portée brace : lignes 309 à 319) : `k5_tuned :: proc(a, b: []f32) -> f32 #no_bounds_check {`
* U ms.odin:352 `#no_bounds_check` (région ; portée brace : lignes 352 à 366) : `q6_tuned :: proc(c: ^Cols, lo, hi: int) -> i64 #no_bounds_check {`
* U ms.odin:381 `#no_bounds_check` (hors région ; portée brace : lignes 381 à 417) : `q1_tuned :: proc(c: ^Cols, lo, hi: int, acc: ^Q1Acc) #no_bounds_check {`
* U ms.odin:421 `#no_bounds_check` (région ; portée brace : lignes 421 à 457) : `q1_tuned_v :: proc(c: ^Cols, lo, hi: int, acc: ^Q1Acc) #no_bounds_check {`
* U ms.odin:479 `rawptr` (région ; portée line : lignes 479 à 479) : `k6_pool_job :: proc(data: rawptr, t: int) {`
* U ms.odin:595 `#no_bounds_check` (hors région ; portée brace : lignes 595 à 602) : `a_build :: proc(a: ^[K8_NODES]ANode, top: ^i32, d: int, c: ^i64) -> i32 #no_bounds_check {`
* U ms.odin:603 `#no_bounds_check` (hors région ; portée brace : lignes 603 à 603) : `a_sum :: proc(a: ^[K8_NODES]ANode, i: i32) -> i64 #no_bounds_check {return i < 0 ? 0 : a[i].v + a_sum(a, a[i].`
* U ms.odin:607 `#no_bounds_check` (hors région ; portée brace : lignes 607 à 617) : `av_build :: proc(a: ^[K8_NODES]ANode, i: i32, d: int, q: i64) -> i32 #no_bounds_check {`
* U ms.odin:627 `#no_bounds_check` (région ; portée brace : lignes 627 à 651) : `ai_build :: proc(a: ^[K8_NODES]ANode, depth: int, q: i64) #no_bounds_check {`
* U ms.odin:652 `#no_bounds_check` (région ; portée brace : lignes 652 à 667) : `ai_sum :: proc(a: ^[K8_NODES]ANode, root: i32) -> i64 #no_bounds_check {`
* U ms.odin:724 `#no_bounds_check` (région ; portée brace : lignes 724 à 735) : `k9_rows :: proc(a, b: []f64, r0, r1: int) #no_bounds_check {`
* U ms.odin:744 `rawptr` (région ; portée line : lignes 744 à 744) : `k9_pool_job :: proc(data: rawptr, t: int) {`

## cpp

* X ms.cpp:23 `immintrin.h` (hors région) : `#include <immintrin.h>`
* X ms.cpp:128 `asm` (hors région ; barrière à gabarit vide : pas propre à une architecture) : `template <class T> static void opaque(T &x) { asm volatile("" : "+r"(x) : : "memory"); }`
* X ms.cpp:130 `asm` (hors région ; barrière à gabarit vide : pas propre à une architecture) : `template <class T> static void keep(const T &x) { asm volatile("" : : "g"(x) : "memory"); }`
* X ms.cpp:300 `_mm512_setzero_si512` (région) : `__m512i acc = _mm512_setzero_si512();`
* X ms.cpp:300 `__m512i` (région) : `__m512i acc = _mm512_setzero_si512();`
* X ms.cpp:301 `_mm512_setzero_si512` (région) : `const __m512i zero = _mm512_setzero_si512();`
* X ms.cpp:301 `__m512i` (région) : `const __m512i zero = _mm512_setzero_si512();`
* X ms.cpp:304 `_mm512_loadu_si512` (région) : `__m512i x = _mm512_loadu_si512(p + i);`
* X ms.cpp:304 `__m512i` (région) : `__m512i x = _mm512_loadu_si512(p + i);`
* X ms.cpp:305 `_mm512_maskz_mov_epi8` (région) : `__m512i y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.cpp:305 `_mm512_movepi8_mask` (région) : `__m512i y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.cpp:305 `__m512i` (région) : `__m512i y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.cpp:306 `_mm512_add_epi64` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(y, zero));`
* X ms.cpp:306 `_mm512_sad_epu8` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(y, zero));`
* X ms.cpp:308 `_mm512_reduce_add_epi64` (région) : `uint64_t s = (uint64_t)_mm512_reduce_add_epi64(acc);`
* X ms.cpp:839 `__builtin_ia32_pause` (hors région) : `if (rd == sq->write_idx_cache) __builtin_ia32_pause();`
* X ms.cpp:851 `__builtin_ia32_pause` (hors région) : `if (w - sq->read_idx_cache == CAP10) __builtin_ia32_pause();`

## c3


## zig

* U ms.zig:478 `@ptrCast` (région ; portée line : lignes 478 à 478) : `const j: *K6Pool = @ptrCast(@alignCast(data));`
* U ms.zig:775 `@ptrCast` (région ; portée line : lignes 775 à 775) : `const j: *K9Pool = @ptrCast(@alignCast(data));`

## rust

* X ms.rs:3 `std::arch` (hors région) : `use std::arch::x86_64::*;`
* U ms.rs:34 `unsafe` (région ; portée brace : lignes 34 à 34) : `unsafe { std::ptr::copy_nonoverlapping(b.as_ptr(), v.as_mut_ptr() as *mut u8, b.len()) };`
* U ms.rs:34 `*mut` (région ; portée line : lignes 34 à 34) : `unsafe { std::ptr::copy_nonoverlapping(b.as_ptr(), v.as_mut_ptr() as *mut u8, b.len()) };`
* U ms.rs:39 `unsafe` (région ; portée brace : lignes 39 à 39) : `ABuf::from_bytes(unsafe { std::slice::from_raw_parts(src.as_ptr() as *const u8, std::mem::size_of_val(src)) })`
* U ms.rs:39 `from_raw_parts` (région ; portée line : lignes 39 à 39) : `ABuf::from_bytes(unsafe { std::slice::from_raw_parts(src.as_ptr() as *const u8, std::mem::size_of_val(src)) })`
* U ms.rs:39 `*const` (région ; portée line : lignes 39 à 39) : `ABuf::from_bytes(unsafe { std::slice::from_raw_parts(src.as_ptr() as *const u8, std::mem::size_of_val(src)) })`
* U ms.rs:42 `unsafe` (région ; portée brace : lignes 42 à 42) : `unsafe { std::slice::from_raw_parts(self.v.as_ptr() as *const T, self.bytes / std::mem::size_of::<T>()) }`
* U ms.rs:42 `from_raw_parts` (région ; portée line : lignes 42 à 42) : `unsafe { std::slice::from_raw_parts(self.v.as_ptr() as *const T, self.bytes / std::mem::size_of::<T>()) }`
* U ms.rs:42 `*const` (région ; portée line : lignes 42 à 42) : `unsafe { std::slice::from_raw_parts(self.v.as_ptr() as *const T, self.bytes / std::mem::size_of::<T>()) }`
* U ms.rs:45 `unsafe` (région ; portée brace : lignes 45 à 45) : `unsafe { std::slice::from_raw_parts_mut(self.v.as_mut_ptr() as *mut T, self.bytes / std::mem::size_of::<T>()) `
* U ms.rs:45 `from_raw_parts_mut` (région ; portée line : lignes 45 à 45) : `unsafe { std::slice::from_raw_parts_mut(self.v.as_mut_ptr() as *mut T, self.bytes / std::mem::size_of::<T>()) `
* U ms.rs:45 `*mut` (région ; portée line : lignes 45 à 45) : `unsafe { std::slice::from_raw_parts_mut(self.v.as_mut_ptr() as *mut T, self.bytes / std::mem::size_of::<T>()) `
* U ms.rs:56 `*const` (région ; portée line : lignes 56 à 56) : `fn tramp<J: Job>(d: *const (), t: usize) {`
* U ms.rs:57 `unsafe` (région ; portée brace : lignes 57 à 57) : `unsafe { (*(d as *const J)).run(t) }`
* U ms.rs:57 `*const` (région ; portée line : lignes 57 à 57) : `unsafe { (*(d as *const J)).run(t) }`
* U ms.rs:62 `*const` (région ; portée line : lignes 62 à 62) : `job: UnsafeCell<(fn(*const (), usize), *const ())>,`
* U ms.rs:62 `*const` (région ; portée line : lignes 62 à 62) : `job: UnsafeCell<(fn(*const (), usize), *const ())>,`
* U ms.rs:65 `unsafe` (région ; portée brace : lignes 65 à 65) : `unsafe impl Sync for Pool {}`
* U ms.rs:68 `*const` (région ; portée line : lignes 68 à 68) : `fn none(_: *const (), _: usize) {}`
* U ms.rs:78 `unsafe` (région ; portée brace : lignes 78 à 78) : `let (f, d) = unsafe { *self.job.get() };`
* U ms.rs:84 `unsafe` (région ; portée brace : lignes 84 à 84) : `unsafe { *self.job.get() = (tramp::<J> as fn(*const (), usize), j as *const J as *const ()) };`
* U ms.rs:84 `*const` (région ; portée line : lignes 84 à 84) : `unsafe { *self.job.get() = (tramp::<J> as fn(*const (), usize), j as *const J as *const ()) };`
* U ms.rs:84 `*const` (région ; portée line : lignes 84 à 84) : `unsafe { *self.job.get() = (tramp::<J> as fn(*const (), usize), j as *const J as *const ()) };`
* U ms.rs:84 `*const` (région ; portée line : lignes 84 à 84) : `unsafe { *self.job.get() = (tramp::<J> as fn(*const (), usize), j as *const J as *const ()) };`
* X ms.rs:159 `#[target_feature` (région) : `#[target_feature(enable = "avx512f")]`
* U ms.rs:160 `unsafe` (région ; portée brace : lignes 160 à 177) : `unsafe fn k1_soa(vx: &[f32], vy: &[f32], vz: &[f32], m: &[f32]) -> f64 {`
* X ms.rs:162 `_mm512_setzero_pd` (région) : `let (mut a0, mut a1) = (_mm512_setzero_pd(), _mm512_setzero_pd());`
* X ms.rs:162 `_mm512_setzero_pd` (région) : `let (mut a0, mut a1) = (_mm512_setzero_pd(), _mm512_setzero_pd());`
* X ms.rs:163 `_mm512_set1_ps` (région) : `let h = _mm512_set1_ps(0.5);`
* U ms.rs:166 `.add(` (région ; portée line : lignes 166 à 166) : `let x = _mm512_loadu_ps(vx.as_ptr().add(i));`
* X ms.rs:166 `_mm512_loadu_ps` (région) : `let x = _mm512_loadu_ps(vx.as_ptr().add(i));`
* U ms.rs:167 `.add(` (région ; portée line : lignes 167 à 167) : `let y = _mm512_loadu_ps(vy.as_ptr().add(i));`
* X ms.rs:167 `_mm512_loadu_ps` (région) : `let y = _mm512_loadu_ps(vy.as_ptr().add(i));`
* U ms.rs:168 `.add(` (région ; portée line : lignes 168 à 168) : `let z = _mm512_loadu_ps(vz.as_ptr().add(i));`
* X ms.rs:168 `_mm512_loadu_ps` (région) : `let z = _mm512_loadu_ps(vz.as_ptr().add(i));`
* U ms.rs:169 `.add(` (région ; portée line : lignes 169 à 169) : `let w = _mm512_loadu_ps(m.as_ptr().add(i));`
* X ms.rs:169 `_mm512_loadu_ps` (région) : `let w = _mm512_loadu_ps(m.as_ptr().add(i));`
* X ms.rs:170 `_mm512_fmadd_ps` (région) : `let v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));`
* X ms.rs:170 `_mm512_fmadd_ps` (région) : `let v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));`
* X ms.rs:170 `_mm512_mul_ps` (région) : `let v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));`
* X ms.rs:171 `_mm512_mul_ps` (région) : `let e = _mm512_mul_ps(_mm512_mul_ps(h, w), v2);`
* X ms.rs:171 `_mm512_mul_ps` (région) : `let e = _mm512_mul_ps(_mm512_mul_ps(h, w), v2);`
* X ms.rs:172 `_mm512_add_pd` (région) : `a0 = _mm512_add_pd(a0, _mm512_cvtps_pd(_mm512_castps512_ps256(e)));`
* X ms.rs:172 `_mm512_cvtps_pd` (région) : `a0 = _mm512_add_pd(a0, _mm512_cvtps_pd(_mm512_castps512_ps256(e)));`
* X ms.rs:172 `_mm512_castps512_ps256` (région) : `a0 = _mm512_add_pd(a0, _mm512_cvtps_pd(_mm512_castps512_ps256(e)));`
* X ms.rs:173 `_mm512_add_pd` (région) : `a1 = _mm512_add_pd(a1, _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1))));`
* X ms.rs:173 `_mm512_cvtps_pd` (région) : `a1 = _mm512_add_pd(a1, _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1))));`
* X ms.rs:173 `_mm256_castpd_ps` (région) : `a1 = _mm512_add_pd(a1, _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1))));`
* X ms.rs:173 `_mm512_extractf64x4_pd` (région) : `a1 = _mm512_add_pd(a1, _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1))));`
* X ms.rs:173 `_mm512_castps_pd` (région) : `a1 = _mm512_add_pd(a1, _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1))));`
* X ms.rs:176 `_mm512_reduce_add_pd` (région) : `_mm512_reduce_add_pd(_mm512_add_pd(a0, a1))`
* X ms.rs:176 `_mm512_add_pd` (région) : `_mm512_reduce_add_pd(_mm512_add_pd(a0, a1))`
* U ms.rs:212 `unsafe` (hors région ; portée brace : lignes 212 à 212) : `bench("k1", v, "energy", reps, || format!("{:.6}", unsafe { k1_soa(c(3), c(4), c(5), c(9)) }));`
* U ms.rs:230 `unsafe` (hors région ; portée brace : lignes 230 à 230) : `i = unsafe { *a.get_unchecked(i as usize) };`
* U ms.rs:230 `get_unchecked` (hors région ; portée line : lignes 230 à 230) : `i = unsafe { *a.get_unchecked(i as usize) };`
* X ms.rs:284 `#[target_feature` (région) : `#[target_feature(enable = "avx512f,avx512bw")]`
* U ms.rs:285 `unsafe` (région ; portée brace : lignes 285 à 305) : `unsafe fn k4_tuned_avx512(v: &[u8]) -> u64 {`
* X ms.rs:288 `_mm512_setzero_si512` (région) : `let zero = _mm512_setzero_si512();`
* X ms.rs:289 `_mm512_setzero_si512` (région) : `let mut acc = _mm512_setzero_si512();`
* U ms.rs:292 `unsafe` (région ; portée brace : lignes 292 à 292) : `let x = unsafe { _mm512_loadu_si512(p.add(i) as *const _) };`
* U ms.rs:292 `*const` (région ; portée line : lignes 292 à 292) : `let x = unsafe { _mm512_loadu_si512(p.add(i) as *const _) };`
* U ms.rs:292 `.add(` (région ; portée line : lignes 292 à 292) : `let x = unsafe { _mm512_loadu_si512(p.add(i) as *const _) };`
* X ms.rs:292 `_mm512_loadu_si512` (région) : `let x = unsafe { _mm512_loadu_si512(p.add(i) as *const _) };`
* X ms.rs:293 `_mm512_maskz_mov_epi8` (région) : `let y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.rs:293 `_mm512_movepi8_mask` (région) : `let y = _mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x);`
* X ms.rs:294 `_mm512_add_epi64` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(y, zero));`
* X ms.rs:294 `_mm512_sad_epu8` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(y, zero));`
* X ms.rs:297 `_mm512_reduce_add_epi64` (région) : `let mut s = _mm512_reduce_add_epi64(acc) as u64;`
* U ms.rs:308 `unsafe` (région ; portée brace : lignes 308 à 308) : `unsafe { k4_tuned_avx512(v) }`
* X ms.rs:359 `#[target_feature` (région) : `#[target_feature(enable = "avx512f")]`
* U ms.rs:360 `unsafe` (région ; portée brace : lignes 360 à 372) : `unsafe fn k5_tuned(a: &[f32], b: &[f32]) -> f32 {`
* X ms.rs:361 `_mm512_setzero_ps` (région) : `let (mut s0, mut s1, mut s2, mut s3) = (_mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_`
* X ms.rs:361 `_mm512_setzero_ps` (région) : `let (mut s0, mut s1, mut s2, mut s3) = (_mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_`
* X ms.rs:361 `_mm512_setzero_ps` (région) : `let (mut s0, mut s1, mut s2, mut s3) = (_mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_`
* X ms.rs:361 `_mm512_setzero_ps` (région) : `let (mut s0, mut s1, mut s2, mut s3) = (_mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_`
* U ms.rs:365 `.add(` (région ; portée line : lignes 365 à 365) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i)), _mm512_load_ps(pb.add(i)), s0);`
* U ms.rs:365 `.add(` (région ; portée line : lignes 365 à 365) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i)), _mm512_load_ps(pb.add(i)), s0);`
* X ms.rs:365 `_mm512_fmadd_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i)), _mm512_load_ps(pb.add(i)), s0);`
* X ms.rs:365 `_mm512_load_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i)), _mm512_load_ps(pb.add(i)), s0);`
* X ms.rs:365 `_mm512_load_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i)), _mm512_load_ps(pb.add(i)), s0);`
* U ms.rs:366 `.add(` (région ; portée line : lignes 366 à 366) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 16)), _mm512_load_ps(pb.add(i + 16)), s1);`
* U ms.rs:366 `.add(` (région ; portée line : lignes 366 à 366) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 16)), _mm512_load_ps(pb.add(i + 16)), s1);`
* X ms.rs:366 `_mm512_fmadd_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 16)), _mm512_load_ps(pb.add(i + 16)), s1);`
* X ms.rs:366 `_mm512_load_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 16)), _mm512_load_ps(pb.add(i + 16)), s1);`
* X ms.rs:366 `_mm512_load_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 16)), _mm512_load_ps(pb.add(i + 16)), s1);`
* U ms.rs:367 `.add(` (région ; portée line : lignes 367 à 367) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 32)), _mm512_load_ps(pb.add(i + 32)), s2);`
* U ms.rs:367 `.add(` (région ; portée line : lignes 367 à 367) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 32)), _mm512_load_ps(pb.add(i + 32)), s2);`
* X ms.rs:367 `_mm512_fmadd_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 32)), _mm512_load_ps(pb.add(i + 32)), s2);`
* X ms.rs:367 `_mm512_load_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 32)), _mm512_load_ps(pb.add(i + 32)), s2);`
* X ms.rs:367 `_mm512_load_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 32)), _mm512_load_ps(pb.add(i + 32)), s2);`
* U ms.rs:368 `.add(` (région ; portée line : lignes 368 à 368) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 48)), _mm512_load_ps(pb.add(i + 48)), s3);`
* U ms.rs:368 `.add(` (région ; portée line : lignes 368 à 368) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 48)), _mm512_load_ps(pb.add(i + 48)), s3);`
* X ms.rs:368 `_mm512_fmadd_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 48)), _mm512_load_ps(pb.add(i + 48)), s3);`
* X ms.rs:368 `_mm512_load_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 48)), _mm512_load_ps(pb.add(i + 48)), s3);`
* X ms.rs:368 `_mm512_load_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 48)), _mm512_load_ps(pb.add(i + 48)), s3);`
* X ms.rs:371 `_mm512_reduce_add_ps` (région) : `_mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)))`
* X ms.rs:371 `_mm512_add_ps` (région) : `_mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)))`
* X ms.rs:371 `_mm512_add_ps` (région) : `_mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)))`
* X ms.rs:371 `_mm512_add_ps` (région) : `_mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)))`
* U ms.rs:381 `unsafe` (hors région ; portée brace : lignes 381 à 381) : `d = if tuned { unsafe { k5_tuned(aa, b) } } else { k5_natural(aa, b) };`
* X ms.rs:418 `#[target_feature` (région) : `#[target_feature(enable = "avx512f,avx512bw")]`
* U ms.rs:419 `unsafe` (région ; portée brace : lignes 419 à 439) : `unsafe fn q6_tuned_v(c: &Cols, lo: usize, hi: usize) -> i64 {`
* X ms.rs:420 `_mm512_set1_epi32` (région) : `let (d0, d1) = (_mm512_set1_epi32(8766), _mm512_set1_epi32(9131));`
* X ms.rs:420 `_mm512_set1_epi32` (région) : `let (d0, d1) = (_mm512_set1_epi32(8766), _mm512_set1_epi32(9131));`
* X ms.rs:421 `_mm512_set1_epi32` (région) : `let (r0, r1, q0) = (_mm512_set1_epi32(5), _mm512_set1_epi32(7), _mm512_set1_epi32(24));`
* X ms.rs:421 `_mm512_set1_epi32` (région) : `let (r0, r1, q0) = (_mm512_set1_epi32(5), _mm512_set1_epi32(7), _mm512_set1_epi32(24));`
* X ms.rs:421 `_mm512_set1_epi32` (région) : `let (r0, r1, q0) = (_mm512_set1_epi32(5), _mm512_set1_epi32(7), _mm512_set1_epi32(24));`
* X ms.rs:422 `_mm512_setzero_si512` (région) : `let (mut a0, mut a1) = (_mm512_setzero_si512(), _mm512_setzero_si512());`
* X ms.rs:422 `_mm512_setzero_si512` (région) : `let (mut a0, mut a1) = (_mm512_setzero_si512(), _mm512_setzero_si512());`
* U ms.rs:426 `unsafe` (région ; portée brace : lignes 426 à 430) : `let (sd, pr, d, q) = unsafe {`
* U ms.rs:427 `*const` (région ; portée line : lignes 427 à 427) : `(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _),`
* U ms.rs:427 `*const` (région ; portée line : lignes 427 à 427) : `(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _),`
* U ms.rs:427 `.add(` (région ; portée line : lignes 427 à 427) : `(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _),`
* U ms.rs:427 `.add(` (région ; portée line : lignes 427 à 427) : `(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _),`
* X ms.rs:427 `_mm512_loadu_si512` (région) : `(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _),`
* X ms.rs:427 `_mm512_loadu_si512` (région) : `(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _),`
* U ms.rs:428 `*const` (région ; portée line : lignes 428 à 428) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.d.as_ptr().add(i) as *const __m128i)),`
* U ms.rs:428 `.add(` (région ; portée line : lignes 428 à 428) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.d.as_ptr().add(i) as *const __m128i)),`
* X ms.rs:428 `_mm512_cvtepu8_epi32` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.d.as_ptr().add(i) as *const __m128i)),`
* X ms.rs:428 `_mm_loadu_si128` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.d.as_ptr().add(i) as *const __m128i)),`
* X ms.rs:428 `__m128i` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.d.as_ptr().add(i) as *const __m128i)),`
* U ms.rs:429 `*const` (région ; portée line : lignes 429 à 429) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.q.as_ptr().add(i) as *const __m128i)))`
* U ms.rs:429 `.add(` (région ; portée line : lignes 429 à 429) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.q.as_ptr().add(i) as *const __m128i)))`
* X ms.rs:429 `_mm512_cvtepu8_epi32` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.q.as_ptr().add(i) as *const __m128i)))`
* X ms.rs:429 `_mm_loadu_si128` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.q.as_ptr().add(i) as *const __m128i)))`
* X ms.rs:429 `__m128i` (région) : `_mm512_cvtepu8_epi32(_mm_loadu_si128(c.q.as_ptr().add(i) as *const __m128i)))`
* X ms.rs:431 `_mm512_cmpge_epi32_mask` (région) : `let m = _mm512_cmpge_epi32_mask(sd, d0) & _mm512_cmplt_epi32_mask(sd, d1) & _mm512_cmpge_epi32_mask(d, r0)`
* X ms.rs:431 `_mm512_cmplt_epi32_mask` (région) : `let m = _mm512_cmpge_epi32_mask(sd, d0) & _mm512_cmplt_epi32_mask(sd, d1) & _mm512_cmpge_epi32_mask(d, r0)`
* X ms.rs:431 `_mm512_cmpge_epi32_mask` (région) : `let m = _mm512_cmpge_epi32_mask(sd, d0) & _mm512_cmplt_epi32_mask(sd, d1) & _mm512_cmpge_epi32_mask(d, r0)`
* X ms.rs:432 `_mm512_cmple_epi32_mask` (région) : `& _mm512_cmple_epi32_mask(d, r1) & _mm512_cmplt_epi32_mask(q, q0);`
* X ms.rs:432 `_mm512_cmplt_epi32_mask` (région) : `& _mm512_cmple_epi32_mask(d, r1) & _mm512_cmplt_epi32_mask(q, q0);`
* X ms.rs:433 `_mm512_maskz_mov_epi32` (région) : `let p = _mm512_maskz_mov_epi32(m, _mm512_mullo_epi32(pr, d));`
* X ms.rs:433 `_mm512_mullo_epi32` (région) : `let p = _mm512_maskz_mov_epi32(m, _mm512_mullo_epi32(pr, d));`
* X ms.rs:434 `_mm512_add_epi64` (région) : `a0 = _mm512_add_epi64(a0, _mm512_cvtepi32_epi64(_mm512_castsi512_si256(p)));`
* X ms.rs:434 `_mm512_cvtepi32_epi64` (région) : `a0 = _mm512_add_epi64(a0, _mm512_cvtepi32_epi64(_mm512_castsi512_si256(p)));`
* X ms.rs:434 `_mm512_castsi512_si256` (région) : `a0 = _mm512_add_epi64(a0, _mm512_cvtepi32_epi64(_mm512_castsi512_si256(p)));`
* X ms.rs:435 `_mm512_add_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64::<1>(p)));`
* X ms.rs:435 `_mm512_cvtepi32_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64::<1>(p)));`
* X ms.rs:435 `_mm512_extracti64x4_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64::<1>(p)));`
* X ms.rs:438 `_mm512_reduce_add_epi64` (région) : `_mm512_reduce_add_epi64(_mm512_add_epi64(a0, a1)) + q6_natural(c, i, hi) // reste (< 16 lignes)`
* X ms.rs:438 `_mm512_add_epi64` (région) : `_mm512_reduce_add_epi64(_mm512_add_epi64(a0, a1)) + q6_natural(c, i, hi) // reste (< 16 lignes)`
* X ms.rs:456 `#[target_feature` (région) : `#[target_feature(enable = "avx512f,avx512bw,avx512vl,bmi2")]`
* U ms.rs:457 `unsafe` (région ; portée brace : lignes 457 à 501) : `unsafe fn q1_tuned(c: &Cols, lo: usize, hi: usize, acc: &mut Q1Acc) {`
* X ms.rs:458 `_mm512_set1_epi32` (région) : `let lim = _mm512_set1_epi32(10471);`
* X ms.rs:459 `_mm512_set1_epi32` (région) : `let c100 = _mm512_set1_epi32(100);`
* X ms.rs:462 `_mm512_setzero_si512` (région) : `let z = _mm512_setzero_si512();`
* U ms.rs:467 `*const` (région ; portée line : lignes 467 à 467) : `let pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), lim);`
* U ms.rs:467 `.add(` (région ; portée line : lignes 467 à 467) : `let pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), lim);`
* X ms.rs:467 `_mm512_cmple_epi32_mask` (région) : `let pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), lim);`
* X ms.rs:467 `_mm512_loadu_si512` (région) : `let pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), lim);`
* U ms.rs:468 `*const` (région ; portée line : lignes 468 à 468) : `let ld8 = |p: &Vec<u8>| _mm512_cvtepu8_epi32(_mm_loadu_si128(p.as_ptr().add(i) as *const __m128i));`
* U ms.rs:468 `.add(` (région ; portée line : lignes 468 à 468) : `let ld8 = |p: &Vec<u8>| _mm512_cvtepu8_epi32(_mm_loadu_si128(p.as_ptr().add(i) as *const __m128i));`
* X ms.rs:468 `_mm512_cvtepu8_epi32` (région) : `let ld8 = |p: &Vec<u8>| _mm512_cvtepu8_epi32(_mm_loadu_si128(p.as_ptr().add(i) as *const __m128i));`
* X ms.rs:468 `_mm_loadu_si128` (région) : `let ld8 = |p: &Vec<u8>| _mm512_cvtepu8_epi32(_mm_loadu_si128(p.as_ptr().add(i) as *const __m128i));`
* X ms.rs:468 `__m128i` (région) : `let ld8 = |p: &Vec<u8>| _mm512_cvtepu8_epi32(_mm_loadu_si128(p.as_ptr().add(i) as *const __m128i));`
* X ms.rs:469 `_mm512_add_epi32` (région) : `let vg = _mm512_add_epi32(_mm512_slli_epi32(ld8(&c.rf), 1), ld8(&c.ls));`
* X ms.rs:469 `_mm512_slli_epi32` (région) : `let vg = _mm512_add_epi32(_mm512_slli_epi32(ld8(&c.rf), 1), ld8(&c.ls));`
* X ms.rs:472 `_mm512_add_epi32` (région) : `let vt = _mm512_add_epi32(ld8(&c.t), c100);`
* U ms.rs:473 `*const` (région ; portée line : lignes 473 à 473) : `let vp = _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _);`
* U ms.rs:473 `.add(` (région ; portée line : lignes 473 à 473) : `let vp = _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _);`
* X ms.rs:473 `_mm512_loadu_si512` (région) : `let vp = _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _);`
* X ms.rs:474 `_mm512_mullo_epi32` (région) : `let vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));`
* X ms.rs:474 `_mm512_sub_epi32` (région) : `let vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));`
* X ms.rs:475 `_mm512_mul_epi32` (région) : `let che = _mm512_mul_epi32(vdp, vt);`
* X ms.rs:476 `_mm512_mul_epi32` (région) : `let cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));`
* X ms.rs:476 `_mm512_srli_epi64` (région) : `let cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));`
* X ms.rs:476 `_mm512_srli_epi64` (région) : `let cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));`
* X ms.rs:478 `_mm512_mask_cmpeq_epi32_mask` (région) : `let m = _mm512_mask_cmpeq_epi32_mask(pass, vg, _mm512_set1_epi32(g as i32));`
* X ms.rs:478 `_mm512_set1_epi32` (région) : `let m = _mm512_mask_cmpeq_epi32_mask(pass, vg, _mm512_set1_epi32(g as i32));`
* X ms.rs:480 `_mm512_mask_add_epi32` (région) : `aq[g] = _mm512_mask_add_epi32(aq[g], m, aq[g], vq);`
* X ms.rs:481 `_mm512_mask_add_epi32` (région) : `ap[g] = _mm512_mask_add_epi32(ap[g], m, ap[g], vp);`
* X ms.rs:482 `_mm512_mask_add_epi32` (région) : `adp[g] = _mm512_mask_add_epi32(adp[g], m, adp[g], vdp);`
* X ms.rs:483 `_mm512_mask_add_epi64` (région) : `ace[g] = _mm512_mask_add_epi64(ace[g], _pext_u32(m as u32, 0x5555) as u8, ace[g], che);`
* X ms.rs:484 `_mm512_mask_add_epi64` (région) : `aco[g] = _mm512_mask_add_epi64(aco[g], _pext_u32(m as u32, 0xAAAA) as u8, aco[g], cho);`
* X ms.rs:490 `_mm512_reduce_add_epi32` (région) : `acc[g][1] += _mm512_reduce_add_epi32(aq[g]) as i64;`
* X ms.rs:491 `_mm512_reduce_add_epi32` (région) : `acc[g][2] += _mm512_reduce_add_epi32(ap[g]) as i64;`
* X ms.rs:492 `_mm512_reduce_add_epi64` (région) : `acc[g][3] += _mm512_reduce_add_epi64(_mm512_add_epi64(`
* X ms.rs:492 `_mm512_add_epi64` (région) : `acc[g][3] += _mm512_reduce_add_epi64(_mm512_add_epi64(`
* X ms.rs:493 `_mm512_cvtepi32_epi64` (région) : `_mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])),`
* X ms.rs:493 `_mm512_castsi512_si256` (région) : `_mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])),`
* X ms.rs:494 `_mm512_cvtepi32_epi64` (région) : `_mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(adp[g], 1))));`
* X ms.rs:494 `_mm512_extracti64x4_epi64` (région) : `_mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(adp[g], 1))));`
* X ms.rs:495 `_mm512_reduce_add_epi64` (région) : `acc[g][4] += _mm512_reduce_add_epi64(_mm512_add_epi64(ace[g], aco[g]));`
* X ms.rs:495 `_mm512_add_epi64` (région) : `acc[g][4] += _mm512_reduce_add_epi64(_mm512_add_epi64(ace[g], aco[g]));`
* U ms.rs:510 `unsafe` (région ; portée brace : lignes 510 à 510) : `unsafe { q1_tuned(c, lo, hi, &mut a) };`
* U ms.rs:513 `unsafe` (région ; portée brace : lignes 513 à 513) : `unsafe { q6_tuned_v(c, lo, hi) }`
* U ms.rs:547 `unsafe` (hors région ; portée brace : lignes 547 à 547) : `("tuned_v", false) => unsafe { q6_tuned_v(&c, 0, N6) },`
* U ms.rs:550 `unsafe` (hors région ; portée brace : lignes 550 à 550) : `unsafe { q1_tuned(&c, 0, N6, &mut a) };`
* U ms.rs:561 `unsafe` (hors région ; portée brace : lignes 561 à 561) : `unsafe { q1_tuned(c, lo, hi, &mut a) };`
* U ms.rs:606 `unsafe` (région ; portée brace : lignes 606 à 606) : `unsafe { _mm_prefetch::<_MM_HINT_ET0>(tab.as_ptr().add(h[b] as usize) as *const i8) };`
* U ms.rs:606 `*const` (région ; portée line : lignes 606 à 606) : `unsafe { _mm_prefetch::<_MM_HINT_ET0>(tab.as_ptr().add(h[b] as usize) as *const i8) };`
* U ms.rs:606 `.add(` (région ; portée line : lignes 606 à 606) : `unsafe { _mm_prefetch::<_MM_HINT_ET0>(tab.as_ptr().add(h[b] as usize) as *const i8) };`
* X ms.rs:606 `_mm_prefetch` (région) : `unsafe { _mm_prefetch::<_MM_HINT_ET0>(tab.as_ptr().add(h[b] as usize) as *const i8) };`
* U ms.rs:665 `unsafe` (hors région ; portée brace : lignes 665 à 665) : `unsafe { a.get_unchecked_mut(i).v = *c };`
* U ms.rs:665 `get_unchecked_mut` (hors région ; portée line : lignes 665 à 665) : `unsafe { a.get_unchecked_mut(i).v = *c };`
* U ms.rs:669 `unsafe` (hors région ; portée brace : lignes 669 à 669) : `unsafe { a.get_unchecked_mut(i).l = l };`
* U ms.rs:669 `get_unchecked_mut` (hors région ; portée line : lignes 669 à 669) : `unsafe { a.get_unchecked_mut(i).l = l };`
* U ms.rs:671 `unsafe` (hors région ; portée brace : lignes 671 à 671) : `unsafe { a.get_unchecked_mut(i).r = r };`
* U ms.rs:671 `get_unchecked_mut` (hors région ; portée line : lignes 671 à 671) : `unsafe { a.get_unchecked_mut(i).r = r };`
* U ms.rs:673 `unsafe` (hors région ; portée brace : lignes 673 à 677) : `unsafe {`
* U ms.rs:674 `get_unchecked_mut` (hors région ; portée line : lignes 674 à 674) : `let n = a.get_unchecked_mut(i);`
* U ms.rs:682 `unsafe` (hors région ; portée brace : lignes 682 à 682) : `if i < 0 { 0 } else { let n = unsafe { *a.get_unchecked(i as usize) }; n.v + ac_sum(a, n.l) + ac_sum(a, n.r) }`
* U ms.rs:682 `get_unchecked` (hors région ; portée line : lignes 682 à 682) : `if i < 0 { 0 } else { let n = unsafe { *a.get_unchecked(i as usize) }; n.v + ac_sum(a, n.l) + ac_sum(a, n.r) }`
* U ms.rs:688 `unsafe` (hors région ; portée brace : lignes 688 à 688) : `unsafe { a.get_unchecked_mut(i as usize).v = q + i as i64 };`
* U ms.rs:688 `get_unchecked_mut` (hors région ; portée line : lignes 688 à 688) : `unsafe { a.get_unchecked_mut(i as usize).v = q + i as i64 };`
* U ms.rs:692 `unsafe` (hors région ; portée brace : lignes 692 à 696) : `unsafe {`
* U ms.rs:693 `get_unchecked_mut` (hors région ; portée line : lignes 693 à 693) : `let n = a.get_unchecked_mut(i as usize);`
* U ms.rs:699 `unsafe` (hors région ; portée brace : lignes 699 à 703) : `unsafe {`
* U ms.rs:700 `get_unchecked_mut` (hors région ; portée line : lignes 700 à 700) : `let n = a.get_unchecked_mut(i as usize);`
* U ms.rs:718 `unsafe` (région ; portée brace : lignes 718 à 718) : `unsafe { a.get_unchecked_mut(i as usize).v = q + i as i64 };`
* U ms.rs:718 `get_unchecked_mut` (région ; portée line : lignes 718 à 718) : `unsafe { a.get_unchecked_mut(i as usize).v = q + i as i64 };`
* U ms.rs:720 `unsafe` (région ; portée brace : lignes 720 à 720) : `let p = unsafe { a.get_unchecked_mut(parent as usize) };`
* U ms.rs:720 `get_unchecked_mut` (région ; portée line : lignes 720 à 720) : `let p = unsafe { a.get_unchecked_mut(parent as usize) };`
* U ms.rs:730 `unsafe` (région ; portée brace : lignes 730 à 734) : `unsafe {`
* U ms.rs:731 `get_unchecked_mut` (région ; portée line : lignes 731 à 731) : `let n = a.get_unchecked_mut(i as usize);`
* U ms.rs:751 `unsafe` (région ; portée brace : lignes 751 à 751) : `let n = unsafe { *a.get_unchecked(stk[sp] as usize) };`
* U ms.rs:751 `get_unchecked` (région ; portée line : lignes 751 à 751) : `let n = unsafe { *a.get_unchecked(stk[sp] as usize) };`
* X ms.rs:847 `#[target_feature` (région) : `#[target_feature(enable = "avx512f")]`
* U ms.rs:848 `unsafe` (région ; portée brace : lignes 848 à 870) : `unsafe fn k9_rows_v(inp: &[f64], out: &mut [f64], r0: usize) {`
* X ms.rs:849 `_mm512_set1_pd` (région) : `let q = _mm512_set1_pd(0.25);`
* U ms.rs:857 `unsafe` (région ; portée brace : lignes 857 à 862) : `unsafe {`
* U ms.rs:858 `.add(` (région ; portée line : lignes 858 à 858) : `let s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up.as_ptr().add(j)), _mm512_loadu_pd(dn.as_p`
* U ms.rs:858 `.add(` (région ; portée line : lignes 858 à 858) : `let s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up.as_ptr().add(j)), _mm512_loadu_pd(dn.as_p`
* X ms.rs:858 `_mm512_add_pd` (région) : `let s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up.as_ptr().add(j)), _mm512_loadu_pd(dn.as_p`
* X ms.rs:858 `_mm512_add_pd` (région) : `let s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up.as_ptr().add(j)), _mm512_loadu_pd(dn.as_p`
* X ms.rs:858 `_mm512_add_pd` (région) : `let s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up.as_ptr().add(j)), _mm512_loadu_pd(dn.as_p`
* X ms.rs:858 `_mm512_loadu_pd` (région) : `let s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up.as_ptr().add(j)), _mm512_loadu_pd(dn.as_p`
* X ms.rs:858 `_mm512_loadu_pd` (région) : `let s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd(up.as_ptr().add(j)), _mm512_loadu_pd(dn.as_p`
* U ms.rs:859 `.add(` (région ; portée line : lignes 859 à 859) : `_mm512_loadu_pd(mid.as_ptr().add(j - 1))),`
* X ms.rs:859 `_mm512_loadu_pd` (région) : `_mm512_loadu_pd(mid.as_ptr().add(j - 1))),`
* U ms.rs:860 `.add(` (région ; portée line : lignes 860 à 860) : `_mm512_loadu_pd(mid.as_ptr().add(j + 1)));`
* X ms.rs:860 `_mm512_loadu_pd` (région) : `_mm512_loadu_pd(mid.as_ptr().add(j + 1)));`
* U ms.rs:861 `.add(` (région ; portée line : lignes 861 à 861) : `_mm512_storeu_pd(o.as_mut_ptr().add(j), _mm512_mul_pd(q, s));`
* X ms.rs:861 `_mm512_storeu_pd` (région) : `_mm512_storeu_pd(o.as_mut_ptr().add(j), _mm512_mul_pd(q, s));`
* X ms.rs:861 `_mm512_mul_pd` (région) : `_mm512_storeu_pd(o.as_mut_ptr().add(j), _mm512_mul_pd(q, s));`
* U ms.rs:873 `*const` (région ; portée line : lignes 873 à 873) : `struct K9Job { a: *const f64, b: *mut f64, vec: bool }`
* U ms.rs:873 `*mut` (région ; portée line : lignes 873 à 873) : `struct K9Job { a: *const f64, b: *mut f64, vec: bool }`
* U ms.rs:874 `unsafe` (région ; portée brace : lignes 874 à 874) : `unsafe impl Sync for K9Job {}`
* U ms.rs:879 `unsafe` (région ; portée brace : lignes 879 à 879) : `let inp = unsafe { std::slice::from_raw_parts(self.a, M9 * M9) };`
* U ms.rs:879 `from_raw_parts` (région ; portée line : lignes 879 à 879) : `let inp = unsafe { std::slice::from_raw_parts(self.a, M9 * M9) };`
* U ms.rs:880 `unsafe` (région ; portée brace : lignes 880 à 880) : `let out = unsafe { std::slice::from_raw_parts_mut(self.b.add(r0 * M9), (r1 - r0) * M9) };`
* U ms.rs:880 `from_raw_parts_mut` (région ; portée line : lignes 880 à 880) : `let out = unsafe { std::slice::from_raw_parts_mut(self.b.add(r0 * M9), (r1 - r0) * M9) };`
* U ms.rs:880 `.add(` (région ; portée line : lignes 880 à 880) : `let out = unsafe { std::slice::from_raw_parts_mut(self.b.add(r0 * M9), (r1 - r0) * M9) };`
* U ms.rs:881 `unsafe` (région ; portée brace : lignes 881 à 881) : `if self.vec { unsafe { k9_rows_v(inp, out, r0) } } else { k9_rows(inp, out, r0) }`
* U ms.rs:941 `unsafe` (région ; portée brace : lignes 941 à 945) : `None => unsafe {`
* U ms.rs:942 `from_raw_parts` (région ; portée line : lignes 942 à 942) : `let inp = std::slice::from_raw_parts(a, M9 * M9);`
* U ms.rs:943 `from_raw_parts_mut` (région ; portée line : lignes 943 à 943) : `let out = std::slice::from_raw_parts_mut(b.add(M9), (M9 - 2) * M9);`
* U ms.rs:943 `.add(` (région ; portée line : lignes 943 à 943) : `let out = std::slice::from_raw_parts_mut(b.add(M9), (M9 - 2) * M9);`
* U ms.rs:950 `unsafe` (hors région ; portée brace : lignes 950 à 950) : `let s: f64 = unsafe { std::slice::from_raw_parts(a, M9 * M9) }.iter().sum();`
* U ms.rs:950 `from_raw_parts` (hors région ; portée line : lignes 950 à 950) : `let s: f64 = unsafe { std::slice::from_raw_parts(a, M9 * M9) }.iter().sum();`
* U ms.rs:1005 `unsafe` (hors région ; portée brace : lignes 1005 à 1005) : `unsafe impl Sync for Spsc {}`
* U ms.rs:1034 `unsafe` (hors région ; portée brace : lignes 1034 à 1034) : `unsafe { *q.buf[w & (CAP10 - 1)].get() = x };`
* U ms.rs:1048 `unsafe` (hors région ; portée brace : lignes 1048 à 1048) : `sum += unsafe { *q.buf[rd & (CAP10 - 1)].get() };`

## nim

* U ms.nim:12 `ptr UncheckedArray` (hors région ; portée line : lignes 12 à 12) : `p: ptr UncheckedArray[T]`
* U ms.nim:17 `ptr UncheckedArray` (hors région ; portée line : lignes 17 à 17) : `result.p = cast[ptr UncheckedArray[T]](aligned_alloc(64, csize_t((s.len + 63) and not 63)))`
* U ms.nim:17 `cast[` (hors région ; portée line : lignes 17 à 17) : `result.p = cast[ptr UncheckedArray[T]](aligned_alloc(64, csize_t((s.len + 63) and not 63)))`
* U ms.nim:18 `unsafeAddr` (hors région ; portée line : lignes 18 à 18) : `copyMem(result.p, s[0].unsafeAddr, s.len)`
* U ms.nim:18 `copyMem` (hors région ; portée line : lignes 18 à 18) : `copyMem(result.p, s[0].unsafeAddr, s.len)`
* X ms.nim:28 `__m512` (région) : `M512 {.importc: "__m512", header: "<immintrin.h>".} = object`
* X ms.nim:28 `immintrin.h` (région) : `M512 {.importc: "__m512", header: "<immintrin.h>".} = object`
* X ms.nim:29 `__m512d` (région) : `M512d {.importc: "__m512d", header: "<immintrin.h>".} = object`
* X ms.nim:29 `immintrin.h` (région) : `M512d {.importc: "__m512d", header: "<immintrin.h>".} = object`
* X ms.nim:30 `__m256` (région) : `M256 {.importc: "__m256", header: "<immintrin.h>".} = object`
* X ms.nim:30 `immintrin.h` (région) : `M256 {.importc: "__m256", header: "<immintrin.h>".} = object`
* X ms.nim:31 `_mm512_setzero_ps` (région) : `proc mm512_setzero_ps(): M512 {.importc: "_mm512_setzero_ps", header: "<immintrin.h>".}`
* X ms.nim:31 `immintrin.h` (région) : `proc mm512_setzero_ps(): M512 {.importc: "_mm512_setzero_ps", header: "<immintrin.h>".}`
* X ms.nim:32 `_mm512_setzero_pd` (région) : `proc mm512_setzero_pd(): M512d {.importc: "_mm512_setzero_pd", header: "<immintrin.h>".}`
* X ms.nim:32 `immintrin.h` (région) : `proc mm512_setzero_pd(): M512d {.importc: "_mm512_setzero_pd", header: "<immintrin.h>".}`
* X ms.nim:33 `_mm512_set1_ps` (région) : `proc mm512_set1_ps(x: float32): M512 {.importc: "_mm512_set1_ps", header: "<immintrin.h>".}`
* X ms.nim:33 `immintrin.h` (région) : `proc mm512_set1_ps(x: float32): M512 {.importc: "_mm512_set1_ps", header: "<immintrin.h>".}`
* X ms.nim:34 `_mm512_load_ps` (région) : `proc mm512_load_ps(p: pointer): M512 {.importc: "_mm512_load_ps", header: "<immintrin.h>".}`
* X ms.nim:34 `immintrin.h` (région) : `proc mm512_load_ps(p: pointer): M512 {.importc: "_mm512_load_ps", header: "<immintrin.h>".}`
* X ms.nim:35 `_mm512_mul_ps` (région) : `proc mm512_mul_ps(a, b: M512): M512 {.importc: "_mm512_mul_ps", header: "<immintrin.h>".}`
* X ms.nim:35 `immintrin.h` (région) : `proc mm512_mul_ps(a, b: M512): M512 {.importc: "_mm512_mul_ps", header: "<immintrin.h>".}`
* X ms.nim:36 `_mm512_add_ps` (région) : `proc mm512_add_ps(a, b: M512): M512 {.importc: "_mm512_add_ps", header: "<immintrin.h>".}`
* X ms.nim:36 `immintrin.h` (région) : `proc mm512_add_ps(a, b: M512): M512 {.importc: "_mm512_add_ps", header: "<immintrin.h>".}`
* X ms.nim:37 `_mm512_fmadd_ps` (région) : `proc mm512_fmadd_ps(a, b, c: M512): M512 {.importc: "_mm512_fmadd_ps", header: "<immintrin.h>".}`
* X ms.nim:37 `immintrin.h` (région) : `proc mm512_fmadd_ps(a, b, c: M512): M512 {.importc: "_mm512_fmadd_ps", header: "<immintrin.h>".}`
* X ms.nim:38 `_mm512_reduce_add_ps` (région) : `proc mm512_reduce_add_ps(a: M512): float32 {.importc: "_mm512_reduce_add_ps", header: "<immintrin.h>".}`
* X ms.nim:38 `immintrin.h` (région) : `proc mm512_reduce_add_ps(a: M512): float32 {.importc: "_mm512_reduce_add_ps", header: "<immintrin.h>".}`
* X ms.nim:39 `_mm512_add_pd` (région) : `proc mm512_add_pd(a, b: M512d): M512d {.importc: "_mm512_add_pd", header: "<immintrin.h>".}`
* X ms.nim:39 `immintrin.h` (région) : `proc mm512_add_pd(a, b: M512d): M512d {.importc: "_mm512_add_pd", header: "<immintrin.h>".}`
* X ms.nim:40 `_mm512_cvtps_pd` (région) : `proc mm512_cvtps_pd(a: M256): M512d {.importc: "_mm512_cvtps_pd", header: "<immintrin.h>".}`
* X ms.nim:40 `immintrin.h` (région) : `proc mm512_cvtps_pd(a: M256): M512d {.importc: "_mm512_cvtps_pd", header: "<immintrin.h>".}`
* X ms.nim:41 `_mm512_castps512_ps256` (région) : `proc mm512_castps512_ps256(a: M512): M256 {.importc: "_mm512_castps512_ps256", header: "<immintrin.h>".}`
* X ms.nim:41 `immintrin.h` (région) : `proc mm512_castps512_ps256(a: M512): M256 {.importc: "_mm512_castps512_ps256", header: "<immintrin.h>".}`
* X ms.nim:42 `_mm512_extractf32x8_ps` (région) : `proc mm512_extractf32x8_ps(a: M512, i: cint): M256 {.importc: "_mm512_extractf32x8_ps", header: "<immintrin.h>`
* X ms.nim:42 `immintrin.h` (région) : `proc mm512_extractf32x8_ps(a: M512, i: cint): M256 {.importc: "_mm512_extractf32x8_ps", header: "<immintrin.h>`
* X ms.nim:43 `_mm512_reduce_add_pd` (région) : `proc mm512_reduce_add_pd(a: M512d): float {.importc: "_mm512_reduce_add_pd", header: "<immintrin.h>".}`
* X ms.nim:43 `immintrin.h` (région) : `proc mm512_reduce_add_pd(a: M512d): float {.importc: "_mm512_reduce_add_pd", header: "<immintrin.h>".}`
* X ms.nim:45 `_mm_pause` (hors région) : `proc cpuRelax() {.importc: "_mm_pause", header: "<immintrin.h>".}`
* X ms.nim:45 `immintrin.h` (hors région) : `proc cpuRelax() {.importc: "_mm_pause", header: "<immintrin.h>".}`
* U ms.nim:55 `{.push boundChecks: off, overflowChecks: off` (région ; portée pushpop : lignes 55 à 81) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:61 `addr` (hors région ; portée line : lignes 61 à 61) : `let q = ps[i + k].addr`
* U ms.nim:66 `ptr UncheckedArray` (région ; portée line : lignes 66 à 66) : `proc k1SoA(vx, vy, vz, m: ptr UncheckedArray[float32], n: int): float {.noinline.} =`
* U ms.nim:72 `addr` (région ; portée line : lignes 72 à 72) : `let x = mm512_load_ps(vx[i].addr)`
* U ms.nim:73 `addr` (région ; portée line : lignes 73 à 73) : `let y = mm512_load_ps(vy[i].addr)`
* U ms.nim:74 `addr` (région ; portée line : lignes 74 à 74) : `let z = mm512_load_ps(vz[i].addr)`
* U ms.nim:75 `addr` (région ; portée line : lignes 75 à 75) : `let w = mm512_load_ps(m[i].addr)`
* U ms.nim:101 `addr` (hors région ; portée line : lignes 101 à 101) : `for i in 0 ..< N1: copyMem(ps[i].addr, raw.p[16 * i].addr, sizeof(Particle))`
* U ms.nim:101 `addr` (hors région ; portée line : lignes 101 à 101) : `for i in 0 ..< N1: copyMem(ps[i].addr, raw.p[16 * i].addr, sizeof(Particle))`
* U ms.nim:101 `copyMem` (hors région ; portée line : lignes 101 à 101) : `for i in 0 ..< N1: copyMem(ps[i].addr, raw.p[16 * i].addr, sizeof(Particle))`
* U ms.nim:109 `ptr UncheckedArray` (région ; portée line : lignes 109 à 109) : `var c: array[16, ptr UncheckedArray[float32]]`
* U ms.nim:111 `ptr UncheckedArray` (région ; portée line : lignes 111 à 111) : `c[k] = cast[ptr UncheckedArray[float32]](aligned_alloc(64, csize_t(N1 * 4)))`
* U ms.nim:111 `cast[` (région ; portée line : lignes 111 à 111) : `c[k] = cast[ptr UncheckedArray[float32]](aligned_alloc(64, csize_t(N1 * 4)))`
* U ms.nim:132 `{.push boundChecks: off` (hors région ; portée pushpop : lignes 132 à 137) : `{.push boundChecks: off.}`
* U ms.nim:133 `ptr UncheckedArray` (hors région ; portée line : lignes 133 à 133) : `proc k2Chase(a: ptr UncheckedArray[uint32], h: int): uint32 {.noinline.} =`
* U ms.nim:166 `addr` (région ; portée line : lignes 166 à 166) : `ctr[t] = if padded: pad[t].v.addr else: packed[t].addr`
* U ms.nim:166 `addr` (région ; portée line : lignes 166 à 166) : `ctr[t] = if padded: pad[t].v.addr else: packed[t].addr`
* X ms.nim:237 `__m512i` (région) : `type M512i {.importc: "__m512i", header: "<immintrin.h>".} = object`
* X ms.nim:237 `immintrin.h` (région) : `type M512i {.importc: "__m512i", header: "<immintrin.h>".} = object`
* X ms.nim:238 `_mm512_setzero_si512` (région) : `proc mm512_setzero_si512(): M512i {.importc: "_mm512_setzero_si512", header: "<immintrin.h>".}`
* X ms.nim:238 `immintrin.h` (région) : `proc mm512_setzero_si512(): M512i {.importc: "_mm512_setzero_si512", header: "<immintrin.h>".}`
* X ms.nim:239 `_mm512_loadu_si512` (région) : `proc mm512_loadu_si512(p: pointer): M512i {.importc: "_mm512_loadu_si512", header: "<immintrin.h>".}`
* X ms.nim:239 `immintrin.h` (région) : `proc mm512_loadu_si512(p: pointer): M512i {.importc: "_mm512_loadu_si512", header: "<immintrin.h>".}`
* X ms.nim:240 `_mm512_movepi8_mask` (région) : `proc mm512_movepi8_mask(a: M512i): uint64 {.importc: "_mm512_movepi8_mask", header: "<immintrin.h>".}`
* X ms.nim:240 `immintrin.h` (région) : `proc mm512_movepi8_mask(a: M512i): uint64 {.importc: "_mm512_movepi8_mask", header: "<immintrin.h>".}`
* X ms.nim:241 `_mm512_maskz_mov_epi8` (région) : `proc mm512_maskz_mov_epi8(k: uint64, a: M512i): M512i {.importc: "_mm512_maskz_mov_epi8", header: "<immintrin.`
* X ms.nim:241 `immintrin.h` (région) : `proc mm512_maskz_mov_epi8(k: uint64, a: M512i): M512i {.importc: "_mm512_maskz_mov_epi8", header: "<immintrin.`
* X ms.nim:242 `_mm512_sad_epu8` (région) : `proc mm512_sad_epu8(a, b: M512i): M512i {.importc: "_mm512_sad_epu8", header: "<immintrin.h>".}`
* X ms.nim:242 `immintrin.h` (région) : `proc mm512_sad_epu8(a, b: M512i): M512i {.importc: "_mm512_sad_epu8", header: "<immintrin.h>".}`
* X ms.nim:243 `_mm512_add_epi64` (région) : `proc mm512_add_epi64(a, b: M512i): M512i {.importc: "_mm512_add_epi64", header: "<immintrin.h>".}`
* X ms.nim:243 `immintrin.h` (région) : `proc mm512_add_epi64(a, b: M512i): M512i {.importc: "_mm512_add_epi64", header: "<immintrin.h>".}`
* X ms.nim:244 `_mm512_reduce_add_epi64` (région) : `proc mm512_reduce_add_epi64(a: M512i): int64 {.importc: "_mm512_reduce_add_epi64", header: "<immintrin.h>".}`
* X ms.nim:244 `immintrin.h` (région) : `proc mm512_reduce_add_epi64(a: M512i): int64 {.importc: "_mm512_reduce_add_epi64", header: "<immintrin.h>".}`
* U ms.nim:251 `unsafeAddr` (région ; portée line : lignes 251 à 251) : `let x = mm512_loadu_si512(v[i].unsafeAddr)`
* U ms.nim:263 `{.push boundChecks: off, overflowChecks: off` (hors région ; portée pushpop : lignes 263 à 283) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:274 `addr` (hors région ; portée line : lignes 274 à 274) : `copyMem(w.addr, v[i].unsafeAddr, 8)`
* U ms.nim:274 `unsafeAddr` (hors région ; portée line : lignes 274 à 274) : `copyMem(w.addr, v[i].unsafeAddr, 8)`
* U ms.nim:274 `copyMem` (hors région ; portée line : lignes 274 à 274) : `copyMem(w.addr, v[i].unsafeAddr, 8)`
* U ms.nim:287 `addr` (hors région ; portée line : lignes 287 à 287) : `copyMem(d[0].addr, b.p, b.len)`
* U ms.nim:287 `copyMem` (hors région ; portée line : lignes 287 à 287) : `copyMem(d[0].addr, b.p, b.len)`
* U ms.nim:300 `ptr UncheckedArray` (région ; portée line : lignes 300 à 300) : `proc k5Natural(a, b: ptr UncheckedArray[float32], n: int): float32 {.noinline.} =`
* U ms.nim:302 `ptr UncheckedArray` (région ; portée line : lignes 302 à 302) : `proc k5Tuned(a, b: ptr UncheckedArray[float32], n: int): float32 {.noinline.} =`
* U ms.nim:309 `addr` (région ; portée line : lignes 309 à 309) : `s0 = mm512_fmadd_ps(mm512_load_ps(a[i].addr), mm512_load_ps(b[i].addr), s0)`
* U ms.nim:309 `addr` (région ; portée line : lignes 309 à 309) : `s0 = mm512_fmadd_ps(mm512_load_ps(a[i].addr), mm512_load_ps(b[i].addr), s0)`
* U ms.nim:310 `addr` (région ; portée line : lignes 310 à 310) : `s1 = mm512_fmadd_ps(mm512_load_ps(a[i + 16].addr), mm512_load_ps(b[i + 16].addr), s1)`
* U ms.nim:310 `addr` (région ; portée line : lignes 310 à 310) : `s1 = mm512_fmadd_ps(mm512_load_ps(a[i + 16].addr), mm512_load_ps(b[i + 16].addr), s1)`
* U ms.nim:311 `addr` (région ; portée line : lignes 311 à 311) : `s2 = mm512_fmadd_ps(mm512_load_ps(a[i + 32].addr), mm512_load_ps(b[i + 32].addr), s2)`
* U ms.nim:311 `addr` (région ; portée line : lignes 311 à 311) : `s2 = mm512_fmadd_ps(mm512_load_ps(a[i + 32].addr), mm512_load_ps(b[i + 32].addr), s2)`
* U ms.nim:312 `addr` (région ; portée line : lignes 312 à 312) : `s3 = mm512_fmadd_ps(mm512_load_ps(a[i + 48].addr), mm512_load_ps(b[i + 48].addr), s3)`
* U ms.nim:312 `addr` (région ; portée line : lignes 312 à 312) : `s3 = mm512_fmadd_ps(mm512_load_ps(a[i + 48].addr), mm512_load_ps(b[i + 48].addr), s3)`
* U ms.nim:315 `ptr UncheckedArray` (hors région ; portée line : lignes 315 à 315) : `var sinkA: ptr UncheckedArray[float32]`
* U ms.nim:324 `addr` (hors région ; portée line : lignes 324 à 324) : `volatileStore(sinkA.addr, a.p) # barrière d'optimisation`
* U ms.nim:325 `addr` (hors région ; portée line : lignes 325 à 325) : `let pa = volatileLoad(sinkA.addr)`
* U ms.nim:334 `ptr UncheckedArray` (hors région ; portée line : lignes 334 à 334) : `sd, pr: ptr UncheckedArray[int32]`
* U ms.nim:335 `ptr UncheckedArray` (hors région ; portée line : lignes 335 à 335) : `q, d, t, rf, ls: ptr UncheckedArray[uint8]`
* U ms.nim:341 `{.push boundChecks: off, overflowChecks: off` (hors région ; portée pushpop : lignes 341 à 346) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:358 `{.push boundChecks: off, overflowChecks: off` (hors région ; portée pushpop : lignes 358 à 378) : `{.push boundChecks: off, overflowChecks: off.}`
* X ms.nim:382 `__m256i` (région) : `M256i {.importc: "__m256i", header: "<immintrin.h>".} = object`
* X ms.nim:382 `immintrin.h` (région) : `M256i {.importc: "__m256i", header: "<immintrin.h>".} = object`
* X ms.nim:383 `__m128i` (région) : `M128i {.importc: "__m128i", header: "<immintrin.h>".} = object`
* X ms.nim:383 `immintrin.h` (région) : `M128i {.importc: "__m128i", header: "<immintrin.h>".} = object`
* X ms.nim:384 `_mm512_set1_epi32` (région) : `proc mm512_set1_epi32(x: int32): M512i {.importc: "_mm512_set1_epi32", header: "<immintrin.h>".}`
* X ms.nim:384 `immintrin.h` (région) : `proc mm512_set1_epi32(x: int32): M512i {.importc: "_mm512_set1_epi32", header: "<immintrin.h>".}`
* X ms.nim:385 `_mm_loadu_si128` (région) : `proc mm_loadu_si128(p: pointer): M128i {.importc: "_mm_loadu_si128", header: "<immintrin.h>".}`
* X ms.nim:385 `immintrin.h` (région) : `proc mm_loadu_si128(p: pointer): M128i {.importc: "_mm_loadu_si128", header: "<immintrin.h>".}`
* X ms.nim:386 `_mm512_cvtepu8_epi32` (région) : `proc mm512_cvtepu8_epi32(a: M128i): M512i {.importc: "_mm512_cvtepu8_epi32", header: "<immintrin.h>".}`
* X ms.nim:386 `immintrin.h` (région) : `proc mm512_cvtepu8_epi32(a: M128i): M512i {.importc: "_mm512_cvtepu8_epi32", header: "<immintrin.h>".}`
* X ms.nim:387 `_mm512_cmple_epi32_mask` (région) : `proc mm512_cmple_epi32_mask(a, b: M512i): uint16 {.importc: "_mm512_cmple_epi32_mask", header: "<immintrin.h>"`
* X ms.nim:387 `immintrin.h` (région) : `proc mm512_cmple_epi32_mask(a, b: M512i): uint16 {.importc: "_mm512_cmple_epi32_mask", header: "<immintrin.h>"`
* X ms.nim:388 `_mm512_cmpge_epi32_mask` (région) : `proc mm512_cmpge_epi32_mask(a, b: M512i): uint16 {.importc: "_mm512_cmpge_epi32_mask", header: "<immintrin.h>"`
* X ms.nim:388 `immintrin.h` (région) : `proc mm512_cmpge_epi32_mask(a, b: M512i): uint16 {.importc: "_mm512_cmpge_epi32_mask", header: "<immintrin.h>"`
* X ms.nim:389 `_mm512_cmplt_epi32_mask` (région) : `proc mm512_cmplt_epi32_mask(a, b: M512i): uint16 {.importc: "_mm512_cmplt_epi32_mask", header: "<immintrin.h>"`
* X ms.nim:389 `immintrin.h` (région) : `proc mm512_cmplt_epi32_mask(a, b: M512i): uint16 {.importc: "_mm512_cmplt_epi32_mask", header: "<immintrin.h>"`
* X ms.nim:390 `_mm512_mask_cmpeq_epi32_mask` (région) : `proc mm512_mask_cmpeq_epi32_mask(k: uint16, a, b: M512i): uint16 {.importc: "_mm512_mask_cmpeq_epi32_mask", he`
* X ms.nim:390 `immintrin.h` (région) : `proc mm512_mask_cmpeq_epi32_mask(k: uint16, a, b: M512i): uint16 {.importc: "_mm512_mask_cmpeq_epi32_mask", he`
* X ms.nim:391 `_mm512_add_epi32` (région) : `proc mm512_add_epi32(a, b: M512i): M512i {.importc: "_mm512_add_epi32", header: "<immintrin.h>".}`
* X ms.nim:391 `immintrin.h` (région) : `proc mm512_add_epi32(a, b: M512i): M512i {.importc: "_mm512_add_epi32", header: "<immintrin.h>".}`
* X ms.nim:392 `_mm512_sub_epi32` (région) : `proc mm512_sub_epi32(a, b: M512i): M512i {.importc: "_mm512_sub_epi32", header: "<immintrin.h>".}`
* X ms.nim:392 `immintrin.h` (région) : `proc mm512_sub_epi32(a, b: M512i): M512i {.importc: "_mm512_sub_epi32", header: "<immintrin.h>".}`
* X ms.nim:393 `_mm512_slli_epi32` (région) : `proc mm512_slli_epi32(a: M512i, n: cuint): M512i {.importc: "_mm512_slli_epi32", header: "<immintrin.h>".}`
* X ms.nim:393 `immintrin.h` (région) : `proc mm512_slli_epi32(a: M512i, n: cuint): M512i {.importc: "_mm512_slli_epi32", header: "<immintrin.h>".}`
* X ms.nim:394 `_mm512_srli_epi64` (région) : `proc mm512_srli_epi64(a: M512i, n: cuint): M512i {.importc: "_mm512_srli_epi64", header: "<immintrin.h>".}`
* X ms.nim:394 `immintrin.h` (région) : `proc mm512_srli_epi64(a: M512i, n: cuint): M512i {.importc: "_mm512_srli_epi64", header: "<immintrin.h>".}`
* X ms.nim:395 `_mm512_mullo_epi32` (région) : `proc mm512_mullo_epi32(a, b: M512i): M512i {.importc: "_mm512_mullo_epi32", header: "<immintrin.h>".}`
* X ms.nim:395 `immintrin.h` (région) : `proc mm512_mullo_epi32(a, b: M512i): M512i {.importc: "_mm512_mullo_epi32", header: "<immintrin.h>".}`
* X ms.nim:396 `_mm512_mul_epi32` (région) : `proc mm512_mul_epi32(a, b: M512i): M512i {.importc: "_mm512_mul_epi32", header: "<immintrin.h>".}`
* X ms.nim:396 `immintrin.h` (région) : `proc mm512_mul_epi32(a, b: M512i): M512i {.importc: "_mm512_mul_epi32", header: "<immintrin.h>".}`
* X ms.nim:397 `_mm512_maskz_mov_epi32` (région) : `proc mm512_maskz_mov_epi32(k: uint16, a: M512i): M512i {.importc: "_mm512_maskz_mov_epi32", header: "<immintri`
* X ms.nim:397 `immintrin.h` (région) : `proc mm512_maskz_mov_epi32(k: uint16, a: M512i): M512i {.importc: "_mm512_maskz_mov_epi32", header: "<immintri`
* X ms.nim:398 `_mm512_mask_add_epi32` (région) : `proc mm512_mask_add_epi32(src: M512i, k: uint16, a, b: M512i): M512i {.importc: "_mm512_mask_add_epi32", heade`
* X ms.nim:398 `immintrin.h` (région) : `proc mm512_mask_add_epi32(src: M512i, k: uint16, a, b: M512i): M512i {.importc: "_mm512_mask_add_epi32", heade`
* X ms.nim:399 `_mm512_mask_add_epi64` (région) : `proc mm512_mask_add_epi64(src: M512i, k: uint8, a, b: M512i): M512i {.importc: "_mm512_mask_add_epi64", header`
* X ms.nim:399 `immintrin.h` (région) : `proc mm512_mask_add_epi64(src: M512i, k: uint8, a, b: M512i): M512i {.importc: "_mm512_mask_add_epi64", header`
* X ms.nim:400 `_mm512_reduce_add_epi32` (région) : `proc mm512_reduce_add_epi32(a: M512i): int32 {.importc: "_mm512_reduce_add_epi32", header: "<immintrin.h>".}`
* X ms.nim:400 `immintrin.h` (région) : `proc mm512_reduce_add_epi32(a: M512i): int32 {.importc: "_mm512_reduce_add_epi32", header: "<immintrin.h>".}`
* X ms.nim:401 `_mm512_cvtepi32_epi64` (région) : `proc mm512_cvtepi32_epi64(a: M256i): M512i {.importc: "_mm512_cvtepi32_epi64", header: "<immintrin.h>".}`
* X ms.nim:401 `immintrin.h` (région) : `proc mm512_cvtepi32_epi64(a: M256i): M512i {.importc: "_mm512_cvtepi32_epi64", header: "<immintrin.h>".}`
* X ms.nim:402 `_mm512_castsi512_si256` (région) : `proc mm512_castsi512_si256(a: M512i): M256i {.importc: "_mm512_castsi512_si256", header: "<immintrin.h>".}`
* X ms.nim:402 `immintrin.h` (région) : `proc mm512_castsi512_si256(a: M512i): M256i {.importc: "_mm512_castsi512_si256", header: "<immintrin.h>".}`
* X ms.nim:403 `_mm512_extracti64x4_epi64` (région) : `proc mm512_extracti64x4_epi64(a: M512i, i: cint): M256i {.importc: "_mm512_extracti64x4_epi64", header: "<immi`
* X ms.nim:403 `immintrin.h` (région) : `proc mm512_extracti64x4_epi64(a: M512i, i: cint): M256i {.importc: "_mm512_extracti64x4_epi64", header: "<immi`
* X ms.nim:404 `immintrin.h` (région) : `proc pext_u32(a, m: uint32): uint32 {.importc: "_pext_u32", header: "<immintrin.h>".}`
* U ms.nim:406 `{.push boundChecks: off, overflowChecks: off` (région ; portée pushpop : lignes 406 à 475) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:422 `addr` (région ; portée line : lignes 422 à 422) : `let sd = mm512_loadu_si512(c.sd[i].addr)`
* U ms.nim:423 `addr` (région ; portée line : lignes 423 à 423) : `let pr = mm512_loadu_si512(c.pr[i].addr)`
* U ms.nim:424 `addr` (région ; portée line : lignes 424 à 424) : `let d = mm512_cvtepu8_epi32(mm_loadu_si128(c.d[i].addr))`
* U ms.nim:425 `addr` (région ; portée line : lignes 425 à 425) : `let q = mm512_cvtepu8_epi32(mm_loadu_si128(c.q[i].addr))`
* U ms.nim:448 `addr` (région ; portée line : lignes 448 à 448) : `let pass = mm512_cmple_epi32_mask(mm512_loadu_si512(c.sd[i].addr), lim)`
* U ms.nim:449 `addr` (région ; portée line : lignes 449 à 449) : `let vg = mm512_add_epi32(mm512_slli_epi32(mm512_cvtepu8_epi32(mm_loadu_si128(c.rf[i].addr)), 1),`
* U ms.nim:450 `addr` (région ; portée line : lignes 450 à 450) : `mm512_cvtepu8_epi32(mm_loadu_si128(c.ls[i].addr)))`
* U ms.nim:451 `addr` (région ; portée line : lignes 451 à 451) : `let vq = mm512_cvtepu8_epi32(mm_loadu_si128(c.q[i].addr))`
* U ms.nim:452 `addr` (région ; portée line : lignes 452 à 452) : `let vd = mm512_cvtepu8_epi32(mm_loadu_si128(c.d[i].addr))`
* U ms.nim:453 `addr` (région ; portée line : lignes 453 à 453) : `let vt = mm512_add_epi32(mm512_cvtepu8_epi32(mm_loadu_si128(c.t[i].addr)), c100)`
* U ms.nim:454 `addr` (région ; portée line : lignes 454 à 454) : `let vp = mm512_loadu_si512(c.pr[i].addr)`
* U ms.nim:493 `cast[` (région ; portée line : lignes 493 à 493) : `let j = cast[ptr K6PoolJob](data)`
* U ms.nim:514 `addr` (région ; portée line : lignes 514 à 514) : `runPool(k6PoolJob, j.addr)`
* U ms.nim:524 `addr` (hors région ; portée line : lignes 524 à 524) : `for t in 0 ..< 4: createThread(th[t], k6Worker, (c, N6 div 4 * t, N6 div 4 * (t + 1), q1, part[t].addr))`
* U ms.nim:559 `addr` (région ; portée line : lignes 559 à 559) : `let e = m.mgetOrPut(keys.p[i], Agg()).addr`
* U ms.nim:569 `ptr UncheckedArray` (région ; portée line : lignes 569 à 569) : `let tab = cast[ptr UncheckedArray[Slot]](aligned_alloc(64, csize_t(CAP * sizeof(Slot))))`
* U ms.nim:569 `cast[` (région ; portée line : lignes 569 à 569) : `let tab = cast[ptr UncheckedArray[Slot]](aligned_alloc(64, csize_t(CAP * sizeof(Slot))))`
* U ms.nim:571 `{.push boundChecks: off, overflowChecks: off` (région ; portée pushpop : lignes 571 à 586) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:577 `addr` (région ; portée line : lignes 577 à 577) : `prefetchw(tab[h[b]].addr, 1, 3)`
* U ms.nim:609 `{.push boundChecks: off` (hors région ; portée pushpop : lignes 609 à 620) : `{.push boundChecks: off.}`
* U ms.nim:621 `{.push boundChecks: off, overflowChecks: off` (région ; portée pushpop : lignes 621 à 694) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:744 `{.push boundChecks: off, overflowChecks: off` (région ; portée pushpop : lignes 744 à 752) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:745 `ptr UncheckedArray` (région ; portée line : lignes 745 à 745) : `proc k9Rows(a, b: ptr UncheckedArray[float], r0, r1: int) {.noinline.} =`
* U ms.nim:747 `ptr UncheckedArray` (région ; portée line : lignes 747 à 747) : `let up = cast[ptr UncheckedArray[float]](a[(i - 1) * M9].addr)`
* U ms.nim:747 `cast[` (région ; portée line : lignes 747 à 747) : `let up = cast[ptr UncheckedArray[float]](a[(i - 1) * M9].addr)`
* U ms.nim:747 `addr` (région ; portée line : lignes 747 à 747) : `let up = cast[ptr UncheckedArray[float]](a[(i - 1) * M9].addr)`
* U ms.nim:748 `ptr UncheckedArray` (région ; portée line : lignes 748 à 748) : `let mid = cast[ptr UncheckedArray[float]](a[i * M9].addr)`
* U ms.nim:748 `cast[` (région ; portée line : lignes 748 à 748) : `let mid = cast[ptr UncheckedArray[float]](a[i * M9].addr)`
* U ms.nim:748 `addr` (région ; portée line : lignes 748 à 748) : `let mid = cast[ptr UncheckedArray[float]](a[i * M9].addr)`
* U ms.nim:749 `ptr UncheckedArray` (région ; portée line : lignes 749 à 749) : `let dn = cast[ptr UncheckedArray[float]](a[(i + 1) * M9].addr)`
* U ms.nim:749 `cast[` (région ; portée line : lignes 749 à 749) : `let dn = cast[ptr UncheckedArray[float]](a[(i + 1) * M9].addr)`
* U ms.nim:749 `addr` (région ; portée line : lignes 749 à 749) : `let dn = cast[ptr UncheckedArray[float]](a[(i + 1) * M9].addr)`
* U ms.nim:750 `ptr UncheckedArray` (région ; portée line : lignes 750 à 750) : `let o = cast[ptr UncheckedArray[float]](b[i * M9].addr)`
* U ms.nim:750 `cast[` (région ; portée line : lignes 750 à 750) : `let o = cast[ptr UncheckedArray[float]](b[i * M9].addr)`
* U ms.nim:750 `addr` (région ; portée line : lignes 750 à 750) : `let o = cast[ptr UncheckedArray[float]](b[i * M9].addr)`
* X ms.nim:753 `_mm512_set1_pd` (région) : `proc mm512_set1_pd(x: float): M512d {.importc: "_mm512_set1_pd", header: "<immintrin.h>".}`
* X ms.nim:753 `immintrin.h` (région) : `proc mm512_set1_pd(x: float): M512d {.importc: "_mm512_set1_pd", header: "<immintrin.h>".}`
* X ms.nim:754 `_mm512_loadu_pd` (région) : `proc mm512_loadu_pd(p: pointer): M512d {.importc: "_mm512_loadu_pd", header: "<immintrin.h>".}`
* X ms.nim:754 `immintrin.h` (région) : `proc mm512_loadu_pd(p: pointer): M512d {.importc: "_mm512_loadu_pd", header: "<immintrin.h>".}`
* X ms.nim:755 `_mm512_storeu_pd` (région) : `proc mm512_storeu_pd(p: pointer, a: M512d) {.importc: "_mm512_storeu_pd", header: "<immintrin.h>".}`
* X ms.nim:755 `immintrin.h` (région) : `proc mm512_storeu_pd(p: pointer, a: M512d) {.importc: "_mm512_storeu_pd", header: "<immintrin.h>".}`
* X ms.nim:756 `_mm512_mul_pd` (région) : `proc mm512_mul_pd(a, b: M512d): M512d {.importc: "_mm512_mul_pd", header: "<immintrin.h>".}`
* X ms.nim:756 `immintrin.h` (région) : `proc mm512_mul_pd(a, b: M512d): M512d {.importc: "_mm512_mul_pd", header: "<immintrin.h>".}`
* U ms.nim:757 `{.push boundChecks: off, overflowChecks: off` (région ; portée pushpop : lignes 757 à 779) : `{.push boundChecks: off, overflowChecks: off.}`
* U ms.nim:763 `ptr UncheckedArray` (région ; portée line : lignes 763 à 763) : `proc k9RowsV(a, b: ptr UncheckedArray[float], r0, r1: int) {.noinline.} =`
* U ms.nim:766 `ptr UncheckedArray` (région ; portée line : lignes 766 à 766) : `let up = cast[ptr UncheckedArray[float]](a[(i - 1) * M9].addr)`
* U ms.nim:766 `cast[` (région ; portée line : lignes 766 à 766) : `let up = cast[ptr UncheckedArray[float]](a[(i - 1) * M9].addr)`
* U ms.nim:766 `addr` (région ; portée line : lignes 766 à 766) : `let up = cast[ptr UncheckedArray[float]](a[(i - 1) * M9].addr)`
* U ms.nim:767 `ptr UncheckedArray` (région ; portée line : lignes 767 à 767) : `let mid = cast[ptr UncheckedArray[float]](a[i * M9].addr)`
* U ms.nim:767 `cast[` (région ; portée line : lignes 767 à 767) : `let mid = cast[ptr UncheckedArray[float]](a[i * M9].addr)`
* U ms.nim:767 `addr` (région ; portée line : lignes 767 à 767) : `let mid = cast[ptr UncheckedArray[float]](a[i * M9].addr)`
* U ms.nim:768 `ptr UncheckedArray` (région ; portée line : lignes 768 à 768) : `let dn = cast[ptr UncheckedArray[float]](a[(i + 1) * M9].addr)`
* U ms.nim:768 `cast[` (région ; portée line : lignes 768 à 768) : `let dn = cast[ptr UncheckedArray[float]](a[(i + 1) * M9].addr)`
* U ms.nim:768 `addr` (région ; portée line : lignes 768 à 768) : `let dn = cast[ptr UncheckedArray[float]](a[(i + 1) * M9].addr)`
* U ms.nim:769 `ptr UncheckedArray` (région ; portée line : lignes 769 à 769) : `let o = cast[ptr UncheckedArray[float]](b[i * M9].addr)`
* U ms.nim:769 `cast[` (région ; portée line : lignes 769 à 769) : `let o = cast[ptr UncheckedArray[float]](b[i * M9].addr)`
* U ms.nim:769 `addr` (région ; portée line : lignes 769 à 769) : `let o = cast[ptr UncheckedArray[float]](b[i * M9].addr)`
* U ms.nim:772 `addr` (région ; portée line : lignes 772 à 772) : `let s = mm512_add_pd(mm512_add_pd(mm512_add_pd(mm512_loadu_pd(up[j].addr), mm512_loadu_pd(dn[j].addr)),`
* U ms.nim:772 `addr` (région ; portée line : lignes 772 à 772) : `let s = mm512_add_pd(mm512_add_pd(mm512_add_pd(mm512_loadu_pd(up[j].addr), mm512_loadu_pd(dn[j].addr)),`
* U ms.nim:773 `addr` (région ; portée line : lignes 773 à 773) : `mm512_loadu_pd(mid[j - 1].addr)), mm512_loadu_pd(mid[j + 1].addr))`
* U ms.nim:773 `addr` (région ; portée line : lignes 773 à 773) : `mm512_loadu_pd(mid[j - 1].addr)), mm512_loadu_pd(mid[j + 1].addr))`
* U ms.nim:774 `addr` (région ; portée line : lignes 774 à 774) : `mm512_storeu_pd(o[j].addr, mm512_mul_pd(q, s))`
* U ms.nim:783 `ptr UncheckedArray` (région ; portée line : lignes 783 à 783) : `a, b: ptr UncheckedArray[float]`
* U ms.nim:786 `cast[` (région ; portée line : lignes 786 à 786) : `let j = cast[ptr K9PoolJob](data)`
* U ms.nim:790 `ptr UncheckedArray` (région ; portée line : lignes 790 à 790) : `type K9Job = tuple[a, b: ptr UncheckedArray[float], r0, r1: int]`
* U ms.nim:829 `ptr UncheckedArray` (région ; portée line : lignes 829 à 829) : `var a = cast[ptr UncheckedArray[float]](aligned_alloc(64, csize_t(M9 * M9 * 8)))`
* U ms.nim:829 `cast[` (région ; portée line : lignes 829 à 829) : `var a = cast[ptr UncheckedArray[float]](aligned_alloc(64, csize_t(M9 * M9 * 8)))`
* U ms.nim:830 `ptr UncheckedArray` (région ; portée line : lignes 830 à 830) : `var b = cast[ptr UncheckedArray[float]](aligned_alloc(64, csize_t(M9 * M9 * 8)))`
* U ms.nim:830 `cast[` (région ; portée line : lignes 830 à 830) : `var b = cast[ptr UncheckedArray[float]](aligned_alloc(64, csize_t(M9 * M9 * 8)))`
* U ms.nim:843 `addr` (région ; portée line : lignes 843 à 843) : `runPool(k9PoolJob, j.addr)`
* U ms.nim:901 `cast[` (hors région ; portée line : lignes 901 à 901) : `let q = cast[ptr Spsc](aligned_alloc(128, csize_t(sizeof(Spsc))))`

## d

* X ms.d:16 `__builtin_ia32_psadbw512` (hors région) : `import ldc.gccbuiltins_x86 : __builtin_ia32_psadbw512;`
* X ms.d:16 `gccbuiltins_x86` (hors région) : `import ldc.gccbuiltins_x86 : __builtin_ia32_psadbw512;`
* U ms.d:37 `cast(ubyte*)` (hors région ; portée line : lignes 37 à 37) : `auto p = cast(ubyte*) aligned_alloc(64, (raw.length + 63) & ~63UL); // copie alignée sur une ligne de cache`
* U ms.d:39 `cast(T*)` (hors région ; portée line : lignes 39 à 39) : `return (cast(T*) p)[0 .. raw.length / T.sizeof];`
* U ms.d:74 `cast(float16*)` (région ; portée line : lignes 74 à 74) : `float16 x = *cast(float16*)(vx + i), y = *cast(float16*)(vy + i), z = *cast(float16*)(vz + i), w = *cast(float`
* U ms.d:74 `cast(float16*)` (région ; portée line : lignes 74 à 74) : `float16 x = *cast(float16*)(vx + i), y = *cast(float16*)(vy + i), z = *cast(float16*)(vz + i), w = *cast(float`
* U ms.d:74 `cast(float16*)` (région ; portée line : lignes 74 à 74) : `float16 x = *cast(float16*)(vx + i), y = *cast(float16*)(vy + i), z = *cast(float16*)(vz + i), w = *cast(float`
* U ms.d:74 `cast(float16*)` (région ; portée line : lignes 74 à 74) : `float16 x = *cast(float16*)(vx + i), y = *cast(float16*)(vy + i), z = *cast(float16*)(vz + i), w = *cast(float`
* U ms.d:105 `cast(Particle*)` (hors région ; portée line : lignes 105 à 105) : `foreach (i; 0 .. N1) ps[i] = *cast(Particle*)&raw[16 * i];`
* U ms.d:110 `.ptr` (hors région ; portée line : lignes 110 à 110) : `if (v == "footprint") { free(raw.ptr); result("k1", v, "energy", 0, 0, format("%.6f", k1Natural(ps))); return;`
* U ms.d:114 `cast(float*)` (région ; portée line : lignes 114 à 114) : `c[k] = cast(float*) aligned_alloc(64, N1 * 4);`
* U ms.d:143 `.ptr` (hors région ; portée line : lignes 143 à 143) : `foreach (_; 0 .. h) i = a.ptr[i];`
* U ms.d:240 `.ptr` (région ; portée line : lignes 240 à 240) : `ubyte64 x = loadUnaligned!ubyte64(v.ptr + i);`
* X ms.d:242 `__builtin_ia32_psadbw512` (région) : `acc += __builtin_ia32_psadbw512(cast(byte64) y, zero);`
* U ms.d:257 `.ptr` (hors région ; portée line : lignes 257 à 257) : `const(ubyte)* p = v.ptr;`
* U ms.d:298 `cast(float16*)` (région ; portée line : lignes 298 à 298) : `s0 += *cast(float16*)(a + i) * *cast(float16*)(b + i);`
* U ms.d:298 `cast(float16*)` (région ; portée line : lignes 298 à 298) : `s0 += *cast(float16*)(a + i) * *cast(float16*)(b + i);`
* U ms.d:299 `cast(float16*)` (région ; portée line : lignes 299 à 299) : `s1 += *cast(float16*)(a + i + 16) * *cast(float16*)(b + i + 16);`
* U ms.d:299 `cast(float16*)` (région ; portée line : lignes 299 à 299) : `s1 += *cast(float16*)(a + i + 16) * *cast(float16*)(b + i + 16);`
* U ms.d:300 `cast(float16*)` (région ; portée line : lignes 300 à 300) : `s2 += *cast(float16*)(a + i + 32) * *cast(float16*)(b + i + 32);`
* U ms.d:300 `cast(float16*)` (région ; portée line : lignes 300 à 300) : `s2 += *cast(float16*)(a + i + 32) * *cast(float16*)(b + i + 32);`
* U ms.d:301 `cast(float16*)` (région ; portée line : lignes 301 à 301) : `s3 += *cast(float16*)(a + i + 48) * *cast(float16*)(b + i + 48);`
* U ms.d:301 `cast(float16*)` (région ; portée line : lignes 301 à 301) : `s3 += *cast(float16*)(a + i + 48) * *cast(float16*)(b + i + 48);`
* U ms.d:316 `.ptr` (hors région ; portée line : lignes 316 à 316) : `atomicStore!(MemoryOrder.raw)(*cast(shared)&sinkA, cast(shared) a.ptr); // barrière d'optimisation`
* U ms.d:318 `.ptr` (hors région ; portée line : lignes 318 à 318) : `d = tuned ? k5Tuned(pa, b.ptr, a.length) : k5Natural(pa[0 .. a.length], b);`
* U ms.d:337 `.ptr` (hors région ; portée line : lignes 337 à 337) : `const(int)* sd = c.sd.ptr, pr = c.pr.ptr;`
* U ms.d:337 `.ptr` (hors région ; portée line : lignes 337 à 337) : `const(int)* sd = c.sd.ptr, pr = c.pr.ptr;`
* U ms.d:338 `.ptr` (hors région ; portée line : lignes 338 à 338) : `const(ubyte)* d = c.d.ptr, q = c.q.ptr;`
* U ms.d:338 `.ptr` (hors région ; portée line : lignes 338 à 338) : `const(ubyte)* d = c.d.ptr, q = c.q.ptr;`
* U ms.d:362 `.ptr` (région ; portée line : lignes 362 à 362) : `return loadUnaligned!int16(a.ptr);`
* U ms.d:368 `.ptr` (région ; portée line : lignes 368 à 368) : `const(int)* sd = c.sd.ptr, pr = c.pr.ptr;`
* U ms.d:368 `.ptr` (région ; portée line : lignes 368 à 368) : `const(int)* sd = c.sd.ptr, pr = c.pr.ptr;`
* U ms.d:369 `.ptr` (région ; portée line : lignes 369 à 369) : `const(ubyte)* q = c.q.ptr, d = c.d.ptr, t = c.t.ptr, rf = c.rf.ptr, ls = c.ls.ptr;`
* U ms.d:369 `.ptr` (région ; portée line : lignes 369 à 369) : `const(ubyte)* q = c.q.ptr, d = c.d.ptr, t = c.t.ptr, rf = c.rf.ptr, ls = c.ls.ptr;`
* U ms.d:369 `.ptr` (région ; portée line : lignes 369 à 369) : `const(ubyte)* q = c.q.ptr, d = c.d.ptr, t = c.t.ptr, rf = c.rf.ptr, ls = c.ls.ptr;`
* U ms.d:369 `.ptr` (région ; portée line : lignes 369 à 369) : `const(ubyte)* q = c.q.ptr, d = c.d.ptr, t = c.t.ptr, rf = c.rf.ptr, ls = c.ls.ptr;`
* U ms.d:369 `.ptr` (région ; portée line : lignes 369 à 369) : `const(ubyte)* q = c.q.ptr, d = c.d.ptr, t = c.t.ptr, rf = c.rf.ptr, ls = c.ls.ptr;`
* U ms.d:408 `.ptr` (région ; portée line : lignes 408 à 408) : `const(int)* sd = c.sd.ptr, pr = c.pr.ptr;`
* U ms.d:408 `.ptr` (région ; portée line : lignes 408 à 408) : `const(int)* sd = c.sd.ptr, pr = c.pr.ptr;`
* U ms.d:409 `.ptr` (région ; portée line : lignes 409 à 409) : `const(ubyte)* d = c.d.ptr, q = c.q.ptr;`
* U ms.d:409 `.ptr` (région ; portée line : lignes 409 à 409) : `const(ubyte)* d = c.d.ptr, q = c.q.ptr;`
* U ms.d:427 `cast(K6Pool*)` (région ; portée line : lignes 427 à 427) : `auto j = cast(K6Pool*) data;`
* U ms.d:489 `cast(Slot*)` (région ; portée line : lignes 489 à 489) : `auto tab = cast(Slot*) aligned_alloc(64, CAP * Slot.sizeof);`
* U ms.d:587 `cast(ANode*)` (région ; portée line : lignes 587 à 587) : `auto arena = cast(ANode*) malloc(ANode.sizeof * ((2 << SIZE_K8_REQ) - 1));`
* U ms.d:636 `cast(K9Pool*)` (région ; portée line : lignes 636 à 636) : `auto j = cast(K9Pool*) data;`
* U ms.d:644 `cast(double*)` (région ; portée line : lignes 644 à 644) : `else { ga = cast(double*) aligned_alloc(64, M9 * M9 * 8); gb = cast(double*) aligned_alloc(64, M9 * M9 * 8); }`
* U ms.d:644 `cast(double*)` (région ; portée line : lignes 644 à 644) : `else { ga = cast(double*) aligned_alloc(64, M9 * M9 * 8); gb = cast(double*) aligned_alloc(64, M9 * M9 * 8); }`
* U ms.d:706 `cast(Spsc*)` (hors région ; portée line : lignes 706 à 706) : `auto q = cast(Spsc*) aligned_alloc(128, Spsc.sizeof);`

## ada

* U ms.adb:21 `Unchecked_Conversion` (hors région ; portée line : lignes 21 à 21) : `with Ada.Unchecked_Conversion;`
* U ms.adb:87 `'Address` (hors région ; portée line : lignes 87 à 87) : `Got := Read (FD, A.all'Address + Storage_Offset (Done), Integer (Long_Integer'Min (Bytes - Done, 2 ** 30)));`
* X ms.adb:103 `__builtin_ia32_pause` (hors région) : `pragma Import (Intrinsic, Pause, "__builtin_ia32_pause");`
* X ms.adb:107 `__builtin_ia32_vfmaddps512_mask` (région) : `pragma Import (Intrinsic, Fmadd, "__builtin_ia32_vfmaddps512_mask");`
* X ms.adb:109 `__builtin_ia32_addps512_mask` (région) : `pragma Import (Intrinsic, Vadd, "__builtin_ia32_addps512_mask");`
* U ms.adb:132 `pragma Suppress` (hors région ; portée unit : lignes 131 à 149) : `pragma Suppress (All_Checks);`
* U ms.adb:151 `pragma Suppress` (région ; portée unit : lignes 150 à 168) : `pragma Suppress (All_Checks);`
* U ms.adb:264 `pragma Suppress` (hors région ; portée unit : lignes 263 à 271) : `pragma Suppress (All_Checks);`
* U ms.adb:289 `pragma Suppress` (région ; portée unit : lignes 288 à 367) : `pragma Suppress (All_Checks);`
* X ms.adb:396 `__builtin_ia32_cvtb2mask512` (région) : `pragma Import (Intrinsic, B2Mask, "__builtin_ia32_cvtb2mask512");`
* X ms.adb:398 `__builtin_ia32_movdquqi512_mask` (région) : `pragma Import (Intrinsic, Mov_Masked, "__builtin_ia32_movdquqi512_mask");`
* X ms.adb:400 `__builtin_ia32_psadbw512` (région) : `pragma Import (Intrinsic, Sad, "__builtin_ia32_psadbw512");`
* X ms.adb:402 `__builtin_ia32_paddq512_mask` (région) : `pragma Import (Intrinsic, Add_Q, "__builtin_ia32_paddq512_mask");`
* U ms.adb:413 `'Address` (région ; portée line : lignes 413 à 413) : `X : V64I8 with Import, Address => B (I)'Address;`
* U ms.adb:438 `pragma Suppress` (région ; portée unit : lignes 437 à 467) : `pragma Suppress (All_Checks);`
* U ms.adb:452 `'Address` (région ; portée line : lignes 452 à 452) : `W : Unsigned_64 with Import, Address => B (I)'Address;`
* U ms.adb:509 `pragma Suppress` (région ; portée unit : lignes 508 à 534) : `pragma Suppress (All_Checks);`
* U ms.adb:519 `'Address` (région ; portée line : lignes 519 à 519) : `S0 := Fmadd (V (A (I)'Address), V (B (I)'Address), S0, 16#FFFF#, 4);`
* U ms.adb:519 `'Address` (région ; portée line : lignes 519 à 519) : `S0 := Fmadd (V (A (I)'Address), V (B (I)'Address), S0, 16#FFFF#, 4);`
* U ms.adb:520 `'Address` (région ; portée line : lignes 520 à 520) : `S1 := Fmadd (V (A (I + 16)'Address), V (B (I + 16)'Address), S1, 16#FFFF#, 4);`
* U ms.adb:520 `'Address` (région ; portée line : lignes 520 à 520) : `S1 := Fmadd (V (A (I + 16)'Address), V (B (I + 16)'Address), S1, 16#FFFF#, 4);`
* U ms.adb:521 `'Address` (région ; portée line : lignes 521 à 521) : `S2 := Fmadd (V (A (I + 32)'Address), V (B (I + 32)'Address), S2, 16#FFFF#, 4);`
* U ms.adb:521 `'Address` (région ; portée line : lignes 521 à 521) : `S2 := Fmadd (V (A (I + 32)'Address), V (B (I + 32)'Address), S2, 16#FFFF#, 4);`
* U ms.adb:522 `'Address` (région ; portée line : lignes 522 à 522) : `S3 := Fmadd (V (A (I + 48)'Address), V (B (I + 48)'Address), S3, 16#FFFF#, 4);`
* U ms.adb:522 `'Address` (région ; portée line : lignes 522 à 522) : `S3 := Fmadd (V (A (I + 48)'Address), V (B (I + 48)'Address), S3, 16#FFFF#, 4);`
* U ms.adb:574 `pragma Suppress` (hors région ; portée unit : lignes 573 à 583) : `pragma Suppress (All_Checks);`
* U ms.adb:604 `pragma Suppress` (hors région ; portée unit : lignes 603 à 645) : `pragma Suppress (All_Checks);`
* X ms.adb:654 `__builtin_ia32_pmovzxbd512_mask` (région) : `pragma Import (Intrinsic, ZxBD, "__builtin_ia32_pmovzxbd512_mask");`
* X ms.adb:656 `__builtin_ia32_cmpd512_mask` (région) : `pragma Import (Intrinsic, CmpD, "__builtin_ia32_cmpd512_mask");`
* X ms.adb:658 `__builtin_ia32_pmulld512_mask` (région) : `pragma Import (Intrinsic, MulLoD, "__builtin_ia32_pmulld512_mask");`
* X ms.adb:660 `__builtin_ia32_paddd512_mask` (région) : `pragma Import (Intrinsic, PaddD, "__builtin_ia32_paddd512_mask");`
* X ms.adb:662 `__builtin_ia32_psubd512_mask` (région) : `pragma Import (Intrinsic, PsubD, "__builtin_ia32_psubd512_mask");`
* X ms.adb:664 `__builtin_ia32_pslldi512_mask` (région) : `pragma Import (Intrinsic, SllD, "__builtin_ia32_pslldi512_mask");`
* X ms.adb:666 `__builtin_ia32_psllqi512_mask` (région) : `pragma Import (Intrinsic, SllQ, "__builtin_ia32_psllqi512_mask");`
* X ms.adb:668 `__builtin_ia32_psrlqi512_mask` (région) : `pragma Import (Intrinsic, SrlQ, "__builtin_ia32_psrlqi512_mask");`
* X ms.adb:670 `__builtin_ia32_psraqi512_mask` (région) : `pragma Import (Intrinsic, SraQ, "__builtin_ia32_psraqi512_mask");`
* X ms.adb:672 `__builtin_ia32_pmuldq512_mask` (région) : `pragma Import (Intrinsic, MulDQ, "__builtin_ia32_pmuldq512_mask");`
* X ms.adb:674 `__builtin_ia32_pext_si` (région) : `pragma Import (Intrinsic, Pext, "__builtin_ia32_pext_si");`
* U ms.adb:677 `Unchecked_Conversion` (région ; portée line : lignes 677 à 677) : `function To_Q is new Ada.Unchecked_Conversion (V16SI, V8I64);`
* U ms.adb:678 `Unchecked_Conversion` (région ; portée line : lignes 678 à 678) : `function To_D is new Ada.Unchecked_Conversion (V8I64, V16SI);`
* U ms.adb:689 `pragma Suppress` (région ; portée unit : lignes 688 à 721) : `pragma Suppress (All_Checks);`
* U ms.adb:701 `'Address` (région ; portée line : lignes 701 à 701) : `Sd : V16SI with Import, Address => C.Sd (I)'Address;`
* U ms.adb:702 `'Address` (région ; portée line : lignes 702 à 702) : `Pr : V16SI with Import, Address => C.Pr (I)'Address;`
* U ms.adb:703 `'Address` (région ; portée line : lignes 703 à 703) : `Db : V16QI with Import, Address => C.D (I)'Address;`
* U ms.adb:704 `'Address` (région ; portée line : lignes 704 à 704) : `Qb : V16QI with Import, Address => C.Q (I)'Address;`
* U ms.adb:729 `pragma Suppress` (région ; portée unit : lignes 728 à 794) : `pragma Suppress (All_Checks);`
* U ms.adb:748 `'Address` (région ; portée line : lignes 748 à 748) : `Sd  : V16SI with Import, Address => C.Sd (I)'Address;`
* U ms.adb:749 `'Address` (région ; portée line : lignes 749 à 749) : `Pr  : V16SI with Import, Address => C.Pr (I)'Address;`
* U ms.adb:750 `'Address` (région ; portée line : lignes 750 à 750) : `Rfb : V16QI with Import, Address => C.Rf (I)'Address;`
* U ms.adb:751 `'Address` (région ; portée line : lignes 751 à 751) : `Lsb : V16QI with Import, Address => C.Ls (I)'Address;`
* U ms.adb:752 `'Address` (région ; portée line : lignes 752 à 752) : `Qb  : V16QI with Import, Address => C.Q (I)'Address;`
* U ms.adb:753 `'Address` (région ; portée line : lignes 753 à 753) : `Db  : V16QI with Import, Address => C.D (I)'Address;`
* U ms.adb:754 `'Address` (région ; portée line : lignes 754 à 754) : `Tb  : V16QI with Import, Address => C.T (I)'Address;`
* U ms.adb:1024 `pragma Suppress` (région ; portée unit : lignes 1023 à 1059) : `pragma Suppress (All_Checks);`
* U ms.adb:1038 `'Address` (région ; portée line : lignes 1038 à 1038) : `Prefetch (Tab (H (B))'Address, 1, 0);`
* U ms.adb:1103 `pragma Suppress` (région ; portée unit : lignes 1102 à 1119) : `pragma Suppress (All_Checks);`
* U ms.adb:1121 `pragma Suppress` (région ; portée unit : lignes 1120 à 1124) : `pragma Suppress (All_Checks);`
* U ms.adb:1133 `pragma Suppress` (hors région ; portée unit : lignes 1132 à 1173) : `pragma Suppress (All_Checks);`
* U ms.adb:1175 `pragma Suppress` (hors région ; portée unit : lignes 1174 à 1193) : `pragma Suppress (All_Checks);`
* U ms.adb:1207 `pragma Suppress` (hors région ; portée unit : lignes 1205 à 1212) : `pragma Suppress (All_Checks);`
* U ms.adb:1210 `'Address` (hors région ; portée line : lignes 1210 à 1210) : `Addr := Pool.Buf (Pool.Buf'First + T)'Address;`
* U ms.adb:1221 `pragma Suppress` (hors région ; portée unit : lignes 1220 à 1230) : `pragma Suppress (All_Checks);`
* U ms.adb:1332 `pragma Suppress` (région ; portée unit : lignes 1331 à 1340) : `pragma Suppress (All_Checks);`
* X ms.adb:1349 `__builtin_ia32_loadupd512_mask` (hors région) : `pragma Import (Intrinsic, LoadU, "__builtin_ia32_loadupd512_mask");`
* X ms.adb:1351 `__builtin_ia32_storeupd512_mask` (hors région) : `pragma Import (Intrinsic, StoreU, "__builtin_ia32_storeupd512_mask");`
* X ms.adb:1353 `__builtin_ia32_addpd512_mask` (hors région) : `pragma Import (Intrinsic, AddPD, "__builtin_ia32_addpd512_mask");`
* X ms.adb:1355 `__builtin_ia32_mulpd512_mask` (hors région) : `pragma Import (Intrinsic, MulPD, "__builtin_ia32_mulpd512_mask");`
* U ms.adb:1357 `pragma Suppress` (hors région ; portée unit : lignes 1356 à 1378) : `pragma Suppress (All_Checks);`
* U ms.adb:1365 `'Address` (hors région ; portée line : lignes 1365 à 1365) : `StoreU (B (I, J)'Address,`
* U ms.adb:1366 `'Address` (hors région ; portée line : lignes 1366 à 1366) : `MulPD (Q, AddPD (AddPD (AddPD (LoadU (A (I - 1, J)'Address, Z, 16#FF#),`
* U ms.adb:1367 `'Address` (hors région ; portée line : lignes 1367 à 1367) : `LoadU (A (I + 1, J)'Address, Z, 16#FF#), Z, 16#FF#, 4),`
* U ms.adb:1368 `'Address` (hors région ; portée line : lignes 1368 à 1368) : `LoadU (A (I, J - 1)'Address, Z, 16#FF#), Z, 16#FF#, 4),`
* U ms.adb:1369 `'Address` (hors région ; portée line : lignes 1369 à 1369) : `LoadU (A (I, J + 1)'Address, Z, 16#FF#), Z, 16#FF#, 4), Z, 16#FF#, 4),`
* U ms.adb:1541 `pragma Suppress` (hors région ; portée unit : lignes 1532 à 1605) : `pragma Suppress (All_Checks);`
* U ms.adb:1547 `'Address` (hors région ; portée line : lignes 1547 à 1547) : `Cache := Unsigned_64 (AP.Atomic_Load_64 (SQ.Read_Idx.V'Address, AP.Acquire));`
* U ms.adb:1554 `'Address` (hors région ; portée line : lignes 1554 à 1554) : `AP.Atomic_Store_64 (SQ.Write_Idx.V'Address, AP.uint64 (W), AP.Release);`
* U ms.adb:1563 `pragma Suppress` (hors région ; portée unit : lignes 1532 à 1605) : `pragma Suppress (All_Checks);`
* U ms.adb:1569 `'Address` (hors région ; portée line : lignes 1569 à 1569) : `Cache := Unsigned_64 (AP.Atomic_Load_64 (SQ.Write_Idx.V'Address, AP.Acquire));`
* U ms.adb:1576 `'Address` (hors région ; portée line : lignes 1576 à 1576) : `AP.Atomic_Store_64 (SQ.Read_Idx.V'Address, AP.uint64 (Rd), AP.Release);`

## chapel

* X ms.chpl:158 `immintrin.h` (hors région) : `require "immintrin.h";`
* X ms.chpl:159 `__m512i` (région) : `extern type __m512i;`
* X ms.chpl:160 `_mm512_setzero_si512` (région) : `extern proc _mm512_setzero_si512(): __m512i;`
* X ms.chpl:160 `__m512i` (région) : `extern proc _mm512_setzero_si512(): __m512i;`
* U ms.chpl:161 `c_ptrConst` (région ; portée line : lignes 161 à 161) : `extern proc _mm512_loadu_si512(p: c_ptrConst(void)): __m512i;`
* X ms.chpl:161 `_mm512_loadu_si512` (région) : `extern proc _mm512_loadu_si512(p: c_ptrConst(void)): __m512i;`
* X ms.chpl:161 `__m512i` (région) : `extern proc _mm512_loadu_si512(p: c_ptrConst(void)): __m512i;`
* X ms.chpl:162 `_mm512_movepi8_mask` (région) : `extern proc _mm512_movepi8_mask(a: __m512i): uint(64);`
* X ms.chpl:162 `__m512i` (région) : `extern proc _mm512_movepi8_mask(a: __m512i): uint(64);`
* X ms.chpl:163 `_mm512_maskz_mov_epi8` (région) : `extern proc _mm512_maskz_mov_epi8(k: uint(64), a: __m512i): __m512i;`
* X ms.chpl:163 `__m512i` (région) : `extern proc _mm512_maskz_mov_epi8(k: uint(64), a: __m512i): __m512i;`
* X ms.chpl:163 `__m512i` (région) : `extern proc _mm512_maskz_mov_epi8(k: uint(64), a: __m512i): __m512i;`
* X ms.chpl:164 `_mm512_sad_epu8` (région) : `extern proc _mm512_sad_epu8(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:164 `__m512i` (région) : `extern proc _mm512_sad_epu8(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:164 `__m512i` (région) : `extern proc _mm512_sad_epu8(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:164 `__m512i` (région) : `extern proc _mm512_sad_epu8(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:165 `_mm512_add_epi64` (région) : `extern proc _mm512_add_epi64(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:165 `__m512i` (région) : `extern proc _mm512_add_epi64(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:165 `__m512i` (région) : `extern proc _mm512_add_epi64(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:165 `__m512i` (région) : `extern proc _mm512_add_epi64(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:166 `_mm512_reduce_add_epi64` (région) : `extern proc _mm512_reduce_add_epi64(a: __m512i): int(64);`
* X ms.chpl:166 `__m512i` (région) : `extern proc _mm512_reduce_add_epi64(a: __m512i): int(64);`
* U ms.chpl:169 `c_ptrToConst` (région ; portée line : lignes 169 à 169) : `const p = c_ptrToConst(b[0]);`
* X ms.chpl:170 `_mm512_setzero_si512` (région) : `const zero = _mm512_setzero_si512();`
* X ms.chpl:171 `_mm512_setzero_si512` (région) : `var acc = _mm512_setzero_si512();`
* U ms.chpl:174 `c_ptrConst` (région ; portée line : lignes 174 à 174) : `const x = _mm512_loadu_si512((p + i): c_ptrConst(void));`
* X ms.chpl:174 `_mm512_loadu_si512` (région) : `const x = _mm512_loadu_si512((p + i): c_ptrConst(void));`
* X ms.chpl:175 `_mm512_add_epi64` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(_mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x), zero));`
* X ms.chpl:175 `_mm512_sad_epu8` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(_mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x), zero));`
* X ms.chpl:175 `_mm512_maskz_mov_epi8` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(_mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x), zero));`
* X ms.chpl:175 `_mm512_movepi8_mask` (région) : `acc = _mm512_add_epi64(acc, _mm512_sad_epu8(_mm512_maskz_mov_epi8(_mm512_movepi8_mask(x), x), zero));`
* X ms.chpl:178 `_mm512_reduce_add_epi64` (région) : `var s = _mm512_reduce_add_epi64(acc): uint;`
* U ms.chpl:193 `c_ptrToConst` (hors région ; portée line : lignes 193 à 193) : `const p = c_ptrToConst(b[0]);`
* U ms.chpl:200 `c_ptrTo` (hors région ; portée line : lignes 200 à 200) : `OS.POSIX.memcpy(c_ptrTo(w): c_ptr(void), (p + i): c_ptr(void), 8);`
* U ms.chpl:200 `c_ptr` (hors région ; portée line : lignes 200 à 200) : `OS.POSIX.memcpy(c_ptrTo(w): c_ptr(void), (p + i): c_ptr(void), 8);`
* U ms.chpl:200 `c_ptr` (hors région ; portée line : lignes 200 à 200) : `OS.POSIX.memcpy(c_ptrTo(w): c_ptr(void), (p + i): c_ptr(void), 8);`
* X ms.chpl:241 `__m512` (région) : `extern type __m512;`
* X ms.chpl:242 `_mm512_setzero_ps` (région) : `extern proc _mm512_setzero_ps(): __m512;`
* X ms.chpl:242 `__m512` (région) : `extern proc _mm512_setzero_ps(): __m512;`
* U ms.chpl:243 `c_ptrConst` (région ; portée line : lignes 243 à 243) : `extern proc _mm512_loadu_ps(p: c_ptrConst(void)): __m512;`
* X ms.chpl:243 `_mm512_loadu_ps` (région) : `extern proc _mm512_loadu_ps(p: c_ptrConst(void)): __m512;`
* X ms.chpl:243 `__m512` (région) : `extern proc _mm512_loadu_ps(p: c_ptrConst(void)): __m512;`
* X ms.chpl:244 `_mm512_fmadd_ps` (région) : `extern proc _mm512_fmadd_ps(a: __m512, b: __m512, c: __m512): __m512;`
* X ms.chpl:244 `__m512` (région) : `extern proc _mm512_fmadd_ps(a: __m512, b: __m512, c: __m512): __m512;`
* X ms.chpl:244 `__m512` (région) : `extern proc _mm512_fmadd_ps(a: __m512, b: __m512, c: __m512): __m512;`
* X ms.chpl:244 `__m512` (région) : `extern proc _mm512_fmadd_ps(a: __m512, b: __m512, c: __m512): __m512;`
* X ms.chpl:244 `__m512` (région) : `extern proc _mm512_fmadd_ps(a: __m512, b: __m512, c: __m512): __m512;`
* X ms.chpl:245 `_mm512_add_ps` (région) : `extern proc _mm512_add_ps(a: __m512, b: __m512): __m512;`
* X ms.chpl:245 `__m512` (région) : `extern proc _mm512_add_ps(a: __m512, b: __m512): __m512;`
* X ms.chpl:245 `__m512` (région) : `extern proc _mm512_add_ps(a: __m512, b: __m512): __m512;`
* X ms.chpl:245 `__m512` (région) : `extern proc _mm512_add_ps(a: __m512, b: __m512): __m512;`
* X ms.chpl:246 `_mm512_reduce_add_ps` (région) : `extern proc _mm512_reduce_add_ps(a: __m512): real(32);`
* X ms.chpl:246 `__m512` (région) : `extern proc _mm512_reduce_add_ps(a: __m512): real(32);`
* U ms.chpl:247 `c_ptrConst` (région ; portée line : lignes 247 à 247) : `proc k5TunedV(a: c_ptrConst(real(32)), b: c_ptrConst(real(32)), n: int): real(32) {`
* U ms.chpl:247 `c_ptrConst` (région ; portée line : lignes 247 à 247) : `proc k5TunedV(a: c_ptrConst(real(32)), b: c_ptrConst(real(32)), n: int): real(32) {`
* X ms.chpl:248 `_mm512_setzero_ps` (région) : `var s0 = _mm512_setzero_ps(), s1 = s0, s2 = s0, s3 = s0;`
* U ms.chpl:251 `c_ptrConst` (région ; portée line : lignes 251 à 251) : `s0 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i): c_ptrConst(void)), _mm512_loadu_ps((b + i): c_ptrConst(void)), s`
* U ms.chpl:251 `c_ptrConst` (région ; portée line : lignes 251 à 251) : `s0 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i): c_ptrConst(void)), _mm512_loadu_ps((b + i): c_ptrConst(void)), s`
* X ms.chpl:251 `_mm512_fmadd_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i): c_ptrConst(void)), _mm512_loadu_ps((b + i): c_ptrConst(void)), s`
* X ms.chpl:251 `_mm512_loadu_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i): c_ptrConst(void)), _mm512_loadu_ps((b + i): c_ptrConst(void)), s`
* X ms.chpl:251 `_mm512_loadu_ps` (région) : `s0 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i): c_ptrConst(void)), _mm512_loadu_ps((b + i): c_ptrConst(void)), s`
* U ms.chpl:252 `c_ptrConst` (région ; portée line : lignes 252 à 252) : `s1 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 16): c_ptrConst(void)), _mm512_loadu_ps((b + i + 16): c_ptrConst`
* U ms.chpl:252 `c_ptrConst` (région ; portée line : lignes 252 à 252) : `s1 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 16): c_ptrConst(void)), _mm512_loadu_ps((b + i + 16): c_ptrConst`
* X ms.chpl:252 `_mm512_fmadd_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 16): c_ptrConst(void)), _mm512_loadu_ps((b + i + 16): c_ptrConst`
* X ms.chpl:252 `_mm512_loadu_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 16): c_ptrConst(void)), _mm512_loadu_ps((b + i + 16): c_ptrConst`
* X ms.chpl:252 `_mm512_loadu_ps` (région) : `s1 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 16): c_ptrConst(void)), _mm512_loadu_ps((b + i + 16): c_ptrConst`
* U ms.chpl:253 `c_ptrConst` (région ; portée line : lignes 253 à 253) : `s2 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 32): c_ptrConst(void)), _mm512_loadu_ps((b + i + 32): c_ptrConst`
* U ms.chpl:253 `c_ptrConst` (région ; portée line : lignes 253 à 253) : `s2 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 32): c_ptrConst(void)), _mm512_loadu_ps((b + i + 32): c_ptrConst`
* X ms.chpl:253 `_mm512_fmadd_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 32): c_ptrConst(void)), _mm512_loadu_ps((b + i + 32): c_ptrConst`
* X ms.chpl:253 `_mm512_loadu_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 32): c_ptrConst(void)), _mm512_loadu_ps((b + i + 32): c_ptrConst`
* X ms.chpl:253 `_mm512_loadu_ps` (région) : `s2 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 32): c_ptrConst(void)), _mm512_loadu_ps((b + i + 32): c_ptrConst`
* U ms.chpl:254 `c_ptrConst` (région ; portée line : lignes 254 à 254) : `s3 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 48): c_ptrConst(void)), _mm512_loadu_ps((b + i + 48): c_ptrConst`
* U ms.chpl:254 `c_ptrConst` (région ; portée line : lignes 254 à 254) : `s3 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 48): c_ptrConst(void)), _mm512_loadu_ps((b + i + 48): c_ptrConst`
* X ms.chpl:254 `_mm512_fmadd_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 48): c_ptrConst(void)), _mm512_loadu_ps((b + i + 48): c_ptrConst`
* X ms.chpl:254 `_mm512_loadu_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 48): c_ptrConst(void)), _mm512_loadu_ps((b + i + 48): c_ptrConst`
* X ms.chpl:254 `_mm512_loadu_ps` (région) : `s3 = _mm512_fmadd_ps(_mm512_loadu_ps((a + i + 48): c_ptrConst(void)), _mm512_loadu_ps((b + i + 48): c_ptrConst`
* X ms.chpl:257 `_mm512_reduce_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* X ms.chpl:257 `_mm512_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* X ms.chpl:257 `_mm512_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* X ms.chpl:257 `_mm512_add_ps` (région) : `return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));`
* U ms.chpl:270 `c_ptrToConst` (hors région ; portée line : lignes 270 à 270) : `else if v == "tuned_v" then k5TunedV(c_ptrToConst(a[0]), c_ptrToConst(b[0]), a.size)`
* U ms.chpl:270 `c_ptrToConst` (hors région ; portée line : lignes 270 à 270) : `else if v == "tuned_v" then k5TunedV(c_ptrToConst(a[0]), c_ptrToConst(b[0]), a.size)`
* U ms.chpl:316 `c_ptrConst` (hors région ; portée line : lignes 316 à 316) : `proc q1Tuned(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8)),`
* U ms.chpl:316 `c_ptrConst` (hors région ; portée line : lignes 316 à 316) : `proc q1Tuned(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8)),`
* U ms.chpl:316 `c_ptrConst` (hors région ; portée line : lignes 316 à 316) : `proc q1Tuned(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8)),`
* U ms.chpl:316 `c_ptrConst` (hors région ; portée line : lignes 316 à 316) : `proc q1Tuned(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8)),`
* U ms.chpl:317 `c_ptrConst` (hors région ; portée line : lignes 317 à 317) : `t: c_ptrConst(uint(8)), rf: c_ptrConst(uint(8)), ls: c_ptrConst(uint(8)), lo: int, hi: int, ref acc: [] int) {`
* U ms.chpl:317 `c_ptrConst` (hors région ; portée line : lignes 317 à 317) : `t: c_ptrConst(uint(8)), rf: c_ptrConst(uint(8)), ls: c_ptrConst(uint(8)), lo: int, hi: int, ref acc: [] int) {`
* U ms.chpl:317 `c_ptrConst` (hors région ; portée line : lignes 317 à 317) : `t: c_ptrConst(uint(8)), rf: c_ptrConst(uint(8)), ls: c_ptrConst(uint(8)), lo: int, hi: int, ref acc: [] int) {`
* X ms.chpl:349 `__m256i` (région) : `extern type __m256i;`
* X ms.chpl:350 `__m128i` (région) : `extern type __m128i;`
* X ms.chpl:351 `_mm512_set1_epi32` (région) : `extern proc _mm512_set1_epi32(x: int(32)): __m512i;`
* X ms.chpl:351 `__m512i` (région) : `extern proc _mm512_set1_epi32(x: int(32)): __m512i;`
* U ms.chpl:352 `c_ptrConst` (région ; portée line : lignes 352 à 352) : `extern proc _mm_loadu_si128(p: c_ptrConst(void)): __m128i;`
* X ms.chpl:352 `_mm_loadu_si128` (région) : `extern proc _mm_loadu_si128(p: c_ptrConst(void)): __m128i;`
* X ms.chpl:352 `__m128i` (région) : `extern proc _mm_loadu_si128(p: c_ptrConst(void)): __m128i;`
* X ms.chpl:353 `_mm512_cvtepu8_epi32` (région) : `extern proc _mm512_cvtepu8_epi32(x: __m128i): __m512i;`
* X ms.chpl:353 `__m128i` (région) : `extern proc _mm512_cvtepu8_epi32(x: __m128i): __m512i;`
* X ms.chpl:353 `__m512i` (région) : `extern proc _mm512_cvtepu8_epi32(x: __m128i): __m512i;`
* X ms.chpl:354 `_mm512_add_epi32` (région) : `extern proc _mm512_add_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:354 `__m512i` (région) : `extern proc _mm512_add_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:354 `__m512i` (région) : `extern proc _mm512_add_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:354 `__m512i` (région) : `extern proc _mm512_add_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:355 `_mm512_sub_epi32` (région) : `extern proc _mm512_sub_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:355 `__m512i` (région) : `extern proc _mm512_sub_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:355 `__m512i` (région) : `extern proc _mm512_sub_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:355 `__m512i` (région) : `extern proc _mm512_sub_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:356 `_mm512_xor_si512` (région) : `extern proc _mm512_xor_si512(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:356 `__m512i` (région) : `extern proc _mm512_xor_si512(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:356 `__m512i` (région) : `extern proc _mm512_xor_si512(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:356 `__m512i` (région) : `extern proc _mm512_xor_si512(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:357 `_mm512_mullo_epi32` (région) : `extern proc _mm512_mullo_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:357 `__m512i` (région) : `extern proc _mm512_mullo_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:357 `__m512i` (région) : `extern proc _mm512_mullo_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:357 `__m512i` (région) : `extern proc _mm512_mullo_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:358 `_mm512_maskz_mullo_epi32` (région) : `extern proc _mm512_maskz_mullo_epi32(k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:358 `__m512i` (région) : `extern proc _mm512_maskz_mullo_epi32(k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:358 `__m512i` (région) : `extern proc _mm512_maskz_mullo_epi32(k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:358 `__m512i` (région) : `extern proc _mm512_maskz_mullo_epi32(k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:359 `_mm512_mul_epi32` (région) : `extern proc _mm512_mul_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:359 `__m512i` (région) : `extern proc _mm512_mul_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:359 `__m512i` (région) : `extern proc _mm512_mul_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:359 `__m512i` (région) : `extern proc _mm512_mul_epi32(a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:360 `_mm512_srli_epi64` (région) : `extern proc _mm512_srli_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:360 `__m512i` (région) : `extern proc _mm512_srli_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:360 `__m512i` (région) : `extern proc _mm512_srli_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:361 `_mm512_slli_epi64` (région) : `extern proc _mm512_slli_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:361 `__m512i` (région) : `extern proc _mm512_slli_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:361 `__m512i` (région) : `extern proc _mm512_slli_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:362 `_mm512_srai_epi64` (région) : `extern proc _mm512_srai_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:362 `__m512i` (région) : `extern proc _mm512_srai_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:362 `__m512i` (région) : `extern proc _mm512_srai_epi64(a: __m512i, n: c_uint): __m512i;`
* X ms.chpl:363 `_mm512_movepi32_mask` (région) : `extern proc _mm512_movepi32_mask(a: __m512i): uint(16);`
* X ms.chpl:363 `__m512i` (région) : `extern proc _mm512_movepi32_mask(a: __m512i): uint(16);`
* X ms.chpl:364 `_mm512_mask_testn_epi32_mask` (région) : `extern proc _mm512_mask_testn_epi32_mask(u: uint(16), a: __m512i, b: __m512i): uint(16);`
* X ms.chpl:364 `__m512i` (région) : `extern proc _mm512_mask_testn_epi32_mask(u: uint(16), a: __m512i, b: __m512i): uint(16);`
* X ms.chpl:364 `__m512i` (région) : `extern proc _mm512_mask_testn_epi32_mask(u: uint(16), a: __m512i, b: __m512i): uint(16);`
* X ms.chpl:365 `_mm512_mask_add_epi32` (région) : `extern proc _mm512_mask_add_epi32(src: __m512i, k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:365 `__m512i` (région) : `extern proc _mm512_mask_add_epi32(src: __m512i, k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:365 `__m512i` (région) : `extern proc _mm512_mask_add_epi32(src: __m512i, k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:365 `__m512i` (région) : `extern proc _mm512_mask_add_epi32(src: __m512i, k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:365 `__m512i` (région) : `extern proc _mm512_mask_add_epi32(src: __m512i, k: uint(16), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:366 `_mm512_mask_add_epi64` (région) : `extern proc _mm512_mask_add_epi64(src: __m512i, k: uint(8), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:366 `__m512i` (région) : `extern proc _mm512_mask_add_epi64(src: __m512i, k: uint(8), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:366 `__m512i` (région) : `extern proc _mm512_mask_add_epi64(src: __m512i, k: uint(8), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:366 `__m512i` (région) : `extern proc _mm512_mask_add_epi64(src: __m512i, k: uint(8), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:366 `__m512i` (région) : `extern proc _mm512_mask_add_epi64(src: __m512i, k: uint(8), a: __m512i, b: __m512i): __m512i;`
* X ms.chpl:367 `_mm512_reduce_add_epi32` (région) : `extern proc _mm512_reduce_add_epi32(a: __m512i): int(32);`
* X ms.chpl:367 `__m512i` (région) : `extern proc _mm512_reduce_add_epi32(a: __m512i): int(32);`
* X ms.chpl:368 `_mm512_cvtepi32_epi64` (région) : `extern proc _mm512_cvtepi32_epi64(a: __m256i): __m512i;`
* X ms.chpl:368 `__m256i` (région) : `extern proc _mm512_cvtepi32_epi64(a: __m256i): __m512i;`
* X ms.chpl:368 `__m512i` (région) : `extern proc _mm512_cvtepi32_epi64(a: __m256i): __m512i;`
* X ms.chpl:369 `_mm512_castsi512_si256` (région) : `extern proc _mm512_castsi512_si256(a: __m512i): __m256i;`
* X ms.chpl:369 `__m512i` (région) : `extern proc _mm512_castsi512_si256(a: __m512i): __m256i;`
* X ms.chpl:369 `__m256i` (région) : `extern proc _mm512_castsi512_si256(a: __m512i): __m256i;`
* X ms.chpl:370 `_mm512_maskz_compress_epi64` (région) : `extern proc _mm512_maskz_compress_epi64(k: uint(8), a: __m512i): __m512i;`
* X ms.chpl:370 `__m512i` (région) : `extern proc _mm512_maskz_compress_epi64(k: uint(8), a: __m512i): __m512i;`
* X ms.chpl:370 `__m512i` (région) : `extern proc _mm512_maskz_compress_epi64(k: uint(8), a: __m512i): __m512i;`
* U ms.chpl:377 `c_ptrConst` (région ; portée line : lignes 377 à 377) : `proc q6TunedV(sd: c_ptrConst(int(32)), d: c_ptrConst(uint(8)), q: c_ptrConst(uint(8)), pr: c_ptrConst(int(32))`
* U ms.chpl:377 `c_ptrConst` (région ; portée line : lignes 377 à 377) : `proc q6TunedV(sd: c_ptrConst(int(32)), d: c_ptrConst(uint(8)), q: c_ptrConst(uint(8)), pr: c_ptrConst(int(32))`
* U ms.chpl:377 `c_ptrConst` (région ; portée line : lignes 377 à 377) : `proc q6TunedV(sd: c_ptrConst(int(32)), d: c_ptrConst(uint(8)), q: c_ptrConst(uint(8)), pr: c_ptrConst(int(32))`
* U ms.chpl:377 `c_ptrConst` (région ; portée line : lignes 377 à 377) : `proc q6TunedV(sd: c_ptrConst(int(32)), d: c_ptrConst(uint(8)), q: c_ptrConst(uint(8)), pr: c_ptrConst(int(32))`
* X ms.chpl:379 `_mm512_set1_epi32` (région) : `const c8766 = _mm512_set1_epi32(8766), c9131 = _mm512_set1_epi32(9131), c5 = _mm512_set1_epi32(5),`
* X ms.chpl:379 `_mm512_set1_epi32` (région) : `const c8766 = _mm512_set1_epi32(8766), c9131 = _mm512_set1_epi32(9131), c5 = _mm512_set1_epi32(5),`
* X ms.chpl:379 `_mm512_set1_epi32` (région) : `const c8766 = _mm512_set1_epi32(8766), c9131 = _mm512_set1_epi32(9131), c5 = _mm512_set1_epi32(5),`
* X ms.chpl:380 `_mm512_set1_epi32` (région) : `c8 = _mm512_set1_epi32(8), c24 = _mm512_set1_epi32(24);`
* X ms.chpl:380 `_mm512_set1_epi32` (région) : `c8 = _mm512_set1_epi32(8), c24 = _mm512_set1_epi32(24);`
* X ms.chpl:381 `_mm512_setzero_si512` (région) : `var a0 = _mm512_setzero_si512(), a1 = _mm512_setzero_si512();`
* X ms.chpl:381 `_mm512_setzero_si512` (région) : `var a0 = _mm512_setzero_si512(), a1 = _mm512_setzero_si512();`
* U ms.chpl:385 `c_ptrConst` (région ; portée line : lignes 385 à 385) : `const vsd = _mm512_loadu_si512((sd + i): c_ptrConst(void)), vp = _mm512_loadu_si512((pr + i): c_ptrConst(void)`
* U ms.chpl:385 `c_ptrConst` (région ; portée line : lignes 385 à 385) : `const vsd = _mm512_loadu_si512((sd + i): c_ptrConst(void)), vp = _mm512_loadu_si512((pr + i): c_ptrConst(void)`
* X ms.chpl:385 `_mm512_loadu_si512` (région) : `const vsd = _mm512_loadu_si512((sd + i): c_ptrConst(void)), vp = _mm512_loadu_si512((pr + i): c_ptrConst(void)`
* X ms.chpl:385 `_mm512_loadu_si512` (région) : `const vsd = _mm512_loadu_si512((sd + i): c_ptrConst(void)), vp = _mm512_loadu_si512((pr + i): c_ptrConst(void)`
* U ms.chpl:386 `c_ptrConst` (région ; portée line : lignes 386 à 386) : `const vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((d + i): c_ptrConst(void)));`
* X ms.chpl:386 `_mm512_cvtepu8_epi32` (région) : `const vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((d + i): c_ptrConst(void)));`
* X ms.chpl:386 `_mm_loadu_si128` (région) : `const vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((d + i): c_ptrConst(void)));`
* U ms.chpl:387 `c_ptrConst` (région ; portée line : lignes 387 à 387) : `const vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((q + i): c_ptrConst(void)));`
* X ms.chpl:387 `_mm512_cvtepu8_epi32` (région) : `const vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((q + i): c_ptrConst(void)));`
* X ms.chpl:387 `_mm_loadu_si128` (région) : `const vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((q + i): c_ptrConst(void)));`
* X ms.chpl:388 `_mm512_movepi32_mask` (région) : `const m = ~_mm512_movepi32_mask(_mm512_sub_epi32(vsd, c8766)) & _mm512_movepi32_mask(_mm512_sub_epi32(vsd, c91`
* X ms.chpl:388 `_mm512_sub_epi32` (région) : `const m = ~_mm512_movepi32_mask(_mm512_sub_epi32(vsd, c8766)) & _mm512_movepi32_mask(_mm512_sub_epi32(vsd, c91`
* X ms.chpl:388 `_mm512_movepi32_mask` (région) : `const m = ~_mm512_movepi32_mask(_mm512_sub_epi32(vsd, c8766)) & _mm512_movepi32_mask(_mm512_sub_epi32(vsd, c91`
* X ms.chpl:388 `_mm512_sub_epi32` (région) : `const m = ~_mm512_movepi32_mask(_mm512_sub_epi32(vsd, c8766)) & _mm512_movepi32_mask(_mm512_sub_epi32(vsd, c91`
* X ms.chpl:389 `_mm512_movepi32_mask` (région) : `& ~_mm512_movepi32_mask(_mm512_sub_epi32(vd, c5)) & _mm512_movepi32_mask(_mm512_sub_epi32(vd, c8))`
* X ms.chpl:389 `_mm512_sub_epi32` (région) : `& ~_mm512_movepi32_mask(_mm512_sub_epi32(vd, c5)) & _mm512_movepi32_mask(_mm512_sub_epi32(vd, c8))`
* X ms.chpl:389 `_mm512_movepi32_mask` (région) : `& ~_mm512_movepi32_mask(_mm512_sub_epi32(vd, c5)) & _mm512_movepi32_mask(_mm512_sub_epi32(vd, c8))`
* X ms.chpl:389 `_mm512_sub_epi32` (région) : `& ~_mm512_movepi32_mask(_mm512_sub_epi32(vd, c5)) & _mm512_movepi32_mask(_mm512_sub_epi32(vd, c8))`
* X ms.chpl:390 `_mm512_movepi32_mask` (région) : `& _mm512_movepi32_mask(_mm512_sub_epi32(vq, c24));`
* X ms.chpl:390 `_mm512_sub_epi32` (région) : `& _mm512_movepi32_mask(_mm512_sub_epi32(vq, c24));`
* X ms.chpl:391 `_mm512_maskz_mullo_epi32` (région) : `const pv = _mm512_maskz_mullo_epi32(m, vp, vd);`
* X ms.chpl:392 `_mm512_add_epi64` (région) : `a0 = _mm512_add_epi64(a0, _mm512_srai_epi64(_mm512_slli_epi64(pv, 32), 32));  // lignes paires`
* X ms.chpl:392 `_mm512_srai_epi64` (région) : `a0 = _mm512_add_epi64(a0, _mm512_srai_epi64(_mm512_slli_epi64(pv, 32), 32));  // lignes paires`
* X ms.chpl:392 `_mm512_slli_epi64` (région) : `a0 = _mm512_add_epi64(a0, _mm512_srai_epi64(_mm512_slli_epi64(pv, 32), 32));  // lignes paires`
* X ms.chpl:393 `_mm512_add_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_srai_epi64(pv, 32));                          // lignes impaires`
* X ms.chpl:393 `_mm512_srai_epi64` (région) : `a1 = _mm512_add_epi64(a1, _mm512_srai_epi64(pv, 32));                          // lignes impaires`
* X ms.chpl:396 `_mm512_reduce_add_epi64` (région) : `var s = _mm512_reduce_add_epi64(_mm512_add_epi64(a0, a1)): int;`
* X ms.chpl:396 `_mm512_add_epi64` (région) : `var s = _mm512_reduce_add_epi64(_mm512_add_epi64(a0, a1)): int;`
* U ms.chpl:404 `c_ptrConst` (région ; portée line : lignes 404 à 404) : `proc q1TunedV(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8))`
* U ms.chpl:404 `c_ptrConst` (région ; portée line : lignes 404 à 404) : `proc q1TunedV(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8))`
* U ms.chpl:404 `c_ptrConst` (région ; portée line : lignes 404 à 404) : `proc q1TunedV(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8))`
* U ms.chpl:404 `c_ptrConst` (région ; portée line : lignes 404 à 404) : `proc q1TunedV(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8))`
* U ms.chpl:405 `c_ptrConst` (région ; portée line : lignes 405 à 405) : `t: c_ptrConst(uint(8)), rf: c_ptrConst(uint(8)), ls: c_ptrConst(uint(8)), lo: int, hi: int, ref acc: [] int) {`
* U ms.chpl:405 `c_ptrConst` (région ; portée line : lignes 405 à 405) : `t: c_ptrConst(uint(8)), rf: c_ptrConst(uint(8)), ls: c_ptrConst(uint(8)), lo: int, hi: int, ref acc: [] int) {`
* U ms.chpl:405 `c_ptrConst` (région ; portée line : lignes 405 à 405) : `t: c_ptrConst(uint(8)), rf: c_ptrConst(uint(8)), ls: c_ptrConst(uint(8)), lo: int, hi: int, ref acc: [] int) {`
* X ms.chpl:408 `_mm512_set1_epi32` (région) : `const lim = _mm512_set1_epi32(10472), c100 = _mm512_set1_epi32(100);`
* X ms.chpl:408 `_mm512_set1_epi32` (région) : `const lim = _mm512_set1_epi32(10472), c100 = _mm512_set1_epi32(100);`
* X ms.chpl:412 `__m512i` (région) : `var aq, ap, adp, ace, aco: 6*__m512i;`
* X ms.chpl:415 `_mm512_setzero_si512` (région) : `aq[g] = _mm512_setzero_si512(); ap[g] = aq[g]; adp[g] = aq[g]; ace[g] = aq[g]; aco[g] = aq[g];`
* U ms.chpl:419 `c_ptrConst` (région ; portée line : lignes 419 à 419) : `const pass = _mm512_movepi32_mask(_mm512_sub_epi32(_mm512_loadu_si512((sd + i): c_ptrConst(void)), lim));`
* X ms.chpl:419 `_mm512_movepi32_mask` (région) : `const pass = _mm512_movepi32_mask(_mm512_sub_epi32(_mm512_loadu_si512((sd + i): c_ptrConst(void)), lim));`
* X ms.chpl:419 `_mm512_sub_epi32` (région) : `const pass = _mm512_movepi32_mask(_mm512_sub_epi32(_mm512_loadu_si512((sd + i): c_ptrConst(void)), lim));`
* X ms.chpl:419 `_mm512_loadu_si512` (région) : `const pass = _mm512_movepi32_mask(_mm512_sub_epi32(_mm512_loadu_si512((sd + i): c_ptrConst(void)), lim));`
* U ms.chpl:420 `c_ptrConst` (région ; portée line : lignes 420 à 420) : `const rfv = _mm512_cvtepu8_epi32(_mm_loadu_si128((rf + i): c_ptrConst(void)));`
* X ms.chpl:420 `_mm512_cvtepu8_epi32` (région) : `const rfv = _mm512_cvtepu8_epi32(_mm_loadu_si128((rf + i): c_ptrConst(void)));`
* X ms.chpl:420 `_mm_loadu_si128` (région) : `const rfv = _mm512_cvtepu8_epi32(_mm_loadu_si128((rf + i): c_ptrConst(void)));`
* U ms.chpl:421 `c_ptrConst` (région ; portée line : lignes 421 à 421) : `const vg = _mm512_add_epi32(_mm512_add_epi32(rfv, rfv), _mm512_cvtepu8_epi32(_mm_loadu_si128((ls + i): c_ptrCo`
* X ms.chpl:421 `_mm512_add_epi32` (région) : `const vg = _mm512_add_epi32(_mm512_add_epi32(rfv, rfv), _mm512_cvtepu8_epi32(_mm_loadu_si128((ls + i): c_ptrCo`
* X ms.chpl:421 `_mm512_add_epi32` (région) : `const vg = _mm512_add_epi32(_mm512_add_epi32(rfv, rfv), _mm512_cvtepu8_epi32(_mm_loadu_si128((ls + i): c_ptrCo`
* X ms.chpl:421 `_mm512_cvtepu8_epi32` (région) : `const vg = _mm512_add_epi32(_mm512_add_epi32(rfv, rfv), _mm512_cvtepu8_epi32(_mm_loadu_si128((ls + i): c_ptrCo`
* X ms.chpl:421 `_mm_loadu_si128` (région) : `const vg = _mm512_add_epi32(_mm512_add_epi32(rfv, rfv), _mm512_cvtepu8_epi32(_mm_loadu_si128((ls + i): c_ptrCo`
* U ms.chpl:422 `c_ptrConst` (région ; portée line : lignes 422 à 422) : `const vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((q + i): c_ptrConst(void)));`
* X ms.chpl:422 `_mm512_cvtepu8_epi32` (région) : `const vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((q + i): c_ptrConst(void)));`
* X ms.chpl:422 `_mm_loadu_si128` (région) : `const vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((q + i): c_ptrConst(void)));`
* U ms.chpl:423 `c_ptrConst` (région ; portée line : lignes 423 à 423) : `const vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((d + i): c_ptrConst(void)));`
* X ms.chpl:423 `_mm512_cvtepu8_epi32` (région) : `const vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((d + i): c_ptrConst(void)));`
* X ms.chpl:423 `_mm_loadu_si128` (région) : `const vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((d + i): c_ptrConst(void)));`
* U ms.chpl:424 `c_ptrConst` (région ; portée line : lignes 424 à 424) : `const vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((t + i): c_ptrConst(void))), c100);`
* X ms.chpl:424 `_mm512_add_epi32` (région) : `const vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((t + i): c_ptrConst(void))), c100);`
* X ms.chpl:424 `_mm512_cvtepu8_epi32` (région) : `const vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((t + i): c_ptrConst(void))), c100);`
* X ms.chpl:424 `_mm_loadu_si128` (région) : `const vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((t + i): c_ptrConst(void))), c100);`
* U ms.chpl:425 `c_ptrConst` (région ; portée line : lignes 425 à 425) : `const vp = _mm512_loadu_si512((pr + i): c_ptrConst(void));`
* X ms.chpl:425 `_mm512_loadu_si512` (région) : `const vp = _mm512_loadu_si512((pr + i): c_ptrConst(void));`
* X ms.chpl:426 `_mm512_mullo_epi32` (région) : `const vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));`
* X ms.chpl:426 `_mm512_sub_epi32` (région) : `const vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));`
* X ms.chpl:427 `_mm512_mul_epi32` (région) : `const che = _mm512_mul_epi32(vdp, vt);                                                  // lignes paires`
* X ms.chpl:428 `_mm512_mul_epi32` (région) : `const cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));   // lignes impaires`
* X ms.chpl:428 `_mm512_srli_epi64` (région) : `const cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));   // lignes impaires`
* X ms.chpl:428 `_mm512_srli_epi64` (région) : `const cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));   // lignes impaires`
* X ms.chpl:430 `_mm512_xor_si512` (région) : `const x = _mm512_xor_si512(vg, _mm512_set1_epi32(g: int(32)));`
* X ms.chpl:430 `_mm512_set1_epi32` (région) : `const x = _mm512_xor_si512(vg, _mm512_set1_epi32(g: int(32)));`
* X ms.chpl:431 `_mm512_mask_testn_epi32_mask` (région) : `const m = _mm512_mask_testn_epi32_mask(pass, x, x);`
* X ms.chpl:433 `_mm512_mask_add_epi32` (région) : `aq[g] = _mm512_mask_add_epi32(aq[g], m, aq[g], vq);`
* X ms.chpl:434 `_mm512_mask_add_epi32` (région) : `ap[g] = _mm512_mask_add_epi32(ap[g], m, ap[g], vp);`
* X ms.chpl:435 `_mm512_mask_add_epi32` (région) : `adp[g] = _mm512_mask_add_epi32(adp[g], m, adp[g], vdp);`
* X ms.chpl:436 `_mm512_mask_add_epi64` (région) : `ace[g] = _mm512_mask_add_epi64(ace[g], _pext_u32(m: c_uint, 0x5555: c_uint): uint(8), ace[g], che);`
* X ms.chpl:437 `_mm512_mask_add_epi64` (région) : `aco[g] = _mm512_mask_add_epi64(aco[g], _pext_u32(m: c_uint, 0xAAAA: c_uint): uint(8), aco[g], cho);`
* X ms.chpl:443 `_mm512_reduce_add_epi32` (région) : `acc[g * 5 + 1] += _mm512_reduce_add_epi32(aq[g]);`
* X ms.chpl:444 `_mm512_reduce_add_epi32` (région) : `acc[g * 5 + 2] += _mm512_reduce_add_epi32(ap[g]);`
* X ms.chpl:445 `_mm512_reduce_add_epi64` (région) : `acc[g * 5 + 3] += _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])))`
* X ms.chpl:445 `_mm512_cvtepi32_epi64` (région) : `acc[g * 5 + 3] += _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])))`
* X ms.chpl:445 `_mm512_castsi512_si256` (région) : `acc[g * 5 + 3] += _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])))`
* X ms.chpl:446 `_mm512_reduce_add_epi64` (région) : `+ _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(`
* X ms.chpl:446 `_mm512_cvtepi32_epi64` (région) : `+ _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(`
* X ms.chpl:446 `_mm512_castsi512_si256` (région) : `+ _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(`
* X ms.chpl:447 `_mm512_maskz_compress_epi64` (région) : `_mm512_maskz_compress_epi64(0xF0: uint(8), adp[g]))));`
* X ms.chpl:448 `_mm512_reduce_add_epi64` (région) : `acc[g * 5 + 4] += _mm512_reduce_add_epi64(ace[g]) + _mm512_reduce_add_epi64(aco[g]);`
* X ms.chpl:448 `_mm512_reduce_add_epi64` (région) : `acc[g * 5 + 4] += _mm512_reduce_add_epi64(ace[g]) + _mm512_reduce_add_epi64(aco[g]);`
* U ms.chpl:464 `c_ptrToConst` (région ; portée line : lignes 464 à 464) : `const psd = c_ptrToConst(sd[0]), ppr = c_ptrToConst(pr[0]), pq = c_ptrToConst(q[0]), pd = c_ptrToConst(d[0]),`
* U ms.chpl:464 `c_ptrToConst` (région ; portée line : lignes 464 à 464) : `const psd = c_ptrToConst(sd[0]), ppr = c_ptrToConst(pr[0]), pq = c_ptrToConst(q[0]), pd = c_ptrToConst(d[0]),`
* U ms.chpl:464 `c_ptrToConst` (région ; portée line : lignes 464 à 464) : `const psd = c_ptrToConst(sd[0]), ppr = c_ptrToConst(pr[0]), pq = c_ptrToConst(q[0]), pd = c_ptrToConst(d[0]),`
* U ms.chpl:464 `c_ptrToConst` (région ; portée line : lignes 464 à 464) : `const psd = c_ptrToConst(sd[0]), ppr = c_ptrToConst(pr[0]), pq = c_ptrToConst(q[0]), pd = c_ptrToConst(d[0]),`
* U ms.chpl:465 `c_ptrToConst` (région ; portée line : lignes 465 à 465) : `pt = c_ptrToConst(t[0]), prf = c_ptrToConst(rf[0]), pls = c_ptrToConst(ls[0]);`
* U ms.chpl:465 `c_ptrToConst` (région ; portée line : lignes 465 à 465) : `pt = c_ptrToConst(t[0]), prf = c_ptrToConst(rf[0]), pls = c_ptrToConst(ls[0]);`
* U ms.chpl:465 `c_ptrToConst` (région ; portée line : lignes 465 à 465) : `pt = c_ptrToConst(t[0]), prf = c_ptrToConst(rf[0]), pls = c_ptrToConst(ls[0]);`
* U ms.chpl:534 `c_ptrTo` (région ; portée line : lignes 534 à 534) : `prefetch(c_ptrTo(tab[h[b]]));`
* X ms.chpl:699 `__m512d` (région) : `extern type __m512d;`
* X ms.chpl:700 `_mm512_set1_pd` (région) : `extern proc _mm512_set1_pd(x: real): __m512d;`
* X ms.chpl:700 `__m512d` (région) : `extern proc _mm512_set1_pd(x: real): __m512d;`
* U ms.chpl:701 `c_ptrConst` (région ; portée line : lignes 701 à 701) : `extern proc _mm512_loadu_pd(p: c_ptrConst(void)): __m512d;`
* X ms.chpl:701 `_mm512_loadu_pd` (région) : `extern proc _mm512_loadu_pd(p: c_ptrConst(void)): __m512d;`
* X ms.chpl:701 `__m512d` (région) : `extern proc _mm512_loadu_pd(p: c_ptrConst(void)): __m512d;`
* U ms.chpl:702 `c_ptr` (région ; portée line : lignes 702 à 702) : `extern proc _mm512_storeu_pd(p: c_ptr(void), a: __m512d);`
* X ms.chpl:702 `_mm512_storeu_pd` (région) : `extern proc _mm512_storeu_pd(p: c_ptr(void), a: __m512d);`
* X ms.chpl:702 `__m512d` (région) : `extern proc _mm512_storeu_pd(p: c_ptr(void), a: __m512d);`
* X ms.chpl:703 `_mm512_add_pd` (région) : `extern proc _mm512_add_pd(a: __m512d, b: __m512d): __m512d;`
* X ms.chpl:703 `__m512d` (région) : `extern proc _mm512_add_pd(a: __m512d, b: __m512d): __m512d;`
* X ms.chpl:703 `__m512d` (région) : `extern proc _mm512_add_pd(a: __m512d, b: __m512d): __m512d;`
* X ms.chpl:703 `__m512d` (région) : `extern proc _mm512_add_pd(a: __m512d, b: __m512d): __m512d;`
* X ms.chpl:704 `_mm512_mul_pd` (région) : `extern proc _mm512_mul_pd(a: __m512d, b: __m512d): __m512d;`
* X ms.chpl:704 `__m512d` (région) : `extern proc _mm512_mul_pd(a: __m512d, b: __m512d): __m512d;`
* X ms.chpl:704 `__m512d` (région) : `extern proc _mm512_mul_pd(a: __m512d, b: __m512d): __m512d;`
* X ms.chpl:704 `__m512d` (région) : `extern proc _mm512_mul_pd(a: __m512d, b: __m512d): __m512d;`
* U ms.chpl:705 `c_ptrConst` (région ; portée line : lignes 705 à 705) : `proc k9RowsV(a: c_ptrConst(real), b: c_ptr(real), r0: int, r1: int) {`
* U ms.chpl:705 `c_ptr` (région ; portée line : lignes 705 à 705) : `proc k9RowsV(a: c_ptrConst(real), b: c_ptr(real), r0: int, r1: int) {`
* X ms.chpl:706 `_mm512_set1_pd` (région) : `const q4 = _mm512_set1_pd(0.25);`
* U ms.chpl:712 `c_ptrConst` (région ; portée line : lignes 712 à 712) : `const s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd((up + j): c_ptrConst(void)),`
* X ms.chpl:712 `_mm512_add_pd` (région) : `const s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd((up + j): c_ptrConst(void)),`
* X ms.chpl:712 `_mm512_add_pd` (région) : `const s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd((up + j): c_ptrConst(void)),`
* X ms.chpl:712 `_mm512_add_pd` (région) : `const s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd((up + j): c_ptrConst(void)),`
* X ms.chpl:712 `_mm512_loadu_pd` (région) : `const s = _mm512_add_pd(_mm512_add_pd(_mm512_add_pd(_mm512_loadu_pd((up + j): c_ptrConst(void)),`
* U ms.chpl:713 `c_ptrConst` (région ; portée line : lignes 713 à 713) : `_mm512_loadu_pd((dn + j): c_ptrConst(void))),`
* X ms.chpl:713 `_mm512_loadu_pd` (région) : `_mm512_loadu_pd((dn + j): c_ptrConst(void))),`
* U ms.chpl:714 `c_ptrConst` (région ; portée line : lignes 714 à 714) : `_mm512_loadu_pd((mid + j - 1): c_ptrConst(void))),`
* X ms.chpl:714 `_mm512_loadu_pd` (région) : `_mm512_loadu_pd((mid + j - 1): c_ptrConst(void))),`
* U ms.chpl:715 `c_ptrConst` (région ; portée line : lignes 715 à 715) : `_mm512_loadu_pd((mid + j + 1): c_ptrConst(void)));`
* X ms.chpl:715 `_mm512_loadu_pd` (région) : `_mm512_loadu_pd((mid + j + 1): c_ptrConst(void)));`
* U ms.chpl:716 `c_ptr` (région ; portée line : lignes 716 à 716) : `_mm512_storeu_pd((o + j): c_ptr(void), _mm512_mul_pd(q4, s));`
* X ms.chpl:716 `_mm512_storeu_pd` (région) : `_mm512_storeu_pd((o + j): c_ptr(void), _mm512_mul_pd(q4, s));`
* X ms.chpl:716 `_mm512_mul_pd` (région) : `_mm512_storeu_pd((o + j): c_ptr(void), _mm512_mul_pd(q4, s));`
* U ms.chpl:727 `c_ptrConst` (région ; portée line : lignes 727 à 727) : `proc k9ParV(a: c_ptrConst(real), b: c_ptr(real)) {`
* U ms.chpl:727 `c_ptr` (région ; portée line : lignes 727 à 727) : `proc k9ParV(a: c_ptrConst(real), b: c_ptr(real)) {`
* U ms.chpl:741 `c_ptrToConst` (hors région ; portée line : lignes 741 à 741) : `k9RowsV(c_ptrToConst(a[0, 0]), c_ptrTo(b[0, 0]), 1, M9 - 2);`
* U ms.chpl:741 `c_ptrTo` (hors région ; portée line : lignes 741 à 741) : `k9RowsV(c_ptrToConst(a[0, 0]), c_ptrTo(b[0, 0]), 1, M9 - 2);`
* U ms.chpl:742 `c_ptrToConst` (hors région ; portée line : lignes 742 à 742) : `k9RowsV(c_ptrToConst(b[0, 0]), c_ptrTo(a[0, 0]), 1, M9 - 2);`
* U ms.chpl:742 `c_ptrTo` (hors région ; portée line : lignes 742 à 742) : `k9RowsV(c_ptrToConst(b[0, 0]), c_ptrTo(a[0, 0]), 1, M9 - 2);`
* U ms.chpl:744 `c_ptrToConst` (hors région ; portée line : lignes 744 à 744) : `k9ParV(c_ptrToConst(a[0, 0]), c_ptrTo(b[0, 0]));`
* U ms.chpl:744 `c_ptrTo` (hors région ; portée line : lignes 744 à 744) : `k9ParV(c_ptrToConst(a[0, 0]), c_ptrTo(b[0, 0]));`
* U ms.chpl:745 `c_ptrToConst` (hors région ; portée line : lignes 745 à 745) : `k9ParV(c_ptrToConst(b[0, 0]), c_ptrTo(a[0, 0]));`
* U ms.chpl:745 `c_ptrTo` (hors région ; portée line : lignes 745 à 745) : `k9ParV(c_ptrToConst(b[0, 0]), c_ptrTo(a[0, 0]));`

## fortran


## swift

* U ms.swift:15 `&*` (hors région ; portée line : lignes 15 à 15) : `return UInt64(t.tv_sec) &* 1_000_000_000 &+ UInt64(t.tv_nsec)`
* U ms.swift:15 `&+` (hors région ; portée line : lignes 15 à 15) : `return UInt64(t.tv_sec) &* 1_000_000_000 &+ UInt64(t.tv_nsec)`
* U ms.swift:17 `&-` (hors région ; portée line : lignes 17 à 17) : `func secs(_ t0: UInt64) -> Double { Double(nowNs() &- t0) * 1e-9 }`
* U ms.swift:23 `UnsafeMutableRawBufferPointer` (hors région ; portée line : lignes 23 à 23) : `func loadRaw(_ name: String) -> UnsafeMutableRawBufferPointer {`
* U ms.swift:30 `UnsafeMutableRawPointer` (hors région ; portée line : lignes 30 à 30) : `let p = UnsafeMutableRawPointer.allocate(byteCount: max(n, 64), alignment: 64)`
* U ms.swift:38 `UnsafeMutableRawBufferPointer` (hors région ; portée line : lignes 38 à 38) : `return UnsafeMutableRawBufferPointer(start: p, count: n)`
* U ms.swift:40 `UnsafeMutableBufferPointer` (hors région ; portée line : lignes 40 à 40) : `func load<T>(_ name: String, _: T.Type) -> UnsafeMutableBufferPointer<T> { loadRaw(name).bindMemory(to: T.self`
* U ms.swift:47 `UnsafeMutablePointer` (région ; portée line : lignes 47 à 47) : `func alignedBuffer<T>(_ n: Int, _: T.Type, alignment: Int = 64) -> UnsafeMutablePointer<T> {`
* U ms.swift:48 `UnsafeMutableRawPointer` (région ; portée line : lignes 48 à 48) : `UnsafeMutableRawPointer.allocate(byteCount: n * MemoryLayout<T>.stride, alignment: alignment).bindMemory(to: T`
* U ms.swift:90 `UnsafePointer` (région ; portée line : lignes 90 à 90) : `@inline(__always) func ld16(_ p: UnsafePointer<Float>) -> SIMD16<Float> { UnsafeRawPointer(p).loadUnaligned(as`
* U ms.swift:90 `UnsafeRawPointer` (région ; portée line : lignes 90 à 90) : `@inline(__always) func ld16(_ p: UnsafePointer<Float>) -> SIMD16<Float> { UnsafeRawPointer(p).loadUnaligned(as`
* U ms.swift:91 `UnsafePointer` (région ; portée line : lignes 91 à 91) : `@inline(__always) func ld16(_ p: UnsafePointer<Int32>) -> SIMD16<Int32> { UnsafeRawPointer(p).loadUnaligned(as`
* U ms.swift:91 `UnsafeRawPointer` (région ; portée line : lignes 91 à 91) : `@inline(__always) func ld16(_ p: UnsafePointer<Int32>) -> SIMD16<Int32> { UnsafeRawPointer(p).loadUnaligned(as`
* U ms.swift:94 `UnsafePointer` (région ; portée line : lignes 94 à 94) : `@inline(__always) func ld16(_ p: UnsafePointer<UInt8>) -> SIMD16<Int32> {`
* U ms.swift:104 `UnsafePointer` (région ; portée line : lignes 104 à 104) : `@inline(__always) func ld8(_ p: UnsafePointer<Double>) -> SIMD8<Double> { UnsafeRawPointer(p).loadUnaligned(as`
* U ms.swift:104 `UnsafeRawPointer` (région ; portée line : lignes 104 à 104) : `@inline(__always) func ld8(_ p: UnsafePointer<Double>) -> SIMD8<Double> { UnsafeRawPointer(p).loadUnaligned(as`
* U ms.swift:122 `UnsafePointer` (hors région ; portée line : lignes 122 à 122) : `func particle(_ f: UnsafePointer<Float>) -> Particle {`
* U ms.swift:134 `UnsafePointer` (hors région ; portée line : lignes 134 à 134) : `@inline(never) func k1AoS(_ p: UnsafePointer<Particle>, _ n: Int) -> Double {`
* U ms.swift:140 `&+` (hors région ; portée line : lignes 140 à 140) : `let q = p[i &+ k]`
* U ms.swift:144 `&+` (hors région ; portée line : lignes 144 à 144) : `i &+= 8`
* U ms.swift:149 `UnsafePointer` (région ; portée line : lignes 149 à 149) : `@inline(never) func k1SoA(_ vx: UnsafePointer<Float>, _ vy: UnsafePointer<Float>, _ vz: UnsafePointer<Float>,`
* U ms.swift:149 `UnsafePointer` (région ; portée line : lignes 149 à 149) : `@inline(never) func k1SoA(_ vx: UnsafePointer<Float>, _ vy: UnsafePointer<Float>, _ vz: UnsafePointer<Float>,`
* U ms.swift:149 `UnsafePointer` (région ; portée line : lignes 149 à 149) : `@inline(never) func k1SoA(_ vx: UnsafePointer<Float>, _ vy: UnsafePointer<Float>, _ vz: UnsafePointer<Float>,`
* U ms.swift:150 `UnsafePointer` (région ; portée line : lignes 150 à 150) : `_ m: UnsafePointer<Float>, _ n: Int) -> Double {`
* U ms.swift:165 `&+` (région ; portée line : lignes 165 à 165) : `let j = i &+ 16`
* U ms.swift:174 `&+` (région ; portée line : lignes 174 à 174) : `i &+= 32`
* U ms.swift:190 `UnsafePointer` (hors région ; portée line : lignes 190 à 190) : `let rp = UnsafePointer(raw.baseAddress!)`
* U ms.swift:200 `UnsafeMutablePointer` (région ; portée line : lignes 200 à 200) : `var f = [UnsafeMutablePointer<Float>]()`
* U ms.swift:202 `withUnsafeBytes` (région ; portée brace : lignes 202 à 207) : `ps.withUnsafeBytes { b in`
* U ms.swift:223 `UnsafeMutableBufferPointer` (hors région ; portée line : lignes 223 à 223) : `_ = UnsafeMutableBufferPointer(start: a, count: N1).initialize(from: ps)`
* U ms.swift:242 `UnsafePointer` (hors région ; portée line : lignes 242 à 242) : `@inline(never) func k2Chase(_ a: UnsafePointer<UInt32>, _ h: Int) -> UInt32 {`
* U ms.swift:263 `UnsafeMutableRawPointer` (région ; portée line : lignes 263 à 263) : `let mem = UnsafeMutableRawPointer.allocate(byteCount: 4 * 128, alignment: 128).bindMemory(to: Atomic<UInt64>.s`
* U ms.swift:275 `&+` (région ; portée line : lignes 275 à 275) : `for _ in 0..<ITER3 { x.pointee.store(x.pointee.load(ordering: .relaxed) &+ 1, ordering: .relaxed) }`
* U ms.swift:293 `UnsafeBufferPointer` (hors région ; portée line : lignes 293 à 293) : `@inline(never) func k4Branchless(_ v: UnsafeBufferPointer<UInt8>) -> UInt64 {`
* U ms.swift:295 `&+` (hors région ; portée line : lignes 295 à 295) : `for x in v { s &+= UInt64(x) &* UInt64(x >> 7) }`
* U ms.swift:295 `&*` (hors région ; portée line : lignes 295 à 295) : `for x in v { s &+= UInt64(x) &* UInt64(x >> 7) }`
* U ms.swift:303 `UnsafeBufferPointer` (région ; portée line : lignes 303 à 303) : `@inline(never) func k4Tuned(_ v: UnsafeBufferPointer<UInt8>) -> UInt64 {`
* U ms.swift:305 `UnsafeRawPointer` (région ; portée line : lignes 305 à 305) : `let base = UnsafeRawPointer(v.baseAddress!)`
* U ms.swift:311 `&+` (région ; portée line : lignes 311 à 311) : `while i &+ 64 <= n {`
* U ms.swift:313 `&*` (région ; portée line : lignes 313 à 313) : `let y = w & (((w &>> 7) & ones) &* 0xFF)`
* U ms.swift:314 `&+` (région ; portée line : lignes 314 à 314) : `let p = (y & lo) &+ ((y &>> 8) & lo)`
* U ms.swift:315 `&+` (région ; portée line : lignes 315 à 315) : `acc &+= (p &* mul) &>> 48`
* U ms.swift:315 `&*` (région ; portée line : lignes 315 à 315) : `acc &+= (p &* mul) &>> 48`
* U ms.swift:316 `&+` (région ; portée line : lignes 316 à 316) : `i &+= 64`
* U ms.swift:320 `&+` (région ; portée line : lignes 320 à 320) : `if v[i] >= 128 { s &+= UInt64(v[i]) }`
* U ms.swift:321 `&+` (région ; portée line : lignes 321 à 321) : `i &+= 1`
* U ms.swift:330 `UnsafeBufferPointer` (hors région ; portée line : lignes 330 à 330) : `@inline(never) func k4Swar(_ v: UnsafeBufferPointer<UInt8>) -> UInt64 {`
* U ms.swift:333 `UnsafeRawPointer` (hors région ; portée line : lignes 333 à 333) : `let base = UnsafeRawPointer(v.baseAddress!)`
* U ms.swift:336 `&+` (hors région ; portée line : lignes 336 à 336) : `while i &+ 8 <= n {`
* U ms.swift:337 `&+` (hors région ; portée line : lignes 337 à 337) : `let end = i &+ 128 * 8 <= n ? i &+ 128 * 8 : n &- (n &- i) % 8`
* U ms.swift:337 `&+` (hors région ; portée line : lignes 337 à 337) : `let end = i &+ 128 * 8 <= n ? i &+ 128 * 8 : n &- (n &- i) % 8`
* U ms.swift:337 `&-` (hors région ; portée line : lignes 337 à 337) : `let end = i &+ 128 * 8 <= n ? i &+ 128 * 8 : n &- (n &- i) % 8`
* U ms.swift:337 `&-` (hors région ; portée line : lignes 337 à 337) : `let end = i &+ 128 * 8 <= n ? i &+ 128 * 8 : n &- (n &- i) % 8`
* U ms.swift:341 `&*` (hors région ; portée line : lignes 341 à 341) : `let y = w & (((w &>> 7) & ones) &* 0xFF)`
* U ms.swift:342 `&+` (hors région ; portée line : lignes 342 à 342) : `acc &+= (y & lo) &+ ((y &>> 8) & lo)`
* U ms.swift:342 `&+` (hors région ; portée line : lignes 342 à 342) : `acc &+= (y & lo) &+ ((y &>> 8) & lo)`
* U ms.swift:343 `&+` (hors région ; portée line : lignes 343 à 343) : `i &+= 8`
* U ms.swift:345 `&+` (hors région ; portée line : lignes 345 à 345) : `acc = (acc & 0x0000_FFFF_0000_FFFF) &+ ((acc &>> 16) & 0x0000_FFFF_0000_FFFF)  // deux voies de 32 bits`
* U ms.swift:346 `&+` (hors région ; portée line : lignes 346 à 346) : `s &+= (acc & 0xFFFF_FFFF) &+ (acc &>> 32)`
* U ms.swift:346 `&+` (hors région ; portée line : lignes 346 à 346) : `s &+= (acc & 0xFFFF_FFFF) &+ (acc &>> 32)`
* U ms.swift:349 `&+` (hors région ; portée line : lignes 349 à 349) : `s &+= UInt64(v[i]) &* UInt64(v[i] &>> 7)`
* U ms.swift:349 `&*` (hors région ; portée line : lignes 349 à 349) : `s &+= UInt64(v[i]) &* UInt64(v[i] &>> 7)`
* U ms.swift:350 `&+` (hors région ; portée line : lignes 350 à 350) : `i &+= 1`
* U ms.swift:356 `UnsafeBufferPointer` (hors région ; portée line : lignes 356 à 356) : `let d = UnsafeBufferPointer(load("k4_bytes.u8", UInt8.self))`
* U ms.swift:384 `UnsafePointer` (région ; portée line : lignes 384 à 384) : `@inline(never) func k5Tuned(_ a: UnsafePointer<Float>, _ b: UnsafePointer<Float>, _ n: Int) -> Float {`
* U ms.swift:384 `UnsafePointer` (région ; portée line : lignes 384 à 384) : `@inline(never) func k5Tuned(_ a: UnsafePointer<Float>, _ b: UnsafePointer<Float>, _ n: Int) -> Float {`
* U ms.swift:389 `&+` (région ; portée line : lignes 389 à 389) : `s1.addProduct(ld16(a + (i &+ 16)), ld16(b + (i &+ 16)))`
* U ms.swift:389 `&+` (région ; portée line : lignes 389 à 389) : `s1.addProduct(ld16(a + (i &+ 16)), ld16(b + (i &+ 16)))`
* U ms.swift:390 `&+` (région ; portée line : lignes 390 à 390) : `s2.addProduct(ld16(a + (i &+ 32)), ld16(b + (i &+ 32)))`
* U ms.swift:390 `&+` (région ; portée line : lignes 390 à 390) : `s2.addProduct(ld16(a + (i &+ 32)), ld16(b + (i &+ 32)))`
* U ms.swift:391 `&+` (région ; portée line : lignes 391 à 391) : `s3.addProduct(ld16(a + (i &+ 48)), ld16(b + (i &+ 48)))`
* U ms.swift:391 `&+` (région ; portée line : lignes 391 à 391) : `s3.addProduct(ld16(a + (i &+ 48)), ld16(b + (i &+ 48)))`
* U ms.swift:392 `&+` (région ; portée line : lignes 392 à 392) : `i &+= 64`
* U ms.swift:422 `UnsafePointer` (région ; portée line : lignes 422 à 422) : `let sd, pr: UnsafePointer<Int32>`
* U ms.swift:423 `UnsafePointer` (région ; portée line : lignes 423 à 423) : `let q, d, t, rf, ls: UnsafePointer<UInt8>`
* U ms.swift:455 `&+` (région ; portée line : lignes 455 à 455) : `s &+= Int64(c.pr[i]) &* Int64(c.d[i])`
* U ms.swift:455 `&*` (région ; portée line : lignes 455 à 455) : `s &+= Int64(c.pr[i]) &* Int64(c.d[i])`
* U ms.swift:459 `UnsafeMutablePointer` (région ; portée line : lignes 459 à 459) : `func q1Tail(_ c: ColsP, _ lo: Int, _ hi: Int, _ acc: UnsafeMutablePointer<Int64>) {`
* U ms.swift:461 `&*` (région ; portée line : lignes 461 à 461) : `let g = Int(c.rf[i]) &* 2 &+ Int(c.ls[i])`
* U ms.swift:461 `&+` (région ; portée line : lignes 461 à 461) : `let g = Int(c.rf[i]) &* 2 &+ Int(c.ls[i])`
* U ms.swift:462 `&*` (région ; portée line : lignes 462 à 462) : `let p = Int64(c.pr[i]), dp = p &* (100 &- Int64(c.d[i]))`
* U ms.swift:462 `&-` (région ; portée line : lignes 462 à 462) : `let p = Int64(c.pr[i]), dp = p &* (100 &- Int64(c.d[i]))`
* U ms.swift:463 `&+` (région ; portée line : lignes 463 à 463) : `acc[g * 5] &+= 1`
* U ms.swift:464 `&+` (région ; portée line : lignes 464 à 464) : `acc[g * 5 + 1] &+= Int64(c.q[i])`
* U ms.swift:465 `&+` (région ; portée line : lignes 465 à 465) : `acc[g * 5 + 2] &+= p`
* U ms.swift:466 `&+` (région ; portée line : lignes 466 à 466) : `acc[g * 5 + 3] &+= dp`
* U ms.swift:467 `&+` (région ; portée line : lignes 467 à 467) : `acc[g * 5 + 4] &+= dp &* (100 &+ Int64(c.t[i]))`
* U ms.swift:467 `&*` (région ; portée line : lignes 467 à 467) : `acc[g * 5 + 4] &+= dp &* (100 &+ Int64(c.t[i]))`
* U ms.swift:467 `&+` (région ; portée line : lignes 467 à 467) : `acc[g * 5 + 4] &+= dp &* (100 &+ Int64(c.t[i]))`
* U ms.swift:477 `&+` (région ; portée line : lignes 477 à 477) : `while i &+ 16 <= hi {`
* U ms.swift:480 `&+` (région ; portée line : lignes 480 à 480) : `acc &+= widen(zero.replacing(with: pr &* d, where: m))`
* U ms.swift:480 `&*` (région ; portée line : lignes 480 à 480) : `acc &+= widen(zero.replacing(with: pr &* d, where: m))`
* U ms.swift:481 `&+` (région ; portée line : lignes 481 à 481) : `i &+= 16`
* U ms.swift:483 `&+` (région ; portée line : lignes 483 à 483) : `return acc.wrappedSum() &+ q6Tail(c, i, hi)`
* U ms.swift:494 `&+` (région ; portée line : lignes 494 à 494) : `cnt &+= z.replacing(with: SIMD16<Int32>(repeating: 1), where: m)`
* U ms.swift:495 `&+` (région ; portée line : lignes 495 à 495) : `q &+= z.replacing(with: vq, where: m)`
* U ms.swift:496 `&+` (région ; portée line : lignes 496 à 496) : `p &+= z.replacing(with: vp, where: m)`
* U ms.swift:497 `&+` (région ; portée line : lignes 497 à 497) : `dp &+= z.replacing(with: vdp, where: m)`
* U ms.swift:498 `&+` (région ; portée line : lignes 498 à 498) : `ch &+= SIMD16<Int64>().replacing(with: vch, where: m64)`
* U ms.swift:500 `UnsafeMutablePointer` (région ; portée line : lignes 500 à 500) : `@inline(__always) func flush(_ a: UnsafeMutablePointer<Int64>) {`
* U ms.swift:501 `&+` (région ; portée line : lignes 501 à 501) : `a[0] &+= Int64(cnt.wrappedSum())`
* U ms.swift:502 `&+` (région ; portée line : lignes 502 à 502) : `a[1] &+= Int64(q.wrappedSum())`
* U ms.swift:503 `&+` (région ; portée line : lignes 503 à 503) : `a[2] &+= Int64(p.wrappedSum())`
* U ms.swift:504 `&+` (région ; portée line : lignes 504 à 504) : `a[3] &+= widen(dp).wrappedSum()`
* U ms.swift:505 `&+` (région ; portée line : lignes 505 à 505) : `a[4] &+= ch.wrappedSum()`
* U ms.swift:508 `UnsafeMutablePointer` (région ; portée line : lignes 508 à 508) : `@inline(never) func q1Tuned(_ c: ColsP, _ lo: Int, _ hi: Int, _ acc: UnsafeMutablePointer<Int64>) {`
* U ms.swift:513 `&+` (région ; portée line : lignes 513 à 513) : `while i &+ 16 <= hi {`
* U ms.swift:515 `&+` (région ; portée line : lignes 515 à 515) : `let end = i &+ 4096 <= hi ? i &+ 4096 : hi &- (hi &- i) % 16`
* U ms.swift:515 `&+` (région ; portée line : lignes 515 à 515) : `let end = i &+ 4096 <= hi ? i &+ 4096 : hi &- (hi &- i) % 16`
* U ms.swift:515 `&-` (région ; portée line : lignes 515 à 515) : `let end = i &+ 4096 <= hi ? i &+ 4096 : hi &- (hi &- i) % 16`
* U ms.swift:515 `&-` (région ; portée line : lignes 515 à 515) : `let end = i &+ 4096 <= hi ? i &+ 4096 : hi &- (hi &- i) % 16`
* U ms.swift:519 `&*` (région ; portée line : lignes 519 à 519) : `let vg = (ld16(c.rf + i) &* two &+ ld16(c.ls + i)).replacing(with: minus1, where: ld16(c.sd + i) .> lim)`
* U ms.swift:519 `&+` (région ; portée line : lignes 519 à 519) : `let vg = (ld16(c.rf + i) &* two &+ ld16(c.ls + i)).replacing(with: minus1, where: ld16(c.sd + i) .> lim)`
* U ms.swift:521 `&+` (région ; portée line : lignes 521 à 521) : `let vq = ld16(c.q + i), vd = ld16(c.d + i), vt = ld16(c.t + i) &+ c100, vp = ld16(c.pr + i)`
* U ms.swift:522 `&*` (région ; portée line : lignes 522 à 522) : `let vdp = vp &* (c100 &- vd)`
* U ms.swift:522 `&-` (région ; portée line : lignes 522 à 522) : `let vdp = vp &* (c100 &- vd)`
* U ms.swift:523 `&*` (région ; portée line : lignes 523 à 523) : `let vch = widen(vdp) &* widen(vt)`
* U ms.swift:530 `&+` (région ; portée line : lignes 530 à 530) : `i &+= 16`
* U ms.swift:559 `UnsafePointer` (région ; portée line : lignes 559 à 559) : `let c = ColsP(sd: UnsafePointer(load("k6_shipdate.i32", Int32.self).baseAddress!),`
* U ms.swift:560 `UnsafePointer` (région ; portée line : lignes 560 à 560) : `pr: UnsafePointer(load("k6_extendedprice.i32", Int32.self).baseAddress!),`
* U ms.swift:561 `UnsafePointer` (région ; portée line : lignes 561 à 561) : `q: UnsafePointer(load("k6_quantity.u8", UInt8.self).baseAddress!),`
* U ms.swift:562 `UnsafePointer` (région ; portée line : lignes 562 à 562) : `d: UnsafePointer(load("k6_discount.u8", UInt8.self).baseAddress!),`
* U ms.swift:563 `UnsafePointer` (région ; portée line : lignes 563 à 563) : `t: UnsafePointer(load("k6_tax.u8", UInt8.self).baseAddress!),`
* U ms.swift:564 `UnsafePointer` (région ; portée line : lignes 564 à 564) : `rf: UnsafePointer(load("k6_returnflag.u8", UInt8.self).baseAddress!),`
* U ms.swift:565 `UnsafePointer` (région ; portée line : lignes 565 à 565) : `ls: UnsafePointer(load("k6_linestatus.u8", UInt8.self).baseAddress!))`
* U ms.swift:566 `UnsafeMutablePointer` (région ; portée line : lignes 566 à 566) : `nonisolated(unsafe) let part = UnsafeMutablePointer<Int64>.allocate(capacity: 4 * 32)`
* U ms.swift:579 `&+` (région ; portée line : lignes 579 à 579) : `for k in 0..<(4 * 32) { s &+= part[k] }`
* U ms.swift:585 `&+` (région ; portée line : lignes 585 à 585) : `for k in 0..<(4 * 32) { s &+= part[k] }`
* U ms.swift:590 `&+` (hors région ; portée line : lignes 590 à 590) : `if q1 && v != "mt" && pool == nil { for k in 0..<30 { s &+= part[k] } }`
* U ms.swift:615 `UnsafeRawPointer` (hors région ; portée line : lignes 615 à 615) : `func llvmPrefetch(_ p: UnsafeRawPointer, _ rw: Int32, _ locality: Int32, _ cache: Int32)`
* U ms.swift:638 `withUnsafeBufferPointer` (hors région ; portée brace : lignes 638 à 668) : `keys.withUnsafeBufferPointer { kb in`
* U ms.swift:639 `withUnsafeBufferPointer` (hors région ; portée brace : lignes 639 à 667) : `vals.withUnsafeBufferPointer { vb in`
* U ms.swift:643 `&+` (hors région ; portée line : lignes 643 à 643) : `while i &+ 16 <= n {`
* U ms.swift:645 `&+` (hors région ; portée line : lignes 645 à 645) : `h[b] = (kb[i &+ b] &* 0x9E37_79B1) &>> (32 &- LOG)`
* U ms.swift:645 `&*` (hors région ; portée line : lignes 645 à 645) : `h[b] = (kb[i &+ b] &* 0x9E37_79B1) &>> (32 &- LOG)`
* U ms.swift:645 `&-` (hors région ; portée line : lignes 645 à 645) : `h[b] = (kb[i &+ b] &* 0x9E37_79B1) &>> (32 &- LOG)`
* U ms.swift:646 `UnsafeRawPointer` (hors région ; portée line : lignes 646 à 646) : `llvmPrefetch(UnsafeRawPointer(tab + Int(h[b])), 1, 3, 1)`
* U ms.swift:649 `&+` (hors région ; portée line : lignes 649 à 649) : `let k = kb[i &+ b]`
* U ms.swift:651 `&+` (hors région ; portée line : lignes 651 à 651) : `while tab[s].count != 0 && tab[s].key != k { s = (s &+ 1) & (CAP &- 1) }`
* U ms.swift:651 `&-` (hors région ; portée line : lignes 651 à 651) : `while tab[s].count != 0 && tab[s].key != k { s = (s &+ 1) & (CAP &- 1) }`
* U ms.swift:653 `&+` (hors région ; portée line : lignes 653 à 653) : `tab[s].count &+= 1`
* U ms.swift:654 `&+` (hors région ; portée line : lignes 654 à 654) : `tab[s].sum &+= UInt64(vb[i &+ b])`
* U ms.swift:654 `&+` (hors région ; portée line : lignes 654 à 654) : `tab[s].sum &+= UInt64(vb[i &+ b])`
* U ms.swift:656 `&+` (hors région ; portée line : lignes 656 à 656) : `i &+= 16`
* U ms.swift:660 `&*` (hors région ; portée line : lignes 660 à 660) : `var s = Int((k &* 0x9E37_79B1) >> (32 &- LOG))`
* U ms.swift:660 `&-` (hors région ; portée line : lignes 660 à 660) : `var s = Int((k &* 0x9E37_79B1) >> (32 &- LOG))`
* U ms.swift:661 `&+` (hors région ; portée line : lignes 661 à 661) : `while tab[s].count != 0 && tab[s].key != k { s = (s &+ 1) & (CAP &- 1) }`
* U ms.swift:661 `&-` (hors région ; portée line : lignes 661 à 661) : `while tab[s].count != 0 && tab[s].key != k { s = (s &+ 1) & (CAP &- 1) }`
* U ms.swift:663 `&+` (hors région ; portée line : lignes 663 à 663) : `tab[s].count &+= 1`
* U ms.swift:664 `&+` (hors région ; portée line : lignes 664 à 664) : `tab[s].sum &+= UInt64(vb[i])`
* U ms.swift:665 `&+` (hors région ; portée line : lignes 665 à 665) : `i &+= 1`
* U ms.swift:672 `&+` (hors région ; portée line : lignes 672 à 672) : `ws &+= tab[s].sum &* UInt64((tab[s].key & 1023) + 1)`
* U ms.swift:672 `&*` (hors région ; portée line : lignes 672 à 672) : `ws &+= tab[s].sum &* UInt64((tab[s].key & 1023) + 1)`
* U ms.swift:680 `withUnsafeBufferPointer` (région ; portée brace : lignes 680 à 691) : `keys.withUnsafeBufferPointer { kb in`
* U ms.swift:681 `withUnsafeBufferPointer` (région ; portée brace : lignes 681 à 690) : `vals.withUnsafeBufferPointer { vb in`
* U ms.swift:684 `&*` (région ; portée line : lignes 684 à 684) : `var s = Int((k &* 0x9E37_79B1) >> (32 &- LOG))`
* U ms.swift:684 `&-` (région ; portée line : lignes 684 à 684) : `var s = Int((k &* 0x9E37_79B1) >> (32 &- LOG))`
* U ms.swift:685 `&+` (région ; portée line : lignes 685 à 685) : `while tab[s].count != 0 && tab[s].key != k { s = (s &+ 1) & (CAP &- 1) }`
* U ms.swift:685 `&-` (région ; portée line : lignes 685 à 685) : `while tab[s].count != 0 && tab[s].key != k { s = (s &+ 1) & (CAP &- 1) }`
* U ms.swift:687 `&+` (région ; portée line : lignes 687 à 687) : `tab[s].count &+= 1`
* U ms.swift:688 `&+` (région ; portée line : lignes 688 à 688) : `tab[s].sum &+= UInt64(vb[i])`
* U ms.swift:695 `&+` (hors région ; portée line : lignes 695 à 695) : `ws &+= tab[s].sum &* UInt64((tab[s].key & 1023) + 1)`
* U ms.swift:695 `&*` (hors région ; portée line : lignes 695 à 695) : `ws &+= tab[s].sum &* UInt64((tab[s].key & 1023) + 1)`
* U ms.swift:730 `UnsafeMutablePointer` (hors région ; portée line : lignes 730 à 730) : `func aBuild(_ a: UnsafeMutablePointer<ANode>, _ top: inout Int32, _ d: Int, _ c: inout Int64) -> Int32 {`
* U ms.swift:732 `&+` (hors région ; portée line : lignes 732 à 732) : `top &+= 1`
* U ms.swift:734 `&+` (hors région ; portée line : lignes 734 à 734) : `c &+= 1`
* U ms.swift:736 `&-` (hors région ; portée line : lignes 736 à 736) : `let l = aBuild(a, &top, d &- 1, &c)`
* U ms.swift:737 `&-` (hors région ; portée line : lignes 737 à 737) : `let r = aBuild(a, &top, d &- 1, &c)`
* U ms.swift:743 `UnsafePointer` (hors région ; portée line : lignes 743 à 743) : `func aSum(_ a: UnsafePointer<ANode>, _ i: Int32) -> Int64 {`
* U ms.swift:746 `&+` (hors région ; portée line : lignes 746 à 746) : `return n.v &+ aSum(a, n.l) &+ aSum(a, n.r)`
* U ms.swift:746 `&+` (hors région ; portée line : lignes 746 à 746) : `return n.v &+ aSum(a, n.l) &+ aSum(a, n.r)`
* U ms.swift:751 `UnsafeMutablePointer` (hors région ; portée line : lignes 751 à 751) : `func avBuild(_ a: UnsafeMutablePointer<ANode>, _ i: Int32, _ d: Int, _ q: Int64) -> Int32 {`
* U ms.swift:752 `&+` (hors région ; portée line : lignes 752 à 752) : `a[Int(i)].v = q &+ Int64(i)`
* U ms.swift:754 `&+` (hors région ; portée line : lignes 754 à 754) : `let l = i &+ 1`
* U ms.swift:755 `&-` (hors région ; portée line : lignes 755 à 755) : `let r = avBuild(a, l, d &- 1, q)`
* U ms.swift:758 `&-` (hors région ; portée line : lignes 758 à 758) : `return avBuild(a, r, d &- 1, q)`
* U ms.swift:762 `&+` (hors région ; portée line : lignes 762 à 762) : `return i &+ 1`
* U ms.swift:769 `UnsafeMutablePointer` (région ; portée line : lignes 769 à 769) : `func aiBuild(_ a: UnsafeMutablePointer<ANode>, _ depth: Int, _ q: Int64) {`
* U ms.swift:775 `&+` (région ; portée line : lignes 775 à 775) : `top &+= 1`
* U ms.swift:776 `&+` (région ; portée line : lignes 776 à 776) : `a[Int(i)].v = q &+ Int64(i)`
* U ms.swift:782 `&-` (région ; portée line : lignes 782 à 782) : `stD[sp] = d &- 1`
* U ms.swift:783 `&+` (région ; portée line : lignes 783 à 783) : `sp &+= 1`
* U ms.swift:786 `&-` (région ; portée line : lignes 786 à 786) : `d &-= 1`
* U ms.swift:791 `&-` (région ; portée line : lignes 791 à 791) : `sp &-= 1`
* U ms.swift:798 `UnsafePointer` (région ; portée line : lignes 798 à 798) : `func aiSum(_ a: UnsafePointer<ANode>, _ root: Int32) -> Int64 {`
* U ms.swift:804 `&-` (région ; portée line : lignes 804 à 804) : `sp &-= 1`
* U ms.swift:806 `&+` (région ; portée line : lignes 806 à 806) : `s &+= n.v`
* U ms.swift:809 `&+` (région ; portée line : lignes 809 à 809) : `st[sp &+ 1] = n.l`
* U ms.swift:810 `&+` (région ; portée line : lignes 810 à 810) : `sp &+= 2`
* U ms.swift:823 `UnsafeMutablePointer` (région ; portée line : lignes 823 à 823) : `let arena = UnsafeMutablePointer<ANode>.allocate(capacity: (2 << SIZE_K8_REQ) - 1)`
* U ms.swift:845 `&-` (hors région ; portée line : lignes 845 à 845) : `lat[q] = nowNs() &- a`
* U ms.swift:878 `UnsafePointer` (région ; portée line : lignes 878 à 878) : `@inline(never) func k9Rows(_ inp: UnsafePointer<Double>, _ o: UnsafeMutablePointer<Double>, _ r0: Int, _ r1: I`
* U ms.swift:878 `UnsafeMutablePointer` (région ; portée line : lignes 878 à 878) : `@inline(never) func k9Rows(_ inp: UnsafePointer<Double>, _ o: UnsafeMutablePointer<Double>, _ r0: Int, _ r1: I`
* U ms.swift:883 `&+` (région ; portée line : lignes 883 à 883) : `while j &+ 8 <= M9 - 1 {`
* U ms.swift:884 `&-` (région ; portée line : lignes 884 à 884) : `let u = ld8(up + j), d = ld8(dn + j), l = ld8(mid + (j &- 1)), rr = ld8(mid + (j &+ 1))`
* U ms.swift:884 `&+` (région ; portée line : lignes 884 à 884) : `let u = ld8(up + j), d = ld8(dn + j), l = ld8(mid + (j &- 1)), rr = ld8(mid + (j &+ 1))`
* U ms.swift:885 `UnsafeMutableRawPointer` (région ; portée line : lignes 885 à 885) : `UnsafeMutableRawPointer(op + j).storeBytes(of: q4 * (((u + d) + l) + rr), as: SIMD8<Double>.self)`
* U ms.swift:886 `&+` (région ; portée line : lignes 886 à 886) : `j &+= 8`
* U ms.swift:889 `&-` (région ; portée line : lignes 889 à 889) : `op[j] = 0.25 * (((up[j] + dn[j]) + mid[j &- 1]) + mid[j &+ 1])`
* U ms.swift:889 `&+` (région ; portée line : lignes 889 à 889) : `op[j] = 0.25 * (((up[j] + dn[j]) + mid[j &- 1]) + mid[j &+ 1])`
* U ms.swift:890 `&+` (région ; portée line : lignes 890 à 890) : `j &+= 1`
* U ms.swift:994 `UnsafeMutableRawPointer` (hors région ; portée line : lignes 994 à 994) : `let raw = UnsafeMutableRawPointer.allocate(byteCount: 256 + CAP10 * 8, alignment: 128)`
* U ms.swift:1001 `UnsafeMutablePointer` (hors région ; portée line : lignes 1001 à 1001) : `nonisolated(unsafe) let res = UnsafeMutablePointer<UInt64>.allocate(capacity: 1)`
* U ms.swift:1008 `&+` (hors région ; portée line : lignes 1008 à 1008) : `s &+= bf[rd & (CAP10 - 1)]`
* U ms.swift:1009 `&+` (hors région ; portée line : lignes 1009 à 1009) : `rd &+= 1`
* U ms.swift:1016 `&-` (hors région ; portée line : lignes 1016 à 1016) : `while w &- rc == CAP10 { rc = ri.pointee.load(ordering: .acquiring) }`
* U ms.swift:1018 `&+` (hors région ; portée line : lignes 1018 à 1018) : `w &+= 1`

## julia

* U ms.jl:28 `@inbounds` (hors région ; portée indent : lignes 28 à 31) : `@inbounds @simd for i in eachindex(ps)   # @simd autorise la réassociation -> vectorisation`
* U ms.jl:36 `@inbounds` (région ; portée indent : lignes 36 à 38) : `@inbounds @simd for i in eachindex(vx)`
* U ms.jl:77 `@inbounds` (hors région ; portée indent : lignes 77 à 79) : `@inbounds for _ in 1:h`
* U ms.jl:134 `@inbounds` (hors région ; portée indent : lignes 134 à 137) : `@inbounds @simd for i in eachindex(v)`
* U ms.jl:156 `llvmcall` (région ; portée ir : lignes 143 à 156) : `@inline k4_block(p::Ptr{UInt8}) = Base.llvmcall(K4_IR, UInt16, Tuple{Ptr{UInt8}}, p)`
* U ms.jl:162 `pointer(` (région ; portée line : lignes 162 à 162) : `p = pointer(v)`
* U ms.jl:169 `@inbounds` (région ; portée indent : lignes 169 à 169) : `@inbounds x = v[i]`
* U ms.jl:186 `pointer(` (hors région ; portée line : lignes 186 à 186) : `p = Ptr{UInt64}(pointer(v))`
* U ms.jl:191 `unsafe_load` (hors région ; portée line : lignes 191 à 191) : `w = unsafe_load(p, (i >> 3) + 1)`
* U ms.jl:200 `@inbounds` (hors région ; portée indent : lignes 200 à 204) : `@inbounds while i < n`
* U ms.jl:228 `@inbounds` (hors région ; portée indent : lignes 228 à 230) : `@inbounds @simd for i in eachindex(a)`
* U ms.jl:285 `pointer(` (région ; portée line : lignes 285 à 285) : `GC.@preserve a b Base.llvmcall(K5_IR, Float32, Tuple{Ptr{Float32}, Ptr{Float32}, Int64}, pointer(a), pointer(b`
* U ms.jl:285 `pointer(` (région ; portée line : lignes 285 à 285) : `GC.@preserve a b Base.llvmcall(K5_IR, Float32, Tuple{Ptr{Float32}, Ptr{Float32}, Int64}, pointer(a), pointer(b`
* U ms.jl:285 `llvmcall` (région ; portée ir : lignes 236 à 285) : `GC.@preserve a b Base.llvmcall(K5_IR, Float32, Tuple{Ptr{Float32}, Ptr{Float32}, Int64}, pointer(a), pointer(b`
* U ms.jl:320 `@inbounds` (région ; portée indent : lignes 320 à 323) : `@inbounds @simd for i in lo:hi`
* U ms.jl:339 `@inbounds` (hors région ; portée indent : lignes 339 à 354) : `@inbounds for b0 in lo:B:hi`
* U ms.jl:363 `@inbounds` (hors région ; portée indent : lignes 363 à 382) : `@inbounds for b0 in lo:B:hi`
* U ms.jl:435 `llvmcall` (région ; portée ir : lignes 388 à 435) : `s = GC.@preserve sd pr q d Base.llvmcall(Q6_IR, Int64, Tuple{Ptr{Int32}, Ptr{Int32}, Ptr{UInt8}, Ptr{UInt8}, I`
* U ms.jl:436 `pointer(` (région ; portée line : lignes 436 à 436) : `pointer(sd, lo), pointer(pr, lo), pointer(d, lo), pointer(q, lo), nb)`
* U ms.jl:436 `pointer(` (région ; portée line : lignes 436 à 436) : `pointer(sd, lo), pointer(pr, lo), pointer(d, lo), pointer(q, lo), nb)`
* U ms.jl:436 `pointer(` (région ; portée line : lignes 436 à 436) : `pointer(sd, lo), pointer(pr, lo), pointer(d, lo), pointer(q, lo), nb)`
* U ms.jl:436 `pointer(` (région ; portée line : lignes 436 à 436) : `pointer(sd, lo), pointer(pr, lo), pointer(d, lo), pointer(q, lo), nb)`
* U ms.jl:772 `llvmcall` (région ; portée ir : lignes 445 à 772) : `Base.llvmcall(Q1_IR, Cvoid, Tuple{Ptr{Int32}, Ptr{Int32}, Ptr{UInt8}, Ptr{UInt8}, Ptr{UInt8}, Ptr{UInt8}, Ptr{`
* U ms.jl:773 `pointer(` (région ; portée line : lignes 773 à 773) : `pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),`
* U ms.jl:773 `pointer(` (région ; portée line : lignes 773 à 773) : `pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),`
* U ms.jl:773 `pointer(` (région ; portée line : lignes 773 à 773) : `pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),`
* U ms.jl:773 `pointer(` (région ; portée line : lignes 773 à 773) : `pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),`
* U ms.jl:773 `pointer(` (région ; portée line : lignes 773 à 773) : `pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),`
* U ms.jl:773 `pointer(` (région ; portée line : lignes 773 à 773) : `pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),`
* U ms.jl:773 `pointer(` (région ; portée line : lignes 773 à 773) : `pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),`
* U ms.jl:774 `pointer(` (région ; portée line : lignes 774 à 774) : `pointer(acc), nb)`
* U ms.jl:819 `llvmcall` (région ; portée ir : lignes 819 à 819) : `@inline prefetchw(p::Ptr) = ccall("llvm.prefetch.p0", llvmcall, Cvoid, (Ptr{Cvoid}, Int32, Int32, Int32), p, I`
* U ms.jl:842 `pointer(` (région ; portée line : lignes 842 à 842) : `ptab = pointer(tab)`
* U ms.jl:844 `@inbounds` (région ; portée indent : lignes 844 à 859) : `GC.@preserve tab @inbounds for i0 in 1:16:length(keys)`
* U ms.jl:870 `@inbounds` (région ; portée indent : lignes 870 à 878) : `@inbounds for i in eachindex(keys)`
* U ms.jl:907 `@inbounds` (hors région ; portée indent : lignes 907 à 907) : `@inbounds a[i] = ANode(c[], -1, -1); c[] += 1`
* U ms.jl:910 `@inbounds` (hors région ; portée indent : lignes 910 à 910) : `@inbounds a[i] = ANode(a[i].v, l, r)`
* U ms.jl:914 `@inbounds` (hors région ; portée indent : lignes 914 à 914) : `a_sum(a::Vector{ANode}, i::Int32) = i < 0 ? 0 : (@inbounds n = a[i]; n.v + a_sum(a, n.l) + a_sum(a, n.r))`
* U ms.jl:923 `@inbounds` (hors région ; portée indent : lignes 923 à 923) : `@inbounds a[i] = ANode(c[], -1, -1); c[] += 1`
* U ms.jl:926 `@inbounds` (hors région ; portée indent : lignes 926 à 926) : `@inbounds a[i] = ANode(a[i].v, l, r)`
* U ms.jl:937 `@inbounds` (hors région ; portée indent : lignes 937 à 937) : `@inbounds a[i] = ANode(q + (i - 1), l, r)`
* U ms.jl:940 `@inbounds` (hors région ; portée indent : lignes 940 à 940) : `@inbounds a[i] = ANode(q + (i - 1), Int32(-1), Int32(-1))`
* U ms.jl:949 `@inbounds` (région ; portée indent : lignes 949 à 963) : `@inbounds while true`
* U ms.jl:967 `@inbounds` (région ; portée indent : lignes 967 à 973) : `@inbounds while sp > 0`
* U ms.jl:1090 `pointer(` (région ; portée line : lignes 1090 à 1090) : `GC.@preserve a b Base.llvmcall(K9_IR, Cvoid, Tuple{Ptr{Float64}, Ptr{Float64}, Int64, Int64}, pointer(a), poin`
* U ms.jl:1090 `pointer(` (région ; portée line : lignes 1090 à 1090) : `GC.@preserve a b Base.llvmcall(K9_IR, Cvoid, Tuple{Ptr{Float64}, Ptr{Float64}, Int64, Int64}, pointer(a), poin`
* U ms.jl:1090 `llvmcall` (région ; portée ir : lignes 1025 à 1090) : `GC.@preserve a b Base.llvmcall(K9_IR, Cvoid, Tuple{Ptr{Float64}, Ptr{Float64}, Int64, Int64}, pointer(a), poin`
* U ms.jl:1098 `@inbounds` (région ; portée indent : lignes 1098 à 1102) : `@inbounds for j in c0:c1`
* U ms.jl:1176 `@inbounds` (hors région ; portée indent : lignes 1176 à 1176) : `@inbounds buf[(w&(CAP10-1))+1] = x`
* U ms.jl:1189 `@inbounds` (hors région ; portée indent : lignes 1189 à 1189) : `@inbounds s += buf[(rd&(CAP10-1))+1]`

## mojo

* U ms.mojo:7 `unsafe_alloc` (hors région ; portée line : lignes 7 à 7) : `from std.memory.alloc import unsafe_alloc`
* U ms.mojo:8 `unsafe_memcpy` (hors région ; portée line : lignes 8 à 8) : `from std.memory import unsafe_memcpy, unsafe_memset_zero, OwnedPointer`
* U ms.mojo:8 `unsafe_memset_zero` (hors région ; portée line : lignes 8 à 8) : `from std.memory import unsafe_memcpy, unsafe_memset_zero, OwnedPointer`
* U ms.mojo:19 `MutUntrackedOrigin` (hors région ; portée line : lignes 19 à 19) : `var p: Pointer[Scalar[Self.dtype], MutUntrackedOrigin]`
* U ms.mojo:21 `MutUntrackedOrigin` (hors région ; portée line : lignes 21 à 21) : `def __init__(out self, p: Pointer[Scalar[Self.dtype], MutUntrackedOrigin], n: Int):`
* U ms.mojo:26 `unsafe_offset` (hors région ; portée line : lignes 26 à 26) : `return self.p[unsafe_offset=i]`
* U ms.mojo:34 `unsafe_alloc` (hors région ; portée line : lignes 34 à 34) : `var p = unsafe_alloc[Scalar[dtype]](n + 64, alignment=64)  # tampon aligné sur 64 octets`
* U ms.mojo:35 `unsafe_memcpy` (hors région ; portée line : lignes 35 à 35) : `unsafe_memcpy(dest=p.unsafe_bitcast[UInt8](), src=b.unsafe_ptr(), count=nb)`
* U ms.mojo:35 `unsafe_bitcast` (hors région ; portée line : lignes 35 à 35) : `unsafe_memcpy(dest=p.unsafe_bitcast[UInt8](), src=b.unsafe_ptr(), count=nb)`
* U ms.mojo:35 `unsafe_ptr` (hors région ; portée line : lignes 35 à 35) : `unsafe_memcpy(dest=p.unsafe_bitcast[UInt8](), src=b.unsafe_ptr(), count=nb)`
* U ms.mojo:76 `unsafe_ptr` (hors région ; portée line : lignes 76 à 76) : `var base = ps.unsafe_ptr()`
* U ms.mojo:89 `unsafe_load` (région ; portée line : lignes 89 à 89) : `var x = vx.p.unsafe_load[width=16, alignment=64](i)`
* U ms.mojo:90 `unsafe_load` (région ; portée line : lignes 90 à 90) : `var y = vy.p.unsafe_load[width=16, alignment=64](i)`
* U ms.mojo:91 `unsafe_load` (région ; portée line : lignes 91 à 91) : `var z = vz.p.unsafe_load[width=16, alignment=64](i)`
* U ms.mojo:92 `unsafe_load` (région ; portée line : lignes 92 à 92) : `var w = m.p.unsafe_load[width=16, alignment=64](i)`
* U ms.mojo:129 `unsafe_alloc` (région ; portée line : lignes 129 à 129) : `var c = unsafe_alloc[Float32](N1, alignment=64)`
* U ms.mojo:131 `unsafe_offset` (région ; portée line : lignes 131 à 131) : `c[unsafe_offset=i] = raw[16 * i + k]`
* U ms.mojo:174 `MutUntrackedOrigin` (région ; portée line : lignes 174 à 174) : `__async def k3_worker(c: Pointer[UInt64, MutUntrackedOrigin], rmw: Bool) -> Int:`
* U ms.mojo:187 `unsafe_alloc` (région ; portée line : lignes 187 à 187) : `var mem = unsafe_alloc[UInt64](128, alignment=128)`
* U ms.mojo:190 `unsafe_offset` (hors région ; portée line : lignes 190 à 190) : `mem[unsafe_offset=16 + t * stride] = 0`
* U ms.mojo:200 `unsafe_offset` (hors région ; portée line : lignes 200 à 200) : `s += mem[unsafe_offset=16 + t * stride]`
* U ms.mojo:226 `unsafe_ptr` (région ; portée line : lignes 226 à 226) : `var p = v.unsafe_ptr()`
* U ms.mojo:231 `unsafe_load` (région ; portée line : lignes 231 à 231) : `var x = p.unsafe_load[width=W](i)`
* U ms.mojo:236 `unsafe_offset` (région ; portée line : lignes 236 à 236) : `var b = p[unsafe_offset=i]`
* U ms.mojo:251 `unsafe_ptr` (hors région ; portée line : lignes 251 à 251) : `var p = v.unsafe_ptr()`
* U ms.mojo:259 `unsafe_bitcast` (hors région ; portée line : lignes 259 à 259) : `var w = (p + i).unsafe_bitcast[UInt64]().unsafe_load[alignment=1](0)`
* U ms.mojo:259 `unsafe_load` (hors région ; portée line : lignes 259 à 259) : `var w = (p + i).unsafe_bitcast[UInt64]().unsafe_load[alignment=1](0)`
* U ms.mojo:266 `unsafe_offset` (hors région ; portée line : lignes 266 à 266) : `var b = p[unsafe_offset=i]`
* U ms.mojo:302 `unsafe_load` (région ; portée line : lignes 302 à 302) : `s0 = a.p.unsafe_load[width=16, alignment=64](i).fma(b.p.unsafe_load[width=16, alignment=64](i), s0)`
* U ms.mojo:302 `unsafe_load` (région ; portée line : lignes 302 à 302) : `s0 = a.p.unsafe_load[width=16, alignment=64](i).fma(b.p.unsafe_load[width=16, alignment=64](i), s0)`
* U ms.mojo:303 `unsafe_load` (région ; portée line : lignes 303 à 303) : `s1 = a.p.unsafe_load[width=16, alignment=64](i + 16).fma(b.p.unsafe_load[width=16, alignment=64](i + 16), s1)`
* U ms.mojo:303 `unsafe_load` (région ; portée line : lignes 303 à 303) : `s1 = a.p.unsafe_load[width=16, alignment=64](i + 16).fma(b.p.unsafe_load[width=16, alignment=64](i + 16), s1)`
* U ms.mojo:304 `unsafe_load` (région ; portée line : lignes 304 à 304) : `s2 = a.p.unsafe_load[width=16, alignment=64](i + 32).fma(b.p.unsafe_load[width=16, alignment=64](i + 32), s2)`
* U ms.mojo:304 `unsafe_load` (région ; portée line : lignes 304 à 304) : `s2 = a.p.unsafe_load[width=16, alignment=64](i + 32).fma(b.p.unsafe_load[width=16, alignment=64](i + 32), s2)`
* U ms.mojo:305 `unsafe_load` (région ; portée line : lignes 305 à 305) : `s3 = a.p.unsafe_load[width=16, alignment=64](i + 48).fma(b.p.unsafe_load[width=16, alignment=64](i + 48), s3)`
* U ms.mojo:305 `unsafe_load` (région ; portée line : lignes 305 à 305) : `s3 = a.p.unsafe_load[width=16, alignment=64](i + 48).fma(b.p.unsafe_load[width=16, alignment=64](i + 48), s3)`
* U ms.mojo:347 `unsafe_load` (région ; portée line : lignes 347 à 347) : `return c.p.unsafe_load[width=16, alignment=16](i).cast[DType.int32]()`
* U ms.mojo:354 `unsafe_load` (région ; portée line : lignes 354 à 354) : `var sd = c.sd.p.unsafe_load[width=16, alignment=64](i)`
* U ms.mojo:358 `unsafe_load` (région ; portée line : lignes 358 à 358) : `acc += m.select(c.pr.p.unsafe_load[width=16, alignment=64](i) * d, I16(0)).cast[DType.int64]()`
* U ms.mojo:388 `unsafe_load` (hors région ; portée line : lignes 388 à 388) : `var p_ = c.sd.p.unsafe_load[width=16, alignment=64](i).le(I16(10471))`
* U ms.mojo:393 `unsafe_load` (hors région ; portée line : lignes 393 à 393) : `var vp = c.pr.p.unsafe_load[width=16, alignment=64](i)`
* U ms.mojo:428 `unsafe_load` (région ; portée line : lignes 428 à 428) : `var p_ = c.sd.p.unsafe_load[width=16, alignment=64](i).le(I16(10471))`
* U ms.mojo:433 `unsafe_load` (région ; portée line : lignes 433 à 433) : `var vp = c.pr.p.unsafe_load[width=16, alignment=64](i)`
* U ms.mojo:546 `unsafe_alloc` (région ; portée line : lignes 546 à 546) : `var tab = unsafe_alloc[Slot](CAP, alignment=64)`
* U ms.mojo:547 `unsafe_memset_zero` (région ; portée line : lignes 547 à 547) : `unsafe_memset_zero(tab.unsafe_bitcast[UInt8](), CAP * size_of[Slot]())`
* U ms.mojo:547 `unsafe_bitcast` (région ; portée line : lignes 547 à 547) : `unsafe_memset_zero(tab.unsafe_bitcast[UInt8](), CAP * size_of[Slot]())`
* U ms.mojo:553 `unsafe_bitcast` (région ; portée line : lignes 553 à 553) : `prefetch[PrefetchOptions().for_write().high_locality()]((tab + Int(h[b])).unsafe_bitcast[UInt8]())`
* U ms.mojo:557 `unsafe_offset` (région ; portée line : lignes 557 à 557) : `while tab[unsafe_offset=s].count != 0 and tab[unsafe_offset=s].key != k:`
* U ms.mojo:557 `unsafe_offset` (région ; portée line : lignes 557 à 557) : `while tab[unsafe_offset=s].count != 0 and tab[unsafe_offset=s].key != k:`
* U ms.mojo:559 `unsafe_offset` (région ; portée line : lignes 559 à 559) : `tab[unsafe_offset=s].key = k`
* U ms.mojo:560 `unsafe_offset` (région ; portée line : lignes 560 à 560) : `tab[unsafe_offset=s].count += 1`
* U ms.mojo:561 `unsafe_offset` (région ; portée line : lignes 561 à 561) : `tab[unsafe_offset=s].sum += UInt64(vals[i + b])`
* U ms.mojo:565 `unsafe_offset` (hors région ; portée line : lignes 565 à 565) : `if tab[unsafe_offset=s].count != 0:`
* U ms.mojo:567 `unsafe_offset` (hors région ; portée line : lignes 567 à 567) : `ws += tab[unsafe_offset=s].sum * UInt64((tab[unsafe_offset=s].key & 1023) + 1)`
* U ms.mojo:567 `unsafe_offset` (hors région ; portée line : lignes 567 à 567) : `ws += tab[unsafe_offset=s].sum * UInt64((tab[unsafe_offset=s].key & 1023) + 1)`
* U ms.mojo:578 `MutUntrackedOrigin` (région ; portée line : lignes 578 à 578) : `var l: Pointer[Node, MutUntrackedOrigin]`
* U ms.mojo:579 `MutUntrackedOrigin` (région ; portée line : lignes 579 à 579) : `var r: Pointer[Node, MutUntrackedOrigin]`
* U ms.mojo:580 `MutUntrackedOrigin` (région ; portée line : lignes 580 à 580) : `def __init__(out self, v: Int64, leaf: Bool, l: Pointer[Node, MutUntrackedOrigin], r: Pointer[Node, MutUntrack`
* U ms.mojo:580 `MutUntrackedOrigin` (région ; portée line : lignes 580 à 580) : `def __init__(out self, v: Int64, leaf: Bool, l: Pointer[Node, MutUntrackedOrigin], r: Pointer[Node, MutUntrack`
* U ms.mojo:586 `MutUntrackedOrigin` (région ; portée line : lignes 586 à 586) : `def t_build(d: Int, mut c: Int64) -> Pointer[Node, MutUntrackedOrigin]:`
* U ms.mojo:587 `unsafe_alloc` (région ; portée line : lignes 587 à 587) : `var n = unsafe_alloc[Node](1)`
* U ms.mojo:593 `unsafe_write` (région ; portée line : lignes 593 à 593) : `n.unsafe_write(Node(v, False, l, r))`
* U ms.mojo:595 `unsafe_write` (région ; portée line : lignes 595 à 595) : `n.unsafe_write(Node(v, True, n, n))`
* U ms.mojo:598 `MutUntrackedOrigin` (région ; portée line : lignes 598 à 598) : `def t_sum(n: Pointer[Node, MutUntrackedOrigin]) -> Int64:`
* U ms.mojo:603 `MutUntrackedOrigin` (région ; portée line : lignes 603 à 603) : `def t_free(n: Pointer[Node, MutUntrackedOrigin]):`
* U ms.mojo:615 `MutUntrackedOrigin` (hors région ; portée line : lignes 615 à 615) : `def a_build(a: Pointer[ANode, MutUntrackedOrigin], mut top: Int32, d: Int, mut c: Int64) -> Int32:`
* U ms.mojo:618 `unsafe_offset` (hors région ; portée line : lignes 618 à 618) : `a[unsafe_offset=Int(i)] = ANode(c, -1, -1)`
* U ms.mojo:622 `unsafe_offset` (hors région ; portée line : lignes 622 à 622) : `a[unsafe_offset=Int(i)].l = l`
* U ms.mojo:623 `unsafe_offset` (hors région ; portée line : lignes 623 à 623) : `a[unsafe_offset=Int(i)].r = a_build(a, top, d - 1, c)`
* U ms.mojo:626 `MutUntrackedOrigin` (région ; portée line : lignes 626 à 626) : `def a_sum(a: Pointer[ANode, MutUntrackedOrigin], i: Int32) -> Int64:`
* U ms.mojo:629 `unsafe_offset` (région ; portée line : lignes 629 à 629) : `var n = a[unsafe_offset=Int(i)]`
* U ms.mojo:635 `MutUntrackedOrigin` (région ; portée line : lignes 635 à 635) : `def av_build(a: Pointer[ANode, MutUntrackedOrigin], i: Int32, d: Int, q: Int64) -> Int32:`
* U ms.mojo:636 `unsafe_offset` (région ; portée line : lignes 636 à 636) : `a[unsafe_offset=Int(i)] = ANode(q + Int64(i), -1, -1)`
* U ms.mojo:640 `unsafe_offset` (région ; portée line : lignes 640 à 640) : `a[unsafe_offset=Int(i)].l = l`
* U ms.mojo:641 `unsafe_offset` (région ; portée line : lignes 641 à 641) : `a[unsafe_offset=Int(i)].r = r`
* U ms.mojo:650 `MutUntrackedOrigin` (hors région ; portée line : lignes 650 à 650) : `def ai_build(a: Pointer[ANode, MutUntrackedOrigin], depth: Int, q: Int64):`
* U ms.mojo:661 `unsafe_offset` (hors région ; portée line : lignes 661 à 661) : `a[unsafe_offset=Int(i)] = ANode(q + Int64(i), -1, -1)`
* U ms.mojo:664 `unsafe_offset` (hors région ; portée line : lignes 664 à 664) : `a[unsafe_offset=Int(parent)].r = i`
* U ms.mojo:666 `unsafe_offset` (hors région ; portée line : lignes 666 à 666) : `a[unsafe_offset=Int(parent)].l = i`
* U ms.mojo:682 `MutUntrackedOrigin` (hors région ; portée line : lignes 682 à 682) : `def ai_sum(a: Pointer[ANode, MutUntrackedOrigin], root: Int32) -> Int64:`
* U ms.mojo:689 `unsafe_offset` (hors région ; portée line : lignes 689 à 689) : `var n = a[unsafe_offset=Int(st[sp])]`
* U ms.mojo:706 `unsafe_alloc` (région ; portée line : lignes 706 à 706) : `var arena = unsafe_alloc[ANode]((2 << K8_REQ) - 1, alignment=64)`
* U ms.mojo:755 `MutUntrackedOrigin` (région ; portée line : lignes 755 à 755) : `def k9_rows(a: Pointer[Float64, MutUntrackedOrigin], b: Pointer[Float64, MutUntrackedOrigin], r0: Int, r1: Int`
* U ms.mojo:755 `MutUntrackedOrigin` (région ; portée line : lignes 755 à 755) : `def k9_rows(a: Pointer[Float64, MutUntrackedOrigin], b: Pointer[Float64, MutUntrackedOrigin], r0: Int, r1: Int`
* U ms.mojo:764 `unsafe_load` (région ; portée line : lignes 764 à 764) : `var x = V(0.25) * (((up.unsafe_load[width=8, alignment=8](j) + dn.unsafe_load[width=8, alignment=8](j)) + mid.`
* U ms.mojo:764 `unsafe_load` (région ; portée line : lignes 764 à 764) : `var x = V(0.25) * (((up.unsafe_load[width=8, alignment=8](j) + dn.unsafe_load[width=8, alignment=8](j)) + mid.`
* U ms.mojo:764 `unsafe_load` (région ; portée line : lignes 764 à 764) : `var x = V(0.25) * (((up.unsafe_load[width=8, alignment=8](j) + dn.unsafe_load[width=8, alignment=8](j)) + mid.`
* U ms.mojo:764 `unsafe_load` (région ; portée line : lignes 764 à 764) : `var x = V(0.25) * (((up.unsafe_load[width=8, alignment=8](j) + dn.unsafe_load[width=8, alignment=8](j)) + mid.`
* U ms.mojo:765 `unsafe_store` (région ; portée line : lignes 765 à 765) : `o.unsafe_store[alignment=8](j, x)`
* U ms.mojo:768 `unsafe_offset` (région ; portée line : lignes 768 à 768) : `o[unsafe_offset=j] = 0.25 * (((up[unsafe_offset=j] + dn[unsafe_offset=j]) + mid[unsafe_offset=j - 1]) + mid[un`
* U ms.mojo:768 `unsafe_offset` (région ; portée line : lignes 768 à 768) : `o[unsafe_offset=j] = 0.25 * (((up[unsafe_offset=j] + dn[unsafe_offset=j]) + mid[unsafe_offset=j - 1]) + mid[un`
* U ms.mojo:768 `unsafe_offset` (région ; portée line : lignes 768 à 768) : `o[unsafe_offset=j] = 0.25 * (((up[unsafe_offset=j] + dn[unsafe_offset=j]) + mid[unsafe_offset=j - 1]) + mid[un`
* U ms.mojo:768 `unsafe_offset` (région ; portée line : lignes 768 à 768) : `o[unsafe_offset=j] = 0.25 * (((up[unsafe_offset=j] + dn[unsafe_offset=j]) + mid[unsafe_offset=j - 1]) + mid[un`
* U ms.mojo:768 `unsafe_offset` (région ; portée line : lignes 768 à 768) : `o[unsafe_offset=j] = 0.25 * (((up[unsafe_offset=j] + dn[unsafe_offset=j]) + mid[unsafe_offset=j - 1]) + mid[un`
* U ms.mojo:771 `MutUntrackedOrigin` (région ; portée line : lignes 771 à 771) : `__async def k9_worker(a: Pointer[Float64, MutUntrackedOrigin], b: Pointer[Float64, MutUntrackedOrigin], r0: In`
* U ms.mojo:771 `MutUntrackedOrigin` (région ; portée line : lignes 771 à 771) : `__async def k9_worker(a: Pointer[Float64, MutUntrackedOrigin], b: Pointer[Float64, MutUntrackedOrigin], r0: In`
* U ms.mojo:828 `unsafe_alloc` (région ; portée line : lignes 828 à 828) : `var a = unsafe_alloc[Float64](M9 * M9, alignment=64)`
* U ms.mojo:829 `unsafe_alloc` (région ; portée line : lignes 829 à 829) : `var b = unsafe_alloc[Float64](M9 * M9, alignment=64)`
* U ms.mojo:834 `unsafe_offset` (hors région ; portée line : lignes 834 à 834) : `a[unsafe_offset=k] = k9_init(k // M9, k % M9)`
* U ms.mojo:835 `unsafe_offset` (hors région ; portée line : lignes 835 à 835) : `b[unsafe_offset=k] = a[unsafe_offset=k]`
* U ms.mojo:835 `unsafe_offset` (hors région ; portée line : lignes 835 à 835) : `b[unsafe_offset=k] = a[unsafe_offset=k]`
* U ms.mojo:851 `unsafe_offset` (hors région ; portée line : lignes 851 à 851) : `s += a[unsafe_offset=k]`
* U ms.mojo:867 `MutUntrackedOrigin` (hors région ; portée line : lignes 867 à 867) : `__async def lq_prod(q: Pointer[LockedQueue, MutUntrackedOrigin]) -> UInt64:`
* U ms.mojo:877 `MutUntrackedOrigin` (hors région ; portée line : lignes 877 à 877) : `__async def lq_cons(q: Pointer[LockedQueue, MutUntrackedOrigin]) -> UInt64:`
* U ms.mojo:891 `MutUntrackedOrigin` (hors région ; portée line : lignes 891 à 891) : `__async def spsc_prod(ctl: Pointer[UInt64, MutUntrackedOrigin], buf: Pointer[UInt64, MutUntrackedOrigin]) -> U`
* U ms.mojo:891 `MutUntrackedOrigin` (hors région ; portée line : lignes 891 à 891) : `__async def spsc_prod(ctl: Pointer[UInt64, MutUntrackedOrigin], buf: Pointer[UInt64, MutUntrackedOrigin]) -> U`
* U ms.mojo:897 `unsafe_offset` (hors région ; portée line : lignes 897 à 897) : `buf[unsafe_offset=Int(w & (CAP10 - 1))] = UInt64(x)`
* U ms.mojo:902 `MutUntrackedOrigin` (hors région ; portée line : lignes 902 à 902) : `__async def spsc_cons(ctl: Pointer[UInt64, MutUntrackedOrigin], buf: Pointer[UInt64, MutUntrackedOrigin]) -> U`
* U ms.mojo:902 `MutUntrackedOrigin` (hors région ; portée line : lignes 902 à 902) : `__async def spsc_cons(ctl: Pointer[UInt64, MutUntrackedOrigin], buf: Pointer[UInt64, MutUntrackedOrigin]) -> U`
* U ms.mojo:909 `unsafe_offset` (hors région ; portée line : lignes 909 à 909) : `s += buf[unsafe_offset=Int(rd & (CAP10 - 1))]`
* U ms.mojo:919 `unsafe_alloc` (hors région ; portée line : lignes 919 à 919) : `var q = unsafe_alloc[LockedQueue](1, alignment=128)`
* U ms.mojo:920 `unsafe_write` (hors région ; portée line : lignes 920 à 920) : `q.unsafe_write(LockedQueue())`
* U ms.mojo:925 `unsafe_deinit_pointee` (hors région ; portée line : lignes 925 à 925) : `q.unsafe_deinit_pointee()`
* U ms.mojo:928 `unsafe_alloc` (hors région ; portée line : lignes 928 à 928) : `var ctl = unsafe_alloc[UInt64](64, alignment=128)  # écriture @16, lecture @32 (128 o d'écart)`
* U ms.mojo:929 `unsafe_offset` (hors région ; portée line : lignes 929 à 929) : `ctl[unsafe_offset=16] = 0`
* U ms.mojo:930 `unsafe_offset` (hors région ; portée line : lignes 930 à 930) : `ctl[unsafe_offset=32] = 0`
* U ms.mojo:931 `unsafe_alloc` (hors région ; portée line : lignes 931 à 931) : `var buf = unsafe_alloc[UInt64](CAP10, alignment=64)`

## csharp

* X Program.cs:9 `System.Runtime.Intrinsics.X86` (hors région) : `using System.Runtime.Intrinsics.X86;`
* U Program.cs:11 `unsafe` (hors région ; modificateur de classe : pas de portée) : `static unsafe class Ms`
* U Program.cs:16 `MemoryMarshal.` (hors région ; portée line : lignes 16 à 16) : `static T[] Load<T>(string n) where T : unmanaged => MemoryMarshal.Cast<byte, T>(LoadBytes(n)).ToArray();`
* U Program.cs:18 `    static T* LoadAligned<T>(` (région ; portée brace : lignes 18 à 25) : `static T* LoadAligned<T>(string n, out int count) where T : unmanaged`
* U Program.cs:18 `T*` (région ; portée line : lignes 18 à 18) : `static T* LoadAligned<T>(string n, out int count) where T : unmanaged`
* U Program.cs:21 `void*` (région ; portée line : lignes 21 à 21) : `void* p = NativeMemory.AlignedAlloc((nuint)b.Length, 64);`
* U Program.cs:24 `T*` (région ; portée line : lignes 24 à 24) : `return (T*)p;`
* U Program.cs:63 `MemoryMarshal.` (hors région ; portée line : lignes 63 à 63) : `ref PS b = ref MemoryMarshal.GetArrayDataReference(ps);`
* U Program.cs:66 `Unsafe.` (hors région ; portée line : lignes 66 à 66) : `ref PS p0 = ref Unsafe.Add(ref b, i); ref PS p1 = ref Unsafe.Add(ref b, i + 1);`
* U Program.cs:66 `Unsafe.` (hors région ; portée line : lignes 66 à 66) : `ref PS p0 = ref Unsafe.Add(ref b, i); ref PS p1 = ref Unsafe.Add(ref b, i + 1);`
* U Program.cs:67 `Unsafe.` (hors région ; portée line : lignes 67 à 67) : `ref PS p2 = ref Unsafe.Add(ref b, i + 2); ref PS p3 = ref Unsafe.Add(ref b, i + 3);`
* U Program.cs:67 `Unsafe.` (hors région ; portée line : lignes 67 à 67) : `ref PS p2 = ref Unsafe.Add(ref b, i + 2); ref PS p3 = ref Unsafe.Add(ref b, i + 3);`
* U Program.cs:76 `    static double K1SoA(float* vx, float* vy, float* vz, float*` (région ; portée brace : lignes 76 à 90) : `static double K1SoA(float* vx, float* vy, float* vz, float* m, int n)`
* U Program.cs:76 `float*` (région ; portée line : lignes 76 à 76) : `static double K1SoA(float* vx, float* vy, float* vz, float* m, int n)`
* U Program.cs:76 `float*` (région ; portée line : lignes 76 à 76) : `static double K1SoA(float* vx, float* vy, float* vz, float* m, int n)`
* U Program.cs:76 `float*` (région ; portée line : lignes 76 à 76) : `static double K1SoA(float* vx, float* vy, float* vz, float* m, int n)`
* U Program.cs:76 `float*` (région ; portée line : lignes 76 à 76) : `static double K1SoA(float* vx, float* vy, float* vz, float* m, int n)`
* U Program.cs:109 `MemoryMarshal.` (hors région ; portée line : lignes 109 à 109) : `PS[] ps = MemoryMarshal.Cast<float, PS>(raw).ToArray();`
* U Program.cs:115 `float*` (région ; portée line : lignes 115 à 115) : `var c = new float*[16];`
* U Program.cs:118 `float*` (région ; portée line : lignes 118 à 118) : `c[k] = (float*)NativeMemory.AlignedAlloc(N1 * 4, 64);`
* U Program.cs:157 `MemoryMarshal.` (hors région ; portée line : lignes 157 à 157) : `ref uint b = ref MemoryMarshal.GetArrayDataReference(a);`
* U Program.cs:159 `Unsafe.` (hors région ; portée line : lignes 159 à 159) : `for (int k = 0; k < h; k++) i = Unsafe.Add(ref b, (nint)i);`
* U Program.cs:208 `MemoryMarshal.` (région ; portée line : lignes 208 à 208) : `ref byte b = ref MemoryMarshal.GetArrayDataReference(v);`
* X Program.cs:217 `Avx512BW.` (région) : `a0 += Avx512BW.SumAbsoluteDifferences(x0 & m0, Vector512<byte>.Zero).AsUInt64();`
* X Program.cs:218 `Avx512BW.` (région) : `a1 += Avx512BW.SumAbsoluteDifferences(x1 & m1, Vector512<byte>.Zero).AsUInt64();`
* U Program.cs:233 `MemoryMarshal.` (hors région ; portée line : lignes 233 à 233) : `ref byte b = ref MemoryMarshal.GetArrayDataReference(v);`
* U Program.cs:242 `Unsafe.` (hors région ; portée line : lignes 242 à 242) : `ulong w = Unsafe.ReadUnaligned<ulong>(ref Unsafe.Add(ref b, i));`
* U Program.cs:242 `Unsafe.` (hors région ; portée line : lignes 242 à 242) : `ulong w = Unsafe.ReadUnaligned<ulong>(ref Unsafe.Add(ref b, i));`
* U Program.cs:265 `    static float K5Tuned(float* a, float*` (région ; portée brace : lignes 265 à 276) : `static float K5Tuned(float* a, float* b, int n)`
* U Program.cs:265 `float*` (région ; portée line : lignes 265 à 265) : `static float K5Tuned(float* a, float* b, int n)`
* U Program.cs:265 `float*` (région ; portée line : lignes 265 à 265) : `static float K5Tuned(float* a, float* b, int n)`
* U Program.cs:280 `float*` (région ; portée line : lignes 280 à 280) : `float* pa = LoadAligned<float>("k5_a.f32", out int n), pb = LoadAligned<float>("k5_b.f32", out _);`
* U Program.cs:301 `MemoryMarshal.` (région ; portée line : lignes 301 à 301) : `static Vector512<int> Ld8(byte[] a, int i) => Avx512F.ConvertToVector512Int32(Vector128.LoadUnsafe(ref MemoryM`
* X Program.cs:301 `Avx512F.` (région) : `static Vector512<int> Ld8(byte[] a, int i) => Avx512F.ConvertToVector512Int32(Vector128.LoadUnsafe(ref MemoryM`
* U Program.cs:302 `MemoryMarshal.` (région ; portée line : lignes 302 à 302) : `static Vector512<int> Ld32(int[] a, int i) => Vector512.LoadUnsafe(ref MemoryMarshal.GetArrayDataReference(a),`
* U Program.cs:338 `stackalloc` (région ; portée line : lignes 338 à 338) : `Span<Vector512<int>> aq = stackalloc Vector512<int>[6], ap = stackalloc Vector512<int>[6], adp = stackalloc Ve`
* U Program.cs:338 `stackalloc` (région ; portée line : lignes 338 à 338) : `Span<Vector512<int>> aq = stackalloc Vector512<int>[6], ap = stackalloc Vector512<int>[6], adp = stackalloc Ve`
* U Program.cs:338 `stackalloc` (région ; portée line : lignes 338 à 338) : `Span<Vector512<int>> aq = stackalloc Vector512<int>[6], ap = stackalloc Vector512<int>[6], adp = stackalloc Ve`
* U Program.cs:339 `stackalloc` (région ; portée line : lignes 339 à 339) : `Span<Vector512<long>> ace = stackalloc Vector512<long>[6], aco = stackalloc Vector512<long>[6];`
* U Program.cs:339 `stackalloc` (région ; portée line : lignes 339 à 339) : `Span<Vector512<long>> ace = stackalloc Vector512<long>[6], aco = stackalloc Vector512<long>[6];`
* U Program.cs:340 `stackalloc` (région ; portée line : lignes 340 à 340) : `Span<long> cnt = stackalloc long[6];`
* X Program.cs:352 `Avx512F.` (région) : `var che = Avx512F.Multiply(vdp, vt);                                                   // lignes paires (vpmul`
* X Program.cs:353 `Avx512F.` (région) : `var cho = Avx512F.Multiply(Vector512.ShiftRightLogical(vdp.AsInt64(), 32).AsInt32(), Vector512.ShiftRightLogic`
* U Program.cs:452 `stackalloc` (région ; portée line : lignes 452 à 452) : `Span<uint> h = stackalloc uint[B];`
* U Program.cs:453 `fixed (` (région ; portée brace : lignes 453 à 465) : `fixed (Slot* tp = tab)`
* U Program.cs:453 `Slot*` (région ; portée line : lignes 453 à 453) : `fixed (Slot* tp = tab)`
* X Program.cs:457 `Sse.` (région) : `for (int b = 0; b < B; b++) { h[b] = (keys[i + b] * 0x9E3779B1u) >> (32 - LOG); Sse.Prefetch0(tp + h[b]); }`
* U Program.cs:509 `stackalloc` (région ; portée line : lignes 509 à 509) : `Span<int> sp = stackalloc int[64], sd8 = stackalloc int[64];`
* U Program.cs:509 `stackalloc` (région ; portée line : lignes 509 à 509) : `Span<int> sp = stackalloc int[64], sd8 = stackalloc int[64];`
* U Program.cs:530 `stackalloc` (région ; portée line : lignes 530 à 530) : `Span<int> st = stackalloc int[64];`
* U Program.cs:589 `    static void K9Rows(double* inp, double*` (région ; portée brace : lignes 589 à 600) : `static void K9Rows(double* inp, double* outp, int r0, int r1)`
* U Program.cs:589 `double*` (région ; portée line : lignes 589 à 589) : `static void K9Rows(double* inp, double* outp, int r0, int r1)`
* U Program.cs:589 `double*` (région ; portée line : lignes 589 à 589) : `static void K9Rows(double* inp, double* outp, int r0, int r1)`
* U Program.cs:594 `double*` (région ; portée line : lignes 594 à 594) : `double* up = inp + (i - 1) * M9, mid = inp + i * M9, dn = inp + (i + 1) * M9, o = outp + i * M9;`
* U Program.cs:605 `double*` (région ; portée line : lignes 605 à 605) : `double* ga = null, gb = null;`
* U Program.cs:607 `double*` (région ; portée line : lignes 607 à 607) : `else { ga = (double*)NativeMemory.AlignedAlloc(M9 * M9 * 8, 64); gb = (double*)NativeMemory.AlignedAlloc(M9 * `
* U Program.cs:607 `double*` (région ; portée line : lignes 607 à 607) : `else { ga = (double*)NativeMemory.AlignedAlloc(M9 * M9 * 8, 64); gb = (double*)NativeMemory.AlignedAlloc(M9 * `
* U Program.cs:622 `double*` (hors région ; portée line : lignes 622 à 622) : `double* a = ga, b = gb;`
* U Program.cs:632 `double*` (région ; portée line : lignes 632 à 632) : `double* fa = a, fb = b;`
* U Program.cs:637 `double*` (hors région ; portée line : lignes 637 à 637) : `double* fa = a, fb = b;`
* U Program.cs:647 `double*` (hors région ; portée line : lignes 647 à 647) : `double* tmp = a; a = b; b = tmp;`

## fpc

* U ms.pas:153 `^T` (hors région ; portée line : lignes 153 à 153) : `PParticle = ^TParticle;`
* U ms.pas:170 `q^` (hors région ; portée line : lignes 170 à 170) : `Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));`
* U ms.pas:170 `q^` (hors région ; portée line : lignes 170 à 170) : `Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));`
* U ms.pas:170 `q^` (hors région ; portée line : lignes 170 à 170) : `Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));`
* U ms.pas:170 `q^` (hors région ; portée line : lignes 170 à 170) : `Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));`
* U ms.pas:170 `q^` (hors région ; portée line : lignes 170 à 170) : `Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));`
* U ms.pas:170 `q^` (hors région ; portée line : lignes 170 à 170) : `Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));`
* U ms.pas:170 `q^` (hors région ; portée line : lignes 170 à 170) : `Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));`
* U ms.pas:290 `Move(` (hors région ; portée line : lignes 290 à 290) : `Move(ps[0], a^, N1 * SizeOf(TParticle));`
* U ms.pas:290 `a^` (hors région ; portée line : lignes 290 à 290) : `Move(ps[0], a^, N1 * SizeOf(TParticle));`
* U ms.pas:362 `^T` (région ; portée line : lignes 362 à 362) : `PK3Arg = ^TK3Arg;`
* U ms.pas:374 `c^` (région ; portée line : lignes 374 à 374) : `InterLockedIncrement64(c^)`
* U ms.pas:377 `c^` (région ; portée line : lignes 377 à 377) : `c^ := c^ + 1;`
* U ms.pas:377 `c^` (région ; portée line : lignes 377 à 377) : `c^ := c^ + 1;`
* U ms.pas:418 `2^` (hors région ; portée line : lignes 418 à 418) : `Emit('k3', v, '4x2^25', r, dt, IntToStr(s));`
* U ms.pas:463 `v^` (hors région ; portée line : lignes 463 à 463) : `x := v^;`
* U ms.pas:733 `^T` (région ; portée line : lignes 733 à 733) : `PColsP = ^TColsP;`
* U ms.pas:915 `^T` (région ; portée line : lignes 915 à 915) : `PK6Arg = ^TK6Arg;`
* U ms.pas:922 `a^` (région ; portée line : lignes 922 à 922) : `with a^.c^ do`
* U ms.pas:922 `c^` (région ; portée line : lignes 922 à 922) : `with a^.c^ do`
* U ms.pas:923 `a^` (région ; portée line : lignes 923 à 923) : `if a^.q1 then`
* U ms.pas:924 `a^` (région ; portée line : lignes 924 à 924) : `Q1Tuned(sd, pr, q, d, t, rf, ls, a^.lo, a^.hi, a^.acc)`
* U ms.pas:924 `a^` (région ; portée line : lignes 924 à 924) : `Q1Tuned(sd, pr, q, d, t, rf, ls, a^.lo, a^.hi, a^.acc)`
* U ms.pas:924 `a^` (région ; portée line : lignes 924 à 924) : `Q1Tuned(sd, pr, q, d, t, rf, ls, a^.lo, a^.hi, a^.acc)`
* U ms.pas:926 `a^` (région ; portée line : lignes 926 à 926) : `a^.s6 := Q6Tuned(sd, d, q, pr, a^.lo, a^.hi);`
* U ms.pas:926 `a^` (région ; portée line : lignes 926 à 926) : `a^.s6 := Q6Tuned(sd, d, q, pr, a^.lo, a^.hi);`
* U ms.pas:926 `a^` (région ; portée line : lignes 926 à 926) : `a^.s6 := Q6Tuned(sd, d, q, pr, a^.lo, a^.hi);`
* U ms.pas:938 `^T` (région ; portée line : lignes 938 à 938) : `PK6Job = ^TK6Job;`
* U ms.pas:949 `j^` (région ; portée line : lignes 949 à 949) : `with j^.c^ do`
* U ms.pas:949 `c^` (région ; portée line : lignes 949 à 949) : `with j^.c^ do`
* U ms.pas:950 `j^` (région ; portée line : lignes 950 à 950) : `if not j^.q1 then`
* U ms.pas:951 `j^` (région ; portée line : lignes 951 à 951) : `j^.s6[w] := Q6Tuned(sd, d, q, pr, lo, hi)`
* U ms.pas:952 `j^` (région ; portée line : lignes 952 à 952) : `else if j^.sc then`
* U ms.pas:953 `j^` (région ; portée line : lignes 953 à 953) : `Q1TunedS(sd, pr, q, d, t, rf, ls, lo, hi, j^.acc[w])`
* U ms.pas:955 `j^` (région ; portée line : lignes 955 à 955) : `Q1Tuned(sd, pr, q, d, t, rf, ls, lo, hi, j^.acc[w]);`
* U ms.pas:1092 `^T` (région ; portée line : lignes 1092 à 1092) : `PSlot = ^TSlot;`
* U ms.pas:1106 `b^` (région ; portée line : lignes 1106 à 1106) : `FillChar(tab^, CAP7 * SizeOf(TSlot), 0);`
* U ms.pas:1236 `^T` (région ; portée line : lignes 1236 à 1236) : `PNode = ^TNode;`
* U ms.pas:1246 `^T` (région ; portée line : lignes 1246 à 1246) : `PANode = ^TANode;`
* U ms.pas:1254 `n^` (région ; portée line : lignes 1254 à 1254) : `n^.v := counter;`
* U ms.pas:1258 `n^` (région ; portée line : lignes 1258 à 1258) : `n^.l := TBuild(depth - 1, counter);`
* U ms.pas:1259 `n^` (région ; portée line : lignes 1259 à 1259) : `n^.r := TBuild(depth - 1, counter);`
* U ms.pas:1263 `n^` (région ; portée line : lignes 1263 à 1263) : `n^.l := nil;`
* U ms.pas:1264 `n^` (région ; portée line : lignes 1264 à 1264) : `n^.r := nil;`
* U ms.pas:1274 `n^` (région ; portée line : lignes 1274 à 1274) : `Result := n^.v + TSum(n^.l) + TSum(n^.r);`
* U ms.pas:1274 `n^` (région ; portée line : lignes 1274 à 1274) : `Result := n^.v + TSum(n^.l) + TSum(n^.r);`
* U ms.pas:1274 `n^` (région ; portée line : lignes 1274 à 1274) : `Result := n^.v + TSum(n^.l) + TSum(n^.r);`
* U ms.pas:1281 `n^` (région ; portée line : lignes 1281 à 1281) : `TFree(n^.l);`
* U ms.pas:1282 `n^` (région ; portée line : lignes 1282 à 1282) : `TFree(n^.r);`
* U ms.pas:1553 `^T` (région ; portée line : lignes 1553 à 1553) : `PGrid = ^TGrid;`
* U ms.pas:1609 `8^` (hors région ; portée line : lignes 1609 à 1609) : `Emit('k9', v, '2048^2x4', r, dt, Format('%.16e', [s]));`
* U ms.pas:1646 `^T` (région ; portée line : lignes 1646 à 1646) : `PK9Arg = ^TK9Arg;`
* U ms.pas:1689 `a^` (hors région ; portée line : lignes 1689 à 1689) : `ga^[i, j] := Double((i * 31 + j * 17) mod 1024) / 1024.0;`
* U ms.pas:1690 `b^` (hors région ; portée line : lignes 1690 à 1690) : `gb^ := ga^; { le bord de b = bord initial }`
* U ms.pas:1690 `a^` (hors région ; portée line : lignes 1690 à 1690) : `gb^ := ga^; { le bord de b = bord initial }`
* U ms.pas:1694 `a^` (hors région ; portée line : lignes 1694 à 1694) : `K9Natural(ga^, gb^);`
* U ms.pas:1694 `b^` (hors région ; portée line : lignes 1694 à 1694) : `K9Natural(ga^, gb^);`
* U ms.pas:1703 `a^` (hors région ; portée line : lignes 1703 à 1703) : `s := s + ga^[i, j];`
* U ms.pas:1705 `8^` (hors région ; portée line : lignes 1705 à 1705) : `Emit('k9', v, '2048^2x4', r, dt, Format('%.16e', [s]));`
* U ms.pas:1720 `Move(` (hors région ; portée line : lignes 1720 à 1720) : `Move(a^, b^, n * SizeOf(Double));`
* U ms.pas:1720 `a^` (hors région ; portée line : lignes 1720 à 1720) : `Move(a^, b^, n * SizeOf(Double));`
* U ms.pas:1720 `b^` (hors région ; portée line : lignes 1720 à 1720) : `Move(a^, b^, n * SizeOf(Double));`
* U ms.pas:1754 `8^` (hors région ; portée line : lignes 1754 à 1754) : `Emit('k9', v, '2048^2x4', r, dt, Format('%.16e', [s]));`
* U ms.pas:1780 `^T` (hors région ; portée line : lignes 1780 à 1780) : `PSpsc = ^TSpsc;`
* U ms.pas:1842 `q^` (hors région ; portée line : lignes 1842 à 1842) : `rc := sq^.readIdx;`
* U ms.pas:1843 `q^` (hors région ; portée line : lignes 1843 à 1843) : `sq^.buf[w and (CAP10 - 1)] := x;`
* U ms.pas:1845 `q^` (hors région ; portée line : lignes 1845 à 1845) : `sq^.writeIdx := w;`
* U ms.pas:1861 `q^` (hors région ; portée line : lignes 1861 à 1861) : `wc := sq^.writeIdx;`
* U ms.pas:1862 `q^` (hors région ; portée line : lignes 1862 à 1862) : `s := s + sq^.buf[rd and (CAP10 - 1)];`
* U ms.pas:1864 `q^` (hors région ; portée line : lignes 1864 à 1864) : `sq^.readIdx := rd;`
* U ms.pas:1884 `q^` (hors région ; portée line : lignes 1884 à 1884) : `FillChar(sq^, SizeOf(TSpsc), 0);`
* U ms.pas:1908 `2^` (hors région ; portée line : lignes 1908 à 1908) : `Emit('k10', v, '2^22', r, dt, IntToStr(k10Sum));`
* U msvec.pas:18 `^T` (région ; portée line : lignes 18 à 18) : `PV4 = ^TV4;`

## java


## go

* X ms.go:10 `simd/archsimd` (hors région) : `"simd/archsimd"`
* U ms.go:40 `unsafe.` (hors région ; portée line : lignes 40 à 40) : `return unsafe.Slice((*T)(unsafe.Pointer(&b[0])), len(b)/int(unsafe.Sizeof(z)))`
* U ms.go:40 `unsafe.` (hors région ; portée line : lignes 40 à 40) : `return unsafe.Slice((*T)(unsafe.Pointer(&b[0])), len(b)/int(unsafe.Sizeof(z)))`
* U ms.go:40 `unsafe.` (hors région ; portée line : lignes 40 à 40) : `return unsafe.Slice((*T)(unsafe.Pointer(&b[0])), len(b)/int(unsafe.Sizeof(z)))`
* X ms.go:97 `archsimd.` (région) : `a0 := archsimd.BroadcastFloat64x8(0)`
* X ms.go:99 `archsimd.` (région) : `h := archsimd.BroadcastFloat32x16(0.5)`
* X ms.go:101 `archsimd.` (région) : `x := archsimd.LoadFloat32x16(vx[i : i+16])`
* X ms.go:102 `archsimd.` (région) : `y := archsimd.LoadFloat32x16(vy[i : i+16])`
* X ms.go:103 `archsimd.` (région) : `z := archsimd.LoadFloat32x16(vz[i : i+16])`
* X ms.go:104 `archsimd.` (région) : `w := archsimd.LoadFloat32x16(m[i : i+16])`
* X ms.go:112 `archsimd.` (région) : `archsimd.ClearAVXUpperBits() // remarque sur Go (docs/GO.md) : passage d'AVX à SSE sans pénalité`
* X ms.go:286 `archsimd.` (région) : `lim := archsimd.BroadcastUint8x64(128)`
* X ms.go:287 `archsimd.` (région) : `zero := archsimd.BroadcastUint8x64(0)`
* X ms.go:288 `archsimd.` (région) : `var acc archsimd.Uint64x8`
* X ms.go:292 `archsimd.` (région) : `x := archsimd.LoadUint8x64(v[i : i+64])`
* X ms.go:370 `archsimd.` (région) : `z := archsimd.BroadcastFloat32x16(0)`
* X ms.go:373 `archsimd.` (région) : `s0 = archsimd.LoadFloat32x16(a[i:i+16]).MulAdd(archsimd.LoadFloat32x16(b[i:i+16]), s0)`
* X ms.go:373 `archsimd.` (région) : `s0 = archsimd.LoadFloat32x16(a[i:i+16]).MulAdd(archsimd.LoadFloat32x16(b[i:i+16]), s0)`
* X ms.go:374 `archsimd.` (région) : `s1 = archsimd.LoadFloat32x16(a[i+16:i+32]).MulAdd(archsimd.LoadFloat32x16(b[i+16:i+32]), s1)`
* X ms.go:374 `archsimd.` (région) : `s1 = archsimd.LoadFloat32x16(a[i+16:i+32]).MulAdd(archsimd.LoadFloat32x16(b[i+16:i+32]), s1)`
* X ms.go:375 `archsimd.` (région) : `s2 = archsimd.LoadFloat32x16(a[i+32:i+48]).MulAdd(archsimd.LoadFloat32x16(b[i+32:i+48]), s2)`
* X ms.go:375 `archsimd.` (région) : `s2 = archsimd.LoadFloat32x16(a[i+32:i+48]).MulAdd(archsimd.LoadFloat32x16(b[i+32:i+48]), s2)`
* X ms.go:376 `archsimd.` (région) : `s3 = archsimd.LoadFloat32x16(a[i+48:i+64]).MulAdd(archsimd.LoadFloat32x16(b[i+48:i+64]), s3)`
* X ms.go:376 `archsimd.` (région) : `s3 = archsimd.LoadFloat32x16(a[i+48:i+64]).MulAdd(archsimd.LoadFloat32x16(b[i+48:i+64]), s3)`
* X ms.go:380 `archsimd.` (région) : `archsimd.ClearAVXUpperBits() // remarque sur Go (docs/GO.md) : passage d'AVX à SSE sans pénalité`
* X ms.go:395 `archsimd.` (région) : `z := archsimd.BroadcastFloat32x16(0)`
* X ms.go:398 `archsimd.` (région) : `s0 = archsimd.LoadFloat32x16(a[i:i+16]).MulAdd(archsimd.LoadFloat32x16(b[i:i+16]), s0)`
* X ms.go:398 `archsimd.` (région) : `s0 = archsimd.LoadFloat32x16(a[i:i+16]).MulAdd(archsimd.LoadFloat32x16(b[i:i+16]), s0)`
* X ms.go:399 `archsimd.` (région) : `s1 = archsimd.LoadFloat32x16(a[i+16:i+32]).MulAdd(archsimd.LoadFloat32x16(b[i+16:i+32]), s1)`
* X ms.go:399 `archsimd.` (région) : `s1 = archsimd.LoadFloat32x16(a[i+16:i+32]).MulAdd(archsimd.LoadFloat32x16(b[i+16:i+32]), s1)`
* X ms.go:400 `archsimd.` (région) : `s2 = archsimd.LoadFloat32x16(a[i+32:i+48]).MulAdd(archsimd.LoadFloat32x16(b[i+32:i+48]), s2)`
* X ms.go:400 `archsimd.` (région) : `s2 = archsimd.LoadFloat32x16(a[i+32:i+48]).MulAdd(archsimd.LoadFloat32x16(b[i+32:i+48]), s2)`
* X ms.go:401 `archsimd.` (région) : `s3 = archsimd.LoadFloat32x16(a[i+48:i+64]).MulAdd(archsimd.LoadFloat32x16(b[i+48:i+64]), s3)`
* X ms.go:401 `archsimd.` (région) : `s3 = archsimd.LoadFloat32x16(a[i+48:i+64]).MulAdd(archsimd.LoadFloat32x16(b[i+48:i+64]), s3)`
* X ms.go:412 `archsimd.` (région) : `archsimd.ClearAVXUpperBits()`
* X ms.go:461 `archsimd.` (région) : `lo8766, hi9131 := archsimd.BroadcastInt32x16(8766), archsimd.BroadcastInt32x16(9131)`
* X ms.go:461 `archsimd.` (région) : `lo8766, hi9131 := archsimd.BroadcastInt32x16(8766), archsimd.BroadcastInt32x16(9131)`
* X ms.go:462 `archsimd.` (région) : `c5, c7, c24 := archsimd.BroadcastInt32x16(5), archsimd.BroadcastInt32x16(7), archsimd.BroadcastInt32x16(24)`
* X ms.go:462 `archsimd.` (région) : `c5, c7, c24 := archsimd.BroadcastInt32x16(5), archsimd.BroadcastInt32x16(7), archsimd.BroadcastInt32x16(24)`
* X ms.go:462 `archsimd.` (région) : `c5, c7, c24 := archsimd.BroadcastInt32x16(5), archsimd.BroadcastInt32x16(7), archsimd.BroadcastInt32x16(24)`
* X ms.go:463 `archsimd.` (région) : `acc := archsimd.BroadcastInt64x8(0)`
* X ms.go:466 `archsimd.` (région) : `sd := archsimd.LoadInt32x16(c.sd[i : i+16])`
* X ms.go:467 `archsimd.` (région) : `d := archsimd.LoadUint8x16(c.d[i : i+16]).ExtendToUint32().AsInt32x16()`
* X ms.go:468 `archsimd.` (région) : `q := archsimd.LoadUint8x16(c.q[i : i+16]).ExtendToUint32().AsInt32x16()`
* X ms.go:470 `archsimd.` (région) : `p := archsimd.LoadInt32x16(c.pr[i : i+16]).Mul(d).Masked(m)`
* X ms.go:475 `archsimd.` (région) : `archsimd.ClearAVXUpperBits() // remarque sur Go (docs/GO.md) : passage d'AVX à SSE sans pénalité`
* X ms.go:538 `archsimd.` (région) : `lim, c100 := archsimd.BroadcastInt32x16(10471), archsimd.BroadcastInt32x16(100)`
* X ms.go:538 `archsimd.` (région) : `lim, c100 := archsimd.BroadcastInt32x16(10471), archsimd.BroadcastInt32x16(100)`
* X ms.go:539 `archsimd.` (région) : `k0 := archsimd.BroadcastInt32x16(0)`
* X ms.go:540 `archsimd.` (région) : `k1 := archsimd.BroadcastInt32x16(1)`
* X ms.go:541 `archsimd.` (région) : `k2 := archsimd.BroadcastInt32x16(2)`
* X ms.go:542 `archsimd.` (région) : `k3 := archsimd.BroadcastInt32x16(3)`
* X ms.go:543 `archsimd.` (région) : `k4 := archsimd.BroadcastInt32x16(4)`
* X ms.go:544 `archsimd.` (région) : `k5 := archsimd.BroadcastInt32x16(5)`
* X ms.go:545 `archsimd.` (région) : `z, zl := archsimd.BroadcastInt32x16(0), archsimd.BroadcastInt64x8(0)`
* X ms.go:545 `archsimd.` (région) : `z, zl := archsimd.BroadcastInt32x16(0), archsimd.BroadcastInt64x8(0)`
* X ms.go:559 `archsimd.` (région) : `pass := archsimd.LoadInt32x16(c.sd[i : i+16]).LessEqual(lim)`
* X ms.go:560 `archsimd.` (région) : `rf := archsimd.LoadUint8x16(c.rf[i : i+16]).ExtendToUint32().AsInt32x16()`
* X ms.go:561 `archsimd.` (région) : `gr := rf.Add(rf).Add(archsimd.LoadUint8x16(c.ls[i : i+16]).ExtendToUint32().AsInt32x16())`
* X ms.go:562 `archsimd.` (région) : `vq := archsimd.LoadUint8x16(c.q[i : i+16]).ExtendToUint32().AsInt32x16()`
* X ms.go:563 `archsimd.` (région) : `vd := archsimd.LoadUint8x16(c.d[i : i+16]).ExtendToUint32().AsInt32x16()`
* X ms.go:564 `archsimd.` (région) : `vt := archsimd.LoadUint8x16(c.t[i : i+16]).ExtendToUint32().AsInt32x16().Add(c100)`
* X ms.go:565 `archsimd.` (région) : `vp := archsimd.LoadInt32x16(c.pr[i : i+16])`
* X ms.go:573 `archsimd.` (région) : `cl0 = cl0.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b0)), cl0)`
* X ms.go:574 `archsimd.` (région) : `ch0 = ch0.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b0>>8)), ch0)`
* X ms.go:579 `archsimd.` (région) : `cl1 = cl1.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b1)), cl1)`
* X ms.go:580 `archsimd.` (région) : `ch1 = ch1.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b1>>8)), ch1)`
* X ms.go:585 `archsimd.` (région) : `cl2 = cl2.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b2)), cl2)`
* X ms.go:586 `archsimd.` (région) : `ch2 = ch2.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b2>>8)), ch2)`
* X ms.go:591 `archsimd.` (région) : `cl3 = cl3.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b3)), cl3)`
* X ms.go:592 `archsimd.` (région) : `ch3 = ch3.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b3>>8)), ch3)`
* X ms.go:597 `archsimd.` (région) : `cl4 = cl4.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b4)), cl4)`
* X ms.go:598 `archsimd.` (région) : `ch4 = ch4.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b4>>8)), ch4)`
* X ms.go:603 `archsimd.` (région) : `cl5 = cl5.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b5)), cl5)`
* X ms.go:604 `archsimd.` (région) : `ch5 = ch5.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b5>>8)), ch5)`
* X ms.go:637 `archsimd.` (région) : `archsimd.ClearAVXUpperBits()`
* X ms.go:643 `archsimd.` (région) : `func sum32(v archsimd.Int32x16) int64 {`
* X ms.go:653 `archsimd.` (région) : `func sum64(v archsimd.Int64x8) int64 {`
* X ms.go:987 `archsimd.` (région) : `q := archsimd.BroadcastFloat64x8(0.25)`
* X ms.go:995 `archsimd.` (région) : `s := archsimd.LoadFloat64x8(up[j : j+8]).Add(archsimd.LoadFloat64x8(dn[j : j+8])).`
* X ms.go:995 `archsimd.` (région) : `s := archsimd.LoadFloat64x8(up[j : j+8]).Add(archsimd.LoadFloat64x8(dn[j : j+8])).`
* X ms.go:996 `archsimd.` (région) : `Add(archsimd.LoadFloat64x8(mid[j-1 : j+7])).Add(archsimd.LoadFloat64x8(mid[j+1 : j+9]))`
* X ms.go:996 `archsimd.` (région) : `Add(archsimd.LoadFloat64x8(mid[j-1 : j+7])).Add(archsimd.LoadFloat64x8(mid[j+1 : j+9]))`
* X ms.go:1000 `archsimd.` (région) : `u, _ := archsimd.LoadFloat64x8Part(up[j : j+n])`
* X ms.go:1001 `archsimd.` (région) : `w, _ := archsimd.LoadFloat64x8Part(dn[j : j+n])`
* X ms.go:1002 `archsimd.` (région) : `l, _ := archsimd.LoadFloat64x8Part(mid[j-1 : j-1+n])`
* X ms.go:1003 `archsimd.` (région) : `r, _ := archsimd.LoadFloat64x8Part(mid[j+1 : j+1+n])`
* X ms.go:1007 `archsimd.` (région) : `archsimd.ClearAVXUpperBits()`

## haskell

* U Ms.hs:20 `Ptr` (hors région ; portée line : lignes 20 à 20) : `import Foreign.Ptr`
* U Ms.hs:25 `unsafeWithForeignPtr` (hors région ; portée line : lignes 25 à 25) : `import GHC.ForeignPtr (mallocPlainForeignPtrAlignedBytes, unsafeWithForeignPtr)`
* U Ms.hs:27 `unsafeDupablePerformIO` (hors région ; portée line : lignes 27 à 27) : `import System.IO.Unsafe (unsafeDupablePerformIO)`
* U Ms.hs:47 `unsafeUseAsCString` (hors région ; portée line : lignes 47 à 47) : `BSU.unsafeUseAsCString bs $ \src -> unsafeWithForeignPtr fp $ \dst -> copyBytes (castPtr dst) src n`
* U Ms.hs:47 `unsafeWithForeignPtr` (hors région ; portée line : lignes 47 à 47) : `BSU.unsafeUseAsCString bs $ \src -> unsafeWithForeignPtr fp $ \dst -> copyBytes (castPtr dst) src n`
* U Ms.hs:50 `Ptr` (hors région ; portée line : lignes 50 à 50) : `withBuf :: Buf a -> (Ptr a -> IO b) -> IO b`
* U Ms.hs:51 `unsafeWithForeignPtr` (hors région ; portée line : lignes 51 à 51) : `withBuf (Buf fp _) = unsafeWithForeignPtr fp`
* U Ms.hs:79 `Ptr` (hors région ; portée line : lignes 79 à 79) : `k1AoS :: Ptr Float -> Int -> IO Double`
* U Ms.hs:84 `peekElemOff` (hors région ; portée line : lignes 84 à 84) : `m <- peekElemOff p (16 * i + 9); x <- peekElemOff p (16 * i + 3); y <- peekElemOff p (16 * i + 4); z <- peekEl`
* U Ms.hs:84 `peekElemOff` (hors région ; portée line : lignes 84 à 84) : `m <- peekElemOff p (16 * i + 9); x <- peekElemOff p (16 * i + 3); y <- peekElemOff p (16 * i + 4); z <- peekEl`
* U Ms.hs:84 `peekElemOff` (hors région ; portée line : lignes 84 à 84) : `m <- peekElemOff p (16 * i + 9); x <- peekElemOff p (16 * i + 3); y <- peekElemOff p (16 * i + 4); z <- peekEl`
* U Ms.hs:84 `peekElemOff` (hors région ; portée line : lignes 84 à 84) : `m <- peekElemOff p (16 * i + 9); x <- peekElemOff p (16 * i + 3); y <- peekElemOff p (16 * i + 4); z <- peekEl`
* U Ms.hs:93 `Ptr` (région ; portée line : lignes 93 à 93) : `k1SoA :: Ptr Float -> Ptr Float -> Ptr Float -> Ptr Float -> Int -> IO Double`
* U Ms.hs:93 `Ptr` (région ; portée line : lignes 93 à 93) : `k1SoA :: Ptr Float -> Ptr Float -> Ptr Float -> Ptr Float -> Int -> IO Double`
* U Ms.hs:93 `Ptr` (région ; portée line : lignes 93 à 93) : `k1SoA :: Ptr Float -> Ptr Float -> Ptr Float -> Ptr Float -> Int -> IO Double`
* U Ms.hs:93 `Ptr` (région ; portée line : lignes 93 à 93) : `k1SoA :: Ptr Float -> Ptr Float -> Ptr Float -> Ptr Float -> Int -> IO Double`
* U Ms.hs:94 `Ptr` (région ; portée line : lignes 94 à 94) : `k1SoA (Ptr vx) (Ptr vy) (Ptr vz) (Ptr m) (I# n) = IO $ \s -> (# s, go 0# 0.0## #)`
* U Ms.hs:94 `Ptr` (région ; portée line : lignes 94 à 94) : `k1SoA (Ptr vx) (Ptr vy) (Ptr vz) (Ptr m) (I# n) = IO $ \s -> (# s, go 0# 0.0## #)`
* U Ms.hs:94 `Ptr` (région ; portée line : lignes 94 à 94) : `k1SoA (Ptr vx) (Ptr vy) (Ptr vz) (Ptr m) (I# n) = IO $ \s -> (# s, go 0# 0.0## #)`
* U Ms.hs:94 `Ptr` (région ; portée line : lignes 94 à 94) : `k1SoA (Ptr vx) (Ptr vy) (Ptr vz) (Ptr m) (I# n) = IO $ \s -> (# s, go 0# 0.0## #)`
* U Ms.hs:99 `indexFloatOffAddrAsFloatX16#` (région ; portée line : lignes 99 à 99) : `let x = indexFloatOffAddrAsFloatX16# vx i`
* U Ms.hs:100 `indexFloatOffAddrAsFloatX16#` (région ; portée line : lignes 100 à 100) : `y = indexFloatOffAddrAsFloatX16# vy i`
* U Ms.hs:101 `indexFloatOffAddrAsFloatX16#` (région ; portée line : lignes 101 à 101) : `z = indexFloatOffAddrAsFloatX16# vz i`
* U Ms.hs:102 `indexFloatOffAddrAsFloatX16#` (région ; portée line : lignes 102 à 102) : `w = indexFloatOffAddrAsFloatX16# m i`
* U Ms.hs:135 `unsafeWithForeignPtr` (région ; portée line : lignes 135 à 135) : `withBuf raw $ \p -> unsafeWithForeignPtr fp $ \c -> forM_ [0 .. n1 - 1] $ \i -> peekElemOff p (16 * i + k) >>=`
* U Ms.hs:135 `peekElemOff` (région ; portée line : lignes 135 à 135) : `withBuf raw $ \p -> unsafeWithForeignPtr fp $ \c -> forM_ [0 .. n1 - 1] $ \i -> peekElemOff p (16 * i + k) >>=`
* U Ms.hs:135 `pokeElemOff` (région ; portée line : lignes 135 à 135) : `withBuf raw $ \p -> unsafeWithForeignPtr fp $ \c -> forM_ [0 .. n1 - 1] $ \i -> peekElemOff p (16 * i + k) >>=`
* U Ms.hs:138 `unsafeWithForeignPtr` (région ; portée line : lignes 138 à 138) : `unsafeWithForeignPtr (c 3) $ \a -> unsafeWithForeignPtr (c 4) $ \b -> unsafeWithForeignPtr (c 5) $ \cc -> unsa`
* U Ms.hs:138 `unsafeWithForeignPtr` (région ; portée line : lignes 138 à 138) : `unsafeWithForeignPtr (c 3) $ \a -> unsafeWithForeignPtr (c 4) $ \b -> unsafeWithForeignPtr (c 5) $ \cc -> unsa`
* U Ms.hs:138 `unsafeWithForeignPtr` (région ; portée line : lignes 138 à 138) : `unsafeWithForeignPtr (c 3) $ \a -> unsafeWithForeignPtr (c 4) $ \b -> unsafeWithForeignPtr (c 5) $ \cc -> unsa`
* U Ms.hs:138 `unsafeWithForeignPtr` (région ; portée line : lignes 138 à 138) : `unsafeWithForeignPtr (c 3) $ \a -> unsafeWithForeignPtr (c 4) $ \b -> unsafeWithForeignPtr (c 5) $ \cc -> unsa`
* U Ms.hs:143 `peekElemOff` (région ; portée line : lignes 143 à 143) : `f <- forM [0 .. 15] $ \k -> peekElemOff p (16 * i + k)`
* U Ms.hs:150 `peekElemOff` (hors région ; portée line : lignes 150 à 150) : `withBuf perm $ \pp -> forM [0 .. n1 - 1] $ \i -> do j <- peekElemOff pp i; return $! arr ! fromIntegral j`
* U Ms.hs:156 `peekElemOff` (hors région ; portée line : lignes 156 à 156) : `raw0 <- withBuf raw $ \p -> peekElemOff p 0`
* U Ms.hs:164 `Ptr` (hors région ; portée line : lignes 164 à 164) : `k2Chase :: Ptr Word32 -> Int -> IO Word32`
* U Ms.hs:168 `peekElemOff` (hors région ; portée line : lignes 168 à 168) : `go !i h = do j <- peekElemOff p (fromIntegral i); go j (h - 1)`
* U Ms.hs:185 `writeIntArray#` (hors région ; portée line : lignes 185 à 185) : `writeI (MBA a) (I# i) (I# x) = IO $ \s -> (# writeIntArray# a i x s, () #)`
* U Ms.hs:188 `readIntArray#` (hors région ; portée line : lignes 188 à 188) : `readI (MBA a) (I# i) = IO $ \s -> case readIntArray# a i s of (# s', x #) -> (# s', I# x #)`
* U Ms.hs:238 `unsafeDupablePerformIO` (région ; portée line : lignes 238 à 238) : `k4Tuned bs = unsafeDupablePerformIO $ BSU.unsafeUseAsCStringLen bs $ \(Ptr a, n) -> return $! k4TunedAddr a n`
* U Ms.hs:238 `unsafeUseAsCStringLen` (région ; portée line : lignes 238 à 238) : `k4Tuned bs = unsafeDupablePerformIO $ BSU.unsafeUseAsCStringLen bs $ \(Ptr a, n) -> return $! k4TunedAddr a n`
* U Ms.hs:238 `Ptr` (région ; portée line : lignes 238 à 238) : `k4Tuned bs = unsafeDupablePerformIO $ BSU.unsafeUseAsCStringLen bs $ \(Ptr a, n) -> return $! k4TunedAddr a n`
* U Ms.hs:250 `indexWord16OffAddrAsWord16X32#` (région ; portée line : lignes 250 à 250) : `case indexWord16OffAddrAsWord16X32# a (uncheckedIShiftRL# i 1#) of  -- indice en unités de 16 bits`
* U Ms.hs:270 `indexWord8OffAddr#` (région ; portée line : lignes 270 à 270) : `let x = W# (word8ToWord# (indexWord8OffAddr# a i))`
* U Ms.hs:281 `unsafeDupablePerformIO` (hors région ; portée line : lignes 281 à 281) : `k4Swar bs = unsafeDupablePerformIO $ BSU.unsafeUseAsCStringLen bs $ \(Ptr a, n) -> return $! k4SwarAddr a n`
* U Ms.hs:281 `unsafeUseAsCStringLen` (hors région ; portée line : lignes 281 à 281) : `k4Swar bs = unsafeDupablePerformIO $ BSU.unsafeUseAsCStringLen bs $ \(Ptr a, n) -> return $! k4SwarAddr a n`
* U Ms.hs:281 `Ptr` (hors région ; portée line : lignes 281 à 281) : `k4Swar bs = unsafeDupablePerformIO $ BSU.unsafeUseAsCStringLen bs $ \(Ptr a, n) -> return $! k4SwarAddr a n`
* U Ms.hs:288 `indexWord8OffAddrAsWord64#` (hors région ; portée line : lignes 288 à 288) : `word (I# i) = W64# (indexWord8OffAddrAsWord64# a (i *# 8#))`
* U Ms.hs:308 `indexWord8OffAddr#` (hors région ; portée line : lignes 308 à 308) : `let x = fromIntegral (W# (word8ToWord# (indexWord8OffAddr# a i#))) :: Word64`
* U Ms.hs:327 `Ptr` (région ; portée line : lignes 327 à 327) : `k5Tuned :: Ptr Float -> Ptr Float -> Int -> Float`
* U Ms.hs:327 `Ptr` (région ; portée line : lignes 327 à 327) : `k5Tuned :: Ptr Float -> Ptr Float -> Int -> Float`
* U Ms.hs:328 `Ptr` (région ; portée line : lignes 328 à 328) : `k5Tuned (Ptr a) (Ptr b) (I# n) = go 0# z z z z`
* U Ms.hs:328 `Ptr` (région ; portée line : lignes 328 à 328) : `k5Tuned (Ptr a) (Ptr b) (I# n) = go 0# z z z z`
* U Ms.hs:338 `indexFloatOffAddrAsFloatX16#` (région ; portée line : lignes 338 à 338) : `let ld p k = indexFloatOffAddrAsFloatX16# p (i +# k)`
* U Ms.hs:353 `unsafeWithForeignPtr` (hors région ; portée line : lignes 353 à 353) : `loop k _ = do Buf fa _ <- readIORef ref; d <- unsafeWithForeignPtr fa $ \pa -> return $! k5Tuned pa pb MS_N5; `
* U Ms.hs:356 `peekElemOff` (région ; portée line : lignes 356 à 356) : `la <- withBuf ba $ \p -> forM [0 .. MS_N5 - 1] (peekElemOff p)`
* U Ms.hs:357 `peekElemOff` (région ; portée line : lignes 357 à 357) : `lb <- withBuf bb $ \p -> forM [0 .. MS_N5 - 1] (peekElemOff p)`
* U Ms.hs:370 `Ptr` (hors région ; portée line : lignes 370 à 370) : `data Cols = Cols { csd, cpr :: !(Ptr Int32), cq, cd, ct, crf, cls :: !(Ptr Word8) }`
* U Ms.hs:370 `Ptr` (hors région ; portée line : lignes 370 à 370) : `data Cols = Cols { csd, cpr :: !(Ptr Int32), cq, cd, ct, crf, cls :: !(Ptr Word8) }`
* U Ms.hs:372 `Ptr` (hors région ; portée line : lignes 372 à 372) : `rd8 :: Ptr Word8 -> Int -> IO Int`
* U Ms.hs:373 `peekElemOff` (hors région ; portée line : lignes 373 à 373) : `rd8 p i = fromIntegral <$> peekElemOff p i`
* U Ms.hs:374 `Ptr` (hors région ; portée line : lignes 374 à 374) : `rd32 :: Ptr Int32 -> Int -> IO Int`
* U Ms.hs:375 `peekElemOff` (hors région ; portée line : lignes 375 à 375) : `rd32 p i = fromIntegral <$> peekElemOff p i`
* U Ms.hs:404 `unsafeWithForeignPtr` (région ; portée line : lignes 404 à 404) : `unsafeWithForeignPtr acc $ \a -> do`
* U Ms.hs:406 `peekElemOff` (région ; portée line : lignes 406 à 406) : `let add k x = peekElemOff a k >>= \y -> pokeElemOff a k (y + x)`
* U Ms.hs:406 `pokeElemOff` (région ; portée line : lignes 406 à 406) : `let add k x = peekElemOff a k >>= \y -> pokeElemOff a k (y + x)`
* U Ms.hs:417 `peekElemOff` (région ; portée line : lignes 417 à 417) : `forM [0 .. 29] (peekElemOff a)`
* U Ms.hs:423 `unsafeWithForeignPtr` (région ; portée line : lignes 423 à 423) : `unsafeWithForeignPtr acc $ \a -> do`
* U Ms.hs:425 `peekElemOff` (région ; portée line : lignes 425 à 425) : `let add k x = peekElemOff a k >>= \y -> pokeElemOff a k (y + x)`
* U Ms.hs:425 `pokeElemOff` (région ; portée line : lignes 425 à 425) : `let add k x = peekElemOff a k >>= \y -> pokeElemOff a k (y + x)`
* U Ms.hs:437 `peekElemOff` (région ; portée line : lignes 437 à 437) : `forM [0 .. 29] (peekElemOff a)`
* U Ms.hs:492 `Ptr` (région ; portée line : lignes 492 à 492) : `k7TunedPf :: Ptr Word32 -> Ptr Word32 -> Int -> Int -> Int -> IO (ForeignPtr Word8)`
* U Ms.hs:492 `Ptr` (région ; portée line : lignes 492 à 492) : `k7TunedPf :: Ptr Word32 -> Ptr Word32 -> Int -> Int -> Int -> IO (ForeignPtr Word8)`
* U Ms.hs:495 `unsafeWithForeignPtr` (région ; portée line : lignes 495 à 495) : `unsafeWithForeignPtr fp $ \t -> allocaBytes (16 * 8) $ \(hs :: Ptr Int) -> do`
* U Ms.hs:495 `Ptr` (région ; portée line : lignes 495 à 495) : `unsafeWithForeignPtr fp $ \t -> allocaBytes (16 * 8) $ \(hs :: Ptr Int) -> do`
* U Ms.hs:497 `Ptr` (région ; portée line : lignes 497 à 497) : `let !(Ptr ta) = t`
* U Ms.hs:503 `peekByteOff` (région ; portée line : lignes 503 à 503) : `cnt <- peekByteOff t (s * 16 + 4) :: IO Word32`
* U Ms.hs:504 `peekByteOff` (région ; portée line : lignes 504 à 504) : `key <- peekByteOff t (s * 16) :: IO Word32`
* U Ms.hs:507 `peekByteOff` (région ; portée line : lignes 507 à 507) : `cnt <- peekByteOff t (s * 16 + 4) :: IO Word32`
* U Ms.hs:508 `peekByteOff` (région ; portée line : lignes 508 à 508) : `sm <- peekByteOff t (s * 16 + 8) :: IO Word64`
* U Ms.hs:509 `pokeByteOff` (région ; portée line : lignes 509 à 509) : `pokeByteOff t (s * 16) k`
* U Ms.hs:510 `pokeByteOff` (région ; portée line : lignes 510 à 510) : `pokeByteOff t (s * 16 + 4) (cnt + 1)`
* U Ms.hs:511 `pokeByteOff` (région ; portée line : lignes 511 à 511) : `pokeByteOff t (s * 16 + 8) (sm + fromIntegral x)`
* U Ms.hs:516 `peekElemOff` (région ; portée line : lignes 516 à 516) : `k <- peekElemOff keys (i + b)`
* U Ms.hs:518 `pokeElemOff` (région ; portée line : lignes 518 à 518) : `pokeElemOff hs b h`
* U Ms.hs:525 `peekElemOff` (région ; portée line : lignes 525 à 525) : `k <- peekElemOff keys (i + b); x <- peekElemOff vals (i + b); h <- peekElemOff hs b`
* U Ms.hs:525 `peekElemOff` (région ; portée line : lignes 525 à 525) : `k <- peekElemOff keys (i + b); x <- peekElemOff vals (i + b); h <- peekElemOff hs b`
* U Ms.hs:525 `peekElemOff` (région ; portée line : lignes 525 à 525) : `k <- peekElemOff keys (i + b); x <- peekElemOff vals (i + b); h <- peekElemOff hs b`
* U Ms.hs:531 `peekElemOff` (région ; portée line : lignes 531 à 531) : `| i < n = do k <- peekElemOff keys i; x <- peekElemOff vals i; ins k x (hashOf k); batch (i + 1)`
* U Ms.hs:531 `peekElemOff` (région ; portée line : lignes 531 à 531) : `| i < n = do k <- peekElemOff keys i; x <- peekElemOff vals i; ins k x (hashOf k); batch (i + 1)`
* U Ms.hs:550 `peekElemOff` (région ; portée line : lignes 550 à 550) : `k <- fromIntegral <$> peekElemOff keys i`
* U Ms.hs:551 `peekElemOff` (région ; portée line : lignes 551 à 551) : `x <- fromIntegral <$> peekElemOff vals i`
* U Ms.hs:560 `unsafeWithForeignPtr` (région ; portée line : lignes 560 à 560) : `unsafeWithForeignPtr fp $ \t -> do`
* U Ms.hs:565 `peekElemOff` (région ; portée line : lignes 565 à 565) : `k <- peekElemOff keys i`
* U Ms.hs:566 `peekElemOff` (région ; portée line : lignes 566 à 566) : `x <- peekElemOff vals i`
* U Ms.hs:569 `peekByteOff` (région ; portée line : lignes 569 à 569) : `cnt <- peekByteOff t (s * 16 + 4) :: IO Word32`
* U Ms.hs:570 `peekByteOff` (région ; portée line : lignes 570 à 570) : `key <- peekByteOff t (s * 16) :: IO Word32`
* U Ms.hs:573 `peekByteOff` (région ; portée line : lignes 573 à 573) : `cnt <- peekByteOff t (s * 16 + 4) :: IO Word32`
* U Ms.hs:574 `peekByteOff` (région ; portée line : lignes 574 à 574) : `sm <- peekByteOff t (s * 16 + 8) :: IO Word64`
* U Ms.hs:575 `pokeByteOff` (région ; portée line : lignes 575 à 575) : `pokeByteOff t (s * 16) k`
* U Ms.hs:576 `pokeByteOff` (région ; portée line : lignes 576 à 576) : `pokeByteOff t (s * 16 + 4) (cnt + 1)`
* U Ms.hs:577 `pokeByteOff` (région ; portée line : lignes 577 à 577) : `pokeByteOff t (s * 16 + 8) (sm + fromIntegral x)`
* U Ms.hs:581 `unsafeWithForeignPtr` (hors région ; portée line : lignes 581 à 581) : `(nk, ws) <- unsafeWithForeignPtr tab $ \t -> foldM (\(!a, !b) s -> do`
* U Ms.hs:582 `peekByteOff` (hors région ; portée line : lignes 582 à 582) : `cnt <- peekByteOff t (s * 16 + 4) :: IO Word32`
* U Ms.hs:584 `peekByteOff` (hors région ; portée line : lignes 584 à 584) : `key <- peekByteOff t (s * 16) :: IO Word32`
* U Ms.hs:585 `peekByteOff` (hors région ; portée line : lignes 585 à 585) : `sm <- peekByteOff t (s * 16 + 8) :: IO Word64`
* U Ms.hs:604 `Ptr` (hors région ; portée line : lignes 604 à 604) : `aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Ptr Int -> Int -> IO Int32`
* U Ms.hs:604 `Ptr` (hors région ; portée line : lignes 604 à 604) : `aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Ptr Int -> Int -> IO Int32`
* U Ms.hs:604 `Ptr` (hors région ; portée line : lignes 604 à 604) : `aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Ptr Int -> Int -> IO Int32`
* U Ms.hs:604 `Ptr` (hors région ; portée line : lignes 604 à 604) : `aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Ptr Int -> Int -> IO Int32`
* U Ms.hs:604 `Ptr` (hors région ; portée line : lignes 604 à 604) : `aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Ptr Int -> Int -> IO Int32`
* U Ms.hs:606 `peek` (hors région ; portée line : lignes 606 à 606) : `i <- peek top`
* U Ms.hs:607 `poke` (hors région ; portée line : lignes 607 à 607) : `poke top (i + 1)`
* U Ms.hs:608 `peek` (hors région ; portée line : lignes 608 à 608) : `c <- peek cnt`
* U Ms.hs:609 `poke` (hors région ; portée line : lignes 609 à 609) : `poke cnt (c + 1)`
* U Ms.hs:610 `pokeElemOff` (hors région ; portée line : lignes 610 à 610) : `pokeElemOff av i c`
* U Ms.hs:612 `pokeElemOff` (hors région ; portée line : lignes 612 à 612) : `then pokeElemOff al i (-1) >> pokeElemOff ar i (-1) >> return (fromIntegral i)`
* U Ms.hs:612 `pokeElemOff` (hors région ; portée line : lignes 612 à 612) : `then pokeElemOff al i (-1) >> pokeElemOff ar i (-1) >> return (fromIntegral i)`
* U Ms.hs:616 `pokeElemOff` (hors région ; portée line : lignes 616 à 616) : `pokeElemOff al i l >> pokeElemOff ar i r`
* U Ms.hs:616 `pokeElemOff` (hors région ; portée line : lignes 616 à 616) : `pokeElemOff al i l >> pokeElemOff ar i r`
* U Ms.hs:619 `Ptr` (hors région ; portée line : lignes 619 à 619) : `aSum :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Int32 -> IO Int`
* U Ms.hs:619 `Ptr` (hors région ; portée line : lignes 619 à 619) : `aSum :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Int32 -> IO Int`
* U Ms.hs:619 `Ptr` (hors région ; portée line : lignes 619 à 619) : `aSum :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Int32 -> IO Int`
* U Ms.hs:623 `peekElemOff` (hors région ; portée line : lignes 623 à 623) : `v <- peekElemOff av (fromIntegral i); l <- peekElemOff al (fromIntegral i); r <- peekElemOff ar (fromIntegral `
* U Ms.hs:623 `peekElemOff` (hors région ; portée line : lignes 623 à 623) : `v <- peekElemOff av (fromIntegral i); l <- peekElemOff al (fromIntegral i); r <- peekElemOff ar (fromIntegral `
* U Ms.hs:623 `peekElemOff` (hors région ; portée line : lignes 623 à 623) : `v <- peekElemOff av (fromIntegral i); l <- peekElemOff al (fromIntegral i); r <- peekElemOff ar (fromIntegral `
* U Ms.hs:630 `Ptr` (hors région ; portée line : lignes 630 à 630) : `aBuildVal :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Int -> Int -> Int -> IO Int`
* U Ms.hs:630 `Ptr` (hors région ; portée line : lignes 630 à 630) : `aBuildVal :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Int -> Int -> Int -> IO Int`
* U Ms.hs:630 `Ptr` (hors région ; portée line : lignes 630 à 630) : `aBuildVal :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Int -> Int -> Int -> IO Int`
* U Ms.hs:632 `pokeElemOff` (hors région ; portée line : lignes 632 à 632) : `pokeElemOff av i (q + i)`
* U Ms.hs:634 `pokeElemOff` (hors région ; portée line : lignes 634 à 634) : `then pokeElemOff al i (-1) >> pokeElemOff ar i (-1) >> return (i + 1)`
* U Ms.hs:634 `pokeElemOff` (hors région ; portée line : lignes 634 à 634) : `then pokeElemOff al i (-1) >> pokeElemOff ar i (-1) >> return (i + 1)`
* U Ms.hs:638 `pokeElemOff` (hors région ; portée line : lignes 638 à 638) : `pokeElemOff al i (fromIntegral l) >> pokeElemOff ar i (fromIntegral r)`
* U Ms.hs:638 `pokeElemOff` (hors région ; portée line : lignes 638 à 638) : `pokeElemOff al i (fromIntegral l) >> pokeElemOff ar i (fromIntegral r)`
* U Ms.hs:648 `Ptr` (région ; portée line : lignes 648 à 648) : `aBuildIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Int -> Int -> IO ()`
* U Ms.hs:648 `Ptr` (région ; portée line : lignes 648 à 648) : `aBuildIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Int -> Int -> IO ()`
* U Ms.hs:648 `Ptr` (région ; portée line : lignes 648 à 648) : `aBuildIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Int -> Int -> IO ()`
* U Ms.hs:648 `Ptr` (région ; portée line : lignes 648 à 648) : `aBuildIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Int -> Int -> IO ()`
* U Ms.hs:653 `pokeElemOff` (région ; portée line : lignes 653 à 653) : `pokeElemOff av i (q + i)`
* U Ms.hs:654 `pokeElemOff` (région ; portée line : lignes 654 à 654) : `when (parent >= 0) $ if right then pokeElemOff ar parent (fromIntegral i) else pokeElemOff al parent (fromInte`
* U Ms.hs:654 `pokeElemOff` (région ; portée line : lignes 654 à 654) : `when (parent >= 0) $ if right then pokeElemOff ar parent (fromIntegral i) else pokeElemOff al parent (fromInte`
* U Ms.hs:657 `pokeElemOff` (région ; portée line : lignes 657 à 657) : `pokeElemOff stk (2 * sp) i`
* U Ms.hs:658 `pokeElemOff` (région ; portée line : lignes 658 à 658) : `pokeElemOff stk (2 * sp + 1) (d - 1)`
* U Ms.hs:661 `pokeElemOff` (région ; portée line : lignes 661 à 661) : `pokeElemOff al i (-1)`
* U Ms.hs:662 `pokeElemOff` (région ; portée line : lignes 662 à 662) : `pokeElemOff ar i (-1)`
* U Ms.hs:666 `peekElemOff` (région ; portée line : lignes 666 à 666) : `pp <- peekElemOff stk (2 * (sp - 1))`
* U Ms.hs:667 `peekElemOff` (région ; portée line : lignes 667 à 667) : `dd <- peekElemOff stk (2 * (sp - 1) + 1)`
* U Ms.hs:670 `Ptr` (région ; portée line : lignes 670 à 670) : `aSumIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int32 -> IO Int`
* U Ms.hs:670 `Ptr` (région ; portée line : lignes 670 à 670) : `aSumIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int32 -> IO Int`
* U Ms.hs:670 `Ptr` (région ; portée line : lignes 670 à 670) : `aSumIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int32 -> IO Int`
* U Ms.hs:670 `Ptr` (région ; portée line : lignes 670 à 670) : `aSumIt :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int32 -> IO Int`
* U Ms.hs:671 `pokeElemOff` (région ; portée line : lignes 671 à 671) : `aSumIt av al ar stk = pokeElemOff stk 0 0 >> go 1 0`
* U Ms.hs:677 `peekElemOff` (région ; portée line : lignes 677 à 677) : `i <- fromIntegral <$> peekElemOff stk (sp - 1)`
* U Ms.hs:678 `peekElemOff` (région ; portée line : lignes 678 à 678) : `x <- peekElemOff av i`
* U Ms.hs:679 `peekElemOff` (région ; portée line : lignes 679 à 679) : `l <- peekElemOff al i`
* U Ms.hs:682 `peekElemOff` (région ; portée line : lignes 682 à 682) : `r <- peekElemOff ar i`
* U Ms.hs:683 `pokeElemOff` (région ; portée line : lignes 683 à 683) : `pokeElemOff stk (sp - 1) r`
* U Ms.hs:684 `pokeElemOff` (région ; portée line : lignes 684 à 684) : `pokeElemOff stk sp l`
* U Ms.hs:697 `unsafeWithForeignPtr` (région ; portée line : lignes 697 à 697) : `unsafeWithForeignPtr fv $ \av -> unsafeWithForeignPtr fl $ \al -> unsafeWithForeignPtr fr $ \ar -> unsafeWithF`
* U Ms.hs:697 `unsafeWithForeignPtr` (région ; portée line : lignes 697 à 697) : `unsafeWithForeignPtr fv $ \av -> unsafeWithForeignPtr fl $ \al -> unsafeWithForeignPtr fr $ \ar -> unsafeWithF`
* U Ms.hs:697 `unsafeWithForeignPtr` (région ; portée line : lignes 697 à 697) : `unsafeWithForeignPtr fv $ \av -> unsafeWithForeignPtr fl $ \al -> unsafeWithForeignPtr fr $ \ar -> unsafeWithF`
* U Ms.hs:697 `unsafeWithForeignPtr` (région ; portée line : lignes 697 à 697) : `unsafeWithForeignPtr fv $ \av -> unsafeWithForeignPtr fl $ \al -> unsafeWithForeignPtr fr $ \ar -> unsafeWithF`
* U Ms.hs:698 `unsafeWithForeignPtr` (région ; portée line : lignes 698 à 698) : `unsafeWithForeignPtr fstk $ \stk -> unsafeWithForeignPtr fss $ \sst ->`
* U Ms.hs:698 `unsafeWithForeignPtr` (région ; portée line : lignes 698 à 698) : `unsafeWithForeignPtr fstk $ \stk -> unsafeWithForeignPtr fss $ \sst ->`
* U Ms.hs:704 `poke` (hors région ; portée line : lignes 704 à 704) : `then do poke top 0; pokeElemOff top 1 qq; root <- aBuild av al ar top (top `plusPtr` 8) MS_K8_REQ; aSum av al `
* U Ms.hs:704 `pokeElemOff` (hors région ; portée line : lignes 704 à 704) : `then do poke top 0; pokeElemOff top 1 qq; root <- aBuild av al ar top (top `plusPtr` 8) MS_K8_REQ; aSum av al `
* U Ms.hs:704 `plusPtr` (hors région ; portée line : lignes 704 à 704) : `then do poke top 0; pokeElemOff top 1 qq; root <- aBuild av al ar top (top `plusPtr` 8) MS_K8_REQ; aSum av al `
* U Ms.hs:733 `Ptr` (région ; portée line : lignes 733 à 733) : `k9Rows :: Ptr Double -> Ptr Double -> Int -> Int -> IO ()`
* U Ms.hs:733 `Ptr` (région ; portée line : lignes 733 à 733) : `k9Rows :: Ptr Double -> Ptr Double -> Int -> Int -> IO ()`
* U Ms.hs:735 `plusPtr` (région ; portée line : lignes 735 à 735) : `let up = a `plusPtr` ((i - 1) * m9 * 8); mid = a `plusPtr` (i * m9 * 8); dn = a `plusPtr` ((i + 1) * m9 * 8)`
* U Ms.hs:735 `plusPtr` (région ; portée line : lignes 735 à 735) : `let up = a `plusPtr` ((i - 1) * m9 * 8); mid = a `plusPtr` (i * m9 * 8); dn = a `plusPtr` ((i + 1) * m9 * 8)`
* U Ms.hs:735 `plusPtr` (région ; portée line : lignes 735 à 735) : `let up = a `plusPtr` ((i - 1) * m9 * 8); mid = a `plusPtr` (i * m9 * 8); dn = a `plusPtr` ((i + 1) * m9 * 8)`
* U Ms.hs:736 `Ptr` (région ; portée line : lignes 736 à 736) : `o = b `plusPtr` (i * m9 * 8) :: Ptr Double`
* U Ms.hs:736 `plusPtr` (région ; portée line : lignes 736 à 736) : `o = b `plusPtr` (i * m9 * 8) :: Ptr Double`
* U Ms.hs:740 `Ptr` (région ; portée line : lignes 740 à 740) : `let !(Ptr u) = up; !(Ptr md) = mid; !(Ptr dw) = dn; !(Ptr oo) = o; !(I# jj) = j`
* U Ms.hs:740 `Ptr` (région ; portée line : lignes 740 à 740) : `let !(Ptr u) = up; !(Ptr md) = mid; !(Ptr dw) = dn; !(Ptr oo) = o; !(I# jj) = j`
* U Ms.hs:740 `Ptr` (région ; portée line : lignes 740 à 740) : `let !(Ptr u) = up; !(Ptr md) = mid; !(Ptr dw) = dn; !(Ptr oo) = o; !(I# jj) = j`
* U Ms.hs:740 `Ptr` (région ; portée line : lignes 740 à 740) : `let !(Ptr u) = up; !(Ptr md) = mid; !(Ptr dw) = dn; !(Ptr oo) = o; !(I# jj) = j`
* U Ms.hs:741 `indexDoubleOffAddrAsDoubleX8#` (région ; portée line : lignes 741 à 741) : `x = plusDoubleX8# (plusDoubleX8# (plusDoubleX8# (indexDoubleOffAddrAsDoubleX8# u jj) (indexDoubleOffAddrAsDoub`
* U Ms.hs:741 `indexDoubleOffAddrAsDoubleX8#` (région ; portée line : lignes 741 à 741) : `x = plusDoubleX8# (plusDoubleX8# (plusDoubleX8# (indexDoubleOffAddrAsDoubleX8# u jj) (indexDoubleOffAddrAsDoub`
* U Ms.hs:742 `indexDoubleOffAddrAsDoubleX8#` (région ; portée line : lignes 742 à 742) : `(indexDoubleOffAddrAsDoubleX8# md (jj -# 1#))) (indexDoubleOffAddrAsDoubleX8# md (jj +# 1#))`
* U Ms.hs:742 `indexDoubleOffAddrAsDoubleX8#` (région ; portée line : lignes 742 à 742) : `(indexDoubleOffAddrAsDoubleX8# md (jj -# 1#))) (indexDoubleOffAddrAsDoubleX8# md (jj +# 1#))`
* U Ms.hs:744 `writeDoubleOffAddrAsDoubleX8#` (région ; portée line : lignes 744 à 744) : `IO (\s -> (# writeDoubleOffAddrAsDoubleX8# oo jj y s, () #))`
* U Ms.hs:749 `peekElemOff` (région ; portée line : lignes 749 à 749) : `u <- peekElemOff up j; dw <- peekElemOff dn j; l <- peekElemOff mid (j - 1); rr <- peekElemOff mid (j + 1)`
* U Ms.hs:749 `peekElemOff` (région ; portée line : lignes 749 à 749) : `u <- peekElemOff up j; dw <- peekElemOff dn j; l <- peekElemOff mid (j - 1); rr <- peekElemOff mid (j + 1)`
* U Ms.hs:749 `peekElemOff` (région ; portée line : lignes 749 à 749) : `u <- peekElemOff up j; dw <- peekElemOff dn j; l <- peekElemOff mid (j - 1); rr <- peekElemOff mid (j + 1)`
* U Ms.hs:749 `peekElemOff` (région ; portée line : lignes 749 à 749) : `u <- peekElemOff up j; dw <- peekElemOff dn j; l <- peekElemOff mid (j - 1); rr <- peekElemOff mid (j + 1)`
* U Ms.hs:750 `pokeElemOff` (région ; portée line : lignes 750 à 750) : `pokeElemOff o j (0.25 * (((u + dw) + l) + rr))`
* U Ms.hs:770 `unsafeWithForeignPtr` (région ; portée line : lignes 770 à 770) : `unsafeWithForeignPtr fa $ \pa -> unsafeWithForeignPtr fb $ \pb ->`
* U Ms.hs:770 `unsafeWithForeignPtr` (région ; portée line : lignes 770 à 770) : `unsafeWithForeignPtr fa $ \pa -> unsafeWithForeignPtr fb $ \pb ->`
* U Ms.hs:772 `pokeElemOff` (hors région ; portée line : lignes 772 à 772) : `forM_ [0 .. m9 * m9 - 1] $ \k -> let x = k9Init (k `div` m9) (k `mod` m9) in pokeElemOff pa k x >> pokeElemOff`
* U Ms.hs:772 `pokeElemOff` (hors région ; portée line : lignes 772 à 772) : `forM_ [0 .. m9 * m9 - 1] $ \k -> let x = k9Init (k `div` m9) (k `mod` m9) in pokeElemOff pa k x >> pokeElemOff`
* U Ms.hs:776 `peekElemOff` (hors région ; portée line : lignes 776 à 776) : `s <- foldM (\acc k -> (acc +) <$> peekElemOff pa k) 0 [0 .. m9 * m9 - 1]`
* U Ms.hs:800 `unsafeWithForeignPtr` (hors région ; portée line : lignes 800 à 800) : `unsafeWithForeignPtr fb $ \buf -> do`
* U Ms.hs:804 `pokeElemOff` (hors région ; portée line : lignes 804 à 804) : `| otherwise = do pokeElemOff buf (w .&. (cap10 - 1)) x; atomicWriteI ctl 16 (w + 1); prod (w + 1) rc (x + 1)`
* U Ms.hs:808 `peekElemOff` (hors région ; portée line : lignes 808 à 808) : `| otherwise = do x <- peekElemOff buf (rd .&. (cap10 - 1)); atomicWriteI ctl 32 (rd + 1); cons (rd + 1) wc (s `

## ocaml

* U ms.ml:44 `unsafe_get` (hors région ; portée line : lignes 44 à 44) : `let e i = let x = Array1.unsafe_get f (i + 3) and y = Array1.unsafe_get f (i + 4) and z = Array1.unsafe_get f `
* U ms.ml:44 `unsafe_get` (hors région ; portée line : lignes 44 à 44) : `let e i = let x = Array1.unsafe_get f (i + 3) and y = Array1.unsafe_get f (i + 4) and z = Array1.unsafe_get f `
* U ms.ml:44 `unsafe_get` (hors région ; portée line : lignes 44 à 44) : `let e i = let x = Array1.unsafe_get f (i + 3) and y = Array1.unsafe_get f (i + 4) and z = Array1.unsafe_get f `
* U ms.ml:45 `unsafe_get` (hors région ; portée line : lignes 45 à 45) : `0.5 *. Array1.unsafe_get f (i + 9) *. ((x *. x) +. (y *. y) +. (z *. z)) in`
* U ms.ml:60 `unsafe_get` (région ; portée line : lignes 60 à 60) : `let x = Array1.unsafe_get vx i and y = Array1.unsafe_get vy i and z = Array1.unsafe_get vz i in`
* U ms.ml:60 `unsafe_get` (région ; portée line : lignes 60 à 60) : `let x = Array1.unsafe_get vx i and y = Array1.unsafe_get vy i and z = Array1.unsafe_get vz i in`
* U ms.ml:60 `unsafe_get` (région ; portée line : lignes 60 à 60) : `let x = Array1.unsafe_get vx i and y = Array1.unsafe_get vy i and z = Array1.unsafe_get vz i in`
* U ms.ml:61 `unsafe_get` (région ; portée line : lignes 61 à 61) : `0.5 *. Array1.unsafe_get m i *. ((x *. x) +. (y *. y) +. (z *. z))`
* U ms.ml:90 `unsafe_set` (région ; portée line : lignes 90 à 90) : `let col k = let c = Array1.create float32 c_layout n1 in for i = 0 to n1 - 1 do Array1.unsafe_set c i (Array1.`
* U ms.ml:90 `unsafe_get` (région ; portée line : lignes 90 à 90) : `let col k = let c = Array1.create float32 c_layout n1 in for i = 0 to n1 - 1 do Array1.unsafe_set c i (Array1.`
* U ms.ml:120 `unsafe_get` (hors région ; portée line : lignes 120 à 120) : `for _ = 1 to h do i := Int32.to_int (Array1.unsafe_get a !i) done;`
* U ms.ml:148 `unsafe_get` (région ; portée line : lignes 148 à 148) : `let x = Char.code (Bytes.unsafe_get v i) in`
* U ms.ml:156 `unsafe_get` (hors région ; portée line : lignes 156 à 156) : `let x = Char.code (Bytes.unsafe_get v i) in`
* U ms.ml:179 `unsafe_get` (région ; portée line : lignes 179 à 179) : `let x = Char.code (Bytes.unsafe_get v !i) in`
* U ms.ml:211 `unsafe_get` (région ; portée line : lignes 211 à 211) : `let x = Char.code (Bytes.unsafe_get v k) in`
* U ms.ml:242 `unsafe_get` (région ; portée line : lignes 242 à 242) : `let g k = Array1.unsafe_get a (!i + k) *. Array1.unsafe_get b (!i + k) in`
* U ms.ml:242 `unsafe_get` (région ; portée line : lignes 242 à 242) : `let g k = Array1.unsafe_get a (!i + k) *. Array1.unsafe_get b (!i + k) in`
* U ms.ml:327 `unsafe_get` (hors région ; portée line : lignes 327 à 327) : `let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q`
* U ms.ml:327 `unsafe_get` (hors région ; portée line : lignes 327 à 327) : `let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q`
* U ms.ml:327 `unsafe_get` (hors région ; portée line : lignes 327 à 327) : `let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q`
* U ms.ml:331 `unsafe_get` (hors région ; portée line : lignes 331 à 331) : `s := !s + (Int32.to_int (Array1.unsafe_get c.pr i) * d * m)`
* U ms.ml:349 `unsafe_get` (région ; portée line : lignes 349 à 349) : `let rej = ((10471 - Int32.to_int (Array1.unsafe_get c.sd i)) lsr 62) land 1 in`
* U ms.ml:350 `unsafe_get` (région ; portée line : lignes 350 à 350) : `let g = ((((Array1.unsafe_get c.rf i * 2) + Array1.unsafe_get c.ls i) * (1 - rej)) + (6 * rej)) * 5 in`
* U ms.ml:350 `unsafe_get` (région ; portée line : lignes 350 à 350) : `let g = ((((Array1.unsafe_get c.rf i * 2) + Array1.unsafe_get c.ls i) * (1 - rej)) + (6 * rej)) * 5 in`
* U ms.ml:351 `unsafe_get` (région ; portée line : lignes 351 à 351) : `let p = Int32.to_int (Array1.unsafe_get c.pr i) in`
* U ms.ml:352 `unsafe_get` (région ; portée line : lignes 352 à 352) : `let dp = p * (100 - Array1.unsafe_get c.d i) in`
* U ms.ml:353 `unsafe_set` (région ; portée line : lignes 353 à 353) : `Array.unsafe_set a g (Array.unsafe_get a g + 1);`
* U ms.ml:353 `unsafe_get` (région ; portée line : lignes 353 à 353) : `Array.unsafe_set a g (Array.unsafe_get a g + 1);`
* U ms.ml:354 `unsafe_set` (région ; portée line : lignes 354 à 354) : `Array.unsafe_set a (g + 1) (Array.unsafe_get a (g + 1) + Array1.unsafe_get c.q i);`
* U ms.ml:354 `unsafe_get` (région ; portée line : lignes 354 à 354) : `Array.unsafe_set a (g + 1) (Array.unsafe_get a (g + 1) + Array1.unsafe_get c.q i);`
* U ms.ml:354 `unsafe_get` (région ; portée line : lignes 354 à 354) : `Array.unsafe_set a (g + 1) (Array.unsafe_get a (g + 1) + Array1.unsafe_get c.q i);`
* U ms.ml:355 `unsafe_set` (région ; portée line : lignes 355 à 355) : `Array.unsafe_set a (g + 2) (Array.unsafe_get a (g + 2) + p);`
* U ms.ml:355 `unsafe_get` (région ; portée line : lignes 355 à 355) : `Array.unsafe_set a (g + 2) (Array.unsafe_get a (g + 2) + p);`
* U ms.ml:356 `unsafe_set` (région ; portée line : lignes 356 à 356) : `Array.unsafe_set a (g + 3) (Array.unsafe_get a (g + 3) + dp);`
* U ms.ml:356 `unsafe_get` (région ; portée line : lignes 356 à 356) : `Array.unsafe_set a (g + 3) (Array.unsafe_get a (g + 3) + dp);`
* U ms.ml:357 `unsafe_set` (région ; portée line : lignes 357 à 357) : `Array.unsafe_set a (g + 4) (Array.unsafe_get a (g + 4) + (dp * (100 + Array1.unsafe_get c.t i)))`
* U ms.ml:357 `unsafe_get` (région ; portée line : lignes 357 à 357) : `Array.unsafe_set a (g + 4) (Array.unsafe_get a (g + 4) + (dp * (100 + Array1.unsafe_get c.t i)))`
* U ms.ml:357 `unsafe_get` (région ; portée line : lignes 357 à 357) : `Array.unsafe_set a (g + 4) (Array.unsafe_get a (g + 4) + (dp * (100 + Array1.unsafe_get c.t i)))`
* U ms.ml:368 `unsafe_get` (région ; portée line : lignes 368 à 368) : `let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q`
* U ms.ml:368 `unsafe_get` (région ; portée line : lignes 368 à 368) : `let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q`
* U ms.ml:368 `unsafe_get` (région ; portée line : lignes 368 à 368) : `let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q`
* U ms.ml:370 `unsafe_get` (région ; portée line : lignes 370 à 370) : `s := !s + (Int32.to_int (Array1.unsafe_get c.pr i) * d * (1 - ((x lsr 62) land 1)))`
* U ms.ml:386 `unsafe_get` (hors région ; portée line : lignes 386 à 386) : `let pm = (Int32.to_int (Array1.unsafe_get c.sd i) - 10472) asr 62 in`
* U ms.ml:387 `unsafe_get` (hors région ; portée line : lignes 387 à 387) : `let g = (Array1.unsafe_get c.rf i * 2) + Array1.unsafe_get c.ls i in`
* U ms.ml:387 `unsafe_get` (hors région ; portée line : lignes 387 à 387) : `let g = (Array1.unsafe_get c.rf i * 2) + Array1.unsafe_get c.ls i in`
* U ms.ml:388 `unsafe_get` (hors région ; portée line : lignes 388 à 388) : `let q = Array1.unsafe_get c.q i and p = Int32.to_int (Array1.unsafe_get c.pr i) in`
* U ms.ml:388 `unsafe_get` (hors région ; portée line : lignes 388 à 388) : `let q = Array1.unsafe_get c.q i and p = Int32.to_int (Array1.unsafe_get c.pr i) in`
* U ms.ml:389 `unsafe_get` (hors région ; portée line : lignes 389 à 389) : `let dp = p * (100 - Array1.unsafe_get c.d i) in`
* U ms.ml:390 `unsafe_get` (hors région ; portée line : lignes 390 à 390) : `let ch = dp * (100 + Array1.unsafe_get c.t i) in`
* U ms.ml:444 `unsafe_get` (hors région ; portée line : lignes 444 à 444) : `let key i = Int32.to_int (Array1.unsafe_get keys i) land 0xFFFFFFFF in`
* U ms.ml:472 `unsafe_get` (région ; portée line : lignes 472 à 472) : `while (let p = Array.unsafe_get tab (2 * !s) in p land cmask <> 0 && p lsr 30 <> k) do s := (!s + 1) land (cap`
* U ms.ml:474 `unsafe_set` (région ; portée line : lignes 474 à 474) : `Array.unsafe_set tab b ((k lsl 30) lor ((Array.unsafe_get tab b land cmask) + 1));`
* U ms.ml:474 `unsafe_get` (région ; portée line : lignes 474 à 474) : `Array.unsafe_set tab b ((k lsl 30) lor ((Array.unsafe_get tab b land cmask) + 1));`
* U ms.ml:475 `unsafe_set` (région ; portée line : lignes 475 à 475) : `Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + Int32.to_int (Array1.unsafe_get vals i))`
* U ms.ml:475 `unsafe_get` (région ; portée line : lignes 475 à 475) : `Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + Int32.to_int (Array1.unsafe_get vals i))`
* U ms.ml:475 `unsafe_get` (région ; portée line : lignes 475 à 475) : `Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + Int32.to_int (Array1.unsafe_get vals i))`
* U ms.ml:493 `unsafe_get` (hors région ; portée line : lignes 493 à 493) : `while Array.unsafe_get tab ((3 * !s) + 1) <> 0 && Array.unsafe_get tab (3 * !s) <> k do s := (!s + 1) land (ca`
* U ms.ml:493 `unsafe_get` (hors région ; portée line : lignes 493 à 493) : `while Array.unsafe_get tab ((3 * !s) + 1) <> 0 && Array.unsafe_get tab (3 * !s) <> k do s := (!s + 1) land (ca`
* U ms.ml:495 `unsafe_set` (hors région ; portée line : lignes 495 à 495) : `Array.unsafe_set tab b k;`
* U ms.ml:496 `unsafe_set` (hors région ; portée line : lignes 496 à 496) : `Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + 1);`
* U ms.ml:496 `unsafe_get` (hors région ; portée line : lignes 496 à 496) : `Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + 1);`
* U ms.ml:497 `unsafe_set` (hors région ; portée line : lignes 497 à 497) : `Array.unsafe_set tab (b + 2) (Array.unsafe_get tab (b + 2) + Int32.to_int (Array1.unsafe_get vals i))`
* U ms.ml:497 `unsafe_get` (hors région ; portée line : lignes 497 à 497) : `Array.unsafe_set tab (b + 2) (Array.unsafe_get tab (b + 2) + Int32.to_int (Array1.unsafe_get vals i))`
* U ms.ml:497 `unsafe_get` (hors région ; portée line : lignes 497 à 497) : `Array.unsafe_set tab (b + 2) (Array.unsafe_get tab (b + 2) + Int32.to_int (Array1.unsafe_get vals i))`
* U ms.ml:527 `unsafe_set` (hors région ; portée line : lignes 527 à 527) : `Array.unsafe_set av i !c; incr c;`
* U ms.ml:528 `unsafe_set` (hors région ; portée line : lignes 528 à 528) : `if d = 0 then (Array.unsafe_set al i (-1); Array.unsafe_set ar i (-1))`
* U ms.ml:528 `unsafe_set` (hors région ; portée line : lignes 528 à 528) : `if d = 0 then (Array.unsafe_set al i (-1); Array.unsafe_set ar i (-1))`
* U ms.ml:531 `unsafe_set` (hors région ; portée line : lignes 531 à 531) : `Array.unsafe_set al i l;`
* U ms.ml:532 `unsafe_set` (hors région ; portée line : lignes 532 à 532) : `Array.unsafe_set ar i (a_build top (d - 1) c)`
* U ms.ml:536 `unsafe_get` (hors région ; portée line : lignes 536 à 536) : `let rec a_sum i = if i < 0 then 0 else Array.unsafe_get av i + a_sum (Array.unsafe_get al i) + a_sum (Array.un`
* U ms.ml:536 `unsafe_get` (hors région ; portée line : lignes 536 à 536) : `let rec a_sum i = if i < 0 then 0 else Array.unsafe_get av i + a_sum (Array.unsafe_get al i) + a_sum (Array.un`
* U ms.ml:536 `unsafe_get` (hors région ; portée line : lignes 536 à 536) : `let rec a_sum i = if i < 0 then 0 else Array.unsafe_get av i + a_sum (Array.unsafe_get al i) + a_sum (Array.un`
* U ms.ml:542 `unsafe_set` (hors région ; portée line : lignes 542 à 542) : `Array.unsafe_set av i (q + i);`
* U ms.ml:543 `unsafe_set` (hors région ; portée line : lignes 543 à 543) : `if d = 0 then (Array.unsafe_set al i (-1); Array.unsafe_set ar i (-1); i + 1)`
* U ms.ml:543 `unsafe_set` (hors région ; portée line : lignes 543 à 543) : `if d = 0 then (Array.unsafe_set al i (-1); Array.unsafe_set ar i (-1); i + 1)`
* U ms.ml:547 `unsafe_set` (hors région ; portée line : lignes 547 à 547) : `Array.unsafe_set al i l;`
* U ms.ml:548 `unsafe_set` (hors région ; portée line : lignes 548 à 548) : `Array.unsafe_set ar i r;`
* U ms.ml:563 `unsafe_set` (région ; portée line : lignes 563 à 563) : `Array.unsafe_set av i (q + i);`
* U ms.ml:564 `unsafe_set` (région ; portée line : lignes 564 à 564) : `if !parent >= 0 then (if !right then Array.unsafe_set ar !parent i else Array.unsafe_set al !parent i);`
* U ms.ml:564 `unsafe_set` (région ; portée line : lignes 564 à 564) : `if !parent >= 0 then (if !right then Array.unsafe_set ar !parent i else Array.unsafe_set al !parent i);`
* U ms.ml:566 `unsafe_set` (région ; portée line : lignes 566 à 566) : `Array.unsafe_set stp !sp i;`
* U ms.ml:567 `unsafe_set` (région ; portée line : lignes 567 à 567) : `Array.unsafe_set std !sp (!d - 1);`
* U ms.ml:573 `unsafe_set` (région ; portée line : lignes 573 à 573) : `Array.unsafe_set al i (-1);`
* U ms.ml:574 `unsafe_set` (région ; portée line : lignes 574 à 574) : `Array.unsafe_set ar i (-1);`
* U ms.ml:578 `unsafe_get` (région ; portée line : lignes 578 à 578) : `parent := Array.unsafe_get stp !sp;`
* U ms.ml:579 `unsafe_get` (région ; portée line : lignes 579 à 579) : `d := Array.unsafe_get std !sp;`
* U ms.ml:587 `unsafe_set` (région ; portée line : lignes 587 à 587) : `Array.unsafe_set sts 0 root;`
* U ms.ml:590 `unsafe_get` (région ; portée line : lignes 590 à 590) : `let i = Array.unsafe_get sts !sp in`
* U ms.ml:591 `unsafe_get` (région ; portée line : lignes 591 à 591) : `s := !s + Array.unsafe_get av i;`
* U ms.ml:592 `unsafe_get` (région ; portée line : lignes 592 à 592) : `let l = Array.unsafe_get al i in`
* U ms.ml:594 `unsafe_set` (région ; portée line : lignes 594 à 594) : `Array.unsafe_set sts !sp (Array.unsafe_get ar i);`
* U ms.ml:594 `unsafe_get` (région ; portée line : lignes 594 à 594) : `Array.unsafe_set sts !sp (Array.unsafe_get ar i);`
* U ms.ml:595 `unsafe_set` (région ; portée line : lignes 595 à 595) : `Array.unsafe_set sts (!sp + 1) l;`
* U ms.ml:655 `unsafe_set` (région ; portée line : lignes 655 à 655) : `Array1.unsafe_set b (mid + j)`
* U ms.ml:656 `unsafe_get` (région ; portée line : lignes 656 à 656) : `(0.25 *. (((Array1.unsafe_get a (up + j) +. Array1.unsafe_get a (dn + j)) +. Array1.unsafe_get a (mid + j - 1)`
* U ms.ml:656 `unsafe_get` (région ; portée line : lignes 656 à 656) : `(0.25 *. (((Array1.unsafe_get a (up + j) +. Array1.unsafe_get a (dn + j)) +. Array1.unsafe_get a (mid + j - 1)`
* U ms.ml:656 `unsafe_get` (région ; portée line : lignes 656 à 656) : `(0.25 *. (((Array1.unsafe_get a (up + j) +. Array1.unsafe_get a (dn + j)) +. Array1.unsafe_get a (mid + j - 1)`
* U ms.ml:656 `unsafe_get` (région ; portée line : lignes 656 à 656) : `(0.25 *. (((Array1.unsafe_get a (up + j) +. Array1.unsafe_get a (dn + j)) +. Array1.unsafe_get a (mid + j - 1)`
* U ms.ml:742 `unsafe_set` (hors région ; portée line : lignes 742 à 742) : `Array.unsafe_set buf (!w land (cap10 - 1)) x;`
* U ms.ml:750 `unsafe_get` (hors région ; portée line : lignes 750 à 750) : `s := !s + Array.unsafe_get buf (!rd land (cap10 - 1));`

## bqn


## php


## js


## python


## lua


