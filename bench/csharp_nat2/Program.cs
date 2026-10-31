// Implémentation C# 14 / .NET 10 (BCL seule). Voir docs/SPEC.md.
// Copie de la remarque sur C# (docs/CSHARP.md) : autres choix de code naturel, marqués « Remarque C# : »
// (K1 : struct dans List<T> ; K6 : colonnes passées en paramètres). Sensibilité seulement.
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Globalization;
using System.Numerics;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;

static unsafe class Ms
{
    // ------------------------------------------------------------------ harnais
    static string DataPath(string n) => Path.Combine(Environment.GetEnvironmentVariable("MS_DATA") ?? "/opt/msdata", n);
    static byte[] LoadBytes(string n) => File.ReadAllBytes(DataPath(n));
    static T[] Load<T>(string n) where T : unmanaged => MemoryMarshal.Cast<byte, T>(LoadBytes(n)).ToArray();
    // tampon natif aligné sur 64 octets (NativeMemory.AlignedAlloc)
    static T* LoadAligned<T>(string n, out int count) where T : unmanaged
    {
        byte[] b = LoadBytes(n);
        void* p = NativeMemory.AlignedAlloc((nuint)b.Length, 64);
        b.AsSpan().CopyTo(new Span<byte>(p, b.Length));
        count = b.Length / sizeof(T);
        return (T*)p;
    }
    static int Warmup => int.TryParse(Environment.GetEnvironmentVariable("WARMUP"), out var w) ? w : 1;
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    static void Result(string k, string v, string p, int rep, double sec, string chk) =>
        Console.WriteLine(string.Create(Inv, $"RESULT;{k};{v};{p};{rep};{sec:F9};{chk}"));
    static void Bench(string k, string v, string p, int reps, Func<string> f)
    {
        for (int r = -Warmup; r < reps; r++)
        {
            long t0 = Stopwatch.GetTimestamp();
            string chk = f();
            double dt = Stopwatch.GetElapsedTime(t0).TotalSeconds;
            if (r >= 0) Result(k, v, p, r, dt, chk);
        }
    }

    // ------------------------------------------------------------------ K1
    const int N1 = 1 << 22;
    // naturel : classe (les directives .NET recommandent une classe au-delà de 16 octets)
    // Remarque C# : enregistrement valeur (struct de 64 octets) au lieu d'une classe scellée
    struct Particle
    {
        public float X, Y, Z, Vx, Vy, Vz, Ax, Ay, Az, Mass, Charge, Radius, Temp, Pressure, Energy, Density;
    }
    // AoS valeur : struct C# séquentielle de 64 octets
    [StructLayout(LayoutKind.Sequential)]
    struct PS { public float X, Y, Z, Vx, Vy, Vz, Ax, Ay, Az, Mass, Charge, Radius, Temp, Pressure, Energy, Density; }

