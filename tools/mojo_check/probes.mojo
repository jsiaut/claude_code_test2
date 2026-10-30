# Sondes de la remarque sur Mojo (docs/MOJO.md) : A4 (@align), A5 (UnsafeUnion), C4 (FastMathFlag),
# E5 (unsafe_as_noalias), D5 (fence, pause par llvm_intrinsic). Mojo 1.2.0 (2016d0cd).
from std.sys import size_of, align_of
from std.memory.alloc import unsafe_alloc
from std.collections import List
from std.ffi import UnsafeUnion
from std.simd import FastMathFlag
from std.atomic import fence
from std.sys.intrinsics import llvm_intrinsic
from std.benchmark import black_box

@align(64)
struct Line(ImplicitlyCopyable, Movable):
    var x: Int64
    def __init__(out self, x: Int64):
        self.x = x

@inline(.never)
def stack_addrs(k: Int64) -> Int:
    var pad = Int8(k)  # décale la pile
    var a = Line(k)
    var b = Line(k + 1)
    _ = black_box(pad)
    return (Int(Pointer(to=a)) % 64) + (Int(Pointer(to=b)) % 64)

@inline(.never)
def fma_reassoc(a: Pointer[Float32, MutUntrackedOrigin], b: Pointer[Float32, MutUntrackedOrigin], n: Int) -> Float32:
    var acc = Float32(0)
    for i in range(n):
        acc = a[unsafe_offset=i].fma[FastMathFlag.REASSOC](b[unsafe_offset=i], acc)
    return acc

@inline(.never)
def add_plain(a: Pointer[Int64, MutUntrackedOrigin], b: Pointer[Int64, MutUntrackedOrigin], n: Int):
    for i in range(n):
        a[unsafe_offset=i] = a[unsafe_offset=i] + b[unsafe_offset=0]

@inline(.never)
def add_noalias(a0: Pointer[Int64, MutUntrackedOrigin], b0: Pointer[Int64, MutUntrackedOrigin], n: Int):
    var a = a0.unsafe_as_noalias()
    var b = b0.unsafe_as_noalias()
    for i in range(n):
        a[unsafe_offset=i] = a[unsafe_offset=i] + b[unsafe_offset=0]

@inline(.never)
def spin_hint():
    llvm_intrinsic["llvm.x86.sse2.pause", NoneType]()

@inline(.never)
def full_fence():
    fence()

def main():
    print("A4 align_of[Line] =", align_of[Line](), "size_of[Line] =", size_of[Line]())
    var bad_stack = 0
    for k in range(64):
        bad_stack += stack_addrs(Int64(k))
    print("A4 pile : somme des adresses mod 64 sur 128 objets =", bad_stack)
    var bad_heap = 0
    for k in range(50):
        var p = unsafe_alloc[Line](k + 1)
        bad_heap += Int(p) % 64
    var l = List[Line]()
    for k in range(100):
        l.append(Line(Int64(k)))
    print("A4 tas : unsafe_alloc mod 64 (50 allocations) =", bad_heap, "; List[Line] mod 64 =", Int(l.unsafe_ptr()) % 64)
    comptime U = UnsafeUnion[Float32, UInt32]
    var u = U(Float32(1.0))
    print("A5 size_of[UnsafeUnion[Float32, UInt32]] =", size_of[U](), "; bits de 1.0f =", u.unsafe_get[UInt32]())
    var fa = unsafe_alloc[Float32](16)
    var fb = unsafe_alloc[Float32](16)
    for i in range(16):
        fa[unsafe_offset=i] = Float32(i)
        fb[unsafe_offset=i] = 0.5
    print("C4 fma[REASSOC] =", fma_reassoc(fa, fb, 16))
    var ia = unsafe_alloc[Int64](16)
    var ib = unsafe_alloc[Int64](1)
    ib[unsafe_offset=0] = 3
    for i in range(16):
        ia[unsafe_offset=i] = Int64(i)
    add_plain(ia, ib, 16)
    add_noalias(ia, ib, 16)
    print("E5 a[15] =", ia[unsafe_offset=15])
    spin_hint()
    full_fence()
    print("D5 pause et fence exécutés")
