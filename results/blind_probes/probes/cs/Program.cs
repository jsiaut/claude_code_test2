using System;
using System.Linq;
using System.Numerics;
using System.Reflection;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
unsafe class P {
  static void Main() {
    var a = new Vector<float>(2f); var b = a * a + a;
    Console.WriteLine($"Vector<float>.Count={Vector<float>.Count} b0={b[0]} V512accel={Vector512.IsHardwareAccelerated}");
    var v = Vector256.Create(1f); Console.WriteLine($"Vector256 sum={Vector256.Sum(v + v)}");
    if (Avx512F.IsSupported) { var z = Avx512F.Add(Vector512.Create(1f), Vector512.Create(2f)); Console.WriteLine($"Avx512F.Add ok {z[0]}"); }
    foreach (var n in new[]{"Avx512Vnni","Avx10v1","Avx10v2","AvxVnni","X86Base"}) Console.WriteLine($"type {n}: {typeof(Sse).Assembly.GetType("System.Runtime.Intrinsics.X86."+n) != null}");
    double tot = 0; object l = new object(); var ids = new System.Collections.Concurrent.ConcurrentDictionary<int,bool>();
    Parallel.For(0, 10_000_000, () => 0.0, (i, s, loc) => { ids[Environment.CurrentManagedThreadId]=true; return loc + 1.0/(1+i); }, loc => { lock(l) tot += loc; });
    Console.WriteLine($"Parallel.For tot={tot:F3} threads={ids.Count}; PLINQ sum={Enumerable.Range(0,1000).AsParallel().Sum()}");
    try { var p = Process.GetCurrentProcess(); p.ProcessorAffinity = (IntPtr)1; Console.WriteLine($"Process.ProcessorAffinity set ok -> {p.ProcessorAffinity}"); } catch (Exception e) { Console.WriteLine("Process affinity: " + e.GetType().Name); }
    try { var t = Process.GetCurrentProcess().Threads[0]; t.ProcessorAffinity = (IntPtr)1; Console.WriteLine("ProcessThread affinity ok"); } catch (Exception e) { Console.WriteLine("ProcessThread affinity: " + e.GetType().Name); }
    Interlocked.MemoryBarrier(); Thread.SpinWait(10); X86Base.Pause(); Console.WriteLine("MemoryBarrier/SpinWait/X86Base.Pause ok");
    int x = 0; Volatile.Write(ref x, 1); Console.WriteLine($"Volatile.Read={Volatile.Read(ref x)}");
    float[] arr = new float[64]; fixed (float* pa = arr) { Sse.Prefetch0(pa); Sse.PrefetchNonTemporal(pa); } Console.WriteLine("Sse.Prefetch0 ok");
    // scan public API surface
    var asms = AppDomain.CurrentDomain.GetAssemblies().ToList();
    foreach (var f in System.IO.Directory.GetFiles(System.IO.Path.GetDirectoryName(typeof(object).Assembly.Location), "System.*.dll")) { try { asms.Add(Assembly.LoadFrom(f)); } catch {} }
    var pubs = asms.Distinct().SelectMany(asm => { try { return asm.GetExportedTypes(); } catch { return Type.EmptyTypes; } }).Distinct().ToList();
    foreach (var key in new[]{"CacheLine","Likely","Unlikely","Prefetch","Affinity","MemoryOrder","Relaxed","FalseSharing","Padded"}) {
      var hits = pubs.SelectMany(t => t.GetMembers(BindingFlags.Public|BindingFlags.Static|BindingFlags.Instance|BindingFlags.DeclaredOnly).Where(m => m.Name.Contains(key, StringComparison.OrdinalIgnoreCase)).Select(m => t.Name+"."+m.Name))
        .Concat(pubs.Where(t => t.Name.Contains(key, StringComparison.OrdinalIgnoreCase)).Select(t => "type " + t.FullName)).Distinct().Take(12).ToList();
      Console.WriteLine($"public[{key}]: {hits.Count} {string.Join(", ", hits)}");
    }
    var ph = typeof(object).Assembly.GetType("System.Threading.PaddingHelpers") ?? typeof(object).Assembly.GetType("System.Runtime.CompilerServices.PaddingHelpers");
    Console.WriteLine($"internal PaddingHelpers: {ph?.FullName} public={ph?.IsPublic} CACHE_LINE_SIZE={ph?.GetField("CACHE_LINE_SIZE", BindingFlags.NonPublic|BindingFlags.Static|BindingFlags.Public)?.GetValue(null)}");
  }
}