    [MethodImpl(MethodImplOptions.NoInlining)]
    static double K1Natural(List<Particle> ps)
    {
        double e = 0;
        foreach (var p in ps) e += 0.5 * p.Mass * (p.Vx * p.Vx + p.Vy * p.Vy + p.Vz * p.Vz);
        return e;
    }
    [MethodImpl(MethodImplOptions.NoInlining)]
    static double K1AoS(PS[] ps)
    {
        double a0 = 0, a1 = 0, a2 = 0, a3 = 0;
        ref PS b = ref MemoryMarshal.GetArrayDataReference(ps);
        for (int i = 0; i < ps.Length; i += 4)
        {
            ref PS p0 = ref Unsafe.Add(ref b, i); ref PS p1 = ref Unsafe.Add(ref b, i + 1);
            ref PS p2 = ref Unsafe.Add(ref b, i + 2); ref PS p3 = ref Unsafe.Add(ref b, i + 3);
            a0 += 0.5f * p0.Mass * (p0.Vx * p0.Vx + p0.Vy * p0.Vy + p0.Vz * p0.Vz);
            a1 += 0.5f * p1.Mass * (p1.Vx * p1.Vx + p1.Vy * p1.Vy + p1.Vz * p1.Vz);
            a2 += 0.5f * p2.Mass * (p2.Vx * p2.Vx + p2.Vy * p2.Vy + p2.Vz * p2.Vz);
            a3 += 0.5f * p3.Mass * (p3.Vx * p3.Vx + p3.Vy * p3.Vy + p3.Vz * p3.Vz);
        }
        return a0 + a1 + a2 + a3;
    }
    [MethodImpl(MethodImplOptions.NoInlining)]
    static double K1SoA(float* vx, float* vy, float* vz, float* m, int n)
    {
        Vector512<double> a0 = default, a1 = default;
        var h = Vector512.Create(0.5f);
        for (int i = 0; i < n; i += 16)
        {
            var x = Vector512.LoadAligned(vx + i); var y = Vector512.LoadAligned(vy + i);
            var z = Vector512.LoadAligned(vz + i); var w = Vector512.LoadAligned(m + i);
            var v2 = Vector512.FusedMultiplyAdd(z, z, Vector512.FusedMultiplyAdd(y, y, x * x));
            var e = h * w * v2;
            a0 += Vector512.WidenLower(e);
            a1 += Vector512.WidenUpper(e);
        }
        return Vector512.Sum(a0 + a1);
    }
    // Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)
    static long LiveNow()
    {
        GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
        return GC.GetTotalMemory(true);
    }
    static long RssNow()
    {
        try { return long.Parse(System.IO.File.ReadAllText("/proc/self/statm").Split(' ')[1]) * 4096; }
        catch { return 0; }
    }
    static void RunK1(string v, int reps)
    {
        if (v == "footprint0") { Result("k1", v, "energy", 0, 0, "0"); return; }
        float[] raw = Load<float>("k1_particles.f32");
        if (v == "footprint_raw") { Result("k1", v, "energy", 0, 0, "0"); return; }
        if (v == "aos")
        {
            PS[] ps = MemoryMarshal.Cast<float, PS>(raw).ToArray();
            Bench("k1", v, "energy", reps, () => K1AoS(ps).ToString("F6", Inv));
            return;
        }
        if (v == "soa")
        {
            var c = new float*[16];
            for (int k = 0; k < 16; k++)
            {
                c[k] = (float*)NativeMemory.AlignedAlloc(N1 * 4, 64);
                for (int i = 0; i < N1; i++) c[k][i] = raw[16 * i + k];
            }
            Bench("k1", v, "energy", reps, () => K1SoA(c[3], c[4], c[5], c[9], N1).ToString("F6", Inv));
            return;
        }
        long m1 = 0, r1 = 0;
        if (v == "footprint") { m1 = LiveNow(); r1 = RssNow(); } // P1 : tampon brut chargé
        var list = new List<Particle>();
        for (int i = 0; i < N1; i++)
        {
            int o = 16 * i;
            list.Add(new Particle { X = raw[o], Y = raw[o + 1], Z = raw[o + 2], Vx = raw[o + 3], Vy = raw[o + 4], Vz = raw[o + 5], Ax = raw[o + 6], Ay = raw[o + 7], Az = raw[o + 8], Mass = raw[o + 9], Charge = raw[o + 10], Radius = raw[o + 11], Temp = raw[o + 12], Pressure = raw[o + 13], Energy = raw[o + 14], Density = raw[o + 15] });
        }
        if (v == "footprint")
        {
            long m2 = LiveNow(), r2 = RssNow(); // P2 : collection construite, tampon brut encore vivant
            Console.WriteLine($"META;mem;live;{m1};{m2}");
            Console.WriteLine($"META;rss;{r1};{r2}");
            Console.WriteLine($"META;raw0;{raw[0].ToString(Inv)}");
            Result("k1", v, "energy", 0, 0, K1Natural(list).ToString("F6", Inv));
            return;
        }
        raw = null!;
        if (v == "natural_shuffled")
        {
            uint[] perm = Load<uint>("k1_perm.u32");
            var s = new List<Particle>(N1);
            foreach (uint j in perm) s.Add(list[(int)j]);
            list = s;
            GC.Collect(); // laisse au GC la possibilité de recompacter
        }
        Bench("k1", v, "energy", reps, () => K1Natural(list).ToString("F6", Inv));
    }

