// Annexe (hors classement) : K1 avec les classes valeur de Valhalla (JEP 401, build EA du JDK 27,
// --enable-preview). Question : un tableau d'objets valeur de 64 octets est-il aplati en mémoire ?
// Usage : java --enable-preview K1V <list|array> <reps> [shuffled|footprint]
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class K1V {
    value record Particle(float x, float y, float z, float vx, float vy, float vz, float ax, float ay, float az,
                          float mass, float charge, float radius, float temp, float pressure, float energy, float density) {}
    static final int N1 = 4194304;

    static double sumList(List<Particle> ps) {
        double e = 0;
        for (Particle p : ps) e += 0.5 * p.mass() * (p.vx() * p.vx() + p.vy() * p.vy() + p.vz() * p.vz());
        return e;
    }
    static double sumArray(Particle[] ps) {
        double e = 0;
        for (Particle p : ps) e += 0.5 * p.mass() * (p.vx() * p.vx() + p.vy() * p.vy() + p.vz() * p.vz());
        return e;
    }
    public static void main(String[] a) throws Exception {
        String d = System.getenv().getOrDefault("MS_DATA", "/opt/msdata");
        ByteBuffer bb = ByteBuffer.wrap(Files.readAllBytes(Path.of(d, "k1_particles.f32"))).order(ByteOrder.LITTLE_ENDIAN);
        float[] raw = new float[N1 * 16];
        bb.asFloatBuffer().get(raw);
        int[] perm = null;
        String mode = a.length > 2 ? a[2] : "";
        if (mode.equals("shuffled")) {
            ByteBuffer pb = ByteBuffer.wrap(Files.readAllBytes(Path.of(d, "k1_perm.u32"))).order(ByteOrder.LITTLE_ENDIAN);
            perm = new int[N1];
            pb.asIntBuffer().get(perm);
        }
        boolean useArray = a[0].equals("array");
        Particle[] arr = useArray ? new Particle[N1] : null;
        List<Particle> lst = useArray ? null : new ArrayList<>();
        for (int i = 0; i < N1; i++) {
            int o = 16 * (perm != null ? perm[i] : i);
            Particle p = new Particle(raw[o], raw[o + 1], raw[o + 2], raw[o + 3], raw[o + 4], raw[o + 5], raw[o + 6], raw[o + 7],
                    raw[o + 8], raw[o + 9], raw[o + 10], raw[o + 11], raw[o + 12], raw[o + 13], raw[o + 14], raw[o + 15]);
            if (useArray) arr[i] = p; else lst.add(p);
        }
        raw = null;
        System.gc();
        Runtime rt = Runtime.getRuntime();
        System.out.println("META;live_bytes_after_gc;" + (rt.totalMemory() - rt.freeMemory()) + ";octets_par_particule;"
                + (rt.totalMemory() - rt.freeMemory()) / (double) N1);
        if (mode.equals("footprint")) return;
        int reps = Integer.parseInt(a[1]);
        for (int r = -3; r < reps; r++) {
            long t0 = System.nanoTime();
            double e = useArray ? sumArray(arr) : sumList(lst);
            long t1 = System.nanoTime();
            if (r >= 0) System.out.printf("RESULT;k1;valhalla_%s%s;energy;%d;%.9f;%.6f%n", a[0], perm != null ? "_shuffled" : "", r, (t1 - t0) / 1e9, e);
        }
    }
}
