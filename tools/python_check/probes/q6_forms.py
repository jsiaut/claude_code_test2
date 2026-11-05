"""Sonde Q6 (remarque sur Python, docs/PYTHON.md 2) : formes de Q6 en CPython, même somme attendue (45333132534).
tuned : code publié (zip et générateur) ; columns : masques par bytes.translate combinés en entiers longs, lignes
retenues par itertools.compress, somme par math.sumprod (copie python_exp, validation) ; find : mêmes masques, lignes
retenues par bytes.find (boucle Python sur les seules lignes retenues, 2 % environ).
Usage : python3.15 q6_forms.py [répétitions]"""
import math, os, sys, time
from array import array
from itertools import compress

DATA = os.environ.get("MS_DATA", "/opt/msdata")


def load(name, code):
    a = array(code)
    with open(f"{DATA}/{name}", "rb") as f:
        a.frombytes(f.read())
    return a


def q6_tuned(c, lo, hi):
    sd, d, q, pr = c["sd"][lo:hi], c["d"][lo:hi], c["q"][lo:hi], c["pr"][lo:hi]
    return sum(p * dd for s, dd, qq, p in zip(sd, d, q, pr) if 8766 <= s < 9131 and 5 <= dd <= 7 and qq < 24)


def _tbl(f):
    return bytes(1 if f(x) else 0 for x in range(256))


T_D, T_Q, T_0 = _tbl(lambda x: 5 <= x <= 7), _tbl(lambda x: x < 24), _tbl(lambda x: x == 0)
T_22, T_23 = _tbl(lambda x: x == 0x22), _tbl(lambda x: x == 0x23)
T_GE3E, T_LTAB = _tbl(lambda x: x >= 0x3E), _tbl(lambda x: x < 0xAB)


def mask(c, lo, hi):
    n = hi - lo
    big = lambda b: int.from_bytes(b, "little")
    sdb = c["sd"][lo:hi].tobytes()
    b0, b1, b2, b3 = sdb[0::4], sdb[1::4], sdb[2::4], sdb[3::4]
    m_sd = ((big(b1.translate(T_22)) & big(b0.translate(T_GE3E))) | (big(b1.translate(T_23)) & big(b0.translate(T_LTAB)))) \
        & big(b2.translate(T_0)) & big(b3.translate(T_0))
    return (m_sd & big(c["d"][lo:hi].tobytes().translate(T_D)) & big(c["q"][lo:hi].tobytes().translate(T_Q))).to_bytes(n, "little")


def q6_columns(c, lo, hi):
    m = mask(c, lo, hi)
    return math.sumprod(compress(c["pr"][lo:hi], m), compress(c["d"][lo:hi], m))


def q6_find(c, lo, hi):
    m = mask(c, lo, hi)
    pr, d = c["pr"], c["d"]
    s, i, find = 0, m.find(1), m.find
    while i >= 0:
        s += pr[lo + i] * d[lo + i]
        i = find(1, i + 1)
    return s


c = {"sd": load("k6_shipdate.i32", "i"), "pr": load("k6_extendedprice.i32", "i"), "q": load("k6_quantity.u8", "B"),
     "d": load("k6_discount.u8", "B")}
N = len(c["sd"])
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
for name, f in (("tuned", q6_tuned), ("columns", q6_columns), ("find", q6_find)):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        s = f(c, 0, N)
        ts.append(time.perf_counter() - t0)
    print(f"{sys.version.split()[0]} {name:8s} {s} " + " ".join(f"{1e3 * t:.0f}" for t in ts) + " ms", flush=True)
t0 = time.perf_counter(); m = mask(c, 0, N); tm = time.perf_counter() - t0
print(f"masque seul {1e3 * tm:.0f} ms ; lignes retenues {m.count(1)} sur {N} ({100 * m.count(1) / N:.2f} %)")
