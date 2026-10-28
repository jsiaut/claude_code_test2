import ctypes, mmap, os
class S(ctypes.Structure):
    _fields_ = [("a", ctypes.c_uint8), ("b", ctypes.c_uint32), ("c", ctypes.c_double)]
class P(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("a", ctypes.c_uint8), ("b", ctypes.c_uint32), ("x", ctypes.c_uint32, 3)]
print(f"CAP;A2;0.5;ctypes S.c.offset={S.c.offset}")
print(f"CAP;A3;0.5;ctypes _pack_=1 et champ de 3 bits : sizeof(P)={ctypes.sizeof(P)}")
with open("/opt/msdata/k5_a.f32", "rb") as f:
    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    v = memoryview(m).cast("f")
    print(f"CAP;F4;1;mmap + memoryview.cast('f') sans copie : {v[0]}")
    v.release()
os.sched_setaffinity(0, {0})
print(f"CAP;D4;0.5;os.sched_setaffinity -> {os.sched_getaffinity(0)}")
