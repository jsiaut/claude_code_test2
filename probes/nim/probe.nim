import std/memfiles, std/atomics, std/sysatomics, std/typedthreads, std/strutils
type
  S = object
    a: uint8
    b: uint32
    c: float64
  P {.packed.} = object
    a: uint8
    b: uint32
  BF = object
    x {.bitsize: 3.}: cuint
    y {.bitsize: 5.}: cuint
  L = object
    v {.align(64).}: int32
  U {.union.} = object
    f: float32
    u: uint32
echo "CAP;A2;1;offsetOf(S, c)=", offsetOf(S, c)
echo "CAP;A3;1;packed sizeof(P)=", sizeof(P), " ; bitsize sizeof(BF)=", sizeof(BF)
echo "CAP;A4;1;align(64) alignof(L)=", alignof(L)
var u: U
u.f = 1.0
echo "CAP;A5;1;union 0x", toHex(u.u)
var mf = memfiles.open("/opt/msdata/k5_a.f32")
let fl = cast[ptr UncheckedArray[float32]](mf.mem)
echo "CAP;F4;1;std/memfiles : ", fl[0]
cpuRelax()
fence(moSequentiallyConsistent)
echo "CAP;D5;1;cpuRelax + fence"
if likely(true): echo "CAP;E3;1;likely/unlikely"
