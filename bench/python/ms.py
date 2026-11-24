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


# ------------------------------------------------------------------ sous-interpréteurs
# remarque sur Python (docs/PYTHON.md) : de vrais fils parallèles dans le build par défaut : des sous-interpréteurs
# de la bibliothèque standard (concurrent.interpreters, depuis 3.14), chacun avec son propre verrou global, chacun sur
# son fil ; ils sont créés avant la mesure (comme les Workers de JavaScript) et ne partagent que des tampons
# (memoryview).
def sub_pool(n, setup, **shared):
    from concurrent import interpreters
    its = []
    for t in range(n):
        it = interpreters.create()
        it.prepare_main(t=t, **shared)
        it.exec(setup)
        its.append(it)
    return its


def sub_run(its, code):
    th = [threading.Thread(target=it.exec, args=(code,)) for it in its]
    for x in th:
        x.start()
    for x in th:
        x.join()


def sub_close(its):
    for it in its:
        it.close()


# v4, point 4 (docs/V4_CONVERGE.md, 3.3, mt_pool) : réserve de quatre fils de travail, le fil principal compris, chacun
# lié à un des sous-interpréteurs (créés avant la mesure, comme pour mt). Les trois autres fils sont créés une fois par
# processus, avant l'échauffement ; à chaque appel, une barrière (threading.Barrier) les réveille, chacun exécute le
# code dans son sous-interpréteur (le fil principal dans le premier : le quart 0) et une seconde barrière attend leur
# fin ; entre deux appels, ils attendent, bloqués, à la première barrière. (La variante mt crée ses quatre fils à
# chaque appel : sub_run.)
class SubPool:
    def __init__(self, its):
        self.its, self.code, self.quit = its, None, False
        self.go, self.done = threading.Barrier(len(its)), threading.Barrier(len(its))
        self.th = [threading.Thread(target=self._loop, args=(it,), daemon=True) for it in its[1:]]
        for x in self.th:
            x.start()

    def _loop(self, it):
        while True:
            self.go.wait()
            if self.quit:
                return
            it.exec(self.code)
            self.done.wait()

    def run(self, code):
        self.code = code
        self.go.wait()
        self.its[0].exec(code)
        self.done.wait()

    def close(self):
        self.quit = True
        self.go.wait()
        for x in self.th:
            x.join()
        sub_close(self.its)

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


def rss_now():
    """Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)."""
    with open("/proc/self/statm") as f:
        return int(f.read().split()[1]) * 4096


def run_k1(v, reps):
    if v == "footprint0":
        result("k1", v, "energy", 0, 0, "0")
        return
    raw = load("k1_particles.f32", "f")
    if v == "footprint_raw":
        result("k1", v, "energy", 0, 0, "0")
        return
    if v == "aos":
        bench("k1", v, "energy", reps, lambda: f"{k1_aos(raw):.6f}")
        return
    if v == "soa":
        cols = [raw[k::16] for k in range(16)]
        bench("k1", v, "energy", reps, lambda: f"{k1_soa(cols[3], cols[4], cols[5], cols[9]):.6f}")
        return
    m1 = rss_now() if v == "footprint" else 0  # P1 : tampon brut chargé
    ps = [Particle(*raw[16 * i:16 * i + 16]) for i in range(N1)]
    if v == "footprint":
        m2 = rss_now()  # P2 : collection construite, tampon brut encore vivant
        print(f"META;mem;rss;{m1};{m2}\nMETA;rss;{m1};{m2}\nMETA;raw0;{raw[0]}", flush=True)
        result("k1", v, "energy", 0, 0, f"{k1_natural(ps):.6f}")
        return
    del raw
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
    print("META;k3_mechanism;" + ("sous-interpréteurs (un fil chacun) ; threading.Lock par compteur, propre à son "
                                  "sous-interpréteur (Python n'a pas d'atomiques)" if rmw
                                  else "sous-interpréteurs (un fil chacun) ; c[i] = c[i] + 1 sur une memoryview partagée "
                                  "de array('q') (écrivain unique)"), flush=True)
    c = array("q", [0] * (16 * 6))
    setup = """
import threading
def work():
    idx = 16 + t * stride
    m = mv
    if rmw:
        lk = threading.Lock()
        for _ in range(ITER):
            with lk:
                m[idx] += 1
    else:
        for _ in range(ITER):
            m[idx] = m[idx] + 1
"""
    its = sub_pool(4, setup, mv=memoryview(c), stride=stride, ITER=ITER3, rmw=rmw)

    def once():
        for t in range(4):
            c[16 + t * stride] = 0
        sub_run(its, "work()")
        return str(sum(c[16 + t * stride] for t in range(4)))
    bench("k3", v, "4x2^25", reps, once)
    sub_close(its)


