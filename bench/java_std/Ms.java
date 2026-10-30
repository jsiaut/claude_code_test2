// Copie « standard » de bench/java/Ms.java pour la confrontation (docs/CONFRONTATION.md, section 4) : sans le module
// en incubation jdk.incubator.vector (changements marqués « standard : »).
// Implémentation Java 27 (JDK seul ; jdk.incubator.vector pour les variantes tuned).
import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.atomic.AtomicLongArray;
import java.util.function.Supplier;

public class Ms {
    // ------------------------------------------------------------------ harnais
    static String dataDir() { String d = System.getenv("MS_DATA"); return d != null ? d : "/opt/msdata"; }
    static byte[] loadBytes(String n) {
        try { return Files.readAllBytes(Path.of(dataDir(), n)); } catch (Exception e) { throw new RuntimeException(e); }
    }
    static ByteBuffer bb(String n) { return ByteBuffer.wrap(loadBytes(n)).order(ByteOrder.LITTLE_ENDIAN); }
    static float[] loadF32(String n) { var b = bb(n).asFloatBuffer(); float[] a = new float[b.remaining()]; b.get(a); return a; }
    static int[] loadI32(String n) { var b = bb(n).asIntBuffer(); int[] a = new int[b.remaining()]; b.get(a); return a; }
    static int warmup() { String w = System.getenv("WARMUP"); return w != null ? Integer.parseInt(w) : 1; }
    static void result(String k, String v, String p, int rep, double sec, String chk) {
        System.out.printf("RESULT;%s;%s;%s;%d;%.9f;%s%n", k, v, p, rep, sec, chk);
    }
    static void bench(String k, String v, String p, int reps, Supplier<String> f) {
        for (int r = -warmup(); r < reps; r++) {
            long t0 = System.nanoTime();
            String chk = f.get();
            long t1 = System.nanoTime();
            if (r >= 0) result(k, v, p, r, (t1 - t0) * 1e-9, chk);
        }
    }


    // ------------------------------------------------------------------ K1
    static final int N1 = 1 << 22;
    // type enregistrement par défaut de Java moderne : record (objet sur le tas)
    record Particle(float x, float y, float z, float vx, float vy, float vz, float ax, float ay, float az,
                    float mass, float charge, float radius, float temp, float pressure, float energy, float density) {}

