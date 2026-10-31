// C2 : un intrinsèque à opérande immédiat (macro de immintrin.h) peut-il s'importer ?
use CTypes;
require "immintrin.h";
extern type __m512;
extern proc _mm512_setzero_ps(): __m512;
extern proc _mm512_cmp_ps_mask(a: __m512, b: __m512, imm: c_int): uint(16);
proc main() { var x = _mm512_setzero_ps(); writeln(_mm512_cmp_ps_mask(x, x, 0: c_int)); }
