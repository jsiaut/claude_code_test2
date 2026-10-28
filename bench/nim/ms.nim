# Implémentation Nim 2.2.12 (bibliothèque standard ; intrinsèques via importc). Voir docs/SPEC.md.
import std/[monotimes, times, os, strutils, strformat, tables, atomics, typedthreads, algorithm, volatile]

# ------------------------------------------------------------------ harnais
var WARMUP = 1
var DATA = "/opt/msdata"

proc aligned_alloc(al, size: csize_t): pointer {.importc, header: "<stdlib.h>".}
proc cfree(p: pointer) {.importc: "free", header: "<stdlib.h>".}

type Buf[T] = object
  p: ptr UncheckedArray[T]
  len: int

proc load[T](name: string): Buf[T] =
  let s = readFile(DATA & "/" & name)
  result.p = cast[ptr UncheckedArray[T]](aligned_alloc(64, csize_t((s.len + 63) and not 63)))
  copyMem(result.p, s[0].unsafeAddr, s.len)
  result.len = s.len div sizeof(T)

proc result(k, v, p: string, rep: int, sec: float, chk: string) =
  stdout.write(&"RESULT;{k};{v};{p};{rep};{sec:.9f};{chk}\n")
  stdout.flushFile()
proc secs(t0: MonoTime): float = (getMonoTime() - t0).inNanoseconds.float * 1e-9

# Intrinsèques AVX-512 importées depuis immintrin.h (mécanisme natif de Nim pour le SIMD)
type
  M512 {.importc: "__m512", header: "<immintrin.h>".} = object
  M512d {.importc: "__m512d", header: "<immintrin.h>".} = object
  M256 {.importc: "__m256", header: "<immintrin.h>".} = object
proc mm512_setzero_ps(): M512 {.importc: "_mm512_setzero_ps", header: "<immintrin.h>".}
proc mm512_setzero_pd(): M512d {.importc: "_mm512_setzero_pd", header: "<immintrin.h>".}
proc mm512_set1_ps(x: float32): M512 {.importc: "_mm512_set1_ps", header: "<immintrin.h>".}
proc mm512_load_ps(p: pointer): M512 {.importc: "_mm512_load_ps", header: "<immintrin.h>".}
proc mm512_mul_ps(a, b: M512): M512 {.importc: "_mm512_mul_ps", header: "<immintrin.h>".}
proc mm512_add_ps(a, b: M512): M512 {.importc: "_mm512_add_ps", header: "<immintrin.h>".}
proc mm512_fmadd_ps(a, b, c: M512): M512 {.importc: "_mm512_fmadd_ps", header: "<immintrin.h>".}
proc mm512_reduce_add_ps(a: M512): float32 {.importc: "_mm512_reduce_add_ps", header: "<immintrin.h>".}
proc mm512_add_pd(a, b: M512d): M512d {.importc: "_mm512_add_pd", header: "<immintrin.h>".}
proc mm512_cvtps_pd(a: M256): M512d {.importc: "_mm512_cvtps_pd", header: "<immintrin.h>".}
proc mm512_castps512_ps256(a: M512): M256 {.importc: "_mm512_castps512_ps256", header: "<immintrin.h>".}
proc mm512_extractf32x8_ps(a: M512, i: cint): M256 {.importc: "_mm512_extractf32x8_ps", header: "<immintrin.h>".}
proc mm512_reduce_add_pd(a: M512d): float {.importc: "_mm512_reduce_add_pd", header: "<immintrin.h>".}
proc prefetchw(p: pointer) {.importc: "__builtin_prefetch", header: "<stddef.h>", varargs.}
proc cpuRelax() {.importc: "_mm_pause", header: "<immintrin.h>".}

# ------------------------------------------------------------------ K1
const N1 = 1 shl 22
type Particle = object
  x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density: float32

proc k1Natural(ps: seq[Particle]): float {.noinline.} =
  for p in ps: result += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)

