# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Python
# (C5 : dask 2026.8.0 ; D2 : atomics 1.0.3 ; F1 : numpy 2.5.5, nommée). Environnement /opt/open/python (CPython 3.15).
import sys
import threading
import time

import numpy as np
import dask
import dask.array as da
import atomics


def c5():
    x = np.arange(1, 40_000_001, dtype=np.int64)
    d = da.from_array(x, chunks=10_000_000)
    t0 = time.perf_counter()
    s = int(d.sum().compute(scheduler="threads", num_workers=4))
    t1 = time.perf_counter()
    s1 = int(x.sum())
    t2 = time.perf_counter()
    ids = set()

    @dask.delayed
    def part(i):
        ids.add(threading.get_native_id())
        return int(x[i * 10_000_000:(i + 1) * 10_000_000].sum())

    s2 = dask.compute(*[part(i) for i in range(4)], scheduler="threads", num_workers=4)
    print(f"RESULT;C5;dask;dask.array (4 blocs) .sum().compute(scheduler='threads', num_workers=4) = {s} "
          f"(attendu 800000020000000) en {(t1 - t0) * 1e3:.1f} ms, contre {(t2 - t1) * 1e3:.1f} ms pour np.sum seul ; "
          f"4 tâches dask.delayed exécutées sur {len(ids)} fils distincts, somme {sum(s2)}")


def d2():
    a = atomics.atomic(width=8, atype=atomics.INT)

    def work():
        for _ in range(100_000):
            a.fetch_inc(order=atomics.MemoryOrder.RELAXED)

    th = [threading.Thread(target=work) for _ in range(4)]
    for t in th:
        t.start()
    for t in th:
        t.join()
    v = a.load(order=atomics.MemoryOrder.ACQUIRE)
    a.store(7, order=atomics.MemoryOrder.RELEASE)
    try:
        a.store(8, order=atomics.MemoryOrder.ACQUIRE)
        refused = "accepté"
    except Exception as e:
        refused = f"refusé ({type(e).__name__})"
    print(f"RESULT;D2;atomics;atomic(width=8, INT) : 4 fils × 100000 fetch_inc(order=RELAXED) = {v} (attendu 400000) ; "
          f"load(order=ACQUIRE), store(order=RELEASE) puis load = {a.load()} ; store(order=ACQUIRE) {refused}")


def f1():
    m, n = 300 * len(sys.argv), 500
    a = np.zeros((m, n))
    a[2, 3] = 7.0
    flat = a.reshape(-1)
    idx = int(np.argmax(flat == 7.0))
    print(f"RESULT;F1;numpy;np.zeros(({m}, {n})) de dimensions connues à l'exécution : shape {a.shape}, strides {a.strides}, "
          f"C_CONTIGUOUS = {a.flags['C_CONTIGUOUS']}, a[2, 3] = {a[2, 3]} à l'indice {idx} de la vue aplatie (2*{n}+3), "
          f"reshape sans copie = {np.shares_memory(a, flat)}")


c5()
d2()
f1()