    // ------------------------------------------------------------------ K2
    [MethodImpl(MethodImplOptions.NoInlining)]
    static uint K2Chase(uint[] a, int h)
    {
        ref uint b = ref MemoryMarshal.GetArrayDataReference(a);
        uint i = 0;
        for (int k = 0; k < h; k++) i = Unsafe.Add(ref b, (nint)i);
        return i;
    }
    static void RunK2(string v, int reps, string p)
    {
        uint[] a = Load<uint>($"k2_chase_{p}.u32");
        Bench("k2", v, p, reps, () => K2Chase(a, 4200000).ToString());
    }

    // ------------------------------------------------------------------ K3
    const int ITER3 = 1 << 25;
    static void RunK3(string v, int reps)
    {
        bool rmw = v.StartsWith("rmw");
        int stride = v.EndsWith("padded") ? 16 : 1;
        Console.WriteLine("META;k3_mechanism;" + (rmw ? "Interlocked.Increment (lock xadd)" : "Volatile.Read/Volatile.Write (mov)"));
        long[] c = new long[96];
        Bench("k3", v, "4x2^25", reps, () =>
        {
            var th = new Thread[4];
            for (int t = 0; t < 4; t++)
            {
                int idx = 16 + t * stride;
                c[idx] = 0;
                th[t] = new Thread(() =>
                {
                    if (rmw) for (int i = 0; i < ITER3; i++) Interlocked.Increment(ref c[idx]);
                    else for (int i = 0; i < ITER3; i++) Volatile.Write(ref c[idx], Volatile.Read(ref c[idx]) + 1);
                });
                th[t].Start();
            }
            foreach (var x in th) x.Join();
            long s = 0;
            for (int t = 0; t < 4; t++) s += Volatile.Read(ref c[16 + t * stride]);
            return s.ToString();
        });
    }

    // ------------------------------------------------------------------ K4
    [MethodImpl(MethodImplOptions.NoInlining)]
    static ulong K4Natural(byte[] v) { ulong s = 0; foreach (byte x in v) if (x >= 128) s += x; return s; }
    [MethodImpl(MethodImplOptions.NoInlining)]
    static ulong K4Branchless(byte[] v) { ulong s = 0; foreach (byte x in v) s += (ulong)x * (ulong)(x >> 7); return s; }
    static void RunK4(string v, int reps)
    {
        byte[] d = LoadBytes("k4_bytes.u8");
        if (v == "natural_sorted") Array.Sort(d);
        bool bl = v == "branchless_unsorted";
        Bench("k4", v, "16M", reps, () => (bl ? K4Branchless(d) : K4Natural(d)).ToString());
    }

