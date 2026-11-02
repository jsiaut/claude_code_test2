import java.lang.foreign.*;
import java.lang.invoke.VarHandle;
import static java.lang.foreign.MemoryLayout.PathElement.*;
public class Ffm {
    public static void main(String[] a) {
        // F1 : tableau 2D contigu (4 x 3 double), accès par deux indices
        MemoryLayout grid = MemoryLayout.sequenceLayout(4, MemoryLayout.sequenceLayout(3, ValueLayout.JAVA_DOUBLE));
        VarHandle g = grid.varHandle(sequenceElement(), sequenceElement());
        try (Arena ar = Arena.ofConfined()) {
            MemorySegment s = ar.allocate(grid);
            for (long i = 0; i < 4; i++) for (long j = 0; j < 3; j++) g.set(s, 0L, i, j, (double) (10 * i + j));
            System.out.println("F1 : taille " + grid.byteSize() + " o ; [2][1] = " + g.get(s, 0L, 2L, 1L)
                + " ; décalage de [2][1] = " + grid.byteOffset(sequenceElement(2), sequenceElement(1))
                + " ; lu à plat : " + s.getAtIndex(ValueLayout.JAVA_DOUBLE, 2 * 3 + 1));
            // tableau 2D sur le tas (segment d'un double[]) : même accès
            double[] heap = new double[12];
            MemorySegment hs = MemorySegment.ofArray(heap);
            g.set(hs, 0L, 3L, 2L, 42.0);
            System.out.println("F1 sur le tas : heap[11] = " + heap[11]);
            // A5 : union float / int
            MemoryLayout u = MemoryLayout.unionLayout(ValueLayout.JAVA_FLOAT.withName("f"), ValueLayout.JAVA_INT.withName("i"));
            VarHandle uf = u.varHandle(groupElement("f")), ui = u.varHandle(groupElement("i"));
            MemorySegment us = ar.allocate(u);
            uf.set(us, 0L, 1.0f);
            System.out.printf("A5 : union de %d o ; bits de 1.0f lus par le membre i : 0x%08x%n", u.byteSize(), (int) ui.get(us, 0L));
            // réinterprétation sans copie d'un tableau du tas
            float[] fa = {1.0f, -2.0f};
            MemorySegment fs = MemorySegment.ofArray(fa);
            System.out.printf("A5 : float[] du tas lu en int : 0x%08x 0x%08x%n", fs.getAtIndex(ValueLayout.JAVA_INT, 0), fs.getAtIndex(ValueLayout.JAVA_INT, 1));
        }
    }
}
