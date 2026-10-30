#include <immintrin.h>
__attribute__((target("avx512f,avx512vnni")))
__m512i dp(__m512i acc, __m512i a, __m512i b) { return _mm512_dpbusd_epi32(acc, a, b); }
__attribute__((target("avx512f")))
__m512 add(__m512 a, __m512 b) { return _mm512_add_ps(a, b); }
int main(void){ return 0; }
