# Audit de la grille, Python 3.15.2 (CPython, construction par défaut avec GIL ; réglages du banc : python3.15) :
# chaque case est exercée sous sa forme la plus forte et imprime un fait observable (docs/V4_PLAN.md 2.1). Lignes FACT
# (reprises par run.sh avec les formes refusées et les recherches) et NOTE.
import array, ctypes, gc, math, mmap, os, random, struct, sys, time, weakref
import concurrent.futures as cf


def fact(c, ev):
    print(f"FACT;{c};{ev}", flush=True)


class P16(ctypes.Structure):
    _fields_ = [(n, ctypes.c_float) for n in "x y z vx vy vz ax ay az m q r t p e d".split()]


class S(ctypes.Structure):
    _fields_ = [("a", ctypes.c_uint8), ("b", ctypes.c_uint32), ("c", ctypes.c_double)]


class Pk(ctypes.Structure):
    _pack_ = 1
    _layout_ = "ms"
    _fields_ = [("a", ctypes.c_uint8), ("b", ctypes.c_uint32), ("f", ctypes.c_uint32, 3)]


class A64(ctypes.Structure):
    _align_ = 64
    _fields_ = [("v", ctypes.c_float)]


class U(ctypes.Union):
    _fields_ = [("f", ctypes.c_float), ("u", ctypes.c_uint32)]


class In(ctypes.Structure):
    _fields_ = [("f", ctypes.c_float * 16), ("n", ctypes.c_int32)]


def cpu_work(n):
    s = 0
    for i in range(n):
        s += i * i
    return s