# ------------------------------------------------------------------ K4
def k4_natural(v):
    s = 0
    for x in v:
        if x >= 128:
            s += x
    return s


def k4_branchless(v):
    return sum(x * (x >> 7) for x in v)


# v4, point 3 (docs/V4_EQUAL.md, R3) : variante tuned. Python n'a pas de SIMD : la meilleure forme trouvée dans la
# bibliothèque standard laisse la boucle au C : bytes.translate remplace les octets < 128 par 0, sum() additionne les
# octets (0,10 s, contre 0,47 pour la boucle naturelle, 0,65 pour collections.Counter et 1,8 pour 128 appels de
# bytes.count).
K4_TABLE = bytes(b if b >= 128 else 0 for b in range(256))


def k4_tuned(v):
    return sum(v.translate(K4_TABLE))


# v4, point 4 (3.3, swar) : huit octets par mot de 64 bits (vue memoryview « Q » des octets, dans le chrono). Par mot
# w : m = (w >> 7) & 0x0101…01 (le bit de poids fort de chaque octet), y = w & (m * 0xFF) (octets >= 128 gardés, les
# autres à zéro), puis les octets de rang pair et impair ajoutés en quatre voies de 16 bits, vidées toutes les 128 mots
# (au plus 128 × 510 = 65 280 < 2^16 par voie). Les n mod 8 derniers octets : x * (x >> 7).
def k4_swar(v):
    n = len(v)
    nw = n >> 3
    w = memoryview(v)[:nw * 8].cast("Q")
    s = 0
    for i0 in range(0, nw, 128):
        acc = 0
        for x in w[i0:i0 + 128]:
            y = x & (((x >> 7) & 0x0101010101010101) * 0xFF)
            acc += (y & 0x00FF00FF00FF00FF) + ((y >> 8) & 0x00FF00FF00FF00FF)
        acc = (acc & 0x0000FFFF0000FFFF) + ((acc >> 16) & 0x0000FFFF0000FFFF)
        s += (acc & 0xFFFFFFFF) + (acc >> 32)
    for x in v[nw * 8:]:
        s += x * (x >> 7)
    return s


def run_k4(v, reps):
    d = load("k4_bytes.u8", "B").tobytes()
    if v == "natural_sorted":
        d = bytes(sorted(d))
    f = k4_tuned if v == "tuned" else k4_swar if v == "swar" else k4_branchless if v == "branchless_unsorted" else k4_natural
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


# v4, point 4 (3.3, Q6 tuned_s) : sans branchement : les trois tests d'intervalle en différences non signées et
# comparaisons (booléens 0/1 réunis par &), s += prix × remise × m (entiers de Python, exacts)
def q6_tuned_s(c, lo, hi):
    sd, d, q, pr = c["sd"][lo:hi], c["d"][lo:hi], c["q"][lo:hi], c["pr"][lo:hi]
    return sum(p * dd * ((((s - 8766) & 0xFFFFFFFF) < 365) & (((dd - 5) & 0xFF) < 3) & (qq < 24))
               for s, dd, qq, p in zip(sd, d, q, pr))