    // ------------------------------------------------------------------ K5
    const int INNER5 = 1 << 16;
    [MethodImpl(MethodImplOptions.NoInlining)]
    static float K5Natural(float[] a, float[] b) { float s = 0; for (int i = 0; i < a.Length; i++) s += a[i] * b[i]; return s; }
    [MethodImpl(MethodImplOptions.NoInlining)]
    static float K5Tuned(float* a, float* b, int n)
    {
        Vector512<float> s0 = default, s1 = default, s2 = default, s3 = default;
        for (int i = 0; i < n; i += 64)
        {
            s0 = Vector512.FusedMultiplyAdd(Vector512.LoadAligned(a + i), Vector512.LoadAligned(b + i), s0);
            s1 = Vector512.FusedMultiplyAdd(Vector512.LoadAligned(a + i + 16), Vector512.LoadAligned(b + i + 16), s1);
            s2 = Vector512.FusedMultiplyAdd(Vector512.LoadAligned(a + i + 32), Vector512.LoadAligned(b + i + 32), s2);
            s3 = Vector512.FusedMultiplyAdd(Vector512.LoadAligned(a + i + 48), Vector512.LoadAligned(b + i + 48), s3);
        }
        return Vector512.Sum((s0 + s1) + (s2 + s3));
    }
    static void RunK5(string v, int reps)
    {
        float[] a = Load<float>("k5_a.f32"), b = Load<float>("k5_b.f32");
        float* pa = LoadAligned<float>("k5_a.f32", out int n), pb = LoadAligned<float>("k5_b.f32", out _);
        bool tuned = v == "tuned";
        Bench("k5", v, "2048x65536", reps, () =>
        {
            float d = 0;
            for (int it = 0; it < INNER5; it++) d = tuned ? K5Tuned(pa, pb, n) : K5Natural(a, b); // appels non inlinés
            return d.ToString("F4", Inv);
        });
    }

