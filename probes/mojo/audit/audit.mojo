# Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de Mojo 1.2, cas positifs. run.sh y ajoute le code produit
# (objdump), les échecs et les recherches d'absence.
from std.sys import size_of, align_of, llvm_intrinsic, inlined_assembly, argv
from std.sys.intrinsics import prefetch, PrefetchOptions
from std.memory.alloc import unsafe_alloc
from std.collections import List, Array
from std.reflection import reflect
from std.atomic import Atomic, Ordering, fence
from std.runtime._asyncrt import create_task
from std.benchmark import black_box
from std.ffi import external_call

struct Part(ImplicitlyCopyable, Movable):
    var x: Float32
    var y: Float32
    var z: Float32
    var m: UInt8
    def __init__(out self, x: Float32, y: Float32, z: Float32, m: UInt8):
        self.x = x; self.y = y; self.z = z; self.m = m

struct Inl(Movable):
    var n: UInt32
    var a: Array[Float32, 16]
    def __init__(out self):
        self.n = 0
        self.a = Array[Float32, 16](fill=0)

struct Noisy(Movable):
    var name: String
    def __init__(out self, name: String):
        self.name = name
    def __deinit__(deinit self):
        print("del(", self.name, ") ", sep="", end="")

__async def worker(t: Int, tid: Pointer[Int32, MutUntrackedOrigin]) -> Int:
    var s = 0
    for i in range(t * 1000, (t + 1) * 1000):
        s += i
    var spin = 0
    for i in range(20_000_000):   # tâche assez longue pour que les quatre se chevauchent
        spin += black_box(i)
    _ = black_box(spin)
    tid[] = external_call["gettid", Int32]()   # observation seulement
    return s

def gsum[T: DType](a: Scalar[T], b: Scalar[T]) -> Scalar[T]:
    return a + b

def fib(n: Int) -> Int:
    var a = 0
    var b = 1
    for _ in range(n):
        var t = a + b
        a = b
        b = t
    return a

def main():
    # A1
    var v = List[Part]()
    for _ in range(8):
        v.append(Part(1.0, 2.0, 3.0, 4))
    var p0 = Int(v.unsafe_ptr())
    var p1 = Int(v.unsafe_ptr() + 1)
    var raw = v.unsafe_ptr().bitcast[UInt8]()
    print("CAP;A1;1;[exécutée] List[Part] : pas de", p1 - p0, "o = size_of[Part]()", size_of[Part](), "; les 4 premiers octets du tampon sont le Float32 x en ligne :", raw[0], raw[1], raw[2], raw[3])
    # A2
    comptime off_z = reflect[Part].field_offset[name="z"]()
    comptime off_m = reflect[Part].field_offset[name="m"]()
    print("CAP;A2;1;[exécutée] reflect[Part].field_offset (à la compilation) : z à", off_z, "o, m à", off_m, "o ; ordre déclaré")
    var l8 = List[UInt8](capacity=1000)
    # A7, A8
    print("CAP;A7;1;[exécutée] struct (n: UInt32, a: Array[Float32, 16]) :", size_of[Inl](), "o, field_offset de a =", reflect[Inl].field_offset[name="a"](), "(tableau en ligne)")
    print("CAP;A8;1;[exécutée] UInt8/Int16/Float16/Float32 :", size_of[UInt8](), "/", size_of[Int16](), "/", size_of[Float16](), "/", size_of[Float32](), "o ; List[UInt8](capacity=1000) : capacité", l8.capacity(), "o")
    # B1
    print("CAP;B1;1;[exécutée] pas de ramasse-miettes (propriété) : ", end="")
    var a = Noisy("a")
    if True:
        var b = Noisy("b")
        _ = b^
    print("fin-portée ", end="")
    _ = a^
    print("; destruction au dernier usage (ASAP), déterministe")
    # B3
    var local = Array[Float32, 1024](fill=0)
    local[0] = 1
    var marker = black_box(local[0])
    var heap = unsafe_alloc[Float32](1)
    var ds = abs(Int(UnsafePointer(to=marker)) - Int(local.unsafe_ptr()))
    var dh = abs(Int(heap) - Int(local.unsafe_ptr()))
    print("CAP;B3;1;[exécutée] Array[Float32, 1024] local à", ds, "o d'une autre variable locale, à", dh, "o du tas : sur la pile")
    # B5
    var buf = unsafe_alloc[UInt32](8)
    for i in range(8):
        buf[i] = 0
    (buf + 3)[] = 42
    (buf.bitcast[UInt8]() + 16).bitcast[UInt32]()[] = 7
    print("CAP;B5;1;[exécutée] UnsafePointer[UInt32] : (p + 3)[] = 42 -> buf[3] =", buf[3], "; écriture par décalage d'octets -> buf[4] =", buf[4])
    # C1
    var va = SIMD[DType.float32, 8](1, 2, 3, 4, 5, 6, 7, 8)
    var vb = va + va
    print("CAP;C1;1;[exécutée] SIMD[DType.float32, 8] : (a + a)[7] =", vb[7], ", a.reduce_add() =", va.reduce_add(), "; type vectoriel du langage")
    # C2
    var k = Int32(len(argv()))
    var t = llvm_intrinsic["llvm.x86.avx512.pternlog.d.512", SIMD[DType.int32, 16]](SIMD[DType.int32, 16](12 * k), SIMD[DType.int32, 16](10 * k), SIMD[DType.int32, 16](k), Int32(0x96))
    print("FACT;C2;llvm_intrinsic[\"llvm.x86.avx512.pternlog.d.512\"] : 12 ^ 10 ^ 1 =", t[0])
    # D1 (½ : runtime._asyncrt, module privé)
    var tids = unsafe_alloc[Int32](4)
    var w0 = create_task(worker(0, tids))
    var w1 = create_task(worker(1, tids + 1))
    var w2 = create_task(worker(2, tids + 2))
    var w3 = create_task(worker(3, tids + 3))
    var tot = w0.wait() + w1.wait() + w2.wait() + w3.wait()
    var nd = 0
    for i in range(4):
        var seen = False
        for j in range(i):
            seen = seen or tids[j] == tids[i]
        if not seen:
            nd += 1
    print("CAP;D1;0.5;[exécutée] create_task de std.runtime._asyncrt (module privé, souligné ; aucune API publique de fils) : 4 tâches sur", nd, "fils distincts (gettid), somme", tot, "(attendu 7998000)")
    # E2
    var x41 = black_box(Int64(41))
    var r = inlined_assembly["leaq 1($1), $0", Int64, constraints="=r,r", has_side_effect=False](x41)
    print("CAP;E2;1;[exécutée] inlined_assembly[\"leaq 1($1), $0\"] : 41 ->", r)
    # E7
    comptime F60 = fib(60)
    print("FACT;E7;comptime F60 = fib(60) =", F60, "; gsum[DType.float32] =", gsum[DType.float32](1.5, 2.5), ", gsum[DType.float64] =", gsum[DType.float64](1.5, 2.25))
    # F3
    var um = UInt32.MAX
    var c250 = UInt8(250)
    print("CAP;F3;1;[exécutée] UInt32.MAX + 1 =", um + 1, ", UInt8(250) + 10 =", c250 + 10, ", Int32.MAX + 1 =", Int32.MAX + 1, "(entiers à largeur fixe enveloppants)")
    heap.free(); buf.free()
