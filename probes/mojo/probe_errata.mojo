# Sonde des errata de la remarque sur Mojo (docs/MOJO.md) : A4, A5, C4, D5, E5. Code machine et IR :
# tools/mojo_check/build.sh, results/mojo_check/binaries.txt.
from std.sys import size_of, align_of
from std.memory.alloc import unsafe_alloc
from std.ffi import UnsafeUnion
from std.simd import FastMathFlag
from std.atomic import fence
from std.utils.lock import SpinWaiter
from std.benchmark import black_box

@align(64)
struct Line(ImplicitlyCopyable, Movable):
    var x: Int64
    def __init__(out self, x: Int64):
        self.x = x

@inline(.never)
def stack_mod(k: Int64) -> Int:
    var pad = Int8(k)
    var a = Line(k)
    _ = black_box(pad)
    return Int(Pointer(to=a)) % 64

def main():
    var bad = 0
    for k in range(64):
        bad += stack_mod(Int64(k))
    for k in range(50):
        bad += Int(unsafe_alloc[Line](k + 1)) % 64
    print("CAP;A4;1;@align(64) : align_of =", align_of[Line](), ", somme des adresses mod 64 (64 sur la pile, 50 sur le tas) =", bad)
    var u = UnsafeUnion[Float32, UInt32](Float32(1.0))
    print("CAP;A5;1;UnsafeUnion[Float32, UInt32] : size_of =", size_of[UnsafeUnion[Float32, UInt32]](), ", bits de 1.0f =", u.unsafe_get[UInt32]())
    var x = Float32(black_box(2.0))
    print("CAP;C4;0.5;fma[FastMathFlag.REASSOC] =", x.fma[FastMathFlag.REASSOC](3.0, 1.0), "(seule opération qui prend le drapeau)")
    fence()
    var w = SpinWaiter()
    for _ in range(8):
        w.wait()
    print("CAP;D5;1;fence() et SpinWaiter.wait() exécutés (pause dans le runtime à partir du 4e appel)")
    var a = unsafe_alloc[Int64](1)
    var b = a.unsafe_as_noalias()
    b[unsafe_offset=0] = 7
    print("CAP;E5;1;Pointer.unsafe_as_noalias() :", a[unsafe_offset=0])
