import std.stdio, std.bitmanip, std.mmfile, core.atomic;
struct S { ubyte a; uint b; double c; }
struct P { align(1): ubyte a; uint b; }
struct BF { mixin(bitfields!(uint, "x", 3, uint, "y", 5)); }
struct L { align(64) int v; }
union U { float f; uint u; }
void main() {
    writefln("CAP;A2;1;S.c.offsetof=%d", S.c.offsetof);
    writefln("CAP;A3;1;align(1) P.sizeof=%d ; bitfields BF.sizeof=%d", P.sizeof, BF.sizeof);
    writefln("CAP;A4;1;align(64) L.alignof=%d", L.alignof);
    U u; u.f = 1.0f;
    writefln("CAP;A5;1;union 0x%x", u.u);
    auto mm = new MmFile("/opt/msdata/k5_a.f32");
    auto fl = cast(float[]) mm[];
    writefln("CAP;F4;1;std.mmfile + cast : %s", fl[0]);
    pause();
    writefln("CAP;D5;1;core.atomic.pause + atomicFence");
}