    // ------------------------------------------------------------------ K6
    const int N6 = 1 << 24;
    static int[] sd = null!, pr = null!; static byte[] q = null!, d = null!, t = null!, rf = null!, ls = null!;
    [MethodImpl(MethodImplOptions.NoInlining)]
    static long Q6Natural(int lo, int hi)
    {
        long s = 0;
        for (int i = lo; i < hi; i++)
            if (sd[i] >= 8766 && sd[i] < 9131 && d[i] >= 5 && d[i] <= 7 && q[i] < 24) s += (long)pr[i] * d[i];
        return s;
    }
    static Vector512<int> Ld8(byte[] a, int i) => Avx512F.ConvertToVector512Int32(Vector128.LoadUnsafe(ref MemoryMarshal.GetArrayDataReference(a), (nuint)i));
    static Vector512<int> Ld32(int[] a, int i) => Vector512.LoadUnsafe(ref MemoryMarshal.GetArrayDataReference(a), (nuint)i);
    [MethodImpl(MethodImplOptions.NoInlining)]
    static long Q6Tuned(int lo, int hi)
    {
        Vector512<long> acc = default;
        int i = lo;
        for (; i + 16 <= hi; i += 16)
        {
            var vsd = Ld32(sd, i); var vd = Ld8(d, i); var vq = Ld8(q, i);
            var m = Vector512.GreaterThanOrEqual(vsd, Vector512.Create(8766)) & Vector512.LessThan(vsd, Vector512.Create(9131))
                  & Vector512.GreaterThanOrEqual(vd, Vector512.Create(5)) & Vector512.LessThanOrEqual(vd, Vector512.Create(7))
                  & Vector512.LessThan(vq, Vector512.Create(24));
            var p = (Ld32(pr, i) * vd) & m;
            var (lo64, hi64) = Vector512.Widen(p);
            acc += lo64 + hi64;
        }
        return Vector512.Sum(acc) + Q6Natural(i, hi);
    }
    [MethodImpl(MethodImplOptions.NoInlining)]
    static void Q1Natural(int lo, int hi, long[] acc)
    {
        for (int i = lo; i < hi; i++)
        {
            if (sd[i] <= 10471)
            {
                int g = rf[i] * 2 + ls[i];
                long p = pr[i], dp = p * (100 - d[i]);
                acc[g * 5] += 1; acc[g * 5 + 1] += q[i]; acc[g * 5 + 2] += p; acc[g * 5 + 3] += dp; acc[g * 5 + 4] += dp * (100 + t[i]);
            }
        }
    }
    // Q1 optimisé : Vector512 + intrinsèques AVX-512, agrégation masquée par groupe (comme la référence C)
    [MethodImpl(MethodImplOptions.NoInlining)]
    static void Q1Tuned(int lo, int hi, long[] acc)
    {
        var c100 = Vector512.Create(100);
        Span<Vector512<int>> aq = stackalloc Vector512<int>[6], ap = stackalloc Vector512<int>[6], adp = stackalloc Vector512<int>[6];
        Span<Vector512<long>> ace = stackalloc Vector512<long>[6], aco = stackalloc Vector512<long>[6];
        Span<long> cnt = stackalloc long[6];
        int i = lo;
        while (i + 16 <= hi)
        {
            aq.Clear(); ap.Clear(); adp.Clear(); ace.Clear(); aco.Clear(); cnt.Clear();
            int end = i + 4096 <= hi ? i + 4096 : hi - (hi - i) % 16;
            for (; i < end; i += 16)
            {
                var pass = Vector512.LessThanOrEqual(Ld32(sd, i), Vector512.Create(10471));
                var vg = (Ld8(rf, i) << 1) + Ld8(ls, i);
                var vq = Ld8(q, i); var vd = Ld8(d, i); var vt = Ld8(t, i) + c100; var vp = Ld32(pr, i);
                var vdp = vp * (c100 - vd);
                var che = Avx512F.Multiply(vdp, vt);                                                   // lignes paires (vpmuldq)
                var cho = Avx512F.Multiply(Vector512.ShiftRightLogical(vdp.AsInt64(), 32).AsInt32(), Vector512.ShiftRightLogical(vt.AsInt64(), 32).AsInt32());
                for (int g = 0; g < 6; g++)
                {
                    var m = pass & Vector512.Equals(vg, Vector512.Create(g));
                    cnt[g] += BitOperations.PopCount((uint)Vector512.ExtractMostSignificantBits(m));
                    aq[g] += vq & m; ap[g] += vp & m; adp[g] += vdp & m;
                    var m64 = m.AsInt64();
                    ace[g] += che & Vector512.ShiftRightArithmetic(Vector512.ShiftLeft(m64, 32), 63);
                    aco[g] += cho & Vector512.ShiftRightArithmetic(m64, 63);
                }
            }
            for (int g = 0; g < 6; g++)
            {
                acc[g * 5] += cnt[g];
                acc[g * 5 + 1] += Vector512.Sum(aq[g]);
                acc[g * 5 + 2] += Vector512.Sum(ap[g]);
                var (l, h) = Vector512.Widen(adp[g]);
                acc[g * 5 + 3] += Vector512.Sum(l + h);
                acc[g * 5 + 4] += Vector512.Sum(ace[g] + aco[g]);
            }
        }
        if (i < hi) Q1Natural(i, hi, acc);
    }
    // Remarque C# : mêmes boucles naturelles, colonnes passées en paramètres au lieu de champs statiques
    [MethodImpl(MethodImplOptions.NoInlining)]
    static long Q6NaturalP(int[] sd, byte[] d, byte[] q, int[] pr, int lo, int hi)
    {
        long s = 0;
        for (int i = lo; i < hi; i++)
            if (sd[i] >= 8766 && sd[i] < 9131 && d[i] >= 5 && d[i] <= 7 && q[i] < 24) s += (long)pr[i] * d[i];
        return s;
    }
    [MethodImpl(MethodImplOptions.NoInlining)]
    static void Q1NaturalP(int[] sd, byte[] rf, byte[] ls, int[] pr, byte[] d, byte[] q, byte[] t, int lo, int hi, long[] acc)
    {
        for (int i = lo; i < hi; i++)
        {
            if (sd[i] <= 10471)
            {
                int g = rf[i] * 2 + ls[i];
                long p = pr[i], dp = p * (100 - d[i]);
                acc[g * 5] += 1; acc[g * 5 + 1] += q[i]; acc[g * 5 + 2] += p; acc[g * 5 + 3] += dp; acc[g * 5 + 4] += dp * (100 + t[i]);
            }
        }
    }
    static void RunK6(string v, int reps, string p)
    {
        sd = Load<int>("k6_shipdate.i32"); pr = Load<int>("k6_extendedprice.i32"); q = LoadBytes("k6_quantity.u8");
        d = LoadBytes("k6_discount.u8"); t = LoadBytes("k6_tax.u8"); rf = LoadBytes("k6_returnflag.u8"); ls = LoadBytes("k6_linestatus.u8");
        bool q1 = p == "q1";
        Bench("k6", v, p, reps, () =>
        {
            long s = 0;
            if (v == "mt")
            {
                var part = new long[4];
                var th = new Thread[4];
                for (int k = 0; k < 4; k++)
                {
                    int kk = k, lo = N6 / 4 * k, hi = N6 / 4 * (k + 1);
                    th[k] = new Thread(() =>
                    {
                        if (q1) { var a = new long[30]; Q1Tuned(lo, hi, a); part[kk] = a.Sum(); }
                        else part[kk] = Q6Tuned(lo, hi);
                    });
                    th[k].Start();
                }
                foreach (var x in th) x.Join();
                s = part.Sum();
            }
            else if (q1)
            {
                var a = new long[30];
                if (v == "tuned") Q1Tuned(0, N6, a); else Q1NaturalP(sd, rf, ls, pr, d, q, t, 0, N6, a); // Remarque C#
                s = a.Sum();
            }
            else s = v == "tuned" ? Q6Tuned(0, N6) : Q6NaturalP(sd, d, q, pr, 0, N6); // Remarque C#
            return s.ToString();
        });
    }

