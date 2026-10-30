# Implémentation Mojo 1.2 (bibliothèque standard std uniquement). Voir docs/SPEC.md.
# Note : Mojo 1.2 n'expose aucune API publique de threads CPU ; parallelize() est dans MAX.
# Les noyaux multi-threads utilisent donc std.runtime._asyncrt (privé, mais livré avec std).
from std.time import perf_counter_ns
from std.sys import argv, size_of
from std.os import getenv
from std.memory.alloc import unsafe_alloc
from std.memory import unsafe_memcpy, unsafe_memset_zero, OwnedPointer
from std.atomic import Atomic, Ordering
from std.collections import Dict, List, Deque, Array
from std.sys.intrinsics import prefetch, PrefetchOptions
from std.runtime._asyncrt import create_task
from std.benchmark import black_box
from std.utils.lock import BlockingSpinLock

comptime DATA = "/opt/msdata/"

struct Col[dtype: DType](ImplicitlyCopyable):
    var p: Pointer[Scalar[Self.dtype], MutUntrackedOrigin]
    var n: Int
    def __init__(out self, p: Pointer[Scalar[Self.dtype], MutUntrackedOrigin], n: Int):
        self.p = p
        self.n = n
    @inline(.always)
    def __getitem__(self, i: Int) -> Scalar[Self.dtype]:
        return self.p[unsafe_offset=i]

def load[dtype: DType](name: String) raises -> Col[dtype]:
    var b: List[UInt8]
    with open(String(DATA) + name, "r") as f:
        b = f.read_bytes()
    var nb = len(b)
    var n = nb // size_of[Scalar[dtype]]()
    var p = unsafe_alloc[Scalar[dtype]](n + 64, alignment=64)  # tampon aligné sur 64 octets
    unsafe_memcpy(dest=p.unsafe_bitcast[UInt8](), src=b.unsafe_ptr(), count=nb)
    return Col[dtype](p, n)

def result(k: String, v: String, p: String, rep: Int, sec: Float64, chk: String):
    print("RESULT;", k, ";", v, ";", p, ";", rep, ";", sec, ";", chk, sep="")

def secs(t0: Int) -> Float64:
    return Float64(perf_counter_ns() - t0) * 1e-9

# ------------------------------------------------------------------ K1
comptime N1 = 1 << 22

@fieldwise_init
struct Particle(Copyable, Movable):
    var x: Float32
    var y: Float32
    var z: Float32
    var vx: Float32
    var vy: Float32
    var vz: Float32
    var ax: Float32
    var ay: Float32
    var az: Float32
    var mass: Float32
    var charge: Float32
    var radius: Float32
    var temp: Float32
    var pressure: Float32
    var energy: Float32
    var density: Float32

@inline(.never)
def k1_natural(ps: List[Particle]) -> Float64:
    var e: Float64 = 0
    for p in ps:
        e += 0.5 * Float64(p.mass) * Float64(p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)
    return e

@inline(.never)
def k1_aos(ps: List[Particle]) -> Float64:
    var acc = SIMD[DType.float64, 8](0)
    var base = ps.unsafe_ptr()
    for i in range(0, len(ps), 8):
        comptime for k in range(8):
            var q = base + (i + k)
            acc[k] += Float64(0.5 * q[].mass * (q[].vx * q[].vx + q[].vy * q[].vy + q[].vz * q[].vz))
    return acc.reduce_add()

@inline(.never)
def k1_soa(vx: Col[DType.float32], vy: Col[DType.float32], vz: Col[DType.float32], m: Col[DType.float32]) -> Float64:
    var a0 = SIMD[DType.float64, 8](0)
    var a1 = SIMD[DType.float64, 8](0)
    var h = SIMD[DType.float32, 16](0.5)
    for i in range(0, vx.n, 16):
        var x = vx.p.unsafe_load[width=16, alignment=64](i)
        var y = vy.p.unsafe_load[width=16, alignment=64](i)
        var z = vz.p.unsafe_load[width=16, alignment=64](i)
        var w = m.p.unsafe_load[width=16, alignment=64](i)
        var e = h * w * z.fma(z, y.fma(y, x * x))
        a0 += e.slice[8, offset=0]().cast[DType.float64]()
        a1 += e.slice[8, offset=8]().cast[DType.float64]()
    return (a0 + a1).reduce_add()