# v4, point 4 (docs/V4_CONVERGE.md, 3.5 et 4.2, forme propre au runtime) : rq_cols, la forme de la remarque sur Python
# (bench/python_exp, tuned_c ; docs/PYTHON.md : × 0,35), recopiée : Q6 en colonnes, boucles en C de la bibliothèque
# standard.
# Masques 0/1 par bytes.translate (sd : octets 0 et 1 de l'entier 32 bits petit-boutiste, octets 2 et 3 nuls ;
# 8766 = 0x223E, 9131 = 0x23AB), combinés par entiers longs ; lignes retenues (1,8 %) trouvées par bytes.find.
def _tbl(f):
    return bytes(1 if f(x) else 0 for x in range(256))


T_D, T_Q, T_0 = _tbl(lambda x: 5 <= x <= 7), _tbl(lambda x: x < 24), _tbl(lambda x: x == 0)
T_22, T_23 = _tbl(lambda x: x == 0x22), _tbl(lambda x: x == 0x23)
T_GE3E, T_LTAB = _tbl(lambda x: x >= 0x3E), _tbl(lambda x: x < 0xAB)


def q6_columns(c, lo, hi):
    n = hi - lo
    big = lambda b: int.from_bytes(b, "little")
    sdb = c["sd"][lo:hi].tobytes()
    b0, b1, b2, b3 = sdb[0::4], sdb[1::4], sdb[2::4], sdb[3::4]
    m_sd = ((big(b1.translate(T_22)) & big(b0.translate(T_GE3E))) | (big(b1.translate(T_23)) & big(b0.translate(T_LTAB)))) \
        & big(b2.translate(T_0)) & big(b3.translate(T_0))
    m = (m_sd & big(c["d"][lo:hi].tobytes().translate(T_D)) & big(c["q"][lo:hi].tobytes().translate(T_Q))).to_bytes(n, "little")
    pr, d, find = c["pr"], c["d"], m.find
    s, i = 0, find(1)
    while i >= 0:
        s += pr[lo + i] * d[lo + i]
        i = find(1, i + 1)
    return s


