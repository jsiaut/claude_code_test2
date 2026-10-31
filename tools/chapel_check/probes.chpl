// Sondes de la remarque sur Chapel (docs/CHAPEL.md) : B2 (Allocators), C2 (intrinsèques importées),
// B3 (c_array contre tableau local), C4 (attribut de boucle llvm.loop.vectorize.enable). Chapel 2.10.0.
use Allocators, CTypes, Time;
require "immintrin.h";
extern type __m512;
extern proc _mm512_loadu_ps(p: c_ptr(real(32))): __m512;
extern proc _mm512_setzero_ps(): __m512;
extern proc _mm512_fmadd_ps(a: __m512, b: __m512, c: __m512): __m512;
extern proc _mm512_reduce_add_ps(a: __m512): real(32);

config const nCalls = 2_000_000, inner = 1 << 16;

class Node { var v: int; var l, r: unmanaged Node?; }

proc dotIntrin(ref a: [] real(32), ref b: [] real(32)): real(32) {
  var acc = _mm512_setzero_ps();
  for i in 0..<a.size by 16 do
    acc = _mm512_fmadd_ps(_mm512_loadu_ps(c_ptrTo(a[i])), _mm512_loadu_ps(c_ptrTo(b[i])), acc);
  return _mm512_reduce_add_ps(acc);
}

proc dotStrict(const ref a: [] real(32), const ref b: [] real(32)): real(32) {
  var s = 0.0: real(32);
  for i in a.domain do s += a[i] * b[i];
  return s;
}

proc dotAttr(const ref a: [] real(32), const ref b: [] real(32)): real(32) {
  var s = 0.0: real(32);
  @llvm.metadata(("llvm.loop.vectorize.enable", true))
  for i in a.domain do s += a[i] * b[i];
  return s;
}

proc localArray(x: real): real {
  var t: [0..15] real;
  for i in 0..15 do t[i] = x + i;
  var s = 0.0;
  for i in 0..15 do s += t[i];
  return s;
}

proc localCArray(x: real): real {
  var t: c_array(real, 16);
  for i in 0..15 do t[i] = x + i;
  var s = 0.0;
  for i in 0..15 do s += t[i];
  return s;
}

proc main() {
  var pool = new bumpPtrMemPool(1 << 20);
  var n = newWithAllocator(pool, unmanaged Node, 42, nil, nil);
  writeln("B2 : Allocators (bumpPtrMemPool + newWithAllocator) : v = ", n.v);

  var a: [0..<2048] real(32), b: [0..<2048] real(32);
  for i in 0..<2048 { a[i] = ((i * 37) % 101): real(32) / 101; b[i] = ((i * 53) % 97): real(32) / 97; }
  writeln("C2 : _mm512_fmadd_ps importé : ", dotIntrin(a, b), " (strict : ", dotStrict(a, b), ")");

  var sw = new stopwatch(), acc = 0.0: real(32);
  sw.start(); for r in 1..inner { a[0] = r: real(32) * 1e-9; acc += dotStrict(a, b); } sw.stop();
  const tStrict = sw.elapsed(); sw.clear();
  sw.start(); for r in 1..inner { a[0] = r: real(32) * 1e-9; acc += dotAttr(a, b); } sw.stop();
  const tAttr = sw.elapsed(); sw.clear();
  sw.start(); for r in 1..inner { a[0] = r: real(32) * 1e-9; acc += dotIntrin(a, b); } sw.stop();
  const tIntrin = sw.elapsed(); sw.clear();
  writeln("C4 : K5 (2^16 produits de 2048) : strict ", tStrict * 1e3, " ms ; attribut de boucle ", tAttr * 1e3,
          " ms ; intrinsèques ", tIntrin * 1e3, " ms (", acc, ")");

  var s = 0.0;
  sw.start(); for i in 1..nCalls do s += localArray(i: real); sw.stop();
  const tArr = sw.elapsed(); sw.clear();
  sw.start(); for i in 1..nCalls do s += localCArray(i: real); sw.stop();
  const tC = sw.elapsed();
  writeln("B3 : tableau local ", tArr * 1e9 / nCalls, " ns par appel ; c_array ", tC * 1e9 / nCalls, " ns par appel (", s, ")");
}
