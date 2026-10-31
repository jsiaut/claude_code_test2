// Sonde de la remarque sur D (docs/DLANG.md) : E3 (core.builtins), E4 (core.simd.prefetch), A3 (champs de bits natifs).
// Sonde E3/E4 (remarque sur D) : API standard de druntime, sans ldc.intrinsics
import core.builtins : likely, unlikely, expect;
import core.simd : prefetch;
import std.stdio : writeln;
pragma(inline, false) long sumHint(const(int)[] a) {
    long s = 0;
    foreach (i, x; a) {
        prefetch!(false, 3)(&a[0] + (i + 64 < a.length ? i + 64 : i));
        if (likely(x >= 0)) s += x; else if (unlikely(x == int.min)) s -= 1;
    }
    return s;
}
// champs de bits natifs (A3), sans -preview=bitfields
struct BF { uint a : 3; uint b : 5; ubyte c; }
void main() {
    auto a = new int[1000];
    foreach (i, ref x; a) x = cast(int) i;
    BF bf; bf.a = 5; bf.b = 17;
    writeln(sumHint(a), " ", BF.sizeof, " ", bf.a, " ", bf.b, " ", expect(3, 3));
}
