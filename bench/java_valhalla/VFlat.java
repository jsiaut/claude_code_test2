// Annexe Valhalla : quelle taille de valeur la JVM EA (JEP 401, 27-jep401ea3) aplatit-elle dans un tableau ?
// Mesure : octets vivants par élément après GC. Usage : java --enable-preview VFlat <v1|v2|v3|v4>
// (avec -XX:+UnlockDiagnosticVMOptions -XX:+PrintFlatArrayLayout, la JVM imprime la disposition choisie)
public class VFlat {
    value record V1(float a) {}                             // 4 o
    value record V2(float a, float b) {}                    // 8 o
    value record V3(float a, float b, float c) {}           // 12 o
    value record V4(float a, float b, float c, float d) {}  // 16 o
    static final int N = 1 << 22;
    static long live() { Runtime r = Runtime.getRuntime(); System.gc(); System.gc(); return r.totalMemory() - r.freeMemory(); }
    public static void main(String[] a) {
        long b0 = live();
        Object keep;
        switch (a[0]) {
            case "v1" -> { V1[] t = new V1[N]; for (int i = 0; i < N; i++) t[i] = new V1(i); keep = t; }
            case "v2" -> { V2[] t = new V2[N]; for (int i = 0; i < N; i++) t[i] = new V2(i, i); keep = t; }
            case "v3" -> { V3[] t = new V3[N]; for (int i = 0; i < N; i++) t[i] = new V3(i, i, i); keep = t; }
            default -> { V4[] t = new V4[N]; for (int i = 0; i < N; i++) t[i] = new V4(i, i, i, i); keep = t; }
        }
        long b1 = live();
        System.out.printf("%s %s : %.1f octets par element%n", a[0], keep.getClass().getName(), (b1 - b0) / (double) N);
        if (keep.hashCode() == 42) System.out.println();
    }
}
