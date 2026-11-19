// Audit de la grille, Java (OpenJDK 27.0.1, réglages du banc : C2, G1, jdk.incubator.vector) : chaque case est
// exercée sous sa forme la plus forte et imprime un fait observable (docs/V4_PLAN.md 2.1). Lignes FACT (reprises par
// run.sh avec les formes refusées par javac et les recherches) et NOTE (contre-épreuves).
import java.lang.foreign.*;
import java.lang.invoke.*;
import java.lang.management.*;
import java.lang.reflect.*;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;
import java.util.stream.*;
import jdk.incubator.vector.*;

public class Audit {
    static void fact(String c, String ev) { System.out.println("FACT;" + c + ";" + ev); }
    static void note(String c, String ev) { System.out.println("NOTE;" + c + ";" + ev); }
    static final com.sun.management.ThreadMXBean TM = (com.sun.management.ThreadMXBean) ManagementFactory.getThreadMXBean();
    static long alloc() { return TM.getCurrentThreadAllocatedBytes(); }
    static long gcCount() { long n = 0; for (GarbageCollectorMXBean g : ManagementFactory.getGarbageCollectorMXBeans()) n += g.getCollectionCount(); return n; }
    static sun.misc.Unsafe U;
    static class P { byte a; long b; int c; }
    static class WithArr { float[] f = new float[16]; int n; }
    record Pt(int x, int y) {}
    static volatile Object sinkO;
    static long sinkL;
    static int vx;

    static Pt make(int i) { return new Pt(i, i + 1); }      // incorporée par C2 : l'analyse d'échappement peut supprimer l'objet
    static Pt makeNI(int i) { return new Pt(i, i + 1); }    // jamais incorporée (run.sh : -XX:CompileCommand=dontinline)
    static long useMake(int n) { long s = 0; for (int i = 0; i < n; i++) { Pt p = make(i); s += p.x() + p.y(); } return s; }
    static long useMakeNI(int n) { long s = 0; for (int i = 0; i < n; i++) { Pt p = makeNI(i); s += p.x() + p.y(); } return s; }
    static void axpy(float[] y, int yo, float[] x, int xo, int n, float a) { for (int i = 0; i < n; i++) y[yo + i] += a * x[xo + i]; }

