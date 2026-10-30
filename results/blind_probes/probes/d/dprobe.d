import core.simd, core.atomic, core.thread, core.cpuid, core.builtins;
import core.sys.linux.sched;
import std.parallelism, std.range, std.stdio;
import ldc.attributes;
import ldc.gccbuiltins_x86;

@target("avx512f,avx512cd")
int16 conflict(int16 a) { return __builtin_ia32_vpconflictsi_512(a); }

@cold int slow(int x) { return x * 3; }

shared int flag; __gshared int data;

void main() {
    float8 a = [1,2,3,4,5,6,7,8];
    float8 b = a * a + a;
    writeln("core.simd float8 ok ", b.array[7]);
    int[128] arr;
    prefetch!(false, 3)(&arr[64]);
    int x = 5;
    if (likely(x > 0)) writeln("likely ok"); else writeln(slow(x));
    auto t = new Thread({
        while (atomicLoad!(MemoryOrder.raw)(flag) == 0) pause();
        atomicFence!(MemoryOrder.acq)();
        writeln("thread saw ", data);
    }).start();
    data = 42;
    atomicFence!(MemoryOrder.rel)();
    atomicStore!(MemoryOrder.raw)(flag, 1);
    t.join();
    writeln("core.cpuid L1D lineSize=", dataCaches()[0].lineSize, " std.parallelism.cacheLineSize=", cacheLineSize);
    cpu_set_t s; CPU_SET(0, &s);
    writeln("sched_setaffinity rc=", sched_setaffinity(0, s.sizeof, &s));
    double sum = taskPool.reduce!"a + b"(0.0, iota(1, 10_000_001).map!(i => 1.0 / i));
    shared int cnt;
    foreach (i; parallel(iota(0, 1000))) atomicOp!"+="(cnt, 1);
    writeln("parallel reduce=", sum, " foreach cnt=", cnt, " workers=", taskPool.size);
}
import std.algorithm : map;
