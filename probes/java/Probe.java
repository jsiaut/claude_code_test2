import java.lang.foreign.*;
import java.lang.invoke.*;
import java.nio.channels.FileChannel;
import java.nio.file.*;
public class Probe {
    static int x;
    public static void main(String[] a) throws Exception {
        VarHandle vh = MethodHandles.lookup().findStaticVarHandle(Probe.class, "x", int.class);
        vh.setRelease(1); int y = (int) vh.getAcquire(); vh.setOpaque(2); VarHandle.fullFence(); Thread.onSpinWait();
        System.out.println("CAP;D2;1;VarHandle setRelease/getAcquire/setOpaque : " + y + " ; D5 fullFence + onSpinWait");
        try (Arena ar = Arena.ofConfined(); FileChannel fc = FileChannel.open(Path.of("/opt/msdata/k5_a.f32"))) {
            MemorySegment seg = fc.map(FileChannel.MapMode.READ_ONLY, 0, 8192, ar);
            System.out.println("CAP;F4;1;FileChannel.map -> MemorySegment : " + seg.get(ValueLayout.JAVA_FLOAT_UNALIGNED.withOrder(java.nio.ByteOrder.LITTLE_ENDIAN), 0));
            StructLayout part = MemoryLayout.structLayout(ValueLayout.JAVA_FLOAT.withName("vx"), MemoryLayout.sequenceLayout(15, ValueLayout.JAVA_FLOAT).withName("rest"));
            MemorySegment ps = ar.allocate(MemoryLayout.sequenceLayout(1024, part));
            System.out.println("CAP;A1;0.5;FFM sequenceLayout(1024, structLayout(...)) : " + ps.byteSize() + " octets ; A7 sequenceLayout dans structLayout");
            StructLayout packed = MemoryLayout.structLayout(ValueLayout.JAVA_BYTE, ValueLayout.JAVA_INT.withByteAlignment(1));
            System.out.println("CAP;A3;0.5;FFM disposition non alignée : " + packed.byteSize() + " octets");
            MemorySegment al = ar.allocate(256, 64);
            System.out.println("CAP;A4;0.5;Arena.allocate(256, 64) adresse mod 64 = " + (al.address() % 64));
        }
    }
}
