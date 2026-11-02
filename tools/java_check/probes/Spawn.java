public class Spawn {
    static volatile long sink;
    public static void main(String[] a) throws Exception {
        int N = 2000; double[] t = new double[N];
        for (int r = -500; r < N; r++) {
            long t0 = System.nanoTime();
            Thread[] th = new Thread[4];
            for (int k = 0; k < 4; k++) { final int kk = k; th[k] = new Thread(() -> { sink += kk; }); th[k].start(); }
            for (Thread x : th) x.join();
            long t1 = System.nanoTime();
            if (r >= 0) t[r] = (t1 - t0) * 1e-3;
        }
        java.util.Arrays.sort(t);
        System.out.printf("Java : 4 fils créés, lancés, attendus : médiane %.1f µs (p10 %.1f, p90 %.1f)%n", t[N / 2], t[N / 10], t[9 * N / 10]);
    }
}
