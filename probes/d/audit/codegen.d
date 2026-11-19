// Code produit, lu par run.sh (-O3 -mcpu=native, -output-s et -output-ll ; -boundscheck=on pour E6).
module codegen;
import core.atomic, core.simd, ldc.attributes, ldc.gccbuiltins_x86;
import core.builtins : unlikely, expect;
extern (C):
void st_release(shared(ulong)* a) { atomicStore!(MemoryOrder.rel)(*a, 1UL); }
void st_seqcst(shared(ulong)* a) { atomicStore!(MemoryOrder.seq)(*a, 1UL); }
ulong add_relaxed(shared(ulong)* a) { return atomicFetchAdd!(MemoryOrder.raw)(*a, 1UL); }
void spin(shared(ulong)* f) { while (atomicLoad!(MemoryOrder.acq)(*f) == 0) pause(); atomicFence(); }
void axpy(@restrict float* a, @restrict float* b, size_t n) { foreach (i; 0 .. n) a[i] += 2 * b[i]; }
float idx_checked(float[] a, size_t i) { return a[i]; }
float idx_unchecked(float[] a, size_t i) { return a.ptr[i]; }
void ext(ulong x);
ulong hinted(ulong x) { ulong r = x; if (expect(x == 7, false)) { ext(x); r = x * 5; } return r + 1; }
ulong hinted_unl(ulong x) { ulong r = x; if (unlikely(x == 10)) { ext(x); r = x * 9; } return r + 4; }
ulong unhinted(ulong x) { ulong r = x; if (x == 9) { ext(x); r = x * 7; } return r + 3; }
void pf(void* p) { prefetch!(false, 3)(p); }
float sum_plain(const(float)* a, size_t n) { float s = 0; foreach (i; 0 .. n) s += a[i]; return s; }
@fastmath float sum_fast(const(float)* a, size_t n) { float s = 0; foreach (i; 0 .. n) s += a[i]; return s; }
int16 tern(int16 a, int16 b, int16 c) { return __builtin_ia32_pternlogd512(a, b, c, 0x96); }
ulong fib(ulong n) { ulong a = 0, b = 1; foreach (_; 0 .. n) { auto t = a + b; a = b; b = t; } return a; }
ulong fib60() { enum F = fib(60); return F; }
extern (D) pragma(inline, false) T gsum(T)(const(T)[] x) { T s = 0; foreach (v; x) s += v; return s; }
double use_both(const(float)[] a, const(double)[] b) { return gsum(a) + gsum(b); }
