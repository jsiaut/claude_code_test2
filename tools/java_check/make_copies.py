#!/usr/bin/env python3
"""Copies de la remarque sur Java (plan : docs/JAVA.md, section 3.3), produites par remplacements de texte contrôlés
(chaque texte remplacé doit apparaître exactement une fois ; tout le reste du fichier est identique à l'octet).

* bench/java_ref : copie exacte de bench/java (même source, même compilation, même jour que les autres copies).
* bench/java_fix : correction publiée. K5 tuned et K1 soa lisent des copies hors tas alignées sur 64 octets (API FFM,
  Arena.allocate(taille, 64), FloatVector.fromMemorySegment), comme toutes les autres implémentations à SIMD explicite
  alignent leurs données ; rien d'autre ne change (K5 naturel et les autres noyaux gardent les tableaux du tas).
* bench/java_exp : sensibilités, sur la base de bench/java_k9h (harnais commun de K9) avec la correction de java_fix :
  variantes nouvelles à côté des variantes d'origine, inchangées :
  - K6 : tuned_1p et mt_1p (Q1 en une passe, accumulateurs des six groupes en variables locales), mt_pool et
    mt_pool_1p (réserve de quatre fils, Executors.newFixedThreadPool(4), créée hors chrono) ;
  - K9 : tuned_vec (Vector API, DoubleVector de 512 bits sur les tableaux du tas), mt_pool, mt_pool_vec ;
  - K7 : natural_iso et tuned_iso (le noyau dans sa propre méthode), tuned_batch (isolé, lots de 16 clés : hachages
    calculés et cases lues d'avance, puis insertion ; Java n'a pas d'instruction de préchargement) ;
  - K8 : tuned_it (arène construite et sommée itérativement, piles explicites, comme la copie c_k8it de la remarque
    sur C).
Usage : make_copies.py (puis build.sh de chaque copie)."""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))


def sub(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"texte trouvé {n} fois (1 attendu) :\n{old[:200]}")
    return text.replace(old, new)


# ------------------------------------------------------------------ correction (java_fix et java_exp)
IMPORT_OLD = "import java.lang.invoke.MethodHandles;\n"
IMPORT_NEW = "import java.lang.foreign.*;\nimport java.lang.invoke.MethodHandles;\n"

HELPER_ANCHOR = "    // ------------------------------------------------------------------ K1\n"
HELPER_NEW = """    // Remarque sur Java (docs/JAVA.md) : avec les en-têtes compacts du JDK 27, les données d'un float[] commencent à
    // 12 octets de l'objet, et chaque chargement de 64 octets chevauche deux lignes de cache. Les variantes à SIMD
    // explicite de K5 et de K1 (soa) lisent donc des copies hors tas alignées sur 64 octets, comme les autres langages.
    static final ByteOrder NO = ByteOrder.nativeOrder();
    static MemorySegment aligned(float[] src) {
        MemorySegment s = Arena.global().allocate(4L * src.length, 64);
        MemorySegment.copy(src, 0, s, ValueLayout.JAVA_FLOAT, 0, src.length);
        return s;
    }

    // ------------------------------------------------------------------ K1
"""

K1SOA_FN_ANCHOR = "    // Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)\n"
K1SOA_FN_NEW = """    static double k1SoASeg(MemorySegment vx, MemorySegment vy, MemorySegment vz, MemorySegment m) {
        DoubleVector a0 = DoubleVector.zero(DS), a1 = DoubleVector.zero(DS);
        FloatVector h = FloatVector.broadcast(FS, 0.5f);
        int n = (int) (vx.byteSize() / 4);
        for (int i = 0; i < n; i += 16) {
            long o = 4L * i;
            FloatVector x = FloatVector.fromMemorySegment(FS, vx, o, NO), y = FloatVector.fromMemorySegment(FS, vy, o, NO);
            FloatVector z = FloatVector.fromMemorySegment(FS, vz, o, NO), w = FloatVector.fromMemorySegment(FS, m, o, NO);
            FloatVector e = h.mul(w).mul(z.fma(z, y.fma(y, x.mul(x))));
            a0 = a0.add((DoubleVector) e.convertShape(VectorOperators.F2D, DS, 0));
            a1 = a1.add((DoubleVector) e.convertShape(VectorOperators.F2D, DS, 1));
        }
        return a0.add(a1).reduceLanes(VectorOperators.ADD);
    }
    // Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)
"""

