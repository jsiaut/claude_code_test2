#!/usr/bin/env python3
"""Copies de la remarque sur Python (plan : docs/PYTHON.md, section 3.3), produites par remplacements de texte contrôlés
(chaque texte remplacé doit apparaître exactement une fois ; le reste du fichier est identique à l'octet).

* bench/python_ref : copie exacte de bench/python_k9h (le code publié, harnais commun de K9), CPython 3.15.2 par défaut.
* bench/python_fix : correction publiée : K3 (quatre variantes), K6 `mt` (Q6 et Q1) et K9 `mt` sur de vrais fils
  parallèles du build par défaut, par des sous-interpréteurs de la bibliothèque standard (`concurrent.interpreters`,
  depuis 3.14 ; un verrou global par interpréteur), créés avant la mesure comme les Workers de JavaScript, les données
  partagées par `memoryview` ; la spécification de K3 exige « de vrais threads matériels parallèles », et Mojo
  (module privé livré avec sa bibliothèque standard) et JavaScript (Workers) en obtiennent par ce qu'ils livrent.
  K9 `mt` passe pour cela à deux grilles plates (`array('d')`), mêmes opérations dans le même ordre.
* bench/python_exp : python_fix et des variantes nouvelles (sensibilités) : K6 `tuned_c` et `mt_c` (Q6 en colonnes :
  masques calculés en C par `bytes.translate`, combinés par entiers longs, lignes retenues trouvées par `bytes.find`,
  seule boucle Python ; `mt_c` : la même fonction dans les quatre sous-interpréteurs de `mt`) ; K8 `natural_f`
  (`gc.freeze()` après la construction de l'arbre longue durée).
* bench/python_ftfix : le code publié exécuté par le build sans GIL (python3.15t, l'annexe `python_ft`), K3 corrigé :
  une `memoryview` propre à chaque fil sur le même tampon, au lieu d'un objet `array` partagé, dont le verrou d'objet du
  build sans GIL sérialise les fils (annexe ; sensibilité S-FT).
Usage : make_copies.py"""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTE = "# remarque sur Python (docs/PYTHON.md) : "


def sub(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"texte trouvé {n} fois (1 attendu) :\n{old[:300]}")
    return text.replace(old, new)


SUBS = '''

# ------------------------------------------------------------------ sous-interpréteurs
''' + NOTE + '''de vrais fils parallèles dans le build par défaut : des sous-interpréteurs
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

'''

FIX = [
    # harnais : sous-interpréteurs
    ("""# ------------------------------------------------------------------ K1
N1 = 1 << 22
""", SUBS.lstrip("\n") + """# ------------------------------------------------------------------ K1
N1 = 1 << 22
"""),
    # K3 : quatre sous-interpréteurs sur une memoryview partagée
    ('''    print("META;k3_mechanism;" + ("threading.Lock par compteur (Python n'a pas d'atomiques)" if rmw
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
''', '''    print("META;k3_mechanism;" + ("sous-interpréteurs (un fil chacun) ; threading.Lock par compteur, propre à son "
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
'''),
    # K6 mt : sous-interpréteurs, colonnes partagées par memoryview
    ('''    q1 = p == "q1"

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
''', '''    q1 = p == "q1"
    if v == "mt":
        import inspect
        part = array("q", [0] * 4)
        setup = inspect.getsource(q6_tuned) + inspect.getsource(q1_tuned) + """
c = {"sd": sd, "pr": pr, "q": q, "d": d, "t": tx, "rf": rf, "ls": ls}
lo, hi = N6 // 4 * t, N6 // 4 * (t + 1)
def work():
    if q1:
        acc = [[0] * 5 for _ in range(6)]
        q1_tuned(c, lo, hi, acc)
        part[t] = sum(map(sum, acc))
    else:
        part[t] = q6_tuned(c, lo, hi)
"""
        its = sub_pool(4, setup, sd=memoryview(c["sd"]), pr=memoryview(c["pr"]), q=memoryview(c["q"]),
                       d=memoryview(c["d"]), tx=memoryview(c["t"]), rf=memoryview(c["rf"]), ls=memoryview(c["ls"]),
                       part=memoryview(part), N6=N6, q1=q1)

    def once():
        if v == "mt":
            for t in range(4):
                part[t] = 0
            sub_run(its, "work()")
            return str(sum(part))
'''),
    ('''        return str(q6_tuned(c, 0, N6) if v == "tuned" else q6_natural(c, 0, N6))
    bench("k6", v, p, reps, once)
''', '''        return str(q6_tuned(c, 0, N6) if v == "tuned" else q6_natural(c, 0, N6))
    bench("k6", v, p, reps, once)
    if v == "mt":
        sub_close(its)
'''),
    # K9 mt : grilles plates partagées, sous-interpréteurs
    ('''def run_k9(v, reps):
    # harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono
''', '''K9_SUB = """
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
    for r in range(-WARMUP, reps):
        ga[:] = init
        gb[:] = init
        t0 = time.perf_counter()
        for it in range(4):
            ctl[0] = it % 2
            sub_run(its, "work()")
        dt = time.perf_counter() - t0
        a = ga if ctl[0] == 1 else gb  # après 4 itérations : a = ga (comme a, b = b, a quatre fois)
        s = 0.0
        for x in a:
            s += x
        if r >= 0:
            result("k9", v, "2048^2x4", r, dt, f"{s:.15e}")
    sub_close(its)


def run_k9(v, reps):
    # harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono
    if v == "mt":
        run_k9_mt(v, reps)
        return
'''),
]


def fix(text):
    for a, b in FIX:
        text = sub(text, a, b)
    return text