def rss_now() raises -> Int:
    """Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)."""
    with open("/proc/self/statm", "r") as f:
        var parts = f.read().split(" ")
        return atol(parts[1]) * 4096


def run_k1(v: String, reps: Int, warmup: Int) raises:
    if v == "footprint0":
        result("k1", v, "energy", 0, 0, "0")
        return
    var raw = load[DType.float32]("k1_particles.f32")
    if v == "footprint_raw":
        result("k1", v, "energy", 0, 0, "0")
        return
    var m1 = rss_now() if v == "footprint" else 0  # P1 : tampon brut chargé
    var ps = List[Particle](capacity=N1)
    for i in range(N1):
        var f = raw.p + 16 * i
        ps.append(Particle(f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[12], f[13], f[14], f[15]))
    if v == "footprint":
        var m2 = rss_now()  # P2 : collection construite, tampon brut encore vivant
        print("META;mem;rss;" + String(m1) + ";" + String(m2))
        print("META;rss;" + String(m1) + ";" + String(m2))
        print("META;raw0;" + String(raw.p[0]))
        raw.p.free()
        result("k1", v, "energy", 0, 0, String(k1_natural(ps)))
        return
    if v == "soa":
        var cols = List[Col[DType.float32]]()
        for k in range(16):
            var c = unsafe_alloc[Float32](N1, alignment=64)
            for i in range(N1):
                c[unsafe_offset=i] = raw[16 * i + k]
            cols.append(Col[DType.float32](c, N1))
        for r in range(-warmup, reps):
            var t0 = perf_counter_ns()
            var e = k1_soa(cols[3], cols[4], cols[5], cols[9])
            var dt = secs(t0)
            if r >= 0:
                result("k1", v, "energy", r, dt, String(e))
        return
    if v == "natural_shuffled":
        var perm = load[DType.uint32]("k1_perm.u32")
        var s = List[Particle](capacity=N1)
        for i in range(N1):
            s.append(ps[Int(perm[i])].copy())
        ps = s^
    var aos = v == "aos"
    for r in range(-warmup, reps):
        var t0 = perf_counter_ns()
        var e = k1_aos(ps) if aos else k1_natural(ps)
        var dt = secs(t0)
        if r >= 0:
            result("k1", v, "energy", r, dt, String(e))

# ------------------------------------------------------------------ K2
@inline(.never)
def k2_chase(a: Col[DType.uint32], h: Int) -> UInt32:
    var i: UInt32 = 0
    for _ in range(h):
        i = a[Int(i)]
    return i

def run_k2(v: String, reps: Int, p: String, warmup: Int) raises:
    var a = load[DType.uint32]("k2_chase_" + p + ".u32")
    for r in range(-warmup, reps):
        var t0 = perf_counter_ns()
        var i = k2_chase(a, 4200000)
        var dt = secs(t0)
        if r >= 0:
            result("k2", v, p, r, dt, String(i))

# ------------------------------------------------------------------ K3
comptime ITER3 = 1 << 25

__async def k3_worker(c: Pointer[UInt64, MutUntrackedOrigin], rmw: Bool) -> Int:
    if rmw:
        for _ in range(ITER3):
            _ = Atomic[UInt64].fetch_add[ordering=Ordering.RELAXED](c, 1)
    else:
        for _ in range(ITER3):
            Atomic[UInt64].store[ordering=Ordering.RELAXED](c, Atomic[UInt64].load[ordering=Ordering.RELAXED](c) + 1)
    return 0

def run_k3(v: String, reps: Int, warmup: Int) raises:
    var rmw = v.startswith("rmw")
    var stride = 16 if v.endswith("padded") else 1
    print("META;k3_mechanism;", "Atomic.fetch_add[RELAXED] (lock xadd)" if rmw else "Atomic.load/store[RELAXED] (mov)", sep="")
    var mem = unsafe_alloc[UInt64](128, alignment=128)
    for r in range(-warmup, reps):
        for t in range(4):
            mem[unsafe_offset=16 + t * stride] = 0
        var t0 = perf_counter_ns()
        var t_0 = create_task(k3_worker(mem + 16, rmw))
        var t_1 = create_task(k3_worker(mem + 16 + stride, rmw))
        var t_2 = create_task(k3_worker(mem + 16 + 2 * stride, rmw))
        var t_3 = create_task(k3_worker(mem + 16 + 3 * stride, rmw))
        _ = t_0.wait() + t_1.wait() + t_2.wait() + t_3.wait()
        var dt = secs(t0)
        var s: UInt64 = 0
        for t in range(4):
            s += mem[unsafe_offset=16 + t * stride]
        if r >= 0:
            result("k3", v, "4x2^25", r, dt, String(s))

