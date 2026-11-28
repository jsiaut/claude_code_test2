// Engendre UnpackGen.java : une routine de décodage par largeur (java GenUnpack.java). Le langage n'a ni généricité sur
// les constantes ni macros, et son compilateur à la volée ne déroule pas la boucle générale ; comme les moteurs écrits
// en Java, le banc engendre ce code. Un groupe de 64 valeurs occupe W mots : la position de chaque valeur est une
// constante, et le texte sait d'avance lesquelles chevauchent deux mots.
import java.nio.file.Files;
import java.nio.file.Path;

public class GenUnpack {
    public static void main(String[] args) throws Exception {
        final StringBuilder b = new StringBuilder();
        b.append("// Code engendré par GenUnpack.java ; ne pas modifier.\n");
        b.append("final class UnpackGen {\n");
        b.append("    /** Décode n valeurs de largeur w, par groupes entiers de 64, à partir de l'adresse in. */\n");
        b.append("    static void unpack(long in, int[] out, int n, int base, int w) {\n        switch (w) {\n");
        for (int w = 1; w <= 32; w++) b.append("            case " + w + " -> unpack" + w + "(in, out, n, base);\n");
        b.append("            default -> throw new IllegalArgumentException();\n        }\n    }\n");
        for (int w = 1; w <= 32; w++) {
            final long mask = (1L << w) - 1;
            b.append("\n    private static void unpack" + w + "(long in, int[] out, int n, int base) {\n");
            b.append("        for (int o = 0; o < n; o += 64, in += " + 8 * w + ") {\n");
            for (int k = 0; k < w; k++) b.append("            final long w" + k + " = Olap.getLong(in" + (k == 0 ? "" : " + " + 8 * k) + ");\n");
            for (int j = 0; j < 64; j++) {
                final int idx = j * w >> 6, sh = j * w & 63;
                final String v = sh == 0 ? "w" + idx
                        : sh + w <= 64 ? "(w" + idx + " >>> " + sh + ")"
                        : "(w" + idx + " >>> " + sh + " | w" + (idx + 1) + " << " + (64 - sh) + ")";
                b.append("            out[o + " + j + "] = (int) (" + v + " & 0x" + Long.toHexString(mask) + "L) + base;\n");
            }
            b.append("        }\n    }\n");
        }
        b.append("}\n");
        Files.writeString(Path.of("UnpackGen.java"), b);
    }
}
