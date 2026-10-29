using System;
using System.Runtime.CompilerServices;
// Le JIT de .NET vectorise-t-il des boucles simples sans aide ? On lit son propre code machine (DOTNET_JitDisasm).
static class P
{
    [MethodImpl(MethodImplOptions.NoInlining)] static int SumInt(int[] a) { int s = 0; for (int i = 0; i < a.Length; i++) s += a[i]; return s; }
    [MethodImpl(MethodImplOptions.NoInlining)] static void AddF(float[] a, float[] b, float[] c) { for (int i = 0; i < c.Length; i++) c[i] = a[i] + b[i]; }
    [MethodImpl(MethodImplOptions.NoInlining)] static long CondSum(byte[] d) { long s = 0; foreach (byte x in d) if (x >= 128) s += x; return s; }
    static void Main()
    {
        var a = new int[4096]; var f = new float[4096]; var g = new float[4096]; var h = new float[4096]; var d = new byte[4096];
        long t = 0;
        for (int r = 0; r < 2000; r++) { t += SumInt(a); AddF(f, g, h); t += CondSum(d); }
        Console.WriteLine(t);
    }
}
