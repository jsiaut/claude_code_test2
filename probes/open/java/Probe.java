// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Java
// (D4 : net.openhft:affinity ; F1 : org.tensorflow:ndarray ; F2 : org.apache.ignite:ignite-numa-allocator).
import net.openhft.affinity.Affinity;
import org.tensorflow.ndarray.NdArrays;
import org.tensorflow.ndarray.DoubleNdArray;
import org.tensorflow.ndarray.Shape;
import org.tensorflow.ndarray.buffer.DataBuffers;
import org.apache.ignite.mem.NumaAllocator;
import org.apache.ignite.mem.SimpleNumaAllocationStrategy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.BitSet;
import java.util.TreeSet;

public class Probe {
  static void d4() throws Exception {
    final String[] out = new String[1];
    Thread t = new Thread(() -> {
      BitSet b = new BitSet(); b.set(2);
      Affinity.setAffinity(b);
      TreeSet<Integer> cpus = new TreeSet<>();
      for (int i = 0; i < 1000; i++) cpus.add(Affinity.getCpu());
      out[0] = "Affinity.setAffinity({2}) dans un fil : getAffinity = " + Affinity.getAffinity() + ", getCpu sur 1000 lectures = " + cpus;
    });
    t.start(); t.join();
    System.out.println("RESULT;D4;affinity;" + out[0]);
  }

  static void f1() {
    int m = Integer.parseInt(System.getProperty("m", "300")), n = 500;
    double[] backing = new double[m * n];
    DoubleNdArray a = NdArrays.wrap(Shape.of(m, n), DataBuffers.of(backing, false, false));
    a.setDouble(7.0, 2, 3);
    int idx = -1;
    for (int i = 0; i < backing.length; i++) if (backing[i] == 7.0) idx = i;
    DoubleNdArray row = a.get(2);
    System.out.println("RESULT;F1;ndarray;NdArrays.wrap(Shape.of(" + m + ", " + n + "), DataBuffers.of(double[" + (m * n) + "])) de dimensions connues à l'exécution : shape " + a.shape() + ", a[2, 3] = " + a.getDouble(2, 3) + " écrit à l'indice " + idx + " du tableau Java sous-jacent (2*" + n + "+3) ; a.get(2) est une vue de forme " + row.shape());
  }

  static void f2() throws Exception {
    NumaAllocator al = new NumaAllocator(new SimpleNumaAllocationStrategy(0));
    long size = 1 << 22;
    long p = al.allocateMemory(size);
    for (long off = 0; off < size; off += 4096) unsafePut(p + off);
    String hex = Long.toHexString(p);
    String line = "(introuvable)";
    for (String l : Files.readAllLines(Path.of("/proc/self/numa_maps"))) {
      long start = Long.parseLong(l.substring(0, l.indexOf(' ')), 16);
      if (start <= p && p < start + size) { line = l; break; }
    }
    System.out.println("RESULT;F2;ignite-numa-allocator;NumaAllocator(SimpleNumaAllocationStrategy(0)).allocateMemory(4 Mio) = 0x" + hex + " ; /proc/self/numa_maps : " + line.trim());
    al.freeMemory(p);
  }

  static final sun.misc.Unsafe U;
  static {
    try {
      java.lang.reflect.Field f = sun.misc.Unsafe.class.getDeclaredField("theUnsafe");
      f.setAccessible(true);
      U = (sun.misc.Unsafe) f.get(null);
    } catch (Exception e) { throw new RuntimeException(e); }
  }
  static void unsafePut(long addr) { U.putByte(addr, (byte) 1); }

  public static void main(String[] args) throws Exception {
    d4(); f1(); f2();
  }
}