K1SOA_OLD = """            float[][] c = new float[16][N1];
            for (int i = 0; i < N1; i++) for (int k = 0; k < 16; k++) c[k][i] = raw[16 * i + k];
            bench("k1", v, "energy", reps, () -> String.format("%.6f", k1SoA(c[3], c[4], c[5], c[9])));
"""
K1SOA_NEW = """            // colonnes hors tas alignées sur 64 octets (remarque sur Java, docs/JAVA.md)
            MemorySegment[] c = new MemorySegment[16];
            for (int k = 0; k < 16; k++) c[k] = Arena.global().allocate(4L * N1, 64);
            for (int i = 0; i < N1; i++) for (int k = 0; k < 16; k++) c[k].setAtIndex(ValueLayout.JAVA_FLOAT, i, raw[16 * i + k]);
            bench("k1", v, "energy", reps, () -> String.format("%.6f", k1SoASeg(c[3], c[4], c[5], c[9])));
"""

K5_OLD = """    static volatile float[] sinkA; // barrière d'optimisation : relu à chaque itération
    static void runK5(String v, int reps) {
        float[] a = loadF32("k5_a.f32"), b = loadF32("k5_b.f32");
        sinkA = a;
        boolean tuned = v.equals("tuned");
        bench("k5", v, "2048x65536", reps, () -> {
            float d = 0;
            for (int it = 0; it < INNER5; it++) d = tuned ? k5Tuned(sinkA, b) : k5Natural(sinkA, b);
            return String.format("%.4f", d);
        });
    }
"""
K5_NEW = """    static float k5TunedSeg(MemorySegment a, MemorySegment b, int n) {
        FloatVector s0 = FloatVector.zero(FS), s1 = s0, s2 = s0, s3 = s0;
        for (int i = 0; i < n; i += 64) {
            long o = 4L * i;
            s0 = FloatVector.fromMemorySegment(FS, a, o, NO).fma(FloatVector.fromMemorySegment(FS, b, o, NO), s0);
            s1 = FloatVector.fromMemorySegment(FS, a, o + 64, NO).fma(FloatVector.fromMemorySegment(FS, b, o + 64, NO), s1);
            s2 = FloatVector.fromMemorySegment(FS, a, o + 128, NO).fma(FloatVector.fromMemorySegment(FS, b, o + 128, NO), s2);
            s3 = FloatVector.fromMemorySegment(FS, a, o + 192, NO).fma(FloatVector.fromMemorySegment(FS, b, o + 192, NO), s3);
        }
        return s0.add(s1).add(s2.add(s3)).reduceLanes(VectorOperators.ADD);
    }
    static volatile float[] sinkA; // barrière d'optimisation : relu à chaque itération
    static volatile MemorySegment sinkSA; // idem pour la copie alignée
    static void runK5(String v, int reps) {
        float[] a = loadF32("k5_a.f32"), b = loadF32("k5_b.f32");
        sinkA = a;
        boolean tuned = v.equals("tuned");
        // tuned : copies hors tas alignées sur 64 octets (remarque sur Java, docs/JAVA.md)
        MemorySegment sa = aligned(a), sb = aligned(b);
        sinkSA = sa;
        int n = a.length;
        bench("k5", v, "2048x65536", reps, () -> {
            float d = 0;
            for (int it = 0; it < INNER5; it++) d = tuned ? k5TunedSeg(sinkSA, sb, n) : k5Natural(sinkA, b);
            return String.format("%.4f", d);
        });
    }
"""


def fix(text):
    text = sub(text, IMPORT_OLD, IMPORT_NEW)
    text = sub(text, HELPER_ANCHOR, HELPER_NEW)
    text = sub(text, K1SOA_FN_ANCHOR, K1SOA_FN_NEW)
    text = sub(text, K1SOA_OLD, K1SOA_NEW)
    text = sub(text, K5_OLD, K5_NEW)
    return text


# ------------------------------------------------------------------ sensibilités (java_exp)
EXP_IMPORT_OLD = "import java.util.concurrent.ArrayBlockingQueue;\n"
EXP_IMPORT_NEW = ("import java.util.concurrent.ArrayBlockingQueue;\nimport java.util.concurrent.ExecutorService;\n"
                  "import java.util.concurrent.Executors;\nimport java.util.concurrent.Future;\n")

Q1_ANCHOR = "    static void runK6(String v, int reps, String p) {\n"

