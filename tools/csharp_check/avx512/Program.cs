using System.Numerics;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
Console.WriteLine($"Vector512.IsHardwareAccelerated={Vector512.IsHardwareAccelerated} Vector256.IsHardwareAccelerated={Vector256.IsHardwareAccelerated} Avx512F.IsSupported={Avx512F.IsSupported} Vector<byte>.Count={Vector<byte>.Count}");
