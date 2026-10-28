"""Implémentation Python 3.15 pure (bibliothèque standard seule, pas de NumPy). Voir docs/SPEC.md.
Exécutée avec CPython 3.15 par défaut (GIL) et avec le build free-threaded (python3.15t)."""
import math
import operator
import os
import queue
import sys
import threading
import time
from array import array
from collections import Counter, deque

# ------------------------------------------------------------------ harnais
DATA = os.environ.get("MS_DATA", "/opt/msdata")
WARMUP = int(os.environ.get("WARMUP", "1"))


def load(name, code):
    a = array(code)
    with open(f"{DATA}/{name}", "rb") as f:
        a.frombytes(f.read())
    return a


def result(k, v, p, rep, sec, chk):
    print(f"RESULT;{k};{v};{p};{rep};{sec:.9f};{chk}", flush=True)


def bench(k, v, p, reps, f):
    for r in range(-WARMUP, reps):
        t0 = time.perf_counter()
        chk = f()
        dt = time.perf_counter() - t0
        if r >= 0:
            result(k, v, p, r, dt, chk)


# ------------------------------------------------------------------ K1
N1 = 1 << 22


class Particle:  # classe ordinaire, comme dans le tutoriel officiel
    def __init__(self, x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.ax, self.ay, self.az = ax, ay, az
        self.mass, self.charge, self.radius = mass, charge, radius
        self.temp, self.pressure, self.energy, self.density = temp, pressure, energy, density


def k1_natural(ps):
    e = 0.0
    for p in ps:
        e += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)
    return e


def k1_aos(f):  # AoS manuel : array('f') entrelacé, tranches étendues (boucles en C)
    vx, vy, vz, m = f[3::16], f[4::16], f[5::16], f[9::16]
    return k1_soa(vx, vy, vz, m)


def k1_soa(vx, vy, vz, m):
    # Σ m·vx² + Σ m·vy² + Σ m·vz² avec math.sumprod (boucle C de la bibliothèque standard)
    mul = operator.mul
    return 0.5 * (math.sumprod(map(mul, m, vx), vx) + math.sumprod(map(mul, m, vy), vy) + math.sumprod(map(mul, m, vz), vz))


def run_k1(v, reps):
    if v == "footprint0":
        result("k1", v, "energy", 0, 0, "0")
        return
    raw = load("k1_particles.f32", "f")
    if v == "aos":
        bench("k1", v, "energy", reps, lambda: f"{k1_aos(raw):.6f}")
        return
    if v == "soa":
        cols = [raw[k::16] for k in range(16)]
        bench("k1", v, "energy", reps, lambda: f"{k1_soa(cols[3], cols[4], cols[5], cols[9]):.6f}")
        return
    ps = [Particle(*raw[16 * i:16 * i + 16]) for i in range(N1)]
    del raw
    if v == "footprint":
        result("k1", v, "energy", 0, 0, f"{k1_natural(ps):.6f}")
        return
    if v == "natural_shuffled":
        perm = load("k1_perm.u32", "I")
        ps = [ps[j] for j in perm]
    bench("k1", v, "energy", reps, lambda: f"{k1_natural(ps):.6f}")


# ------------------------------------------------------------------ K2
def k2_chase(a, h):
    i = 0
    for _ in range(h):
        i = a[i]
    return i


def run_k2(v, reps, p):
    a = load(f"k2_chase_{p}.u32", "I")
    bench("k2", v, p, reps, lambda: str(k2_chase(a, 4200000)))


# ------------------------------------------------------------------ K3
ITER3 = 1 << 25


