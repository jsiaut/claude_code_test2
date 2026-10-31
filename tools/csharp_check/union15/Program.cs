using System.Reflection;
using System.Runtime.CompilerServices;
public record struct A(int X);
public record struct B(double Y);
public union AB(A, B);
public static class P
{
    public static void Main()
    {
        AB u = new B(1.5);
        Console.WriteLine($"IsValueType={typeof(AB).IsValueType} SizeOf={(typeof(AB).IsValueType ? Unsafe.SizeOf<AB>() : -1)} sizeof(A)={Unsafe.SizeOf<A>()} sizeof(B)={Unsafe.SizeOf<B>()}");
        foreach (var f in typeof(AB).GetFields(BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public))
            Console.WriteLine($"field {f.Name} : {f.FieldType}  explicitLayout={typeof(AB).IsExplicitLayout}");
        Console.WriteLine(u switch { A a => $"A {a.X}", B b => $"B {b.Y}" });
    }
}