K6_OLD = """            } else if (q1) {
                long[] a = new long[30];
                if (v.equals("tuned")) q1Tuned(0, N6, a); else q1Natural(0, N6, a);
                for (long x : a) s += x;
            } else s = v.equals("tuned") ? q6Tuned(0, N6) : q6Natural(0, N6);
            return Long.toString(s);
        });
    }
"""
K6_NEW = """            } else if (v.equals("mt_1p") || v.equals("mt_pool") || v.equals("mt_pool_1p")) {
                // sensibilités : Q1 en une passe (_1p), réserve de quatre fils créée hors chrono (mt_pool)
                boolean one = v.endsWith("_1p");
                long[] part = new long[4];
                Runnable[] work = new Runnable[4];
                for (int k = 0; k < 4; k++) {
                    final int kk = k, lo = N6 / 4 * k, hi = N6 / 4 * (k + 1);
                    work[k] = () -> {
                        if (q1) { long[] a = new long[30]; if (one) q1OnePass(lo, hi, a); else q1Tuned(lo, hi, a); part[kk] = Arrays.stream(a).sum(); }
                        else part[kk] = q6Tuned(lo, hi);
                    };
                }
                if (pool6 == null) {
                    Thread[] th = new Thread[4];
                    for (int k = 0; k < 4; k++) { th[k] = new Thread(work[k]); th[k].start(); }
                    try { for (Thread x : th) x.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
                } else {
                    Future<?>[] f = new Future<?>[4];
                    for (int k = 0; k < 4; k++) f[k] = pool6.submit(work[k]);
                    try { for (Future<?> x : f) x.get(); } catch (Exception e) { throw new RuntimeException(e); }
                }
                for (long x : part) s += x;
            } else if (q1) {
                long[] a = new long[30];
                if (v.equals("tuned")) q1Tuned(0, N6, a); else if (v.equals("tuned_1p")) q1OnePass(0, N6, a); else q1Natural(0, N6, a);
                for (long x : a) s += x;
            } else s = v.equals("tuned") ? q6Tuned(0, N6) : q6Natural(0, N6);
            return Long.toString(s);
        });
        if (pool6 != null) pool6.shutdown();
    }
"""
K6_POOL_OLD = """        boolean q1 = p.equals("q1");
        bench("k6", v, p, reps, () -> {
"""
K6_POOL_NEW = """        boolean q1 = p.equals("q1");
        ExecutorService pool6 = v.startsWith("mt_pool") ? Executors.newFixedThreadPool(4) : null;
        bench("k6", v, p, reps, () -> {
"""

K7_OLD = """            } else {
                final int LOG = 21, CAP = 1 << LOG;
                long t0 = System.nanoTime();
"""
K7_NEW = """            } else if (!v.equals("tuned")) {
                // sensibilités : noyau isolé dans sa propre méthode (natural_iso, tuned_iso), lots de 16 (tuned_batch)
                long t0 = System.nanoTime();
                HashMap<Integer, Agg> m = null;
                long[] tab = null;
                if (v.equals("natural_iso")) m = k7NaturalIso(keys, vals);
                else if (v.equals("tuned_iso")) tab = k7TunedIso(keys, vals);
                else tab = k7TunedBatch(keys, vals);
                dt = (System.nanoTime() - t0) * 1e-9;
                if (m != null) {
                    nk = m.size();
                    for (var e : m.entrySet()) ws += e.getValue().sum * ((e.getKey() & 1023) + 1);
                } else {
                    for (int s = 0; s < (1 << 21); s++) {
                        long w = tab[2 * s];
                        if ((w & 0xFFFFFFFFL) != 0) { nk++; ws += tab[2 * s + 1] * (((int) (w >>> 32) & 1023) + 1); }
                    }
                }
            } else {
                final int LOG = 21, CAP = 1 << LOG;
                long t0 = System.nanoTime();
"""
K7_FN_ANCHOR = "    static void runK7(String v, int reps) {\n"
K7_FN_NEW = """    static HashMap<Integer, Agg> k7NaturalIso(int[] keys, int[] vals) {
        HashMap<Integer, Agg> m = new HashMap<>();
        for (int i = 0; i < keys.length; i++) {
            Agg a = m.computeIfAbsent(keys[i], k -> new Agg());
            a.count++; a.sum += vals[i];
        }
        return m;
    }
    static long[] k7TunedIso(int[] keys, int[] vals) {
        final int LOG = 21, CAP = 1 << LOG;
        long[] tab = new long[2 * CAP];
        for (int i = 0; i < keys.length; i++) {
            int k = keys[i];
            int s = (k * 0x9E3779B1) >>> (32 - LOG);
            long w;
            while ((w = tab[2 * s]) != 0 && (int) (w >>> 32) != k) s = (s + 1) & (CAP - 1);
            tab[2 * s] = ((long) k << 32) | ((w & 0xFFFFFFFFL) + 1);
            tab[2 * s + 1] += vals[i];
        }
        return tab;
    }
    static long touch7;
    static long[] k7TunedBatch(int[] keys, int[] vals) {
        final int LOG = 21, CAP = 1 << LOG, B = 16;
        long[] tab = new long[2 * CAP];
        int[] h = new int[B];
        long touch = 0;
        for (int i0 = 0; i0 + B <= keys.length; i0 += B) {
            // lecture anticipée : les 16 cases visées sont lues d'abord (accès indépendants, défauts de cache recouverts)
            for (int b = 0; b < B; b++) { int s = (keys[i0 + b] * 0x9E3779B1) >>> (32 - LOG); h[b] = s; touch += tab[2 * s]; }
            for (int b = 0; b < B; b++) {
                int k = keys[i0 + b], s = h[b];
                long w;
                while ((w = tab[2 * s]) != 0 && (int) (w >>> 32) != k) s = (s + 1) & (CAP - 1);
                tab[2 * s] = ((long) k << 32) | ((w & 0xFFFFFFFFL) + 1);
                tab[2 * s + 1] += vals[i0 + b];
            }
        }
        touch7 = touch;
        return tab;
    }
    static void runK7(String v, int reps) {
"""

