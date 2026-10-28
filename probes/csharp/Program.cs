using System;
using System.IO.MemoryMappedFiles;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Explicit)] struct U { [FieldOffset(0)] public float F; [FieldOffset(0)] public uint I; }
[StructLayout(LayoutKind.Sequential)] struct S { public byte A; public uint B; public double C; }
[InlineArray(16)] struct Buf16 { private float _e; }
struct In { public Buf16 V; public int N; }
unsafe class Probe {
    static void Main() {
        Console.WriteLine($"CAP;A2;1;Marshal.OffsetOf(S, C)={Marshal.OffsetOf<S>("C")}");
        var u = new U { F = 1.0f };
        Console.WriteLine($"CAP;A5;1;FieldOffset recouvrants 0x{u.I:x8}");
        Console.WriteLine($"CAP;A7;1;[InlineArray(16)] sizeof(In)={sizeof(In)}");
        using var mmf = MemoryMappedFile.CreateFromFile("/opt/msdata/k5_a.f32", System.IO.FileMode.Open);
        using var acc = mmf.CreateViewAccessor(0, 8192, MemoryMappedFileAccess.Read);
        byte* p = null; acc.SafeMemoryMappedViewHandle.AcquirePointer(ref p);
        Console.WriteLine($"CAP;F4;1;MemoryMappedFile + pointeur : {((float*)p)[0]}");
        acc.SafeMemoryMappedViewHandle.ReleasePointer();
    }
}
