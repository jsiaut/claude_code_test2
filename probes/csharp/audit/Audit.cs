// Audit de la grille, C# (.NET 10, réglages du banc) : chaque case est exercée sous sa forme la plus forte et imprime
// un fait observable (docs/V4_PLAN.md 2.1). Lignes CAP (preuve complète), FACT (complétée par run.sh avec le code
// machine des méthodes Cg*, listé par DOTNET_JitDisasm) et NOTE (contre-épreuves).
using System;
using System.Buffers;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.IO;
using System.IO.MemoryMappedFiles;
using System.Linq;
using System.Numerics;
using System.Runtime;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
using System.Threading;
using System.Threading.Tasks;

struct P16 { public float X, Y, Z, VX, VY, VZ, AX, AY, AZ, M, Q, R, T, Pr, E, D; }
[StructLayout(LayoutKind.Sequential)] struct S { public byte A; public uint B; public double C; }
[StructLayout(LayoutKind.Explicit)] struct X { [FieldOffset(0)] public byte A; [FieldOffset(16)] public double C; }
[StructLayout(LayoutKind.Sequential, Pack = 1)] struct Pk { public byte A; public uint B; }
[StructLayout(LayoutKind.Sequential, Size = 64)] struct S64 { public float V; }
[StructLayout(LayoutKind.Explicit)] struct U { [FieldOffset(0)] public float F; [FieldOffset(0)] public uint I; }
[InlineArray(16)] struct Buf16 { private float _e; }
struct In { public Buf16 V; public int N; }

static unsafe class Audit
{
    static void Cap(string c, string v, string ev) => Console.WriteLine($"CAP;{c};{v};{ev}");
    static void Fact(string c, string ev) => Console.WriteLine($"FACT;{c};{ev}");
    static void Note(string c, string ev) => Console.WriteLine($"NOTE;{c};{ev}");
    static long Alloc() => GC.GetAllocatedBytesForCurrentThread();
    static float sink;

    // --- méthodes dont run.sh lit le code machine (optimisées dès la première compilation)
    const MethodImplOptions CG = MethodImplOptions.NoInlining | MethodImplOptions.AggressiveOptimization;
    [MethodImpl(CG)] static Vector256<float> CgFma(Vector256<float> a, Vector256<float> b, Vector256<float> c) => Vector256.FusedMultiplyAdd(a, b, c);
    [MethodImpl(CG)] static Vector512<float> CgVec512(Vector512<float> a, Vector512<float> b) => a * b + a;
    [MethodImpl(CG)] static Vector512<float> CgAvx512(Vector512<float> a, Vector512<float> b) => Avx512F.Add(a, b);
    [MethodImpl(CG)] static long CgInc(ref long x) => Interlocked.Increment(ref x);
    [MethodImpl(CG)] static int CgCas(ref int x, int v) => Interlocked.CompareExchange(ref x, v, 0);
    [MethodImpl(CG)] static void CgVolWrite(ref int x, int v) => Volatile.Write(ref x, v);
    [MethodImpl(CG)] static int CgVolRead(ref int x) => Volatile.Read(ref x);
    [MethodImpl(CG)] static void CgPause() => X86Base.Pause();
    [MethodImpl(CG)] static void CgBarrier() => Interlocked.MemoryBarrier();
    [MethodImpl(CG)] static void CgPrefetch(byte* p) => Sse.Prefetch0(p);
    [MethodImpl(CG)] static float CgIdx(float[] a, int i) => a[i];
    [MethodImpl(CG)] static float CgIdxUnsafe(float[] a, int i) => Unsafe.Add(ref MemoryMarshal.GetArrayDataReference(a), i);
    [MethodImpl(CG)] static T CgSum<T>(T[] a) where T : INumber<T> { T s = T.Zero; foreach (var e in a) s += e; return s; }
    [MethodImpl(CG)] static int CgCount<T>(T[] a) where T : class { int n = 0; foreach (var e in a) if (e != null) n++; return n; }