    // ------------------------------------------------------------------ K7
    [StructLayout(LayoutKind.Sequential)] struct Slot { public uint Key, Count; public ulong Sum; }
    static void RunK7(string v, int reps)
    {
        uint[] keys = Load<uint>("k7_keys.u32"), vals = Load<uint>("k7_vals.u32");
        for (int r = -Warmup; r < reps; r++)
        {
            ulong nk = 0, ws = 0; double dt;
            if (v == "natural")
            {
                long t0 = Stopwatch.GetTimestamp();
                var m = new Dictionary<uint, (uint Count, ulong Sum)>();
                for (int i = 0; i < keys.Length; i++)
                {
                    uint k = keys[i];
                    m[k] = m.TryGetValue(k, out var e) ? (e.Count + 1, e.Sum + vals[i]) : (1u, vals[i]);
                }
                dt = Stopwatch.GetElapsedTime(t0).TotalSeconds;
                nk = (ulong)m.Count;
                foreach (var (k, e) in m) ws += e.Sum * ((k & 1023) + 1);
            }
            else
            {
                const int LOG = 21, CAP = 1 << LOG, B = 16;
                long t0 = Stopwatch.GetTimestamp();
                var tab = new Slot[CAP];
                Span<uint> h = stackalloc uint[B];
                fixed (Slot* tp = tab)
                {
                    for (int i = 0; i < keys.Length; i += B)
                    {
                        for (int b = 0; b < B; b++) { h[b] = (keys[i + b] * 0x9E3779B1u) >> (32 - LOG); Sse.Prefetch0(tp + h[b]); }
                        for (int b = 0; b < B; b++)
                        {
                            uint k = keys[i + b], s = h[b];
                            while (tp[s].Count != 0 && tp[s].Key != k) s = (s + 1) & (CAP - 1);
                            tp[s].Key = k; tp[s].Count++; tp[s].Sum += vals[i + b];
                        }
                    }
                }
                dt = Stopwatch.GetElapsedTime(t0).TotalSeconds;
                foreach (var e in tab) if (e.Count != 0) { nk++; ws += e.Sum * ((e.Key & 1023) + 1); }
            }
            if (r >= 0) Result("k7", v, "16M/1M", r, dt, $"{nk}:{ws}");
        }
    }