{.push boundChecks: off, overflowChecks: off.}
proc k1AoS(ps: seq[Particle]): float {.noinline.} =
  var acc: array[8, float]
  var i = 0
  while i < ps.len:
    for k in 0 ..< 8:
      let q = ps[i + k].addr
      acc[k] += float(0.5'f32 * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz))
    i += 8
  for a in acc: result += a

proc k1SoA(vx, vy, vz, m: ptr UncheckedArray[float32], n: int): float {.noinline.} =
  var a0 = mm512_setzero_pd()
  var a1 = mm512_setzero_pd()
  let h = mm512_set1_ps(0.5)
  var i = 0
  while i < n:
    let x = mm512_load_ps(vx[i].addr)
    let y = mm512_load_ps(vy[i].addr)
    let z = mm512_load_ps(vz[i].addr)
    let w = mm512_load_ps(m[i].addr)
    let e = mm512_mul_ps(mm512_mul_ps(h, w), mm512_fmadd_ps(z, z, mm512_fmadd_ps(y, y, mm512_mul_ps(x, x))))
    a0 = mm512_add_pd(a0, mm512_cvtps_pd(mm512_castps512_ps256(e)))
    a1 = mm512_add_pd(a1, mm512_cvtps_pd(mm512_extractf32x8_ps(e, 1)))
    i += 16
  result = mm512_reduce_add_pd(mm512_add_pd(a0, a1))
{.pop.}

proc rssNow(): int =
  ## Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)
  ## (readFile se fie à la taille du fichier, nulle sous /proc : on lit une ligne)
  try:
    let f = open("/proc/self/statm")
    defer: f.close()
    f.readLine().splitWhitespace()[1].parseInt * 4096
  except CatchableError: 0

proc runK1(v: string, reps: int) =
  if v == "footprint0":
    result("k1", v, "energy", 0, 0, "0"); return
  let raw = load[float32]("k1_particles.f32")
  if v == "footprint_raw":
    result("k1", v, "energy", 0, 0, "0"); return
  let m1 = if v == "footprint": rssNow() else: 0  # P1 : tampon brut chargé
  let o1 = getOccupiedMem()
  var ps = newSeq[Particle](N1)
  for i in 0 ..< N1: copyMem(ps[i].addr, raw.p[16 * i].addr, sizeof(Particle))
  if v == "footprint":
    let m2 = rssNow()  # P2 : collection construite, tampon brut encore vivant
    # l'allocateur de Nim garde le tampon transitoire du chargement et le réutilise : le RSS ne voit pas
    # la collection ; on compte donc les octets occupés selon l'allocateur (getOccupiedMem)
    echo &"META;mem;live;{o1};{getOccupiedMem()}\nMETA;rss;{m1};{m2}\nMETA;raw0;{raw.p[0]}"
    cfree(raw.p); result("k1", v, "energy", 0, 0, &"{k1Natural(ps):.6f}"); return
  if v == "soa":
    var c: array[16, ptr UncheckedArray[float32]]
    for k in 0 ..< 16:
      c[k] = cast[ptr UncheckedArray[float32]](aligned_alloc(64, csize_t(N1 * 4)))
      for i in 0 ..< N1: c[k][i] = raw.p[16 * i + k]
    for r in -WARMUP ..< reps:
      let t0 = getMonoTime()
      let e = k1SoA(c[3], c[4], c[5], c[9], N1)
      let dt = secs(t0)
      if r >= 0: result("k1", v, "energy", r, dt, &"{e:.6f}")
    return
  if v == "natural_shuffled":
    let perm = load[uint32]("k1_perm.u32")
    var s = newSeq[Particle](N1)
    for i in 0 ..< N1: s[i] = ps[perm.p[i]]
    ps = s
  let aos = v == "aos"
  for r in -WARMUP ..< reps:
    let t0 = getMonoTime()
    let e = if aos: k1AoS(ps) else: k1Natural(ps)
    let dt = secs(t0)
    if r >= 0: result("k1", v, "energy", r, dt, &"{e:.6f}")

# ------------------------------------------------------------------ K2
{.push boundChecks: off.}
proc k2Chase(a: ptr UncheckedArray[uint32], h: int): uint32 {.noinline.} =
  var i = 0'u32
  for _ in 0 ..< h: i = a[i]
  i
{.pop.}
proc runK2(v: string, reps: int, p: string) =
  let a = load[uint32](&"k2_chase_{p}.u32")
  for r in -WARMUP ..< reps:
    let t0 = getMonoTime()
    let i = k2Chase(a.p, 4200000)
    let dt = secs(t0)
    if r >= 0: result("k2", v, p, r, dt, $i)

# ------------------------------------------------------------------ K3
const ITER3 = 1 shl 25
type
  Padded = object
    v {.align(128).}: Atomic[uint64]
  K3Arg = tuple[c: ptr Atomic[uint64], rmw: bool]
proc k3Worker(a: K3Arg) {.thread.} =
  if a.rmw:
    for _ in 0 ..< ITER3: discard a.c[].fetchAdd(1, moRelaxed)
  else:
    for _ in 0 ..< ITER3: a.c[].store(a.c[].load(moRelaxed) + 1, moRelaxed)
proc runK3(v: string, reps: int) =
  let rmw = v.startsWith("rmw")
  let padded = v.endsWith("padded")
  echo "META;k3_mechanism;", (if rmw: "fetchAdd(moRelaxed) (lock xadd)" else: "load/store(moRelaxed) (mov)")
  var pad: array[4, Padded]
  var packed {.align(64).}: array[4, Atomic[uint64]]
  for r in -WARMUP ..< reps:
    var ctr: array[4, ptr Atomic[uint64]]
    for t in 0 ..< 4:
      ctr[t] = if padded: pad[t].v.addr else: packed[t].addr
      ctr[t][].store(0)
    let t0 = getMonoTime()
    var th: array[4, Thread[K3Arg]]
    for t in 0 ..< 4: createThread(th[t], k3Worker, (ctr[t], rmw))
    joinThreads(th)
    let dt = secs(t0)
    var s = 0'u64
    for c in ctr: s += c[].load()
    if r >= 0: result("k3", v, "4x2^25", r, dt, $s)

# ------------------------------------------------------------------ K4
proc k4Natural(v: seq[uint8]): uint64 {.noinline.} =
  for x in v:
    if x >= 128: result += x
proc k4Branchless(v: seq[uint8]): uint64 {.noinline.} =
  for x in v: result += uint64(x) * uint64(x shr 7)
proc runK4(v: string, reps: int) =
  let b = load[uint8]("k4_bytes.u8")
  var d = newSeq[uint8](b.len)
  copyMem(d[0].addr, b.p, b.len)
  if v == "natural_sorted": d.sort()
  let bl = v == "branchless_unsorted"
  for r in -WARMUP ..< reps:
    let t0 = getMonoTime()
    let s = if bl: k4Branchless(d) else: k4Natural(d)
    let dt = secs(t0)
    if r >= 0: result("k4", v, "16M", r, dt, $s)

# ------------------------------------------------------------------ K5
const INNER5 = 1 shl 16
proc k5Natural(a, b: ptr UncheckedArray[float32], n: int): float32 {.noinline.} =
  for i in 0 ..< n: result += a[i] * b[i]
proc k5Tuned(a, b: ptr UncheckedArray[float32], n: int): float32 {.noinline.} =
  var s0 = mm512_setzero_ps()
  var s1 = s0
  var s2 = s0
  var s3 = s0
  var i = 0
  while i < n:
    s0 = mm512_fmadd_ps(mm512_load_ps(a[i].addr), mm512_load_ps(b[i].addr), s0)
    s1 = mm512_fmadd_ps(mm512_load_ps(a[i + 16].addr), mm512_load_ps(b[i + 16].addr), s1)
    s2 = mm512_fmadd_ps(mm512_load_ps(a[i + 32].addr), mm512_load_ps(b[i + 32].addr), s2)
    s3 = mm512_fmadd_ps(mm512_load_ps(a[i + 48].addr), mm512_load_ps(b[i + 48].addr), s3)
    i += 64
  mm512_reduce_add_ps(mm512_add_ps(mm512_add_ps(s0, s1), mm512_add_ps(s2, s3)))
var sinkA: ptr UncheckedArray[float32]
proc runK5(v: string, reps: int) =
  let a = load[float32]("k5_a.f32")
  let b = load[float32]("k5_b.f32")
  let tuned = v == "tuned"
  for r in -WARMUP ..< reps:
    var d = 0'f32
    let t0 = getMonoTime()
    for _ in 0 ..< INNER5:
      volatileStore(sinkA.addr, a.p) # barrière d'optimisation
      let pa = volatileLoad(sinkA.addr)
      d = if tuned: k5Tuned(pa, b.p, a.len) else: k5Natural(pa, b.p, a.len)
    let dt = secs(t0)
    if r >= 0: result("k5", v, "2048x65536", r, dt, &"{d:.4f}")

# ------------------------------------------------------------------ K6
const N6 = 1 shl 24
type
  Cols = object
    sd, pr: ptr UncheckedArray[int32]
    q, d, t, rf, ls: ptr UncheckedArray[uint8]
  Q1Acc = array[6, array[5, int64]]
proc q6Natural(c: Cols, lo, hi: int): int64 {.noinline.} =
  for i in lo ..< hi:
    if c.sd[i] >= 8766 and c.sd[i] < 9131 and c.d[i] >= 5 and c.d[i] <= 7 and c.q[i] < 24:
      result += int64(c.pr[i]) * int64(c.d[i])
{.push boundChecks: off, overflowChecks: off.}
proc q6Tuned(c: Cols, lo, hi: int): int64 {.noinline.} =
  for i in lo ..< hi:
    let m = int64(uint32(c.sd[i] - 8766) < 365'u32) and int64(uint8(c.d[i] - 5) <= 2'u8) and int64(c.q[i] < 24)
    result += int64(c.pr[i] * int32(c.d[i])) and -m
{.pop.}
proc q1Natural(c: Cols, lo, hi: int, acc: var Q1Acc) {.noinline.} =
  for i in lo ..< hi:
    if c.sd[i] <= 10471:
      let g = int(c.rf[i]) * 2 + int(c.ls[i])
      let p = int64(c.pr[i])
      let dp = p * (100 - int64(c.d[i]))
      acc[g][0] += 1
      acc[g][1] += int64(c.q[i])
      acc[g][2] += p
      acc[g][3] += dp
      acc[g][4] += dp * (100 + int64(c.t[i]))
{.push boundChecks: off, overflowChecks: off.}
# Q1 optimisé : agrégation masquée par groupe sur blocs (le compilateur C vectorise)
proc q1Tuned(c: Cols, lo, hi: int, acc: var Q1Acc) {.noinline.} =
  const B = 4096
  var b0 = lo
  while b0 < hi:
    let b1 = min(b0 + B, hi)
    for g in 0'i32 ..< 6'i32:
      var cnt, sq, sp, sdp: int32
      var sch: int64
      for i in b0 ..< b1:
        let m = -(int32(c.sd[i] <= 10471) and int32(int32(c.rf[i]) * 2 + int32(c.ls[i]) == g))
        let dp = c.pr[i] * (100 - int32(c.d[i]))
        cnt -= m
        sq += int32(c.q[i]) and m
        sp += c.pr[i] and m
        sdp += dp and m
        sch += int64(dp and m) * (100 + int64(c.t[i]))
      acc[g][0] += cnt; acc[g][1] += sq; acc[g][2] += sp; acc[g][3] += sdp; acc[g][4] += sch
    b0 = b1
{.pop.}
proc fold(a: Q1Acc): int64 =
  for row in a:
    for x in row: result += x
type K6Job = tuple[c: Cols, lo, hi: int, q1: bool, res: ptr int64]
proc k6Worker(j: K6Job) {.thread.} =
  if j.q1:
    var a: Q1Acc
    q1Tuned(j.c, j.lo, j.hi, a)
    j.res[] = fold(a)
  else: j.res[] = q6Tuned(j.c, j.lo, j.hi)
proc runK6(v: string, reps: int, p: string) =
  let c = Cols(sd: load[int32]("k6_shipdate.i32").p, pr: load[int32]("k6_extendedprice.i32").p, q: load[uint8]("k6_quantity.u8").p,
               d: load[uint8]("k6_discount.u8").p, t: load[uint8]("k6_tax.u8").p, rf: load[uint8]("k6_returnflag.u8").p,
               ls: load[uint8]("k6_linestatus.u8").p)
  let q1 = p == "q1"
  for r in -WARMUP ..< reps:
    let t0 = getMonoTime()
    var s = 0'i64
    if v == "mt":
      var part: array[4, int64]
      var th: array[4, Thread[K6Job]]
      for t in 0 ..< 4: createThread(th[t], k6Worker, (c, N6 div 4 * t, N6 div 4 * (t + 1), q1, part[t].addr))
      joinThreads(th)
      for x in part: s += x
    elif v == "tuned":
      if q1:
        var a: Q1Acc
        q1Tuned(c, 0, N6, a); s = fold(a)
      else: s = q6Tuned(c, 0, N6)
    else:
      if q1:
        var a: Q1Acc
        q1Natural(c, 0, N6, a); s = fold(a)
      else: s = q6Natural(c, 0, N6)
    let dt = secs(t0)
    if r >= 0: result("k6", v, p, r, dt, $s)

# ------------------------------------------------------------------ K7
type
  Agg = object
    count: uint32
    sum: uint64
  Slot = object
    key, count: uint32
    sum: uint64
proc runK7(v: string, reps: int) =
  let keys = load[uint32]("k7_keys.u32")
  let vals = load[uint32]("k7_vals.u32")
  for r in -WARMUP ..< reps:
    var nk, ws: uint64
    var dt: float
    if v == "natural":
      let t0 = getMonoTime()
      var m = initTable[uint32, Agg]()
      for i in 0 ..< keys.len:
        let e = m.mgetOrPut(keys.p[i], Agg()).addr
        e.count += 1
        e.sum += vals.p[i]
      dt = secs(t0)
      nk = uint64(m.len)
      for k, e in m: ws += e.sum * uint64((k and 1023) + 1)
    else:
      const LOG = 21
      const CAP = 1 shl LOG
      let t0 = getMonoTime()
      let tab = cast[ptr UncheckedArray[Slot]](aligned_alloc(64, csize_t(CAP * sizeof(Slot))))
      zeroMem(tab, CAP * sizeof(Slot))
      {.push boundChecks: off, overflowChecks: off.}
      var i = 0
      while i < keys.len:
        var h: array[16, uint32]
        for b in 0 ..< 16:
          h[b] = (keys.p[i + b] * 0x9E3779B1'u32) shr (32 - LOG)
          prefetchw(tab[h[b]].addr, 1, 3)
        for b in 0 ..< 16:
          let k = keys.p[i + b]
          var s = h[b]
          while tab[s].count != 0 and tab[s].key != k: s = (s + 1) and (CAP - 1)
          tab[s].key = k
          tab[s].count += 1
          tab[s].sum += vals.p[i + b]
        i += 16
      {.pop.}
      dt = secs(t0)
      for s in 0 ..< CAP:
        if tab[s].count != 0:
          nk += 1; ws += tab[s].sum * uint64((tab[s].key and 1023) + 1)
      cfree(tab)
    if r >= 0: result("k7", v, "16M/1M", r, dt, &"{nk}:{ws}")

# ------------------------------------------------------------------ K8
type
  Node = ref object # référence gérée (ARC/ORC : comptage de références déterministe)
    v: int64
    l, r: Node
  ANode = object
    v: int64
    l, r: int32
proc tBuild(d: int, c: var int64): Node =
  result = Node(v: c)
  inc c
  if d > 0:
    result.l = tBuild(d - 1, c)
    result.r = tBuild(d - 1, c)
proc tSum(n: Node): int64 = (if n.isNil: 0 else: n.v + tSum(n.l) + tSum(n.r))
{.push boundChecks: off.}
proc aBuild(a: var array[2047, ANode], top: var int32, d: int, c: var int64): int32 =
  result = top
  inc top
  a[result] = ANode(v: c, l: -1, r: -1)
  inc c
  if d > 0:
    let l = aBuild(a, top, d - 1, c)
    a[result].l = l
    a[result].r = aBuild(a, top, d - 1, c)
proc aSum(a: array[2047, ANode], i: int32): int64 = (if i < 0: 0 else: a[i].v + aSum(a, a[i].l) + aSum(a, a[i].r))
{.pop.}
proc runK8(v: string, reps: int) =
  const Q = 16384
  let tuned = v == "tuned"
  var c0 = 0'i64
  let keep = tBuild(20, c0)
  let lsum = tSum(keep)
  var lat = newSeq[int64](Q)
  var arena = new array[2047, ANode]
  for r in -WARMUP ..< reps:
    var total = 0'i64
    let t0 = getMonoTime()
    for q in 0 ..< Q:
      let a = getMonoTime()
      var c = int64(q)
      var s: int64
      if tuned:
        var top = 0'i32
        s = aSum(arena[], aBuild(arena[], top, 10, c))
      else:
        s = tSum(tBuild(10, c)) # l'arbre est libéré dès qu'il n'est plus référencé
      total += s
      lat[q] = (getMonoTime() - a).inNanoseconds
    let dt = secs(t0)
    if r >= 0:
      result("k8", v, "16384x2047", r, dt, $(total + lsum))
      lat.sort()
      echo &"LAT;{v};{lat[Q div 2]};{lat[Q * 9 div 10]};{lat[Q * 99 div 100]};{lat[Q * 999 div 1000]};{lat[Q - 1]}"

# ------------------------------------------------------------------ K9
const M9 = 2048
proc k9Init(i, j: int): float = float((i * 31 + j * 17) mod 1024) / 1024.0
proc k9Natural(a: seq[seq[float]], b: var seq[seq[float]]) {.noinline.} =
  for i in 1 ..< M9 - 1:
    for j in 1 ..< M9 - 1:
      b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1])
{.push boundChecks: off, overflowChecks: off.}
proc k9Rows(a, b: ptr UncheckedArray[float], r0, r1: int) {.noinline.} =
  for i in r0 ..< r1:
    let up = cast[ptr UncheckedArray[float]](a[(i - 1) * M9].addr)
    let mid = cast[ptr UncheckedArray[float]](a[i * M9].addr)
    let dn = cast[ptr UncheckedArray[float]](a[(i + 1) * M9].addr)
    let o = cast[ptr UncheckedArray[float]](b[i * M9].addr)
    for j in 1 ..< M9 - 1: o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1])
{.pop.}
type K9Job = tuple[a, b: ptr UncheckedArray[float], r0, r1: int]
proc k9Worker(j: K9Job) {.thread.} = k9Rows(j.a, j.b, j.r0, j.r1)
proc runK9(v: string, reps: int) =
  for r in -WARMUP ..< reps:
    var s, dt: float
    if v == "natural":
      var a = newSeq[seq[float]](M9)
      for i in 0 ..< M9:
        a[i] = newSeq[float](M9)
        for j in 0 ..< M9: a[i][j] = k9Init(i, j)
      var b = a
      let t0 = getMonoTime()
      for _ in 0 ..< 4:
        k9Natural(a, b)
        swap(a, b)
      dt = secs(t0)
      for row in a:
        for x in row: s += x
    else:
      var a = cast[ptr UncheckedArray[float]](aligned_alloc(64, csize_t(M9 * M9 * 8)))
      var b = cast[ptr UncheckedArray[float]](aligned_alloc(64, csize_t(M9 * M9 * 8)))
      for k in 0 ..< M9 * M9:
        a[k] = k9Init(k div M9, k mod M9); b[k] = a[k]
      let t0 = getMonoTime()
      for _ in 0 ..< 4:
        if v == "tuned": k9Rows(a, b, 1, M9 - 1)
        else:
          var th: array[4, Thread[K9Job]]
          for t in 0 ..< 4: createThread(th[t], k9Worker, (a, b, 1 + (M9 - 2) * t div 4, 1 + (M9 - 2) * (t + 1) div 4))
          joinThreads(th)
        swap(a, b)
      dt = secs(t0)
      for k in 0 ..< M9 * M9: s += a[k]
      cfree(a); cfree(b)
    if r >= 0: result("k9", v, "2048^2x4", r, dt, formatFloat(s, ffScientific, 15).replace("e+", "e+0"))