    static double k1Natural(List<Particle> ps) {
        double e = 0;
        for (Particle p : ps) e += 0.5 * p.mass() * (p.vx() * p.vx() + p.vy() * p.vy() + p.vz() * p.vz());
        return e;
    }
    // AoS « valeur » impossible sans Valhalla : la représentation la plus proche est un float[]
    // entrelacé (pas de 16), c.-à-d. une disposition AoS gérée à la main.
    static double k1AoS(float[] f) {
        double a0 = 0, a1 = 0, a2 = 0, a3 = 0;
        for (int i = 0; i < f.length; i += 64) {
            a0 += 0.5f * f[i + 9] * (f[i + 3] * f[i + 3] + f[i + 4] * f[i + 4] + f[i + 5] * f[i + 5]);
            a1 += 0.5f * f[i + 25] * (f[i + 19] * f[i + 19] + f[i + 20] * f[i + 20] + f[i + 21] * f[i + 21]);
            a2 += 0.5f * f[i + 41] * (f[i + 35] * f[i + 35] + f[i + 36] * f[i + 36] + f[i + 37] * f[i + 37]);
            a3 += 0.5f * f[i + 57] * (f[i + 51] * f[i + 51] + f[i + 52] * f[i + 52] + f[i + 53] * f[i + 53]);
        }
        return a0 + a1 + a2 + a3;
    }
    // standard : sans jdk.incubator.vector ; 8 accumulateurs scalaires indépendants (C2 ne vectorise pas une réduction
    // flottante, dont l'ordre est fixé par le langage), FMA par Math.fma comme la version vectorielle
    static double k1SoA(float[] vx, float[] vy, float[] vz, float[] m) {
        double a0 = 0, a1 = 0, a2 = 0, a3 = 0, a4 = 0, a5 = 0, a6 = 0, a7 = 0;
        int n = vx.length & ~7;
        for (int i = 0; i < n; i += 8) {
            a0 += e1(vx, vy, vz, m, i);
            a1 += e1(vx, vy, vz, m, i + 1);
            a2 += e1(vx, vy, vz, m, i + 2);
            a3 += e1(vx, vy, vz, m, i + 3);
            a4 += e1(vx, vy, vz, m, i + 4);
            a5 += e1(vx, vy, vz, m, i + 5);
            a6 += e1(vx, vy, vz, m, i + 6);
            a7 += e1(vx, vy, vz, m, i + 7);
        }
        return ((a0 + a1) + (a2 + a3)) + ((a4 + a5) + (a6 + a7));
    }
    static double e1(float[] vx, float[] vy, float[] vz, float[] m, int i) {
        return (double) (0.5f * m[i] * Math.fma(vz[i], vz[i], Math.fma(vy[i], vy[i], vx[i] * vx[i])));
    }
    // Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)
    static long liveNow() {
        Runtime rt = Runtime.getRuntime();
        System.gc();
        System.gc();
        return rt.totalMemory() - rt.freeMemory();
    }
    static long rssNow() {
        try {
            return Long.parseLong(java.nio.file.Files.readString(java.nio.file.Path.of("/proc/self/statm")).trim().split("\\s+")[1]) * 4096;
        } catch (Exception e) {
            return 0;
        }
    }
    static void runK1(String v, int reps) {
        if (v.equals("footprint0")) { result("k1", v, "energy", 0, 0, "0"); return; }
        float[] raw = loadF32("k1_particles.f32");
        if (v.equals("footprint_raw")) { result("k1", v, "energy", 0, 0, "0"); return; }
        if (v.equals("aos")) { bench("k1", v, "energy", reps, () -> String.format("%.6f", k1AoS(raw))); return; }
        if (v.equals("soa")) {
            float[][] c = new float[16][N1];
            for (int i = 0; i < N1; i++) for (int k = 0; k < 16; k++) c[k][i] = raw[16 * i + k];
            bench("k1", v, "energy", reps, () -> String.format("%.6f", k1SoA(c[3], c[4], c[5], c[9])));
            return;
        }
        long m1 = 0, r1 = 0;
        if (v.equals("footprint")) { m1 = liveNow(); r1 = rssNow(); } // P1 : tampon brut chargé
        List<Particle> ps = new ArrayList<>();
        for (int i = 0; i < N1; i++) {
            int o = 16 * i;
            ps.add(new Particle(raw[o], raw[o + 1], raw[o + 2], raw[o + 3], raw[o + 4], raw[o + 5], raw[o + 6], raw[o + 7],
                    raw[o + 8], raw[o + 9], raw[o + 10], raw[o + 11], raw[o + 12], raw[o + 13], raw[o + 14], raw[o + 15]));
        }
        if (v.equals("footprint")) {
            long m2 = liveNow(), r2 = rssNow(); // P2 : collection construite, tampon brut encore vivant
            System.out.println("META;mem;live;" + m1 + ";" + m2);
            System.out.println("META;rss;" + r1 + ";" + r2);
            System.out.println("META;raw0;" + raw[0]);
            result("k1", v, "energy", 0, 0, String.format("%.6f", k1Natural(ps)));
            return;
        }
        if (v.equals("natural_shuffled")) {
            int[] perm = loadI32("k1_perm.u32");
            List<Particle> s = new ArrayList<>(N1);
            for (int j = 0; j < N1; j++) s.add(ps.get(perm[j]));
            ps = s;
            System.gc(); // laisse au GC la possibilité de recompacter
        }
        final List<Particle> fp = ps;
        bench("k1", v, "energy", reps, () -> String.format("%.6f", k1Natural(fp)));
    }

    // ------------------------------------------------------------------ K2
    static int k2Chase(int[] a, int h) { int i = 0; for (int k = 0; k < h; k++) i = a[i]; return i; }
    static void runK2(String v, int reps, String p) {
        int[] a = loadI32("k2_chase_" + p + ".u32");
        bench("k2", v, p, reps, () -> Integer.toString(k2Chase(a, 4200000)));
    }

