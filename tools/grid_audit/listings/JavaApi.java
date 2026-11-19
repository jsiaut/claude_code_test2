// API publique de la construction Java du banc : pour chaque module système, les paquets exportés sans restriction,
// leurs classes publiques et leurs membres publics ou protégés, un nom par ligne, pour tools/grid_audit/search.py.
// Lancer : java --add-modules ALL-SYSTEM JavaApi.java
import java.lang.module.*;
import java.lang.reflect.*;
import java.net.URI;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

public class JavaApi {
    public static void main(String[] a) throws Exception {
        FileSystem jrt = FileSystems.getFileSystem(URI.create("jrt:/"));
        TreeSet<String> out = new TreeSet<>();
        for (ModuleReference mr : ModuleFinder.ofSystem().findAll()) {
            ModuleDescriptor md = mr.descriptor();
            for (ModuleDescriptor.Exports ex : md.exports()) {
                if (ex.isQualified()) continue;
                Path dir = jrt.getPath("/modules", md.name(), ex.source().replace('.', '/'));
                if (!Files.isDirectory(dir)) continue;
                List<Path> files;
                try (Stream<Path> s = Files.list(dir)) { files = s.collect(Collectors.toList()); }
                for (Path p : files) {
                    String fn = p.getFileName().toString();
                    if (!fn.endsWith(".class") || fn.startsWith("module-info") || fn.startsWith("package-info")) continue;
                    Class<?> c;
                    try { c = Class.forName(ex.source() + "." + fn.substring(0, fn.length() - 6), false, ClassLoader.getSystemClassLoader()); }
                    catch (Throwable t) { continue; }
                    if (!visible(c)) continue;
                    String tn = c.getName();
                    out.add("type " + tn + " (" + md.name() + ")");
                    try {
                        for (Method m : c.getDeclaredMethods()) if (vis(m.getModifiers()) && !m.isSynthetic()) out.add("méthode " + tn + "." + m.getName());
                        for (Field f : c.getDeclaredFields()) if (vis(f.getModifiers()) && !f.isSynthetic()) out.add("champ " + tn + "." + f.getName());
                    } catch (Throwable t) { out.add("type " + tn + " (membres illisibles)"); }
                }
            }
        }
        out.forEach(System.out::println);
    }
    static boolean vis(int m) { return Modifier.isPublic(m) || Modifier.isProtected(m); }
    static boolean visible(Class<?> c) {
        if (c.isAnonymousClass() || c.isLocalClass() || c.isSynthetic()) return false;
        for (Class<?> k = c; k != null; k = k.getDeclaringClass()) if (!vis(k.getModifiers())) return false;
        return true;
    }
}