# v4, point 4 (3.3, Q1 tuned_s) : une passe, les 30 accumulateurs en variables locales ; par ligne, pm = -1 si
# shipdate <= 10471 (décalage arithmétique du signe de shipdate - 10472), et pour chaque groupe k,
# mk = pm & (signe de (g ^ k) - 1), -1 si g = k ; additions masquées par & mk, sans branchement (entiers exacts)
def q1_tuned_s(c, lo, hi):
    sl = slice(lo, hi)
    n0 = q0 = p0 = e0 = c0 = n1 = q1 = p1 = e1 = c1 = n2 = q2 = p2 = e2 = c2 = 0
    n3 = q3 = p3 = e3 = c3 = n4 = q4 = p4 = e4 = c4 = n5 = q5 = p5 = e5 = c5 = 0
    for s, p, qq, dd, tt, r, l in zip(c["sd"][sl], c["pr"][sl], c["q"][sl], c["d"][sl], c["t"][sl], c["rf"][sl], c["ls"][sl]):
        pm = (s - 10472) >> 63
        g = r * 2 + l
        dp = p * (100 - dd)
        ch = dp * (100 + tt)
        m = pm & ((g - 1) >> 63)
        n0 -= m; q0 += qq & m; p0 += p & m; e0 += dp & m; c0 += ch & m
        m = pm & (((g ^ 1) - 1) >> 63)
        n1 -= m; q1 += qq & m; p1 += p & m; e1 += dp & m; c1 += ch & m
        m = pm & (((g ^ 2) - 1) >> 63)
        n2 -= m; q2 += qq & m; p2 += p & m; e2 += dp & m; c2 += ch & m
        m = pm & (((g ^ 3) - 1) >> 63)
        n3 -= m; q3 += qq & m; p3 += p & m; e3 += dp & m; c3 += ch & m
        m = pm & (((g ^ 4) - 1) >> 63)
        n4 -= m; q4 += qq & m; p4 += p & m; e4 += dp & m; c4 += ch & m
        m = pm & (((g ^ 5) - 1) >> 63)
        n5 -= m; q5 += qq & m; p5 += p & m; e5 += dp & m; c5 += ch & m
    return (n0 + q0 + p0 + e0 + c0 + n1 + q1 + p1 + e1 + c1 + n2 + q2 + p2 + e2 + c2
            + n3 + q3 + p3 + e3 + c3 + n4 + q4 + p4 + e4 + c4 + n5 + q5 + p5 + e5 + c5)


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
    # v4, point 4 : mt_pool (formes publiées), mt_pool_s (tuned_s), rq_cols_mt (Q6 en colonnes) : réserve SubPool
    pools = ("mt_pool", "mt_pool_s", "rq_cols_mt")
    if v == "mt" or v in pools:
        import inspect
        part = array("q", [0] * 4)
        setup = (inspect.getsource(q6_tuned) + inspect.getsource(q1_tuned) + inspect.getsource(q6_tuned_s)
                 + inspect.getsource(q1_tuned_s) + inspect.getsource(q6_columns)) + """
c = {"sd": sd, "pr": pr, "q": q, "d": d, "t": tx, "rf": rf, "ls": ls}
lo, hi = N6 // 4 * t, N6 // 4 * (t + 1)
def work():
    if q1 and form == 1:
        part[t] = q1_tuned_s(c, lo, hi)
    elif q1:
        acc = [[0] * 5 for _ in range(6)]
        q1_tuned(c, lo, hi, acc)
        part[t] = sum(map(sum, acc))
    else:
        part[t] = q6_tuned_s(c, lo, hi) if form == 1 else q6_columns(c, lo, hi) if form == 2 else q6_tuned(c, lo, hi)
"""
        its = sub_pool(4, setup, sd=memoryview(c["sd"]), pr=memoryview(c["pr"]), q=memoryview(c["q"]),
                       d=memoryview(c["d"]), tx=memoryview(c["t"]), rf=memoryview(c["rf"]), ls=memoryview(c["ls"]),
                       part=memoryview(part), N6=N6, q1=q1, form={"mt_pool_s": 1, "rq_cols_mt": 2}.get(v, 0),
                       T_D=T_D, T_Q=T_Q, T_0=T_0, T_22=T_22, T_23=T_23, T_GE3E=T_GE3E, T_LTAB=T_LTAB)
        pool = SubPool(its) if v in pools else None

    def once():
        if v == "mt" or v in pools:
            for t in range(4):
                part[t] = 0
            if pool is None:
                sub_run(its, "work()")
            else:
                pool.run("work()")
            return str(sum(part))
        if v == "tuned_s":
            return str(q1_tuned_s(c, 0, N6) if q1 else q6_tuned_s(c, 0, N6))
        if v == "rq_cols" and not q1:
            return str(q6_columns(c, 0, N6))
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
    if v == "mt":
        sub_close(its)
    elif v in pools:
        pool.close()


# ------------------------------------------------------------------ K7
# v4, point 4 (3.3, K7 tuned_oa : forme de repli, Python n'ayant pas de préchargement) : la table de tuned_pf sans
# préchargement : capacité 2^(LOG2+1), cases de 16 octets contiguës dans un array('Q') (clé << 32 | compte, somme),
# allouée et remise à zéro dans le chrono, hachage de Fibonacci (clé × 0x9E3779B1 mod 2^32) >> (32 − LOG), sondage
# linéaire ; une case est vide si son premier mot vaut 0 (un compte vaut au moins 1)
def k7_tuned_oa(keys, vals, log):
    cap = 1 << log
    msk, sh = cap - 1, 32 - log
    tab = array("Q", [0]) * (2 * cap)
    for k, x in zip(keys, vals):
        s = ((k * 0x9E3779B1) & 0xFFFFFFFF) >> sh
        while True:
            w = tab[2 * s]
            if w == 0:
                tab[2 * s] = (k << 32) | 1
                tab[2 * s + 1] = x
                break
            if w >> 32 == k:
                tab[2 * s] = w + 1
                tab[2 * s + 1] += x
                break
            s = (s + 1) & msk
    return tab