# ------------------------------------------------------------------ K10
const M10 = 1 shl 22
const CAP10 = 1 shl 14
type Spsc = object
  writeIdx {.align(128).}: Atomic[int]
  readIdx {.align(128).}: Atomic[int]
  buf {.align(128).}: array[CAP10, uint64]
var chan10: Channel[uint64]
var res10: uint64
proc chanProd() {.thread.} =
  for x in 1'u64 .. uint64(M10): chan10.send(x)
proc chanCons() {.thread.} =
  var s = 0'u64
  for _ in 0 ..< M10: s += chan10.recv()
  res10 = s
proc spscProd(q: ptr Spsc) {.thread.} =
  var w, rc = 0
  for x in 1'u64 .. uint64(M10):
    while w - rc == CAP10:
      rc = q.readIdx.load(moAcquire)
      if w - rc == CAP10: cpuRelax()
    q.buf[w and (CAP10 - 1)] = x
    inc w
    q.writeIdx.store(w, moRelease)
proc spscCons(q: ptr Spsc) {.thread.} =
  var rd, wc = 0
  var s = 0'u64
  for _ in 0 ..< M10:
    while rd == wc:
      wc = q.writeIdx.load(moAcquire)
      if rd == wc: cpuRelax()
    s += q.buf[rd and (CAP10 - 1)]
    inc rd
    q.readIdx.store(rd, moRelease)
  res10 = s
