import java.lang.foreign.*;
import java.nio.ByteOrder;
import java.nio.file.*;
import jdk.incubator.vector.*;
public class K5Probe {
    static final VectorSpecies<Float> FS = FloatVector.SPECIES_512;
    static final ByteOrder LE = ByteOrder.LITTLE_ENDIAN;
    static float heap(float[] a, float[] b) {
        FloatVector s0 = FloatVector.zero(FS), s1 = s0, s2 = s0, s3 = s0;
        for (int i = 0; i < a.length; i += 64) {
            s0 = FloatVector.fromArray(FS, a, i).fma(FloatVector.fromArray(FS, b, i), s0);
            s1 = FloatVector.fromArray(FS, a, i + 16).fma(FloatVector.fromArray(FS, b, i + 16), s1);
            s2 = FloatVector.fromArray(FS, a, i + 32).fma(FloatVector.fromArray(FS, b, i + 32), s2);
            s3 = FloatVector.fromArray(FS, a, i + 48).fma(FloatVector.fromArray(FS, b, i + 48), s3);
        }
        return s0.add(s1).add(s2.add(s3)).reduceLanes(VectorOperators.ADD);
    }
    static float seg(MemorySegment a, MemorySegment b, int n) {
        FloatVector s0 = FloatVector.zero(FS), s1 = s0, s2 = s0, s3 = s0;
        for (int i = 0; i < n; i += 64) {
            long o = 4L * i;
            s0 = FloatVector.fromMemorySegment(FS, a, o, LE).fma(FloatVector.fromMemorySegment(FS, b, o, LE), s0);
            s1 = FloatVector.fromMemorySegment(FS, a, o + 64, LE).fma(FloatVector.fromMemorySegment(FS, b, o + 64, LE), s1);
            s2 = FloatVector.fromMemorySegment(FS, a, o + 128, LE).fma(FloatVector.fromMemorySegment(FS, b, o + 128, LE), s2);
            s3 = FloatVector.fromMemorySegment(FS, a, o + 192, LE).fma(FloatVector.fromMemorySegment(FS, b, o + 192, LE), s3);
        }
        return s0.add(s1).add(s2.add(s3)).reduceLanes(VectorOperators.ADD);
    }
    static volatile float[] sinkA; static volatile MemorySegment sinkS;
    public static void main(String[] args) throws Exception {
        String mode = args[0];
        var bb = java.nio.ByteBuffer.wrap(Files.readAllBytes(Path.of("/opt/msdata/k5_a.f32"))).order(LE).asFloatBuffer();
        float[] a = new float[bb.remaining()]; bb.get(a);
        bb = java.nio.ByteBuffer.wrap(Files.readAllBytes(Path.of("/opt/msdata/k5_b.f32"))).order(LE).asFloatBuffer();
        float[] b = new float[bb.remaining()]; bb.get(b);
        int n = a.length;
        long off = mode.equals("seg12") ? 12 : 0;
        MemorySegment sa = Arena.global().allocate(4L * n + 64, 64).asSlice(off, 4L * n);
        MemorySegment sb = Arena.global().allocate(4L * n + 64, 64).asSlice(off, 4L * n);
        MemorySegment.copy(a, 0, sa, ValueLayout.JAVA_FLOAT_UNALIGNED, 0, n);
        MemorySegment.copy(b, 0, sb, ValueLayout.JAVA_FLOAT_UNALIGNED, 0, n);
        sinkA = a; sinkS = sa;
        double[] t = new double[31]; float d = 0;
        for (int r = -3; r < 31; r++) {
            long t0 = System.nanoTime();
            for (int it = 0; it < 65536; it++) d = mode.equals("heap") ? heap(sinkA, b) : seg(sinkS, sb, n);
            long t1 = System.nanoTime();
            if (r >= 0) t[r] = (t1 - t0) * 1e-6;
        }
        java.util.Arrays.sort(t);
        System.out.printf("Java %s : médiane %.3f ms (min %.3f) somme %.4f adresse%%64=%d%n", mode, t[15], t[0], d, sa.address() % 64);
    }
}
