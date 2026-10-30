import core.simd;
float16 f(float16 a, float16 b) { float16 r; asm nothrow @nogc { "vaddps %2, %1, %0" : "=v"(r) : "v"(a), "v"(b); } return r; }
