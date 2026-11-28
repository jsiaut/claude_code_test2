// v7 : niveau spécialisé des primitives à deux niveaux du banc OLAP en Java (classe Level du binaire olap_s ;
// olap/SPEC.md, 7) : AVX-512 par l'API vectorielle (jdk.incubator.vector). Même plan, mêmes structures, mêmes
// fonctions de hachage.
//
//   0. décodage : seize valeurs à la fois, par permutation d'octets et décalages variables ;
//   1. sélection : comparaison de 16 valeurs et compression des positions retenues ;
//   2. agrégation de T1 : sommes masquées par groupe, huit lignes à la fois ;
//   3. recherche de sous-chaîne : premier et dernier octet de l'aiguille comparés à 64 positions à la fois ;
//   4. expressions de T1 et hachage des clés, huit lignes à la fois.
//
// Le langage n'offre ni écriture non temporelle ni préchargement : la répartition et les sondes restent celles du
// niveau portable. Ce sont deux manques.
import java.nio.ByteOrder;
import jdk.incubator.vector.ByteVector;
import jdk.incubator.vector.IntVector;
import jdk.incubator.vector.LongVector;
import jdk.incubator.vector.VectorMask;
import jdk.incubator.vector.VectorOperators;
import jdk.incubator.vector.VectorShuffle;
import jdk.incubator.vector.VectorSpecies;

final class Level {
    static final String LEVEL = "s";
    static final int SEARCH_STEP = 64;

    static final VectorSpecies<Integer> I16 = IntVector.SPECIES_512, I8 = IntVector.SPECIES_256;
    static final VectorSpecies<Long> L8 = LongVector.SPECIES_512;
    static final VectorSpecies<Byte> B64 = ByteVector.SPECIES_512;

    // ------------------------------------------------------------------------------------------------ 0. décodage
    // Seize valeurs à la fois (largeur de 25 bits au plus) : elles occupent 2 x largeur octets ; une permutation
    // d'octets amène dans chaque voie de 32 bits les 4 octets où commence sa valeur, un décalage variable la cale, un
    // masque la borne. Au-delà de 25 bits : huit valeurs à la fois dans des voies de 64 bits. Chaque pas lit 64
    // octets : les colonnes sont chargées avec cette marge.
    @SuppressWarnings({"unchecked", "rawtypes"})
    static final VectorShuffle<Byte>[] IDX = new VectorShuffle[33];
    static final IntVector[] SH32 = new IntVector[33];
    static final LongVector[] SH64 = new LongVector[33];
    static {
        for (int w = 1; w <= 32; w++) {
            final int lanes = w <= 25 ? 16 : 8, size = 64 / lanes;
            final int[] idx = new int[64], sh32 = new int[16];
            final long[] sh64 = new long[8];
            for (int j = 0; j < lanes; j++) {
                for (int k = 0; k < size; k++) idx[size * j + k] = (j * w >> 3) + k;
                if (w <= 25) sh32[j] = j * w & 7; else sh64[j] = j * w & 7;
            }
            IDX[w] = VectorShuffle.fromArray(B64, idx, 0);
            SH32[w] = IntVector.fromArray(I16, sh32, 0);
            SH64[w] = LongVector.fromArray(L8, sh64, 0);
        }
    }
    static void unpack(long in, int[] out, int n, int base, int w) {
        final VectorShuffle<Byte> idx = IDX[w];
        if (w <= 25) {
            final IntVector sh = SH32[w];
            final int mask = (1 << w) - 1;
            for (int i = 0; i < n; i += 16, in += 2L * w) {
                final IntVector x = ByteVector.fromMemorySegment(B64, Olap.MEM, in, ByteOrder.LITTLE_ENDIAN).rearrange(idx).reinterpretAsInts();
                x.lanewise(VectorOperators.LSHR, sh).and(mask).add(base).intoArray(out, i);
            }
        } else {
            final LongVector sh = SH64[w];
            final long mask = (1L << w) - 1;
            for (int i = 0; i < n; i += 8, in += w) {
                final LongVector x = ByteVector.fromMemorySegment(B64, Olap.MEM, in, ByteOrder.LITTLE_ENDIAN).rearrange(idx).reinterpretAsLongs();
                ((IntVector) x.lanewise(VectorOperators.LSHR, sh).and(mask).convertShape(VectorOperators.L2I, I8, 0)).add(base).intoArray(out, i);
            }
        }
    }

    // ------------------------------------------------------------------------------------------------ 1. sélection
    /** Masque des valeurs de v[i..i+16) comprises entre lo et hi, limité aux n - i valeurs qui restent. */
    private static VectorMask<Integer> between(int[] v, int i, int n, int lo, int hi) {
        final IntVector x = IntVector.fromArray(I16, v, i);
        final VectorMask<Integer> m = x.compare(VectorOperators.GE, lo).and(x.compare(VectorOperators.LE, hi));
        return n - i >= 16 ? m : m.and(VectorMask.fromLong(I16, (1L << (n - i)) - 1));
    }
    /** Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises. */
    static int selBetween(int[] v, int n, int lo, int hi, int base, int[] pos) {
        IntVector idx = IntVector.broadcast(I16, base).addIndex(1);
        int k = 0;
        for (int i = 0; i < n; i += 16) {
            final VectorMask<Integer> m = between(v, i, n, lo, hi);
            idx.compress(m).intoArray(pos, k);
            k += m.trueCount();
            idx = idx.add(16);
        }
        return k;
    }
    /** Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi. */
    static int keepBetween(int[] v, int[] posIn, int[] payIn, int n, int lo, int hi, int[] posOut, int[] payOut) {
        int k = 0;
        for (int i = 0; i < n; i += 16) {
            final VectorMask<Integer> m = between(v, i, n, lo, hi);
            IntVector.fromArray(I16, posIn, i).compress(m).intoArray(posOut, k);
            IntVector.fromArray(I16, payIn, i).compress(m).intoArray(payOut, k);
            k += m.trueCount();
        }
        return k;
    }

