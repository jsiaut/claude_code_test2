// v7 : niveau portable des primitives à deux niveaux du banc OLAP en Java (classe Level du binaire olap_p). Aucune
// vectorisation explicite : le compilateur à la volée vectorise ce qu'il sait vectoriser.
final class Level {
    static final String LEVEL = "p";
    static final int SEARCH_STEP = 0;  // pas de recherche par 64 positions à ce niveau

    static long searchCandidates(long p, int m, byte c0, byte c1) { return 0; }

    /** Décodage : une routine par largeur, engendrée (GenUnpack.java écrit UnpackGen.java). */
    static void unpack(long in, int[] out, int n, int base, int w) { UnpackGen.unpack(in, out, n, base, w); }

    /** Expressions de T1 sur un vecteur : prix remisé, prix taxé, groupe. */
    static void t1Expr(int[] ext, int[] disc, int[] tax, int[] rf, int[] ls, long[] x, long[] y, int[] g, int n) {
        for (int i = 0; i < n; i++) x[i] = (long) ext[i] * (100 - disc[i]);
        for (int i = 0; i < n; i++) y[i] = x[i] * (100 + tax[i]);
        for (int i = 0; i < n; i++) g[i] = rf[i] * 2 + ls[i];
    }
    /** Hachage d'un vecteur de clés de 32 bits, puis de 64 bits lues à une adresse. */
    static void hashKeys(int[] key, int n, long[] h) {
        for (int i = 0; i < n; i++) h[i] = Olap.hash64(key[i]);
    }
    static void hashLongs(long v, int n, long[] h) {
        for (int i = 0; i < n; i++) h[i] = Olap.hash64(Olap.getLong(v + 8L * i));
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
