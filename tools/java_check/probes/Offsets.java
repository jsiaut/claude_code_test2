import java.lang.reflect.Field;
public class Offsets {
    public static void main(String[] a) throws Exception {
        Field f = sun.misc.Unsafe.class.getDeclaredField("theUnsafe"); f.setAccessible(true);
        sun.misc.Unsafe u = (sun.misc.Unsafe) f.get(null);
        System.out.println("byte[] " + u.arrayBaseOffset(byte[].class) + " int[] " + u.arrayBaseOffset(int[].class)
            + " float[] " + u.arrayBaseOffset(float[].class) + " long[] " + u.arrayBaseOffset(long[].class)
            + " double[] " + u.arrayBaseOffset(double[].class) + " Object[] " + u.arrayBaseOffset(Object[].class));
    }
}