proc runK10(v: string, reps: int) =
  for r in -WARMUP ..< reps:
    let t0 = getMonoTime()
    if v == "natural": # Channel[T] du module system : canal borné entre threads
      chan10.open(CAP10)
      var p, c: Thread[void]
      createThread(c, chanCons)
      createThread(p, chanProd)
      joinThread(p); joinThread(c)
      chan10.close()
    else:
      let q = cast[ptr Spsc](aligned_alloc(128, csize_t(sizeof(Spsc))))
      zeroMem(q, sizeof(Spsc))
      var p, c: Thread[ptr Spsc]
      createThread(c, spscCons, q)
      createThread(p, spscProd, q)
      joinThread(p); joinThread(c)
      cfree(q)
    let dt = secs(t0)
    if r >= 0: result("k10", v, "2^22", r, dt, $res10)

when isMainModule:
  WARMUP = parseInt(getEnv("WARMUP", "1"))
  DATA = getEnv("MS_DATA", "/opt/msdata")
  let k = paramStr(1)
  let v = paramStr(2)
  let reps = parseInt(paramStr(3))
  let p = if paramCount() > 3: paramStr(4) else: ""
  case k
  of "k1": runK1(v, reps)
  of "k2": runK2(v, reps, p)
  of "k3": runK3(v, reps)
  of "k4": runK4(v, reps)
  of "k5": runK5(v, reps)
  of "k6": runK6(v, reps, p)
  of "k7": runK7(v, reps)
  of "k8": runK8(v, reps)
  of "k9": runK9(v, reps)
  of "k10": runK10(v, reps)
  else: discard
