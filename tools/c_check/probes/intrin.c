/* Sonde : _mm_prefetch et _mm_pause viennent du même <immintrin.h> que les intrinsèques AVX-512 (C2), en C23 strict */
#include <immintrin.h>
int main(void) {
    static float buf[64];
    _mm_prefetch((const char *)buf, _MM_HINT_T0);
    _mm_pause();
    __m512 v = _mm512_loadu_ps(buf);
    return (int)_mm512_reduce_add_ps(v);
}
