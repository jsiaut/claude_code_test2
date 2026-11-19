# Code produit, lu par run.sh (objdump des fonctions exportées ; mojo build, réglages par défaut comme au banc).
from std.sys import llvm_intrinsic, argv
from std.sys.intrinsics import prefetch, PrefetchOptions, unlikely
from std.atomic import Atomic, Ordering
from std.collections import List
from std.ffi import external_call
from std.benchmark import black_box
from std.memory.alloc import unsafe_alloc

@export("st_release")
def st_release(p: Pointer[UInt64, MutUntrackedOrigin]) abi("C"):
    Atomic[UInt64].store[ordering=Ordering.RELEASE](p, 1)

@export("st_seqcst")
def st_seqcst(p: Pointer[UInt64, MutUntrackedOrigin]) abi("C"):
    Atomic[UInt64].store[ordering=Ordering.SEQUENTIAL](p, 1)

@export("add_relaxed")
def add_relaxed(p: Pointer[UInt64, MutUntrackedOrigin]) abi("C") -> UInt64:
    return Atomic[UInt64].fetch_add[ordering=Ordering.RELAXED](p, 1)

@export("pf")
def pf(p: Pointer[UInt8, MutUntrackedOrigin]) abi("C"):
    prefetch[PrefetchOptions().for_read().high_locality()](p)

@export("tern")
def tern(k: Int32) abi("C") -> Int32:
    var r = llvm_intrinsic["llvm.x86.avx512.pternlog.d.512", SIMD[DType.int32, 16]](SIMD[DType.int32, 16](12 * k), SIMD[DType.int32, 16](10 * k), SIMD[DType.int32, 16](k), Int32(0x96))
    return r[0]

@export("hinted")
def hinted(x: Int) abi("C") -> Int:
    var r = x
    if unlikely(x == 7):
        _ = external_call["sched_yield", Int32]()
        r = x * 5
    return r + 1

@export("unhinted")
def unhinted(x: Int) abi("C") -> Int:
    var r = x
    if x == 9:
        _ = external_call["sched_yield", Int32]()
        r = x * 7
    return r + 3

def fib(n: Int) -> Int:
    var a = 0
    var b = 1
    for _ in range(n):
        var t = a + b
        a = b
        b = t
    return a

@export("fib60")
def fib60() abi("C") -> Int:
    comptime F = fib(60)
    return F

@export("noalloc")
def noalloc(n: Int) abi("C") -> Float32:
    # structures, SIMD, fermeture capturante, boucles : aucune allocation attendue
    var v = SIMD[DType.float32, 8](Float32(n))
    var k = Float32(3)
    def scale(x: SIMD[DType.float32, 8]) capturing -> SIMD[DType.float32, 8]:
        return x * k
    var acc = SIMD[DType.float32, 8](0)
    for i in range(n):
        acc += scale(v + Float32(i))
    return acc.reduce_add()

def main():
    var p = unsafe_alloc[UInt64](1)
    p[] = 0
    st_release(p); st_seqcst(p); _ = add_relaxed(p)
    var b = unsafe_alloc[UInt8](64)
    pf(b)
    print(tern(Int32(len(argv()))), hinted(len(argv())), unhinted(len(argv())), fib60(), noalloc(len(argv()) + 10), p[])
