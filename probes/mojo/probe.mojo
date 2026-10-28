from std.sys.intrinsics import prefetch, likely, PrefetchOptions
from std.atomic import Atomic, Ordering
from std.memory import bitcast

def main():
    var a = Atomic[DType.int64](0)
    _ = a.fetch_add[ordering=Ordering.RELAXED](1)
    print("CAP;D2;1;Atomic.fetch_add[ordering=RELAXED]")
    var x: Float32 = 1.0
    print("CAP;A5;0.5;bitcast[DType.uint32] =", bitcast[DType.uint32](x))
    if likely(x == 1.0):
        print("CAP;E3;1;likely")
