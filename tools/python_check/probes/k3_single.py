"""Sonde K3, un seul fil (référence de k3_probe.py) : ITER incréments dans une fonction, sur l'array ou par une
memoryview. Usage : python3.15 k3_single.py [ITER]"""
import sys, time
from array import array
ITER = int(sys.argv[1]) if len(sys.argv) > 1 else 1 << 22


def work(c, idx):
    for _ in range(ITER):
        c[idx] = c[idx] + 1


for name in ("array", "view"):
    a = array("q", [0] * 96)
    c = a if name == "array" else memoryview(a)
    t0 = time.perf_counter()
    work(c, 16)
    dt = time.perf_counter() - t0
    assert a[16] == ITER
    print(f"{sys.version.split()[0]} GIL={sys._is_gil_enabled()} un fil  {name:6s} {dt:.3f} s", flush=True)