K8_FN_ANCHOR = "    static Node keep;\n"
K8_FN_NEW = """    // sensibilité tuned_it : construction et somme itératives, piles explicites ; même ordre préfixe, même arène et mêmes
    // valeurs que aBuild et aSum (comme la copie c_k8it de la remarque sur C)
    static final int[] stP = new int[64], stD = new int[64], stS = new int[64];
    static int aBuildIt(int depth, long base) {
        int sp = 0, nxt = 0, parent = -1, dd = depth;
        boolean right = false;
        for (;;) {
            int i = nxt++;
            av[i] = base + i;
            if (parent >= 0) { if (right) ar[parent] = i; else al[parent] = i; }
            if (dd > 0) { stP[sp] = i; stD[sp] = dd - 1; sp++; parent = i; right = false; dd = dd - 1; }
            else {
                al[i] = ar[i] = -1;
                if (sp == 0) break;
                sp--; parent = stP[sp]; dd = stD[sp]; right = true;
            }
        }
        return 0;
    }
    static long aSumIt(int root) {
        int sp = 0;
        long s = 0;
        stS[sp++] = root;
        while (sp > 0) {
            int i = stS[--sp];
            s += av[i];
            if (al[i] >= 0) { stS[sp++] = ar[i]; stS[sp++] = al[i]; }
        }
        return s;
    }
    static Node keep;
"""
K8_OLD = "                if (tuned) { top = 0; s = aSum(aBuild(10)); } else s = tSum(tBuild(10));\n"
K8_NEW = ("                if (tuned) { top = 0; s = aSum(aBuild(10)); } else if (tunedIt) s = aSumIt(aBuildIt(10, qq)); "
          "else s = tSum(tBuild(10));\n")
K8_FLAG_OLD = "        boolean tuned = v.equals(\"tuned\");\n        for (int r = -warmup(); r < reps; r++) {\n            long total = 0;\n"
K8_FLAG_NEW = ("        boolean tuned = v.equals(\"tuned\"), tunedIt = v.equals(\"tuned_it\");\n"
               "        for (int r = -warmup(); r < reps; r++) {\n            long total = 0;\n")