# ------------------------------------------------------------------ K4
@inline(.never)
def k4_natural(v: List[UInt8]) -> UInt64:
    var s: UInt64 = 0
    for x in v:
        if x >= 128:
            s += UInt64(x)
    return s

@inline(.never)
def k4_branchless(v: List[UInt8]) -> UInt64:
    var s: UInt64 = 0
    for x in v:
        s += UInt64(x) * UInt64(x >> 7)
    return s

# Remarque sur Mojo (docs/MOJO.md) : K4 en SIMD explicite, hors spécification (K4 n'a pas de variante tuned).
# 64 octets par tour, masque >= 128, accumulateurs 32 bits (au plus 255 x 2^18 par voie : pas de débordement).
@inline(.never)
def k4_simd(v: List[UInt8]) -> UInt64:
    comptime W = 64
    var p = v.unsafe_ptr()
    var n = len(v)
    var acc = SIMD[DType.uint32, W](0)
    var i = 0
    while i + W <= n:
        var x = p.unsafe_load[width=W](i)
        acc += x.ge(SIMD[DType.uint8, W](128)).select(x, SIMD[DType.uint8, W](0)).cast[DType.uint32]()
        i += W
    var s = acc.cast[DType.uint64]().reduce_add()
    while i < n:
        var b = p[unsafe_offset=i]
        if b >= 128:
            s += UInt64(b)
        i += 1
    return s

def run_k4(v: String, reps: Int, warmup: Int) raises:
    var d: List[UInt8]
    with open(String(DATA) + "k4_bytes.u8", "r") as f:
        d = f.read_bytes()
    if v == "natural_sorted":
        sort(d)
    var bl = v == "branchless_unsorted"
    var simd = v == "simd_unsorted" or v == "simd_cold"
    var cold = v == "simd_cold"
    comptime NFLUSH = 64 << 20  # 64 Mio écrits avant chaque répétition (hors chrono) : le L3 de 33 Mio est vidé
    var fl = unsafe_alloc[UInt8](NFLUSH, alignment=64)
    for r in range(-warmup, reps):
        if cold:
            unsafe_memset_zero(fl, NFLUSH)
            _ = black_box(fl[unsafe_offset=r & 4095])
        var t0 = perf_counter_ns()
        var s = k4_simd(d) if simd else (k4_branchless(d) if bl else k4_natural(d))
        var dt = secs(t0)
        if r >= 0:
            result("k4", v, "16M", r, dt, String(s))

# ------------------------------------------------------------------ K5
comptime INNER5 = 1 << 16

@inline(.never)
def k5_natural(a: Col[DType.float32], b: Col[DType.float32]) -> Float32:
    var s: Float32 = 0
    for i in range(a.n):
        s += a[i] * b[i]
    return s

@inline(.never)
def k5_tuned(a: Col[DType.float32], b: Col[DType.float32]) -> Float32:
    var s0 = SIMD[DType.float32, 16](0)
    var s1 = s0
    var s2 = s0
    var s3 = s0
    for i in range(0, a.n, 64):
        s0 = a.p.unsafe_load[width=16, alignment=64](i).fma(b.p.unsafe_load[width=16, alignment=64](i), s0)
        s1 = a.p.unsafe_load[width=16, alignment=64](i + 16).fma(b.p.unsafe_load[width=16, alignment=64](i + 16), s1)
        s2 = a.p.unsafe_load[width=16, alignment=64](i + 32).fma(b.p.unsafe_load[width=16, alignment=64](i + 32), s2)
        s3 = a.p.unsafe_load[width=16, alignment=64](i + 48).fma(b.p.unsafe_load[width=16, alignment=64](i + 48), s3)
    return ((s0 + s1) + (s2 + s3)).reduce_add()

