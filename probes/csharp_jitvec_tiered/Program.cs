using System;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Threading;
// Même sonde que probes/csharp_jitvec, mais avec la compilation par niveaux et la PGO dynamique par défaut (comme le
// benchmark) : on appelle les méthodes assez longtemps pour qu'elles atteignent le niveau 1 avec profil, et on lit le
// code machine de chaque niveau (DOTNET_JitDisasm).
static class P
{
    [MethodImpl(MethodImplOptions.NoInlining)] static int SumInt(int[] a) { int s = 0; for (int i = 0; i < a.Length; i++) s += a[i]; return s; }
    [MethodImpl(MethodImplOptions.NoInlining)] static void AddF(float[] a, float[] b, float[] c) { for (int i = 0; i < c.Length; i++) c[i] = a[i] + b[i]; }
    [MethodImpl(MethodImplOptions.NoInlining)] static long CondSum(byte[] d) { long s = 0; foreach (byte x in d) if (x >= 128) s += x; return s; }
    static void Main()
    {
        var a = new int[256]; var f = new float[256]; var g = new float[256]; var h = new float[256]; var d = new byte[256];
        long t = 0;
        var sw = Stopwatch.StartNew();
        while (sw.ElapsedMilliseconds < 3000)
        {
            for (int r = 0; r < 1000; r++) { t += SumInt(a); AddF(f, g, h); t += CondSum(d); }
            Thread.Sleep(1);
        }
        Console.WriteLine(t);
    }
}