EXP = [
    # K6 Q6 en colonnes
    ('''def q1_natural(c, lo, hi, acc):''', NOTE + '''sensibilité : Q6 en colonnes, boucles en C de la bibliothèque standard.
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
    m_sd = ((big(b1.translate(T_22)) & big(b0.translate(T_GE3E))) | (big(b1.translate(T_23)) & big(b0.translate(T_LTAB)))) \\
        & big(b2.translate(T_0)) & big(b3.translate(T_0))
    m = (m_sd & big(c["d"][lo:hi].tobytes().translate(T_D)) & big(c["q"][lo:hi].tobytes().translate(T_Q))).to_bytes(n, "little")
    pr, d, find = c["pr"], c["d"], m.find
    s, i = 0, find(1)
    while i >= 0:
        s += pr[lo + i] * d[lo + i]
        i = find(1, i + 1)
    return s


def q1_natural(c, lo, hi, acc):'''),
    ('''        return str(q6_tuned(c, 0, N6) if v == "tuned" else q6_natural(c, 0, N6))''',
     '''        if v == "tuned_c":
            return str(q6_columns(c, 0, N6))
        return str(q6_tuned(c, 0, N6) if v == "tuned" else q6_natural(c, 0, N6))'''),
    # K6 mt_c : Q6 en colonnes dans les sous-interpréteurs de mt (tables partagées en bytes)
    ('''    if v == "mt":
        import inspect
        part = array("q", [0] * 4)
        setup = inspect.getsource(q6_tuned) + inspect.getsource(q1_tuned) + """''',
     '''    if v in ("mt", "mt_c"):  ''' + NOTE + '''sensibilité : mt_c, Q6 en colonnes
        import inspect
        part = array("q", [0] * 4)
        setup = inspect.getsource(q6_tuned) + inspect.getsource(q1_tuned) + inspect.getsource(q6_columns) + """'''),
    ('''    else:
        part[t] = q6_tuned(c, lo, hi)
"""''', '''    else:
        part[t] = q6_columns(c, lo, hi) if cols else q6_tuned(c, lo, hi)
"""'''),
    ('''                       part=memoryview(part), N6=N6, q1=q1)''',
     '''                       part=memoryview(part), N6=N6, q1=q1, cols=v == "mt_c", T_D=T_D, T_Q=T_Q, T_0=T_0,
                       T_22=T_22, T_23=T_23, T_GE3E=T_GE3E, T_LTAB=T_LTAB)'''),
    ('''    def once():
        if v == "mt":
            for t in range(4):''', '''    def once():
        if v in ("mt", "mt_c"):
            for t in range(4):'''),
    ('''    bench("k6", v, p, reps, once)
    if v == "mt":
        sub_close(its)''', '''    bench("k6", v, p, reps, once)
    if v in ("mt", "mt_c"):
        sub_close(its)'''),
    # K8 : gc.freeze après l'arbre longue durée
    ('''    keep = t_build(20)
    lsum = t_sum(keep)
''', '''    keep = t_build(20)
    lsum = t_sum(keep)
    if v == "natural_f":  ''' + NOTE + '''sensibilité : l'arbre longue durée sort du ramasse-miettes de cycles
        import gc
        gc.freeze()
'''),
]


def exp(text):
    text = fix(text)
    for a, b in EXP:
        text = sub(text, a, b)
    return text


FTFIX = [
    ('''    def work(t):
        idx = 16 + t * stride
        if rmw:
            lk = locks[t]
            for _ in range(ITER3):
                with lk:
                    c[idx] += 1
        else:
            for _ in range(ITER3):
                c[idx] = c[idx] + 1
''', '''    def work(t):
        idx = 16 + t * stride
        m = memoryview(c)  ''' + NOTE + '''une vue propre à chaque fil sur le même tampon, sans le verrou
        # d'objet de l'array partagé (build sans GIL)
        if rmw:
            lk = locks[t]
            for _ in range(ITER3):
                with lk:
                    m[idx] += 1
        else:
            for _ in range(ITER3):
                m[idx] = m[idx] + 1
'''),
]


def ftfix(text):
    for a, b in FTFIX:
        text = sub(text, a, b)
    return text


RUN_FT = """#!/bin/sh
# Remarque sur Python (docs/PYTHON.md) : CPython 3.15.2 sans GIL (annexe python_ft), K3 corrigé
exec python3.15t "$(dirname "$0")/ms.py" "$@"
"""
BUILD_FT = """#!/bin/sh
# CPython 3.15.2 sans GIL : vérification syntaxique seulement
python3.15t -m py_compile "$(dirname "$0")/ms.py"
"""


def copy(dst, text, run=None, build=None):
    d = os.path.join(ROOT, "bench", dst)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    open(os.path.join(d, "ms.py"), "w", encoding="utf-8").write(text)
    for f, t in (("run", run), ("build.sh", build)):
        if t is None:
            shutil.copy2(os.path.join(ROOT, "bench", "python_k9h", f), os.path.join(d, f))
        else:
            open(os.path.join(d, f), "w").write(t)
            os.chmod(os.path.join(d, f), 0o755)
    print(f"{dst} écrit")


def main():
    src = open(os.path.join(ROOT, "bench", "python_k9h", "ms.py"), encoding="utf-8").read()
    copy("python_ref", src)
    copy("python_fix", fix(src))
    copy("python_exp", exp(src))
    copy("python_ftfix", ftfix(src), RUN_FT, BUILD_FT)
    open(os.path.join(ROOT, "bench", "python_exp", "extra_variants"), "w").write("k6 tuned_c q6\nk6 mt_c q6\nk8 natural_f\n")


if __name__ == "__main__":
    main()