def run_k5(v: String, reps: Int, warmup: Int) raises:
    var a = load[DType.float32]("k5_a.f32")
    var b = load[DType.float32]("k5_b.f32")
    var tuned = v == "tuned"
    for r in range(-warmup, reps):
        var d: Float32 = 0
        var t0 = perf_counter_ns()
        for _ in range(INNER5):
            var aa = black_box(a)  # barrière d'optimisation
            d = k5_tuned(aa, b) if tuned else k5_natural(aa, b)
        var dt = secs(t0)
        if r >= 0:
            result("k5", v, "2048x65536", r, dt, String(d))

# ------------------------------------------------------------------ K6
comptime N6 = 1 << 24

@fieldwise_init
struct Cols(ImplicitlyCopyable):
    var sd: Col[DType.int32]
    var pr: Col[DType.int32]
    var q: Col[DType.uint8]
    var d: Col[DType.uint8]
    var t: Col[DType.uint8]
    var rf: Col[DType.uint8]
    var ls: Col[DType.uint8]

@inline(.never)
def q6_natural(c: Cols, lo: Int, hi: Int) -> Int64:
    var s: Int64 = 0
    for i in range(lo, hi):
        if c.sd[i] >= 8766 and c.sd[i] < 9131 and c.d[i] >= 5 and c.d[i] <= 7 and c.q[i] < 24:
            s += Int64(c.pr[i]) * Int64(c.d[i])
    return s

comptime I16 = SIMD[DType.int32, 16]

@inline(.always)
def ld8(c: Col[DType.uint8], i: Int) -> I16:
    return c.p.unsafe_load[width=16, alignment=16](i).cast[DType.int32]()

@inline(.never)
def q6_tuned(c: Cols, lo: Int, hi: Int) -> Int64:
    var acc = SIMD[DType.int64, 16](0)
    var i = lo
    while i + 16 <= hi:
        var sd = c.sd.p.unsafe_load[width=16, alignment=64](i)
        var d = ld8(c.d, i)
        var q = ld8(c.q, i)
        var m = sd.ge(I16(8766)) & sd.lt(I16(9131)) & d.ge(I16(5)) & d.le(I16(7)) & q.lt(I16(24))
        acc += m.select(c.pr.p.unsafe_load[width=16, alignment=64](i) * d, I16(0)).cast[DType.int64]()
        i += 16
    return acc.reduce_add() + q6_natural(c, i, hi)

@inline(.never)
def q1_natural(c: Cols, lo: Int, hi: Int, mut acc: List[Int64]):
    for i in range(lo, hi):
        if c.sd[i] <= 10471:
            var g = (Int(c.rf[i]) * 2 + Int(c.ls[i])) * 5
            var p = Int64(c.pr[i])
            var dp = p * (100 - Int64(c.d[i]))
            acc[g] += 1
            acc[g + 1] += Int64(c.q[i])
            acc[g + 2] += p
            acc[g + 3] += dp
            acc[g + 4] += dp * (100 + Int64(c.t[i]))

# Q1 optimisé : agrégation masquée par groupe en SIMD (même algorithme que la référence C)
@inline(.never)
def q1_tuned(c: Cols, lo: Int, hi: Int, mut acc: List[Int64]):
    comptime L16 = SIMD[DType.int64, 16]
    var i = lo
    while i + 16 <= hi:
        var aq = Array[I16, 6](fill=I16(0))
        var ap = Array[I16, 6](fill=I16(0))
        var adp = Array[I16, 6](fill=I16(0))
        var ach = Array[L16, 6](fill=L16(0))
        var cnt = Array[Int64, 6](fill=0)
        var end = i + 4096 if i + 4096 <= hi else hi - (hi - i) % 16
        while i < end:
            var p_ = c.sd.p.unsafe_load[width=16, alignment=64](i).le(I16(10471))
            var vg = ld8(c.rf, i) * 2 + ld8(c.ls, i)
            var vq = ld8(c.q, i)
            var vd = ld8(c.d, i)
            var vt = ld8(c.t, i) + 100
            var vp = c.pr.p.unsafe_load[width=16, alignment=64](i)
            var vdp = vp * (100 - vd)
            var ch = vdp.cast[DType.int64]() * vt.cast[DType.int64]()
            comptime for g in range(6):
                var m = p_ & vg.eq(I16(g))
                cnt[g] += Int64(m.select(I16(1), I16(0)).reduce_add())
                aq[g] += m.select(vq, I16(0))
                ap[g] += m.select(vp, I16(0))
                adp[g] += m.select(vdp, I16(0))
                ach[g] += m.select(ch, L16(0))
            i += 16
        for g in range(6):
            acc[g * 5] += cnt[g]
            acc[g * 5 + 1] += Int64(aq[g].reduce_add())
            acc[g * 5 + 2] += Int64(ap[g].reduce_add())
            acc[g * 5 + 3] += adp[g].cast[DType.int64]().reduce_add()
            acc[g * 5 + 4] += ach[g].reduce_add()
    if i < hi:
        q1_natural(c, i, hi, acc)