    // ------------------------------------------------------------------------------------------------ 2. agrégation de T1
    // Huit lignes à la fois : pour chacun des six groupes, un masque et cinq additions masquées. Les accumulateurs
    // sont des voies d'un tableau de travail du fil appelant (six groupes de cinq sommes de huit voies).
    private static final ThreadLocal<long[]> ACC = ThreadLocal.withInitial(() -> new long[6 * 5 * 8]);

    static void t1Aggregate(long[] agg, int[] grp, int[] qty, int[] ext, int[] disc, long[] dp, long[] ch, int[] ship, int cut, int n,
            int[] sel) {
        final long[] acc = ACC.get();
        java.util.Arrays.fill(acc, 0);
        final int[] cnt = new int[6];
        for (int i = 0; i < n; i += 8) {
            VectorMask<Integer> live = n - i >= 8 ? I8.maskAll(true) : VectorMask.fromLong(I8, (1L << (n - i)) - 1);
            if (ship != null) live = live.and(IntVector.fromArray(I8, ship, i).compare(VectorOperators.LE, cut));
            final IntVector g8 = IntVector.fromArray(I8, grp, i);
            final LongVector q = (LongVector) IntVector.fromArray(I8, qty, i).convertShape(VectorOperators.I2L, L8, 0);
            final LongVector e = (LongVector) IntVector.fromArray(I8, ext, i).convertShape(VectorOperators.I2L, L8, 0);
            final LongVector d = (LongVector) IntVector.fromArray(I8, disc, i).convertShape(VectorOperators.I2L, L8, 0);
            final LongVector x = LongVector.fromArray(L8, dp, i), y = LongVector.fromArray(L8, ch, i);
            for (int g = 0; g < 6; g++) {
                final VectorMask<Integer> m32 = g8.compare(VectorOperators.EQ, g).and(live);
                final VectorMask<Long> m = m32.cast(L8);
                final int o = g * 40;
                LongVector.fromArray(L8, acc, o).add(q, m).intoArray(acc, o);
                LongVector.fromArray(L8, acc, o + 8).add(e, m).intoArray(acc, o + 8);
                LongVector.fromArray(L8, acc, o + 16).add(x, m).intoArray(acc, o + 16);
                LongVector.fromArray(L8, acc, o + 24).add(y, m).intoArray(acc, o + 24);
                LongVector.fromArray(L8, acc, o + 32).add(d, m).intoArray(acc, o + 32);
                cnt[g] += m32.trueCount();
            }
        }
        for (int g = 0; g < 6; g++) {
            for (int j = 0; j < 5; j++) {
                long sum = 0;
                for (int l = 0; l < 8; l++) sum += acc[g * 40 + j * 8 + l];
                agg[g * 8 + j] += sum;
            }
            agg[g * 8 + 5] += cnt[g];
        }
    }

    // ------------------------------------------------------------------------------------------------ 4. expressions, hachage
    private static LongVector widen(int[] v, int i) {
        return (LongVector) IntVector.fromArray(I8, v, i).convertShape(VectorOperators.I2L, L8, 0);
    }
    /** Expressions de T1 sur un vecteur, huit lignes à la fois : prix remisé, prix taxé, groupe. */
    static void t1Expr(int[] ext, int[] disc, int[] tax, int[] rf, int[] ls, long[] x, long[] y, int[] g, int n) {
        for (int i = 0; i < n; i += 8) {
            final LongVector xv = widen(ext, i).mul(widen(disc, i).neg().add(100));
            xv.intoArray(x, i);
            xv.mul(widen(tax, i).add(100)).intoArray(y, i);
            IntVector.fromArray(I8, rf, i).lanewise(VectorOperators.LSHL, 1).add(IntVector.fromArray(I8, ls, i)).intoArray(g, i);
        }
    }
    /** Hachage d'un vecteur de clés de 32 bits, huit à la fois. */
    static void hashKeys(int[] key, int n, long[] h) {
        for (int i = 0; i < n; i += 8) {
            final LongVector k = widen(key, i).mul(Olap.K1);
            k.lanewise(VectorOperators.XOR, k.lanewise(VectorOperators.LSHR, 32)).intoArray(h, i);
        }
    }
    /** Hachage d'un vecteur de clés de 64 bits lues à une adresse : huit à la fois, puis le reste une à une. */
    static void hashLongs(long v, int n, long[] h) {
        int i = 0;
        for (; i + 8 <= n; i += 8) {
            final LongVector k = LongVector.fromMemorySegment(L8, Olap.MEM, v + 8L * i, ByteOrder.LITTLE_ENDIAN).mul(Olap.K1);
            k.lanewise(VectorOperators.XOR, k.lanewise(VectorOperators.LSHR, 32)).intoArray(h, i);
        }
        for (; i < n; i++) h[i] = Olap.hash64(Olap.getLong(v + 8L * i));
    }

    // ------------------------------------------------------------------------------------------------ 3. sous-chaînes
    /** Candidates parmi les 64 positions qui partent de p : premier octet de l'aiguille en p + i, dernier en p + i + m - 1. */
    static long searchCandidates(long p, int m, byte c0, byte c1) {
        return ByteVector.fromMemorySegment(B64, Olap.MEM, p, ByteOrder.LITTLE_ENDIAN).eq(c0).toLong()
                & ByteVector.fromMemorySegment(B64, Olap.MEM, p + m - 1, ByteOrder.LITTLE_ENDIAN).eq(c1).toLong();
    }
}