    static double Pairwise(double[] a, int lo, int hi)
    {
        if (hi - lo <= 8) { double s = 0; for (int i = lo; i < hi; i++) s += a[i]; return s; }
        int m = (lo + hi) / 2;
        return Pairwise(a, lo, m) + Pairwise(a, m, hi);
    }
    static void Axpy(Span<float> y, ReadOnlySpan<float> x, float a) { for (int i = 0; i < y.Length; i++) y[i] += a * x[i]; }

    static void Main(string[] args)
    {
        // ---------- A : disposition
        var ps = new P16[1000];
        Cap("A1", "1", $"[exécutée] P16[1000] (struct de 16 float) : Unsafe.SizeOf = {Unsafe.SizeOf<P16>()} o, écart entre éléments {Unsafe.ByteOffset(ref ps[0], ref ps[1])} o (valeurs en ligne)");
        S s = default; X x = default;
        Cap("A2", "1", $"[exécutée] LayoutKind.Sequential {{byte; uint; double}} : décalages A=0 B={Unsafe.ByteOffset(ref s.A, ref Unsafe.As<uint, byte>(ref s.B))} C={Unsafe.ByteOffset(ref s.A, ref Unsafe.As<double, byte>(ref s.C))} (ordre déclaré) ; LayoutKind.Explicit, FieldOffset(16) : C à {Unsafe.ByteOffset(ref x.A, ref Unsafe.As<double, byte>(ref x.C))} ; Marshal.OffsetOf(S, C) = {Marshal.OffsetOf<S>("C")}");
        Fact("A3", $"StructLayout(Pack = 1) {{byte; uint}} : Unsafe.SizeOf = {Unsafe.SizeOf<Pk>()} o");
        var al = new long[3];
        for (int k = 0; k < 3; k++) { var arr = new S64[4]; al[k] = (long)Unsafe.AsPointer(ref arr[0]) % 64; GC.KeepAlive(arr); }
        void* na = NativeMemory.AlignedAlloc(256, 64);
        Cap("A4", "0.5", $"[exécutée] NativeMemory.AlignedAlloc(256, 64) : adresse mod 64 = {(long)na % 64} (alignement par allocation, à la main) ; pas d'attribut d'alignement de type : StructLayout(Size = 64) donne {Unsafe.SizeOf<S64>()} o, mais le premier élément de trois tableaux new S64[4] est à {string.Join(", ", al)} modulo 64");
        NativeMemory.AlignedFree(na);
        var u = new U { F = 1.0f };
        Cap("A5", "1", $"[exécutée] FieldOffset(0) recouvrants (union brute) : float 1.0 → 0x{u.I:x8} ; BitConverter.SingleToUInt32Bits(1f) = 0x{BitConverter.SingleToUInt32Bits(1f):x8} ; Unsafe.As<float, uint> = 0x{Unsafe.As<float, uint>(ref u.F):x8}");
        In inl = default;
        Cap("A7", "1", $"[exécutée] [InlineArray(16)] de float dans une struct : sizeof(In) = {sizeof(In)} o, N à {Unsafe.ByteOffset(ref Unsafe.As<Buf16, byte>(ref inl.V), ref Unsafe.As<int, byte>(ref inl.N))} (tableau fixe en ligne)");
        Half h = (Half)1.5f;
        Cap("A8", "1", $"[exécutée] sizeof : byte {sizeof(byte)}, short {sizeof(short)}, Half {sizeof(Half)} ({h}), float {sizeof(float)}");

        // ---------- B : mémoire
        long c0 = GC.CollectionCount(0);
        for (int i = 0; i < 1024 * 1024; i++) { var g = new byte[1024]; GC.KeepAlive(g); }
        long c1 = GC.CollectionCount(0);
        Fact("B1", $"1 Gio de tableaux de 1 Kio sans référence : {c1 - c0} collectes de génération 0 déclenchées par le runtime, sans appel du programme (ramasse-miettes traçant)");
        bool started = GC.TryStartNoGCRegion(16 << 20);
        long n0 = GC.CollectionCount(0);
        for (int i = 0; i < 8 * 1024; i++) { var g = new byte[1024]; GC.KeepAlive(g); }
        long n1 = GC.CollectionCount(0);
        string mode1 = GCSettings.LatencyMode.ToString();
        if (GCSettings.LatencyMode == GCLatencyMode.NoGCRegion) GC.EndNoGCRegion();
        GC.TryStartNoGCRegion(16 << 20);
        long m0 = GC.CollectionCount(0);
        for (int i = 0; i < 64 * 1024; i++) { var g = new byte[1024]; GC.KeepAlive(g); }
        long m1 = GC.CollectionCount(0);
        string end;
        try { GC.EndNoGCRegion(); end = "fermée normalement"; } catch (InvalidOperationException e) { end = "EndNoGCRegion : " + e.GetType().Name; }
        Note("B1", $"GC.TryStartNoGCRegion(16 Mio) = {started} : 8 Mio alloués, collectes : {n1 - n0} (mode {mode1}) ; 64 Mio dans une région de 16 Mio, collectes : {m1 - m0}, la région se termine ({end}) : suspension bornée, la mémoire n'est rendue que par le ramasse-miettes");

        var pool = ArrayPool<float>.Shared;
        var r1 = pool.Rent(1000); pool.Return(r1); var r2 = pool.Rent(1000);
        void* nm = NativeMemory.Alloc(4096);
        Fact("B2", $"ArrayPool<float>.Shared : Rent, Return, Rent rend le même tableau ({ReferenceEquals(r1, r2)}) ; NativeMemory.Alloc hors du tas géré ({(nm != null ? "non nul" : "nul")}) ; new, List<T> et les autres conteneurs ne prennent pas d'allocateur");
        NativeMemory.Free(nm);

        long b0 = Alloc();
        float* sb = stackalloc float[16];
        int local = 7;
        long dist = Math.Abs((long)&local - (long)sb);
        Span<float> sp = new Span<float>(sb, 16);
        for (int i = 0; i < 16; i++) sp[i] = i * 0.5f;
        var pv = new P16 { X = sp[3] };
        long b1 = Alloc();
        Cap("B3", "1", $"[exécutée] stackalloc float[16] : à {dist} o d'une variable locale (pile) ; Span<float> sur ce tampon et struct locale : {b1 - b0} octets alloués sur le tas (x = {pv.X})");

        // allocations implicites, comptées par GC.GetAllocatedBytesForCurrentThread
        var data = new float[1000];
        for (int i = 0; i < data.Length; i++) data[i] = (i * 7919) % 1000 - 500;
        int N = 1000;
        long a0 = Alloc(); float acc = 0; for (int i = 0; i < N; i++) { var q = new P16 { X = i }; acc += q.X * 2; } long a1 = Alloc();
        object o = null; long x0 = Alloc(); for (int i = 0; i < N; i++) o = i; long x1 = Alloc();
        Func<int> f = null; long f0 = Alloc(); for (int i = 0; i < N; i++) { int cap = i; f = () => cap + 1; } long f1 = Alloc();
        long l0 = Alloc(); float ls = 0; for (int i = 0; i < N; i++) ls += data.Where(v => v > 0).Sum(); long l1 = Alloc();
        var srt = (float[])data.Clone(); long s0 = Alloc(); Array.Sort(srt); long s1 = Alloc();
        sink = acc + ls + f() + (int)o;
        Cap("B4", "0.5", $"[exécutée] octets alloués par opération (GC.GetAllocatedBytesForCurrentThread) : arithmétique sur des structs {(a1 - a0) / N} ; allocations implicites : boîte d'un int {(x1 - x0) / N}, fermeture capturante {(f1 - f0) / N}, LINQ Where + Sum {(l1 - l0) / N}, Array.Sort d'un float[1000] {s1 - s0} (une fois)");

        var buf = new uint[8];
        fixed (uint* p = buf) { *(p + 3) = 42; *(uint*)((byte*)p + 16) = 7; }
        Cap("B5", "1", $"[exécutée] pointeurs unsafe : *(p + 3) = 42 → buf[3] = {buf[3]} ; écriture par décalage d'octets → buf[4] = {buf[4]}");

        // ---------- C : SIMD
        var va = Vector256.Create(2f); var vb = Vector256.Create(3f); var vc = Vector256.Create(1f);
        Fact("C1", $"Vector256.FusedMultiplyAdd(2, 3, 1) = {CgFma(va, vb, vc).GetElement(0)} ; Vector512<float> (Vector512.IsHardwareAccelerated = {Vector512.IsHardwareAccelerated}) : a*b + a = {CgVec512(Vector512.Create(2f), Vector512.Create(3f)).GetElement(15)}");
        Fact("C2", $"System.Runtime.Intrinsics.X86 : Avx512F.IsSupported = {Avx512F.IsSupported}, Avx512F.Add = {CgAvx512(Vector512.Create(1f), Vector512.Create(2f)).GetElement(0)}");

        var rnd = new Random(42);
        var dv = new double[1_000_000];
        for (int i = 0; i < dv.Length; i++) dv[i] = rnd.NextDouble() - 0.5;
        double loop = 0;
        for (int rep = 0; rep < 50; rep++) { loop = 0; foreach (var e in dv) loop += e; }   // assez de passages pour le niveau 1 du JIT
        double linq = dv.Sum();
        double pw = Pairwise(dv, 0, dv.Length);
        Fact("C4", $"un million de doubles : boucle foreach (JIT, niveau 1) {loop:R}, Enumerable.Sum {linq:R} ({(loop == linq ? "identiques, ordre gardé" : "différentes")}) ; somme par paires écrite à la main {pw:R} (écart {Math.Abs(pw - loop):G3}) ; aucune option ni API de réassociation");

        var tids = new ConcurrentDictionary<int, int>();
        Parallel.For(0, 64, i => { tids[Environment.CurrentManagedThreadId] = 1; Thread.SpinWait(200000); });
        Cap("C5", "1", $"[exécutée] Parallel.For : 64 itérations sur {tids.Count} fils (PLINQ aussi : System.Linq.ParallelEnumerable)");

        // ---------- D : parallélisme
        long cnt = 0;
        var ths = new Thread[4];
        for (int t = 0; t < 4; t++) { ths[t] = new Thread(() => { for (int i = 0; i < 1000; i++) Interlocked.Increment(ref cnt); }); ths[t].Start(); }
        foreach (var t in ths) t.Join();
        Cap("D1", "1", $"[exécutée] System.Threading.Thread : 4 fils, {cnt} incréments");
        long li = 0; int ci = 0, vi = 0;
        CgInc(ref li); CgCas(ref ci, 5); CgVolWrite(ref vi, 9);
        Fact("D2", $"Interlocked.Increment → {li}, Interlocked.CompareExchange → {ci}, Volatile.Write/Read → {CgVolRead(ref vi)}");

        // D4 : ProcessorAffinity, puis l'affinité de chaque fil (/proc/self/task/*/status)
        var proc = Process.GetCurrentProcess();
        long before = (long)proc.ProcessorAffinity;
        proc.ProcessorAffinity = (IntPtr)0b10;
        var cpu = Thread.GetCurrentProcessorId();
        int pinned = 0, others = 0;
        foreach (var d in Directory.GetDirectories("/proc/self/task"))
        {
            var line = File.ReadLines(Path.Combine(d, "status")).First(l => l.StartsWith("Cpus_allowed_list:"));
            if (line.Split(':')[1].Trim() == "1") pinned++; else others++;
        }
        string thr;
        try { proc.Threads[0].ProcessorAffinity = (IntPtr)1; thr = "accepté"; } catch (Exception e) { thr = e.GetType().Name; }
        Fact("D4", $"Process.ProcessorAffinity : 0x{before:x} → 0x2, processeur courant {cpu} ; sur Linux, sched_setaffinity sur le PID n'épingle que le fil principal : {pinned} fil épinglé, {others} autres fils du runtime inchangés ; ProcessThread.ProcessorAffinity : {thr}");
        proc.ProcessorAffinity = (IntPtr)before;

        CgPause(); CgBarrier();
        var sw = new SpinWait(); for (int i = 0; i < 5; i++) sw.SpinOnce();
        Fact("D5", $"X86Base.Pause, Interlocked.MemoryBarrier, Thread.SpinWait et SpinWait.SpinOnce ({sw.Count} tours)");

        // ---------- E : contrôle du code
        var pf = new byte[256];
        fixed (byte* p = pf) CgPrefetch(p + 64);
        Fact("E4", "Sse.Prefetch0(p)");
        var y = new float[16]; for (int i = 0; i < 16; i++) y[i] = 1;
        Axpy(y.AsSpan(1, 8), y.AsSpan(0, 8), 2);
        Fact("E5", $"Axpy(y[1..9], y[0..8], 2) sur des tranches qui se recouvrent : y[8] = {y[8]} (chaque écriture relue : le JIT doit supposer l'alias)");
        var fa = new float[] { 1, 2, 3, 4 };
        string oob;
        try { CgIdx(fa, 4); oob = "rien"; } catch (IndexOutOfRangeException e) { oob = e.GetType().Name; }
        Fact("E6", $"a[4] sur un float[4] : {oob} ; Unsafe.Add(ref MemoryMarshal.GetArrayDataReference(a), 2) = {CgIdxUnsafe(fa, 2)}");
        Fact("E7", $"CgSum<T> where T : INumber<T> : int {CgSum(new[] { 1, 2, 3 })}, double {CgSum(new[] { 0.5, 0.25 })}, float {CgSum(new[] { 1.5f })} ; CgCount<T> where T : class : {CgCount(new[] { "a", null, "b" })} (string), {CgCount(new object[] { 1 })} (object)");

        // ---------- F : données et arithmétique
        int rows = 3 + args.Length, cols = 4;
        var g2 = new double[rows, cols];
        for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) g2[i, j] = i * cols + j;
        Cap("F1", "1", $"[exécutée] double[{rows},{cols}] aux dimensions connues à l'exécution : écart entre lignes {Unsafe.ByteOffset(ref g2[0, 0], ref g2[1, 0])} o, g2[2,3] à {Unsafe.ByteOffset(ref g2[0, 0], ref g2[2, 3])} o = élément {g2[2, 3]} du bloc contigu");
        uint um = uint.MaxValue; string chk;
        try { checked { um += 1; } chk = "rien"; } catch (OverflowException e) { chk = e.GetType().Name; }
        uint wrap = unchecked(uint.MaxValue + (uint)args.Length + 6u);
        Cap("F3", "1", $"[exécutée] byte…ulong, Int128 ({sizeof(Int128)} o) : uint.MaxValue + 6 = {wrap} (unchecked, défaut) ; checked : {chk}");
        using (var mmf = MemoryMappedFile.CreateFromFile("/opt/msdata/k5_a.f32", FileMode.Open, null, 0, MemoryMappedFileAccess.Read))
        using (var acc2 = mmf.CreateViewAccessor(0, 8192, MemoryMappedFileAccess.Read))
        {
            byte* mp = null;
            acc2.SafeMemoryMappedViewHandle.AcquirePointer(ref mp);
            bool mapped = File.ReadLines("/proc/self/maps").Any(l => l.EndsWith("/opt/msdata/k5_a.f32"));
            Cap("F4", "1", $"[exécutée] MemoryMappedFile + pointeur : k5_a.f32 projeté ({mapped}, /proc/self/maps), premier float {((float*)mp)[0]}, dernier {((float*)mp)[2047]}");
            acc2.SafeMemoryMappedViewHandle.ReleasePointer();
        }
    }
}