def main():
    # ---------- A
    arr = (P16 * 1000)()
    fact("A1", f"ctypes (P16 * 1000) : sizeof(P16) = {ctypes.sizeof(P16)} o, élément 1 à {ctypes.addressof(arr[1]) - ctypes.addressof(arr[0])} o (à plat) ; "
               f"une liste d'objets ne tient que des références ({sys.getsizeof([None] * 1000) - sys.getsizeof([])} o pour 1000 cases, objets à part)")
    fact("A2", f"ctypes Structure {{uint8; uint32; double}} : décalages a={S.a.offset} b={S.b.offset} c={S.c.offset}, taille {ctypes.sizeof(S)} (disposition C)")
    fact("A3", f"ctypes _pack_ = 1 et champ de 3 bits : sizeof = {ctypes.sizeof(Pk)}, b à {Pk.b.offset}")
    a64 = (A64 * 2)()
    raw = ctypes.create_string_buffer(256 + 63)
    al = (ctypes.addressof(raw) + 63) & ~63
    fact("A4", f"ctypes _align_ = 64 : alignment(A64) = {ctypes.alignment(A64)}, mais le tampon alloué n'est pas aligné (adresse de a64[0] mod 64 = {ctypes.addressof(a64[0]) % 64}) ; sur-allocation + ctypes.addressof : {al % 64} mod 64 (à la main) ; rien pour les objets Python")
    u = U(f=1.0)
    fact("A5", f"ctypes.Union : float 1.0 relu en uint32 = 0x{u.u:08x} ; struct.unpack('<I', struct.pack('<f', 1.0)) = 0x{struct.unpack('<I', struct.pack('<f', 1.0))[0]:08x}")
    fact("A7", f"ctypes {{c_float * 16; int32}} : sizeof = {ctypes.sizeof(In)}, n à {In.n.offset} (tableau fixe en ligne)")
    fact("A8", f"array : 'b' {array.array('b').itemsize} o, 'h' {array.array('h').itemsize}, 'e' (demi) {array.array('e').itemsize}, 'f' {array.array('f').itemsize} (stockage) ; lus, des int de précision arbitraire et des float de 64 bits")

    # ---------- B
    class O:
        pass
    freed = []
    o = O()
    weakref.finalize(o, lambda: freed.append(True))
    del o
    gc.disable()
    fact("B1", f"comptage de références : objet libéré dès la dernière référence (finaliseur appelé : {bool(freed)}) ; gc.disable() → gc.isenabled() = {gc.isenabled()} (le collecteur de cycles se coupe)")
    gc.enable()
    def pair(i):
        return (i, i + 1)
    b0 = sys.getallocatedblocks()
    keep = [pair(i) for i in range(100000)]
    b1 = sys.getallocatedblocks()
    fact("B3", f"n-uplet rendu par une fonction : {(b1 - b0) / 100000:.1f} blocs alloués par appel, gardés en vie ; aucune valeur composée sur la pile")
    del keep
    x = 1.5
    ids = {id(x + i) for i in range(3)}
    fs = [float(i) + 0.5 for i in range(100000)]
    fact("B4", f"tout est objet : un float occupe {sys.getsizeof(1.5)} o, un int {sys.getsizeof(10**6)} o ; chaque x + i crée un nouvel objet ; une liste de 100 000 float coûte {(sys.getsizeof(fs) + sum(sys.getsizeof(v) for v in fs)) // 100000} o par élément")
    buf = (ctypes.c_uint32 * 8)()
    base = ctypes.addressof(buf)
    ctypes.c_uint32.from_address(base + 12).value = 42
    ctypes.cast(base + 16, ctypes.POINTER(ctypes.c_uint32))[0] = 7
    fact("B5", f"ctypes : écriture par adresse + 12 → buf[3] = {buf[3]} ; pointeur ctypes.cast(adresse + 16) → buf[4] = {buf[4]}")

    # ---------- C
    rnd = random.Random(42)
    big = [rnd.random() - 0.5 for _ in range(1 << 20)]
    s = 0.0
    for v in big:
        s += v
    def pw(a, lo, hi):
        if hi - lo <= 8:
            t = 0.0
            for i in range(lo, hi):
                t += a[i]
            return t
        m = (lo + hi) // 2
        return pw(a, lo, m) + pw(a, m, hi)
    p = pw(big, 0, len(big))
    fact("C4", f"un million de float : boucle {s!r}, somme par paires écrite à la main {p!r} (écart {abs(p - s):.3g}), sum() {sum(big)!r} (compensée), math.fsum {math.fsum(big)!r} (exacte) : aucune option qui autorise la réassociation")
    with cf.ProcessPoolExecutor(4) as ex:
        pids = set(ex.map(lambda_pid, range(16)))
    fact("C5", f"concurrent.futures.ProcessPoolExecutor(4).map : 16 tâches sur {len(pids)} processus (arguments et résultats copiés par pickle) ; multiprocessing.Pool.map aussi")

    # ---------- D
    n = 2_000_000
    t0 = time.perf_counter(); [cpu_work(n) for _ in range(4)]; t1 = time.perf_counter()
    with cf.ThreadPoolExecutor(4) as ex:
        list(ex.map(cpu_work, [n] * 4))
    t2 = time.perf_counter()
    with cf.InterpreterPoolExecutor(4) as ex:
        list(ex.map(cpu_work, [n] * 4))
    t3 = time.perf_counter()
    fact("D1", f"GIL actif (sys._is_gil_enabled() = {sys._is_gil_enabled()}) : 4 calculs en série {t1 - t0:.2f} s, sur 4 fils {t2 - t1:.2f} s (aucun gain), sur 4 sous-interpréteurs (InterpreterPoolExecutor) {t3 - t2:.2f} s")
    before = os.sched_getaffinity(0)
    os.sched_setaffinity(0, {1})
    with open("/proc/self/stat") as f:
        cpu = f.read().rsplit(")", 1)[1].split()[36]
    fact("D4", f"os.sched_setaffinity(0, {{1}}) : {sorted(before)} → {sorted(os.sched_getaffinity(0))}, processeur courant {cpu} (/proc/self/stat)")
    os.sched_setaffinity(0, before)

    # ---------- E
    fact("E1", f"sys._jit.is_available() = {sys._jit.is_available()}, is_enabled() = {sys._jit.is_enabled()} : JIT expérimental absent de cette construction ; dis montre le bytecode, pas le code machine")
    lst = [1, 2, 3, 4]
    try:
        lst[4]; msg = "rien"
    except IndexError as e:
        msg = f"IndexError: {e}"
    ia = (ctypes.c_int32 * 4)(1, 2, 3, 4)
    ptr = ctypes.cast(ia, ctypes.POINTER(ctypes.c_int32))
    fact("E6", f"lst[4] : {msg} ; pointeur ctypes ptr[6] lu sans contrôle hors du tableau de 4 ({type(ptr[6]).__name__})")

    # ---------- F
    mv = memoryview(array.array("d", range(12))).cast("B").cast("d", shape=[3, 4])
    fact("F1", f"memoryview.cast('d', shape=[3, 4]) : m[2, 3] = {mv[2, 3]:.0f}, élément 11 du tampon à plat ; strides {mv.strides}")
    fact("F3", f"int de précision arbitraire : 2**64 + 1 = {2**64 + 1} ; ctypes.c_uint32(2**32 + 5).value = {ctypes.c_uint32(2**32 + 5).value} (enveloppe) ; masques & 0xFFFFFFFF")
    with open("/opt/msdata/k5_a.f32", "rb") as f:
        mm = mmap.mmap(f.fileno(), 8192, access=mmap.ACCESS_READ)
        fl = memoryview(mm).cast("f")
        with open("/proc/self/maps") as m:
            mapped = "/opt/msdata/k5_a.f32" in m.read()
        fact("F4", f"mmap.mmap + memoryview.cast('f') sans copie : k5_a.f32 projeté ({mapped}, /proc/self/maps), premier float {fl[0]:.7g}, dernier {fl[2047]:.8g}")
        fl.release()
        mm.close()


def lambda_pid(_):
    time.sleep(0.05)
    return os.getpid()


if __name__ == "__main__":
    main()