    // ------------------------------------------------------------------ K8
    sealed class Node { public long V; public Node? L, R; }
    static long cnt8;
    static Node TBuild(int dp) { var n = new Node { V = cnt8++ }; if (dp > 0) { n.L = TBuild(dp - 1); n.R = TBuild(dp - 1); } return n; }
    static long TSum(Node? n) => n == null ? 0 : n.V + TSum(n.L) + TSum(n.R);
    struct ANode { public long V; public int L, R; }
    static readonly ANode[] arena = new ANode[2047]; static int top;
    static int ABuild(int dp)
    {
        int i = top++; arena[i].V = cnt8++; arena[i].L = arena[i].R = -1;
        if (dp > 0) { int l = ABuild(dp - 1); arena[i].L = l; arena[i].R = ABuild(dp - 1); }
        return i;
    }
    static long ASum(int i) => i < 0 ? 0 : arena[i].V + ASum(arena[i].L) + ASum(arena[i].R);
    static Node? keep;
    static void RunK8(string v, int reps)
    {
        const int Q = 16384;
        cnt8 = 0; keep = TBuild(20); long lsum = TSum(keep);
        var lat = new long[Q];
        bool tuned = v == "tuned";
        for (int r = -Warmup; r < reps; r++)
        {
            long total = 0;
            long t0 = Stopwatch.GetTimestamp();
            for (int qq = 0; qq < Q; qq++)
            {
                long a = Stopwatch.GetTimestamp();
                cnt8 = qq;
                long s = tuned ? (top = 0) + ASum(ABuild(10)) : TSum(TBuild(10));
                total += s;
                lat[qq] = (long)Stopwatch.GetElapsedTime(a).TotalNanoseconds;
            }
            double dt = Stopwatch.GetElapsedTime(t0).TotalSeconds;
            if (r >= 0)
            {
                Result("k8", v, "16384x2047", r, dt, (total + lsum).ToString());
                Array.Sort(lat);
                Console.WriteLine($"LAT;{v};{lat[Q / 2]};{lat[Q * 9 / 10]};{lat[Q * 99 / 100]};{lat[Q * 999 / 1000]};{lat[Q - 1]}");
            }
        }
        GC.KeepAlive(keep);
    }