def run_k7(v, reps):
    keys, vals = load("k7_keys.u32", "I"), load("k7_vals.u32", "I")
    for r in range(-WARMUP, reps):
        if v == "tuned_oa":
            t0 = time.perf_counter()
            tab = k7_tuned_oa(keys, vals, 21)
            dt = time.perf_counter() - t0
            nk = ws = 0
            for s in range(0, len(tab), 2):
                w = tab[s]
                if w:
                    nk += 1
                    ws += tab[s + 1] * (((w >> 32) & 1023) + 1)
        elif v == "natural":
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


# v4, point 4 (3.3, K8 tuned_val) : la même arène (listes AV, AL, AR), construite en ordre préfixe ; l'état passe par
# valeur (i : indice du nœud ; q : numéro de requête, valeur du nœud = q + i), le prochain indice libre revient en
# résultat ; ni compteur de classe ni n-uplet. Somme : a_sum (récursive, par les liens).
def a_build_val(i, dp, q):
    AV[i] = q + i
    if dp == 0:
        AL[i] = AR[i] = -1
        return i + 1
    l = i + 1
    r = a_build_val(l, dp - 1, q)
    AL[i] = l
    AR[i] = r
    return a_build_val(r, dp - 1, q)


# v4, point 4 (3.3, K8 tuned_it) : la même arène, construction et somme itératives avec des piles explicites de 64
# entrées (listes allouées une fois) ; la construction descend à gauche en empilant le sous-arbre droit de chaque nœud
# interne, puis le reprend à la feuille suivante (même ordre préfixe, mêmes valeurs que a_build). La profondeur doit
# rester sous 63 (vérifié dans run_k8).
STP, STD, STS = [0] * 64, [0] * 64, [0] * 64


def a_build_it(depth, q):
    sp, i, parent, right, d = 0, 0, -1, False, depth
    while True:
        AV[i] = q + i
        if parent >= 0:
            if right:
                AR[parent] = i
            else:
                AL[parent] = i
        if d > 0:
            STP[sp] = i
            STD[sp] = d - 1
            sp += 1
            parent, right, d = i, False, d - 1
        else:
            AL[i] = AR[i] = -1
            if sp == 0:
                return
            sp -= 1
            parent, d, right = STP[sp], STD[sp], True
        i += 1


def a_sum_it(root):
    STS[0] = root
    sp, s = 1, 0
    while sp:
        sp -= 1
        i = STS[sp]
        s += AV[i]
        l = AL[i]
        if l >= 0:
            STS[sp] = AR[i]
            STS[sp + 1] = l
            sp += 2
    return s


def run_k8(v, reps):
    Q = 16384
    sys.setrecursionlimit(10000)
    Counter8.c = 0
    keep = t_build(20)
    lsum = t_sum(keep)
    lat = [0] * Q
    tuned = v == "tuned"
    tval, tit, d8 = v == "tuned_val", v == "tuned_it", 10  # v4, point 4
    if tit and d8 >= 63:
        raise SystemExit("K8 tuned_it : piles de 64 entrées, la profondeur doit rester sous 63")
    clock = time.perf_counter_ns
    for r in range(-WARMUP, reps):
        total = 0
        t0 = time.perf_counter()
        for q in range(Q):
            a = clock()
            Counter8.c = q
            if tval:
                a_build_val(0, d8, q)
                s = a_sum(0)
            elif tit:
                a_build_it(d8, q)
                s = a_sum_it(0)
            elif tuned:
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


# v4, point 3 (docs/V4_EQUAL.md, R2) : naturel en grille contiguë, une seule liste indexée i * M9 + j ; même boucle que le
# naturel publié, qui sort les lignes de la boucle intérieure : ici, leurs décalages
def k9_natural_flat(a, b):
    for i in range(1, M9 - 1):
        up, mid, dn = (i - 1) * M9, i * M9, (i + 1) * M9
        for j in range(1, M9 - 1):
            b[mid + j] = 0.25 * (((a[up + j] + a[dn + j]) + a[mid + j - 1]) + a[mid + j + 1])


