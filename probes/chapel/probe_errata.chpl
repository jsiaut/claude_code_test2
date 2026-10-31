// Sonde des errata de la remarque sur Chapel (docs/CHAPEL.md) : B2, C2, E5 (et B3, C4 : textes corrigés).
// IR et cas qui échouent : tools/chapel_check/, results/chapel_check/.
use Allocators, CTypes;
require "immintrin.h";
extern type __m512;
extern proc _mm512_set1_ps(x: real(32)): __m512;
extern proc _mm512_fmadd_ps(a: __m512, b: __m512, c: __m512): __m512;
extern proc _mm512_reduce_add_ps(a: __m512): real(32);
class Node { var v: int; }
proc main() {
  var pool = new bumpPtrMemPool(1 << 16);
  var n = newWithAllocator(pool, unmanaged Node, 7);
  writeln("CAP;B2;0.5;Allocators (instable) : bumpPtrMemPool + newWithAllocator, v = ", n.v);
  const x = _mm512_set1_ps(2.0: real(32));
  writeln("CAP;C2;0.5;_mm512_fmadd_ps importé de immintrin.h : somme = ", _mm512_reduce_add_ps(_mm512_fmadd_ps(x, x, x)),
          " (macros à immédiat et builtins : refusés)");
  var t: c_array(real, 4);
  for i in 0..<4 do t[i] = i;
  writeln("CAP;B3;0.5;c_array local (pile) : ", t[3], " ; tableaux Chapel sur le tas");
  writeln("CAP;C4;0.5;@llvm.metadata((\"llvm.loop.vectorize.enable\", true)) par boucle (instable)");
  var a, b: [0..<64] real = 1.0;
  foreach i in a.domain do a[i] += b[i];
  writeln("CAP;E5;0.5;foreach (instable) : llvm.loop.parallel_accesses ; noalias automatique, a[0] = ", a[0]);
}