    public static void main(String[] args) throws Throwable {
        if (args.length > 0 && args[0].equals("eps")) { epsilon(Integer.parseInt(args[1])); return; }
        Field uf = sun.misc.Unsafe.class.getDeclaredField("theUnsafe"); uf.setAccessible(true); U = (sun.misc.Unsafe) uf.get(null);
        try (Arena ar = Arena.ofConfined()) {
            // ---------- A : disposition
            StructLayout part = MemoryLayout.structLayout(MemoryLayout.sequenceLayout(16, ValueLayout.JAVA_FLOAT).withName("f"));
            SequenceLayout parts = MemoryLayout.sequenceLayout(1000, part);
            MemorySegment ps = ar.allocate(parts);
            long off1 = parts.byteOffset(MemoryLayout.PathElement.sequenceElement(1));
            fact("A1", "FFM : sequenceLayout(1000, struct de 16 float) : " + ps.byteSize() + " o, élément 1 à " + off1
                + " o (en ligne, hors tas) ; un tableau d'objets ne contient que des références : arrayIndexScale(Object[]) = "
                + U.arrayIndexScale(Object[].class) + " o par élément, chaque objet à part sur le tas");
            StructLayout c = MemoryLayout.structLayout(ValueLayout.JAVA_BYTE.withName("a"), MemoryLayout.paddingLayout(3),
                ValueLayout.JAVA_INT.withName("b"), ValueLayout.JAVA_DOUBLE.withName("c"));
            fact("A2", "FFM : structLayout {byte; padding 3; int; double} : décalages a=" + c.byteOffset(MemoryLayout.PathElement.groupElement("a"))
                + " b=" + c.byteOffset(MemoryLayout.PathElement.groupElement("b")) + " c=" + c.byteOffset(MemoryLayout.PathElement.groupElement("c"))
                + " (disposition C écrite à la main) ; objets : class P {byte a; long b; int c;} placée par HotSpot à a="
                + U.objectFieldOffset(P.class.getDeclaredField("a")) + " b=" + U.objectFieldOffset(P.class.getDeclaredField("b"))
                + " c=" + U.objectFieldOffset(P.class.getDeclaredField("c")) + " (ordre déclaré non gardé, aucun contrôle)");
            StructLayout packed = MemoryLayout.structLayout(ValueLayout.JAVA_BYTE, ValueLayout.JAVA_INT.withByteAlignment(1));
            fact("A3", "FFM : structLayout {byte; int.withByteAlignment(1)} : " + packed.byteSize() + " o (non aligné)");
            MemorySegment al = ar.allocate(256, 64);
            var hs = ManagementFactory.getPlatformMXBean(com.sun.management.HotSpotDiagnosticMXBean.class);
            fact("A4", "Arena.allocate(256, 64) : adresse mod 64 = " + (al.address() % 64) + " (hors tas seulement) ; objets du tas alignés sur ObjectAlignmentInBytes = "
                + hs.getVMOption("ObjectAlignmentInBytes").getValue() + " o, sans attribut d'alignement");
            MemorySegment un = ar.allocate(MemoryLayout.unionLayout(ValueLayout.JAVA_FLOAT, ValueLayout.JAVA_INT));
            un.set(ValueLayout.JAVA_FLOAT, 0, 1.0f);
            fact("A5", String.format("Float.floatToRawIntBits(1f) = 0x%08x ; FFM unionLayout {float; int} (%d o) : float 1.0 relu en int 0x%08x (segments seulement, pas d'union d'objets)",
                Float.floatToRawIntBits(1f), un.byteSize(), un.get(ValueLayout.JAVA_INT, 0)));
            StructLayout inl = MemoryLayout.structLayout(MemoryLayout.sequenceLayout(16, ValueLayout.JAVA_FLOAT).withName("f"), ValueLayout.JAVA_INT.withName("n"));
            fact("A7", "FFM : structLayout {float[16]; int} : " + inl.byteSize() + " o, n à " + inl.byteOffset(MemoryLayout.PathElement.groupElement("n"))
                + " ; objets : le champ float[] f de class WithArr est une référence (n à " + U.objectFieldOffset(WithArr.class.getDeclaredField("n"))
                + ", f à " + U.objectFieldOffset(WithArr.class.getDeclaredField("f")) + "), le tableau est un objet séparé");
            fact("A8", String.format("byte %d, short %d, float %d (Byte.BYTES…) ; Float.floatToFloat16(1.5f) = 0x%04x (demi-précision rangée dans un short)",
                Byte.BYTES, Short.BYTES, Float.BYTES, Float.floatToFloat16(1.5f)));

            // ---------- B : mémoire
            long g0 = gcCount();
            for (int i = 0; i < 1 << 20; i++) sinkO = new byte[1024];
            long g1 = gcCount();
            fact("B1", "1 Gio de tableaux de 1 Kio sans référence : " + (g1 - g0) + " collectes déclenchées par la JVM (G1), sans appel du programme (ramasse-miettes traçant)");
            MemorySegment slab = ar.allocate(4096, 64);
            SegmentAllocator bump = SegmentAllocator.slicingAllocator(slab);
            MemorySegment s1 = bump.allocate(400), s2 = bump.allocate(400);
            Arena tmp = Arena.ofConfined(); MemorySegment t1 = tmp.allocate(64); tmp.close();
            fact("B2", "SegmentAllocator.slicingAllocator (arène par tranches) : deux blocs à " + (s2.address() - s1.address())
                + " o d'écart dans le même tampon ; Arena.close libère tout d'un coup (portée vivante après close : " + t1.scope().isAlive()
                + ") ; segments hors tas seulement : new n'accepte pas d'allocateur");
            for (int r = 0; r < 20; r++) { sinkL += useMake(100_000); sinkL += useMakeNI(100_000); }   // compilation par C2
            long m0 = alloc(); sinkL += useMake(1_000_000); long m1 = alloc();
            long n0 = alloc(); sinkL += useMakeNI(1_000_000); long n1 = alloc();
            fact("B3", "record Pt(int, int) rendu par une méthode non incorporée : " + (n1 - n0) / 1_000_000 + " o de tas par appel (un million d'appels compilés par C2) ; aucun agrégat sur la pile ni retour multiple sans objet");
            note("B3", "même méthode incorporée par C2 : " + (m1 - m0) / 1_000_000 + " o par appel (l'analyse d'échappement supprime l'objet, optimisation non garantie par le langage)");
            for (int r = 0; r < 5; r++) { var w = new ArrayList<Integer>(); for (int i = 0; i < 100_000; i++) w.add(i + 1000); sinkO = w; }
            long l0 = alloc(); var lst = new ArrayList<Integer>(100_000); long l1 = alloc();
            for (int i = 0; i < 100_000; i++) lst.add(i + 1000);
            long l2 = alloc(); sinkO = lst;
            long v0 = alloc(); for (int i = 0; i < 1000; i++) sinkO = Arrays.asList(i, i + 1, i + 2); long v1 = alloc();
            long f0 = alloc(); for (int i = 0; i < 1000; i++) { final int k = i; IntSupplier sup = () -> k + 1; sinkO = sup; } long f1 = alloc();
            fact("B4", "ArrayList<Integer> de 100 000 entiers (génériques effacés : un Integer par élément) : " + (l2 - l1) / 100_000
                + " o de tas par élément ajouté, en plus du tableau de références (" + (l1 - l0) / 100_000 + " o par case) ; Arrays.asList(i, i + 1, i + 2) (tableau des varargs, boîtes, liste) : "
                + (v1 - v0) / 1000 + " o par appel ; lambda capturante : " + (f1 - f0) / 1000 + " o par création");
            int[] ia = new int[8];
            MemorySegment hseg = MemorySegment.ofArray(ia);
            hseg.set(ValueLayout.JAVA_INT, 12, 42);
            String oob;
            try { hseg.get(ValueLayout.JAVA_INT, 32); oob = "rien"; } catch (IndexOutOfBoundsException e) { oob = e.getClass().getSimpleName(); }
            fact("B5", "MemorySegment : écriture à l'octet 12 → ia[3] = " + ia[3] + " ; lecture hors du segment : " + oob + " (accès vérifié, pas de pointeur ni d'arithmétique libre)");

            // ---------- C : SIMD
            var sp = FloatVector.SPECIES_512;
            float[] fa = new float[16], fb = new float[16], fc = new float[16];
            Arrays.fill(fa, 2f); Arrays.fill(fb, 3f); Arrays.fill(fc, 1f);
            var vr = FloatVector.fromArray(sp, fa, 0).fma(FloatVector.fromArray(sp, fb, 0), FloatVector.fromArray(sp, fc, 0));
            fact("C1", "Vector API : FloatVector.SPECIES_512 (" + sp.length() + " voies), fma(2, 3, 1) = " + vr.lane(0) + " ; module jdk.incubator.vector");
            var rnd = new Random(42);
            float[] big = new float[1 << 20];
            for (int i = 0; i < big.length; i++) big[i] = rnd.nextFloat() - 0.5f;
            float seq = 0, red = 0;
            for (int r = 0; r < 30; r++) {
                seq = 0; for (float e : big) seq += e;
                var acc = FloatVector.zero(sp);
                for (int i = 0; i < big.length; i += sp.length()) acc = acc.add(FloatVector.fromArray(sp, big, i));
                red = acc.reduceLanes(VectorOperators.ADD);
            }
            fact("C4", "un million de float : boucle ordonnée (C2) " + seq + ", accumulateur FloatVector + reduceLanes(ADD), ordre libre " + red
                + " (écart " + Math.abs(seq - red) + ") ; la boucle scalaire garde l'ordre (pas de réassociation automatique)");
            var tids = ConcurrentHashMap.newKeySet();
            IntStream.range(0, 64).parallel().forEach(i -> { tids.add(Thread.currentThread().getName()); long t = System.nanoTime(); while (System.nanoTime() - t < 2_000_000) Thread.onSpinWait(); });
            fact("C5", "IntStream.range(0, 64).parallel() : 64 itérations sur " + tids.size() + " fils (ForkJoinPool commun)");

            // ---------- D : parallélisme
            var cnt = new java.util.concurrent.atomic.AtomicLong();
            Thread[] th = new Thread[4];
            for (int t = 0; t < 4; t++) { th[t] = new Thread(() -> { for (int i = 0; i < 1000; i++) cnt.incrementAndGet(); }); th[t].start(); }
            for (Thread t : th) t.join();
            fact("D1", "java.lang.Thread : 4 fils, " + cnt.get() + " incréments (fils virtuels aussi)");
            VarHandle vh = MethodHandles.lookup().findStaticVarHandle(Audit.class, "vx", int.class);
            vh.setRelease(1); int acq = (int) vh.getAcquire(); vh.setOpaque(2); int opq = (int) vh.getOpaque();
            boolean cas = vh.compareAndSet(2, 5); int gaa = (int) vh.getAndAdd(3);
            fact("D2", "VarHandle : setRelease/getAcquire → " + acq + ", setOpaque/getOpaque → " + opq + ", compareAndSet(2, 5) → " + cas + ", getAndAdd(3) → " + gaa + " puis " + vx);
            VarHandle.fullFence(); VarHandle.acquireFence(); VarHandle.releaseFence();
            for (int i = 0; i < 10; i++) Thread.onSpinWait();
            fact("D5", "Thread.onSpinWait, VarHandle.fullFence / acquireFence / releaseFence exécutés (code machine invisible sans hsdis, E1)");
            // contre-épreuve D4 : sched_setaffinity de la glibc appelée par l'API FFM (FFI vers la libc, exclue par la règle)
            Linker lk = Linker.nativeLinker();
            MethodHandle setaff = lk.downcallHandle(lk.defaultLookup().find("sched_setaffinity").orElseThrow(),
                FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.JAVA_LONG, ValueLayout.ADDRESS));
            MethodHandle getcpu = lk.downcallHandle(lk.defaultLookup().find("sched_getcpu").orElseThrow(), FunctionDescriptor.of(ValueLayout.JAVA_INT));
            MemorySegment mask = ar.allocate(128); mask.set(ValueLayout.JAVA_LONG, 0, 2L);
            int rc = (int) setaff.invokeExact(0, 128L, mask);
            note("D4", "sched_setaffinity de la glibc par l'API FFM (Linker.nativeLinker) : retour " + rc + ", processeur courant " + (int) getcpu.invokeExact() + " (FFI vers la libc, non comptée)");

            // ---------- E : contrôle du code
            float[] y = new float[16]; Arrays.fill(y, 1f);
            axpy(y, 1, y, 0, 8, 2f);
            fact("E5", "axpy(y, 1, y, 0, 8, 2) sur un même tableau : y[8] = " + y[8] + " (chaque écriture relue : le compilateur doit supposer l'alias)");
            int[] four = {1, 2, 3, 4};
            String aio;
            try { sinkL += four[4]; aio = "rien"; } catch (ArrayIndexOutOfBoundsException e) { aio = e.getClass().getSimpleName(); }
            fact("E6", "four[4] sur un int[4] : " + aio + " ; ni option ni construction pour couper la vérification (MemorySegment vérifie aussi, B5)");
            note("E6", "sun.misc.Unsafe.getInt(four, base + 4*5) lit hors du tableau sans contrôle : " + U.getInt(four, (long) U.arrayBaseOffset(int[].class) + 4L * 5)
                + " (méthode de jdk.unsupported, dépréciée pour suppression : avertissement à la première utilisation)");

            // ---------- F : données et arithmétique
            int rows = 3 + args.length, cols = 4;
            double[][] g2 = new double[rows][cols];
            g2[1] = new double[7];
            SequenceLayout grid = MemoryLayout.sequenceLayout(3, MemoryLayout.sequenceLayout(4, ValueLayout.JAVA_DOUBLE));
            long o23 = grid.byteOffset(MemoryLayout.PathElement.sequenceElement(2), MemoryLayout.PathElement.sequenceElement(3));
            fact("F1", "double[" + rows + "][" + cols + "] : tableau de tableaux (lignes séparées, g2[1] remplacée par une ligne de " + g2[1].length
                + " éléments) ; FFM : sequenceLayout(3, sequenceLayout(4, double)) contigu, [2][3] à " + o23 + " o = élément " + o23 / 8);
            String ovf;
            try { Math.addExact(Integer.MAX_VALUE, 1); ovf = "rien"; } catch (ArithmeticException e) { ovf = e.getClass().getSimpleName(); }
            fact("F3", "entiers signés seulement : (byte) 200 = " + (byte) 200 + ", Integer.MAX_VALUE + 1 = " + (Integer.MAX_VALUE + 1)
                + " (enveloppe) ; Integer.toUnsignedString(-1) = " + Integer.toUnsignedString(-1) + ", divideUnsigned(-1, 2) = "
                + Integer.divideUnsigned(-1, 2) + " ; Math.addExact : " + ovf);
            try (FileChannel fch = FileChannel.open(Path.of("/opt/msdata/k5_a.f32"))) {
                MemorySegment ms = fch.map(FileChannel.MapMode.READ_ONLY, 0, 8192, ar);
                boolean mapped = Files.readAllLines(Path.of("/proc/self/maps")).stream().anyMatch(l -> l.endsWith("/opt/msdata/k5_a.f32"));
                var le = ValueLayout.JAVA_FLOAT_UNALIGNED.withOrder(ByteOrder.LITTLE_ENDIAN);
                fact("F4", "FileChannel.map → MemorySegment : k5_a.f32 projeté (" + mapped + ", /proc/self/maps), premier float " + ms.get(le, 0) + ", dernier " + ms.get(le, 8188));
            }
        }
    }

    // Contre-épreuve B1 (run.sh) : avec le collecteur Epsilon (expérimental), aucune collecte ; rien n'est rendu
    static void epsilon(int mib) {
        Runtime rt = Runtime.getRuntime();
        for (int i = 0; i < mib; i++) sinkO = new byte[1 << 20];
        System.out.println("EPS;" + mib + ";" + gcCount() + ";" + (rt.totalMemory() - rt.freeMemory()) / (1 << 20));
    }
}