def run_k3(v, reps):
    rmw = v.startswith("rmw")
    stride = 16 if v.endswith("padded") else 1  # array('q') : 128 o ou 8 o
    print("META;k3_mechanism;" + ("threading.Lock par compteur (Python n'a pas d'atomiques)" if rmw
                                  else "c[i] = c[i] + 1 sur array('q') (sûr grâce au GIL ou à l'écrivain unique)"), flush=True)
    c = array("q", [0] * (16 * 6))
    locks = [threading.Lock() for _ in range(4)]

    def work(t):
        idx = 16 + t * stride
        if rmw:
            lk = locks[t]
            for _ in range(ITER3):
                with lk:
                    c[idx] += 1
        else:
            for _ in range(ITER3):
                c[idx] = c[idx] + 1

    def once():
        for t in range(4):
            c[16 + t * stride] = 0
        th = [threading.Thread(target=work, args=(t,)) for t in range(4)]
        for x in th:
            x.start()
        for x in th:
            x.join()
        return str(sum(c[16 + t * stride] for t in range(4)))
    bench("k3", v, "4x2^25", reps, once)


# ------------------------------------------------------------------ K4
def k4_natural(v):
    s = 0
    for x in v:
        if x >= 128:
            s += x
    return s


def k4_branchless(v):
    return sum(x * (x >> 7) for x in v)


def run_k4(v, reps):
    d = load("k4_bytes.u8", "B").tobytes()
    if v == "natural_sorted":
        d = bytes(sorted(d))
    f = k4_branchless if v == "branchless_unsorted" else k4_natural
    bench("k4", v, "16M", reps, lambda: str(f(d)))


# ------------------------------------------------------------------ K5
INNER5 = 1 << 16


def k5_natural(a, b):
    s = 0.0
    for i in range(len(a)):
        s += a[i] * b[i]
    return s


def run_k5(v, reps):
    a, b = load("k5_a.f32", "f"), load("k5_b.f32", "f")
    f = math.sumprod if v == "tuned" else k5_natural

    def once():
        d = 0.0
        for _ in range(INNER5):
            d = f(a, b)
        return f"{d:.4f}"
    bench("k5", v, "2048x65536", reps, once)


# ------------------------------------------------------------------ K6
N6 = 1 << 24


def q6_natural(c, lo, hi):
    sd, d, q, pr = c["sd"], c["d"], c["q"], c["pr"]
    s = 0
    for i in range(lo, hi):
        if sd[i] >= 8766 and sd[i] < 9131 and d[i] >= 5 and d[i] <= 7 and q[i] < 24:
            s += pr[i] * d[i]
    return s


def q6_tuned(c, lo, hi):
    sd, d, q, pr = c["sd"][lo:hi], c["d"][lo:hi], c["q"][lo:hi], c["pr"][lo:hi]
    return sum(p * dd for s, dd, qq, p in zip(sd, d, q, pr) if 8766 <= s < 9131 and 5 <= dd <= 7 and qq < 24)


def q1_natural(c, lo, hi, acc):
    sd, pr, q, d, t, rf, ls = c["sd"], c["pr"], c["q"], c["d"], c["t"], c["rf"], c["ls"]
    for i in range(lo, hi):
        if sd[i] <= 10471:
            g = (rf[i] * 2 + ls[i]) * 5
            p = pr[i]
            dp = p * (100 - d[i])
            acc[g] += 1
            acc[g + 1] += q[i]
            acc[g + 2] += p
            acc[g + 3] += dp
            acc[g + 4] += dp * (100 + t[i])


def q1_tuned(c, lo, hi, acc):
    sl = slice(lo, hi)
    for s, p, qq, dd, tt, r, l in zip(c["sd"][sl], c["pr"][sl], c["q"][sl], c["d"][sl], c["t"][sl], c["rf"][sl], c["ls"][sl]):
        if s <= 10471:
            a = acc[r * 2 + l]
            dp = p * (100 - dd)
            a[0] += 1
            a[1] += qq
            a[2] += p
            a[3] += dp
            a[4] += dp * (100 + tt)