    // ------------------------------------------------------------------ K9
    const int M9 = 2048;
    static double K9Init(int i, int j) => ((i * 31 + j * 17) % 1024) / 1024.0;
    [MethodImpl(MethodImplOptions.NoInlining)]
    static void K9Natural(double[,] inp, double[,] outp)
    {
        for (int i = 1; i < M9 - 1; i++)
            for (int j = 1; j < M9 - 1; j++)
                outp[i, j] = 0.25 * (((inp[i - 1, j] + inp[i + 1, j]) + inp[i, j - 1]) + inp[i, j + 1]);
    }
    // ligne vectorisée (Vector512<double>), mêmes opérations dans le même ordre
    [MethodImpl(MethodImplOptions.NoInlining)]
    static void K9Rows(double* inp, double* outp, int r0, int r1)
    {
        var q4 = Vector512.Create(0.25);
        for (int i = r0; i < r1; i++)
        {
            double* up = inp + (i - 1) * M9, mid = inp + i * M9, dn = inp + (i + 1) * M9, o = outp + i * M9;
            int j = 1;
            for (; j + 8 <= M9 - 1; j += 8)
                Vector512.Store(q4 * (((Vector512.Load(up + j) + Vector512.Load(dn + j)) + Vector512.Load(mid + j - 1)) + Vector512.Load(mid + j + 1)), o + j);
            for (; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
        }
    }
    static void RunK9(string v, int reps)
    {
        for (int r = -Warmup; r < reps; r++)
        {
            double s = 0, dt;
            if (v == "natural")
            {
                var a = new double[M9, M9]; var b = new double[M9, M9];
                for (int i = 0; i < M9; i++) for (int j = 0; j < M9; j++) a[i, j] = b[i, j] = K9Init(i, j);
                long t0 = Stopwatch.GetTimestamp();
                for (int it = 0; it < 4; it++) { K9Natural(a, b); (a, b) = (b, a); }
                dt = Stopwatch.GetElapsedTime(t0).TotalSeconds;
                foreach (double x in a) s += x;
            }
            else
            {
                double* a = (double*)NativeMemory.AlignedAlloc(M9 * M9 * 8, 64), b = (double*)NativeMemory.AlignedAlloc(M9 * M9 * 8, 64);
                for (int k = 0; k < M9 * M9; k++) a[k] = b[k] = K9Init(k / M9, k % M9);
                long t0 = Stopwatch.GetTimestamp();
                for (int it = 0; it < 4; it++)
                {
                    if (v == "tuned") K9Rows(a, b, 1, M9 - 1);
                    else
                    {
                        double* fa = a, fb = b;
                        var th = new Thread[4];
                        for (int k = 0; k < 4; k++)
                        {
                            int r0 = 1 + (M9 - 2) * k / 4, r1 = 1 + (M9 - 2) * (k + 1) / 4;
                            th[k] = new Thread(() => K9Rows(fa, fb, r0, r1));
                            th[k].Start();
                        }
                        foreach (var x in th) x.Join();
                    }
                    double* tmp = a; a = b; b = tmp;
                }
                dt = Stopwatch.GetElapsedTime(t0).TotalSeconds;
                for (int k = 0; k < M9 * M9; k++) s += a[k];
                NativeMemory.AlignedFree(a); NativeMemory.AlignedFree(b);
            }
            if (r >= 0) Result("k9", v, "2048^2x4", r, dt, s.ToString("0.000000000000000e+00", Inv));
        }
    }

    // ------------------------------------------------------------------ K10
    const int M10 = 1 << 22, CAP10 = 1 << 14;
    static void RunK10(string v, int reps)
    {
        Bench("k10", v, "2^22", reps, () =>
        {
            long sum = 0;
            Thread prod, cons;
            if (v == "natural")
            {
                var bc = new BlockingCollection<long>(CAP10);
                prod = new Thread(() => { for (long x = 1; x <= M10; x++) bc.Add(x); bc.CompleteAdding(); });
                cons = new Thread(() => { long s = 0; foreach (var x in bc.GetConsumingEnumerable()) s += x; sum = s; });
            }
            else
            {
                long[] idx = new long[64]; // écriture @16, lecture @48 : 256 o d'écart
                long[] buf = new long[CAP10];
                prod = new Thread(() =>
                {
                    long w = 0, rc = 0;
                    for (long x = 1; x <= M10; x++)
                    {
                        while (w - rc == CAP10) { rc = Volatile.Read(ref idx[48]); if (w - rc == CAP10) Thread.SpinWait(1); }
                        buf[w & (CAP10 - 1)] = x;
                        Volatile.Write(ref idx[16], ++w);
                    }
                });
                cons = new Thread(() =>
                {
                    long rd = 0, wc = 0, s = 0;
                    for (int k = 0; k < M10; k++)
                    {
                        while (rd == wc) { wc = Volatile.Read(ref idx[16]); if (rd == wc) Thread.SpinWait(1); }
                        s += buf[rd & (CAP10 - 1)];
                        Volatile.Write(ref idx[48], ++rd);
                    }
                    sum = s;
                });
            }
            cons.Start(); prod.Start(); prod.Join(); cons.Join();
            return sum.ToString();
        });
    }

    static void Main(string[] a)
    {
        string k = a[0], v = a[1], p = a.Length > 3 ? a[3] : "";
        int reps = int.Parse(a[2]);
        switch (k)
        {
            case "k1": RunK1(v, reps); break;
            case "k2": RunK2(v, reps, p); break;
            case "k3": RunK3(v, reps); break;
            case "k4": RunK4(v, reps); break;
            case "k5": RunK5(v, reps); break;
            case "k6": RunK6(v, reps, p); break;
            case "k7": RunK7(v, reps); break;
            case "k8": RunK8(v, reps); break;
            case "k9": RunK9(v, reps); break;
            case "k10": RunK10(v, reps); break;
        }
    }
}
