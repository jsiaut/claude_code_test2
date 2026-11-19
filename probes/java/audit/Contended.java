// Audit de la grille, Java, D3 : @Contended (annotation interne de java.base) sur deux champs voisins ; décalages lus
// par sun.misc.Unsafe. Compilé avec --add-exports java.base/jdk.internal.vm.annotation=ALL-UNNAMED (run.sh).
import java.lang.reflect.Field;
public class Contended {
    static class Pad { @jdk.internal.vm.annotation.Contended long a; @jdk.internal.vm.annotation.Contended long b; }
    public static void main(String[] x) throws Exception {
        Field uf = sun.misc.Unsafe.class.getDeclaredField("theUnsafe"); uf.setAccessible(true);
        sun.misc.Unsafe u = (sun.misc.Unsafe) uf.get(null);
        long a = u.objectFieldOffset(Pad.class.getDeclaredField("a")), b = u.objectFieldOffset(Pad.class.getDeclaredField("b"));
        System.out.println(Math.abs(b - a));
    }
}
