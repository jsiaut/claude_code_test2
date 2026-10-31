// Sonde des errata de la remarque sur D (docs/DLANG.md) : E3 (core.builtins) et E4 (core.simd.prefetch), API de druntime ;
// A3, champs de bits natifs sans -preview.
import core.builtins : likely, unlikely;
import core.simd : prefetch;
import std.stdio : writefln;
pragma(inline, false) long hinted(const(int)[] a) {
    long s = 0;
    foreach (i, x; a) {
        prefetch!(false, 3)(a.ptr + (i + 64 < a.length ? i + 64 : i));
        if (likely(x >= 0)) s += x; else if (unlikely(x == int.min)) s -= 1;
    }
    return s;
}
struct NativeBF { uint a : 3; uint b : 5; }
void main() {
    auto a = new int[1000];
    foreach (i, ref x; a) x = cast(int) i;
    const s = hinted(a);
    writefln("CAP;E3;1;core.builtins.likely/unlikely (druntime) : somme %d", s);
    writefln("CAP;E4;1;core.simd.prefetch!(false, 3) (druntime) : prefetcht0, somme %d", s);
    NativeBF bf; bf.a = 5; bf.b = 17;
    writefln("CAP;A3;1;champs de bits natifs sans -preview : NativeBF.sizeof=%d a=%d b=%d", NativeBF.sizeof, bf.a, bf.b);
}
