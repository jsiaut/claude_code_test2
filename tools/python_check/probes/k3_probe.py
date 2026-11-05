"""Sonde K3 (sw) : 4 fils, compteurs espacés (padded) ou adjacents (packed), ITER incréments chacun.
Modes : array partagé (code publié), memoryview propre à chaque fil, sous-interpréteurs (concurrent.interpreters)
avec une memoryview partagée."""
import sys, threading, time
from array import array
ITER = int(sys.argv[2]) if len(sys.argv) > 2 else 1 << 22
mode = sys.argv[1]

def bench(stride):
    c = array("q", [0] * (16 * 6))
    def work_shared(t):
        idx = 16 + t * stride
        for _ in range(ITER):
            c[idx] = c[idx] + 1
    def work_view(t):
        mv = memoryview(c)
        idx = 16 + t * stride
        for _ in range(ITER):
            mv[idx] = mv[idx] + 1
    if mode in ("shared", "view"):
        f = work_shared if mode == "shared" else work_view
        th = [threading.Thread(target=f, args=(t,)) for t in range(4)]
        t0 = time.perf_counter()
        for x in th: x.start()
        for x in th: x.join()
        dt = time.perf_counter() - t0
    else:
        from concurrent import interpreters
        mv = memoryview(c)
        its = [interpreters.create() for _ in range(4)]
        for t, it in enumerate(its):
            it.prepare_main(mv=mv, idx=16 + t * stride, ITER=ITER)
        code = "for _ in range(ITER):\n    mv[idx] = mv[idx] + 1\n"
        th = [threading.Thread(target=it.exec, args=(code,)) for it in its]
        t0 = time.perf_counter()
        for x in th: x.start()
        for x in th: x.join()
        dt = time.perf_counter() - t0
        for it in its: it.close()
    s = sum(c[16 + t * stride] for t in range(4))
    assert s == 4 * ITER, (s, 4 * ITER)
    return dt

for stride, name in ((16, "padded"), (1, "packed")):
    print(f"{sys.version.split()[0]} GIL={sys._is_gil_enabled()} {mode:7s} {name:6s} {bench(stride):.3f} s", flush=True)