def run_k6(v, reps, p):
    c = {"sd": load("k6_shipdate.i32", "i"), "pr": load("k6_extendedprice.i32", "i"), "q": load("k6_quantity.u8", "B"),
         "d": load("k6_discount.u8", "B"), "t": load("k6_tax.u8", "B"), "rf": load("k6_returnflag.u8", "B"),
         "ls": load("k6_linestatus.u8", "B")}
    q1 = p == "q1"

    def once():
        if v == "mt":
            part = [0] * 4

            def work(t):
                lo, hi = N6 // 4 * t, N6 // 4 * (t + 1)
                if q1:
                    acc = [[0] * 5 for _ in range(6)]
                    q1_tuned(c, lo, hi, acc)
                    part[t] = sum(map(sum, acc))
                else:
                    part[t] = q6_tuned(c, lo, hi)
            th = [threading.Thread(target=work, args=(t,)) for t in range(4)]
            for x in th:
                x.start()
            for x in th:
                x.join()
            return str(sum(part))
        if q1:
            if v == "tuned":
                acc = [[0] * 5 for _ in range(6)]
                q1_tuned(c, 0, N6, acc)
                return str(sum(map(sum, acc)))
            acc = [0] * 30
            q1_natural(c, 0, N6, acc)
            return str(sum(acc))
        return str(q6_tuned(c, 0, N6) if v == "tuned" else q6_natural(c, 0, N6))
    bench("k6", v, p, reps, once)


# ------------------------------------------------------------------ K7
def run_k7(v, reps):
    keys, vals = load("k7_keys.u32", "I"), load("k7_vals.u32", "I")
    for r in range(-WARMUP, reps):
        if v == "natural":
            t0 = time.perf_counter()
            m = {}
            for k, x in zip(keys, vals):
                e = m.get(k)
                if e is None:
                    m[k] = [1, x]
                else:
                    e[0] += 1
                    e[1] += x
            dt = time.perf_counter() - t0
            nk = len(m)
            ws = sum(e[1] * ((k & 1023) + 1) for k, e in m.items())
        else:  # comptage par collections.Counter (boucle C) + sommes via dict.get
            t0 = time.perf_counter()
            cnt = Counter(keys)
            sums = dict.fromkeys(cnt, 0)
            for k, x in zip(keys, vals):
                sums[k] += x
            dt = time.perf_counter() - t0
            nk = len(cnt)
            ws = sum(s * ((k & 1023) + 1) for k, s in sums.items())
        if r >= 0:
            result("k7", v, "16M/1M", r, dt, f"{nk}:{ws}")


# ------------------------------------------------------------------ K8
class Node:
    __slots__ = ("v", "l", "r")

    def __init__(self, v, l, r):
        self.v, self.l, self.r = v, l, r


class Counter8:
    c = 0


def t_build(dp):
    v = Counter8.c
    Counter8.c += 1
    if dp > 0:
        l = t_build(dp - 1)
        return Node(v, l, t_build(dp - 1))
    return Node(v, None, None)


def t_sum(n):
    return 0 if n is None else n.v + t_sum(n.l) + t_sum(n.r)


AV, AL, AR = [0] * 2047, [-1] * 2047, [-1] * 2047


def a_build(dp, top):  # arène : listes préallouées réutilisées ; renvoie (index, prochain libre)
    i = top
    AV[i] = Counter8.c
    Counter8.c += 1
    if dp > 0:
        l, top = a_build(dp - 1, top + 1)
        r, top = a_build(dp - 1, top)
        AL[i], AR[i] = l, r
        return i, top
    AL[i] = AR[i] = -1
    return i, top + 1


def a_sum(i):
    return 0 if i < 0 else AV[i] + a_sum(AL[i]) + a_sum(AR[i])


def run_k8(v, reps):
    Q = 16384
    sys.setrecursionlimit(10000)
    Counter8.c = 0
    keep = t_build(20)
    lsum = t_sum(keep)
    lat = [0] * Q
    tuned = v == "tuned"
    clock = time.perf_counter_ns
    for r in range(-WARMUP, reps):
        total = 0
        t0 = time.perf_counter()
        for q in range(Q):
            a = clock()
            Counter8.c = q
            if tuned:
                s = a_sum(a_build(10, 0)[0])
            else:
                s = t_sum(t_build(10))
            total += s
            lat[q] = clock() - a
        dt = time.perf_counter() - t0
        if r >= 0:
            result("k8", v, "16384x2047", r, dt, str(total + lsum))
            lat.sort()
            print(f"LAT;{v};{lat[Q // 2]};{lat[Q * 9 // 10]};{lat[Q * 99 // 100]};{lat[Q * 999 // 1000]};{lat[Q - 1]}", flush=True)