def k9_rows(a, b, r0, r1):  # compréhension sur zip : boucle C, mêmes opérations dans le même ordre
    for i in range(r0, r1):
        up, mid, dn = a[i - 1], a[i], a[i + 1]
        b[i][1:M9 - 1] = [0.25 * (((u + d) + l) + r) for u, d, l, r in zip(up[1:M9 - 1], dn[1:M9 - 1], mid[0:M9 - 2], mid[2:M9])]


K9_SUB = """
from array import array
def rows(A, B, r0, r1):
    for i in range(r0, r1):
        up, mid, dn = A[(i - 1) * M9:i * M9], A[i * M9:(i + 1) * M9], A[(i + 1) * M9:(i + 2) * M9]
        B[i * M9 + 1:(i + 1) * M9 - 1] = array("d", [0.25 * (((u + d) + l) + r) for u, d, l, r in
                                                     zip(up[1:M9 - 1], dn[1:M9 - 1], mid[0:M9 - 2], mid[2:M9])])
r0, r1 = 1 + (M9 - 2) * t // 4, 1 + (M9 - 2) * (t + 1) // 4
def work():
    if ctl[0] == 0:
        rows(ga, gb, r0, r1)
    else:
        rows(gb, ga, r0, r1)
"""


def run_k9_mt(v, reps):
    """K9 mt sur sous-interpréteurs : deux grilles plates array('d') allouées une fois par processus (harnais commun),
    réinitialisées hors chrono ; mêmes opérations que k9_rows, dans le même ordre ; somme de contrôle dans le même
    ordre (ligne par ligne)."""
    init = array("d", (k9_init(i, j) for i in range(M9) for j in range(M9)))
    ga, gb, ctl = array("d", init), array("d", init), array("q", [0])
    its = sub_pool(4, K9_SUB, ga=memoryview(ga), gb=memoryview(gb), ctl=memoryview(ctl), M9=M9)
    pool = SubPool(its) if v == "mt_pool" else None  # v4, point 4 : réserve de fils (chaque quart : rows publiée)
    for r in range(-WARMUP, reps):
        ga[:] = init
        gb[:] = init
        t0 = time.perf_counter()
        for it in range(4):
            ctl[0] = it % 2
            if pool is None:
                sub_run(its, "work()")
            else:
                pool.run("work()")
        dt = time.perf_counter() - t0
        a = ga if ctl[0] == 1 else gb  # après 4 itérations : a = ga (comme a, b = b, a quatre fois)
        s = 0.0
        for x in a:
            s += x
        if r >= 0:
            result("k9", v, "2048^2x4", r, dt, f"{s:.15e}")
    if pool is None:
        sub_close(its)
    else:
        pool.close()


def run_k9(v, reps):
    # harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono
    if v in ("mt", "mt_pool"):
        run_k9_mt(v, reps)
        return
    if v == "natural_flat":  # v4, point 3 (docs/V4_EQUAL.md, R2) : K9 naturel contigu, au harnais commun de K9
        finit = [k9_init(k // M9, k % M9) for k in range(M9 * M9)]
        fa, fb = finit[:], finit[:]
        for r in range(-WARMUP, reps):
            fa[:] = finit
            fb[:] = finit
            a, b = fa, fb
            t0 = time.perf_counter()
            for _ in range(4):
                k9_natural_flat(a, b)
                a, b = b, a
            dt = time.perf_counter() - t0
            s = 0.0
            for x in a:  # somme naïve séquentielle, comme le naturel publié
                s += x
            if r >= 0:
                result("k9", v, "2048^2x4", r, dt, f"{s:.15e}")
        return
    init = [[k9_init(i, j) for j in range(M9)] for i in range(M9)]
    ga = [row[:] for row in init]
    gb = [row[:] for row in init]
    for r in range(-WARMUP, reps):
        for i in range(M9):
            ga[i][:] = init[i]
            gb[i][:] = init[i]
        a, b = ga, gb
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