    // ------------------------------------------------------------------ K3
    static final int ITER3 = 1 << 25;
    static final VarHandle LA = MethodHandles.arrayElementVarHandle(long[].class);
    static void runK3(String v, int reps) {
        boolean rmw = v.startsWith("rmw");
        int stride = v.endsWith("padded") ? 16 : 1; // 128 o ou 8 o
        System.out.println("META;k3_mechanism;" + (rmw ? "VarHandle.getAndAdd (lock xadd)" : "VarHandle getOpaque/setOpaque (mov)"));
        long[] c = new long[4 * 16 + 32];
        int base = 16; // évite le partage avec l'en-tête du tableau
        bench("k3", v, "4x2^25", reps, () -> {
            Thread[] th = new Thread[4];
            for (int t = 0; t < 4; t++) {
                final int idx = base + t * stride;
                LA.setOpaque(c, idx, 0L);
                th[t] = new Thread(() -> {
                    if (rmw) for (int i = 0; i < ITER3; i++) LA.getAndAdd(c, idx, 1L);
                    else for (int i = 0; i < ITER3; i++) LA.setOpaque(c, idx, (long) LA.getOpaque(c, idx) + 1);
                });
                th[t].start();
            }
            long s = 0;
            try { for (int t = 0; t < 4; t++) { th[t].join(); } } catch (InterruptedException e) { throw new RuntimeException(e); }
            for (int t = 0; t < 4; t++) s += (long) LA.getVolatile(c, base + t * stride);
            return Long.toString(s);
        });
    }

    // ------------------------------------------------------------------ K4
    static long k4Natural(byte[] v) { long s = 0; for (byte b : v) { int x = b & 0xFF; if (x >= 128) s += x; } return s; }
    static long k4Branchless(byte[] v) { long s = 0; for (byte b : v) { int x = b & 0xFF; s += x * (x >> 7); } return s; }
    static void runK4(String v, int reps) {
        byte[] d = loadBytes("k4_bytes.u8");
        if (v.equals("natural_sorted")) { // tri par comptage (octets non signés), hors chrono
            int[] cnt = new int[256];
            for (byte b : d) cnt[b & 0xFF]++;
            int k = 0;
            for (int b = 0; b < 256; b++) for (int c = 0; c < cnt[b]; c++) d[k++] = (byte) b;
        }
        boolean bl = v.equals("branchless_unsorted");
        bench("k4", v, "16M", reps, () -> Long.toString(bl ? k4Branchless(d) : k4Natural(d)));
    }

