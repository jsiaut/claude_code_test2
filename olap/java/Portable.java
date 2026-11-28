// v7 : niveau portable des primitives à deux niveaux du banc OLAP en Java (classe Level du binaire olap_p). Aucune
// vectorisation explicite : le compilateur à la volée vectorise ce qu'il sait vectoriser.
import static java.lang.foreign.ValueLayout.JAVA_LONG_UNALIGNED;

final class Level {
    static final String LEVEL = "p";
    static final int SEARCH_STEP = 0;  // pas de recherche par 64 positions à ce niveau

    static long searchCandidates(long p, int m, byte c0, byte c1) { return 0; }

    private static long word(long a) { return Olap.MEM.get(JAVA_LONG_UNALIGNED, a); }

    // Décodage. Le langage n'a pas de généricité sur les constantes : chaque largeur appelle une des deux formes avec
    // sa largeur en constante, et le compilateur à la volée spécialise la forme là où elle est intégrée.
    static void unpack(long in, int[] out, int n, int base, int w) {
        switch (w) {
            case 1 -> one(in, out, n, base, 1);
            case 2 -> one(in, out, n, base, 2);
            case 3 -> two(in, out, n, base, 3);
            case 4 -> one(in, out, n, base, 4);
            case 5 -> two(in, out, n, base, 5);
            case 6 -> two(in, out, n, base, 6);
            case 7 -> two(in, out, n, base, 7);
            case 8 -> one(in, out, n, base, 8);
            case 9 -> two(in, out, n, base, 9);
            case 10 -> two(in, out, n, base, 10);
            case 11 -> two(in, out, n, base, 11);
            case 12 -> two(in, out, n, base, 12);
            case 13 -> two(in, out, n, base, 13);
            case 14 -> two(in, out, n, base, 14);
            case 15 -> two(in, out, n, base, 15);
            case 16 -> one(in, out, n, base, 16);
            case 17 -> two(in, out, n, base, 17);
            case 18 -> two(in, out, n, base, 18);
            case 19 -> two(in, out, n, base, 19);
            case 20 -> two(in, out, n, base, 20);
            case 21 -> two(in, out, n, base, 21);
            case 22 -> two(in, out, n, base, 22);
            case 23 -> two(in, out, n, base, 23);
            case 24 -> two(in, out, n, base, 24);
            case 25 -> two(in, out, n, base, 25);
            case 26 -> two(in, out, n, base, 26);
            case 27 -> two(in, out, n, base, 27);
            case 28 -> two(in, out, n, base, 28);
            case 29 -> two(in, out, n, base, 29);
            case 30 -> two(in, out, n, base, 30);
            case 31 -> two(in, out, n, base, 31);
            default -> one(in, out, n, base, 32);
        }
    }
    /** La largeur divise 64 : chaque mot porte 64 / w valeurs entières. */
    private static void one(long in, int[] out, int n, int base, int w) {
        final long mask = (1L << w) - 1;
        final int per = 64 / w;
        for (int o = 0; o < n; in += 8) {
            long v = word(in);
            for (int i = 0; i < per; i++, v >>>= w) out[o++] = (int) (v & mask) + base;
        }
    }
    /** Cas général : deux mots voisins sont toujours combinés, sans test ; un groupe de 64 valeurs occupe w mots. */
    private static void two(long in, int[] out, int n, int base, int w) {
        final long mask = (1L << w) - 1;
        for (int g = 0; g < n; g += 64, in += 8L * w) {
            for (int j = 0; j < 64; j++) {
                final int bit = j * w, sh = bit & 63;
                final long a = in + (bit >>> 6 << 3);
                out[g + j] = (int) (((word(a) >>> sh) | (word(a + 8) << 1 << (63 - sh))) & mask) + base;
            }
        }
    }

    /** 1 si x est entre lo et lo + span, 0 sinon ; sans branchement : la retenue d'une soustraction non signée. */
    private static int inRange(int x, int lo, long span) {
        return (int) (1 - ((span - ((x - lo) & 0xFFFFFFFFL)) >>> 63));
    }
    /** Sélection. Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises. */
    static int selBetween(int[] v, int n, int lo, int hi, int base, int[] pos) {
        final long span = (hi - lo) & 0xFFFFFFFFL;
        int k = 0;
        for (int i = 0; i < n; i++) {
            pos[k] = base + i;
            k += inRange(v[i], lo, span);
        }
        return k;
    }
    /** Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi. */
    static int keepBetween(int[] v, int[] posIn, int[] payIn, int n, int lo, int hi, int[] posOut, int[] payOut) {
        final long span = (hi - lo) & 0xFFFFFFFFL;
        int k = 0;
        for (int i = 0; i < n; i++) {
            posOut[k] = posIn[i];
            payOut[k] = payIn[i];
            k += inRange(v[i], lo, span);
        }
        return k;
    }

    /**
     * Agrégation de T1 : un vecteur de n lignes dans le tableau des six groupes (huit cases par groupe) ; ship non
     * nul : seules comptent les lignes dont la date ne dépasse pas cut (vecteur de sélection dans sel).
     */
    static void t1Aggregate(long[] agg, int[] grp, int[] qty, int[] ext, int[] disc, long[] dp, long[] ch, int[] ship, int cut, int n,
            int[] sel) {
        if (ship == null) {
            for (int i = 0; i < n; i++) add(agg, grp[i] * 8, qty[i], ext[i], dp[i], ch[i], disc[i]);
        } else {
            final int k = selBetween(ship, n, Integer.MIN_VALUE, cut, 0, sel);
            for (int j = 0; j < k; j++) {
                final int i = sel[j];
                add(agg, grp[i] * 8, qty[i], ext[i], dp[i], ch[i], disc[i]);
            }
        }
    }
    private static void add(long[] agg, int g, int qty, int ext, long dp, long ch, int disc) {
        agg[g] += qty;
        agg[g + 1] += ext;
        agg[g + 2] += dp;
        agg[g + 3] += ch;
        agg[g + 4] += disc;
        agg[g + 5]++;
    }
}