# ------------------------------------------------------------------ K9
M9 = 2048


def k9_init(i, j):
    return ((i * 31 + j * 17) % 1024) / 1024.0


def k9_natural(a, b):
    for i in range(1, M9 - 1):
        up, mid, dn, o = a[i - 1], a[i], a[i + 1], b[i]
        for j in range(1, M9 - 1):
            o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1])


def k9_rows(a, b, r0, r1):  # compréhension sur zip : boucle C, mêmes opérations dans le même ordre
    for i in range(r0, r1):
        up, mid, dn = a[i - 1], a[i], a[i + 1]
        b[i][1:M9 - 1] = [0.25 * (((u + d) + l) + r) for u, d, l, r in zip(up[1:M9 - 1], dn[1:M9 - 1], mid[0:M9 - 2], mid[2:M9])]


def run_k9(v, reps):
    for r in range(-WARMUP, reps):
        a = [[k9_init(i, j) for j in range(M9)] for i in range(M9)]
        b = [row[:] for row in a]
        t0 = time.perf_counter()
        for _ in range(4):
            if v == "natural":
                k9_natural(a, b)
            elif v == "tuned":
                k9_rows(a, b, 1, M9 - 1)
            else:
                th = [threading.Thread(target=k9_rows, args=(a, b, 1 + (M9 - 2) * t // 4, 1 + (M9 - 2) * (t + 1) // 4)) for t in range(4)]
                for x in th:
                    x.start()
                for x in th:
                    x.join()
            a, b = b, a
        dt = time.perf_counter() - t0
        s = 0.0
        for row in a:  # somme naïve séquentielle (sum() de Python est compensée depuis 3.12)
            for x in row:
                s += x
        if r >= 0:
            result("k9", v, "2048^2x4", r, dt, f"{s:.15e}")


# ------------------------------------------------------------------ K10
M10 = 1 << 22
CAP10 = 1 << 14


def run_k10(v, reps):
    def once():
        out = [0]
        if v == "natural":
            qq = queue.Queue(maxsize=CAP10)

            def prod():
                for x in range(1, M10 + 1):
                    qq.put(x)

            def cons():
                s = 0
                for _ in range(M10):
                    s += qq.get()
                out[0] = s
        else:  # deque (opérations atomiques en C) + attente active, sans verrou explicite
            dq = deque()

            def prod():
                app = dq.append
                for x in range(1, M10 + 1):
                    while len(dq) >= CAP10:
                        pass
                    app(x)

            def cons():
                s = 0
                pop = dq.popleft
                n = 0
                while n < M10:
                    try:
                        s += pop()
                        n += 1
                    except IndexError:
                        pass
                out[0] = s
        th = [threading.Thread(target=cons), threading.Thread(target=prod)]
        for x in th:
            x.start()
        for x in th:
            x.join()
        return str(out[0])
    bench("k10", v, "2^22", reps, once)


def main():
    k, v, reps = sys.argv[1], sys.argv[2], int(sys.argv[3])
    p = sys.argv[4] if len(sys.argv) > 4 else ""
    {"k1": lambda: run_k1(v, reps), "k2": lambda: run_k2(v, reps, p), "k3": lambda: run_k3(v, reps),
     "k4": lambda: run_k4(v, reps), "k5": lambda: run_k5(v, reps), "k6": lambda: run_k6(v, reps, p),
     "k7": lambda: run_k7(v, reps), "k8": lambda: run_k8(v, reps), "k9": lambda: run_k9(v, reps),
     "k10": lambda: run_k10(v, reps)}[k]()


if __name__ == "__main__":
    main()
