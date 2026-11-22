# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Mojo, par MAX 26.7.0
# (C5 : boucle parallèle ; D1 : fils en mémoire partagée ; F1 : LayoutTensor).
from std.ffi import external_call
from max.algorithm.functional import sync_parallelize
from layout import Layout, LayoutTensor, RuntimeLayout, UNKNOWN_VALUE
from std.utils.index import IndexList

def c5_d1() raises:
    var out = List[Int](length=4, fill=0)
    var tids = List[Int](length=4, fill=0)
    var p = out.unsafe_ptr()
    var q = tids.unsafe_ptr()
    def work(i: Int) raises {var p, var q}:
        var s = 0
        for k in range(i * 10000000 + 1, (i + 1) * 10000000 + 1):
            s += k
        (p + i)[] = s
        (q + i)[] = Int(external_call["gettid", Int32]())
    sync_parallelize(work, num_work_items=4)
    var total = out[0] + out[1] + out[2] + out[3]
    var distinct = 0
    for a in range(4):
        var seen = False
        for b in range(a):
            if tids[a] == tids[b]:
                seen = True
        if not seen:
            distinct += 1
    print("RESULT;C5;MAX;sync_parallelize(work, num_work_items=4) : somme =", total, "(attendu 800000020000000) ; éléments de travail exécutés sur", distinct, "fils distincts (gettid)")
    print("RESULT;D1;MAX;les quatre éléments de travail écrivent dans la même List (mémoire partagée) : out =", out[0], out[1], out[2], out[3])

def f1() raises:
    var m = 300
    var n = 500
    var storage = List[Float64](length=m * n, fill=0.0)
    comptime lay = Layout.row_major(UNKNOWN_VALUE, UNKNOWN_VALUE)
    var rt = RuntimeLayout[lay].row_major(IndexList[2](m, n))
    var t = LayoutTensor[DType.float64, lay](storage.unsafe_ptr(), rt)
    t[2, 3] = 7.0
    var idx = -1
    for i in range(m * n):
        if storage[i] == 7.0:
            idx = i
    print("RESULT;F1;MAX;LayoutTensor[float64, row_major(UNKNOWN, UNKNOWN)] sur RuntimeLayout(", m, ",", n, ") : t[2, 3] = 7 écrit à l'indice", idx, "du tampon contigu (2*", n, "+3) ; dim(0) =", t.dim(0), ", dim(1) =", t.dim(1))

def main() raises:
    c5_d1()
    f1()
