using System.Runtime.CompilerServices;
public interface IAdder { int Add(int x); }
public struct P : IAdder { public int V; public int Add(int x) => V + x; }
public sealed class Q : IAdder { public int V; public int Add(int x) => V + x; }
public static class G
{
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Apply<T>(T a, int n) where T : IAdder => a.Add(n);
    public static void Main()
    {
        int s = 0;
        for (int i = 0; i < 10; i++) s += Apply(new P { V = 3 }, i) + Apply(new Q { V = 3 }, i);
        Console.WriteLine(s);
    }
}