def fold(acc: List[Int64]) -> Int64:
    var s: Int64 = 0
    for x in acc:
        s += x
    return s

__async def k6_worker(c: Cols, lo: Int, hi: Int, q1: Bool) -> Int64:
    if q1:
        var a = List[Int64](length=30, fill=0)
        q1_tuned(c, lo, hi, a)
        return fold(a)
    return q6_tuned(c, lo, hi)

def run_k6(v: String, reps: Int, p: String, warmup: Int) raises:
    var c = Cols(load[DType.int32]("k6_shipdate.i32"), load[DType.int32]("k6_extendedprice.i32"), load[DType.uint8]("k6_quantity.u8"),
                 load[DType.uint8]("k6_discount.u8"), load[DType.uint8]("k6_tax.u8"), load[DType.uint8]("k6_returnflag.u8"),
                 load[DType.uint8]("k6_linestatus.u8"))
    var q1 = p == "q1"
    for r in range(-warmup, reps):
        var t0 = perf_counter_ns()
        var s: Int64 = 0
        if v == "mt":
            var a0 = create_task(k6_worker(c, 0, N6 // 4, q1))
            var a1 = create_task(k6_worker(c, N6 // 4, N6 // 2, q1))
            var a2 = create_task(k6_worker(c, N6 // 2, 3 * (N6 // 4), q1))
            var a3 = create_task(k6_worker(c, 3 * (N6 // 4), N6, q1))
            s = a0.wait() + a1.wait() + a2.wait() + a3.wait()
        elif q1:
            var a = List[Int64](length=30, fill=0)
            if v == "tuned":
                q1_tuned(c, 0, N6, a)
            else:
                q1_natural(c, 0, N6, a)
            s = fold(a)
        else:
            s = q6_tuned(c, 0, N6) if v == "tuned" else q6_natural(c, 0, N6)
        var dt = secs(t0)
        if r >= 0:
            result("k6", v, p, r, dt, String(s))

# ------------------------------------------------------------------ K7
@fieldwise_init
struct Agg(ImplicitlyCopyable):
    var count: UInt32
    var sum: UInt64

@fieldwise_init
struct Slot(ImplicitlyCopyable):
    var key: UInt32
    var count: UInt32
    var sum: UInt64

def run_k7(v: String, reps: Int, warmup: Int) raises:
    var keys = load[DType.uint32]("k7_keys.u32")
    var vals = load[DType.uint32]("k7_vals.u32")
    for r in range(-warmup, reps):
        var nk: UInt64 = 0
        var ws: UInt64 = 0
        var dt: Float64
        if v == "natural":
            var t0 = perf_counter_ns()
            var m = Dict[UInt32, Agg]()
            for i in range(keys.n):
                var k = keys[i]
                var e = m.get(k)
                if e:
                    var a = e.value()
                    m[k] = Agg(a.count + 1, a.sum + UInt64(vals[i]))
                else:
                    m[k] = Agg(1, UInt64(vals[i]))
            dt = secs(t0)
            nk = UInt64(len(m))
            for item in m.items():
                ws += item.value.sum * UInt64((item.key & 1023) + 1)
        else:
            comptime LOG = 21
            comptime CAP = 1 << LOG
            var t0 = perf_counter_ns()
            var tab = unsafe_alloc[Slot](CAP, alignment=64)
            unsafe_memset_zero(tab.unsafe_bitcast[UInt8](), CAP * size_of[Slot]())
            var i = 0
            while i < keys.n:
                var h = Array[UInt32, 16](fill=0)
                comptime for b in range(16):
                    h[b] = (keys[i + b] * 0x9E3779B1) >> (32 - LOG)
                    prefetch[PrefetchOptions().for_write().high_locality()]((tab + Int(h[b])).unsafe_bitcast[UInt8]())
                comptime for b in range(16):
                    var k = keys[i + b]
                    var s = Int(h[b])
                    while tab[unsafe_offset=s].count != 0 and tab[unsafe_offset=s].key != k:
                        s = (s + 1) & (CAP - 1)
                    tab[unsafe_offset=s].key = k
                    tab[unsafe_offset=s].count += 1
                    tab[unsafe_offset=s].sum += UInt64(vals[i + b])
                i += 16
            dt = secs(t0)
            for s in range(CAP):
                if tab[unsafe_offset=s].count != 0:
                    nk += 1
                    ws += tab[unsafe_offset=s].sum * UInt64((tab[unsafe_offset=s].key & 1023) + 1)
            tab.free()
        if r >= 0:
            result("k7", v, "16M/1M", r, dt, String(nk) + ":" + String(ws))

# ------------------------------------------------------------------ K8
# Le type récursif Optional[OwnedPointer[Node]] est refusé par le compilateur 1.2 (non « Deinitable ») :
# on alloue donc chaque nœud sur le tas explicitement, avec libération explicite (style C).
struct Node(ImplicitlyCopyable):
    var v: Int64
    var leaf: Bool
    var l: Pointer[Node, MutUntrackedOrigin]
    var r: Pointer[Node, MutUntrackedOrigin]
    def __init__(out self, v: Int64, leaf: Bool, l: Pointer[Node, MutUntrackedOrigin], r: Pointer[Node, MutUntrackedOrigin]):
        self.v = v
        self.leaf = leaf
        self.l = l
        self.r = r

def t_build(d: Int, mut c: Int64) -> Pointer[Node, MutUntrackedOrigin]:
    var n = unsafe_alloc[Node](1)
    var v = c
    c += 1
    if d > 0:
        var l = t_build(d - 1, c)
        var r = t_build(d - 1, c)
        n.unsafe_write(Node(v, False, l, r))
    else:
        n.unsafe_write(Node(v, True, n, n))
    return n

def t_sum(n: Pointer[Node, MutUntrackedOrigin]) -> Int64:
    if n[].leaf:
        return n[].v
    return n[].v + t_sum(n[].l) + t_sum(n[].r)

def t_free(n: Pointer[Node, MutUntrackedOrigin]):
    if not n[].leaf:
        t_free(n[].l)
        t_free(n[].r)
    n.free()

@fieldwise_init
struct ANode(ImplicitlyCopyable):
    var v: Int64
    var l: Int32
    var r: Int32

def a_build(a: Pointer[ANode, MutUntrackedOrigin], mut top: Int32, d: Int, mut c: Int64) -> Int32:
    var i = top
    top += 1
    a[unsafe_offset=Int(i)] = ANode(c, -1, -1)
    c += 1
    if d > 0:
        var l = a_build(a, top, d - 1, c)
        a[unsafe_offset=Int(i)].l = l
        a[unsafe_offset=Int(i)].r = a_build(a, top, d - 1, c)
    return i

def a_sum(a: Pointer[ANode, MutUntrackedOrigin], i: Int32) -> Int64:
    if i < 0:
        return 0
    var n = a[unsafe_offset=Int(i)]
    return n.v + a_sum(a, n.l) + a_sum(a, n.r)

def run_k8(v: String, reps: Int, warmup: Int) raises:
    comptime Q = 16384
    var tuned = v == "tuned"
    var c0: Int64 = 0
    var keep = t_build(20, c0)
    var lsum = t_sum(keep)
    var lat = List[Int](length=Q, fill=0)
    var arena = unsafe_alloc[ANode](2047, alignment=64)
    for r in range(-warmup, reps):
        var total: Int64 = 0
        var t0 = perf_counter_ns()
        for q in range(Q):
            var a = perf_counter_ns()
            var c = Int64(q)
            var s: Int64
            if tuned:
                var top: Int32 = 0
                s = a_sum(arena, a_build(arena, top, 10, c))
            else:
                var t = t_build(10, c)
                s = t_sum(t)
                t_free(t)
            total += s
            lat[q] = Int(perf_counter_ns() - a)
        var dt = secs(t0)
        if r >= 0:
            result("k8", v, "16384x2047", r, dt, String(total + lsum))
            sort(lat)
            print("LAT;", v, ";", lat[Q // 2], ";", lat[Q * 9 // 10], ";", lat[Q * 99 // 100], ";", lat[Q * 999 // 1000], ";", lat[Q - 1], sep="")

# ------------------------------------------------------------------ K9
comptime M9 = 2048

def k9_init(i: Int, j: Int) -> Float64:
    return Float64((i * 31 + j * 17) % 1024) / 1024.0

@inline(.never)
def k9_natural(a: List[List[Float64]], mut b: List[List[Float64]]):
    for i in range(1, M9 - 1):
        for j in range(1, M9 - 1):
            b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1])

@inline(.never)
def k9_rows(a: Pointer[Float64, MutUntrackedOrigin], b: Pointer[Float64, MutUntrackedOrigin], r0: Int, r1: Int):
    comptime V = SIMD[DType.float64, 8]
    for i in range(r0, r1):
        var up = a + (i - 1) * M9
        var mid = a + i * M9
        var dn = a + (i + 1) * M9
        var o = b + i * M9
        var j = 1
        while j + 8 <= M9 - 1:
            var x = V(0.25) * (((up.unsafe_load[width=8, alignment=8](j) + dn.unsafe_load[width=8, alignment=8](j)) + mid.unsafe_load[width=8, alignment=8](j - 1)) + mid.unsafe_load[width=8, alignment=8](j + 1))
            o.unsafe_store[alignment=8](j, x)
            j += 8
        while j < M9 - 1:
            o[unsafe_offset=j] = 0.25 * (((up[unsafe_offset=j] + dn[unsafe_offset=j]) + mid[unsafe_offset=j - 1]) + mid[unsafe_offset=j + 1])
            j += 1

__async def k9_worker(a: Pointer[Float64, MutUntrackedOrigin], b: Pointer[Float64, MutUntrackedOrigin], r0: Int, r1: Int) -> Int:
    k9_rows(a, b, r0, r1)
    return 0

def run_k9(v: String, reps: Int, warmup: Int) raises:
    for r in range(-warmup, reps):
        var s: Float64 = 0
        var dt: Float64
        if v == "natural":
            var a = List[List[Float64]]()
            for i in range(M9):
                var row = List[Float64](capacity=M9)
                for j in range(M9):
                    row.append(k9_init(i, j))
                a.append(row^)
            var b = a.copy()
            var t0 = perf_counter_ns()
            for it in range(4):
                if it % 2 == 0:
                    k9_natural(a, b)
                else:
                    k9_natural(b, a)
            dt = secs(t0)
            for row in a:
                for x in row:
                    s += x
        else:
            var a = unsafe_alloc[Float64](M9 * M9, alignment=64)
            var b = unsafe_alloc[Float64](M9 * M9, alignment=64)
            for k in range(M9 * M9):
                a[unsafe_offset=k] = k9_init(k // M9, k % M9)
                b[unsafe_offset=k] = a[unsafe_offset=k]
            var t0 = perf_counter_ns()
            for _ in range(4):
                if v == "tuned":
                    k9_rows(a, b, 1, M9 - 1)
                else:
                    var w0 = create_task(k9_worker(a, b, 1, 1 + (M9 - 2) // 4))
                    var w1 = create_task(k9_worker(a, b, 1 + (M9 - 2) // 4, 1 + (M9 - 2) * 2 // 4))
                    var w2 = create_task(k9_worker(a, b, 1 + (M9 - 2) * 2 // 4, 1 + (M9 - 2) * 3 // 4))
                    var w3 = create_task(k9_worker(a, b, 1 + (M9 - 2) * 3 // 4, M9 - 1))
                    _ = w0.wait() + w1.wait() + w2.wait() + w3.wait()
                var tmp = a
                a = b
                b = tmp
            dt = secs(t0)
            for k in range(M9 * M9):
                s += a[unsafe_offset=k]
            a.free()
            b.free()
        if r >= 0:
            result("k9", v, "2048^2x4", r, dt, String(s))

# ------------------------------------------------------------------ K10
comptime M10 = 1 << 22
comptime CAP10 = 1 << 14

struct LockedQueue(Movable):
    var lock: BlockingSpinLock
    var dq: Deque[UInt64]
    def __init__(out self):
        self.lock = BlockingSpinLock()
        self.dq = Deque[UInt64]()

__async def lq_prod(q: Pointer[LockedQueue, MutUntrackedOrigin]) -> UInt64:
    var x: UInt64 = 1
    while x <= M10:
        q[].lock.lock(1)
        if len(q[].dq) < CAP10:
            q[].dq.append(x)
            x += 1
        _ = q[].lock.unlock(1)
    return 0

__async def lq_cons(q: Pointer[LockedQueue, MutUntrackedOrigin]) -> UInt64:
    var s: UInt64 = 0
    var n = 0
    while n < M10:
        q[].lock.lock(2)
        if len(q[].dq) > 0:
            try:
                s += q[].dq.popleft()
            except:
                pass
            n += 1
        _ = q[].lock.unlock(2)
    return s

__async def spsc_prod(ctl: Pointer[UInt64, MutUntrackedOrigin], buf: Pointer[UInt64, MutUntrackedOrigin]) -> UInt64:
    var w: UInt64 = 0
    var rc: UInt64 = 0
    for x in range(1, M10 + 1):
        while w - rc == CAP10:
            rc = Atomic[UInt64].load[ordering=Ordering.ACQUIRE](ctl + 32)
        buf[unsafe_offset=Int(w & (CAP10 - 1))] = UInt64(x)
        w += 1
        Atomic[UInt64].store[ordering=Ordering.RELEASE](ctl + 16, w)
    return 0

__async def spsc_cons(ctl: Pointer[UInt64, MutUntrackedOrigin], buf: Pointer[UInt64, MutUntrackedOrigin]) -> UInt64:
    var rd: UInt64 = 0
    var wc: UInt64 = 0
    var s: UInt64 = 0
    for _ in range(M10):
        while rd == wc:
            wc = Atomic[UInt64].load[ordering=Ordering.ACQUIRE](ctl + 16)
        s += buf[unsafe_offset=Int(rd & (CAP10 - 1))]
        rd += 1
        Atomic[UInt64].store[ordering=Ordering.RELEASE](ctl + 32, rd)
    return s

def run_k10(v: String, reps: Int, warmup: Int) raises:
    for r in range(-warmup, reps):
        var s: UInt64
        var t0 = perf_counter_ns()
        if v == "natural":  # Deque + BlockingSpinLock : seuls primitives de file/verrou de std
            var q = unsafe_alloc[LockedQueue](1, alignment=128)
            q.unsafe_write(LockedQueue())
            var c = create_task(lq_cons(q))
            var p = create_task(lq_prod(q))
            _ = p.wait()
            s = c.wait()
            q.unsafe_deinit_pointee()
            q.free()
        else:
            var ctl = unsafe_alloc[UInt64](64, alignment=128)  # écriture @16, lecture @32 (128 o d'écart)
            ctl[unsafe_offset=16] = 0
            ctl[unsafe_offset=32] = 0
            var buf = unsafe_alloc[UInt64](CAP10, alignment=64)
            var c = create_task(spsc_cons(ctl, buf))
            var p = create_task(spsc_prod(ctl, buf))
            _ = p.wait()
            s = c.wait()
            ctl.free()
            buf.free()
        var dt = secs(t0)
        if r >= 0:
            result("k10", v, "2^22", r, dt, String(s))

def main() raises:
    var args = argv()
    var warmup = Int(getenv("WARMUP", "1"))
    var k = String(args[1])
    var v = String(args[2])
    var reps = Int(String(args[3]))
    var p = String(args[4]) if len(args) > 4 else String("")
    if k == "k1":
        run_k1(v, reps, warmup)
    elif k == "k2":
        run_k2(v, reps, p, warmup)
    elif k == "k3":
        run_k3(v, reps, warmup)
    elif k == "k4":
        run_k4(v, reps, warmup)
    elif k == "k5":
        run_k5(v, reps, warmup)
    elif k == "k6":
        run_k6(v, reps, p, warmup)
    elif k == "k7":
        run_k7(v, reps, warmup)
    elif k == "k8":
        run_k8(v, reps, warmup)
    elif k == "k9":
        run_k9(v, reps, warmup)
    elif k == "k10":
        run_k10(v, reps, warmup)
