// Code produit, lu par run.sh (--emit-asm et --emit-llvm, -O3 ; -O1, mode sûr, pour E6).
module codegen;
import std::atomic, std::thread;
fn void st_release(Atomic{ulong}* a) @export @cname("st_release") { a.store(1, RELEASE); }
fn void st_seqcst(Atomic{ulong}* a) @export @cname("st_seqcst") { a.store(1, SEQ_CONSISTENT); }
fn ulong add_relaxed(Atomic{ulong}* a) @export @cname("add_relaxed") { return a.add(1, RELAXED); }
fn void spin(Atomic{ulong}* f) @export @cname("spin") { while (f.load(ACQUIRE) == 0) {} thread::fence(SEQ_CONSISTENT); }
fn void axpy(float* a @noalias, float* b, sz n) @export @cname("axpy") { for (sz i = 0; i < n; i++) a[i] += 2 * b[i]; }
fn void axpy2(float* a, float* b @noalias, sz n) @export @cname("axpy2") { for (sz i = 0; i < n; i++) a[i] += 2 * b[i]; }
fn float idx_checked(float[] a, sz i) @export @cname("idx_checked") { return a[i]; }
fn float idx_unchecked(float[] a, sz i) @export @cname("idx_unchecked") { return a.ptr[i]; }
extern fn void ext(ulong x) @cname("ext");
fn ulong hinted(ulong x) @export @cname("hinted") { ulong r = x; if (@unlikely(x == 7)) { ext(x); r = x * 5; } return r + 1; }
fn ulong unhinted(ulong x) @export @cname("unhinted") { ulong r = x; if (x == 9) { ext(x); r = x * 7; } return r + 3; }
fn void pf(void* p) @export @cname("pf") { @prefetch(p, VERY_NEAR, false); }
fn float sum_plain(float* a, sz n) @export @cname("sum_plain") { float s; for (sz i = 0; i < n; i++) s += a[i]; return s; }
extern fn void cpu_pause() @cname("llvm.x86.sse2.pause");
fn void relax() @export @cname("relax") { cpu_pause(); }
macro ulong @fib($n)
{
	var $a = (ulong)0;
	var $b = (ulong)1;
	$for var $i = 0; $i < $n; $i++:
		var $t = $a + $b;
		$a = $b;
		$b = $t;
	$endfor
	return $a;
}
fn ulong fib60() @export @cname("fib60") { return @fib(60); }
fn Type gsum(Type[] x) <Type> @noinline { Type s; foreach (v : x) s += v; return s; }
fn double use_both(float[] a, double[] b) @export @cname("use_both") { return (double)gsum{float}(a) + gsum{double}(b); }
