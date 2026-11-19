# Code produit, lu par run.sh (désassemblage du binaire et C généré dans nimcache), mêmes options que le banc.
import std/[atomics, sysatomics]
import fastsum

type M512i {.importc: "__m512i", header: "immintrin.h".} = object
proc mm512_set1(x: cint): M512i {.importc: "_mm512_set1_epi32", header: "immintrin.h".}
proc mm512_ternlog(a, b, c: M512i, imm: cint): M512i {.importc: "_mm512_ternarylogic_epi32", header: "immintrin.h".}
proc mm512_cvt(a: M512i): cint {.importc: "_mm512_cvtsi512_si32", header: "immintrin.h".}
proc builtinPrefetch(p: pointer, rw, loc: cint) {.importc: "__builtin_prefetch", nodecl.}
proc ext(x: uint64) {.importc: "ext_hook", nodecl.}
{.emit: """__attribute__((noinline)) void ext_hook(unsigned long long x) { __asm__ volatile("" :: "r"(x)); }""".}

proc st_release(a: var Atomic[uint64]) {.exportc: "st_release", noinline.} = a.store(1, moRelease)
proc st_seqcst(a: var Atomic[uint64]) {.exportc: "st_seqcst", noinline.} = a.store(1, moSequentiallyConsistent)
proc add_relaxed(a: var Atomic[uint64]): uint64 {.exportc: "add_relaxed", noinline.} = a.fetchAdd(1, moRelaxed)
proc spin(f: var Atomic[uint64]) {.exportc: "spin", noinline.} =
  while f.load(moAcquire) == 0: cpuRelax()
  fence(moSequentiallyConsistent)
proc axpy(a {.noalias.}: ptr UncheckedArray[float32], b {.noalias.}: ptr UncheckedArray[float32], n: int) {.exportc: "axpy", noinline.} =
  for i in 0 ..< n: a[i] += 2 * b[i]
proc idx_checked(a: seq[float32], i: int): float32 {.exportc: "idx_checked", noinline.} = a[i]
{.push boundChecks: off.}
proc idx_unchecked(a: seq[float32], i: int): float32 {.exportc: "idx_unchecked", noinline.} = a[i]
{.pop.}
proc hinted(x: uint64): uint64 {.exportc: "hinted", noinline.} =
  var r = x
  if unlikely(x == 7):
    ext(x)
    r = x * 5
  r + 1
proc unhinted(x: uint64): uint64 {.exportc: "unhinted", noinline.} =
  var r = x
  if x == 9:
    ext(x)
    r = x * 7
  r + 3
proc pf(p: pointer) {.exportc: "pf", noinline.} = builtinPrefetch(p, 0, 3)
proc tern(k: cint): cint {.exportc: "tern", noinline.} =
  mm512_cvt(mm512_ternlog(mm512_set1(12 * k), mm512_set1(10 * k), mm512_set1(k), 0x96))
proc sum_plain(a: ptr UncheckedArray[float32], n: int): float32 {.exportc: "sum_plain", noinline.} =
  for i in 0 ..< n: result += a[i]
proc fib(n: int): uint64 =
  var a = 0'u64
  var b = 1'u64
  for _ in 0 ..< n:
    let t = a + b
    a = b
    b = t
  a
proc fib60(): uint64 {.exportc: "fib60", noinline.} =
  const F = fib(60)
  F
proc gsum[T](x: openArray[T]): T {.noinline.} =
  for v in x: result += v
proc use_both(a: seq[float32], b: seq[float64]): float64 {.exportc: "use_both", noinline.} = float64(gsum(a)) + gsum(b)

var at: Atomic[uint64]
st_release(at); st_seqcst(at); discard add_relaxed(at); spin(at)
var xs = newSeq[float32](64)
var ys = newSeq[float64](64)
axpy(cast[ptr UncheckedArray[float32]](addr xs[0]), cast[ptr UncheckedArray[float32]](addr xs[0]), 64)
echo idx_checked(xs, 3) + idx_unchecked(xs, 3), " ", hinted(7), " ", unhinted(9), " ", tern(1), " ", sum_plain(cast[ptr UncheckedArray[float32]](addr xs[0]), 64), " ", sum_fast(cast[ptr UncheckedArray[float32]](addr xs[0]), 64), " ", fib60(), " ", use_both(xs, ys)
pf(addr xs[0])
