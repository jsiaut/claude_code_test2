# Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de Nim 2.2.12 (C par clang 23), cas positifs. run.sh y ajoute
# le code produit, les échecs et les recherches d'absence.
import std/[typedthreads, atomics, sysatomics, strutils, os, algorithm, sequtils]

type
  Part = object
    x, y, z: float32
    m: uint8
  Inl = object
    n: uint32
    a: array[16, float32]
  Noisy = object
    name: char
  WArg = tuple[t: int, res: ptr uint64, tid: ptr int]

var order = ""
proc `=destroy`(x: Noisy) = order.add("destroy(" & x.name & ") ")

proc sched_getcpu(): cint {.importc, header: "<sched.h>".} # observation seulement

proc worker(a: WArg) {.thread.} =
  var s = 0'u64
  for i in a.t * 1000 ..< (a.t + 1) * 1000: s += uint64(i)
  a.res[] = s
  a.tid[] = getThreadId()

var pinnedCpu: int
var go: Atomic[bool]
proc pinned(x: int) {.thread.} =
  while not go.load(moAcquire): cpuRelax()
  pinnedCpu = int(sched_getcpu())

proc gsum[T](x: openArray[T]): T =
  for v in x: result += v
proc fib(n: int): uint64 =
  var a = 0'u64
  var b = 1'u64
  for _ in 0 ..< n:
    let t = a + b
    a = b
    b = t
  a
proc mkClosure(k: int): proc (x: int): int =
  result = proc (x: int): int = x * k

proc main() =
  # A1
  var v = newSeq[Part](8)
  for e in v.mitems: e = Part(x: 1, y: 2, z: 3, m: 4)
  let stride = cast[int](addr v[1]) - cast[int](addr v[0])
  let raw = cast[ptr array[4, uint8]](addr v[0])[]
  echo "CAP;A1;1;[exécutée] seq[Part] : pas de ", stride, " o = sizeof(Part) ", sizeof(Part), " ; les 4 premiers octets du tampon sont le float32 x en ligne : ", raw.mapIt(toHex(it)).join(" ")
  # A7, A8
  echo "CAP;A7;1;[exécutée] object (n: uint32, a: array[16, float32]) : ", sizeof(Inl), " o, offsetOf(Inl, a) = ", offsetOf(Inl, a), " (tableau en ligne)"
  let b8 = newSeq[uint8](1000)
  echo "CAP;A8;1;[exécutée] uint8/int16/float32 : ", sizeof(uint8), "/", sizeof(int16), "/", sizeof(float32), " o ; seq[uint8] de 1000 éléments : ", b8.len * sizeof(uint8), " o, seq[int16] : ", 1000 * sizeof(int16), " o"
  # B1
  block:
    let a1 = Noisy(name: 'a')
    block:
      let b1 = Noisy(name: 'b')
      discard b1
    order.add("fin-portée ")
    discard a1
  let nt = toSeq(walkDir("/proc/self/task")).len
  echo "CAP;B1;1;[exécutée] ORC/ARC, destruction déterministe : ", order.strip, " ; ", nt, " fil dans /proc/self/task (aucun fil de collecteur ; le collecteur de cycles d'ORC ne parcourt que les types cycliques, --mm:arc le retire)"
  # B2 (½ : alloc/dealloc, pas d'interface d'allocateur)
  let p = alloc0(400)
  let q = cast[ptr UncheckedArray[uint32]](p)
  q[99] = 7
  echo "FACT;B2;alloc0/dealloc du tas de Nim : bloc de 400 o, q[99] = ", q[99]
  dealloc(p)
  # B3
  var local: array[4096, uint8]
  local[0] = 1
  var marker = local[0]
  let ds = abs(cast[int](addr marker) - cast[int](addr local))
  let dh = abs(cast[int](unsafeAddr b8[0]) - cast[int](addr local))
  echo "CAP;B3;1;[exécutée] array[4096, uint8] local à ", ds, " o d'une autre variable locale, à ", dh, " o du tas : sur la pile"
  # B4 (½ : allocations implicites)
  let s0 = getAllocStats()
  let cl = mkClosure(3)
  let s1 = getAllocStats()
  var st = "ab"
  st.add($cl(3))
  let s2 = getAllocStats()
  let sq = @[1, 2, 3]
  let s3 = getAllocStats()
  echo "CAP;B4;0.5;[exécutée] getAllocStats (-d:nimAllocStats) : fermeture qui capture ", $(s1 - s0), ", ajout à une chaîne ", $(s2 - s1), ", littéral de seq @[1, 2, 3] ", $(s3 - s2), " (", st, ", ", sq.len, ") : allocations implicites"
  # B5
  var buf: array[8, uint32]
  let mp = cast[ptr UncheckedArray[uint32]](addr buf[0])
  mp[3] = 42
  let bp = cast[int](addr buf[0])
  cast[ptr uint32](bp + 16)[] = 7
  echo "CAP;B5;1;[exécutée] ptr UncheckedArray[uint32] : mp[3] = 42 -> buf[3] = ", buf[3], " ; écriture par décalage d'octets -> buf[4] = ", buf[4]
  # D1
  var parts: array[4, uint64]
  var tids: array[4, int]
  var th: array[4, Thread[WArg]]
  for t in 0 ..< 4: createThread(th[t], worker, (t, addr parts[t], addr tids[t]))
  joinThreads(th)
  echo "CAP;D1;1;[exécutée] std/typedthreads : 4 fils, ", tids.toSeq.deduplicate.len, " identifiants de fil (getThreadId) distincts, somme ", parts.foldl(a + b), " (attendu 7998000)"
  # D4
  var pt: Thread[int]
  createThread(pt, pinned, 0)
  pinToCpu(pt, 1)
  go.store(true, moRelease)
  joinThread(pt)
  echo "FACT;D4;Thread.pinToCpu(t, 1) : sched_getcpu() dans le fil = ", pinnedCpu
  # E2
  var ex = 41
  asm """
    addq $1, %0
    : "+r"(`ex`)
  """
  echo "CAP;E2;1;[exécutée] instruction asm (assembleur étendu de GCC, variables Nim entre accents graves) : 41 -> ", ex
  # E7, F1, F3
  const F60 = fib(60)
  echo "FACT;E7;const F60 = fib(60) évalué par la VM du compilateur = ", F60, " ; gsum[float32] = ", gsum([1.5'f32, 2.5]), ", gsum[float64] = ", gsum([1.5, 2.25])
  var m: array[3, array[4, float32]]
  echo "FACT;F1;array[3, array[4, float32]] contigu : &m[1][0] - &m[0][3] = ", cast[int](addr m[1][0]) - cast[int](addr m[0][3]), " o, sizeof = ", sizeof(m), " o"
  let um = high(uint32)
  let c250 = 250'u8
  echo "CAP;F3;1;[exécutée] high(uint32) + 1 = ", um + 1, ", high(int32) +% 1 = ", high(int32) +% 1, ", 250'u8 + 10 = ", c250 + 10, " (non signés modulaires ; +% pour les signés, qui sinon lèvent OverflowDefect)"
main()