K9_FN_ANCHOR = "    static void runK9(String v, int reps) {\n"
K9_FN_NEW = """    // sensibilité tuned_vec : la même boucle en Vector API (8 double par vecteur), même ordre des additions
    static final DoubleVector Q9 = DoubleVector.broadcast(DS, 0.25);
    static void k9RowsVec(double[] in, double[] out, int r0, int r1) {
        for (int i = r0; i < r1; i++) {
            int up = (i - 1) * M9, mid = i * M9, dn = (i + 1) * M9;
            int j = 1;
            for (; j + 8 <= M9 - 1; j += 8) {
                DoubleVector s = DoubleVector.fromArray(DS, in, up + j).add(DoubleVector.fromArray(DS, in, dn + j))
                        .add(DoubleVector.fromArray(DS, in, mid + j - 1)).add(DoubleVector.fromArray(DS, in, mid + j + 1));
                Q9.mul(s).intoArray(out, mid + j);
            }
            for (; j < M9 - 1; j++) out[mid + j] = 0.25 * (((in[up + j] + in[dn + j]) + in[mid + j - 1]) + in[mid + j + 1]);
        }
    }
    static void runK9(String v, int reps) {
"""
K9_POOL_OLD = """        if (v.equals("natural")) { na = new double[M9][M9]; nb = new double[M9][M9]; }
        else { ga = new double[M9 * M9]; gb = new double[M9 * M9]; }
"""
K9_POOL_NEW = """        if (v.equals("natural")) { na = new double[M9][M9]; nb = new double[M9][M9]; }
        else { ga = new double[M9 * M9]; gb = new double[M9 * M9]; }
        // sensibilités : réserve de quatre fils créée hors chrono (mt_pool, mt_pool_vec)
        ExecutorService pool9 = v.startsWith("mt_pool") ? Executors.newFixedThreadPool(4) : null;
        boolean vec9 = v.endsWith("_vec");
"""
K9_OLD = """                    if (v.equals("tuned")) k9Rows(a, b, 1, M9 - 1);
                    else {
"""
K9_NEW = """                    if (v.equals("tuned")) k9Rows(a, b, 1, M9 - 1);
                    else if (v.equals("tuned_vec")) k9RowsVec(a, b, 1, M9 - 1);
                    else if (pool9 != null) {
                        Future<?>[] f = new Future<?>[4];
                        final double[] fa = a, fb = b;
                        for (int k = 0; k < 4; k++) {
                            final int r0 = 1 + (M9 - 2) * k / 4, r1 = 1 + (M9 - 2) * (k + 1) / 4;
                            f[k] = pool9.submit(() -> { if (vec9) k9RowsVec(fa, fb, r0, r1); else k9Rows(fa, fb, r0, r1); });
                        }
                        try { for (Future<?> x : f) x.get(); } catch (Exception e) { throw new RuntimeException(e); }
                    }
                    else {
"""
K9_END_OLD = """            if (r >= 0) result("k9", v, "2048^2x4", r, (t1 - t0) * 1e-9, String.format("%.15e", s));
        }
    }
"""
K9_END_NEW = """            if (r >= 0) result("k9", v, "2048^2x4", r, (t1 - t0) * 1e-9, String.format("%.15e", s));
        }
        if (pool9 != null) pool9.shutdown();
    }
"""


def exp(text):
    text = fix(text)
    text = sub(text, EXP_IMPORT_OLD, EXP_IMPORT_NEW)
    q1 = open(os.path.join(HERE, "q1_onepass.java.txt")).read()
    text = sub(text, Q1_ANCHOR, q1 + Q1_ANCHOR)
    text = sub(text, K6_POOL_OLD, K6_POOL_NEW)
    text = sub(text, K6_OLD, K6_NEW)
    text = sub(text, K7_FN_ANCHOR, K7_FN_NEW)
    text = sub(text, K7_OLD, K7_NEW)
    text = sub(text, K8_FN_ANCHOR, K8_FN_NEW)
    text = sub(text, K8_FLAG_OLD, K8_FLAG_NEW)
    text = sub(text, K8_OLD, K8_NEW)
    text = sub(text, K9_FN_ANCHOR, K9_FN_NEW)
    text = sub(text, K9_POOL_OLD, K9_POOL_NEW)
    text = sub(text, K9_OLD, K9_NEW)
    text = sub(text, K9_END_OLD, K9_END_NEW)
    return text


def copy(src, dst, transform):
    d = os.path.join(ROOT, "bench", dst)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "classes"))
    s = os.path.join(ROOT, "bench", src)
    for f in ("build.sh", "run"):
        shutil.copy2(os.path.join(s, f), os.path.join(d, f))
    text = open(os.path.join(s, "Ms.java"), encoding="utf-8").read()
    open(os.path.join(d, "Ms.java"), "w", encoding="utf-8").write(transform(text))
    print(dst, "écrit")


EXTRA = """k6 tuned_1p q1
k6 mt_1p q1
k6 mt_pool q1
k6 mt_pool_1p q1
k6 mt_pool q6
k9 tuned_vec
k9 mt_pool
k9 mt_pool_vec
k7 natural_iso
k7 tuned_iso
k7 tuned_batch
k8 tuned_it
"""


def main():
    copy("java", "java_ref", lambda t: t)
    copy("java", "java_fix", fix)
    copy("java_k9h", "java_exp", exp)
    # variantes nouvelles, déclarées au pilote (tools/driver.py)
    open(os.path.join(ROOT, "bench", "java_exp", "extra_variants"), "w").write(EXTRA)


if __name__ == "__main__":
    main()