    // ------------------------------------------------------------------ K5
    static final int INNER5 = 1 << 16;
    static float k5Natural(float[] a, float[] b) { float s = 0; for (int i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }
    // standard : sans jdk.incubator.vector ; 64 sommes partielles explicites (les 4 accumulateurs de 16 voies), Math.fma
    static float k5Tuned(float[] a, float[] b) {
        float[] s = new float[64];
        for (int i = 0; i + 64 <= a.length; i += 64)
            for (int k = 0; k < 64; k++) s[k] = Math.fma(a[i + k], b[i + k], s[k]);
        float r = 0;
        for (int k = 0; k < 16; k++) r += (s[k] + s[16 + k]) + (s[32 + k] + s[48 + k]);
        return r;
    }
    static volatile float[] sinkA; // barrière d'optimisation : relu à chaque itération
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

    // ------------------------------------------------------------------ K6
    static final int N6 = 1 << 24;
    static int[] sd, pr; static byte[] q, d, t, rf, ls;
    static long q6Natural(int lo, int hi) {
        long s = 0;
        for (int i = lo; i < hi; i++)
            if (sd[i] >= 8766 && sd[i] < 9131 && d[i] >= 5 && d[i] <= 7 && q[i] < 24) s += (long) pr[i] * d[i];
        return s;
    }
    // standard : sans jdk.incubator.vector ; prédicat sans branchement (opérateurs & non court-circuités)
    static long q6Tuned(int lo, int hi) {
        long s = 0;
        for (int i = lo; i < hi; i++) {
            int x = sd[i], dd = d[i];
            boolean ok = Integer.compareUnsigned(x - 8766, 365) < 0 & Integer.compareUnsigned(dd - 5, 3) < 0 & q[i] < 24;
            s += ok ? (long) (pr[i] * dd) : 0L;
        }
        return s;
    }
    static void q1Natural(int lo, int hi, long[] acc) {
        for (int i = lo; i < hi; i++) {
            if (sd[i] <= 10471) {
                int g = rf[i] * 2 + ls[i];
                long p = pr[i], dp = p * (100 - d[i]);
                acc[g * 5] += 1; acc[g * 5 + 1] += q[i]; acc[g * 5 + 2] += p; acc[g * 5 + 3] += dp; acc[g * 5 + 4] += dp * (100 + t[i]);
            }
        }
    }
    // Q1 optimisé, standard : sans jdk.incubator.vector ; même découpage (une passe par groupe sur des blocs de 2048
    // lignes), sommes masquées sans branchement que C2 peut vectoriser
    static void q1Tuned(int lo, int hi, long[] acc) {
        for (int b0 = lo; b0 < hi; b0 += 2048) {
            int b1 = Math.min(b0 + 2048, hi);
            for (int g = 0; g < 6; g++) {
                long cnt = 0, sq = 0, sp = 0, sdp = 0, sch = 0;
                for (int i = b0; i < b1; i++) {
                    int m = (sd[i] <= 10471 & rf[i] * 2 + ls[i] == g) ? -1 : 0;
                    int dp = pr[i] * (100 - d[i]);
                    cnt -= m;
                    sq += q[i] & m;
                    sp += pr[i] & m;
                    sdp += dp & m;
                    sch += (long) (dp & m) * (100 + t[i]);
                }
                acc[g * 5] += cnt;
                acc[g * 5 + 1] += sq;
                acc[g * 5 + 2] += sp;
                acc[g * 5 + 3] += sdp;
                acc[g * 5 + 4] += sch;
            }
        }
    }
    static void runK6(String v, int reps, String p) {
        sd = loadI32("k6_shipdate.i32"); pr = loadI32("k6_extendedprice.i32"); q = loadBytes("k6_quantity.u8");
        d = loadBytes("k6_discount.u8"); t = loadBytes("k6_tax.u8"); rf = loadBytes("k6_returnflag.u8"); ls = loadBytes("k6_linestatus.u8");
        boolean q1 = p.equals("q1");
        bench("k6", v, p, reps, () -> {
            long s = 0;
            if (v.equals("mt")) {
                long[] part = new long[4];
                Thread[] th = new Thread[4];
                for (int k = 0; k < 4; k++) {
                    final int kk = k, lo = N6 / 4 * k, hi = N6 / 4 * (k + 1);
                    th[k] = new Thread(() -> {
                        if (q1) { long[] a = new long[30]; q1Tuned(lo, hi, a); part[kk] = Arrays.stream(a).sum(); }
                        else part[kk] = q6Tuned(lo, hi);
                    });
                    th[k].start();
                }
                try { for (Thread x : th) x.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
                for (long x : part) s += x;
            } else if (q1) {
                long[] a = new long[30];
                if (v.equals("tuned")) q1Tuned(0, N6, a); else q1Natural(0, N6, a);
                for (long x : a) s += x;
            } else s = v.equals("tuned") ? q6Tuned(0, N6) : q6Natural(0, N6);
            return Long.toString(s);
        });
    }

    // ------------------------------------------------------------------ K7
    static final class Agg { int count; long sum; }
    static void runK7(String v, int reps) {
        int[] keys = loadI32("k7_keys.u32"), vals = loadI32("k7_vals.u32");
        for (int r = -warmup(); r < reps; r++) {
            long nk = 0, ws = 0; double dt;
            if (v.equals("natural")) {
                long t0 = System.nanoTime();
                HashMap<Integer, Agg> m = new HashMap<>();
                for (int i = 0; i < keys.length; i++) {
                    Agg a = m.computeIfAbsent(keys[i], k -> new Agg());
                    a.count++; a.sum += vals[i];
                }
                dt = (System.nanoTime() - t0) * 1e-9;
                nk = m.size();
                for (var e : m.entrySet()) ws += e.getValue().sum * ((e.getKey() & 1023) + 1);
            } else {
                final int LOG = 21, CAP = 1 << LOG;
                long t0 = System.nanoTime();
                // AoS manuel dans un long[] : [clé<<32 | compteur, somme] = 16 o par case, comme en C
                long[] tab = new long[2 * CAP];
                for (int i = 0; i < keys.length; i++) {
                    int k = keys[i];
                    int s = (k * 0x9E3779B1) >>> (32 - LOG);
                    long w;
                    while ((w = tab[2 * s]) != 0 && (int) (w >>> 32) != k) s = (s + 1) & (CAP - 1);
                    tab[2 * s] = ((long) k << 32) | ((w & 0xFFFFFFFFL) + 1);
                    tab[2 * s + 1] += vals[i];
                }
                dt = (System.nanoTime() - t0) * 1e-9;
                for (int s = 0; s < CAP; s++) {
                    long w = tab[2 * s];
                    if ((w & 0xFFFFFFFFL) != 0) { nk++; ws += tab[2 * s + 1] * (((int) (w >>> 32) & 1023) + 1); }
                }
            }
            if (r >= 0) result("k7", v, "16M/1M", r, dt, nk + ":" + ws);
        }
    }

    // ------------------------------------------------------------------ K8
    static final class Node { long v; Node l, r; }
    static long cnt8;
    static Node tBuild(int dpt) { Node n = new Node(); n.v = cnt8++; if (dpt > 0) { n.l = tBuild(dpt - 1); n.r = tBuild(dpt - 1); } return n; }
    static long tSum(Node n) { return n == null ? 0 : n.v + tSum(n.l) + tSum(n.r); }
    // arène SoA indexée, réutilisée à chaque requête
    static final long[] av = new long[2047]; static final int[] al = new int[2047], ar = new int[2047]; static int top;
    static int aBuild(int dpt) {
        int i = top++; av[i] = cnt8++; al[i] = ar[i] = -1;
        if (dpt > 0) { al[i] = aBuild(dpt - 1); ar[i] = aBuild(dpt - 1); }
        return i;
    }
    static long aSum(int i) { return i < 0 ? 0 : av[i] + aSum(al[i]) + aSum(ar[i]); }
    static Node keep;
    static void runK8(String v, int reps) {
        final int Q = 16384;
        cnt8 = 0; keep = tBuild(20); long lsum = tSum(keep);
        long[] lat = new long[Q];
        boolean tuned = v.equals("tuned");
        for (int r = -warmup(); r < reps; r++) {
            long total = 0;
            long t0 = System.nanoTime();
            for (int qq = 0; qq < Q; qq++) {
                long a = System.nanoTime();
                cnt8 = qq;
                long s;
                if (tuned) { top = 0; s = aSum(aBuild(10)); } else s = tSum(tBuild(10));
                total += s;
                lat[qq] = System.nanoTime() - a;
            }
            long t1 = System.nanoTime();
            if (r >= 0) {
                result("k8", v, "16384x2047", r, (t1 - t0) * 1e-9, Long.toString(total + lsum));
                Arrays.sort(lat);
                System.out.printf("LAT;%s;%d;%d;%d;%d;%d%n", v, lat[Q / 2], lat[Q * 9 / 10], lat[Q * 99 / 100], lat[Q * 999 / 1000], lat[Q - 1]);
            }
        }
    }

    // ------------------------------------------------------------------ K9
    static final int M9 = 2048;
    static double k9Init(int i, int j) { return ((i * 31 + j * 17) % 1024) / 1024.0; }
    static void k9Natural(double[][] in, double[][] out) {
        for (int i = 1; i < M9 - 1; i++)
            for (int j = 1; j < M9 - 1; j++)
                out[i][j] = 0.25 * (((in[i - 1][j] + in[i + 1][j]) + in[i][j - 1]) + in[i][j + 1]);
    }
    static void k9Rows(double[] in, double[] out, int r0, int r1) {
        for (int i = r0; i < r1; i++) {
            int up = (i - 1) * M9, mid = i * M9, dn = (i + 1) * M9;
            for (int j = 1; j < M9 - 1; j++) out[mid + j] = 0.25 * (((in[up + j] + in[dn + j]) + in[mid + j - 1]) + in[mid + j + 1]);
        }
    }
    static void runK9(String v, int reps) {
        for (int r = -warmup(); r < reps; r++) {
            double s = 0; long t0, t1;
            if (v.equals("natural")) {
                double[][] a = new double[M9][M9], b = new double[M9][M9];
                for (int i = 0; i < M9; i++) for (int j = 0; j < M9; j++) a[i][j] = b[i][j] = k9Init(i, j);
                t0 = System.nanoTime();
                for (int it = 0; it < 4; it++) { k9Natural(a, b); double[][] tmp = a; a = b; b = tmp; }
                t1 = System.nanoTime();
                for (double[] row : a) for (double x : row) s += x;
            } else {
                double[] a = new double[M9 * M9], b = new double[M9 * M9];
                for (int k = 0; k < M9 * M9; k++) a[k] = b[k] = k9Init(k / M9, k % M9);
                t0 = System.nanoTime();
                for (int it = 0; it < 4; it++) {
                    if (v.equals("tuned")) k9Rows(a, b, 1, M9 - 1);
                    else {
                        Thread[] th = new Thread[4];
                        final double[] fa = a, fb = b;
                        for (int k = 0; k < 4; k++) {
                            final int r0 = 1 + (M9 - 2) * k / 4, r1 = 1 + (M9 - 2) * (k + 1) / 4;
                            th[k] = new Thread(() -> k9Rows(fa, fb, r0, r1));
                            th[k].start();
                        }
                        try { for (Thread x : th) x.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
                    }
                    double[] tmp = a; a = b; b = tmp;
                }
                t1 = System.nanoTime();
                for (double x : a) s += x;
            }
            if (r >= 0) result("k9", v, "2048^2x4", r, (t1 - t0) * 1e-9, String.format("%.15e", s));
        }
    }

    // ------------------------------------------------------------------ K10
    static final int M10 = 1 << 22, CAP10 = 1 << 14;
    // indices séparés par du bourrage (128 o) dans un long[] ; ordres acquire/release via VarHandle
    static void runK10(String v, int reps) {
        bench("k10", v, "2^22", reps, () -> {
            long[] sum = new long[1];
            Thread prod, cons;
            if (v.equals("natural")) {
                ArrayBlockingQueue<Long> qq = new ArrayBlockingQueue<>(CAP10);
                prod = new Thread(() -> { try { for (long x = 1; x <= M10; x++) qq.put(x); } catch (InterruptedException e) { throw new RuntimeException(e); } });
                cons = new Thread(() -> { long s = 0; try { for (int k = 0; k < M10; k++) s += qq.take(); } catch (InterruptedException e) { throw new RuntimeException(e); } sum[0] = s; });
            } else {
                long[] idx = new long[64]; // write @16, read @48
                long[] buf = new long[CAP10];
                prod = new Thread(() -> {
                    long w = 0, rc = 0;
                    for (long x = 1; x <= M10; x++) {
                        while (w - rc == CAP10) { rc = (long) LA.getAcquire(idx, 48); if (w - rc == CAP10) Thread.onSpinWait(); }
                        buf[(int) (w & (CAP10 - 1))] = x;
                        LA.setRelease(idx, 16, ++w);
                    }
                });
                cons = new Thread(() -> {
                    long rd = 0, wc = 0, s = 0;
                    for (int k = 0; k < M10; k++) {
                        while (rd == wc) { wc = (long) LA.getAcquire(idx, 16); if (rd == wc) Thread.onSpinWait(); }
                        s += buf[(int) (rd & (CAP10 - 1))];
                        LA.setRelease(idx, 48, ++rd);
                    }
                    sum[0] = s;
                });
            }
            cons.start(); prod.start();
            try { prod.join(); cons.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
            return Long.toString(sum[0]);
        });
    }

    public static void main(String[] a) {
        String k = a[0], v = a[1], p = a.length > 3 ? a[3] : "";
        int reps = Integer.parseInt(a[2]);
        switch (k) {
            case "k1" -> runK1(v, reps);
            case "k2" -> runK2(v, reps, p);
            case "k3" -> runK3(v, reps);
            case "k4" -> runK4(v, reps);
            case "k5" -> runK5(v, reps);
            case "k6" -> runK6(v, reps, p);
            case "k7" -> runK7(v, reps);
            case "k8" -> runK8(v, reps);
            case "k9" -> runK9(v, reps);
            case "k10" -> runK10(v, reps);
            default -> throw new IllegalArgumentException(k);
        }
    }
}
